import asyncio,json
from pathlib import Path
from uuid import uuid4
from app.active import load,active_scope,DEFAULT_PROFILE
from app.agents.mcp import brokers
from app.mcp.civicly.contracts import Context

async def main():
 p=load();fixture=json.loads(Path('docs/evidence/B10-live-fixture.json').read_text());case=fixture['cases']['WATERLOGGING']
 with active_scope(p):
  async with brokers(p,DEFAULT_PROFILE) as tools:
   result={'mode':'ACTUAL_OPERATOR_DISCOVERY_AND_READBACK_NOT_MODEL_SELECTION','graph':p.graph,
     'official_inventory':tools.official.operator_inventory,'domain_initialization':tools.domain.operator_initialization,
     'domain_inventory':tools.domain.operator_inventory,'validated_model_catalog':tools.catalog(),'inventory_hash':tools.inventory_hash,'calls':[]}
   for id in [case['receipt']['incident_id'],case['receipt']['cluster_id'],case['investigation']]:
    ctx=Context(trace_id=uuid4().hex,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=case['investigation'])
    value=await tools.call('official::query_graph_readonly',{'template':'node','id':id},ctx,None)
    result['calls'].append({'name':'official::query_graph_readonly','arguments':{'template':'node','id':id},'result':value,'persisted_trace':tools.store.get(ctx.execution_id).model_dump(mode='json')})
   ctx=Context(trace_id=uuid4().hex,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=case['investigation'])
   args={'incident_id':case['receipt']['incident_id'],'max_results':10,'as_of':'2026-10-18T12:00:00Z'}
   value=await tools.call('civicly::find_related_incidents',args,ctx,None)
   result['calls'].append({'name':'civicly::find_related_incidents','arguments':args,'result':value,'persisted_trace':tools.store.get(ctx.execution_id).model_dump(mode='json')})
   result['official_transport']=tools.traces
   assert len({call['result']['graph_revision'] for call in result['calls']})==1
   Path('docs/evidence/B10-discovery-and-readback.json').write_text(json.dumps(result,indent=2)+'\n')
   print(json.dumps({'status':'PASS','official_discovered':len(result['official_inventory']),'domain_discovered':len(result['domain_inventory']),'approved_model_tools':len(result['validated_model_catalog']),'actual_calls':len(result['calls'])}))
asyncio.run(main())
