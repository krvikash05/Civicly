"""B09-R real FalkorDB decisions, edge readback and version compatibility."""
import json
from pathlib import Path
from datetime import datetime
import pytest
from app.graph.repository import GraphRepository, PreconditionFailed
from app.graph.models import digest
from app.graph.analysis.counterfactual import capture
from app.services.evidence import EvidenceService, Actor
from app.services.evidence.models import Assessment, Receipt
from app.services.evidence.reader import Reader
from tests.b09_fixtures import create, open_case, propose, request, advance_inspection, report, assess, ANALYST, Clock
from tests.graph_fixtures import evidence

pytestmark = pytest.mark.integration
PROOF = Path('docs/evidence/B09R-runtime-proof.json')


@pytest.fixture
def f(db):
    value = create(db)
    try:
        yield value
    finally:
        db.select_graph(value.repo.graph.name).delete()


def save(name, f, receipt, **other):
    a = receipt.assessment
    stored = Assessment.model_validate_json(f.repo.get_node(a.id).properties['rationale'])
    assert stored == a
    assert f.repo.get_node(a.hypothesis_id).properties['status'] == a.state_transitions[-1]
    supported = sorted(e.target for e in Reader(f.repo, f.clock()).edges('SUPPORTED_BY', source=a.id))
    contradicted = sorted(e.target for e in Reader(f.repo, f.clock()).edges('CONTRADICTED_BY', source=a.id))
    assert supported == a.supporting_evidence_ids
    assert contradicted == a.contradicting_evidence_ids
    assert Receipt.model_validate_json(receipt.model_dump_json()) == receipt
    proof = json.loads(PROOF.read_text()) if PROOF.exists() else {'class':'REAL_FALKORDB_NO_MOCKED_SUCCESS','results':{}}
    proof['results'][name] = {'receipt':receipt.model_dump(mode='json'),'supported_by':supported,
        'contradicted_by':contradicted,'hypothesis_status':a.state_transitions[-1], 'graph_fingerprint':capture(f.repo).fingerprint, **other}
    PROOF.write_text(json.dumps(proof,indent=2)+'\n')


@pytest.mark.parametrize('case,sources,label', [
    ('unreviewed-negative',[(False,False)],'INCONCLUSIVE'),
    ('reviewed-negative',[(False,True)],'CONTRADICTED'),
    ('unreviewed-positive',[(True,False)],'POSSIBLE'),
    ('reviewed-positive',[(True,True)],'SUPPORTED'),
    ('independent-reviewed',[(True,True),(True,True)],'VERIFIED'),
    ('unreviewed-conflict',[(True,True),(True,True),(False,False)],'INCONCLUSIVE'),
    ('reviewed-conflict',[(True,True),(False,True)],'INCONCLUSIVE'),
])
def test_actual_persisted_authority_matrix(f,case,sources,label):
    inv=open_case(f);h=propose(f,inv)
    ids=[]
    for i,(support,reviewed) in enumerate(sources):
        ids.append(report(f,inv,ref=str(i),codes=None if support else ['DRAIN_CLEAR'],reviewed=reviewed).entity_id)
    r=assess(f,h,ids)
    assert r.assessment.assessment == label
    c=r.assessment.classification
    if case=='unreviewed-negative':
        assert c.unreviewed_contradiction_ids==ids and not r.assessment.contradicting_evidence_ids
    if case=='unreviewed-positive':
        assert c.unreviewed_support_ids==ids and not r.assessment.supporting_evidence_ids
    save(case,f,r)


@pytest.mark.parametrize('source,kind', [('AGENT','LLM_STATEMENT'),('USER','COMPLAINT_NARRATIVE'),('SYNTHETIC','CANDIDATE_NETWORK_ASSOCIATION')])
def test_context_keeps_source_hash_without_causal_edge(f,source,kind):
    inv=open_case(f);h=propose(f,inv)
    ev=evidence(f.repo,'CONTEXT',evidence_type=kind,source_kind=source)
    r=assess(f,h,[ev.id])
    assert r.assessment.assessment=='INCONCLUSIVE'
    assert r.assessment.classification.contextual_evidence_ids==[ev.id]
    ref=next(ref for ref in r.assessment.evidence_references if ref.id==ev.id)
    assert ref.source_kind==source and ref.content_hash==ev.content_hash and ref.source_record_id
    assert not r.assessment.supporting_evidence_ids
    save('context-'+source,f,r)


