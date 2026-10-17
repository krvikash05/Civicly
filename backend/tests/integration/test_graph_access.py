import json
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from redis.exceptions import ConnectionError, ResponseError

from app.graph.migration import MigrationRunner
from app.graph.models import QueryRequest
from app.graph.queries import GraphQueries, ReadLimits
from app.graph.repository import GraphRepository, Conflict, NotFound, PreconditionFailed, OutcomeUnknown, ScopeError
from app.graph.schema import SchemaError
from tests.schema_examples import asset, common, edge, NOW
from tests.graph_fixtures import evidence, task, fixture_graph

pytestmark = pytest.mark.integration


@pytest.fixture
def repo(db):
    name='civicly_b03_test_'+uuid4().hex
    g=db.select_graph(name)
    try:
        assert MigrationRunner(db,name).apply()['ready']
        yield GraphRepository(db,name)
    finally:
        if name in db.list_graphs():
            g.delete()


@pytest.fixture
def populated(repo):
    return fixture_graph(repo)


def test_repository_strict_types_identity_update_and_append_only(repo):
    n=repo.create_node('DrainSegment',asset('DrainSegment','A'))
    assert n.labels==('DrainSegment','InfrastructureAsset')
    with pytest.raises(Conflict): repo.create_node('RoadSegment',asset('RoadSegment','A'))
    for bad in ({'unknown':1},{'schema_version':2},{'operational_status':False}):
        with pytest.raises(SchemaError): repo.create_node('RoadSegment',{**asset('RoadSegment','BAD'),**bad})
    with pytest.raises(SchemaError): repo.create_node('RoadSegment',{**asset('RoadSegment','BAD'),'municipality_id':'elsewhere'})
    with pytest.raises(NotFound): repo.get_node('MISSING')
    n2=repo.update_node('A',{'name':'updated'},expected_hash=n.content_hash)
    assert n2.properties['name']=='updated'
    with pytest.raises(PreconditionFailed): repo.update_node('A',{'name':'stale'},expected_hash=n.content_hash)
    with pytest.raises(PreconditionFailed): repo.update_node('A',{'id':'B'},expected_hash=n2.content_hash)
    props=common('HA'); props.pop('updated_at')
    a=repo.create_node('HypothesisAssessment',{**props,'assessment':'POSSIBLE','rationale':'test','assessed_at':NOW})
    with pytest.raises(PreconditionFailed): repo.update_node('HA',{'rationale':'rewrite'},expected_hash=a.content_hash)


def test_endpoint_direction_scope_evidence_and_cross_type_edge_ids(repo):
    repo.create_node('DrainSegment',asset('DrainSegment','D'))
    repo.create_node('RoadSegment',asset('RoadSegment','R'))
    repo.create_node('Location',{**common('L'),'name':'Test','latitude':0.0,'longitude':0.0})
    with pytest.raises(SchemaError): repo.create_relationship('SERVES','L','D',edge('BAD-DIR'))
    with pytest.raises(NotFound): repo.create_relationship('SERVES','D','MISSING',edge('BAD-MISSING'))
    with pytest.raises(NotFound): repo.create_relationship('SERVES','D','L',{**edge('BAD-EV'),'association_status':'VERIFIED','source_evidence_id':'NONE'})
    evidence(repo,reliability='UNVERIFIED')
    with pytest.raises(PreconditionFailed): repo.create_relationship('SERVES','D','L',{**edge('BAD-EV'),'association_status':'VERIFIED','source_evidence_id':'EV'})
    ev=repo.get_node('EV'); repo.update_node('EV',{'reliability':'VERIFIED'},expected_hash=ev.content_hash)
    e=repo.create_relationship('SERVES','D','L',{**edge('REL'),'association_status':'VERIFIED','source_evidence_id':'EV'})
    with pytest.raises(Conflict): repo.create_relationship('LOCATED_AT','R','L',edge('REL'))
    with pytest.raises(Conflict): repo.create_node('DrainInlet',asset('DrainInlet','REL'))
    with pytest.raises(Conflict): repo.create_relationship('SERVES','D','L',edge('DUP'))
    with pytest.raises(SchemaError): repo.update_relationship('REL',{'unknown':1},expected_hash=e.content_hash)
    e2=repo.update_relationship('REL',{'valid_from':NOW,'valid_to':'2026-10-18T00:00:00Z'},expected_hash=e.content_hash)
    assert e2.properties['valid_to']=='2026-10-18T00:00:00Z'
    with pytest.raises(PreconditionFailed): repo.update_relationship('REL',{'valid_to':'2026-10-19T00:00:00Z'},expected_hash=e.content_hash)
    ev=repo.get_node('EV')
    with pytest.raises(PreconditionFailed): repo.update_node('EV',{'reliability':'UNVERIFIED'},expected_hash=ev.content_hash)
    # Privileged raw corruption is deliberately outside repository authorization; reads fail closed.
    repo.graph.query('MATCH (n:CivicEntity {id:$id}) SET n.municipality_id=$scope',params={'id':'L','scope':'other'})
    with pytest.raises(ScopeError): repo.create_relationship('LOCATED_AT','R','L',edge('BAD-SCOPE'))
    assert repo.graph.ro_query('MATCH ()-[r]->() RETURN count(r)').result_set==[[1]]


