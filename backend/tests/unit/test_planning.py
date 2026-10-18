"""Closed drafts/DAG/hash/monitoring and legacy state compatibility, no mock DB proof."""
import copy,json
import pytest
from pydantic import ValidationError
from app.services.planning.models import PlanDraft
from app.agents.models import InvestigationState
from tests.b12_fixtures import sample,REQUIRED
@pytest.mark.parametrize('damage',['self','cycle','unknown','duplicate','unknown_field','missing_outcome','foreign_evidence','monitoring','missing_alternative','version'])
def test_rejects_invalid_draft_semantics(damage):
 value=sample();task=value['tasks'][0]
 if damage=='self':task['depends_on']=['inspect']
 if damage=='cycle':
  other=copy.deepcopy(task);other['id']='second';other['depends_on']=['inspect'];task['depends_on']=['second'];value['tasks'].append(other)
 if damage=='unknown':task['depends_on']=['missing']
 if damage=='duplicate':value['tasks'].append(copy.deepcopy(task))
 if damage=='unknown_field':task['estimated_cost']=42
 if damage=='missing_outcome':del task['expected_outcome']
 if damage=='foreign_evidence':task['evidence_ids']=['foreign']
 if damage=='monitoring':value['monitoring']['required_evidence']=['FOLLOWUP_PAVEMENT','WEAR_EXPOSURE']
 if damage=='missing_alternative':value['basis'][1]['addressed']=True
 if damage=='version':value['version']=2
 with pytest.raises(ValidationError):PlanDraft.model_validate(value)
@pytest.mark.parametrize('issue',list(REQUIRED))
def test_issue_specific_monitoring_and_no_execution_authority(issue):
 value=sample();value['issue']=value['monitoring']['issue']=issue;value['monitoring']['required_evidence']=REQUIRED[issue]
 draft=PlanDraft.model_validate(value);assert draft.monitoring.missing_opportunity=='UNRESOLVED' and draft.monitoring.completion_implies_resolution is False
 value['monitoring']['completion_implies_resolution']=True
 with pytest.raises(ValidationError):PlanDraft.model_validate(value)
def test_hash_stable_ordering_and_changed_semantics_bound():
 value=sample();first=PlanDraft.model_validate(value);value['basis'].reverse()
 assert PlanDraft.model_validate(value).content_hash==first.content_hash
 value['tasks'][0]['expected_outcome']='Changed outcome needing separate review';assert PlanDraft.model_validate(value).content_hash!=first.content_hash
 value['version']=2;value['previous_plan_id']='PLAN1';assert PlanDraft.model_validate(value).content_hash!=first.content_hash

def test_current_prompt_closed_plan_schema_and_historical_state_defaults():
 from app.agents.provider import PROMPT,PROMPT_VERSION
 from app.agents.runtime import InvestigationAgent
 assert PROMPT_VERSION=='B12-1' and '{plan_draft:' in PROMPT and 'competing explanations' in PROMPT and 'No municipal execution or approval' in PROMPT
 assert InvestigationAgent.action_schemas()['RECOMMEND']['properties']['plan_draft']==PlanDraft.model_json_schema()
 state=InvestigationState(graph='g',investigation_id='INV',thread_id='T',problem_cluster_id='PC',incident_ids=['I'],asset_ids=['D'],issue='WATERLOGGING',graph_revision=0,inventory_hash='h',as_of='2026-10-18T00:00:00Z',recommendation={'binding':False})
 assert state.current_plan_id is None and state.current_plan_version is None and state.recommendation=={'binding':False}
