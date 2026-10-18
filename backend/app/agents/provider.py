"""Opt-in Gemini with durable reserved spending, strict JSON and bounded recovery."""
import asyncio,json,re,time
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4
import httpx
from pydantic import Field,SecretStr
from pydantic_settings import BaseSettings,SettingsConfigDict
from app.graph.models import digest
from .models import Selection
from .tokens import plan,total_usage
from .policy import LiveDenied
from .spending import Ledger,Pricing,SpendError

PROMPT_VERSION='B10-3'
PROMPT=(Path(__file__).parent/'prompts/B10-3.txt').read_text()

class ProviderSettings(BaseSettings):
    model_config=SettingsConfigDict(extra='ignore',hide_input_in_errors=True)
    provider:str=Field(default='gemini',validation_alias='CIVICLY_LLM_PROVIDER')
    model:str=Field(default='gemini-3.8-flash',validation_alias='CIVICLY_LLM_MODEL',pattern=r'^[A-Za-z0-9._-]{1,100}$')
    key:SecretStr|None=Field(default=None,validation_alias='GEMINI_API_KEY')
    timeout:float=Field(default=45,ge=1,le=60,validation_alias='CIVICLY_LLM_TIMEOUT')
    transient_retries:int=Field(default=2,ge=0,le=4,validation_alias='CIVICLY_LLM_TRANSIENT_RETRIES')
    retry_wait_budget:float=Field(default=8,ge=0,le=30,validation_alias='CIVICLY_LLM_RETRY_WAIT_BUDGET')
    pricing_file:Path|None=Field(default=None,validation_alias='CIVICLY_AI_PRICING_FILE')
    project_limit:str|None=Field(default=None,validation_alias='CIVICLY_AI_PROJECT_LIMIT_USD')

class ProviderError(RuntimeError):
    def __init__(self,code,category=None):self.code=code;self.category=category or code;super().__init__(code)

def retry_after_seconds(value):
    try:
        f=float(value)
        return f if 0<=f<=86400 else None
    except (TypeError,ValueError):return None

def classify(response):
    status=response.status_code;hint=retry_after_seconds(response.headers.get('retry-after'));quota=[]
    try:
        for detail in response.json().get('error',{}).get('details',[]):
            if str(detail.get('@type','')).endswith('QuotaFailure'):
                quota.extend(str(v.get('quotaId',''))+' '+str(v.get('quotaMetric','')) for v in detail.get('violations',[]))
            if str(detail.get('@type','')).endswith('RetryInfo') and hint is None:
                value=detail.get('retryDelay','')
                if re.fullmatch(r'\d+(?:\.\d+)?s',value):hint=retry_after_seconds(value[:-1])
    except Exception:pass
    names=' '.join(quota).lower()
    if status in (401,403):return 'AUTHENTICATION_OR_PERMISSION',None,False
    if status==400:return 'INVALID_CONFIGURATION',None,False
    if status==404:return 'MODEL_UNAVAILABLE',None,False
    if status==429:
        if any(s in names for s in ['perday','daily','per_day']):return 'DAILY_QUOTA_EXHAUSTED',hint,False
        if any(s in names for s in ['projectquota','billing','monthly','permonth']):return 'PROJECT_QUOTA_EXHAUSTED',hint,False
        if ('perminute' in names or 'persecond' in names or hint is not None) and (hint is None or hint<=8):return 'SHORT_TERM_THROTTLE',hint,True
        return 'QUOTA_OR_RATE_LIMIT_UNKNOWN',hint,False
    if status==503:return 'SERVICE_UNAVAILABLE',hint,True
    if status in (408,500,502,504):return 'TRANSIENT_HTTP',hint,True
    return 'NON_RETRYABLE_HTTP',hint,False

