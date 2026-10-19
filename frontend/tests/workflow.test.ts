import {test} from 'node:test';
import assert from 'node:assert/strict';
import type {InvestigationDTO,AgentTracePage,PlanDTO,OutcomeDTO,WorkOrderDTO,IncidentDTO,ComplaintDTO,HypothesisDTO} from '../lib/generated/models.ts';
import {caseProgress,currentPlan,directoryCases,scopedOrders,taskForOrder,approvalAssignments,incidentIntroduction,incidentCardGlimpse,reportJourney,describeWork} from '../lib/read/workflow.ts';
import {translateStatus,translateAssessment,formatMissingEvidence,cleanTextIdentifiers} from '../lib/read/display.ts';
import {loadSelectedCase} from '../lib/read/cases.ts';
import {ApiClient} from '../lib/api/client.ts';
import {activeCases,matchingOrders,loadMetricRows} from '../lib/read/dashboard.ts';
const inv=(changes:Partial<InvestigationDTO>={}):InvestigationDTO=>({id:'INV',expected_hash:'a'.repeat(64),status:'OPEN',incident_ids:['INC'],historical_incident_ids:[],active_hypothesis_ids:[],pending_inspection_ids:[],problem_cluster_id:null,current_plan_id:null,graph_revision:1,runtime_status:'DETERMINISTIC_DEVELOPMENT_ONLY_NO_LIVE_AUTHORIZATION',...changes});
const trace=(modes:string[]=['LIVE_GEMINI'],pause='HUMAN_REVIEW')=>({items:modes.map(execution_mode=>({execution_mode})),pause_reason:pause,recovery_required:false} as AgentTracePage);
const plan=(status='PENDING_APPROVAL',id='PLAN')=>({plan_id:id,status,version:1,task_bindings:[],draft:{tasks:[]}} as unknown as PlanDTO);
const outcome=(status='RESOLUTION_VERIFIED',closed=true,order='WO')=>({id:'OUT',work_order_id:order,assessment_status:status,case_closed:closed} as OutcomeDTO);
const work=(id='WO',pid='PLAN')=>({id,plan_id:pid} as WorkOrderDTO);
test('work descriptions explain purpose without inventing completion or verified results',()=>{
 assert.match(describeWork('UTILITY_ISOLATION'),/safety conditions/);
 assert.match(describeWork('UTILITY_LEAK_REPAIR'),/separate check must assess/);
 assert.match(describeWork('DRAIN_BLOCKAGE_CLEARANCE'),/comparable rain/);
 assert.match(describeWork('SUBGRADE_REPAIR'),/Later observations/);
 assert.match(describeWork('MISSED_PICKUP_RECOVERY'),/check whether waste builds up again/);
 assert.match(describeWork(),/not available/);
 assert.match(describeWork('FUTURE_ACTION'),/recorded prerequisites/);
 assert.doesNotMatch(describeWork('UTILITY_LEAK_REPAIR'),/leak has stopped|resolution verified|work completed/i);
});
test('dashboard record filters use the count definitions and separate completion from verification',()=>{
 assert.deepEqual(activeCases([inv(),inv({id:'DONE',status:'COMPLETED'}),inv({id:'CANCEL',status:'CANCELLED'}),inv({id:'MON',status:'MONITORING'})]).map(i=>i.id),['INV','MON']);
 const orders=[{...work('DONE'),status:'COMPLETED',resolution_verified:false},{...work('VERIFIED'),status:'COMPLETED',resolution_verified:true},{...work('ACTIVE'),status:'ASSIGNED',resolution_verified:false}];
 assert.deepEqual(matchingOrders(orders,'completed_work_orders').map(w=>w.id),['DONE','VERIFIED']);
 assert.deepEqual(matchingOrders(orders,'verified_work_orders').map(w=>w.id),['VERIFIED']);
});
test('pending decision drilldown follows accessible plans, paginates and links to approval section',async()=>{
 const calls:string[]=[];
 const c={request:async(key:string,opts:{query?:{cursor?:string}}={})=>{calls.push(key);return {data:key==='GET /api/v1/investigations'?{items:[inv()],next_cursor:null}:opts.query?.cursor?{items:[{...plan(),draft:{issue:'ROAD_DAMAGE',tasks:[{action_type:'SUBGRADE_REPAIR'}]}}],next_cursor:null}:{items:[],next_cursor:'NEXT'}};}} as unknown as ApiClient;
 const rows=await loadMetricRows(c,'pending_approvals');assert.equal(rows.length,1);assert.match(rows[0].href,/section=plan/);assert.ok(!calls.some(k=>k.includes('/approvals')));
});
test('dashboard drilldown refuses repeated cursors instead of claiming a complete empty list',async()=>{
 const c={request:async()=>({data:{items:[],next_cursor:'REPEAT'}})} as unknown as ApiClient;
 await assert.rejects(loadMetricRows(c,'completed_work_orders'),e=>(e as {code:string}).code==='READ_CAPACITY');
});
test('report overview separates supporting evidence, approval and completion from resolution',()=>{
 const p={...plan(),approval_status:'PENDING'};
 const summary=reportJourney('ROAD_DAMAGE',[{cause_code:'UTILITY_LEAK',status:'SUPPORTED'}] as HypothesisDTO[],p,[{...work(),status:'COMPLETED'}],[]);
 assert.match(summary.why,/nearby pipe alone does not establish a leak/);
 assert.match(summary.findings[0],/possible explanation.*not a verified cause/);
 assert.match(summary.approval,/awaiting/);assert.match(summary.work,/1 of 1/);
 assert.match(summary.followup,/not established/);
});
test('report overview only claims verified resolution for an evidenced matching completed order',()=>{
 const p={...plan('COMPLETED'),approval_status:'APPROVED'};
 const completed=[{...work(),status:'COMPLETED'}];
 const valid={...outcome(),evidence_ids:['EV']};
 assert.match(reportJourney('WATERLOGGING',[],p,completed,[valid]).followup,/recorded a verified resolution/);
 for(const o of [{...valid,work_order_id:'FOREIGN'},{...valid,evidence_ids:[]},{...valid,assessment_status:'UTILITY_VERIFIED'}])assert.match(reportJourney('ROAD_DAMAGE',[],p,completed,[o]).followup,/not established/);
 assert.match(reportJourney('ROAD_DAMAGE',[],p,[{...work(),status:'IN_PROGRESS'}],[valid]).followup,/not established/);
});
test('report overview makes unavailable records explicit for unfinished waste case',()=>{
 const summary=reportJourney('WASTE_ACCUMULATION',null,null,null,null);
 assert.match(summary.why,/missed service, excess demand and later dumping/);
 assert.equal(summary.findings.length,0);assert.match(summary.work,/not available/);assert.match(summary.followup,/not available/);
 assert.match(summary.approval,/No action plan.*loaded records/);
});
test('report overview uses current assessments and actual authorization records, not the legacy approval field',()=>{
 const h={cause_code:'UTILITY_LEAK',status:'SUPPORTED',current_assessment_id:'NEW',assessment_history:[{id:'NEW',assessment:'INCONCLUSIVE'}]} as HypothesisDTO;
 const p={...plan('COMPLETED'),approval_status:'COMPLETED'};
 const summary=reportJourney('ROAD_DAMAGE',[h,h],p,[{...work(),status:'COMPLETED',authorized_by:'APPROVAL'}],[]);
 assert.equal(summary.findings.length,1);assert.match(summary.findings[0],/not established/);
 assert.match(summary.approval,/Work was authorized/);
 assert.doesNotMatch(reportJourney('ROAD_DAMAGE',[],{...p,approval_status:'APPROVED'},[],[]).approval,/has a recorded approval|Work was authorized/);
});

