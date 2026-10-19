import {test} from 'node:test';
import assert from 'node:assert/strict';
import {ApiClient} from '../lib/api/client.ts';
import {ApiError} from '../lib/api/errors.ts';
import {validSchema} from '../lib/api/validation.ts';
import {DemoConnection} from '../lib/api/session.ts';
import {backendOrigin,proxy,demoSession} from '../lib/api/proxy.ts';
const account={id:'OP-ANALYST',display_name:'Synthetic OP-ANALYST',role:'ANALYST',department_id:'DEPT-COORD',enabled:true};
const session={access_token:'TEST_ONLY_TOKEN',operator_id:'OP-ANALYST',role:'ANALYST',expires_at:new Date(Date.now()+600000).toISOString()};
const ok=(data:unknown)=>Response.json({data,request_id:'test-request',schema_version:1});
const error=(code:string,status:number,details={})=>Response.json({error:{code,message:'sanitized',retryable:false,details},request_id:'test-error'},{status});
const rejects=(code:string)=>(value:unknown)=>value instanceof ApiError&&value.code===code;
const noFetch:typeof fetch=async()=>{assert.fail('must not fetch');};
const req=(path:string,init?:RequestInit)=>new Request('http://127.0.0.1:3100'+path,init);

test('closed schema rejects invented privilege and extra fields',()=>{assert(validSchema('OperatorAccount',account));assert(!validSchema('OperatorAccount',{...account,secret:'no'}));assert(!validSchema('OperatorAccount',{...account,enabled:false}));});
test('validated identity response preserves request ID and bearer/no-cache',async()=>{
 const client=new ApiClient(async(path,init)=>{assert.equal(path,'/api/v1/auth/me');assert.equal(new Headers(init?.headers).get('Authorization'),'Bearer TEST_ONLY_TOKEN');assert.equal(init?.cache,'no-store');assert.equal(init?.redirect,'error');return ok(account);});client.setSession('TEST_ONLY_TOKEN');assert.deepEqual(await client.request('GET /api/v1/auth/me'),{data:account,requestId:'test-request'});
});
test('protected request without token never fetches',async()=>{await assert.rejects(new ApiClient(noFetch).request('GET /api/v1/auth/me'),rejects('UNAUTHORIZED'));});
test('dashboard pagination/hypothesis date/unknown query/bad bounds fail before fetch',async()=>{
 const c=new ApiClient(noFetch);c.setSession('test');
 await assert.rejects(c.request('GET /api/v1/dashboard/summary',{query:{limit:5} as never}),rejects('CLIENT_VALIDATION'));
 await assert.rejects(c.request('GET /api/v1/investigations/{id}/hypotheses',{params:{id:'I1'},query:{after:'2026-10-18'} as never}),rejects('CLIENT_VALIDATION'));
 await assert.rejects(c.request('GET /api/v1/complaints',{query:{limit:51}}),rejects('CLIENT_VALIDATION'));
});
test('path traversal and extra parameters fail before fetch',async()=>{const c=new ApiClient(noFetch);c.setSession('test');for(const params of [{id:'../auth/me'},{id:'I1',graph:'other'}])await assert.rejects(c.request('GET /api/v1/incidents/{id}',{params:params as Record<string,string>}),rejects('CLIENT_VALIDATION'));});
test('closed request validation excludes credentials from error',async()=>{const c=new ApiClient(noFetch);await assert.rejects(c.request('POST /api/v1/auth/demo-login',{body:{operator_id:'OP-ANALYST',demo_password:'PRIVATE',role:'ADMIN'} as never}),e=>rejects('CLIENT_VALIDATION')(e)&&!JSON.stringify(e).includes('PRIVATE'));});
test('403 preserves session; 401 clears it and blocks further fetch',async()=>{let calls=0,ended=0;const c=new ApiClient(async()=>{calls++;return error(calls===1?'PERMISSION_DENIED':'UNAUTHORIZED',calls===1?403:401);});c.setSession('x');c.onUnauthorized(()=>ended++);await assert.rejects(c.request('GET /api/v1/auth/me'),rejects('PERMISSION_DENIED'));assert.equal(ended,0);await assert.rejects(c.request('GET /api/v1/auth/me'),rejects('UNAUTHORIZED'));assert.equal(ended,1);await assert.rejects(c.request('GET /api/v1/auth/me'),rejects('UNAUTHORIZED'));assert.equal(calls,2);});
test('non-JSON response and incompatible identity fail closed',async()=>{for(const response of [new Response('<html>PRIVATE</html>',{status:502}),ok({...account,role:'SUPERADMIN'})]){const c=new ApiClient(async()=>response);c.setSession('x');await assert.rejects(c.request('GET /api/v1/auth/me'),rejects('CONTRACT_MISMATCH'));}});
test('uncertain mutation preserves explicit key, sends once and never retries',async()=>{let calls=0;const c=new ApiClient(async(_,init)=>{calls++;assert.equal(new Headers(init?.headers).get('Idempotency-Key'),'original');throw Error('network');});c.setSession('x');const body={reason:'Review'};await assert.rejects(c.request('POST /api/v1/investigations/{id}/resume',{params:{id:'I1'},body}),rejects('CLIENT_VALIDATION'));await assert.rejects(c.request('POST /api/v1/investigations/{id}/resume',{params:{id:'I1'},body,idempotencyKey:'original'}),rejects('WRITE_OUTCOME_UNKNOWN'));assert.equal(calls,1);});
test('recovery details retained with no redispatch',async()=>{let calls=0;const c=new ApiClient(async()=>{calls++;return error('RECOVERY_REQUIRED',409,{commitment:'UNKNOWN',request_id:'original'});});c.setSession('x');await assert.rejects(c.request('POST /api/v1/investigations/{id}/resume',{params:{id:'I1'},body:{reason:'Review'},idempotencyKey:'original'}),e=>e instanceof ApiError&&e.uncertain&&e.details.request_id==='original');assert.equal(calls,1);});
test('late 401 cannot clear replacement session',async()=>{let finish!:(r:Response)=>void;const c=new ApiClient(async()=>new Promise(r=>{finish=r;}));c.setSession('old');const pending=c.request('GET /api/v1/auth/me');c.setSession('new');finish(error('UNAUTHORIZED',401));await assert.rejects(pending,rejects('SESSION_CHANGED'));});
test('automatic connect deduplicates opens and verifies identity',async()=>{let calls=0;const c=new DemoConnection(async path=>{calls++;return path==='/api/demo-session'?ok(session):ok(account);});const first=c.open();assert.equal(first,c.open());assert.equal((await first).account.id,'OP-ANALYST');assert.equal(calls,2);});
test('expired or mismatched identity is refused',async()=>{const c=new DemoConnection(async path=>path==='/api/demo-session'?ok(session):ok({...account,id:'OP-ADMIN'}));await assert.rejects(c.open(),rejects('CONTRACT_MISMATCH'));await assert.rejects(c.client.request('GET /api/v1/auth/me'),rejects('UNAUTHORIZED'));const expired=new DemoConnection(async()=>ok({...session,expires_at:'2000-01-01T00:00:00Z'}));await assert.rejects(expired.open(),rejects('CONTRACT_MISMATCH'));});
test('end during pending connect cannot restore old session',async()=>{let finish!:(r:Response)=>void;const c=new DemoConnection(async()=>new Promise(r=>{finish=r;}));const pending=c.open();await c.close();finish(ok(session));await assert.rejects(pending,rejects('SESSION_CHANGED'));});
test('logout clears local token when revocation unavailable',async()=>{const c=new DemoConnection(async path=>path==='/api/demo-session'?ok(session):path==='/api/v1/auth/me'?ok(account):error('EXTERNAL_UNAVAILABLE',503));await c.open();await assert.rejects(c.close(),rejects('EXTERNAL_UNAVAILABLE'));await assert.rejects(c.client.request('GET /api/v1/auth/me'),rejects('UNAUTHORIZED'));});
test('SSE excluded from REST client pending F05',async()=>{await assert.rejects(new ApiClient(noFetch).request('GET /api/v1/events/stream'),rejects('CLIENT_VALIDATION'));});
test('proxy only accepts host loopback origin',()=>{assert.equal(backendOrigin('http://localhost:8011'),'http://localhost:8011');for(const v of ['https://example.com','http://localhost:3100','http://u:p@localhost:8000','http://localhost:8000/path'])assert.equal(backendOrigin(v),null);});
test('unconfigured proxy returns sanitized unavailable envelope',async()=>{const r=await proxy(req('/api/v1/auth/me'),undefined,noFetch);assert.equal(r.status,503);assert.equal((await r.json()).error.code,'EXTERNAL_UNAVAILABLE');});
test('proxy denies unknown/repeated selectors and unsupported routes',async()=>{for(const path of ['/api/v1/auth/me?graph=secret','/api/v1/complaints?limit=1&limit=2','/api/v1/dashboard/summary?cursor=x'])assert.equal((await proxy(req(path),'http://localhost:8011',noFetch)).status,422);assert.equal((await proxy(req('/api/v1/raw-query'),'http://localhost:8011',noFetch)).status,404);});
test('cross-origin session/proxy are refused',async()=>{const init={method:'POST',headers:{Origin:'https://other.example'}};assert.equal((await demoSession(req('/api/demo-session',init),{},noFetch)).status,403);assert.equal((await proxy(req('/api/v1/auth/logout',init),'http://localhost:8011',noFetch)).status,403);});
test('proxy preserves bearer/key but strips cookies/extra headers',async()=>{const r=await proxy(req('/api/v1/investigations/I1/resume',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer TEST',Cookie:'private','Idempotency-Key':'original','X-Other':'no'},body:'{}'}),'http://localhost:8011',async(url,init)=>{assert.equal(url,'http://localhost:8011/api/v1/investigations/I1/resume');const h=new Headers(init?.headers);assert.equal(h.get('Authorization'),'Bearer TEST');assert.equal(h.get('Cookie'),null);assert.equal(h.get('X-Other'),null);assert.equal(h.get('Idempotency-Key'),'original');return Response.json({data:{}},{headers:{'Set-Cookie':'private','X-Request-ID':'safe'}});});assert.equal(r.headers.get('Set-Cookie'),null);assert.equal(r.headers.get('Cache-Control'),'no-store');});
test('proxy transport fault on write does not retry',async()=>{let n=0;const r=await proxy(req('/api/v1/investigations/I1/resume',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}),'http://localhost:8011',async()=>{n++;throw Error('network');});assert.equal(n,1);assert.equal(r.status,409);assert.equal((await r.json()).error.code,'RECOVERY_REQUIRED');});
test('automatic session accepts neither browser credentials nor elevated host identity',async()=>{assert.equal((await demoSession(req('/api/demo-session',{method:'POST',body:'{"role":"ADMIN"}'}),{},noFetch)).status,422);assert.equal((await demoSession(req('/api/demo-session',{method:'POST'}),{origin:'http://localhost:8011',password:'PRIVATE',operator:'OP-ADMIN'},noFetch)).status,503);});
test('automatic session never echoes secret/upstream failure text',async()=>{const r=await demoSession(req('/api/demo-session',{method:'POST'}),{origin:'http://localhost:8011',password:'PRIVATE'},async()=>new Response('PRIVATE',{status:500}));assert.equal(r.status,503);assert(!(await r.text()).includes('PRIVATE'));});
test('non-JSON/oversized proxy bodies refused before forwarding',async()=>{assert.equal((await proxy(req('/api/v1/auth/logout',{method:'POST',body:'{}'}),'http://localhost:8011',noFetch)).status,422);assert.equal((await proxy(req('/api/v1/auth/logout',{method:'POST',headers:{'Content-Type':'application/json'},body:'x'.repeat(262145)}),'http://localhost:8011',noFetch)).status,422);});
test('Next internal localhost normalization preserves legitimate browser origin',async()=>{
 const r=await proxy(new Request('http://localhost:3120/api/v1/auth/me',{headers:{Host:'127.0.0.1:3120',Origin:'http://127.0.0.1:3120','Sec-Fetch-Site':'same-origin'}}),'http://localhost:8011',async()=>ok(account));assert.equal(r.status,200);
 const spoof=await proxy(new Request('http://localhost:3120/api/v1/auth/me',{headers:{Host:'127.0.0.1:3120',Origin:'https://other.example','X-Forwarded-Host':'other.example'}}),'http://localhost:8011',noFetch);assert.equal(spoof.status,403);
});
test('late response body cannot restore prior session state',async()=>{
 let finish!:(r:unknown)=>void;const response=ok(account);response.json=()=>new Promise(resolve=>{finish=resolve;});
 const c=new ApiClient(async()=>response);c.setSession('old');const pending=c.request('GET /api/v1/auth/me');
 await new Promise(resolve=>setImmediate(resolve));c.setSession('new');finish({data:account,request_id:'old',schema_version:1});await assert.rejects(pending,rejects('SESSION_CHANGED'));
});
test('default browser fetch remains a bare global call, not a class method receiver',async t=>{
 const original=globalThis.fetch;
 t.after(()=>{globalThis.fetch=original;});
 globalThis.fetch=function(this:unknown,path:RequestInfo|URL){assert(this===undefined||this===globalThis,'native browser fetch receiver must not be a class instance');return Promise.resolve(String(path)==='/api/demo-session'?ok(session):ok(account));} as typeof fetch;
 const connection=new DemoConnection();assert.equal((await connection.open()).account.id,'OP-ANALYST');
});
test('query optional null/undefined values are omitted while unknown fields still fail',async()=>{
 const c=new ApiClient(async path=>{assert.equal(path,'/api/v1/dashboard/summary');return ok({});});c.setSession('x');
 // A deliberately incomplete response reaches response validation, proving the query was accepted/omitted.
 await assert.rejects(c.request('GET /api/v1/dashboard/summary',{query:{issue:null,status:undefined}}),rejects('CONTRACT_MISMATCH'));
});
test('finishing old logout cannot erase a new connection',async()=>{
 let end!:(r:Response)=>void;
 const c=new DemoConnection(async path=>path==='/api/demo-session'?ok(session):path==='/api/v1/auth/me'?ok(account):new Promise(resolve=>{end=resolve;}));
 await c.open();const closing=c.close();await c.open();end(ok({status:'LOGGED_OUT'}));await closing;
 assert.equal((await c.client.request('GET /api/v1/auth/me')).data.id,'OP-ANALYST');
});

test('hosted proxy permits only the configured HTTPS host and origin',async()=>{
 const publicOrigin='https://civicly.example.com';
 const request=(host:string,origin?:string,extra:Record<string,string>={})=>new Request('http://localhost:3100/api/v1/auth/me',{headers:{Host:host,...(origin?{Origin:origin}:{}),...extra}});
 const fetcher:typeof fetch=async()=>ok(account);
 assert.equal((await proxy(request('civicly.example.com',publicOrigin),'http://localhost:8011',fetcher,publicOrigin)).status,200);
 assert.equal((await proxy(request('civicly.example.com'),'http://localhost:8011',fetcher,publicOrigin)).status,200);
 for(const [host,origin] of [['other.example',publicOrigin],['civicly.example.com','https://other.example'],['civicly.example.com','http://civicly.example.com']])assert.equal((await proxy(request(host,origin),'http://localhost:8011',noFetch,publicOrigin)).status,403);
 assert.equal((await proxy(request('other.example',publicOrigin,{'X-Forwarded-Host':'civicly.example.com'}),'http://localhost:8011',noFetch,publicOrigin)).status,403);
 assert.equal((await proxy(request('civicly.example.com',publicOrigin,{'Sec-Fetch-Site':'cross-site'}),'http://localhost:8011',noFetch,publicOrigin)).status,403);
});
test('hosted sessions require an exact browser Origin and HTTPS configuration',async()=>{
 const publicOrigin='https://civicly.example.com';
 const request=(origin?:string)=>new Request('http://localhost:3100/api/demo-session',{method:'POST',headers:{Host:'civicly.example.com',...(origin?{Origin:origin}:{})}});
 for(const origin of [undefined,'https://other.example'])assert.equal((await demoSession(request(origin),{publicOrigin},noFetch)).status,403);
 for(const configured of ['http://civicly.example.com','https://u:p@civicly.example.com','https://civicly.example.com/path','https://civicly.example.com?x=1'])assert.equal((await demoSession(request(publicOrigin),{publicOrigin:configured},noFetch)).status,403);
 const response=await demoSession(request(publicOrigin),{publicOrigin,origin:'http://localhost:8011',password:'PRIVATE'},async()=>ok(session));
 assert.equal(response.status,200);
 assert(!(await response.text()).includes('PRIVATE'));
});

// F36: connection transitions never expose stale session/case data or fake absence.
import {visibleReadState,type OwnedRead} from '../lib/read/read-state.ts';
test('connecting reads are loading, while actual unavailable and ended sessions stay unavailable',()=>{
 const owner={};const saved:OwnedRead<string>={owner,key:'CASE',state:{status:'ready',data:'prior record',message:'',requestId:null}};
 assert.deepEqual(visibleReadState({status:'connecting',identity:null,message:'Connecting',requestId:null},'CASE',true,saved),{status:'loading',data:null,message:'Connecting to the demo workspace…',requestId:null});
 for(const status of ['unavailable','ended'] as const){const result=visibleReadState({status,identity:owner,message:'Session unavailable',requestId:'R'},'CASE',true,saved);assert.equal(result.status,'unavailable');assert.equal(result.data,null);assert.equal(result.requestId,'R');}
});
test('read presentation rejects cached records from a different case or session and disabled selection',()=>{
 const owner={};const saved:OwnedRead<string>={owner,key:'CASE-A',state:{status:'ready',data:'case A',message:'',requestId:null}};
 const connected={status:'connected' as const,identity:owner,message:'Ready',requestId:null};
 for(const [identity,key] of [[owner,'CASE-B'],[{},'CASE-A'],[null,'CASE-A']] as const){const result=visibleReadState({...connected,identity},key,true,saved);assert.equal(result.status,'loading');assert.equal(result.data,null);}
 assert.equal(visibleReadState(connected,'CASE-A',false,saved).data,null);
 assert.equal(visibleReadState(connected,'CASE-A',true,saved).data,'case A');
});
test('same-scope refresh can retain ready data but a confirmed error remains an error',()=>{
 const owner={};const connection={status:'connected' as const,identity:owner,message:'Ready',requestId:null};
 const saved:OwnedRead<string>={owner,key:'CASE',state:{status:'error',data:null,message:'Source unavailable',requestId:'R',errorCode:'GRAPH_UNAVAILABLE'}};
 assert.equal(visibleReadState(connection,'CASE',true,saved).status,'error');assert.equal(visibleReadState(connection,'CASE',true,saved).errorCode,'GRAPH_UNAVAILABLE');
 saved.state={status:'ready',data:'retained during refresh',message:'',requestId:null};assert.equal(visibleReadState(connection,'CASE',true,saved).data,'retained during refresh');
});
