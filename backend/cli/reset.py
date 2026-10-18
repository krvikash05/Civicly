"""Fresh-only deterministic starter, never a destructive scenario/city reset."""
import json,os
from pathlib import Path
from app.active import new_profile,save,active_scope,provision,load
from app.graph.models import digest
from app.graph.repository import GraphRepository,Conflict
from app.graph.migration import MigrationRunner
from app.services.http.service import Recovery
from app.services.operations.auth import Denied
from .private import read_json,write_private,scope
ROOT=Path(__file__).resolve().parents[2]

def fixture():
 from app.ingestion.conversion import validate_bundle
 bundle=json.loads((ROOT/'data/ingestion/city-v3.json').read_text())
 validate_bundle(bundle)
 edges=[e for e in bundle['relationships'] if e['source_id']=='DRAIN-100' and e['type'] in {'LOCATED_AT','MAINTAINED_BY'}]
 ids={'DRAIN-100'}|{e['target_id'] for e in edges}|{e['properties']['source_evidence_id'] for e in edges}
 nodes=[n for n in bundle['nodes'] if n['properties']['id'] in ids]
 if len(edges)!=2 or len(nodes)!=4:raise ValueError('FIXED_STARTER_SCOPE')
 hashes={id:bundle['manifest']['record_hashes'][id] for id in ids|{e['properties']['id'] for e in edges}}
 return nodes,edges,hashes

def reset(s,directory,key,actor):
 if actor.role!='ADMIN':raise Denied('RESET_ADMIN_REQUIRED')
 path=Path(directory);manifest=path/'reset.json';binding=digest([scope(s.profile,s.auth.path),actor.id,key,str(path.absolute())])
 request='RESET-B18-'+digest([s.profile.graph,actor.id,key])[:32];store=s.delivery.store
 with s.repo._session() as session:
  prior=store.get('cli_reset',request)
  if prior:
   if prior['binding']!=binding:raise Conflict('RESET_KEY_DESTINATION_CONFLICT')
   if prior['status']!='DONE':raise Recovery(request)
   receipt=prior['receipt']
   if load(path/'profile.json').graph!=receipt['source_graph']:raise Conflict('RESET_PROFILE_BINDING')
   return receipt
 if path.is_symlink():raise ValueError('RESET_DIRECTORY_SYMLINK')
 if path.exists():raise Conflict('RESET_OUTPUT_ALREADY_OWNED')
 nodes,edges,hashes=fixture();profile=new_profile()
 with s.repo._session() as session:
  # Recheck under the same fence: simultaneous callers may have won since read.
  if store.get('cli_reset',request):raise Recovery(request)
  try:store.write(session,[('cli_reset',request,{'id':request,'binding':binding,'status':'DISPATCHING'})])
  except Exception:raise Recovery(request) from None
 started={'binding':binding,'request_id':request,'status':'STARTED'}
 try:
  path.mkdir(mode=0o700,parents=False,exist_ok=False);write_private(manifest,started)
  # Neither target is caller supplied, retained or shared. No drop/delete path.
  if s.repo.client.connection.exists(profile.graph) or s.repo.client.connection.exists(profile.checkpoints):raise Conflict('FRESH_TARGET_EXISTS')
  save(profile,path/'profile.json')
  with active_scope(profile):
   MigrationRunner(s.repo.client,profile.graph).apply()
   repo=GraphRepository(s.repo.client,profile.graph)
   from app.services.planning.storage import PlanMigration
   from app.services.operations.migration import OperationsMigration
   PlanMigration(s.repo.client,profile.graph).apply();OperationsMigration(s.repo.client,profile.graph).apply()
   for n in nodes:repo.create_node(n['label'],n['properties'])
   for e in edges:repo.create_relationship(e['type'],e['source_id'],e['target_id'],e['properties'])
   actual={n['properties']['id']:repo.get_node(n['properties']['id']).content_hash for n in nodes}
   actual.update({e['properties']['id']:repo.get_relationship(e['properties']['id']).content_hash for e in edges})
   if actual!=hashes:raise Conflict('RESET_FIXTURE_READBACK')
   provision(s.repo.client,profile)
   from app.memory.runtime import Profile
   memory=read_json(s._cli_memory_path,private=True)
   Profile.model_validate({**memory,'source_graphs':[profile.graph]}).json_private(path/'memory.json')
   from app.events.service import Delivery
   Delivery(repo,s.clock).activate(operator=actor.id,reason='Explicit B18 fresh starter; no retained history activation',authorize=True)
  receipt={'request_id':request,'source_graph':profile.graph,'fixture_hash':digest(actual),'nodes':4,'edges':2,'previous_source_preserved':True,'source_profile_saved':True,'memory_profile_saved':True,'fixture_asset_id':'DRAIN-100','fixture_location_id':'LOC-005','authority':'CANDIDATE ownership remains unverified; no incident, cause or work seeded'}
  temp=path/'reset.done.json';write_private(temp,{**started,'status':'DONE','receipt':receipt});os.replace(temp,manifest)
  with s.repo._session() as session:store.write(session,[('cli_reset',request,{'id':request,'binding':binding,'status':'DONE','receipt':receipt})])
  return receipt
 except Exception:
  raise Recovery(request) from None
