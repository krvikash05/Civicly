"""Bounded adapters from committed accepted records, never reconstructed executions."""
import json
from app.graph.models import digest
from app.graph.schema import utc_now
from app.graph.repository import PreconditionFailed
from app.services.operations.storage import Storage
from .models import Event

class Sources:
 def __init__(self,repo,clock=utc_now):self.repo=repo;self.store=Storage(repo);self.clock=clock
 def scan(self):
  # One explicitly activated source graph only. Incomplete journals remain visible
  # and will be reconsidered when their actual COMMITTED receipt becomes available.
  native=self.repo._read('MATCH (e:DomainEvent) RETURN properties(e) ORDER BY e.id LIMIT 501')
  legacy=self.repo._read('MATCH (e:Evidence) WHERE e.evidence_type IN $types RETURN properties(e) ORDER BY e.id LIMIT 501',{'types':['COMPLAINT_INTAKE','GROUPING_CORRECTION','B09_OPERATION']})
  drafts=self.repo._read('MATCH (d:CivicPlanDraft) RETURN d.id ORDER BY d.id LIMIT 101')
  if len(native)>500 or len(legacy)>500 or len(drafts)>100:raise PreconditionFailed('SOURCE_SCAN_BOUND_RECONCILIATION_REQUIRED')
  activity=[]
  bound=self.repo._read('MATCH (i:Investigation) WHERE i.thread_id IS NOT NULL RETURN i.id ORDER BY i.id LIMIT 101')
  if len(bound)>100:raise PreconditionFailed('ACTIVITY_SOURCE_CAPACITY')
  if bound:
   from app.services.activity import activity as persisted_activity
   from app.mcp.civicly.runtime import connections
   from app.mcp.civicly.storage import TraceStore
   decisions=self.repo._read('MATCH (n:AgentDecision) RETURN n.id,n.rationale,n.decided_at ORDER BY n.id LIMIT 501')
   if len(decisions)>500:raise PreconditionFailed('ACTIVITY_SOURCE_CAPACITY')
   with connections() as (_,writer,name):
    store=TraceStore(writer,name)
    for row in bound:
     for fact in persisted_activity(self.repo,row[0],self.clock(),decisions=decisions,store=store):
      activity.append(('activity',fact['event_id'],fact))
      if len(activity)>500:raise PreconditionFailed('ACTIVITY_SOURCE_CAPACITY')
  return activity+[('native',p[0]['id'],p[0]) for p in native]+[('journal',p[0]['id'],p[0]) for p in legacy]+[('draft',p[0],{}) for p in drafts]
 def case(self,event):
  entity=self.repo.get_node(event.entity_id)
  if entity.kind=='Investigation':return entity.id
  rows=[]
  queries=[
   'MATCH (i:Investigation)-[:INVESTIGATES]->(n:CivicEntity {id:$id}) RETURN i.id LIMIT 2',
   'MATCH (i:Investigation)-[:PRODUCED_PLAN]->(p:ResolutionPlan {id:$id}) RETURN i.id LIMIT 2',
   'MATCH (i:Investigation)-[:PRODUCED_PLAN]->(:ResolutionPlan)-[:HAS_TASK]->(:ActionTask)<-[:IMPLEMENTS]-(w:WorkOrder {id:$id}) RETURN i.id LIMIT 2']
  for query in queries:rows.extend(self.repo._read(query,{'id':entity.id}))
  inv=event.payload.get('investigation_id')
  if inv:
   self.repo.get_node(inv,'Investigation');rows.append([inv])
  ids={r[0] for r in rows}
  return next(iter(ids)) if len(ids)==1 else None
 def events(self,kind,id,p):
  if kind=='activity':
   typ='AGENT_TOOL_EXECUTED' if p['kind']=='TOOL' else 'AGENT_DECISION_RECORDED'
   yield self.derived(id,typ,p['investigation_id'],p['graph_revision'] or 0,p['timestamp'],'AGENT','civicly-b10-analyst','SYSTEM',{'investigation_id':p['investigation_id'],'execution_id':id if p['kind']=='TOOL' else None,'decision_id':id if p['kind']=='DECISION' else None})
   return
  if kind=='native':
   ref=p.get('payload_ref','')
   if ref.startswith('operation:'):
    value=self.store.get('operation',ref.removeprefix('operation:'))
    rows=[e for e in value['events'] if e['id']==id] if value else []
   elif ref=='delivery:'+id:
    old=self.store.get('delivery',id);rows=[old['event']] if old and old['event'] else []
   else:rows=[]
   if len(rows)!=1:raise ValueError('NATIVE_EVENT_ENVELOPE_UNAVAILABLE')
   e=Event.model_validate(rows[0])
   if (e.type,e.entity_id,e.occurred_at,e.idempotency_key)!=(p['event_type'],p['subject_id'],p['occurred_at'],p['idempotency_key']):raise ValueError('NATIVE_EVENT_BINDING')
   yield e;return
  if kind=='draft':
   from app.services.planning.storage import Store
   saved=Store(self.repo).get(id)
   props=self.repo.get_node(id,'ResolutionPlan').properties
   yield self.derived(id,'GRAPH_EVIDENCE_CHANGED',id,saved['proof']['source_graph_revision']+1,props['created_at'],'SYNTHETIC',saved['proof']['actor_id'],saved['proof']['actor_role'],{'investigation_id':saved['draft']['investigation_id'],'plan_id':id,'operation':'draft'})
   return
  raw=json.loads(p['summary'])
  if raw.get('state')!='COMMITTED':return
  if p['evidence_type']=='B09_OPERATION':
   from app.services.evidence.models import Journal
   from app.services.evidence.service import EvidenceService
   j=Journal.model_validate(raw);service=EvidenceService(self.repo)
   _,checked=service.load(id,j.request_hash);receipt=service.readback(checked.receipt)
   typ={'open':'CASE_OPENED','assess':'HYPOTHESIS_ASSESSED','report_inspection':'INSPECTION_RESULT_RECORDED'}.get(j.command['operation'],'GRAPH_EVIDENCE_CHANGED')
   inv=j.command.get('investigation_id')
   if j.command['operation']=='open':inv=receipt.entity_id
   elif j.command.get('inspection_id'):
    from app.services.evidence.reader import Reader
    inv=service.inspection_source(Reader(self.repo,receipt.recorded_at),j.command['inspection_id'])[0]['investigation_id']
   elif j.command.get('hypothesis_id'):
    rows=self.repo._read('MATCH (i:Investigation)-[:PROPOSES]->(h:Hypothesis {id:$id}) RETURN i.id LIMIT 2',{'id':j.command['hypothesis_id']});inv=rows[0][0] if len(rows)==1 else None
   yield self.derived(id,typ,receipt.entity_id,receipt.graph_revision,receipt.recorded_at,'USER',j.actor.id,j.actor.role,{'investigation_id':inv,'operation':j.command['operation'],'source_journal_id':id})
  else:
   from app.services.complaints.models import Journal
   from app.services.complaints.service import ComplaintService
   j=Journal.model_validate(raw);service=ComplaintService(self.repo);_,checked=service.load(id,j.request_hash,j.operation)
   if j.operation!='INTAKE':
    r=checked.receipt
    yield self.derived(id,'GRAPH_EVIDENCE_CHANGED',r['incident_id'],r['graph_revision'],p['updated_at'],p['source_kind'],j.canonical['reviewer_id'],j.canonical['role'],{'operation':'regroup','source_journal_id':id})
    return
   result=service.receipt(checked)
   for typ,entity in [('COMPLAINT_ACCEPTED',result.complaint_id),('INCIDENT_LINKED',result.incident_id)]:
    yield self.derived(id,typ,entity,result.graph_revision,result.as_of,p['source_kind'],None,None,{'cluster_id':result.cluster_id,'source_journal_id':id})
 def derived(self,source,typ,entity,revision,at,origin,actor,role,payload):
  id='ADAPT-B15-'+digest([source,typ,entity])[:32]
  return Event(id=id,type=typ,entity_id=entity,aggregate_revision=revision,occurred_at=at,payload_schema_version=1,source_kind=origin,idempotency_key=id,actor_id=actor,actor_role=role,payload=payload)
