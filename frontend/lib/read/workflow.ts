/** Human-readable summaries of recorded state. A saved trace is never liveness proof. */
import type {ApiModels, InvestigationDTO, AgentTracePage, PlanDTO, OutcomeDTO, WorkOrderDTO, IncidentDTO, ComplaintDTO, HypothesisDTO} from '../generated/models.ts';
import type {ApiClient} from '../api/client.ts';
import {ApiError} from '../api/errors.ts';
import {translateStatus, translateRole, translateCauseCode, translateLocation,translateActionType,translateDepartment} from './display.ts';
import {issueName, type Issue, type RegisteredCase} from './cases.ts';

/** Only source-linked reports and loaded hypotheses contribute to this introduction. */
export function incidentIntroduction(incident:IncidentDTO, reports:ComplaintDTO[], hypotheses:HypothesisDTO[]=[]){
 const linked=reports.filter(r=>incident.complaint_ids.includes(r.id)&&r.incident_id===incident.id);
 const plain:Record<string,string>={
  'inlet cleaned twice but junction floods in ordinary rain':'The report describes flooding during ordinary rain, even after the drain entrance was cleaned twice.',
  'subsidence, recurring potholes and repeated low pressure complaints':'The report describes sinking road surfaces, returning potholes and repeated complaints about low water pressure.',
  'road repaired twice and pipe lies underneath; leak unverified':'The report says road damage returned after two repairs. It also mentions a pipe beneath the road, but does not establish that it is leaking.',
  'overflow every market day; service schedule says daily':'The report describes waste overflowing on market days, although the collection schedule says pickups should happen daily.',
  'trash repeatedly appears beside accessible collection point':'The report describes waste repeatedly appearing beside a collection point that can be reached by collection crews.',
 };
 const report=linked[0]?.description;
 const causes=[...new Set(hypotheses.map(h=>translateCauseCode(h.cause_code).title))];
 const focus=causes.length?`Possible explanations being compared: ${causes.slice(0,3).join('; ')}${causes.length>3?'; and other recorded explanations':''}.`:{
  WATERLOGGING:'The investigation checks how water drains from the affected area and what evidence could explain the flooding.',
  ROAD_DAMAGE:'The investigation checks the road, the ground beneath it and relevant utility evidence to understand the damage.',
  WASTE_ACCUMULATION:'The investigation checks collection records and site observations to understand why waste is building up.',
 }[incident.issue_type]??'The investigation reviews the report and connected evidence to understand what happened.';
 return {report:report?(plain[report]??report):null,focus};
}

export function currentPlan(plans:PlanDTO[], id?:string|null):PlanDTO|null {
 if(id)return plans.find(p=>p.plan_id===id)??null;
 return [...plans].sort((a,b)=>b.version-a.version)[0]??null;
}

