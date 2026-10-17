import json
from copy import deepcopy
import pytest
from app.graph.targets import new_test_graph_name
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository,PreconditionFailed,OutcomeUnknown
from app.graph.analysis.models import AnalysisRequest,AnalysisLimits,CaseRequest
from app.graph.analysis.engine import GraphAnalysis
from app.graph.analysis.counterfactual import Counterfactual,capture
from app.graph.analysis.reader import AnalysisBudgetExceeded
from tests.b05_fixtures import network,AS_OF
from tests.schema_examples import common,asset,edge,NOW

pytestmark=pytest.mark.integration


@pytest.fixture
def repo(db):
    name=new_test_graph_name(5)
    try:
        assert MigrationRunner(db,name).apply()['ready']
        yield network(GraphRepository(db,name))
    finally:
        if name in db.list_graphs():db.select_graph(name).delete()


def q(operation,ids=('D1',),**kw):return AnalysisRequest(operation=operation,ids=ids,as_of=AS_OF,**kw)


def test_directed_reachability_temporal_and_geographic_negative(repo):
    engine=GraphAnalysis(repo)
    down=engine.run(q('reachability'));up=engine.run(q('reachability',('D5',),direction='upstream'))
    assert down.rows[0].related_ids==('D2','D3','D5')
    assert up.rows[0].related_ids==('D1','D2','D3','D4')
    assert 'EXPIRED' not in down.rows[0].related_ids and 'NEARBY' not in down.rows[0].related_ids
    assert any('INCOMING' in p.directions for p in up.paths)
    assert all(p.evidence_ids==('EV',) for p in down.paths)
    assert any(n.id=='EV' and n.properties['source_record_id'].startswith('b05-controlled') for n in down.nodes)
    assert down.graph_revision==capture(repo).fingerprint['graph_revision']
    assert json.loads(down.model_dump_json())['as_of']==AS_OF


def test_shared_bottlenecks_and_connector_budget(repo):
    engine=GraphAnalysis(repo)
    result=engine.run(q('shared_downstream',(),incident_ids=('SEED','DEPENDENT-CASE')))
    assert [row.id for row in result.rows]==['D2','D3','D5']
    assert all(row.factors['distinct_incident_coverage']==2 for row in result.rows)
    small=engine.run(q('shared_downstream',(),incident_ids=('SEED','DEPENDENT-CASE'),max_hops=1))
    assert not small.rows and small.search_limited
    direct=engine.run(q('shared_downstream',(),incident_ids=('SEED','OLD'),max_hops=1))
    assert [row.id for row in direct.rows]==['D1']
    assert direct.budgets['infrastructure_hops']==0


def test_impacted_coverage_and_transparent_criticality(repo):
    engine=GraphAnalysis(repo)
    impact=engine.run(q('impacted_assets',('D2',)))
    assert impact.rows[0].related_ids==('D3','D5')
    ranks=engine.run(q('criticality',('D4','D1','NEARBY')))
    assert [row.id for row in ranks.rows]==['D1','D4','NEARBY']
    assert [row.factors['distinct_infrastructure_assets'] for row in ranks.rows]==[3,2,0]
    assert 'confidence' not in ranks.model_dump_json()


def test_induced_components_and_typed_dependencies(repo):
    engine=GraphAnalysis(repo)
    result=engine.run(q('components',('D1','NEARBY')))
    assert [row.related_ids for row in result.rows]==[('D1','D2','D3','D4','D5'),('NEARBY',)]
    assert result.search_limited and any('bounded' in gap for gap in result.gaps)
    deps=engine.run(q('dependencies',('PIPE','WASTE')))
    assert {row.id:row.related_ids for row in deps.rows}=={'PIPE':('ROAD',),'WASTE':('ROUTE',)}


