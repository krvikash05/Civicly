"""Actual official Node MCP + Python SDK + real retained FalkorDB; no mock success."""
import asyncio
from contextlib import contextmanager
import json
import os
from pathlib import Path
import signal
import subprocess

import pytest
from mcp import Client
from redis import Redis
from redis.exceptions import ResponseError

from app.mcp.broker import open_broker, BrokerError, parse_content
from app.mcp.__main__ import proof
from app.mcp.policy import ALLOWED
from app.mcp.runtime import provision, server_parameters, load_credentials, CITY_GRAPH, RUNTIME
from app.graph.repository import GraphRepository
from app.graph.analysis.evaluation import verify_city

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def configure_acl(db):
 provision(db)


def child_pids():
 rows=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines()
 return {int(p[0]) for r in rows if len(p:=r.strip().split(None,2))==3 and int(p[1])==os.getpid()
         and str(RUNTIME/'node_modules/@falkordb/mcpserver/dist/index.js') in p[2]}


def test_live_discovery_all_approved_reads_independent_client_and_cleanup(db):
 before=verify_city(GraphRepository(db,CITY_GRAPH),json.loads(Path('data/ingestion/city-v3.json').read_text()))
 assert not child_pids()
 result=asyncio.run(proof())
 assert result['status']=='PASS' and result['independent_official_python_client_equal']
 assert len(result['available_inventory'])==7 and set(result['allowed_tools'])==ALLOWED
 assert result['results'][3]['rows'][0]['properties']['id']=='DRAIN-D12'
 edges=result['results'][4]['rows'];assert edges and all(r['properties']['association_status']=='CANDIDATE' for r in edges)
 assert all(r['graph_revision']==2104 for r in result['results'])
 assert not child_pids()
 assert before==verify_city(GraphRepository(db,CITY_GRAPH),json.loads(Path('data/ingestion/city-v3.json').read_text()))


def test_actual_broker_deny_by_default_and_parameter_injection():
 async def run():
  traces=[]
  async with open_broker(traces) as b:
   assert {t['name'] for t in b.tools()}==ALLOWED
   cases=[({'tool':'query_graph'},'DENIED_TOOL'),({'tool':'delete_graph'},'DENIED_TOOL'),
    ({'tool':'list_graphs'},'DENIED_TOOL'),({'tool':'QUERY_GRAPH_READONLY'},'DENIED_TOOL'),
    ({'tool':'query_graph_readonly\x00'},'DENIED_TOOL'),
    ({'tool':'get_graph_schema','graph':'civicly_docs'},'DENIED_GRAPH'),
    ({'tool':'get_graph_schema','graph':'civicly_knowledge'},'DENIED_GRAPH'),
    ({'tool':'get_graph_schema','graph':'civicly_b01_runtime'},'DENIED_GRAPH'),
    ({'tool':'get_graph_schema','graph':'hidden_ground_truth'},'DENIED_GRAPH'),
    ({'tool':'query_graph_readonly','template':'node','id':'DRAIN-D12','query':'CREATE (:Evil)'},'INVALID_ARGUMENTS'),
    ({'tool':'get_node_schema','label':'CivicSchemaMigration'},'INVALID_ARGUMENTS'),
    ({'tool':'get_relationship_schema','relationship_type':'DRAINS_TO','sample_size':101},'INVALID_ARGUMENTS')]
   calls=sum(t['operation']=='tools/call' for t in traces)
   for args,code in cases:
    with pytest.raises(BrokerError,match=code):await b.call(args)
   assert calls==sum(t['operation']=='tools/call' for t in traces)
   r=await b.call({'tool':'query_graph_readonly','template':'node','id':"DRAIN-D12'}) CREATE (:Injected) //"})
   assert r.rows==[]
 asyncio.run(run())


@pytest.mark.parametrize('query',['CREATE (:B06Forbidden)',
 'MATCH (n:CivicEntity {id:$id}) SET n.name=$value RETURN n.id',
 'MATCH (n:CivicEntity {id:$id}) DELETE n'])