/** Read-only overview: report, assessment, authorization and outcome stay distinct. */
export function reportJourney(issue:string,hypotheses:HypothesisDTO[]|null,plan:PlanDTO|null,orders:WorkOrderDTO[]|null,outcomes:OutcomeDTO[]|null){
 const why:Record<string,string>={
  WATERLOGGING:'The key question is why water is collecting here. Drainage connections and field observations help distinguish a blockage from insufficient drainage capacity.',
  ROAD_DAMAGE:'The key question is what is damaging the road, so the response addresses the cause as well as the surface. A nearby pipe alone does not establish a leak.',
  WASTE_ACCUMULATION:'The key question is why waste keeps building up. Collection records and dated site observations help distinguish missed service, excess demand and later dumping.',
 };
 const findings=[...new Set(hypotheses?.map(h=>{
  const name=translateCauseCode(h.cause_code).title;
  const assessment=h.assessment_history?.find(a=>a.id===h.current_assessment_id)?.assessment??h.status;
  if(assessment==='SUPPORTED')return `${name}: recorded evidence supports this possible explanation; it is not a verified cause.`;
  if(assessment==='CONTRADICTED'||assessment==='REJECTED')return `${name}: recorded evidence challenges this explanation.`;
  if(assessment==='VERIFIED')return `${name} is recorded as verified; its supporting sources are available in Evidence.`;
  return `${name}: the recorded assessment has not established this explanation.`;
 })??[])];
 const response=plan?.draft.tasks.map(t=>`${translateActionType(t.action_type)} — ${translateDepartment(t.department_id)}`)??[];
 const scoped=plan?orders?.filter(w=>w.plan_id===plan.plan_id):null;
 const completed=scoped?.filter(w=>w.status==='COMPLETED')??[];
 const verified=plan&&outcomes?.some(o=>o.case_closed&&o.assessment_status==='RESOLUTION_VERIFIED'&&o.evidence_ids.length>0&&completed.some(w=>w.id===o.work_order_id));
 const approval=plan?(scoped?.some(w=>w.authorized_by)?'Work was authorized under this plan. Its recorded tasks are listed below.':plan.status==='PENDING_APPROVAL'?'The proposed plan is awaiting an authorized approval.':'The plan lists proposed tasks. Review Plan & approval for the recorded approval decision before starting work.'):'No action plan is available in the loaded records.';
 const work=orders===null?'Work records are not available in this view yet.':!plan?'No work is linked here to a current plan.':scoped?.length?`${completed.length} of ${scoped.length} recorded work orders are completed. Work completion is separate from resolving the problem.`:'No work orders were returned for this plan.';
 const followup=verified?'Independent follow-up recorded a verified resolution for this episode. Review Monitoring & memory for the dated observations and retained history.':outcomes===null?'Follow-up records are not available in this view yet.':'A verified resolution is not established by the loaded follow-up records. Further evidence or a suitable observation period may still be needed.';
 return {why:why[issue]??'The investigation compares the report with connected evidence before deciding what action is justified.',findings,response,approval,work,followup};
}
export function taskForOrder(plan:PlanDTO|null|undefined,order:WorkOrderDTO){
 const binding=plan?.task_bindings?.find(t=>t.task_id===order.task_id);
 return binding?plan?.draft.tasks.find(t=>t.id===binding.local_task_id):undefined;
}
export function describeWork(action?:string){
 const descriptions:Record<string,string>={
  UTILITY_ISOLATION:'Isolate the affected water pipe so repair work can proceed under the plan’s safety conditions.',
  UTILITY_LEAK_REPAIR:'Repair the leak in the affected pipe. A separate check must assess whether the repair stopped the leak.',
  SUBGRADE_REPAIR:'Repair the supporting ground beneath the damaged road. Later observations are needed to assess whether the road damage returns.',
  DRAIN_BLOCKAGE_CLEARANCE:'Remove the obstruction from the drain to help restore water flow. Follow-up during comparable rain checks whether flooding returns.',
  MISSED_PICKUP_RECOVERY:'Carry out the missed waste collection. Later collection records and site observations check whether waste builds up again.',
  INSPECTION:'Inspect the assigned area and record observations to help assess the possible cause.',
 };
 return action?descriptions[action]??'Carry out the work defined in the approved plan, subject to its recorded prerequisites.':'The work description is not available in the loaded task records.';
}
export function scopedOrders(orders:WorkOrderDTO[],planIds:string[]){return orders.filter(w=>planIds.includes(w.plan_id));}
export function caseProgress(inv:InvestigationDTO,trace?:AgentTracePage|null,plan?:PlanDTO|null,outcomes:OutcomeDTO[]=[],orders:WorkOrderDTO[]=[]){
 const modes=new Set(trace?.items.map(e=>e.execution_mode).filter(Boolean));
 const live=modes.has('LIVE_GEMINI');const other=[...modes].some(m=>m!=='LIVE_GEMINI');
 const origin=live?(other?'Civicly’s AI and development activity recorded':'Civicly’s AI investigation recorded'):modes.size?'Development test activity recorded':'Agent activity not established';
 const originDetail=live?'The saved trace contains real activity from Civicly’s AI.':modes.size?'This trace contains development or scripted activity; it is not evidence of live activity from Civicly’s AI.':'No available trace establishes how this investigation was run.';
 const closed=outcomes.some(o=>o.case_closed&&orders.some(w=>w.id===o.work_order_id&&w.plan_id===plan?.plan_id));
 let next='Review the case';let detail='Review the recorded evidence and decide whether an authorized follow-up is needed.';
 if(inv.status==='COMPLETED'){next=closed?'Review the verified outcome':'Review the completed investigation';detail=closed?'The recorded follow-up closed this episode. Review its evidence and retained memory.':'The investigation is marked complete. Check the outcome record before calling the problem resolved.';}
 else if(inv.status==='CANCELLED'){next='Investigation cancelled';detail='Review the retained history; no automatic continuation is implied.';}
 else if(plan?.status==='PENDING_APPROVAL'){next='Awaiting plan approval';detail='An authorized approver must review the exact plan version, scope and assignees before work can start.';}
 else if(plan?.status==='DRAFT'){next='Review the proposed plan';detail='The draft needs review and submission before an approver can authorize it.';}
 else if(plan?.status==='MONITORING'||inv.status==='MONITORING'){next='Review independent follow-up';detail='Work completion is recorded. Separate observations must establish whether the problem persists.';}
 else if(plan?.status==='APPROVED'||plan?.status==='IN_EXECUTION'){next='Follow the approved work';detail='Check assigned work, inspection evidence and prerequisites. Approval does not satisfy unmet safety or dependency conditions.';}
 else if(trace?.pause_reason==='TOKEN_BUDGET'||trace?.pause_reason==='BUDGET'){next='Agent paused at its usage limit';detail='The saved run reached its allowed usage. Review existing findings; this screen does not resume it or raise its budget.';}
 else if(trace?.pause_reason==='MISSING_EVIDENCE'||inv.pending_inspection_ids.length){next='Awaiting inspection evidence';detail='Review the requested inspections and add independently reviewed findings through the authorized workflow.';}
 else if(trace?.pause_reason==='HUMAN_REVIEW'){next='Awaiting investigator review';detail='Review the saved findings and any proposed plan before deciding what happens next.';}
 else if(trace?.pause_reason==='DEPENDENCY_UNAVAILABLE'||trace?.pause_reason==='DEPENDENCY'){next='Investigation paused';detail='A required service or source could not be used. The presenter must review the failure before continuing.';}
 if(trace?.recovery_required){next='Operator review required';detail='An earlier operation has an uncertain outcome. Keep its original request identity; do not replay it as a new action.';}
 const pause=trace?.pause_reason&&trace.pause_reason!=='NONE'?translateStatus(trace.pause_reason):'No pause recorded';
 return {status:inv.status==='COMPLETED'?'Investigation complete':translateStatus(inv.status),origin,originDetail,next,detail,pause,role:trace?.current_agent_role?translateRole(trace.current_agent_role):'No current role recorded'};
}