const introIncident=(issue_type='WATERLOGGING')=>({id:'INC',issue_type,complaint_ids:['CMP']} as IncidentDTO);
const introReport=(description:string)=>({id:'CMP',incident_id:'INC',description} as ComplaintDTO);
test('directory glimpse distinguishes reports and locations without claiming a verified cause',()=>{
 const road=incidentCardGlimpse({...introIncident('ROAD_DAMAGE'),location_id:'LOC-JUNCTION'},[introReport('road repaired twice and pipe lies underneath; leak unverified')]);
 assert.equal(road.glimpse,'Reported: Road repaired twice; pipe leak unverified');
 assert.equal(road.location,'Market Junction');
 const waste=incidentCardGlimpse(introIncident('WASTE_ACCUMULATION'),[introReport('overflow every market day; service schedule says daily')]);
 assert.match(waste.glimpse,/Reported: Market-day overflow.*schedule/);
 assert.doesNotMatch(waste.glimpse,/missed pickup|verified/i);
});
test('directory glimpse ignores foreign reports and bounds unknown descriptions',()=>{
 assert.equal(incidentCardGlimpse(introIncident(),[{...introReport('foreign'),incident_id:'OTHER'}]).glimpse,'Report details not available');
 const text=incidentCardGlimpse(introIncident(),[introReport('A'.repeat(200))]).glimpse;
 assert.ok(text.length<125);assert.ok(text.endsWith('…'));
 assert.equal(incidentCardGlimpse(introIncident(),[]).location,'Location not recorded');
});
test('case introduction explains the reported flooding without turning claims into findings',()=>{
 const intro=incidentIntroduction(introIncident(),[introReport('inlet cleaned twice but junction floods in ordinary rain')],[{cause_code:'BLOCKAGE'},{cause_code:'CAPACITY_DEFICIT'}] as HypothesisDTO[]);
 assert.match(intro.report!,/report describes flooding.*drain entrance.*twice/);
 assert.match(intro.focus,/Possible explanations.*Drain blockage.*Insufficient drainage capacity/);
 assert.doesNotMatch(intro.focus,/confirmed|verified|resolved/i);
});
test('road and waste introductions retain unproven leak and reported schedule distinctions',()=>{
 const road=incidentIntroduction(introIncident('ROAD_DAMAGE'),[introReport('road repaired twice and pipe lies underneath; leak unverified')]);
 assert.match(road.report!,/does not establish that it is leaking/);
 const waste=incidentIntroduction(introIncident('WASTE_ACCUMULATION'),[introReport('overflow every market day; service schedule says daily')]);
 assert.match(waste.report!,/report describes waste.*schedule says/);
 assert.doesNotMatch(waste.report!,/pickup was missed|pickups happened/);
});
test('case introduction rejects foreign reports and preserves unknown source wording',()=>{
 assert.equal(incidentIntroduction(introIncident(),[{...introReport('foreign'),incident_id:'OTHER'},{...introReport('foreign'),id:'OTHER'}]).report,null);
 assert.equal(incidentIntroduction(introIncident(),[introReport('A new reported symptom.')]).report,'A new reported symptom.');
 assert.match(incidentIntroduction(introIncident(),[]).focus,/checks how water drains/);
});

