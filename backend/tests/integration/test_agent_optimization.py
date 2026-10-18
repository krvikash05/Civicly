"""Real FalkorDB/MCP/Saver, explicit mock HTTP: zero live AI reasoning claims."""
import asyncio,json
from pathlib import Path
from uuid import uuid4
import httpx,pytest
from app.active import active_scope
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.agents.provider import Gemini,ProviderSettings
from app.agents.policy import Permit
from app.agents.spending import Ledger
from app.graph.queries import GraphQueries
from app.mcp.civicly.contracts import Context
from tests.b10_fixtures import create,state,choose
from tests.schema_examples import common
pytestmark=pytest.mark.integration


def cleanup(db,p):
    for name in [p.graph,p.checkpoints]:
        if name in db.list_graphs():db.select_graph(name).delete()
    db.connection.execute_command('ACL','DELUSER',p.read_user,p.checkpoint_user)


def test_real_mcp_read_cache_scope_time_and_revision_invalidation(db,tmp_path):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path)
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                tools.bind_read_cache(GraphQueries(r)._state)
                ctx=Context(trace_id='B10O-CACHE',execution_id=uuid4().hex,investigation_id=inv,source_graph=p.graph,caller_role='READ_ONLY',invocation_origin='APPLICATION')
                name='civicly::trace_infrastructure_dependencies'
                args={'investigation_id':inv,'asset_id':'D1','network':'TYPED_DEPENDENCIES','direction':'DOWNSTREAM','max_hops':2,'as_of':clock(),'include_candidates':False}
                original=tools._actual_call;calls=[]
                async def counted(*a,**k):calls.append(a[0]);return await original(*a,**k)
                tools._actual_call=counted
                first=await tools.call(name,args,ctx,'Authored test read',cutoff=clock());count=len(calls)
                repeat=await tools.call(name,args,ctx.model_copy(update={'execution_id':uuid4().hex}),'Authored identical read',cutoff=clock())
                assert first==repeat and len(calls)==count
                assert tools.last_cache_receipt['original_execution_id']==first['execution_id']
                assert tools.last_cache_receipt['bounded_negative_is_not_absence'] and repeat['search_limited']
                await tools.call(name,{**args,'max_hops':3},ctx.model_copy(update={'execution_id':uuid4().hex}),'Changed arguments',cutoff=clock());assert len(calls)==count+1
                await tools.call(name,args,ctx.model_copy(update={'execution_id':uuid4().hex,'caller_role':'OPERATOR_REVIEW'}),'Changed permission',cutoff=clock());assert len(calls)==count+2
                clock.advance();await tools.call(name,{**args,'as_of':clock()},ctx.model_copy(update={'execution_id':uuid4().hex}),'Changed cutoff',cutoff=clock());assert len(calls)==count+3
                r.create_node('Evidence',{**common('EV-B10O-CHANGED'),'recorded_at':clock(),'source_kind':'SYNTHETIC','evidence_type':'CONTEXT','summary':'Changed source invalidates all cached reads','reliability':'UNVERIFIED'})
                await tools.call(name,args,ctx.model_copy(update={'execution_id':uuid4().hex}),'Changed revision',cutoff=args['as_of']);assert len(calls)==count+4 and tools.last_cache_receipt is None
                Path('/tmp/civicly-b10o-cache-proof.json').write_text(json.dumps({'mode':'REAL_MCP','actual_calls':len(calls),'identical_read_reused_original_execution':True,'args_permission_time_revision_invalidated':True,'bounded_negative_preserved':True},indent=2))
    try:asyncio.run(run())
    finally:cleanup(db,p)


def test_budget_pause_real_checkpoint_and_fresh_ledger_resume(db,tmp_path):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path)
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                initial=state(p,r,tools,clock,receipt,inv);ledger_path=tmp_path/'spend.sqlite3';ledger=Ledger(ledger_path);seen=[]
                def handler(req):
                    seen.append(1);return httpx.Response(200,json={'modelVersion':'gemini-3.8-flash','usageMetadata':{'promptTokenCount':100,'candidatesTokenCount':20,'totalTokenCount':120},'candidates':[{'content':{'parts':[{'text':json.dumps(choose())}]}}]})
                permit=Permit(inv,initial.thread_id,'B10-O-TEST','.001','MOCK_HTTP')
                model=Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key'),permit=permit,ledger=ledger,transport=httpx.MockTransport(handler))
                first=await InvestigationAgent(p,r,tools,model,saver(p),clock=clock).run(initial,thread_id=initial.thread_id)
                assert not seen and first['__interrupt__'] and 'INVESTIGATION_SPENDING_CAP' in first['data']['errors']
                assert saver(p).get_tuple({'configurable':{'thread_id':initial.thread_id}}) is not None
                next_permit=Permit(inv,initial.thread_id,'B10-O-TEST','.15','MOCK_HTTP')
                recovered=Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key'),permit=next_permit,ledger=Ledger(ledger_path),transport=httpx.MockTransport(handler))
                clock.advance();result=await InvestigationAgent(p,r,tools,recovered,saver(p),clock=clock).run(thread_id=initial.thread_id,resume=True)
                assert result['__interrupt__'] and len(seen)==1 and result['data']['wakes']==1
                assert recovered.ledger.summary(inv)['case_accounted']==150000
                Path('/tmp/civicly-b10o-budget-checkpoint-proof.json').write_text(json.dumps({'mode':'MOCK_HTTP_REAL_MCP_SAVER','blocked_before_request':True,'fresh_ledger_same_investigation_resumed':True,'mock_requests':len(seen),'simulated_nusd':150000,'actual_gemini_requests':0},indent=2))
    try:asyncio.run(run())
    finally:cleanup(db,p)

