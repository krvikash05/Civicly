"""Real canonical FalkorDB writes/reads; injected failures surround actual queries."""
import json,asyncio,sys
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from pathlib import Path
from uuid import uuid4
import pytest
from redis.exceptions import ConnectionError
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository,Conflict,PreconditionFailed,OutcomeUnknown,NotFound
from app.graph.targets import new_test_graph_name
from app.graph.models import QueryRequest
from app.graph.queries import GraphQueries
from app.graph.analysis.engine import GraphAnalysis
from app.graph.analysis.models import CaseRequest
from app.graph.analysis.evaluation import verify_city
from app.mcp.runtime import CITY_GRAPH,ROOT
from app.services.complaints import ComplaintService,Review
from app.services.complaints.models import Journal
from tests.b08_fixtures import payload,populate,CLOCK
from tests.schema_examples import common,edge,NOW

pytestmark=pytest.mark.integration
PROOF=ROOT/'docs/evidence/B08-runtime-proof.json'

@pytest.fixture
def repo(db):
    name=new_test_graph_name(8)
    try:
        MigrationRunner(db,name).apply();r=GraphRepository(db,name,lease_seconds=30);populate(r);yield r
    finally:
        if name in db.list_graphs():db.select_graph(name).delete()

def service(repo):return ComplaintService(repo,clock=lambda:CLOCK)
def counts(repo):return repo._read('MATCH (n:CivicEntity) RETURN count(n)')[0][0],repo._read('MATCH ()-[e]->() RETURN count(e)')[0][0]
def save(name,value,repo):
    report=json.loads(PROOF.read_text()) if PROOF.exists() else {'evidence_class':'REAL_FALKORDB_CONTROLLED_FIXTURES_AND_READONLY_CITY','examples':{}}
    report['examples'][name]={'graph':repo.graph.name,'result':value.model_dump(mode='json') if hasattr(value,'model_dump') else value,'counts':counts(repo)}
    PROOF.write_text(json.dumps(report,indent=2)+'\n')


def test_same_report_stable_retry_and_raw_source_preservation(repo):
    s=service(repo);raw=payload(description='  Synthetic\n reported condition  ');before=counts(repo);r=s.intake(raw);after=counts(repo)
    retry=s.intake(raw);assert counts(repo)==after and retry.incident_id==r.incident_id and retry.replayed and retry.historical_receipt
    assert r.graph_revision==GraphQueries(repo)._state() and r.pattern_type=='SINGLE_EVENT'
    j=Journal.model_validate_json(repo.get_node(r.journal_id).properties['summary'])
    assert j.original==raw and j.state=='COMMITTED';assert repo.get_node(r.complaint_id).properties['description']=='Synthetic reported condition'
    assert repo._read('MATCH (c:Complaint {id:$id})-[:REPORTS]->(i:Incident)-[:PART_OF]->(p:ProblemCluster) RETURN c.id,i.id,p.id',{'id':r.complaint_id})==[[r.complaint_id,r.incident_id,r.cluster_id]]
    assert all(repo.get_relationship(e).properties.get('association_status')!='VERIFIED' for p in r.graph_paths for e in p.edge_ids)
    save('same-report',{'before':before,'after':after,'first':r.model_dump(mode='json'),'retry':retry.model_dump(mode='json')},repo)


def test_changed_source_version_or_content_conflicts(repo):
    s=service(repo);s.intake(payload());before=counts(repo)
    for raw in [payload(description='changed'),payload(source_version='2'),payload(issue_type='ROAD_DAMAGE',asset_ids=['R1'])]:
        with pytest.raises(Conflict):s.intake(raw)
    assert counts(repo)==before


def test_independent_reports_share_ongoing_incident_not_complaint_identity(repo):
    s=service(repo);a=s.intake(payload());b=s.intake(payload(ref='report-2',source_id='independent-source'))
    assert a.complaint_id!=b.complaint_id and a.journal_id!=b.journal_id and a.incident_id==b.incident_id and b.classification=='SAME_INCIDENT'
    assert b.pattern_type=='SINGLE_EVENT';assert len(repo._read('MATCH (c:Complaint)-[:REPORTS]->(i:Incident {id:$id}) RETURN c.id',{'id':a.incident_id}))==2
    save('independent-reports',b,repo)


