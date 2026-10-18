"""B13 real isolated DB/B11/native lifecycle/audit; no providers or field execution."""
import asyncio,copy,json,os,subprocess
from pathlib import Path
import pytest
from app.active import active_scope
from app.graph.repository import Conflict,PreconditionFailed
from app.services.operations.auth import Denied
from app.services.operations.models import OpsRecovery
from app.services.planning.service import PlanningBlocked
from tests.b13_fixtures import setup,binding
from tests.integration.test_memory_graphrag import memory
pytestmark=pytest.mark.integration
async def approved(ops,planning,draft,tokens,tag='base'):
 receipt=await ops.draft(draft,request_id=tag+'-draft',token=tokens['OP-ANALYST']);saved=planning.store.get(receipt.id);b=binding(saved)
 pending=await ops.execute({**b,'operation':'submit','request_id':tag+'-submit'},token=tokens['OP-ANALYST'])
 approved=await ops.execute({**b,'operation':'decide','request_id':tag+'-approve','approval_id':pending['id'],'expected_hash':pending['expected_hash'],'decision':'APPROVED','reason':'Synthetic human review of exact scope, guards and source reservations'},token=tokens['OP-APPROVER'])
 return b,saved,pending,approved

def test_actual_approval_order_scope_idempotency_and_competing_updates(db,tmp_path,memory):
 p,r,clock,path,inv,draft,planning,auth,tokens,ops=setup(db,tmp_path,memory)
 async def run():
  with active_scope(p):
   original_orders=r._read('MATCH (w:WorkOrder) RETURN count(w)')[0][0]
   b,saved,pending,decision=await approved(ops,planning,draft,tokens)
   assert planning.store.get(b['plan_id'])==saved # Historical draft receipt/bytes remain unchanged.
   assert r.get_node(b['plan_id']).properties['status']=='APPROVED'
   command={**b,'operation':'order','request_id':'order-original','approval_id':decision['id'],'task_id':b['assignments'][0]['task_id']}
   for operator in ['OP-ANALYST','OP-DRAIN-LEAD','OP-ADMIN']:
    with pytest.raises(Denied):await ops.execute(command,token=tokens[operator])
   with pytest.raises(Denied):await ops.execute(command,token={'role':'APPROVER'})
   wrong=copy.deepcopy(command);wrong['assignments'][0]['assignee_id']='OP-ROAD-LEAD'
   with pytest.raises(Denied):await ops.execute(wrong,token=tokens['OP-APPROVER'])
   wrong=copy.deepcopy(command);wrong['assignments'][0]['target_ids']=['D2']
   with pytest.raises(PreconditionFailed):await ops.execute(wrong,token=tokens['OP-APPROVER'])
   order=await ops.execute(command,token=tokens['OP-APPROVER']);assert order['status']=='AUTHORIZED'
   assert await ops.execute(command,token=tokens['OP-APPROVER'])==order
   assert await ops.execute({**command,'request_id':'same-task-other-request'},token=tokens['OP-APPROVER'])==order
   changed=copy.deepcopy(command);changed['plan_hash']='0'*64
   with pytest.raises(Conflict):await ops.execute(changed,token=tokens['OP-APPROVER'])
   with pytest.raises(Denied):ops.read_work_order(order['id'],token=tokens['OP-ROAD-LEAD'])
   assert ops.read_work_order(order['id'],token=tokens['OP-DRAIN-LEAD'])['native']['status']=='AUTHORIZED'
   bad_update={'operation':'update','request_id':'wrong-department-update','work_order_id':order['id'],'expected_hash':order['expected_hash'],'new_status':'ASSIGNED','reason':'Must reject wrong department'}
   with pytest.raises(Denied):await ops.execute(bad_update,token=tokens['OP-ROAD-LEAD'])
   async def update(key):
    try:return await asyncio.to_thread(lambda:asyncio.run(ops.execute({'operation':'update','request_id':key,'work_order_id':order['id'],'expected_hash':order['expected_hash'],'new_status':'ASSIGNED','reason':'Authenticated synthetic assignment only; no execution'},token=tokens['OP-DRAIN-LEAD'])))
    except Conflict:return 'STALE'
   race=await asyncio.gather(update('race-left'),update('race-right'))
   assert sum(v=='STALE' for v in race)==1 and sum(isinstance(v,dict) for v in race)==1
   assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[original_orders+1]]
   assert r._read('MATCH (:WorkOrder {id:$id})-[:AUTHORIZED_BY]->(:Approval) RETURN count(*)',{'id':order['id']})==[[1]]
   assert r._read('MATCH (:WorkOrder {id:$id})-[:HAS_EVENT]->(:StatusEvent) RETURN count(*)',{'id':order['id']})==[[1]]
   out=tmp_path/'fresh.json'
   process=subprocess.run([str(Path('backend/.venv/bin/python').absolute()),'-m','tests.b13_worker',str(path),order['id'],str(out)],env={**os.environ,'PYTHONPATH':str(Path('backend').absolute())},input=json.dumps({'auth_path':str(auth.path),'token':tokens['OP-DRAIN-LEAD']}).encode(),capture_output=True,timeout=30)
   assert process.returncode==0,process.stderr.decode()[-500:]
   fresh=json.loads(out.read_text());assert fresh['order']['native']['status']=='ASSIGNED' and fresh['events']
   assert fresh['authenticated_operator']['id']=='OP-DRAIN-LEAD'
   Path('docs/evidence/B13-flow.json').write_text(json.dumps({'graph':p.graph,'binding':b,'pending':pending,'decision':decision,'order':order,'competing_updates':race,'fresh_process':fresh,'provider_calls':0,'no_execution':True},indent=2)+'\n')
 asyncio.run(run())

