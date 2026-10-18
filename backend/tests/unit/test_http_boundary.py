"""B16-R request-local phase/replay guards, mocked persistence only."""
import asyncio,copy
from contextlib import contextmanager
from types import SimpleNamespace
import pytest
from app.api import models as m
from app.services.http.service import Services,Boundary,Recovery,request_identity
from app.services.operations.auth import Denied
from app.graph.repository import Conflict,PreconditionFailed
from app.services.planning.service import PlanningBlocked

class Store:
 def __init__(self):self.values={};self.fail=False
 def get(self,kind,id):return copy.deepcopy(self.values.get(id))
 def write(self,session,rows):
  if self.fail:raise RuntimeError('PRIVATE_SENTINEL')
  for _,id,row in rows:self.values[id]=copy.deepcopy(row)
class Repo:
 def __init__(self):self.revision=1;self.pending=''
 @contextmanager
 def _session(self):yield None
 def _read(self,query):return [[self.pending]] if 'RETURN coalesce' in query else [[self.revision,self.pending]]
@pytest.fixture
def adapter():
 s=object.__new__(Services);s.profile=SimpleNamespace(graph='SOURCE');s.repo=Repo();s.delivery=SimpleNamespace(store=Store());s.auth=SimpleNamespace(resolve=lambda token:SimpleNamespace(id='OP',role='ANALYST'))
 s.reads=SimpleNamespace();s.calls=0
 async def dispatch(name,id,value,actor,token,request,reviewer,boundary):
  s.calls+=1
  def effect():s.repo.revision+=1;return {'id':'ENTITY'}
  await boundary.invoke(s.repo,effect)
  return {'status':'OK'}
 s.dispatch=dispatch
 return s

def run(s,key='KEY',reason='Bounded request'):
 return asyncio.run(s.command('resume','/test',None,m.ResumeRequest(reason=reason),SimpleNamespace(id='OP',role='ANALYST'),'token',key,m.Ack))

@pytest.mark.parametrize('error',[ValueError('PRIVATE_SENTINEL'),Denied('PRIVATE_SENTINEL'),Conflict('PRIVATE_SENTINEL')])
def test_proven_prewrite_rejection_stays_actionable(adapter,error):
 s=adapter
 async def reject(*args):raise error
 s.dispatch=reject
 with pytest.raises(type(error)):run(s)
 assert s.delivery.store.get('api_request',request_identity('SOURCE','OP','KEY'))['status']=='REJECTED'

@pytest.mark.parametrize('error',[Denied('scope'),Conflict('stale'),PreconditionFailed('gate'),PlanningBlocked('KNOWN_PREWRITE_GATE')])
def test_known_no_write_service_rejection_requires_unchanged_audit(adapter,error):
 s=adapter
 async def reject(name,id,value,actor,token,request,reviewer,boundary):
  def action():raise error
  await boundary.invoke(s.repo,action)
 s.dispatch=reject
 with pytest.raises(type(error)):run(s)
 assert s.delivery.store.get('api_request',request_identity('SOURCE','OP','KEY'))['status']=='REJECTED'

def test_value_error_after_invocation_is_unknown_even_without_observed_write(adapter):
 s=adapter
 async def reject(name,id,value,actor,token,request,reviewer,boundary):
  def action():raise ValueError('PRIVATE_SENTINEL')
  await boundary.invoke(s.repo,action)
 s.dispatch=reject
 with pytest.raises(Recovery):run(s)
 assert s.delivery.store.get('api_request',request_identity('SOURCE','OP','KEY'))['status']=='DISPATCHING'

def test_done_replay_and_conflicting_key_never_redispatch(adapter):
 s=adapter;first=run(s);assert run(s)==first and s.calls==1
 with pytest.raises(Conflict):run(s,reason='Changed request')
 assert s.calls==1
 row=s.delivery.store.values[request_identity('SOURCE','OP','KEY')];row['response']={'unexpected':'PRIVATE_SENTINEL'}
 with pytest.raises(Recovery):run(s)
 assert row['status']=='DONE' and s.calls==1

def test_recovery_write_failure_preserves_last_durable_intent(adapter):
 s=adapter
 async def reject(name,id,value,actor,token,request,reviewer,boundary):
  await boundary.invoke(s.repo,lambda:{'id':'ENTITY'})
  s.delivery.store.fail=True
  raise ValueError('PRIVATE_SENTINEL')
 s.dispatch=reject
 with pytest.raises(Recovery) as caught:run(s)
 assert caught.value.reconciliation['entity_id']=='ENTITY'
 row=s.delivery.store.get('api_request',request_identity('SOURCE','OP','KEY'))
 assert row['status']=='DISPATCHING' and 'recovery' not in row

@pytest.mark.parametrize('error',[Conflict('stale after commit'),PreconditionFailed('readback'),Denied('projection')])
def test_known_exception_after_audited_mutation_is_not_a_rejection(adapter,error):
 s=adapter
 async def reject(name,id,value,actor,token,request,reviewer,boundary):
  def action():s.repo.revision+=1;raise error
  await boundary.invoke(s.repo,action)
 s.dispatch=reject
 with pytest.raises(Recovery):run(s)
 assert s.delivery.store.get('api_request',request_identity('SOURCE','OP','KEY'))['status']=='DISPATCHING'

@pytest.mark.parametrize('case,status',[('malformed',422),('forbidden',403),('stale',409),('healthy',200)])
def test_focused_http_prewrite_codes_and_successful_replay(adapter,case,status):
 from fastapi.testclient import TestClient
 from app.api.application import create_app
 from app.active import new_profile
 s=adapter;s.profile=new_profile();actor=SimpleNamespace(id='OP',role='APPROVER' if case=='forbidden' else 'ANALYST',department_id='DEPT-COORD')
 s.auth.resolve=lambda token:actor
 async def dispatch(name,id,value,actor,token,request,reviewer,boundary):
  s.calls+=1
  def action():
   if case=='stale':raise Conflict('PRIVATE_SENTINEL')
   return {'id':id}
  await boundary.invoke(s.repo,action)
  return {'investigation_id':id,'accepted':True,'event_id':'EVENT','status':'PENDING'}
 s.dispatch=dispatch;c=TestClient(create_app(s),raise_server_exceptions=False)
 body={'reason':'Explicit'} if case!='malformed' else {'reason':'Explicit','role':'ADMIN'}
 h={'Authorization':'Bearer test-only-stub','Idempotency-Key':'HTTP-KEY'}
 res=c.post('/api/v1/investigations/INV/resume',json=body,headers=h)
 assert res.status_code==status,res.text
 assert 'PRIVATE_SENTINEL' not in res.text
 if case in {'malformed','forbidden'}:assert s.calls==0
 if case=='healthy':
  assert c.post('/api/v1/investigations/INV/resume',json=body,headers=h).json()['data']==res.json()['data'] and s.calls==1
  assert c.post('/api/v1/investigations/INV/resume',json={'reason':'Changed'},headers=h).status_code==409 and s.calls==1

def test_retained_request_journal_prevents_false_rejection_without_new_revision(adapter):
 s=adapter;s.repo._node_optional=lambda id:SimpleNamespace(id=id)
 async def reject(name,id,value,actor,token,request,reviewer,boundary):
  boundary.journal_id='EXISTING-JOURNAL'
  def action():raise Conflict('Readback of prior committed receipt')
  await boundary.invoke(s.repo,action)
 s.dispatch=reject
 with pytest.raises(Recovery):run(s)
 assert s.delivery.store.get('api_request',request_identity('SOURCE','OP','KEY'))['status']=='DISPATCHING'
