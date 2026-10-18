"""Simulated plausible Gemini receipts with real graph/MCP/B09/LangGraph/Saver."""
import asyncio,json,subprocess,os
from datetime import datetime
from pathlib import Path
import pytest
from app.active import active_scope
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.agents.models import Budget
from app.agents.spending import Ledger,Pricing
from tests.b10or2_fixtures import prepare,initial,SimulatedHTTP,model,ASSET
from tests.b09_fixtures import Fixture,report
from tests.integration.test_agent_optimization import cleanup
pytestmark=pytest.mark.integration

@pytest.mark.parametrize('issue,topology,fault',[
 ('WATERLOGGING','VERIFIED',None),('ROAD_DAMAGE','VERIFIED',None),('ROAD_DAMAGE','CANDIDATE',None),
 ('WASTE_ACCUMULATION','VERIFIED',None),('WATERLOGGING','VERIFIED','503'),('WATERLOGGING','VERIFIED','invalid')])
def test_six_real_context_decisions_with_plausible_usage(db,tmp_path,issue,topology,fault):
 path=tmp_path/'profile.json';p,r,clock,receipt,inv,h=prepare(db,path,issue,topology)
 async def run():
  with active_scope(p):
   async with brokers(p,path) as tools:
    s=await initial(p,r,clock,receipt,inv,h,tools);http=SimulatedHTTP(clock,fault=fault);m=model(s,tmp_path,http)
    result=await InvestigationAgent(p,r,tools,m,saver(p),clock=clock).run(s,thread_id=s.thread_id)
    out=result['data']
    Path('/tmp/civicly-b10or2-debug-'+issue+'-'+str(fault)+'.json').write_text(json.dumps({'result':result,'receipts':http.receipts,'usage':m.last_usage},default=str,indent=2))
    assert result['__interrupt__'] and len(out['decisions'])==6 and len(out['hypotheses'])==2 and len(out['pending_inspections'])==1
    assert out['tokens']>60000 and out['tokens']<=400000 and out['pause_reason']=='MISSING_EVIDENCE'
    assert not any(v in out['errors'] for v in ['TOKEN_BUDGET','INVESTIGATION_SPENDING_CAP','PROJECT_SPENDING_CAP'])
    assert all(u['promptTokenCount']>10000 and u['totalTokenCount']>12000 for u in http.receipts)
    assert len(tools.catalog())==16 and len(out['executions'])==2
    assert all(len(c['catalog'])==16 and c['tool_schemas'] for c in http.contexts)
    assert len(set(c['state']['graph_revision'] for c in http.contexts))>=6
    classification=http.contexts[-1]['hypotheses'][0]['assessments'][0]['classification']
    assert classification['reviewed_contradiction_ids'] and classification['unreviewed_support_ids']
    assert len(http.contexts[-1]['hypotheses'][0]['history_references'])==9
    assert len(http.contexts[-1]['material_observations'])>=8
    if issue=='ROAD_DAMAGE':
     targets=r._read('MATCH (:Inspection {id:$id})-[:INSPECTS]->(n) RETURN n.id',{'id':out['pending_inspections'][0]})
     assert targets==[['P1' if topology=='VERIFIED' else 'R1']]
     # Drainage and utility relationships coexist; candidate utility is not verified.
     assert r.get_relationship('R2-FLOW').properties['association_status']=='VERIFIED'
     facts=http.contexts[-1]['facts'].values()
     assert any(v.get('kind')=='DRAINS_TO' for v in facts)
     assert any(v.get('kind')=='UNDERLIES' and v.get('properties',{}).get('association_status')==topology for v in facts)
     incident_records=[v for v in facts if v.get('properties',{}).get('id')!=receipt.incident_id and v.get('properties',{}).get('issue_type')=='ROAD_DAMAGE']
     assert incident_records
    if issue=='WASTE_ACCUMULATION':assert len(s.observations[0]['pickup_executions'])==3
    with m.ledger.db() as dbi:rows=[dict(row) for row in dbi.execute('SELECT * FROM requests ORDER BY created')]
    counts=[row for row in rows if row['id'].startswith('AI-COUNT-')];gens=[row for row in rows if not row['id'].startswith('AI-COUNT-')]
    assert all(row['charged']==0 and row['status']=='SETTLED' for row in counts)
    assert len(gens)==(7 if fault else 6)
    assert out['tokens']==Ledger(tmp_path/'ledger').thread_tokens(s.thread_id)
    assert m.ledger.summary()['project_accounted']==sum(Pricing().actual(u) for u in http.receipts)+sum(row['reserved'] for row in gens if row['charged'] is None)
    Path('/tmp/civicly-b10or2-multistep-'+issue+'-'+topology+'-'+str(fault)+'.json').write_text(json.dumps({'mode':'SIMULATED_GEMINI_HTTP_REAL_MCP_B09_SAVER','issue':issue,'topology':topology,'fault':fault,'result':result,'token_plans':http.plans,'simulated_usage':http.receipts,'count_tokens':http.counts,'ledger_requests':rows,'actual_external_gemini_requests':0},default=str,indent=2))
 try:asyncio.run(run())
 finally:cleanup(db,p)

