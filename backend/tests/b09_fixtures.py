"""Authored B09 observations and actual B08 intake copies; no evaluator fixtures."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.graph.targets import new_test_graph_name
from app.graph.analysis.counterfactual import capture
from app.services.complaints import ComplaintService
from app.services.evidence import EvidenceService, Actor
from app.services.evidence.policies import POLICIES
from tests.b08_fixtures import populate, payload, CLOCK
from tests.schema_examples import common

ANALYST = Actor(id='synthetic-analyst', role='ANALYST')


class Clock:
    def __init__(self):
        self.value = datetime.fromisoformat(CLOCK.replace('Z', '+00:00'))

    def __call__(self):
        return self.value.isoformat(timespec='microseconds').replace('+00:00', 'Z')

    def advance(self, seconds=1):
        self.value += timedelta(seconds=seconds)
        return self()


@dataclass
class Fixture:
    repo: GraphRepository
    clock: Clock
    receipts: dict
    source_graph: str
    source_fingerprint: dict

    @property
    def service(self):
        return EvidenceService(self.repo, clock=self.clock)


def create(db, *, retain_source=False):
    source_name, name = new_test_graph_name(8), new_test_graph_name(9)
    try:
        MigrationRunner(db, source_name).apply()
        source = GraphRepository(db, source_name, lease_seconds=30)
        populate(source)
        source.create_node('Department', {**common('DEP'), 'name': 'Synthetic inspection department', 'department_type': 'ENGINEERING'})
        receipts = {issue: ComplaintService(source, clock=lambda: CLOCK).intake(payload(issue, ref='B09-source-' + issue))
                    for issue in POLICIES}
        snapshot = capture(source)
        MigrationRunner(db, name).apply()
        repo = GraphRepository(db, name, lease_seconds=30)
        for n in sorted(snapshot.nodes, key=lambda n: (n.kind != 'Evidence', n.id)):
            repo.create_node(n.kind, n.properties)
        for e in snapshot.edges:
            repo.create_relationship(e.kind, e.source, e.target, e.properties)
        assert capture(repo).records == snapshot.records
        assert capture(source).fingerprint == snapshot.fingerprint
        fixture = Fixture(repo, Clock(), receipts, source_name, snapshot.fingerprint)
        if not retain_source:
            db.select_graph(source_name).delete()  # Only this newly owned temporary source.
        return fixture
    except BaseException:
        for owned in [source_name, name]:
            if owned in db.list_graphs():
                db.select_graph(owned).delete()
        raise


def open_case(f, issue='WATERLOGGING', ref='open'):
    receipt = f.receipts[issue]
    return f.service.execute({'operation': 'open', 'request_id': ref, 'incident_ids': [receipt.incident_id],
                              'cluster_id': receipt.cluster_id}, ANALYST).entity_id


def propose(f, inv, issue='WATERLOGGING', cause='BLOCKAGE', ref='hypothesis', **changes):
    rule = POLICIES[issue][cause]
    return f.service.execute({'operation': 'propose', 'request_id': ref, 'investigation_id': inv,
        'incident_ids': [f.receipts[issue].incident_id], 'asset_ids': [{'WATERLOGGING': 'D1', 'ROAD_DAMAGE': 'R1', 'WASTE_ACCUMULATION': 'W1'}[issue]],
        'cause_code': cause, 'statement': 'Synthetic competing explanation: ' + cause,
        'mechanism': 'Authored physical/operational mechanism under inspection, not asserted truth',
        'confirming_codes': rule['confirming'], 'falsifying_codes': rule['falsifying'], **changes}, ANALYST).entity_id


def request(f, inv, ref='request', assets=None):
    return f.service.execute({'operation': 'request_inspection', 'request_id': ref, 'investigation_id': inv,
        'asset_ids': assets or ['D1'], 'department_id': 'DEP', 'inspection_type': 'SYNTHETIC_FIELD_TEST'}, ANALYST).entity_id


def advance_inspection(f, id, state, ref=None, **changes):
    f.clock.advance()
    actor = Actor(id='synthetic-inspector-A', role='DEPARTMENT_LEAD', department_id='DEP')
    return f.service.execute({'operation': 'transition_inspection', 'request_id': ref or id + '-' + state + '-' + f.clock(),
        'inspection_id': id, 'expected_hash': f.repo.get_node(id).content_hash, 'status': state,
        **({'scheduled_at': f.clock()} if state == 'SCHEDULED' else {}), **changes}, actor)


def report(f, inv, ref='first', codes=None, assets=None, inspector=None, source=None, reviewed=True, result='OBSERVED'):
    assets = assets or ['D1']
    id = request(f, inv, 'request-' + ref, assets)
    for state in ['REQUESTED', 'SCHEDULED', 'IN_PROGRESS']:
        advance_inspection(f, id, state)
    f.clock.advance()
    observations = [{'asset_id': assets[0], 'code': code, 'statement': 'Authored synthetic field observation ' + code,
                     'method': 'DIRECT_SYNTHETIC_FIELD_TEST', 'observed_at': f.clock(), 'result': result}
                    for code in (codes or POLICIES['WATERLOGGING']['BLOCKAGE']['confirming'])]
    actor = Actor(id=inspector or 'synthetic-inspector-' + ref, role='DEPARTMENT_LEAD', department_id='DEP')
    payload = {'operation': 'report_inspection', 'request_id': 'report-' + ref, 'inspection_id': id,
        'expected_hash': f.repo.get_node(id).content_hash, 'source_id': source or 'independent-source-' + ref,
        'record_id': 'field-record-' + ref, 'observations': observations}
    if reviewed:
        payload['review'] = {'reviewer_id': 'synthetic-reviewer', 'role': 'ANALYST', 'reviewed': True, 'reason': 'Reviewed authored methods and attributed observations'}
    return f.service.execute(payload, actor)


def assess(f, hypothesis_id, evidence_ids=None, ref='assessment', as_of=None, **changes):
    f.clock.advance()
    return f.service.execute({'operation': 'assess', 'request_id': ref, 'hypothesis_id': hypothesis_id,
        'expected_hash': f.repo.get_node(hypothesis_id).content_hash, 'evidence_ids': evidence_ids or [],
        'as_of': as_of or f.clock(), **changes}, ANALYST)
