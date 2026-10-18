"""One authorized B11 smoke; manual CLI outside pytest, no resume or cap flags."""
import argparse,asyncio,hashlib,json,os,sqlite3,sys
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.active import load,active_scope
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.schema import utc_now,timestamp
from app.agents.models import InvestigationState,Budget
from app.agents.provider import Gemini,ProviderSettings,PROMPT,ProviderError
from app.agents.policy import Permit
from app.agents.spending import Ledger,Pricing,DEFAULT_LEDGER
from app.agents.limits import CountBillingPolicy
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.agents.mcp import brokers
from app.memory.runtime import Profile,PROFILE
from app.mcp.civicly.contracts import Context
from app.graph.models import digest
PREFIX=ROOT/'docs/evidence/B11-LIVE-SMOKE-R-'
AGENT=ROOT/'.runtime/b11-live-smoke-r-agent.json'
MEMORY=ROOT/'.runtime/b11-live-smoke-r-memory.json'
STATE=ROOT/'.runtime/b11-live-smoke-r-state.json'
AUTH=Path(str(PREFIX)+'authorization.json')
STARTED=ROOT/'.runtime/b11-live-smoke-r-started.json'
CAP='.15'
def emit(suffix,value):
 Path(str(PREFIX)+suffix+'.json').write_text(json.dumps(value,indent=2,default=str)+'\n')
def private(path,value):
 fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w') as f:json.dump(value,f)
def smoke_graph(agent):
 # Public StateGraph compile flags; handlers/routing and native Saver unchanged.
 return agent.graph.builder.compile(checkpointer=agent.saver,
  interrupt_before=['RootCauseAnalyst','ResolutionPlanner','Coordinator'],interrupt_after=['Investigator'])
def settings():
 s=ProviderSettings(_env_file=ROOT/'.env').model_copy(update={'transient_retries':0,'retry_wait_budget':0.,'max_output_tokens':2048})
 assert s.model=='gemini-3.8-flash' and s.provider=='gemini' and s.key
 p=Pricing(s.pricing_file);p.validate(s.model)
 assert CountBillingPolicy().nonbillable(s.model,p.clock())
 return s,p
def accounting(case):
 # Inspect existing live ledger read-only, never initialize/reset during verification.
 with sqlite3.connect('file:'+str(DEFAULT_LEDGER)+'?mode=ro',uri=True) as db:
  db.row_factory=sqlite3.Row
  rows=[dict(r) for r in db.execute('SELECT * FROM requests WHERE case_id=? ORDER BY created,id',(case,))]
  caps=dict(db.execute('SELECT * FROM config').fetchone())
  known=sum(r['charged'] or 0 for r in rows)
  held=sum(r['reserved'] for r in rows if r['charged'] is None)
  return {'requests':rows,'known_nusd':known,'held_nusd':held,'exposure_nusd':known+held,'project_config':caps,
   'active_sessions':db.execute('SELECT count(*) FROM sessions').fetchone()[0],
   'open_holds':db.execute("SELECT count(*) FROM request_holds WHERE status='OPEN'").fetchone()[0],
   'generation_attempts':sum(not r['id'].startswith('AI-COUNT-') for r in rows),
   'count_attempts':sum(r['id'].startswith('AI-COUNT-') for r in rows)}
def sanitized_exceptions(exc):
 result=[]
 def walk(error,depth=0):
  if depth>8 or len(result)>=24:return
  code=getattr(error,'code',None);category=getattr(error,'category',None)
  safe=lambda v:v if isinstance(v,str) and __import__('re').fullmatch(r'[A-Z][A-Z0-9_]{0,79}',v) else None
  result.append({'class':type(error).__name__,'code':safe(code),'category':safe(category)})
  for child in getattr(error,'exceptions',[]):walk(child,depth+1)
  if error.__cause__ is not None:walk(error.__cause__,depth+1)
 walk(exc);return result

