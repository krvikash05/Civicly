import json
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor

import pytest
from redis.exceptions import ConnectionError

from app.graph.connection import connect
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.graph.targets import new_test_graph_name
from app.graph.queries import GraphQueries
from app.graph.models import QueryRequest
from app.ingestion.conversion import convert,manifest_for,ROOT
from app.ingestion.importer import Importer,ImportFailure
from tests.ingestion_examples import source,example,COMPILED
from tests.graph_fixtures import fixture_graph

pytestmark=pytest.mark.integration


@pytest.fixture
def repo(db):
    name=new_test_graph_name(4)
    try:
        assert MigrationRunner(db,name).apply()['ready']
        yield GraphRepository(db,name)
    finally:
        if name in db.list_graphs():db.select_graph(name).delete()


def tiny():
    nodes=[example('DrainSegment','A'),example('DrainSegment','B')]
    edges=[{'type':'DRAINS_TO','source_id':'A','target_id':'B','properties':{}}]
    return source(nodes,edges)


def test_real_counts_hashes_and_noop_repeats(repo):
    bundle,_=convert(tiny(),COMPILED);importer=Importer(repo)
    first=importer.run(bundle);again=importer.run(bundle);third=importer.run(bundle)
    total=len(bundle['nodes'])+len(bundle['relationships'])
    assert first['created']==total and first['graph_revision']==total
    assert again['created']==third['created']==0 and again['matched']==total
    assert first['verified_content_hash']==again['verified_content_hash']==bundle['manifest']['content_hash']
    assert first['graph_revision']==again['graph_revision']==third['graph_revision']
    assert first['audit_entries']==again['audit_entries']==third['audit_entries']


def test_changed_record_conflicts_and_invalid_source_cannot_write(repo):
    raw=tiny();bundle,_=convert(raw,COMPILED);first=Importer(repo).run(bundle)
    raw['nodes'][0]['properties']['name']='Changed source'
    changed,_=convert(raw,COMPILED)
    with pytest.raises(ImportFailure,match='SOURCE_CONFLICT'):Importer(repo).run(changed)
    tampered=deepcopy(bundle);tampered['nodes'][0]['properties']['unknown']='bad'
    with pytest.raises(ImportFailure,match='INVALID_SOURCE'):Importer(repo).run(tampered)
    again=Importer(repo).run(bundle)
    assert first['graph_revision']==again['graph_revision'] and repo.get_node('A').properties['name']!='Changed source'


def test_interrupted_prefix_resumes_without_duplicate_mutations(repo):
    bundle,_=convert(tiny(),COMPILED)
    def interrupt(kind,id,report):
        if report['created']==3:raise RuntimeError('Injected process interruption after actual writes')
    with pytest.raises(RuntimeError,match='interruption'):Importer(repo).run(bundle,after_record=interrupt)
    resumed=Importer(repo).run(bundle)
    assert resumed['matched']==3 and resumed['created']==len(bundle['nodes'])+len(bundle['relationships'])-3
    assert resumed['graph_revision']==len(bundle['nodes'])+len(bundle['relationships'])


@pytest.mark.parametrize('after_commit',[False,True])
def test_uncertain_write_stops_then_explicit_recovery_and_resume(repo,monkeypatch,after_commit):
    bundle,_=convert(tiny(),COMPILED);original=repo.graph.query;fired=False
    def fail(query,*a,**kw):
        nonlocal fired
        if not fired and 'SET g.repo_revision=$next_revision' in query:
            fired=True
            if after_commit:original(query,*a,**kw)
            raise ConnectionError('Injected lost mutation response')
        return original(query,*a,**kw)
    monkeypatch.setattr(repo.graph,'query',fail)
    with pytest.raises(ImportFailure,match='DATABASE_OUTCOME_UNKNOWN'):Importer(repo).run(bundle)
    monkeypatch.setattr(repo.graph,'query',original)
    repo.recover_pending()
    resumed=Importer(repo).run(bundle)
    assert resumed['graph_revision']==len(bundle['nodes'])+len(bundle['relationships'])
    assert resumed['matched']==int(after_commit)


def test_concurrent_equal_importers_are_idempotent(repo):
    bundle,_=convert(tiny(),COMPILED)
    with ThreadPoolExecutor(2) as pool:results=list(pool.map(lambda _:Importer(repo).run(bundle),range(2)))
    total=len(bundle['nodes'])+len(bundle['relationships'])
    final=Importer(repo).run(bundle)
    assert sum(r['created'] for r in results)==total and final['graph_revision']==total and final['created']==0


