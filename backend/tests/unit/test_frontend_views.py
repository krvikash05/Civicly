"""B17 units: pure bounds/framing and mocked read transport, not DB proof."""
import asyncio,json
from types import SimpleNamespace
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from app.api.application import create_app
from app.api.view_models import ReadFilters
from app.api.coverage import ROUTES,B17_PATHS
from app.api.dependencies import HTTPFailure
from app.services.http.stream import cursor_value,frame,EVENT_NAMES,Stream
from app.events.models import TYPES
from app.services.operations.auth import Denied

@pytest.mark.parametrize('query,header,value',[(None,None,0),('0',None,0),(None,'12',12),('12','12',12)])
def test_cursor_precedence(query,header,value):assert cursor_value(query,header)==value
@pytest.mark.parametrize('query,header,code',[('01',None,'CURSOR_INVALID'),('-1',None,'CURSOR_INVALID'),('1.2',None,'CURSOR_INVALID'),('1','2','CURSOR_CONFLICT'),('private-token',None,'CURSOR_INVALID'),('1\n',None,'CURSOR_INVALID')])
def test_cursor_rejections(query,header,code):
 with pytest.raises(HTTPFailure) as error:cursor_value(query,header)
 assert error.value.code==code
@pytest.mark.parametrize('value',[{'limit':51},{'depth':6},{'issue':'OTHER'},{'graph':'private'},{'after':'2026-10-19T00:00:00Z','before':'2026-10-18T00:00:00Z'},{'include_candidates':'yes'}])
def test_closed_finite_filters(value):
 with pytest.raises(ValidationError):ReadFilters.model_validate(value)
def test_framing_escape_and_total_event_mapping():
 text=frame('case_updated',{'safe':'line\nline'},17)
 assert text.count('\ndata: ')==1 and '\nid: ' not in text
 assert text.startswith('id: 17\nevent: case_updated\n') and text.endswith('\n\n')
 assert set(EVENT_NAMES)==set(TYPES)
 assert EVENT_NAMES['AGENT_TOOL_EXECUTED']=='case_tool_called'
def test_openapi_new_routes_are_closed_and_stream_is_stream():
 api=create_app().openapi()
 assert len(api['paths'])==49 and sum(len(v) for v in api['paths'].values())==52
 for path in B17_PATHS:assert 'get' in api['paths']['/api/v1'+path]
 content=api['paths']['/api/v1/events/stream']['get']['responses']['200']['content']
 assert set(content)=={'text/event-stream'}
 assert api['components']['schemas']['GraphSubgraphDTO']['additionalProperties'] is False
 c=TestClient(create_app(),raise_server_exceptions=False)
 assert c.get('/api/v1/events/stream?access_token=private').status_code==503

def test_stream_expired_or_revoked_stops_sanitized_without_cursor_or_ack():
 def denied(token):raise Denied('private raw auth details')
 s=SimpleNamespace(profile=SimpleNamespace(),auth=SimpleNamespace(resolve=denied))
 feed=Stream(s,'private',None,0)
 # Supply context manager-neutral validator to isolate transport expiry behavior.
 feed.validate=lambda:denied('private')
 from contextlib import nullcontext
 import app.services.http.stream as module
 old=module.active_scope;module.active_scope=lambda p:nullcontext()
 class Request:
  async def is_disconnected(self):return False
 try:
  async def collect():return [v async for v in feed.events(Request())]
  result=asyncio.run(collect())
  assert result==[frame('error',{'code':'UNAUTHORIZED','retryable':False})]
  assert 'private' not in ''.join(result) and 'id:' not in result[0]
 finally:module.active_scope=old

def test_disconnect_returns_before_any_read():
 feed=Stream(SimpleNamespace(),None,None,0)
 feed.validate=lambda:(_ for _ in ()).throw(AssertionError('No disconnected reads'))
 class Request:
  async def is_disconnected(self):return True
 async def collect():return [v async for v in feed.events(Request())]
 assert asyncio.run(collect())==[]

@pytest.mark.parametrize('path',B17_PATHS)
def test_every_new_route_requires_a_session(path):
 s=SimpleNamespace(auth=SimpleNamespace(resolve=lambda token:(_ for _ in ()).throw(Denied('private'))))
 c=TestClient(create_app(s),raise_server_exceptions=False)
 res=c.get('/api/v1'+path.replace('{id}','ABSENT'))
 assert res.status_code==401 and res.json()['error']['code']=='UNAUTHORIZED'
 assert 'private' not in res.text

@pytest.mark.parametrize('after,root,cursors,code',[(4,3,[],'CURSOR_FUTURE'),(0,3,[1,3],'CURSOR_EXPIRED'),(1,3,[],'CURSOR_EXPIRED')])
def test_stream_detects_future_and_missing_registration_without_skips(after,root,cursors,code):
 actor=object()
 delivery=SimpleNamespace(active=lambda:None,store=SimpleNamespace(get=lambda *args:{'cursor':root}),public=lambda **kw:{'events':[{'cursor':c} for c in cursors]})
 s=SimpleNamespace(auth=SimpleNamespace(resolve=lambda token:actor),delivery=delivery)
 feed=Stream(s,'private',actor,after)
 with pytest.raises(HTTPFailure) as error:feed.validate()
 assert error.value.code==code

