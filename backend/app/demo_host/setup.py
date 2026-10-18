"""Fresh-only presenter bootstrap through accepted services; no model decisions."""
import hashlib,secrets
from pathlib import Path
from uuid import uuid4
from graphrag_sdk import ConnectionConfig
from app.active import new_profile,save,provision,active_scope,load
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.graph.schema import utc_now
from app.graph.models import digest
from app.memory.storage import MemoryMigration
from app.memory.service import Memory
from app.memory.models import sources,OWNERS
from app.memory.runtime import Profile
from app.services.planning.storage import PlanMigration
from app.services.planning.service import PlanningService
from app.services.operations.migration import OperationsMigration
from app.services.operations.service import Operations
from app.services.operations.auth import Auth,OPERATORS
from app.services.http.service import Services,request_identity
from app.events.service import Delivery
from cli.private import write_private
from .config import HostConfig,Case

async def setup(db,settings,directory):
 directory=Path(directory).absolute()
 if directory.exists() or directory.is_symlink():raise ValueError('FRESH_DEMO_DIRECTORY_REQUIRED')
 directory.mkdir(mode=0o700,parents=False)
 # New independent organizational-memory graphs, no accepted corpus overwritten.
 from app.graph.targets import new_test_graph_name
 canonical=new_test_graph_name(11);docs='civicly_docs_b11_test_'+uuid4().hex
 MigrationRunner(db,canonical).apply();mr=GraphRepository(db,canonical);now=utc_now()
 for name,id in OWNERS.items():mr.create_node('Department',{'id':id,'schema_version':3,'municipality_id':'demo-city','created_at':now,'updated_at':now,'name':name,'department_type':'SYNTHETIC_ORGANIZATIONAL_OWNER'})
 MemoryMigration(db,canonical).apply()
 cfg=ConnectionConfig(host=settings.host,port=settings.port,username=settings.username,password=settings.password.get_secret_value() if settings.password else None,graph_name=docs,retry_count=1)
 memory=Memory(mr,cfg);ingested=[]
 selected=[s for s in sources() if s.document_id!='D001-PDF' and s.owner_department_id in {'DEPT-DRAIN','DEPT-ROAD','DEPT-WATER','DEPT-SAN'}][:4]
 # Select one actual inspection procedure per responsible department.
 selected=[next(s for s in sources() if s.owner_department_id==dept and s.document_id!='D001-PDF') for dept in ['DEPT-DRAIN','DEPT-ROAD','DEPT-WATER','DEPT-SAN']]
 for s in [*selected,*sources(Path('data/documents/b12r/manifest.json')),*sources(Path('data/documents/b20r_utility/manifest.json'))]:
  result=await memory.ingest(s);ingested.append({'document_id':s.document_id,'canonical_id':s.id,'replayed':result['replayed']})
 root_profile=new_profile();save(root_profile,directory/'bootstrap-profile.json')
 passwords={id:secrets.token_urlsafe(32) for id in OPERATORS}
 auth=Auth.provision(directory/'auth.sqlite3',passwords);write_private(directory/'presenter-credentials.json',passwords)
 tokens={id:auth.login(id,pw) for id,pw in passwords.items()}
 with active_scope(root_profile):
  MigrationRunner(db,root_profile.graph).apply();PlanMigration(db,root_profile.graph).apply();OperationsMigration(db,root_profile.graph).apply();root=GraphRepository(db,root_profile.graph)
  from cli.reset import fixture
  nodes,edges,_=fixture()
  for n in nodes:root.create_node(n['label'],n['properties'])
  for e in edges:root.create_relationship(e['type'],e['source_id'],e['target_id'],e['properties'])
  provision(db,root_profile)
  user='demo_memory_'+uuid4().hex;pw=secrets.token_urlsafe(48)
  db.connection.execute_command('ACL','SETUSER',user,'reset','on','#'+hashlib.sha256(pw.encode()).hexdigest(),'~'+canonical,'~'+docs,'-@all','+ping','+info','+client|setinfo','+graph.ro_query')
  mp=directory/'bootstrap-memory.json';Profile(docs_graph=docs,canonical_graph=canonical,source_graphs=[root_profile.graph],reader_user=user,reader_password=pw).json_private(mp)
  delivery=Delivery(root,utc_now);delivery.activate(operator='OP-ADMIN',reason='Explicit FRONTEND-BACKEND-DEMO new host bootstrap source',authorize=True)
  services=Services(root_profile,directory/'bootstrap-profile.json',root,auth,Operations(PlanningService(root,memory),auth),delivery,utc_now,memory=memory);services._demo_memory_path=mp
  from app.services.demo.service import Demo
  demo=Demo(services);actor=auth.resolve(tokens['OP-ADMIN']);value={'scenario_id':'S05','variant':'PRIMARY','seed':19,'confirm':True}
  demo.prepare_reset(value,actor)
  reset=demo.reset(value,actor,request_identity(root_profile.graph,actor.id,'FRONTEND-BACKEND-DEMO-SOURCE'))
 child=directory/reset['profile_reference'];profile=load(child/'profile.json')
 with active_scope(profile):
  repo=GraphRepository(db,profile.graph)
  from app.services.evidence.writer import common
  for name,kind,a,b in [('FLOW','DRAINS_TO','DRAIN-100','DRAIN-101'),('CONTEXT','UNDERLIES','PIPE-100','ROAD-100')]:
   eid='DEMO-SURVEY-'+name;at=utc_now()
   repo.create_node('Evidence',{**common(eid,at),'recorded_at':at,'observed_at':at,'evidence_type':'SYNTHETIC_TOPOLOGY_SURVEY','summary':'Attributed synthetic inventory survey of physical connectivity only; no cause asserted','source_kind':'SYNTHETIC','source_record_id':'FRONTEND-DEMO-survey-'+name,'basis':'OBSERVED','reliability':'VERIFIED'})
   repo.create_relationship(kind,a,b,{'id':'DEMO-TOPOLOGY-'+name,'municipality_id':'demo-city','created_at':at,'valid_from':at,'source_evidence_id':eid,'association_status':'VERIFIED'})
  from app.services.demo.definitions import load as worlds,intake
  from app.services.complaints.service import ComplaintService
  from app.services.evidence.service import EvidenceService
  from app.services.evidence.reader import Reader
  cases=[];public=[]
  for scenario,issue in [('S01','WATERLOGGING'),('S04','ROAD_DAMAGE'),('S05','WASTE_ACCUMULATION')]:
   out=ComplaintService(repo,clock=utc_now).intake(intake(worlds()[scenario],issue))
   if scenario=='S05':inv=reset['scenario']['cases'][0]['investigation_id']
   else:inv=EvidenceService(repo).execute({'operation':'open','request_id':request_identity(profile.graph,'OP-ANALYST','DEMO-OPEN-'+scenario),'incident_ids':[out.incident_id],'cluster_id':out.cluster_id},auth.resolve(tokens['OP-ANALYST'])).entity_id
   case=Case(scenario=scenario,issue=issue,investigation_id=inv,incident_id=out.incident_id,thread_id='DEMO-'+digest([profile.graph,inv])[:32]);cases.append(case)
   public.append({**case.model_dump(),'complaint_id':out.complaint_id,'cluster_id':out.cluster_id})
  from app.services.responsibility.service import Responsibility
  ownership=Responsibility(repo,auth)
  for asset,dept,who in [('DRAIN-101','DEPT-DRAIN','OP-DRAIN-LEAD'),('ROAD-100','DEPT-ROAD','OP-ROAD-LEAD'),('PIPE-100','DEPT-WATER','OP-WATER-LEAD'),('WASTE-100','DEPT-SAN','OP-WASTE-LEAD')]:
   at=utc_now();row=ownership.execute('submit',None,{'asset_id':asset,'department_id':dept,'source_id':'DEMO-inventory','source_record_id':asset,'source_kind':'SYNTHETIC','observed_at':at,'valid_from':at},request_id='DEMO-OWNER-'+asset,token=tokens[who])
   ownership.execute('review',row['id'],{'expected_hash':row['expected_hash'],'reviewed':True,'reason':'Explicit independent presenter review of synthetic asset responsibility for demonstration'},request_id='DEMO-REVIEW-'+asset,token=tokens['OP-ANALYST'])
  config=HostConfig(mode='LIVE_GEMINI',model=__import__('app.agents.provider',fromlist=['ProviderSettings']).ProviderSettings(_env_file='.env').model,profile=str(child/'profile.json'),memory_profile=str(child/'memory.json'),auth_store=str(directory/'auth.sqlite3'),cases=cases)
  write_private(directory/'host.json',config.model_dump(mode='json'))
  proof={'status':'PREPARED_NOT_LIVE_VERIFIED','source_graph':profile.graph,'checkpoint_graph':profile.checkpoints,'host_config':str(directory/'host.json'),'api_profile':config.profile,'memory_profile':config.memory_profile,'auth_store':config.auth_store,'cases':public,'documents':ingested,'simulated_field_world':True,'model_requests':0,'approvals_created':0,'existing_sources_preserved':True}
  write_private(directory/'setup-receipt.json',proof)
  return proof