def test_distinct_explicit_occurrences_and_continued_unresolved_context(repo):
    s=service(repo);a=s.intake(payload(event_reference='event-1'));b=s.intake(payload(ref='next',event_reference='event-2'))
    assert a.incident_id!=b.incident_id and a.cluster_id==b.cluster_id
    assert b.pattern_type=='PERSISTENT' and b.classification=='CONTINUING_UNRESOLVED'
    save('distinct-unresolved',b,repo)


def test_persistent_duration_does_not_require_report_count(repo):
    r=service(repo).intake(payload(occurred_at='2026-10-16T04:00:00Z'))
    assert r.pattern_type=='PERSISTENT' and r.classification=='CONTINUING_UNRESOLVED'


def test_after_recorded_end_is_recurrent_with_separate_incident(repo):
    s=service(repo);a=s.intake(payload(occurred_at='2026-10-17T01:00:00Z',reported_at='2026-10-17T02:00:00Z'))
    n=repo.get_node(a.incident_id);n=repo.update_node(n.id,{'status':'ACTIVE'},expected_hash=n.content_hash);repo.update_node(n.id,{'status':'ENDED','ended_at':'2026-10-17T03:00:00Z'},expected_hash=n.content_hash)
    b=s.intake(payload(ref='later'));assert b.incident_id!=a.incident_id and b.cluster_id==a.cluster_id and b.pattern_type=='RECURRENT'
    assert b.classification=='AFTER_RECORDED_END' and any('completed orders alone' in x for x in b.explanations)
    save('recurrent-after-end',b,repo)


def test_missing_end_date_is_explicit_unknown_not_invented_recurrence(repo):
    s=service(repo);a=s.intake(payload(occurred_at='2026-10-17T01:00:00Z',reported_at='2026-10-17T02:00:00Z'))
    n=repo.get_node(a.incident_id);n=repo.update_node(n.id,{'status':'ACTIVE'},expected_hash=n.content_hash);repo.update_node(n.id,{'status':'ENDED'},expected_hash=n.content_hash)
    b=s.intake(payload(ref='later'));assert b.cluster_id!=a.cluster_id and b.pattern_type!='RECURRENT'
    assert any('termination date' in g for g in b.uncertainty)


def test_nearby_disconnected_assets_do_not_merge(repo):
    s=service(repo);a=s.intake(payload());b=s.intake(payload(ref='nearby',location_id='L2',asset_ids=['D2']))
    assert a.incident_id!=b.incident_id and a.cluster_id!=b.cluster_id and b.pattern_type=='SINGLE_EVENT'
    save('nearby-disconnected',b,repo)

@pytest.mark.parametrize('reverse',[False,True])
@pytest.mark.parametrize('status,shared',[('VERIFIED',True),('CANDIDATE',False)])
def test_cross_category_topology_qualification_keeps_incidents_distinct(repo,status,shared,reverse):
    repo.create_relationship('UNDERLIES','P1','R1',{**edge('P-R'),'association_status':status,'source_evidence_id':'EV'})
    s=service(repo)
    first=payload(ref='water',asset_ids=['P1']) if reverse else payload('ROAD_DAMAGE')
    second=payload('ROAD_DAMAGE') if reverse else payload(ref='water',asset_ids=['P1'])
    a=s.intake(first);b=s.intake(second)
    assert a.incident_id!=b.incident_id
    assert (a.cluster_id==b.cluster_id)==shared
    assert b.pattern_type==('CROSS_CATEGORY' if shared else 'SINGLE_EVENT')
    if shared:assert any('P-R' in p.edge_ids for p in b.graph_paths)
    save('cross-category-'+status+'-'+str(reverse),b,repo)


