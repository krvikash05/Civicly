from datetime import datetime,timedelta,timezone
import pytest
from app.graph.repository import PreconditionFailed
from app.services.evidence.models import Observation
from app.services.operations.verification import evaluate,validate_observation,REQUIRED

def time(hours):return (datetime(2026,10,18,tzinfo=timezone.utc)+timedelta(hours=hours)).isoformat().replace('+00:00','Z')
def ob(code,hour=2,value=None,unit=None,**extra):return Observation(asset_id='A',code=code,statement='Authored synthetic observation',method='DIRECT_SYNTHETIC_FIELD_TEST',observed_at=time(hour),value=value,unit=unit,**extra)
def rows(issue,adverse=0.0):
 if issue=='WASTE_ACCUMULATION':return [ob('SCHEDULED_PICKUPS',2,1.0,'pickups'),ob('ACTUAL_PICKUPS',2,1.0,'pickups'),ob('REACCUMULATION_WINDOW',26,24.0,'hours'),ob('WASTE_REACCUMULATION',26,adverse,'boolean')]
 return [ob(REQUIRED[issue][0],2),ob(REQUIRED[issue][1],3,adverse,'boolean')]
@pytest.mark.parametrize('issue',list(REQUIRED))
@pytest.mark.parametrize('adverse,expected',[(0.0,'RESOLUTION_VERIFIED'),(1.0,'PROBLEM_PERSISTS')])
def test_policy_qualifying_and_adverse(issue,adverse,expected):assert evaluate(issue,['A'],rows(issue,adverse),time(1),time(27),time(0),time(28))[0]==expected
@pytest.mark.parametrize('issue',list(REQUIRED))
def test_missing_opportunity_and_conflicting_observations(issue):
 assert evaluate(issue,['A'],[],time(1),time(27),time(0),time(28))[0]=='MONITORING'
 data=rows(issue)+[ob(REQUIRED[issue][-1],26,1.0,'boolean')]
 assert evaluate(issue,['A'],data,time(1),time(27),time(0),time(28))[0]=='INCONCLUSIVE'
@pytest.mark.parametrize('start,end,now',[(0,27,28),(2,1,28),(1,27,26)])
def test_invalid_temporal_boundaries(start,end,now):
 with pytest.raises(PreconditionFailed):evaluate('ROAD_DAMAGE',['A'],rows('ROAD_DAMAGE'),time(start),time(end),time(0),time(now))
def test_temporal_target_and_waste_adequacy():
 unknown=rows('ROAD_DAMAGE')+[ob('FOLLOWUP_PAVEMENT',3,None,None,result='UNKNOWN')]
 # UNKNOWN may omit a measurement, and never supplies positive evidence.
 assert evaluate('ROAD_DAMAGE',['A'],unknown,time(1),time(27),time(0),time(28))[0]=='MONITORING'
 assert evaluate('ROAD_DAMAGE',['A','B'],rows('ROAD_DAMAGE'),time(1),time(27),time(0),time(28))[0]=='MONITORING'
 assert evaluate('ROAD_DAMAGE',['A'],[ob('WEAR_EXPOSURE',4),ob('FOLLOWUP_PAVEMENT',3,0.0,'boolean')],time(1),time(27),time(0),time(28))[0]=='MONITORING'
 data=rows('WASTE_ACCUMULATION');data[2]=ob('REACCUMULATION_WINDOW',10,8.0,'hours')
 assert evaluate('WASTE_ACCUMULATION',['A'],data,time(1),time(27),time(0),time(28))[0]=='MONITORING'
 data=rows('WASTE_ACCUMULATION');data[1]=ob('ACTUAL_PICKUPS',3,0.0,'pickups')
 assert evaluate('WASTE_ACCUMULATION',['A'],data,time(1),time(27),time(0),time(28))[0]=='MONITORING'
 with pytest.raises(PreconditionFailed):evaluate('ROAD_DAMAGE',['A'],rows('ROAD_DAMAGE'),time(4),time(27),time(0),time(28))
@pytest.mark.parametrize('code,value,unit',[('UNKNOWN',None,None),('FOLLOWUP_PAVEMENT',2.0,'boolean'),('ACTUAL_PICKUPS',1.5,'pickups'),('REACCUMULATION_WINDOW',-1.0,'hours'),('WEAR_EXPOSURE',1.0,'hours')])
def test_invalid_observation_units_and_codes(code,value,unit):
 with pytest.raises(PreconditionFailed):validate_observation(ob(code,2,value,unit),set(REQUIRED['ROAD_DAMAGE'])|set(REQUIRED['WASTE_ACCUMULATION']))