def test_task_dag_prerequisite_first_and_external_members(repo):
    result=GraphAnalysis(repo).run(AnalysisRequest(operation='task_dag',plan_id='PLAN',as_of=AS_OF))
    assert [row.id for row in result.rows]==['T3','T2','T1']
    assert result.rows[0].factors['external_to_plan'] and not result.rows[-1].factors['external_to_plan']
    assert result.rows[-1].factors['unmet_prerequisites']==1
    with pytest.raises(PreconditionFailed):repo.create_relationship('DEPENDS_ON','T3','T1',edge('CYCLE'))
    assert GraphAnalysis(repo).run(q('task_dag',('T1',))).rows[0].id=='T3'


def test_case_ranking_dates_real_history_and_coverage_gaps(repo):
    result=GraphAnalysis(repo).cases(CaseRequest(as_of=AS_OF,seed_incident_id='SEED'))
    assert result.rows[0].id=='OLD'
    old=result.rows[0];dependent=next(row for row in result.rows if row.id=='DEPENDENT-CASE')
    assert old.factors['shared_asset_count']==1 and old.factors['shared_cluster_count']==1
    assert old.factors['inspection_context_count']==old.factors['work_order_context_count']==old.factors['outcome_context_count']==1
    assert dependent.factors['drainage_dependency_asset_count']==1
    assert dependent.factors['same_issue'] is False
    assert any('No linked historical outcome' in gap for gap in dependent.gaps)
    assert 'LATER' not in [row.id for row in result.rows]
    assert any(n.id=='OUT' and n.properties['result']=='INCONCLUSIVE' for n in result.nodes)
    assert all(set(row.path_ids)<={p.id for p in result.paths} for row in result.rows)


def test_case_zone_issue_filter_and_missing_history(repo):
    result=GraphAnalysis(repo).cases(CaseRequest(as_of=AS_OF,zone_id='Z',issue_type='WATERLOGGING',before='2026-09-06T00:00:00Z'))
    assert [row.id for row in result.rows]==['OLD']
    empty=GraphAnalysis(repo).cases(CaseRequest(as_of=AS_OF,asset_ids=('NEARBY',),before='2026-08-01T00:00:00Z'))
    assert not empty.rows and any('No historical' in gap for gap in empty.gaps)


def test_counterfactual_ablation_changes_ranking_and_preserves_source(repo):
    before=capture(repo);experiment=Counterfactual(repo)
    try:
        assert capture(experiment.repository).records==before.records
        removed=experiment.remove('CUT')
        assert removed.properties['association_status']=='VERIFIED'
        comparison=experiment.compare(q('criticality',('D1','D4')))
        assert comparison.source_unchanged and comparison.before_ranking==('D1','D4') and comparison.after_ranking==('D4','D1')
        assert comparison.lost_path_ids and not comparison.gained_path_ids
        assert comparison.changes[0]['edge']['id']=='CUT'
        assert comparison.after.graph_revision==comparison.clone_initial_revision+1
        coverage=experiment.compare(q('impacted_assets',('D2',)))
        assert coverage.before.rows[0].related_ids==('D3','D5') and coverage.after.rows[0].related_ids==()
        shared=experiment.compare(q('shared_downstream',(),incident_ids=('SEED','DEPENDENT-CASE')))
        assert [row.id for row in shared.before.rows]==['D2','D3','D5']
        assert [row.id for row in shared.after.rows]==['D2']
        experiment.add_candidate('D2','D3',{**edge('CANDIDATE'),'source_evidence_id':'EV-CANDIDATE','association_status':'CANDIDATE','valid_from':NOW})
        still=experiment.compare(q('criticality',('D1','D4')))
        assert still.after_ranking==comparison.after_ranking
        exploratory=experiment.compare(q('criticality',('D1','D4'),include_candidates=True))
        assert exploratory.after_ranking==('D1','D4') and exploratory.gained_path_ids
        assert capture(repo).fingerprint==before.fingerprint and capture(repo).records==before.records
    finally:experiment.cleanup()


