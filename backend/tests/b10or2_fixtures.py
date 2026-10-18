"""TEST ONLY representative B09 context and graph-reactive simulated Gemini HTTP."""
import asyncio,json,math
from pathlib import Path
from uuid import uuid4
import httpx
from app.active import active_scope
from app.agents.models import Selection
from app.agents.provider import Gemini,ProviderSettings,PROMPT
from app.agents.policy import Permit
from app.agents.spending import Ledger
from app.agents.tokens import plan
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.services.evidence.policies import POLICIES
from app.services.complaints import ComplaintService
from app.mcp.civicly.contracts import Context
from tests.b10_fixtures import create,state,choose,ScriptedModel
from tests.b08_fixtures import populate_history,payload
from tests.b09_fixtures import Fixture,propose,report,assess
from tests.schema_examples import edge,NOW

ASSET={'WATERLOGGING':'D1','ROAD_DAMAGE':'R1','WASTE_ACCUMULATION':'W1'}
CAUSE={'WATERLOGGING':'BLOCKAGE','ROAD_DAMAGE':'SUBGRADE_FAILURE','WASTE_ACCUMULATION':'MISSED_PICKUP'}
ALT={'WATERLOGGING':'CAPACITY_DEFICIT','ROAD_DAMAGE':'UTILITY_LEAK','WASTE_ACCUMULATION':'CAPACITY_SHORTFALL'}

def prepare(db,path,issue,topology='VERIFIED'):
 p,r,clock,receipt,inv=create(db,path,issue)
 with active_scope(p):
  populate_history(r)
  for kind,s,t,id in [('DRAINS_TO','D1','D2','FLOW'),('SERVES','D1','L1','DRAIN-LOCATION'),('UNDERLIES','P1','R1','PIPE-ROAD')]:
   r.create_relationship(kind,s,t,{**edge('R2-'+id),'valid_from':NOW,'source_evidence_id':'EV','association_status':topology if kind=='UNDERLIES' else 'VERIFIED'})
  if issue=='ROAD_DAMAGE':
   old=ComplaintService(r,clock=clock).intake(payload(issue,ref='R2-older-episode',occurred_at='2026-09-01T04:00:00Z',reported_at='2026-09-01T05:00:00Z'))
   assert old.incident_id!=receipt.incident_id
  f=Fixture(r,clock,{issue:receipt},p.graph,{})
  h=propose(f,inv,issue,CAUSE[issue]);rule=POLICIES[issue][CAUSE[issue]]
  report(f,inv,'r2-reviewed-contradiction',codes=rule['falsifying'][:1],assets=[ASSET[issue]])
  report(f,inv,'r2-unreviewed-support',codes=rule['confirming'][:1],assets=[ASSET[issue]],reviewed=False)
  for i in range(8):assess(f,h,ref='R2-history-'+str(i))
 return p,r,clock,receipt,inv,h

def history_read(c):
 s=c['state'];issue=s['issue'];asset=ASSET[issue]
 if issue=='WASTE_ACCUMULATION':return choose('READ',{'collection_point_id':asset,'days':30,'as_of':s['as_of']},'civicly::get_pickup_execution_history')
 return choose('READ',{'asset_id':asset,'from_time':'2026-10-01T00:00:00Z','to_time':s['as_of']},'civicly::get_maintenance_history')

def simulated_selection(c):
 """A test responder, not production routing or proof of genuine AI reasoning."""
 s=c['state'];hs=c['hypotheses'];last=s.get('selection');issue=s['issue'];asset=ASSET[issue]
 if not last or s['refresh_required'] or last['action']=='PAUSE':return history_read(c)
 if len(hs)<2:
  cause=ALT[issue];rule=POLICIES[issue][cause]
  args={'cause_code':cause,'asset_ids':['P1'] if issue=='ROAD_DAMAGE' else [asset],
   'statement':'Simulated competing explanation requiring evidence','mechanism':'Unverified alternative requiring discriminating observations',
   'confirming_codes':rule['confirming'],'falsifying_codes':rule['falsifying']}
  if issue=='ROAD_DAMAGE':args['topology']={'source_id':'P1','target_id':'R1','operation':'dependencies','max_hops':3}
  return choose('PROPOSE',args)
 if last['action']=='PROPOSE' or (last['action']=='READ' and 'trace_infrastructure_dependencies' not in last['tool_name']):return choose('ASSESS',{'hypothesis_id':hs[0]['id']})
 if last['action']=='ASSESS' and json.loads(last['arguments_json'])['hypothesis_id']==hs[0]['id']:
  return choose('READ',{'investigation_id':s['investigation_id'],'asset_id':'P1' if issue=='ROAD_DAMAGE' else asset,'network':'TYPED_DEPENDENCIES','direction':'DOWNSTREAM','max_hops':3,'as_of':s['as_of'],'include_candidates':False},'civicly::trace_infrastructure_dependencies')
 if last['action']=='READ':return choose('ASSESS',{'hypothesis_id':hs[1]['id']})
 if last['action']=='ASSESS':
  verified=any(v.get('kind')=='UNDERLIES' and v.get('properties',{}).get('association_status')=='VERIFIED' for v in c['facts'].values() if isinstance(v,dict))
  target='P1' if issue=='ROAD_DAMAGE' and verified else asset
  contrary=bool(hs[0]['assessments'][0]['classification']['reviewed_contradiction_ids'])
  return choose('INSPECT',{'asset_ids':[target],'department_id':'DEP','inspection_type':('CAPACITY_TEST' if contrary else 'DISCRIMINATING_FIELD_TEST')})
 return choose()