def test_temporal_cardinality_and_domain_cycles(repo):
    for id in ('A','B','C'): repo.create_node('DrainSegment',asset('DrainSegment',id))
    for id in ('DEP1','DEP2'): repo.create_node('Department',{**common(id),'name':'test','department_type':'TEST'})
    repo.create_relationship('MAINTAINED_BY','A','DEP1',{**edge('OWN1'),'valid_from':NOW,'valid_to':'2026-10-18T00:00:00Z'})
    with pytest.raises(Conflict): repo.create_relationship('MAINTAINED_BY','A','DEP2',{**edge('OWN2'),'valid_from':NOW})
    repo.create_relationship('MAINTAINED_BY','A','DEP2',{**edge('OWN2'),'valid_from':'2026-10-18T00:00:00Z'})
    with pytest.raises(SchemaError): repo.create_relationship('DRAINS_TO','A','B',{**edge('REVERSED'),'valid_from':'2026-10-18T00:00:00Z','valid_to':NOW})
    with pytest.raises(SchemaError): repo.create_relationship('DRAINS_TO','A','A',edge('SELF'))
    repo.create_relationship('DRAINS_TO','A','B',edge('AB'))
    with pytest.raises(PreconditionFailed): repo.create_relationship('DRAINS_TO','B','A',edge('BA'))
    evidence(repo)
    repo.create_relationship('DRAINS_TO','B','A',{**edge('BA'),'association_status':'VERIFIED','source_evidence_id':'EV'},inspected_cycle_evidence_id='EV')
    for id in ('T1','T2','T3'): task(repo,id)
    repo.create_relationship('DEPENDS_ON','T1','T2',edge('T12'))
    repo.create_relationship('DEPENDS_ON','T2','T3',edge('T23'))
    with pytest.raises(PreconditionFailed): repo.create_relationship('DEPENDS_ON','T3','T1',edge('T31'))


def test_disjoint_drain_history_not_universally_acyclic(repo):
    for id in ('A','B'): repo.create_node('DrainSegment',asset('DrainSegment',id))
    repo.create_relationship('DRAINS_TO','A','B',{**edge('AB'),'valid_from':NOW,'valid_to':'2026-10-18T00:00:00Z'})
    repo.create_relationship('DRAINS_TO','B','A',{**edge('BA'),'valid_from':'2026-10-18T00:00:00Z'})


def test_concurrent_node_cas_and_relationship_identity(repo):
    n=repo.create_node('DrainSegment',asset('DrainSegment','A'))
    barrier=Barrier(2)
    def change(value):
        barrier.wait()
        try: repo.update_node('A',{'name':value},expected_hash=n.content_hash); return 'ok'
        except PreconditionFailed: return 'stale'
    with ThreadPoolExecutor(2) as pool: assert sorted(pool.map(change,['one','two']))==['ok','stale']
    repo.create_node('Location',{**common('L'),'name':'test','latitude':0.0,'longitude':0.0})
    barrier=Barrier(2)
    def add(kind):
        barrier.wait()
        try: repo.create_relationship(kind,'A','L',edge('GLOBAL')); return 'ok'
        except Conflict: return 'conflict'
    with ThreadPoolExecutor(2) as pool: assert sorted(pool.map(add,['SERVES','LOCATED_AT']))==['conflict','ok']
    assert repo.graph.ro_query('MATCH ()-[r]->() WHERE r.id=$id RETURN count(r)',params={'id':'GLOBAL'}).result_set==[[1]]