test('legacy runtime constant is not translated into false execution evidence',()=>{
 const recorded=caseProgress(inv(),trace());assert.equal(recorded.origin,'Civicly’s AI investigation recorded');assert.equal(recorded.originDetail,'The saved trace contains real activity from Civicly’s AI.');
 const absent=caseProgress(inv(),null);assert.equal(absent.origin,'Agent activity not established');assert.doesNotMatch(absent.origin,/Gemini/);
});
test('development and mixed traces remain explicit',()=>{
 assert.equal(caseProgress(inv(),trace(['SCRIPTED'])).origin,'Development test activity recorded');
 assert.equal(caseProgress(inv(),trace(['LIVE_GEMINI','SCRIPTED'])).origin,'Civicly’s AI and development activity recorded');
});
test('water draft awaits exact approval even if a historical agent pause was a usage limit',()=>{
 const p=caseProgress(inv(),trace(['LIVE_GEMINI'],'TOKEN_BUDGET'),plan());assert.equal(p.next,'Awaiting plan approval');assert.match(p.detail,/exact plan version/);assert.equal(p.pause,'Agent usage limit reached');
});
test('waste with no draft honestly stops at its usage limit',()=>{
 const p=caseProgress(inv(),trace(['LIVE_GEMINI'],'TOKEN_BUDGET'));assert.equal(p.next,'Agent paused at its usage limit');assert.match(p.detail,/does not resume.*raise/);
});
test('completed road operation is separate from stale saved agent pause',()=>{
 const p=caseProgress(inv({status:'COMPLETED'}),trace(['LIVE_GEMINI'],'TOKEN_BUDGET'),plan('COMPLETED'),[outcome()],[work()]);assert.equal(p.next,'Review the verified outcome');assert.equal(p.status,'Investigation complete');assert.match(p.detail,/recorded follow-up/);
});
test('completion, a component result, and a foreign outcome cannot prove resolution',()=>{
 for(const outcomes of [[],[outcome('UTILITY_VERIFIED',false)],[outcome('RESOLUTION_VERIFIED',true,'OTHER-WO')]]){
  assert.equal(caseProgress(inv({status:'COMPLETED'}),trace(),plan('COMPLETED'),outcomes,[work()]).next,'Review the completed investigation');
 }
 assert.equal(caseProgress(inv(),trace(),plan('MONITORING'),[outcome('UTILITY_VERIFIED',false)],[work()]).next,'Review independent follow-up');
});
test('recovery blocks routine continuation without erasing terminal operational history',()=>{
 const t={...trace(),recovery_required:true};assert.equal(caseProgress(inv({status:'COMPLETED'}),t,plan('COMPLETED')).next,'Operator review required');
 assert.match(caseProgress(inv(),t).detail,/do not replay/);
});
test('current operational plan is authoritative, including when an older draft is first',()=>{
 const old=plan('DRAFT','OLD'),latest={...plan('COMPLETED','NEW'),version:2};assert.equal(currentPlan([old,latest],'NEW'),latest);assert.equal(currentPlan([old,latest]),latest);assert.equal(currentPlan([old,latest],'MISSING'),null);
 assert.deepEqual(scopedOrders([work(),work('OTHER','FOREIGN')],['PLAN']),[work()]);
});
test('category directory derives all three issue categories including a closed road episode',()=>{
 const investigations=[inv({id:'INV-WATER',incident_ids:['WATER']}),inv({id:'INV-ROAD',status:'COMPLETED',incident_ids:[],historical_incident_ids:['ROAD']}),inv({id:'INV-WASTE',incident_ids:['WASTE']})];
 const incidents=[{id:'WATER',issue_type:'WATERLOGGING'},{id:'ROAD',issue_type:'ROAD_DAMAGE'},{id:'WASTE',issue_type:'WASTE_ACCUMULATION'}] as IncidentDTO[];
 const rows=directoryCases(investigations,incidents,[]);assert.deepEqual(rows.map(r=>r.issue_type),['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']);assert.equal(rows[1].incident_id,'ROAD');assert.deepEqual(rows[1].incident_ids,['ROAD']);
 assert.equal(directoryCases(investigations,incidents,[],'ROAD_DAMAGE').length,1);assert.equal(directoryCases([inv()],[],[]).length,0);
});
test('completed investigation loads its incident by history link and retains selected scope checks',async()=>{
 const calls:string[]=[];const client=new ApiClient(async path=>{calls.push(String(path));return Response.json({data:String(path).includes('/investigations/')?inv({status:'COMPLETED',incident_ids:[],historical_incident_ids:['INC']}):{id:'INC',expected_hash:'a'.repeat(64),issue_type:'ROAD_DAMAGE',subtype:'UNSPECIFIED',location_id:'LOC',started_at:'2026-10-18T10:00:00Z',ended_at:'2026-10-18T12:00:00Z',status:'ENDED',cluster_id:'CLUSTER',complaint_ids:[]},request_id:'TEST',schema_version:1});});client.setSession('test');
 const selected=await loadSelectedCase(client,{investigation:'INV',issue:'ROAD_DAMAGE'});assert.equal(selected.incidents[0].id,'INC');assert.ok(calls.includes('/api/v1/incidents/INC'));
 await assert.rejects(loadSelectedCase(client,{investigation:'INV',incident:'FOREIGN'}),/response|case|match/i);
});
test('native task binding supplies work title and never guesses an assignee',()=>{
 const p=plan();p.draft.tasks=[{id:'local',action_type:'SUBGRADE_REPAIR',department_id:'DEPT-ROAD',target_ids:['ROAD']}] as PlanDTO['draft']['tasks'];p.task_bindings=[{local_task_id:'local',task_id:'NATIVE',action_type:'SUBGRADE_REPAIR',department_id:'DEPT-ROAD',target_ids:['ROAD'],eligible_assignee_ids:['OP-ROAD-LEAD']}] as PlanDTO['task_bindings'];
 assert.equal(taskForOrder(p,{...work(),task_id:'NATIVE'})?.action_type,'SUBGRADE_REPAIR');assert.equal(approvalAssignments(p)[0].task_id,'NATIVE');
 p.task_bindings![0].eligible_assignee_ids=[];assert.throws(()=>approvalAssignments(p));p.task_bindings![0].eligible_assignee_ids=['A','B'];assert.throws(()=>approvalAssignments(p));p.task_bindings=[];assert.throws(()=>approvalAssignments(p));
});
test('evidence, work and outcomes have distinct neutral labels',()=>{
 assert.equal(translateStatus('COMPLETED'),'Completed');assert.equal(translateStatus('VERIFIED'),'Verified');assert.equal(translateStatus('RESOLUTION_VERIFIED'),'Resolution verified by follow-up');assert.doesNotMatch(translateStatus('CONTROLLED'),/no recurrence/i);
 assert.doesNotMatch(translateAssessment('SUPPORTED').description,/verified physical|proven/i);assert.doesNotMatch(translateAssessment('CONTRADICTED').description,/inspection|measurement/);
 assert.equal(formatMissingEvidence('EV-REPORT-ABC'),'Evidence reference #REPORT-ABC needs review');
});


