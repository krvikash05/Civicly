"""Actual Python MCP server/client/FalkorDB; fault injection explicitly labeled."""
import asyncio,json,os,signal,subprocess
from pathlib import Path
from uuid import uuid4
import pytest
from mcp import Client
from redis.exceptions import ResponseError
from app.config import Settings
from app.graph.connection import connect
from app.graph.targets import new_test_graph_name
from app.graph.migration import MigrationRunner,MigrationError
from app.graph.repository import GraphRepository,Conflict
from app.graph.analysis.evaluation import verify_city
from app.mcp.runtime import CITY_GRAPH
from app.mcp.broker import BrokerError
from app.mcp.civicly.runtime import configure,connections,parameters,load_config
from app.mcp.civicly.broker import open_domain,DomainBroker
from app.mcp.civicly.router import open_runtime
from app.mcp.civicly.storage import TraceStore,TraceMigration
from app.mcp.civicly.contracts import READ,context,digest
from app.mcp.civicly.models import TraceRecord
from app.mcp.civicly.__main__ import proof
from app.graph.schema import utc_now

pytestmark=pytest.mark.integration
REQ={'investigation_id':'B07-TEST','asset_id':'DRAIN-D12','direction':'DOWNSTREAM','max_hops':4}

@pytest.fixture(scope='module',autouse=True)
def runtime_setup():
 with connect(Settings(_env_file='.env')) as admin:configure(admin)

def pids():
 return {int(parts[0]) for r in subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines()
  if len(parts:=r.strip().split(None,2))==3 and int(parts[1])==os.getpid() and '-m app.mcp.civicly.server' in parts[2]}


def test_actual_twelve_handlers_provenance_and_source_unchanged(db):
 bundle=json.loads(Path('data/ingestion/city-v3.json').read_text());before=verify_city(GraphRepository(db,CITY_GRAPH),bundle)
 r=asyncio.run(proof());assert len(r['inventory'])==12
 assert r['initialization']['server']['name']=='civicly-domain' and len(r['actual_tools_list'])==12
 assert all(v['status']!='ERROR' for v in r['results'])
 assert r['verified_default_edges']==0 and r['exploratory_edges']>0
 assert all(e['properties']['association_status']=='CANDIDATE' for e in r['exploratory']['data']['edges'])
 assert all(t['rationale_summary'] is None and t['validated_output'] for t in r['persisted_server_traces'])
 maintenance=next(v for v in r['results'] if v['tool_name']=='get_maintenance_history')
 assert maintenance['records'] and any(n['kind']=='Inspection' for n in maintenance['data']['nodes'])
 assert before==verify_city(GraphRepository(db,CITY_GRAPH),bundle)
 assert not pids()


def test_actual_candidate_temporal_and_bounded_negative_semantics():
 async def run():
  async with open_domain() as b:
   safe=await b.call('civicly::trace_infrastructure_dependencies',REQ)
   exploratory=await b.call('civicly::trace_infrastructure_dependencies',{**REQ,'include_candidates':True})
   assert safe['paths']==[] and safe['status']=='PARTIAL' and safe['search_limited']
   assert exploratory['paths'] and all(p['verification_status']=='CANDIDATE' for p in exploratory['paths'])
   assert exploratory['source_evidence_ids']
   past=await b.call('civicly::trace_infrastructure_dependencies',{**REQ,'as_of':'2020-01-01T00:00:00Z'})
   assert past['status']=='ERROR' and not past['data']['paths'] and past['error']
 asyncio.run(run())

@pytest.mark.parametrize('name',['record_hypothesis_assessment','propose_inspection','propose_resolution_plan','request_plan_approval','create_work_order','record_intervention_outcome','query_graph','delete_graph'])
def test_real_server_does_not_register_or_execute_write_admin_tools(name):
 async def run():
  with parameters() as p:
   async with Client(p,mode='legacy',read_timeout_seconds=8) as c:
    listing=await c.list_tools();assert name not in {t.name for t in listing.tools}
    result=await c.call_tool(name,{'query':'CREATE (:Forbidden)','_context':context().model_dump(mode='json')});assert result.is_error
 asyncio.run(run());assert not pids()

@pytest.mark.parametrize('extra',[{'query':'CREATE (:Forbidden)'},{'graph':'civicly_docs'},{'municipality_id':'other'},{'_context':{}},{'role':'ADMIN'}])
def test_broker_denies_unknown_arguments_and_graphs(extra):
 async def run():
  async with open_domain() as b:
   with pytest.raises(BrokerError,match='INVALID_ARGUMENTS'):await b.call('civicly::trace_infrastructure_dependencies',{**REQ,**extra})
 asyncio.run(run())

@pytest.mark.parametrize('changes',[{'source_graph':'civicly_docs'},{'caller_role':'ADMIN'},{'municipality_id':'other'}])
def test_actual_server_rejects_forged_scope_and_role(changes):
 async def run():
  with parameters() as p:
   async with Client(p,mode='legacy',read_timeout_seconds=8) as c:
    result=await c.call_tool('trace_infrastructure_dependencies',{**REQ,'_context':{**context('B07-TEST').model_dump(mode='json'),**changes}})
    assert result.is_error
 asyncio.run(run())


