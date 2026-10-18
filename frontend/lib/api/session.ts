import {ApiClient} from './client.ts';
import {ApiError} from './errors.ts';
import {validSchema} from './validation.ts';
import type {ApiModels} from '../generated/models.ts';
export type DemoIdentity={account:ApiModels['OperatorAccount'];expiresAt:string};
export class DemoConnection {
  readonly client:ApiClient;
  private fetcher:typeof fetch;
  private revision=0;
  private pending:Promise<DemoIdentity>|null=null;
  constructor(fetcher:typeof fetch=(...args)=>fetch(...args)){this.fetcher=fetcher;this.client=new ApiClient(fetcher);}
  getToken(): string|null { return this.client.getToken(); }
  open():Promise<DemoIdentity>{
    if(this.pending)return this.pending;
    const revision=++this.revision;
    this.pending=this.connect(revision).finally(()=>{if(revision===this.revision)this.pending=null;});
    return this.pending;
  }
  private async connect(revision:number):Promise<DemoIdentity>{
    let response:Response;
    try{response=await this.fetcher('/api/demo-session',{method:'POST',cache:'no-store',credentials:'omit',redirect:'error',signal:AbortSignal.timeout(15000)});}catch{throw new ApiError('DEMO_UNAVAILABLE');}
    if(revision!==this.revision)throw new ApiError('SESSION_CHANGED');
    let value:unknown;
    try{value=await response.json();}catch{throw new ApiError('CONTRACT_MISMATCH');}
    if(revision!==this.revision)throw new ApiError('SESSION_CHANGED');
    if(!response.ok){const error=validSchema('ErrorEnvelope',value)?value as ApiModels['ErrorEnvelope']:null;throw new ApiError('DEMO_UNAVAILABLE',response.status,error?.request_id??null);}
    const envelope=value as {data:ApiModels['DemoSession'];schema_version:number;request_id:string};
    if(!envelope||envelope.schema_version!==1||typeof envelope.request_id!=='string'||!validSchema('DemoSession',envelope.data))throw new ApiError('CONTRACT_MISMATCH');
    const session=envelope.data;const expires=Date.parse(session.expires_at);
    if(session.operator_id!=='OP-ANALYST'||session.role!=='ANALYST'||!session.access_token||!Number.isFinite(expires)||expires<=Date.now())throw new ApiError('CONTRACT_MISMATCH');
    this.client.setSession(session.access_token);
    try{
      const identity=await this.client.request('GET /api/v1/auth/me');
      if(revision!==this.revision)throw new ApiError('SESSION_CHANGED');
      if(identity.data.id!==session.operator_id||identity.data.role!==session.role)throw new ApiError('CONTRACT_MISMATCH');
      return {account:identity.data,expiresAt:session.expires_at};
    }catch(error){if(revision===this.revision)this.client.setSession(null);throw error;}
  }
  async close():Promise<void>{
    this.revision++;this.pending=null;
    const token=this.client.detach();
    if(!token)return;
    const revoker=new ApiClient(this.fetcher);revoker.setSession(token);
    try{await revoker.request('POST /api/v1/auth/logout',{body:{}});}finally{revoker.setSession(null);}
  }
  forget(){this.revision++;this.pending=null;this.client.setSession(null);}
}