def test_unrelated_investigation_same_asset_is_not_occurrence_evidence(f):
    inv=open_case(f);h=propose(f,inv)
    # Actual distinct B08 intake incident, same asset but a different declared occurrence.
    from app.services.complaints import ComplaintService
    from tests.b08_fixtures import payload
    from tests.b09r_fixtures import source_copy
    other=source_copy(f,issue='WATERLOGGING',ref='unrelated',occurred='2026-10-18T12:10:00Z',reported='2026-10-18T12:11:00Z')
    f.clock.value=datetime.fromisoformat('2026-10-18T12:20:00+00:00')
    inv2=f.service.execute({'operation':'open','request_id':'other-open','incident_ids':[other.incident_id],'cluster_id':other.cluster_id},ANALYST).entity_id
    ev=report(f,inv2,ref='unrelated-report').entity_id
    r=assess(f,h,[ev])
    assert ev in r.assessment.excluded_evidence_ids and not r.assessment.supporting_evidence_ids
    save('unrelated-same-asset',f,r)


def test_post_end_evidence_is_excluded_and_later_ongoing_evidence_is_valid(f):
    inv=open_case(f);h=propose(f,inv)
    incident=f.repo.get_node(f.receipts['WATERLOGGING'].incident_id)
    active=f.repo.update_node(incident.id,{'status':'ACTIVE'},expected_hash=incident.content_hash)
    f.repo.update_node(active.id,{'status':'ENDED','ended_at':'2026-10-18T11:00:00Z'},expected_hash=active.content_hash)
    ev=report(f,inv).entity_id
    r=assess(f,h,[ev])
    assert r.assessment.assessment=='INCONCLUSIVE' and ev in r.assessment.excluded_evidence_ids
    save('after-end',f,r)
    inv2=open_case(f,'ROAD_DAMAGE','ongoing-open');h2=propose(f,inv2,'ROAD_DAMAGE','SUBGRADE_FAILURE',ref='ongoing-hyp')
    f.clock.advance(86400*30)
    ev2=report(f,inv2,'late-continuous',['SUBGRADE_FAILURE_OBSERVED'],['R1']).entity_id
    r2=assess(f,h2,[ev2],ref='continuous')
    assert r2.assessment.assessment=='SUPPORTED'
    save('continuous-ongoing',f,r2)


