"""Packed provider requests with real MCP/Saver; Gemini HTTP is explicitly mocked."""
import json
import pytest
from app.agents.provider import Gemini
from app.agents.wire_context import unpack,VERSION
from tests.b10_fixtures import choose
from tests.integration.test_agent_read_contract_runtime import test_invalid_selection_corrected_before_real_mcp_dispatch as journey
pytestmark=pytest.mark.integration


def test_real_mcp_dispatch_and_saver_with_lossless_packed_context(db,tmp_path,monkeypatch):
 original=Gemini.choose;seen=[]
 async def choose_checked(self,context,remaining):
  self.settings=self.settings.model_copy(update={'context_wire':True})
  original_transport=self.transport
  import httpx
  async def capture(request):
   body=json.loads(request.content)
   text=body['contents'][0]['parts'][0]['text']
   payload=text.split('CONTEXT_JSON:\n',1)[1].split('\nPrevious output',1)[0]
   wire=json.loads(payload);assert wire['wire_version']==VERSION
   # JSON transport maps tuple-valued policy constants to arrays; compare canonical JSON.
   assert json.dumps(unpack(wire),sort_keys=True)==json.dumps(context,sort_keys=True)
   seen.append(wire['wire_version'])
   return await original_transport.handle_async_request(request)
  self.transport=httpx.MockTransport(capture)
  try:
   result=await original(self,context,remaining)
   assert self.last_usage['context_encoding']['lossless_roundtrip_checked']
   return result
  finally:self.transport=original_transport
 monkeypatch.setattr(Gemini,'choose',choose_checked)
 malformed=choose('READ',{'id':'R1','sample_size':20},'official::query_graph_readonly')
 journey(db,tmp_path,'ROAD_DAMAGE',malformed)
 assert len(seen)==3
