"""Real FalkorDB B09 state/path evidence; failure wrappers never fake success."""
import asyncio
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from pathlib import Path
import pytest
from redis.exceptions import ConnectionError
from app.graph.repository import GraphRepository, Conflict, PreconditionFailed, OutcomeUnknown
from app.graph.models import QueryRequest
from app.graph.queries import GraphQueries
from app.graph.analysis.counterfactual import capture
from app.graph.analysis.evaluation import CITY_GRAPH, verify_city
from app.services.evidence import EvidenceService, Actor
from app.services.evidence.models import Journal, Assessment
from app.services.evidence.reader import Reader
from app.services.evidence.policies import POLICIES
from tests.b09_fixtures import create, open_case, propose, request, advance_inspection, report, assess, ANALYST
from tests.schema_examples import edge

pytestmark = pytest.mark.integration
PROOF = Path('docs/evidence/B09-runtime-proof.json')


@pytest.fixture
def f(db):
    fixture = create(db)
    try:
        yield fixture
    finally:
        db.select_graph(fixture.repo.graph.name).delete()  # Only this test's newly owned B09 graph.


def save(name, f, **values):
    old = json.loads(PROOF.read_text()) if PROOF.exists() else {'evidence_class': 'REAL_FALKORDB_AUTHORED_SYNTHETIC_FIXTURES', 'examples': {}}
    old['examples'][name] = {'graph': f.repo.graph.name, 'source_B08_graph': f.source_graph,
        'source_B08_fingerprint': f.source_fingerprint, 'copied_actual_B08_ids': {k: {'incident_id': v.incident_id, 'cluster_id': v.cluster_id} for k, v in f.receipts.items()},
        'values': {k: v.model_dump(mode='json') if hasattr(v, 'model_dump') else v for k, v in values.items()},
        'actual_counts': f.repo._read('MATCH (n:CivicEntity) RETURN count(n)')[0][0]}
    PROOF.write_text(json.dumps(old, indent=2) + '\n')


def test_two_competing_hypotheses_supported_and_contradicted(f):
    inv = open_case(f)
    blockage = propose(f, inv)
    capacity = propose(f, inv, cause='CAPACITY_DEFICIT', ref='capacity')
    first = report(f, inv, codes=['DRAIN_CLEAR', 'CAPACITY_TEST_EXCEEDED'])
    a = assess(f, blockage, [first.entity_id], ref='blockage')
    b = assess(f, capacity, [first.entity_id], ref='assess-capacity')
    assert a.assessment.assessment == 'CONTRADICTED'
    assert b.assessment.assessment == 'SUPPORTED'
    assert f.repo.get_node(blockage).properties['status'] == 'REJECTED'
    assert {e.target for e in Reader(f.repo, f.clock()).edges('PROPOSES', source=inv)} == {blockage, capacity}
    assert f.repo._read('MATCH (h:Hypothesis)-[:HAS_ASSESSMENT]->(a:HypothesisAssessment)-[:CONTRADICTED_BY]->(e:Evidence) RETURN a.id,e.id') == [[a.entity_id, first.entity_id]]
    save('competing', f, contradicted=a, supported=b)


def test_missing_inspection_is_inconclusive_and_request_never_fabricates_completion(f):
    inv = open_case(f)
    h = propose(f, inv)
    ins = request(f, inv)
    before = capture(f.repo)
    assert f.repo.get_node(ins).properties['status'] == 'PROPOSED'
    assert f.repo._read('MATCH (:Inspection)-[:PRODUCED]->(e) RETURN count(e)') == [[0]]
    a = assess(f, h)
    assert a.assessment.assessment == 'INCONCLUSIVE'
    assert f.repo.get_node(ins).properties['status'] == 'PROPOSED'
    assert not any(n.kind == 'Finding' for n in capture(f.repo).nodes)
    assert set(before.records) <= capture(f.repo).records.keys()
    save('missing-inspection', f, assessment=a)


