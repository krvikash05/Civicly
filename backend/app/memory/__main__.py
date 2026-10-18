"""Trusted local operator bootstrap; never exposed as an MCP/model write tool."""
import argparse,asyncio,hashlib,json
from uuid import uuid4
from pathlib import Path
from graphrag_sdk import ConnectionConfig
from app.config import Settings
from app.graph.connection import connect
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository,NotFound
from app.graph.schema import utc_now
from app.mcp.runtime import CITY_GRAPH
from app.active import DEFAULT_PROFILE,load
from .models import sources,OWNERS
from .storage import MemoryMigration
from .service import Memory
from .runtime import Profile,PROFILE
async def setup(output,manifest=None):
 settings=Settings(_env_file='.env')
 with connect(settings) as db:
  MigrationRunner(db,'civicly_knowledge').apply();repo=GraphRepository(db,'civicly_knowledge')
  MemoryMigration(db,'civicly_knowledge').apply()
  for name,id in OWNERS.items():
   try:old=repo.get_node(id,'Department');assert old.properties['name']==name
   except NotFound:
    now=utc_now();repo.create_node('Department',{'id':id,'schema_version':3,'municipality_id':'demo-city','created_at':now,'updated_at':now,'name':name,'department_type':'SYNTHETIC_ORGANIZATIONAL_OWNER'})
  cfg=ConnectionConfig(host=settings.host,port=settings.port,username=settings.username,password=settings.password.get_secret_value() if settings.password else None,graph_name='civicly_docs',retry_count=1)
  m=Memory(repo,cfg);results=[]
  for s in (sources(manifest) if manifest else sources()):results.append(await m.ingest(s))
  if PROFILE.exists():
   if PROFILE.is_symlink() or PROFILE.stat().st_mode&0o077:raise ValueError('Private regular profile required')
   profile=Profile.model_validate_json(PROFILE.read_text())
   if (profile.canonical_graph,profile.docs_graph)!=('civicly_knowledge','civicly_docs'):raise ValueError('Existing profile conflict; explicit operator review')
  else:
   allowed=[CITY_GRAPH]
   if DEFAULT_PROFILE.exists():allowed.append(load().graph)
   profile=Profile(docs_graph='civicly_docs',canonical_graph='civicly_knowledge',source_graphs=allowed,reader_user='b11_ro_'+uuid4().hex,reader_password=uuid4().hex+uuid4().hex)
   profile.json_private(PROFILE)
  db.connection.execute_command('ACL','SETUSER',profile.reader_user,'reset','on','#'+hashlib.sha256(profile.reader_password.get_secret_value().encode()).hexdigest(),'~civicly_docs','~civicly_knowledge','-@all','+ping','+info','+client|setinfo','+graph.ro_query')
  now=utc_now();example=await m.retrieve(as_of=now,document_id='D001')
  proof={'status':'PASS','mode':'ACTUAL_SDK_OFFLINE_SOURCED_MEMORY','canonical_graph':'civicly_knowledge','docs_graph':'civicly_docs','migration':MemoryMigration(db,'civicly_knowledge').status(),'registered_versions':len(results),'replayed':sum(r['replayed'] for r in results),'source_ids':[r['id'] for r in results],'example':example,'external_model_requests':0,'source_scope':'demo-city only; unchanged city/active graph read permissions; separate memory reader'}
  Path(output).write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items() if k not in {'example','source_ids'}}))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['setup']);p.add_argument('--output',default='docs/evidence/B11-canonical-setup.json');p.add_argument('--manifest',type=Path);a=p.parse_args();asyncio.run(setup(a.output,a.manifest))
if __name__=='__main__':main()
