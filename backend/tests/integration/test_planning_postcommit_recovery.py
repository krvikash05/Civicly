"""B12-R2 actual commit/MCP/Saver/quarantine, with an injected ACK-only mismatch."""
import asyncio,copy,json,os
from pathlib import Path
from uuid import uuid4
import pytest
from app.active import active_scope
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.models import InvestigationState
from app.agents.checkpoints import saver,RecoveryRequired
from app.agents.control import identity
from app.graph.models import digest
from app.services.evidence.reader import Reader
from app.services.planning.feedback import feedback
from tests.b10_fixtures import ScriptedModel,choose
from tests.b12_fixtures import prepared
from tests.integration.test_memory_graphrag import memory
pytestmark=pytest.mark.integration

def test_actual_postcommit_mismatch_retains_plan_and_quarantines(db,tmp_path,memory,monkeypatch):
 p,r,clock,path,inv,draft,service=prepared(db,tmp_path,memory,'WATERLOGGING')
 original_get=service.store.get;readbacks=[]
 def mismatch(id):
  saved=original_get(id);readbacks.append(id)
  damaged_ack=copy.deepcopy(saved);damaged_ack['receipt']['plan_hash']='0'*64
  return damaged_ack  # Only the acknowledgment is altered; actual stored data stays intact.
 monkeypatch.setattr(service.store,'get',mismatch)
 async def run():
  with active_scope(p):
   async with brokers(p,path,timeout=10) as tools:
    bound=Reader(r,clock()).edges('INVESTIGATES',source=inv)
    incidents=[e.target for e in bound if r.get_node(e.target).kind=='Incident']
    cluster=next(e.target for e in bound if r.get_node(e.target).kind=='ProblemCluster')
    thread=uuid4().hex;request=identity('PLANREQ',thread,2,0)
    state=InvestigationState(graph=p.graph,investigation_id=inv,thread_id=thread,problem_cluster_id=cluster,discovered_tool_names=[t['name'] for t in tools.catalog()],incident_ids=incidents,asset_ids=['D1'],issue='WATERLOGGING',graph_revision=r._read("MATCH (g:CivicSchemaMigration {id:'0001'}) RETURN g.repo_revision")[0][0],inventory_hash=tools.inventory_hash,as_of=clock(),hypotheses=[b.hypothesis_id for b in draft.basis])
    actions=[choose('READ',{'template':'node','id':'D1'},'official::query_graph_readonly'),choose('RECOMMEND',{'plan_draft':draft.model_dump(mode='json')},summary='Authored deterministic B12R2 commit verification regression')]
    agent=InvestigationAgent(p,r,tools,ScriptedModel(actions),saver(p),clock=clock,planning_service=service)
    with pytest.raises(RecoveryRequired,match='^PLAN_OPERATOR_RECOVERY_REQUIRED') as caught:await agent.run(state,thread_id=thread)
    assert str(caught.value)=='PLAN_OPERATOR_RECOVERY_REQUIRED'
    context=caught.value.reconciliation
    assert context=={'graph':p.graph,'request_id':request,'investigation_id':inv,'plan_id':readbacks[0],'expected_version':1,'expected_plan_hash':draft.content_hash,'stage':'ACKNOWLEDGMENT_VERIFICATION'}
    assert len(readbacks)==1
    assert r._read('MATCH (p:ResolutionPlan) RETURN p.id,p.version,p.plan_hash')==[[context['plan_id'],1,draft.content_hash]]
    assert r._read('MATCH (d:CivicPlanDraft) RETURN d.id,d.request_id,d.investigation_id,d.version')==[[context['plan_id'],request,inv,1]]
    # Read-only supported integrity inspection; never call create/replay/resume or clear quarantine.
    saved=original_get(context['plan_id']);assert saved['receipt']['plan_hash']==draft.content_hash and saved['request_id']==request
    before_hash=digest(saved)
    checkpoint=saver(p).get_tuple({'configurable':{'thread_id':thread}})
    durable=checkpoint.checkpoint['channel_values']['data']
    assert durable['selection']['action']=='RECOMMEND' and durable['iterations']==2 and durable['wakes']==0
    assert durable['current_plan_id'] is None and durable['planning_feedback'] is None
    assert durable['pause_reason']!='PLAN_CLARIFICATION_REQUIRED'
    assert all(o.get('operation') not in {'PLAN_DRAFT_REJECTED','PLAN_DRAFTED'} for o in durable['observations'])
    assert 'PLAN_DRAFT_REJECTED' not in durable['errors']
    selected=agent.control.selected(identity('DEC',thread,2,0))[0]
    assert selected.arguments['plan_draft']==draft.model_dump(mode='json')
    key='civicly:b10:'+p.graph+':'+digest(thread)+':quarantine'
    assert db.connection.get(key)
    diagnostic=feedback(caught.value).model_dump(mode='json')
    assert diagnostic['draft_committed']=='UNKNOWN' and diagnostic['resolution']=='OPERATOR_RECOVERY'
    assert digest(original_get(context['plan_id']))==before_hash
    assert r._read('MATCH (p:ResolutionPlan) RETURN count(p),max(p.version)')==[[1,1]]
    assert db.connection.get(key)  # Deliberately retained for explicit operator reconciliation.
    proof={'mode':'SCRIPTED_MODEL_REAL_FALKORDB_B11_MCP_LANGGRAPH_SAVER','fault':'ACK-only mismatched plan hash after real commit; stored payload never corrupted',
     'runtime_error':str(caught.value),'reconciliation':context,'thread_id':thread,'last_durable_checkpoint_id':checkpoint.config['configurable']['checkpoint_id'],
     'last_durable_current_plan_id':durable['current_plan_id'],'last_durable_planning_feedback':durable['planning_feedback'],
     'false_rejection_emitted':False,'safe_receipt_emitted':False,'operator_diagnostic_not_checkpoint_ack':diagnostic,
     'stored_receipt_read_only_verified':saved['receipt'],'stored_request_id':saved['request_id'],'stored_payload_unchanged_sha256':before_hash,
     'plan_count':1,'maximum_version':1,'quarantine_retained':True,'wake_retry_or_replay_performed':False,'provider_calls':0,
     'remaining_operator_steps':'Stop old process/confirm ownership; inspect original request, decision, companion/hash/native plan and pending write; reconcile last checkpoint via existing reviewed recovery procedure. No automatic reset or quarantine clearance.'}
    Path('docs/evidence/'+os.environ.get('CIVICLY_PLANNING_EVIDENCE_PREFIX','B12R2')+'-postcommit-recovery.json').write_text(json.dumps(proof,indent=2)+'\n')
 asyncio.run(run())