@pytest.mark.parametrize('issue,cause,asset', [('WATERLOGGING', 'BLOCKAGE', 'D1'), ('ROAD_DAMAGE', 'SUBGRADE_FAILURE', 'R1'), ('WASTE_ACCUMULATION', 'MISSED_PICKUP', 'W1')])
def test_real_independent_reviewed_findings_verify_each_issue(f, issue, cause, asset):
    inv = open_case(f, issue)
    h = propose(f, inv, issue, cause)
    codes = POLICIES[issue][cause]['confirming']
    a = report(f, inv, 'first', codes, [asset])
    b = report(f, inv, 'second', codes, [asset])
    result = assess(f, h, [a.entity_id, b.entity_id])
    assert result.assessment.assessment == 'VERIFIED'
    assert f.repo.get_node(h).properties['status'] == 'VERIFIED'
    assert len(result.assessment.evidence_references) == 2
    assert all(ref.finding_hashes and ref.report.review for ref in result.assessment.evidence_references)
    assert f.repo._read('MATCH (:Inspection {status:$status})-[:PRODUCED]->(:Evidence)-[:ESTABLISHES]->(f:Finding) RETURN count(f)', {'status': 'COMPLETED'}) == [[4]]
    save(issue, f, verified=result)


def test_second_inspection_corrects_assessment_and_preserves_immutable_history(f):
    inv = open_case(f)
    h = propose(f, inv)
    first = report(f, inv)
    second = report(f, inv, 'second')
    original = assess(f, h, [first.entity_id, second.entity_id], ref='original')
    original_hash = f.repo.get_node(original.entity_id).content_hash
    contradiction = report(f, inv, 'later-clear', ['DRAIN_CLEAR'])
    revised = assess(f, h, [first.entity_id, second.entity_id, contradiction.entity_id], ref='revision')
    assert original.assessment.assessment == 'VERIFIED' and revised.assessment.assessment == 'INCONCLUSIVE'
    assert revised.assessment.previous_assessment_id == original.entity_id
    assert f.repo.get_node(original.entity_id).content_hash == original_hash
    with pytest.raises(PreconditionFailed):
        f.repo.update_node(original.entity_id, {'assessment': 'CONTRADICTED'}, expected_hash=original_hash)
    history = f.service.history(h, f.clock())
    assert [a.assessment for a in history] == ['VERIFIED', 'INCONCLUSIVE']
    assert history[0].supporting_evidence_ids == [first.entity_id, second.entity_id] or set(history[0].supporting_evidence_ids) == {first.entity_id, second.entity_id}
    paths = GraphQueries(f.repo).run(QueryRequest(template='hypothesis_evidence', id=h, as_of=f.clock()))
    assert {original.entity_id, revised.entity_id} <= {n.id for n in paths.nodes}
    save('revision', f, original=original, revised=revised, history=[a.model_dump(mode='json') for a in history], graph_paths=paths)


@pytest.mark.parametrize('inspector,source,reviewed,result', [('same', None, True, 'OBSERVED'), (None, 'same-source', True, 'OBSERVED'), (None, None, False, 'OBSERVED'), (None, None, True, 'UNKNOWN')])
def test_corroboration_cannot_be_copied_or_unreviewed_or_unknown(f, inspector, source, reviewed, result):
    inv = open_case(f)
    h = propose(f, inv)
    a = report(f, inv, 'first', inspector=inspector, source=source, reviewed=reviewed, result=result)
    b = report(f, inv, 'second', inspector=inspector, source=source, reviewed=reviewed, result=result)
    r = assess(f, h, [a.entity_id, b.entity_id])
    assert r.assessment.assessment != 'VERIFIED'
    assert r.assessment.missing_evidence