def test_expired_writer_fenced_by_successor(repo):
    repo.lease_seconds=0.1
    statement=repo.registry.node_statement('DrainSegment',asset('DrainSegment','STALE'))
    with repo._session() as stale:
        time.sleep(0.15)
        repo.create_node('DrainSegment',asset('DrainSegment','CURRENT'))
        with pytest.raises(PreconditionFailed):
            repo._commit(stale,'node','STALE','',statement.query.split(' RETURN n.id')[0],statement.params,'n')
    with pytest.raises(NotFound): repo.get_node('STALE')
    assert repo.get_node('CURRENT').id=='CURRENT'


@pytest.mark.parametrize('after_commit',[False,True])
def test_lost_response_actual_database_reconciliation(repo,monkeypatch,after_commit):
    original=repo.graph.query
    def fault(query,*args,**kwargs):
        if 'SET g.repo_revision=$next_revision' in query:
            if after_commit: original(query,*args,**kwargs)
            raise ConnectionError('injected lost response')
        return original(query,*args,**kwargs)
    monkeypatch.setattr(repo.graph,'query',fault)
    with pytest.raises(OutcomeUnknown): repo.create_node('DrainSegment',asset('DrainSegment','UNCERTAIN'))
    monkeypatch.setattr(repo.graph,'query',original)
    if not after_commit:
        with pytest.raises(OutcomeUnknown): GraphQueries(repo)._state()
    status=repo.recover_pending()
    assert status['revision']==int(after_commit)
    if after_commit:
        assert repo.get_node('UNCERTAIN').id=='UNCERTAIN'
        with pytest.raises(Conflict): repo.create_node('DrainSegment',asset('DrainSegment','UNCERTAIN'))
    else:
        with pytest.raises(NotFound): repo.get_node('UNCERTAIN')
        repo.create_node('DrainSegment',asset('DrainSegment','UNCERTAIN'))
    audit=json.loads(repo.graph.ro_query("MATCH (m:CivicSchemaMigration) RETURN m.repo_audit").result_set[0][0])
    assert audit[0]['state']==('COMMITTED' if after_commit else 'ABORTED_UNCHANGED')


def test_failed_statement_atomic_domain_and_metadata_rollback(repo):
    repo.create_node('DrainSegment',asset('DrainSegment','EXIST'))
    with repo._session() as session:
        before=session.revision
        with pytest.raises(OutcomeUnknown):
            repo._commit(session,'node','PARTIAL','',
                'CREATE (n:DrainSegment:InfrastructureAsset:CivicEntity) SET n=$first '
                'CREATE (dup:DrainSegment:InfrastructureAsset:CivicEntity) SET dup=$duplicate',
                {'first':asset('DrainSegment','PARTIAL'),'duplicate':asset('DrainSegment','EXIST')},'n')
    assert repo.recover_pending()['revision']==before
    with pytest.raises(NotFound): repo.get_node('PARTIAL')
    assert repo.graph.ro_query('MATCH (n:CivicEntity) RETURN count(n)').result_set==[[1]]


@pytest.mark.parametrize('template,id',[
 ('drainage_paths','D1'),('shared_infrastructure',''),('incident_history','LW'),
 ('maintenance_history','D1'),('cross_category_paths','W'),('hypothesis_evidence','INV'),
 ('ownership_dependencies','W'),('task_dependencies','T1')])
