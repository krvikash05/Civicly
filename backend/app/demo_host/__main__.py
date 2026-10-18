"""Host-only demo preparation/preflight/worker. HTTP never grants these permits."""
import argparse,asyncio,json
from pathlib import Path
from app.config import Settings
from app.active import active_scope,load as profile_load
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.schema import utc_now
from cli.private import write_private,read_json
from .config import load
from .runtime import local_preflight,model_preflight,LiveRuntime,HostBlocked

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config');sub=p.add_subparsers(dest='operation',required=True)
 s=sub.add_parser('setup');s.add_argument('--directory',required=True)
 s=sub.add_parser('preflight');s.add_argument('--authorize-model-metadata',action='store_true');s.add_argument('--case')
 s=sub.add_parser('queue');s.add_argument('--case',required=True);s.add_argument('--key',required=True)
 s=sub.add_parser('api');s.add_argument('--port',type=int,default=8010)
 sub.add_parser('status')
 sub.add_parser('discover')
 sub.add_parser('alternatives')
 sub.add_parser('rehearsal')
 s=sub.add_parser('release');s.add_argument('--case',required=True);s.add_argument('--inspection',required=True)
 s=sub.add_parser('worker');s.add_argument('--live',action='store_true');s.add_argument('--case',required=True);s.add_argument('--batches',type=int,default=1)
 s=sub.add_parser('context-smoke');s.add_argument('--live',action='store_true');s.add_argument('--case',required=True)
 sub.add_parser('context-smoke-verify')
 s=sub.add_parser('reconcile-no-effect');s.add_argument('--case',required=True);s.add_argument('--decision',required=True);s.add_argument('--authorized',action='store_true')
 args=p.parse_args()
 if args.operation=='setup':
  from .setup import setup
  with connect(Settings(_env_file='.env')) as db:print(json.dumps(asyncio.run(setup(db,Settings(_env_file='.env'),args.directory)),indent=2))
  return
 if not args.config:raise HostBlocked('PRIVATE_HOST_CONFIGURATION_REQUIRED')
 config=load(args.config);profile=profile_load(config.profile);parent=Path(args.config).parent
 if args.operation=='api':
  if not 1024<=args.port<=65535:raise HostBlocked('LOCAL_PORT_REQUIRED')
  import uvicorn
  from .api import api
  uvicorn.run(api(config),host='127.0.0.1',port=args.port,workers=1,access_log=False,log_level='critical',log_config=None)
  return
 with connect(Settings(_env_file='.env')) as db,active_scope(profile):
  repo=GraphRepository(db,profile.graph)
  if args.operation=='reconcile-no-effect':
   from .reconciliation import reconcile
   print(json.dumps(reconcile(config,profile,repo,args.case,args.decision,authorized=args.authorized),indent=2));return
  if args.operation=='context-smoke-verify':
   from .context_smoke import verify_smoke
   print(json.dumps(verify_smoke(config,profile,repo),indent=2));return
  if args.operation=='context-smoke':
   from .context_smoke import smoke
   print(json.dumps(asyncio.run(smoke(config,profile,repo,args.case,live=args.live)),indent=2));return
  if args.operation=='discover':
   from app.events.service import Delivery
   from .source import source_writer
   with source_writer(repo,60):ids=Delivery(repo,utc_now).discover()
   print(json.dumps({'registered_event_ids':ids,'count':len(ids),'execution_performed':False}));return
  if args.operation in {'alternatives','rehearsal'}:
   from .alternatives import alternatives
   from .source import source_writer
   with source_writer(repo,60):result=alternatives(config,repo,rehearsal=args.operation=='rehearsal')
   print(json.dumps(result,indent=2));return
  if args.operation=='release':
   from .release import release
   from .source import source_writer
   with source_writer(repo,60):result=release(config,repo,args.case,args.inspection)
   print(json.dumps(result,indent=2));return
  if args.operation=='status':
   from .status import status
   print(json.dumps(asyncio.run(status(config,profile,repo)),indent=2));return
  if args.operation=='queue':
   if args.case not in {c.investigation_id for c in config.cases}:raise HostBlocked('CASE_NOT_HOST_AUTHORIZED')
   from app.events.service import Delivery
   from .source import source_writer
   with source_writer(repo,60):row=Delivery(repo,utc_now).request_resume(args.case,args.key,operator='PRESENTER',reason='Explicit host-authorized demo investigation wake',authorize=True)
   print(json.dumps({'event_id':row['id'],'status':row['status'],'investigation_id':args.case,'provider_requests':0}));return
  if args.operation=='preflight':
   result=local_preflight(config,profile,repo,case_id=args.case)
   if args.authorize_model_metadata:
    proof=asyncio.run(model_preflight(config));write_private(parent/('compatibility-'+__import__('uuid').uuid4().hex+'.json'),proof)
    # Print safe proof only. Host selects the immutable compatible proof explicitly.
    result['model_metadata']=proof
   print(json.dumps(result,indent=2));return
  if args.live is not True or not 1<=args.batches<=10:raise HostBlocked('EXPLICIT_BOUNDED_HOST_LIVE_AUTHORIZATION_REQUIRED')
  # One operator-authorized invocation handles exactly one allowlisted case;
  # worker claims for other cases are refused rather than paid automatically.
  case=next((c for c in config.cases if c.investigation_id==args.case),None)
  if case is None:raise HostBlocked('CASE_NOT_HOST_AUTHORIZED')
  local_preflight(config,profile,repo,case_id=args.case)
  proofs=[]
  for f in parent.glob('compatibility-*.json'):
   value=read_json(f,private=True)
   if value.get('config_sha256')==config.fingerprint and value.get('status')=='COMPATIBLE':proofs.append(value)
  if not proofs:raise HostBlocked('MODEL_COMPATIBILITY_REQUIRED')
  proof=max(proofs,key=lambda v:v['checked_at'])
  from app.memory.runtime import configured
  from app.services.planning.service import PlanningService
  from app.events.service import Delivery
  from app.events.worker import Worker
  memdb,memory=configured(profile.graph,config.memory_profile).connect()
  try:
   class SelectedRuntime(LiveRuntime):
    async def handle(self,claim):
     if claim['case_id']!=args.case:raise HostBlocked('CASE_NOT_INVOCATION_AUTHORIZED')
     return await super().handle(claim)
   runtime=SelectedRuntime(config,profile,repo,utc_now,planning_service=PlanningService(repo,memory),compatibility=proof)
   worker=Worker(Delivery(repo,utc_now),runtime,'FRONTEND-BACKEND-DEMO-HOST')
   async def selected():
    rows=[]
    for _ in range(args.batches):
     claim=await worker.once(discover=False,case_id=args.case)
     if claim is None:break
     retained=worker.delivery.store.get('delivery_case',claim['case_key'])
     rows.append({'key':claim['key'],'event_ids':claim['ids'],'status':retained['status']})
     if retained['status']!='DONE':break
    return rows
   rows=asyncio.run(selected())
   print(json.dumps({'mode':'LIVE_GEMINI','source_graph':profile.graph,'authorized_case':args.case,'batches':rows,'automatic_retries':False,'result_requires_receipt_and_checkpoint_readback':True}))
   if not rows or any(r['status']!='DONE' for r in rows):raise HostBlocked('LIVE_WAKE_NOT_COMPLETED_REVIEW_REQUIRED')
  finally:memdb.connection.close();memdb.connection.connection_pool.disconnect()
if __name__=='__main__':
 try:main()
 except Exception as error:
  import re
  code=str(error) if isinstance(error,HostBlocked) and re.fullmatch(r'[A-Z][A-Z0-9_]{0,99}',str(error)) else 'HOST_COMMAND_FAILED_REQUIRES_INSPECTION'
  print(json.dumps({'error':code,'raw_exception_exported':False}));raise SystemExit(1)
