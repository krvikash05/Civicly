"""Narrow analytical draft service: trusted analyst, source references, no dispatch."""
import asyncio,json
from app.services.evidence.models import Actor,Assessment
from app.services.evidence.reader import Reader
from app.graph.schema import utc_now,timestamp
from app.graph.models import digest
from app.graph.repository import Conflict,OutcomeUnknown
from app.memory.models import Citation
from .models import PlanDraft,PlanReceipt
from .storage import Store
class PlanningBlocked(ValueError):
 def __init__(self,code,*,task_id=None):self.code=code;self.task_id=task_id;super().__init__(code)
class PlanRecoveryRequired(OutcomeUnknown):
 """No receipt: a commit attempt or persisted replay requires operator verification."""
 def __init__(self,*,graph,request_id,investigation_id,plan_id,version,plan_hash,stage):
  # Only validated domain/host identities; never copy the underlying exception.
  super().__init__('INJECTED_ACK_LOSS' if stage=='INJECTED_ACK_LOSS' else 'PLAN_COMMIT_VERIFICATION_REQUIRED')
  self.reconciliation={'graph':graph,'request_id':request_id,'investigation_id':investigation_id,
   'plan_id':plan_id,'expected_version':version,'expected_plan_hash':plan_hash,'stage':stage}
