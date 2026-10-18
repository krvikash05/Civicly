"""Real LangGraph, MCP and FalkorDBSaver; explicitly fake deterministic model."""
import asyncio,json
from pathlib import Path
import pytest
from app.active import active_scope
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver,RecoveryRequired
from app.services.evidence.policies import POLICIES
from tests.b10_fixtures import create,state,ScriptedModel,choose

pytestmark=pytest.mark.integration

@pytest.mark.parametrize('issue,cause',[('WATERLOGGING','BLOCKAGE'),('ROAD_DAMAGE','SUBGRADE_FAILURE'),('WASTE_ACCUMULATION','MISSED_PICKUP')])
def test_real_graph_pause_resume(db,tmp_path,issue,cause):
    path=tmp_path/'profile.json';p,repo,clock,receipt,inv=create(db,path,issue)
    rule=POLICIES[issue][cause];asset={'WATERLOGGING':'D1','ROAD_DAMAGE':'R1','WASTE_ACCUMULATION':'W1'}[issue]
    actions=[choose('READ',{'template':'node','id':receipt.incident_id},'official::query_graph_readonly'),
        choose('PROPOSE',{'cause_code':cause,'asset_ids':[asset],'statement':'Synthetic possible explanation','mechanism':'Must be independently inspected','confirming_codes':rule['confirming'],'falsifying_codes':rule['falsifying']}),
        choose('INSPECT',{'asset_ids':[asset],'department_id':'DEP','inspection_type':'B10_CONTROLLED'})]
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                s=state(p,repo,tools,clock,receipt,inv,issue);agent=InvestigationAgent(p,repo,tools,ScriptedModel(actions),saver(p),clock=clock)
                result=await agent.run(s,thread_id=s.thread_id)
                final=result['data'];assert final['pending_inspections'] and final['hypotheses'] and final['executions']
                assert all(role in final['nodes'] for role in ['Supervisor','Investigator','RootCauseAnalyst','Coordinator'])
                assert result['__interrupt__']
                # New agent + new Saver connection, stable investigation/thread; real changed graph.
                clock.advance();repo.create_node('Evidence',{'id':'EV-B10-NEW','municipality_id':'demo-city','schema_version':3,'created_at':clock(),'updated_at':clock(),'recorded_at':clock(),'source_kind':'SYNTHETIC','evidence_type':'CONTEXT','summary':'Additional source requires fresh read','reliability':'UNVERIFIED'})
                model=ScriptedModel([choose('READ',{'template':'node','id':'EV-B10-NEW'},'official::query_graph_readonly'),choose()])
                agent2=InvestigationAgent(p,repo,tools,model,saver(p),clock=clock)
                resumed=await agent2.run(thread_id=s.thread_id,resume=True)
                assert 'SOURCE_CHANGED_REFRESH_REQUIRED' in resumed['data']['errors']
                assert resumed['data']['wakes']==1 and resumed['data']['pending_inspections']==final['pending_inspections']
                assert len(resumed['data']['decisions'])==5
                Path('/tmp/civicly-b10-runtime-'+issue+'.json').write_text(json.dumps({'mode':'DETERMINISTIC_FAKE_MODEL_REAL_MCP_AND_SAVER','initial':result,'resumed':resumed},default=str,indent=2))
    try:asyncio.run(run())
    finally:
        for name in [p.graph,p.checkpoints]:
            if name in db.list_graphs():db.select_graph(name).delete()
        db.connection.execute_command('ACL','DELUSER',p.read_user,p.checkpoint_user)


def test_actual_python_process_restart_resume(db,tmp_path):
    import subprocess,os
    from uuid import uuid4
    path=tmp_path/'profile.json';p,repo,clock,receipt,inv=create(db,path)
    try:
        async def prepare():
            with active_scope(p):
                async with brokers(p,path) as tools:return state(p,repo,tools,clock,receipt,inv)
        initial=asyncio.run(prepare());input_path=tmp_path/'state.json';input_path.write_text(initial.model_dump_json())
        outputs=[]
        for phase in ['create','resume']:
            out=tmp_path/(phase+'.json')
            process=subprocess.run([str(Path('backend/.venv/bin/python').absolute()),'-m','tests.b10_worker',str(path),phase,str(input_path),str(out)],env={**os.environ,'PYTHONPATH':'backend'},capture_output=True,timeout=70)
            assert process.returncode==0,'Restart driver failed; inspect sanitized local test output'
            value=json.loads(out.read_text());outputs.append(value);assert value['result']['__interrupt__']
        assert outputs[1]['result']['data']['wakes']==1
        assert len(outputs[1]['result']['data']['executions'])==2
        assert len(set(outputs[1]['result']['data']['decisions']))==4
        Path('/tmp/civicly-b10-process-proof.json').write_text(json.dumps({'fresh_processes':2,'outputs':outputs},indent=2))
    finally:
        for name in [p.graph,p.checkpoints]:
            if name in db.list_graphs():db.select_graph(name).delete()
        db.connection.execute_command('ACL','DELUSER',p.read_user,p.checkpoint_user)