def test_actual_stale_sources_assessments_owners_supersession_and_rejection(db,tmp_path,memory):
 p,r,clock,path,inv,draft,planning,auth,tokens,ops=setup(db,tmp_path,memory)
 async def run():
  with active_scope(p):
   receipt=await ops.draft(draft,request_id='draft',token=tokens['OP-ANALYST']);saved=planning.store.get(receipt.id);b=binding(saved)
   pending=await ops.execute({**b,'operation':'submit','request_id':'submit'},token=tokens['OP-ANALYST'])
   cmd={**b,'operation':'decide','request_id':'decide','approval_id':pending['id'],'expected_hash':pending['expected_hash'],'decision':'APPROVED','reason':'Synthetic review'}
   for operator in ['OP-ANALYST','OP-DRAIN-LEAD','OP-ADMIN']:
    with pytest.raises(Denied):await ops.execute(cmd,token=tokens[operator])
   owner=r.get_relationship('B12-OWNER-D1');r.update_relationship(owner.id,{'association_status':'CANDIDATE'},expected_hash=owner.content_hash)
   with pytest.raises(PlanningBlocked,match='OWNERSHIP'):await ops.execute(cmd,token=tokens['OP-APPROVER'])
   owner=r.get_relationship(owner.id);r.update_relationship(owner.id,{'association_status':'VERIFIED'},expected_hash=owner.content_hash)
   from tests.b09_fixtures import Fixture,assess
   f=Fixture(r,clock,{},p.graph,{})
   assess(f,draft.basis[0].hypothesis_id,ref='B13-new-current-assessment')
   with pytest.raises(PreconditionFailed,match='ASSESSMENT_STALE'):await ops.execute(cmd,token=tokens['OP-APPROVER'])
   from app.services.evidence.reader import Reader
   updated=draft.model_dump(mode='json');updated.update(version=2,previous_plan_id=receipt.id)
   updated['basis'][0]['assessment_id']=Reader(r,clock()).histories(draft.basis[0].hypothesis_id)[-1].id
   updated['tasks'][0]['assessment_ids']=[b['assessment_id'] for b in updated['basis']]
   # Current version still cites original source: revoke it, and approval must fail closed.
   source=memory.store.get(draft.tasks[0].procedure_citation.canonical_document_id)[0]
   memory.store.revoke(source.id,operator='synthetic-source-curator',reason='B13 scoped revocation test')
   with pytest.raises(PlanningBlocked,match='PROCEDURE_STALE'):await ops.draft(updated,request_id='revoked-draft',token=tokens['OP-ANALYST'])
   from app.memory.models import Source
   newsource=Source.model_validate({**source.model_dump(),'version':2,'supersedes':1,'status':'ACTIVE','effective_from':'2026-10-18T00:00:00Z'})
   await memory.ingest(newsource);updated['tasks'][0]['procedure_citation']=(await memory.retrieve(as_of=clock(),document_id=source.document_id))['citations'][0]
   second=await ops.draft(updated,request_id='new-version',token=tokens['OP-ANALYST']);second_saved=planning.store.get(second.id);b2=binding(second_saved)
   second_pending=await ops.execute({**b2,'operation':'submit','request_id':'submit2'},token=tokens['OP-ANALYST'])
   assert r.get_node(receipt.id).properties['status']=='SUPERSEDED' and planning.store.get(receipt.id)==saved
   with pytest.raises(PreconditionFailed,match='PLAN_SUPERSEDED'):await ops.execute(cmd,token=tokens['OP-APPROVER'])
   current_source=memory.store.get(newsource.id)[0]
   memory.store.revoke(current_source.id,operator='synthetic-source-curator',reason='B13 revoke pending approval source')
   approve2={**b2,'operation':'decide','request_id':'invalid-source-approve2','approval_id':second_pending['id'],'expected_hash':second_pending['expected_hash'],'decision':'APPROVED','reason':'Must be denied on revoked source'}
   with pytest.raises(PlanningBlocked,match='PROCEDURE_STALE'):await ops.execute(approve2,token=tokens['OP-APPROVER'])
   rejected=await ops.execute({**b2,'operation':'decide','request_id':'reject2','approval_id':second_pending['id'],'expected_hash':second_pending['expected_hash'],'decision':'REJECTED','reason':'Synthetic approver rejects proposal scope; retain reason'},token=tokens['OP-APPROVER'])
   assert rejected['status']=='REJECTED' and ops.store.get('approval',rejected['id'])['reason'].startswith('Synthetic approver rejects')
   assert planning.store.get(second.id)==second_saved
   Path('docs/evidence/B13-denials.json').write_text(json.dumps({'graph':p.graph,'unauthorized_roles_denied':True,'candidate_owner_denied':True,'stale_assessment_denied':True,'revoked_source_denied':True,'superseded_plan_denied':True,'rejection':rejected,'old_receipt_immutable':True,'procedure_status':memory.repo.get_node(newsource.id.replace('ORG:','ORGPROC:'),'KnowledgeProcedure').properties['status']},indent=2)+'\n')
 asyncio.run(run())

