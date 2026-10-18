"""Explicit inventory authority acquisition; existing fenced operations batch only."""
import json
from app.graph.models import digest
from app.graph.schema import utc_now,timestamp
from app.graph.repository import Conflict,PreconditionFailed
from app.services.evidence.reader import Reader
from app.services.operations.auth import Denied
from app.services.operations.storage import Storage
from app.services.operations.models import OpsRecovery
from app.services.operations.service import common
from .models import Submission,Review,SubmissionRecord,ReviewRecord,ResponsibilityDTO
SUBMISSION='RESPONSIBILITY_ASSERTION'
REVIEW='RESPONSIBILITY_REVIEW'
def identity(graph,q):return 'RESP-B20R-'+digest([graph,q.source_id,q.source_record_id,q.source_version])[:32]
def stable(prefix,*parts):return prefix+'-B20R-'+digest(parts)[:32]
def authorization(actor,operation,department=None,submitted_by=None):
 if operation=='submit':
  if actor.role!='DEPARTMENT_LEAD' or actor.department_id!=department:raise Denied('RESPONSIBILITY_DEPARTMENT_SCOPE')
 elif operation=='review':
  if actor.role!='ANALYST' or actor.id==submitted_by:raise Denied('RESPONSIBILITY_INDEPENDENT_REVIEW')
 elif actor.role not in {'ANALYST','APPROVER','DEPARTMENT_LEAD','ADMIN'}:raise Denied('RESPONSIBILITY_READ_DENIED')
def source(repo,id):
 node=repo.get_node(id,'Evidence');record=SubmissionRecord.model_validate_json(node.properties['summary'])
 q=record.command
 if node.properties['evidence_type']!=SUBMISSION or node.properties['reliability']!='UNVERIFIED' or node.properties['source_kind']!='SYNTHETIC' or record.command_hash!=digest(q.model_dump(mode='json')) or id!=identity(repo.graph.name,q):raise PreconditionFailed('RESPONSIBILITY_SOURCE_INTEGRITY')
 expected={'observed_at':q.observed_at,'recorded_at':record.submitted_at,'created_at':record.submitted_at,'updated_at':record.submitted_at,'source_record_id':q.source_id+':'+q.source_record_id+':'+str(q.source_version),'basis':'REPORTED'}
 if any(node.properties.get(k)!=v for k,v in expected.items()):raise PreconditionFailed('RESPONSIBILITY_SOURCE_INTEGRITY')
 return node,record
def validate_review_evidence(repo,props):
 """Also validates the narrowly staged atomic review source before persistence."""
 review=ReviewRecord.model_validate_json(props['summary']);node,record=source(repo,review.submission_id)
 if node.content_hash!=review.submission_hash or review.reviewed_by==record.submitted_by or props.get('id')!=stable('EV-RESP-REVIEW',node.id) or props.get('evidence_type')!=REVIEW or props.get('reliability')!='VERIFIED' or props.get('source_kind')!='SYNTHETIC' or props.get('basis')!='OBSERVED':raise PreconditionFailed('RESPONSIBILITY_REVIEW_INTEGRITY')
 if timestamp(record.command.observed_at)>timestamp(record.submitted_at) or timestamp(record.submitted_at)>timestamp(review.reviewed_at):raise PreconditionFailed('RESPONSIBILITY_REVIEW_TIME')
 expected={'observed_at':record.command.observed_at,'created_at':review.reviewed_at,'updated_at':review.reviewed_at,'recorded_at':review.reviewed_at,'source_record_id':node.properties['source_record_id']+':review'}
 if any(props.get(k)!=v for k,v in expected.items()):raise PreconditionFailed('RESPONSIBILITY_REVIEW_INTEGRITY')
 return review,record