@pytest.mark.parametrize('issue,cause',[('WATERLOGGING','BLOCKAGE'),('ROAD_DAMAGE','SUBGRADE_FAILURE'),('WASTE_ACCUMULATION','MISSED_PICKUP')])
def test_compact_real_b09_history_preserves_reviewed_contradiction_and_unreviewed_support(db,tmp_path,issue,cause):
    from tests.b09_fixtures import Fixture,propose,report,assess
    from app.services.evidence.policies import POLICIES
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path,issue)
    async def run():
        with active_scope(p):
            f=Fixture(r,clock,{issue:receipt},p.graph,{})
            hypothesis=propose(f,inv,issue,cause)
            rule=POLICIES[issue][cause];asset={'WATERLOGGING':'D1','ROAD_DAMAGE':'R1','WASTE_ACCUMULATION':'W1'}[issue]
            report(f,inv,'negative',codes=rule['falsifying'][:1],assets=[asset])
            first=assess(f,hypothesis,ref='old').assessment
            report(f,inv,'unreviewed',codes=rule['confirming'][:1],assets=[asset],reviewed=False)
            latest=assess(f,hypothesis,ref='latest').assessment
            assert latest.classification.reviewed_contradiction_ids and latest.classification.unreviewed_support_ids
            async with brokers(p,path) as tools:
                s=state(p,r,tools,clock,receipt,inv,issue);s.hypotheses=[hypothesis]
                from tests.b10_fixtures import ScriptedModel
                agent=InvestigationAgent(p,r,tools,ScriptedModel([]),saver(p),clock=clock);compact=agent.context(s)
                assert len(compact['catalog'])==16
                for actual,projected in zip(tools.catalog(),compact['catalog']):
                    assert actual['name']==projected['name'] and actual['input_schema']==compact['tool_schemas'][projected['input_schema_ref']]
                old_context={'state':s.model_dump(mode='json'),'catalog':tools.catalog(),'policies':POLICIES[issue],'controlled_action_schemas':agent.action_schemas(),
                    'hypotheses':[{'id':hypothesis,'definition':r.get_node(hypothesis).properties,'assessments':[v.model_dump(mode='json') for v in agent.service.history(hypothesis,clock())]}],
                    'departments':r._read('MATCH (d:Department {municipality_id:$scope}) RETURN d.id LIMIT 10',{'scope':'demo-city'}),'budget_notice':'Missing/history/candidate/negative results never prove causation; B09 assessments authoritative.'}
                sizes={'before':len(json.dumps(old_context,separators=(',',':')).encode()),'after':len(json.dumps(compact,separators=(',',':')).encode())}
                assert compact['hypotheses'][0]['assessments'][0]['classification']==latest.classification.model_dump(mode='json')
                prior=compact['hypotheses'][0]['historical_material'][0]
                assert prior['classification']==first.classification.model_dump(mode='json')
                for ref in prior['evidence_references']:
                    if ref['report'] is not None:assert compact['facts'][ref['report']['fact_ref']]==next(v.model_dump(mode='json')['report'] for v in first.evidence_references if v.id==ref['id'])
                assert [a.id for a in agent.service.history(hypothesis,clock())]==[first.id,latest.id]
                Path('/tmp/civicly-b10o-authority-'+issue+'.json').write_text(json.dumps({'mode':'REAL_B09_MCP_CATALOG_NO_LIVE_MODEL','issue':issue,'latest_classification':latest.classification.model_dump(mode='json'),'historical_classification':prior['classification'],'full_history_unchanged':True,'catalog_count':16,'actual_tool_names':[t['name'] for t in tools.catalog()],'real_graph_context_json_bytes':sizes},indent=2))
    try:asyncio.run(run())
    finally:cleanup(db,p)