def temporal_preflight(repo,profile,initial,cutoff,*,checkpointer=None):
 """Read-only before ownership; fails before bind/provider on invalid preparation."""
 from app.services.evidence.reader import Reader
 if initial.graph!=profile.graph or repo.graph.name!=profile.graph:raise ValueError('SOURCE_PROFILE_MISMATCH')
 reader=Reader(repo,cutoff)
 inv=reader.node(initial.investigation_id,'Investigation')
 if inv.properties.get('thread_id') not in (None,initial.thread_id):raise ValueError('INCOMPATIBLE_THREAD_BINDING')
 if timestamp(inv.properties.get('updated_at',inv.properties['created_at']))>timestamp(cutoff):raise ValueError('NONMONOTONIC_BIND')
 expected=set(initial.incident_ids+[initial.problem_cluster_id])
 edges=reader.edges('INVESTIGATES',source=inv.id)
 if not expected<={e.target for e in edges}:raise ValueError('INVESTIGATION_REFERENCE_UNAVAILABLE')
 ids={inv.id,initial.problem_cluster_id,*initial.incident_ids,*initial.asset_ids}
 for id in ids:reader.node(id)
 asset_edges=[]
 for incident in initial.incident_ids:
  reader.node(incident,'Incident')
  asset_edges.extend(reader.edges('AFFECTS',source=incident))
  memberships=reader.edges('PART_OF',source=incident)
  if initial.problem_cluster_id not in {e.target for e in memberships}:raise ValueError('CLUSTER_REFERENCE_UNAVAILABLE')
  for edge in memberships:reader.node(edge.source);reader.node(edge.target)
 if not set(initial.asset_ids)<={e.target for e in asset_edges}:raise ValueError('ASSET_REFERENCE_UNAVAILABLE')
 for edge in edges+asset_edges:
  reader.node(edge.source);reader.node(edge.target)
 key='civicly:b10:'+profile.graph+':'+digest(initial.thread_id)
 if repo.client.connection.get(key+':quarantine'):raise ValueError('CHECKPOINT_QUARANTINED')
 if repo.client.connection.get(key):raise ValueError('THREAD_OWNERSHIP_BUSY')
 if (checkpointer or saver(profile)).get_tuple({'configurable':{'thread_id':initial.thread_id}}) is not None:raise ValueError('CHECKPOINT_ALREADY_EXISTS')
 return {'status':'PASS','cutoff':cutoff,'visible_required_ids':sorted(ids),'visible_relationships':sorted(e.id for e in edges+asset_edges),'binding_monotonic':True,'no_checkpoint_quarantine_or_owner':True}

async def prepare():
 private(ROOT/'.runtime/b11-live-smoke-r-preparing.json',{'scope':'One investigation only; no automatic reprepare','at':utc_now()})
 s,pricing=settings();existed=DEFAULT_LEDGER.exists();assert existed,'Use existing ledger only'
 ledger=Ledger(project_limit=s.project_limit)
 before=ledger.summary();assert not before['sessions'] and not before['holds'] and before['project_remaining']>=150000000
 from tests.b10_fixtures import create,state
 with connect(Settings(_env_file=ROOT/'.env')) as db:
  prepared_at=utc_now()
  p,r,clock,receipt,inv=create(db,AGENT,'WATERLOGGING',clock=lambda:prepared_at)
  existing=Profile.model_validate_json(PROFILE.read_text())
  mp=existing.model_copy(update={'source_graphs':[p.graph]});Profile.model_validate(mp);mp.json_private(MEMORY)
  thread=uuid4().hex
  permit=Permit.explicit_live(approved=True,investigation_id=inv,thread_id=thread,max_usd=CAP,milestone='B11-LIVE-SMOKE-R')
  ledger.configure_case(inv,CAP)
  with active_scope(p):
   async with brokers(p,AGENT,memory_path=MEMORY,timeout=10) as tools:
    catalog=tools.catalog();assert len(catalog)==16
    c=Context(trace_id=thread,execution_id='PREFLIGHT-'+uuid4().hex,source_graph=p.graph,investigation_id=inv,caller_role='READ_ONLY',invocation_origin='APPLICATION')
    result=await tools.call('civicly::get_organizational_procedures',{'department_id':'DEPT-DRAIN','action_type':'INSPECTION'},c,'Host nonbillable source capability preflight; not a model-selected call',cutoff=utc_now())
    assert result['procedures'] and all(v['citation']['owner_department_id']=='DEPT-DRAIN' for v in result['procedures'])
    user=db.connection.acl_getuser(p.read_user);assert '+graph.ro_query' in user['commands'] and '+graph.query' not in user['commands']
    assert user['keys']==['~'+p.graph]
    model=Gemini(s,permit=permit,ledger=ledger,pricing=pricing)
    initial=state(p,r,tools,utc_now,receipt,inv,thread=thread)
    initial.budget=Budget(max_iterations=2,max_tools=1,max_tokens=60000,max_seconds=120,max_wakes=1)
    initial.missing_evidence=['Source-backed Drainage Operations (DEPT-DRAIN) INSPECTION procedures and citations are needed before planning this synthetic waterlogging investigation. Choose one useful allowed READ; if organizational guidance cannot be accessed, report the limitation and select relevant graph evidence or pause.']
    agent=InvestigationAgent(p,r,tools,model,saver(p));agent.graph=smoke_graph(agent)
    temporal=temporal_preflight(r,p,initial,utc_now())
    context=agent.context(initial);model.check(context)
    text=PROMPT+'\nCONTEXT_JSON:\n'+json.dumps(context,sort_keys=True,separators=(',',':'),allow_nan=False)
    from app.agents.models import Selection
    body={'contents':[{'role':'user','parts':[{'text':text}]}],'generationConfig':{'responseMimeType':'application/json','responseJsonSchema':Selection.model_json_schema(),'maxOutputTokens':s.max_output_tokens,'thinkingConfig':{'thinkingLevel':'LOW'}}}
    from app.agents.tokens import plan
    allocation=plan(body);reservation=pricing.estimate(allocation['serialized_utf8_bytes'],s.max_output_tokens,input_tokens=allocation['input_allowance_tokens'])
    assert reservation<=150000000
    private(STATE,initial.model_dump(mode='json'))
    authorization={'task':'B11-LIVE-SMOKE-R','status':'READY','recorded_at':utc_now(),'profile_path':str(AGENT.relative_to(ROOT)),'memory_profile_path':str(MEMORY.relative_to(ROOT)),'graph':p.graph,'checkpoint_graph':p.checkpoints,'investigation_id':inv,'thread_id':thread,'model':s.model,'pricing_version':pricing.version,'max_total_usd':CAP,'max_generation_attempts':2,'transient_retries':0,'max_count_per_generation':1,'max_provider_selections':1,'max_live_wakes':1,'output_tokens':s.max_output_tokens,'budget':initial.budget.model_dump(),'initial_generation_reservation_nusd':reservation,'default_ledger_first_initialization':not existed,'ledger':str(DEFAULT_LEDGER.relative_to(ROOT)),'graph_interrupts':{'before':['RootCauseAnalyst','ResolutionPlanner','Coordinator'],'after':['Investigator']},'original_prompt_sha256':hashlib.sha256(PROMPT.encode()).hexdigest(),'prompt_version':__import__('app.agents.provider',fromlist=['PROMPT_VERSION']).PROMPT_VERSION,'original_attempt':json.loads((ROOT/'docs/evidence/B11-LIVE-SMOKE-authorization.json').read_text())['thread_id'],'temporal_preflight':temporal,'profile_sha256':hashlib.sha256(AGENT.read_bytes()).hexdigest(),'memory_profile_sha256':hashlib.sha256(MEMORY.read_bytes()).hexdigest(),'initial_state_sha256':hashlib.sha256(STATE.read_bytes()).hexdigest()}
    authorization['prompt_sha256']=authorization.pop('original_prompt_sha256')
    emit('authorization',authorization)
    emit('preflight',{'status':'PASS','authorization':authorization,'model_key_present_not_logged':True,'actual_mcp_catalog':catalog,'non_model_selected_source_result':result,'official_transport':tools.traces,'source_reader_commands':user['commands'],'source_reader_keys':user['keys'],'ledger_before':before,'ledger_after_case_allocation':ledger.summary(inv),'provider_calls':0,'token_plan':allocation})
    print(json.dumps(authorization,indent=2))