def test_namespace_router_keeps_official_and_domain_runtime_working():
 async def run():
  async with open_runtime() as b:
   names={t['name'] for t in b.tools()};assert len(names)==16
   node=await b.call('official::query_graph_readonly',{'template':'node','id':'DRAIN-D12'})
   assert node['rows'][0]['properties']['id']=='DRAIN-D12'
   domain=await b.call('civicly::trace_infrastructure_dependencies',REQ);assert domain['graph_revision']==2104
   for name in ['query_graph_readonly','official::delete_graph','civicly::query_graph_readonly','official::trace_infrastructure_dependencies']:
    with pytest.raises(BrokerError):await b.call(name,{})
 asyncio.run(run())


def test_trace_nodes_persist_after_session_shutdown_and_idempotence():
 async def run():
  async with open_domain() as b:return await b.call('civicly::trace_infrastructure_dependencies',REQ)
 result=asyncio.run(run())
 with connections() as (_,writer,name):
  store=TraceStore(writer,name);record=store.get(result['execution_id']);assert record and record.phase=='SERVER'
  before=store.repo._read('MATCH (n:ToolExecution) RETURN count(n)')[0][0]
  assert store.append(record)==result['execution_id']
  assert store.repo._read('MATCH (n:ToolExecution) RETURN count(n)')[0][0]==before
  with pytest.raises(Conflict):store.append(record.model_copy(update={'status':'FORGED'}))
  rows=store.repo._read('MATCH (d:CivicMCPTraceDetail) RETURN d.payload_json LIMIT 1000')
  children=[json.loads(row[0]) for row in rows if json.loads(row[0])['context']['parent_execution_id']==result['execution_id']]
  assert len(children)==1 and children[0]['phase']=='BROKER' and children[0]['validated_output']
  assert record.context.source_graph==CITY_GRAPH and record.graph_revision==2104


def test_separate_database_capabilities_cannot_write_or_cross_graphs():
 with connections() as (reader,writer,name):
  for c,graph,command in [(reader,CITY_GRAPH,'GRAPH.QUERY'),(reader,name,'GRAPH.RO_QUERY'),(writer,CITY_GRAPH,'GRAPH.QUERY'),(writer,CITY_GRAPH,'GRAPH.RO_QUERY')]:
   with pytest.raises(ResponseError):c.connection.execute_command(command,graph,'RETURN 1')


def test_actual_stalled_domain_server_timeout_persists_host_trace_and_recovers():
 async def run():
  async with open_domain(timeout=2) as b:
   pid=next(iter(pids()));os.kill(pid,signal.SIGSTOP)
   try:
    with pytest.raises(BrokerError,match='TIMEOUT'):await b.call('civicly::trace_infrastructure_dependencies',REQ)
    with pytest.raises(BrokerError,match='SESSION_UNAVAILABLE'):await b.call('civicly::trace_infrastructure_dependencies',REQ)
   finally:os.kill(pid,signal.SIGCONT)
  async with open_domain() as b:assert (await b.call('civicly::trace_infrastructure_dependencies',REQ))['graph_revision']==2104
 asyncio.run(run());assert not pids()
 with connections() as (_,writer,name):
  rows=TraceStore(writer,name).repo._read('MATCH (n:ToolExecution {status:$status}) RETURN count(n)',{'status':'TIMEOUT'})
  assert rows[0][0]>0


def test_actual_process_downtime_and_clean_reconnect():
 async def run():
  async with open_domain() as b:
   os.kill(next(iter(pids())),signal.SIGKILL)
   with pytest.raises(BrokerError):await b.call('civicly::trace_infrastructure_dependencies',REQ)
  async with open_domain() as b:assert (await b.call('civicly::trace_infrastructure_dependencies',REQ))['status']=='PARTIAL'
 asyncio.run(run());assert not pids()


def test_after_real_result_corruption_is_rejected_and_retains_server_trace():
 class Fault:
  def __init__(self,c):self.c=c
  @property
  def server_info(self):return self.c.server_info
  @property
  def protocol_version(self):return self.c.protocol_version
  async def list_tools(self):return await self.c.list_tools()
  async def call_tool(self,*a,**kw):
   wire=await self.c.call_tool(*a,**kw);v=json.loads(wire.content[0].text);v['invented_untrusted_field']=True
   return wire.model_copy(update={'content':[wire.content[0].model_copy(update={'text':json.dumps(v)})],'structured_content':v})
 async def run():
  with connections() as (_,writer,name),parameters() as p:
   async with Client(p,mode='legacy',read_timeout_seconds=8) as client:
    b=DomainBroker(Fault(client),TraceStore(writer,name));await b.discover()
    with pytest.raises(BrokerError,match='INVALID_OUTPUT'):await b.call('civicly::trace_infrastructure_dependencies',REQ)
  async with open_domain() as b:assert (await b.call('civicly::trace_infrastructure_dependencies',REQ))['status']=='PARTIAL'
 asyncio.run(run())


