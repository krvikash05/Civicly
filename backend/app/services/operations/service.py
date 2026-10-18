"""Authenticated exact-plan approval/order services; no field execution or worker."""
import json
from app.graph.models import digest
from app.graph.repository import Conflict,PreconditionFailed
from app.graph.schema import utc_now
from app.services.evidence.service import transition
from app.services.evidence.reader import Reader
from app.services.planning.models import PlanDraft
from app.services.planning.policy import validate_remediation
from app.services.planning.service import PlanningBlocked
from .auth import Denied
from .models import Submit,Decide,Order,Update,Binding,OpsRecovery
from .storage import Storage
from .migration import OperationsMigration
from .utility import fulfilled as utility_fulfilled

def stable(prefix,*parts):return prefix+'-B13-'+digest(parts)[:32]
def common(id,at):return {'id':id,'schema_version':3,'municipality_id':'demo-city','created_at':at,'updated_at':at}
def native_hash(kind,props):return digest({'kind':kind,'properties':props})
def scope(command):return Binding.model_validate(command.model_dump(include={'plan_id','plan_version','plan_hash','assignments'})).normalized()
def execution_gates(task,dependency_statuses,fulfilled=frozenset()):
 if task.remediation and any(c.status!='MET' and c.kind not in fulfilled for c in task.remediation.conditions):raise PreconditionFailed('UNMET_EXECUTION_GATES')
 if any(status!='COMPLETED' for status in dependency_statuses):raise PreconditionFailed('UNMET_TASK_DEPENDENCIES')
