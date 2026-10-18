"""Explicit localhost API host; no seeding, migration, activation or worker start."""
import argparse,os
from contextlib import asynccontextmanager
from app.api.application import create_app

def configured_app(profile_path,auth_path,memory_path,at=None):
 @asynccontextmanager
 async def lifespan(app):
  from app.active import load,active_scope
  from app.config import Settings
  from app.graph.connection import connect
  from app.graph.repository import GraphRepository
  from app.graph.schema import utc_now,timestamp
  from app.services.operations.auth import Auth
  from app.services.planning.service import PlanningService
  from app.services.operations.service import Operations
  from app.events.service import Delivery
  from app.memory.runtime import configured
  from app.services.http.service import Services
  if at:timestamp(at)
  profile=load(profile_path);clock=(lambda:at) if at else utc_now
  with connect(Settings(_env_file='.env')) as db,active_scope(profile):
   memory_profile=configured(profile.graph,memory_path)
   if memory_profile is None:raise RuntimeError('MEMORY_PROFILE_MUST_AUTHORIZE_SOURCE')
   memory_db,memory=memory_profile.connect()
   try:
    r=GraphRepository(db,profile.graph);auth=Auth(auth_path);ops=Operations(PlanningService(r,memory,clock=clock),auth,clock=clock);delivery=Delivery(r,clock);delivery.active()
    app.state.services=Services(profile,profile_path,r,auth,ops,delivery,clock,memory=memory)
    app.state.services._demo_memory_path=memory_path
    yield
   finally:memory_db.connection.close();memory_db.connection.connection_pool.disconnect()
 return create_app(lifespan=lifespan)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',required=True);p.add_argument('--auth-store',required=True);p.add_argument('--memory-profile',required=True);p.add_argument('--at');p.add_argument('--port',type=int,default=8000)
 args=p.parse_args()
 if not 1024<=args.port<=65535:p.error('Local unprivileged port required')
 # No paid permit or provider adapter is constructed by this process.
 import uvicorn
 uvicorn.run(configured_app(args.profile,args.auth_store,args.memory_profile,args.at),host='127.0.0.1',port=args.port,workers=1,access_log=False,log_level='critical',log_config=None)
if __name__=='__main__':
 try:main()
 except Exception:print('CIVICLY_API_CONFIGURATION_FAILED: inspect private configuration and required setup; no raw exception exported');raise SystemExit(1)