def test_future_evidence_does_not_influence_prior_cutoff(f):
    inv = open_case(f)
    h = propose(f, inv)
    first = report(f, inv)
    cutoff = f.clock()
    second = report(f, inv, 'future')
    r = assess(f, h, [first.entity_id, second.entity_id], as_of=cutoff)
    assert r.assessment.assessment == 'SUPPORTED'
    assert r.assessment.excluded_evidence_ids == [second.entity_id]
    assert r.assessment.supporting_evidence_ids == [first.entity_id]
    save('temporal-cutoff', f, assessment=r)


@pytest.mark.parametrize('status', ['CANDIDATE', 'VERIFIED'])
def test_topology_candidate_boundary_and_actual_path_provenance(f, status):
    inv = open_case(f, 'ROAD_DAMAGE')
    # Physical link authored through unchanged B03 guard with dated source proof.
    f.repo.create_relationship('UNDERLIES', 'P1', 'R1', {**edge('PHYSICAL'), 'association_status': status, 'source_evidence_id': 'EV', 'valid_from': '2026-10-17T00:00:00Z'})
    h = propose(f, inv, 'ROAD_DAMAGE', 'UTILITY_LEAK', asset_ids=['P1'], topology={'source_id': 'P1', 'target_id': 'R1', 'operation': 'dependencies', 'max_hops': 4})
    codes = POLICIES['ROAD_DAMAGE']['UTILITY_LEAK']['confirming']
    a = report(f, inv, 'first', codes, ['P1'])
    b = report(f, inv, 'second', codes, ['P1'])
    r = assess(f, h, [a.entity_id, b.entity_id])
    assert r.assessment.assessment == ('VERIFIED' if status == 'VERIFIED' else 'SUPPORTED')
    if status == 'VERIFIED':
        assert r.assessment.path_ids and any('PHYSICAL' in p.edge_ids for p in r.assessment.paths)
        assert 'EV' in {ref.id for ref in r.assessment.evidence_references}
    else:
        assert not r.assessment.paths and any('candidate/proximity' in g for g in r.assessment.missing_evidence)
    save('topology-' + status, f, assessment=r)


def test_verified_link_uses_actual_dated_inspection_report_and_topology_change_revises(f):
    inv = open_case(f)
    direct = propose(f, inv)
    # D2 is first explicitly affected by a real B08 source? D1 remains incident asset;
    # inspect D1 and use observed report to attribute D2 -> D1 physical connection.
    proof = report(f, inv, 'physical-link', ['D2_TO_D1_FLOW_TRACED'])
    f.clock.advance()
    f.repo.create_relationship('DRAINS_TO', 'D2', 'D1', {**edge('INSPECTED-LINK'), 'created_at': f.clock(), 'valid_from': f.clock(),
        'association_status': 'VERIFIED', 'source_evidence_id': proof.entity_id})
    h = propose(f, inv, ref='downstream', asset_ids=['D2'], topology={'source_id': 'D2', 'target_id': 'D1'})
    a = report(f, inv, 'first', assets=['D2'])
    b = report(f, inv, 'second', assets=['D2'])
    verified = assess(f, h, [a.entity_id, b.entity_id], ref='linked')
    assert verified.assessment.assessment == 'VERIFIED'
    assert proof.entity_id in {ev for p in verified.assessment.paths for ev in p.evidence_ids}
    edge_before = f.repo.get_relationship('INSPECTED-LINK')
    f.clock.advance()
    f.repo.update_relationship(edge_before.id, {'valid_to': f.clock()}, expected_hash=edge_before.content_hash)
    after = assess(f, h, [a.entity_id, b.entity_id], ref='after-link-end')
    assert after.assessment.assessment == 'SUPPORTED' and not after.assessment.paths
    assert f.repo.get_node(verified.entity_id).properties['assessment'] == 'VERIFIED'
    save('topology-revision', f, before=verified, after=after)


