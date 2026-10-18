"""Real MCP/Saver, mocked provider correction. Never live Gemini acceptance."""
import asyncio,json
import httpx,pytest
from app.active import active_scope
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.agents.provider import Gemini,ProviderSettings
from app.agents.policy import Permit
from app.agents.spending import Ledger
from tests.b10_fixtures import create,state,choose

pytestmark=pytest.mark.integration

@pytest.mark.parametrize('issue,malformed',[
 ('ROAD_DAMAGE',choose('READ',{'id':'R1','sample_size':20},'official::query_graph_readonly')),
 ('WASTE_ACCUMULATION',choose('READ',{'location_id':'W1','evidence_type':'RAINFALL','from_time':'2026-10-18T10:00:00Z','to_time':'2026-10-18T11:00:00Z'},'civicly::retrieve_external_evidence'))])
def test_invalid_selection_corrected_before_real_mcp_dispatch(db,tmp_path,issue,malformed):
 path=tmp_path/'profile.json';p,repo,clock,receipt,inv=create(db,path,issue)
 calls=[];responses=[malformed,choose('READ',{'template':'node','id':receipt.incident_id},'official::query_graph_readonly'),choose()]
 def respond(request):
  calls.append(json.loads(request.content));value=responses.pop(0)
  return httpx.Response(200,json={'usageMetadata':{'promptTokenCount':50,'candidatesTokenCount':20,'totalTokenCount':70},'candidates':[{'content':{'parts':[{'text':json.dumps(value)}]}}]})
 async def run():
  with active_scope(p):
   async with brokers(p,path) as tools:
    s=state(p,repo,tools,clock,receipt,inv,issue)
    model=Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key',CIVICLY_LLM_TRANSIENT_RETRIES=0),permit=Permit.mocked(inv,s.thread_id),transport=httpx.MockTransport(respond),ledger=Ledger(tmp_path/'ledger'))
    before=repo._read('MATCH (n:Inspection) RETURN count(n)')[0][0]
    final=await InvestigationAgent(p,repo,tools,model,saver(p),clock=clock).run(s,thread_id=s.thread_id)
    saved=final['data']
    assert saved['tool_calls']==1 and len(saved['executions'])==1
    assert not saved['errors'] and saved['pause_reason']=='MISSING_EVIDENCE'
    assert saved['tokens']==210 and len(calls)==3
    assert repo._read('MATCH (n:Inspection) RETURN count(n)')[0][0]==before
    # Invalid model input was never selected/persisted as a dispatched operation.
    decisions=repo._read('MATCH (n:AgentDecision) RETURN n.rationale LIMIT 10')
    chosen=[json.loads(row[0])['selection'] for row in decisions]
    assert all(v!=malformed for v in chosen)
    assert len(chosen)==2
    assert saver(p).get_tuple({'configurable':{'thread_id':s.thread_id}})
 try:asyncio.run(run())
 finally:
  for name in [p.graph,p.checkpoints]:
   if name in db.list_graphs():db.select_graph(name).delete()
  db.connection.execute_command('ACL','DELUSER',p.read_user,p.checkpoint_user)