test('long action codes stay whole when their prefix is also a cause code',()=>{
 const text=cleanTextIdentifiers('UTILITY_LEAK_REPAIR follows UTILITY_ISOLATION; SUBGRADE_REPAIR follows.');
 assert.equal(text,'Repair the water pipe leak follows Safely isolate the water pipe; Repair the ground beneath the road follows.');
 assert.doesNotMatch(text,/_REPAIR|_ISOLATION/);
});

// F33: summaries cannot promote ambiguous or foreign records into a result.
import {stageTakeaway} from '../lib/read/stage-takeaway.ts';
test('stage takeaways distinguish missing evidence from supported and superseded assessments',()=>{
 assert.match(stageTakeaway({stage:2}).text,/No supported or verified/);
 const h={cause_code:'UTILITY_LEAK',status:'SUPPORTED',current_assessment_id:'NEW',assessment_history:[{id:'NEW',assessment:'INCONCLUSIVE'}]} as HypothesisDTO;
 assert.match(stageTakeaway({stage:2,hypotheses:[h]}).text,/No supported or verified/);
 assert.match(stageTakeaway({stage:2,hypotheses:[{...h,current_assessment_id:null}]}).text,/Support is not proof/);
});
test('takeaways do not turn plan status or foreign work into approval or execution',()=>{
 const p=plan('COMPLETED');
 assert.match(stageTakeaway({stage:3,plan:p,orders:[{...work('FOREIGN','OTHER'),authorized_by:'A'}]}).text,/does not itself authorize/);
 assert.match(stageTakeaway({stage:3,plan:{...p,approval_status:'APPROVED'}}).text,/does not itself authorize/);
 assert.match(stageTakeaway({stage:3,plan:plan()}).title,/awaits a decision/);
 assert.match(stageTakeaway({stage:4,plan:p,orders:[{...work('FOREIGN','OTHER'),status:'COMPLETED'}]}).title,/No work orders/);
 assert.match(stageTakeaway({stage:4,plan:p,orders:[{...work(),status:'COMPLETED'}]}).text,/Separate follow-up/);
});
test('takeaway closure needs matching completed work, closure status and evidence; memory is scoped',()=>{
 const base={stage:5,plan:plan(),orders:[{...work(),status:'COMPLETED'}],investigationId:'INV'};
 const valid={...outcome(),evidence_ids:['EV']};
 for(const bad of [{...valid,evidence_ids:[]},{...valid,work_order_id:'OTHER'},{...valid,assessment_status:'UTILITY_VERIFIED'},{...valid,case_closed:false}])assert.match(stageTakeaway({...base,outcomes:[bad]}).title,/still needs/);
 assert.match(stageTakeaway({...base,orders:[{...work(),status:'IN_PROGRESS'}],outcomes:[valid]}).title,/still needs/);
 assert.match(stageTakeaway({...base,outcomes:[valid]}).title,/verified resolution/);
 assert.match(stageTakeaway({...base,outcomes:[{...valid,evaluated_at:'2026-10-18T10:00:00Z'},{...valid,evaluated_at:'2026-10-19T10:00:00Z',case_closed:false}]}).title,/still needs/);
 assert.match(stageTakeaway({...base,memory:{source_investigation_id:'OTHER'} as never}).text,/memory is not established/);
 assert.match(stageTakeaway({...base,memory:{source_investigation_id:'INV'} as never}).text,/retained history is available/);
});
test('investigation takeaway counts validated success only and preserves recovery priority',()=>{
 const t={...trace(),items:[{kind:'TOOL',status:'SUCCESS',validated_output:true},{kind:'TOOL',status:'FAILED',validated_output:true},{kind:'DECISION',status:'SUCCESS',validated_output:true}]} as AgentTracePage;
 assert.match(stageTakeaway({stage:1,trace:t}).text,/1 validated tool/);
 assert.match(stageTakeaway({stage:1,trace:{...t,recovery_required:true}}).title,/needs review/);
 assert.match(stageTakeaway({stage:0}).text,/not available/);
});

