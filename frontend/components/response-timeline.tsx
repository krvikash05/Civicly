'use client';

import type {PlanDTO,WorkOrderDTO,OutcomeDTO} from '../lib/generated/models';
import {responseTimeline} from '../lib/read/response-timeline';
import {displayTime} from '../lib/read/cases';

export function ResponseTimeline({plan,orders,outcomes,onSelectStage,onSelectEvidence}:{
  plan:PlanDTO|null;orders:WorkOrderDTO[]|null;outcomes:OutcomeDTO[]|null;
  onSelectStage:(stage:number)=>void;onSelectEvidence:(id:string)=>void;
}){
  const milestones=responseTimeline(plan,orders,outcomes);
  return <section className="response-timeline" aria-label="Response timeline">
    <header><span className="response-timeline-eyebrow">From recommendation to follow-up</span>
      <h3>The response at a glance</h3>
      <p>The current plan’s recorded milestones. Field work and follow-up observations are simulated.</p>
    </header>
    <ol className="response-milestones">
      {milestones.map((step,i)=><li key={step.id} className={`response-milestone ${step.tone}`}>
        <span className="response-milestone-number" aria-hidden="true">{i+1}</span>
        <div className="response-milestone-body">
          <div className="response-milestone-top"><h4>{step.title}</h4><span>{step.status}</span></div>
          <p>{step.summary}</p>
          {step.records.length>0&&<details className="response-records"><summary>{step.id==='recommendation'?'See the recommended actions':step.id==='work'?'See work progress':'See dated follow-up'} ({step.records.length})</summary>
            <ul>{step.records.map(record=><li key={record.id}>
              <div className="response-record-top"><strong>{record.title}</strong>{record.status&&<span>{record.status}</span>}</div>
              {record.at&&<time dateTime={record.at}>{displayTime(record.at)}</time>}
              <p>{record.detail}</p>
              {Boolean(record.evidenceIds?.length)&&<button type="button" className="text-button" onClick={()=>onSelectEvidence(record.evidenceIds![0])}>Review supporting evidence</button>}
            </li>)}</ul>
          </details>}
          <button type="button" className="text-button response-stage-link" onClick={()=>onSelectStage(step.section)}>{step.section===3?'View plan & approval':step.section===4?'View work details':'View monitoring & memory'} <span aria-hidden="true">→</span></button>
        </div>
      </li>)}
    </ol>
  </section>;
}