class Gemini:
    mode='LIVE_GEMINI'
    def __init__(self,settings,*,permit=None,ledger=None,pricing=None,transport=None,verify_tokens=None):
        if settings.provider!='gemini':raise ValueError('Unsupported provider; no automatic paid fallback')
        self.settings,self.permit,self.transport=settings,permit,transport
        if permit is not None and permit.mode=='MOCK_HTTP':self.mode='MOCK_GEMINI_HTTP'
        self.verify_tokens=(permit is not None and permit.mode=='LIVE') if verify_tokens is None else verify_tokens
        if permit is not None and permit.mode=='LIVE' and not self.verify_tokens:raise ValueError('Live generation requires provider token verification')
        self._ledger=ledger;self.pricing=pricing or Pricing(settings.pricing_file);self.owner=None;self.last_usage={};self.last_failure=None;self.requests_sent=0
    @property
    def ledger(self):
        if self._ledger is None:self._ledger=Ledger(project_limit=self.settings.project_limit)
        return self._ledger
    def check(self,context):
        if self.permit is None:raise ProviderError('LIVE_NOT_AUTHORIZED','EXECUTION_POLICY')
        try:self.permit.check(self.transport,context)
        except LiveDenied as e:raise ProviderError(str(e),'EXECUTION_POLICY') from None
        if self.settings.key is None:raise ProviderError('PROVIDER_CREDENTIAL_MISSING','AUTHENTICATION_OR_PERMISSION')
        self.pricing.validate(self.settings.model)
    @asynccontextmanager
    async def execution_scope(self,thread,investigation):
        context={'state':{'thread_id':thread,'investigation_id':investigation}}
        self.check(context)
        if (thread,investigation)!=(self.permit.thread_id,self.permit.investigation_id):raise ProviderError('LIVE_INVOCATION_SCOPE_MISMATCH')
        owner=uuid4().hex
        try:
            self.ledger.configure_case(self.permit.case_key,self.permit.max_usd)
            self.ledger.acquire(self.permit.case_key,thread,owner)
        except SpendError as e:raise ProviderError(str(e),'SPENDING_CONTROL') from None
        self.owner=owner;healthy=True
        async def beat():
            nonlocal healthy
            try:
                while True:
                    await asyncio.sleep(15);await asyncio.to_thread(self.ledger.heartbeat,owner)
            except asyncio.CancelledError:raise
            except Exception:healthy=False
        task=asyncio.create_task(beat())
        try:
            yield
            if not healthy:raise ProviderError('LIVE_SESSION_LOST')
        finally:
            task.cancel()
            try:await task
            except asyncio.CancelledError:pass
            self.owner=None;self.ledger.release(owner)
    def spending(self):return self.ledger.summary(self.permit.case_key) if self.permit else {'live_authorized':False}
    async def choose(self,context,remaining_tokens):
        self.last_usage={};self.last_failure=None;self.requests_sent=0
        try:self.check(context)
        except SpendError as e:raise ProviderError(str(e),'PRICING') from None
        try:
            if self.owner is None:
                async with self.execution_scope(self.permit.thread_id,self.permit.investigation_id):return await self._choose(context,remaining_tokens)
            return await self._choose(context,remaining_tokens)
        except TimeoutError:
            self.last_usage={**self.last_usage,'provider':self.settings.provider,'model':self.settings.model,'prompt_version':PROMPT_VERSION,'pricing_version':self.pricing.version,'attempts':self.requests_sent,'usage_status':'UNCERTAIN' if self.requests_sent else 'NOT_SENT','spending':self.spending()}
            self.last_failure={'category':'NETWORK_TIMEOUT','reservation_retained':self.requests_sent>0}
            raise ProviderError('PROVIDER_TIMEOUT','NETWORK_TIMEOUT') from None
    async def _choose(self,context,remaining_tokens):
        if type(remaining_tokens)is not int or not 0<=remaining_tokens<=1_000_000:raise ProviderError('INVALID_TOKEN_ALLOWANCE')
        state=context.get('state',{});base=state.get('tokens',0)
        if type(base)is not int or not 0<=base<=1_000_000:raise ProviderError('INVALID_TOKEN_BASELINE')
        ceiling=base+remaining_tokens;used_total=0;waited=0.;attempts=[];counts={}
        text=PROMPT+'\nCONTEXT_JSON:\n'+json.dumps(context,sort_keys=True,separators=(',',':'),allow_nan=False)
        group=digest([self.permit.thread_id,state.get('iterations'),state.get('wakes'),'provider-decision'])
        def exposure():return max(base,self.ledger.thread_tokens(self.permit.thread_id))
        def metadata():
            self.last_usage={**self.last_usage,'total_tokens':used_total,'accounted_tokens':max(0,self.ledger.thread_tokens(self.permit.thread_id)-base),
                'provider':self.settings.provider,'model':self.settings.model,'model_version':self.last_usage.get('model_version','UNAVAILABLE'),
                'prompt_version':PROMPT_VERSION,'pricing_version':self.pricing.version,'attempts':self.requests_sent,'requests':attempts,'spending':self.spending()}
        async with httpx.AsyncClient(timeout=self.settings.timeout,follow_redirects=False,transport=self.transport) as client:
            async with asyncio.timeout(2*self.settings.timeout+self.settings.retry_wait_budget):
                try:
                    for repair in range(2):
                        body={'contents':[{'role':'user','parts':[{'text':text}]}],'generationConfig':{'responseMimeType':'application/json','responseJsonSchema':Selection.model_json_schema(),'maxOutputTokens':4096,'thinkingConfig':{'thinkingLevel':'LOW'}}}
                        estimate=plan(body);count_key=digest(body)
                        if ceiling-exposure()<4096:raise ProviderError('TOKEN_BUDGET')
                        if self.verify_tokens and count_key not in counts:
                            # Counting is a real authorized/accounted RPC, not free billing metadata.
                            cid='AI-COUNT-'+digest([group,repair,count_key])
                            self.ledger.reserve(cid,self.permit.case_key,self.permit.thread_id,self.settings.model,self.permit.milestone,self.pricing.version,self.pricing.estimate(estimate['serialized_utf8_bytes'],0),self.owner)
                            self.requests_sent+=1
                            try:
                                counted=await client.post('https://generativelanguage.googleapis.com/v1beta/models/'+self.settings.model+':countTokens',headers={'x-goog-api-key':self.settings.key.get_secret_value()},json={'generateContentRequest':{'model':'models/'+self.settings.model,**body}})
                                value=counted.json()
                                if counted.status_code!=200:raise ProviderError('COUNT_HTTP_'+str(counted.status_code),classify(counted)[0])
                                count=value.get('totalTokens') if isinstance(value,dict) else None
                                if type(count)is not int or not 0<=count<=1_000_000:raise ProviderError('INVALID_PROVIDER_COUNT')
                                counts[count_key]=count
                            except (httpx.HTTPError,ValueError,TimeoutError):raise ProviderError('COUNT_TRANSPORT_OR_PAYLOAD','COUNT_UNAVAILABLE') from None
                            finally:
                                self.ledger.reconcile(cid,None,{},'COUNT_BILLING_UNCONFIRMED')
                                attempts.append({'request_id':cid,'kind':'COUNT_TOKENS','billing':'UNCERTAIN_RESERVATION_HELD','count_is_not_consumed_generation_tokens':True})
                        allocation=plan(body,provider_count=counts.get(count_key))
                        allocation['provider_count_origin']='SIMULATED_PROVIDER_RESPONSE' if self.mode=='MOCK_GEMINI_HTTP' and self.verify_tokens else ('PROVIDER_COUNT_API' if self.verify_tokens else 'NO_PROVIDER_COUNT')
                        for retry in range(self.settings.transient_retries+1):
                            request_id='AI-'+digest([group,repair,retry]);self.pricing.validate(self.settings.model)
                            reserve=self.pricing.estimate(allocation['serialized_utf8_bytes'],4096)
                            self.ledger.reserve(request_id,self.permit.case_key,self.permit.thread_id,self.settings.model,self.permit.milestone,self.pricing.version,reserve,self.owner,
                                token_reservation=allocation['total_allowance_tokens'],token_limit=ceiling,base_tokens=base)
                            self.requests_sent+=1
                            entry={'request_id':request_id,'kind':'GENERATE','token_plan':allocation,'reserved_nusd':reserve};attempts.append(entry)
                            try:
                                response=await client.post('https://generativelanguage.googleapis.com/v1beta/models/'+self.settings.model+':generateContent',headers={'x-goog-api-key':self.settings.key.get_secret_value()},json=body)
                            except (httpx.HTTPError,TimeoutError) as e:
                                category='NETWORK_TIMEOUT' if isinstance(e,(httpx.TimeoutException,TimeoutError)) else 'NETWORK_TRANSPORT'
                                self.ledger.reconcile(request_id,None,{},category);entry['category']=category
                                raise ProviderError('PROVIDER_TIMEOUT' if category=='NETWORK_TIMEOUT' else 'PROVIDER_TRANSPORT',category) from None
                            value={};usage={}
                            try:
                                parsed=response.json();value=parsed if isinstance(parsed,dict) else {}
                                raw_usage=value.get('usageMetadata',{})
                                if isinstance(raw_usage,dict):usage={k:v for k,v in raw_usage.items() if k in {'promptTokenCount','candidatesTokenCount','thoughtsTokenCount','totalTokenCount','cachedContentTokenCount','toolUsePromptTokenCount'} and type(v)is int and 0<=v<=1_000_000}
                            except ValueError:pass
                            actual=self.pricing.actual(usage);used=total_usage(usage);category=None
                            if response.status_code!=200:category,hint,retryable=classify(response)
                            self.ledger.reconcile(request_id,actual,usage,category or ('USAGE_UNCERTAIN' if actual is None else None))
                            if used is not None:used_total+=used
                            version=value.get('modelVersion',self.settings.model)
                            self.last_usage['model_version']=version if isinstance(version,str) and re.fullmatch(r'[A-Za-z0-9._-]{1,100}',version) else 'UNAVAILABLE'
                            entry.update({'status':response.status_code,'category':category,'usage':usage,'actual_nusd':actual,'consumed_tokens':used,'unknown_tokens_held':used is None})
                            metadata()
                            if exposure()>ceiling:raise ProviderError('TOKEN_BUDGET')
                            if response.status_code==200:break
                            delay=hint if hint is not None else min(2**retry,4)
                            can_retry=retryable and retry<self.settings.transient_retries and delay<=self.settings.retry_wait_budget-waited
                            self.last_failure={'category':category,'status_code':response.status_code,'request_id':request_id,'retry_after_seconds':hint,'retry_possible':can_retry}
                            if not can_retry:raise ProviderError('PROVIDER_HTTP_'+str(response.status_code),category)
                            await asyncio.sleep(delay);waited+=delay
                        if used is None or used==0:raise ProviderError('PROVIDER_USAGE_MISSING')
                        try:
                            raw=''.join(p.get('text','') for p in value['candidates'][0]['content']['parts'] if not p.get('thought'))
                            selection=Selection.model_validate_json(raw);self.last_failure=None
                            return selection,self.last_usage['accounted_tokens']
                        except Exception:
                            if repair:raise ProviderError('INVALID_MODEL_OUTPUT','INVALID_STRUCTURED_OUTPUT') from None
                            text+='\nPrevious output failed strict validation. Return exactly the supplied schema; no additional fields.'
                except SpendError as e:
                    category='SPENDING_CONTROL' if str(e)!='TOKEN_BUDGET' else 'TOKEN_BUDGET';self.last_failure={'category':category,'code':str(e)}
                    raise ProviderError(str(e),category) from None
                except ProviderError as e:
                    self.last_failure={**(self.last_failure or {}),'category':e.category,'code':e.code};raise
                finally:metadata()
        raise ProviderError('INVALID_MODEL_OUTPUT','INVALID_STRUCTURED_OUTPUT')