def test_all_issue_validators_histories_claims_and_measurements(repo):
    # Add source history to the existing base without duplicating base identities.
    from tests.b08_fixtures import populate_history
    populate_history(repo)
    s=service(repo)
    measurement={'name':'water_depth','value':.2,'unit':'m','observed_at':'2026-10-18T04:00:00Z','source_id':'fixture-observer','source_reference':'depth-1','basis':'OBSERVED'}
    water=s.intake(payload(ref='depth',details={'measurements':[measurement],'claims':[{'kind':'BLOCKAGE','statement':'Reporter suspects blockage','source_id':'fixture-observer','source_reference':'claim-1'}]}))
    assert water.assessment.measurements[0]['value']==20. and water.assessment.measurements[0]['verification_status']=='REPORTED'
    assert any('rainfall measurement missing' in g for g in water.assessment.gaps)
    road=s.intake(payload('ROAD_DAMAGE',ref='road',details={'distress_description':'Pothole','claims':[{'kind':'PIPE_LEAK','statement':'Suspected cause only','source_id':'s','source_reference':'r'}]}))
    assert {'INS','ORDER','OUTCOME'}<=set(road.assessment.history_ids)
    assert 'EV-INS' in road.source_evidence_ids and any('do not verify resolution' in g for g in road.assessment.gaps)
    waste=s.intake(payload('WASTE_ACCUMULATION',ref='waste',details={'reported_pickup_status':'MISSED','illegal_dumping_claim':True,'quantity_description':'several bags'}))
    assert {'PICKUP-MISSED','PICKUP-PARTIAL','PICKUP-COMPLETED'}<=set(waste.assessment.history_ids)
    assert waste.assessment.contradictions and any('clock' in g for g in waste.assessment.gaps) and any('ambiguous' in g for g in waste.assessment.gaps)
    for name,r in [('water-validator',water),('road-validator',road),('waste-validator',waste)]:save(name,r,repo)

@pytest.mark.parametrize('change',[{'location_id':'MISSING'},{'asset_ids':['MISSING']},{'evidence_ids':['MISSING']},{'issue_type':'ROAD_DAMAGE','asset_ids':['D1']}])
def test_invalid_references_do_not_prepare_journal(repo,change):
    before=counts(repo)
    with pytest.raises((NotFound,PreconditionFailed)):service(repo).intake(payload(**change))
    assert counts(repo)==before


def test_concurrent_external_retry_and_same_event_intake(repo):
    barrier=Barrier(2)
    def run(raw):barrier.wait();return service(repo).intake(raw)
    with ThreadPoolExecutor(2) as pool:results=list(pool.map(run,[payload(),payload()]))
    assert len({r.complaint_id for r in results})==1
    barrier=Barrier(2)
    with ThreadPoolExecutor(2) as pool:results=list(pool.map(run,[payload(ref='two'),payload(ref='three',source_id='independent')]))
    assert len({r.incident_id for r in results})==1
    assert repo._read('MATCH (n:Complaint) RETURN count(n)')==[[3]] and repo._read('MATCH (n:Incident) RETURN count(n)')==[[1]]
    save('concurrent',{'complaints':3,'incidents':1,'result':results[0].model_dump(mode='json')},repo)

@pytest.mark.parametrize('committed',[False,True])
def test_real_uncertain_response_recovery_without_duplicate_batches(repo,monkeypatch,committed):
    original=repo.graph.query;fired=False
    def fault(query,*args,**kwargs):
        nonlocal fired
        if 'SET j.summary=$summary' in query and not fired:
            fired=True
            if committed:original(query,*args,**kwargs)
            raise ConnectionError('B08 injected lost response; real graph state retained')
        return original(query,*args,**kwargs)
    monkeypatch.setattr(repo.graph,'query',fault)
    with pytest.raises(OutcomeUnknown):service(repo).intake(payload())
    state=repo._read("MATCH (e:Evidence {evidence_type:'COMPLAINT_INTAKE'}) RETURN e.summary")[0][0]
    assert Journal.model_validate_json(state).state==('COMMITTED' if committed else 'PREPARED')
    assert repo._read('MATCH (c:Complaint) RETURN count(c)')==[[1 if committed else 0]]
    monkeypatch.setattr(repo.graph,'query',original);r=service(repo).intake(payload())
    assert repo._read('MATCH (c:Complaint) RETURN count(c)')==[[1]] and service(repo).incomplete()==[]
    save('uncertain-'+str(committed),r,repo)


def test_real_native_batch_failure_rolls_back_and_resumes(repo,monkeypatch):
    original=repo.graph.query;fired=False
    def fault(query,*args,**kw):
        nonlocal fired
        if 'SET j.summary=$summary' in query and not fired:
            fired=True;query=query.replace('SET j.summary=$summary','CREATE (:CivicEntity {id:$existing0}) SET j.summary=$summary')
        return original(query,*args,**kw)
    monkeypatch.setattr(repo.graph,'query',fault)
    with pytest.raises(OutcomeUnknown):service(repo).intake(payload())
    assert repo._read('MATCH (c:Complaint) RETURN count(c)')==[[0]] and service(repo).incomplete()
    assert repo._read('MATCH (i:Incident) RETURN count(i)')==[[0]] and repo._read('MATCH (p:ProblemCluster) RETURN count(p)')==[[0]]
    monkeypatch.setattr(repo.graph,'query',original);r=service(repo).intake(payload());assert service(repo).incomplete()==[]
    save('native-rollback-recovery',r,repo)


