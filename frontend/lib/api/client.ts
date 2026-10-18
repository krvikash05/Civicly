import {routes} from '../generated/routes.ts';
import type {ApiRoutes} from '../generated/routes.ts';
import type {ApiModels} from '../generated/models.ts';
import {validSchema,validQuery} from './validation.ts';
import {ApiError} from './errors.ts';
export type RequestOptions<K extends keyof ApiRoutes> = {
  params?: Record<string,string>;
  query?: ApiRoutes[K]['query'];
  body?: ApiRoutes[K]['request'];
  idempotencyKey?: string;
  signal?: AbortSignal;
};
export type Result<T> = {data:T;requestId:string};
export type Fetcher = typeof fetch;
export class ApiClient {
  private token: string|null=null;
  private revision=0;
  private unauthorized: (()=>void)|undefined;
  private fetcher: Fetcher;
  constructor(fetcher: Fetcher=(...args)=>fetch(...args)) { this.fetcher=fetcher; }
  setSession(token: string|null) { this.token=token;this.revision++; }
  getToken(): string|null { return this.token; }
  detach(){const token=this.token;this.setSession(null);return token;}
  onUnauthorized(callback:()=>void) { this.unauthorized=callback; }
  async request<K extends keyof ApiRoutes>(key:K,options:RequestOptions<K>={}):Promise<Result<ApiRoutes[K]['response']>> {
    const route=routes[key];
    if(!route || route.path==='/api/v1/events/stream') throw new ApiError('CLIENT_VALIDATION');
    const requestSchema = route.request_schema_id;
    if(requestSchema ? !validSchema(requestSchema,options.body) : options.body!==undefined) throw new ApiError('CLIENT_VALIDATION');
    const rawQuery = (options.query??{}) as Record<string,unknown>;
    const query = Object.fromEntries(Object.entries(rawQuery).filter(([,value])=>value!==undefined&&value!==null));
    const allowed: readonly string[] = 'query_parameters' in route ? route.query_parameters:[];
    const querySchema = 'query_schema_id' in route ? route.query_schema_id:undefined;
    if(Object.keys(rawQuery).some(key=>!allowed.includes(key))||!validQuery(allowed,querySchema,query)) throw new ApiError('CLIENT_VALIDATION');
    const expectedParams = [...route.path.matchAll(/\{([^}]+)\}/g)].map(match=>match[1]);
    if(Object.keys(options.params??{}).some(key=>!expectedParams.includes(key)) || expectedParams.some(key=>!options.params?.[key] || options.params[key].length>200 || /[\\/\u0000]/.test(options.params[key]) || ['.','..'].includes(options.params[key]))) throw new ApiError('CLIENT_VALIDATION');
    const path=route.path.replace(/\{([^}]+)\}/g,(_,name)=>encodeURIComponent(options.params![name]));
    if(route.idempotency_key && (!options.idempotencyKey || !/^[!-~]{1,200}$/.test(options.idempotencyKey)))throw new ApiError('CLIENT_VALIDATION');
    if(!route.idempotency_key && options.idempotencyKey)throw new ApiError('CLIENT_VALIDATION');
    const revision=this.revision;
    if(route.role!=='PUBLIC'&&!this.token)throw new ApiError('UNAUTHORIZED',401);
    const headers: Record<string,string>={'Accept':'application/json'};
    if(this.token)headers.Authorization=`Bearer ${this.token}`;
    if(requestSchema)headers['Content-Type']='application/json';
    if(options.idempotencyKey)headers['Idempotency-Key']=options.idempotencyKey;
    const search=new URLSearchParams(Object.entries(query).map(([key,value])=>[key,String(value)]));
    let response:Response;
    try {
      response=await this.fetcher(path+(search.size?'?'+search.toString():''),{method:route.method,headers,body:requestSchema?JSON.stringify(options.body):undefined,cache:'no-store',credentials:'omit',redirect:'error',signal:options.signal?AbortSignal.any([options.signal,AbortSignal.timeout(15000)]):AbortSignal.timeout(15000)});
    } catch {
      if(revision!==this.revision)throw new ApiError('SESSION_CHANGED');
      throw new ApiError(route.method==='POST'&&route.idempotency_key?'WRITE_OUTCOME_UNKNOWN':options.signal?.aborted?'REQUEST_CANCELLED':'NETWORK_ERROR');
    }
    if(revision!==this.revision)throw new ApiError('SESSION_CHANGED');
    let value:unknown;
    try {value=await response.json();}catch {
      if(revision!==this.revision)throw new ApiError('SESSION_CHANGED');
      if(response.status===401){this.setSession(null);this.unauthorized?.();throw new ApiError('UNAUTHORIZED',401);}
      throw new ApiError(route.idempotency_key?'WRITE_OUTCOME_UNKNOWN':'CONTRACT_MISMATCH',response.status);
    }
    if(revision!==this.revision)throw new ApiError('SESSION_CHANGED');
    if(response.status===401){
      this.setSession(null);this.unauthorized?.();
      const failure=validSchema('ErrorEnvelope',value)?value as ApiModels['ErrorEnvelope']:null;
      throw new ApiError('UNAUTHORIZED',401,failure?.request_id??null);
    }
    if(!response.ok){
      if(!validSchema('ErrorEnvelope',value))throw new ApiError(route.idempotency_key?'WRITE_OUTCOME_UNKNOWN':'CONTRACT_MISMATCH',response.status);
      const failure=value as ApiModels['ErrorEnvelope'];
      throw new ApiError(failure.error.code,response.status,failure.request_id,failure.error.details??{});
    }
    if(!value||typeof value!=='object'||Array.isArray(value))throw new ApiError(route.idempotency_key?'WRITE_OUTCOME_UNKNOWN':'CONTRACT_MISMATCH');
    const envelope=value as Record<string,unknown>;
    if(Object.keys(envelope).some(key=>!['data','request_id','schema_version'].includes(key))||envelope.schema_version!==1||typeof envelope.request_id!=='string'||!envelope.request_id||!validSchema(route.response_schema_id,envelope.data))throw new ApiError(route.idempotency_key?'WRITE_OUTCOME_UNKNOWN':'CONTRACT_MISMATCH',response.status);
    return {data:envelope.data as ApiRoutes[K]['response'],requestId:envelope.request_id};
  }
}
