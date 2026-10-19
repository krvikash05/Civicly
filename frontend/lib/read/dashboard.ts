import type {ApiClient} from '../api/client.ts';
import type {InvestigationDTO,WorkOrderDTO} from '../generated/models.ts';
import {ApiError} from '../api/errors.ts';
import {caseHref,issueName} from './cases.ts';
import {incidentCardGlimpse,taskForOrder} from './workflow.ts';
import {translateActionType,translateDepartment,formatShortIdentifier} from './display.ts';
export type MetricKind='active_investigations'|'pending_approvals'|'completed_work_orders'|'verified_work_orders';
export type MetricRow={id:string;title:string;detail:string;status:string;href:string};
export function activeCases(items:InvestigationDTO[]){return items.filter(i=>!['COMPLETED','CANCELLED'].includes(i.status));}
export function matchingOrders(items:WorkOrderDTO[],kind:MetricKind){return items.filter(w=>kind==='verified_work_orders'?w.resolution_verified===true:w.status==='COMPLETED');}
/** Follow bounded pages instead of silently dropping records beyond the first page. */
async function pages<T>(read:(cursor?:string)=>Promise<{items:T[];next_cursor?:string|null}>){
 const items:T[]=[];let cursor:string|undefined;const seen=new Set<string>();
 for(let page=0;page<10;page++){
  const data=await read(cursor);items.push(...data.items);
  if(!data.next_cursor)return items;
  if(seen.has(data.next_cursor))throw new ApiError('READ_CAPACITY');
  seen.add(data.next_cursor);cursor=data.next_cursor;
 }
 throw new ApiError('READ_CAPACITY');
}
export async function loadMetricRows(client:ApiClient,kind:MetricKind,signal?:AbortSignal):Promise<MetricRow[]>{
 if(kind==='active_investigations'){
  const items=activeCases(await pages(async cursor=>(await client.request('GET /api/v1/investigations',{query:{limit:50,cursor},signal})).data));
  return Promise.all(items.map(async inv=>{
   const id=inv.incident_ids[0]??inv.historical_incident_ids[0];
   if(!id)return {id:inv.id,title:'Investigation #'+formatShortIdentifier(inv.id),detail:'No linked incident was returned.',status:inv.status,href:caseHref({investigation:inv.id,section:'investigation'})};
   const incident=(await client.request('GET /api/v1/incidents/{id}',{params:{id},signal})).data;
   const reportId=incident.complaint_ids[0];
   const reports=reportId?[(await client.request('GET /api/v1/complaints/{id}',{params:{id:reportId},signal})).data]:[];
   const glimpse=incidentCardGlimpse(incident,reports);
   return {id:inv.id,title:glimpse.glimpse,detail:issueName(incident.issue_type)+' · '+glimpse.location,status:inv.status,href:caseHref({investigation:inv.id,incident:id,section:'investigation'})};
  }));
 }
 if(kind==='pending_approvals'){
  // The judge's analyst session can read plans, but cannot list/decide approvals.
  // Read the pending plans through the existing authorized read surface.
  const investigations=await pages(async cursor=>(await client.request('GET /api/v1/investigations',{query:{limit:50,cursor},signal})).data);
  const rows:MetricRow[]=[];
  for(const inv of investigations){
   const plans=await pages(async cursor=>(await client.request('GET /api/v1/investigations/{id}/plans',{params:{id:inv.id},query:{limit:50,cursor},signal})).data);
   for(const plan of plans.filter(p=>p.status==='PENDING_APPROVAL'))rows.push({id:plan.plan_id,title:issueName(plan.draft.issue)+' plan awaiting approval',detail:plan.draft.tasks.map(t=>translateActionType(t.action_type)).join(' · '),status:plan.status,href:caseHref({investigation:inv.id,section:'plan'})});
  }
  return rows;
 }
 const orders=matchingOrders(await pages(async cursor=>(await client.request('GET /api/v1/work-orders',{query:{limit:50,cursor},signal})).data),kind);
 const rows:MetricRow[]=[];
 for(const w of orders){
  const plan=(await client.request('GET /api/v1/plans/{id}',{params:{id:w.plan_id},signal})).data;
  const task=taskForOrder(plan,w);
  rows.push({id:w.id,title:task?translateActionType(task.action_type):'Work order #'+formatShortIdentifier(w.id),detail:translateDepartment(w.department_id)+' · Case #'+formatShortIdentifier(plan.investigation_id),status:kind==='verified_work_orders'?'RESOLUTION_VERIFIED':w.status,href:caseHref({investigation:plan.investigation_id,section:kind==='verified_work_orders'?'monitoring':'report'})});
 }
 return rows;
}
