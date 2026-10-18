"""B15 real FalkorDB claims/restart/replay; no mock DB completion."""
import asyncio,json,os,subprocess,sys
from pathlib import Path
import pytest
from app.active import active_scope
from app.events.service import Delivery,later
from app.events.runtime import Runtime
from app.events.worker import Worker
from app.events.models import Event
from app.services.planning.storage import PlanMigration
from app.services.operations.migration import OperationsMigration
from app.graph.repository import PreconditionFailed,Conflict
from tests.b10_fixtures import create
pytestmark=pytest.mark.integration

def setup(db,tmp_path):
 path=tmp_path/'active.json';p,r,clock,receipt,inv=create(db,path)
 PlanMigration(db,p.graph).apply();OperationsMigration(db,p.graph).apply()
 return p,r,clock,path,inv

def proof(name,value):Path('docs/evidence/B15-'+name+'.json').write_text(json.dumps(value,indent=2)+'\n')
def child(path,clock,mode,*args):
 env={**os.environ,'PYTHONPATH':str(Path('backend/test_guards').resolve())+os.pathsep+str(Path('backend').resolve())}
 return subprocess.run([sys.executable,'-m','tests.b15_process',str(path),clock(),mode,*map(str,args)],env=env,capture_output=True,text=True,timeout=45)

def wake(d,inv,id):
 # Authored operator resume request, not fabricated environmental evidence.
 return d.request_resume(inv,id,operator='B15-test-operator',reason='Explicit deterministic verification',authorize=True)

def test_committed_monitor_claim_process_death_restart_public_cursor(db,tmp_path):
 p,r,clock,path,inv=setup(db,tmp_path)
 with active_scope(p):
  d=Delivery(r,clock)
  with pytest.raises(PreconditionFailed):d.discover()
  d.activate(operator='test',reason='Only this fresh profile',authorize=True)
  m=d.monitor(inv,later(clock(),1),'monitor-1',authorize=True);clock.advance();d.due()
  assert d.store.get('delivery_monitor',m['id'])['status']=='FIRED'
  assert d.store.get('delivery',m['id'])['status']=='PENDING'
  crashed=child(path,clock,'claim-exit');assert crashed.returncode==71,crashed.stderr[-600:]
  claimed=d.store.get('delivery',m['id']);assert claimed['status']=='CLAIMED' and claimed['attempts']==1
  clock.advance(61);restarted=child(path,clock,'restart');assert restarted.returncode==0,restarted.stderr[-600:]
  done=d.store.get('delivery',m['id']);assert done['status']=='DONE' and done['attempts']==2
  assert 'NO_OBSERVATION_OPPORTUNITY' in done['receipt']['classification']
  assert r.get_node(inv).properties['status']!='COMPLETED'
  assert d.discover()==[] and asyncio.run(Worker(d,Runtime(p,path,r,clock),'duplicate').once()) is None
  assert r._read('MATCH (e:DomainEvent {id:$id}) RETURN count(e)',{'id':m['id']})==[[1]]
  page=child(path,clock,'public',0);assert page.returncode==0,page.stderr[-600:]
  page=json.loads(page.stdout);assert len(page['events'])==1 and page['next_cursor']==1
  after=child(path,clock,'public',1);assert after.returncode==0,after.stderr[-600:]
  assert json.loads(after.stdout)['events']==[]
  assert d.public(limit=1)==page
  for kw in [{'after':-1},{'limit':101},{'after':True}]:
   with pytest.raises(ValueError):d.public(**kw)
  proof('process-restart',{'graph':p.graph,'process_exit':71,'initial_status':claimed['status'],'final_status':done['status'],'attempts':done['attempts'],'receipt':done['receipt'],'public':page,'fresh_process_cursor_stable':True,'duplicate_domain_events':0,'invented_observations':0})

