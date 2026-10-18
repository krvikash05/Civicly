"""B14 real FalkorDB/SDK/native B09 journals and B08 recurrence, zero providers."""
import asyncio,json,copy,os
from pathlib import Path
import pytest
from app.active import active_scope
from app.graph.repository import PreconditionFailed,Conflict
from app.services.operations.auth import Denied
from app.services.operations.models import OpsRecovery
from app.services.operations.service import stable
from app.services.evidence.reader import Reader
from app.services.evidence.models import Receipt
from app.services.evidence.service import EvidenceService
from app.graph.analysis.engine import GraphAnalysis
from app.graph.analysis.models import CaseRequest
from tests.b14_fixtures import prepare,Run
from tests.integration.test_memory_graphrag import memory
pytestmark=pytest.mark.integration

def save(name,value):Path('docs/evidence/'+os.environ.get('CIVICLY_OPERATIONS_EVIDENCE_PREFIX','B14')+'-'+name+'.json').write_text(json.dumps(value,indent=2)+'\n')

@pytest.mark.parametrize('issue',['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION'])
def test_actual_three_issue_completion_verification_and_water_recurrence(db,tmp_path,memory,issue):
 p,r,clock,path,inv,draft,planning,auth,tokens,ops=prepare(db,tmp_path,memory,issue)
 async def run():
  with active_scope(p):
   f=Run(r,clock,ops,tokens,issue);await f.begin(planning,draft)
   draft_saved=copy.deepcopy(f.saved)
   report_cmd,report,completion_cmd,completed=await f.complete()
   assert completed['status']=='COMPLETED' and completed['result']=='ACTION_COMPLETED'
   assert r.get_node(f.b['plan_id']).properties['status']=='MONITORING'
   assert r.get_node(inv).properties['status']=='MONITORING'
   assert planning.store.get(f.b['plan_id'])==draft_saved
   assert (await f.call(completion_cmd))==completed
   assert await f.call(report_cmd,reviewer_token=tokens['OP-ANALYST'])==report
   EvidenceService(r,clock=clock).readback(Receipt.model_validate(report))
   # Independent monitor has no opportunity yet; complete work does not close case.
   clock.advance();start=clock();clock.advance()
   empty={'operation':'evaluate','request_id':f.key(),'work_order_id':f.w['id'],'expected_hash':f.hash(),'evidence_ids':[],'window_start':start,'window_end':clock()}
   awaiting=await f.call(empty,'OP-ANALYST');assert awaiting['assessment_status']=='MONITORING' and not awaiting['case_closed']
   query,followup=await f.followup()
   verified=await f.call(query,'OP-ANALYST')
   assert verified['assessment_status']=='RESOLUTION_VERIFIED' and verified['case_closed']
   from app.services.operations.verification import VERSION
   assert verified['policy_version']==VERSION and verified['evidence_references'][0]['id']==followup['entity_id']
   assert r.get_node(f.b['plan_id']).properties['status']=='COMPLETED' and r.get_node(inv).properties['status']=='COMPLETED'
   assert planning.store.get(f.b['plan_id'])==draft_saved
   assert await f.call(query,'OP-ANALYST')==verified
   assert r._read('MATCH (w:WorkOrder {id:$id})-[:RESULTED_IN]->(o:InterventionOutcome) RETURN count(o)',{'id':f.w['id']})==[[3]]
   proof={'graph':p.graph,'binding':f.b,'completion':completed,'no_opportunity':awaiting,'verified':verified,'report':report,'followup':followup,'provider_calls':0}
   if issue=='WATERLOGGING':
    before_agent=None
    if os.environ.get('CIVICLY_B14R_CHECKPOINT_PROOF')=='1':
     from tests.b14r_runtime import pause
     before_agent=await pause(p,r,clock,path,inv,f,planning)
    recurrence,rep=await f.followup(1.0)
    incident=Reader(r,clock()).edges('INVESTIGATES',source=inv)
    old=next(r.get_node(e.target) for e in incident if r.get_node(e.target).kind=='Incident')
    loc=next(e.target for e in r._edges('OCCURRED_AT') if e.source==old.id)
    recurrence.update(operation='recur',verified_outcome_id=verified['id'],complaint={'description':'Synthetic observed return after independently verified outcome','source_id':'B14-recurrence','external_record_id':'distinct-later-occurrence','source_channel':'SIMULATOR','source_kind':'SYNTHETIC','issue_type':issue,'subtype':old.properties['subtype'],'reported_at':clock(),'occurred_at':recurrence['window_start'],'location_id':loc,'asset_ids':draft.tasks[0].target_ids,'evidence_ids':[rep['entity_id']]})
    reopened=await f.call(recurrence,'OP-ANALYST')
    assert reopened['assessment_status']=='RECURRENCE_DETECTED' and reopened['classification']=='AFTER_RECORDED_END'
    assert r.get_node(reopened['cluster_id']).properties['status']=='REOPENED' and r.get_node(inv).properties['status']=='REOPENED'
    assert reopened['new_incident_id']!=old.id and r.get_node(old.id).properties['status']=='ENDED'
    assert ops.store.get('outcome',verified['id'])==verified
    scope_before=r._read('MATCH (i:Investigation {id:$id})-[e:INVESTIGATES]->(n:Incident) RETURN n.id,e.id ORDER BY n.id',{'id':inv})
    assert {row[0] for row in scope_before}=={old.id,reopened['new_incident_id']}
    assert reopened['investigation_id']==inv and reopened['investigates_relationship_id'] in {row[1] for row in scope_before}
    native_before=r._read('MATCH (n:CivicEntity) RETURN count(n)');events_before=r._read('MATCH (e:DomainEvent) RETURN count(e)')
    assert await f.call(recurrence,'OP-ANALYST')==reopened
    assert scope_before==r._read('MATCH (i:Investigation {id:$id})-[e:INVESTIGATES]->(n:Incident) RETURN n.id,e.id ORDER BY n.id',{'id':inv})
    assert r._read('MATCH (n:CivicEntity) RETURN count(n)')==native_before and r._read('MATCH (e:DomainEvent) RETURN count(e)')==events_before
    if before_agent:
     from tests.b14r_runtime import resume
     proof['checkpoint_refresh']=await resume(p,r,clock,path,inv,f,planning,before_agent,reopened,rep)
    # Existing B05 case-memory retrieval, rather than a B14 fake history.
    memory_result=GraphAnalysis(r).cases(CaseRequest(seed_incident_id=reopened['new_incident_id'],as_of=clock(),limit=40,max_hops=4,include_candidates=True))
    assert verified['id'] in {n.id for n in memory_result.nodes}
    assert f.w['id'] in {n.id for n in memory_result.nodes}
    proof.update(recurrence=reopened,memory=memory_result.model_dump(mode='json'))
   save('outcome-'+issue,proof)
 asyncio.run(run())