def test_real_readonly_server_rejects_cypher_mutation(query,db):
 before=db.select_graph(CITY_GRAPH).ro_query('MATCH (n:CivicEntity {id:$id}) RETURN properties(n) LIMIT 1',params={'id':'DRAIN-D12'}).result_set
 async def run():
  with server_parameters() as p:
   async with Client(p,mode='legacy',read_timeout_seconds=4) as c:
    result=await c.call_tool('query_graph_readonly',{'graphName':CITY_GRAPH,'query':query,'params':{'id':'DRAIN-D12','value':'forbidden'}})
    assert result.is_error
 asyncio.run(run())
 assert before==db.select_graph(CITY_GRAPH).ro_query('MATCH (n:CivicEntity {id:$id}) RETURN properties(n) LIMIT 1',params={'id':'DRAIN-D12'}).result_set
 assert db.select_graph(CITY_GRAPH).ro_query('MATCH (n:B06Forbidden) RETURN count(n)').result_set==[[0]]


def test_official_strict_mode_acl_other_graph_and_invalid_argument_denials():
 async def run():
  with server_parameters() as p:
   async with Client(p,mode='legacy',read_timeout_seconds=4) as c:
    for tool,args in [
     ('query_graph',{'graphName':CITY_GRAPH,'query':'CREATE (:B06Forbidden)','readOnly':False}),
     ('delete_graph',{'graphName':CITY_GRAPH,'confirmDelete':True}),
     ('query_graph_readonly',{'graphName':'civicly_b01_runtime','query':'RETURN 1'}),
     ('query_graph_readonly',{'graphName':'civicly_docs','query':'RETURN 1'}),
     ('list_graphs',{}),
     ('query_graph_readonly',{'graphName':CITY_GRAPH}),
     ('get_node_schema',{'graphName':CITY_GRAPH,'label':'DrainSegment','sampleSize':0}),
     ('not_a_tool',{})]:
     result=await c.call_tool(tool,args);assert result.is_error,tool
 asyncio.run(run())


def test_database_acl_independent_write_admin_and_key_denials():
 creds=load_credentials()
 c=Redis(host='127.0.0.1',port=6379,username=creds.username,password=creds.password.get_secret_value(),socket_timeout=2)
 try:
  assert c.ping()
  for cmd in [('GRAPH.QUERY',CITY_GRAPH,'RETURN 1'),('GRAPH.DELETE',CITY_GRAPH),('GRAPH.LIST',),
              ('GRAPH.RO_QUERY','civicly_knowledge','RETURN 1'),('CONFIG','GET','*'),('ACL','WHOAMI')]:
   with pytest.raises(ResponseError):c.execute_command(*cmd)
 finally:c.close()


@pytest.mark.parametrize('password',['','incorrect-authentication-value'])
def test_missing_or_incorrect_database_auth_prevents_mcp_startup(password):
 async def run():
  initialized=[False]
  with server_parameters() as p:
   p=p.model_copy(update={'env':{**p.env,'FALKORDB_PASSWORD':password}})
   with pytest.raises(Exception):
    async with Client(p,mode='legacy',read_timeout_seconds=1):
     initialized[0]=True
  assert not initialized[0], 'Unexpected authenticated initialization'
 asyncio.run(run());assert not child_pids()


def test_actual_process_downtime_then_fresh_session_reconnects():
 async def run():
  traces=[]
  async with open_broker(traces) as b:
   assert (await b.call({'tool':'query_graph_readonly','template':'node','id':'DRAIN-D12'})).rows
   pids=child_pids();assert len(pids)==1
   os.kill(next(iter(pids)),signal.SIGKILL)
   with pytest.raises(BrokerError):await b.call({'tool':'get_graph_schema'})
  assert not child_pids()
  async with open_broker(traces) as b:
   assert (await b.call({'tool':'get_graph_schema'})).schema_data
  assert len([t for t in traces if t['operation']=='initialize' and t['status']=='SUCCESS'])==2
 asyncio.run(run());assert not child_pids()


def test_real_stalled_server_timeout_shutdown_and_recovery():
 async def run():
  traces=[]
  async with open_broker(traces,timeout=2) as b:
   pid=next(iter(child_pids()));os.kill(pid,signal.SIGSTOP)
   try:
    with pytest.raises(BrokerError,match='TIMEOUT'):await b.call({'tool':'get_graph_schema'})
    with pytest.raises(BrokerError,match='SESSION_UNAVAILABLE'):await b.call({'tool':'get_graph_schema'})
   finally:os.kill(pid,signal.SIGCONT)
  assert any(t['status']=='TIMEOUT' for t in traces)
  async with open_broker() as b:assert (await b.call({'tool':'get_node_schema','label':'DrainSegment'})).schema_data
 asyncio.run(run());assert not child_pids()


