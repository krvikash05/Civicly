"""Bounded synthetic service provenance; shared read validation, no public writer."""
from typing import Literal
import json
from pydantic import model_validator
from app.services.evidence.models import Model,ID,Time
from app.graph.models import digest
from app.graph.schema import timestamp
from app.graph.repository import PreconditionFailed,Conflict
from app.services.evidence.reader import Reader
from app.services.operations.storage import Storage
from app.services.operations.service import stable,common
VERSION='B20-SERVICE-1'
TYPE='SERVICE_EXECUTION_SOURCE'

def policy_required(repo,investigation_id):
 scoped=Storage(repo).get('service_policy_scope',investigation_id)
 if scoped and scoped.get('source_graph')==repo.graph.name and scoped.get('investigation_id')==investigation_id and scoped.get('scenario') in {'S05','S06'}:return True
 state=Storage(repo).get('demo','current')
 return bool(state and state['id'] in {'S05','S06'} and any(c['investigation_id']==investigation_id for c in state['cases']))
class ServiceRecord(Model):
 version:Literal['B20-SERVICE-1']=VERSION
 id:ID
 pickup_id:ID|None
 report_evidence_id:ID
 investigation_id:ID
 incident_id:ID
 target_id:ID
 route_id:ID
 scheduled_at:Time
 checked_at:Time
 actual_at:Time|None
 recorded_at:Time
 status:Literal['COMPLETED','MISSED','UNKNOWN']
 source_kind:Literal['SYNTHETIC']='SYNTHETIC'
 source_id:Literal['B20-synthetic-service-log']='B20-synthetic-service-log'
 record_id:ID
 department_id:Literal['DEPT-SAN']='DEPT-SAN'
 observed_by:ID
 reviewed_by:ID
 @model_validator(mode='after')
 def chronology(self):
  due,checked,recorded=map(timestamp,[self.scheduled_at,self.checked_at,self.recorded_at])
  if not due<=checked<=recorded or self.observed_by==self.reviewed_by:raise ValueError('SERVICE_TIME_OR_REVIEW')
  if self.status=='COMPLETED':
   if self.actual_at is None or not due<=timestamp(self.actual_at)<=checked:raise ValueError('SERVICE_ACTUAL_REQUIRED')
  elif self.actual_at is not None:raise ValueError('SERVICE_ACTUAL_NOT_ESTABLISHED')
  if (self.pickup_id is None)!=(self.status=='UNKNOWN'):raise ValueError('SERVICE_EXECUTION_ID_REQUIRED')
  return self

def source_properties(record):
 return {**common(record.id,record.recorded_at),'evidence_type':TYPE,'reliability':'VERIFIED','recorded_at':record.recorded_at,'observed_at':record.checked_at,'source_kind':'SYNTHETIC','source_record_id':record.source_id+':'+record.record_id,'basis':'OBSERVED','summary':record.model_dump_json()}
def parse_source(props):
 record=ServiceRecord.model_validate_json(props['summary'])
 if props!=source_properties(record):raise PreconditionFailed('SERVICE_SOURCE_INTEGRITY')
 return record