def test_actual_contradiction_preserves_assessments_and_prevents_closure(db,tmp_path,memory):
 p,r,clock,path,inv,draft,planning,auth,tokens,ops=prepare(db,tmp_path,memory,'WATERLOGGING')
 async def run():
  with active_scope(p):
   f=Run(r,clock,ops,tokens,'WATERLOGGING');await f.begin(planning,draft)
   basis=next(b for b in draft.basis if b.addressed);old=Reader(r,clock()).histories(basis.hypothesis_id)
   report_cmd,report=await f.report('COMPLETION',lambda at:[f.observation('ACTION_COMPLETED',at),f.observation('DRAIN_CLEAR',at)])
   clock.advance();key=f.key()
   c={'operation':'inspect','request_id':key,'work_order_id':f.w['id'],'expected_hash':f.hash(),'purpose':'ASSESSMENT','command':{'operation':'assess','request_id':key,'hypothesis_id':basis.hypothesis_id,'expected_hash':r.get_node(basis.hypothesis_id).content_hash,'evidence_ids':[report['entity_id']],'as_of':clock()}}
   revised=await f.call(c,'OP-ANALYST');history=Reader(r,clock()).histories(basis.hypothesis_id)
   assert history[:-1]==old and history[-1].assessment in {'CONTRADICTED','INCONCLUSIVE'}
   assert report['entity_id'] in history[-1].contradicting_evidence_ids
   _,done=await f.progress('COMPLETE',[report['entity_id']]);assert done['result']=='ACTION_COMPLETED'
   query,_=await f.followup();result=await f.call(query,'OP-ANALYST')
   assert result['assessment_status']=='INCONCLUSIVE' and not result['case_closed']
   assert r.get_node(f.b['plan_id']).properties['status']=='MONITORING'
   save('contradiction',{'graph':p.graph,'old_assessment_ids':[a.id for a in old],'new_assessment':history[-1].model_dump(mode='json'),'result':result,'completion':done})
 asyncio.run(run())

