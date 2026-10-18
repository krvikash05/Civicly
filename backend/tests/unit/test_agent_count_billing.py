"""Endpoint-specific billing and realistic receipts; all Gemini HTTP simulated."""
import asyncio,json,math,os,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
import httpx,pytest
from pydantic import ValidationError
from app.agents.provider import Gemini,ProviderSettings,ProviderError
from app.agents.policy import Permit
from app.agents.spending import Ledger,Pricing
from app.agents.models import Budget,InvestigationState
from app.agents.limits import CountBillingPolicy,INPUT_LIMIT,OUTPUT_LIMIT,MAX_RECEIPT_TOKENS,TOKEN_PROFILES
from app.agents.tokens import plan,total_usage
from tests.b10_fixtures import choose

def response(usage):return httpx.Response(200,json={'usageMetadata':usage,'candidates':[{'content':{'parts':[{'text':json.dumps(choose())}]}}]})
def make(tmp_path,handle,policy=None,**settings):
 return Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key',CIVICLY_LLM_TRANSIENT_RETRIES=0,**settings),permit=Permit('I','T','B10OR2','.50','MOCK_HTTP'),ledger=Ledger(tmp_path/'ledger'),transport=httpx.MockTransport(handle),verify_tokens=True,count_policy=policy)
def rows(m):
 with m.ledger.db() as db:return [dict(r) for r in db.execute('SELECT * FROM requests ORDER BY created')]

def test_repeated_successful_counts_release_all_dollar_exposure(tmp_path):
 seen=[]
 def handle(req):seen.append(req.url.path);return httpx.Response(200,json={'totalTokens':20000})
 m=make(tmp_path,handle)
 for i in range(8):
  with pytest.raises(ProviderError,match='TOKEN_BUDGET'):asyncio.run(m.choose({'state':{'iterations':i,'wakes':0,'tokens':0}},4096))
  assert m.ledger.summary()['project_accounted']==0
 assert len(seen)==8 and all(r['charged']==0 and r['status']=='SETTLED' for r in rows(m))
 assert all(json.loads(r['usage'])['provider_count_tokens']==20000 and 'totalTokenCount' not in json.loads(r['usage']) for r in rows(m))
 assert Ledger(tmp_path/'ledger').summary()['uncertain_requests']==0
 with m.ledger.db() as db:assert db.execute('SELECT count(*) FROM token_usage').fetchone()[0]==0
 # Reopen in a genuinely fresh interpreter; no session or hidden reservation remains.
 proc=subprocess.run([sys.executable,'-c',"from app.agents.spending import Ledger;import sys,json;print(json.dumps(Ledger(sys.argv[1]).summary()))",str(tmp_path/'ledger')],env={**os.environ,'PYTHONPATH':'backend'},capture_output=True,text=True,timeout=10)
 assert proc.returncode==0 and json.loads(proc.stdout)['project_accounted']==0

@pytest.mark.parametrize('status',[400,401,403,429,500,503])
def test_count_rejection_is_not_generation_or_unknown_billing(tmp_path,status):
 seen=[]
 m=make(tmp_path,lambda req:(seen.append(req.url.path),httpx.Response(status,json={}))[1])
 with pytest.raises(ProviderError,match='COUNT_HTTP_'+str(status)):asyncio.run(m.choose({},Budget().max_tokens))
 assert len(seen)==1 and m.ledger.summary()['project_accounted']==0
 assert json.loads(rows(m)[0]['usage'])['outcome']=='HTTP_'+str(status)


def test_count_timeout_has_unknown_completion_but_known_nonbilling(tmp_path):
 def handle(req):raise httpx.ReadTimeout('SIMULATED',request=req)
 m=make(tmp_path,handle)
 with pytest.raises(ProviderError,match='COUNT_TRANSPORT'):asyncio.run(m.choose({},Budget().max_tokens))
 r=rows(m)[0];assert r['charged']==0 and r['status']=='SETTLED'
 u=json.loads(r['usage']);assert u['outcome']=='COMPLETION_UNCONFIRMED' and u['provider_count_tokens'] is None
 assert not m.last_usage['total_tokens'] and m.ledger.thread_tokens('T')==0

@pytest.mark.parametrize('policy',[CountBillingPolicy(verified=False),CountBillingPolicy(version='UNVERIFIED_POLICY'),CountBillingPolicy(valid_until=datetime(2026,1,1,tzinfo=timezone.utc))])
def test_unknown_or_expired_count_billing_contract_retains_reservation(tmp_path,policy):
 m=make(tmp_path,lambda req:httpx.Response(200,json={'totalTokens':20000}),policy)
 with pytest.raises(ProviderError,match='TOKEN_BUDGET'):asyncio.run(m.choose({},4096))
 before=rows(m);assert before[0]['charged'] is None and before[0]['status']=='UNCERTAIN'
 assert m.ledger.summary()['project_accounted']==before[0]['reserved']>0
 assert rows(m)==before and Ledger(tmp_path/'ledger').summary()['project_accounted']>0

@pytest.mark.parametrize('failure',['503','timeout'])
def test_generation_uncertainty_is_still_reserved_after_free_count(tmp_path,failure):
 def handle(req):
  if req.url.path.endswith(':countTokens'):return httpx.Response(200,json={'totalTokens':20000})
  if failure=='timeout':raise httpx.ReadTimeout('SIMULATED',request=req)
  return httpx.Response(503,json={})
 m=make(tmp_path,handle)
 with pytest.raises(ProviderError):asyncio.run(m.choose({},Budget().max_tokens))
 c,g=rows(m);assert c['charged']==0 and g['charged'] is None
 assert m.ledger.summary()['project_accounted']==g['reserved'] and m.ledger.thread_tokens('T')==24112


