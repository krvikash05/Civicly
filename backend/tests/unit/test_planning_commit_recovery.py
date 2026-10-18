"""B12-R2 pure fault classification; no database success claimed by these tests."""
import asyncio,json
from types import SimpleNamespace
import pytest
from pydantic import ValidationError
from app.services.planning.service import PlanRecoveryRequired,PlanningBlocked,PlanningService
from app.services.planning.feedback import feedback
from app.services.planning.models import PlanDraft,PlanReceipt
from app.services.evidence.models import Actor
from app.agents.checkpoints import RecoveryRequired
from app.agents.models import InvestigationState,Selection
from app.agents.runtime import InvestigationAgent
from tests.b12_fixtures import sample

def failure(stage='ACKNOWLEDGMENT_VERIFICATION'):
 return PlanRecoveryRequired(graph='civicly_b10_test_'+'a'*32,request_id='request-original',investigation_id='INV',plan_id='PLAN-original',version=1,plan_hash='a'*64,stage=stage)

@pytest.mark.parametrize('error',[failure(),PlanningBlocked('PLAN_READBACK')])
def test_commit_verification_never_reports_uncommitted(error):
 f=feedback(error)
 assert f.draft_committed=='UNKNOWN' and f.resolution=='OPERATOR_RECOVERY' and f.category=='RECOVERY'
 assert not f.task_ids and not f.field_paths

def test_prewrite_validation_stays_actionable_and_uncommitted():
 f=feedback(PlanningBlocked('OWNERSHIP_UNKNOWN_OR_CONFLICTING',task_id='inspect'))
 assert f.draft_committed=='NO' and f.category=='OWNERSHIP' and f.task_ids==['inspect']
 v=sample();v['tasks'][0]['action_type']='PASSWORD=DO_NOT_ECHO'
 with pytest.raises(ValidationError) as caught:PlanDraft.model_validate(v)
 f=feedback(caught.value)
 assert f.draft_committed=='NO' and f.code=='PLAN_ACTION_UNSUPPORTED' and 'PASSWORD' not in f.model_dump_json()

def test_runtime_preserves_reconciliation_identity_without_rejection():
 error=failure()
 class FailedService:
  async def create(self,*args,**kwargs):raise error
 state=InvestigationState(graph='g',investigation_id='INV',thread_id='T',problem_cluster_id='PC',incident_ids=['I'],asset_ids=['D1'],issue='WATERLOGGING',graph_revision=0,inventory_hash='h',as_of='2026-10-18T00:00:00Z',selection=Selection(action='RECOMMEND',summary='Authored test proposal',tool_name='',arguments_json=json.dumps({'plan_draft':sample()}),pause_reason='NONE'))
 agent=object.__new__(InvestigationAgent);agent.decode=lambda channel:state;agent.planning_service=FailedService();agent.check=lambda:None
 with pytest.raises(RecoveryRequired,match='^PLAN_OPERATOR_RECOVERY_REQUIRED$') as caught:asyncio.run(agent.planner({}))
 assert caught.value.reconciliation==error.reconciliation
 assert state.current_plan_id is None and not state.observations and state.planning_feedback is None

@pytest.mark.parametrize('shape',['pydantic','missing'])
def test_saved_replay_verification_fault_is_recovery(shape):
 """Stub only the existing-row read to test adjacent pre-return classification."""
 from contextlib import nullcontext
 v=sample();draft=PlanDraft.model_validate(v)
 class BrokenStore:
  def get(self,id):
   if shape=='missing':return None
   # Represents storage corruption/validation, not an invalid incoming model draft.
   return {'receipt':{'credential':'DO_NOT_ECHO'}}
 service=object.__new__(PlanningService);service.repo=SimpleNamespace(graph=SimpleNamespace(name='civicly_b10_test_'+'a'*32),_session=lambda:nullcontext(None),_read=lambda *args:[['PLAN-original']]);service.store=BrokenStore();service.clock=lambda:'2026-10-18T12:00:00Z'
 with pytest.raises(PlanRecoveryRequired) as caught:asyncio.run(service.create(draft,request_id='request-original',actor=Actor(id='analyst',role='ANALYST')))
 assert caught.value.reconciliation['plan_id']=='PLAN-original' and caught.value.reconciliation['stage']=='REPLAY_VERIFICATION'
 assert 'DO_NOT_ECHO' not in str(caught.value) and feedback(caught.value).draft_committed=='UNKNOWN'
