import pytest
from pydantic import ValidationError
from app.graph.analysis.models import AnalysisRequest,AnalysisLimits,CaseRequest
from app.graph.analysis.engine import topological_order
from app.graph.analysis.counterfactual import _CloneWriter
from app.graph.targets import new_test_graph_name
from app.graph.repository import PreconditionFailed


@pytest.mark.parametrize('change',[{'max_hops':7},{'max_hops':True},{'as_of':'yesterday'},{'ids':('','D')},{'ids':('D','D')},{'operation':'raw Cypher'},{'unknown':1},{'include_candidates':'true'},{'limit':101}])
def test_algorithm_request_strictness(change):
    with pytest.raises(ValidationError):AnalysisRequest(**{'operation':'reachability','ids':('D',),'as_of':'2026-10-17T00:00:00Z',**change})


@pytest.mark.parametrize('field,value',[('max_nodes',121),('max_edges',201),('max_queries',65),('max_steps',10001),('timeout_ms',1001),('wall_seconds',5.1),('max_paths',101)])
def test_limits_cannot_weaken_caps(field,value):
    with pytest.raises(ValidationError):AnalysisLimits(**{field:value})


def test_topological_direction_determinism_and_cycle():
    assert topological_order(['a','b','c'],[('a','b'),('b','c')])==('c','b','a')
    with pytest.raises(PreconditionFailed,match='Cycle'):topological_order(['a','b'],[('a','b'),('b','a')])
    with pytest.raises(PreconditionFailed,match='Unresolved'):topological_order(['a'],[('a','missing')])


@pytest.mark.parametrize('name',['civicly_knowledge','civicly_b01_runtime','civicly_docs',new_test_graph_name(4),new_test_graph_name(5),'arbitrary'])
def test_clone_cannot_be_nominated_or_authorized_with_arbitrary_token(name):
    with pytest.raises(PreconditionFailed):_CloneWriter(object(),name,object())


def test_history_window_and_minimum_inputs():
    with pytest.raises(ValidationError):CaseRequest(as_of='2026-10-17T00:00:00Z')
    with pytest.raises(ValidationError):CaseRequest(as_of='2026-10-17T00:00:00Z',zone_id='Z',after='2026-10-18T00:00:00Z')
    with pytest.raises(ValidationError):AnalysisRequest(operation='shared_downstream',incident_ids=('I',),as_of='2026-10-17T00:00:00Z')


def test_machine_contract_matches_serializable_models():
    import json
    from pathlib import Path
    from jsonschema import Draft202012Validator
    from app.graph.analysis.models import AnalysisResult
    contract=json.loads((Path(__file__).resolve().parents[3]/'contracts/graph_algorithms.json').read_text())
    for model in (AnalysisRequest,CaseRequest,AnalysisLimits,AnalysisResult):
        schema=contract['schemas'][model.__name__]
        Draft202012Validator.check_schema(schema)
        assert schema==model.model_json_schema()


def test_binding_audit_distinguishes_broader_missing_and_budget_unknown():
    from types import SimpleNamespace
    from app.graph.analysis.evaluation import classify_bindings
    scenario={'scenario_id':'CONTROL','actual_incident_assets':['A'],'asset_ids':['A','B'],
              'actual_incident_clusters':['C'],'cluster_ids':['C']}
    proof=SimpleNamespace(id='P',node_ids=('A','B'))
    result=SimpleNamespace(paths=[proof],truncated=False,search_limited=True,graph_revision=3)
    assert classify_bindings(scenario,result)['asset_classification']=='BROADER_EXPLORATORY_CANDIDATE_SET'
    result.paths=[]
    assert classify_bindings(scenario,result)['asset_classification']=='UNPROVEN_EXTRA_BINDING_CONTEXT_WITHIN_BUDGET'
    scenario['asset_ids']=['B']
    assert classify_bindings(scenario,result)['asset_classification']=='STARTING_ASSET_BINDING_SOURCE_CONFLICT'
    scenario['cluster_ids']=[]
    assert classify_bindings(scenario,result)['cluster_classification']=='UNSPECIFIED_CLUSTER_CONTEXT'


@pytest.mark.parametrize('change',[{'plan_id':'PLAN'},{'incident_ids':('I1','I2')},{'threshold':3}])
def test_irrelevant_request_fields_are_rejected_not_ignored(change):
    with pytest.raises(ValidationError):AnalysisRequest(operation='reachability',ids=('D',),as_of='2026-10-17T00:00:00Z',**change)