def test_claim_case_fencing_retries_invalid_and_uncertain_dispatch(db,tmp_path):
 p,r,clock,path,inv=setup(db,tmp_path)
 with active_scope(p):
  d=Delivery(r,clock);d.activate(operator='test',reason='Explicit fresh graph',authorize=True)
  first=wake(d,inv,'first');second=wake(d,inv,'second')
  a=d.claim('owner-1',limit=1);assert a and d.claim('owner-2',limit=1) is None
  before=d.store.get('delivery',first['id']);clock.advance(61)
  b=d.claim('owner-2',limit=1);assert b and b['token']!=a['token']
  with pytest.raises(Conflict):d.running(a)
  d.running(b);clock.advance(61)
  # No checkpoint proves consumption: never blindly resume this uncertain case.
  w=Worker(d,Runtime(p,path,r,clock),'owner-3');asyncio.run(w.recover_expired())
  assert d.store.get('delivery',first['id'])['status']=='RECOVERY_REQUIRED'
  assert d.claim('owner-3') is None # Second event cannot bypass case recovery.
  with pytest.raises(PreconditionFailed):d.replay(first['id'],operator='test',reason='Not safe',ceiling=4,authorize=True)
  # Independent informational monitoring event exercises only known pre-dispatch retry.
  m=d.monitor(inv,clock(),'retry-monitor',authorize=True);d.due()
  for attempt in range(1,4):
   asyncio.run(w.once(fault='pre_dispatch_unavailable',discover=False))
   row=d.store.get('delivery',m['id']);assert row['attempts']==attempt
   clock.advance(10)
  assert row['status']=='FAILED'
  with pytest.raises(PreconditionFailed):d.replay(m['id'],operator='test',reason='No budget increase',ceiling=3,authorize=True)
  replay=d.replay(m['id'],operator='test',reason='Known pre-dispatch outage resolved',ceiling=4,authorize=True)
  assert replay['attempts']==3 and any(h.get('status')=='OPERATOR_REPLAY' for h in replay['history'])
  asyncio.run(w.once(discover=False));done=d.store.get('delivery',m['id']);assert done['status']=='DONE' and done['attempts']==4
  # Actual malformed committed native source remains inspectable, not silently dropped.
  from tests.schema_examples import common
  r.create_node('DomainEvent',{**common('BAD-B15'), 'created_at':clock(),'updated_at':clock(),'event_type':'GRAPH_EVIDENCE_CHANGED','subject_id':inv,'occurred_at':clock(),'delivery_status':'PENDING','idempotency_key':'BAD-B15','payload_ref':'missing:committed-envelope'})
  d.discover();bad=d.store.get('delivery','BAD-B15');assert bad['status']=='FAILED' and bad['event'] is None
  with pytest.raises(PreconditionFailed):d.replay('BAD-B15',operator='test',reason='Cannot replay invalid source',ceiling=4,authorize=True)
  assert all(e['id']!='BAD-B15' for e in d.public()['events'])
  proof('claims-failures',{'graph':p.graph,'stale_owner_denied':True,'second_case_claim_denied':True,'expired_unproven_dispatch':d.store.get('delivery',first['id'])['status'],'attempts':done['attempts'],'retry_history':done['history'],'invalid':bad,'automatic_recovery_replay_denied':True})

def test_real_racing_claims_and_existing_quarantine(db,tmp_path):
 from concurrent.futures import ThreadPoolExecutor
 from threading import Barrier
 from app.graph.repository import GraphRepository
 from app.agents.checkpoints import ownership,RecoveryRequired,saver
 from app.graph.models import digest
 p,r,clock,path,inv=setup(db,tmp_path)
 with active_scope(p):
  d=Delivery(r,clock);d.activate(operator='proof',reason='Exact profile',authorize=True)
  a=wake(d,inv,'race-a');b=wake(d,inv,'race-b');barrier=Barrier(2)
  def compete(owner):
   with active_scope(p):
    separate=Delivery(GraphRepository(db,p.graph),clock);barrier.wait();return separate.claim(owner,limit=1)
  with ThreadPoolExecutor(max_workers=2) as pool:claims=list(pool.map(compete,['race-1','race-2']))
  assert sum(c is not None for c in claims)==1
  runtime=Runtime(p,path,r,clock);thread=runtime.thread(inv);key='civicly:b10:'+p.graph+':'+digest(thread)+':quarantine'
  async def quarantine():
   with pytest.raises(RecoveryRequired):
    async with ownership(db,p,thread):raise RecoveryRequired('Authored uncertain checkpoint fault; no repair')
  asyncio.run(quarantine());original=db.connection.get(key);assert original
  clock.advance(61);asyncio.run(Worker(d,runtime,'replacement').once(discover=False))
  active=[d.store.get('delivery',i) for i in [a['id'],b['id']]]
  assert all(row['status']=='RECOVERY_REQUIRED' for row in active)
  assert db.connection.get(key)==original and saver(p).get_tuple({'configurable':{'thread_id':thread}}) is None
  assert r._read('MATCH (d:AgentDecision) RETURN count(d)')==[[0]]
  proof('quarantine-race',{'graph':p.graph,'simultaneous_claimants':2,'successful_claims':1,'states':[x['status'] for x in active],'quarantine_preserved':True,'checkpoint_created':False,'agent_decisions':0,'operator_reconciliation_required':True})
