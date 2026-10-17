"""B07 trusted configuration and actual runtime proof CLI."""
import argparse,asyncio,json
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from .runtime import configure,connections
from .broker import open_domain
from .storage import TraceStore
from .contracts import READ
from app.graph.schema import utc_now

async def proof():
    at=utc_now();results=[]
    args={
      'find_related_incidents':{'incident_id':'INC-FLOOD-02','max_results':5},
      'trace_infrastructure_dependencies':{'investigation_id':'B07-REVIEW','asset_id':'DRAIN-D12','direction':'DOWNSTREAM','max_hops':4},
      'get_maintenance_history':{'asset_id':'ROAD-R08','from_time':'2025-01-01T00:00:00Z','to_time':at},
      'retrieve_external_evidence':{'location_id':'LOC-004','evidence_type':'RAINFALL','from_time':'2026-01-01T00:00:00Z','to_time':at},
      'retrieve_case_memory':{'investigation_id':'B07-REVIEW','max_results':5},
      'get_organizational_procedures':{'department_id':'DEPT-DRAIN','action_type':'INSPECT'},
      'get_work_order_status':{'work_order_id':'NO-SUCH-ORDER'},
      'get_pickup_execution_history':{'collection_point_id':'WASTE-W03','days':180},
      'get_road_condition_history':{'road_segment_id':'ROAD-R08','days':730},
      'get_source_document_excerpt':{'document_id':'DOC-NOT-AVAILABLE'},
      'get_monitoring_status':{'problem_cluster_id':'CLUSTER-NOT-AVAILABLE'},
      'get_decision_evidence_path':{'decision_id':'NO-SUCH-DECISION'}}
    async with open_domain() as b:
        inventory=b.tools();actual_inventory=b.operator_inventory;initialization=b.operator_initialization
        for name,values in args.items():
            result=await b.call('civicly::'+name,{**values,'as_of':at})
            if result['status']=='ERROR':raise ValueError('Proof handler failed:'+name)
            results.append(result)
        typed={}
        for key,id in [('waste','WASTE-W03'),('utility','PIPE-P02')]:
            typed[key]=await b.call('civicly::trace_infrastructure_dependencies',{**args['trace_infrastructure_dependencies'],'asset_id':id,'network':'TYPED_DEPENDENCIES','include_candidates':True,'as_of':at})
            if typed[key]['status']=='ERROR' or not typed[key]['data']['edges']:raise ValueError('Typed dependency proof failed')
        exploration=await b.call('civicly::trace_infrastructure_dependencies',{**args['trace_infrastructure_dependencies'],'as_of':at,'include_candidates':True})
    with connections() as (_,writer,name):
        store=TraceStore(writer,name)
        traces=[store.get(r['execution_id']).model_dump(mode='json') for r in results+[exploration]+list(typed.values())]
    return {'status':'PASS','initialization':initialization,'actual_tools_list':actual_inventory,'inventory':inventory,'results':results,'exploratory':exploration,'persisted_server_traces':traces,
        'typed_dependencies':typed,'trace_graph':name,'verified_default_edges':len(results[1]['data']['edges']),'exploratory_edges':len(exploration['data']['edges']),
        'model_selected_rationale':None}

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['configure','proof']);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.command=='configure':
        with connect(Settings(_env_file='.env')) as admin:r=configure(admin)
    else:r=asyncio.run(proof())
    if a.output:a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'status':r['status'],'output':str(a.output) if a.output else None}))
if __name__=='__main__':main()