def test_actual_failed_attempt_and_persistent_problem_are_retained(db,tmp_path,memory):
 p,r,clock,path,inv,draft,planning,auth,tokens,ops=prepare(db,tmp_path,memory,'WATERLOGGING')
 async def run():
  with active_scope(p):
   f=Run(r,clock,ops,tokens,'WATERLOGGING');await f.begin(planning,draft)
   _,report,cmd,result=await f.complete(fail=True)
   assert result['status']=='BLOCKED' and result['task_status']=='FAILED' and result['assessment_status']=='INTERVENTION_FAILED'
   assert await f.call(cmd)==result
   assert r.get_node(report['entity_id'],'Evidence') and r.get_node(result['id'],'WorkOrder')
   assert r._read('MATCH (:WorkOrder {id:$id})-[:RESULTED_IN]->(o:InterventionOutcome) RETURN o.result,o.assessment_status',{'id':f.w['id']})==[['INCONCLUSIVE','INTERVENTION_FAILED']]
   with pytest.raises(PreconditionFailed):await f.progress('START')
   save('failure',{'graph':p.graph,'work_order_id':f.w['id'],'report':report,'result':result})
 asyncio.run(run())

def test_actual_execution_denials_replay_and_uncertain_completion(db,tmp_path,memory):
 p,r,clock,path,inv,draft,planning,auth,tokens,ops=prepare(db,tmp_path,memory,'WATERLOGGING')
 async def run():
  with active_scope(p):
   f=Run(r,clock,ops,tokens,'WATERLOGGING');await f.begin(planning,draft)
   bad={'operation':'progress','request_id':f.key(),'work_order_id':f.w['id'],'expected_hash':f.hash(),'action':'COMPLETE','reason':'Cannot claim completion without evidence'}
   for operator in ['OP-ANALYST','OP-ADMIN','OP-ROAD-LEAD']:
    with pytest.raises(Denied):await f.call(bad,operator)
   with pytest.raises(PreconditionFailed):await f.call(bad)
   with pytest.raises(Conflict):await f.call({**bad,'request_id':f.key(),'expected_hash':'0'*64})
   with pytest.raises(PreconditionFailed):await f.progress('START')
   # Explicit blocked-progress/unchanged assessment must not invalidate immutable gates.
   await f.progress('BLOCK')
   basis=next(b for b in draft.basis if b.addressed);old_assessment=Reader(r,clock()).histories(basis.hypothesis_id)[-1]
   clock.advance();key=f.key()
   reassess={'operation':'inspect','request_id':key,'work_order_id':f.w['id'],'expected_hash':f.hash(),'purpose':'ASSESSMENT','command':{'operation':'assess','request_id':key,'hypothesis_id':basis.hypothesis_id,'expected_hash':r.get_node(basis.hypothesis_id).content_hash,'evidence_ids':[],'as_of':clock()}}
   await f.call(reassess,'OP-ANALYST');latest=Reader(r,clock()).histories(basis.hypothesis_id)[-1]
   assert latest.id!=old_assessment.id and latest.assessment==old_assessment.assessment
   await f.progress('START');bad['expected_hash']=f.hash()
   # Native approval tamper must not become execution authority; restore exact bytes only in isolated fault fixture.
   approval=r.get_node(ops.store.get('order',f.w['id'])['approval_id']);props=approval.properties
   r.update_node(approval.id,{'status':'REVOKED'},expected_hash=approval.content_hash)
   with pytest.raises(PreconditionFailed):await f.call(bad)
   altered=r.get_node(approval.id);r.update_node(approval.id,{'status':props['status']},expected_hash=altered.content_hash)
   _,report=await f.report('COMPLETION',lambda at:[f.observation('ACTION_COMPLETED',at)])
   command={**bad,'request_id':f.key(),'expected_hash':f.hash(),'evidence_ids':[report['entity_id']]}
   with pytest.raises(OpsRecovery) as caught:await f.call(command,interrupt='after_commit')
   assert caught.value.reconciliation['commitment']=='UNKNOWN'
   assert r.get_node(f.w['id']).properties['status']=='COMPLETED'
   receipt=await f.call(command)
   assert await f.call(command)==receipt
   op=ops.store.get('operation',stable('OP',command['request_id']))
   assert op['proof']['validation_scope']=='IMMUTABLE_BINDING_RECORD_EXISTING_WORK_OR_MONITOR'
   assert r._read('MATCH (:WorkOrder {id:$id})-[:RESULTED_IN]->(o:InterventionOutcome) RETURN count(o)',{'id':f.w['id']})==[[1]]
   assert r.get_node(f.b['plan_id']).properties['status']=='MONITORING'
   # Persistent observation after technically completed repair remains unresolved.
   query,_=await f.followup(1.0);persistent=await f.call(query,'OP-ANALYST')
   assert persistent['assessment_status']=='PROBLEM_PERSISTS' and not persistent['case_closed']
   before=r._read('MATCH (o:InterventionOutcome) RETURN count(o)')
   assert await f.call({**query,'request_id':f.key()},'OP-ANALYST')==persistent
   assert r._read('MATCH (o:InterventionOutcome) RETURN count(o)')==before
   save('recovery-denials',{'graph':p.graph,'recovery':caught.value.reconciliation,'retained_completion':receipt,'persistent':persistent,'outcome_count':before,'provider_calls':0})
 asyncio.run(run())