class Responsibility:
 def __init__(self,repo,auth,*,clock=utc_now):
  from app.services.operations.migration import OperationsMigration
  if not OperationsMigration(repo.client,repo.graph.name).status()['ready']:raise PreconditionFailed('RESPONSIBILITY_0005_REQUIRED')
  self.repo,self.auth,self.clock=repo,auth,clock;self.store=Storage(repo)
 def readback(self,id):
  node,record=source(self.repo,id);state=self.store.get('responsibility',id)
  if not state or state['submission_hash']!=node.content_hash:raise PreconditionFailed('RESPONSIBILITY_STATE_INTEGRITY')
  op=self.store.get('operation',state['last_operation'])
  if not op or op['receipt']['id']!=id:raise PreconditionFailed('RESPONSIBILITY_AUDIT_INTEGRITY')
  reviewer=None
  if state['review_evidence_id']:
   evidence=self.repo.get_node(state['review_evidence_id'],'Evidence');review,_=validate_review_evidence(self.repo,evidence.properties);reviewer=review.reviewed_by
   edge=self.repo.get_relationship(state['relationship_id']);q=record.command
   if edge.kind!='MAINTAINED_BY' or edge.source!=q.asset_id or edge.target!=q.department_id or edge.properties.get('source_evidence_id')!=evidence.id or edge.properties.get('association_status')!='VERIFIED' or edge.properties.get('valid_from')!=q.valid_from or edge.properties.get('valid_to')!=q.valid_to:raise PreconditionFailed('RESPONSIBILITY_EDGE_INTEGRITY')
   if op['native_hashes'].get(evidence.id)!=digest(evidence.properties) or state['relationship_hash']!=edge.content_hash:raise PreconditionFailed('RESPONSIBILITY_REVIEW_INTEGRITY')
  q=record.command;at=self.clock()
  applicability='UNREVIEWED' if reviewer is None else 'FUTURE' if timestamp(q.valid_from)>timestamp(at) else 'HISTORICAL' if q.valid_to and timestamp(q.valid_to)<=timestamp(at) else 'CURRENT'
  return ResponsibilityDTO(id=id,**q.model_dump(mode='json'),submitted_by=record.submitted_by,reviewed_by=reviewer,status='VERIFIED' if reviewer else 'SUBMITTED',applicability=applicability,expected_hash=node.content_hash,source_evidence_id=id,review_evidence_id=state['review_evidence_id'],relationship_id=state['relationship_id'],event_id=state['event_id'],as_of=at).model_dump(mode='json')
 def get(self,id,*,token):
  actor=self.auth.resolve(token);authorization(actor,'read');out=self.readback(id)
  if actor.role=='DEPARTMENT_LEAD' and actor.department_id!=out['department_id']:raise Denied('RESPONSIBILITY_DEPARTMENT_SCOPE')
  return out
 def prepare(self,operation,id,value,token):
  if operation not in {'submit','review'}:raise PreconditionFailed('RESPONSIBILITY_CLOSED_OPERATION')
  actor=self.auth.resolve(token);q=(Submission if operation=='submit' else Review).model_validate(value)
  if operation=='submit':authorization(actor,operation,q.department_id)
  else:
   node,record=source(self.repo,id);authorization(actor,operation,submitted_by=record.submitted_by)
   if node.content_hash!=q.expected_hash:raise Conflict('STALE_RESPONSIBILITY_SOURCE')
  return q,actor
 def execute(self,operation,id,value,*,request_id,token):
  from app.active import is_shared_target
  from pydantic import TypeAdapter
  from app.services.evidence.models import ID
  TypeAdapter(ID).validate_python(request_id)
  if self.repo.graph.name!='civicly_knowledge' and not is_shared_target(self.repo.graph.name):raise PreconditionFailed('RESPONSIBILITY_EXACT_TARGET_REQUIRED')
  q,actor=self.prepare(operation,id,value,token);id=identity(self.repo.graph.name,q) if operation=='submit' else id
  opid=stable('OP-RESP',request_id);sha=digest([actor.id,operation,id,q.model_dump(mode='json')]);at=self.clock()
  with self.repo._session() as session:
   prior=self.store.get('operation',opid)
   if prior:
    if prior['request_hash']!=sha:raise Conflict('RESPONSIBILITY_REQUEST_CONFLICT')
    return self.readback(id)
   nodes=[];edges=[];hashes={}
   def node(kind,props):nodes.append((kind,props));hashes[props['id']]=digest(props)
   if operation=='submit':
    Reader(self.repo,at).node(q.asset_id,'InfrastructureAsset');Reader(self.repo,at).node(q.department_id,'Department')
    if timestamp(q.observed_at)>timestamp(at):raise PreconditionFailed('RESPONSIBILITY_FUTURE_OBSERVATION')
    old=self.repo._node_optional(id)
    if old:
     _,previous=source(self.repo,id)
     if previous.command!=q or previous.submitted_by!=actor.id:raise Conflict('RESPONSIBILITY_SOURCE_IDENTITY_CONFLICT')
     return self.readback(id)
    record=SubmissionRecord(command=q,submitted_by=actor.id,submitted_at=at,command_hash=digest(q.model_dump(mode='json')))
    node('Evidence',{**common(id,at),'evidence_type':SUBMISSION,'reliability':'UNVERIFIED','recorded_at':at,'observed_at':q.observed_at,'source_kind':'SYNTHETIC','source_record_id':q.source_id+':'+q.source_record_id+':'+str(q.source_version),'basis':'REPORTED','summary':record.model_dump_json()})
    submission_hash=self.repo.decode_node(self.repo.registry.labels('Evidence'),nodes[0][1]).content_hash
    state={'submission_hash':submission_hash,'review_evidence_id':None,'relationship_id':None}
   else:
    original,record=source(self.repo,id);qsource=record.command
    actor=self.auth.resolve(token);authorization(actor,'review',submitted_by=record.submitted_by)
    submitting=self.auth.operator(record.submitted_by);authorization(submitting,'submit',qsource.department_id)
    if original.content_hash!=q.expected_hash:raise Conflict('STALE_RESPONSIBILITY_SOURCE')
    state=self.store.get('responsibility',id)
    if not state or state['submission_hash']!=original.content_hash:raise PreconditionFailed('RESPONSIBILITY_STATE_INTEGRITY')
    if state['review_evidence_id']:raise Conflict('RESPONSIBILITY_ALREADY_REVIEWED')
    reader=Reader(self.repo,at);reader.node(qsource.asset_id,'InfrastructureAsset');reader.node(qsource.department_id,'Department')
    review=ReviewRecord(submission_id=id,submission_hash=original.content_hash,reviewed_by=actor.id,reviewed_at=at,reason=q.reason)
    eid=stable('EV-RESP-REVIEW',id);rid=stable('REL-RESP',id)
    ep={**common(eid,at),'evidence_type':REVIEW,'reliability':'VERIFIED','recorded_at':at,'observed_at':qsource.observed_at,'source_kind':'SYNTHETIC','source_record_id':original.properties['source_record_id']+':review','basis':'OBSERVED','summary':review.model_dump_json()}
    validate_review_evidence(self.repo,ep);node('Evidence',ep)
    props={'id':rid,'municipality_id':'demo-city','created_at':at,'valid_from':qsource.valid_from,'association_status':'VERIFIED','source_evidence_id':eid}
    if qsource.valid_to:props['valid_to']=qsource.valid_to
    edges=[('MAINTAINED_BY',qsource.asset_id,qsource.department_id,props)]
    # Preflight before dispatch; Storage rechecks under this same writer fence.
    src=self.repo.get_node(qsource.asset_id);dst=self.repo.get_node(qsource.department_id)
    planned=self.repo.decode_node(self.repo.registry.labels('Evidence'),ep)
    self.repo._relationship_policies('MAINTAINED_BY',src,dst,props,planned_evidence=planned)
    from app.graph.models import EdgeRecord
    state={**state,'review_evidence_id':eid,'relationship_id':rid,'relationship_hash':EdgeRecord(id=rid,kind='MAINTAINED_BY',source=src.id,target=dst.id,properties=props).content_hash}
   eventid=stable('EVENT-RESP',opid)
   event={'id':eventid,'type':'GRAPH_EVIDENCE_CHANGED','entity_id':id,'aggregate_revision':session.revision+1,'occurred_at':at,'payload_schema_version':1,'source_kind':'SYNTHETIC','idempotency_key':request_id,'actor_id':actor.id,'actor_role':actor.role,'payload':{'operation':'responsibility_'+operation}}
   node('DomainEvent',{**common(eventid,at),'event_type':event['type'],'subject_id':id,'occurred_at':at,'delivery_status':'PENDING','idempotency_key':request_id,'payload_ref':'operation:'+opid})
   state={**state,'last_operation':opid,'event_id':eventid}
   saved={'request_hash':sha,'request_id':request_id,'actor':actor.model_dump(mode='json'),'command':q.model_dump(mode='json'),'receipt':{'id':id},'native_hashes':hashes,'events':[event],'occurred_at':at}
   self.auth.resolve(token)
   try:
    self.store.commit(session,id,nodes,[],edges,[('responsibility',id,state),('operation',opid,saved)])
    return self.readback(id)
   except Exception:raise OpsRecovery(self.repo.graph.name,request_id,id,operation='responsibility_'+operation) from None