def validate(repo,report_id,as_of):
 """Validate current canonical hashes, actual B09 reviewed report/journal and scope."""
 store=Storage(repo);state=store.get('service_evidence',report_id)
 if not state:return None
 record=ServiceRecord.model_validate(state['record']);reader=Reader(repo,as_of)
 source=reader.node(record.id,'Evidence')
 if parse_source(source.properties)!=record:raise PreconditionFailed('SERVICE_SOURCE_STATE_MISMATCH')
 if source.content_hash!=state['source_hash'] or record.report_evidence_id!=report_id:raise PreconditionFailed('SERVICE_SOURCE_BINDING')
 ref=reader.evidence(report_id);report=ref.report
 if not report or not report.review or report.inspector_id!=record.observed_by or report.review.reviewer_id!=record.reviewed_by or report.department_id!=record.department_id or report.source_kind!='SYNTHETIC' or report.source_id==record.source_id or source.properties['source_record_id']==ref.source_record_id:raise PreconditionFailed('SERVICE_REVIEW_BINDING')
 if ref.content_hash!=state['report_hash']:raise PreconditionFailed('SERVICE_REPORT_CHANGED')
 from app.services.evidence.relevance import inspection_incidents
 if record.incident_id not in inspection_incidents(reader,report):raise PreconditionFailed('SERVICE_INCIDENT_BINDING')
 request,_=__import__('app.services.evidence.service',fromlist=['EvidenceService']).EvidenceService(repo).inspection_source(reader,report.inspection_id)
 if request['investigation_id']!=record.investigation_id or request['asset_ids']!=[record.target_id]:raise PreconditionFailed('SERVICE_TARGET_BINDING')
 reader.node(record.target_id,'WasteCollectionPoint');reader.node(record.route_id,'CollectionRoute')
 if record.pickup_id:
  n=reader.node(record.pickup_id,'PickupExecution');edge=repo.get_relationship(state['relationship_id'])
  expected={**common(record.pickup_id,record.recorded_at),'route_id':record.route_id,'scheduled_at':record.scheduled_at,'status':record.status,'source_record_id':source.properties['source_record_id'],**({'actual_at':record.actual_at} if record.actual_at else {})}
  if n.properties!=expected or n.content_hash!=state['pickup_hash'] or edge.content_hash!=state['relationship_hash'] or (edge.kind,edge.source,edge.target,edge.properties.get('source_evidence_id'))!=('PICKUP_FOR',n.id,record.target_id,source.id) or not reader.visible(edge.properties):raise PreconditionFailed('SERVICE_EXECUTION_BINDING')
 operation=store.get('operation',state['operation_id'])
 if not operation or operation.get('receipt')!=state['receipt'] or operation.get('record')!=state['record'] or operation.get('source_hash')!=state['source_hash']:raise PreconditionFailed('SERVICE_AUDIT_BINDING')
 return record

def qualify(record,*,target,report_source,observed_at,code,cause):
 """No narrative/code/count alone proves service result or strictly later deposit."""
 if record is None:return False,'Dated reviewed service execution unavailable; no missed service inferred'
 if record.target_id!=target or record.source_id==report_source:return False,'Service target/source does not establish independent log provenance'
 if observed_at is None:return False,'Deposit/field occurrence time is unknown'
 try:at=timestamp(observed_at)
 except (ValueError,TypeError):return False,'Deposit/field occurrence time is invalid'
 if at>timestamp(record.recorded_at) or at<timestamp(record.checked_at):return False,'Service/field chronology is not established'
 if cause=='MISSED_PICKUP':
  if code=='PICKUP_COMPLETED_CONFIRMED':return record.status=='COMPLETED' and record.actual_at is not None,'Reviewed dated execution result required'
  return record.status=='MISSED' and record.pickup_id is not None,'Explicit reviewed missed-service observation required; absence is not a miss'
 if cause=='ILLEGAL_DUMPING':
  return record.status=='COMPLETED' and record.actual_at is not None and timestamp(record.actual_at)<at,'Strict pickup-before-deposit timing required; later waste alone is not dumping proof'
 return True,''

