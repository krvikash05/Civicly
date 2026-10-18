"""Scripted model; real MCP/LangGraph/FalkorDBSaver/domain draft service."""
import asyncio,json,os,subprocess
from pathlib import Path
import os
PREFIX=os.environ.get("CIVICLY_PLANNING_EVIDENCE_PREFIX","B12R")
from uuid import uuid4
import pytest
from app.active import active_scope
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from tests.b10_fixtures import ScriptedModel,choose
from tests.integration.test_memory_graphrag import memory
from tests.b12_fixtures import prepared
pytestmark=pytest.mark.integration
@pytest.mark.parametrize('invalid',[False,True,'dependency'])
def test_model_draft_real_mcp_persist_fresh_process_and_resume(db,tmp_path,memory,invalid):
 p,r,clock,path,inv,draft,service=prepared(db,tmp_path,memory,'WATERLOGGING',remedial=not invalid)
 async def run():
  with active_scope(p):
   async with brokers(p,path,timeout=10) as tools:
    from app.agents.models import InvestigationState
    from app.services.evidence.reader import Reader
    incidents=[e.target for e in Reader(r,clock()).edges('INVESTIGATES',source=inv) if r.get_node(e.target).kind=='Incident']
    cluster=next(e.target for e in Reader(r,clock()).edges('INVESTIGATES',source=inv) if r.get_node(e.target).kind=='ProblemCluster')
    state=InvestigationState(graph=p.graph,investigation_id=inv,thread_id=uuid4().hex,problem_cluster_id=cluster,discovered_tool_names=[t['name'] for t in tools.catalog()],incident_ids=incidents,asset_ids=['D1'],issue='WATERLOGGING',graph_revision=0,inventory_hash=tools.inventory_hash,as_of=clock(),hypotheses=[b.hypothesis_id for b in draft.basis])
    state.graph_revision=r._read("MATCH (g:CivicSchemaMigration {id:'0001'}) RETURN g.repo_revision")[0][0]
    value=draft.model_dump(mode='json')
    if invalid is True:value['tasks'][0]['depends_on']=[value['tasks'][0]['id']]
    actions=[choose('READ',{'template':'node','id':'D1'},'official::query_graph_readonly'),choose('RECOMMEND',{'plan_draft':value},summary='Authored deterministic draft proposal requiring domain validation')]
    if invalid=='dependency':
     from app.graph.migration import MigrationError
     async def unavailable(*args,**kwargs):raise MigrationError('credential=DO_NOT_LEAK_dependency_body')
     service.create=unavailable # Deliberate pre-write dependency fault, not a mock success.
    model=ScriptedModel(actions);agent=InvestigationAgent(p,r,tools,model,saver(p),clock=clock,planning_service=service)
    result=await agent.run(state,thread_id=state.thread_id);final=result['data']
    assert result['__interrupt__'] and final['executions']
    if invalid=='dependency':
     assert final['pause_reason']=='PLAN_OPERATOR_RECOVERY_REQUIRED' and final['current_plan_id'] is None
     assert final['planning_feedback']['resolution']=='OPERATOR_RECOVERY' and final['planning_feedback']['category']=='DEPENDENCY'
     assert 'DO_NOT_LEAK' not in json.dumps(final)
     assert final['observations'][-1]['feedback']==final['planning_feedback']
     assert r._read('MATCH (p:ResolutionPlan) RETURN count(p)')==[[0]]
    elif invalid:
     assert final['pause_reason']=='PLAN_CLARIFICATION_REQUIRED' and final['current_plan_id'] is None
     assert r._read('MATCH (p:ResolutionPlan) RETURN count(p)')==[[0]]
     assert final['planning_feedback']['code']=='PLAN_DAG_INVALID'
     assert final['planning_feedback']['task_ids']==['inspect0']
     assert final['observations'][-1]['feedback']==final['planning_feedback']
    else:
     assert final['current_plan_id'] and final['current_plan_version']==1
     saved=service.store.get(final['current_plan_id']);assert saved['receipt']['plan_hash']==final['current_plan_hash']
     out=tmp_path/'fresh.json'
     process=subprocess.run([str(Path('backend/.venv/bin/python').absolute()),'-m','tests.b12_worker',str(path),state.thread_id,str(out)],env={**os.environ,'PYTHONPATH':str(Path('backend').absolute())},capture_output=True,timeout=30)
     assert process.returncode==0,process.stderr.decode()[-1000:]
     fresh=json.loads(out.read_text());assert fresh['draft']['tasks'][0]['action_type']=='DRAIN_BLOCKAGE_CLEARANCE';assert fresh['checkpoint_id'] and fresh['receipt']==saved['receipt']
     resumed=await InvestigationAgent(p,r,tools,ScriptedModel([choose()]),saver(p),clock=clock,planning_service=service).run(None,thread_id=state.thread_id,resume=True)
     assert resumed['data']['current_plan_id']==final['current_plan_id'] and r._read('MATCH (p:ResolutionPlan) RETURN count(p)')==[[1]]
     Path(f'docs/evidence/{PREFIX}-agent-fresh-process.json').write_text(json.dumps(fresh,indent=2)+'\n')
    Path(f'docs/evidence/{PREFIX}-agent-'+('dependency' if invalid=='dependency' else 'invalid' if invalid else 'valid')+'.json').write_text(json.dumps({'mode':'SCRIPTED_MODEL_REAL_MCP_LANGGRAPH_SAVER','graph':p.graph,'thread':state.thread_id,'result':final,'provider_calls':0},indent=2)+'\n')
 asyncio.run(run())
