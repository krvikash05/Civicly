"""B20 closed-boundary tests. No mock successes or live model reasoning claims."""
import copy
import pytest
from app.services.evidence.models import parse_command
from app.services.planning.models import PlanDraft,TaskDraft
from app.services.evidence.policies import classify_reviewed
from tests.b12_fixtures import sample

@pytest.mark.parametrize('action',['UTILITY_REPAIR','CAPACITY_UPGRADE','ROUTE_REDESIGN','DUMPING_ENFORCEMENT'])
def test_unsupported_interventions_remain_closed(action):
 value=sample()['tasks'][0];value['action_type']=action
 with pytest.raises(ValueError):TaskDraft.model_validate(value)

@pytest.mark.parametrize('claimed',['VERIFIED','SUPPORTED','CONTRADICTED'])
def test_caller_cannot_force_diagnosis_status(claimed):
 with pytest.raises(ValueError):parse_command({'operation':'assess','request_id':'B20-forced','hypothesis_id':'H','expected_hash':'a'*64,'as_of':'2026-10-18T12:00:00Z','assessment':claimed})

@pytest.mark.parametrize('mutation',['cycle','unknown_dependency','no_safety','fake_resolution'])
def test_invalid_plan_or_resolution_fails_at_strict_boundary(mutation):
 value=sample()
 if mutation=='cycle':value['tasks'][0]['depends_on']=['inspect']
 if mutation=='unknown_dependency':value['tasks'][0]['depends_on']=['absent']
 if mutation=='no_safety':value['tasks'][0].update(action_type='DRAIN_BLOCKAGE_CLEARANCE',remediation={'mode':'SUPPORTED_NOW','conditions':[{'kind':'CAUSAL_INSPECTION','status':'MET','evidence_ids':['EV']}]})
 if mutation=='fake_resolution':value['monitoring']['completion_implies_resolution']=True
 with pytest.raises(ValueError):PlanDraft.model_validate(value)

@pytest.mark.parametrize('reviewed_support,unreviewed_support,reviewed_contradiction,expected',[(False,True,True,'INCONCLUSIVE'),(False,False,True,'CONTRADICTED'),(True,False,False,'SUPPORTED')])
def test_source_authority_never_promotes_single_report_to_verified(reviewed_support,unreviewed_support,reviewed_contradiction,expected):
 assert classify_reviewed(reviewed_support=reviewed_support,unreviewed_support=unreviewed_support,reviewed_contradiction=reviewed_contradiction,unreviewed_contradiction=False,sufficient=False)==expected
