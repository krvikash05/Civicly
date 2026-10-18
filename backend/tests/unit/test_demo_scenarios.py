"""B19 host definition, chronology, closed control and safe inventory units."""
import json,copy
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.services.demo.definitions import load,intake,BASE,Worlds
from app.services.demo.models import DemoResetRequest,DemoAdvanceRequest
from app.services.demo.inventory import ISSUES
from app.services.demo.errors import DemoBlocked
from app.api.application import create_app
from cli.main import parser,ACTIONS
@pytest.mark.parametrize('id',list(ISSUES))
@pytest.mark.parametrize('variant',['release','negative'])
def test_all_world_packets_and_intake_valid(id,variant):
 world=load()[id];catalog=json.loads(Path('contracts/scenarios/catalog.json').read_text())['scenarios']
 assert world.issues==next(s['issue_types'] for s in catalog if s['id']==id)
 for issue in world.issues:
  q=intake(world,issue);assert q['occurred_at']==q['reported_at']==BASE and q['source_kind']=='SYNTHETIC'
  assert getattr(world,variant)[issue]
@pytest.mark.parametrize('bad',[{'scenario_id':'S13'},{'scenario_id':'S01','graph':'civicly_knowledge'},{'scenario_id':'S01','file':'secret'},{'scenario_id':'S01','variant':'other'}])
def test_reset_closed(bad):
 with pytest.raises(ValidationError):DemoResetRequest.model_validate({'scenario_id':'S01','seed':19,'confirm':True,**bad})
@pytest.mark.parametrize('field',['query','world','tool','command','clock','observations','hidden_truth','plan_id'])
def test_release_closed_and_relevant(field):
 with pytest.raises(ValidationError):DemoAdvanceRequest.model_validate({'expected_current_stage':'BASELINE_VISIBLE','stage':'EVIDENCE_REVEALED',field:'forbidden'})
@pytest.mark.parametrize('change',['duplicate','missing','unit','issue'])
def test_definition_validation(change):
 raw=json.loads(Path('data/scenarios/runtime-v1.json').read_text())
 if change=='duplicate':raw['scenarios'][1]=copy.deepcopy(raw['scenarios'][0])
 elif change=='missing':raw['scenarios'][0]['release']={}
 elif change=='unit':raw['scenarios'][0]['release']['WATERLOGGING'][0]['value']=1.0
 else:raw['scenarios'][0]['issues']=['MISC']
 with pytest.raises(ValidationError):Worlds.model_validate(raw)
def test_demo_openapi_cli_parity_and_no_selectors():
 api=create_app().openapi()
 for a,(method,path) in ACTIONS['demo'].items():
  assert method.lower() in api['paths']['/api/v1'+path]
 assert not api['paths']['/api/v1/demo/scenarios']['get'].get('parameters')
 parsed=parser().parse_args(['--profile','private','--auth-store','private','--memory-profile','private','--session','private','demo','advance','--id','S01','--payload','request.json','--key','one','--field-session','field','--reviewer-session','reviewer'])
 assert parsed.field_session=='field' and parsed.reviewer_session=='reviewer'
def test_no_raw_blocker():
 with pytest.raises(ValueError):DemoBlocked('private raw exception')
@pytest.mark.parametrize('id',list(ISSUES))
def test_baseline_references_issue_assets_and_time(id):
 world=load()[id]
 bundle=json.loads(Path('data/ingestion/city-v3.json').read_text());nodes={n['properties']['id']:n for n in bundle['nodes']}
 from app.services.demo.definitions import target
 for issue in world.issues:
  q=intake(world,issue);asset,location,department=target(world,issue)
  assert asset in q['asset_ids'] and asset in nodes
  assert location in nodes or (id=='S08' and location=='B19-NEARBY')
  assert department in nodes and nodes[department]['label']=='Department'
  if issue=='ROAD_DAMAGE':assert any(nodes[a]['label']=='RoadSegment' for a in q['asset_ids'])
  if issue=='WASTE_ACCUMULATION':assert any(nodes[a]['label']=='WasteCollectionPoint' for a in q['asset_ids'])
  assert all(n['properties']['created_at']<=BASE for a,n in nodes.items() if a in q['asset_ids'])