class ServiceEvidence:
 """Called only by authenticated B19 controller after an actual reviewed report."""
 def __init__(self,services):self.s=services;self.repo=services.repo;self.store=services.ops.store
 def readback(self,report_id):
  record=validate(self.repo,report_id,self.s.clock())
  if record is None:raise PreconditionFailed('SERVICE_SOURCE_UNAVAILABLE')
  return self.store.get('service_evidence',report_id)['receipt']
 def record(self,record,request):
  r=self.repo;at=self.s.clock();reader=Reader(r,at);ref=reader.evidence(record.report_evidence_id);report=ref.report
  if not report or not report.review or record.recorded_at!=at or report.inspector_id!=record.observed_by or report.review.reviewer_id!=record.reviewed_by or report.department_id!='DEPT-SAN':raise PreconditionFailed('SERVICE_AUTHENTICATED_REVIEW_REQUIRED')
  field=self.s.auth.operator(record.observed_by);reviewer=self.s.auth.operator(record.reviewed_by)
  if field.role!='DEPARTMENT_LEAD' or field.department_id!='DEPT-SAN' or reviewer.role!='ANALYST':raise PreconditionFailed('SERVICE_DEPARTMENT_OR_REVIEWER')
  reader.node(record.route_id,'CollectionRoute');reader.node(record.target_id,'WasteCollectionPoint')
  rows=r._read('MATCH (:WasteCollectionPoint {id:$target})-[:COLLECTED_BY]->(r:CollectionRoute {id:$route}) RETURN r.id LIMIT 2',{'target':record.target_id,'route':record.route_id})
  if rows!=[[record.route_id]]:raise PreconditionFailed('SERVICE_ROUTE_SCOPE')
  eid=record.id;props=source_properties(record);nodes=[('Evidence',props)];edges=[];edge_id=None;pickup_hash=None;relationship_hash=None
  if record.pickup_id:
   pickup={**common(record.pickup_id,at),'route_id':record.route_id,'scheduled_at':record.scheduled_at,'status':record.status,'source_record_id':props['source_record_id'],**({'actual_at':record.actual_at} if record.actual_at else {})};nodes.append(('PickupExecution',pickup))
   edge_id=stable('SERVICE-PICKUP-FOR',eid);ep={'id':edge_id,'municipality_id':'demo-city','created_at':at,'valid_from':at,'source_evidence_id':eid};edges.append(('PICKUP_FOR',record.pickup_id,record.target_id,ep));pickup_hash=r.decode_node(r.registry.labels('PickupExecution'),pickup).content_hash
   from app.graph.models import EdgeRecord
   relationship_hash=EdgeRecord(id=edge_id,kind='PICKUP_FOR',source=record.pickup_id,target=record.target_id,properties=ep).content_hash
  opid=stable('SERVICE-OP',request);eventid=stable('SERVICE-EVENT',request)
  receipt={'id':eid,'pickup_id':record.pickup_id,'report_evidence_id':record.report_evidence_id,'event_id':eventid,'status':record.status,'policy_version':VERSION}
  event={'id':eventid,'type':'GRAPH_EVIDENCE_CHANGED','entity_id':record.investigation_id,'aggregate_revision':0,'occurred_at':at,'payload_schema_version':1,'source_kind':'SYNTHETIC','idempotency_key':request,'actor_id':record.observed_by,'actor_role':'DEPARTMENT_LEAD','payload':receipt}
  nodes.append(('DomainEvent',{**common(eventid,at),'event_type':event['type'],'subject_id':event['entity_id'],'occurred_at':at,'delivery_status':'PENDING','idempotency_key':request,'payload_ref':'operation:'+opid}));edges.append(('EMITTED_EVENT',record.investigation_id,eventid,{'id':stable('SERVICE-EVENT-REL',request),'municipality_id':'demo-city','created_at':at,'valid_from':at}))
  state={'record':record.model_dump(mode='json'),'source_hash':r.decode_node(r.registry.labels('Evidence'),props).content_hash,'report_hash':ref.content_hash,'pickup_hash':pickup_hash,'relationship_id':edge_id,'relationship_hash':relationship_hash,'operation_id':opid,'receipt':receipt}
  with r._session() as session:
   if self.store.get('service_evidence',record.report_evidence_id):raise Conflict('SERVICE_SOURCE_ALREADY_RECORDED')
   if r._read('MATCH (e:Evidence {source_record_id:$id}) RETURN e.id LIMIT 2',{'id':props['source_record_id']}):raise Conflict('SERVICE_SOURCE_IDENTITY_CONFLICT')
   event['aggregate_revision']=session.revision+1
   operation={'record':state['record'],'source_hash':state['source_hash'],'receipt':receipt,'events':[event],'occurred_at':at,'native_hashes':{p['id']:digest(p) for _,p in nodes}}
   self.store.commit(session,eid,nodes,[],edges,[('service_evidence',record.report_evidence_id,state),('operation',opid,operation)])
  return self.readback(record.report_evidence_id)
