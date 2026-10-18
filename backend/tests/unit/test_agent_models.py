"""Pure validation tests; no provider/DB success asserted."""
import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.active import new_profile,save,load,active_scope,is_shared_target,require_source
from app.agents.models import Selection,Budget
from tests.b10_fixtures import choose

@pytest.mark.parametrize('changes',[{'action':'EXECUTE'},{'status':'VERIFIED'},{'arguments_json':'[]'},{'tool_name':'arbitrary','action':'PAUSE'},{'pause_reason':'NONE'}])
def test_invalid_selection(changes):
    with pytest.raises((ValidationError,ValueError)):Selection.model_validate({**choose(),**changes})

def test_profile_requires_exact_context(tmp_path):
    p,q=new_profile(),new_profile()
    assert not is_shared_target(p.graph)
    with active_scope(p):
        assert is_shared_target(p.graph) and not is_shared_target(q.graph)
        with pytest.raises(ValueError):require_source(q.graph)
    path=tmp_path/'profile.json';save(p,path);assert load(path)==p
    path.chmod(0o644)
    with pytest.raises(ValueError):load(path)

@pytest.mark.parametrize('changes',[{'graph':'civicly_knowledge'},{'checkpoints':'civicly_knowledge'},{'version':2},{'read_user':'default'}])
def test_profile_rejects_unapproved_names(changes):
    with pytest.raises(ValidationError):type(new_profile()).model_validate({**new_profile().model_dump(),**changes})

@pytest.mark.parametrize('changes',[{'max_iterations':100},{'max_tools':0},{'max_tokens':2000001},{'max_seconds':1000},{'max_wakes':100}])
def test_finite_budgets(changes):
    with pytest.raises(ValidationError):Budget(**changes)


def test_nested_analytical_schemas_reuse_b09_contracts():
    from app.agents.runtime import InvestigationAgent
    from app.services.evidence.models import Propose
    schemas=InvestigationAgent.action_schemas()
    assert schemas['PROPOSE']['$defs']['Topology']==Propose.model_json_schema()['$defs']['Topology']
    assert set(schemas['PROPOSE']['$defs']['Topology']['required'])=={'source_id','target_id'}
    for schema in schemas.values():
        assert not set(schema['properties'])&{'operation','request_id','investigation_id','incident_ids','expected_hash','as_of'}


def test_failed_official_call_persists_actual_host_error_observation_mocked():
    """Mock broker failure, real envelope model; no real transport claim."""
    import asyncio
    from app.agents.mcp import Tools
    from app.mcp.broker import BrokerError
    from app.mcp.civicly.contracts import Context
    class Official:
        operator_inventory=[{'name':'query_graph_readonly','description':'Fixed template'}]
        def tools(self):return [{'name':'query_graph_readonly'}]
        async def call(self,args):raise BrokerError('TIMEOUT')
    class Domain:
        def tools(self):return []
    class Store:
        def __init__(self):self.rows=[]
        def append(self,record):self.rows.append(record)
    store=Store();tools=Tools(Official(),Domain(),store,[],'unused-test-name')
    with pytest.raises(BrokerError,match='TIMEOUT'):
        asyncio.run(tools.call('official::query_graph_readonly',{'template':'node','id':'D1'},Context(trace_id='T',execution_id='E'),'Actual test-selected public summary'))
    assert len(store.rows)==1 and store.rows[0].status=='TIMEOUT'
    assert store.rows[0].error_code=='TIMEOUT' and store.rows[0].output_sha256 is None
    assert store.rows[0].rationale_summary=='Actual test-selected public summary'
