"""B14-R regression: observed elapsed time, not declared/evaluation duration."""
import pytest
from app.services.operations.verification import evaluate,VERSION
from app.services.operations.verification_v1 import evaluate as historical,VERSION as OLD
from tests.unit.test_execution_policy import ob,time

def data(pickup,observed):
 return [ob('SCHEDULED_PICKUPS',pickup,1.0,'pickups'),ob('ACTUAL_PICKUPS',pickup,1.0,'pickups'),ob('REACCUMULATION_WINDOW',observed,24.0,'hours'),ob('WASTE_REACCUMULATION',observed,0.0,'boolean')]
def check(values):return evaluate('WASTE_ACCUMULATION',['A'],values,time(1),time(75),time(0),time(76))[0]
def test_one_hour_false_positive_and_frozen_historical_policy():
 values=data(25,26)
 assert OLD=='B14-1' and VERSION=='B14-2'
 assert historical('WASTE_ACCUMULATION',['A'],values,time(1),time(27),time(0),time(28))[0]=='RESOLUTION_VERIFIED'
 assert check(values)=='MONITORING'
@pytest.mark.parametrize('hours,expected',[(23.999,'MONITORING'),(24,'RESOLUTION_VERIFIED'),(24.001,'RESOLUTION_VERIFIED')])
def test_elapsed_post_pickup_boundary(hours,expected):assert check(data(25,25+hours))==expected

def test_multiple_aggregate_pickups_use_latest_anchor_without_summing_or_choosing_first():
 values=data(25,49)+[ob('ACTUAL_PICKUPS',40,1.0,'pickups')]
 assert check(values)=='MONITORING'
 assert check(list(reversed(values)))=='MONITORING'
 assert check(data(25,64)+[ob('ACTUAL_PICKUPS',40,1.0,'pickups')])=='RESOLUTION_VERIFIED'
 conflicting=data(25,64)+[ob('ACTUAL_PICKUPS',40,2.0,'pickups')]
 assert check(conflicting)=='INCONCLUSIVE'
