"""Fresh process read-only verification of the actual B12 plan/Saver binding."""
import json,sys
from pathlib import Path
from app.active import load,active_scope
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.agents.checkpoints import saver
from app.services.planning.storage import Store
p=load(sys.argv[1]);thread=sys.argv[2];saved=saver(p).get_tuple({'configurable':{'thread_id':thread}})
state=saved.checkpoint['channel_values']['data']
with connect(Settings(_env_file='.env')) as db,active_scope(p):
 payload=Store(GraphRepository(db,p.graph)).get(state['current_plan_id']);assert payload['receipt']['plan_hash']==state['current_plan_hash']
 Path(sys.argv[3]).write_text(json.dumps({'checkpoint_id':saved.config['configurable']['checkpoint_id'],'receipt':payload['receipt'],'draft':payload['draft'],'task_ids':payload['task_ids'],'source_proof':payload['proof'],'thread':thread},indent=2)+'\n')