def test_filtering_precedes_resource_count_and_page():
 # Pure mocked rows, not a database-success substitute.
 from app.services.http.views import Views
 v=object.__new__(Views);v.f=ReadFilters(limit=1,status='OPEN');v.actor=None;v.token=None
 rows=[SimpleNamespace(id='A',properties={'status':'ENDED'}),SimpleNamespace(id='B',properties={'status':'OPEN'}),SimpleNamespace(id='C',properties={'status':'OPEN'})]
 v.candidates=lambda kind:rows;v.matches=lambda n:n.properties['status']==v.f.status
 from app.services.http.reads import Reads
 v.r=SimpleNamespace(project=lambda n,*args:{'id':n.id},page=Reads.page)
 v.r.page=lambda items,limit,cursor:Reads.page(None,items,limit,cursor)
 result=v.listing('Incident')
 assert result['total_count']==2 and result['items']==[{'id':'B'}] and result['next_cursor']=='B'


def test_trace_dto_does_not_permit_raw_source_or_provider_properties():
 from app.api.view_models import AgentTraceEvent
 schema=AgentTraceEvent.model_json_schema()
 assert schema['additionalProperties'] is False
 assert not {'arguments','output','journal','provider_body','credentials','reasoning'}&set(schema['properties'])

def test_projection_capacity_is_explicit_and_sanitized(monkeypatch):
 from contextlib import nullcontext
 import app.api.application as application
 import app.services.http.views as views
 from app.graph.analysis.reader import AnalysisBudgetExceeded
 from app.services.evidence.models import Actor
 actor=Actor(id='OP-ANALYST',role='ANALYST',department_id='DEPT-COORD')
 s=SimpleNamespace(profile=None,auth=SimpleNamespace(resolve=lambda token:actor))
 class OverCapacity:
  def __init__(self,*args):pass
  def run(self,*args):raise AnalysisBudgetExceeded('private diagnostic')
 monkeypatch.setattr(views,'Views',OverCapacity);monkeypatch.setattr(application,'active_scope',lambda p:nullcontext())
 response=TestClient(create_app(s),raise_server_exceptions=False).get('/api/v1/dashboard/summary',headers={'Authorization':'Bearer fake-unit-token'})
 assert response.status_code==409 and response.json()['error']['code']=='READ_CAPACITY'
 assert 'private diagnostic' not in response.text

def test_trace_source_binding_mismatch_fails_closed(monkeypatch):
 from contextlib import nullcontext
 from app.graph.repository import PreconditionFailed
 import app.services.activity as module
 import app.mcp.civicly.runtime as runtime
 import app.mcp.civicly.storage as storage
 repo=SimpleNamespace(graph=SimpleNamespace(name='SOURCE-A'),get_node=lambda *args:SimpleNamespace(properties={'thread_id':'THREAD'}),_read=lambda *args:[])
 record=SimpleNamespace(context=SimpleNamespace(source_graph='SOURCE-B',investigation_id='INV',trace_id='THREAD'))
 store=SimpleNamespace(repo=SimpleNamespace(_read=lambda *args:[['EXEC']]),get=lambda id:record)
 monkeypatch.setattr(runtime,'connections',lambda:nullcontext((None,None,'trace-unit')))
 monkeypatch.setattr(storage,'TraceStore',lambda *args:store)
 with pytest.raises(PreconditionFailed,match='TRACE_SCOPE_BINDING'):module.activity(repo,'INV','2026-10-18T00:00:00Z')

def test_trace_cursor_is_canonical_utc_url_safe_and_tie_broken():
 from app.services.activity import trace_key
 a=trace_key({'timestamp':'2026-10-18T12:00:00Z','event_id':'A'})
 b=trace_key({'timestamp':'2026-10-18T12:00:00.000000Z','event_id':'B'})
 assert a=='2026-10-18T12:00:00.000000Z|A' and '+' not in a
 assert a<b

@pytest.mark.parametrize('phase,source',[('BROKER','SOURCE-A'),('SERVER','SOURCE-B')])
def test_trace_parent_phase_and_source_binding_fail_closed(monkeypatch,phase,source):
 from contextlib import nullcontext
 from app.graph.repository import PreconditionFailed
 import app.services.activity as module
 import app.mcp.civicly.runtime as runtime
 import app.mcp.civicly.storage as storage
 repo=SimpleNamespace(graph=SimpleNamespace(name='SOURCE-A'),get_node=lambda *args:SimpleNamespace(properties={'thread_id':'THREAD'}),_read=lambda *args:[])
 ctx=SimpleNamespace(source_graph='SOURCE-A',investigation_id='INV',trace_id='THREAD',parent_execution_id='SERVER')
 record=SimpleNamespace(context=ctx,phase='BROKER',finished_at='2026-10-18T00:00:00Z')
 parent=SimpleNamespace(phase=phase,context=SimpleNamespace(source_graph=source,investigation_id='INV',trace_id='THREAD',parent_execution_id='DECISION'))
 store=SimpleNamespace(repo=SimpleNamespace(_read=lambda *args:[['CHILD']]),get=lambda id:record if id=='CHILD' else parent)
 monkeypatch.setattr(runtime,'connections',lambda:nullcontext((None,None,'trace-unit')))
 monkeypatch.setattr(storage,'TraceStore',lambda *args:store)
 with pytest.raises(PreconditionFailed,match='TRACE_PARENT_BINDING'):module.activity(repo,'INV','2026-10-18T00:00:00Z')