def test_clone_cannot_remove_wrong_kind_candidate_or_stale_content(repo):
    experiment=Counterfactual(repo)
    try:
        with pytest.raises(PreconditionFailed):experiment.remove('A-SEED')
        with pytest.raises(PreconditionFailed):experiment.repository.remove_verified_drain('CUT','stale')
        with pytest.raises(PreconditionFailed):experiment.add_candidate('D2','D3',{**edge('BAD'),'association_status':'VERIFIED','source_evidence_id':'EV'})
        assert experiment.assert_source_unchanged()
    finally:experiment.cleanup()


def test_small_budget_and_long_connected_path_are_not_global_negatives(repo):
    limited=GraphAnalysis(repo).run(q('reachability',max_hops=1))
    assert limited.rows[0].related_ids==('D2',) and limited.search_limited
    disconnected=GraphAnalysis(repo).run(q('reachability',('NEARBY',)))
    assert not disconnected.rows[0].related_ids and disconnected.search_limited
    truncated=GraphAnalysis(repo,AnalysisLimits(max_paths=1)).run(q('reachability'))
    assert truncated.truncated and any('lower bounds' in gap for gap in truncated.gaps)
    with pytest.raises(AnalysisBudgetExceeded):GraphAnalysis(repo,AnalysisLimits(max_queries=1)).run(q('reachability'))


def test_read_only_calls_and_pending_state(repo,monkeypatch):
    fingerprint=capture(repo).fingerprint
    def forbidden(*a,**kw):raise AssertionError('Source mutation attempted by read algorithm')
    monkeypatch.setattr(repo.graph,'query',forbidden)
    GraphAnalysis(repo).run(q('reachability'));GraphAnalysis(repo).cases(CaseRequest(as_of=AS_OF,issue_type='WATERLOGGING'))
    assert capture(repo).fingerprint==fingerprint


def test_native_bfs_probe_does_not_apply_temporal_proof_filters(repo):
    rows=repo.graph.ro_query('MATCH (a:DrainSegment {id:$id}) CALL algo.BFS(a,$depth,$relationship) YIELD nodes,edges RETURN nodes,edges LIMIT 1',params={'id':'D1','depth':6,'relationship':'DRAINS_TO'},timeout=1000).result_set
    ids={n.properties['id'] for row in rows for n in row[0]}
    assert 'EXPIRED' in ids
    safe=GraphAnalysis(repo).run(q('reachability'))
    assert 'EXPIRED' not in safe.rows[0].related_ids


def test_candidate_reported_and_future_evidence_are_qualified(repo):
    engine=GraphAnalysis(repo)
    repo.create_relationship('DRAINS_TO','D2','NEARBY',{**edge('REPORTED'),'source_evidence_id':'EV-CANDIDATE','association_status':'REPORTED','valid_from':NOW})
    verified=engine.run(q('reachability'));exploratory=engine.run(q('reachability',include_candidates=True))
    assert 'NEARBY' not in verified.rows[0].related_ids and 'NEARBY' in exploratory.rows[0].related_ids
    assert any('REPORTED' in note for note in exploratory.reservations)
    p={**common('FUTURE-EV'),'evidence_type':'UNVERIFIED_REPORT','summary':'Controlled future knowledge',
       'reliability':'UNVERIFIED','recorded_at':'2026-10-18T00:00:00Z','source_kind':'SYNTHETIC','source_record_id':'future-fixture'}
    repo.create_node('Evidence',p)
    repo.create_relationship('DRAINS_TO','D2','EXPIRED',{**edge('FUTURE-CLAIM'),'association_status':'CANDIDATE','source_evidence_id':'FUTURE-EV','valid_from':NOW})
    result=engine.run(q('reachability',include_candidates=True))
    assert 'EXPIRED' not in result.rows[0].related_ids
    assert result.measurements['future_evidence_paths_excluded']>0