def test_all_preapproved_templates_real_results_and_readonly(populated,template,id):
    q=GraphQueries(populated)
    before=populated.graph.ro_query('MATCH (n) RETURN count(n)').result_set
    revision=q._state()
    request=QueryRequest(template=template,id=id,incident_ids=('I1','I2'),as_of=NOW,max_hops=6)
    result=q.run(request)
    assert result.paths and result.nodes and result.edges
    assert result.graph_revision==revision and not result.truncated
    assert json.loads(result.model_dump_json())['municipality_id']=='demo-city'
    assert populated.graph.ro_query('MATCH (n) RETURN count(n)').result_set==before and q._state()==revision
    if template=='cross_category_paths':
        assert set(n.id for n in result.nodes)=={'W','LW','D1','D2','D3','LR','R'}
        assert 'NEARBY' not in {n.id for n in result.nodes}
        # A different location has identical coordinates but no physical-network link.
        assert populated.get_node('LN').properties['latitude']==populated.get_node('LW').properties['latitude']
        assert not populated.graph.ro_query('MATCH (n:Location {id:$id})<-[:SERVES]-() RETURN n.id',
                                            params={'id':'LN'},timeout=1000).result_set
        assert result.paths[0].directions==('OUTGOING','INCOMING','OUTGOING','OUTGOING','OUTGOING','INCOMING')
    if template=='shared_infrastructure':
        assert {'D2','D3'}=={p.context['shared_asset_id'] for p in result.paths}
        assert all(set(p.context['shared_incident_ids'])=={'I1','I2'} for p in result.paths)
    if template=='hypothesis_evidence':
        assert {p.context['evidence_relation'] for p in result.paths}=={'SUPPORTED_BY','CONTRADICTED_BY'}
    if template=='maintenance_history': assert {'INS','WO','OUT'} <= {n.id for n in result.nodes}


def test_directions_time_candidates_and_budgets(populated):
    q=GraphQueries(populated)
    upstream=q.run(QueryRequest(template='drainage_paths',id='D3',direction='upstream',as_of=NOW))
    assert {e.id for e in upstream.edges}=={'E0','E1'}
    assert all(all(d=='INCOMING' for d in p.directions) for p in upstream.paths)
    assert not q.run(QueryRequest(template='drainage_paths',id='D1',as_of='2026-10-16T23:59:59Z')).paths
    e=populated.get_relationship('E0')
    populated.update_relationship('E0',{'valid_from':NOW,'valid_to':'2026-10-18T00:00:00Z'},expected_hash=e.content_hash)
    assert not q.run(QueryRequest(template='drainage_paths',id='D1',as_of='2026-10-18T00:00:00Z')).paths
    limited=q.run(QueryRequest(template='drainage_paths',id='D1',as_of=NOW,limit=1))
    assert limited.truncated and len(limited.paths)==1
    capped=GraphQueries(populated,ReadLimits(max_nodes=1)).run(QueryRequest(template='drainage_paths',id='D1',as_of=NOW))
    assert capped.truncated and not capped.paths and not capped.nodes
    with pytest.raises(PreconditionFailed): GraphQueries(populated,ReadLimits(max_hops=1)).run(QueryRequest(template='drainage_paths',id='D1',as_of=NOW))
    with pytest.raises(TypeError): q.run('CREATE (:Bad)')
    with pytest.raises(NotFound): q.run(QueryRequest(template='drainage_paths',id="D1'}) CREATE (:Bad) //",as_of=NOW))
    e=populated.get_relationship('E1')
    populated.update_relationship('E1',{'association_status':'CANDIDATE'},expected_hash=e.content_hash)
    assert not q.run(QueryRequest(template='drainage_paths',id='D2',as_of=NOW)).paths
    assert q.run(QueryRequest(template='drainage_paths',id='D2',as_of=NOW,include_candidates=True)).paths


def test_temporal_fraction_precision_history_and_future_updates(populated):
    q=GraphQueries(populated)
    # Fractional as_of after whole-second data includes it (raw lexical Z ordering would fail).
    assert q.run(QueryRequest(template='drainage_paths',id='D1',as_of='2026-10-17T00:00:00.1Z')).paths
    incident=populated.get_node('I2')
    populated.update_node('I2',{'started_at':'2026-10-17T00:00:00.5Z','updated_at':'2026-10-17T00:00:00.5Z'},expected_hash=incident.content_hash)
    result=q.run(QueryRequest(template='incident_history',id='LW',as_of='2026-10-17T00:00:00.9Z',after='2026-10-17T00:00:00.2Z'))
    assert {n.id for n in result.nodes if n.kind=='Incident'}=={'I2'}
    earlier=q.run(QueryRequest(template='incident_history',id='LW',as_of='2026-10-17T00:00:00.4Z'))
    assert {n.id for n in earlier.nodes if n.kind=='Incident'}=={'I1'}
    with pytest.raises(PreconditionFailed): q.run(QueryRequest(template='incident_history',id='LW',as_of=NOW,after='2026-10-18T00:00:00Z'))


