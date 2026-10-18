"""Mock HTTP recovery with real durable reservations; simulated cost only."""
import asyncio,json
import httpx,pytest
from app.agents.provider import Gemini,ProviderSettings,ProviderError,classify
from app.agents.policy import Permit
from app.agents.spending import Ledger
from tests.b10_fixtures import choose


def response():return httpx.Response(200,json={'modelVersion':'gemini-3.8-flash','usageMetadata':{'promptTokenCount':50,'candidatesTokenCount':20,'thoughtsTokenCount':0,'totalTokenCount':70},'candidates':[{'content':{'parts':[{'text':json.dumps(choose())}]}}]})

def model(tmp_path,responses):
    seen=[]
    def handle(req):seen.append(1);value=responses.pop(0);return value
    p=Permit.mocked();return Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key',CIVICLY_LLM_RETRY_WAIT_BUDGET=0),permit=p,ledger=Ledger(tmp_path/'ledger'),transport=httpx.MockTransport(handle)),seen


def test_503_and_short_429_retry_are_each_reserved(tmp_path):
    m,seen=model(tmp_path,[httpx.Response(503,headers={'retry-after':'0'}),httpx.Response(429,headers={'retry-after':'0'}),response()])
    assert asyncio.run(m.choose({},60000))[0].action=='PAUSE'
    assert len(seen)==3 and m.last_usage['attempts']==3
    assert m.ledger.summary()['uncertain_requests']==2
    assert m.ledger.summary()['project_accounted']>m.last_usage['requests'][-1]['actual_nusd']

@pytest.mark.parametrize('status,body,category',[
 (401,{},'AUTHENTICATION_OR_PERMISSION'),(400,{},'INVALID_CONFIGURATION'),(404,{},'MODEL_UNAVAILABLE'),
 (429,{'error':{'details':[{'@type':'type.googleapis.com/google.rpc.QuotaFailure','violations':[{'quotaId':'GenerateRequestsPerDayPerProject'}]}]}},'DAILY_QUOTA_EXHAUSTED'),
 (429,{'error':{'details':[{'@type':'type.googleapis.com/google.rpc.QuotaFailure','violations':[{'quotaId':'ProjectQuotaExhausted'}]}]}},'PROJECT_QUOTA_EXHAUSTED'),
 (429,{},'QUOTA_OR_RATE_LIMIT_UNKNOWN')])
def test_non_transient_or_unknown_quota_not_retried(tmp_path,status,body,category):
    m,seen=model(tmp_path,[httpx.Response(status,json=body)])
    with pytest.raises(ProviderError):asyncio.run(m.choose({},60000))
    assert len(seen)==1 and m.last_failure['category']==category
    assert m.ledger.summary()['uncertain_requests']==1


def test_network_timeout_retains_reservation(tmp_path):
    m,seen=model(tmp_path,[])
    def timeout(req):raise httpx.ReadTimeout('Untrusted detail must not be copied')
    m.transport=httpx.MockTransport(timeout)
    with pytest.raises(ProviderError,match='PROVIDER_TIMEOUT'):asyncio.run(m.choose({},60000))
    assert m.last_failure['category']=='NETWORK_TIMEOUT' and m.ledger.summary()['uncertain_requests']==1


def test_unknown_usage_never_becomes_free(tmp_path):
    m,seen=model(tmp_path,[httpx.Response(200,json={'usageMetadata':{'totalTokenCount':70},'candidates':[{'content':{'parts':[{'text':json.dumps(choose())}]}}]})])
    asyncio.run(m.choose({},60000));assert m.ledger.summary()['project_accounted']>0 and m.ledger.summary()['uncertain_requests']==1


def test_retry_rechecks_remaining_token_budget_before_new_http(tmp_path):
    m,seen=model(tmp_path,[httpx.Response(503,headers={'retry-after':'0'},json={'usageMetadata':{'promptTokenCount':25000,'candidatesTokenCount':0,'totalTokenCount':25000}}),response()])
    with pytest.raises(ProviderError,match='TOKEN_BUDGET'):asyncio.run(m.choose({},30000))
    assert len(seen)==1 and m.last_failure['category']=='TOKEN_BUDGET'


def test_overall_deadline_retains_reservation_and_trace_versions(tmp_path,monkeypatch):
    m,seen=model(tmp_path,[])
    async def slow(req):
        await asyncio.sleep(1);return response()
    m.transport=httpx.MockTransport(slow)
    original=asyncio.timeout
    monkeypatch.setattr(asyncio,'timeout',lambda seconds:original(.01))
    with pytest.raises(ProviderError,match='PROVIDER_TIMEOUT'):asyncio.run(m.choose({},60000))
    assert m.ledger.summary()['uncertain_requests']==1
    assert m.last_usage['prompt_version']=='B10-3' and m.last_usage['usage_status']=='UNCERTAIN'
    assert m.last_failure['reservation_retained']


def test_invalid_json_exhausts_one_reserved_repair_only(tmp_path):
    bad=lambda:httpx.Response(200,json={'usageMetadata':{'promptTokenCount':50,'candidatesTokenCount':20,'totalTokenCount':70},'candidates':[{'content':{'parts':[{'text':'{'}]}}]})
    m,seen=model(tmp_path,[bad(),bad()])
    with pytest.raises(ProviderError,match='INVALID_MODEL_OUTPUT'):asyncio.run(m.choose({},60000))
    assert len(seen)==2 and m.last_failure['category']=='INVALID_STRUCTURED_OUTPUT'
    assert m.last_usage['attempts']==2 and m.ledger.summary()['uncertain_requests']==0
