"""F02 isolated real HTTP verification. No existing graph/profile/auth mutation."""
import os,sys,json,secrets,socket,subprocess,threading,time,hashlib
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'frontend/.runtime'/('f02-'+uuid4().hex)
RUN.mkdir(parents=True,mode=0o700)
RUN.parent.chmod(0o700)
os.environ['CIVICLY_TEST_NO_LIVE']='1'
os.environ['CIVICLY_REQUEST_AUDIT_FILE']=str(RUN/'provider-audit.jsonl')
sys.path[:0]=[str(ROOT/'backend/test_guards'),str(ROOT/'backend')]
from civicly_no_live import install
install()
from app.active import new_profile,save,active_scope
from app.config import Settings
from app.graph.connection import connect
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.graph.schema import utc_now
from app.services.planning.storage import PlanMigration
from app.services.planning.service import PlanningService
from app.services.operations.auth import Auth,OPERATORS
from app.services.operations.migration import OperationsMigration
from app.services.operations.service import Operations,common
from app.events.service import Delivery
from app.services.http.service import Services
from app.api.application import create_app
import uvicorn,httpx

def free_port():
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));return sock.getsockname()[1]

def hashes():
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for name in ['backend/app','backend/tests','contracts'] for p in (ROOT/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts}

before=hashes()
settings=Settings(_env_file=ROOT/'.env',socket_timeout_seconds=10,connect_timeout_seconds=5)
assert settings.host in {'127.0.0.1','localhost'}
profile=new_profile();save(profile,RUN/'profile.json')
passwords={key:secrets.token_urlsafe(24) for key in OPERATORS}
auth=Auth.provision(RUN/'auth.sqlite3',passwords)
backend_port,frontend_port=free_port(),free_port()
with connect(settings) as db,active_scope(profile):
 assert db.connection.ping()
 MigrationRunner(db,profile.graph).apply();PlanMigration(db,profile.graph).apply();OperationsMigration(db,profile.graph).apply()
 repo=GraphRepository(db,profile.graph)
 repo.create_node('Department',{**common('DEPT-F02',utc_now()),'name':'Synthetic frontend integration department','department_type':'ENGINEERING'})
 repo.create_node('Incident',{**common('INC-F03-01',utc_now()),'issue_type':'WATERLOGGING','subtype':'STREET_FLOODING','status':'ACTIVE','severity':'HIGH','started_at':utc_now()})
 repo.create_node('Investigation',{**common('INV-F04-01',utc_now()),'status':'ACTIVE','opened_at':utc_now(),'priority':'HIGH'})
 repo.create_relationship('INVESTIGATES','INV-F04-01','INC-F03-01',{'id':'EDGE-INV-INC','municipality_id':'demo-city','created_at':utc_now()})
 repo.create_node('Evidence',{**common('EVID-F04-01',utc_now()),'evidence_type':'FIELD_INSPECTION','reliability':'VERIFIED','source_kind':'MUNICIPAL','recorded_at':utc_now(),'summary':'Field team confirmed culvert 90% blocked'})
 ops=Operations(PlanningService(repo,clock=utc_now),auth,clock=utc_now)
 delivery=Delivery(repo,utc_now)
 delivery.activate(operator='OP-ANALYST',reason='Isolated frontend verification',authorize=True)
 # No full deployment startup/memory capability or worker activation is implied.
 services=Services(profile,RUN/'profile.json',repo,auth,ops,delivery,utc_now)
 app=create_app(services)
 server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=backend_port,access_log=False,log_level='critical',log_config=None))
 thread=threading.Thread(target=server.run,daemon=True);thread.start()
 frontend=None
 try:
  with httpx.Client(timeout=2) as client:
   for _ in range(100):
    if server.started:break
    time.sleep(.05)
   assert server.started,'ISOLATED_API_STARTUP_FAILED'
   runtime=client.get(f'http://127.0.0.1:{backend_port}/openapi.json').json()
   contract=json.loads((ROOT/'contracts/api_endpoints.json').read_text())
   runtime_routes={(method.upper(),path) for path,value in runtime['paths'].items() for method in value}
   assert runtime_routes=={(r['method'],r['path']) for r in contract['routes']}
   defs=json.loads((ROOT/'contracts/api_models.json').read_text())['$defs']
   for name in ['LoginRequest','DemoSession','OperatorAccount','ErrorEnvelope','DepartmentDTO']:
    assert json.loads(json.dumps(runtime['components']['schemas'][name]).replace('#/components/schemas/','#/$defs/'))==defs[name],name
  env={**os.environ,'CIVICLY_API_ORIGIN':f'http://127.0.0.1:{backend_port}','CIVICLY_DEMO_PASSWORD':passwords['OP-ANALYST'],'CIVICLY_DEMO_OPERATOR_ID':'OP-ANALYST','NEXT_TELEMETRY_DISABLED':'1','F02_FRONTEND_ORIGIN':f'http://127.0.0.1:{frontend_port}'}
  with (RUN/'frontend.log').open('w') as log:
   frontend=subprocess.Popen(['node','node_modules/next/dist/bin/next','start','--hostname','127.0.0.1','--port',str(frontend_port)],cwd=ROOT/'frontend',env=env,stdout=log,stderr=log)
   with httpx.Client(timeout=2) as client:
    for _ in range(150):
     try:
      res=client.get(env['F02_FRONTEND_ORIGIN']);assert res.status_code==200;break
     except httpx.ConnectError:
      assert frontend.poll() is None,'ISOLATED_FRONTEND_STARTUP_FAILED';time.sleep(.1)
    else:raise AssertionError('ISOLATED_FRONTEND_DEADLINE')
   if '--browser' in sys.argv:
    ready=ROOT/'frontend/.runtime/f02-browser-ready.json'
    ready.write_text(json.dumps({'origin':env['F02_FRONTEND_ORIGIN'],'finish':str(RUN/'browser.done')}))
    print('ISOLATED_BROWSER_READY',flush=True)
    deadline=time.monotonic()+55
    while not (RUN/'browser.done').exists() and time.monotonic()<deadline:time.sleep(.1)
    assert (RUN/'browser.done').exists(),'BROWSER_REVIEW_DEADLINE'
   probe=subprocess.run(['node','--experimental-strip-types','scripts/integration_probe.ts'],cwd=ROOT/'frontend',env=env,capture_output=True,text=True,timeout=45)
   # Probe outputs no credentials or response bodies; retain private diagnostics on failure.
   (RUN/'probe.log').write_text(probe.stdout+probe.stderr)
   assert probe.returncode==0,'HTTP_PROBE_FAILED: inspect private frontend/.runtime review logs'
   proof=json.loads(probe.stdout.strip().splitlines()[-1])
   proof.update({'source_graph':profile.graph,'runtime_routes':len(runtime_routes),'runtime_schema_parity':True,'full_readiness':False,'memory_worker_mcp':'NOT_EXERCISED','fresh_auth_store':True,'retained_graph':True})
   assert all(secret not in (RUN/'frontend.log').read_text()+(RUN/'probe.log').read_text() for secret in passwords.values())
   audit=Path(os.environ['CIVICLY_REQUEST_AUDIT_FILE'])
   assert not audit.exists() or not audit.read_text().strip(),'UNEXPECTED_PROVIDER_ATTEMPT'
   after=hashes();proof['backend_code_contract_retention']=before==after
   assert before==after,'CONCURRENT_BACKEND_SOURCE_CHANGED_DURING_CHECK: review rather than overwrite'
   (ROOT/'frontend/docs/evidence/F08-integration.json').write_text(json.dumps(proof,indent=2)+'\n')
   print(json.dumps(proof))
 finally:
  if frontend is not None:frontend.terminate();frontend.wait(timeout=15)
  server.should_exit=True;thread.join(timeout=15)
  assert not thread.is_alive(),'ISOLATED_API_DID_NOT_STOP'