def test_v1_real_history_and_receipt_replay_remain_immutable(db):
    from types import SimpleNamespace
    proof=json.loads(Path('docs/evidence/B09R-v1-proof.json').read_text())
    repo=GraphRepository(db,proof['graph'],lease_seconds=30)
    clock=Clock();clock.value=datetime.fromisoformat(proof.get('correction_as_of',proof['clock']).replace('Z','+00:00'));clock.advance(10)
    service=EvidenceService(repo,clock=clock)
    original=service.execute(proof['v1_command'],Actor.model_validate(proof['actor']))
    assert original.replayed and original.assessment.format_version==1
    assert original.assessment.assessment=='CONTRADICTED'  # Preserve historical v1 meaning, even when wrong.
    assert repo.get_node(original.entity_id).content_hash==proof['v1_assessment_node_hash']
    assert repo.get_node(original.journal_id).content_hash==proof['v1_journal_node_hash']
    f=SimpleNamespace(repo=repo,clock=clock,service=service)
    existing=service.history(proof['hypothesis_id'],clock())
    if len(existing)==1:
        proof['before_correction_hypothesis_hash']=repo.get_node(proof['hypothesis_id']).content_hash
        proof['correction_as_of']=clock.advance()
        Path('docs/evidence/B09R-v1-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
        r=service.execute({'operation':'assess','request_id':'rule-v2-correction','hypothesis_id':proof['hypothesis_id'],
            'expected_hash':proof['before_correction_hypothesis_hash'],'as_of':proof['correction_as_of']},ANALYST)
    else:
        r=service.execute({'operation':'assess','request_id':'rule-v2-correction','hypothesis_id':proof['hypothesis_id'],
            'expected_hash':proof['before_correction_hypothesis_hash'],'as_of':proof['correction_as_of']},ANALYST)
    history=service.history(proof['hypothesis_id'],clock())
    assert [(a.format_version,a.assessment) for a in history]==[(1,'CONTRADICTED'),(2,'INCONCLUSIVE')]
    assert history[1].previous_assessment_id==history[0].id
    assert repo.get_node(original.entity_id).content_hash==proof['v1_assessment_node_hash']
    assert repo.get_node(original.journal_id).content_hash==proof['v1_journal_node_hash']
    save('v1-to-v2-append',f,r,history=[a.model_dump(mode='json') for a in history])


def test_january_repair_august_recurrence_and_retrospective_attribution(f):
    from tests.b09r_fixtures import source_copy, at, attributed_report
    from tests.schema_examples import common,edge
    january=source_copy(f,issue='ROAD_DAMAGE',ref='january',occurred='2027-01-05T04:00:00Z',reported='2027-01-05T05:00:00Z')
    f.receipts['ROAD_DAMAGE']=january;at(f,'2027-01-05T12:00:00Z')
    jan_inv=open_case(f,'ROAD_DAMAGE','jan-open');jan_h=propose(f,jan_inv,'ROAD_DAMAGE','SUBGRADE_FAILURE',ref='jan-hyp')
    codes=['SUBGRADE_FAILURE_OBSERVED','STRUCTURAL_TEST_FAILED']
    jan_ev=report(f,jan_inv,'january-field',codes,['R1']).entity_id
    first=assess(f,jan_h,[jan_ev],ref='jan-first');immutable_hash=f.repo.get_node(first.entity_id).content_hash
    at(f,'2027-02-10T12:00:00Z')
    incident=f.repo.get_node(january.incident_id)
    incident=f.repo.update_node(incident.id,{'status':'ACTIVE','updated_at':f.clock()},expected_hash=incident.content_hash)
    f.repo.update_node(incident.id,{'status':'ENDED','ended_at':f.clock(),'updated_at':f.clock()},expected_hash=incident.content_hash)
    # Authored recorded repair outcome, not implementation of future dispatch/monitoring workflows.
    props={**common('FEB-REPAIR'),'created_at':f.clock(),'updated_at':f.clock()}
    evidence(f.repo,'FEB-REPAIR-SOURCE',evidence_type='AUTHORED_REPAIR_RECORD',source_kind='MUNICIPAL',
        observed_at=f.clock(),recorded_at=f.clock(),created_at=f.clock(),updated_at=f.clock())
    f.repo.create_node('WorkOrder',{**props,'status':'COMPLETED','execution_mode':'SIMULATED','plan_version':1,'idempotency_key':'AUTHORED-FEB-REPAIR'})
    f.repo.create_node('ActionTask',{**props,'id':'FEB-TASK','action_type':'AUTHORED_SUBGRADE_REPAIR','status':'COMPLETED','priority':'HIGH'})
    for kind,source,target,ref in [('IMPLEMENTS','FEB-REPAIR','FEB-TASK','FEB-IMPL'),('TARGETS','FEB-TASK','R1','FEB-TARGET')]:
        f.repo.create_relationship(kind,source,target,{**edge(ref),'created_at':f.clock(),'source_evidence_id':'FEB-REPAIR-SOURCE'})
    august=source_copy(f,issue='ROAD_DAMAGE',ref='august',occurred='2027-08-02T04:00:00Z',reported='2027-08-02T05:00:00Z')
    assert january.incident_id!=august.incident_id and january.cluster_id==august.cluster_id and august.pattern_type=='RECURRENT'
    f.receipts['ROAD_DAMAGE']=august;at(f,'2027-08-02T12:00:00Z')
    aug_inv=open_case(f,'ROAD_DAMAGE','aug-open');aug_h=propose(f,aug_inv,'ROAD_DAMAGE','SUBGRADE_FAILURE',ref='aug-hyp')
    aug_ev=report(f,aug_inv,'august-field',codes,['R1']).entity_id
    jan=assess(f,jan_h,[aug_ev],ref='jan-after-aug')
    assert jan.assessment.supporting_evidence_ids==[jan_ev] and aug_ev in jan.assessment.excluded_evidence_ids
    save('january-vs-august',f,jan,january_incident=january.incident_id,august_incident=august.incident_id,
         B08_pattern=august.pattern_type,repair_id='FEB-REPAIR')
    aug=assess(f,aug_h,[jan_ev,aug_ev],ref='aug-assessment')
    assert aug.assessment.supporting_evidence_ids==[aug_ev] and jan_ev in aug.assessment.excluded_evidence_ids
    save('august-only',f,aug)
    combined_inv=f.service.execute({'operation':'open','request_id':'combined-open',
        'incident_ids':[january.incident_id,august.incident_id],'cluster_id':august.cluster_id},ANALYST).entity_id
    combined_h=propose(f,combined_inv,'ROAD_DAMAGE','SUBGRADE_FAILURE',ref='combined-hyp',
        incident_ids=[january.incident_id,august.incident_id])
    combined=assess(f,combined_h,[jan_ev,aug_ev],ref='combined-assessment')
    assert combined.assessment.assessment=='SUPPORTED'  # Two sources globally are not two per occurrence.
    assert all(any('required for '+i in gap for gap in combined.assessment.missing_evidence)
               for i in [january.incident_id,august.incident_id])
    save('per-occurrence-corroboration',f,combined)
    at(f,'2027-09-01T12:00:00Z')
    retrospective=attributed_report(f,jan_inv,'retrospective',codes=codes,attribution={
        'incident_ids':[january.incident_id],'mode':'RETROSPECTIVE','rationale':'Rechecked the archived January field tests against this named repaired occurrence',
        'basis_evidence_ids':[jan_ev]}).entity_id
    retro=assess(f,jan_h,[retrospective],ref='retro-assessment')
    assert set(retro.assessment.supporting_evidence_ids)=={jan_ev,retrospective}
    assert retro.assessment.assessment=='SUPPORTED'  # Derivative report cannot invent independent corroboration.
    assert any(u.evidence_id==retrospective and u.basis_evidence_ids==[jan_ev] and u.incident_ids==[january.incident_id]
               for u in retro.assessment.classification.uses)
    save('retrospective-validated',f,retro)
    past=assess(f,jan_h,[retrospective,aug_ev],ref='past-cutoff',as_of='2027-03-01T12:00:00Z')
    assert set(past.assessment.excluded_evidence_ids)>={retrospective,aug_ev}
    assert past.assessment.supporting_evidence_ids==[jan_ev]
    assert not {retrospective,aug_ev}&{r.id for r in past.assessment.evidence_references}
    assert f.repo.get_node(first.entity_id).content_hash==immutable_hash
    assert f.repo.get_node(january.cluster_id).properties['pattern_type']=='RECURRENT'
    save('past-cutoff-without-future-knowledge',f,past,immutable_first_hash=immutable_hash)


def test_utility_path_expiry_reassessment_preserves_context_and_nearby_disconnection(f):
    from tests.schema_examples import edge, asset
    from app.services.evidence.policies import POLICIES
    inv=open_case(f,'ROAD_DAMAGE')
    f.repo.create_relationship('UNDERLIES','P1','R1',{**edge('PIPE-ROAD'),
        'association_status':'VERIFIED','source_evidence_id':'EV','valid_from':'2026-10-17T00:00:00Z'})
    h=propose(f,inv,'ROAD_DAMAGE','UTILITY_LEAK',asset_ids=['P1'],
        topology={'source_id':'P1','target_id':'R1','operation':'dependencies'})
    codes=POLICIES['ROAD_DAMAGE']['UTILITY_LEAK']['confirming']
    a=report(f,inv,'pipe-first',codes,['P1']);b=report(f,inv,'pipe-second',codes,['P1'])
    first=assess(f,h,[a.entity_id,b.entity_id],ref='verified-pipe')
    assert first.assessment.assessment=='VERIFIED' and first.assessment.paths
    assert 'EV' in first.assessment.classification.contextual_evidence_ids
    save('utility-verified-path',f,first)
    link=f.repo.get_relationship('PIPE-ROAD');f.clock.advance()
    f.repo.update_relationship(link.id,{'valid_to':f.clock()},expected_hash=link.content_hash)
    after=assess(f,h,ref='expired-pipe')
    assert after.assessment.assessment=='SUPPORTED' and not after.assessment.paths
    assert 'EV' not in after.assessment.supporting_evidence_ids
    assert f.repo.get_node(first.entity_id).properties['assessment']=='VERIFIED'
    save('utility-expired-path',f,after)
    f.repo.create_node('WaterPipe',asset('WaterPipe','NEARBY-PIPE'))
    f.repo.create_relationship('LOCATED_AT','NEARBY-PIPE','L1',{**edge('NEARBY-LOCATION'),'source_evidence_id':'EV'})
    with pytest.raises(PreconditionFailed):
        propose(f,inv,'ROAD_DAMAGE','UTILITY_LEAK',ref='nearby-no-path',asset_ids=['NEARBY-PIPE'],
            topology={'source_id':'NEARBY-PIPE','target_id':'R1','operation':'dependencies'})


def test_real_mcp_broker_reads_v2_report_provenance_without_contract_changes(f,db):
    import asyncio
    import sys
    from mcp import Client,StdioServerParameters
    from app.mcp.runtime import ROOT
    from app.mcp.civicly.runtime import configure,connections
    from app.mcp.civicly.broker import DomainBroker
    from app.mcp.civicly.storage import TraceStore
    from app.services.evidence.models import Report
    from tests.b09r_fixtures import attributed_report
    inv=open_case(f);h=propose(f,inv)
    a=attributed_report(f,inv,'explicit-current',codes=['OBSTRUCTION_OBSERVED','FLOW_RESTRICTED'],assets=['D1'],
        attribution={'incident_ids':[f.receipts['WATERLOGGING'].incident_id],
            'rationale':'Direct observation for the explicitly named ongoing occurrence'})
    b=report(f,inv,'independent-current')
    assessment=assess(f,h,[a.entity_id,b.entity_id])
    assert assessment.assessment.assessment=='VERIFIED'
    configure(db)
    async def run():
        params=StdioServerParameters(command=sys.executable,args=['-m','tests.b09_server',f.repo.graph.name],
            cwd=str(ROOT),env={'PYTHONPATH':str(ROOT/'backend')})
        with connections() as (_,writer,name):
            store=TraceStore(writer,name)
            async with Client(params,mode='legacy',read_timeout_seconds=8) as client:
                broker=DomainBroker(client,store);await broker.discover()
                assert len(broker.tools())==12
                value=await broker.call('civicly::get_maintenance_history',{'asset_id':'D1',
                    'from_time':'2026-10-17T00:00:00Z','to_time':f.clock(),'as_of':f.clock()})
                assert value['status'] in {'SUCCESS','PARTIAL'},value.get('error')
                records={event['record_id']:event for event in value['records']}
                assert a.entity_id in records[a.updated_ids[0]]['evidence_ids']
                assert b.entity_id not in records[a.updated_ids[0]]['evidence_ids']
                actual=next(n for n in value['data']['nodes'] if n['id']==a.entity_id)
                typed=Report.model_validate_json(actual['properties']['summary'])
                assert typed.format_version==2 and typed.attribution.incident_ids==[f.receipts['WATERLOGGING'].incident_id]
                assert store.get(value['execution_id']).validated_output
                save('real-mcp-v2-report',f,assessment,mcp_result=value)
    asyncio.run(run())
