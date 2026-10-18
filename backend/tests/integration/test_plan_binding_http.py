"""Real sourced plan -> HTTP task bindings -> exact pending approval; no live LLM."""
import asyncio
import pytest
from fastapi.testclient import TestClient
from app.active import active_scope
from app.api.application import create_app
from app.events.service import Delivery
from app.services.http.service import Services
from tests.b13_fixtures import setup
from tests.integration.test_memory_graphrag import memory
pytestmark=pytest.mark.integration


def test_api_bindings_submit_exact_persisted_tasks_without_guessing_ids(db,tmp_path,memory):
 p,r,clock,path,inv,draft,planning,auth,tokens,ops=setup(db,tmp_path,memory)
 from app.graph.schema import timestamp,utc_now
 clock.value=max(clock.value,timestamp(utc_now()),*(timestamp(t.procedure_citation.retrieved_at) for t in draft.tasks))
 with active_scope(p):
  original_orders=r._read('MATCH (w:WorkOrder) RETURN count(w)')[0][0]
  receipt=asyncio.run(ops.draft(draft,request_id='BINDING-DRAFT',token=tokens['OP-ANALYST']))
  delivery=Delivery(r,clock);delivery.activate(operator='TEST',reason='Isolated exact binding HTTP test',authorize=True)
  services=Services(p,path,r,auth,ops,delivery,clock,memory=memory)
 client=TestClient(create_app(services),raise_server_exceptions=False);headers={'Authorization':'Bearer '+tokens['OP-ANALYST']}
 response=client.get('/api/v1/plans/'+receipt.id,headers=headers);assert response.status_code==200,response.text
 data=response.json()['data'];rows=data['task_bindings'];assert len(rows)==len(draft.tasks)
 with active_scope(p):saved=planning.store.get(receipt.id)
 assert {v['local_task_id']:v['task_id'] for v in rows}==saved['task_ids']
 assert data['execution_gates_verified'] is False and data['status']=='DRAFT'
 body={'plan_version':data['version'],'plan_hash':data['content_hash'],'assignments':[{k:v[k] for k in ['task_id','action_type','target_ids','department_id']}|{'assignee_id':v['eligible_assignee_ids'][0]} for v in rows]}
 request_headers={**headers,'Idempotency-Key':'BINDING-SUBMIT'}
 response=client.post('/api/v1/plans/'+receipt.id+'/submit-approval',json=body,headers=request_headers)
 assert response.status_code==200,response.text
 approval=response.json()['data'];assert approval['status']=='PENDING' and approval['approved_by'] is None
 replay=client.post('/api/v1/plans/'+receipt.id+'/submit-approval',json=body,headers=request_headers)
 assert replay.status_code==200 and replay.json()['data']['id']==approval['id']
 wrong=client.get('/api/v1/plans/'+receipt.id,headers={'Authorization':'Bearer '+tokens['OP-ROAD-LEAD']})
 assert wrong.status_code==403
 with active_scope(p):
  assert planning.store.get(receipt.id)==saved
  assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[original_orders]]
