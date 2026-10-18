"""Real offline SentencePiece, mocked Gemini only; no provider-confirmed live counts."""
import asyncio,json
import httpx,pytest
from app.agents.tokens import plan,tokenizer
from app.agents.provider import Gemini,ProviderSettings,ProviderError,PROMPT
from app.agents.spending import Ledger,Pricing
from app.agents.policy import Permit
from app.agents.models import Selection
from tests.b10_fixtures import choose

def body(context):
    return {'contents':[{'role':'user','parts':[{'text':PROMPT+'\nCONTEXT_JSON:\n'+json.dumps(context,sort_keys=True,separators=(',',':'),allow_nan=False)}]}],'generationConfig':{'responseMimeType':'application/json','responseJsonSchema':Selection.model_json_schema(),'maxOutputTokens':4096,'thinkingConfig':{'thinkingLevel':'LOW'}}}

def response():return httpx.Response(200,json={'modelVersion':'gemini-3.8-flash','usageMetadata':{'promptTokenCount':100,'candidatesTokenCount':20,'thoughtsTokenCount':10,'totalTokenCount':130},'candidates':[{'content':{'parts':[{'text':json.dumps(choose())}]}}]})

def make(tmp_path,handler,*,verify=False):
    return Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key',CIVICLY_LLM_RETRY_WAIT_BUDGET=0),permit=Permit.mocked(),ledger=Ledger(tmp_path/'ledger'),transport=httpx.MockTransport(handler),verify_tokens=verify)

def test_official_vocab_smoke_and_byte_false_rejection_fixed(tmp_path):
    assert len(tokenizer().encode('What is your name?'))==5
    context={'source':'water '*20000};p=plan(body(context));seen=[]
    assert p['serialized_utf8_bytes']>60000>p['total_allowance_tokens']
    model=make(tmp_path,lambda r:(seen.append(r),response())[1]);result,used=asyncio.run(model.choose(context,60000))
    assert result.action=='PAUSE' and used==130 and len(seen)==1
    assert model.last_usage['requests'][0]['token_plan']['provider_count_tokens'] is None

@pytest.mark.parametrize('delta',[-1,0,1])
@pytest.mark.parametrize('verified',[False,True])
def test_exact_token_boundaries(tmp_path,delta,verified):
    c={'source':'water '*1000};allocation=plan(body(c),provider_count=1000 if verified else None);seen=[]
    def handle(req):
        seen.append(req.url.path)
        if req.url.path.endswith(':countTokens'):
            sent=json.loads(req.content);assert sent['generateContentRequest']['generationConfig']['responseJsonSchema']==Selection.model_json_schema()
            return httpx.Response(200,json={'totalTokens':1000})
        return response()
    m=make(tmp_path,handle,verify=verified)
    if delta<0:
        with pytest.raises(ProviderError,match='TOKEN_BUDGET'):asyncio.run(m.choose(c,allocation['total_allowance_tokens']+delta))
        assert not any(path.endswith(':generateContent') for path in seen)
    else:assert asyncio.run(m.choose(c,allocation['total_allowance_tokens']+delta))[1]==130
    if verified:
        assert m.ledger.summary()['uncertain_requests']==1  # Count result isn't a billing receipt.


def test_unknown_retry_token_allowance_survives_reopen(tmp_path):
    m=make(tmp_path,lambda r:httpx.Response(503,headers={'retry-after':'0'}));n=plan(body({}))['total_allowance_tokens']
    with pytest.raises(ProviderError,match='TOKEN_BUDGET'):asyncio.run(m.choose({},n))
    assert m.last_usage['accounted_tokens']==n and m.last_usage['total_tokens']==0
    assert Ledger(tmp_path/'ledger').thread_tokens(m.permit.thread_id)==n

@pytest.mark.parametrize('value',[-1,True,1.5,1_000_001])
def test_invalid_provider_counts_fail_without_generation(tmp_path,value):
    seen=[]
    def handle(req):seen.append(req.url.path);return httpx.Response(200,json={'totalTokens':value})
    m=make(tmp_path,handle,verify=True)
    with pytest.raises(ProviderError,match='INVALID_PROVIDER_COUNT'):asyncio.run(m.choose({},60000))
    assert len(seen)==1 and m.ledger.summary()['uncertain_requests']==1

@pytest.mark.parametrize('value',[-1,True,1.5,1_000_001])
def test_invalid_budget_never_calls_http(tmp_path,value):
    seen=[];m=make(tmp_path,lambda r:seen.append(r))
    with pytest.raises(ProviderError,match='INVALID_TOKEN_ALLOWANCE'):asyncio.run(m.choose({},value))
    assert not seen

@pytest.mark.parametrize('payload',[[],None,'bad',{'usageMetadata':[]}])
def test_malformed_provider_envelopes_hold_cost_and_tokens(tmp_path,payload):
    m=make(tmp_path,lambda r:httpx.Response(200,json=payload))
    with pytest.raises(ProviderError,match='PROVIDER_USAGE_MISSING'):asyncio.run(m.choose({},60000))
    assert m.last_usage['accounted_tokens']>0 and m.ledger.summary()['uncertain_requests']==1


def test_cumulative_actual_and_unknown_allowance_cannot_reset_on_reopen(tmp_path):
    m=make(tmp_path,lambda r:response());c={'state':{'tokens':100,'iterations':1,'wakes':0}}
    assert asyncio.run(m.choose(c,60000))[1]==130
    assert Ledger(tmp_path/'ledger').thread_tokens(m.permit.thread_id)==230
    # A stale checkpoint with a lower counter cannot erase durable exposure.
    c['state'].update(tokens=0,iterations=2);seen=[]
    again=Gemini(m.settings,permit=m.permit,ledger=Ledger(tmp_path/'ledger'),transport=httpx.MockTransport(lambda r:(seen.append(r),response())[1]))
    with pytest.raises(ProviderError,match='TOKEN_BUDGET'):asyncio.run(again.choose(c,plan(body(c))['total_allowance_tokens']))
    assert not seen and again.ledger.thread_tokens(m.permit.thread_id)==230

@pytest.mark.parametrize('value',[-1,True,1_000_001])
def test_invalid_usage_total_never_resets_unknown_allowance(tmp_path,value):
    def handle(req):return httpx.Response(200,json={'usageMetadata':{'totalTokenCount':value},'candidates':[{'content':{'parts':[{'text':json.dumps(choose())}]}}]})
    m=make(tmp_path,handle)
    with pytest.raises(ProviderError,match='PROVIDER_USAGE_MISSING'):asyncio.run(m.choose({},60000))
    assert m.ledger.thread_tokens(m.permit.thread_id)==plan(body({}))['total_allowance_tokens']
