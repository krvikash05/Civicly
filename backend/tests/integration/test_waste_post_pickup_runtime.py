"""One real B14-R waste flow: premature follow-up remains unresolved, later verifies."""
import asyncio,json
from pathlib import Path
import pytest
from app.active import active_scope
from tests.b14_fixtures import prepare,Run
from tests.integration.test_memory_graphrag import memory
pytestmark=pytest.mark.integration

def test_actual_waste_post_pickup_elapsed_window(db,tmp_path,memory):
 p,r,clock,path,inv,draft,planning,auth,tokens,ops=prepare(db,tmp_path,memory,'WASTE_ACCUMULATION')
 async def run():
  with active_scope(p):
   f=Run(r,clock,ops,tokens,'WASTE_ACCUMULATION');await f.begin(planning,draft);await f.complete()
   clock.advance();start=clock();clock.advance(24*3600)
   pickup={}
   def pickups(at):
    pickup['at']=at
    return [f.observation('SCHEDULED_PICKUPS',at,1.0,'pickups'),f.observation('ACTUAL_PICKUPS',at,1.0,'pickups')]
   _,record=await f.report('FOLLOWUP',pickups)
   clock.advance(3600)
   def window(at):return [f.observation('REACCUMULATION_WINDOW',at,24.0,'hours'),f.observation('WASTE_REACCUMULATION',at,0.0,'boolean')]
   _,early=await f.report('FOLLOWUP',window)
   def query(report):return {'operation':'evaluate','request_id':f.key(),'work_order_id':f.w['id'],'expected_hash':f.hash(),'evidence_ids':[record['entity_id'],report['entity_id']],'window_start':start,'window_end':clock()}
   premature=await f.call(query(early),'OP-ANALYST')
   assert premature['assessment_status']=='MONITORING' and not premature['case_closed'] and premature['policy_version']=='B14-2'
   assert r.get_node(f.b['plan_id']).properties['status']=='MONITORING'
   clock.advance(23*3600)
   _,late=await f.report('FOLLOWUP',window);q=query(late);verified=await f.call(q,'OP-ANALYST')
   assert verified['assessment_status']=='RESOLUTION_VERIFIED' and verified['case_closed']
   assert verified['policy_version']=='B14-2' and await f.call(q,'OP-ANALYST')==verified
   assert ops.store.get('outcome',premature['id'])==premature
   Path('docs/evidence/B14R-waste.json').write_text(json.dumps({'graph':p.graph,'pickup_at':pickup['at'],'premature':premature,'verified':verified,'early_report':early['entity_id'],'late_report':late['entity_id'],'pickup_report':record['entity_id'],'historical_premature_outcome_retained':True,'provider_calls':0},indent=2)+'\n')
 asyncio.run(run())
