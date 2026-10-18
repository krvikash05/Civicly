"""Trusted B09 domain service. No MCP writes, dispatch, agent, or event delivery."""
import json
from pathlib import Path
from app.graph.models import digest, PathRecord
from app.graph.queries import GraphQueries
from app.graph.repository import Conflict, PreconditionFailed
from app.graph.schema import utc_now, timestamp
from .models import (Actor, Journal, Receipt, Report, Assessment, parse_command,
                     OpenInvestigation, Propose, RequestInspection, TransitionInspection, ReportInspection, Assess, InspectionView)
from .policies import POLICIES, classify_reviewed
from .classification import classify_evidence, add_topology_context
from .reader import Reader
from .writer import target, common, node, link, stable, commit

MACHINES = json.loads((Path(__file__).resolve().parents[4] / 'contracts/state_machines.json').read_text())['machines']


def transition(kind, old, new):
    if new not in MACHINES[kind]['transitions'].get(old, []):
        raise PreconditionFailed('Illegal domain state transition')
    return new


class EvidenceService:
    def __init__(self, repository, *, clock=utc_now):
        self.repo, self.clock = repository, clock

    def load(self, id, sha):
        n = self.repo._node_optional(id)
        if n is None:
            return None, None
        if n.kind != 'Evidence' or n.properties['evidence_type'] != 'B09_OPERATION' or n.properties['reliability'] != 'UNVERIFIED':
            raise Conflict('B09 journal identity/type collision')
        j = Journal.model_validate_json(n.properties['summary'])
        if j.request_hash != sha or digest({'actor': j.actor.model_dump(mode='json'), 'command': j.command}) != sha:
            raise Conflict('Request ID reused with different command/actor')
        return n, j

    def readback(self, receipt, replayed=False):
        if receipt.graph != self.repo.graph.name:
            raise PreconditionFailed('Receipt graph mismatch')
        for id in [receipt.entity_id, *receipt.created_ids, *receipt.updated_ids]:
            self.repo.get_node(id)
        for id in receipt.relationship_ids:
            self.repo.get_relationship(id)
        if receipt.assessment:
            actual = self.repo.get_node(receipt.assessment.id, 'HypothesisAssessment')
            if Assessment.model_validate_json(actual.properties['rationale']) != receipt.assessment:
                raise PreconditionFailed('Immutable assessment readback mismatch')
            supported = {e.target for e in Reader(self.repo, receipt.recorded_at).edges('SUPPORTED_BY', source=actual.id)}
            contradicted = {e.target for e in Reader(self.repo, receipt.recorded_at).edges('CONTRADICTED_BY', source=actual.id)}
            if supported != set(receipt.assessment.supporting_evidence_ids) or contradicted != set(receipt.assessment.contradicting_evidence_ids):
                raise PreconditionFailed('Assessment evidence relationships mismatch')
            for p in receipt.assessment.paths:
                for i, id in enumerate(p.edge_ids):
                    e = self.repo.get_relationship(id)
                    ends = (e.source, e.target) if p.directions[i] == 'OUTGOING' else (e.target, e.source)
                    if ends != (p.node_ids[i], p.node_ids[i+1]):
                        raise PreconditionFailed('Assessment path readback mismatch')
        return receipt.model_copy(update={'replayed': replayed})

    def execute(self, payload, actor):
        target(self.repo)
        if not isinstance(actor, Actor):
            raise TypeError('Trusted typed actor required; not public authentication')
        q = parse_command(payload)
        self.authorize(q, actor)
        now = self.clock()
        timestamp(now)
        canonical = q.model_dump(mode='json')
        sha = digest({'actor': actor.model_dump(mode='json'), 'command': canonical})
        jid = stable('EV-JOURNAL', actor.id, q.request_id)
        old, journal = self.load(jid, sha)
        if not old:
            journal = Journal(request_hash=sha, actor=actor, command=canonical)
            try:
                self.repo.create_node('Evidence', {**common(jid, now), 'evidence_type': 'B09_OPERATION',
                    'summary': journal.serialized(), 'reliability': 'UNVERIFIED', 'recorded_at': now,
                    'source_kind': 'USER', 'source_record_id': actor.id + ':' + q.request_id})
            except Conflict:
                self.load(jid, sha)  # Equal concurrent prepare only; unknown outcomes never retried.
        with self.repo._session() as session:
            old, journal = self.load(jid, sha)
            if journal.state == 'COMMITTED':
                return self.readback(journal.receipt, True)
            q = parse_command(journal.command)
            now = self.clock()
            reader = Reader(self.repo, now)
            entity, nodes, updates, edges, assessment = self.plan(q, actor, reader, jid, now, session.revision)
            receipt = Receipt(operation=q.operation, journal_id=jid, entity_id=entity, graph=self.repo.graph.name,
                graph_revision=session.revision + 1, recorded_at=now, created_ids=[n.id for n in nodes],
                relationship_ids=[e.id for e in edges], updated_ids=[n.id for n in updates], assessment=assessment)
            saved = journal.model_copy(update={'state': 'COMMITTED', 'receipt': receipt})
            commit(self.repo, session, old, nodes, updates, edges, saved.serialized(), now)
        _, saved = self.load(jid, sha)
        if saved.state != 'COMMITTED':
            raise PreconditionFailed('B09 receipt was not committed')
        return self.readback(saved.receipt)

    @staticmethod
    def authorize(q, actor):
        allowed = {'ANALYST', 'ADMIN'} if isinstance(q, (OpenInvestigation, Propose, Assess)) else {'ANALYST', 'DEPARTMENT_LEAD', 'ADMIN'}
        if isinstance(q, ReportInspection) or (isinstance(q, TransitionInspection) and q.status != 'REQUESTED'):
            allowed = {'DEPARTMENT_LEAD', 'ADMIN'}
        if actor.role not in allowed:
            raise PreconditionFailed('Role cannot perform this B09 operation')
        if actor.role == 'DEPARTMENT_LEAD' and not actor.department_id:
            raise PreconditionFailed('Department actor scope required')

    def inspection_source(self, reader, id):
        edges = reader.edges('INSPECTS', source=id)
        sources = {e.properties.get('source_evidence_id') for e in edges}
        if len(sources) != 1 or None in sources:
            raise PreconditionFailed('Unique inspection request source required')
        j = reader.journal(next(iter(sources)))
        if j.state != 'COMMITTED' or j.command['operation'] != 'request_inspection' or j.receipt.entity_id != id:
            raise PreconditionFailed('Inspection request binding mismatch')
        return j.command, {e.target for e in edges}

    def plan(self, q, actor, r, jid, now, revision):
        n = lambda kind, props: node(self.repo, kind, props)
        edge = lambda kind, s, t: link(kind, s, t, jid, now)
        if isinstance(q, OpenInvestigation):
            r.node(q.cluster_id, 'ProblemCluster')
            for id in q.incident_ids:
                r.node(id, 'Incident')
                if not any(e.target == q.cluster_id for e in r.edges('PART_OF', source=id)):
                    raise PreconditionFailed('Incident must have the specified active primary cluster')
            id = stable('INV', jid)
            inv = n('Investigation', {**common(id, now), 'status': 'OPEN', 'priority': q.priority, 'opened_at': now, 'graph_revision': revision})
            return id, [inv], [], [edge('INVESTIGATES', id, t) for t in [q.cluster_id, *q.incident_ids]], None
        if isinstance(q, Propose):
            r.node(q.investigation_id, 'Investigation')
            bound = {e.target for e in r.edges('INVESTIGATES', source=q.investigation_id)}
            if not set(q.incident_ids) <= bound:
                raise PreconditionFailed('Hypothesis incidents outside investigation')
            incidents = [r.node(id, 'Incident') for id in q.incident_ids]
            issues = {i.properties['issue_type'] for i in incidents}
            if len(issues) != 1:
                raise PreconditionFailed('One hypothesis issue; use competing hypotheses across categories')
            issue = next(iter(issues))
            rule = POLICIES[issue].get(q.cause_code)
            if rule and (not set(rule['confirming']) <= set(q.confirming_codes) or not set(rule['falsifying']) <= set(q.falsifying_codes)):
                raise PreconditionFailed('Expected observations cannot weaken domain criteria')
            affected = {e.target for id in q.incident_ids for e in r.edges('AFFECTS', source=id)}
            for id in q.asset_ids:
                r.node(id, 'InfrastructureAsset')
            if rule and not any(set(r.node(id).labels) & set(rule['asset_labels']) for id in q.asset_ids):
                raise PreconditionFailed('Known cause lacks its typed primary infrastructure asset')
            if q.topology:
                r.node(q.topology.source_id, 'InfrastructureAsset')
                r.node(q.topology.target_id, 'InfrastructureAsset')
                if rule and rule['requires_topology'] and (q.topology.operation != 'dependencies'
                        or not set(r.node(q.topology.source_id).labels) & set(rule['asset_labels'])
                        or 'RoadSegment' not in r.node(q.topology.target_id).labels):
                    raise PreconditionFailed('Utility leak topology must originate at the concerned pipe and end at the affected road')
                if q.topology.source_id not in q.asset_ids or q.topology.target_id not in affected:
                    raise PreconditionFailed('Topology must connect a concerned asset to an affected incident asset')
                result = r.topology(q.topology, exploratory=True)
                connected = any(p.node_ids[-1] == q.topology.target_id for p in result.paths)
                if not connected or result.truncated:
                    raise PreconditionFailed('Candidate mechanism lacks bounded explicit topology context')
            if not set(q.asset_ids) <= affected | ({q.topology.source_id} if q.topology else set()):
                raise PreconditionFailed('Unrelated infrastructure cannot become cause from proximity')
            id = stable('HYP', jid)
            h = n('Hypothesis', {**common(id, now), 'cause_code': q.cause_code, 'statement': q.statement, 'status': 'PROPOSED'})
            edges = [edge('PROPOSES', q.investigation_id, id)]
            edges += [edge('EXPLAINS', id, t) for t in q.incident_ids] + [edge('CONCERNS', id, t) for t in q.asset_ids]
            return id, [h], [], edges, None
        if isinstance(q, RequestInspection):
            r.node(q.investigation_id, 'Investigation')
            r.node(q.department_id, 'Department')
            if actor.role == 'DEPARTMENT_LEAD' and actor.department_id != q.department_id:
                raise PreconditionFailed('Inspection outside actor department')
            incidents = [e.target for e in r.edges('INVESTIGATES', source=q.investigation_id) if r.node(e.target).kind == 'Incident']
            assets = {e.target for id in incidents for e in r.edges('AFFECTS', source=id)}
            for e in r.edges('PROPOSES', source=q.investigation_id):
                assets.update(v.target for v in r.edges('CONCERNS', source=e.target))
            if not set(q.asset_ids) <= assets:
                raise PreconditionFailed('Inspection assets outside investigation context')
            for id in q.asset_ids:
                r.node(id, 'InfrastructureAsset')
            id = stable('INS', jid)
            ins = n('Inspection', {**common(id, now), 'inspection_type': q.inspection_type, 'status': 'PROPOSED', 'requested_at': now})
            return id, [ins], [], [edge('INSPECTS', id, t) for t in q.asset_ids], None
        if isinstance(q, (TransitionInspection, ReportInspection)):
            ins = r.node(q.inspection_id, 'Inspection')
            if ins.content_hash != q.expected_hash:
                raise PreconditionFailed('Stale inspection revision')
            source, assets = self.inspection_source(r, ins.id)
            if actor.role == 'DEPARTMENT_LEAD' and actor.department_id != source['department_id']:
                raise PreconditionFailed('Inspection outside actor department')
            if isinstance(q, TransitionInspection):
                state = transition('Inspection', ins.properties['status'], q.status)
                props = {**ins.properties, 'status': state, 'updated_at': now}
                if q.status == 'SCHEDULED':
                    if not q.scheduled_at or timestamp(q.scheduled_at) < timestamp(ins.properties['requested_at']):
                        raise PreconditionFailed('Schedule must follow request')
                    props['scheduled_at'] = q.scheduled_at
                elif q.scheduled_at is not None:
                    raise PreconditionFailed('Schedule time belongs to scheduling transition')
                if q.status == 'IN_PROGRESS' and timestamp(ins.properties['scheduled_at']) > timestamp(now):
                    raise PreconditionFailed('Inspection cannot start before schedule')
                return ins.id, [], [n('Inspection', props)], [], None
            transition('Inspection', ins.properties['status'], 'COMPLETED')
            if q.review and q.review.reviewer_id == actor.id:
                raise PreconditionFailed('Independent reviewer required')
            observed = max((ob.observed_at for ob in q.observations), key=timestamp)
            for ob in q.observations:
                if ob.asset_id not in assets or timestamp(ob.observed_at) < max(timestamp(ins.properties['scheduled_at']), timestamp(ins.properties['updated_at'])) or timestamp(ob.observed_at) > timestamp(now):
                    raise PreconditionFailed('Observation asset/inspection chronology invalid')
            duplicates = r.query("MATCH (e:Evidence {evidence_type:'INSPECTION_REPORT'}) WHERE e.source_record_id=$record RETURN e.id LIMIT 1", {'record': q.source_id + ':' + q.record_id})
            if duplicates:
                raise Conflict('Inspection source record already represented; cannot fabricate independent copies')
            if q.attribution:
                for incident_id in q.attribution.incident_ids:
                    r.node(incident_id, 'Incident')
                bound = {e.target for e in r.edges('INVESTIGATES', source=source['investigation_id'])}
                if not set(q.attribution.incident_ids) <= bound:
                    raise PreconditionFailed('Explicit report attribution outside inspection investigation')
                if q.attribution.mode == 'RETROSPECTIVE' and not q.review:
                    raise PreconditionFailed('Retrospective report requires independent review')
            eid = stable('EV-REPORT', q.source_kind, q.source_id, q.record_id)
            fids = [stable('FINDING', eid, i) for i in range(len(q.observations))]
            report = Report(format_version=2 if q.attribution else 1, attribution=q.attribution, inspection_id=ins.id, inspector_id=actor.id, department_id=source['department_id'],
                source_id=q.source_id, record_id=q.record_id, source_kind=q.source_kind, observed_at=observed,
                recorded_at=now, observations=q.observations, finding_ids=fids, review=q.review)
            raw = report.model_dump_json()
            ev = n('Evidence', {**common(eid, now), 'evidence_type': 'INSPECTION_REPORT', 'summary': raw,
                'reliability': 'VERIFIED' if q.review else 'UNVERIFIED', 'basis': 'OBSERVED', 'observed_at': observed,
                'recorded_at': now, 'source_kind': q.source_kind, 'source_record_id': q.source_id + ':' + q.record_id,
                'content_hash': digest(json.loads(raw)), 'review_status': 'REVIEWED' if q.review else 'UNREVIEWED'})
            findings = [n('Finding', {**common(id, now), 'finding_type': ob.code, 'statement': ob.statement,
                'verification_status': 'VERIFIED' if q.review and ob.result == 'OBSERVED' else 'UNVERIFIED',
                **({'verified_at': now} if q.review and ob.result == 'OBSERVED' else {})}) for id, ob in zip(fids, q.observations, strict=True)]
            updated = n('Inspection', {**ins.properties, 'status': 'COMPLETED', 'completed_at': observed, 'updated_at': now})
            return eid, [ev, *findings], [updated], [edge('PRODUCED', ins.id, eid), *[edge('ESTABLISHES', eid, id) for id in fids]], None
        if isinstance(q, Assess):
            if timestamp(q.as_of) > timestamp(now):
                raise PreconditionFailed('Assessment cutoff after service clock')
            h = r.node(q.hypothesis_id, 'Hypothesis')
            if h.content_hash != q.expected_hash:
                raise PreconditionFailed('Stale hypothesis revision')
            cutoff = Reader(self.repo, q.as_of)
            _, definition = cutoff.definition(h.id)
            result = self.evaluate(q, definition, h, cutoff, now, revision)
            id = result.id
            props = common(id, now)
            props.pop('updated_at')
            assessment = n('HypothesisAssessment', {**props, 'assessment': result.assessment, 'assessed_at': now, 'rationale': result.model_dump_json()})
            edges = [edge('HAS_ASSESSMENT', h.id, id)]
            edges += [link(kind, id, eid, eid, now) for kind, ids in [('SUPPORTED_BY', result.supporting_evidence_ids), ('CONTRADICTED_BY', result.contradicting_evidence_ids)] for eid in ids]
            updated = n('Hypothesis', {**h.properties, 'status': result.state_transitions[-1], 'updated_at': now})
            return id, [assessment], [updated], edges, result
        raise PreconditionFailed('Unapproved B09 operation')

    def evaluate(self, q, definition, h, r, now, revision):
        incidents = [r.node(id, 'Incident') for id in definition.incident_ids]
        issue = incidents[0].properties['issue_type']
        rule = POLICIES[issue].get(definition.cause_code)
        history = Reader(self.repo, now).histories(h.id)
        refs, classification, gaps, complete = classify_evidence(self.repo, r, q, definition, incidents, rule, history)
        support = classification.reviewed_support_ids
        contradiction = classification.reviewed_contradiction_ids
        excluded = classification.excluded_evidence_ids
        paths, pathids, truncated, topology_ok = [], [], False, True
        if rule and rule['requires_topology'] and not definition.topology:
            topology_ok = False
            gaps.append('This domain cause requires explicit verified topology; reported impact alone is insufficient')
        if definition.topology:
            result = r.topology(definition.topology)
            paths = [PathRecord(**p.model_dump(exclude={'id'}),) for p in result.paths if p.node_ids[-1] == definition.topology.target_id]
            pathids = [p.id for p in result.paths if p.node_ids[-1] == definition.topology.target_id]
            paths = [p.model_copy(update={'context': {**p.context, 'path_id': id}}) for p, id in zip(paths, pathids, strict=True)]
            truncated = result.truncated
            topology_ok = bool(paths) and not truncated
            gaps.extend(result.gaps)
            if not topology_ok:
                gaps.append('Required verified-only topology path unavailable within bounded search; candidate/proximity insufficient')
            for id in sorted({ev for p in paths for ev in p.evidence_ids} - {ref.id for ref in refs}):
                refs.append(r.evidence(id, context_only=True))
                classification = add_topology_context(classification, id)
        if len(refs) > 20:
            raise PreconditionFailed('B09 total source evidence references exceed20 including topology')
        sufficient = bool(rule and complete and topology_ok)
        label = classify_reviewed(reviewed_support=bool(support),
            unreviewed_support=bool(classification.unreviewed_support_ids),
            reviewed_contradiction=bool(contradiction),
            unreviewed_contradiction=bool(classification.unreviewed_contradiction_ids), sufficient=sufficient)
        if (support or classification.unreviewed_support_ids) and (contradiction or classification.unreviewed_contradiction_ids):
            gaps.append('Conflicting evidence retained; no automatic source arbitration')
        if not support and not contradiction:
            gaps.append('Reviewed discriminating inspection evidence missing or insufficient; no completed inspection invented')
        final = {'POSSIBLE': 'UNDER_REVIEW', 'SUPPORTED': 'SUPPORTED', 'CONTRADICTED': 'REJECTED', 'VERIFIED': 'VERIFIED', 'INCONCLUSIVE': 'INCONCLUSIVE'}[label]
        state = h.properties['status']
        sequence = [state]
        if state != 'UNDER_REVIEW':
            sequence.append(transition('Hypothesis', state, 'UNDER_REVIEW'))
        if final != 'UNDER_REVIEW':
            sequence.append(transition('Hypothesis', 'UNDER_REVIEW', final))
        id = stable('ASSESS', q.hypothesis_id, q.request_id)
        return Assessment(format_version=2, rule_version=3 if __import__('app.services.service_evidence',fromlist=['policy_required']).policy_required(self.repo,definition.investigation_id) and issue=='WASTE_ACCUMULATION' and definition.cause_code in {'MISSED_PICKUP','ILLEGAL_DUMPING'} else 2, classification=classification, id=id, hypothesis_id=h.id, previous_assessment_id=history[-1].id if history else None,
            assessment=label, cause_code=definition.cause_code, mechanism=definition.mechanism,
            confirming_codes=definition.confirming_codes, falsifying_codes=definition.falsifying_codes,
            supporting_evidence_ids=support, contradicting_evidence_ids=contradiction, evidence_references=refs,
            excluded_evidence_ids=excluded, missing_evidence=list(dict.fromkeys(gaps)), graph=self.repo.graph.name,
            source_graph_revision=revision, graph_revision=revision+1, as_of=q.as_of, assessed_at=now,
            paths=paths, path_ids=pathids, truncated=truncated, state_transitions=sequence,
            reservations=['Observed findings and connectivity are distinct from causal criteria.',
                'Verification uses versioned reviewed synthetic-domain criteria with per-occurrence coverage; rule3 service/ordering requires bound dated execution. Not prediction or resolution verification.',
                'Attribution-based independence is a conservative demo rule, not proof against colluding sources.',
                'Current versions only; future-updated evidence excluded, historical source versions not reconstructed.'])

    def history(self, hypothesis_id, as_of):
        before = GraphQueries(self.repo)._state()
        reader = Reader(self.repo, as_of)
        reader.definition(hypothesis_id)
        result = reader.histories(hypothesis_id)
        if before != GraphQueries(self.repo)._state():
            raise PreconditionFailed('Graph changed during B09 history retrieval')
        return result

    def context(self, incident_id, as_of, *, exploratory=False):
        return Reader(self.repo, as_of).cases(incident_id, exploratory=exploratory)

    def inspection(self, inspection_id, as_of):
        before = GraphQueries(self.repo)._state()
        reader = Reader(self.repo, as_of)
        value = self.repo._node_optional(inspection_id)
        if value is None or not reader.visible(value.properties):
            result = InspectionView(inspection_id=inspection_id, availability='UNAVAILABLE', state=None,
                graph=self.repo.graph.name, graph_revision=before, as_of=as_of,
                gaps=['Inspection unavailable at cutoff; no current or historical completion inferred'])
        else:
            value = reader.node(inspection_id, 'Inspection')
            reports = [reader.evidence(e.target) for e in reader.edges('PRODUCED', source=inspection_id)]
            gaps = []
            if not reports:
                gaps.append('No actual inspection report available; request/pending state is not conducted inspection')
            if any(not ref.report or not ref.report.review for ref in reports):
                gaps.append('Unreviewed/context-only report cannot verify a cause')
            result = InspectionView(inspection_id=inspection_id, availability='AVAILABLE', state=value.properties['status'],
                graph=self.repo.graph.name, graph_revision=before, as_of=as_of,
                requested_at=value.properties['requested_at'], scheduled_at=value.properties.get('scheduled_at'),
                completed_at=value.properties.get('completed_at'), report_evidence_ids=[ref.id for ref in reports],
                finding_ids=[id for ref in reports if ref.report for id in ref.report.finding_ids], gaps=gaps)
        if before != GraphQueries(self.repo)._state():
            raise PreconditionFailed('Graph changed during inspection read')
        return result

    def incomplete(self):
        rows = self.repo._read("MATCH (e:Evidence {evidence_type:'B09_OPERATION'}) RETURN e.id,e.summary LIMIT 101")
        if len(rows) > 100:
            raise PreconditionFailed('B09 reconciliation journal cap exceeded')
        return [id for id, raw in rows if Journal.model_validate_json(raw).state == 'PREPARED']
