"""Scripted model choices; actual committed recurrence, broker, agent and Saver."""
import copy
from app.events.service import Delivery
from app.events.runtime import Runtime
from app.events.worker import Worker
from app.agents.checkpoints import saver
from app.agents.models import InvestigationState
from tests.b10_fixtures import ScriptedModel,choose

async def consume(p,r,clock,path,inv,f,planning,before,reopened,report):
 events=r._read('MATCH (e:DomainEvent {event_type:$type}) RETURN e.id ORDER BY e.id',{'type':'RECURRENCE_DETECTED'})
 assert len(events)==1;event_id=events[0][0]
 d=Delivery(r,clock);d.activate(operator='B15-proof',reason='Explicitly admit only the committed recurrence; leave older evidence unchanged',event_ids=[event_id],authorize=True)
 registered=d.discover();assert registered==[event_id]
 row=d.store.get('delivery',event_id);assert row['case_id']==inv and row['action']=='WAKE'
 assert d.discover()==[]
 models=[]
 def factory():
  m=ScriptedModel([choose('READ',{'template':'node','id':reopened['new_incident_id']},'official::query_graph_readonly'),choose('READ',{'template':'node','id':report['entity_id']},'official::query_graph_readonly'),choose()]);models.append(m);return m
 runtime=Runtime(p,path,r,clock,model_factory=factory);w=Worker(d,runtime,'B15-first-process')
 def saved():return saver(p).get_tuple({'configurable':{'thread_id':before['thread_id']}})
 initial=saved();assert initial.checkpoint['channel_values']['data']==before['values']['data']
 scope='MATCH (i:Investigation {id:$id})-[e:INVESTIGATES]->(n:Incident) RETURN n.id,e.id,n.status ORDER BY n.id'
 scope_before=r._read(scope,{'id':inv});work_before=r._read('MATCH (w:WorkOrder) RETURN count(w)');outcomes_before=r._read('MATCH (o:InterventionOutcome) RETURN count(o)')
 claim=await w.once(fault='after_handler');assert claim and d.store.get('delivery',event_id)['status']=='RUNNING'
 first=saved();state=InvestigationState.model_validate(first.checkpoint['channel_values']['data'])
 assert state.wakes==1 and state.incident_ids==[reopened['new_incident_id']] and state.tool_calls==2 and not state.refresh_required
 assert report['entity_id'] in state.evidence and models[0].contexts[0]['state']['refresh_required'] is True
 assert any(o.get('operation')=='B15_DELIVERY_CONSUMED' and o.get('delivery_key')==claim['key'] for o in state.observations)
 # A genuinely new worker instance reconciles the exact persisted batch checkpoint.
 clock.advance(61);replacement=Worker(d,Runtime(p,path,r,clock,model_factory=lambda:(_ for _ in ()).throw(AssertionError('Recovery must not redispatch'))),'B15-replacement')
 await replacement.recover_expired()
 done=d.store.get('delivery',event_id);assert done['status']=='DONE' and done['attempts']==1
 assert saved().checkpoint==first.checkpoint and len(models)==1
 # A later explicit source update and two compatible requests coalesce into one wake.
 clock.advance();source='EV-B15-SOURCE-UPDATE'
 r.create_node('Evidence',{'id':source,'municipality_id':'demo-city','schema_version':3,'created_at':clock(),'updated_at':clock(),'recorded_at':clock(),'source_kind':'SYNTHETIC','source_record_id':'B15:explicit-source-update','evidence_type':'CONTEXT','summary':'Authored additional context, no causal assertion','reliability':'UNVERIFIED'})
 req=d.request_resume(inv,'B15-repeat-refresh-1',operator='proof',reason='Explicit new context',authorize=True)
 other=d.request_resume(inv,'B15-repeat-refresh-2',operator='proof',reason='Compatible refresh',authorize=True)
 assert d.request_resume(inv,'B15-repeat-refresh-1',operator='proof',reason='Replay same request',authorize=True)['id']==req['id']
 next_model=ScriptedModel([choose('READ',{'template':'node','id':source},'official::query_graph_readonly'),choose()])
 second_worker=Worker(d,Runtime(p,path,r,clock,model_factory=lambda:next_model),'B15-second-wake')
 second_claim=await second_worker.once();assert set(second_claim['ids'])=={req['id'],other['id']}
 second=saved();s=InvestigationState.model_validate(second.checkpoint['channel_values']['data'])
 assert s.wakes==2 and s.incident_ids==state.incident_ids and s.tool_calls==3 and not s.refresh_required
 assert next_model.contexts[0]['state']['refresh_required'] is True
 assert len([o for o in s.observations if o.get('operation')=='RECURRENCE_SCOPE_REFRESH'])==1
 old=saver(p).get_tuple(before['config']);assert old.checkpoint==initial.checkpoint
 retained=saver(p).get_tuple(first.config);assert retained.checkpoint==first.checkpoint
 assert r._read(scope,{'id':inv})==scope_before and r._read('MATCH (w:WorkOrder) RETURN count(w)')==work_before and r._read('MATCH (o:InterventionOutcome) RETURN count(o)')==outcomes_before
 assert all(d.store.get('delivery',i)['status']=='DONE' for i in second_claim['ids'])
 assert await second_worker.once() is None
 return {'mode':'SCRIPTED_MODEL_REAL_FALKORDB_MCP_SAVER','graph':p.graph,'thread_id':before['thread_id'],'native_event_id':event_id,'original_checkpoint_id':before['config']['configurable']['checkpoint_id'],'first_checkpoint_id':first.config['configurable']['checkpoint_id'],'second_checkpoint_id':second.config['configurable']['checkpoint_id'],'checkpoint_before_ack_status':'RUNNING','recovered_status':done['status'],'recovery_redispatches':0,'original_checkpoint_unchanged':True,'first_checkpoint_unchanged':True,'active_incident_ids':s.incident_ids,'wakes':s.wakes,'fresh_mcp_executions':s.executions,'coalesced_ids':second_claim['ids'],'old_ended_incident_and_scope_preserved':True,'work_orders_unchanged':work_before,'outcomes_unchanged':outcomes_before,'provider_calls':0}
