"""B19 mechanics: actual DB/HTTP/CLI/MCP/Saver; no model solver/live provider."""
import asyncio,hashlib,json,os,secrets,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
from types import SimpleNamespace
import pytest,httpx
from app.config import Settings
from app.graph.connection import connect
from app.active import new_profile,save,provision,active_scope,load
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.services.planning.storage import PlanMigration
from app.services.operations.migration import OperationsMigration
from app.services.operations.auth import Auth,OPERATORS
from app.services.demo.inventory import ISSUES
from app.services.demo.definitions import load as worlds,BASE
from app.api.__main__ import configured_app
from tests.integration.test_memory_graphrag import memory as memory_fixture
pytestmark=pytest.mark.integration
AT='2026-10-18T12:00:00.000000Z'
@pytest.fixture(scope='module')
def shared(tmp_path_factory):
 settings=Settings(_env_file='.env');parent=Path('.runtime/b19-review').resolve();parent.mkdir(mode=0o700,parents=True,exist_ok=True);directory=parent/uuid4().hex;directory.mkdir(mode=0o700)
 with connect(settings) as db:
  gen=memory_fixture.__wrapped__(db,settings);memory=next(gen)
  from app.memory.models import sources
  for dept in ['DEPT-DRAIN','DEPT-ROAD','DEPT-WATER','DEPT-SAN']:
   asyncio.run(memory.ingest(next(s for s in sources() if s.owner_department_id==dept and s.document_id!='D001-PDF')))
  p=new_profile();path=directory/'agent.json';save(p,path)
  with active_scope(p):
   MigrationRunner(db,p.graph).apply();PlanMigration(db,p.graph).apply();OperationsMigration(db,p.graph).apply();r=GraphRepository(db,p.graph)
   from cli.reset import fixture
   nodes,edges,_=fixture()
   for n in nodes:r.create_node(n['label'],n['properties'])
   for e in edges:r.create_relationship(e['type'],e['source_id'],e['target_id'],e['properties'])
   provision(db,p)
   from app.events.service import Delivery
   Delivery(r,lambda:AT).activate(operator='B19-test',reason='Explicit new isolated scenario harness source',authorize=True)
  passwords={id:secrets.token_urlsafe(24) for id in OPERATORS};auth=Auth.provision(directory/'auth.sqlite3',passwords);tokens={id:auth.login(id,pw) for id,pw in passwords.items()}
  from app.memory.runtime import Profile
  user='b19_memory_'+uuid4().hex;pw=secrets.token_urlsafe(48)
  db.connection.execute_command('ACL','SETUSER',user,'reset','on','#'+hashlib.sha256(pw.encode()).hexdigest(),'~'+memory.repo.graph.name,'~'+memory.config.graph_name,'-@all','+ping','+info','+client|setinfo','+graph.ro_query')
  mp=directory/'memory.json';Profile(docs_graph=memory.config.graph_name,canonical_graph=memory.repo.graph.name,source_graphs=[p.graph],reader_user=user,reader_password=pw).json_private(mp)
  yield SimpleNamespace(db=db,p=p,path=path,directory=directory,auth=auth,tokens=tokens,mp=mp,memory=memory,proofs=[])
  Path('docs/evidence/B19-mechanics-'+directory.name+'.json').write_text(json.dumps({'mode':'REAL_FALKORDB_HTTP_CLI_MCP_SAVER_OFFLINE_WORLD_NOT_AI_SOLVER','runs':shared_proofs,'provider_requests':0},indent=2)+'\n')
  try:next(gen)
  except StopIteration:pass
shared_proofs=[]
async def client_run(shared,path=None,fn=None):
 path=path or shared.path;mp=path.parent/'memory.json' if path!=shared.path else shared.mp
 app=configured_app(path,shared.auth.path,mp,AT)
 async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://local') as c:
  return await fn(c,app.state.services)
def headers(shared,who='OP-ADMIN',key=None,field=None,reviewer=None):
 h={'Authorization':'Bearer '+shared.tokens[who]}
 if key:h['Idempotency-Key']=key
 if field:h['X-Field-Authorization']='Bearer '+shared.tokens[field]
 if reviewer:h['X-Reviewer-Authorization']='Bearer '+shared.tokens[reviewer]
 return h
