"""Real repository benchmark. No bulk mutations, graph resets or volume deletion."""
import argparse
from copy import deepcopy
import json
import platform
import time
import tracemalloc

from app.config import Settings
from app.graph.connection import connect
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.graph.targets import new_test_graph_name
from app.ingestion.conversion import ROOT,manifest_for,validate_bundle
from app.ingestion.importer import Importer,ImportFailure
from app.ingestion.__main__ import write


def subset(bundle):
    by={n['properties']['id']:n for n in bundle['nodes']};edges=[];kinds=set()
    for e in bundle['relationships']:
        if e['type'] not in kinds:edges.append(e);kinds.add(e['type'])
    for e in bundle['relationships']:
        if len(edges)>=100:break
        if e not in edges:edges.append(e)
    ids={e[f] for e in edges for f in ('source_id','target_id')}
    ids.update(e['properties']['source_evidence_id'] for e in edges if 'source_evidence_id' in e['properties'])
    for kind in bundle['manifest']['node_types']:ids.add(next(n['properties']['id'] for n in bundle['nodes'] if n['label']==kind))
    policy=json.loads((ROOT/'contracts/graph_access.json').read_text())
    while True:
        extra={by[id]['properties'][f] for id in ids for f in policy['node_references'].get(by[id]['label'],{}) if f in by[id]['properties']}
        if extra<=ids:break
        ids |= extra
    result={**bundle,'nodes':[by[id] for id in sorted(ids)],'relationships':edges}
    result['manifest']=manifest_for(result['nodes'],edges);validate_bundle(result);return result


def quantiles(values):
    xs=sorted(values)
    return {p:xs[min(len(xs)-1,int((len(xs)-1)*q))] if xs else None for p,q in [('p50',.5),('p95',.95),('p99',.99)]}


def storage(client):
    p=client.connection.info('persistence');m=client.connection.info('memory')
    return {'aof_current_size':p.get('aof_current_size',0),'used_memory':m['used_memory']}


def trial(client,bundle,*,retain=False):
    name=new_test_graph_name(4);g=client.select_graph(name);migration_start=time.perf_counter();succeeded=False
    try:
        assert MigrationRunner(client,name).apply()['ready'];migration_seconds=time.perf_counter()-migration_start
        repo=GraphRepository(client,name);metrics={'query_calls':0,'ro_calls':0,'parameter_bytes':0,'largest_policy_scan':{}}
        for method in ('query','ro_query'):
            original=getattr(repo.graph,method)
            def wrapper(query,*args,_original=original,_method=method,**kwargs):
                metrics['query_calls' if _method=='query' else 'ro_calls']+=1
                metrics['parameter_bytes']+=len(json.dumps(kwargs.get('params',{})).encode())
                return _original(query,*args,**kwargs)
            setattr(repo.graph,method,wrapper)
        original_edges=repo._edges
        def scan(kind,**kw):
            rows=original_edges(kind,**kw);metrics['largest_policy_scan'][kind]=max(len(rows),metrics['largest_policy_scan'].get(kind,0));return rows
        repo._edges=scan
        checkpoints=[];total=len(bundle['nodes'])+len(bundle['relationships']);marks={1,max(1,total//4),total//2,total*3//4,total}
        def progress(kind,id,report):
            count=report['created']+report['matched']
            if count in marks:
                row=repo.graph.ro_query("MATCH (m:CivicSchemaMigration {id:$id}) RETURN m.repo_revision,m.repo_audit",params={'id':'0001'},timeout=1000).result_set[0]
                checkpoints.append({'records':count,'revision':row[0],'audit_bytes':len(row[1].encode())})
                print(json.dumps({'graph':name,'progress_records':count,'total':total,'audit_bytes':len(row[1].encode())}),flush=True)
        before=storage(client);tracemalloc.start()
        result=Importer(repo).run(bundle,after_record=progress)
        peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop();after=storage(client)
        result['latency_seconds']=quantiles(result.pop('latencies_seconds'))
        result.update(throughput_records_per_second=total/result['wall_seconds'],peak_python_bytes=peak,
                      migration_seconds=migration_seconds,metrics=metrics,checkpoints=checkpoints,
                      storage_before=before,storage_after=after,
                      storage_growth={k:after[k]-before[k] for k in before})
        repeats=[]
        for _ in range(2):
            repeat=Importer(repo).run(bundle);repeat['latency_seconds']=quantiles(repeat.pop('latencies_seconds'))
            assert repeat['created']==0 and repeat['matched']==total
            assert repeat['graph_revision']==result['graph_revision'] and repeat['audit_entries']==result['audit_entries']
            repeats.append(repeat)
        result['repeats']=repeats
        result['proposed_initial_target_met']=result['wall_seconds']<=300
        result['proposed_repeat_target_met']=all(x['wall_seconds']<=120 for x in repeats)
        result['proposed_memory_target_met']=peak<=256*1024*1024
        succeeded=True
        return result
    finally:
        if tracemalloc.is_tracing():tracemalloc.stop()
        if succeeded and not retain and name in client.list_graphs():g.delete()


def main():
    p=argparse.ArgumentParser();p.add_argument('--bundle',default='data/ingestion/city-v3.json');p.add_argument('--output',default='docs/evidence/B04-benchmarks.json');p.add_argument('--retain-last',action='store_true');args=p.parse_args()
    bundle=json.load(open(args.bundle));validate_bundle(bundle)
    report={'versions':{'python':platform.python_version(),'machine':platform.machine()},'bundle_content_hash':bundle['manifest']['content_hash'],'pilot':None,'full_trials':[]}
    with connect(Settings(_env_file='.env')) as client:
        try:report['pilot']=trial(client,subset(bundle))
        except ImportFailure as error:
            report['failure']=error.report;write(args.output,report);raise
        write(args.output,report)
        for i in range(3):
            print(f'Starting real full import trial {i+1}/3',flush=True)
            try:result=trial(client,bundle,retain=args.retain_last and i==2)
            except ImportFailure as error:
                report['failure']=error.report;write(args.output,report);raise
            report['full_trials'].append(result);write(args.output,report)
            print(json.dumps({'trial':i+1,'graph':result['graph'],'wall_seconds':result['wall_seconds'],'created':result['created'],'repeat_created':[x['created'] for x in result['repeats']]}),flush=True)
    totals=sorted(x['wall_seconds'] for x in report['full_trials']);report['median_initial_seconds']=totals[1];write(args.output,report)


if __name__=='__main__':main()
