"""Trusted local profile CLI; never enables a paid provider or public listener."""
import argparse,asyncio,json,signal
from app.active import load,active_scope
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.schema import utc_now
from .service import Delivery
from .runtime import Runtime
from .worker import Worker

def main():
 p=argparse.ArgumentParser();p.add_argument('--profile',required=True);p.add_argument('--at');sub=p.add_subparsers(dest='command',required=True)
 a=sub.add_parser('activate');a.add_argument('--operator',required=True);a.add_argument('--reason',required=True);a.add_argument('--event-id',action='append',default=[]);a.add_argument('--authorize',action='store_true')
 a=sub.add_parser('run');a.add_argument('--owner',required=True);a.add_argument('--batches',type=int,default=10);a.add_argument('--poll-seconds',type=float,default=1)
 a=sub.add_parser('public');a.add_argument('--after',type=int,default=0);a.add_argument('--limit',type=int,default=50)
 a=sub.add_parser('inspect');a.add_argument('event_id')
 a=sub.add_parser('reconcile');a.add_argument('case_key')
 a=sub.add_parser('replay');a.add_argument('event_id');a.add_argument('--operator',required=True);a.add_argument('--reason',required=True);a.add_argument('--ceiling',type=int,required=True);a.add_argument('--authorize',action='store_true')
 a=sub.add_parser('resume');a.add_argument('investigation_id');a.add_argument('--request-id',required=True);a.add_argument('--operator',required=True);a.add_argument('--reason',required=True);a.add_argument('--authorize',action='store_true')
 a=sub.add_parser('monitor');a.add_argument('investigation_id');a.add_argument('--due',required=True);a.add_argument('--request-id',required=True);a.add_argument('--authorize',action='store_true')
 args=p.parse_args();profile=load(args.profile);clock=(lambda:args.at) if args.at else utc_now
 with connect(Settings(_env_file='.env')) as db,active_scope(profile):
  repo=GraphRepository(db,profile.graph);d=Delivery(repo,clock);worker=Worker(d,Runtime(profile,args.profile,repo,clock),'local-cli')
  if args.command=='activate':value=d.activate(operator=args.operator,reason=args.reason,event_ids=args.event_id,authorize=args.authorize)
  elif args.command=='public':value=d.public(after=args.after,limit=args.limit)
  elif args.command=='inspect':
   row=d.store.get('delivery',args.event_id);value={k:v for k,v in (row or {}).items() if k in {'id','status','attempts','ceiling','owner','lease_until','batch','history','receipt','source_ref','reason','case_id'}}
  elif args.command=='replay':value=d.replay(args.event_id,operator=args.operator,reason=args.reason,ceiling=args.ceiling,authorize=args.authorize)
  elif args.command=='reconcile':
   claim=d.store.get('delivery_case',args.case_key)
   value={'reconciled':asyncio.run(worker.reconcile(claim))} if claim else {'reconciled':False}
  elif args.command=='resume':
   row=d.request_resume(args.investigation_id,args.request_id,operator=args.operator,reason=args.reason,authorize=args.authorize);value={k:row[k] for k in ['id','status','attempts','case_id']}
  elif args.command=='monitor':value=d.monitor(args.investigation_id,args.due,args.request_id,authorize=args.authorize)
  else:
   worker.owner=args.owner
   async def run():
    loop=asyncio.get_running_loop()
    for sig in [signal.SIGINT,signal.SIGTERM]:loop.add_signal_handler(sig,lambda:setattr(worker,'stopping',True))
    await worker.run(poll_seconds=args.poll_seconds,max_batches=args.batches)
   asyncio.run(run());value={'stopped':True,'mode':'DETERMINISTIC_NO_PROVIDER','graph':profile.graph}
  # Closed public projections only; activation never includes profile credentials.
  if args.command=='replay':value={k:value[k] for k in ['id','status','attempts','ceiling']}
  print(json.dumps(value,indent=2))
if __name__=='__main__':
 try:main()
 except Exception:
  print(json.dumps({'error':'DELIVERY_COMMAND_FAILED_REQUIRES_INSPECTION','detail':'No raw exception exported; inspect durable delivery and repository recovery state'}))
  raise SystemExit(1)
