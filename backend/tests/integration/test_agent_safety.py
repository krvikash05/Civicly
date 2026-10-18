"""Real source/MCP/Saver, explicitly deterministic model fault probes."""
import asyncio,json,os,signal,subprocess
from pathlib import Path
import pytest
from app.active import active_scope
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver,ownership,RecoveryRequired
from app.graph.models import digest
from tests.b10_fixtures import create,state,ScriptedModel,choose

pytestmark=pytest.mark.integration

@pytest.fixture
def f(db,tmp_path):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path)
    try:yield p,r,clock,receipt,inv,path
    finally:
        for name in [p.graph,p.checkpoints]:
            if name in db.list_graphs():db.select_graph(name).delete()
        db.connection.execute_command('ACL','DELUSER',p.read_user,p.checkpoint_user)

@pytest.mark.parametrize('tool,args',[('official::query_graph',{'query':'CREATE (:Forbidden)'}),('civicly::create_plan',{}),('official::query_graph_readonly',{'template':'node','id':'D1','graph':'civicly_knowledge'}),('civicly::get_maintenance_history',{'asset_id':'D1','surprise':True})])
def test_invalid_model_tool_or_args_pauses(f,tool,args):
    p,r,clock,receipt,inv,path=f
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                s=state(p,r,tools,clock,receipt,inv);agent=InvestigationAgent(p,r,tools,ScriptedModel([choose('READ',args,tool)]),saver(p),clock=clock)
                result=await agent.run(s,thread_id=s.thread_id)
                assert result['__interrupt__'] and result['data']['pause_reason']=='DEPENDENCY_UNAVAILABLE'
                assert not result['data']['hypotheses']
    asyncio.run(run())

def test_concurrent_lease_denial_and_corrupt_checkpoint(f):
    p,r,clock,receipt,inv,path=f
    async def run():
        with active_scope(p):
            async with ownership(r.client,p,'ownership-thread'):
                with pytest.raises(RecoveryRequired,match='CONCURRENT'):
                    async with ownership(r.client,p,'ownership-thread'):pass
            async with brokers(p,path) as tools:
                s=state(p,r,tools,clock,receipt,inv);agent=InvestigationAgent(p,r,tools,ScriptedModel([choose()]),saver(p),clock=clock)
                paused=await agent.run(s,thread_id=s.thread_id)
                # Public LangGraph API creates a new incompatible state version; no SDK schema mutation.
                config={'configurable':{'thread_id':s.thread_id}}
                await agent.graph.aupdate_state(config,{'data':{**paused['data'],'version':99}})
                with pytest.raises(Exception):await agent.run(thread_id=s.thread_id,resume=True)
                with pytest.raises(RecoveryRequired,match='QUARANTINED'):await agent.run(thread_id=s.thread_id,resume=True)
                assert len(r._read('MATCH (d:AgentDecision) RETURN d.id LIMIT 100'))==1
    asyncio.run(run())


def test_actual_mcp_timeout_and_fresh_session_recovery(f):
    p,r,clock,receipt,inv,path=f
    async def run():
        with active_scope(p):
            async with brokers(p,path,timeout=2) as tools:
                # Identify only this owned B10 profile server, never unrelated processes.
                rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines()
                ids=[int(row.strip().split(None,1)[0]) for row in rows if '-m app.agents.server '+str(path) in row]
                print('owned B10 server count',len(ids));assert len(ids)==1;pid=ids[0];os.kill(pid,signal.SIGSTOP)
                try:
                    s=state(p,r,tools,clock,receipt,inv)
                    model=ScriptedModel([choose('READ',{'asset_id':'D1','from_time':'2026-10-17T00:00:00Z','to_time':clock(),'as_of':clock()},'civicly::get_maintenance_history')])
                    agent=InvestigationAgent(p,r,tools,model,saver(p),clock=clock);paused=await agent.run(s,thread_id=s.thread_id)
                    print('timeout result',paused['data']['pause_reason'],paused['data']['observations'])
                    assert paused['data']['pause_reason']=='DEPENDENCY_UNAVAILABLE'
                    assert paused['data']['observations'][0]['error']['code']=='TIMEOUT'
                finally:os.kill(pid,signal.SIGCONT)
            async with brokers(p,path) as tools:
                model=ScriptedModel([choose('READ',{'template':'node','id':'D1'},'official::query_graph_readonly'),choose()])
                fresh=InvestigationAgent(p,r,tools,model,saver(p),clock=clock)
                result=await fresh.run(thread_id=s.thread_id,resume=True)
                assert result['data']['tool_calls']==2 and result['data']['observations'][-1]['rows'][0]['properties']['id']=='D1'
    asyncio.run(run())

@pytest.mark.parametrize('case',['future-cutoff','future-raw-fact'])
def test_agent_rejects_future_knowledge_before_model_context(f,case):
    p,r,clock,receipt,inv,path=f
    with active_scope(p):
        future='2026-10-19T00:00:00Z'
        r.create_node('Evidence',{'id':'EV-FUTURE','municipality_id':'demo-city','schema_version':3,'created_at':future,'updated_at':future,'recorded_at':future,'source_kind':'SYNTHETIC','reliability':'UNVERIFIED','evidence_type':'CONTEXT','summary':'Future source must not enter model observation'})
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                args={'template':'node','id':'EV-FUTURE'} if case=='future-raw-fact' else {'asset_id':'D1','from_time':'2026-10-17T00:00:00Z','to_time':future,'as_of':future}
                tool='official::query_graph_readonly' if case=='future-raw-fact' else 'civicly::get_maintenance_history'
                initial=state(p,r,tools,clock,receipt,inv);model=ScriptedModel([choose('READ',args,tool)])
                result=await InvestigationAgent(p,r,tools,model,saver(p),clock=clock).run(initial,thread_id=initial.thread_id)
                assert result['data']['pause_reason']=='DEPENDENCY_UNAVAILABLE'
                assert result['data']['observations'][0]['error']['code']==('OUTPUT_OUTSIDE_CUTOFF' if case=='future-raw-fact' else 'INVALID_ARGUMENTS')
                assert 'Future source must not enter model observation' not in json.dumps(result,default=str)
    asyncio.run(run())
