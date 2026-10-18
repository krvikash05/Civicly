"""Explicit bounded offline delivery, using existing fenced companion storage."""
from app.graph.models import digest
from app.graph.repository import Conflict
from app.services.http.service import Recovery
from app.services.operations.auth import Denied

async def advance(s,action,batches,key,actor,token):
 if actor.role not in {'ADMIN','ANALYST'}:raise Denied('ADVANCE_ROLE')
 if action not in {'discover','run'} or type(batches) is not int or not 1<=batches<=4:raise ValueError('ADVANCE_BOUND')
 request='CLI-B18-'+digest([s.profile.graph,actor.id,key])[:32];sha=digest([action,batches]);store=s.delivery.store
 with s.repo._session() as session:
  old=store.get('cli_advance',request)
  if old:
   if old['hash']!=sha:raise Conflict('ADVANCE_KEY_CONFLICT')
   if old['status']=='DONE':return old['receipt']
   raise Recovery(request)
  row={'id':request,'hash':sha,'actor_id':actor.id,'status':'DISPATCHING'}
  try:store.write(session,[('cli_advance',request,row)])
  except Exception:raise Recovery(request) from None
 try:
  if action=='discover':
   ids=s.delivery.discover();value={'request_id':request,'action':'DISCOVERY_ONLY','registered_ids':ids,'execution_completed':False}
  else:
   from app.events.runtime import Runtime
   from app.events.worker import Worker
   worker=Worker(s.delivery,Runtime(s.profile,s.profile_path,s.repo,s.clock),'CLI-'+request);rows=[]
   for _ in range(batches):
    s.auth.resolve(token)
    claim=await worker.once(discover=False)
    if not claim:break
    states=[s.delivery.store.get('delivery',id)['status'] for id in claim['ids']]
    if any(v!='DONE' for v in states):raise Recovery(request,identities={'investigation_id':claim['case_id']} if claim['case_id'] else None)
    rows.append({'batch_key':claim['key'],'event_ids':claim['ids'],'investigation_id':claim['case_id'],'status':'DONE','action':claim['action']})
   value={'request_id':request,'action':'BOUNDED_OFFLINE_WORKER','batches':rows,'discovery_performed':False,'execution_mode':'B15_DETERMINISTIC_DEVELOPMENT_NO_PROVIDER','resolution_verified':False}
  with s.repo._session() as session:store.write(session,[('cli_advance',request,{**row,'status':'DONE','receipt':value})])
  return value
 except Exception as exc:
  if isinstance(exc,Recovery):raise
  raise Recovery(request) from None