// F34: timeline milestones follow authorized loaded records, not guessed event dates.
import {responseTimeline} from '../lib/read/response-timeline.ts';
test('timeline ignores foreign plan work and outcomes and has honest missing-plan milestones',()=>{
 const rows=responseTimeline(plan('DRAFT'),[{...work('OTHER','FOREIGN'),status:'COMPLETED',authorized_by:'A'}],[{...outcome('RESOLUTION_VERIFIED',true,'OTHER'),evidence_ids:['E']}]);
 assert.equal(rows[1].status,'Not established');assert.equal(rows[2].records.length,0);assert.equal(rows[3].records.length,0);assert.equal(rows[3].status,'Verification still needed');
 const none=responseTimeline(null,[],[]);assert.equal(none[0].status,'Not available');assert.equal(none[1].status,'Not established');
});
test('timeline separates pending and legacy plan labels from recorded authorization',()=>{
 const pending=responseTimeline(plan(),[],[]);assert.equal(pending[1].status,'Awaiting a decision');
 const legacy=responseTimeline({...plan('COMPLETED'),approval_status:'APPROVED'},[],[]);assert.equal(legacy[1].status,'Not established');
 const auth=responseTimeline(plan(),[{...work(),authorized_by:'APPROVAL'}],[]);
 assert.equal(auth[1].status,'Authorization recorded');assert.match(auth[1].summary,/decision time are restricted/);assert.equal(auth[1].records.length,0);
});
test('completed work and utility-only follow-up cannot close the response timeline',()=>{
 const w={...work(),status:'COMPLETED'};
 const rows=responseTimeline(plan(),[w],[{...outcome('UTILITY_VERIFIED',false),evidence_ids:['E']}]);
 assert.equal(rows[2].status,'1 of 1 completed');assert.equal(rows[3].status,'Verification still needed');
 assert.match(rows[2].summary,/Completion times are not available/);
 assert.ok(rows[2].records.every(r=>r.at===undefined));
});
test('timeline dates actual follow-up, retains earlier checks, and rejects superseded or unevidenced closure',()=>{
 const w={...work(),status:'COMPLETED'};
 const old={...outcome('MONITORING',false),id:'OLD',evidence_ids:['E'],evaluated_at:'2026-10-18T10:00:00Z'};
 const valid={...outcome(),id:'CLOSED',evidence_ids:['E'],evaluated_at:'2026-10-19T10:00:00Z'};
 const rows=responseTimeline(plan(),[w],[valid,old]);assert.equal(rows[3].status,'Resolution verified');assert.deepEqual(rows[3].records.map(r=>r.id),['OLD','CLOSED']);assert.equal(rows[3].records[1].at,valid.evaluated_at);
 for(const o of [{...valid,evidence_ids:[]},{...valid,case_closed:false}])assert.equal(responseTimeline(plan(),[w],[o])[3].status,'Verification still needed');
 assert.equal(responseTimeline(plan(),[w],[valid,{...old,id:'LATER',evaluated_at:'2026-10-20T10:00:00Z'}])[3].status,'Verification still needed');
 assert.equal(responseTimeline(plan(),[{...w,status:'IN_PROGRESS'}],[valid])[3].status,'Verification still needed');
});
test('unavailable timeline reads stay unavailable rather than becoming an empty successful response',()=>{
 const rows=responseTimeline(plan(),null,null);assert.equal(rows[1].status,'Records unavailable');assert.equal(rows[2].status,'Records unavailable');assert.equal(rows[3].status,'Records unavailable');
 assert.deepEqual(rows.map(r=>r.section),[3,3,4,5]);
});
