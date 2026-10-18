import {routes} from '../generated/routes.ts';
import {validSchema} from './validation.ts';

export function failure(code:string,status:number) {
  return Response.json({error:{code,message:'The local demo request could not be completed.',details:code==='RECOVERY_REQUIRED'?{commitment:'UNKNOWN'}:{},retryable:false},request_id:crypto.randomUUID().replaceAll('-','')},{status,headers:{'Cache-Control':'no-store'}});
}
export function backendOrigin(value:string|undefined):string|null {
  if(!value)return null;
  try {
    const url=new URL(value);
    if(url.protocol!=='http:'||!['127.0.0.1','localhost','[::1]'].includes(url.hostname)||!url.port||url.port==='3100'||url.username||url.password||url.pathname!=='/'||url.search||url.hash)return null;
    return url.origin;
  } catch{return null;}
}
function sameOrigin(request:Request,publicOrigin?:string) {
  if(publicOrigin){
    let expected:URL;
    try{expected=new URL(publicOrigin);}catch{return false;}
    if(expected.protocol!=='https:'||expected.username||expected.password||expected.pathname!=='/'||expected.search||expected.hash)return false;
    const host=request.headers.get('Host')??new URL(request.url).host;
    const origin=request.headers.get('Origin');
    return host===expected.host && (origin===expected.origin || (!origin&&request.method==='GET')) && !['cross-site','same-site'].includes(request.headers.get('Sec-Fetch-Site')??'');
  }
  const internal=new URL(request.url);
  // Next can normalize request.url to localhost while the browser used 127.0.0.1.
  // Use the original Host, never a caller-supplied forwarded-host selector.
  const host=request.headers.get('Host')??internal.host;
  let external:URL;
  try{external=new URL('http://'+host);}catch{return false;}
  if(external.host!==host||!['127.0.0.1','localhost','[::1]'].includes(external.hostname))return false;
  const origin=request.headers.get('Origin');
  return (!origin||origin===external.origin) && !['cross-site','same-site'].includes(request.headers.get('Sec-Fetch-Site')??'');
}

export async function proxy(request:Request,configuredOrigin:string|undefined,fetcher:typeof fetch=fetch,publicOrigin?:string):Promise<Response> {
  if(!sameOrigin(request,publicOrigin))return failure('PERMISSION_DENIED',403);
  const url=new URL(request.url);
  const route=Object.values(routes).find(route=>route.method===request.method && new RegExp('^'+route.path.replace(/\{[^}]+\}/g,'[^/]+')+'$').test(url.pathname));
  if(!route)return failure('NOT_FOUND',404);
  const isStream=route.path==='/api/v1/events/stream';
  const allowed:readonly string[]=isStream?['cursor','investigation_id']:('query_parameters' in route?route.query_parameters:[]);
  if([...url.searchParams.keys()].some(key=>!allowed.includes(key)||url.searchParams.getAll(key).length!==1))return failure('VALIDATION_ERROR',422);
  if(url.pathname.split('/').some(part=>{try {return /[\\/\u0000]/.test(decodeURIComponent(part))||['.','..'].includes(decodeURIComponent(part));}catch{return true;}}))return failure('VALIDATION_ERROR',422);
  const origin=backendOrigin(configuredOrigin);
  if(!origin)return failure('EXTERNAL_UNAVAILABLE',503);
  const headers=new Headers({'Accept':isStream?'text/event-stream':'application/json'});
  for(const name of ['Authorization','Idempotency-Key','X-Request-ID','X-Reviewer-Authorization','X-Field-Authorization','Last-Event-ID']){
    const value=request.headers.get(name);if(value)headers.set(name,value);
  }
  let body:string|undefined;
  if(request.method==='POST'){
    if(!request.headers.get('Content-Type')?.startsWith('application/json'))return failure('VALIDATION_ERROR',422);
    if(Number(request.headers.get('Content-Length'))>262144)return failure('VALIDATION_ERROR',422);
    const reader=request.body?.getReader();let length=0;const chunks:Uint8Array[]=[];
    if(reader){while(true){const item=await reader.read();if(item.done)break;length+=item.value.length;if(length>262144){await reader.cancel();return failure('VALIDATION_ERROR',422);}chunks.push(item.value);}}
    const bytes=new Uint8Array(length);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}body=new TextDecoder().decode(bytes);
    try{JSON.parse(body);}catch{return failure('VALIDATION_ERROR',422);}
    headers.set('Content-Type','application/json');
  }
  try{
    const signal=isStream?request.signal:AbortSignal.any([request.signal,AbortSignal.timeout(15000)]);
    const upstream=await fetcher(origin+url.pathname+url.search,{method:request.method,headers,body,cache:'no-store',redirect:'error',signal});
    const upstreamType=upstream.headers.get('Content-Type')||'application/json';
    const isEventStream=upstreamType.includes('text/event-stream');
    const forwarded=new Headers({
      'Cache-Control':isEventStream?'no-cache, no-transform':'no-store',
      'Content-Type':isEventStream?'text/event-stream':'application/json',
    });
    if(isEventStream)forwarded.set('Connection','keep-alive');
    for(const name of ['X-Request-ID','WWW-Authenticate']){const value=upstream.headers.get(name);if(value)forwarded.set(name,value);}
    return new Response(upstream.body,{status:upstream.status,headers:forwarded});
  }catch {
    return failure(request.method==='POST'&&route.idempotency_key?'RECOVERY_REQUIRED':'EXTERNAL_UNAVAILABLE',request.method==='POST'&&route.idempotency_key?409:503);
  }
}
export async function demoSession(request:Request,config:{origin?:string;password?:string;operator?:string;publicOrigin?:string},fetcher:typeof fetch=fetch):Promise<Response> {
  if(request.method!=='POST'||!sameOrigin(request,config.publicOrigin))return failure('PERMISSION_DENIED',403);
  // No credentials, roles or target selectors are accepted from the browser.
  if(new URL(request.url).search||request.headers.get('Content-Length') && request.headers.get('Content-Length')!=='0')return failure('VALIDATION_ERROR',422);
  if((await request.text()).length)return failure('VALIDATION_ERROR',422);
  const origin=backendOrigin(config.origin);
  if(!origin||!config.password||config.password.length>256||config.operator && config.operator!=='OP-ANALYST')return failure('DEMO_UNAVAILABLE',503);
  try{
    const login=await fetcher(origin+'/api/v1/auth/demo-login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({operator_id:'OP-ANALYST',demo_password:config.password}),cache:'no-store',redirect:'error',signal:AbortSignal.timeout(15000)});
    const value=await login.json();
    if(!login.ok||!value||value.schema_version!==1||typeof value.request_id!=='string'||!validSchema('DemoSession',value.data)||value.data.operator_id!=='OP-ANALYST'||value.data.role!=='ANALYST'||!Number.isFinite(Date.parse(value.data.expires_at))||Date.parse(value.data.expires_at)<=Date.now())return failure('DEMO_UNAVAILABLE',503);
    return Response.json(value,{headers:{'Cache-Control':'no-store'}});
  }catch{return failure('DEMO_UNAVAILABLE',503);}
}
