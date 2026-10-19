/** Read-only domain verification for the retained local demo; auth session is ended. */
import {ApiClient} from '../lib/api/client.ts';
import {loadSelectedCase,registeredCases} from '../lib/read/cases.ts';
import {loadDirectory,caseProgress,currentPlan,scopedOrders} from '../lib/read/workflow.ts';
const origin='http://127.0.0.1:3100';
const login=await fetch(origin+'/api/demo-session',{method:'POST',headers:{Origin:origin}});if(!login.ok)throw Error('LOGIN_FAILED');
const session=(await login.json()).data;const client=new ApiClient((path,init)=>fetch(origin+path,init));client.setSession(session.access_token);
try{
 const catalog=(await client.request('GET /api/v1/demo/scenarios')).data;
 const directory=await loadDirectory(client,registeredCases(catalog));
 const categories=[...new Set(directory.items.map(r=>r.issue_type))];
 if(categories.length!==3)throw Error('CATEGORY_DIRECTORY_FAILED');
 const rows=[];
 for(const [id,expected] of [['INV-B09-8b006fb97aa2b908fc69addcf7ecd037','Review the verified outcome'],['INV-B09-b9d4d66e130ed348c4f6a50e9d66a891','Review the verified outcome'],['INV-B09-95e00a75e74b708c966db68bc595dca0','Agent paused at its usage limit']]){
  const {investigation:inv,incidents}=await loadSelectedCase(client,{investigation:id});
  const trace=(await client.request('GET /api/v1/investigations/{id}/trace',{params:{id}})).data;
  const plans=(await client.request('GET /api/v1/investigations/{id}/plans',{params:{id}})).data.items;
  const orders=scopedOrders((await client.request('GET /api/v1/work-orders',{query:{limit:50}})).data.items,plans.map(p=>p.plan_id));
  const outcomes=(await client.request('GET /api/v1/problem-clusters/{id}/outcomes',{params:{id:inv.problem_cluster_id}})).data.items;
  const memory=(await client.request('GET /api/v1/cases/{id}/memory',{params:{id:incidents[0].id}})).data;
  const progress=caseProgress(inv,trace,currentPlan(plans,inv.current_plan_id),outcomes,orders);
  if(progress.next!==expected||progress.origin!=='Civicly’s AI investigation recorded')throw Error('PROGRESS_FAILED');
  rows.push({investigation:id,incident:incidents[0].id,issue:incidents[0].issue_type,status:inv.status,legacy_runtime_status_retained:inv.runtime_status,display:progress,scoped_work_orders:orders.length,memory_items:memory.items.length,graph_revision:inv.graph_revision});
 }
 if(rows[1].scoped_work_orders!==3||rows[1].memory_items!==1)throw Error('ROAD_READBACK_FAILED');
 const out={mode:'REAL_HTTP_TYPED_CLIENT_AND_PRESENTATION_HELPERS_NO_PROVIDER',categories,directory_count:directory.items.length,cases:rows,provider_requests:0,domain_writes:0};
 console.log(JSON.stringify(out,null,2));
}finally{await client.request('POST /api/v1/auth/logout',{body:{}});}
