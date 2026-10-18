"""B14 explicit domain handlers; reuse B09/B08 planners and existing fenced storage."""
import json
from app.graph.models import digest
from app.graph.repository import PreconditionFailed, Conflict
from app.graph.schema import timestamp
from app.services.evidence.service import EvidenceService, transition
from app.services.evidence.reader import Reader
from app.services.evidence.models import (RequestInspection, TransitionInspection, ReportInspection,
    Assess, Review, Journal, Receipt)
from app.services.evidence.writer import stable as evidence_id, common as evidence_common
from .models import OpsRecovery
from .auth import Denied
from .service import stable, common, native_hash, execution_gates
from .execution_models import COMMANDS, Progress, Inspect, Evaluate, Recur
from .verification import VERSION, REQUIRED, CODES, validate_observation, evaluate
from . import utility

class Execution:
 def __init__(self,ops):self.ops=ops;self.repo=ops.repo;self.store=ops.store
 async def execute(self,payload,*,token,interrupt=None,reviewer_token=None):
  self.ops.target()
  q=COMMANDS[payload['operation']].model_validate(payload) if isinstance(payload,dict) else payload
  if type(q) not in set(COMMANDS.values()):raise PreconditionFailed('CLOSED_COMMAND_REQUIRED')
  actor=self.ops.auth.require(token,q.operation);reviewer=None
  if reviewer_token is not None:
   reviewer=self.ops.auth.require(reviewer_token,'draft')
   if reviewer.id==actor.id:raise Denied('INDEPENDENT_REVIEW_REQUIRED')
  at=self.ops.clock();timestamp(at)
  value=q.model_dump(mode='json')
  if len(json.dumps(value).encode())>32768:raise PreconditionFailed('EXECUTION_REQUEST_LIMIT')
  request_hash=digest({'actor':actor.model_dump(mode='json'),'command':value,'reviewer':reviewer.id if reviewer else None})
  opid=stable('OP',q.request_id)
  with self.repo._session() as session:
   try:old=self.store.get('operation',opid)
   except Exception:raise OpsRecovery(self.repo.graph.name,q.request_id,q.work_order_id,operation=q.operation) from None
   if old:
    if old['request_hash']!=request_hash:raise Conflict('IDEMPOTENCY_CONFLICT')
    return old['receipt']
   w,v=self.ops.verified_order(q.work_order_id)
   if w.content_hash!=q.expected_hash:raise Conflict('STALE_ORDER_REVISION')
   binding=v['binding'];assignment=v['assignment']
   is_assessment=isinstance(q,Inspect) and isinstance(q.command,Assess)
   if isinstance(q,Progress) or (isinstance(q,Inspect) and not is_assessment):
    if actor.id!=assignment['assignee_id'] or actor.department_id!=assignment['department_id']:raise Denied('DEPARTMENT_SCOPE_DENIED')
   elif actor.role!='ANALYST':raise Denied('INDEPENDENT_ANALYST_REQUIRED')
   saved,draft,tasks,proof=await self.ops.validate(binding,at,review_sources=isinstance(q,Progress) and q.action=='START',progress=True)
   if not (isinstance(q,Progress) and q.action=='START'):
    proof={'validated_at':at,'validation_scope':'IMMUTABLE_BINDING_RECORD_EXISTING_WORK_OR_MONITOR','causal_validation':'Not authority to start further work; ownership and procedure separately rechecked'}
   approval,av=self.ops.approval(v['approval_id'],binding)
   plan=self.repo.get_node(binding['plan_id'],'ResolutionPlan')
   if approval.properties['status']!='APPROVED' or av.get('decision')!='APPROVED' or av.get('decided_by')!=approval.properties.get('decided_by') or plan.properties['status'] not in {'APPROVED','IN_EXECUTION','MONITORING','COMPLETED'}:raise PreconditionFailed('APPROVAL_NO_LONGER_VALID')
   task=tasks[assignment['task_id']];task_node=self.repo.get_node(assignment['task_id'],'ActionTask')
   reader=Reader(self.repo,at);inv=reader.node(draft.investigation_id,'Investigation')
   # Binding-only evidence/result recording still verifies current ownership/procedure.
   await self.ops.planning.resolve(task,reader,at)
   nodes=[];updates={};edges=[];states=[];hashes={};transitions=[]
   def node(kind,props):nodes.append((kind,props));hashes[props['id']]=digest(props);return props
   def changed(old,sequence,**extra):
    seq=[sequence] if isinstance(sequence,str) else sequence
    state=old.properties['status']
    for new in seq:transition(old.kind,state,new);transitions.append([old.id,state,new]);state=new
    props={**old.properties,'status':state,'updated_at':at,**extra};updates[old.id]=(old,props);hashes[old.id]=digest(props)
    if old.kind=='ResolutionPlan':states.append(('plan',old.id,{'binding':binding,'state':state,'native_hash':digest(props),'last_operation':opid}))
    return props
   def edge(kind,a,b,source=None):
    props={'id':stable('REL',opid,kind,a,b),'municipality_id':'demo-city','created_at':at,'valid_from':at}
    if source:props['source_evidence_id']=source
    edges.append((kind,a,b,props))
   def state_event(old,status,reason):
    props={'id':stable('STATUS',opid,old.id),'schema_version':3,'municipality_id':'demo-city','created_at':at,'entity_id':old.id,'from_status':old.properties['status'],'to_status':status,'occurred_at':at,'actor_type':'HUMAN','actor_id':actor.id,'reason':reason}
    node('StatusEvent',props);edge('HAS_EVENT',old.id,props['id'])
   def reports(ids,purpose):
    if len(ids)!=len(set(ids)):raise PreconditionFailed('DUPLICATE_EVIDENCE')
    refs=[]
    for id in ids:
     ref=reader.evidence(id);report=ref.report
     auth=self.store.get('inspection',report.inspection_id) if report else None
     if not report or not report.review or report.source_kind!='SYNTHETIC' or report.inspector_id!=assignment['assignee_id'] or not auth or auth['work_order_id']!=w.id or auth['purpose']!=purpose or auth['procedure']!=task.procedure_citation.model_dump(mode='json'):raise PreconditionFailed('ATTRIBUTABLE_WORK_REPORT_REQUIRED')
     refs.append(ref)
    return refs
   def outcome(status,result,refs,window=None,gaps=None):
    id=stable('OUTCOME',opid)
    node('InterventionOutcome',{'id':id,'municipality_id':'demo-city','schema_version':3,'created_at':at,'evaluated_at':at,'result':result,'assessment_status':status})
    edge('RESULTED_IN',w.id,id,refs[0].id if refs else None)
    metadata={'id':id,'work_order_id':w.id,'plan_id':plan.id,'approval_id':approval.id,'policy_version':utility.VERSION if task.action_type in {'UTILITY_ISOLATION','UTILITY_LEAK_REPAIR'} else VERSION,'assessment_status':status,'result':result,'evidence_references':[r.model_dump(mode='json') for r in refs],'window':window,'gaps':gaps or [],'actor_id':actor.id,'evaluated_at':at,'execution_mode':'SIMULATED','last_operation':opid}
    states.append(('outcome',id,metadata));return metadata
   event_type='WORK_ORDER_STATUS_CHANGED';event_subject=w.id;emitter=w.id
   if isinstance(q,Progress):
    if plan.properties['status'] not in {'APPROVED','IN_EXECUTION'}:raise PreconditionFailed('PLAN_NOT_EXECUTABLE')
    if q.action=='START':
     execution_gates(task,[self.repo.get_node(saved['task_ids'][id],'ActionTask').properties['status'] for id in task.depends_on],utility.fulfilled(self.ops,task,saved,at))
     if q.evidence_ids:raise PreconditionFailed('START_HAS_NO_RESULT')
     tseq=['QUEUED','IN_PROGRESS'] if task_node.properties['status'] in {'APPROVED','BLOCKED'} else []
     if not tseq:raise PreconditionFailed('TASK_NOT_STARTABLE')
     wseq=['ASSIGNED','IN_PROGRESS'] if w.properties['status']=='BLOCKED' and task_node.properties['status']=='BLOCKED' else ['IN_PROGRESS']
     changed(task_node,tseq);updated=changed(w,wseq)
     if plan.properties['status']=='APPROVED':changed(plan,'IN_EXECUTION',graph_revision=session.revision+1)
    else:
     if w.properties['status']!='IN_PROGRESS' or task_node.properties['status']!='IN_PROGRESS':raise PreconditionFailed('WORK_NOT_IN_PROGRESS')
     if q.action in {'COMPLETE','FAIL'}:
      refs=reports(q.evidence_ids,'COMPLETION');code='ACTION_COMPLETED' if q.action=='COMPLETE' else 'ACTION_FAILED'
      covered=set()
      for ref in refs:
       for ob in ref.report.observations:
        if ob.code==code and ob.result=='OBSERVED' and timestamp(ob.observed_at)>=timestamp(w.properties['updated_at']):covered.add(ob.asset_id)
      if covered!=set(task.target_ids):raise PreconditionFailed('RESULT_EVIDENCE_TARGET_COVERAGE')
      if q.action=='COMPLETE' and task.action_type=='UTILITY_ISOLATION':utility.isolation_proof(refs,task.target_ids,w.properties['updated_at'])
      states.append(('completion',w.id,{'at':at,'evidence_ids':q.evidence_ids,'source_records':[ref.source_record_id for ref in refs],'last_operation':opid,'action':q.action}))
      if q.action=='FAIL':
       result=outcome('INTERVENTION_FAILED','INCONCLUSIVE',refs,gaps=[q.reason]);event_type='INTERVENTION_OUTCOME_RECORDED'
      changed(task_node,'COMPLETED' if q.action=='COMPLETE' else 'FAILED');updated=changed(w,'COMPLETED' if q.action=='COMPLETE' else 'BLOCKED')
      if q.action=='COMPLETE':
       result=outcome('MONITORING','ACTION_COMPLETED',refs,gaps=['Work completed; independent follow-up required']);event_type='INTERVENTION_OUTCOME_RECORDED'
       if all(id==task_node.id or self.repo.get_node(id,'ActionTask').properties['status']=='COMPLETED' for id in tasks):
        changed(plan,'MONITORING',graph_revision=session.revision+1)
        state=inv.properties['status']
        if state!='MONITORING':changed(inv,['INVESTIGATING','MONITORING'] if state=='OPEN' else ['MONITORING'])
        for e in reader.edges('INVESTIGATES',source=inv.id):
         target=reader.node(e.target)
         if target.kind=='ProblemCluster' and target.properties['status'] in {'OPEN','REOPENED'}:changed(target,'MONITORING')
     else:changed(task_node,'BLOCKED');updated=changed(w,'BLOCKED')
    state_event(w,updated['status'],q.reason)
    result={**(result if q.action in {'COMPLETE','FAIL'} else {}),'id':w.id,'status':updated['status'],'expected_hash':native_hash('WorkOrder',updated),'task_status':updates[task_node.id][1]['status'],'reason':q.reason,'simulation_mode':True}
   elif isinstance(q,Inspect):
    c=q.command;ev=EvidenceService(self.repo,clock=self.ops.clock);ev.authorize(c,actor)
    if c.request_id!=q.request_id:raise PreconditionFailed('NESTED_REQUEST_ID_MISMATCH')
    if isinstance(c,Assess):
     if q.purpose!='ASSESSMENT' or actor.role!='ANALYST' or c.hypothesis_id not in {b.hypothesis_id for b in draft.basis}:raise Denied('ASSESSMENT_SCOPE')
    else:
     if q.purpose=='ASSESSMENT':raise PreconditionFailed('INSPECTION_PURPOSE')
     if (q.purpose=='COMPLETION' and w.properties['status']!='IN_PROGRESS') or (q.purpose=='FOLLOWUP' and w.properties['status']!='COMPLETED'):raise PreconditionFailed('INSPECTION_WORK_STATE')
     if isinstance(c,RequestInspection):
      if set(c.asset_ids)!=set(task.target_ids) or c.department_id!=task.department_id or c.investigation_id!=draft.investigation_id or c.inspection_type!=('B14_FOLLOWUP' if q.purpose=='FOLLOWUP' else task.action_type):raise PreconditionFailed('INSPECTION_EXACT_TASK_PROCEDURE')
     else:
      bound=self.store.get('inspection',c.inspection_id)
      if not bound or bound['work_order_id']!=w.id or bound['purpose']!=q.purpose or bound['procedure']!=task.procedure_citation.model_dump(mode='json'):raise PreconditionFailed('INSPECTION_WORK_BINDING')
     if isinstance(c,ReportInspection):
      if c.review is not None or not reviewer or not q.review_reason or c.source_kind!='SYNTHETIC':raise Denied('AUTHENTICATED_INDEPENDENT_REVIEW_REQUIRED')
      from app.services.evidence.policies import POLICIES
      from app.services.planning.policy import ACTIONS
      allowed=set(REQUIRED[draft.issue]) if q.purpose=='FOLLOWUP' else {'ACTION_COMPLETED','ACTION_FAILED'}|{code for p in POLICIES[draft.issue].values() for key in ['confirming','falsifying'] for code in p[key]}|{p['safety_code'] for p in ACTIONS.values() if p['issue']==draft.issue}
      if task.action_type=='UTILITY_ISOLATION' and q.purpose=='COMPLETION':allowed.add(utility.ISOLATION)
      if task.action_type=='UTILITY_LEAK_REPAIR' and q.purpose=='FOLLOWUP':allowed=set(utility.FOLLOWUP)
      for ob in c.observations:validate_observation(ob,allowed)
      c=c.model_copy(update={'review':Review(reviewer_id=reviewer.id,role='ANALYST',reviewed=True,reason=q.review_reason)})
    jid=evidence_id('EV-JOURNAL',actor.id,c.request_id)
    if self.repo._node_optional(jid):raise Conflict('INSPECTION_REQUEST_ALREADY_REPRESENTED')
    entity,new,changed_nodes,links,assessment=ev.plan(c,actor,reader,jid,at,session.revision)
    receipt=Receipt(operation=c.operation,journal_id=jid,entity_id=entity,graph=self.repo.graph.name,graph_revision=session.revision+1,recorded_at=at,created_ids=[n.id for n in new],relationship_ids=[e.id for e in links],updated_ids=[n.id for n in changed_nodes],assessment=assessment)
    journal=Journal(state='COMMITTED',request_hash=digest({'actor':actor.model_dump(mode='json'),'command':c.model_dump(mode='json')}),actor=actor,command=c.model_dump(mode='json'),receipt=receipt)
    node('Evidence',{**evidence_common(jid,at),'evidence_type':'B09_OPERATION','summary':journal.serialized(),'reliability':'UNVERIFIED','recorded_at':at,'source_kind':'USER','source_record_id':actor.id+':'+c.request_id})
    for n in new:node(n.kind,n.properties)
    for n in changed_nodes:
     old=self.repo.get_node(n.id);updates[n.id]=(old,n.properties);hashes[n.id]=digest(n.properties)
    edges.extend((e.kind,e.source,e.target,e.properties) for e in links)
    if isinstance(c,RequestInspection):states.append(('inspection',entity,{'work_order_id':w.id,'purpose':q.purpose,'procedure':task.procedure_citation.model_dump(mode='json'),'last_operation':opid}))
    result=receipt.model_dump(mode='json');event_type='INSPECTION_RESULT_RECORDED' if isinstance(c,ReportInspection) else 'HYPOTHESIS_ASSESSED' if isinstance(c,Assess) else 'GRAPH_EVIDENCE_CHANGED'
   else:
    if task.action_type=='UTILITY_ISOLATION':raise PreconditionFailed('ISOLATION_NOT_CASE_RESOLUTION')
    if w.properties['status']!='COMPLETED':raise PreconditionFailed('COMPLETED_INTERVENTION_REQUIRED')
    completion=self.store.get('completion',w.id)
    if not completion or completion['action']!='COMPLETE':raise PreconditionFailed('COMPLETION_ATTESTATION_REQUIRED')
    refs=reports(q.evidence_ids,'FOLLOWUP');observations=[]
    for ref in refs:
     if ref.source_record_id in completion['source_records']:raise PreconditionFailed('INDEPENDENT_FOLLOWUP_SOURCE_REQUIRED')
     observations.extend(ref.report.observations)
    utility_component=task.action_type=='UTILITY_LEAK_REPAIR'
    if utility_component and isinstance(q,Recur):raise PreconditionFailed('UTILITY_COMPONENT_NOT_CASE_RESOLUTION')
    status,gaps=utility.evaluate(task.target_ids,observations,q.window_start,q.window_end,completion['at'],at) if utility_component else evaluate(draft.issue,task.target_ids,observations,q.window_start,q.window_end,completion['at'],at)
    if isinstance(q,Recur):
     prior=self.store.get('outcome',q.verified_outcome_id)
     if not prior or prior['work_order_id']!=w.id or prior['assessment_status']!='RESOLUTION_VERIFIED' or plan.properties['status']!='COMPLETED':raise PreconditionFailed('PRIOR_VERIFIED_OUTCOME_REQUIRED')
     if status!='PROBLEM_PERSISTS' or timestamp(q.window_start)<=timestamp(prior['evaluated_at']):raise PreconditionFailed('QUALIFYING_LATER_RECURRENCE_REQUIRED')
     from app.services.complaints.models import normalize,Journal as IntakeJournal
     from app.services.complaints.service import ComplaintService,stable as intake_id
     intake=ComplaintService(self.repo,clock=self.ops.clock);iq,norm=normalize(q.complaint)
     old_incidents=[reader.node(e.target) for e in reader.edges('INVESTIGATES',source=inv.id) if reader.node(e.target).kind=='Incident']
     if not old_incidents or any(n.properties['status']!='ENDED' for n in old_incidents):raise PreconditionFailed('RECURRENCE_REQUIRES_RECORDED_END')
     locations={e.target for n in old_incidents for e in self.repo._edges('OCCURRED_AT') if e.source==n.id}
     if iq.source_kind!='SYNTHETIC' or iq.issue_type!=draft.issue or set(iq.asset_ids)!=set(task.target_ids) or iq.location_id not in locations or not timestamp(q.window_start)<=timestamp(iq.occurred_at)<=timestamp(q.window_end) or set(iq.evidence_ids)!=set(q.evidence_ids) or timestamp(iq.reported_at)>timestamp(at):raise PreconditionFailed('RECURRENCE_OCCURRENCE_SCOPE')
     jid=intake_id('EV-B08',iq.source_kind,iq.source_id,iq.external_record_id)
     if self.repo._node_optional(jid):raise Conflict('RECURRENCE_SOURCE_ALREADY_REPRESENTED')
     prepared=IntakeJournal(operation='INTAKE',original=norm.original,canonical=norm.canonical,request_hash=norm.request_hash)
     planned_journal={**common(jid,at),'evidence_type':'COMPLAINT_INTAKE','summary':prepared.serialized(),'reliability':'UNVERIFIED','recorded_at':at,'source_kind':'SYNTHETIC','source_record_id':iq.source_id+':'+iq.external_record_id}
     intake_result,new,changes,links=intake.plan(iq,norm,at,session.revision+1,planned_journal=planned_journal)
     clusters={e.target for e in reader.edges('INVESTIGATES',source=inv.id) if reader.node(e.target).kind=='ProblemCluster'}
     if intake_result.classification!='AFTER_RECORDED_END' or not intake_result.created_incident or intake_result.cluster_id not in clusters:raise PreconditionFailed('RECURRENCE_CLASSIFICATION')
     j=IntakeJournal(operation='INTAKE',original=norm.original,canonical=norm.canonical,request_hash=norm.request_hash,state='COMMITTED',receipt=intake_result.model_dump(mode='json'))
     node('Evidence',{**common(jid,at),'evidence_type':'COMPLAINT_INTAKE','summary':j.serialized(),'reliability':'UNVERIFIED','recorded_at':at,'source_kind':'SYNTHETIC','source_record_id':iq.source_id+':'+iq.external_record_id})
     for n in new:node(n.kind,n.properties)
     for n in changes:
      old=self.repo.get_node(n.id)
      if old.kind=='ProblemCluster':
       transition(old.kind,old.properties['status'],'REOPENED');n=n.model_copy(update={'properties':{**n.properties,'status':'REOPENED'}})
      updates[n.id]=(old,n.properties);hashes[n.id]=digest(n.properties)
     edges.extend((e.kind,e.source,e.target,e.properties) for e in links)
     if len(old_incidents)>=3:raise PreconditionFailed('RECURRENCE_INVESTIGATION_SCOPE_LIMIT')
     edge('INVESTIGATES',inv.id,intake_result.incident_id,jid)
     scope_link=edges[-1][3]['id']
     changed(inv,'REOPENED');status='RECURRENCE_DETECTED';event_type='RECURRENCE_DETECTED'
     result=outcome(status,'INCONCLUSIVE',refs,{'start':q.window_start,'end':q.window_end},gaps)
     result.update(investigation_id=inv.id,investigates_relationship_id=scope_link,prior_outcome_id=prior['id'],new_incident_id=intake_result.incident_id,cluster_id=intake_result.cluster_id,classification=intake_result.classification)
     states[-1]=('outcome',result['id'],result)
    else:
     if plan.properties['status'] not in ({'IN_EXECUTION','MONITORING'} if utility_component else {'MONITORING'}):raise PreconditionFailed('PLAN_NOT_MONITORING')
     signature=digest({'work_order_id':w.id,'policy':utility.VERSION if utility_component else VERSION,'evidence':sorted(q.evidence_ids),'start':q.window_start,'end':q.window_end})
     existing=self.store.get('evaluation',signature)
     if existing:return existing['receipt']
     if status=='RESOLUTION_VERIFIED':
      for id,t in tasks.items():
       if self.repo.get_node(id,'ActionTask').properties['status']!='COMPLETED':raise PreconditionFailed('OPEN_BLOCKING_TASK')
       execution_gates(t,[self.repo.get_node(saved['task_ids'][d],'ActionTask').properties['status'] for d in t.depends_on],utility.fulfilled(self.ops,t,saved,at))
      for basis in draft.basis:
       history=reader.histories(basis.hypothesis_id)
       if basis.addressed and history and history[-1].assessment in {'CONTRADICTED','INCONCLUSIVE'}:status='INCONCLUSIVE';gaps.append('Latest addressed causal assessment requires revised plan/investigation')
     case_ready=status=='RESOLUTION_VERIFIED'
     if case_ready:
      for id in tasks:
       if id==task_node.id:continue
       other=self.store.get('verification',stable('WO',plan.id,id))
       if tasks[id].action_type=='UTILITY_ISOLATION':
        # Isolation alone cannot become an independently resolved component.
        repairs=[other_id for other_id,other_task in tasks.items() if other_task.action_type=='UTILITY_LEAK_REPAIR' and set(other_task.target_ids)==set(tasks[id].target_ids)]
        if not repairs or any(not (self.store.get('verification',stable('WO',plan.id,repair)) or {}).get('assessment_status')=='UTILITY_VERIFIED' for repair in repairs):
         case_ready=False;gaps.append('Isolation requires independent utility repair verification: '+id)
        continue
       required='UTILITY_VERIFIED' if tasks[id].action_type=='UTILITY_LEAK_REPAIR' else 'RESOLUTION_VERIFIED'
       if not other or other['assessment_status']!=required:case_ready=False;gaps.append('Other task follow-up not yet verified: '+id)
     if case_ready:
      changed(plan,'COMPLETED',graph_revision=session.revision+1);changed(inv,'COMPLETED')
      for e in reader.edges('INVESTIGATES',source=inv.id):
       n=reader.node(e.target)
       if n.kind=='Incident':
        sequence=['ACTIVE','ENDED'] if n.properties['status']=='REPORTED' else ['ENDED'];changed(n,sequence,ended_at=at)
       elif n.kind=='ProblemCluster':changed(n,'CONTROLLED')
     result=outcome(status,'MITIGATION_VERIFIED' if status in {'RESOLUTION_VERIFIED','UTILITY_VERIFIED'} else 'INCONCLUSIVE',refs,{'start':q.window_start,'end':q.window_end},gaps);event_type='INTERVENTION_OUTCOME_RECORDED'
     result['case_closed']=case_ready
     states[-1]=('outcome',result['id'],result)
     states.append(('evaluation',signature,{'receipt':result}))
     states.append(('verification',w.id,{'assessment_status':status,'outcome_id':result['id']}))
   if w.id in updates:states.append(('order',w.id,{**v,'last_operation':opid}))
   event={'id':stable('EVENT',opid),'type':event_type,'entity_id':event_subject,'aggregate_revision':session.revision+1,'occurred_at':at,'payload_schema_version':1,'source_kind':'SYNTHETIC','idempotency_key':q.request_id,'actor_id':actor.id,'actor_role':actor.role,'payload':result}
   node('DomainEvent',{**common(event['id'],at),'event_type':event_type,'subject_id':event_subject,'occurred_at':at,'delivery_status':'PENDING','idempotency_key':q.request_id,'payload_ref':'operation:'+opid});edge('EMITTED_EVENT',emitter,event['id'])
   operation={'request_id':q.request_id,'request_hash':request_hash,'actor':actor.model_dump(mode='json'),'command':value,'receipt':result,'occurred_at':at,'native_hashes':hashes,'events':[event],'proof':proof,'state_transitions':transitions,'reviewer_id':reviewer.id if reviewer else None}
   states.append(('operation',opid,operation));self.ops.auth.require(token,q.operation)
   if reviewer:self.ops.auth.require(reviewer_token,'draft')
   try:
    self.store.commit(session,w.id,nodes,list(updates.values()),edges,states)
    if interrupt=='after_commit':raise RuntimeError('INJECTED_ACK_LOSS')
    if self.store.get('operation',opid)!=operation:raise RuntimeError('READBACK_MISMATCH')
   except Exception:raise OpsRecovery(self.repo.graph.name,q.request_id,w.id,operation=q.operation,plan_id=plan.id,approval_id=approval.id) from None
   return result