def test_actual_ack_loss_order_replay_without_duplicate(db,tmp_path,memory):
 p,r,clock,path,inv,draft,planning,auth,tokens,ops=setup(db,tmp_path,memory)
 async def run():
  with active_scope(p):
   b,saved,pending,decision=await approved(ops,planning,draft,tokens,'ack')
   cmd={**b,'operation':'order','request_id':'ack-original','approval_id':decision['id'],'task_id':b['assignments'][0]['task_id']}
   with pytest.raises(OpsRecovery) as caught:await ops.execute(cmd,token=tokens['OP-APPROVER'],interrupt='after_commit')
   identity=caught.value.reconciliation
   assert identity['request_id']=='ack-original' and identity['commitment']=='UNKNOWN'
   assert r._read('MATCH (:WorkOrder)-[:AUTHORIZED_BY]->(:Approval {id:$id}) RETURN count(*)',{'id':decision['id']})==[[1]]
   result=await ops.execute(cmd,token=tokens['OP-APPROVER']);assert result['id']==identity['entity_id']
   assert await ops.execute(cmd,token=tokens['OP-APPROVER'])==result
   assert r._read('MATCH (:WorkOrder)-[:AUTHORIZED_BY]->(:Approval {id:$id}) RETURN count(*)',{'id':decision['id']})==[[1]]
   Path('docs/evidence/B13-ack-recovery.json').write_text(json.dumps({'graph':p.graph,'recovery':identity,'same_request_replayed':True,'receipt':result,'order_count_for_approval':1,'automatic_retry':False,'false_rejection':False,'provider_calls':0},indent=2)+'\n')
 asyncio.run(run())

