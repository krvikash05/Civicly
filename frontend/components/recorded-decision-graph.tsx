'use client';
import {useState} from 'react';
import type {GraphSubgraphDTO} from '../lib/generated/models';
import {focusDecisionPath,pathExplanation,type RecordedGraphStep} from '../lib/read/decision-paths';
import {translateRelationshipType} from '../lib/read/graph';
import {cleanTextIdentifiers,translateStatus,translateToolAction} from '../lib/read/display';
import {FalkorDBCanvasView,GraphCaption} from './falkordb-canvas-view';
import {TechnicalDetails} from './technical-details';

type Props={subgraph:GraphSubgraphDTO;steps:RecordedGraphStep[];selectedPathId:string|null;onSelectPath:(id:string)=>void;onSelectEvidenceId:(id:string)=>void;isExpanded:boolean;onToggleExpand:()=>void};
export function RecordedDecisionGraph({subgraph,steps,selectedPathId,onSelectPath,...canvasProps}:Props){
 const [focusedFor,setFocusedFor]=useState<string|null>(null);
 const step=steps.find(s=>s.path.id===selectedPathId);
 const full=!step||focusedFor!==step.path.id;
 const explanation=step?pathExplanation(subgraph,step.path):null;
 const graph=step&&!full?focusDecisionPath(subgraph,step.path):subgraph;
 return (
  <section className="graph-decision-guide" aria-label="How FalkorDB informed a recorded step">
   <h3>How FalkorDB informed this step</h3>
   {step&&explanation?<>
    <label htmlFor="recorded-graph-step">Choose a recorded lookup</label>
    <select id="recorded-graph-step" value={step.path.id} onChange={e=>onSelectPath(e.target.value)}>
     {steps.map((s,i)=><option key={s.path.id} value={s.path.id}>{i+1}. {pathExplanation(subgraph,s.path).name(s.path.node_ids[0])} · {s.path.node_ids.length} records</option>)}
    </select>
   </>:null}
   <div className="graph-guide-visual">
    <FalkorDBCanvasView key={(step?.path.id??'context')+':'+full} subgraph={graph} selectedDecisionPathId={step?.path.id??null} focusedPath={!!step&&!full} showCaption={false} {...canvasProps}/>
   </div>
   {step&&explanation?<>
    <div className="graph-guide-controls"><button type="button" className="button secondary" onClick={()=>setFocusedFor(full?step.path.id:null)}>{full?'Focus on this path':'Show wider case graph'}</button><span>{full?'Wider case context':`${graph.nodes.length} linked records · ${graph.edges.length} connections`}</span></div>
    <div className="graph-guide-section"><h4>What was being checked</h4><p>{cleanTextIdentifiers(step.decision.rationale_summary??'The saved lookup has no recorded rationale.').replaceAll('state.as_of','the recorded time cutoff')}</p></div>
    <div className="graph-guide-section"><h4>What the graph connected</h4><p>{explanation.summary}</p>
     <ul className="graph-guide-connections">{subgraph.edges.filter(e=>step.path.edge_ids.includes(e.id)).map(e=><li key={e.id}>
      <span>{explanation.name(e.source)} <strong>→ {translateRelationshipType(e.type).toLowerCase()} →</strong> {explanation.name(e.target)}</span>
      <small>{e.verification_status==='RECORDED_ASSOCIATION_NOT_CAUSATION'?'Recorded link · cause requires evidence':translateStatus(e.verification_status)}</small>
     </li>)}</ul>
    </div>
    <div className="graph-guide-section"><h4>Next recorded choice</h4>{step.next?<><strong>{step.next.tool_name?translateToolAction(step.next.tool_name):translateStatus(step.next.status)}</strong><p>{cleanTextIdentifiers(step.next.rationale_summary??'No rationale was recorded for this choice.')}</p></>:<p>No later choice is included in the loaded activity.</p>}</div>
    <GraphCaption subgraph={graph} selectedDecisionPathId={step.path.id} focusedPath={!full}/>
    <p className="graph-guide-reservation">{explanation.reservation}</p>
    <div className="graph-guide-sources">{subgraph.nodes.filter(n=>step.path.node_ids.includes(n.id)&&(n.kind==='Evidence'||n.labels.includes('Evidence'))).map(n=><button type="button" key={n.id} className="chip chip-evidence" onClick={()=>canvasProps.onSelectEvidenceId(n.id)}>Open linked evidence</button>)}</div>
    <TechnicalDetails title="Original lookup and path references" items={[
     {label:'Recorded tool',value:<code>{step.lookup.tool_name}</code>},
     {label:'Recorded activity',value:<span>{step.lookup.execution_mode==='LIVE_GEMINI'?'Civicly’s AI':step.lookup.execution_mode?.includes('SCRIPT')||step.lookup.execution_mode?.includes('DETERMINISTIC')?'Development activity':'Recorded execution'}</span>},
     {label:'Recorded at',value:<span>{step.lookup.timestamp}</span>},
     {label:'Decision',value:<code>{step.decision.event_id}</code>},
     {label:'Original recorded question',value:<span>{step.decision.rationale_summary}</span>},
     {label:'Path',value:<code>{step.path.id}</code>},
    ]}/>
   </>:<p>No saved lookup can be matched to a complete path in this graph view. The graph above shows available case context; recorded activity may contain paths outside this bounded view.</p>}
   {!step&&<GraphCaption subgraph={graph}/>}
  </section>
 );
}
