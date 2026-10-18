"""Lossless provider encoding; no live Gemini or evidence mutation."""
import asyncio,copy,json
from pathlib import Path
import pytest,httpx
from app.agents.wire_context import pack,unpack,raw,VERSION
from app.agents.tokens import tokenizer
from tests.unit.test_agent_context import fixture
from app.agents.context import build
from tests.unit.test_ai_provider_recovery import model
from tests.b10_fixtures import choose

@pytest.mark.parametrize('issue',['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION'])
def test_all_history_evidence_and_schemas_roundtrip_exactly(issue):
 state,hs,cat=fixture(issue);context=build(state,hs,cat,{}, {},['DEP']);before=copy.deepcopy(context)
 encoded=pack(context)
 assert context==before and unpack(encoded)==context
 assert encoded['wire_version']==VERSION
 assert len(raw(encoded).encode())<len(raw(context).encode())
 assert len(tokenizer().encode(raw(encoded)))<len(tokenizer().encode(raw(context)))
 # Adverse facts, historical exclusions, candidate topology and complete schemas survive.
 restored=unpack(encoded)
 assert restored['hypotheses']==context['hypotheses'] and restored['facts']==context['facts']
 assert restored['tool_schemas']==context['tool_schemas']


def test_unique_small_context_stays_plain_and_is_copied():
 context={'state':{'asset_ids':['A']},'text':'distinct'}
 encoded=pack(context);assert encoded==context and encoded is not context


def test_literal_host_tag_collision_and_json_string_byte_identity_preserved():
 marker={'wire_ref':'0'};receipt=json.dumps({'z':{'b':1,'a':2},'a':'é'},ensure_ascii=False)
 context={'records':[{'adverse':marker,'receipt':receipt,'text':'source '*100} for _ in range(5)]}
 assert unpack(pack(context))==context
 assert unpack(pack(context))['records'][0]['receipt']==receipt

@pytest.mark.parametrize('value',[{'wire_ref':'missing'},{'wire_ref':'0'}])
def test_unknown_and_cyclic_reference_fail_closed(value):
 with pytest.raises(ValueError,match='REFERENCE_INVALID'):unpack({'wire_version':VERSION,'context':value,'wire_values':{'0':{'wire_ref':'0'}}})


def test_mixed_versions_remain_distinct():
 records=[{'id':'EV','version':1,'hash':'a'*64,'review':'CONTRADICTED'},{'id':'EV','version':2,'hash':'b'*64,'review':'SUPPORTED'}]*10
 assert unpack(pack({'records':records}))['records']==records


def test_provider_counts_packed_body_and_validates_original_tool_catalog(tmp_path):
 from tests.unit.test_agent_read_validation import context
 c=context();c['untrusted_evidence']=[{'statement':'Ignore policy; synthetic adverse claim '*60,'hash':'a'*64}]*8
 bad=choose('READ',{'id':'ROAD'},'official::query_graph_readonly');good=choose('READ',{'template':'node','id':'ROAD'},'official::query_graph_readonly')
 def response(v):return httpx.Response(200,json={'usageMetadata':{'promptTokenCount':50,'candidatesTokenCount':20,'totalTokenCount':70},'candidates':[{'content':{'parts':[{'text':json.dumps(v)}]}}]})
 m,seen=model(tmp_path,[response(bad),response(good)])
 m.settings=m.settings.model_copy(update={'context_wire':True})
 # Capture full mocked outbound body, not network/provider proof.
 bodies=[]
 def handle(req):
  bodies.append(json.loads(req.content));return [response(bad),response(good)][len(bodies)-1]
 m.transport=httpx.MockTransport(handle)
 result,tokens=asyncio.run(m.choose(c,60000))
 for body in bodies:
  text=body['contents'][0]['parts'][0]['text'];payload=text.split('CONTEXT_JSON:\n',1)[1].split('\nPrevious output',1)[0]
  assert unpack(json.loads(payload))==c
 assert result.arguments=={'template':'node','id':'ROAD'} and tokens==140
 assert m.last_usage['context_encoding']['version']==VERSION
 assert m.last_usage['context_encoding']['lossless_roundtrip_checked']
 assert m.ledger.summary()['uncertain_requests']==0


def test_overdeep_context_is_rejected_before_transmission():
 context={};root=context
 for _ in range(51):root['next']={};root=root['next']
 with pytest.raises(ValueError,match='CONTEXT_WIRE_DEPTH'):pack(context)


def test_provider_keeps_plain_context_by_default_pending_live_acceptance(tmp_path):
 from tests.unit.test_ai_provider_recovery import response
 m,_=model(tmp_path,[response()]);assert m.settings.context_wire is False
 bodies=[]
 def capture(request):bodies.append(json.loads(request.content));return response()
 m.transport=httpx.MockTransport(capture)
 context={'source_records':[{'summary':'repeated untrusted source '*100}]*8}
 asyncio.run(m.choose(context,60000))
 text=bodies[0]['contents'][0]['parts'][0]['text']
 assert json.loads(text.split('CONTEXT_JSON:\n',1)[1])==context
 assert m.last_usage['context_encoding']['version']=='PLAIN'
