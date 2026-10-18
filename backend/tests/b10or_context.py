"""Real registry/B09 history/MCP catalog context benchmark, no model/provider calls."""
import asyncio,json,tempfile
from pathlib import Path
from uuid import uuid4
from app.active import active_scope
from app.config import Settings
from app.graph.connection import connect
from app.graph.queries import GraphQueries
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.agents.spending import Pricing
from app.agents.provider import Gemini,ProviderSettings
from app.agents.policy import Permit
from app.agents.spending import Ledger
from app.agents.tokens import plan
from tests.unit.test_agent_token_accounting import body,response
from tests.b08_fixtures import populate_history,payload
from tests.schema_examples import edge,NOW
from app.services.complaints import ComplaintService
import httpx,pytest
from app.mcp.civicly.contracts import Context
from app.services.evidence.policies import POLICIES
from tests.b10_fixtures import create,state,ScriptedModel
from tests.b09_fixtures import Fixture,propose,report,assess


async def measure(db,issue,cause):
    with tempfile.TemporaryDirectory(prefix='civicly-b10o-benchmark-') as directory:
        path=Path(directory)/'profile.json';p,r,clock,receipt,inv=create(db,path,issue)
        try:
            with active_scope(p):
                f=Fixture(r,clock,{issue:receipt},p.graph,{})
                populate_history(r)
                h=propose(f,inv,issue,cause);rule=POLICIES[issue][cause]
                other={'WATERLOGGING':'CAPACITY_DEFICIT','ROAD_DAMAGE':'UTILITY_LEAK','WASTE_ACCUMULATION':'CAPACITY_SHORTFALL'}[issue]
                changes={}
                if issue=='ROAD_DAMAGE':
                    r.create_relationship('UNDERLIES','P1','R1',{**edge('B10OR-DEPENDENCY'),'valid_from':NOW,'association_status':'VERIFIED','source_evidence_id':'EV'})
                    changes={'asset_ids':['P1'],'topology':{'source_id':'P1','target_id':'R1','operation':'dependencies','max_hops':3}}
                    older=ComplaintService(r,clock=clock).intake(payload(issue,ref='older-episode',occurred_at='2026-09-01T04:00:00Z',reported_at='2026-09-01T05:00:00Z'))
                    assert older.incident_id!=receipt.incident_id
                h2=propose(f,inv,issue,other,ref='alternative',**changes)
                asset={'WATERLOGGING':'D1','ROAD_DAMAGE':'R1','WASTE_ACCUMULATION':'W1'}[issue]
                report(f,inv,'negative',codes=rule['falsifying'][:1],assets=[asset])
                report(f,inv,'unreviewed',codes=rule['confirming'][:1],assets=[asset],reviewed=False)
                for index in range(8):assess(f,h,ref='benchmark-assessment-'+str(index))
                async with brokers(p,path) as tools:
                    s=state(p,r,tools,clock,receipt,inv,issue);s.hypotheses=[h,h2];s.iterations=13
                    agent=InvestigationAgent(p,r,tools,ScriptedModel([]),saver(p),clock=clock)
                    cached=0
                    for index in range(4):
                        ctx=Context(trace_id=s.thread_id,execution_id=uuid4().hex,investigation_id=inv,source_graph=p.graph,caller_role='READ_ONLY',invocation_origin='APPLICATION')
                        name='civicly::get_pickup_execution_history' if issue=='WASTE_ACCUMULATION' else 'official::query_graph_readonly'
                        args={'collection_point_id':'W1','days':30,'as_of':clock()} if issue=='WASTE_ACCUMULATION' else {'template':'node','id':receipt.incident_id}
                        if issue=='ROAD_DAMAGE':
                            if index==1:
                                name='civicly::trace_infrastructure_dependencies';args={'investigation_id':inv,'asset_id':'P1','network':'TYPED_DEPENDENCIES','direction':'DOWNSTREAM','max_hops':3,'as_of':clock(),'include_candidates':False}
                            elif index==2:args={'template':'node','id':older.incident_id}
                        result=await tools.call(name,args,ctx,'Operator benchmark, no model selected rationale',cutoff=s.as_of)
                        if tools.last_cache_receipt:cached+=1;result={**result,'host_read_cache':tools.last_cache_receipt}
                        s.observations.append(result)
                    s.tool_calls=4
                    history=agent.service.history(h,clock());original=[a.model_dump(mode='json') for a in history]
                    s.evidence={ref.id:ref.content_hash for a in history for ref in a.evidence_references}
                    old={'state':s.model_dump(mode='json'),'catalog':tools.catalog(),'policies':POLICIES[issue],'controlled_action_schemas':agent.action_schemas(),
                        'hypotheses':[{'id':h,'definition':r.get_node(h).properties,'assessments':original},{'id':h2,'definition':r.get_node(h2).properties,'assessments':[]}],
                        'departments':r._read('MATCH (d:Department {municipality_id:$scope}) RETURN d.id LIMIT 10',{'scope':'demo-city'}),'budget_notice':'Missing/history/candidate/negative results never prove causation; B09 assessments authoritative.'}
                    new=agent.context(s)
                    assert len(history)==8 and len(new['catalog'])==16 and [v.model_dump(mode='json') for v in agent.service.history(h,clock())]==original
                    for a,b in zip(original[:-1],new['hypotheses'][0]['historical_material']):assert a['classification']==b['classification'] and a['paths']==b['paths']
                    sizes={key:len(json.dumps(value,separators=(',',':')).encode()) for key,value in [('before',old),('after',new)]}
                    assert sizes['after']<sizes['before']
                    before_plan,after_plan=plan(body(old)),plan(body(new))
                    assert before_plan['serialized_utf8_bytes']+4096>60000
                    assert after_plan['total_allowance_tokens']<60000
                    assert new['hypotheses'][0]['assessments'][0]['classification']['reviewed_contradiction_ids']
                    assert new['hypotheses'][0]['assessments'][0]['classification']['unreviewed_support_ids']
                    if issue=='WASTE_ACCUMULATION':assert len(s.observations[0]['pickup_executions'])==3
                    boundaries=[]
                    for delta in [-1,0,1]:
                        seen=[]
                        m=Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key'),permit=Permit.mocked(),ledger=Ledger(Path(directory)/('budget'+str(delta))),transport=httpx.MockTransport(lambda req:(seen.append(1),response())[1]))
                        if delta<0:
                            with pytest.raises(__import__('app.agents.provider',fromlist=['ProviderError']).ProviderError,match='TOKEN_BUDGET'):await m.choose(new,after_plan['total_allowance_tokens']+delta)
                            assert not seen
                        else:assert (await m.choose(new,after_plan['total_allowance_tokens']+delta))[1]==130
                        boundaries.append({'delta':delta,'generation_requests':len(seen),'simulated_consumed_tokens':130 if seen else 0})
                    return {'token_plans':{'before':before_plan,'after':after_plan},'boundary_cases':boundaries,'episode_ids':[receipt.incident_id,older.incident_id] if issue=='ROAD_DAMAGE' else [receipt.incident_id],'competing_hypotheses':[cause,other],'issue':issue,'mode':'REAL_B09_GRAPH_AND_MCP_NO_MODEL','assessment_versions':8,'observations':4,'actual_mcp_read_calls':4-cached,'cached_original_execution_references':cached,
                        'json_utf8_bytes':sizes,'reduction_fraction':1-sizes['after']/sizes['before'],
                        'simulated_context_allocation_nusd':{k:Pricing().estimate(v,4096) for k,v in sizes.items()},
                        'estimate_scope':'Context JSON plus framing/output allowance, excludes prompt/selection schema. Not tokenizer or billed savings',
                        'classification_and_paths_preserved':True,'full_history_unchanged':True,'all_actual_tool_names':[v['name'] for v in tools.catalog()],'actual_gemini_requests':0}
        finally:
            for name in [p.graph,p.checkpoints]:
                if name in db.list_graphs():db.select_graph(name).delete()
            db.connection.execute_command('ACL','DELUSER',p.read_user,p.checkpoint_user)
