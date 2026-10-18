"""Fresh process actual native order/audit read; no mutation/provider."""
import json,sys
from pathlib import Path
from app.active import load,active_scope
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.services.operations.storage import Storage
from app.services.operations.auth import Auth
private=json.loads(sys.stdin.read());actor=Auth(private['auth_path']).resolve(private['token'])
p=load(sys.argv[1]);id=sys.argv[2]
with connect(Settings(_env_file='.env')) as db,active_scope(p):
 repo=GraphRepository(db,p.graph);store=Storage(repo);v=store.get('order',id);op=store.get('operation',v['last_operation'])
 events=repo._read('MATCH (:WorkOrder {id:$id})-[:EMITTED_EVENT]->(e:DomainEvent) RETURN properties(e) LIMIT 20',{'id':id})
 Path(sys.argv[3]).write_text(json.dumps({'authenticated_operator':actor.model_dump(mode='json'),'order':{**v,'native':repo.get_node(id,'WorkOrder').properties},'operation':op,'events':events},indent=2)+'\n')
