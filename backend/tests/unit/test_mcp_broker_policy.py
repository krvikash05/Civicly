"""Mocked/structural unit tests only; real official server tested separately."""
import asyncio
import json
from types import SimpleNamespace
import pytest
from pydantic import ValidationError
from app.graph.schema import SchemaError
from app.mcp.policy import Request, ALLOWED, NODE_QUERY, EDGE_QUERY
from app.mcp.broker import ReadBroker, BrokerError, parse_content
from app.mcp.runtime import CITY_GRAPH


@pytest.mark.parametrize('data', [
 {'tool':'query_graph'}, {'tool':'delete_graph'}, {'tool':'list_graphs'},
 {'tool':'query_graph_readonly\x00'}, {'tool':'Query_graph_readonly'},
 {'tool':'query_graph_readonly','query':'CREATE (:X)'},
 {'tool':'query_graph_readonly','template':'node'},
 {'tool':'query_graph_readonly','template':'node','id':'D1','readOnly':False},
 {'tool':'query_graph_readonly','template':'node','id':'D1','params':{}},
 {'tool':'query_graph_readonly','template':'node','id':'D1','as_of':'2026-10-17T00:00:00Z'},
 {'tool':'query_graph_readonly','template':'drainage_edges','id':'D1'},
 {'tool':'query_graph_readonly','template':'drainage_edges','id':'D1','as_of':'yesterday'},
 {'tool':'get_graph_schema','sample_size':101},
 {'tool':'get_graph_schema','template':'node','id':'D1'},
 {'tool':'get_node_schema','label':'CivicSchemaMigration'},
 {'tool':'get_node_schema','label':'DrainSegment) DELETE n'},
 {'tool':'get_relationship_schema','relationship_type':'UNKNOWN'},
 {'tool':'get_node_schema','label':'DrainSegment','sample_size':True},
 {'tool':'get_node_schema','label':'DrainSegment','relationship_type':'DRAINS_TO'},
 {'tool':'get_graph_schema','graph':'civicly_docs'},
])
def test_strict_policy_rejects(data):
 with pytest.raises((ValidationError,SchemaError)):Request.model_validate(data)


def test_parameter_values_never_become_query_text():
 value="x'}) CREATE (:Injected) //"
 args=Request(tool='query_graph_readonly',template='node',id=value).arguments()
 assert args['query']==NODE_QUERY and args['params']['id']==value and value not in args['query']
 args=Request(tool='query_graph_readonly',template='drainage_edges',id=value,as_of='2026-10-17T00:00:00Z').arguments()
 assert args['query']==EDGE_QUERY and 'LIMIT 101' in args['query']


@pytest.mark.parametrize('result',[
 SimpleNamespace(is_error=True,content=[]), SimpleNamespace(is_error=False,content=[]),
 SimpleNamespace(is_error=False,content=[SimpleNamespace(type='image')]),
 SimpleNamespace(is_error=False,content=[SimpleNamespace(type='text',text='not json')]),
 SimpleNamespace(is_error=False,content=[SimpleNamespace(type='text',text='[]')]),
 SimpleNamespace(is_error=False,content=[SimpleNamespace(type='text',text='x'*262145)]),
])
def test_malformed_vendor_outputs_are_rejected(result):
 with pytest.raises((BrokerError,ValueError)):parse_content(result)


def test_denial_traces_withhold_input_and_do_not_invent_identity():
 async def run():
  traces=[];b=ReadBroker(None,traces)
  for payload in ({'tool':'evil-secret-value'}, {'tool':'query_graph_readonly','graph':'private-secret-graph'},
                  {'tool':'get_graph_schema','password':'secret-value'}, {'tool':'get_graph_schema','other':set()}):
   with pytest.raises(BrokerError):await b.call(payload)
  rendered=json.dumps(traces)
  assert 'secret-value' not in rendered and 'private-secret-graph' not in rendered
  assert all(t['server'] is None and t['graph_revision'] is None and t['selection_rationale'] is None for t in traces)
 asyncio.run(run())