def test_compatible_trace_migration_operational_rerun_and_checksum_guard(db):
 name=new_test_graph_name(7)
 try:
  MigrationRunner(db,name).apply();m=TraceMigration(db,name);a=m.apply();assert a['ready'] and m.apply()==a
  assert MigrationRunner(db,name).status()['ready']
  db.select_graph(name).query("MATCH (m:CivicMCPTraceMigration {id:$id}) SET m.checksum=$bad",params={'id':'0002','bad':'invalid'})
  with pytest.raises(MigrationError):m.apply()
  assert db.select_graph(name).ro_query('MATCH (m:CivicMCPTraceMigration) RETURN m.checksum').result_set==[['invalid']]
 finally:
  if name in db.list_graphs():db.select_graph(name).delete()


def test_invalid_dates_and_client_call_budget_are_denied():
 async def run():
  async with open_domain(max_calls=1) as b:
   for values in [{**REQ,'as_of':'2026-10-17T00:00:00+05:30'},{**REQ,'max_hops':7},{**REQ,'max_hops':True}]:
    with pytest.raises(BrokerError,match='INVALID_ARGUMENTS'):await b.call('civicly::trace_infrastructure_dependencies',values)
   await b.call('civicly::trace_infrastructure_dependencies',REQ)
   with pytest.raises(BrokerError,match='CALL_BUDGET'):await b.call('civicly::trace_infrastructure_dependencies',REQ)
 asyncio.run(run())


def test_trace_constraint_failure_retains_records_and_failed_ledger(db):
 name=new_test_graph_name(7);g=db.select_graph(name)
 try:
  MigrationRunner(db,name).apply()
  g.query('CREATE (:CivicMCPTraceDetail {id:$id,payload_json:$raw,payload_sha256:$sha}),(:CivicMCPTraceDetail {id:$id,payload_json:$raw,payload_sha256:$sha})',params={'id':'DUPLICATE','raw':'{}','sha':'test'})
  with pytest.raises(Exception):TraceMigration(db,name).apply()
  assert g.ro_query('MATCH (d:CivicMCPTraceDetail) RETURN count(d)').result_set==[[2]]
  assert g.ro_query('MATCH (m:CivicMCPTraceMigration) RETURN m.state').result_set==[['FAILED']]
  assert MigrationRunner(db,name).status()['ready']
 finally:
  if name in db.list_graphs():g.delete()


def test_partial_trace_migration_can_finish_additively(db):
 name=new_test_graph_name(7);g=db.select_graph(name)
 try:
  MigrationRunner(db,name).apply();m=TraceMigration(db,name)
  g.query('CREATE (m:CivicMCPTraceMigration) SET m=$props',params={'props':{'id':'0002','checksum':m.checksum,'state':'APPLYING','updated_at':utc_now()}})
  m.base._ensure_index(m.plan['indexes'][0])
  assert m.apply()['ready'] and m.apply()['ready']
 finally:
  if name in db.list_graphs():g.delete()


def test_unavailable_custom_server_fails_closed(monkeypatch):
 from contextlib import contextmanager
 from app.mcp.civicly import broker
 @contextmanager
 def absent():
  with parameters() as p:yield p.model_copy(update={'command':'/unavailable/civicly-python'})
 monkeypatch.setattr(broker,'parameters',absent)
 async def run():
  with pytest.raises(BrokerError):
   async with open_domain():raise AssertionError('Unavailable server accepted')
 asyncio.run(run());assert not pids()


def test_trace_write_failure_prevents_acknowledged_success(db):
 from app.mcp.civicly.runtime import TRACE_USER
 async def run():
  try:
   async with open_domain() as b:
    db.connection.execute_command('ACL','SETUSER',TRACE_USER,'-@all')
    with pytest.raises(BrokerError,match='TRACE_PERSISTENCE_FAILED'):
     await b.call('civicly::trace_infrastructure_dependencies',REQ)
  finally:configure(db)
 asyncio.run(run());assert not pids()


@pytest.mark.parametrize('root,relationship',[('WASTE-W03','COLLECTED_BY'),('PIPE-P02','UNDERLIES')])
def test_existing_b05_typed_cross_category_dependencies_exposed(root,relationship):
 async def run():
  async with open_domain() as b:
   args={**REQ,'asset_id':root,'network':'TYPED_DEPENDENCIES','include_candidates':True}
   result=await b.call('civicly::trace_infrastructure_dependencies',args)
   assert result['status']!='ERROR' and any(e['kind']==relationship for e in result['data']['edges'])
   assert all(p['verification_status'] in {'CANDIDATE','REPORTED','VERIFIED'} for p in result['paths'])
   wrong=await b.call('civicly::trace_infrastructure_dependencies',{**args,'asset_id':'INC-FLOOD-02'})
   assert wrong['status']=='ERROR' and not wrong['data']['nodes']
   for direction in ['UPSTREAM','BOTH']:
    with pytest.raises(BrokerError,match='INVALID_ARGUMENTS'):await b.call('civicly::trace_infrastructure_dependencies',{**args,'direction':direction})
 asyncio.run(run())