def test_reviewed_regroup_preserves_old_interval_and_rejects_stale_review(repo):
    s=service(repo);a=s.intake(payload());b=s.intake(payload(ref='other',asset_ids=['D2'],location_id='L2'))
    old=next(e for e in repo._edges('PART_OF') if e.source==a.incident_id)
    args={'request_id':'correction-1','reviewer_id':'synthetic-analyst','role':'ANALYST','reviewed':True,'reason':'Reviewed mistaken grouping; preserve history',
        'incident_id':a.incident_id,'target_cluster_id':b.cluster_id,'expected_incident_hash':repo.get_node(a.incident_id).content_hash,'expected_membership_hash':old.content_hash,'expected_target_hash':repo.get_node(b.cluster_id).content_hash}
    newer=ComplaintService(repo,clock=lambda:'2026-10-18T12:01:00Z');r=newer.regroup(Review(**args))
    assert repo.get_relationship(old.id).properties['valid_to']==r['effective_at']
    assert repo.get_relationship(r['membership_id']).properties['valid_from']==r['effective_at']
    assert newer.regroup(Review(**args))['replayed']
    with pytest.raises(PreconditionFailed):newer.regroup(Review(**{**args,'request_id':'stale-new-request'}))
    with pytest.raises(Conflict):repo.create_relationship('PART_OF',a.incident_id,a.cluster_id,{**edge('CONFLICT'),'valid_from':r['effective_at']})
    replay=s.intake(payload());assert replay.historical_receipt and replay.cluster_id==a.cluster_id
    save('reviewed-correction',r,repo)


def test_city_readonly_preview_preserves_all_source_fingerprints(db):
    bundle=json.loads(Path('data/ingestion/city-v3.json').read_text());repo=GraphRepository(db,CITY_GRAPH)
    before=verify_city(repo,bundle)
    r=ComplaintService(repo,clock=lambda:CLOCK).preview(payload(ref='city',location_id='LOC-004',asset_ids=['DRAIN-D12']))
    assert r.preview and r.search_limited and r.uncertainty and not any(p.context.get('classification')=='REPORTED_INTAKE_CONTEXT' for p in r.graph_paths)
    with pytest.raises(PreconditionFailed):ComplaintService(repo).intake(payload())
    assert verify_city(repo,bundle)==before;save('city-preview',r,repo)


def test_claimed_end_and_completed_work_do_not_verify_resolution(repo):
    from tests.b08_fixtures import populate_history
    populate_history(repo);s=service(repo)
    a=s.intake(payload('ROAD_DAMAGE',event_reference='road-1',ended_at='2026-10-18T04:30:00Z'))
    b=s.intake(payload('ROAD_DAMAGE',ref='road-2',event_reference='road-2',occurred_at='2026-10-18T04:40:00Z'))
    assert repo.get_node(a.incident_id).properties['status']=='REPORTED'
    assert b.pattern_type=='PERSISTENT' and b.classification!='AFTER_RECORDED_END'
    assert any(h.result=='ACTION_COMPLETED' for h in b.assessment.history_records)
    save('completion-not-resolution',b,repo)


def test_same_location_different_infrastructure_and_claim_conflict(repo):
    s=service(repo);a=s.intake(payload());b=s.intake(payload(ref='different-asset',asset_ids=['D2']))
    assert a.cluster_id!=b.cluster_id and a.incident_id!=b.incident_id
    assert any('conflicts with inventory' in g for g in b.assessment.gaps)