async def fresh(shared,id,variant,key):
 async def run(c,s):
  start=time.perf_counter();response=await c.post('/api/v1/demo/reset',json={'scenario_id':id,'seed':19,'confirm':True,'variant':variant},headers=headers(shared,key=key));assert response.status_code==200,response.json()
  out=response.json()['data'];out['setup_seconds']=round(time.perf_counter()-start,4)
  replay=await c.post('/api/v1/demo/reset',json={'scenario_id':id,'seed':19,'confirm':True,'variant':variant},headers=headers(shared,key=key));assert replay.status_code==200 and replay.json()['data']=={k:v for k,v in out.items() if k!='setup_seconds'}
  return out
 return await client_run(shared,fn=run)
async def inspection(shared,c,case,key):
 q={'investigation_id':case['investigation_id'],'asset_ids':[case['asset_id']],'department_id':case['department_id'],'inspection_type':'B19_FIELD_SURVEY'}
 made=await c.post('/api/v1/inspections',json=q,headers=headers(shared,'OP-ANALYST',key+'-request'));assert made.status_code==200,made.json();view=made.json()['data']
 lead={'DEPT-DRAIN':'OP-DRAIN-LEAD','DEPT-ROAD':'OP-ROAD-LEAD','DEPT-SAN':'OP-WASTE-LEAD','DEPT-WATER':'OP-WATER-LEAD'}[case['department_id']]
 for status in ['REQUESTED','SCHEDULED','IN_PROGRESS']:
  body={'expected_hash':view['expected_hash'],'status':status}
  if status=='SCHEDULED':body['scheduled_at']=AT
  res=await c.post('/api/v1/inspections/'+view['id']+'/transitions',json=body,headers=headers(shared,lead,key+'-'+status));assert res.status_code==200,res.json();view=res.json()['data']
 return view,lead
@pytest.mark.parametrize('id',list(ISSUES))
@pytest.mark.parametrize('variant',['PRIMARY','NEGATIVE'])
def test_all_scenario_setup_release_and_retained_reset(shared,id,variant):
 async def run():
  first=await fresh(shared,id,variant,id+variant+'-first');second=await fresh(shared,id,variant,id+variant+'-second')
  assert first['source_graph']!=second['source_graph'] and first['baseline_content_hash']==second['baseline_content_hash']
  assert {c['investigation_id'] for c in first['scenario']['cases']}.isdisjoint({c['investigation_id'] for c in second['scenario']['cases']})
  path=shared.path.parent/first['profile_reference']/'profile.json';p=load(path)
  async def progress(c,s):
   catalog=(await c.get('/api/v1/demo/scenarios',headers=headers(shared))).json()['data'];assert len(catalog['items'])==12
   assert all(x['title']=='Demonstration '+x['id'] for x in catalog['items'])
   assert 'underlying_cause' not in json.dumps(catalog) and 'expected_safe_next_actions' not in json.dumps(catalog)
   assert s.repo._read("MATCH (e:Evidence {evidence_type:'INSPECTION_REPORT'}) RETURN count(e)")==[[0]]
   # Out-of-order and missing actual inspection fail before mutation, with safe blockers.
   bad=await c.post('/api/v1/demo/scenarios/'+id+'/advance',json={'expected_current_stage':'BASELINE_VISIBLE','stage':'FOLLOW_UP'},headers=headers(shared,key='wrong-order'));assert bad.status_code==409 and bad.json()['error']['details']['blocker_code']=='DEMO_STAGE_ORDER'
   denied=await c.post('/api/v1/demo/scenarios/'+id+'/advance',json={'expected_current_stage':'BASELINE_VISIBLE','stage':'EVIDENCE_REVEALED'},headers=headers(shared,'OP-ANALYST','wrong-role'));assert denied.status_code==403
   timings=[];released=[]
   for i,case in enumerate(first['scenario']['cases']):
    view,lead=await inspection(shared,c,case,'case-'+str(i))
    body={'expected_current_stage':'BASELINE_VISIBLE','stage':'EVIDENCE_REVEALED','investigation_id':case['investigation_id'],'inspection_id':view['id'],'expected_hash':view['expected_hash']}
    h=headers(shared,key='release-'+str(i),field=lead,reviewer='OP-ANALYST');t=time.perf_counter();response=await c.post('/api/v1/demo/scenarios/'+id+'/advance',json=body,headers=h);assert response.status_code==200,response.json();timings.append(round(time.perf_counter()-t,4));out=response.json()['data'];assert out['scenario_id']==id and out['stage']==out['scenario']['stage'] and out['revealed_evidence_ids']==out['released_evidence_ids'];assert s.delivery.store.get('delivery',out['event_id'])['status']=='PENDING';released+=out['released_evidence_ids']
    replay=await c.post('/api/v1/demo/scenarios/'+id+'/advance',json=body,headers=h);assert replay.status_code==200 and replay.json()['data']==out
    evidence=await c.get('/api/v1/evidence/'+released[-1],headers=headers(shared));assert evidence.status_code==200 and evidence.json()['data']['reviewed']
    report=s.repo.get_node(released[-1],'Evidence');codes={o['code'] for o in json.loads(report.properties['summary'])['observations']};packet=worlds()[id];expected=packet.release if variant=='PRIMARY' else packet.negative;assert codes=={x.code for x in expected[case['issue_type']]}
   assert out['scenario']['current_stage']=='EVIDENCE_REVEALED'
   blocked=await c.post('/api/v1/demo/scenarios/'+id+'/advance',json={'expected_current_stage':'EVIDENCE_REVEALED','stage':'PLAN_AND_APPROVAL'},headers=headers(shared,key='no-plan'));assert blocked.status_code==409 and blocked.json()['error']['details']['blocker_code']=='DEMO_APPROVED_PLAN_REQUIRED'
   assert s.repo._read('MATCH (p:ResolutionPlan) RETURN count(p)')==[[0]] and s.repo._read('MATCH (w:WorkOrder) RETURN count(w)')==[[0]]
   assert s.repo._read("MATCH ()-[r:MAINTAINED_BY]->() WHERE r.association_status<>'CANDIDATE' RETURN count(r)")==[[0]]
   return {'id':id,'variant':variant,'source_graph':p.graph,'retained_second_source':second['source_graph'],'baseline_content_hash':first['baseline_content_hash'],'cases':out['scenario']['cases'],'released_evidence_ids':released,'setup_seconds':[first['setup_seconds'],second['setup_seconds']],'release_seconds':timings,'stage':'EVIDENCE_REVEALED','no_plan_or_work_fabricated':True}
  result=await client_run(shared,path,progress);shared_proofs.append(result)
 asyncio.run(run())

