"""Public projections of existing persisted selections and validated MCP traces."""
import json
from app.agents.models import Selection,InvestigationState
from app.graph.schema import timestamp
from app.graph.repository import PreconditionFailed
from app.graph.models import digest

def activity(repo,investigation,as_of,*,decisions=None,store=None):
 n=repo.get_node(investigation,'Investigation');thread=n.properties.get('thread_id')
 if not thread:return []
 rows=decisions if decisions is not None else repo._read('MATCH (n:AgentDecision) RETURN n.id,n.rationale,n.decided_at ORDER BY n.id LIMIT 501')
 if len(rows)>500:raise PreconditionFailed('DECISION_CAPACITY')
 result=[];modes={}
 for id,raw,at in rows:
  value=json.loads(raw);meta=value.get('metadata',{})
  if meta.get('investigation_id')!=investigation or meta.get('thread_id')!=thread:continue
  if value.get('version')!=1:raise PreconditionFailed('DECISION_VERSION')
  selection=Selection.model_validate(value['selection'])
  if timestamp(at)>timestamp(as_of):continue
  mode=meta['mode'];modes[id]=mode
  result.append({'event_id':id,'investigation_id':investigation,'timestamp':at,'agent_role':'Supervisor','kind':'DECISION','tool_name':selection.tool_name or None,'status':selection.action,'rationale_summary':selection.summary,'graph_revision':meta['graph_revision'],'execution_mode':mode})
 from app.mcp.civicly.runtime import connections
 from app.mcp.civicly.storage import TraceStore
 from contextlib import nullcontext
 with connections() if store is None else nullcontext(None) as connection:
  if connection is not None:
   _,writer,name=connection;store=TraceStore(writer,name)
  rows=store.repo._read('MATCH (n:ToolExecution {trace_id:$thread}) RETURN n.id ORDER BY n.id LIMIT 161',{'thread':thread})
  if len(rows)>160:raise PreconditionFailed('TRACE_CAPACITY')
  for row in rows:
   record=store.get(row[0]);ctx=record.context
   if ctx.source_graph!=repo.graph.name or ctx.investigation_id!=investigation or ctx.trace_id!=thread:raise PreconditionFailed('TRACE_SCOPE_BINDING')
   if record.phase!='BROKER' or timestamp(record.finished_at)>timestamp(as_of):continue
   # A trace without a matching selected decision is retained but never labelled
   # as autonomous/model selected. No raw arguments/output or private reasoning.
   decision=ctx.parent_execution_id
   if decision not in modes:
    parent=store.get(decision) if decision else None
    if parent:
     if parent.phase!='SERVER' or (parent.context.source_graph,parent.context.investigation_id,parent.context.trace_id)!=(repo.graph.name,investigation,thread):raise PreconditionFailed('TRACE_PARENT_BINDING')
     decision=parent.context.parent_execution_id
   mode=modes.get(decision,'RECORDED_TOOL_EXECUTION_MODE_UNAVAILABLE')
   result.append({'event_id':ctx.execution_id,'investigation_id':investigation,'timestamp':record.finished_at,'agent_role':'Investigator','kind':'TOOL','tool_name':record.tool_name,'server_id':record.server_id,'status':record.status,'rationale_summary':None,'arguments_sha256':record.arguments_sha256,'output_sha256':record.output_sha256,'validated_output':record.validated_output,'duration_ms':record.latency_ms,'evidence_ids':record.source_evidence_ids,'graph_path_ids':record.graph_path_ids,'graph_revision':record.graph_revision,'error_code':record.error_code,'execution_mode':mode,'parent_execution_id':ctx.parent_execution_id,'decision_id':decision if decision in modes else None})
 if len(result)>500:raise PreconditionFailed('ACTIVITY_CAPACITY')
 return sorted(result,key=lambda v:(timestamp(v['timestamp']),v['event_id']))