class PlanningService:
 def __init__(self,repo,memory=None,*,clock=utc_now):self.repo=repo;self.memory=memory;self.clock=clock;self.store=Store(repo)
 async def resolve(self,task,reader,as_of):
  owners=[]
  for target in task.target_ids:
   reader.node(target,'InfrastructureAsset')
   rows=self.repo._read('MATCH (:InfrastructureAsset {id:$id})-[r:MAINTAINED_BY]->(d:Department) RETURN r.id,d.id LIMIT 21',{'id':target})
   if len(rows)>20:raise PlanningBlocked('OWNERSHIP_SCAN_LIMIT')
   verified=[]
   for edge_id,department in rows:
    edge=self.repo.get_relationship(edge_id)
    if not reader.visible(edge.properties) or edge.properties.get('association_status')!='VERIFIED':continue
    reader.node(department,'Department')
    evidence=reader.node(edge.properties.get('source_evidence_id',''),'Evidence')
    if evidence.properties['reliability']!='VERIFIED' or evidence.properties.get('source_kind')=='AGENT' or not evidence.properties.get('observed_at'):raise PlanningBlocked('OWNERSHIP_EVIDENCE_INVALID')
    if evidence.properties['evidence_type']=='RESPONSIBILITY_REVIEW':
     from app.services.responsibility.service import validate_review_evidence
     review,record=validate_review_evidence(self.repo,evidence.properties)
     state=__import__('app.services.operations.storage',fromlist=['Storage']).Storage(self.repo).get('responsibility',review.submission_id)
     q=record.command
     if not state or state['relationship_id']!=edge_id or state['relationship_hash']!=edge.content_hash or (q.asset_id,q.department_id,q.valid_from,q.valid_to)!=(target,department,edge.properties.get('valid_from'),edge.properties.get('valid_to')):raise PlanningBlocked('OWNERSHIP_REVIEW_BINDING')
    self.repo._check_evidence(edge.properties)  # Reuse B03 attribution/date ordering guarantees.
    verified.append((department,edge_id,evidence.id))
   if len(verified)!=1:raise PlanningBlocked('OWNERSHIP_UNKNOWN_OR_CONFLICTING')
   if verified[0][0]!=task.department_id:raise PlanningBlocked('ACCOUNTABLE_DEPARTMENT_MISMATCH')
   owners.append({'asset_id':target,'department_id':verified[0][0],'relationship_id':verified[0][1],'evidence_id':verified[0][2],'relationship_hash':self.repo.get_relationship(verified[0][1]).content_hash,'evidence_hash':self.repo.get_node(verified[0][2],'Evidence').content_hash})
  if self.memory is None:raise PlanningBlocked('PROCEDURE_CAPABILITY_UNAVAILABLE')
  citation=task.procedure_citation
  if timestamp(citation.retrieved_at)>timestamp(as_of):raise PlanningBlocked('PROCEDURE_CITATION_FROM_FUTURE')
  found=await self.memory.retrieve(as_of=as_of,document_id=citation.source_document_id,version=citation.source_version)
  fresh=[Citation.model_validate(v) for v in found['citations']]
  def binding(value):return value.model_dump(mode='json',exclude={'retrieved_at'})
  if not any(binding(c)==binding(citation) for c in fresh):raise PlanningBlocked('PROCEDURE_STALE_REVOKED_OR_UNAVAILABLE')
  source=self.memory.store.get(citation.canonical_document_id)[0]
  if task.action_type not in source.action_types:raise PlanningBlocked('PROCEDURE_ACTION_MISMATCH')
  procedure_id=citation.canonical_document_id.replace('ORG:','ORGPROC:',1)
  procedure=self.memory.repo.get_node(procedure_id,'KnowledgeProcedure')
  if procedure.properties.get('document_ref')!=citation.canonical_document_id or procedure.properties.get('version')!=str(citation.source_version) or procedure.properties['status']!='PROPOSED':raise PlanningBlocked('PROCEDURE_BINDING')
  return {'owners':owners,'procedure_id':procedure_id,'procedure_graph':self.memory.repo.graph.name,'document_owner_id':source.owner_department_id,'execution_department_id':task.department_id,'procedure_status':'PROPOSED','reservations':found['gaps']}
 async def create(self,value,*,request_id,actor,interrupt=None):
  if not isinstance(actor,Actor) or actor.role not in {'ANALYST','ADMIN'}:raise PlanningBlocked('DRAFT_ROLE_DENIED')
  if not isinstance(request_id,str) or not 1<=len(request_id)<=200:raise ValueError('REQUEST_ID')
  draft=PlanDraft.model_validate(value);at=self.clock();reader=Reader(self.repo,at)
  # Entire source validation/version/CAS occurs under repository writer fence.
  with self.repo._session() as session:
   existing=self.repo._read('MATCH (d:CivicPlanDraft {request_id:$id}) RETURN d.id LIMIT 2',{'id':request_id})
   if existing:
    try:
     saved=self.store.get(existing[0][0]);saved_receipt=PlanReceipt.model_validate(saved['receipt'])
    except Exception:
     raise PlanRecoveryRequired(graph=self.repo.graph.name,request_id=request_id,investigation_id=draft.investigation_id,plan_id=existing[0][0],version=draft.version,plan_hash=draft.content_hash,stage='REPLAY_VERIFICATION') from None
    if saved['draft']!=draft.normalized():raise Conflict('PLAN_REQUEST_CONFLICT')
    return saved_receipt
   inv=reader.node(draft.investigation_id,'Investigation')
   incidents=[reader.node(e.target,'Incident') for e in reader.edges('INVESTIGATES',source=inv.id) if self.repo.get_node(e.target).kind=='Incident']
   if not incidents or {n.properties['issue_type'] for n in incidents}!={draft.issue}:raise PlanningBlocked('INVESTIGATION_ISSUE_BINDING')
   hypotheses={e.target for e in reader.edges('PROPOSES',source=inv.id)};allowed_targets=set();allowed_evidence=set();assessments=[]
   for incident in incidents:allowed_targets.update(e.target for e in reader.edges('AFFECTS',source=incident.id))
   for basis in draft.basis:
    if basis.hypothesis_id not in hypotheses:raise PlanningBlocked('HYPOTHESIS_OUTSIDE_INVESTIGATION')
    history=reader.histories(basis.hypothesis_id)
    if not history or history[-1].id!=basis.assessment_id:raise PlanningBlocked('ASSESSMENT_STALE_OR_OUTSIDE_HYPOTHESIS')
    assessment=history[-1];assessments.append(assessment)
    allowed_evidence.update(assessment.supporting_evidence_ids+assessment.contradicting_evidence_ids)
    for e in reader.edges('CONCERNS',source=basis.hypothesis_id):
     if 'InfrastructureAsset' in self.repo.get_node(e.target).labels:allowed_targets.add(e.target)
   if not set(draft.evidence_ids)<=allowed_evidence:raise PlanningBlocked('EVIDENCE_OUTSIDE_ASSESSMENTS')
   for id in draft.evidence_ids:reader.node(id,'Evidence')
   rows=self.store.rows(inv.id);head=max(rows,key=lambda r:r[1]) if rows else None
   if (not head and draft.version!=1) or head and (draft.version!=head[1]+1 or draft.previous_plan_id!=head[0]):raise PlanningBlocked('PLAN_VERSION_CONFLICT')
   proof={'actor_id':actor.id,'actor_role':actor.role,'validated_at':at,'source_graph':self.repo.graph.name,'source_graph_revision':session.revision,'tasks':{}}
   memory_revision=self.memory.repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision,m.repo_pending") if self.memory else None
   for task in draft.tasks:
    if not set(task.target_ids)<=allowed_targets:raise PlanningBlocked('TARGET_OUTSIDE_INVESTIGATION')
    try:
     from .policy import validate_remediation
     action_proof=validate_remediation(task,draft,reader,assessments,PlanningBlocked)
     proof['tasks'][task.id]={**await self.resolve(task,reader,at),'remediation':action_proof}
    except PlanningBlocked as e:
     e.task_id=task.id;raise
   if self.memory and memory_revision!=self.memory.repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision,m.repo_pending"):raise PlanningBlocked('PROCEDURE_REVISION_CHANGED')
   proof['procedure_reference_revision']=memory_revision
   receipt=PlanReceipt(id='PLAN-B12-'+digest([inv.id,draft.version])[:32],version=draft.version,plan_hash=draft.content_hash)
   stage='COMMIT_ATTEMPT'
   try:
    self.store.commit(session,draft,receipt,request_id,proof,at)
    stage='INJECTED_ACK_LOSS' if interrupt=='after_commit' else 'ACKNOWLEDGMENT_VERIFICATION'
    if interrupt=='after_commit':raise RuntimeError('INJECTED_ACK_LOSS')
    if self.store.get(receipt.id)['receipt']!=receipt.model_dump(mode='json'):raise PlanningBlocked('PLAN_READBACK')
   except Exception:
    # Includes Pydantic/Migration/PlanningBlocked failures after the write boundary.
    # A failed commit response can also have persisted: never claim rollback.
    raise PlanRecoveryRequired(graph=self.repo.graph.name,request_id=request_id,investigation_id=inv.id,plan_id=receipt.id,version=receipt.version,plan_hash=receipt.plan_hash,stage=stage) from None
   return receipt