def test_unavailable_server_fail_closed_no_fabricated_identity(monkeypatch):
 from app.mcp import broker
 @contextmanager
 def unavailable():
  with server_parameters() as p:yield p.model_copy(update={'command':'/nonexistent/civicly-node'})
 monkeypatch.setattr(broker,'server_parameters',unavailable)
 async def run():
  traces=[]
  with pytest.raises(BrokerError):
   async with open_broker(traces):raise AssertionError('Unavailable server accepted')
  assert not any(t['operation']=='initialize' and t['status']=='SUCCESS' for t in traces)
 asyncio.run(run());assert not child_pids()


def test_real_call_budget_and_serial_requests():
 async def run():
  async with open_broker(max_calls=3) as b:
   first=await b.call({'tool':'query_graph_readonly','template':'node','id':'DRAIN-D12'});assert first.rows
   with pytest.raises(BrokerError,match='CALL_BUDGET'):await b.call({'tool':'get_graph_schema'})
  async with open_broker() as b:
   rows=await asyncio.gather(*(b.call({'tool':'query_graph_readonly','template':'node','id':id}) for id in ['DRAIN-D12','DRAIN-D18']))
   assert all(r.graph_revision==2104 for r in rows)
 asyncio.run(run());assert not child_pids()


def test_real_fractional_time_boundary_uses_accepted_precision(db):
 from datetime import timedelta
 from app.graph.schema import timestamp
 props=db.select_graph(CITY_GRAPH).ro_query('MATCH (:InfrastructureAsset {id:$id})-[r:DRAINS_TO]->() RETURN properties(r) LIMIT 1',params={'id':'DRAIN-D12'}).result_set[0][0]
 instant=timestamp(props['created_at'])
 same=instant.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
 prior=(instant-timedelta(microseconds=1)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
 async def run():
  async with open_broker() as b:
   req={'tool':'query_graph_readonly','template':'drainage_edges','id':'DRAIN-D12'}
   first=await b.call({**req,'as_of':props['created_at']})
   second=await b.call({**req,'as_of':same})
   earlier=await b.call({**req,'as_of':prior})
   assert first.rows==second.rows and any(r.properties['id']==props['id'] for r in second.rows)
   assert all(r.properties['id']!=props['id'] for r in earlier.rows)
 asyncio.run(run());assert not child_pids()


def test_real_mcp_result_fault_injection_rejected_then_reconnect():
 """Actual transport/read followed by explicit local corruption, not upstream defect."""
 from app.mcp.broker import ReadBroker
 class CorruptAfterRealCall:
  def __init__(self,client):self.client=client
  @property
  def server_info(self):return self.client.server_info
  @property
  def protocol_version(self):return self.client.protocol_version
  async def list_tools(self):return await self.client.list_tools()
  async def call_tool(self,tool,args,**kwargs):
   result=await self.client.call_tool(tool,args,**kwargs)
   if args.get('params',{}).get('id')=='DRAIN-D12':
    data=parse_content(result);assert data['data'][0]['properties']['id']=='DRAIN-D12'
    data['data'][0]['properties']['unknown_contract_property']=True
    result=result.model_copy(update={'content':[result.content[0].model_copy(update={'text':json.dumps(data)})]})
   return result
 async def run():
  traces=[]
  with server_parameters() as p:
   async with Client(p,mode='legacy',read_timeout_seconds=4) as c:
    b=ReadBroker(CorruptAfterRealCall(c),traces);await b.discover()
    with pytest.raises(BrokerError,match='INVALID_OUTPUT'):
     await b.call({'tool':'query_graph_readonly','template':'node','id':'DRAIN-D12'})
    assert traces[-1]['status']=='INVALID_OUTPUT' and traces[-1]['graph_revision'] is None
  async with open_broker() as b:
   assert (await b.call({'tool':'query_graph_readonly','template':'node','id':'DRAIN-D12'})).rows
 asyncio.run(run());assert not child_pids()
