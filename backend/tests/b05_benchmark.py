"""Read-only repeated B05 measurement; existing review graphs must be present."""
import json
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.analysis.models import AnalysisRequest,CaseRequest
from app.graph.analysis.engine import GraphAnalysis
from app.graph.analysis.counterfactual import capture
from app.graph.analysis.evaluation import CITY_GRAPH,verify_city,ROOT
from app.graph.schema import utc_now
from app.ingestion.__main__ import write
from tests.b05_fixtures import AS_OF


def percentiles(values):
    xs=sorted(values)
    return {name:xs[min(len(xs)-1,int((len(xs)-1)*q))] for name,q in [('p50',.5),('p95',.95),('p99',.99)]}


def main():
    controlled=json.loads((ROOT/'docs/evidence/B05-controlled-results.json').read_text())
    bundle=json.loads((ROOT/'data/ingestion/city-v3.json').read_text())
    report={'repetitions':10,'timing_scope':'GraphAnalysis call incl revision/strict validation; excludes client/repository/migration construction and administrative manifest verification',
            'statistic':'Sorted order-statistic index floor((n-1)*q);10 samples are descriptive, not tail-latency assurance',
            'workloads':{},'city_task_dag':'Unavailable: no plans/tasks in accepted city; controlled fixture tested'}
    with connect(Settings(_env_file='.env')) as client:
        fixture=GraphRepository(client,controlled['source_graph']);city=GraphRepository(client,CITY_GRAPH)
        before={'fixture':capture(fixture).fingerprint,'city':verify_city(city,bundle)}
        workloads=[]
        for op,ids in [('reachability',('D1',)),('shared_downstream',()),('impacted_assets',('D2',)),('criticality',('D1','D4')),('components',('D1','NEARBY')),('dependencies',('PIPE','WASTE')),('task_dag',('T1',))]:
            kw={'incident_ids':('SEED','DEPENDENT-CASE')} if op=='shared_downstream' else {}
            workloads.append((f'controlled/{op}',fixture,AnalysisRequest(operation=op,ids=ids,as_of=AS_OF,**kw)))
        workloads.append(('controlled/cases',fixture,CaseRequest(as_of=AS_OF,seed_incident_id='SEED')))
        at=utc_now()
        for candidates in (False,True):
            mode='exploratory' if candidates else 'verified_only'
            for op,ids in [('reachability',('DRAIN-D12',)),('shared_downstream',()),('impacted_assets',('DRAIN-D12',)),('criticality',('INLET-I01','DRAIN-D12','DRAIN-D18')),('components',('DRAIN-D12',)),('dependencies',('WASTE-W03',))]:
                kw={'incident_ids':('INC-FLOOD-02','INC-ROAD-01','INC-WASTE-01')} if op=='shared_downstream' else {}
                workloads.append((f'city/{mode}/{op}',city,AnalysisRequest(operation=op,ids=ids,as_of=at,include_candidates=candidates,**kw)))
            for issue in ('WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION'):
                workloads.append((f'city/{mode}/cases/{issue}',city,CaseRequest(as_of=at,issue_type=issue,include_candidates=candidates)))
        for name,repo,request in workloads:
            engine=GraphAnalysis(repo);samples=[]
            for _ in range(10):
                result=engine.cases(request) if isinstance(request,CaseRequest) else engine.run(request)
                samples.append({**result.measurements,'rows':len(result.rows),'paths':len(result.paths),
                                'truncated':result.truncated,'graph_revision':result.graph_revision})
            report['workloads'][name]={'wall_seconds':percentiles([s['wall_seconds'] for s in samples]),
                'query_count_range':[min(s['queries'] for s in samples),max(s['queries'] for s in samples)],'samples':samples}
        after={'fixture':capture(fixture).fingerprint,'city':verify_city(city,bundle)}
        assert after==before
        report['source_before']=before;report['source_after']=after;report['sources_unchanged']=True
        report['clone_creation_seconds']=controlled['counterfactuals']['criticality']['clone_creation_wall_seconds']
        write('docs/evidence/B05-performance.json',report)
        print(json.dumps({'status':'PASS','workloads':len(workloads),'reads':len(workloads)*10,'sources_unchanged':True}))


if __name__=='__main__':main()
