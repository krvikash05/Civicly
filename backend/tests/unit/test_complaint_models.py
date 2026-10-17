"""Pure typed normalization/units checks, not graph or MCP proof."""
import json,math
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.services.complaints.models import normalize,Measurement,INTAKE,Review,IntakeResult,UNITS
from tests.b08_fixtures import payload


def test_normalization_preserves_original_and_does_not_infer_facts():
    raw=payload(description='  Reported\n standing   water  ',source_id='  fixture-portal ',reported_at='2026-10-18T10:30:00+05:30')
    q,n=normalize(raw)
    assert n.original==raw and q.description=='Reported standing water'
    assert q.source_id=='fixture-portal' and q.reported_at=='2026-10-18T05:00:00.000000Z'
    assert not q.details.measurements and not q.details.claims
    assert normalize(payload(description='Reported standing water'))[1].request_hash==n.request_hash

@pytest.mark.parametrize('changes',[{'issue_type':'UNKNOWN'},{'description':' '},{'source_id':5},{'reported_at':'2026-10-18T05:00:00'},{'occurred_at':'2026-10-19T00:00:00Z'},{'ended_at':'2026-10-18T03:00:00Z'},{'unknown':'discard-me'},{'asset_ids':['D1',' D1 ']},{'asset_ids':('D1',)},{'severity':'URGENT'},{'source_kind':'PRIVATE'}])
def test_invalid_report_rejected_explicitly(changes):
    with pytest.raises((ValueError,ValidationError)):normalize(payload(**changes))

@pytest.mark.parametrize('name,value,unit,expected,canonical',[
 ('water_depth',.5,'m',50.0,'cm'),('rainfall',2.,'cm',20.,'mm'),('duration',2.,'hours',120.,'min'),
 ('pothole_depth',30.,'mm',3.,'cm'),('damage_area',10000.,'cm2',1.,'m2'),('waste_quantity',.25,'m3',250.,'L'),('drain_capacity',2.,'m3/s',2.,'m3/s')])
def test_supported_units_lossless_source_retention(name,value,unit,expected,canonical):
    m=Measurement(name=name,value=value,unit=unit,observed_at='2026-10-18T04:00:00Z',source_id='reported-source',source_reference='measurement-1',basis='OBSERVED')
    result=m.canonical();assert result['value']==expected and result['unit']==canonical
    assert result['original_value']==value and result['original_unit']==unit and result['verification_status']=='REPORTED'

@pytest.mark.parametrize('value,unit',[(True,'cm'),('10','cm'),(-1.,'cm'),(math.inf,'cm'),(1.,'bags'),(math.nan,'cm')])
def test_invalid_measurement_rejected(value,unit):
    with pytest.raises(ValidationError):Measurement(name='water_depth',value=value,unit=unit,observed_at='2026-10-18T04:00:00Z',source_id='s',source_reference='r')


def test_issue_specific_measurement_and_rainfall_chronology():
    m={'name':'water_depth','value':10.,'unit':'cm','observed_at':'2026-10-18T04:00:00Z','source_id':'s','source_reference':'r'}
    with pytest.raises(ValidationError):normalize(payload('ROAD_DAMAGE',details={'measurements':[m]}))
    with pytest.raises(ValidationError):normalize(payload(details={'rainfall_from':'2026-10-18T04:00:00Z','rainfall_to':'2026-10-17T04:00:00Z'}))


def test_contract_schemas_match_actual_strict_models():
    c=json.loads(Path('contracts/complaint_intake.json').read_text())
    assert c['schemas']=={'Intake':INTAKE.json_schema(),'IntakeResult':IntakeResult.model_json_schema(),'Review':Review.model_json_schema()}
    assert c['units']=={name:{unit:list(v) for unit,v in units.items()} for name,units in UNITS.items()}


def test_unit_conversion_overflow_and_future_rainfall_are_rejected():
    with pytest.raises(ValidationError):Measurement(name='water_depth',value=1e308,unit='m',observed_at='2026-10-18T04:00:00Z',source_id='s',source_reference='r')
    with pytest.raises(ValidationError):normalize(payload(details={'rainfall_from':'2026-10-18T03:00:00Z','rainfall_to':'2026-10-18T06:00:00Z'}))


@pytest.mark.parametrize('changes',[{'reviewed':False},{'reviewed':1},{'role':'AGENT'},{'reason':' '}])
def test_grouping_requires_explicit_typed_review_context(changes):
    args={'request_id':'r','reviewer_id':'synthetic-analyst','role':'ANALYST','reviewed':True,'reason':'Reviewed correction','incident_id':'i','target_cluster_id':'p','expected_incident_hash':'a'*64,'expected_membership_hash':'b'*64,'expected_target_hash':'c'*64}
    with pytest.raises(ValidationError):Review(**{**args,**changes})


def test_equivalent_measurements_have_one_canonical_request_identity():
    m={'name':'water_depth','value':.29,'unit':'m','observed_at':'2026-10-18T04:00:00Z','source_id':'source','source_reference':'reading'}
    a=payload(details={'measurements':[m]});b=payload(details={'measurements':[{**m,'value':29.,'unit':'cm'}]})
    qa,na=normalize(a);qb,nb=normalize(b)
    assert na.original==a and nb.original==b
    assert na.request_hash==nb.request_hash
    assert qa.details.measurements[0].canonical()['value']==29.
