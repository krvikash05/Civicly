"""Private host authority; never accepted from HTTP, source text or checkpoints."""
from pathlib import Path
from typing import Literal
from pydantic import Field,model_validator
from app.agents.models import Model,Budget
from app.graph.models import digest
from cli.private import read_json

class Case(Model):
 scenario:Literal['S01','S03','S04','S05','S06']
 issue:Literal['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']
 investigation_id:str=Field(min_length=1,max_length=200)
 incident_id:str=Field(min_length=1,max_length=200)
 thread_id:str=Field(min_length=1,max_length=200)

class HostConfig(Model):
 version:Literal[1]=1
 mode:Literal['LIVE_GEMINI']
 model:str=Field(pattern=r'^[A-Za-z0-9._-]{1,100}$')
 profile:str
 memory_profile:str
 auth_store:str
 cases:list[Case]=Field(min_length=3,max_length=3)
 budget:Budget=Field(default_factory=Budget)
 @model_validator(mode='after')
 def scope(self):
  expected={'S01':'WATERLOGGING','S03':'ROAD_DAMAGE','S04':'ROAD_DAMAGE','S05':'WASTE_ACCUMULATION','S06':'WASTE_ACCUMULATION'}
  if {c.issue for c in self.cases}!={'WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION'} or any(expected[c.scenario]!=c.issue for c in self.cases):raise ValueError('EXACT_THREE_CATEGORY_SCOPE_REQUIRED')
  for key in ['investigation_id','incident_id','thread_id']:
   if len({getattr(c,key) for c in self.cases})!=3:raise ValueError('DISTINCT_CASE_IDENTITIES_REQUIRED')
  default=Budget()
  if any(getattr(self.budget,k)>getattr(default,k) for k in type(default).model_fields):raise ValueError('DEMO_BUDGET_INCREASE_DENIED')
  for path in [self.profile,self.memory_profile,self.auth_store]:
   if not Path(path).is_absolute():raise ValueError('ABSOLUTE_PRIVATE_HOST_PATH_REQUIRED')
  return self
 @property
 def fingerprint(self):return digest(self.model_dump(mode='json'))

def load(path):return HostConfig.model_validate(read_json(Path(path),private=True))