def test_measurement_units_and_rainfall_attribution_real_intake(repo):
    s=service(repo)
    rainfall={'name':'rainfall','value':2.,'unit':'cm','observed_at':'2026-10-18T04:00:00Z','source_id':'synthetic-weather','source_reference':'rain-1','basis':'OBSERVED'}
    water=s.intake(payload(ref='rain',details={'measurements':[rainfall],'rainfall_station_reference':'SYNTHETIC-STATION','rainfall_from':'2026-10-18T03:00:00Z','rainfall_to':'2026-10-18T04:00:00Z'}))
    assert water.assessment.measurements[0]['value']==20. and water.assessment.measurements[0]['unit']=='mm'
    road=s.intake(payload('ROAD_DAMAGE',ref='damage',details={'distress_description':'Pothole','measurements':[{**rainfall,'name':'pothole_depth','value':30.,'unit':'mm'}]}))
    assert road.assessment.measurements[0]['value']==3. and road.assessment.measurements[0]['unit']=='cm'
    waste=s.intake(payload('WASTE_ACCUMULATION',ref='volume',details={'measurements':[{**rainfall,'name':'waste_quantity','value':.25,'unit':'m3'}]}))
    assert waste.assessment.measurements[0]['value']==250. and waste.assessment.measurements[0]['unit']=='L'
    for name,r in [('rain-attribution',water),('road-measurement',road),('waste-measurement',waste)]:
        assert all(x.reliability=='UNVERIFIED' for x in r.evidence_references if x.id==r.journal_id);save(name,r,repo)


def test_incomplete_journal_can_resume_after_application_interruption(repo,monkeypatch):
    from app.services.complaints.writer import Writer
    original=Writer.commit
    def stopped(*a,**k):raise RuntimeError('Actual prepared journal retained; application stopped before domain commit')
    monkeypatch.setattr(Writer,'commit',stopped)
    with pytest.raises(RuntimeError):service(repo).intake(payload())
    assert service(repo).incomplete() and repo._read('MATCH (n:Complaint) RETURN count(n)')==[[0]]
    monkeypatch.setattr(Writer,'commit',original)
    r=service(repo).intake(payload());assert not service(repo).incomplete();save('application-resume',r,repo)


def test_concurrent_conflicting_external_identity_fails_closed(repo):
    barrier=Barrier(2)
    def run(desc):
        barrier.wait()
        try:return service(repo).intake(payload(description=desc)).complaint_id
        except Conflict:return 'CONFLICT'
    with ThreadPoolExecutor(2) as pool:results=list(pool.map(run,['synthetic report A','synthetic report B']))
    assert results.count('CONFLICT')==1 and repo._read('MATCH (c:Complaint) RETURN count(c)')==[[1]]


def test_b03_b05_and_actual_mcp_broker_read_new_incidents(repo,db):
    from mcp import Client,StdioServerParameters
    from app.mcp.civicly.runtime import configure,connections
    from app.mcp.civicly.broker import DomainBroker
    from app.mcp.civicly.storage import TraceStore
    s=service(repo)
    a=s.intake(payload(event_reference='first',occurred_at='2026-10-18T02:00:00Z'))
    b=s.intake(payload(ref='second',event_reference='second'))
    paths=GraphQueries(repo).run(QueryRequest(template='incident_history',id='D1',as_of=CLOCK,include_candidates=True))
    assert {a.incident_id,b.incident_id}<={n.id for n in paths.nodes if n.kind=='Incident'}
    verified=GraphQueries(repo).run(QueryRequest(template='incident_history',id='D1',as_of=CLOCK))
    assert not verified.paths # reported intake does not become verified association
    cases=GraphAnalysis(repo).cases(CaseRequest(seed_incident_id=b.incident_id,as_of=CLOCK,include_candidates=True))
    assert a.incident_id in {row.id for row in cases.rows}
    configure(db)
    async def run():
        params=StdioServerParameters(command=sys.executable,args=['-m','tests.b08_server',repo.graph.name],cwd=str(ROOT),env={'PYTHONPATH':str(ROOT/'backend')})
        with connections() as (_,writer,name):
            store=TraceStore(writer,name)
            async with Client(params,mode='legacy',read_timeout_seconds=8) as client:
                broker=DomainBroker(client,store);await broker.discover()
                assert len(broker.tools())==12 and not any('intake' in t['name'] for t in broker.tools())
                r=await broker.call('civicly::find_related_incidents',{'incident_id':b.incident_id,'max_results':10,'include_candidates':True,'as_of':CLOCK})
                assert r['status']=='PARTIAL' and r['graph_revision']==GraphQueries(repo)._state()
                assert a.incident_id in {v['incident_id'] for v in r['related_incidents']}
                assert all(e['properties'].get('association_status')!='VERIFIED' for e in r['data']['edges'] if e['kind']=='AFFECTS')
                assert store.get(r['execution_id']).validated_output
                save('actual-mcp-fixture-source',{'note':'TEST ONLY source substitution; production context/namespace unchanged','result':r},repo)
    asyncio.run(run())


