import type {AgentTracePage, CaseMemoryDTO, HypothesisDTO, PlanDTO, WorkOrderDTO, OutcomeDTO} from '../generated/models.ts';
import {translateCauseCode, translateActionType} from './display.ts';

type TakeawayInput = {
  stage:number;
  report?:string|null;
  location?:string;
  trace?:AgentTracePage|null;
  hypotheses?:HypothesisDTO[];
  plan?:PlanDTO|null;
  orders?:WorkOrderDTO[];
  outcomes?:OutcomeDTO[];
  memory?:CaseMemoryDTO|null;
  investigationId?:string;
};
/** Summarize loaded records only. Completion, supported causes and closure are separate. */
export function stageTakeaway(input:TakeawayInput){
  const {stage,report,location,trace,hypotheses=[],plan,orders=[],outcomes=[],memory,investigationId}=input;
  const currentOrders=orders.filter(w=>w.plan_id===plan?.plan_id);
  const completed=currentOrders.filter(w=>w.status==='COMPLETED');
  if(stage===0)return {title:'Start with what was reported',text:report?`${report}${location?` Location: ${location}.`:''}`:'The linked report description is not available yet; the cause has not been established by a report alone.'};
  if(stage===1){
    const reads=trace?.items.filter(e=>e.kind==='TOOL'&&e.status==='SUCCESS'&&e.validated_output===true)??[];
    if(trace?.recovery_required)return {title:'An earlier operation needs review',text:'The saved investigation contains an uncertain operation. Its outcome must be reconciled before the investigation can safely continue.'};
    return {title:reads.length?'Follow the recorded checks':'No completed checks are shown yet',text:reads.length?`${reads.length} validated tool results are recorded. Follow the questions, returned evidence and decisions below to see how the investigation developed.`:'The available activity does not establish a completed tool check. Review any recorded pause or evidence request below.'};
  }
  if(stage===2){
    const assessed=hypotheses.map(h=>({h,status:h.assessment_history?.find(a=>a.id===h.current_assessment_id)?.assessment??h.status}));
    const supported=assessed.filter(a=>a.status==='SUPPORTED'||a.status==='VERIFIED');
    const names=[...new Set(supported.map(a=>translateCauseCode(a.h.cause_code).title))];
    const challenged=assessed.filter(a=>a.status==='CONTRADICTED'||a.status==='REJECTED').length;
    return {title:names.length?'The evidence narrows the possible causes':'The cause still needs evidence',text:names.length?`Recorded evidence supports: ${names.slice(0,3).join('; ')}${names.length>3?'; and other assessed explanations':''}. ${supported.some(a=>a.status==='SUPPORTED')?'Support is not proof of the cause.':'These explanations are recorded as verified; review their sources below.'}${challenged?' Other explanations have been challenged; their history remains below.':''}`:'No supported or verified explanation appears in the loaded assessments. Review the alternatives and missing observations before recommending work.'};
  }
  if(stage===3){
    if(!plan)return {title:'A response has not been planned yet',text:'No current plan was returned. Evidence, responsibility and applicable procedures must be checked before work can be proposed.'};
    const actions=[...new Set(plan.draft.tasks.map(t=>translateActionType(t.action_type)))];
    const scope=actions.slice(0,3).join('; ')+(actions.length>3?'; further planned work':'');
    const approved=currentOrders.some(w=>Boolean(w.authorized_by));
    return {title:approved?'The response has recorded authorization':plan.status==='PENDING_APPROVAL'?'The proposed response awaits a decision':'Review the proposed response',text:`${scope?`Planned actions: ${scope}. `:''}${approved?'Approval applies to the recorded scope; safety checks and task prerequisites still govern the work.':plan.status==='PENDING_APPROVAL'?'An authorized person must approve this exact plan before work starts.':'A saved plan does not itself authorize work; review its approval decision below.'}`};
  }
  if(stage===4)return {title:completed.length===currentOrders.length&&completed.length?'The recorded work is complete':currentOrders.length?'Follow the authorized work':'No work orders are recorded for this plan',text:currentOrders.length?`${completed.length} of ${currentOrders.length} work orders for the current plan are completed. Separate follow-up must establish whether the problem was resolved.`:'Review requested inspections and the plan’s approval before expecting field work. No completed intervention is established here.'};
  const latestOutcomes=outcomes.filter(o=>!outcomes.some(other=>other.work_order_id===o.work_order_id&&Date.parse(other.evaluated_at)>Date.parse(o.evaluated_at)));
  const verified=latestOutcomes.some(o=>o.assessment_status==='RESOLUTION_VERIFIED'&&o.case_closed&&o.evidence_ids.length>0&&completed.some(w=>w.id===o.work_order_id));
  const retained=memory?.source_investigation_id===investigationId;
  return {title:verified?'Follow-up verified resolution for this episode':'The outcome still needs verification',text:(verified?'A recorded follow-up links evidence to a completed work order and closes this episode.':'The loaded follow-up does not establish a verified closure. Completed work or a utility-only check is not enough.')+(retained?' This episode’s retained history is available below for future investigations.':' Retained episode memory is not established in this view.')};
}
