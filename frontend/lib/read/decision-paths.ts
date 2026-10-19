import type {AgentTracePage,AgentTraceEvent,GraphSubgraphDTO,DecisionPath} from '../generated/models.ts';
import {formatEntityDisplayName} from './display.ts';

export type RecordedGraphStep={path:DecisionPath;lookup:AgentTraceEvent;decision:AgentTraceEvent;next:AgentTraceEvent|null};
const tool=(name:string|null|undefined)=>(name??'').split('::').pop();

/** Only paths bound to a successful saved lookup and present in this graph view. */
export function recordedGraphSteps(trace:AgentTracePage|null|undefined,graph:GraphSubgraphDTO):RecordedGraphStep[]{
 const nodes=new Set(graph.nodes.map(n=>n.id));const edges=new Map(graph.edges.map(e=>[e.id,e]));
 const decisions=(trace?.items??[]).filter(e=>e.kind==='DECISION');
 const steps:RecordedGraphStep[]=[];
 for(const lookup of trace?.items??[]){
  if(lookup.kind!=='TOOL'||lookup.status!=='SUCCESS'||lookup.validated_output!==true||!lookup.decision_id||!lookup.tool_name)continue;
  const decision=decisions.find(d=>d.event_id===lookup.decision_id&&d.status==='READ'&&d.investigation_id===lookup.investigation_id&&d.execution_mode===lookup.execution_mode&&Date.parse(d.timestamp)<=Date.parse(lookup.timestamp)&&tool(d.tool_name)===tool(lookup.tool_name));
  if(!decision)continue;
  const paths=(graph.decision_paths??[]).filter(p=>{
   if(p.execution_id!==lookup.event_id||!lookup.graph_path_ids?.includes(p.id)||!p.edge_ids.length||p.node_ids.length!==p.edge_ids.length+1||!p.node_ids.every(id=>nodes.has(id)))return false;
   return p.edge_ids.every((id,index)=>{
    const e=edges.get(id),a=p.node_ids[index],b=p.node_ids[index+1];
    return e&&((e.source===a&&e.target===b)||(e.source===b&&e.target===a));
   });
  }).sort((a,b)=>b.edge_ids.length-a.edge_ids.length);
  // Prefer the fullest available source trail for each lookup, not its prefixes.
  if(!paths.length)continue;
  const next=decisions.filter(d=>d.investigation_id===lookup.investigation_id&&Date.parse(d.timestamp)>Date.parse(lookup.timestamp)).sort((a,b)=>Date.parse(a.timestamp)-Date.parse(b.timestamp))[0]??null;
  steps.push({path:paths[0],lookup,decision,next});
 }
 return steps.sort((a,b)=>Date.parse(a.lookup.timestamp)-Date.parse(b.lookup.timestamp));
}

/** Retain exact returned entities/edges and provenance; never invent connectors. */
export function focusDecisionPath(graph:GraphSubgraphDTO,path:DecisionPath):GraphSubgraphDTO{
 const nodes=new Set(path.node_ids),edges=new Set(path.edge_ids);
 return {...graph,nodes:graph.nodes.filter(n=>nodes.has(n.id)),edges:graph.edges.filter(e=>edges.has(e.id)),decision_paths:[path],decision_path_ids:[path.id]};
}

export function pathExplanation(graph:GraphSubgraphDTO,path:DecisionPath){
 const name=(id:string)=>{const n=graph.nodes.find(n=>n.id===id);return formatEntityDisplayName({id,kind:n?.kind,displayLabel:n?.display_label}).primary;};
 const edges=graph.edges.filter(e=>path.edge_ids.includes(e.id));
 const inspection=edges.find(e=>e.type==='INSPECTS');
 const report=inspection&&edges.find(e=>e.type==='PRODUCED'&&e.source===inspection.source);
 const summary=inspection&&report?`FalkorDB connects ${name(inspection.target)} to its inspection and the report that inspection produced.`:'FalkorDB returned the recorded connections between these case records.';
 const reservation=edges.some(e=>e.verification_status==='CANDIDATE')?'This trail includes a candidate connection that still needs verification.':edges.some(e=>e.verification_status==='RECORDED_ASSOCIATION_NOT_CAUSATION')?'Inspection and report links show where evidence came from. Reviewed findings are needed to assess the cause.':'Relationship status is shown for each connection. Cause assessment also requires reviewed findings.';
 return {name,summary,reservation};
}
