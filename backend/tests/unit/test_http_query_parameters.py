"""B17-R route/query units; mocked projection boundary, never database proof."""
from contextlib import nullcontext
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.api.application import create_app
from app.api.coverage import ROUTES
from app.api.dependencies import HTTPFailure
from app.api.view_models import ReadFilters,VIEW_QUERY_FIELDS,VIEW_QUERY_MODELS
from app.services.evidence.models import Actor

@pytest.fixture
def transport(monkeypatch):
 import app.api.application as application
 import app.services.http.views as views
 calls=[];actor=Actor(id='OP-APPROVER',role='APPROVER',department_id='DEPT-COORD')
 services=SimpleNamespace(profile=None,auth=SimpleNamespace(resolve=lambda token:actor))
 class ProjectionBoundary:
  def __init__(self,s,actor,token,filters):self.filters=filters
  def run(self,name,id):
   calls.append((name,self.filters.model_dump()))
   raise HTTPFailure(409,'READ_CAPACITY')  # Sentinel: accepted input reached projection.
 monkeypatch.setattr(application,'active_scope',lambda profile:nullcontext())
 monkeypatch.setattr(views,'Views',ProjectionBoundary)
 return TestClient(create_app(services),raise_server_exceptions=False),calls

PATHS={name:path for method,path,role,req,res,name in ROUTES if method=='GET' and name in VIEW_QUERY_FIELDS}
UNSUPPORTED=[('hypotheses','before=2020-01-01T00:00:00Z'),('hypotheses','after=2020-01-01T00:00:00Z'),('dashboard','limit=1'),('dashboard','cursor=PRIVATE-INPUT'),('dashboard','investigation_id=PRIVATE-INPUT'),('trace','issue=WATERLOGGING'),('trace','department_id=PRIVATE-INPUT'),('graph','limit=1'),('neighbors','cursor=PRIVATE-INPUT'),('asset','before=2020-01-01T00:00:00Z'),('asset','limit=1'),('map','depth=1'),('map','include_candidates=true'),('list:Incident','investigation_id=PRIVATE-INPUT'),('list:WorkOrder','depth=1'),('hypotheses','status=OPEN&private=PRIVATE-INPUT')]
@pytest.mark.parametrize('name,query',UNSUPPORTED)
def test_unsupported_queries_are_sanitized_and_never_project(transport,name,query):
 client,calls=transport
 response=client.get('/api/v1'+PATHS[name].replace('{id}','INV')+'?'+query,headers={'Authorization':'Bearer unit-token'})
 assert response.status_code==422 and response.json()['error']['code']=='VALIDATION_ERROR'
 assert 'PRIVATE-INPUT' not in response.text and not calls

@pytest.mark.parametrize('name,field,value',[('hypotheses','status','OPEN'),('hypotheses','limit','1'),('hypotheses','cursor','A'),('dashboard','issue','WATERLOGGING'),('dashboard','before','2020-01-01T00:00:00Z'),('trace','after','2020-01-01T00:00:00Z'),('map','investigation_id','INV'),('map','limit','1'),('graph','depth','2'),('neighbors','include_candidates','true'),('list:Incident','department_id','DEP')])
def test_repeated_supported_queries_reject_before_projection(transport,name,field,value):
 client,calls=transport
 response=client.get('/api/v1'+PATHS[name].replace('{id}','INV'),params=[(field,value),(field,value)],headers={'Authorization':'Bearer unit-token'})
 assert response.status_code==422 and response.json()['error']['code']=='VALIDATION_ERROR' and not calls

@pytest.mark.parametrize('name,query,expected',[
 ('hypotheses',{'limit':'1','cursor':'H1','status':'SUPPORTED'},{'limit':1,'cursor':'H1','status':'SUPPORTED'}),
 ('dashboard',{'issue':'WATERLOGGING','status':'COMPLETED','department_id':'DEP','after':'2020-01-01T00:00:00Z','before':'2026-01-01T00:00:00Z'},{'issue':'WATERLOGGING','status':'COMPLETED','department_id':'DEP'}),
 ('trace',{'limit':'1','status':'SUCCESS','after':'2020-01-01T00:00:00Z','before':'2026-01-01T00:00:00Z'},{'limit':1,'status':'SUCCESS','after':'2020-01-01T00:00:00Z','before':'2026-01-01T00:00:00Z'}),
 ('map',{'limit':'2','cursor':'L1','investigation_id':'INV','issue':'WATERLOGGING'},{'limit':2,'cursor':'L1','investigation_id':'INV','issue':'WATERLOGGING'}),
 ('graph',{'depth':'4','include_candidates':'true'},{'depth':4,'include_candidates':True}),
 ('neighbors',{'depth':'1','include_candidates':'false'},{'depth':1,'include_candidates':False}),
 ('asset',{},{}),
 *[(name,{'limit':'2','status':'OPEN','issue':'WATERLOGGING','department_id':'DEP','after':'2020-01-01T00:00:00Z'},{'limit':2,'status':'OPEN','issue':'WATERLOGGING','department_id':'DEP','after':'2020-01-01T00:00:00Z'}) for name in VIEW_QUERY_FIELDS if name.startswith('list:')],
])
def test_supported_queries_reach_projection_with_existing_types(transport,name,query,expected):
 client,calls=transport
 response=client.get('/api/v1'+PATHS[name].replace('{id}','INV'),params=query,headers={'Authorization':'Bearer unit-token'})
 assert response.status_code==409 and response.json()['error']['code']=='READ_CAPACITY'
 assert len(calls)==1 and calls[0][0]==name
 assert all(calls[0][1][key]==value for key,value in expected.items())

@pytest.mark.parametrize('name',VIEW_QUERY_FIELDS)
def test_openapi_and_closed_model_exactly_match_route_allowlist(name):
 api=create_app().openapi();op=api['paths']['/api/v1'+PATHS[name]]['get']
 query={v['name'] for v in op.get('parameters',[]) if v['in']=='query'}
 assert query==set(VIEW_QUERY_FIELDS[name])==set(VIEW_QUERY_MODELS[name].model_fields)
 assert VIEW_QUERY_MODELS[name].model_json_schema()['additionalProperties'] is False
 with pytest.raises(ValidationError):VIEW_QUERY_MODELS[name].model_validate({'private':'PRIVATE-INPUT'})

@pytest.mark.parametrize('name,query',[('hypotheses','limit=51'),('trace','after=2026-01-01T00:00:00Z&before=2020-01-01T00:00:00Z'),('graph','depth=6'),('neighbors','include_candidates=yes'),('dashboard','issue=INVALID'),('map','limit=-1')])
def test_route_models_preserve_bounds_enums_and_time_validation(transport,name,query):
 client,calls=transport
 response=client.get('/api/v1'+PATHS[name].replace('{id}','INV')+'?'+query,headers={'Authorization':'Bearer unit-token'})
 assert response.status_code==422 and not calls
