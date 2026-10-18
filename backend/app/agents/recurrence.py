"""Validated active-episode refresh on explicit owned resume; no checkpoint rewrite."""
from app.graph.schema import timestamp
from app.graph.models import digest
from app.services.evidence.reader import Reader
from app.services.complaints.models import Journal,normalize
from app.services.complaints.service import ComplaintService
from .models import InvestigationState
from .checkpoints import RecoveryRequired

def refresh(repo,state):
 reader=Reader(repo,state.as_of)
 links=reader.edges('INVESTIGATES',source=state.investigation_id)
 incidents={e.target:reader.node(e.target) for e in links if reader.node(e.target).kind=='Incident'}
 # Reuse persisted validation proofs, not an ENDED-status exemption. History
 # remains graph-bound even when active state advances to another episode.
 historical=set()
 for audit in getattr(state,'observations',[]):
  if audit.get('operation')!='RECURRENCE_SCOPE_REFRESH' or audit.get('host_generated') is not True or audit.get('investigation_id')!=state.investigation_id:continue
  try:
   prior=set(audit['historical_incident_ids'])
   if not prior<=set(audit['previous_incident_ids'])|historical:raise ValueError()
   related=set();adopted=[]
   for proof in audit['scope_proofs']:
    edge=next(e for e in links if e.id==proof['investigates_relationship_id'] and e.target==proof['incident_id'])
    jid=proof['journal_id'];native=reader.node(jid,'Evidence')
    if edge.properties.get('source_evidence_id')!=jid or getattr(state,'evidence',{}).get(jid)!=native.content_hash:raise ValueError()
    journal=Journal.model_validate_json(native.properties['summary']);_,norm=normalize(journal.original)
    service=ComplaintService(repo);_,stored=service.load(jid,norm.request_hash);receipt=service.receipt(stored)
    if receipt.classification!='AFTER_RECORDED_END' or receipt.incident_id!=edge.target or receipt.cluster_id!=state.problem_cluster_id or receipt.graph!=state.graph or digest(receipt.model_dump(mode='json'))!=proof['receipt_hash']:raise ValueError()
    related.update(receipt.related_incident_ids);adopted.append(incidents[edge.target])
   if not adopted or {n.id for n in adopted}!=set(audit['active_incident_ids']):raise ValueError()
   for id in prior:
    n=incidents[id]
    if id not in related or n.properties['status']!='ENDED' or n.properties['issue_type']!=state.issue or {e.target for e in reader.edges('PART_OF',source=id)}!={state.problem_cluster_id} or not n.properties.get('ended_at') or not all(timestamp(n.properties['ended_at'])<timestamp(a.properties['started_at']) for a in adopted):raise ValueError()
   historical.update(prior)
  except (ValueError,KeyError,TypeError,StopIteration):raise RecoveryRequired('RECURRENCE_HISTORY_PROOF_INVALID') from None
 additions=set(incidents)-set(state.incident_ids)-historical
 if len(incidents)>3:raise RecoveryRequired('RECURRENCE_SCOPE_NOT_REFRESHABLE')
 if not additions:
  if reader.node(state.investigation_id,'Investigation').properties['status']=='REOPENED' and not any(n.properties['status'] in {'REPORTED','ACTIVE','MITIGATED'} for n in incidents.values()):raise RecoveryRequired('RECURRENCE_SCOPE_MISSING_ACTIVE_EPISODE')
  return state
 if len(incidents)>3 or reader.node(state.investigation_id,'Investigation').properties['status']!='REOPENED':raise RecoveryRequired('RECURRENCE_SCOPE_NOT_REFRESHABLE')
 evidence={};proof=[]
 for id in sorted(additions):
  incident=incidents[id];edge=next(e for e in links if e.target==id)
  journal_id=edge.properties.get('source_evidence_id')
  if not journal_id:raise RecoveryRequired('RECURRENCE_SCOPE_PROVENANCE')
  native=reader.node(journal_id,'Evidence')
  try:journal=Journal.model_validate_json(native.properties['summary'])
  except ValueError:raise RecoveryRequired('RECURRENCE_SCOPE_PROVENANCE') from None
  q,norm=normalize(journal.original)
  intake=ComplaintService(repo)
  _,stored=intake.load(journal_id,norm.request_hash)
  receipt=intake.receipt(stored)
  previous=[incidents[old] for old in state.incident_ids if old in receipt.related_incident_ids and old in incidents]
  memberships=reader.edges('PART_OF',source=id)
  affected={e.target for e in reader.edges('AFFECTS',source=id)}
  if (journal.operation!='INTAKE' or journal.state!='COMMITTED' or journal.canonical!=norm.canonical
      or receipt.graph!=state.graph or receipt.incident_id!=id or not receipt.created_incident
      or receipt.classification!='AFTER_RECORDED_END' or receipt.cluster_id!=state.problem_cluster_id
      or {e.target for e in memberships}!={state.problem_cluster_id} or q.issue_type!=state.issue
      or incident.properties['issue_type']!=state.issue or incident.properties['started_at']!=q.occurred_at
      or affected!=set(q.asset_ids) or not q.evidence_ids or not previous
      or not any(n.properties['status']=='ENDED' and n.properties.get('ended_at') and timestamp(n.properties['ended_at'])<timestamp(q.occurred_at) for n in previous)):
   raise RecoveryRequired('RECURRENCE_SCOPE_BINDING')
  for eid in q.evidence_ids:
   ref=reader.evidence(eid)
   if not ref.report or not ref.report.review or ref.source_kind!='SYNTHETIC' or timestamp(ref.observed_at)<timestamp(q.occurred_at):raise RecoveryRequired('RECURRENCE_SCOPE_EVIDENCE')
   evidence[eid]=ref.content_hash
  evidence[journal_id]=native.content_hash
  proof.append({'incident_id':id,'investigates_relationship_id':edge.id,'journal_id':journal_id,'receipt_hash':digest(receipt.model_dump(mode='json'))})
 active=sorted(id for id,n in incidents.items() if n.properties['status'] in {'REPORTED','ACTIVE','MITIGATED'})
 assets=sorted({e.target for id in active for e in reader.edges('AFFECTS',source=id)})
 audit={'operation':'RECURRENCE_SCOPE_REFRESH','host_generated':True,'investigation_id':state.investigation_id,'previous_incident_ids':state.incident_ids,'active_incident_ids':active,'historical_incident_ids':sorted(set(incidents)-set(active)),'evidence_ids':sorted(evidence),'scope_proofs':proof,'limitations':['Earlier plan/hypotheses describe their recorded episodes; not causal authority for recurrence. Fresh MCP READ required.']}
 # Full closed model validation, original graph/thread/inventory/plan identities intact.
 return InvestigationState.model_validate({**state.model_dump(mode='json'),'incident_ids':active,'asset_ids':assets,
  'evidence':{**state.evidence,**evidence},'observations':[*state.observations,audit],'refresh_required':True})