def test_importer_preserves_explicit_cross_category_path_and_disconnected_control(db,repo):
    # Purpose-built graph is genuine test data, not invented municipal evidence.
    original_name=new_test_graph_name(4)
    try:
        MigrationRunner(db,original_name).apply();original=fixture_graph(GraphRepository(db,original_name))
        nodes=original.graph.ro_query('MATCH (n:CivicEntity) RETURN labels(n),properties(n) LIMIT 100',timeout=1000).result_set
        records=[original.decode_node(*row) for row in nodes]
        edges=original.graph.ro_query('MATCH (s)-[r]->(t) RETURN type(r),s.id,t.id,properties(r) LIMIT 100',timeout=1000).result_set
        bundle={'contract_version':1,'converter_version':'1.0','conversion_at':COMPILED,'source_hash':'test-fixture','registry_hash':original.registry.sha256,
                'nodes':[{'label':n.kind,'properties':n.properties} for n in records],
                'relationships':[{'type':k,'source_id':s,'target_id':t,'properties':p} for k,s,t,p in edges]}
        bundle['manifest']=manifest_for(bundle['nodes'],bundle['relationships']);Importer(repo).run(bundle)
        q=QueryRequest(template='cross_category_paths',id='W',as_of='2026-10-17T23:00:00Z')
        before=GraphQueries(original).run(q);after=GraphQueries(repo).run(q)
        assert [p.model_dump() for p in before.paths]==[p.model_dump() for p in after.paths]
        assert 'NEARBY' not in {n.id for n in after.nodes}
    finally:
        if original_name in db.list_graphs():db.select_graph(original_name).delete()


def test_inline_enums_and_temporal_cardinality_rejected_before_import(repo):
    bundle,_=convert(tiny(),COMPILED)
    bad=deepcopy(bundle);bad['relationships'][0]['properties']['valid_from']='2026-10-18T00:00:00Z';bad['relationships'][0]['properties']['valid_to']='2026-10-17T00:00:00Z'
    with pytest.raises(ImportFailure,match='INVALID_SOURCE'):Importer(repo).run(bad)
    assert repo.graph.ro_query('MATCH (n:CivicEntity) RETURN count(n)',timeout=1000).result_set==[[0]]


def test_all_registry_types_roundtrip_through_real_importer(repo):
    from app.graph.schema import Registry
    from tests.ingestion_examples import complete_source
    r=Registry();nodes=[example(kind) for kind in sorted(r.nodes)];edges=[]
    for kind,shape in r.edges.items():
        s=example(shape['from'][0],'SOURCE-'+kind);t=example(shape['to'][0],'TARGET-'+kind)
        nodes.extend([s,t]);edges.append({'type':kind,'source_id':s['properties']['id'],'target_id':t['properties']['id'],'properties':{}})
    bundle,report=convert(complete_source(nodes,edges),COMPILED)
    assert not report['quarantine']
    assert set(bundle['manifest']['node_types'])==set(r.nodes)
    assert set(bundle['manifest']['relationship_types'])==set(r.edges)
    result=Importer(repo).run(bundle)
    assert result['verified_content_hash']==bundle['manifest']['content_hash']
    assert result['created']==len(bundle['nodes'])+len(bundle['relationships'])


def test_coordinate_wire_precision_roundtrips_with_exact_hash(repo):
    n=example('Location');n['properties']['longitude']=82.96839999999999
    bundle,report=convert(source([n]),COMPILED)
    result=Importer(repo).run(bundle)
    assert result['verified_content_hash']==bundle['manifest']['content_hash']
    assert repo.get_node(n['properties']['id']).properties['longitude']==82.9684


def test_final_verification_connection_failure_reports_and_safe_rerun(repo,monkeypatch):
    bundle,_=convert(tiny(),COMPILED);original=repo.graph.ro_query
    def fail(query,*args,**kwargs):
        if query=='MATCH (n:CivicEntity) RETURN count(n)':raise ConnectionError('Injected verification connection failure')
        return original(query,*args,**kwargs)
    monkeypatch.setattr(repo.graph,'ro_query',fail)
    with pytest.raises(ImportFailure) as caught:Importer(repo).run(bundle)
    assert caught.value.code=='DATABASE_UNAVAILABLE'
    assert caught.value.report['errors'][-1]['phase']=='FINAL_VERIFICATION'
    monkeypatch.setattr(repo.graph,'ro_query',original)
    resumed=Importer(repo).run(bundle)
    assert resumed['created']==0 and resumed['matched']==len(bundle['nodes'])+len(bundle['relationships'])