def test_nearby_unrelated_infrastructure_is_not_a_cause(f):
    inv = open_case(f)
    before = len(capture(f.repo).nodes)
    with pytest.raises(PreconditionFailed):
        propose(f, inv, asset_ids=['D2'])
    assert f.repo._read('MATCH (h:Hypothesis) RETURN count(h)') == [[0]]
    assert len(capture(f.repo).nodes) == before + 1  # Explicit PREPARED journal only; no partial hypothesis.


def test_inspection_machine_chronology_and_department_checks(f):
    inv = open_case(f)
    ins = request(f, inv)
    with pytest.raises(PreconditionFailed):
        advance_inspection(f, ins, 'IN_PROGRESS')
    advance_inspection(f, ins, 'REQUESTED')
    advance_inspection(f, ins, 'SCHEDULED', scheduled_at='2026-10-20T00:00:00Z')
    with pytest.raises(PreconditionFailed):
        advance_inspection(f, ins, 'IN_PROGRESS')
    wrong = Actor(id='wrong-dept', role='DEPARTMENT_LEAD', department_id='OTHER')
    with pytest.raises(PreconditionFailed):
        f.service.execute({'operation': 'transition_inspection', 'request_id': 'wrong', 'inspection_id': ins,
                          'expected_hash': f.repo.get_node(ins).content_hash, 'status': 'CANCELLED'}, wrong)
    assert f.repo.get_node(ins).properties['status'] == 'SCHEDULED'
    assert f.repo._read('MATCH (f:Finding) RETURN count(f)') == [[0]]


def test_idempotence_concurrent_equal_commands_and_payload_conflict(f):
    inv = open_case(f)
    h = propose(f, inv)
    q = {'operation': 'assess', 'request_id': 'same', 'hypothesis_id': h, 'expected_hash': f.repo.get_node(h).content_hash, 'as_of': f.clock()}
    barrier = Barrier(2)
    def run(_):
        barrier.wait()
        return f.service.execute(q, ANALYST)
    with ThreadPoolExecutor(2) as pool:
        values = list(pool.map(run, range(2)))
    assert len({v.entity_id for v in values}) == 1 and any(v.replayed for v in values)
    before = capture(f.repo)
    assert f.service.execute(q, ANALYST).replayed
    after = capture(f.repo)
    assert before.records == after.records and before.fingerprint['graph_revision'] == after.fingerprint['graph_revision']
    with pytest.raises(Conflict):
        f.service.execute({**q, 'as_of': '2026-10-18T11:00:00Z'}, ANALYST)
    assert f.repo._read('MATCH (a:HypothesisAssessment) RETURN count(a)') == [[1]]


def test_concurrent_stale_assessments_rejected_not_overwritten(f):
    inv = open_case(f)
    h = propose(f, inv)
    sha = f.repo.get_node(h).content_hash
    barrier = Barrier(2)
    def run(ref):
        barrier.wait()
        try:
            return f.service.execute({'operation': 'assess', 'request_id': ref, 'hypothesis_id': h, 'expected_hash': sha, 'as_of': f.clock()}, ANALYST)
        except PreconditionFailed:
            return None
    with ThreadPoolExecutor(2) as pool:
        values = list(pool.map(run, ['one', 'two']))
    assert sum(v is not None for v in values) == 1
    assert f.repo._read('MATCH (a:HypothesisAssessment) RETURN count(a)') == [[1]]


