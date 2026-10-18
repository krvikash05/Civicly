"""Current request-status metadata, not a substitute for an MCP evidence read."""
from app.services.evidence.reader import Reader
from app.graph.repository import PreconditionFailed


def requested_inspections(service,state):
 reader=Reader(service.repo,state.as_of);rows=[]
 linked=service.repo._read('MATCH (i:Inspection)-[:INSPECTS]->(a:InfrastructureAsset) WHERE a.id IN $assets RETURN DISTINCT i.id ORDER BY i.id LIMIT 101',{'assets':state.asset_ids})
 if len(linked)>100:raise PreconditionFailed('INSPECTION_CONTEXT_CAPACITY')
 for id in sorted(set(state.pending_inspections)|{r[0] for r in linked}):
  node=reader.node(id,'Inspection');scope,assets=service.inspection_source(reader,id)
  if scope['investigation_id']!=state.investigation_id:
   if id in state.pending_inspections:raise PreconditionFailed('INSPECTION_CONTEXT_SCOPE')
   continue
  reports=[]
  for edge in reader.edges('PRODUCED',source=id):
   ref=reader.evidence(edge.target)
   if ref.report is None or ref.report.inspection_id!=id:raise PreconditionFailed('INSPECTION_CONTEXT_REPORT_BINDING')
   reports.append(ref.id)
  rows.append({'inspection_id':id,'status':node.properties['status'],
   'asset_ids':sorted(assets),'department_id':scope['department_id'],
   'requested_at':node.properties['requested_at'],'completed_at':node.properties.get('completed_at'),
   'report_evidence_ids':sorted(reports),'metadata_only_not_causal_evidence':True})
 return rows