def test_revision_retry_and_pending_source_fail_closed(repo,monkeypatch):
    reader=__import__('app.graph.analysis.reader',fromlist=['Reader']).Reader
    original=reader.query;changed=False
    def concurrent(self,query,params=None):
        nonlocal changed
        actual=original(self,query,params)
        if not changed and query.startswith('MATCH p='):
            changed=True
            n=repo.get_node('D5')
            repo.update_node('D5',{'name':'Controlled concurrent revision'},expected_hash=n.content_hash)
        return actual
    monkeypatch.setattr(reader,'query',concurrent)
    result=GraphAnalysis(repo).run(q('reachability'))
    assert result.measurements['snapshot_retries']==1
    assert next(n for n in result.nodes if n.id=='D5').properties['name']=='Controlled concurrent revision'
    monkeypatch.setattr(reader,'query',original)
    # Explicit storage fault injection, not an algorithm write or mocked success.
    repo.graph.query("MATCH (m:CivicSchemaMigration {id:$id}) SET m.repo_pending=$pending",params={'id':'0001','pending':'CONTROLLED-UNRESOLVED'},timeout=1000)
    try:
        with pytest.raises(OutcomeUnknown):GraphAnalysis(repo).run(q('reachability'))
    finally:
        repo.graph.query("MATCH (m:CivicSchemaMigration {id:$id}) SET m.repo_pending=$pending",params={'id':'0001','pending':''},timeout=1000)


@pytest.mark.parametrize('after_commit',[False,True])
def test_counterfactual_uncertain_removal_retains_clone_and_recovers(repo,monkeypatch,after_commit):
    from redis.exceptions import ConnectionError
    from app.graph.analysis.counterfactual import CounterfactualFailure
    from app.graph.repository import NotFound
    experiment=Counterfactual(repo);original=experiment.repository.graph.query;fired=False
    source=capture(repo).fingerprint
    def lost(query,*a,**kw):
        nonlocal fired
        if not fired and 'DELETE r' in query:
            fired=True
            if after_commit:original(query,*a,**kw)
            raise ConnectionError('Controlled dropped counterfactual mutation response')
        return original(query,*a,**kw)
    monkeypatch.setattr(experiment.repository.graph,'query',lost)
    try:
        with pytest.raises(CounterfactualFailure) as caught:experiment.remove('CUT')
        assert caught.value.code=='COUNTERFACTUAL_CLONE_WRITE_UNKNOWN'
        assert caught.value.graph==experiment.clone_name and experiment.clone_name in repo.client.list_graphs()
        monkeypatch.setattr(experiment.repository.graph,'query',original)
        experiment.repository.recover_pending()
        if after_commit:
            with pytest.raises(NotFound):experiment.repository.get_relationship('CUT')
        else:assert experiment.repository.get_relationship('CUT').id=='CUT'
        assert experiment.assert_source_unchanged() and capture(repo).fingerprint==source
        assert experiment.changes[-1]['state']=='OUTCOME_UNKNOWN'
    finally:
        monkeypatch.setattr(experiment.repository.graph,'query',original)
        experiment.cleanup()


def test_export_caps_and_deadline_never_return_half_paths(repo,monkeypatch):
    import time
    for limits in (AnalysisLimits(max_nodes=2),AnalysisLimits(max_edges=1)):
        result=GraphAnalysis(repo,limits).run(q('reachability'))
        assert result.truncated
        for p in result.paths:
            assert set(p.node_ids)<={n.id for n in result.nodes}
            assert set(p.edge_ids)<={e.id for e in result.edges}
    original=repo.graph.ro_query
    def delayed(*a,**kw):
        value=original(*a,**kw);time.sleep(.01);return value
    monkeypatch.setattr(repo.graph,'ro_query',delayed)
    with pytest.raises(AnalysisBudgetExceeded,match='wall'):GraphAnalysis(repo,AnalysisLimits(wall_seconds=.001)).run(q('reachability'))


