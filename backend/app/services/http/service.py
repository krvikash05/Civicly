"""B16 transport adapter; all mutations delegate to accepted domain services."""
import inspect
from datetime import datetime,timezone
from app.api import models as m
from app.graph.models import digest
from app.graph.repository import Conflict,PreconditionFailed,OutcomeUnknown
from app.services.operations.auth import Denied
from app.services.evidence.models import Actor
from app.services.evidence.service import EvidenceService
from app.services.complaints.service import ComplaintService
from app.services.planning.service import PlanningBlocked
from .reads import Reads
def request_identity(source,actor,key):return 'HTTP-B16-'+digest([source,actor,key])[:32]

class Recovery(OutcomeUnknown):
 def __init__(self,id,entity=None,identities=None):
  self.correlation_id=id;self.entity_id=entity;self.reconciliation={'request_id':id,**({'entity_id':entity} if entity else {}),**(identities or {})};super().__init__('API_RECONCILIATION_REQUIRED')
class Boundary:
 """Request-local outcome evidence, never a second persisted recovery mechanism."""
 def __init__(self,request,entity):
  self.phase='PRE_WRITE';self.before=None;self.journal_id=None
  self.identities={'request_id':request,**({'entity_id':entity} if entity else {})}
 async def invoke(self,repo,call):
  self.phase='CHECKING'
  self.before=repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision,coalesce(m.repo_pending,'')")
  if not self.before or self.before[0][1]:raise OutcomeUnknown('SOURCE_WRITE_UNCERTAIN')
  self.phase='DISPATCHED'
  result=call()
  if inspect.isawaitable(result):result=await result
  self.phase='RETURNED'
  entity=getattr(result,'entity_id',None) or getattr(result,'id',None) or getattr(result,'complaint_id',None)
  if isinstance(result,dict):entity=result.get('entity_id') or result.get('id') or entity
  if entity:self.identities['entity_id']=__import__('pydantic').TypeAdapter(m.ID).validate_python(entity)
  return result
 def no_write(self,repo):
  # An existing request journal may already contain a committed historical receipt.
  # No new revision alone cannot establish non-commit for that request.
  if self.journal_id and repo._node_optional(self.journal_id) is not None:return False
  return bool(self.before and not self.before[0][1] and self.before==repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision,coalesce(m.repo_pending,'')"))

class Services:
 def __init__(self,profile,profile_path,repo,auth,ops,delivery,clock,*,memory=None):
  if repo.graph.name!=profile.graph or ops.repo is not repo or delivery.repo is not repo:raise ValueError('EXACT_SERVICE_SOURCE_REQUIRED')
  self.profile,self.profile_path,self.repo,self.auth,self.ops,self.delivery,self.clock=profile,profile_path,repo,auth,ops,delivery,clock
  self.reads=Reads(repo,ops,delivery,clock,memory)
 def identity(self,actor):return {'id':actor.id,'display_name':'Synthetic '+actor.id,'role':actor.role,'department_id':actor.department_id,'enabled':True}
 def login(self,body):
  token=self.auth.login(body.operator_id,body.demo_password.get_secret_value());actor=self.auth.resolve(token)
  return {'access_token':token,'expires_at':datetime.fromtimestamp(self.auth.clock()+1800,timezone.utc).isoformat().replace('+00:00','Z'),'operator_id':actor.id,'role':actor.role}
 async def health(self,ready=False):
  checks={'api':'ready','graph':'not_checked','delivery':'not_checked','mcp':'not_checked','checkpoint':'not_checked','memory':'not_checked','auth':'not_checked'}
  if ready:
   for key,fn in [('graph',lambda:self.repo.client.connection.ping()),('delivery',self.delivery.active),('auth',lambda:self.auth.operator('OP-ANALYST'))]:
    try:assert fn();checks[key]='ready'
    except Exception:checks[key]='unavailable'
   try:
    from app.agents.checkpoints import saver
    saver(self.profile).get_tuple({'configurable':{'thread_id':'B16-READINESS-NONEXISTENT'}});checks['checkpoint']='ready'
   except Exception:checks['checkpoint']='unavailable'
   try:
    from app.agents.mcp import brokers
    async with brokers(self.profile,self.profile_path,timeout=3) as tools:assert tools.catalog()
    checks['mcp']='ready'
   except Exception:checks['mcp']='unavailable'
   try:assert self.reads.memory is not None;self.reads.memory.store.all();checks['memory']='ready'
   except Exception:checks['memory']='unavailable'
  return {'status':'unavailable' if 'unavailable' in checks.values() else 'ok','dependencies':checks}
 async def command(self,name,path,id,body,actor,token,key,model,reviewer_token=None,field_token=None):
  if not key or len(key)>200 or any(ord(c)<33 or ord(c)>126 for c in key):raise ValueError('IDEMPOTENCY_KEY_REQUIRED')
  if id is not None:__import__('pydantic').TypeAdapter(m.ID).validate_python(id)
  if actor.role=='DEPARTMENT_LEAD' and name in {'update','progress','inspect'}:self.reads.node(id,'WorkOrder',actor,token)
  field=self.auth.resolve(field_token) if field_token else None
  value=body.model_dump(mode='json');reviewer=self.auth.resolve(reviewer_token) if reviewer_token else None
  if reviewer and reviewer.role!='ANALYST':raise Denied('INDEPENDENT_ANALYST_REQUIRED')
  if reviewer and reviewer.id==actor.id:raise Denied('INDEPENDENT_ANALYST_REQUIRED')
  if name=='open':
   for incident in value['incident_ids']:self.reads.node(incident,'Incident',actor,token)
   self.reads.node(value['cluster_id'],'ProblemCluster',actor,token)
  if name in {'transition_inspection','report_inspection'}:self.reads.node(id,'Inspection',actor,token)
  request=request_identity(self.profile.graph,actor.id,key);sha=digest([actor.id,path,id,value,reviewer.id if reviewer else None]+([field.id if field else None] if name=='demo_advance' else []))
  store=self.delivery.store
  with self.repo._session() as session:
   prior=store.get('api_request',request)
   if prior:
    if prior['hash']!=sha:raise Conflict('IDEMPOTENCY_CONFLICT')
    if prior['status']=='DONE':
     try:return model.model_validate(prior['response']).model_dump(mode='json')
     except Exception:raise Recovery(request,prior.get('entity_id'),prior.get('recovery',{}).get('identities')) from None
    if prior['status']!='REJECTED':raise Recovery(request,prior.get('entity_id'),prior.get('recovery',{}).get('identities'))
   row={'id':request,'hash':sha,'actor_id':actor.id,'status':'DISPATCHING','path':path,'entity_id':id}
   store.write(session,[('api_request',request,row)])
  boundary=Boundary(request,id)
  for key in ['investigation_id','plan_id']:
   identity=value.get(key) or value.get('draft',{}).get(key)
   if identity:boundary.identities[key]=__import__('pydantic').TypeAdapter(m.ID).validate_python(identity)
  try:
   self.auth.resolve(token)
   if name in {'demo_reset','demo_advance'}:
    from app.services.demo.service import Demo
    demo=Demo(self,token)
    if name=='demo_reset':
     demo.prepare_reset(value,actor)
     result=await boundary.invoke(self.repo,lambda:demo.reset(value,actor,request))
    else:
     if value['stage']=='EVIDENCE_REVEALED' and field:
      from app.services.evidence.writer import stable
      boundary.journal_id=stable('EV-JOURNAL',field.id,request);boundary.journal_actor=field.id
      if value['inspection_id']:boundary.identities['entity_id']=value['inspection_id']
     prepared=await demo.prepare_advance(id,value,actor,field,reviewer)
     result=await boundary.invoke(self.repo,lambda:demo.advance(id,value,actor,field,reviewer,request,prepared))
   else:result=await self.dispatch(name,id,value,actor,token,request,reviewer_token,boundary)
  except Exception as error:
   # Exception classes are never proof of non-commit after an invocation. Only
   # explicit pre-write phase, or known rejection + unchanged audited source, is.
   rejected=boundary.phase=='PRE_WRITE' and isinstance(error,(Conflict,PreconditionFailed,Denied,ValueError)) and not isinstance(error,OutcomeUnknown)
   if boundary.phase=='DISPATCHED' and isinstance(error,(Conflict,PreconditionFailed,Denied,PlanningBlocked)):
    try:rejected=boundary.no_write(self.repo)
    except Exception:rejected=False
   if rejected:
    with self.repo._session() as session:store.write(session,[('api_request',request,{**row,'status':'REJECTED'})])
    raise
   raise self.recovery(request,row,boundary,error) from None
  # Projection/schema/receipt persistence is post-dispatch: never claim rejection.
  try:
   result=model.model_validate(result).model_dump(mode='json')
   with self.repo._session() as session:store.write(session,[('api_request',request,{**row,'status':'DONE','response':result})])
   return result
  except Exception as error:raise self.recovery(request,row,boundary,error) from None
 def recovery(self,request,row,boundary,error):
  identities=dict(boundary.identities)
  for key in ['entity_id','investigation_id','plan_id']:
   value=getattr(error,'reconciliation',{}).get(key)
   if value is not None:
    try:identities[key]=__import__('pydantic').TypeAdapter(m.ID).validate_python(value)
    except Exception:pass
  if boundary.journal_id:
   try:
    from app.services.evidence.models import Journal
    journal=Journal.model_validate_json(self.repo.get_node(boundary.journal_id,'Evidence').properties['summary'])
    if journal.state=='COMMITTED' and journal.command['request_id']==request and journal.actor.id==getattr(boundary,'journal_actor',row['actor_id']) and journal.receipt.graph==self.repo.graph.name:
     identities['entity_id']=journal.receipt.entity_id
     if journal.command['operation']=='open':identities['investigation_id']=journal.receipt.entity_id
     elif journal.command.get('investigation_id'):identities['investigation_id']=journal.command['investigation_id']
   except Exception:pass # Unreadable/missing evidence is uncertainty, not absence.
  detail={'phase':boundary.phase,'identities':identities,**({'journal_id':boundary.journal_id} if boundary.journal_id else {})}
  try:
   state=self.repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN coalesce(m.repo_pending,'')")
   if not state or state[0][0]:return Recovery(request,identities=identities)
   with self.repo._session() as session:self.delivery.store.write(session,[('api_request',request,{**row,'recovery':detail})])
  except Exception:pass # Last durable DISPATCHING intent remains; no feedback guarantee.
  return Recovery(request,identities=identities)
 async def dispatch(self,name,id,v,actor,token,request,reviewer_token,boundary):
  reads=self.reads;ev=EvidenceService(self.repo,clock=self.clock)
  if name in {'responsibility_submit','responsibility_review'}:
   from app.services.responsibility.service import Responsibility,identity
   service=Responsibility(self.repo,self.auth,clock=self.clock);operation=name.removeprefix('responsibility_')
   q,_=service.prepare(operation,id,v,token)
   boundary.identities['entity_id']=identity(self.repo.graph.name,q) if operation=='submit' else id
   return await boundary.invoke(self.repo,lambda:service.execute(operation,id,v,request_id=request,token=token))
  if name=='intake':
   from app.services.complaints.models import normalize
   from app.services.complaints.service import stable
   q,_=normalize(v['complaint']) # Pure validation, before any invocation.
   boundary.journal_id=stable('EV-B08',q.source_kind,q.source_id,q.external_record_id)
   result=await boundary.invoke(self.repo,lambda:ComplaintService(self.repo,clock=self.clock).intake(v['complaint']));return reads.get(result.complaint_id,'Complaint',actor,token)
  if name=='open':
   self.delivery.active() # Must be set up explicitly before mutation.
   q={**v,'operation':'open','request_id':request}
   from app.services.evidence.models import parse_command
   from app.services.evidence.writer import stable
   q=parse_command(q);ev.authorize(q,actor);boundary.journal_id=stable('EV-JOURNAL',actor.id,request)
   if hasattr(q,'expected_hash'):
    target=getattr(q,'inspection_id',None) or q.hypothesis_id
    if self.repo.get_node(target).content_hash!=q.expected_hash:raise Conflict('STALE_DOMAIN_REVISION')
   result=await boundary.invoke(self.repo,lambda:ev.execute(q.model_dump(mode='json'),actor))
   self.delivery.request_resume(result.entity_id,request,operator=actor.id,reason='Authenticated API case creation',authorize=True)
   return reads.get(result.entity_id,'Investigation',actor,token)
  if name=='resume':
   reads.node(id,'Investigation',actor,token)
   row=await boundary.invoke(self.repo,lambda:self.delivery.request_resume(id,request,operator=actor.id,reason=v['reason'],authorize=True))
   return {'investigation_id':id,'accepted':True,'event_id':row['id'],'status':row['status']}
  if name=='draft':
   result=await boundary.invoke(self.repo,lambda:self.ops.draft(v['draft'],request_id=request,token=token));return reads.get(result.id,'ResolutionPlan',actor,token)
  if name in {'propose','assess','request_inspection','transition_inspection','report_inspection'}:
   q={**v,'operation':name,'request_id':request}
   if name=='propose':q['investigation_id']=id
   elif name=='assess':q['hypothesis_id']=id
   elif name in {'transition_inspection','report_inspection'}:
    reads.node(id,'Inspection',actor,token);q['inspection_id']=id
    if name=='transition_inspection' and v['status']!='REQUESTED' and actor.role!='DEPARTMENT_LEAD':raise Denied('FIELD_TRANSITION_REQUIRES_ASSIGNED_DEPARTMENT')
   # B09 standalone reports are unreviewed. Reviewed operational reports must use
   # the existing B14 inspect command with independent authenticated header.
   from app.services.evidence.models import parse_command
   from app.services.evidence.writer import stable
   q=parse_command(q);ev.authorize(q,actor);boundary.journal_id=stable('EV-JOURNAL',actor.id,request)
   if hasattr(q,'expected_hash'):
    target=getattr(q,'inspection_id',None) or q.hypothesis_id
    if self.repo.get_node(target).content_hash!=q.expected_hash:raise Conflict('STALE_DOMAIN_REVISION')
   result=await boundary.invoke(self.repo,lambda:ev.execute(q.model_dump(mode='json'),actor))
   if name in {'propose','assess'}:return {'status':result.entity_id}
   return reads.get(result.entity_id,'Evidence' if name=='report_inspection' else 'Inspection',actor,token)
  if name in {'submit','decide','order','update','progress','inspect','evaluate','recur'}:
   q={**v,'operation':name,'request_id':request}
   if name=='submit':q['plan_id']=id
   elif name=='decide':q['approval_id']=id
   elif name!='order':q['work_order_id']=id
   if name=='inspect':q['command']={**q['command'],'request_id':request}
   from app.services.operations.models import Submit,Decide,Order,Update
   from app.services.operations.execution_models import COMMANDS
   cls={'submit':Submit,'decide':Decide,'order':Order,'update':Update,**COMMANDS}[name]
   q=cls.model_validate(q).model_dump(mode='json')
   result=await boundary.invoke(self.repo,lambda:self.ops.execute(q,token=token,reviewer_token=reviewer_token))
   if name=='inspect':return {'status':result['entity_id']}
   if name in {'evaluate','recur'}:return reads.outcome(result)
   kind='Approval' if name in {'submit','decide'} else 'WorkOrder'
   return reads.get(result['id'],kind,actor,token)
  raise ValueError('CLOSED_API_COMMAND')
 async def read(self,name,id,actor,token,limit,cursor):
  r=self.reads
  if name=='responsibility_get':
   from app.services.responsibility.service import Responsibility
   return Responsibility(self.repo,self.auth,clock=self.clock).get(id,token=token)
  if name=='demo_catalog':
   from app.services.demo.service import Demo
   return Demo(self).catalog()
  if name.startswith('get:'):return r.get(id,name.split(':')[1],actor,token)
  if name.startswith('list:'):return r.list(name.split(':')[1],actor,token,limit,cursor)
  if name=='plans':return r.plans(id,actor,token,limit,cursor)
  if name=='document':return await r.document(id,actor,token)
  if name=='procedures':return await r.procedures(actor,token,limit,cursor)
  if name=='memory':return r.case_memory(id,actor,token,limit,cursor)
  if name=='monitoring':return r.monitoring(actor,token,limit,cursor)
  if name=='outcomes':return r.outcomes(id,actor,token,limit,cursor)
  raise ValueError('CLOSED_API_READ')