@pytest.mark.parametrize('committed', [False, True])
def test_real_lost_response_recovery_preserves_one_assessment(f, monkeypatch, committed):
    inv = open_case(f)
    h = propose(f, inv)
    q = {'operation': 'assess', 'request_id': 'uncertain', 'hypothesis_id': h, 'expected_hash': f.repo.get_node(h).content_hash, 'as_of': f.clock()}
    original, fired = f.repo.graph.query, False
    def fault(query, *args, **kw):
        nonlocal fired
        if 'SET j.summary=$summary' in query and not fired:
            fired = True
            if committed:
                original(query, *args, **kw)
            raise ConnectionError('Injected lost response around real B09 batch')
        return original(query, *args, **kw)
    monkeypatch.setattr(f.repo.graph, 'query', fault)
    with pytest.raises(OutcomeUnknown):
        f.service.execute(q, ANALYST)
    assert f.repo._read('MATCH (a:HypothesisAssessment) RETURN count(a)') == [[int(committed)]]
    monkeypatch.setattr(f.repo.graph, 'query', original)
    r = f.service.execute(q, ANALYST)
    assert f.repo._read('MATCH (a:HypothesisAssessment) RETURN count(a)') == [[1]]
    assert not f.service.incomplete()
    save('uncertain-' + str(committed), f, result=r)


def test_actual_constraint_failure_rolls_back_domain_and_recovers(f, monkeypatch):
    inv = open_case(f)
    h = propose(f, inv)
    original, fired = f.repo.graph.query, False
    def fault(query, *args, **kw):
        nonlocal fired
        if 'SET j.summary=$summary' in query and not fired:
            fired = True
            query = query.replace('SET j.summary=$summary', 'CREATE (:CivicEntity {id:$existing0}) SET j.summary=$summary')
        return original(query, *args, **kw)
    monkeypatch.setattr(f.repo.graph, 'query', fault)
    q = {'operation': 'assess', 'request_id': 'rollback', 'hypothesis_id': h, 'expected_hash': f.repo.get_node(h).content_hash, 'as_of': f.clock()}
    with pytest.raises(OutcomeUnknown):
        f.service.execute(q, ANALYST)
    assert f.repo._read('MATCH (a:HypothesisAssessment) RETURN count(a)') == [[0]]
    assert f.repo.get_node(h).properties['status'] == 'PROPOSED'
    monkeypatch.setattr(f.repo.graph, 'query', original)
    assert f.service.execute(q, ANALYST).assessment.assessment == 'INCONCLUSIVE'


def test_retained_city_readonly_context_and_mutation_denied(db):
    repo = GraphRepository(db, CITY_GRAPH)
    bundle = json.loads(Path('data/ingestion/city-v3.json').read_text())
    before = verify_city(repo, bundle)
    service = EvidenceService(repo)
    result = service.context('INC-FLOOD-02', '2026-10-19T00:00:00Z', exploratory=True)
    assert result.search_limited and result.include_candidates
    with pytest.raises(PreconditionFailed):
        service.execute({'operation': 'open', 'request_id': 'denied', 'incident_ids': ['INC-FLOOD-02'], 'cluster_id': 'ANY'}, ANALYST)
    assert verify_city(repo, bundle) == before


def test_role_and_direct_state_assessment_fields_denied(f):
    with pytest.raises(PreconditionFailed):
        f.service.execute({'operation': 'open', 'request_id': 'denied', 'incident_ids': [f.receipts['WATERLOGGING'].incident_id], 'cluster_id': f.receipts['WATERLOGGING'].cluster_id}, Actor(id='approver', role='APPROVER'))
    before = capture(f.repo).records
    with pytest.raises(ValueError):
        f.service.execute({'operation': 'assess', 'request_id': 'forged', 'hypothesis_id': 'H', 'expected_hash': 'a' * 64, 'as_of': f.clock(), 'assessment': 'VERIFIED'}, ANALYST)
    assert capture(f.repo).records == before


def test_omitted_known_contradiction_cannot_reverify_and_prior_sources_survive(f):
    inv = open_case(f)
    h = propose(f, inv)
    a, b = report(f, inv, 'one'), report(f, inv, 'two')
    first = assess(f, h, [a.entity_id, b.entity_id], ref='verified')
    counter = report(f, inv, 'clear', ['DRAIN_CLEAR'])
    omitted = assess(f, h, [], ref='omitted-counter')
    assert first.assessment.assessment == 'VERIFIED'
    assert omitted.assessment.assessment == 'INCONCLUSIVE'
    assert counter.entity_id in omitted.assessment.contradicting_evidence_ids
    assert {a.entity_id, b.entity_id} <= set(omitted.assessment.supporting_evidence_ids)
    save('omission-guard', f, original=first, corrected=omitted)


