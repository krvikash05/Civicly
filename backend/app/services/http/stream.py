"""Read-only SSE transport over B15 durable registration, never a consumer ack."""
import asyncio,json,re,time
from app.active import active_scope
from app.api.view_models import SSEEvent
from app.api.dependencies import HTTPFailure
from app.services.operations.auth import Denied
from app.graph.repository import NotFound,PreconditionFailed
from app.events.models import TYPES

# Total normative mapping, including safe generic updates for non-UI-specific facts.
EVENT_NAMES={kind:'case_updated' for kind in TYPES}
EVENT_NAMES.update(AGENT_TOOL_EXECUTED='case_tool_called',AGENT_DECISION_RECORDED='decision_recorded',INSPECTION_RESULT_RECORDED='inspection_recorded',PLAN_SUBMITTED='approval_needed',WORK_ORDER_CREATED='work_order_updated',WORK_ORDER_STATUS_CHANGED='work_order_updated',RECURRENCE_DETECTED='case_reopened',EVENT_DELIVERY_FAILED='error')
def cursor_value(query,header):
 def parse(v):
  if v is None:return None
  if not isinstance(v,str) or not re.fullmatch(r'0|[1-9][0-9]{0,14}',v):raise HTTPFailure(422,'CURSOR_INVALID')
  return int(v)
 q,h=parse(query),parse(header)
 if q is not None and h is not None and q!=h:raise HTTPFailure(409,'CURSOR_CONFLICT')
 return h if h is not None else q if q is not None else 0

def frame(name,data,cursor=None):
 return (('id: '+str(cursor)+'\n') if cursor is not None else '')+'event: '+name+'\ndata: '+json.dumps(data,separators=(',',':'),allow_nan=False)+'\n\n'
class Stream:
 poll_seconds=.25
 max_seconds=30
 batch_size=50
 def __init__(self,services,token,actor,after,investigation=None):self.s,self.token,self.actor,self.after,self.investigation=services,token,actor,after,investigation
 def validate(self):
  actor=self.s.auth.resolve(self.token)
  if actor!=self.actor:raise Denied('SESSION_SCOPE_CHANGED')
  if self.investigation:self.s.reads.node(self.investigation,'Investigation',actor,self.token)
  self.s.delivery.active()
  root=self.s.delivery.store.get('delivery_stream','root')['cursor']
  if self.after>root:raise HTTPFailure(409,'CURSOR_FUTURE')
  # No retention deletion is currently implemented. Detect a missing durable
  # registration instead of silently skipping a hole or claiming complete replay.
  rows=self.s.delivery.public(after=self.after,limit=self.batch_size)
  if ([v['cursor'] for v in rows['events']]!=list(range(self.after+1,self.after+1+len(rows['events'])))) or (not rows['events'] and root>self.after):raise HTTPFailure(409,'CURSOR_EXPIRED')
  return actor,rows
 def visible(self,event,actor):
  if self.investigation and event.investigation_id!=self.investigation:return False
  reads=self.s.reads
  try:
   if event.investigation_id:reads.node(event.investigation_id,'Investigation',actor,self.token)
   elif actor.role=='DEPARTMENT_LEAD':return False
   # Agent activity IDs reside in separate trace storage; its exact investigation
   # binding was validated before registration. Other resources retain detail RBAC.
   if event.event_type not in {'AGENT_TOOL_EXECUTED','AGENT_DECISION_RECORDED'}:
    n=self.s.repo.get_node(event.entity_id)
    if not reads.allowed(n,actor,self.token):return False
   return True
  except (Denied,NotFound):return False
 async def events(self,request):
  deadline=time.monotonic()+self.max_seconds;heartbeat=time.monotonic()
  try:
   while time.monotonic()<deadline:
    if await request.is_disconnected():return
    try:
     with active_scope(self.s.profile):
      actor,rows=self.validate()
      # Bound buffer; all records closed-schema validated before public framing.
      batch=[SSEEvent.model_validate(v) for v in rows['events']]
      visible=[v for v in batch if self.visible(v,actor)]
     for event in visible:
      # Revalidate immediately before each emit, not only at connection opening.
      current=self.s.auth.resolve(self.token)
      with active_scope(self.s.profile):
       if current!=self.actor or not self.visible(event,current):continue
      name='inspection_requested' if event.event_type=='GRAPH_EVIDENCE_CHANGED' and event.payload.operation=='request_inspection' else EVENT_NAMES[event.event_type]
      yield frame(name,event.model_dump(mode='json'),event.cursor)
     if batch:
      self.s.auth.resolve(self.token)
      self.after=batch[-1].cursor
      # Safe progress across filtered/unauthorized rows prevents replay starvation.
      yield frame('cursor',{'cursor':self.after},self.after)
     elif time.monotonic()-heartbeat>=5:
      yield ': heartbeat\n\n';heartbeat=time.monotonic()
    except Denied:
     yield frame('error',{'code':'UNAUTHORIZED','retryable':False});return
    except Exception:
     yield frame('error',{'code':'STREAM_UNAVAILABLE','retryable':False});return
    await asyncio.sleep(self.poll_seconds)
   yield ': reconnect and refetch authoritative resources\n\n'
  finally:
   # Cancellation owns no lease, queue, domain acknowledgement or mutation.
   pass
