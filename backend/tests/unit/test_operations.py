"""Authentication/gate/state contract tests; no mocked database success."""
import pytest
from app.services.operations.auth import Auth,Denied,PERMISSIONS
from app.services.operations.models import Binding,Update
from app.services.evidence.service import transition
from app.graph.repository import PreconditionFailed
from tests.b13_fixtures import auth_setup
from pydantic import ValidationError
@pytest.fixture
def identities(tmp_path):return auth_setup(tmp_path/'auth.sqlite3')
def test_signed_sessions_expiry_logout_revocation_and_forgery(identities):
 auth,t=identities
 assert auth.resolve(t['OP-ANALYST']).role=='ANALYST'
 for forged in [t['OP-ANALYST']+'x',{'role':'APPROVER'},'OP-APPROVER',None,'A'*43+'.'+'é'*64]:
  with pytest.raises(Denied):auth.resolve(forged)
 with pytest.raises(Denied):auth.login('OP-APPROVER','incorrect')
 auth.logout(t['OP-ANALYST'])
 with pytest.raises(Denied):auth.resolve(t['OP-ANALYST'])
 auth.revoke_session(t['OP-ADMIN'],t['OP-ROAD-LEAD'])
 with pytest.raises(Denied):auth.resolve(t['OP-ROAD-LEAD'])
 auth.clock=lambda:10**12
 with pytest.raises(Denied):auth.resolve(t['OP-APPROVER'])
@pytest.mark.parametrize('operator,allowed',[('OP-ANALYST',{'draft','submit','read','inspect','evaluate','recur'}),('OP-APPROVER',{'decide','order','read'}),('OP-DRAIN-LEAD',{'read','update','progress','inspect'}),('OP-ADMIN',{'read','revoke_session'})])
def test_no_implicit_role_bypass(identities,operator,allowed):
 auth,t=identities
 for operation in PERMISSIONS:
  if operation in allowed:assert auth.require(t[operator],operation).id==operator
  else:
   with pytest.raises(Denied):auth.require(t[operator],operation)
def test_exact_scope_closed_and_canonical():
 b={'plan_id':'P','plan_version':1,'plan_hash':'a'*64,'assignments':[{'task_id':'T','action_type':'INSPECTION','target_ids':['B','A'],'department_id':'DEPT-DRAIN','assignee_id':'OP-DRAIN-LEAD'}]}
 first=Binding.model_validate(b).normalized();b['assignments'][0]['target_ids'].reverse()
 assert Binding.model_validate(b).normalized()==first
 for key,value in [('role','APPROVER'),('approved',True)]:
  with pytest.raises(ValidationError):Binding.model_validate({**b,key:value})
 b['assignments'].append(b['assignments'][0])
 with pytest.raises(ValidationError):Binding.model_validate(b)
@pytest.mark.parametrize('old,new,valid',[('AUTHORIZED','ASSIGNED',True),('AUTHORIZED','CANCELLED',True),('AUTHORIZED','COMPLETED',False),('ASSIGNED','AUTHORIZED',False),('CANCELLED','ASSIGNED',False)])
def test_work_order_state_guard_and_b14_boundary(old,new,valid):
 if valid:assert transition('WorkOrder',old,new)==new
 else:
  with pytest.raises(PreconditionFailed):transition('WorkOrder',old,new)
 with pytest.raises(ValidationError):Update(request_id='r',work_order_id='w',expected_hash='a'*64,new_status='IN_PROGRESS',reason='B13 Update remains closed; B14 uses separate Progress command')

def test_conditional_approval_is_not_execution_clearance():
 from app.services.planning.models import TaskDraft
 from app.services.operations.service import execution_gates
 from tests.b12_fixtures import sample
 v=sample()['tasks'][0];v.update(action_type='DRAIN_BLOCKAGE_CLEARANCE',remediation={'mode':'CONDITIONAL','conditions':[{'kind':'CAUSAL_INSPECTION','status':'MET','evidence_ids':['EV']},{'kind':'SAFETY_REVIEW','status':'UNMET','evidence_ids':[]}]})
 task=TaskDraft.model_validate(v)
 with pytest.raises(PreconditionFailed,match='UNMET_EXECUTION_GATES'):execution_gates(task,[])
 v['action_type']='INSPECTION';v['remediation']=None;task=TaskDraft.model_validate(v)
 with pytest.raises(PreconditionFailed,match='UNMET_TASK_DEPENDENCIES'):execution_gates(task,['APPROVED'])
 execution_gates(task,['COMPLETED'])