def test_actual_road_water_dependency_progress_and_native_lifecycle(db,tmp_path,memory):
 from tests.b12_fixtures import prepared
 from tests.b13_fixtures import auth_setup
 from app.services.operations.migration import OperationsMigration
 from app.services.operations.service import Operations
 p,r,clock,path,inv,draft,planning=prepared(db,tmp_path,memory,'ROAD_DAMAGE')
 auth,tokens=auth_setup(tmp_path/'auth.sqlite3');OperationsMigration(db,p.graph).apply();ops=Operations(planning,auth,clock=clock)
 async def run():
  with active_scope(p):
   f=Run(r,clock,ops,tokens,'ROAD_DAMAGE');await f.begin(planning,draft)
   b=f.b;approval=ops.store.get('order',f.w['id'])['approval_id'];second=b['assignments'][1]
   command={**b,'operation':'order','request_id':f.key(),'approval_id':approval,'task_id':second['task_id']}
   with pytest.raises(PreconditionFailed):await f.call(command,'OP-APPROVER')
   _,_,_,first=await f.complete();assert r.get_node(b['plan_id']).properties['status']=='IN_EXECUTION'
   # Completed predecessor and legitimate graph revisions now permit dependent order.
   command['request_id']=f.key();f.w=await f.call(command,'OP-APPROVER');f.assignment_index=1;f.lead='OP-WATER-LEAD'
   await f.call({'operation':'update','request_id':f.key(),'work_order_id':f.w['id'],'expected_hash':f.hash(),'new_status':'ASSIGNED','reason':'Approved dependent utility inspection after predecessor completion'})
   await f.progress('START');_,_,_,second_done=await f.complete()
   assert r.get_node(b['plan_id']).properties['status']=='MONITORING'
   assert all(r.get_node(a['task_id']).properties['status']=='COMPLETED' for a in b['assignments'])
   assert planning.store.get(b['plan_id'])==f.saved
   save('dependency',{'graph':p.graph,'binding':b,'predecessor':first,'dependent':second_done,'plan_state':'MONITORING','historical_draft_unchanged':True})
 asyncio.run(run())
