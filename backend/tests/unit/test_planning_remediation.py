"""New closed guards/feedback; pure contract tests, no database success claimed."""
import copy,json
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.services.planning.models import PlanDraft
from app.services.planning.feedback import feedback
from app.services.planning.service import PlanningBlocked
from app.graph.migration import MigrationError
from app.graph.repository import OutcomeUnknown
from app.agents.checkpoints import RecoveryRequired
from tests.b12_fixtures import sample
@pytest.mark.parametrize('damage',['unsupported','text_only','met_without_evidence','conditional_all_met','missing_safety','foreign_gate_evidence'])
def test_closed_remedial_prerequisite_contract(damage):
 v=sample();t=v['tasks'][0];t['action_type']='DRAIN_BLOCKAGE_CLEARANCE'
 t['remediation']={'mode':'SUPPORTED_NOW','conditions':[{'kind':k,'status':'MET','evidence_ids':['EV']} for k in ['CAUSAL_INSPECTION','SAFETY_REVIEW']]}
 if damage=='unsupported':t['action_type']='ARBITRARY_REPAIR'
 if damage=='text_only':t.pop('remediation');t['prerequisites']=['subject to inspection']
 if damage=='met_without_evidence':t['remediation']['conditions'][0]['evidence_ids']=[]
 if damage=='conditional_all_met':t['remediation']['mode']='CONDITIONAL'
 if damage=='missing_safety':t['remediation']['conditions'][1]['kind']='CAUSAL_INSPECTION'
 if damage=='foreign_gate_evidence':t['remediation']['conditions'][0]['evidence_ids']=['FOREIGN']
 with pytest.raises(ValidationError) as caught:PlanDraft.model_validate(v)
 f=feedback(caught.value);assert f.resolution=='DRAFT_CLARIFICATION' and f.category in {'ACTION','PREREQUISITE'}
 assert 'subject to inspection' not in f.model_dump_json()
@pytest.mark.parametrize('error,category,resolution',[
 (PlanningBlocked('OWNERSHIP_UNKNOWN_OR_CONFLICTING',task_id='repair'), 'OWNERSHIP','MISSING_EVIDENCE_OR_CAPABILITY'),
 (PlanningBlocked('PROCEDURE_STALE_REVOKED_OR_UNAVAILABLE'),'SOURCE','MISSING_EVIDENCE_OR_CAPABILITY'),
 (PlanningBlocked('REMEDIAL_EVIDENCE_INSUFFICIENT'),'EVIDENCE','MISSING_EVIDENCE_OR_CAPABILITY'),
 (MigrationError('PASSWORD=must-never-appear'),'DEPENDENCY','OPERATOR_RECOVERY'),
 (OutcomeUnknown('PASSWORD=must-never-appear'),'RECOVERY','OPERATOR_RECOVERY'),
 (RecoveryRequired('PASSWORD=must-never-appear'),'RECOVERY','OPERATOR_RECOVERY'),
 (OSError('PASSWORD=must-never-appear'),'RECOVERY','OPERATOR_RECOVERY'),
])
def test_static_feedback_redaction_and_recovery(error,category,resolution):
 f=feedback(error);assert f.category==category and f.resolution==resolution
 assert 'PASSWORD' not in f.model_dump_json() and 'must-never-appear' not in f.model_dump_json()
 if category=='RECOVERY':assert f.draft_committed=='UNKNOWN'
def test_unknown_property_names_are_not_echoed_and_old_hashes_survive():
 v=sample();v['tasks'][0]['SECRET_PASSWORD_name']='sensitive body'
 with pytest.raises(ValidationError) as caught:PlanDraft.model_validate(v)
 f=feedback(caught.value);assert f.field_paths==['tasks.0'] and 'SECRET' not in f.model_dump_json()
 for path in Path('docs/evidence').glob('B12-*-draft.json'):
  body=json.loads(path.read_text())['saved'];assert PlanDraft.model_validate(body['draft']).content_hash==body['receipt']['plan_hash']

@pytest.mark.parametrize('error',[OutcomeUnknown('PASSWORD=uncertain'),RecoveryRequired('PASSWORD=lost-lease'),OSError('PASSWORD=storage-fault')])
def test_planner_does_not_acknowledge_unsafe_failures_as_rejected(error):
 """Deliberate unit fault injection; no checkpoint/database success claimed."""
 import asyncio
 from app.agents.models import InvestigationState,Selection
 from app.agents.runtime import InvestigationAgent
 class FailedService:
  async def create(self,*args,**kwargs):raise error
 state=InvestigationState(graph='g',investigation_id='INV',thread_id='T',problem_cluster_id='PC',incident_ids=['I'],asset_ids=['D1'],issue='WATERLOGGING',graph_revision=0,inventory_hash='h',as_of='2026-10-18T00:00:00Z',selection=Selection(action='RECOMMEND',summary='Authored test draft',tool_name='',arguments_json=json.dumps({'plan_draft':sample()}),pause_reason='NONE'))
 agent=object.__new__(InvestigationAgent);agent.decode=lambda c:state;agent.planning_service=FailedService();agent.check=lambda:None
 with pytest.raises(RecoveryRequired,match='^PLAN_OPERATOR_RECOVERY_REQUIRED$') as caught:asyncio.run(agent.planner({}))
 assert 'PASSWORD' not in str(caught.value) and state.planning_feedback is None and not state.errors and not state.observations
