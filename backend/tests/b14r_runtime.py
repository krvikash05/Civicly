"""Explicit same-thread resume, scripted choices; real MCP/Saver/source validation."""
import copy
from uuid import uuid4
from app.agents.models import InvestigationState
from app.agents.runtime import InvestigationAgent
from app.agents.mcp import brokers
from app.agents.checkpoints import saver,ownership,RecoveryRequired
from app.services.evidence.reader import Reader
from tests.b10_fixtures import ScriptedModel,choose

async def pause(p,r,clock,path,inv,f,planning):
 async with brokers(p,path,timeout=10) as tools:
  bound=Reader(r,clock()).edges('INVESTIGATES',source=inv);thread=uuid4().hex
  s=InvestigationState(graph=p.graph,investigation_id=inv,thread_id=thread,problem_cluster_id=next(e.target for e in bound if r.get_node(e.target).kind=='ProblemCluster'),incident_ids=[e.target for e in bound if r.get_node(e.target).kind=='Incident'],asset_ids=['D1'],issue='WATERLOGGING',graph_revision=r._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision")[0][0],inventory_hash=tools.inventory_hash,as_of=clock(),hypotheses=[v['hypothesis_id'] for v in f.saved['draft']['basis']],current_plan_id=f.b['plan_id'],current_plan_version=f.b['plan_version'],current_plan_hash=f.b['plan_hash'])
  agent=InvestigationAgent(p,r,tools,ScriptedModel([choose()]),saver(p),clock=clock,planning_service=planning)
  result=await agent.run(s,thread_id=thread);assert result['__interrupt__']
  snap=await agent.graph.aget_state({'configurable':{'thread_id':thread}})
  return {'thread_id':thread,'config':copy.deepcopy(snap.config),'values':copy.deepcopy(snap.values)}

async def resume(p,r,clock,path,inv,f,planning,before,reopened,report):
 async with brokers(p,path,timeout=10) as tools:
  model=ScriptedModel([choose('READ',{'template':'node','id':reopened['new_incident_id']},'official::query_graph_readonly'),choose('READ',{'template':'node','id':report['entity_id']},'official::query_graph_readonly'),choose()])
  agent=InvestigationAgent(p,r,tools,model,saver(p),clock=clock,planning_service=planning)
  thread=before['thread_id'];config={'configurable':{'thread_id':thread}}
  after=await agent.graph.aget_state(config)
  assert after.values==before['values'] and after.config==before['config'] # Domain write did not rewrite checkpoint.
  async with ownership(r.client,p,thread) as check:
   agent.check=check;forged=copy.deepcopy(after.values);forged['data']['incident_ids']=['UNBOUND-INCIDENT']
   try:agent.decode(forged)
   except RecoveryRequired:pass
   else:raise AssertionError('Unvalidated incident binding accepted')
  result=await agent.run(thread_id=thread,resume=True);state=result['data']
  assert state['incident_ids']==[reopened['new_incident_id']] and state['wakes']==1
  assert report['entity_id'] in state['evidence']
  refresh=next(x for x in state['observations'] if x.get('operation')=='RECURRENCE_SCOPE_REFRESH')
  assert refresh['previous_incident_ids']==before['values']['data']['incident_ids']
  assert state['tool_calls']==2 and not state['refresh_required'] and len(state['executions'])==2
  assert model.contexts[0]['state']['refresh_required'] is True
  assert model.contexts[0]['state']['incident_ids']==[reopened['new_incident_id']]
  assert report['entity_id'] in model.contexts[0]['source_evidence_hashes']
  assert any(row.get('rows') and row['rows'][0]['properties']['id']==reopened['new_incident_id'] for row in state['observations'])
  assert any(row.get('rows') and row['rows'][0]['properties']['id']==report['entity_id'] for row in state['observations'])
  # Public SDK reads an old checkpoint by ID, proving it was retained byte-for-byte.
  old=await agent.graph.aget_state(before['config']);assert old.values==before['values']
  latest=await agent.graph.aget_state(config)
  # A second legitimate wake must not reinterpret the retained ENDED episode.
  first_checkpoint=copy.deepcopy(latest.values);first_config=copy.deepcopy(latest.config)
  scope_query='MATCH (i:Investigation {id:$id})-[e:INVESTIGATES]->(n:Incident) RETURN n.id,e.id,n.status ORDER BY n.id'
  scope_before=r._read(scope_query,{'id':inv});events_before=r._read('MATCH (e:DomainEvent) RETURN count(e)')
  clock.advance();update_id='EV-B14R2-SOURCE-UPDATE'
  r.create_node('Evidence',{'id':update_id,'municipality_id':'demo-city','schema_version':3,'created_at':clock(),'updated_at':clock(),'recorded_at':clock(),'source_kind':'SYNTHETIC','source_record_id':'B14R2:explicit-source-update','evidence_type':'CONTEXT','summary':'Authored additional context; no causal assertion','reliability':'UNVERIFIED'})
  next_model=ScriptedModel([choose('READ',{'template':'node','id':update_id},'official::query_graph_readonly'),choose()])
  again=InvestigationAgent(p,r,tools,next_model,saver(p),clock=clock,planning_service=planning)
  second=await again.run(thread_id=thread,resume=True);second_state=second['data']
  assert second_state['incident_ids']==state['incident_ids'] and second_state['wakes']==2
  assert second_state['tool_calls']==3 and not second_state['refresh_required']
  assert next_model.contexts[0]['state']['refresh_required'] is True
  assert next_model.contexts[0]['state']['incident_ids']==[reopened['new_incident_id']]
  assert any(row.get('rows') and row['rows'][0]['properties']['id']==update_id for row in second_state['observations'])
  assert len([x for x in second_state['observations'] if x.get('operation')=='RECURRENCE_SCOPE_REFRESH'])==1
  assert (await again.graph.aget_state(before['config'])).values==before['values']
  assert (await again.graph.aget_state(first_config)).values==first_checkpoint
  assert r._read(scope_query,{'id':inv})==scope_before and r._read('MATCH (e:DomainEvent) RETURN count(e)')==events_before
  second_latest=await again.graph.aget_state(config)
  second_proof={'wakes':second_state['wakes'],'active_incident_ids':second_state['incident_ids'],'source_update_id':update_id,'checkpoint_id':second_latest.config['configurable']['checkpoint_id'],'first_resume_checkpoint_unchanged':True,'original_checkpoint_unchanged':True,'scope_links_and_domain_events_unchanged':True,'scope_refresh_count':1,'fresh_mcp_executions':second_state['executions'],'fresh_read_required_then_satisfied':True}
  return {'mode':'SCRIPTED_MODEL_REAL_FALKORDB_MCP_SAVER','thread_id':thread,'old_checkpoint_id':before['config']['configurable']['checkpoint_id'],'new_checkpoint_id':latest.config['configurable']['checkpoint_id'],'old_checkpoint_unchanged':True,'explicit_resume_only':True,'active_incident_ids':state['incident_ids'],'recurrence_evidence_id':report['entity_id'],'refresh_audit':refresh,'fresh_mcp_executions':state['executions'],'unvalidated_binding_rejected':True,'second_resume':second_proof,'provider_calls':0}