class SimulatedHTTP:
 def __init__(self,clock,*,fault=None):self.clock=clock;self.fault=fault;self.plans=[];self.receipts=[];self.counts=[];self.contexts=[];self.generated=0
 async def __call__(self,req):
  b=json.loads(req.content);counting=req.url.path.endswith(':countTokens')
  if counting:b={k:v for k,v in b['generateContentRequest'].items() if k!='model'}
  assert b['generationConfig']['responseJsonSchema']==Selection.model_json_schema()
  text=b['contents'][0]['parts'][0]['text'];assert text.startswith(PROMPT+'\nCONTEXT_JSON:\n')
  c=json.loads(text.split('\nCONTEXT_JSON:\n',1)[1].split('\nPrevious output failed strict validation.',1)[0])
  n=math.ceil(plan(b)['local_proxy_tokens']*1.05)
  if counting:self.counts.append(n);return httpx.Response(200,json={'totalTokens':n})
  self.generated+=1;self.contexts.append(c);self.plans.append(plan(b,provider_count=n))
  if self.fault=='503' and self.generated==1:return httpx.Response(503,headers={'retry-after':'0'},json={})
  usage={'promptTokenCount':n,'candidatesTokenCount':512,'thoughtsTokenCount':1536,'totalTokenCount':n+2048};self.receipts.append(usage)
  value={'SIMULATED_INVALID':True} if self.fault=='invalid' and self.generated==1 else simulated_selection(c)
  self.clock.advance()
  return httpx.Response(200,json={'modelVersion':'gemini-3.8-flash','usageMetadata':usage,'candidates':[{'content':{'parts':[{'text':json.dumps(value)}]}}]})

def model(s,directory,http,cap='.50'):
 return Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key',CIVICLY_LLM_RETRY_WAIT_BUDGET=0),permit=Permit(s.investigation_id,s.thread_id,'B10OR2-SIMULATED',cap,'MOCK_HTTP'),ledger=Ledger(Path(directory)/'ledger'),transport=httpx.MockTransport(http),verify_tokens=True)

async def initial(p,r,clock,receipt,inv,h,tools):
 s=state(p,r,tools,clock,receipt,inv,receipt.issue_type if hasattr(receipt,'issue_type') else r.get_node(receipt.incident_id).properties['issue_type']);s.hypotheses=[h]
 s.asset_ids=['D1','D2','P1','R1','W1']
 # Four real source observations, all retained; no enlarged fake transcript.
 for i in range(4):
  if s.issue=='WASTE_ACCUMULATION':args={'collection_point_id':'W1','days':30,'as_of':s.as_of};name='civicly::get_pickup_execution_history'
  else:args={'template':'node','id':receipt.incident_id};name='official::query_graph_readonly'
  if s.issue=='ROAD_DAMAGE':
   if i in {0,1}:
    args={'investigation_id':inv,'asset_id':'P1' if i==0 else 'D1','network':'TYPED_DEPENDENCIES','direction':'DOWNSTREAM','max_hops':3,'as_of':s.as_of,'include_candidates':i==0};name='civicly::trace_infrastructure_dependencies'
   elif i==3:
    old=r._read('MATCH (n:Incident) WHERE n.id<>$id RETURN n.id LIMIT 1',{'id':receipt.incident_id})[0][0]
    args={'template':'node','id':old}
  if s.issue=='WASTE_ACCUMULATION' and i==3:args={'template':'node','id':'SCHEDULE'};name='official::query_graph_readonly'
  ctx=Context(trace_id=s.thread_id,execution_id=uuid4().hex,investigation_id=inv,source_graph=p.graph,caller_role='READ_ONLY',invocation_origin='APPLICATION')
  result=await tools.call(name,args,ctx,'Authored context preparation, not model-selected',cutoff=s.as_of)
  if tools.last_cache_receipt:result={**result,'host_read_cache':tools.last_cache_receipt}
  s.observations.append(result)
 s.tool_calls=4
 return s
