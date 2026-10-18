"""Closed draft contracts; no cost/duration/confidence or executable permissions."""
from typing import Literal
from pydantic import Field,model_validator
from pydantic_core import PydanticCustomError
from app.services.evidence.models import Model,ID,Text,Time
from app.memory.models import Citation
from app.graph.models import digest
class Basis(Model):
 hypothesis_id:ID
 assessment_id:ID
 reason:Text
 addressed:bool
class Monitoring(Model):
 issue:Literal['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']
 required_evidence:list[Literal['COMPARABLE_FOLLOWUP_RAINFALL','FOLLOWUP_WATERLOGGING','FOLLOWUP_PAVEMENT','WEAR_EXPOSURE','SCHEDULED_PICKUPS','ACTUAL_PICKUPS','REACCUMULATION_WINDOW']]=Field(min_length=2,max_length=7)
 observation_opportunity:Text
 verification_criteria:Text
 missing_opportunity:Literal['UNRESOLVED']='UNRESOLVED'
 completion_implies_resolution:Literal[False]=False
 @model_validator(mode='after')
 def correct_policy(self):
  required={'WATERLOGGING':{'COMPARABLE_FOLLOWUP_RAINFALL','FOLLOWUP_WATERLOGGING'},'ROAD_DAMAGE':{'FOLLOWUP_PAVEMENT','WEAR_EXPOSURE'},'WASTE_ACCUMULATION':{'SCHEDULED_PICKUPS','ACTUAL_PICKUPS','REACCUMULATION_WINDOW'}}[self.issue]
  if set(self.required_evidence)!=required or len(self.required_evidence)!=len(required):raise ValueError('Issue-specific monitoring evidence required')
  return self
class Prerequisite(Model):
 kind:Literal['CAUSAL_INSPECTION','SAFETY_REVIEW','ISOLATION_PROOF','UTILITY_VERIFICATION']
 status:Literal['MET','UNMET']
 evidence_ids:list[ID]=Field(default_factory=list,max_length=12)
 depends_on_task_id:ID|None=None
 @model_validator(mode='after')
 def binding(self):
  if (self.status=='MET')!=bool(self.evidence_ids) or self.status=='MET' and self.depends_on_task_id is not None:
   raise PydanticCustomError('plan_prerequisite','Invalid prerequisite evidence binding')
  return self
class Remediation(Model):
 mode:Literal['SUPPORTED_NOW','CONDITIONAL']
 conditions:list[Prerequisite]=Field(min_length=2,max_length=4)
 @model_validator(mode='after')
 def guards(self):
  if not {'CAUSAL_INSPECTION','SAFETY_REVIEW'}<={c.kind for c in self.conditions} or len({c.kind for c in self.conditions})!=len(self.conditions) or (self.mode=='SUPPORTED_NOW')!=all(c.status=='MET' for c in self.conditions):
   raise PydanticCustomError('plan_prerequisite','Explicit causal and safety gates required')
  return self
class TaskDraft(Model):
 id:ID
 action_type:Literal['INSPECTION','DRAIN_BLOCKAGE_CLEARANCE','SUBGRADE_REPAIR','MISSED_PICKUP_RECOVERY','UTILITY_ISOLATION','UTILITY_LEAK_REPAIR']
 remediation:Remediation|None=None
 target_ids:list[ID]=Field(min_length=1,max_length=5)
 department_id:ID
 priority:Literal['LOW','MODERATE','HIGH','CRITICAL']
 prerequisites:list[Text]=Field(min_length=1,max_length=8)
 depends_on:list[ID]=Field(default_factory=list,max_length=12)
 evidence_ids:list[ID]=Field(min_length=1,max_length=12)
 assessment_ids:list[ID]=Field(min_length=1,max_length=10)
 procedure_citation:Citation
 expected_outcome:Text
 verification_criteria:Text
 risks:list[Text]=Field(min_length=1,max_length=8)
 @model_validator(mode='after')
 def action_guards(self):
  if (self.action_type=='INSPECTION')!=(self.remediation is None):raise PydanticCustomError('plan_prerequisite','Remedial actions require typed prerequisites')
  if self.remediation and any(not set(c.evidence_ids)<=set(self.evidence_ids) for c in self.remediation.conditions):raise PydanticCustomError('plan_prerequisite','Prerequisite evidence outside task')
  return self
class PlanDraft(Model):
 investigation_id:ID
 issue:Literal['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']
 version:int=Field(ge=1,le=100)
 previous_plan_id:ID|None=None
 simulation_mode:Literal['SIMULATED']='SIMULATED'
 basis:list[Basis]=Field(min_length=2,max_length=10)
 evidence_ids:list[ID]=Field(min_length=1,max_length=30)
 tasks:list[TaskDraft]=Field(min_length=1,max_length=12)
 expected_outcomes:list[Text]=Field(min_length=1,max_length=8)
 risks:list[Text]=Field(min_length=1,max_length=8)
 uncertainties:list[Text]=Field(min_length=1,max_length=12)
 monitoring:Monitoring
 @model_validator(mode='after')
 def integrity(self):
  ids=[t.id for t in self.tasks];hyp=[b.hypothesis_id for b in self.basis]
  if len(set(ids))!=len(ids) or len(set(hyp))!=len(hyp):raise ValueError('Duplicate task/hypothesis IDs')
  if not any(b.addressed for b in self.basis) or not any(not b.addressed for b in self.basis):raise ValueError('Addressed and alternative hypotheses required')
  if self.monitoring.issue!=self.issue:raise ValueError('Monitoring issue mismatch')
  if (self.version==1)!=(self.previous_plan_id is None):raise ValueError('Previous version binding required')
  adjacency={t.id:t.depends_on for t in self.tasks};visiting=set();done=set()
  def visit(id):
   if id in visiting:raise PydanticCustomError('plan_dag','Dependency cycle',{'task_id':id})
   if id in done:return
   visiting.add(id)
   for other in adjacency[id]:
    if other not in adjacency:raise PydanticCustomError('plan_dag','Unknown dependency',{'task_id':id})
    visit(other)
   visiting.remove(id);done.add(id)
  for t in self.tasks:
   if len(set(t.depends_on))!=len(t.depends_on) or len(set(t.target_ids))!=len(t.target_ids):raise ValueError('Duplicate task references')
   if not set(t.evidence_ids)<=set(self.evidence_ids) or not set(t.assessment_ids)<={b.assessment_id for b in self.basis}:raise ValueError('Task references outside plan')
   visit(t.id)
  return self
 def normalized(self):
  value=self.model_dump(mode='json');value['tasks']=sorted(value['tasks'],key=lambda t:t['id']);value['basis']=sorted(value['basis'],key=lambda b:b['hypothesis_id'])
  for task in value['tasks']:
   if task['remediation'] is None:task.pop('remediation') # Preserve accepted B12 hashes byte-for-byte.
   else:
    task['remediation']['conditions'].sort(key=lambda c:c['kind'])
    for c in task['remediation']['conditions']:c['evidence_ids'].sort()
   for key in ['depends_on','target_ids','assessment_ids','evidence_ids']:task[key]=sorted(task[key])
  value['evidence_ids']=sorted(value['evidence_ids'])
  return value
 @property
 def content_hash(self):return digest(self.normalized())
class PlanReceipt(Model):
 id:ID
 version:int
 plan_hash:str=Field(pattern='^[0-9a-f]{64}$')
 status:Literal['DRAFT']='DRAFT'
 simulation_mode:Literal['SIMULATED']='SIMULATED'
 approved:Literal[False]=False
 executable:Literal[False]=False
