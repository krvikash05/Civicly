"""Narrow single-query batches through unchanged B03 fence/intent/audit machinery."""
from app.graph.models import NodeRecord,EdgeRecord
from app.graph.repository import Conflict,PreconditionFailed,interval,intersection
from app.graph.schema import timestamp


def node(repo,kind,props):
    repo.registry.validate_node(kind,props)
    return NodeRecord(id=props['id'],kind=kind,labels=tuple(sorted(set(repo.registry.labels(kind))-{repo.registry.base_label})),properties=props)

class Writer:
    def __init__(self,repo):self.repo=repo
    def commit(self,session,journal,new_nodes,updates,new_edges,edge_updates,summary,now):
        r=self.repo
        if r.graph.name!='civicly_knowledge' and not r.graph.name.startswith('civicly_b08_test_'):raise PreconditionFailed('B08 batch target protected')
        if any(n.kind not in {'Complaint','Incident','ProblemCluster'} for n in new_nodes) or any(n.kind!='ProblemCluster' for n in updates):raise PreconditionFailed('Unapproved intake node mutation')
        if any(e.kind not in {'REPORTS','PART_OF','OCCURRED_AT','AFFECTS'} for e in new_edges) or any(e.kind!='PART_OF' for e in edge_updates):raise PreconditionFailed('Unapproved intake relationship mutation')
        if any(e.properties.get('source_evidence_id')!=journal.id or (e.kind=='AFFECTS' and e.properties.get('association_status')!='REPORTED') for e in new_edges):raise PreconditionFailed('Intake cannot assert verified/unattributed associations')
        if journal.kind!='Evidence' or journal.properties['reliability']!='UNVERIFIED':raise PreconditionFailed('Intake journal must remain unverified')
        new={n.id:n for n in new_nodes}
        all_ids=[n.id for n in new_nodes]+[e.id for e in new_edges]
        if len(all_ids)!=len(set(all_ids)):raise Conflict('Cross-kind batch identity collision')
        if len(new)!=len(new_nodes) or len(new_edges)>8 or len(new_nodes)>3:raise PreconditionFailed('Intake batch shape exceeds scope')
        for n in [*new_nodes,*updates]:
            r.registry.validate_node(n.kind,n.properties);r._node_references(n.kind,n.properties)
            if n.id in new and (r._node_optional(n.id) or r._edge_optional(n.id)):raise Conflict('Intake identity collision')
        changed_edges={e.id for e in edge_updates}
        planned=[*new_edges,*edge_updates]
        if len({e.id for e in planned})!=len(planned):raise Conflict('Duplicate batch edge IDs')
        existing={journal.id:journal}
        for n in updates:
            old=r.get_node(n.id,n.kind);existing[n.id]=old
            if any(n.properties[k]!=old.properties[k] for k in ('id','created_at','municipality_id','schema_version','status')):raise PreconditionFailed('B08 cannot change cluster origin/state')
            if timestamp(n.properties['updated_at'])<timestamp(old.properties['updated_at']):raise PreconditionFailed('Update time moved backwards')
        for e in edge_updates:
            old=r.get_relationship(e.id)
            if e.kind!=old.kind or e.source!=old.source or e.target!=old.target or any(e.properties.get(k)!=v for k,v in old.properties.items() if k!='valid_to') or set(e.properties)-set(old.properties)-{'valid_to'}:raise PreconditionFailed('Regroup may only close old validity interval')
        for e in planned:
            for id in [e.source,e.target]:
                if id not in new and id not in existing:existing[id]=r.get_node(id)
            s=new.get(e.source) or existing[e.source];t=new.get(e.target) or existing[e.target]
            r.registry.validate_edge(e.kind,s.kind,s.properties,t.kind,t.properties,e.properties)
            r._check_evidence(e.properties)
            # Policy checks against persisted graph; closing old membership is excluded
            # only from the replacement check, then batch intervals checked together.
            excluded=e.id if e.id in changed_edges else next((old.id for old in edge_updates if old.kind==e.kind and old.source==e.source),None)
            r._relationship_policies(e.kind,s,t,e.properties,exclude=excluded)
            if e in new_edges and (r._node_optional(e.id) or r._edge_optional(e.id)):raise Conflict('Intake relationship ID collision')
        for i,e in enumerate(planned):
            for other in planned[:i]:
                if e.kind==other.kind and e.source==other.source and intersection(interval(e.properties),interval(other.properties)) is not None:
                    if e.target==other.target or e.kind in r.policy['singleton_outgoing']:raise Conflict('Batch temporal/cardinality conflict')
        params={'summary':summary,'now':now};parts=[];aliases={}
        # Resolve every existing endpoint BEFORE any writes. Missing endpoints cannot
        # leave preceding CREATEs behind through an empty later MATCH.
        for i,(id,n) in enumerate(sorted(existing.items())):
            alias='j' if id==journal.id else 'x'+str(i);aliases[id]=alias
            parts.append(f'MATCH ({alias}:CivicEntity {{id:$existing{i},municipality_id:$scope}}) ');params['existing'+str(i)]=id
        params['scope']=r.registry.scope
        for i,n in enumerate(new_nodes):
            alias='n'+str(i);aliases[n.id]=alias
            parts.append(f'CREATE ({alias}:'+':'.join(r.registry.labels(n.kind))+f') SET {alias}=$node{i} ');params['node'+str(i)]=n.properties
        for i,n in enumerate(updates):
            parts.append(f'SET {aliases[n.id]}=$update{i} ');params['update'+str(i)]=n.properties
        for i,e in enumerate(edge_updates):
            parts.insert(0,f'MATCH (es{i}:CivicEntity {{id:$es{i}}})-[old{i}:{e.kind} {{id:$oldid{i}}}]->(et{i}:CivicEntity {{id:$et{i}}}) ')
            params.update({f'es{i}':e.source,f'et{i}':e.target,f'oldid{i}':e.id,f'edgeupdate{i}':e.properties})
            parts.append(f'SET old{i}=$edgeupdate{i} ')
        for i,e in enumerate(new_edges):
            parts.append(f'CREATE ({aliases[e.source]})-[e{i}:{e.kind}]->({aliases[e.target]}) SET e{i}=$edge{i} ');params['edge'+str(i)]=e.properties
        parts.append('SET j.summary=$summary,j.updated_at=$now ')
        r._commit(session,'node',journal.id,journal.content_hash,''.join(parts),params,'j')
