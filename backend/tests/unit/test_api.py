"""HTTP/schema tests with real Auth, mocked read health only, no DB success claim."""
import secrets
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from app.api.application import create_app
from app.api.coverage import ROUTES,DEFERRED_B17,DEFERRED_B19
from app.services.operations.auth import Auth,OPERATORS
@pytest.fixture(scope='module')
def client(tmp_path_factory):
 passwords={id:secrets.token_urlsafe(24) for id in OPERATORS};auth=Auth.provision(tmp_path_factory.mktemp('b16auth')/'auth.sqlite3',passwords)
 from app.services.http.service import Services
 s=object.__new__(Services);s.auth=auth
 async def health(ready=False):return {'status':'ok','dependencies':{'api':'ready'}}
 s.health=health
 c=TestClient(create_app(s),raise_server_exceptions=False);return c,auth,passwords

def test_openapi_exact_matrix_closed_models_and_no_deferred_stubs(client):
 c,_,_=client;v=c.get('/openapi.json').json()
 actual={(method.upper(),path) for path,row in v['paths'].items() for method in row}
 assert actual=={(method,'/api/v1'+path) for method,path,*_ in ROUTES}
 assert all(('GET','/api/v1'+path) not in actual for path in DEFERRED_B17)
 assert all('/api/v1'+path not in v['paths'] for path in DEFERRED_B19)
 for method,path,role,req,res,name in ROUTES:
  op=v['paths']['/api/v1'+path][method.lower()]
  if name=='stream':assert set(op['responses']['200']['content'])=={'text/event-stream'}
  else:assert '$ref' in op['responses']['200']['content']['application/json']['schema']
  if req:assert req.model_json_schema()['additionalProperties'] is False
 assert c.get('/docs').status_code==200
 assert 'Access-Control-Allow-Origin' not in c.get('/openapi.json').headers

@pytest.mark.parametrize('method,path,role,req,res,name',[r for r in ROUTES if r[2]!='PUBLIC'])
def test_every_protected_route_denies_missing_session(client,method,path,role,req,res,name):
 c,_,_=client;r=c.request(method,'/api/v1'+path.replace('{id}','UNKNOWN'),json={} if method=='POST' else None)
 assert r.status_code==401,(path,r.text)
 assert set(r.json())=={'error','request_id'} and r.json()['error']['code']=='UNAUTHORIZED'

@pytest.mark.parametrize('id',['OP-ANALYST','OP-APPROVER','OP-DRAIN-LEAD','OP-ADMIN'])
def test_real_auth_login_identity_logout_revoked(client,id):
 c,auth,pw=client
 bad=c.post('/api/v1/auth/demo-login',json={'operator_id':id,'demo_password':'wrong'});assert bad.status_code==401
 r=c.post('/api/v1/auth/demo-login',json={'operator_id':id,'demo_password':pw[id]});assert r.status_code==200
 token=r.json()['data']['access_token'];h={'Authorization':'Bearer '+token}
 me=c.get('/api/v1/auth/me',headers=h);assert me.status_code==200 and me.json()['data']['role']==OPERATORS[id][0]
 assert c.post('/api/v1/auth/logout',json={},headers=h).status_code==200
 assert c.get('/api/v1/auth/me',headers=h).status_code==401

@pytest.mark.parametrize('body',[{'operator_id':'OP-ANALYST','demo_password':'private','role':'ADMIN'},{'operator_id':'OP-ANALYST','demo_password':'private','graph':'civicly_knowledge'}])
def test_closed_error_does_not_echo_password_or_request(client,body):
 c,_,_=client;r=c.post('/api/v1/auth/demo-login',json=body,headers={'X-Request-ID':'private'})
 assert r.status_code==422 and 'private' not in r.text and len(r.json()['request_id'])==32

def test_expired_session_and_unknown_routes_are_closed(client):
 c,auth,pw=client;token=auth.login('OP-ANALYST',pw['OP-ANALYST'])
 old=auth.clock;auth.clock=lambda:old()+3600
 try:assert c.get('/api/v1/auth/me',headers={'Authorization':'Bearer '+token}).status_code==401
 finally:auth.clock=old
 assert c.get('/api/v1/events/stream').status_code==401  # B17 implemented, protected instead of absent