def test_unknown_cause_and_llm_claims_never_verify(f):
    inv = open_case(f)
    h = propose(f, inv, cause_code='UNREGISTERED_DEMO_CRITERION')
    report(f, inv, 'one')
    report(f, inv, 'two')
    r = assess(f, h)
    assert r.assessment.assessment == 'SUPPORTED'
    assert any('No approved deterministic' in gap for gap in r.assessment.missing_evidence)
    # Native VERIFIED on an AGENT/context record is never inspection corroboration.
    from tests.graph_fixtures import evidence
    evidence(f.repo, 'AGENT-CLAIM', evidence_type='LLM_STATEMENT', source_kind='AGENT')
    other = propose(f, inv, cause='CAPACITY_DEFICIT', ref='alternative')
    result = assess(f, other, ['AGENT-CLAIM'], ref='model-statement')
    assert result.assessment.assessment != 'VERIFIED'
    assert any('context only' in gap for gap in result.assessment.missing_evidence)


def test_inspection_failure_retry_cancel_and_no_report_for_pending(f):
    inv = open_case(f)
    ins = request(f, inv)
    actor = Actor(id='synthetic-inspector', role='DEPARTMENT_LEAD', department_id='DEP')
    with pytest.raises(PreconditionFailed):
        f.service.execute({'operation': 'report_inspection', 'request_id': 'premature', 'inspection_id': ins,
            'expected_hash': f.repo.get_node(ins).content_hash, 'source_id': 'source', 'record_id': 'report',
            'observations': [{'asset_id': 'D1', 'code': 'TEST', 'statement': 'Submitted test', 'method': 'TEST', 'observed_at': f.clock()}]}, actor)
    for state in ['REQUESTED', 'SCHEDULED', 'IN_PROGRESS', 'FAILED', 'REQUESTED']:
        advance_inspection(f, ins, state, ref=state + f.clock())
    advance_inspection(f, ins, 'CANCELLED')
    with pytest.raises(PreconditionFailed):
        advance_inspection(f, ins, 'REQUESTED', ref='after-cancel')
    assert not f.repo._read('MATCH (f:Finding) RETURN f.id')


def test_tampered_report_or_finding_fails_closed(f):
    inv = open_case(f)
    h = propose(f, inv)
    value = report(f, inv)
    source = Reader(f.repo, f.clock()).evidence(value.entity_id)
    finding = f.repo.get_node(source.report.finding_ids[0])
    # Deliberate privileged low-level mutation demonstrates guard, not service behavior.
    f.repo.update_node(finding.id, {'statement': 'Changed outside B09 service'}, expected_hash=finding.content_hash)
    with pytest.raises(PreconditionFailed):
        assess(f, h)
    assert f.repo._read('MATCH (a:HypothesisAssessment) RETURN count(a)') == [[0]]


def test_duplicate_source_report_cannot_create_independent_evidence(f):
    inv = open_case(f)
    first = report(f, inv)
    original = Reader(f.repo, f.clock()).evidence(first.entity_id).report
    ins = request(f, inv, 'another')
    for state in ['REQUESTED', 'SCHEDULED', 'IN_PROGRESS']:
        advance_inspection(f, ins, state)
    f.clock.advance()
    obs = [ob.model_copy(update={'observed_at': f.clock()}).model_dump(mode='json') for ob in original.observations]
    with pytest.raises(Conflict):
        f.service.execute({'operation': 'report_inspection', 'request_id': 'duplicate-source', 'inspection_id': ins,
            'expected_hash': f.repo.get_node(ins).content_hash, 'source_id': original.source_id, 'record_id': original.record_id,
            'observations': obs}, Actor(id='second-inspector', role='DEPARTMENT_LEAD', department_id='DEP'))
    assert f.repo.get_node(ins).properties['status'] == 'IN_PROGRESS'
    assert f.repo._read("MATCH (e:Evidence {evidence_type:'INSPECTION_REPORT',basis:'OBSERVED'}) RETURN count(e)") == [[1]]


