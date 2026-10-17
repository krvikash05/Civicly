"""B03-R real corrective cases. Original B01/B02/B03 tests remain intact."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from app.graph.migration import MigrationRunner, MigrationError
from app.graph.models import QueryRequest
from app.graph.queries import GraphQueries, ReadLimits
from app.graph.repository import GraphRepository, Conflict, PreconditionFailed
from app.graph.targets import new_test_graph_name
from tests.graph_fixtures import evidence, fixture_graph
from tests.schema_examples import NOW, common, asset, edge

pytestmark=pytest.mark.integration
END='2026-10-18T00:00:00Z'
LATER='2026-10-19T00:00:00Z'


@pytest.fixture
def repo(db):
    name=new_test_graph_name(3)
    try:
        assert MigrationRunner(db,name).apply()['ready']
        yield GraphRepository(db,name)
    finally:
        if name in db.list_graphs(): db.select_graph(name).delete()


def location(repo,id):
    return repo.create_node('Location',{**common(id),'name':'Synthetic','latitude':12.0,'longitude':77.0})


def incident(repo,id):
    return repo.create_node('Incident',{**common(id),'issue_type':'WATERLOGGING','subtype':'TEST',
        'status':'OPEN','severity':'HIGH','started_at':NOW})


def schedule(repo,id,service='WASTE',**bounds):
    return repo.create_node('ServiceSchedule',{**common(id),'service_type':service,'timezone':'UTC',
        'schedule_spec':'TEST opaque schedule','valid_from':NOW,**bounds})


def route(repo,id='ROUTE'):
    return repo.create_node('CollectionRoute',{**common(id),'route_code':id,'operational_status':'ACTIVE'})


@pytest.mark.parametrize('kind',['IN_ZONE','PART_OF'])
def test_primary_zone_and_cluster_overlap_history_and_many_members(repo,kind):
    for id in ('S1','S2'):
        location(repo,id) if kind=='IN_ZONE' else incident(repo,id)
    for id in ('T1','T2'):
        props=common(id)
        if kind=='IN_ZONE':repo.create_node('Zone',{**props,'name':id,'zone_type':'WARD'})
        else:repo.create_node('ProblemCluster',{**props,'title':id,'pattern_type':'RECURRENT','status':'OPEN','first_seen_at':NOW})
    first=repo.create_relationship(kind,'S1','T1',{**edge('FIRST'),'valid_from':NOW,'valid_to':END})
    with pytest.raises(Conflict): repo.create_relationship(kind,'S1','T2',{**edge('OVERLAP'),'valid_from':NOW})
    repo.create_relationship(kind,'S1','T2',{**edge('HISTORY'),'valid_from':END})
    with pytest.raises(Conflict): repo.update_relationship('FIRST',{'valid_to':LATER},expected_hash=first.content_hash)
    assert repo.get_relationship('FIRST').content_hash==first.content_hash
    # Many different locations/incidents may belong to the same zone/cluster.
    repo.create_relationship(kind,'S2','T1',edge('ANOTHER-MEMBER'))
    assert repo.graph.ro_query('MATCH ()-[r]->() RETURN count(r)',timeout=1000).result_set==[[3]]


def test_schedules_use_service_and_effective_intervals_and_node_update_proof(repo):
    route(repo)
    a=schedule(repo,'A',valid_to=END)
    b=schedule(repo,'B',valid_from=END)
    c=schedule(repo,'C','STREET_SWEEPING')
    schedule(repo,'D')
    schedule(repo,'EMPTY-SCHEDULE',valid_to=END)
    # Edge bounds are open: node bounds still make A/B nonoverlapping.
    repo.create_relationship('HAS_SCHEDULE','ROUTE','A',edge('SA'))
    repo.create_relationship('HAS_SCHEDULE','ROUTE','B',edge('SB'))
    repo.create_relationship('HAS_SCHEDULE','ROUTE','C',edge('SC'))
    with pytest.raises(Conflict): repo.create_relationship('HAS_SCHEDULE','ROUTE','D',edge('OVERLAP'))
    with pytest.raises(PreconditionFailed): repo.create_relationship('HAS_SCHEDULE','ROUTE','EMPTY-SCHEDULE',{**edge('EMPTY'),'valid_from':LATER})
    with pytest.raises(Conflict): repo.update_node('B',{'valid_from':NOW},expected_hash=b.content_hash)
    with pytest.raises(Conflict): repo.update_node('C',{'service_type':'WASTE'},expected_hash=c.content_hash)
    with pytest.raises(Conflict): repo.update_node('A',{'valid_from':END,'valid_to':LATER},expected_hash=a.content_hash)
    assert repo.get_node('B').content_hash==b.content_hash
    assert repo.get_node('C').content_hash==c.content_hash
    assert repo.graph.ro_query('MATCH ()-[r:HAS_SCHEDULE]->() RETURN count(r)',timeout=1000).result_set==[[3]]


def test_schedule_edge_update_cannot_expand_into_conflict(repo):
    route(repo); schedule(repo,'A'); schedule(repo,'B')
    repo.create_relationship('HAS_SCHEDULE','ROUTE','A',{**edge('SA'),'valid_from':NOW,'valid_to':END})
    b=repo.create_relationship('HAS_SCHEDULE','ROUTE','B',{**edge('SB'),'valid_from':END})
    with pytest.raises(Conflict): repo.update_relationship('SB',{'valid_from':NOW},expected_hash=b.content_hash)
    assert repo.get_relationship('SB').content_hash==b.content_hash
    # Node edits that leave active intervals compatible are permitted.
    a=repo.get_node('A')
    assert repo.update_node('A',{'valid_to':END},expected_hash=a.content_hash).properties['valid_to']==END


def test_schedule_race_serialized(repo):
    route(repo); schedule(repo,'A'); schedule(repo,'B')
    barrier=Barrier(2)
    def add(id):
        barrier.wait()
        try:repo.create_relationship('HAS_SCHEDULE','ROUTE',id,edge('S'+id));return 'ok'
        except Conflict:return 'conflict'
    with ThreadPoolExecutor(2) as pool:assert sorted(pool.map(add,['A','B']))==['conflict','ok']


def connected_network(repo,drain_hops):
    evidence(repo)
    for id,label in [('W','WasteCollectionPoint'),('ROAD','RoadSegment'),('NEARBY','RoadSegment')]:
        repo.create_node(label,asset(label,id))
    for id in ('LW','LR','LN'):location(repo,id)
    for i in range(drain_hops+1):repo.create_node('DrainSegment',asset('DrainSegment','D'+str(i)))
    relations=[('LOCATED_AT','W','LW'),('LOCATED_AT','ROAD','LR'),('LOCATED_AT','NEARBY','LN'),
               ('SERVES','D0','LW'),('SERVES','D'+str(drain_hops),'LR')]
    relations += [('DRAINS_TO','D'+str(i),'D'+str(i+1)) for i in range(drain_hops)]
    for i,(kind,s,t) in enumerate(relations):
        props=edge('E'+str(i))
        if kind in repo.policy['verified_associations']:props.update(association_status='VERIFIED',source_evidence_id='EV')
        repo.create_relationship(kind,s,t,props)


@pytest.mark.parametrize('drain_hops',[1,2,3])
def test_default_cross_category_total_budget_and_bounded_negatives(repo,drain_hops):
    connected_network(repo,drain_hops)
    result=GraphQueries(repo).run(QueryRequest(template='cross_category_paths',id='W',as_of=NOW))
    assert result.search_budget.effective_total_hops==6 and result.search_budget.infrastructure_hops==2
    assert result.search_limited and not result.truncated
    assert 'NEARBY' not in {n.id for n in result.nodes}
    if drain_hops<=2:
        assert len(result.paths)==1 and len(result.paths[0].edge_ids)==4+drain_hops
        assert result.paths[0].directions[:2]==('OUTGOING','INCOMING')
    else:
        assert not result.paths  # Actual seven-edge connection exists, outside this search.
        assert repo.graph.ro_query('MATCH p=(:DrainSegment {id:$id})-[:DRAINS_TO*3..3]->() RETURN size(relationships(p)) LIMIT 1',params={'id':'D0'},timeout=1000).result_set==[[3]]
        assert any('does not prove global absence' in r for r in result.reservations)


def test_cross_category_minimum_and_insufficient_budgets(repo):
    connected_network(repo,1)
    q=GraphQueries(repo)
    result=q.run(QueryRequest(template='cross_category_paths',id='W',as_of=NOW,max_hops=5))
    assert len(result.paths[0].edge_ids)==5 and result.search_budget.infrastructure_hops==1
    for hops in (1,4):
        with pytest.raises(PreconditionFailed,match='at least 5'):q.run(QueryRequest(template='cross_category_paths',id='W',as_of=NOW,max_hops=hops))
    with pytest.raises(PreconditionFailed):GraphQueries(repo,ReadLimits(max_hops=4)).run(QueryRequest(template='cross_category_paths',id='W',as_of=NOW))


def test_six_edge_connection_is_not_falsely_absent_at_default(repo):
    connected_network(repo,2)
    q=GraphQueries(repo)
    short=q.run(QueryRequest(template='cross_category_paths',id='W',as_of=NOW,max_hops=5))
    assert not short.paths and short.search_limited and not short.truncated
    assert q.run(QueryRequest(template='cross_category_paths',id='W',as_of=NOW)).paths
    # Genuinely disconnected network: neither coordinates nor LOCATED_AT bridge it.
    location(repo,'ISOLATED-L')
    repo.create_node('WasteCollectionPoint',asset('WasteCollectionPoint','ISOLATED'))
    repo.create_relationship('LOCATED_AT','ISOLATED','ISOLATED-L',edge('ISOLATED-AT'))
    empty=q.run(QueryRequest(template='cross_category_paths',id='ISOLATED',as_of=NOW))
    assert not empty.paths and empty.search_limited


def test_shared_infrastructure_connector_and_zero_hop_boundaries(repo):
    evidence(repo)
    for id in ('D0','D1'):repo.create_node('DrainSegment',asset('DrainSegment',id))
    for id in ('I1','I2'):incident(repo,id)
    verified={'association_status':'VERIFIED','source_evidence_id':'EV'}
    repo.create_relationship('AFFECTS','I1','D0',{**edge('A1'),**verified})
    repo.create_relationship('AFFECTS','I2','D1',{**edge('A2'),**verified})
    repo.create_relationship('DRAINS_TO','D0','D1',{**edge('D01'),**verified})
    q=GraphQueries(repo)
    one=q.run(QueryRequest(template='shared_infrastructure',incident_ids=('I1','I2'),as_of=NOW,max_hops=1))
    assert not one.paths and one.search_budget.infrastructure_hops==0 and one.search_limited
    two=q.run(QueryRequest(template='shared_infrastructure',incident_ids=('I1','I2'),as_of=NOW,max_hops=2))
    assert {p.context['shared_asset_id'] for p in two.paths}=={'D1'}
    assert {len(p.edge_ids) for p in two.paths}=={1,2} and two.search_budget.infrastructure_hops==1
    # When both incidents directly affect one asset, total budget1 is sufficient.
    repo.create_relationship('AFFECTS','I2','D0',{**edge('A3'),**verified})
    direct=q.run(QueryRequest(template='shared_infrastructure',incident_ids=('I1','I2'),as_of=NOW,max_hops=1))
    assert direct.paths and all(len(p.edge_ids)==1 for p in direct.paths)


@pytest.mark.parametrize('milestone',[4,25])
def test_later_milestone_isolated_graphs_real_migration_and_repository(db,milestone):
    name=new_test_graph_name(milestone)
    try:
        assert MigrationRunner(db,name).apply()['ready']
        repo=GraphRepository(db,name)
        assert repo.create_node('DrainSegment',asset('DrainSegment','ONLY-TEST')).id=='ONLY-TEST'
    finally:
        if name in db.list_graphs():db.select_graph(name).delete()


def test_fixed_template_minima_and_omitted_branches_are_explicit(repo):
    fixture_graph(repo)
    q=GraphQueries(repo)
    for hops,paths in [(1,1),(2,3),(3,4)]:
        result=q.run(QueryRequest(template='maintenance_history',id='D1',as_of=NOW,max_hops=hops))
        assert len(result.paths)==paths
        assert max(len(p.edge_ids) for p in result.paths)<=hops
        assert result.search_limited==(hops<3) and result.search_budget.template_max_hops==3
        assert ('OUT' in {n.id for n in result.nodes})==(hops==3)
    with pytest.raises(PreconditionFailed,match='at least 3'):
        q.run(QueryRequest(template='hypothesis_evidence',id='INV',as_of=NOW,max_hops=2))
    with pytest.raises(PreconditionFailed,match='at least 2'):
        q.run(QueryRequest(template='hypothesis_evidence',id='H',as_of=NOW,max_hops=1))
    result=q.run(QueryRequest(template='hypothesis_evidence',id='H',as_of=NOW,max_hops=2))
    assert result.paths and not result.search_limited and result.search_budget.template_max_hops==2
    one=q.run(QueryRequest(template='ownership_dependencies',id='W',as_of=NOW,max_hops=1))
    two=q.run(QueryRequest(template='ownership_dependencies',id='W',as_of=NOW,max_hops=2))
    assert one.search_limited and not two.search_limited
    assert 'SCHEDULE' not in {n.id for n in one.nodes} and 'SCHEDULE' in {n.id for n in two.nodes}
