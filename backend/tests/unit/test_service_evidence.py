"""Synthetic service chronology/identity rules; no database or model success claimed."""
from types import SimpleNamespace
import pytest
from pydantic import ValidationError
from app.services.service_evidence import ServiceRecord,source_properties,parse_source,qualify
from app.graph.repository import PreconditionFailed
T0='2026-10-18T11:58:00.000000Z';T1='2026-10-18T11:59:00.000000Z';T2='2026-10-18T12:00:00.000000Z'
def record(**extra):
 return ServiceRecord.model_validate({'id':'SOURCE','pickup_id':'PICKUP','report_evidence_id':'REPORT','investigation_id':'INV','incident_id':'INC','target_id':'WASTE','route_id':'ROUTE','scheduled_at':T0,'checked_at':T1,'actual_at':T1,'recorded_at':T2,'status':'COMPLETED','record_id':'service-1','observed_by':'LEAD','reviewed_by':'ANALYST',**extra})
@pytest.mark.parametrize('case,ok',[('valid',True),('equal',False),('reverse',False),('unknown',False),('missing_execution',False),('target',False),('source',False),('missed',False)])
def test_pickup_before_deposit(case,ok):
 r=record();at=T2;target='WASTE';source='field-survey'
 if case=='equal':at=T1
 if case=='reverse':at=T0
 if case=='unknown':at=None
 if case=='missing_execution':r=None
 if case=='target':target='OTHER'
 if case=='source':source=r.source_id
 if case=='missed':r=record(status='MISSED',actual_at=None)
 assert qualify(r,target=target,report_source=source,observed_at=at,code='DUMPING_OBSERVED',cause='ILLEGAL_DUMPING')[0]==ok
@pytest.mark.parametrize('status,actual,pickup,ok',[('MISSED',None,'P',True),('UNKNOWN',None,None,False),('COMPLETED',T1,'P',False)])
def test_explicit_missed_service_not_absence(status,actual,pickup,ok):
 r=record(status=status,actual_at=actual,pickup_id=pickup)
 assert qualify(r,target='WASTE',report_source='field',observed_at=T2,code='PICKUP_MISSED_CONFIRMED',cause='MISSED_PICKUP')[0]==ok
@pytest.mark.parametrize('damage',[{'scheduled_at':T2},{'checked_at':T0},{'actual_at':None},{'status':'MISSED'},{'pickup_id':None},{'reviewed_by':'LEAD'},{'department_id':'DEPT-ROAD'},{'source_kind':'AGENT'},{'verified':True}])
def test_closed_service_source(damage):
 with pytest.raises(ValidationError):record(**damage)
@pytest.mark.parametrize('damage',['label','identity','source','date','body'])
def test_source_labels_and_identity_do_not_confer_authority(damage):
 props=source_properties(record())
 if damage=='label':props['reliability']='UNVERIFIED'
 if damage=='identity':props['id']='OTHER'
 if damage=='source':props['source_record_id']='wrong-source'
 if damage=='date':props['observed_at']=T2
 if damage=='body':props['summary']=record(id='OTHER').model_dump_json()
 with pytest.raises(PreconditionFailed):parse_source(props)
def test_roundtrip_unknown_does_not_create_execution_or_schedule():
 r=record(status='UNKNOWN',actual_at=None,pickup_id=None);assert parse_source(source_properties(r))==r
 assert 'schedule_id' not in r.model_dump() # Candidate schedule supplies no execution authority.
@pytest.mark.parametrize('code,cause',[('PICKUP_COMPLETED_CONFIRMED','MISSED_PICKUP'),('PICKUP_MISSED_CONFIRMED','MISSED_PICKUP'),('DUMPING_OBSERVED','ILLEGAL_DUMPING')])
def test_qualitative_code_without_dated_source_never_authorizes(code,cause):
 assert not qualify(None,target='WASTE',report_source='schedule-only',observed_at=T2,code=code,cause=cause)[0]

@pytest.mark.parametrize('scenario,investigation,expected',[('S05','INV',True),('S06','INV',True),('S04','INV',False),('S05','OTHER',False),(None,'INV',False)])
def test_rule3_scope_is_controller_bound(monkeypatch,scenario,investigation,expected):
 from app.services.service_evidence import policy_required,Storage
 monkeypatch.setattr(Storage,'get',lambda self,*a:None if scenario is None else {'id':scenario,'cases':[{'investigation_id':'INV'}]})
 assert policy_required(object(),investigation)==expected

@pytest.mark.parametrize('scenario',['S05','S06'])
def test_accepted_rule2_assessment_bytes_remain_parseable(scenario):
 import json,hashlib
 from pathlib import Path
 from app.services.evidence.models import Assessment
 path=Path('docs/evidence/B20-'+scenario+'-PRIMARY.json');before=hashlib.sha256(path.read_bytes()).hexdigest();body=json.loads(path.read_text());count=0
 for rows in body['assessment_history'].values():
  for value in rows:
   a=Assessment.model_validate(value);assert a.rule_version==2;count+=1
 assert count and hashlib.sha256(path.read_bytes()).hexdigest()==before


def test_new_controller_packet_unavailable_to_agent_reads():
 from pathlib import Path
 from app.agents.isolation import agent_files
 path=Path('data/scenarios/service-evidence-v1.json')
 with agent_files():
  with pytest.raises(PermissionError):path.read_text()
 assert path.is_file()


@pytest.mark.parametrize('present',[False,True])
def test_optional_service_projection_preserves_legacy_evidence_shape(present):
 from app.api.models import EvidenceDTO
 value={'id':'E','expected_hash':'a'*64,'evidence_type':'SOURCE','summary':'Attributed source','source_kind':'SYNTHETIC','source_record_id':'source-record','reliability':'UNVERIFIED','observed_at':None,'recorded_at':T2,'document_id':None,'reviewed':False}
 if present:value['service_record']=record()
 out=EvidenceDTO.model_validate(value).model_dump(mode='json')
 assert ('service_record' in out)==present
 if present:assert out['service_record']==record().model_dump(mode='json')