@pytest.mark.parametrize('case', ['future', 'before-start', 'wrong-asset'])
def test_report_chronology_and_asset_scope_cannot_be_forged(f, case):
    inv = open_case(f)
    ins = request(f, inv)
    for state in ['REQUESTED', 'SCHEDULED', 'IN_PROGRESS']:
        advance_inspection(f, ins, state)
    f.clock.advance()
    observed = '2026-10-20T00:00:00Z' if case == 'future' else '2026-10-17T00:00:00Z' if case == 'before-start' else f.clock()
    with pytest.raises(PreconditionFailed):
        f.service.execute({'operation': 'report_inspection', 'request_id': 'bad-report', 'inspection_id': ins,
            'expected_hash': f.repo.get_node(ins).content_hash, 'source_id': 'source', 'record_id': 'record',
            'observations': [{'asset_id': 'D2' if case == 'wrong-asset' else 'D1', 'code': 'OBSTRUCTION_OBSERVED', 'statement': 'Submitted field record', 'method': 'TEST', 'observed_at': observed}]},
            Actor(id='inspector', role='DEPARTMENT_LEAD', department_id='DEP'))
    assert f.repo.get_node(ins).properties['status'] == 'IN_PROGRESS'
    assert f.repo._read('MATCH (f:Finding) RETURN count(f)') == [[0]]


def test_proposal_criteria_cannot_be_weakened_or_use_foreign_incident(f):
    inv = open_case(f)
    with pytest.raises(PreconditionFailed):
        propose(f, inv, confirming_codes=['OBSTRUCTION_OBSERVED'])
    with pytest.raises(PreconditionFailed):
        propose(f, inv, ref='foreign', incident_ids=[f.receipts['ROAD_DAMAGE'].incident_id])
    assert f.repo._read('MATCH (h:Hypothesis) RETURN count(h)') == [[0]]


def test_parameterized_source_text_cannot_execute_cypher(f):
    inv = open_case(f)
    h = propose(f, inv, statement="Untrusted ' MATCH (n) DETACH DELETE n //", mechanism='Untrusted content is data only')
    assert 'DETACH DELETE' in f.repo.get_node(h).properties['statement']
    assert all(f.repo.get_node(r.incident_id).kind == 'Incident' for r in f.receipts.values())


def test_real_mcp_broker_reads_b09_inspections_with_distinct_event_provenance(f, db):
    from mcp import Client, StdioServerParameters
    from app.mcp.runtime import ROOT
    from app.mcp.civicly.runtime import configure, connections
    from app.mcp.civicly.broker import DomainBroker
    from app.mcp.broker import BrokerError
    from app.mcp.civicly.storage import TraceStore
    inv = open_case(f)
    a, b = report(f, inv, 'one'), report(f, inv, 'two')
    configure(db)
    async def run():
        params = StdioServerParameters(command=sys.executable, args=['-m', 'tests.b09_server', f.repo.graph.name],
            cwd=str(ROOT), env={'PYTHONPATH': str(ROOT / 'backend')})
        with connections() as (_, writer, name):
            store = TraceStore(writer, name)
            async with Client(params, mode='legacy', read_timeout_seconds=8) as client:
                broker = DomainBroker(client, store)
                await broker.discover()
                assert len(broker.tools()) == 12
                value = await broker.call('civicly::get_maintenance_history', {'asset_id': 'D1', 'from_time': '2026-10-17T00:00:00Z', 'to_time': f.clock(), 'as_of': f.clock()})
                assert value['status'] == 'PARTIAL', value.get('error')
                records = {v['record_id']: v for v in value['records']}
                ai, bi = a.updated_ids[0], b.updated_ids[0]
                assert ai in records and bi in records
                assert a.entity_id in records[ai]['evidence_ids'] and b.entity_id not in records[ai]['evidence_ids']
                assert b.entity_id in records[bi]['evidence_ids'] and a.entity_id not in records[bi]['evidence_ids']
                assert value['graph_revision'] == GraphQueries(f.repo)._state()
                assert store.get(value['execution_id']).validated_output
                for tool in ['assess', 'report_inspection', 'propose_hypothesis', 'query_graph', 'delete_graph']:
                    with pytest.raises(BrokerError):
                        await broker.call('civicly::' + tool, {})
                save('actual-mcp', f, result=value)
    asyncio.run(run())


