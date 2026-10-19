import type {PlanDTO, WorkOrderDTO, OutcomeDTO} from '../generated/models.ts';
import {taskForOrder} from './workflow.ts';
import {translateActionType, translateDepartment, translateRole, translateStatus} from './display.ts';
import {explainOutcome} from './memory.ts';

export type ResponseMilestone = {
  id:string;
  title:string;
  status:string;
  tone:'recorded'|'pending';
  summary:string;
  section:number;
  records:{id:string;title:string;detail:string;status?:string;at?:string;evidenceIds?:string[]}[];
};

/** A milestone view, not an invented event history. Only follow-up supplies dates. */
export function responseTimeline(plan:PlanDTO|null,orders:WorkOrderDTO[]|null,outcomes:OutcomeDTO[]|null):ResponseMilestone[]{
  const scoped=plan?(orders??[]).filter(w=>w.plan_id===plan.plan_id):[];
  const completed=scoped.filter(w=>w.status==='COMPLETED');
  const authorized=scoped.filter(w=>Boolean(w.authorized_by));
  const followups=(outcomes??[]).filter(o=>scoped.some(w=>w.id===o.work_order_id))
    .sort((a,b)=>(Date.parse(a.evaluated_at)||0)-(Date.parse(b.evaluated_at)||0)||a.id.localeCompare(b.id));
  const latest=followups.filter(o=>!followups.some(n=>n.work_order_id===o.work_order_id&&Date.parse(n.evaluated_at)>Date.parse(o.evaluated_at)));
  const verified=latest.some(o=>o.case_closed&&o.assessment_status==='RESOLUTION_VERIFIED'&&o.evidence_ids.length>0&&completed.some(w=>w.id===o.work_order_id));
  const workTitle=(w:WorkOrderDTO)=>{const task=taskForOrder(plan,w);return task?translateActionType(task.action_type):'Recorded work order';};
  return [
    {id:'recommendation',title:'Recommended response',section:3,tone:plan?'recorded':'pending',
      status:plan?'Plan recorded':'Not available',
      summary:plan?'The current plan sets out the proposed actions and their prerequisites.':'No current plan was returned. Evidence and responsibility must be checked before proposing work.',
      records:plan?.draft.tasks.map(t=>({id:t.id,title:translateActionType(t.action_type),detail:translateDepartment(t.department_id)}))??[]},
    {id:'authorization',title:'Human authorization',section:3,tone:authorized.length?'recorded':'pending',
      status:orders===null?'Records unavailable':authorized.length?'Authorization recorded':plan?.status==='PENDING_APPROVAL'?'Awaiting a decision':'Not established',
      summary:orders===null?'Work authorization records could not be read in this view.':authorized.length?'Work orders reference approval of this plan. Approver details and decision time are restricted in this view; safety conditions remain separate.':plan?.status==='PENDING_APPROVAL'?'An authorized approver must decide on this exact plan before work can start.':'The loaded work records do not establish authorization. A saved plan or its lifecycle label alone is not an approval decision.',records:[]},
    {id:'work',title:'Simulated work',section:4,tone:completed.length?'recorded':'pending',
      status:orders===null?'Records unavailable':scoped.length?`${completed.length} of ${scoped.length} completed`:'No work returned',
      summary:orders===null?'Work progress is unavailable.':scoped.length?'These are the current recorded work statuses. Completion times are not available in this view; this list does not establish the order of execution.':'No work orders were returned for the current plan. Approval and prerequisites must be satisfied before work can proceed.',
      records:scoped.map(w=>({id:w.id,title:workTitle(w),detail:`${translateDepartment(w.department_id)} · ${translateRole(w.assignee_id)}`,status:translateStatus(w.status)}))},
    {id:'followup',title:'Independent follow-up',section:5,tone:verified?'recorded':'pending',
      status:outcomes===null?'Records unavailable':verified?'Resolution verified':'Verification still needed',
      summary:outcomes===null?'Follow-up records could not be read.':verified?'Evidence-backed follow-up closed this episode after completed work. The dated assessments below preserve the checks along the way.':'Completed work does not establish resolution. Review the dated assessments and remaining observation requirements.',
      records:followups.map(o=>({id:o.id,title:translateStatus(o.assessment_status),detail:explainOutcome(o),at:o.evaluated_at,evidenceIds:o.evidence_ids}))},
  ];
}
