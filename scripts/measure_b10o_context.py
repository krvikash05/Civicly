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
                h=propose(f,inv,issue,cause);rule=POLICIES[issue][cause]
                asset={'WATERLOGGING':'D1','ROAD_DAMAGE':'R1','WASTE_ACCUMULATION':'W1'}[issue]
                report(f,inv,'negative',codes=rule['falsifying'][:1],assets=[asset])
                report(f,inv,'unreviewed',codes=rule['confirming'][:1],assets=[asset],reviewed=False)
                for index in range(8):assess(f,h,ref='benchmark-assessment-'+str(index))
                async with brokers(p,path) as tools:
                    s=state(p,r,tools,clock,receipt,inv,issue);s.hypotheses=[h];s.iterations=13
                    agent=InvestigationAgent(p,r,tools,ScriptedModel([]),saver(p),clock=clock)
                    cached=0
                    for index in range(4):
                        ctx=Context(trace_id=s.thread_id,execution_id=uuid4().hex,investigation_id=inv,source_graph=p.graph,caller_role='READ_ONLY',invocation_origin='APPLICATION')
                        result=await tools.call('official::query_graph_readonly',{'template':'node','id':receipt.incident_id},ctx,'Operator benchmark, no model selected rationale',cutoff=s.as_of)
                        if tools.last_cache_receipt:cached+=1;result={**result,'host_read_cache':tools.last_cache_receipt}
                        s.observations.append(result)
                    s.tool_calls=4
                    history=agent.service.history(h,clock());original=[a.model_dump(mode='json') for a in history]
                    s.evidence={ref.id:ref.content_hash for a in history for ref in a.evidence_references}
                    old={'state':s.model_dump(mode='json'),'catalog':tools.catalog(),'policies':POLICIES[issue],'controlled_action_schemas':agent.action_schemas(),
                        'hypotheses':[{'id':h,'definition':r.get_node(h).properties,'assessments':original}],
                        'departments':r._read('MATCH (d:Department {municipality_id:$scope}) RETURN d.id LIMIT 10',{'scope':'demo-city'}),'budget_notice':'Missing/history/candidate/negative results never prove causation; B09 assessments authoritative.'}
                    new=agent.context(s)
                    assert len(history)==8 and len(new['catalog'])==16 and [v.model_dump(mode='json') for v in agent.service.history(h,clock())]==original
                    for a,b in zip(original[:-1],new['hypotheses'][0]['historical_material']):assert a['classification']==b['classification'] and a['paths']==b['paths']
                    sizes={key:len(json.dumps(value,separators=(',',':')).encode()) for key,value in [('before',old),('after',new)]}
                    assert sizes['after']<sizes['before']
                    return {'issue':issue,'mode':'REAL_B09_GRAPH_AND_MCP_NO_MODEL','assessment_versions':8,'observations':4,'actual_mcp_read_calls':4-cached,'cached_original_execution_references':cached,
                        'json_utf8_bytes':sizes,'reduction_fraction':1-sizes['after']/sizes['before'],
                        'simulated_context_allocation_nusd':{k:Pricing().estimate(v,4096) for k,v in sizes.items()},
                        'estimate_scope':'Context JSON plus framing/output allowance, excludes prompt/selection schema. Not tokenizer or billed savings',
                        'classification_and_paths_preserved':True,'full_history_unchanged':True,'all_actual_tool_names':[v['name'] for v in tools.catalog()],'actual_gemini_requests':0}
        finally:
            for name in [p.graph,p.checkpoints]:
                if name in db.list_graphs():db.select_graph(name).delete()
            db.connection.execute_command('ACL','DELUSER',p.read_user,p.checkpoint_user)


async def main():
    with connect(Settings(_env_file='.env')) as db:
        values=[await measure(db,*case) for case in [('WATERLOGGING','BLOCKAGE'),('ROAD_DAMAGE','SUBGRADE_FAILURE'),('WASTE_ACCUMULATION','MISSED_PICKUP')]]
    Path('docs/evidence/B10O-real-context-benchmark.json').write_text(json.dumps({'cases':values,'actual_live_model_quality':'NOT RUN'},indent=2)+'\n')
    print(json.dumps({'status':'PASS','cases':len(values),'bytes':{v['issue']:v['json_utf8_bytes'] for v in values},'actual_gemini_requests':0}))
if __name__=='__main__':asyncio.run(main())