def test_query_only_uses_real_ro_command_and_bounded_timeout(populated,monkeypatch):
    seen=[]; original=populated.graph.ro_query
    def readonly(query,*args,**kwargs):
        seen.append(kwargs.get('timeout'))
        return original(query,*args,**kwargs)
    def deny_write(*args,**kwargs): raise AssertionError('Read template attempted GRAPH.QUERY')
    monkeypatch.setattr(populated.graph,'ro_query',readonly)
    monkeypatch.setattr(populated.graph,'query',deny_write)
    assert GraphQueries(populated).run(QueryRequest(template='drainage_paths',id='D1',as_of=NOW,timeout_ms=750)).paths
    assert 750 in seen and all(0<t<=1000 for t in seen)


def test_concurrent_cardinality_and_cycle_serialized(repo):
    for id in ('A','B'): repo.create_node('DrainSegment',asset('DrainSegment',id))
    for id in ('X','Y'): repo.create_node('Department',{**common(id),'name':'test','department_type':'TEST'})
    barrier=Barrier(2)
    def assign(id):
        barrier.wait()
        try: repo.create_relationship('MAINTAINED_BY','A',id,edge('OWNER-'+id)); return 'ok'
        except Conflict: return 'conflict'
    with ThreadPoolExecutor(2) as pool: assert sorted(pool.map(assign,['X','Y']))==['conflict','ok']
    barrier=Barrier(2)
    def connect(pair):
        barrier.wait()
        try: repo.create_relationship('DRAINS_TO',*pair,edge(''.join(pair))); return 'ok'
        except PreconditionFailed: return 'cycle'
    with ThreadPoolExecutor(2) as pool: assert sorted(pool.map(connect,[('A','B'),('B','A')]))==['cycle','ok']


def test_missing_property_reference_future_evidence_and_recovery_mismatch(repo):
    with pytest.raises(NotFound):
        repo.create_node('AssetConditionSnapshot',{**common('SNAP'),'asset_id':'MISSING','evidence_id':'MISSING',
                         'observed_at':NOW,'condition':'TEST'})
    # Recovery never erases an intent if privileged external state differs from its pre-state.
    pending={'kind':'node','id':'CHANGED','before_hash':'','request_id':'test','request_hash':'test','at':NOW}
    statement=repo.registry.node_statement('DrainSegment',asset('DrainSegment','CHANGED'))
    repo.graph.query(statement.query,params=statement.params)
    repo.graph.query('MATCH (m:CivicSchemaMigration) SET m.repo_pending=$pending',params={'pending':json.dumps(pending)})
    with pytest.raises(OutcomeUnknown): repo.recover_pending()
    with pytest.raises(OutcomeUnknown): GraphQueries(repo)._state()
    assert repo.get_node('CHANGED').id=='CHANGED'


def test_candidate_pointer_cannot_leak_future_evidence(repo):
    for id in ('A','B'): repo.create_node('DrainSegment',asset('DrainSegment',id))
    future='2026-10-18T00:00:00Z'
    evidence(repo,created_at=future,updated_at=future,observed_at=future,recorded_at=future)
    with pytest.raises(PreconditionFailed):
        repo.create_relationship('DRAINS_TO','A','B',{**edge('VERIFIED-FUTURE'),'association_status':'VERIFIED','source_evidence_id':'EV'})
    repo.create_relationship('DRAINS_TO','A','B',{**edge('CANDIDATE'),'association_status':'CANDIDATE','source_evidence_id':'EV'})
    q=GraphQueries(repo)
    assert not q.run(QueryRequest(template='drainage_paths',id='A',as_of=NOW,include_candidates=True)).paths
    assert q.run(QueryRequest(template='drainage_paths',id='A',as_of=future,include_candidates=True)).paths


def test_native_point_repository_roundtrip_update(repo):
    n=repo.create_node('Location',{**common('POINT'),'name':'Test','latitude':12.5,'longitude':77.5,
                                    'geo_point':{'latitude':12.5,'longitude':77.5}})
    assert n.properties['geo_point']=={'latitude':12.5,'longitude':77.5}
    changed=repo.update_node('POINT',{'name':'Changed'},expected_hash=n.content_hash)
    assert changed.properties['geo_point']==n.properties['geo_point']
