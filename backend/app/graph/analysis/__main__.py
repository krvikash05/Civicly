"""B05 review/evaluation CLI, not the later product/MCP command surface."""
import argparse
import json
import platform
from pathlib import Path
from redis.exceptions import RedisError
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository,RepositoryError
from app.graph.migration import MigrationRunner
from app.graph.targets import new_test_graph_name
from app.ingestion.__main__ import write
from .engine import GraphAnalysis
from .models import AnalysisRequest,CaseRequest
from .counterfactual import Counterfactual,capture,CounterfactualFailure
from .evaluation import evaluate_city,CITY_GRAPH


def controlled(client,retain):
    # Test-only explicit synthetic source factory; never city or hidden oracle data.
    from tests.b05_fixtures import network,AS_OF,NOW,edge
    name=new_test_graph_name(5);experiment=None;success=False
    try:
        MigrationRunner(client,name).apply();repo=network(GraphRepository(client,name));engine=GraphAnalysis(repo)
        report={'source_graph':name,'source_before':capture(repo).fingerprint,'algorithms':{},'native_procedures':repo._read('CALL dbms.procedures() YIELD name,mode RETURN name,mode LIMIT 100')}
        for op,ids in [('reachability',('D1',)),('shared_downstream',()),('impacted_assets',('D2',)),('criticality',('D1','D4')),('components',('D1','NEARBY')),('dependencies',('PIPE','WASTE')),('task_dag',('T1',))]:
            args={'incident_ids':('SEED','DEPENDENT-CASE')} if op=='shared_downstream' else {}
            report['algorithms'][op]=engine.run(AnalysisRequest(operation=op,ids=ids,as_of=AS_OF,**args)).model_dump(mode='json')
        report['cases']=engine.cases(CaseRequest(as_of=AS_OF,seed_incident_id='SEED')).model_dump(mode='json')
        bfs=repo.graph.ro_query('MATCH (a:DrainSegment {id:$id}) CALL algo.BFS(a,$depth,$relationship) YIELD nodes,edges RETURN nodes,edges LIMIT 1',params={'id':'D1','depth':6,'relationship':'DRAINS_TO'},timeout=1000).result_set
        report['native_bfs_unfiltered_ids']=sorted({n.properties['id'] for row in bfs for n in row[0]})
        experiment=Counterfactual(repo);experiment.remove('CUT')
        requests={'reachability':AnalysisRequest(operation='reachability',ids=('D1',),as_of=AS_OF),
                  'criticality':AnalysisRequest(operation='criticality',ids=('D1','D4'),as_of=AS_OF),
                  'impacted_assets':AnalysisRequest(operation='impacted_assets',ids=('D2',),as_of=AS_OF),
                  'shared_downstream':AnalysisRequest(operation='shared_downstream',incident_ids=('SEED','DEPENDENT-CASE'),as_of=AS_OF)}
        report['counterfactuals']={key:experiment.compare(req).model_dump(mode='json') for key,req in requests.items()}
        experiment.add_candidate('D2','D3',{**edge('CANDIDATE'),'association_status':'CANDIDATE','source_evidence_id':'EV-CANDIDATE','valid_from':NOW})
        report['candidate_verified_only']=experiment.compare(requests['criticality']).model_dump(mode='json')
        report['candidate_exploratory']=experiment.compare(requests['criticality'].model_copy(update={'include_candidates':True})).model_dump(mode='json')
        report['source_after']=capture(repo).fingerprint;assert report['source_after']==report['source_before']
        report['clone_graph']=experiment.clone_name;success=True;return report
    finally:
        if success and not retain:
            if experiment:experiment.cleanup()
            if name in client.list_graphs():client.select_graph(name).delete()


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['controlled','city']);p.add_argument('--graph',default=CITY_GRAPH)
    p.add_argument('--output',required=True);p.add_argument('--retain',action='store_true');args=p.parse_args()
    try:
        with connect(Settings(_env_file='.env')) as client:
            if args.command=='controlled':result=controlled(client,args.retain)
            else:
                result,dependencies=evaluate_city(GraphRepository(client,args.graph))
                write(Path(args.output).with_name('B05-scenario-dependencies.json'),dependencies)
            result['versions']={'python':platform.python_version(),'redis_server':client.connection.info('server')['redis_version'],
                'modules':client.connection.module_list(),'client':__import__('importlib.metadata',fromlist=['version']).version('falkordb')}
            write(args.output,result);print(json.dumps({'status':'PASS','output':args.output,'source_graph':result.get('source_graph',args.graph)}))
    except (RedisError,RepositoryError,ValueError) as error:
        failure={'status':'FAILED','error_code':getattr(error,'code','ANALYSIS_OR_DATABASE_FAILURE'),'error_type':type(error).__name__}
        if isinstance(error,CounterfactualFailure):failure['retained_clone']=error.graph
        write(args.output,failure);print(json.dumps(failure));raise SystemExit(1) from None


if __name__=='__main__':main()