def test_real_postcommit_release_failure_no_redispatch(shared,monkeypatch):
 async def run():
  receipt=await fresh(shared,'S01','PRIMARY','fault-source');path=shared.path.parent/receipt['profile_reference']/'profile.json'
  async def fault(c,s):
   case=receipt['scenario']['cases'][0];view,lead=await inspection(shared,c,case,'fault')
   from app.services.evidence.service import EvidenceService
   original=EvidenceService.readback
   def broken(self,receipt,*a,**kw):
    out=original(self,receipt,*a,**kw)
    if receipt.operation=='report_inspection':raise ValueError('PRIVATE_TEST_FAILURE')
    return out
   monkeypatch.setattr(EvidenceService,'readback',broken)
   body={'expected_current_stage':'BASELINE_VISIBLE','stage':'EVIDENCE_REVEALED','investigation_id':case['investigation_id'],'inspection_id':view['id'],'expected_hash':view['expected_hash']};h=headers(shared,key='uncertain-release',field=lead,reviewer='OP-ANALYST')
   response=await c.post('/api/v1/demo/scenarios/S01/advance',json=body,headers=h);assert response.status_code==409,response.json();error=response.json()['error'];assert error['code']=='RECOVERY_REQUIRED' and error['details']['commitment']=='UNKNOWN'
   monkeypatch.setattr(EvidenceService,'readback',original)
   again=await c.post('/api/v1/demo/scenarios/S01/advance',json=body,headers=h);assert again.status_code==409 and again.json()['error']['details']['request_id']==error['details']['request_id']
   assert again.json()['error']['details']['entity_id']==error['details']['entity_id']
   assert again.json()['error']['details']['investigation_id']==case['investigation_id']
   assert s.repo._read("MATCH (e:Evidence {evidence_type:'INSPECTION_REPORT'}) RETURN count(e)")==[[1]]
   from app.services.evidence.writer import stable
   journal=s.repo.get_node(stable('EV-JOURNAL',lead,error['details']['request_id']),'Evidence')
   assert json.loads(journal.properties['summary'])['state']=='COMMITTED'
   assert s.delivery.store.get('api_request',error['details']['request_id'])['status']=='DISPATCHING'
   # A new key cannot bypass a retained uncertain release reservation/lifecycle.
   new=await c.post('/api/v1/demo/scenarios/S01/advance',json=body,headers=headers(shared,key='replacement-denied',field=lead,reviewer='OP-ANALYST'));assert new.status_code==409
   Path('docs/evidence/B19-uncertain-release.json').write_text(json.dumps({'source_graph':s.profile.graph,'error':error,'committed_journal_id':journal.id,'inspection_id':view['id'],'inspection_report_count':1,'same_key_no_redispatch':True,'replacement_no_release':True,'reservation_retained':True},indent=2)+'\n')
  await client_run(shared,path,fault)
 asyncio.run(run())

