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
    project_limit:str=Field(default='6',validation_alias='CIVICLY_AI_PROJECT_LIMIT_USD')

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
    def __init__(self,settings,*,permit=None,ledger=None,pricing=None,transport=None):
        if settings.provider!='gemini':raise ValueError('Unsupported provider; no automatic paid fallback')
        self.settings,self.permit,self.transport=settings,permit,transport
        if permit is not None and permit.mode=='MOCK_HTTP':self.mode='MOCK_GEMINI_HTTP'
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
        text=PROMPT+'\nCONTEXT_JSON:\n'+json.dumps(context,sort_keys=True,separators=(',',':'),allow_nan=False)
        if len(text.encode())+4096>remaining_tokens:raise ProviderError('TOKEN_BUDGET')
        used_total=0;waited=0.;attempts=[];state=context.get('state',{})
        group=digest([self.permit.thread_id,state.get('iterations'),state.get('wakes'),'provider-decision'])
        async with httpx.AsyncClient(timeout=self.settings.timeout,follow_redirects=False,transport=self.transport) as client:
            async with asyncio.timeout(2*self.settings.timeout+self.settings.retry_wait_budget):
                for repair in range(2):
                    for retry in range(self.settings.transient_retries+1):
                        if used_total+len(text.encode())+4096>remaining_tokens:
                            self.last_failure={'category':'TOKEN_BUDGET'}
                            raise ProviderError('TOKEN_BUDGET')
                        body={'contents':[{'role':'user','parts':[{'text':text}]}],'generationConfig':{'responseMimeType':'application/json','responseJsonSchema':Selection.model_json_schema(),'maxOutputTokens':4096,'thinkingConfig':{'thinkingLevel':'LOW'}}}
                        request_id='AI-'+digest([group,repair,retry])
                        self.pricing.validate(self.settings.model)
                        reserve=self.pricing.estimate(len(json.dumps(body,ensure_ascii=False).encode()),4096)
                        try:self.ledger.reserve(request_id,self.permit.case_key,self.permit.thread_id,self.settings.model,self.permit.milestone,self.pricing.version,reserve,self.owner)
                        except SpendError as e:
                            self.last_failure={'category':'SPENDING_CONTROL','code':str(e)}
                            raise ProviderError(str(e),'SPENDING_CONTROL') from None
                        self.requests_sent+=1
                        try:
                            response=await client.post('https://generativelanguage.googleapis.com/v1beta/models/'+self.settings.model+':generateContent',headers={'x-goog-api-key':self.settings.key.get_secret_value()},json=body)
                        except (httpx.HTTPError,TimeoutError) as e:
                            category='NETWORK_TIMEOUT' if isinstance(e,(httpx.TimeoutException,TimeoutError)) else 'NETWORK_TRANSPORT'
                            self.ledger.reconcile(request_id,None,{},category)
                            self.last_usage={'total_tokens':used_total,'provider':self.settings.provider,'model':self.settings.model,'model_version':'UNAVAILABLE','prompt_version':PROMPT_VERSION,'pricing_version':self.pricing.version,'attempts':self.requests_sent,'usage_status':'UNCERTAIN','spending':self.spending()}
                            self.last_failure={'category':category,'request_id':request_id}
                            raise ProviderError('PROVIDER_TIMEOUT' if category=='NETWORK_TIMEOUT' else 'PROVIDER_TRANSPORT',category) from None
                        value={};usage={}
                        try:
                            value=response.json()
                            usage={k:v for k,v in value.get('usageMetadata',{}).items() if k in {'promptTokenCount','candidatesTokenCount','thoughtsTokenCount','totalTokenCount','cachedContentTokenCount','toolUsePromptTokenCount'} and type(v)is int and v>=0}
                        except Exception:pass
                        actual=self.pricing.actual(usage)
                        category=None
                        if response.status_code!=200:category,hint,retryable=classify(response)
                        self.ledger.reconcile(request_id,actual,usage,category or ('USAGE_UNCERTAIN' if actual is None else None))
                        used=usage.get('totalTokenCount',0)
                        if type(used)is not int or used<0:used=0
                        used_total+=used
                        attempts.append({'request_id':request_id,'status':response.status_code,'category':category,'usage':usage,'reserved_nusd':reserve,'actual_nusd':actual})
                        self.last_usage={'total_tokens':used_total,'provider':self.settings.provider,'model':self.settings.model,'model_version':value.get('modelVersion',self.settings.model) if re.fullmatch(r'[A-Za-z0-9._-]{1,100}',str(value.get('modelVersion',self.settings.model))) else self.settings.model,
                            'prompt_version':PROMPT_VERSION,'pricing_version':self.pricing.version,'attempts':self.requests_sent,'requests':attempts,'spending':self.spending()}
                        if response.status_code==200:break
                        delay=hint if hint is not None else min(2**retry,4)
                        can_retry=retryable and retry<self.settings.transient_retries and delay<=self.settings.retry_wait_budget-waited
                        self.last_failure={'category':category,'status_code':response.status_code,'request_id':request_id,'retry_after_seconds':hint,'retry_possible':can_retry}
                        if not can_retry:raise ProviderError('PROVIDER_HTTP_'+str(response.status_code),category)
                        await asyncio.sleep(delay);waited+=delay
                    try:
                        if used_total>remaining_tokens:raise ProviderError('TOKEN_BUDGET')
                        if not used:raise ProviderError('PROVIDER_USAGE_MISSING')
                        raw=''.join(p.get('text','') for p in value['candidates'][0]['content']['parts'] if not p.get('thought'))
                        selection=Selection.model_validate_json(raw)
                        self.last_failure=None
                        return selection,used_total
                    except ProviderError:raise
                    except Exception:
                        self.last_failure={'category':'INVALID_STRUCTURED_OUTPUT','request_id':request_id}
                        if repair or used_total+len(text.encode())+4096>remaining_tokens:raise ProviderError('INVALID_MODEL_OUTPUT','INVALID_STRUCTURED_OUTPUT') from None
                        text+='\nPrevious output failed strict validation. Return exactly the supplied schema; no additional fields.'
        raise ProviderError('INVALID_MODEL_OUTPUT','INVALID_STRUCTURED_OUTPUT')