def test_typed_inspection_read_distinguishes_pending_missing_and_actual_findings(f):
    inv = open_case(f)
    ins = request(f, inv)
    pending = f.service.inspection(ins, f.clock())
    missing = f.service.inspection('NO-SUCH-INSPECTION', f.clock())
    assert pending.state == 'PROPOSED' and not pending.report_evidence_ids and pending.gaps
    assert missing.availability == 'UNAVAILABLE' and missing.state is None
    completed = report(f, inv)
    source = Reader(f.repo, f.clock()).evidence(completed.entity_id).report
    actual = f.service.inspection(source.inspection_id, f.clock())
    assert actual.state == 'COMPLETED' and actual.report_evidence_ids == [completed.entity_id]
    assert actual.finding_ids == source.finding_ids
    assert actual.graph_revision == GraphQueries(f.repo)._state()


def test_known_domain_cause_requires_appropriate_primary_asset(f):
    inv = open_case(f)
    with pytest.raises(PreconditionFailed):
        propose(f, inv, cause='PUMP_FAILURE', asset_ids=['D1'])
    assert f.repo._read('MATCH (h:Hypothesis) RETURN count(h)') == [[0]]


def test_proposal_journal_tampering_cannot_weaken_verification(f):
    inv = open_case(f)
    h = propose(f, inv)
    source = Reader(f.repo, f.clock()).edges('PROPOSES', target=h)[0].properties['source_evidence_id']
    old = f.repo.get_node(source)
    payload = json.loads(old.properties['summary'])
    payload['command']['confirming_codes'] = ['OBSTRUCTION_OBSERVED']
    f.repo.update_node(source, {'summary': json.dumps(payload)}, expected_hash=old.content_hash)
    with pytest.raises(PreconditionFailed):
        assess(f, h)
    assert f.repo._read('MATCH (a:HypothesisAssessment) RETURN count(a)') == [[0]]


def test_utility_mechanism_cannot_substitute_another_assets_topology(f):
    inv = open_case(f, 'ROAD_DAMAGE')
    incident = f.receipts['ROAD_DAMAGE'].incident_id
    for asset in ['D1', 'D2']:
        f.repo.create_relationship('AFFECTS', incident, asset, {**edge('EXTRA-' + asset), 'association_status': 'REPORTED', 'source_evidence_id': 'EV'})
    f.repo.create_relationship('DRAINS_TO', 'D1', 'D2', {**edge('UNRELATED-DRAIN'), 'association_status': 'VERIFIED', 'source_evidence_id': 'EV'})
    with pytest.raises(PreconditionFailed, match='originate at the concerned pipe'):
        propose(f, inv, 'ROAD_DAMAGE', 'UTILITY_LEAK', asset_ids=['P1', 'D1'],
                topology={'source_id': 'D1', 'target_id': 'D2', 'operation': 'dependencies'})
    assert f.repo._read('MATCH (h:Hypothesis) RETURN count(h)') == [[0]]
