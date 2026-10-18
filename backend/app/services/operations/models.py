"""Closed B13 service commands, separate from future API transport."""
from typing import Literal
from app.graph.repository import OutcomeUnknown
from pydantic import Field,model_validator
from app.services.evidence.models import Model,ID,Text,Hash
class Assignment(Model):
 task_id:ID
 action_type:ID
 target_ids:list[ID]=Field(min_length=1,max_length=5)
 department_id:ID
 assignee_id:ID
class Binding(Model):
 plan_id:ID
 plan_version:int=Field(ge=1,le=100)
 plan_hash:Hash
 assignments:list[Assignment]=Field(min_length=1,max_length=12)
 @model_validator(mode='after')
 def distinct(self):
  if len({a.task_id for a in self.assignments})!=len(self.assignments) or any(len(set(a.target_ids))!=len(a.target_ids) for a in self.assignments):raise ValueError('DUPLICATE_SCOPE')
  return self
 def normalized(self):
  v=self.model_dump(mode='json');v['assignments'].sort(key=lambda a:a['task_id'])
  for a in v['assignments']:a['target_ids'].sort()
  return v
class Submit(Binding):
 operation:Literal['submit']='submit'
 request_id:ID
class Decide(Binding):
 operation:Literal['decide']='decide'
 request_id:ID
 approval_id:ID
 expected_hash:Hash
 decision:Literal['APPROVED','REJECTED']
 reason:Text
class Order(Binding):
 operation:Literal['order']='order'
 request_id:ID
 approval_id:ID
 task_id:ID
class Update(Model):
 operation:Literal['update']='update'
 request_id:ID
 work_order_id:ID
 expected_hash:Hash
 new_status:Literal['ASSIGNED','CANCELLED']
 reason:Text
class OpsRecovery(OutcomeUnknown):
 def __init__(self,graph,request_id,entity_id,*,operation=None,plan_id=None,approval_id=None):
  super().__init__('OPERATIONS_RECOVERY_REQUIRED');self.reconciliation={'graph':graph,'request_id':request_id,'entity_id':entity_id,'commitment':'UNKNOWN','operation':operation,'plan_id':plan_id,'approval_id':approval_id}