def test_actual_conditional_approval_retains_unmet_gate_no_order(db,tmp_path,memory):
 from tests.b12_fixtures import prepared
 from tests.b13_fixtures import auth_setup
 from app.services.operations.migration import OperationsMigration
 from app.services.operations.service import Operations
 p,r,clock,path,inv,draft,planning=prepared(db,tmp_path,memory,'WATERLOGGING',remedial=True)
 auth,tokens=auth_setup(tmp_path/'auth.sqlite3');OperationsMigration(db,p.graph).apply();ops=Operations(planning,auth,clock=clock)
 value=draft.model_dump(mode='json');value['tasks'][0]['remediation']['mode']='CONDITIONAL'
 value['tasks'][0]['remediation']['conditions'][1].update(status='UNMET',evidence_ids=[])
 async def run():
  with active_scope(p):
   before=r._read('MATCH (w:WorkOrder) RETURN count(w)')[0][0]
   b,saved,pending,decision=await approved(ops,planning,value,tokens,'conditional')
   cmd={**b,'operation':'order','request_id':'conditional-block','approval_id':decision['id'],'task_id':b['assignments'][0]['task_id']}
   with pytest.raises(PreconditionFailed,match='UNMET_EXECUTION_GATES'):await ops.execute(cmd,token=tokens['OP-APPROVER'])
   assert planning.store.get(b['plan_id'])==saved and saved['draft']['tasks'][0]['remediation']['conditions'][1]['status']=='UNMET'
   assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[before]]
   Path('docs/evidence/B13-conditional.json').write_text(json.dumps({'graph':p.graph,'binding':b,'decision':decision,'unmet_conditions_preserved':True,'order_creation_denied':True,'work_order_delta':0,'no_field_execution':True,'provider_calls':0},indent=2)+'\n')
 asyncio.run(run())