async def execute(approved):
 assert approved is True,'Explicit --live required'
 auth=json.loads(AUTH.read_text());assert auth['status']=='READY'
 for path,field in [(AGENT,'profile_sha256'),(MEMORY,'memory_profile_sha256'),(STATE,'initial_state_sha256')]:assert hashlib.sha256(path.read_bytes()).hexdigest()==auth[field]
 assert not STARTED.exists(),'One attempt only'
 p=load(AGENT);initial=InvestigationState.model_validate_json(STATE.read_text());assert (initial.thread_id,initial.investigation_id)==(auth['thread_id'],auth['investigation_id'])
 s,pricing=settings();ledger=Ledger(project_limit=s.project_limit)
 assert not accounting(initial.investigation_id)['requests']
 permit=Permit.explicit_live(approved=True,investigation_id=initial.investigation_id,thread_id=initial.thread_id,max_usd=CAP,milestone='B11-LIVE-SMOKE-R')
 model=Gemini(s,permit=permit,ledger=ledger,pricing=pricing);failure=None;result=None
 try:
  with connect(Settings(_env_file=ROOT/'.env')) as db,active_scope(p):
   r=GraphRepository(db,p.graph,lease_seconds=30)
   async with brokers(p,AGENT,memory_path=MEMORY,timeout=10) as tools:
    assert tools.inventory_hash==initial.inventory_hash
    agent=InvestigationAgent(p,r,tools,model,saver(p));agent.graph=smoke_graph(agent)
    temporal=temporal_preflight(r,p,initial,utc_now())
    assert hashlib.sha256(PROMPT.encode()).hexdigest()==auth['prompt_sha256']
    assert not ledger.summary()['sessions'] and not ledger.summary()['holds']
    private(STARTED,{'authorization_sha256':hashlib.sha256(AUTH.read_bytes()).hexdigest(),'started_at':utc_now(),'no_resume_or_second_wake':True,'temporal_preflight':temporal})
    result=await agent.run(initial,thread_id=initial.thread_id)
 except Exception as exc:failure={'observed_exceptions':sanitized_exceptions(exc),'diagnostic_inferences':[]}
 finally:
  finance=accounting(initial.investigation_id)
  assert finance['generation_attempts']<=2 and finance['count_attempts']<=2
  emit('execution',{'status':'FINISHED_REVIEW_REQUIRED','authorization':auth,'result':result,'host_failure':failure,'provider_usage':model.last_usage,'provider_failure':model.last_failure,'accounting':finance,'no_further_live_calls':True})
  print(json.dumps({'phase':'execution','host_failure':failure,'generation_attempts':finance['generation_attempts'],'count_attempts':finance['count_attempts'],'exposure_nusd':finance['exposure_nusd']}))
