import asyncio,json,tempfile
from pathlib import Path
import httpx
from app.agents.provider import Gemini,ProviderSettings,ProviderError
from app.agents.models import Budget
from app.agents.policy import Permit
from app.agents.spending import Ledger,Pricing
from app.agents.tokens import plan
from tests.unit.test_agent_token_accounting import body
from tests.b10_fixtures import choose
async def main():
 with tempfile.TemporaryDirectory() as tmp:
  c={'source':'water '*20000,'state':{'iterations':0,'wakes':0,'tokens':0}};calls=[]
  def handle(req):
   b=json.loads(req.content);is_count=req.url.path.endswith(':countTokens');actual=b['generateContentRequest'] if is_count else b
   count=plan(actual)['local_proxy_tokens'];calls.append('COUNT' if is_count else 'GENERATE')
   if is_count:return httpx.Response(200,json={'totalTokens':count})
   return httpx.Response(200,json={'usageMetadata':{'promptTokenCount':count,'candidatesTokenCount':512,'thoughtsTokenCount':1536,'totalTokenCount':count+2048},'candidates':[{'content':{'parts':[{'text':json.dumps(choose())}]}}]})
  m=Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key'),permit=Permit('TEST_INV','TEST_THREAD','B10OR2','.50','MOCK_HTTP'),ledger=Ledger(Path(tmp)/'ledger'),transport=httpx.MockTransport(handle),verify_tokens=True);steps=[]
  for i in range(8):
   c['state']['iterations']=i+1
   try:_,used=await m.choose(c,Budget().max_tokens-c['state']['tokens']);c['state']['tokens']+=used;code='PASS'
   except ProviderError as e:code=e.code
   steps.append({'decision':i+1,'result':code,'tokens':c['state']['tokens'],'summary':m.ledger.summary(m.permit.case_key)})
   if code!='PASS':break
  with m.ledger.db() as db:rows=[dict(r) for r in db.execute('SELECT id,reserved,charged,status,usage,error FROM requests')]
  with m.ledger.db() as db:events=[dict(r) for r in db.execute('SELECT * FROM accounting_events ORDER BY id')]
  Path('docs/evidence/B10OR2-after-reproduction.json').write_text(json.dumps({'mode':'CORRECTED_ACTUAL_ADAPTER_MOCK_HTTP','baseline':'af42149','cumulative_default_tokens':Budget().max_tokens,'calls':calls,'steps':steps,'requests':rows,'immutable_accounting_events':events,'actual_external_gemini_requests':0},indent=2)+'\n')
  print(json.dumps({'cumulative_default':Budget().max_tokens,'step_results':[v['result'] for v in steps],'uncertain_counts':sum(r['error']=='COUNT_BILLING_UNCONFIRMED' for r in rows),'actual_gemini_requests':0}))
asyncio.run(main())
