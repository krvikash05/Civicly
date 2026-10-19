import type {ApiModels} from '../generated/models.ts';
import type {ApiClient} from '../api/client.ts';
import {ApiError} from '../api/errors.ts';
export type Issue='WATERLOGGING'|'ROAD_DAMAGE'|'WASTE_ACCUMULATION';
export const issues:readonly Issue[]=['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION'];
export const issueNames:Record<Issue,string>={WATERLOGGING:'Waterlogging',ROAD_DAMAGE:'Road damage',WASTE_ACCUMULATION:'Waste accumulation'};
export function issueName(value:string){return issueNames[value as Issue]??value.replaceAll('_',' ').toLowerCase();}
export function parseIssue(value:string|null):Issue|undefined {return issues.includes(value as Issue)?value as Issue:undefined;}
export function displayStatus(value:string|null|undefined){return value?value.replaceAll('_',' ').toLowerCase():'Not recorded';}
export function displayTime(value:string){const date=new Date(value);return Number.isFinite(date.getTime())?new Intl.DateTimeFormat('en-IN',{dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Kolkata'}).format(date)+' IST':'Date unavailable';}
export const metrics=[
 {field:'completed_work_orders',label:'Work completed',icon:'clock',description:'Completion alone does not prove resolution'},
 {field:'verified_work_orders',label:'Verified outcomes',icon:'shield',description:'Orders with a verified resolution outcome'},
 {field:'active_investigations',label:'Active investigations',icon:'search',description:'Excludes completed and cancelled cases'},
 {field:'pending_approvals',label:'Awaiting a decision',icon:'file',description:'Plans with a pending approval'},
] as const;
import {SCENARIO_TITLES} from './display.ts';
export type RegisteredCase=ApiModels['ScenarioCase']&{scenarioId:string;stage:string;scenarioTitle?:string};
export function registeredCases(catalog:ApiModels['ScenarioPage'],issue?:Issue):RegisteredCase[]{
 return catalog.items.filter(row=>row.stage!=='NOT_STARTED').flatMap(row=>(row.cases??[]).filter(c=>!issue||c.issue_type===issue).map(c=>({...c,scenarioId:row.id,stage:row.stage,scenarioTitle:SCENARIO_TITLES[row.id]||(row.title&&!row.title.startsWith('Demonstration')?row.title:undefined)})));
}
export function uniqueCaseForIncident(cases:RegisteredCase[],incident:string):RegisteredCase|undefined{
 const matches=cases.filter(c=>c.incident_id===incident);return matches.length>0?matches[0]:undefined;
}
export function caseHref(values:{issue?:string;incident?:string;investigation?:string;section?:string}){
 const query=new URLSearchParams(Object.entries(values).filter(([,v])=>!!v) as [string,string][]);return '/investigations'+(query.size?'?'+query:'')+'#case-workspace';
}
export type SelectedCase={investigation:ApiModels['InvestigationDTO']|null;incidents:ApiModels['IncidentDTO'][]};
export async function loadSelectedCase(client:ApiClient,selection:{investigation?:string;incident?:string;issue?:Issue},signal?:AbortSignal):Promise<SelectedCase>{
 if(selection.investigation){
  const {data:investigation}=await client.request('GET /api/v1/investigations/{id}',{params:{id:selection.investigation},signal});
  const allIds=[...investigation.incident_ids,...investigation.historical_incident_ids];
  if(selection.incident&&!allIds.includes(selection.incident))throw new ApiError('CONTRACT_MISMATCH');
  const idsToFetch=Array.from(new Set(allIds));
  const incidents=await Promise.all(idsToFetch.map(async id=>(await client.request('GET /api/v1/incidents/{id}',{params:{id},signal})).data));
  if(selection.issue&&!incidents.some(i=>i.issue_type===selection.issue))throw new ApiError('SELECTION_MISMATCH');
  return {investigation,incidents};
 }
 if(selection.incident){const {data}=await client.request('GET /api/v1/incidents/{id}',{params:{id:selection.incident},signal});if(data.id!==selection.incident||selection.issue&&data.issue_type!==selection.issue)throw new ApiError('SELECTION_MISMATCH');return {investigation:null,incidents:[data]};}
 throw new ApiError('CLIENT_VALIDATION');
}
