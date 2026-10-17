"""Reproducible B03 runtime report; only writes/deletes its disposable graph."""
import importlib.metadata
import json
from uuid import uuid4

import httpx

from app.config import Settings
from app.graph.connection import connect
from app.graph.migration import MigrationRunner
from app.graph.models import QueryRequest
from app.graph.queries import GraphQueries
from app.graph.repository import GraphRepository
from tests.graph_fixtures import fixture_graph
from tests.schema_examples import NOW


def main():
    with connect(Settings(_env_file='.env')) as client:
        canonical=MigrationRunner(client,"civicly_knowledge").status()
        assert canonical['ready']
        probe=client.select_graph('civicly_b01_runtime').ro_query(
            'MATCH (n:B01Probe {id:$id}) RETURN properties(n)',params={'id':'B01-PERSISTENCE'},timeout=1000).result_set
        assert len(probe)==1
        assert client.select_graph('civicly_knowledge').ro_query('MATCH (n:CivicEntity) RETURN count(n)',timeout=1000).result_set==[[0]]
        report={'packages':{name:importlib.metadata.version(name) for name in ['falkordb','redis','pydantic','pytest']},
                'redis_version':client.connection.info('server')['redis_version'],
                'modules':client.connection.execute_command('MODULE','LIST'),
                'canonical_status':canonical,'canonical_domain_nodes':0,'b01_probe':probe,
                'browser_http_status':httpx.get('http://127.0.0.1:3000',follow_redirects=True,timeout=10).status_code}
        g=client.select_graph('civicly_b03_test_'+uuid4().hex)
        try:
            MigrationRunner(client,g.name).apply()
            repo=fixture_graph(GraphRepository(client,g.name)); q=GraphQueries(repo)
            plans={}; examples={}
            # Repository owns a separate Graph object; wrap that object's real reads.
            original=repo.graph.ro_query
            def capture(query,*args,**kwargs):
                if 'nodes(p) AS' in query:
                    plans[current]=str(repo.graph.explain(query,params=kwargs['params']))
                return original(query,*args,**kwargs)
            repo.graph.ro_query=capture
            for current,id in [('drainage_paths','D1'),('shared_infrastructure',''),('incident_history','LW'),
                ('maintenance_history','D1'),('cross_category_paths','W'),('hypothesis_evidence','INV'),
                ('ownership_dependencies','W'),('task_dependencies','T1')]:
                examples[current]=q.run(QueryRequest(template=current,id=id,as_of=NOW,max_hops=6,incident_ids=('I1','I2'))).model_dump(mode='json')
            report['examples']=examples; report['explain_plans']=plans
            # Minimal runtime observation: metadata projection on upstream variable path.
            raw=repo.graph.ro_query('MATCH (m:CivicSchemaMigration {id:$migration}) WITH m '
                'MATCH p=(a:InfrastructureAsset {id:$id})<-[:DRAINS_TO*1..4]-(b:InfrastructureAsset) '
                'RETURN coalesce(m.repo_revision,0),nodes(p)',params={'migration':'0001','id':'D3'},timeout=1000).result_set
            report['metadata_projection_spike']={'separate_revision':q._state(),'upstream_projected_revisions':[r[0] for r in raw]}
            assert MigrationRunner(client,g.name).apply()['ready']
            report['repository_revision_survives_migration_rerun']=q._state()
        finally:
            g.delete()
        print(json.dumps(report,indent=2,default=lambda x: x.decode() if isinstance(x,bytes) else str(x)))


if __name__=='__main__': main()