@pytest.mark.parametrize('model,payload',[
 ('ResumeRequest',{'reason':'Request','role':'ADMIN'}),
 ('ReportRequest',{'expected_hash':'a'*64,'source_id':'S','record_id':'R','observations':[],'review':{'reviewer_id':'OP-ANALYST','reviewed':True,'role':'ANALYST','reason':'Forged'}}),
 ('WorkInspectionRequest',{'expected_hash':'a'*64,'purpose':'COMPLETION','command':{'operation':'report_inspection','request_id':'CALLER','inspection_id':'I','expected_hash':'a'*64,'source_id':'S','record_id':'R','observations':[]}}),
 ('RecurRequest',{'expected_hash':'a'*64,'evidence_ids':[],'window_start':'2026-10-18T00:00:00Z','window_end':'2026-10-18T00:00:01Z','verified_outcome_id':'O','complaint':{'issue_type':'WATERLOGGING','role':'ADMIN'}}),
])
def test_closed_command_models_reject_auth_and_request_identity(model,payload):
 from app.api import models
 from pydantic import ValidationError
 with pytest.raises(ValidationError):getattr(models,model).model_validate(payload)

def test_request_identity_is_stable_source_bound_and_not_graph_disclosure():
 from app.services.http.service import request_identity
 assert request_identity('SOURCE-A','OP','KEY')==request_identity('SOURCE-A','OP','KEY')
 assert request_identity('SOURCE-A','OP','KEY')!=request_identity('SOURCE-B','OP','KEY')
 assert request_identity('SOURCE-A','OP','KEY')!=request_identity('SOURCE-A','OTHER','KEY')
 assert 'SOURCE-A' not in request_identity('SOURCE-A','OP','KEY')

def test_unconfigured_api_fails_closed_without_setup_or_fallback():
 c=TestClient(create_app(),raise_server_exceptions=False)
 r=c.get('/api/v1/health/ready');assert r.status_code==503 and r.json()['error']['code']=='EXTERNAL_UNAVAILABLE'
 assert c.get('/docs').status_code==200

def test_response_validation_is_sanitized_not_raw_data(client,monkeypatch):
 c,auth,pw=client;s=c.app.state.services
 token=auth.login('OP-ANALYST',pw['OP-ANALYST'])
 monkeypatch.setattr(s,'identity',lambda actor:{'password':'private-value','role':'ADMIN'})
 r=c.get('/api/v1/auth/me',headers={'Authorization':'Bearer '+token})
 assert r.status_code==500 and r.json()['error']['code']=='INTERNAL_ERROR'
 assert 'private-value' not in r.text and 'password' not in r.text

@pytest.mark.parametrize('status,verified',[('MONITORING',False),('RESOLUTION_VERIFIED',True),('RECURRENCE_DETECTED',False)])
def test_work_projection_uses_latest_recorded_assessment(status,verified):
 # Mocked projection inputs only; real operational outcomes exercised in HTTP test.
 from app.services.http.reads import Reads
 from types import SimpleNamespace
 native=SimpleNamespace(id='W',kind='WorkOrder',properties={'status':'COMPLETED'},content_hash='a'*64)
 states={'OLD':{'id':'OLD','work_order_id':'W','assessment_status':'RESOLUTION_VERIFIED','evaluated_at':'2026-10-18T00:00:00Z'},'LATEST':{'id':'LATEST','work_order_id':'W','assessment_status':status,'evaluated_at':'2026-10-18T00:00:01Z'}}
 ops=SimpleNamespace(store=SimpleNamespace(get=lambda kind,id:states[id]),read_work_order=lambda id,token:{'assignment':{'task_id':'T','department_id':'D','assignee_id':'OP'},'binding':{'plan_id':'P'},'authorized_by':'APPROVER'})
 reads=Reads(None,ops,None,None);reads.targets=lambda kind,id:['OLD','LATEST'] if kind=='RESULTED_IN' else []
 dto=reads.project(native,None,'private');assert dto['resolution_verified'] is verified and dto['latest_assessment_status']==status