def verify():
 auth=json.loads(AUTH.read_text());p=load(AGENT);thread=auth['thread_id'];inv=auth['investigation_id']
 saved=saver(p).get_tuple({'configurable':{'thread_id':thread}})
 if saved is None:
  emit('fresh-process',{'status':'BLOCKED','native_checkpoint_id':None,'accounting':accounting(inv),'no_checkpoint':True,'no_resume':True});return
 state=InvestigationState.model_validate(saved.checkpoint['channel_values']['data'])
 from app.mcp.civicly.runtime import connections
 from app.mcp.civicly.storage import TraceStore
 with connect(Settings(_env_file=ROOT/'.env')) as db,active_scope(p),connections() as (_,writer,name):
  r=GraphRepository(db,p.graph);traces=TraceStore(writer,name)
  decisions=[{'id':id,'record':json.loads(r.get_node(id,'AgentDecision').properties['rationale'])} for id in state.decisions]
  actual_traces=[]
  for id in state.executions:
   row=traces.get(id);assert row is not None;actual_traces.append(row.model_dump(mode='json'))
   children=traces.repo._read('MATCH (d:CivicMCPTraceDetail) WHERE d.payload_json CONTAINS $id RETURN d.id LIMIT 8',{'id':id})
   for child, in children:
    item=traces.get(child)
    if item.context.parent_execution_id==id:actual_traces.append(item.model_dump(mode='json'))
  journals=[]
  for d in decisions:
   from app.agents.control import identity
   journal_id=identity('EV',thread,1,0);node=r._node_optional(journal_id)
   if node:journals.append({'id':journal_id,'payload':json.loads(node.properties['summary'])})
  selection=decisions[0]['record']['selection'] if decisions else None
  read_ok=bool(selection and selection['action']=='READ' and state.executions and state.observations and journals and journals[0]['payload']['status']=='COMMITTED')
  result=journals[0]['payload']['result'] if journals else {}
  citations=[v['citation'] for v in result.get('procedures',[])]+result.get('document_excerpt',{}).get('citations',[])
  evidence=bool(citations or result.get('rows') or result.get('data',{}).get('nodes'))
  validated=any(t['validated_output'] for t in actual_traces)
  if read_ok:
   assert digest(result)==actual_traces[0]['output_sha256']
   assert result in state.observations
  finance=accounting(inv)
  within_limits=finance['generation_attempts']<=2 and finance['count_attempts']<=2 and finance['exposure_nusd']<=150000000
  status='PASS' if read_ok and evidence and validated and citations and within_limits else 'PARTIAL' if read_ok and evidence and validated and within_limits else 'BLOCKED'
  emit('fresh-process',{'status':status,'checked_at':utc_now(),'process':os.getpid(),'authorization':auth,'native_checkpoint_id':saved.config['configurable'].get('checkpoint_id'),'next_pending_tasks':getattr(saved,'pending_writes',None),'state':state.model_dump(mode='json'),'durable_decisions':decisions,'durable_journals':journals,'durable_traces':actual_traces,'selected':selection,'live_organizational_citations':citations,'read_executed_persisted':read_ok,'validated_evidence_present':evidence and validated,'accounting':finance,'limits_observed':finance['generation_attempts']<=2 and finance['count_attempts']<=2 and finance['exposure_nusd']<=150000000,'b10_full_acceptance':'OPEN/PARTIAL','no_resume':True})
  print(json.dumps({'status':status,'native_checkpoint_id':saved.config['configurable'].get('checkpoint_id'),'selected':selection,'citations':len(citations),'accounting':finance},indent=2))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['prepare','execute','verify']);parser.add_argument('--live',action='store_true');args=parser.parse_args()
 if args.phase=='verify':verify()
 else:asyncio.run(prepare() if args.phase=='prepare' else execute(args.live))
if __name__=='__main__':main()
