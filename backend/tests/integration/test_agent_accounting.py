"""Simulated Gemini HTTP, actual FalkorDB/B09/MCP/LangGraph/Saver and SQLite."""
import asyncio,json,os,subprocess
from pathlib import Path
import httpx,pytest
from app.active import active_scope
from app.agents.provider import Gemini,ProviderSettings
from app.agents.policy import Permit
from app.agents.spending import Ledger
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver,RecoveryRequired
from app.agents.mcp import brokers
from app.agents.models import Budget
from tests.b10_fixtures import create,state
from tests.b10or_http import ReactiveHTTP,ReadPause,HistoryReactive
from tests.integration.test_agent_reasoning import EvidenceReactiveFake,TopologyReactiveFake
from tests.integration.test_agent_optimization import cleanup
from tests.b09_fixtures import Fixture,report
from tests.schema_examples import edge,NOW
pytestmark=pytest.mark.integration

def model(initial,tmp,handler):
    return Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key',CIVICLY_LLM_RETRY_WAIT_BUDGET=0),permit=Permit(initial.investigation_id,initial.thread_id,'B10OR-TEST','.50','MOCK_HTTP'),ledger=Ledger(tmp/'ledger'),transport=httpx.MockTransport(handler))

def test_http_graph_contradiction_changes_inspection(db,tmp_path):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path)
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                s=state(p,r,tools,clock,receipt,inv);http=ReactiveHTTP(HistoryReactive());m=model(s,tmp_path,http)
                first=await InvestigationAgent(p,r,tools,m,saver(p),clock=clock).run(s,thread_id=s.thread_id)
                assert len(first['data']['hypotheses'])==2 and first['data']['executions']
                f=Fixture(r,clock,{'WATERLOGGING':receipt},p.graph,{})
                report(f,inv,'reviewed-clear',codes=['DRAIN_CLEAR'],assets=['D1'])
                report(f,inv,'context-only',codes=['GENERAL_DRAIN_NOTE'],assets=['D1'])
                report(f,inv,'unreviewed-blockage',codes=['OBSTRUCTION_OBSERVED'],assets=['D1'],reviewed=False)
                clock.advance()
                resumed=await InvestigationAgent(p,r,tools,model(s,tmp_path,http),saver(p),clock=clock).run(thread_id=s.thread_id,resume=True)
                a,b=[v['data']['pending_inspections'][-1] for v in [first,resumed]]
                assert r.get_node(a).properties['inspection_type']=='BLOCKAGE_INSPECTION'
                assert r.get_node(b).properties['inspection_type']=='CAPACITY_TEST'
                assert resumed['data']['tokens']>first['data']['tokens']>0
                assert len(http.contexts[-1]['catalog'])==16
                classification=http.contexts[-1]['hypotheses'][0]['assessments'][0]['classification']
                assert classification['reviewed_contradiction_ids'] and classification['unreviewed_support_ids'] and classification['contextual_evidence_ids']
                Path('/tmp/civicly-b10or-http-contradiction.json').write_text(json.dumps({'mode':'SIMULATED_GEMINI_HTTP_REAL_MCP_B09_SAVER','requests':http.calls,'classification':classification,'first':first,'resumed':resumed},default=str,indent=2))
    try:asyncio.run(run())
    finally:cleanup(db,p)

@pytest.mark.parametrize('topology,target',[('VERIFIED','P1'),('CANDIDATE','R1'),('DISCONNECTED','R1')])
def test_http_topology_selection(db,tmp_path,topology,target):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path,'ROAD_DAMAGE')
    async def run():
        with active_scope(p):
            if topology!='DISCONNECTED':r.create_relationship('UNDERLIES','P1','R1',{**edge('B10OR-PIPE'),'valid_from':NOW,'association_status':topology,'source_evidence_id':'EV'})
            async with brokers(p,path) as tools:
                s=state(p,r,tools,clock,receipt,inv,'ROAD_DAMAGE');s.asset_ids=['P1','R1'];h=ReactiveHTTP(TopologyReactiveFake())
                result=await InvestigationAgent(p,r,tools,model(s,tmp_path,h),saver(p),clock=clock).run(s,thread_id=s.thread_id)
                assert r._read('MATCH (:Inspection {id:$id})-[:INSPECTS]->(n) RETURN n.id',{'id':result['data']['pending_inspections'][-1]})==[[target]]
                assert result['data']['observations'][0]['search_limited'] is True
                assert result['data']['tokens']==130*h.calls
    try:asyncio.run(run())
    finally:cleanup(db,p)

@pytest.mark.parametrize('fault',['503','429','invalid','timeout','quota'])
def test_http_failure_recovery_no_duplicate_actions(db,tmp_path,fault):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path)
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                s=state(p,r,tools,clock,receipt,inv);h=ReactiveHTTP(ReadPause(),fault=fault)
                first=await InvestigationAgent(p,r,tools,model(s,tmp_path,h),saver(p),clock=clock).run(s,thread_id=s.thread_id)
                assert first['__interrupt__']
                if fault in {'timeout','quota'}:
                    assert h.calls==1 and not first['data']['executions']
                    clock.advance();first=await InvestigationAgent(p,r,tools,model(s,tmp_path,h),saver(p),clock=clock).run(thread_id=s.thread_id,resume=True)
                assert len(first['data']['executions'])==1 and len(set(first['data']['decisions']))==2
                assert len(first['data']['hypotheses'])==len(first['data']['pending_inspections'])==0
                assert first['data']['tokens']>=130*len(first['data']['decisions'])
                assert h.calls<=4
    try:asyncio.run(run())
    finally:cleanup(db,p)

