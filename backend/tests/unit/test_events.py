"""Pure event/routing/backoff/redaction tests, no simulated DB success."""
import pytest
from pydantic import ValidationError
from app.events.models import Event,route,public,backoff,batch_key

def event(**kw):return Event.model_validate({'id':'E','type':'RECURRENCE_DETECTED','entity_id':'INV','aggregate_revision':3,'occurred_at':'2026-10-18T00:00:00Z','payload_schema_version':1,'source_kind':'SYNTHETIC','idempotency_key':'R',**kw})
@pytest.mark.parametrize('changes',[{'type':'UNKNOWN'},{'aggregate_revision':-1},{'occurred_at':'tomorrow'},{'payload_schema_version':2},{'password':'private'},{'type':'INSPECTION_RESULT_RECORDED'}])
def test_event_contract_denials(changes):
 with pytest.raises((ValueError,ValidationError)):event(**changes)
@pytest.mark.parametrize('typ,case,action',[('RECURRENCE_DETECTED','INV','WAKE'),('CASE_OPENED',None,'INFO'),('PLAN_SUBMITTED','INV','INFO'),('PLAN_DRAFTED','INV','INFO'),('AGENT_TOOL_EXECUTED','INV','INFO'),('WORK_ORDER_STATUS_CHANGED','INV','INFO'),('MONITORING_DUE','INV','MONITOR')])
def test_routes(typ,case,action):
 value=event(type=typ,actor_id='OP',actor_role='ANALYST');assert route(value,case)[0]==action
 assert route(value.model_copy(update={'actor_id':'civicly-b10-analyst'}),case)[0]=='INFO'
def test_backoff_bounds_and_coalescing_identity():
 assert [backoff(i) for i in range(1,9)]==[1,2,4,8,16,32,60,60]
 for i in [0,9]:
  with pytest.raises(ValueError):backoff(i)
 assert batch_key(['A','B'])==batch_key(['B','A']) and batch_key(['A'])!=batch_key(['A','B'])
def test_public_payload_redaction_and_distinct_cursor():
 e=event(payload={'plan_id':'P','source_text':'untrusted private source','password':'secret','provider_body':{},'reasoning':'private'})
 p=public(e,'INV',9,'native:E');assert p['payload']=={'plan_id':'P'} and p['cursor']==9 and p['id']=='E'
 assert not {'actor_id','idempotency_key','source_text','reasoning'}&set(p)

def test_safe_stop_finishes_inflight_before_next_poll():
 import asyncio
 from app.events.worker import Worker
 async def run():
  w=Worker(None,None,'unit');calls=[]
  async def once():
   calls.append('handler-start');w.stopping=True;await asyncio.sleep(0);calls.append('handler-finished')
  w.once=once
  await w.run(poll_seconds=.01,max_batches=3)
  assert calls==['handler-start','handler-finished']
  for kw in [{'max_batches':101},{'poll_seconds':0}]:
   with pytest.raises(ValueError):await w.run(**kw)
 asyncio.run(run())

@pytest.mark.parametrize('pause,consumed',[('RECOVERY_REQUIRED',False),('PLAN_OPERATOR_RECOVERY_REQUIRED',False),('DEPENDENCY_UNAVAILABLE',False),('HUMAN_REVIEW',True)])
def test_only_safe_checkpoint_pause_can_record_consumption(pause,consumed):
 import asyncio
 from types import SimpleNamespace
 from app.agents.runtime import InvestigationAgent
 agent=object.__new__(InvestigationAgent)
 state=SimpleNamespace(selection=SimpleNamespace(action='PAUSE',pause_reason=pause),pause_reason=pause,observations=[{'operation':'B15_DELIVERY_STARTED','host_generated':True,'delivery_key':batch_key(['E'])}])
 agent.decode=lambda channel:channel;agent.output=lambda s,node:s
 result=asyncio.run(agent.coordinator(state))
 assert any(o.get('operation')=='B15_DELIVERY_CONSUMED' for o in result.observations)==consumed

def test_probe_corrupt_checkpoint_is_sanitized_recovery(monkeypatch):
 import asyncio
 from contextlib import asynccontextmanager
 from app.events import runtime
 from app.agents.checkpoints import RecoveryRequired
 @asynccontextmanager
 async def owned(*args):yield lambda:None
 monkeypatch.setattr(runtime,'ownership',owned)
 monkeypatch.setattr(runtime,'saver',lambda profile:object())
 r=runtime.Runtime(None,None,type('Repo',(),{'client':None})(),lambda:'2026-10-18T00:00:00Z')
 r.thread=lambda inv:'thread'
 with pytest.raises(RecoveryRequired,match='^CONSUMER_CHECKPOINT_VERIFICATION_FAILED$'):
  asyncio.run(r.probe('INV',batch_key(['E'])))