def test_baseline_clock_literal_and_quantity_chronology():
 raw=json.loads(Path('data/scenarios/runtime-v1.json').read_text());raw['baseline_at']='2026-01-01T00:00:00Z'
 with pytest.raises(ValidationError):Worlds.model_validate(raw)
 q=intake(load()['S02'],'WATERLOGGING');m=q['details']['measurements'][0]
 assert m['unit']=='mm' and m['value']==125.0 and m['observed_at']==BASE and m['basis']=='REPORTED'
@pytest.mark.parametrize('path',['data/scenarios/hidden_truth.json','data/scenarios/event_reveals.json','data/scenarios/runtime-v1.json','contracts/scenarios/catalog.json','contracts/demo_scenarios.json','docs/demo/SCENARIOS.md'])
def test_agent_cannot_open_world_or_evaluator_files(path):
 from app.agents.isolation import agent_files
 with agent_files():
  with pytest.raises(PermissionError):Path(path).read_text()
 assert Path(path).is_file()
def test_guard_scope_restored_and_symlink_denied(tmp_path):
 from app.agents.isolation import agent_files
 alias=tmp_path/'alias.json';alias.symlink_to(Path('data/scenarios/hidden_truth.json').resolve())
 with agent_files():
  with pytest.raises(PermissionError):alias.read_text()
  assert Path('contracts/schema_registry.json').read_text()
 assert Path('data/scenarios/hidden_truth.json').read_text()
@pytest.mark.parametrize('patch',[{'seed':0},{'seed':True},{'seed':19.0},{'confirm':False},{'confirm':1}])
def test_explicit_normative_seed_and_confirmation(patch):
 with pytest.raises(ValidationError):DemoResetRequest.model_validate({'scenario_id':'S01','seed':19,'confirm':True,**patch})
def test_normative_dto_fields_remain_required():
 from app.services.demo.models import SeedReport,SimulationStepDTO,ScenarioPage,ScenarioDTO
 for cls,names in [(DemoResetRequest,{'scenario_id','seed','confirm'}),(DemoAdvanceRequest,{'stage','expected_current_stage'}),(ScenarioDTO,{'id','title','issue_types','stage'}),(ScenarioPage,{'items','next_cursor','total_count'}),(SeedReport,{'nodes','relationships','source_documents','seed_fingerprint'}),(SimulationStepDTO,{'scenario_id','stage','event_id','revealed_evidence_ids'})]:
  assert names<={k for k,v in cls.model_fields.items() if v.is_required()}
@pytest.mark.parametrize('query',['limit=1','after=2020-01-01T00:00:00Z','x=PRIVATE_INPUT&x=OTHER'])
def test_demo_catalog_rejects_unused_or_repeated_parameters(query):
 from types import SimpleNamespace
 from fastapi.testclient import TestClient
 from app.services.evidence.models import Actor
 s=SimpleNamespace(auth=SimpleNamespace(resolve=lambda token:Actor(id='OP-ANALYST',role='ANALYST')))
 with TestClient(create_app(s)) as c:
  response=c.get('/api/v1/demo/scenarios?'+query,headers={'Authorization':'Bearer mock'})
 assert response.status_code==422 and response.json()['error']['code']=='VALIDATION_ERROR'
 assert 'PRIVATE_INPUT' not in response.text

def test_uncertain_replay_preserves_verified_entity_over_route_label():
 from app.services.http.service import Recovery
 error=Recovery('REQUEST','S01',{'request_id':'REQUEST','entity_id':'ACTUAL-REPORT','investigation_id':'INV'})
 assert error.reconciliation=={'request_id':'REQUEST','entity_id':'ACTUAL-REPORT','investigation_id':'INV'}
 assert Recovery('REQUEST','KNOWN-INSPECTION').reconciliation['entity_id']=='KNOWN-INSPECTION'
