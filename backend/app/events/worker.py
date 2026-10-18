"""One bounded local polling loop. Unknown wakes are never blindly repeated."""
import asyncio
from app.agents.checkpoints import RecoveryRequired
from app.graph.repository import OutcomeUnknown
from app.graph.schema import timestamp

class PreDispatchUnavailable(RuntimeError):pass
class Worker:
 def __init__(self,delivery,runtime,owner):self.delivery,self.runtime,self.owner=delivery,runtime,owner;self.stopping=False
 async def reconcile(self,claim):
  d=self.delivery;receipt=d.store.get('delivery_consumer',claim['key'])
  if receipt:receipt=receipt['receipt']
  elif claim['action']=='WAKE':receipt=await self.runtime.probe(claim['case_id'],claim['key'])
  else:receipt=None
  if receipt:d.finish(claim,receipt,reconciled=True);return True
  if claim['status']=='RUNNING':d.failed(claim,'UNCERTAIN_DISPATCH_OPERATOR_RECONCILIATION')
  return False
 async def recover_expired(self):
  for claim in self.delivery.store.rows('delivery_case'):
   if claim['status']=='RUNNING' and timestamp(claim['lease_until'])<=timestamp(self.delivery.clock()):
    try:await self.reconcile(claim)
    except RecoveryRequired:self.delivery.failed(claim,'CHECKPOINT_QUARANTINE_OR_OWNERSHIP_REQUIRES_OPERATOR')
 async def once(self,*,fault=None,discover=True,case_id=None):
  d=self.delivery
  if discover:d.discover();d.due()
  await self.recover_expired()
  claim=d.claim(self.owner,case_id=case_id) if case_id is not None else d.claim(self.owner)
  if not claim:return None
  if fault=='after_claim':return claim # Test process may terminate here; no handler started.
  heartbeat=None
  async def renew():
   while True:
    await asyncio.sleep(10);await asyncio.to_thread(d.renew,claim)
  try:
   # Only the explicit known pre-dispatch hook is safe to retry.
   if fault=='pre_dispatch_unavailable':raise PreDispatchUnavailable()
   claim=d.running(claim);heartbeat=asyncio.create_task(renew())
   if claim['action']=='WAKE':
    receipt=await self.runtime.handle(claim)
    if not receipt:raise RecoveryRequired('CONSUMER_COMPLETION_NOT_ESTABLISHED')
   else:receipt={'kind':claim['action'],'classification':'FOLLOWUP_REQUESTED_NO_OBSERVATION_OPPORTUNITY_ESTABLISHED' if claim['action']=='MONITOR' else 'INFORMATIONAL_NO_OPERATIONAL_AUTHORITY','event_ids':claim['ids']}
   if fault=='after_handler':return claim # Persisted handler checkpoint, no acknowledgment yet.
   d.finish(claim,receipt);return claim
  except PreDispatchUnavailable:d.failed(claim,'PRE_DISPATCH_UNAVAILABLE',safe_retry=True)
  except (RecoveryRequired,OutcomeUnknown):d.failed(claim,'RECOVERY_REQUIRED_NO_AUTOMATIC_RETRY')
  except Exception:d.failed(claim,'UNCERTAIN_HANDLER_OR_TRANSPORT_NO_AUTOMATIC_RETRY')
  finally:
   if heartbeat:
    heartbeat.cancel()
    try:await heartbeat
    except asyncio.CancelledError:pass
  return claim
 async def run(self,*,poll_seconds=1,max_batches=100):
  if not .01<=poll_seconds<=5 or not 1<=max_batches<=100:raise ValueError('WORKER_LOOP_BOUND')
  for _ in range(max_batches):
   if self.stopping:break
   await self.once()
   try:await asyncio.sleep(poll_seconds)
   except asyncio.CancelledError:self.stopping=True;break