def checkpoint(repo,profile,inv):
 n=repo.get_node(inv,'Investigation');thread=n.properties.get('thread_id')
 if not thread:return None,False
 from app.agents.checkpoints import saver
 saved=saver(profile).get_tuple({'configurable':{'thread_id':thread}})
 quarantined=bool(repo.client.connection.get('civicly:b10:'+profile.graph+':'+digest(thread)+':quarantine'))
 if saved is None:return None,quarantined
 state=InvestigationState.model_validate(saved.checkpoint['channel_values']['data'])
 if (state.graph,state.investigation_id,state.thread_id)!=(profile.graph,inv,thread):raise PreconditionFailed('CHECKPOINT_SCOPE_BINDING')
 return state,quarantined

def selected_paths(repo,inv,items,node_ids,edges,as_of):
 """Highlight only path bodies actually retained by the accepted B10 journal."""
 from app.graph.models import PathRecord
 tools={v.get('decision_id') or v['parent_execution_id']:v for v in items if v['kind']=='TOOL' and v.get('validated_output') and v.get('graph_path_ids')}
 if not tools:return []
 rows=repo._read('MATCH (e:Evidence) WHERE e.evidence_type=$kind AND e.source_record_id IN $decisions RETURN e.source_record_id,e.summary ORDER BY e.id LIMIT 161',{'kind':'B10_OPERATION','decisions':list(tools)})
 if len(rows)>160:raise PreconditionFailed('SELECTED_PATH_CAPACITY')
 found={}
 for decision,raw in rows:
  value=json.loads(raw)
  if value.get('version')!=1 or value.get('decision_id')!=decision or value.get('status')!='COMMITTED':continue
  definition=repo.get_node(decision,'AgentDecision');saved=json.loads(definition.properties['rationale'])
  if saved['metadata'].get('investigation_id')!=inv or value['selection_sha256']!=digest(Selection.model_validate(saved['selection']).model_dump(mode='json')):raise PreconditionFailed('PATH_JOURNAL_BINDING')
  for path in (value.get('result') or {}).get('data',{}).get('paths',[]):
   if path.get('id') not in tools[decision]['graph_path_ids']:continue
   p=PathRecord.model_validate_json(json.dumps({k:v for k,v in path.items() if k!='id'}))
   if path['id'] not in {digest({k:v for k,v in path.items() if k!='id'}),'PATH-'+digest([p.node_ids,p.edge_ids])[:32]}:raise PreconditionFailed('PATH_IDENTITY')
   if not set(p.node_ids)<=node_ids or not set(p.edge_ids)<=set(edges):continue
   expected_evidence={edges[e].properties['source_evidence_id'] for e in p.edge_ids if edges[e].properties.get('source_evidence_id')}|{i for i in p.node_ids if repo.get_node(i).kind=='Evidence'}
   if set(p.evidence_ids)!=expected_evidence:raise PreconditionFailed('PATH_EVIDENCE_BINDING')
   if len(p.node_ids)!=len(p.edge_ids)+1 or len(p.directions)!=len(p.edge_ids):raise PreconditionFailed('PATH_SHAPE')
   for index,eid in enumerate(p.edge_ids):
    e=edges[eid];pair=(p.node_ids[index],p.node_ids[index+1])
    if pair!=((e.source,e.target) if p.directions[index]=='OUTGOING' else (e.target,e.source)):raise PreconditionFailed('PATH_ENDPOINT_BINDING')
   found[path['id']]={'id':path['id'],'node_ids':list(p.node_ids),'edge_ids':list(p.edge_ids),'evidence_ids':list(p.evidence_ids),'execution_id':tools[decision]['event_id']}
 if len(found)>100:raise PreconditionFailed('SELECTED_PATH_CAPACITY')
 return list(found.values())

def trace_key(value):
 return timestamp(value['timestamp']).strftime('%Y-%m-%dT%H:%M:%S.%fZ')+'|'+value['event_id']