def test_conflicting_measurements_retained_without_arbitrary_choice(repo):
    m={'name':'water_depth','value':.2,'unit':'m','observed_at':'2026-10-18T04:00:00Z','source_id':'source-a','source_reference':'a'}
    r=service(repo).intake(payload(details={'measurements':[m,{**m,'value':5.,'unit':'cm','source_id':'source-b','source_reference':'b'}]}))
    assert {x['value'] for x in r.assessment.measurements}=={20.,5.}
    assert r.assessment.contradictions and 'no arbitrary winner' in r.assessment.contradictions[0]
    save('contradictory-measurements',r,repo)


def test_missing_asset_context_does_not_merge_location_only_reports(repo):
    s=service(repo);a=s.intake(payload(asset_ids=[]));b=s.intake(payload(ref='location-only',asset_ids=[]))
    assert a.incident_id!=b.incident_id and a.cluster_id!=b.cluster_id
    assert any('No explicit infrastructure' in g for g in b.uncertainty)


def test_multiple_eligible_clusters_require_review_instead_of_arbitrary_assignment(repo):
    s=service(repo);a=s.intake(payload(event_reference='event-a'));b=s.intake(payload(ref='b',event_reference='event-b'))
    repo.create_node('ProblemCluster',{**common('REVIEW-TARGET'),'title':'Explicit synthetic review target','status':'OPEN','first_seen_at':NOW,'pattern_type':'SINGLE_EVENT'})
    old=next(e for e in repo._edges('PART_OF') if e.source==b.incident_id)
    review=Review(request_id='split-b',reviewer_id='synthetic-analyst',role='ANALYST',reviewed=True,reason='Reviewed separate group',incident_id=b.incident_id,target_cluster_id='REVIEW-TARGET',expected_incident_hash=repo.get_node(b.incident_id).content_hash,expected_membership_hash=old.content_hash,expected_target_hash=repo.get_node('REVIEW-TARGET').content_hash)
    ComplaintService(repo,clock=lambda:'2026-10-18T12:01:00Z').regroup(review)
    c=ComplaintService(repo,clock=lambda:'2026-10-18T12:02:00Z').intake(payload(ref='c',event_reference='event-c'))
    assert c.cluster_id not in {a.cluster_id,'REVIEW-TARGET'} and any('Multiple eligible primary clusters' in g for g in c.uncertainty)
    save('ambiguous-cluster-review',c,repo)


def test_prepared_equivalent_unit_retry_preserves_first_raw_measurement(repo,monkeypatch):
    from app.services.complaints.writer import Writer
    m={'name':'water_depth','value':.29,'unit':'m','observed_at':'2026-10-18T04:00:00Z','source_id':'source','source_reference':'reading'}
    first=payload(details={'measurements':[m]});equivalent=payload(details={'measurements':[{**m,'value':29.,'unit':'cm'}]})
    original=Writer.commit
    def stopped(*a,**kw):raise RuntimeError('Real prepared intake interrupted')
    monkeypatch.setattr(Writer,'commit',stopped)
    with pytest.raises(RuntimeError):service(repo).intake(first)
    monkeypatch.setattr(Writer,'commit',original);r=service(repo).intake(equivalent)
    assert r.assessment.measurements[0]['value']==29. and r.assessment.measurements[0]['original_value']==.29 and r.assessment.measurements[0]['original_unit']=='m'
    j=Journal.model_validate_json(repo.get_node(r.journal_id).properties['summary'])
    assert j.original==first and j.canonical['details']['measurements'][0]['unit']=='cm'
    before=counts(repo);assert service(repo).intake(first).replayed and counts(repo)==before
    save('equivalent-unit-original-recovery',r,repo)


def test_issue_primary_asset_allows_secondary_cross_category_infrastructure(repo):
    repo.create_relationship('UNDERLIES','P1','R1',{**edge('MIXED-P-R'),'association_status':'VERIFIED','source_evidence_id':'EV'})
    r=service(repo).intake(payload('ROAD_DAMAGE',asset_ids=['R1','P1','D1']))
    actual={e.target for e in repo._edges('AFFECTS') if e.source==r.incident_id}
    assert actual=={'R1','P1','D1'} and all(e.properties['association_status']=='REPORTED' for e in repo._edges('AFFECTS'))
    save('mixed-asset-context',r,repo)