def test_token_budget_checkpoint_authorized_increase_preserves_counters(db,tmp_path):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path)
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                s=state(p,r,tools,clock,receipt,inv);s.budget=Budget(max_tokens=2000,max_wakes=1);h=ReactiveHTTP(ReadPause())
                first=await InvestigationAgent(p,r,tools,model(s,tmp_path,h),saver(p),clock=clock).run(s,thread_id=s.thread_id)
                assert first['__interrupt__'] and 'TOKEN_BUDGET' in first['data']['errors'] and h.calls==0
                a=InvestigationAgent(p,r,tools,model(s,tmp_path,h),saver(p),clock=clock)
                with pytest.raises(RecoveryRequired,match='AUTHORIZATION'):await a.run(thread_id=s.thread_id,resume=True,budget_increase=Budget().model_dump())
                with pytest.raises(RecoveryRequired,match='DECREASE'):await a.run(thread_id=s.thread_id,resume=True,budget_increase=Budget(max_tokens=2000,max_tools=1).model_dump(),authorized=True,operator_reason='Invalid reduction')
                clock.advance();result=await a.run(thread_id=s.thread_id,resume=True,budget_increase=Budget(max_wakes=1).model_dump(),authorized=True,operator_reason='Approved synthetic complex-case allowance')
                assert result['data']['wakes']==1 and result['data']['tokens']==260 and len(result['data']['executions'])==1
                assert result['data']['iterations']>first['data']['iterations']
                assert any(o.get('operation')=='AUTHORIZED_BUDGET_INCREASE' for o in result['data']['observations'])
                with pytest.raises(RecoveryRequired,match='WAKE_BUDGET'):await a.run(thread_id=s.thread_id,resume=True)
                clock.advance();again=await a.run(thread_id=s.thread_id,resume=True,budget_increase=Budget(max_wakes=2).model_dump(),authorized=True,operator_reason='Approve one more wake; preserve all counters')
                assert again['data']['wakes']==2 and again['data']['tokens']==520
    try:asyncio.run(run())
    finally:cleanup(db,p)

def test_mock_http_real_process_restart(db,tmp_path):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path)
    try:
        async def prepare():
            with active_scope(p):
                async with brokers(p,path) as tools:return state(p,r,tools,clock,receipt,inv)
        s=asyncio.run(prepare());src=tmp_path/'state.json';src.write_text(s.model_dump_json());results=[]
        for phase in ['create','resume']:
            out=tmp_path/(phase+'.json')
            proc=subprocess.run([str(Path('backend/.venv/bin/python').absolute()),'-m','tests.b10or_worker',str(path),phase,str(src),str(out)],env={**os.environ,'PYTHONPATH':'backend'},capture_output=True,timeout=90)
            assert proc.returncode==0,proc.stderr.decode()[-2000:]
            results.append(json.loads(out.read_text()))
        assert results[0]['data']['tokens']==260 and results[1]['data']['tokens']==520
        assert results[1]['data']['wakes']==1 and len(results[1]['data']['executions'])==2
        assert Ledger(tmp_path/'ledger').thread_tokens(s.thread_id)==520
        Path('/tmp/civicly-b10or-process-proof.json').write_text(json.dumps({'mode':'SIMULATED_HTTP_TWO_REAL_PROCESSES','results':results},default=str,indent=2))
    finally:cleanup(db,p)

@pytest.mark.parametrize('issue,cause',[('WATERLOGGING','BLOCKAGE'),('ROAD_DAMAGE','SUBGRADE_FAILURE'),('WASTE_ACCUMULATION','MISSED_PICKUP')])
def test_complex_real_context_token_boundaries(db,issue,cause):
    from tests.b10or_context import measure
    value=asyncio.run(measure(db,issue,cause))
    Path('/tmp/civicly-b10or-context-'+issue+'.json').write_text(json.dumps(value,indent=2))


def test_reported_usage_overrun_persists_without_counter_overflow(db,tmp_path):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path)
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                s=state(p,r,tools,clock,receipt,inv);s.budget=Budget(max_tokens=150000);s.tokens=100000;seen=[]
                def oversized(req):
                    seen.append(1);v=ReactiveHTTP.response(__import__('tests.b10_fixtures',fromlist=['choose']).choose()).json()
                    v['usageMetadata']={'promptTokenCount':999980,'candidatesTokenCount':20,'totalTokenCount':1000000}
                    return httpx.Response(200,json=v)
                m=model(s,tmp_path,oversized)
                result=await InvestigationAgent(p,r,tools,m,saver(p),clock=clock).run(s,thread_id=s.thread_id)
                assert result['__interrupt__'] and result['data']['tokens']==1100000 and 'TOKEN_BUDGET' in result['data']['errors']
                assert len(seen)==1 and not result['data']['executions']
                assert Ledger(tmp_path/'ledger').thread_tokens(s.thread_id)==1100000
    try:asyncio.run(run())
    finally:cleanup(db,p)