export function incidentCardGlimpse(incident:IncidentDTO,reports:ComplaintDTO[]){
 const description=reports.find(r=>r.incident_id===incident.id&&(incident.complaint_ids??[]).includes(r.id))?.description.trim();
 const short:Record<string,string>={
  'inlet cleaned twice but junction floods in ordinary rain':'Flooding despite two drain cleanings',
  'subsidence, recurring potholes and repeated low pressure complaints':'Sinking road, recurring potholes and low water pressure',
  'road repaired twice and pipe lies underneath; leak unverified':'Road repaired twice; pipe leak unverified',
  'overflow every market day; service schedule says daily':'Market-day overflow despite a daily collection schedule',
  'trash repeatedly appears beside accessible collection point':'Waste repeatedly appears beside a collection point',
 };
 const text=description?(short[description]??(description.length>110?description.slice(0,107).trimEnd()+'…':description)):null;
 return {glimpse:text?`Reported: ${text}`:'Report details not available',location:incident.location_id?translateLocation(incident.location_id):'Location not recorded'};
}
export type DirectoryCase={investigation_id:string;incident_id:string;incident_ids:string[];issue_type:string;stage:string;title?:string;scenarioTitle?:string;glimpse?:string;location?:string};
/** Category comes from linked IncidentDTOs, never a default or an ID substring. */
export function directoryCases(investigations:InvestigationDTO[],incidents:IncidentDTO[],scenarios:RegisteredCase[],issue?:Issue,reports:ComplaintDTO[]=[]):DirectoryCase[]{
 const rows:DirectoryCase[]=investigations.flatMap(inv=>{
  const ids=[...new Set([...inv.incident_ids,...inv.historical_incident_ids])];
  const linked=incidents.filter(i=>ids.includes(i.id)&&(!issue||i.issue_type===issue));
  const categories=[...new Set(linked.map(i=>i.issue_type))];
  return categories.map(category=>{const group=linked.filter(i=>i.issue_type===category);const sc=scenarios.find(c=>c.investigation_id===inv.id&&c.issue_type===category);
   return {investigation_id:inv.id,incident_id:group[0].id,incident_ids:group.map(i=>i.id),issue_type:category,stage:inv.status,title:`${issueName(category)} investigation`,scenarioTitle:sc?.scenarioTitle,...incidentCardGlimpse(group[0],reports)};});
 });
 for(const sc of scenarios)if(!rows.some(r=>r.investigation_id===sc.investigation_id)&&(!issue||sc.issue_type===issue))rows.push({...sc,incident_ids:[sc.incident_id]});
 return rows;
}
export async function loadDirectory(client:ApiClient,scenarios:RegisteredCase[],issue?:Issue,signal?:AbortSignal){
 const {data}=await client.request('GET /api/v1/investigations',{query:{issue,limit:20},signal});
 const ids=[...new Set(data.items.flatMap(i=>[...i.incident_ids,...i.historical_incident_ids]))];
 if(ids.length>60)throw new ApiError('READ_CAPACITY');
 const incidents=await Promise.all(ids.map(async id=>(await client.request('GET /api/v1/incidents/{id}',{params:{id},signal})).data));
 const reportIds=[...new Set(incidents.map(i=>i.complaint_ids[0]).filter(Boolean))];
 const reports=await Promise.all(reportIds.map(async id=>(await client.request('GET /api/v1/complaints/{id}',{params:{id},signal})).data));
 return {items:directoryCases(data.items,incidents,scenarios,issue,reports),next_cursor:data.next_cursor,total_count:data.total_count};
}

/** Never guess a native task or an eligible assignee from a department name. */
export function approvalAssignments(plan:PlanDTO){
 const bindings=plan.task_bindings??[];
 if(bindings.length!==plan.draft.tasks.length||!bindings.length)throw new ApiError('DEPENDENCY_BLOCKED');
 return bindings.map(binding=>{
  const task=plan.draft.tasks.find(t=>t.id===binding.local_task_id);
  if(!task||binding.eligible_assignee_ids.length!==1||task.action_type!==binding.action_type||task.department_id!==binding.department_id||JSON.stringify([...task.target_ids].sort())!==JSON.stringify([...binding.target_ids].sort()))throw new ApiError('DEPENDENCY_BLOCKED');
  return {task_id:binding.task_id,action_type:binding.action_type,target_ids:binding.target_ids,department_id:binding.department_id,assignee_id:binding.eligible_assignee_ids[0]};
 });
}