@pytest.mark.parametrize('kind',['token','dollar'])
def test_realistic_pause_fresh_process_explicit_increase_same_checkpoint(db,tmp_path,kind):
 path=tmp_path/'profile.json';p,r,clock,receipt,inv,h=prepare(db,path,'WATERLOGGING')
 try:
  async def prep():
   with active_scope(p):
    async with brokers(p,path) as tools:return await initial(p,r,clock,receipt,inv,h,tools)
  s=asyncio.run(prep());s.budget=Budget(max_tokens=60000 if kind=='token' else 400000)
  src=tmp_path/'input.json';src.write_text(json.dumps({'state':s.model_dump(mode='json'),'clock':clock(),'kind':kind}))
  results=[]
  for phase in ['create','resume']:
   out=tmp_path/(phase+'.json')
   proc=subprocess.run([str(Path('backend/.venv/bin/python').absolute()),'-m','tests.b10or2_worker',str(path),phase,str(src),str(out)],env={**os.environ,'PYTHONPATH':'backend'},capture_output=True,timeout=120)
   assert proc.returncode==0,proc.stderr.decode()[-2500:]
   value=json.loads(out.read_text());results.append(value)
   if phase=='create':
    reason='TOKEN_BUDGET' if kind=='token' else 'INVESTIGATION_SPENDING_CAP'
    assert value['result']['data']['pause_reason']==reason and value['result']['__interrupt__'] and value['result']['data']['tokens']>0
    clock.value=datetime.fromisoformat(value['result']['data']['as_of'].replace('Z','+00:00'));clock.advance(20)
    with active_scope(p):report(Fixture(r,clock,{'WATERLOGGING':receipt},p.graph,{}),inv,'after-pause',codes=['DRAIN_CLEAR'],assets=['D1'])
    src.write_text(json.dumps({'state':s.model_dump(mode='json'),'clock':clock(),'kind':kind}))
  a,b=[v['result']['data'] for v in results]
  assert b['wakes']==1 and b['tokens']>a['tokens'] and set(a['decisions'])<=set(b['decisions'])
  assert set(a['executions'])<set(b['executions']) and 'SOURCE_CHANGED_REFRESH_REQUIRED' in b['errors']
  assert len(b['hypotheses'])==2 and len(b['pending_inspections'])==1 and len(set(b['decisions']))==len(b['decisions'])
  assert b['budget']['max_tokens']==400000
  before={row['id']:row for row in results[0]['requests']};after={row['id']:row for row in results[1]['requests']}
  assert all(after[k]==row for k,row in before.items())
  assert results[1]['summary']['case_accounted']>=results[0]['summary']['case_accounted']
  assert Ledger(tmp_path/'ledger').thread_tokens(s.thread_id)==b['tokens']
  Path('/tmp/civicly-b10or2-resume-'+kind+'.json').write_text(json.dumps({'mode':'SIMULATED_RECEIPTS_TWO_REAL_PROCESSES_REAL_MCP_SAVER','kind':kind,'outputs':results,'actual_external_gemini_requests':0},default=str,indent=2))
 finally:cleanup(db,p)