def test_sequential_realistic_usage_is_not_counting_usage(tmp_path):
 receipts=[]
 def handle(req):
  data=json.loads(req.content);b=data.get('generateContentRequest',data);b={k:v for k,v in b.items() if k!='model'}
  n=math.ceil(plan(b)['local_proxy_tokens']*1.05)
  if req.url.path.endswith(':countTokens'):return httpx.Response(200,json={'totalTokens':n})
  u={'promptTokenCount':n,'candidatesTokenCount':512,'thoughtsTokenCount':1536,'totalTokenCount':n+2048};receipts.append(u);return response(u)
 m=make(tmp_path,handle);c={'source':'water '*20000,'state':{'iterations':0,'wakes':0,'tokens':0}}
 for i in range(8):
  c['state']['iterations']=i+1;_,used=asyncio.run(m.choose(c,Budget().max_tokens-c['state']['tokens']));c['state']['tokens']+=used
  assert m.ledger.thread_tokens('T')==sum(u['totalTokenCount'] for u in receipts)
  assert m.ledger.summary()['project_accounted']==sum(Pricing().actual(u) for u in receipts)
 assert len(receipts)==8 and c['state']['tokens']>60000
 assert all(u['totalTokenCount']>20000 for u in receipts)

@pytest.mark.parametrize('delta',[-1,0,1])
def test_request_input_limit_distinct_from_cumulative_allowance(tmp_path,delta):
 seen=[]
 def handle(req):
  seen.append(req.url.path)
  if req.url.path.endswith(':countTokens'):return httpx.Response(200,json={'totalTokens':1024+delta})
  return response({'promptTokenCount':1024+delta,'candidatesTokenCount':20,'totalTokenCount':1044+delta})
 m=make(tmp_path,handle,CIVICLY_LLM_MAX_INPUT_TOKENS=1024,CIVICLY_LLM_MAX_OUTPUT_TOKENS=512)
 if delta>0:
  with pytest.raises(ProviderError,match='PROVIDER_INPUT_LIMIT'):asyncio.run(m.choose({},Budget().max_tokens))
  assert len(seen)==1
 else:
  assert asyncio.run(m.choose({},Budget().max_tokens))[1]==1044+delta
  assert m.last_usage['configured_output_allowance']==512
 assert rows(m)[0]['charged']==0


def test_supported_capacity_profiles_and_saved_settings_are_distinct():
 c=json.loads(Path('contracts/gemini_provider.json').read_text())
 assert c['per_request']['published_input_tokens']==INPUT_LIMIT and c['per_request']['published_output_tokens']==OUTPUT_LIMIT
 assert c['count_billing']['policy_id']==CountBillingPolicy().version
 assert c['cumulative']['standard_tokens']==Budget().max_tokens
 assert (INPUT_LIMIT,OUTPUT_LIMIT)==(1048576,65536)
 assert TOKEN_PROFILES=={'standard':400000,'complex':800000} and Budget().max_tokens==400000
 assert Budget.model_validate({'max_tokens':60000}).max_tokens==60000
 assert total_usage({'totalTokenCount':MAX_RECEIPT_TOKENS})==MAX_RECEIPT_TOKENS
 assert total_usage({'totalTokenCount':MAX_RECEIPT_TOKENS+1}) is None
 for changes in [{'CIVICLY_LLM_MAX_INPUT_TOKENS':INPUT_LIMIT+1},{'CIVICLY_LLM_MAX_OUTPUT_TOKENS':OUTPUT_LIMIT+1}]:
  with pytest.raises(ValidationError):ProviderSettings(**changes)


@pytest.mark.parametrize('payload',[b'not JSON',b'[]'])
def test_malformed_count_response_is_failed_but_endpoint_is_nonbillable(tmp_path,payload):
 m=make(tmp_path,lambda req:httpx.Response(200,content=payload))
 with pytest.raises(ProviderError):asyncio.run(m.choose({},Budget().max_tokens))
 row=rows(m)[0];u=json.loads(row['usage'])
 assert row['charged']==0 and u['provider_count_tokens'] is None
 assert u['outcome'] in {'INVALID_RESPONSE','INVALID_PROVIDER_COUNT'}
 assert m.last_usage['total_tokens']==0


@pytest.mark.parametrize('nonbillable',[True,False])
def test_outer_deadline_count_summary_matches_durable_billing(tmp_path,nonbillable):
 async def handle(req):
  assert req.url.path.endswith(':countTokens')
  await asyncio.sleep(10)
 m=make(tmp_path,handle,CountBillingPolicy(verified=nonbillable),CIVICLY_LLM_TIMEOUT=1,CIVICLY_LLM_RETRY_WAIT_BUDGET=0)
 with pytest.raises(ProviderError,match='PROVIDER_TIMEOUT'):asyncio.run(m.choose({},Budget().max_tokens))
 row=rows(m)[0]
 assert row['charged']==(0 if nonbillable else None)
 assert m.last_failure['reservation_retained'] is (not nonbillable)
 assert m.last_usage['usage_status']=='NOT_GENERATED' and m.ledger.thread_tokens('T')==0
 assert json.loads(row['usage'])['outcome']=='COMPLETION_UNCONFIRMED'
 assert Ledger(tmp_path/'ledger').summary()['project_accounted']==(0 if nonbillable else row['reserved'])
