"""Bounded canonical reads; reuse B03 timing and B05 graph algorithms."""
import json
import time
from app.graph.models import PathRecord, digest
from app.graph.queries import GraphQueries
from app.graph.repository import PreconditionFailed
from app.graph.schema import timestamp
from app.graph.analysis.engine import GraphAnalysis
from app.graph.analysis.models import AnalysisRequest, CaseRequest
from .models import Journal, Report, EvidenceReference, Propose

EDGE_KINDS = {'PART_OF', 'AFFECTS', 'INVESTIGATES', 'PROPOSES', 'CONCERNS', 'EXPLAINS',
              'HAS_ASSESSMENT', 'INSPECTS', 'PRODUCED', 'ESTABLISHES', 'SUPPORTED_BY', 'CONTRADICTED_BY'}


class Reader:
    def __init__(self, repo, as_of):
        self.repo, self.as_of = repo, as_of
        self.cache = {}
        self.queries = 0
        self.started = time.perf_counter()

    def query(self, query, params=None):
        self.queries += 1
        if self.queries > 300 or time.perf_counter() - self.started > 8:
            raise PreconditionFailed('B09 read budget exceeded')
        return self.repo._read(query, {'scope': self.repo.registry.scope, **(params or {})})

    def visible(self, props, *, definition=False):
        at = timestamp(self.as_of)
        fields = ['created_at', 'observed_at', 'recorded_at', 'requested_at', 'completed_at', 'assessed_at', 'started_at']
        if not definition:
            fields.append('updated_at')
        return (all(timestamp(props[k]) <= at for k in fields if k in props)
                and ('valid_from' not in props or timestamp(props['valid_from']) <= at)
                and ('valid_to' not in props or at < timestamp(props['valid_to'])))

    def node(self, id, kind=None, *, definition=False):
        if id not in self.cache:
            rows = self.query('MATCH (n:CivicEntity {id:$id,municipality_id:$scope}) RETURN labels(n),properties(n) LIMIT 2', {'id': id})
            if len(rows) != 1:
                raise PreconditionFailed('Unique B09 reference unavailable')
            self.cache[id] = self.repo.decode_node(*rows[0])
        n = self.cache[id]
        if (kind and kind not in n.labels) or not self.visible(n.properties, definition=definition):
            raise PreconditionFailed('B09 reference type/time unavailable')
        return n

    def edges(self, kind, source=None, target=None):
        if kind not in EDGE_KINDS:
            raise PreconditionFailed('Unapproved B09 read family')
        rows = self.query(f'MATCH (s:CivicEntity)-[e:{kind}]->(t:CivicEntity) WHERE e.municipality_id=$scope AND ($source IS NULL OR s.id=$source) AND ($target IS NULL OR t.id=$target) RETURN type(e),properties(e),labels(s),properties(s),labels(t),properties(t) LIMIT 101',
                          {'source': source, 'target': target})
        if len(rows) > 100:
            raise PreconditionFailed('B09 relationship scan exceeds100; incomplete evidence cannot verify')
        result = []
        for row in rows:
            e = self.repo._decode_edge_row(row)
            if not self.visible(e.properties):
                continue
            ev = e.properties.get('source_evidence_id')
            if ev:
                self.node(ev, 'Evidence')
            result.append(e)
        return result

    def definition(self, hypothesis_id):
        h = self.node(hypothesis_id, 'Hypothesis', definition=True)
        proposals = self.edges('PROPOSES', target=h.id)
        if len(proposals) != 1:
            raise PreconditionFailed('Unique proposal source required')
        journal = self.journal(proposals[0].properties['source_evidence_id'])
        if journal.state != 'COMMITTED' or journal.command['operation'] != 'propose' or journal.receipt.entity_id != h.id:
            raise PreconditionFailed('Proposal journal binding mismatch')
        q = Propose.model_validate_json(json.dumps(journal.command))
        if q.investigation_id != proposals[0].source or q.cause_code != h.properties['cause_code'] or q.statement != h.properties['statement']:
            raise PreconditionFailed('Hypothesis definition changed outside domain service')
        return h, q

    def journal(self, id):
        ev = self.node(id, 'Evidence')
        j = Journal.model_validate_json(ev.properties['summary'])
        if (ev.properties['evidence_type'] != 'B09_OPERATION' or ev.properties['reliability'] != 'UNVERIFIED'
                or digest({'actor': j.actor.model_dump(mode='json'), 'command': j.command}) != j.request_hash
                or j.state != 'COMMITTED' or j.receipt.journal_id != id or j.receipt.graph != self.repo.graph.name):
            raise PreconditionFailed('B09 journal hash/scope/receipt mismatch')
        return j

    def evidence(self, id, *, context_only=False):
        ev = self.node(id, 'Evidence')
        p = ev.properties
        if not p.get('source_record_id'):
            raise PreconditionFailed('Evidence lacks attributed source record')
        ref = EvidenceReference(id=id, content_hash=ev.content_hash, source_kind=p['source_kind'],
                                source_record_id=p['source_record_id'], reliability=p['reliability'],
                                observed_at=p.get('observed_at'), recorded_at=p['recorded_at'], basis=p.get('basis'))
        if context_only or p['evidence_type'] != 'INSPECTION_REPORT' or p.get('basis') != 'OBSERVED':
            return ref
        report = Report.model_validate_json(p['summary'])
        if (digest(json.loads(p['summary'])) != p.get('content_hash')
                or report.source_kind != p['source_kind']
                or p['source_record_id'] != report.source_id + ':' + report.record_id
                or p.get('observed_at') != report.observed_at or p['recorded_at'] != report.recorded_at
                or len(report.finding_ids) != len(report.observations)):
            raise PreconditionFailed('Inspection report provenance/hash mismatch')
        ins = self.node(report.inspection_id, 'Inspection')
        if ins.properties['status'] != 'COMPLETED' or ins.properties.get('completed_at') != report.observed_at:
            raise PreconditionFailed('Actual completed inspection required')
        produced = [e for e in self.edges('PRODUCED', source=ins.id) if e.target == id]
        if len(produced) != 1:
            raise PreconditionFailed('Report is not produced by the declared inspection')
        journal = self.journal(produced[0].properties['source_evidence_id'])
        original = journal.command
        if (original['operation'] != 'report_inspection' or journal.receipt.entity_id != id
                or journal.actor.id != report.inspector_id or original['inspection_id'] != ins.id
                or original['source_id'] != report.source_id or original['record_id'] != report.record_id
                or original['source_kind'] != report.source_kind
                or original['observations'] != [ob.model_dump(mode='json') for ob in report.observations]
                or original.get('attribution') != (report.attribution.model_dump(mode='json') if report.attribution else None)
                or original['review'] != (report.review.model_dump(mode='json') if report.review else None)):
            raise PreconditionFailed('Report disagrees with original attributed operation')
        assets = {e.target for e in self.edges('INSPECTS', source=ins.id)}
        established = {e.target for e in self.edges('ESTABLISHES', source=id)}
        if established != set(report.finding_ids):
            raise PreconditionFailed('Report finding relationships mismatch')
        hashes = {}
        for fid, ob in zip(report.finding_ids, report.observations, strict=True):
            finding = self.node(fid, 'Finding')
            expected = 'VERIFIED' if report.review and ob.result == 'OBSERVED' else 'UNVERIFIED'
            if ob.asset_id not in assets or finding.properties['statement'] != ob.statement or finding.properties['finding_type'] != ob.code or finding.properties['verification_status'] != expected:
                raise PreconditionFailed('Attributable finding/asset mismatch')
            if timestamp(ob.observed_at) > timestamp(report.observed_at) or timestamp(ob.observed_at) < timestamp(ins.properties['requested_at']):
                raise PreconditionFailed('Inspection observation chronology mismatch')
            hashes[fid] = finding.content_hash
        if p['reliability'] != ('VERIFIED' if report.review else 'UNVERIFIED'):
            raise PreconditionFailed('Review and evidence reliability mismatch')
        return ref.model_copy(update={'report': report, 'finding_hashes': hashes})

    def topology(self, topology, *, exploratory=False):
        return GraphAnalysis(self.repo).run(AnalysisRequest(operation=topology.operation,
            ids=(topology.source_id,), as_of=self.as_of, max_hops=topology.max_hops,
            include_candidates=exploratory, limit=100))

    def histories(self, hypothesis_id):
        key = GraphQueries._time_key
        rows = self.query('MATCH (h:Hypothesis {id:$id})-[:HAS_ASSESSMENT]->(a:HypothesisAssessment) WHERE a.municipality_id=$scope AND '
            + key('a.created_at') + '<=$at AND ' + key('a.assessed_at')
            + '<=$at RETURN a.id,a.rationale ORDER BY ' + key('a.assessed_at') + ',a.id LIMIT 101',
            {'id': hypothesis_id, 'at': timestamp(self.as_of).strftime('%Y-%m-%dT%H:%M:%S.%f')})
        if len(rows) > 100:
            raise PreconditionFailed('B09 assessment history exceeds100; no hidden latest record')
        from .models import Assessment
        result = []
        for id, raw in rows:
            value = Assessment.model_validate_json(raw)
            n = self.node(id, 'HypothesisAssessment')
            if value.id != id or value.hypothesis_id != hypothesis_id or value.assessment != n.properties['assessment']:
                raise PreconditionFailed('Assessment history binding mismatch')
            result.append(value)
        return sorted(result, key=lambda value: (timestamp(value.assessed_at), value.graph_revision, value.id))

    def cases(self, incident_id, *, exploratory=False):
        return GraphAnalysis(self.repo).cases(CaseRequest(seed_incident_id=incident_id, as_of=self.as_of,
                                                        include_candidates=exploratory, limit=40))
