import json
from pathlib import Path
from typing import Literal
from pydantic import Field,model_validator
from app.services.evidence.models import Model,ID,Time
from app.graph.models import digest
TYPES=json.loads((Path(__file__).resolve().parents[3]/'contracts/event_types.json').read_text())['types']

class Event(Model):
 id:ID
 type:ID
 entity_id:ID
 aggregate_revision:int=Field(ge=0)
 occurred_at:Time
 payload_schema_version:Literal[1]
 source_kind:Literal['SYNTHETIC','PUBLIC','MUNICIPAL','USER','AGENT']
 idempotency_key:ID
 actor_id:ID|None=None
 actor_role:Literal['ANALYST','DEPARTMENT_LEAD','APPROVER','ADMIN','SYSTEM']|None=None
 payload:dict=Field(default_factory=dict)
 @model_validator(mode='after')
 def valid(self):
  if self.type not in TYPES or len(json.dumps(self.payload).encode())>150000:raise ValueError('EVENT_TYPE_OR_SIZE')
  if TYPES[self.type]['actor_audit_required'] and (not self.actor_id or not self.actor_role):raise ValueError('EVENT_ACTOR_REQUIRED')
  return self

def route(event,case):
 if event.actor_id=='civicly-b10-analyst' or event.source_kind=='AGENT':return 'INFO','SELF_GENERATED_ANALYTICAL'
 if event.payload.get('operation') in {'draft','propose','request_inspection','transition_inspection','regroup'}:return 'INFO','DRAFT_OR_PENDING_INSPECTION_OR_REBIND_REQUIRED'
 if event.type=='MONITORING_DUE':return 'MONITOR','FOLLOWUP_REQUESTED_NO_OBSERVATION_INVENTED'
 if event.type in {'AGENT_TOOL_EXECUTED','PLAN_DRAFTED','PLAN_SUBMITTED','WORK_ORDER_CREATED','WORK_ORDER_STATUS_CHANGED','HYPOTHESIS_ASSESSED','AGENT_DECISION_RECORDED','SOURCE_DOCUMENT_UPDATED','EVENT_DELIVERY_FAILED'}:return 'INFO','HUMAN_OR_INFORMATIONAL_ONLY'
 if not case:return 'INFO','EXPLICIT_CASE_BINDING_REQUIRED'
 return 'WAKE','BOUNDED_INVESTIGATION_WAKE'

def backoff(attempt):
 if not 1<=attempt<=8:raise ValueError('ATTEMPT_BOUND')
 return min(60,2**(attempt-1))

def batch_key(ids):return 'BATCH-B15-'+digest(sorted(ids))[:32]

def public(event,case,cursor,source):
 # Never export arbitrary source text, command bodies, actor capabilities or model output.
 return {'cursor':cursor,'id':event.id,'event_type':event.type,'entity_id':event.entity_id,'investigation_id':case,
  'revision':event.aggregate_revision,'occurred_at':event.occurred_at,'source_kind':event.source_kind,'simulation_mode':'SIMULATED',
  'payload_schema_version':1,'payload':{k:v for k,v in event.payload.items() if k in {'plan_id','plan_version','approval_id','task_id','new_incident_id','cluster_id','prior_outcome_id','investigates_relationship_id','execution_id','decision_id','operation'} and (isinstance(v,int) or isinstance(v,str) and len(v)<=200)},
  'source_ref':source}