def test_actual_b12_checkpoint_survives_approval_and_rejects_native_rollback(db,tmp_path,memory):
 from uuid import uuid4
 from app.agents.models import InvestigationState
 from app.agents.mcp import brokers
 from app.agents.runtime import InvestigationAgent
 from app.agents.checkpoints import saver
 from app.services.evidence.reader import Reader
 from tests.b10_fixtures import ScriptedModel,choose
 p,r,clock,path,inv,draft,planning,auth,tokens,ops=setup(db,tmp_path,memory)
 async def run():
  with active_scope(p):
   receipt=await ops.draft(draft,request_id='checkpoint-draft',token=tokens['OP-ANALYST']);saved=planning.store.get(receipt.id);b=binding(saved)
   async with brokers(p,path,timeout=10) as tools:
    bound=Reader(r,clock()).edges('INVESTIGATES',source=inv);thread=uuid4().hex
    state=InvestigationState(graph=p.graph,investigation_id=inv,thread_id=thread,problem_cluster_id=next(e.target for e in bound if r.get_node(e.target).kind=='ProblemCluster'),incident_ids=[e.target for e in bound if r.get_node(e.target).kind=='Incident'],asset_ids=['D1'],issue='WATERLOGGING',graph_revision=0,inventory_hash=tools.inventory_hash,as_of=clock(),hypotheses=[v.hypothesis_id for v in draft.basis],current_plan_id=receipt.id,current_plan_version=receipt.version,current_plan_hash=receipt.plan_hash)
    agent=InvestigationAgent(p,r,tools,ScriptedModel([choose()]),saver(p),clock=clock,planning_service=planning)
    result=await agent.run(state,thread_id=thread);assert result['__interrupt__']
    before=await agent.graph.aget_state({'configurable':{'thread_id':thread}})
    pending=await ops.execute({**b,'operation':'submit','request_id':'checkpoint-submit'},token=tokens['OP-ANALYST'])
    decision=await ops.execute({**b,'operation':'decide','request_id':'checkpoint-approve','approval_id':pending['id'],'expected_hash':pending['expected_hash'],'decision':'APPROVED','reason':'Synthetic exact-plan review'},token=tokens['OP-APPROVER'])
    after=await agent.graph.aget_state({'configurable':{'thread_id':thread}})
    assert before.config==after.config and before.values==after.values
    from app.agents.checkpoints import ownership
    async with ownership(db,p,thread) as check:
     agent.check=check
     assert agent.decode(after.values).current_plan_hash==receipt.plan_hash and planning.store.get(receipt.id)==saved
    native=r.get_node(receipt.id);r.update_node(native.id,{'status':'DRAFT'},expected_hash=native.content_hash)
    with pytest.raises(PreconditionFailed,match='LIFECYCLE_INTEGRITY'):planning.store.get(native.id)
    native=r.get_node(native.id);r.update_node(native.id,{'status':'APPROVED'},expected_hash=native.content_hash)
    async with ownership(db,p,thread) as check:
     agent.check=check
     assert agent.decode(after.values).current_plan_id==receipt.id
    Path('docs/evidence/B13-checkpoint-compatibility.json').write_text(json.dumps({'graph':p.graph,'thread_id':thread,'checkpoint_id':after.config['configurable']['checkpoint_id'],'historical_receipt':receipt.model_dump(mode='json'),'current_decision':decision,'saved_checkpoint_unchanged':True,'native_rollback_rejected':True,'model':'SCRIPTED_PAUSE_REAL_MCP_SAVER','provider_calls':0},indent=2)+'\n')
 asyncio.run(run())

def test_accepted_road_water_dag_approval_and_dependency_boundary(db,tmp_path,memory):
 from tests.b12_fixtures import prepared
 from tests.b13_fixtures import auth_setup
 from app.services.operations.migration import OperationsMigration
 from app.services.operations.service import Operations
 p,r,clock,path,inv,draft,planning=prepared(db,tmp_path,memory,'ROAD_DAMAGE')
 auth,tokens=auth_setup(tmp_path/'auth.sqlite3');OperationsMigration(db,p.graph).apply();ops=Operations(planning,auth,clock=clock)
 async def run():
  with active_scope(p):
   b,saved,pending,decision=await approved(ops,planning,draft,tokens,'road-water')
   assert {a['assignee_id'] for a in b['assignments']}=={'OP-ROAD-LEAD','OP-WATER-LEAD'}
   first=next(a for a in b['assignments'] if a['department_id']=='DEPT-ROAD');second=next(a for a in b['assignments'] if a['department_id']=='DEPT-WATER')
   order=await ops.execute({**b,'operation':'order','request_id':'road-inspection-order','approval_id':decision['id'],'task_id':first['task_id']},token=tokens['OP-APPROVER'])
   with pytest.raises(PreconditionFailed,match='UNMET_TASK_DEPENDENCIES'):await ops.execute({**b,'operation':'order','request_id':'blocked-water-order','approval_id':decision['id'],'task_id':second['task_id']},token=tokens['OP-APPROVER'])
   with pytest.raises(Denied):ops.read_work_order(order['id'],token=tokens['OP-WATER-LEAD'])
   assert planning.store.get(b['plan_id'])==saved
   Path('docs/evidence/B13-road-water.json').write_text(json.dumps({'graph':p.graph,'binding':b,'decision':decision,'road_order':order,'water_dependency_blocked':True,'cross_department_access_denied':True,'b12_dag_unchanged':True,'provider_calls':0},indent=2)+'\n')
 asyncio.run(run())
