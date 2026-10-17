"""Narrow B09 batch compiler; unchanged B03 integrity/fence/intent machinery."""
from app.graph.models import NodeRecord, EdgeRecord, digest
from app.graph.repository import Conflict, PreconditionFailed, interval, intersection
from app.graph.schema import timestamp
from app.graph.targets import is_allowed_graph_target

NODES = {'Investigation', 'Hypothesis', 'HypothesisAssessment', 'Inspection', 'Evidence', 'Finding'}
EDGES = {'INVESTIGATES', 'PROPOSES', 'CONCERNS', 'EXPLAINS', 'HAS_ASSESSMENT', 'SUPPORTED_BY',
         'CONTRADICTED_BY', 'INSPECTS', 'PRODUCED', 'ESTABLISHES'}


def target(repo):
    name = repo.graph.name
    if not is_allowed_graph_target(name) or (name != 'civicly_knowledge' and not name.startswith('civicly_b09_test_')):
        raise PreconditionFailed('B09 writes require canonical or isolated B09 graph; retained sources protected')


def stable(prefix, *parts):
    return prefix + '-B09-' + digest(parts)[:32]


def common(id, now):
    return {'id': id, 'municipality_id': 'demo-city', 'schema_version': 3, 'created_at': now, 'updated_at': now}


def node(repo, kind, props):
    repo.registry.validate_node(kind, props)
    return NodeRecord(id=props['id'], kind=kind, labels=tuple(sorted(set(repo.registry.labels(kind)) - {repo.registry.base_label})), properties=props)


def link(kind, source, dest, evidence_id, now):
    id = stable('REL', kind, source, dest, evidence_id)
    return EdgeRecord(id=id, kind=kind, source=source, target=dest,
        properties={'id': id, 'municipality_id': 'demo-city', 'created_at': now, 'valid_from': now, 'source_evidence_id': evidence_id})


def commit(repo, session, journal, nodes, updates, edges, summary, now):
    target(repo)
    if (len(nodes) > 12 or len(edges) > 35 or len(updates) > 1 or any(n.kind not in NODES for n in nodes)
            or any(n.kind not in {'Hypothesis', 'Inspection'} for n in updates)
            or any(e.kind not in EDGES for e in edges)):
        raise PreconditionFailed('B09 mutation exceeds authorized batch shape')
    planned = {n.id: n for n in nodes}
    ids = [n.id for n in nodes] + [e.id for e in edges]
    if len(ids) != len(set(ids)):
        raise Conflict('B09 batch identity collision')
    existing = {journal.id: journal}
    for n in nodes:
        repo.registry.validate_node(n.kind, n.properties)
        repo._node_references(n.kind, n.properties)
        if repo._node_optional(n.id) or repo._edge_optional(n.id):
            raise Conflict('B09 record identity collision')
    for n in updates:
        old = repo.get_node(n.id, n.kind)
        allowed = {'status', 'updated_at', 'scheduled_at', 'completed_at'} if n.kind == 'Inspection' else {'status', 'updated_at'}
        if any(n.properties.get(k) != v for k, v in old.properties.items() if k not in allowed) or set(n.properties) - set(old.properties) - allowed:
            raise PreconditionFailed('B09 cannot rewrite origin or hypothesis definition')
        if timestamp(n.properties['updated_at']) < timestamp(old.properties['updated_at']):
            raise PreconditionFailed('Update moved backwards')
        repo.registry.validate_node(n.kind, n.properties)
        existing[n.id] = old
    for e in edges:
        for id in (e.source, e.target):
            if id not in planned and id not in existing:
                existing[id] = repo.get_node(id)
        s, t = planned.get(e.source) or existing[e.source], planned.get(e.target) or existing[e.target]
        repo._relationship_policies(e.kind, s, t, e.properties)
        if repo._node_optional(e.id) or repo._edge_optional(e.id):
            raise Conflict('B09 relationship identity collision')
    for i, e in enumerate(edges):
        for other in edges[:i]:
            if e.kind == other.kind and e.source == other.source and intersection(interval(e.properties), interval(other.properties)) is not None:
                if e.target == other.target or e.kind in repo.policy['singleton_outgoing']:
                    raise Conflict('B09 batch relationship conflict')
    parts, params, aliases = [], {'scope': repo.registry.scope, 'summary': summary, 'now': now}, {}
    # Resolve all persisted endpoints BEFORE creating anything.
    for i, (id, n) in enumerate(sorted(existing.items())):
        alias = 'j' if id == journal.id else 'x' + str(i)
        aliases[id] = alias
        parts.append(f'MATCH ({alias}:CivicEntity {{id:$existing{i},municipality_id:$scope}}) ')
        params['existing' + str(i)] = id
    for i, n in enumerate(nodes):
        alias = 'n' + str(i)
        aliases[n.id] = alias
        parts.append(f'CREATE ({alias}:' + ':'.join(repo.registry.labels(n.kind)) + f') SET {alias}=$node{i} ')
        params['node' + str(i)] = n.properties
    for i, n in enumerate(updates):
        parts.append(f'SET {aliases[n.id]}=$update{i} ')
        params['update' + str(i)] = n.properties
    for i, e in enumerate(edges):
        parts.append(f'CREATE ({aliases[e.source]})-[e{i}:{e.kind}]->({aliases[e.target]}) SET e{i}=$edge{i} ')
        params['edge' + str(i)] = e.properties
    parts.append('SET j.summary=$summary,j.updated_at=$now ')
    repo._commit(session, 'node', journal.id, journal.content_hash, ''.join(parts), params, 'j')
