"""B19 mechanics: actual DB/HTTP/CLI/MCP/Saver; no model solver/live provider."""
import asyncio,hashlib,json,os,secrets,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
from types import SimpleNamespace
import pytest,httpx
from app.config import Settings
from app.graph.connection import connect
from app.active import new_profile,save,provision,active_scope,load
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.services.planning.storage import PlanMigration
from app.services.operations.migration import OperationsMigration
from app.services.operations.auth import Auth,OPERATORS
from app.services.demo.inventory import ISSUES
from app.services.demo.definitions import load as worlds,BASE
from app.api.__main__ import configured_app
from tests.integration.test_memory_graphrag import memory as memory_fixture
pytestmark=pytest.mark.integration
AT='2026-10-18T12:00:00.000000Z'
@pytest.fixture(scope='module')
def shared():
 settings=Settings(_env_file='.env');parent=Path('.runtime/b20-review').resolve();parent.mkdir(mode=0o700,parents=True,exist_ok=True);directory=parent/uuid4().hex;directory.mkdir(mode=0o700)
 with connect(settings) as db:
  gen=memory_fixture.__wrapped__(db,settings);memory=next(gen)
  from app.memory.models import sources
  for dept in ['DEPT-DRAIN','DEPT-ROAD','DEPT-WATER','DEPT-SAN']:
   asyncio.run(memory.ingest(next(s for s in sources() if s.owner_department_id==dept and s.document_id!='D001-PDF')))
  p=new_profile();path=directory/'agent.json';save(p,path)
  with active_scope(p):
   MigrationRunner(db,p.graph).apply();PlanMigration(db,p.graph).apply();OperationsMigration(db,p.graph).apply();r=GraphRepository(db,p.graph)
   from cli.reset import fixture
   nodes,edges,_=fixture()
   for n in nodes:r.create_node(n['label'],n['properties'])
   for e in edges:r.create_relationship(e['type'],e['source_id'],e['target_id'],e['properties'])
   provision(db,p)
   from app.events.service import Delivery
   Delivery(r,lambda:AT).activate(operator='B20-test',reason='Explicit new isolated scenario harness source',authorize=True)
  passwords={id:secrets.token_urlsafe(24) for id in OPERATORS};auth=Auth.provision(directory/'auth.sqlite3',passwords);tokens={id:auth.login(id,pw) for id,pw in passwords.items()}
  from app.memory.runtime import Profile
  user='b20_memory_'+uuid4().hex;pw=secrets.token_urlsafe(48)
  db.connection.execute_command('ACL','SETUSER',user,'reset','on','#'+hashlib.sha256(pw.encode()).hexdigest(),'~'+memory.repo.graph.name,'~'+memory.config.graph_name,'-@all','+ping','+info','+client|setinfo','+graph.ro_query')
  mp=directory/'memory.json';Profile(docs_graph=memory.config.graph_name,canonical_graph=memory.repo.graph.name,source_graphs=[p.graph],reader_user=user,reader_password=pw).json_private(mp)
  yield SimpleNamespace(db=db,p=p,path=path,directory=directory,auth=auth,tokens=tokens,mp=mp,memory=memory,proofs=[])
  try:next(gen)
  except StopIteration:pass


from app.agents.models import Selection
from tests.b10_fixtures import choose
from app.services.evidence.policies import POLICIES
class PolicyModel:
 """Issue-only authored choices, no scenario ID, variant, oracle, or tool results."""
 mode='B20_SCRIPTED_POLICY_SELECTIONS_NOT_GENUINE_AI'
 def __init__(self,*,resume=False):self.resume=resume;self.step=0;self.contexts=[]
 async def choose(self,context,remaining_tokens):
  self.contexts.append(context);state=context['state'];issue=state['issue'];rules=context['policies']
  causes={'WATERLOGGING':['BLOCKAGE','CAPACITY_DEFICIT'],'ROAD_DAMAGE':['SUBGRADE_FAILURE','UTILITY_LEAK'],'WASTE_ACCUMULATION':['MISSED_PICKUP','CAPACITY_SHORTFALL','ILLEGAL_DUMPING']}[issue]
  n=self.step;self.step+=1
  if n==0:
   value=choose('READ',{'asset_id':state['asset_ids'][0],'from_time':'2026-10-18T10:00:00.000000Z','to_time':state['as_of'],'as_of':state['as_of']},'civicly::get_maintenance_history') if self.resume else choose('READ',{'template':'node','id':state['incident_ids'][0]},'official::query_graph_readonly')
  elif not self.resume and n==1:
   args={'investigation_id':state['investigation_id'],'asset_id':'PIPE-100' if issue=='ROAD_DAMAGE' else state['asset_ids'][0],'direction':'DOWNSTREAM' if issue=='ROAD_DAMAGE' else 'BOTH','max_hops':4,'network':'TYPED_DEPENDENCIES' if issue=='ROAD_DAMAGE' else 'DRAINAGE','as_of':state['as_of']}
   value=choose('READ',args,'civicly::trace_infrastructure_dependencies')
  elif not self.resume and n<=len(causes)+1:
   cause=causes[n-2];rule=rules[cause];asset=state['asset_ids'][0]
   if issue=='ROAD_DAMAGE':asset='PIPE-100' if cause=='UTILITY_LEAK' else 'ROAD-100'
   args={'cause_code':cause,'asset_ids':[asset],'statement':'Test competing '+cause+' mechanism; awaiting attributed evidence','mechanism':'Authored synthetic mechanism requiring domain evidence validation','confirming_codes':rule['confirming'],'falsifying_codes':rule['falsifying']}
   if cause=='UTILITY_LEAK':args['topology']={'source_id':asset,'target_id':'ROAD-100','operation':'dependencies','max_hops':3}
   value=choose('PROPOSE',args)
  else:
   offset=n-1 if self.resume else n-2-len(causes)
   value=choose('ASSESS',{'hypothesis_id':context['hypotheses'][offset]['id'],'evidence_ids':[]}) if offset<len(causes) else choose()
  return Selection.model_validate(value),0
