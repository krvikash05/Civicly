"""Fresh-process delivery proof. Inherits the ordinary provider interlock."""
import asyncio,json,os,sys
from app.active import load,active_scope
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.events.service import Delivery
from app.events.runtime import Runtime
from app.events.worker import Worker
path,at,mode=sys.argv[1:4];p=load(path)
with connect(Settings(_env_file='.env')) as db,active_scope(p):
 r=GraphRepository(db,p.graph);d=Delivery(r,lambda:at)
 if mode=='public':print(json.dumps(d.public(after=int(sys.argv[4]),limit=1)))
 else:
  w=Worker(d,Runtime(p,path,r,lambda:at),'fresh-process-'+mode)
  asyncio.run(w.once(fault='after_claim' if mode=='claim-exit' else None))
  if mode=='claim-exit':os._exit(71)
  print(json.dumps({'status':'RESTARTED','graph':p.graph}))
