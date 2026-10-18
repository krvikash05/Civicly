"""Host-only world packets. This module is never imported by agents/MCP/readers."""
import json
from pathlib import Path
from typing import Literal
from pydantic import Field,model_validator
from .models import Model,ScenarioID
from app.services.complaints.models import WaterIntake,RoadIntake,WasteIntake
from app.services.evidence.models import Observation
ROOT=Path(__file__).resolve().parents[4]
BASE='2026-10-18T10:00:00.000000Z'
TARGETS={'WATERLOGGING':('DRAIN-100','LOC-005','DEPT-DRAIN'),'ROAD_DAMAGE':('ROAD-100','LOC-JUNCTION','DEPT-ROAD'),'WASTE_ACCUMULATION':('WASTE-100','LOC-MARKET','DEPT-SAN')}
def target(world,issue):
 if world.id in {'S01','S10'} and issue=='WATERLOGGING':return 'DRAIN-101','LOC-006','DEPT-DRAIN'
 if world.id=='S04' and issue=='ROAD_DAMAGE':return 'PIPE-100','LOC-JUNCTION','DEPT-WATER'
 if world.id=='S08' and issue=='WASTE_ACCUMULATION':return 'WASTE-100','B19-NEARBY','DEPT-SAN'
 return TARGETS[issue]
class Sample(Model):
 code:str=Field(min_length=1,max_length=100)
 statement:str=Field(min_length=1,max_length=1000)
 value:float|None=None
 unit:str|None=None
 result:Literal['OBSERVED','UNKNOWN']='OBSERVED'
 @model_validator(mode='after')
 def quantity(self):
  Observation(asset_id='validation',method='SYNTHETIC_FIELD_SURVEY',observed_at=BASE,**self.model_dump());return self
class World(Model):
 id:ScenarioID
 issues:list[Literal['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']]=Field(min_length=1,max_length=3)
 report:str=Field(min_length=1,max_length=1000)
 release:dict[str,list[Sample]]
 negative:dict[str,list[Sample]]
 @model_validator(mode='after')
 def references(self):
  if len(set(self.issues))!=len(self.issues) or set(self.release)!=set(self.issues) or set(self.negative)!=set(self.issues):raise ValueError('WORLD_SCOPE')
  for packet in [self.release,self.negative]:
   for obs in packet.values():
    if not 1<=len(obs)<=10 or len({x.code for x in obs})!=len(obs):raise ValueError('WORLD_BOUND')
  for issue in self.issues:intake(self,issue)
  return self
class Worlds(Model):
 version:Literal[1]
 baseline_at:Literal['2026-10-18T10:00:00.000000Z']
 scenarios:list[World]=Field(min_length=12,max_length=12)
 @model_validator(mode='after')
 def inventory(self):
  if {s.id for s in self.scenarios}!={f'S{i:02}' for i in range(1,13)}:raise ValueError('WORLD_INVENTORY')
  return self

def intake(world,issue):
 asset,loc,_=target(world,issue)
 cls={'WATERLOGGING':WaterIntake,'ROAD_DAMAGE':RoadIntake,'WASTE_ACCUMULATION':WasteIntake}[issue]
 # Catalog history is a source claim, never fabricated verified repair/inspection.
 assets=['ROAD-100','PIPE-100'] if world.id=='S04' else [asset,'DRAIN-100'] if world.id=='S07' and asset!='DRAIN-100' else [asset]
 measurements=[]
 if world.id=='S02':measurements=[{'name':'rainfall','value':125.0,'unit':'mm','observed_at':BASE,'source_id':'B19-synthetic-rain-gauge','source_reference':'baseline-gauge','basis':'REPORTED'}]
 return cls.model_validate({'details':{'measurements':measurements},'issue_type':issue,'description':world.report,'source_id':'B19-baseline-'+world.id,'external_record_id':issue,'source_channel':'SYNTHETIC_DEMO','reported_at':BASE,'occurred_at':BASE,'location_id':loc,'asset_ids':assets}).model_dump(mode='json')
def load():
 value=Worlds.model_validate_json((ROOT/'data/scenarios/runtime-v1.json').read_text())
 return {s.id:s for s in value.scenarios}