def test_partial_clone_failure_is_identified_retained_and_source_unchanged(repo,monkeypatch):
    from redis.exceptions import ConnectionError
    from app.graph.analysis.counterfactual import CounterfactualFailure
    original=GraphRepository.create_node;count=0;before=capture(repo).fingerprint
    def fail(self,*args,**kw):
        nonlocal count
        if self.graph.name!=repo.graph.name:
            count+=1
            if count==2:raise ConnectionError('Controlled interruption before second clone write')
        return original(self,*args,**kw)
    monkeypatch.setattr(GraphRepository,'create_node',fail)
    target=None
    try:
        with pytest.raises(CounterfactualFailure) as caught:Counterfactual(repo)
        target=caught.value.graph
        assert target in repo.client.list_graphs()
        assert repo.client.select_graph(target).ro_query('MATCH (n:CivicEntity) RETURN count(n)',timeout=1000).result_set==[[1]]
        assert capture(repo).fingerprint==before
    finally:
        # Retention verified above; clean only this newly generated disposable test target.
        if target and target in repo.client.list_graphs():repo.client.select_graph(target).delete()


def test_actual_b04_city_separates_verified_exploration_and_no_history(db):
    from app.graph.schema import utc_now
    from app.graph.analysis.evaluation import CITY_GRAPH,verify_city,ROOT
    bundle=json.loads((ROOT/'data/ingestion/city-v3.json').read_text())
    city=GraphRepository(db,CITY_GRAPH);before=verify_city(city,bundle);engine=GraphAnalysis(city);at=utc_now()
    verified=engine.run(AnalysisRequest(operation='reachability',ids=('DRAIN-D12',),as_of=at))
    exploratory=engine.run(AnalysisRequest(operation='reachability',ids=('DRAIN-D12',),as_of=at,include_candidates=True))
    assert verified.rows[0].related_ids==()
    assert exploratory.rows[0].related_ids==('DRAIN-D18',)
    for issue in ('WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION'):
        cases=engine.cases(CaseRequest(as_of=at,issue_type=issue,include_candidates=True))
        assert cases.rows
        assert all(row.factors['work_order_context_count']==row.factors['outcome_context_count']==0 for row in cases.rows)
        assert all('Incident'==n.kind or n.kind in city.registry.nodes for n in cases.nodes)
    names=set(db.list_graphs())
    with pytest.raises(AnalysisBudgetExceeded):Counterfactual(city)
    assert set(db.list_graphs())==names
    assert verify_city(city,bundle)==before


def test_clone_writer_redirect_and_unrecorded_changes_are_refused(repo):
    experiment=Counterfactual(repo);writer=experiment.repository;clone=writer.graph;before=capture(repo).fingerprint
    try:
        writer.graph=repo.graph
        with pytest.raises(PreconditionFailed):writer.create_node('Location',{**common('UNAUTHORIZED'),'name':'Should never be created','latitude':12.0,'longitude':77.0})
        writer.graph=clone
        n=writer.get_node('D5');writer.update_node('D5',{'name':'Unrecorded clone edit'},expected_hash=n.content_hash)
        with pytest.raises(PreconditionFailed,match='unrecorded'):experiment.compare(q('reachability'))
        assert capture(repo).fingerprint==before
    finally:
        writer.graph=clone;experiment.cleanup()


def test_dynamic_root_id_is_parameterized_not_executable(repo):
    from app.graph.repository import NotFound
    before=capture(repo).fingerprint
    with pytest.raises(NotFound):GraphAnalysis(repo).run(q('reachability',("D1'}) DELETE n //",)))
    assert capture(repo).fingerprint==before


def test_positive_zone_proof_is_not_lost_when_later_context_truncates(repo):
    result=GraphAnalysis(repo,AnalysisLimits(max_paths=3)).cases(CaseRequest(as_of=AS_OF,zone_id='Z',issue_type='WATERLOGGING'))
    assert result.truncated and result.rows
    assert {row.id for row in result.rows}=={'OLD','SEED'}
    assert all(row.factors['same_zone'] for row in result.rows)
    assert all(row.path_ids for row in result.rows)