def test_mock_timeout_invalidates_session_and_records_status():
 class MockClient:
  async def call_tool(self,*args,**kwargs):await asyncio.sleep(1)
 async def run():
  traces=[];b=ReadBroker(MockClient(),traces,timeout=.01)
  b._ReadBroker__schemas={'query_graph_readonly':{'type':'object'}}
  with pytest.raises(BrokerError,match='TIMEOUT'):await b.call({'tool':'query_graph_readonly','template':'node','id':'D1'})
  with pytest.raises(BrokerError,match='SESSION_UNAVAILABLE'):await b.call({'tool':'query_graph_readonly','template':'node','id':'D1'})
  assert any(t['status']=='TIMEOUT' for t in traces)
 asyncio.run(run())


def test_mock_malformed_result_does_not_become_success():
 class MockClient:
  async def call_tool(self,*args,**kwargs):return SimpleNamespace(is_error=False,content=[SimpleNamespace(type='text',text='{"data":[{"revision":"invented"}],"metadata":[]}')])
 async def run():
  traces=[];b=ReadBroker(MockClient(),traces)
  b._ReadBroker__schemas={'query_graph_readonly':{'type':'object'}}
  with pytest.raises(BrokerError,match='INVALID_OUTPUT'):await b.call({'tool':'get_graph_schema'})
  assert traces[-1]['status']=='INVALID_OUTPUT' and traces[-1]['graph_revision'] is None
 asyncio.run(run())


@pytest.mark.parametrize('failure',['pending','revision_changed','unexpected_node_property','wrong_scope','unknown_schema_label','unknown_schema_property','wrong_endpoint'])
def test_mocked_integrity_and_revision_fail_closed(failure):
 from tests.schema_examples import asset,edge,NOW
 from app.graph.schema import Registry
 registry=Registry();calls=[]
 class MockClient:
  async def call_tool(self,tool,args,**kwargs):
   calls.append(args)
   if args.get('params',{}).get('id')=='0001':
    rev=11 if failure=='revision_changed' and len(calls)>2 else 10
    data={'metadata':[],'data':[{'revision':rev,'pending':'intent' if failure=='pending' else '', 'state':'READY'}]}
   elif tool=='get_graph_schema':
    data={'nodeLabels':['UnregisteredSecretLabel'],'relationshipTypes':[],'connections':[],'connectionSampleSize':100}
   elif tool=='get_node_schema':
    data={'label':'DrainSegment','requestedSampleSize':20,'sampledCount':1,'properties':[{'property':'unknown','frequency':1}]}
   elif failure=='wrong_endpoint':
    data={'metadata':[],'data':[{'source_id':'D1','source_labels':list(registry.labels('Zone')),'target_id':'D2','target_labels':list(registry.labels('DrainSegment')),'relationship':'DRAINS_TO','properties':{**edge('E'),'association_status':'CANDIDATE'}}]}
   else:
    props=asset('DrainSegment','D1')
    if failure=='unexpected_node_property':props['unregistered']='must not discard'
    if failure=='wrong_scope':props['municipality_id']='elsewhere'
    data={'metadata':[],'data':[{'labels':list(registry.labels('DrainSegment')),'properties':props}]}
   return SimpleNamespace(is_error=False,content=[SimpleNamespace(type='text',text=json.dumps(data))])
 async def run():
  traces=[];b=ReadBroker(MockClient(),traces)
  b._ReadBroker__schemas={tool:{'type':'object'} for tool in ALLOWED}
  request={'tool':'query_graph_readonly','template':'node','id':'D1'}
  if failure=='unknown_schema_label':request={'tool':'get_graph_schema'}
  if failure=='unknown_schema_property':request={'tool':'get_node_schema','label':'DrainSegment'}
  if failure=='wrong_endpoint':request={'tool':'query_graph_readonly','template':'drainage_edges','id':'D1','as_of':NOW}
  expected={'pending':'GRAPH_WRITE_PENDING','revision_changed':'GRAPH_REVISION_CHANGED'}.get(failure,'INVALID_OUTPUT')
  with pytest.raises(BrokerError,match=expected):await b.call(request)
  assert traces[-1]['status']==expected and traces[-1]['graph_revision'] is None
 asyncio.run(run())