def test_representative_real_cli_mcp_saver_events_and_hidden_isolation(shared):
 async def run():
  receipt=await fresh(shared,'S07','PRIMARY','representative-source');path=shared.path.parent/receipt['profile_reference']/'profile.json';p=load(path)
  case=next(c for c in receipt['scenario']['cases'] if c['issue_type']=='WATERLOGGING')
  private=path.parent;mp=private/'memory.json'
  from cli.private import write_private,scope
  sessions={}
  for who in ['OP-ADMIN','OP-ANALYST','OP-DRAIN-LEAD']:
   sessions[who]=private/(who+'.session.json');write_private(sessions[who],{'version':1,'scope':scope(p,shared.auth.path),'token':shared.tokens[who],'operator_id':who,'login_key':'B19-host-provisioned-session'})
  calls=[];env={**os.environ,'PYTHONPATH':str(Path('backend/test_guards').resolve())+os.pathsep+str(Path('backend').resolve())}
  def cli(args,who='OP-ADMIN'):
   result=subprocess.run([sys.executable,'-m','cli','--profile',str(path),'--auth-store',str(shared.auth.path),'--memory-profile',str(mp),'--session',str(sessions[who]),'--at',AT,*args],env=env,capture_output=True,text=True,timeout=60)
   assert all(t not in result.stdout+result.stderr for t in shared.tokens.values())
   value=json.loads(result.stdout);assert result.returncode==0,value;calls.append({'command':' '.join(args[:2]),'status':value['status']});return value['data']
  catalog=cli(['demo','scenarios']);assert len(catalog['items'])==12
  public=cli(['investigate','get','--id',case['investigation_id']],'OP-ANALYST')
  # Every runtime tool catalog is discovered from actual servers. Explicit test-only
  # calls probe the boundary; no claim of model-selected sequence/autonomy.
  from app.agents.mcp import brokers
  from app.mcp.civicly.contracts import context
  future_phrases=[x.statement for world in worlds().values() for packet in [world.release,world.negative] for rows in packet.values() for x in rows]
  truth=json.loads(Path('data/scenarios/hidden_truth.json').read_text())
  async def reads(phase):
   outputs=[]
   async with brokers(p,path,timeout=10,memory_path=mp) as tools:
    ctx=context(case['investigation_id']).model_copy(update={'source_graph':p.graph})
    for forbidden in ['data/scenarios/hidden_truth.json','data/scenarios/event_reveals.json','data/scenarios/runtime-v1.json','contracts/scenarios/catalog.json']:
     with pytest.raises(PermissionError):Path(forbidden).read_text()
    assert tools.catalog() and not any('demo' in t['name'] or 'scenario' in t['name'] or 'hidden' in t['name'] for t in tools.catalog())
    for name,args in [('official::query_graph_readonly',{'template':'node','id':case['incident_id']}),('civicly::get_maintenance_history',{'asset_id':case['asset_id'],'from_time':BASE,'to_time':AT,'as_of':AT}),('civicly::retrieve_external_evidence',{'location_id':'LOC-005','evidence_type':'RAINFALL','from_time':BASE,'to_time':AT,'as_of':AT})]:
     out=await tools.call(name,args,ctx.model_copy(update={'execution_id':uuid4().hex}),'B19 operator boundary probe; not model-selected',cutoff=AT);outputs.append(out)
    docs=await tools.call('civicly::get_organizational_procedures',{'department_id':'DEPT-DRAIN','action_type':'INSPECTION','as_of':AT},ctx.model_copy(update={'execution_id':uuid4().hex}),'B19 sourced organizational read',cutoff=AT);outputs.append(docs)
   raw=json.dumps(outputs)
   assert 'underlying_cause' not in raw and 'evaluation_note' not in raw and 'expected_safe_next_actions' not in raw and 'EVALUATOR_ONLY' not in raw
   if phase=='baseline':assert all(text not in raw for text in future_phrases)
   assert outputs[2]['status']=='UNAVAILABLE'
   return outputs
  before=await reads('baseline')
  # Explicit queue and one actual offline worker, genuine Saver/MCP I/O.
  resume=private/'resume.json';resume.write_text(json.dumps({'reason':'B19 explicit offline boundary check'}))
  queued=cli(['investigate','resume','--id',case['investigation_id'],'--payload',str(resume),'--key','B19-wake'],'OP-ANALYST');assert queued['status']=='PENDING'
  advanced=cli(['advance','run','--key','B19-worker','--batches','1']);assert advanced['batches'][0]['status']=='DONE'
  trace=cli(['investigate','trace','--id',case['investigation_id']],'OP-ANALYST');assert trace['items'] and not trace['recovery_required']
  assert all(x['execution_mode']=='B15_DETERMINISTIC_DEVELOPMENT_NO_PROVIDER' for x in trace['items'])
  from app.agents.checkpoints import saver
  saved=list(saver(p).list(None));assert saved
  checkpoints=[(s.config['configurable']['checkpoint_id'],hashlib.sha256(json.dumps(s.checkpoint,default=str,sort_keys=True).encode()).hexdigest()) for s in saved]
  async def release(c,s):
   view,lead=await inspection(shared,c,case,'representative')
   q={'expected_current_stage':'BASELINE_VISIBLE','stage':'EVIDENCE_REVEALED','investigation_id':case['investigation_id'],'inspection_id':view['id'],'expected_hash':view['expected_hash']};payload=private/'release.json';payload.write_text(json.dumps(q))
   out=cli(['demo','advance','--id','S07','--payload',str(payload),'--key','representative-release','--field-session',str(sessions[lead]),'--reviewer-session',str(sessions['OP-ANALYST'])]);assert not out['stage_advanced']
   # Other categories' unreleased packets remain absent from canonical records and all public views.
   evidence=await c.get('/api/v1/evidence/'+out['released_evidence_ids'][0],headers=headers(shared));assert evidence.status_code==200 and evidence.json()['data']['reviewed']
   graph=(await c.get('/api/v1/investigations/'+case['investigation_id']+'/graph',params={'depth':4,'include_candidates':'true'},headers=headers(shared))).json()['data']
   visible=json.dumps(graph)
   for issue in ['ROAD_DAMAGE','WASTE_ACCUMULATION']:
    assert all(x.statement not in visible for x in worlds()['S07'].release[issue])
   later=s.delivery.discover();assert later
   return out,graph,later
  out,graph,later=await client_run(shared,path,release)
  after=await reads('released')
  assert out['released_evidence_ids'][0] in json.dumps(after)
  assert all('underlying_cause' not in json.dumps(x) and 'expected_safe_next_actions' not in json.dumps(x) for x in [catalog,public,trace,graph])
  assert {(s.config['configurable']['checkpoint_id'],hashlib.sha256(json.dumps(s.checkpoint,default=str,sort_keys=True).encode()).hexdigest()) for s in saver(p).list(None)}>=set(checkpoints)
  Path('docs/evidence/B19-hidden-isolation.json').write_text(json.dumps({'mode':'REAL_CLI_HTTP_MCP_SAVER_EVENTS_SCRIPTED_READPAUSE_NO_SOLVER','source_graph':p.graph,'investigation_id':case['investigation_id'],'cli_calls':calls,'baseline_future_packets_absent':True,'evaluator_fields_absent':True,'unreleased_other_categories_absent':True,'before':before,'after':after,'released_evidence_ids':out['released_evidence_ids'],'graph':graph,'trace':trace,'checkpoint_ids_retained':[id for id,_ in checkpoints],'discovered_event_ids':later,'external_provider_calls':0},indent=2)+'\n')
 asyncio.run(run())
