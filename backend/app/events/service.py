"""Durable activation, discovery, claims, receipts and redacted public replay."""
from datetime import timedelta
from uuid import uuid4
from app.graph.models import digest
from app.graph.schema import timestamp
from app.graph.repository import Conflict,PreconditionFailed,RepositoryError
from app.services.operations.service import common
from .store import Store
from .sources import Sources
from .models import Event,route,public,batch_key,backoff

def later(at,seconds):return (timestamp(at)+timedelta(seconds=seconds)).isoformat().replace('+00:00','Z')
class Delivery:
 def __init__(self,repo,clock):self.repo=repo;self.clock=clock;self.store=Store(repo,clock);self.sources=Sources(repo,clock)
 def active(self):
  a=self.store.get('delivery_activation','root')
  if not a or a['graph']!=self.repo.graph.name:raise PreconditionFailed('EXPLICIT_DELIVERY_ACTIVATION_REQUIRED')
  return a
 def activate(self,*,operator,reason,event_ids=None,authorize=False):
  if authorize is not True or not operator or not reason or len(operator)>200 or len(reason)>512 or len(event_ids or [])>20:raise PreconditionFailed('EXPLICIT_ACTIVATION_REQUIRED')
  with self.repo._session() as s:
   old=self.store.get('delivery_activation','root')
   if old:return old
   sources=self.sources.scan();a={'graph':self.repo.graph.name,'floor_revision':s.revision,'existing_sources':[kind+':'+id for kind,id,_ in sources],'event_ids':sorted(set(event_ids or [])),'operator':operator,'reason':reason,'at':self.clock()}
   self.store.write(s,[('delivery_activation','root',a),('delivery_stream','root',{'cursor':0})]);return a
 def discover(self):
  a=self.active();registered=[]
  for kind,id,props in self.sources.scan():
   source=kind+':'+id
   try:
    candidates=list(self.sources.events(kind,id,props))
    for event in candidates:self.sources.case(event)
   except (ValueError,KeyError,TypeError,RepositoryError):
    if source not in a['existing_sources'] or id in a['event_ids'] or self.store.get('delivery',id):
     self.invalid(id,source);registered.append(id)
    continue
   for event in candidates:
    if event.aggregate_revision<=a['floor_revision'] and event.id not in a['event_ids']:continue
    if self.store.get('delivery',event.id):continue
    self.register(event,source);registered.append(event.id)
  return registered
 def register(self,event,source,extra=None):
  self.active();event=Event.model_validate(event.model_dump(mode='json'));case=self.sources.case(event);action,reason=route(event,case)
  with self.repo._session() as s:
   old=self.store.get('delivery',event.id)
   if old:
    if old['event']!=event.model_dump(mode='json'):raise Conflict('EVENT_ID_REUSED')
    return old
   stream=self.store.get('delivery_stream','root');cursor=stream['cursor']+1
   row={'id':event.id,'event':event.model_dump(mode='json'),'source_ref':source,'case_id':case,'action':action,'reason':reason,'status':'PENDING','attempts':0,'ceiling':3,'due_at':self.clock(),'owner':None,'lease_until':None,'batch':None,'history':[],'public':public(event,case,cursor,source),'receipt':None}
   nodes=[]
   if self.repo._node_optional(event.id) is None:
    nodes=[('DomainEvent',{**common(event.id,self.clock()),'event_type':event.type,'subject_id':event.entity_id,'occurred_at':event.occurred_at,'delivery_status':'PENDING','idempotency_key':event.idempotency_key,'payload_ref':'delivery:'+event.id})]
   self.store.write(s,[('delivery',event.id,row),('delivery_stream','root',{'cursor':cursor}),*(extra or [])],nodes=nodes)
   return row
 def invalid(self,id,source):
  with self.repo._session() as s:
   old=self.store.get('delivery',id)
   if old:
    if old['status'] in {'FAILED','RECOVERY_REQUIRED'}:return
    status='RECOVERY_REQUIRED' if old['status'] in {'RUNNING','CLAIMED'} else 'DONE' if old['status']=='DONE' else 'FAILED'
    value={**old,'status':status,'history':[*old['history'],{'at':self.clock(),'code':'INVALID_COMMITTED_SOURCE'}]}
   else:value={'id':id,'event':None,'source_ref':source,'status':'FAILED','attempts':0,'ceiling':3,'history':[{'at':self.clock(),'code':'INVALID_COMMITTED_EVENT'}],'receipt':None,'public':None}
   states=[('delivery',id,value)]
   if old and old.get('batch') and value['status']=='RECOVERY_REQUIRED':
    key=old['case_id'] if old['action']=='WAKE' else 'event:'+id
    c=self.store.get('delivery_case',key)
    if c and c['key']==old['batch']:states.append(('delivery_case',key,{**c,'status':'RECOVERY_REQUIRED'}))
   self.store.write(s,states,updates=self.native_status(value,value['status']))
 def public(self,*,after=0,limit=50):
  self.active()
  if type(after) is not int or after<0 or type(limit) is not int or not 1<=limit<=100:raise ValueError('PUBLIC_CURSOR_LIMIT')
  rows=sorted([r['public'] for r in self.store.rows('delivery') if r.get('public') and r['public']['cursor']>after],key=lambda r:r['cursor'])
  page=rows[:limit]
  return {'events':page,'next_cursor':page[-1]['cursor'] if page else after,'has_more':len(rows)>limit,'ordering':'source registration cursor; occurred_at/revision are original facts','graph':self.repo.graph.name}
 def native_status(self,row,status):
  old=self.repo._node_optional(row['id'])
  if old and old.kind=='DomainEvent':return [(old,{**old.properties,'updated_at':self.clock(),'delivery_status':status,**({'processed_at':self.clock()} if status=='DONE' else {})})]
  return []
 def claim(self,owner,*,limit=4,lease_seconds=60,case_id=None):
  self.active()
  if not owner or len(owner)>200 or not 1<=limit<=4 or not 1<=lease_seconds<=120:raise ValueError('CLAIM_BOUND')
  with self.repo._session() as s:
   now=self.clock();rows=sorted([r for r in self.store.rows('delivery') if r.get('event')],key=lambda r:r['public']['cursor'])
   eligible=[r for r in rows if (case_id is None or (r['case_id']==case_id and r['action']=='WAKE')) and ((r['status'] in {'PENDING','RETRY'} and timestamp(r['due_at'])<=timestamp(now)) or (r['status']=='CLAIMED' and timestamp(r['lease_until'])<=timestamp(now)))]
   for head in eligible:
    if head['attempts']>=head['ceiling']:
     failed={**head,'status':'FAILED','history':[*head['history'],{'at':now,'code':'CLAIM_RETRY_EXHAUSTED'}]}
     self.store.write(s,[('delivery',head['id'],failed)],updates=self.native_status(failed,'FAILED'));return None
    case=head['case_id'] if head['action']=='WAKE' else 'event:'+head['id']
    prior=self.store.get('delivery_case',case)
    if prior and prior['status'] in {'CLAIMED','RUNNING','RECOVERY_REQUIRED'}:
     if prior['status']!='CLAIMED' or timestamp(prior['lease_until'])>timestamp(now):continue
    group=[r for r in eligible if r['action']==head['action'] and (r['case_id']==head['case_id'] if head['action']=='WAKE' else r['id']==head['id'])][:limit]
    ids=[r['id'] for r in group];key=batch_key(ids);token=uuid4().hex;updates=[];states=[]
    for r in group:
     if r['attempts']>=r['ceiling']:continue
     r={**r,'status':'CLAIMED','attempts':r['attempts']+1,'owner':owner,'token':token,'lease_until':later(now,lease_seconds),'batch':key,'history':[*r['history'],{'at':now,'status':'CLAIMED','owner':owner,'attempt':r['attempts']+1}]}
     states.append(('delivery',r['id'],r));updates+=self.native_status(r,'CLAIMED')
    if not states:continue
    ids=[v['id'] for _,_,v in states];key=batch_key(ids)
    claim={'key':key,'ids':ids,'case_id':head['case_id'],'case_key':case,'action':head['action'],'owner':owner,'token':token,'status':'CLAIMED','lease_until':later(now,lease_seconds)}
    for _,_,v in states:v['batch']=key
    self.store.write(s,[*states,('delivery_case',case,claim)],updates=updates);return claim
  return None
 def current(self,claim,*,allow_expired=False):
  c=self.store.get('delivery_case',claim['case_key'])
  if not c or c['token']!=claim['token'] or c['key']!=claim['key'] or c['status'] not in {'CLAIMED','RUNNING','RECOVERY_REQUIRED'}:raise Conflict('STALE_DELIVERY_CLAIM')
  if not allow_expired and timestamp(c['lease_until'])<=timestamp(self.clock()):raise Conflict('DELIVERY_LEASE_EXPIRED')
  return c
 def renew(self,claim):
  with self.repo._session() as s:
   c=self.current(claim);c={**c,'lease_until':later(self.clock(),60)}
   states=[('delivery_case',c['case_key'],c)]
   for id in c['ids']:
    r=self.store.get('delivery',id);states.append(('delivery',id,{**r,'lease_until':c['lease_until']}))
   self.store.write(s,states)
 def running(self,claim):
  with self.repo._session() as s:
   c=self.current(claim)
   if c['status']!='CLAIMED':raise Conflict('ALREADY_DISPATCHED')
   c={**c,'status':'RUNNING'};states=[('delivery_case',c['case_key'],c)];updates=[]
   for id in c['ids']:
    r=self.store.get('delivery',id);r={**r,'status':'RUNNING'};states.append(('delivery',id,r));updates+=self.native_status(r,'RUNNING')
   self.store.write(s,states,updates=updates);return c
 def finish(self,claim,receipt,*,reconciled=False):
  with self.repo._session() as s:
   c=self.current(claim,allow_expired=reconciled)
   if c['status']!='RUNNING' and not (reconciled and c['status']=='RECOVERY_REQUIRED'):raise Conflict('NO_RUNNING_CONSUMER')
   states=[('delivery_consumer',c['key'],{'key':c['key'],'ids':c['ids'],'case_id':c['case_id'],'receipt':receipt,'at':self.clock()}),('delivery_case',c['case_key'],{**c,'status':'DONE'})];updates=[]
   for id in c['ids']:
    r=self.store.get('delivery',id);r={**r,'status':'DONE','receipt':receipt,'history':[*r['history'],{'at':self.clock(),'status':'DONE','batch':c['key']} ]};states.append(('delivery',id,r));updates+=self.native_status(r,'DONE')
   self.store.write(s,states,updates=updates)
 def failed(self,claim,code,*,safe_retry=False):
  with self.repo._session() as s:
   c=self.current(claim,allow_expired=True);states=[];updates=[];status='RECOVERY_REQUIRED'
   for id in c['ids']:
    r=self.store.get('delivery',id);status=('RETRY' if r['attempts']<r['ceiling'] else 'FAILED') if safe_retry else 'RECOVERY_REQUIRED'
    r={**r,'status':status,'due_at':later(self.clock(),backoff(r['attempts'])),'history':[*r['history'],{'at':self.clock(),'status':status,'code':code}]};states.append(('delivery',id,r));updates+=self.native_status(r,status)
   states.append(('delivery_case',c['case_key'],{**c,'status':status}));self.store.write(s,states,updates=updates)
 def replay(self,id,*,operator,reason,ceiling,authorize=False):
  if not authorize or not operator or not reason or len(reason)>512 or not 1<=ceiling<=8:raise ValueError('EXPLICIT_REPLAY_REQUIRED')
  with self.repo._session() as s:
   r=self.store.get('delivery',id)
   if not r or r['status']!='FAILED' or not r.get('event') or ceiling<=r['attempts'] or ceiling<r['ceiling']:raise PreconditionFailed('REPLAY_NOT_SAFE_OR_BUDGET_NOT_INCREASED')
   r={**r,'status':'RETRY','ceiling':ceiling,'due_at':self.clock(),'history':[*r['history'],{'at':self.clock(),'status':'OPERATOR_REPLAY','operator':operator,'reason':reason}]}
   self.store.write(s,[('delivery',id,r)],updates=self.native_status(r,'RETRY'));return r
 def request_resume(self,inv,request_id,*,operator,reason,authorize=False):
  if authorize is not True or not operator or not reason or len(reason)>512:raise PreconditionFailed('EXPLICIT_RESUME_REQUIRED')
  self.repo.get_node(inv,'Investigation');id='RESUME-B15-'+digest([inv,request_id])[:32]
  old=self.store.get('delivery',id)
  if old:return old
  revision=self.repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision")[0][0]
  e=Event(id=id,type='AGENT_RESUME_REQUESTED',entity_id=inv,aggregate_revision=revision,occurred_at=self.clock(),payload_schema_version=1,source_kind='SYNTHETIC',idempotency_key=request_id,actor_id=operator,actor_role='SYSTEM',payload={'investigation_id':inv})
  return self.register(e,'explicit-resume:'+id)
 def monitor(self,inv,due_at,request_id,*,authorize=False):
  if authorize is not True or timestamp(due_at)<timestamp(self.clock()):raise ValueError('EXPLICIT_MONITOR_INTENT_REQUIRED')
  self.repo.get_node(inv,'Investigation');id='MONITOR-B15-'+digest([inv,request_id])[:32]
  with self.repo._session() as s:
   old=self.store.get('delivery_monitor',id)
   value={'id':id,'investigation_id':inv,'due_at':due_at,'request_id':request_id,'status':'PENDING'}
   if old:
    if any(old[k]!=value[k] for k in ['investigation_id','due_at','request_id']):raise Conflict('MONITOR_REQUEST_REUSED')
    return old
   self.store.write(s,[('delivery_monitor',id,value)]);return value
 def due(self):
  for m in self.store.rows('delivery_monitor',100):
   if m['status']=='PENDING' and timestamp(m['due_at'])<=timestamp(self.clock()):
    revision=self.repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision")[0][0]
    e=Event(id=m['id'],type='MONITORING_DUE',entity_id=m['investigation_id'],aggregate_revision=revision,occurred_at=m['due_at'],payload_schema_version=1,source_kind='SYNTHETIC',idempotency_key=m['request_id'],actor_id='civicly-monitor',actor_role='SYSTEM',payload={'investigation_id':m['investigation_id']})
    self.register(e,'monitor:'+m['id'],extra=[('delivery_monitor',m['id'],{**m,'status':'FIRED'})])
