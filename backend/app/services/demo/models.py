"""Closed public scenario controls; no world observations/answers in inputs."""
from typing import Literal
from pydantic import Field,model_validator,field_validator
from app.services.evidence.models import Model,ID,Hash,Observation
ScenarioID=Literal['S01','S02','S03','S04','S05','S06','S07','S08','S09','S10','S11','S12']
Stage=Literal['BASELINE_VISIBLE','EVIDENCE_REVEALED','PLAN_AND_APPROVAL','FOLLOW_UP']
class DemoResetRequest(Model):
 scenario_id:ScenarioID
 seed:Literal[19]
 confirm:Literal[True]
 @field_validator('seed','confirm',mode='before')
 @classmethod
 def exact_confirmation(cls,value,info):
  if type(value) is not (int if info.field_name=='seed' else bool):raise ValueError('EXPLICIT_SEED_CONFIRMATION_REQUIRED')
  return value
 variant:Literal['PRIMARY','NEGATIVE']='PRIMARY'
class DemoAdvanceRequest(Model):
 expected_current_stage:Stage
 stage:Literal['EVIDENCE_REVEALED','PLAN_AND_APPROVAL','FOLLOW_UP']
 investigation_id:ID|None=None
 inspection_id:ID|None=None
 expected_hash:Hash|None=None
 plan_id:ID|None=None
 work_order_id:ID|None=None
 @model_validator(mode='after')
 def relevant_fields(self):
  supplied={k for k in ['investigation_id','inspection_id','expected_hash','plan_id','work_order_id'] if getattr(self,k) is not None}
  allowed={'investigation_id','inspection_id','expected_hash'} if self.stage=='EVIDENCE_REVEALED' else {'plan_id'} if self.stage=='PLAN_AND_APPROVAL' else {'plan_id','work_order_id'}
  if supplied-allowed:raise ValueError('IRRELEVANT_STAGE_FIELD')
  return self
class ScenarioCase(Model):
 issue_type:Literal['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']
 investigation_id:ID
 incident_id:ID
 cluster_id:ID
 asset_id:ID
 department_id:ID
 evidence_ids:list[ID]=Field(default_factory=list,max_length=3)
 plan_id:ID|None=None
 work_order_id:ID|None=None
class ScenarioDTO(Model):
 id:ScenarioID
 title:str
 issue_types:list[str]
 stage:Literal['NOT_STARTED','BASELINE_VISIBLE','EVIDENCE_REVEALED','PLAN_AND_APPROVAL','FOLLOW_UP']
 current_stage:Stage|None=None
 cases:list[ScenarioCase]=Field(default_factory=list,max_length=3)
 next_operator_steps:list[str]
 limitations:list[str]
ScenarioSummary=ScenarioDTO
class ScenarioPage(Model):
 items:list[ScenarioSummary]=Field(max_length=12)
 next_cursor:None
 total_count:int=Field(ge=0,le=12)
 definition_version:Literal[1]=1
 simulated:Literal[True]=True
class SeedReport(Model):
 nodes:int=Field(ge=0)
 relationships:int=Field(ge=0)
 source_documents:int=Field(ge=0)
 seed_fingerprint:Hash
 scenario:ScenarioSummary
 source_graph:ID
 profile_reference:ID
 baseline_content_hash:Hash
 previous_source_preserved:Literal[True]=True
 simulated:Literal[True]=True
class SimulationStepDTO(Model):
 scenario_id:ScenarioID
 stage:Stage
 event_id:ID
 revealed_evidence_ids:list[ID]=Field(max_length=3)
 scenario:ScenarioSummary
 released_evidence_ids:list[ID]=Field(default_factory=list,max_length=3)
 stage_advanced:bool
 simulated:Literal[True]=True
