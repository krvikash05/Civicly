"""Read-only exact task scope and synthetic assignee projection."""
import copy
from types import SimpleNamespace as N
import pytest
from app.services.http.plan_bindings import task_bindings
from app.graph.repository import PreconditionFailed
from app.services.operations.auth import Denied


def fixture():
 saved={'draft':{'tasks':[{'id':'local','action_type':'INSPECTION','target_ids':['D1'],'department_id':'DEPT-DRAIN','depends_on':[]}]},'task_ids':{'local':'native'},'receipt':{'id':'PLAN'}}
 links={('HAS_TASK','PLAN'):['native'],('ASSIGNED_TO','native'):['DEPT-DRAIN'],('TARGETS','native'):['D1'],('DEPENDS_ON','native'):[]}
 node=N(id='native',properties={'action_type':'INSPECTION','status':'PROPOSED'},content_hash='a'*64)
 ops=N(repo=N(get_node=lambda *a:node),projection=lambda kind,id:links[(kind,id)],auth=N(operator=lambda id:N(role='DEPARTMENT_LEAD',department_id='DEPT-DRAIN')))
 return ops,saved,links,node


def test_exact_server_mapping_preserves_draft_and_is_not_authority():
 ops,saved,_,_=fixture();old=copy.deepcopy(saved)
 rows=task_bindings(ops,saved)
 assert saved==old and rows[0]['local_task_id']=='local' and rows[0]['task_id']=='native'
 assert rows[0]['eligible_assignee_ids']==['OP-DRAIN-LEAD'] and rows[0]['status']=='PROPOSED'
 assert 'approved' not in rows[0]

@pytest.mark.parametrize('kind',['HAS_TASK','ASSIGNED_TO','TARGETS','DEPENDS_ON'])
def test_native_scope_drift_fails_closed(kind):
 ops,saved,links,_=fixture();links[(kind,'PLAN' if kind=='HAS_TASK' else 'native')]=['WRONG']
 with pytest.raises(PreconditionFailed,match='PLAN_TASK_BINDING_INTEGRITY'):task_bindings(ops,saved)


def test_action_or_map_tampering_fails_closed():
 ops,saved,_,node=fixture();node.properties['action_type']='OTHER'
 with pytest.raises(PreconditionFailed):task_bindings(ops,saved)
 saved['task_ids']={'other':'native'}
 with pytest.raises(PreconditionFailed):task_bindings(ops,saved)


def test_disabled_assignee_is_not_offered():
 ops,saved,_,_=fixture()
 def denied(id):raise Denied('AUTHENTICATION_REQUIRED')
 ops.auth.operator=denied
 assert task_bindings(ops,saved)[0]['eligible_assignee_ids']==[]