class Operations:
 def __init__(self,planning,auth,*,clock=utc_now):
  self.planning,self.repo,self.auth,self.clock=planning,planning.repo,auth,clock;self.store=Storage(self.repo)
  if not OperationsMigration(self.repo.client,self.repo.graph.name).status()['ready']:raise PreconditionFailed('OPERATIONS_MIGRATION_REQUIRED')
 def target(self):
  from app.active import is_shared_target
  if self.repo.graph.name!='civicly_knowledge' and not self.repo.graph.name.startswith('civicly_b13_test_') and not is_shared_target(self.repo.graph.name):raise PreconditionFailed('OPERATIONS_TARGET_NOT_AUTHORIZED')
 async def draft(self,value,*,request_id,token):
  self.target();actor=self.auth.require(token,'draft');return await self.planning.create(value,request_id=request_id,actor=actor)
 def projection(self,kind,source):
  if kind not in {'HAS_TASK','ASSIGNED_TO','TARGETS','DEPENDS_ON'}:raise PreconditionFailed('PROJECTION_FAMILY')
  rows=self.repo._read(f'MATCH (:CivicEntity {{id:$id}})-[r:{kind}]->(n:CivicEntity) RETURN r.id,n.id LIMIT 101',{'id':source})
  if len(rows)>100:raise PreconditionFailed('PROJECTION_LIMIT')
  reader=Reader(self.repo,self.clock())
  return [id for edge,id in rows if reader.visible(self.repo.get_relationship(edge).properties)]
 async def validate(self,binding,at,*,review_sources=True,progress=False):
  Reader(self.repo,at).node(binding['plan_id'],'ResolutionPlan')
  saved=self.planning.store.get(binding['plan_id'])
  if not saved:raise PreconditionFailed('PLAN_UNAVAILABLE')
  draft=PlanDraft.model_validate(saved['draft']);receipt=saved['receipt']
  if (binding['plan_version'],binding['plan_hash'])!=(receipt['version'],receipt['plan_hash']):raise PreconditionFailed('PLAN_BINDING_CHANGED')
  head=max(self.planning.store.rows(draft.investigation_id),key=lambda row:row[1])
  if head[0]!=binding['plan_id']:raise PreconditionFailed('PLAN_SUPERSEDED')
  tasks={saved['task_ids'][t.id]:t for t in draft.tasks}
  if {a['task_id'] for a in binding['assignments']}!=set(tasks):raise PreconditionFailed('TASK_SCOPE_CHANGED')
  if sorted(self.projection('HAS_TASK',binding['plan_id']))!=sorted(tasks):raise PreconditionFailed('NATIVE_TASK_SCOPE_CHANGED')
  for a in binding['assignments']:
   t=tasks[a['task_id']];assignee=self.auth.operator(a['assignee_id'])
   if a['action_type']!=t.action_type or sorted(a['target_ids'])!=sorted(t.target_ids) or a['department_id']!=t.department_id:raise PreconditionFailed('APPROVAL_SCOPE_CHANGED')
   if assignee.role!='DEPARTMENT_LEAD' or assignee.department_id!=t.department_id:raise Denied('ASSIGNEE_SCOPE_DENIED')
   native=self.repo.get_node(a['task_id'],'ActionTask')
   if native.properties['action_type']!=t.action_type or native.properties['priority']!=t.priority:raise PreconditionFailed('NATIVE_TASK_CHANGED')
   if self.projection('ASSIGNED_TO',native.id)!=[t.department_id] or sorted(self.projection('TARGETS',native.id))!=sorted(t.target_ids) or sorted(self.projection('DEPENDS_ON',native.id))!=sorted(saved['task_ids'][id] for id in t.depends_on):raise PreconditionFailed('NATIVE_TASK_BINDING_CHANGED')
  if not review_sources:return saved,draft,tasks,{'validated_at':at,'validation_scope':'IMMUTABLE_BINDING_ONLY_REJECTION','causal_validation':'Not authority for work; rejected proposal may have invalid current sources'}
  reader=Reader(self.repo,at);reader.node(draft.investigation_id,'Investigation');assessments=[]
  proposed={e.target for e in reader.edges('PROPOSES',source=draft.investigation_id)}
  for b in draft.basis:
   history=reader.histories(b.hypothesis_id)
   if b.hypothesis_id not in proposed or not history:raise PreconditionFailed('ASSESSMENT_STALE')
   if history[-1].id!=b.assessment_id:
    original=next((a for a in history if a.id==b.assessment_id),None);latest=history[-1]
    if not progress or not original or latest.cause_code!=original.cause_code or latest.assessment!=original.assessment or latest.contradicting_evidence_ids!=original.contradicting_evidence_ids or not set(original.supporting_evidence_ids)<=set(latest.supporting_evidence_ids):raise PreconditionFailed('ASSESSMENT_STALE_REVISED_PLAN_REQUIRED')
   # Immutable plan gates remain bound to their original assessment IDs after
   # the latest assessment has passed the unchanged-meaning check above.
   a=original if progress and history[-1].id!=b.assessment_id else history[-1];assessments.append(a)
   for ref in a.evidence_references:
    if ref.id in draft.evidence_ids:
     current=reader.evidence(ref.id)
     if current.content_hash!=ref.content_hash or current.finding_hashes!=ref.finding_hashes:raise PreconditionFailed('ASSESSMENT_SOURCE_CHANGED')
  memory=self.planning.memory
  before=memory.repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision,m.repo_pending") if memory else None
  proofs={}
  for t in draft.tasks:
   resolution=await self.planning.resolve(t,reader,at)
   original_owners=saved['proof']['tasks'][t.id]['owners']
   current={v['asset_id']:v for v in resolution['owners']}
   if len(current)!=len(original_owners) or any(o['asset_id'] not in current or any(current[o['asset_id']].get(k)!=v for k,v in o.items()) for o in original_owners):raise PreconditionFailed('OWNERSHIP_BINDING_CHANGED_REVISED_PLAN_REQUIRED')
   proofs[t.id]={'resolution':resolution,'remediation':validate_remediation(t,draft,reader,assessments,PlanningBlocked)}
  if memory and before!=memory.repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision,m.repo_pending"):raise PreconditionFailed('SOURCE_REVISION_CHANGED')
  return saved,draft,tasks,{'validated_at':at,'tasks':proofs,'memory_revision':before}
 def approval(self,id,binding):
  a=self.repo.get_node(id,'Approval');v=self.store.get('approval',id)
  op=self.store.get('operation',v['last_operation']) if v else None
  if not v or v['binding']!=binding or not op or op['native_hashes'].get(id)!=digest(a.properties):raise PreconditionFailed('APPROVAL_INTEGRITY_OR_SCOPE')
  if (a.properties['plan_version'],a.properties['plan_hash'])!=(binding['plan_version'],binding['plan_hash']):raise PreconditionFailed('APPROVAL_NATIVE_BINDING')
  return a,v
 def verified_order(self,id):
  v=self.store.get('order',id);w=self.repo.get_node(id,'WorkOrder')
  op=self.store.get('operation',v['last_operation']) if v else None
  if not v or not op or op['native_hashes'].get(id)!=digest(w.properties):raise PreconditionFailed('ORDER_INTEGRITY')
  return w,v
 def read_work_order(self,id,*,token):
  self.target();actor=self.auth.require(token,'read');w,v=self.verified_order(id)
  if not v:raise PreconditionFailed('ORDER_UNAVAILABLE')
  a=v['assignment']
  if actor.role=='DEPARTMENT_LEAD' and (a['department_id']!=actor.department_id or a['assignee_id']!=actor.id):raise Denied('DEPARTMENT_SCOPE_DENIED')
  return {**v,'native':self.repo.get_node(id,'WorkOrder').properties}
 async def execute(self,command,*,token,interrupt=None,reviewer_token=None):
  from .execution_models import COMMANDS
  if (isinstance(command,dict) and command.get("operation") in COMMANDS) or type(command) in set(COMMANDS.values()):
   from .execution import Execution
   return await Execution(self).execute(command,token=token,interrupt=interrupt,reviewer_token=reviewer_token)
  self.target()
  if isinstance(command,dict):
   cls={'submit':Submit,'decide':Decide,'order':Order,'update':Update}.get(command.get('operation'))
   if cls is None:raise PreconditionFailed('OPERATION_UNAVAILABLE')
   command=cls.model_validate(command)
  if type(command) not in {Submit,Decide,Order,Update}:raise PreconditionFailed('CLOSED_COMMAND_REQUIRED')
  q=command;actor=self.auth.require(token,q.operation);at=self.clock()
  value=q.model_dump(mode='json')
  if isinstance(q,Binding):value={**value,**scope(q)}
  request_hash=digest({'actor':actor.model_dump(mode='json'),'command':value});opid=stable('OP',q.request_id)
  with self.repo._session() as session:
   try:old=self.store.get('operation',opid)
   except Exception:raise OpsRecovery(self.repo.graph.name,q.request_id,opid,operation=q.operation,plan_id=getattr(q,'plan_id',None),approval_id=getattr(q,'approval_id',None)) from None
   if old:
    if old['request_hash']!=request_hash:raise Conflict('IDEMPOTENCY_CONFLICT')
    return old['receipt'] # Historical acknowledgment; never authority for a new write.
   nodes=[];updates=[];edges=[];states=[];native_hashes={};events=[]
   def node(kind,props):nodes.append((kind,props));native_hashes[props['id']]=digest(props);return props
   def changed(old,status,**extra):
    transition(old.kind,old.properties['status'],status)
    props={**old.properties,'status':status,'updated_at':at,**extra};updates.append((old,props));native_hashes[old.id]=digest(props);return props
   def edge(kind,a,b):edges.append((kind,a,b,{'id':stable('REL',opid,kind,a,b),'municipality_id':'demo-city','created_at':at}))
   def attest(plan,binding,state):states.append(('plan',plan['id'],{'binding':binding,'state':state,'native_hash':digest(plan),'last_operation':opid}))
   binding=scope(q) if isinstance(q,Binding) else None
   proof={}
   if binding:
    saved,draft,tasks,proof=await self.validate(binding,at,review_sources=not(isinstance(q,Decide) and q.decision=='REJECTED'),progress=isinstance(q,Order));plan=self.repo.get_node(q.plan_id,'ResolutionPlan');inv=draft.investigation_id
   if isinstance(q,Submit):
    if plan.properties['status']!='DRAFT':raise PreconditionFailed('PLAN_NOT_DRAFT')
    aid=stable('APPROVAL',q.plan_id)
    approval=node('Approval',{**common(aid,at),'status':'PENDING','requested_at':at,'requested_by':actor.id,'plan_version':q.plan_version,'plan_hash':q.plan_hash})
    p=changed(plan,'PENDING_APPROVAL',graph_revision=session.revision+1);attest(p,binding,'PENDING_APPROVAL')
    states.append(('approval',aid,{'binding':binding,'submitted_by':actor.id,'proof':proof,'last_operation':opid}))
    if draft.previous_plan_id:
     previous=self.repo.get_node(draft.previous_plan_id,'ResolutionPlan')
     if previous.properties['status']!='SUPERSEDED':
      previous_props=changed(previous,'SUPERSEDED',graph_revision=session.revision+1)
      prior=self.store.get('plan',previous.id);oldbinding=prior['binding'] if prior else {'plan_id':previous.id,'plan_version':previous.properties['version'],'plan_hash':previous.properties['plan_hash']}
      attest(previous_props,oldbinding,'SUPERSEDED')
    result={'id':aid,'plan_id':q.plan_id,'plan_version':q.plan_version,'plan_hash':q.plan_hash,'status':'PENDING','expected_hash':native_hash('Approval',approval),'scope_hash':digest(binding)};subject=aid;event_type='PLAN_SUBMITTED';event_subject=q.plan_id;emitter=inv
   elif isinstance(q,Decide):
    a,v=self.approval(q.approval_id,binding)
    if not v or v['binding']!=binding or actor.id==v['submitted_by']:raise Denied('APPROVAL_BINDING_OR_SELF_APPROVAL')
    if a.content_hash!=q.expected_hash:raise Conflict('STALE_APPROVAL_REVISION')
    if plan.properties['status']!='PENDING_APPROVAL':raise PreconditionFailed('PLAN_NOT_PENDING')
    updated=changed(a,q.decision,decided_at=at,decided_by=actor.id);p=changed(plan,q.decision,graph_revision=session.revision+1);attest(p,binding,q.decision)
    if q.decision=='APPROVED':
     for id in tasks:changed(self.repo.get_node(id,'ActionTask'),'APPROVED')
    states.append(('approval',a.id,{**v,'decided_by':actor.id,'decided_at':at,'decision':q.decision,'reason':q.reason,'proof':proof,'last_operation':opid}))
    result={'id':a.id,'plan_id':q.plan_id,'plan_version':q.plan_version,'plan_hash':q.plan_hash,'status':q.decision,'expected_hash':native_hash('Approval',updated),'scope_hash':digest(binding)};subject=a.id;event_type='PLAN_APPROVED' if q.decision=='APPROVED' else 'PLAN_REJECTED';event_subject=q.plan_id;emitter=inv
   elif isinstance(q,Order):
    a,v=self.approval(q.approval_id,binding)
    if not v or v['binding']!=binding or a.properties['status']!='APPROVED' or v.get('decision')!='APPROVED' or v.get('decided_by')!=a.properties.get('decided_by') or plan.properties['status'] not in {'APPROVED','IN_EXECUTION'}:raise PreconditionFailed('VALID_EXACT_APPROVAL_REQUIRED')
    task=tasks.get(q.task_id)
    if not task:raise PreconditionFailed('TASK_OUTSIDE_APPROVAL')
    execution_gates(task,[self.repo.get_node(saved['task_ids'][id],'ActionTask').properties['status'] for id in task.depends_on],utility_fulfilled(self,task,saved,at))
    if self.repo.get_node(q.task_id,'ActionTask').properties['status']!='APPROVED':raise PreconditionFailed('TASK_NOT_APPROVED')
    assignment=next(a for a in binding['assignments'] if a['task_id']==q.task_id);wid=stable('WO',q.plan_id,q.task_id);prior=self.store.get('order',wid)
    expected={'binding':binding,'approval_id':q.approval_id,'assignment':assignment}
    if prior:
     self.verified_order(wid)
     if any(prior[k]!=v for k,v in expected.items()):raise Conflict('TASK_ORDER_SCOPE_CONFLICT')
     result=prior['creation_receipt'];subject=wid;event_type=None;emitter=wid
    else:
     w=node('WorkOrder',{**common(wid,at),'status':'AUTHORIZED','execution_mode':'SIMULATED','plan_version':q.plan_version,'idempotency_key':q.request_id})
     result={'id':wid,'status':'AUTHORIZED','expected_hash':native_hash('WorkOrder',w),'approval_id':q.approval_id,'task_id':q.task_id,'plan_id':q.plan_id,'department_id':assignment['department_id'],'assignee_id':assignment['assignee_id'],'execution_mode':'SIMULATED'}
     states.append(('order',wid,{**expected,'creation_receipt':result,'proof':proof,'originating_request':q.request_id,'authorized_by':actor.id,'last_operation':opid}))
     edge('IMPLEMENTS',wid,q.task_id);edge('AUTHORIZED_BY',wid,q.approval_id);subject=wid;event_type='WORK_ORDER_CREATED';event_subject=wid;emitter=wid
   else:
    w,v=self.verified_order(q.work_order_id)
    if not v:raise PreconditionFailed('B13_ORDER_REQUIRED')
    assignment=v['assignment']
    if actor.department_id!=assignment['department_id'] or actor.id!=assignment['assignee_id']:raise Denied('DEPARTMENT_SCOPE_DENIED')
    if q.expected_hash!=w.content_hash:raise Conflict('STALE_ORDER_REVISION')
    saved,draft,tasks,proof=await self.validate(v['binding'],at,progress=True);plan=self.repo.get_node(v['binding']['plan_id'],'ResolutionPlan');a,approval_state=self.approval(v['approval_id'],v['binding'])
    if plan.properties['status'] not in {'APPROVED','IN_EXECUTION'} or a.properties['status']!='APPROVED':raise PreconditionFailed('APPROVAL_NO_LONGER_VALID')
    task=tasks[assignment['task_id']]
    execution_gates(task,[self.repo.get_node(saved['task_ids'][id],'ActionTask').properties['status'] for id in task.depends_on],utility_fulfilled(self,task,saved,at))
    if self.repo.get_node(assignment['task_id'],'ActionTask').properties['status']!='APPROVED':raise PreconditionFailed('TASK_NO_LONGER_APPROVED')
    if q.new_status not in {'ASSIGNED','CANCELLED'}:raise PreconditionFailed('B14_EXECUTION_NOT_AVAILABLE')
    updated=changed(w,q.new_status);states.append(('order',w.id,{**v,'last_operation':opid}))
    se=node('StatusEvent',{'id':stable('STATUS',opid),'municipality_id':'demo-city','schema_version':3,'created_at':at,'entity_id':w.id,'from_status':w.properties['status'],'to_status':q.new_status,'occurred_at':at,'actor_type':'HUMAN','actor_id':actor.id,'reason':q.reason})
    edge('HAS_EVENT',w.id,se['id']);subject=w.id;event_type='WORK_ORDER_STATUS_CHANGED';event_subject=w.id;emitter=w.id
    result={'id':w.id,'status':q.new_status,'expected_hash':native_hash('WorkOrder',updated),'status_event_id':se['id']}
   if event_type:
    event={'id':stable('EVENT',opid),'type':event_type,'entity_id':event_subject,'aggregate_revision':session.revision+1,'occurred_at':at,'payload_schema_version':1,'source_kind':'SYNTHETIC','idempotency_key':q.request_id,'actor_id':actor.id,'actor_role':actor.role,'payload':result}
    node('DomainEvent',{**common(event['id'],at),'event_type':event_type,'subject_id':event_subject,'occurred_at':at,'delivery_status':'PENDING','idempotency_key':q.request_id,'payload_ref':'operation:'+opid});edge('EMITTED_EVENT',emitter,event['id']);events=[event]
   operation={'request_id':q.request_id,'request_hash':request_hash,'actor':actor.model_dump(mode='json'),'command':value,'receipt':result,'occurred_at':at,'native_hashes':native_hashes,'events':events,'proof':proof}
   states.append(('operation',opid,operation))
   self.auth.require(token,q.operation) # Revoked/expired sessions fail before dispatch.
   try:
    self.store.commit(session,subject,nodes,updates,edges,states)
    if interrupt=='after_commit':raise RuntimeError('INJECTED_ACK_LOSS')
    if self.store.get('operation',opid)!=operation:raise RuntimeError('READBACK_MISMATCH')
   except Exception:raise OpsRecovery(self.repo.graph.name,q.request_id,subject,operation=q.operation,plan_id=binding['plan_id'] if binding else v['binding']['plan_id'],approval_id=getattr(q,'approval_id',None) or (v.get('approval_id') if q.operation=='update' else result.get('id'))) from None
   return result
