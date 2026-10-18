"""B20 issue-only scripted choices, actual B19/HTTP/FalkorDB/MCP/LangGraph/Saver."""
import asyncio,copy,json,hashlib
from pathlib import Path
from uuid import uuid4
import pytest
from app.active import active_scope,load
from app.graph.repository import GraphRepository,PreconditionFailed
from app.graph.queries import GraphQueries
from app.agents.runtime import InvestigationAgent
from app.agents.models import InvestigationState,Budget
from app.agents.mcp import brokers
from app.agents.checkpoints import saver
from app.services.evidence import EvidenceService,Actor
from app.services.evidence.reader import Reader
from app.services.evidence.policies import POLICIES
from app.services.planning.models import PlanDraft
from app.services.planning.service import PlanningService,PlanningBlocked
from tests.b20_fixtures import shared,PolicyModel,AT
from tests.integration.test_demo_runtime import fresh,client_run,headers,inspection
from tests.b12_fixtures import sample,REQUIRED
pytestmark=pytest.mark.integration
ANALYST=Actor(id='B20-explicit-evaluator',role='ANALYST')
EXPECTED={
 'S01':({'BLOCKAGE':'SUPPORTED','CAPACITY_DEFICIT':'INCONCLUSIVE'},{'BLOCKAGE':'CONTRADICTED','CAPACITY_DEFICIT':'SUPPORTED'}),
 'S02':({'BLOCKAGE':'CONTRADICTED','CAPACITY_DEFICIT':'SUPPORTED'},{'BLOCKAGE':'CONTRADICTED','CAPACITY_DEFICIT':'SUPPORTED'}),
 'S03':({'SUBGRADE_FAILURE':'SUPPORTED','UTILITY_LEAK':'INCONCLUSIVE'},{'SUBGRADE_FAILURE':'INCONCLUSIVE','UTILITY_LEAK':'INCONCLUSIVE'}),
 'S04':({'SUBGRADE_FAILURE':'INCONCLUSIVE','UTILITY_LEAK':'SUPPORTED'},{'SUBGRADE_FAILURE':'INCONCLUSIVE','UTILITY_LEAK':'CONTRADICTED'}),
 'S05':({'MISSED_PICKUP':'SUPPORTED','CAPACITY_SHORTFALL':'SUPPORTED','ILLEGAL_DUMPING':'INCONCLUSIVE'},{'MISSED_PICKUP':'INCONCLUSIVE','CAPACITY_SHORTFALL':'INCONCLUSIVE','ILLEGAL_DUMPING':'INCONCLUSIVE'}),
 'S06':({'MISSED_PICKUP':'CONTRADICTED','CAPACITY_SHORTFALL':'INCONCLUSIVE','ILLEGAL_DUMPING':'SUPPORTED'},{'MISSED_PICKUP':'CONTRADICTED','CAPACITY_SHORTFALL':'INCONCLUSIVE','ILLEGAL_DUMPING':'INCONCLUSIVE'}),
}
def histories(r,inv):
 service=EvidenceService(r,clock=lambda:'2026-10-18T14:00:00.000000Z')
 return {r.get_node(e.target).properties['cause_code']:service.history(e.target,'2026-10-18T14:00:00.000000Z') for e in Reader(r,AT).edges('PROPOSES',source=inv)}
def proof_history(values):return {cause:[x.model_dump(mode='json') for x in rows] for cause,rows in values.items()}

async def run_agent(p,r,path,case,*,resume=False,thread=None):
 at='2026-10-18T12:00:02.000000Z' if resume and thread else '2026-10-18T11:00:00.000000Z'
 if resume:
  previous=saver(p).get_tuple({'configurable':{'thread_id':thread}})
  from datetime import datetime,timedelta
  at=(datetime.fromisoformat(previous.checkpoint['channel_values']['data']['as_of'].replace('Z','+00:00'))+timedelta(hours=1,seconds=1)).isoformat(timespec='microseconds').replace('+00:00','Z')
 async with brokers(p,path,timeout=10,memory_path=path.parent/'memory.json') as tools:
  model=PolicyModel(resume=resume);agent=InvestigationAgent(p,r,tools,model,saver(p),clock=lambda:at)
  thread=thread or uuid4().hex
  initial=None if resume else InvestigationState(graph=p.graph,investigation_id=case['investigation_id'],thread_id=thread,problem_cluster_id=case['cluster_id'],incident_ids=[case['incident_id']],asset_ids=[case['asset_id']],issue=case['issue_type'],inventory_hash=tools.inventory_hash,discovered_tool_names=[t['name'] for t in tools.catalog()],graph_revision=GraphQueries(r)._state(),as_of=at,budget=Budget(max_iterations=32))
  result=await agent.run(initial,thread_id=thread,resume=resume)
  assert result['__interrupt__'] and result['data']['pause_reason']=='MISSING_EVIDENCE',result['data']['errors']
  assert not any(e not in {'SOURCE_CHANGED_REFRESH_REQUIRED'} for e in result['data']['errors']),result['data']['errors']
  assert result['data']['executions'] and all(v.get('status')!='ERROR' for v in result['data']['observations'])
  if resume:assert model.contexts[0]['state']['refresh_required'] and not result['data']['refresh_required']
  snap=await agent.graph.aget_state({'configurable':{'thread_id':thread}})
  return agent,thread,result['data'],copy.deepcopy(snap)

async def draft_boundaries(shared,r,case,values):
 rows=[x[-1] for x in values.values()]
 from app.memory.models import sources
 source=next(s for s in sources() if s.owner_department_id==case['department_id'] and s.document_id!='D001-PDF')
 citation=(await shared.memory.retrieve(as_of=AT,document_id=source.document_id))['citations']
 assert citation
 value=sample();value.update(investigation_id=case['investigation_id'],issue=case['issue_type'])
 value['basis']=[{'hypothesis_id':a.hypothesis_id,'assessment_id':a.id,'reason':'Retain actual evaluated evidence and alternatives','addressed':i==0} for i,a in enumerate(rows)]
 ids=list(dict.fromkeys(id for a in rows for id in a.supporting_evidence_ids+a.contradicting_evidence_ids))
 value['evidence_ids']=ids or ['B20-MISSING-EVIDENCE']
 task=value['tasks'][0];task.update(target_ids=[case['asset_id']],department_id=case['department_id'],evidence_ids=value['evidence_ids'],assessment_ids=[rows[0].id],procedure_citation=citation[0])
 value['monitoring'].update(issue=case['issue_type'],required_evidence=REQUIRED[case['issue_type']])
 service=PlanningService(r,shared.memory,clock=lambda:'2026-10-18T14:00:00.000000Z')
 task_model=PlanDraft.model_validate(value).tasks[0]
 with pytest.raises(PlanningBlocked,match='OWNERSHIP_UNKNOWN_OR_CONFLICTING'):await service.resolve(task_model,Reader(r,AT),AT)
 with pytest.raises((PlanningBlocked,PreconditionFailed)):await service.create(value,request_id='B20-candidate-owner-or-missing-evidence',actor=ANALYST)
 invalid=copy.deepcopy(value);invalid['tasks'][0]['depends_on']=['inspect']
 with pytest.raises(ValueError):await service.create(invalid,request_id='B20-invalid-DAG',actor=ANALYST)
 missing=copy.deepcopy(value);missing['evidence_ids']=missing['tasks'][0]['evidence_ids']=['B20-MISSING-EVIDENCE']
 with pytest.raises(PlanningBlocked,match='EVIDENCE_OUTSIDE_ASSESSMENTS'):await service.create(missing,request_id='B20-missing-evidence',actor=ANALYST)
 # Force an unrelated supported remedy against the actual latest assessments.
 remedy={'WATERLOGGING':'DRAIN_BLOCKAGE_CLEARANCE','ROAD_DAMAGE':'SUBGRADE_REPAIR','WASTE_ACCUMULATION':'MISSED_PICKUP_RECOVERY'}[case['issue_type']]
 from app.services.planning.policy import validate_remediation
 forced=copy.deepcopy(value);forced['tasks'][0].update(action_type=remedy,remediation={'mode':'SUPPORTED_NOW','conditions':[{'kind':kind,'status':'MET','evidence_ids':forced['evidence_ids']} for kind in ['CAUSAL_INSPECTION','SAFETY_REVIEW']]})
 parsed=PlanDraft.model_validate(forced)
 with pytest.raises(PlanningBlocked):validate_remediation(parsed.tasks[0],parsed,Reader(r,AT),rows,PlanningBlocked)
 assert r._read('MATCH (p:ResolutionPlan) RETURN count(p)')==[[0]]
 return {'candidate_ownership_rejected':True,'missing_evidence_rejected':True,'invalid_DAG_rejected':True,'forced_remedy_without_required_causal_safety_evidence_rejected':True,'plan_count':0}

@pytest.mark.parametrize('scenario',[f'S{i:02}' for i in range(1,7)])
@pytest.mark.parametrize('variant',['PRIMARY','NEGATIVE'])
def test_six_scenario_behavior(shared,scenario,variant):
 async def run():
  setup=await fresh(shared,scenario,variant,'B20-'+scenario+'-'+variant);path=shared.path.parent/setup['profile_reference']/'profile.json';p=load(path);case=setup['scenario']['cases'][0]
  with active_scope(p):
   r=GraphRepository(shared.db,p.graph)
   agent,thread,baseline,old=await run_agent(p,r,path,case)
   before=histories(r,case['investigation_id']);assert len(before)>=2 and all(x[-1].assessment=='INCONCLUSIVE' for x in before.values())
   async def release(c,s):
    view,lead=await inspection(shared,c,case,'B20-release')
    body={'expected_current_stage':'BASELINE_VISIBLE','stage':'EVIDENCE_REVEALED','investigation_id':case['investigation_id'],'inspection_id':view['id'],'expected_hash':view['expected_hash']}
    res=await c.post('/api/v1/demo/scenarios/'+scenario+'/advance',json=body,headers=headers(shared,key='B20-release',field=lead,reviewer='OP-ANALYST'));assert res.status_code==200,res.json()
    return res.json()['data']
   released=await client_run(shared,path,release)
   agent,_,state,new=await run_agent(p,r,path,case,resume=True,thread=thread)
   assert (await agent.graph.aget_state(old.config)).values==old.values
   after=histories(r,case['investigation_id']);assert {k:v[-1].assessment for k,v in after.items()}==EXPECTED[scenario][variant=='NEGATIVE']
   assert all(v[0]==before[k][0] and v[-1].previous_assessment_id==v[0].id for k,v in after.items())
   for rows in after.values():
    a=rows[-1];assert a.rule_version==2 and a.classification and a.graph==p.graph
    assert all(ref.report and ref.report.review and ref.report.attribution and case['incident_id'] in ref.report.attribution.incident_ids for ref in a.evidence_references if ref.report)
   boundaries=await draft_boundaries(shared,r,case,after)
   extra={}
   if scenario=='S01' and variant=='PRIMARY':
    async def clear_drain(c,s):
     view,lead=await inspection(shared,c,case,'B20-clear-contradiction')
     q={'operation':'report_inspection','request_id':'B20-clear-contradiction','inspection_id':view['id'],'expected_hash':view['expected_hash'],'source_id':'B20-independent-clear-drain-survey','record_id':'B20-clear','observations':[{'asset_id':case['asset_id'],'code':'DRAIN_CLEAR','statement':'New independent synthetic clear-drain observation contradicts retained obstruction evidence','method':'SYNTHETIC_DRAIN_SURVEY','observed_at':AT}], 'review':{'reviewer_id':'OP-ANALYST','role':'ANALYST','reviewed':True,'reason':'Independent synthetic clear-drain review'},'attribution':{'incident_ids':[case['incident_id']],'rationale':'Direct present episode drainage survey'}}
     return EvidenceService(r,clock=lambda:AT).execute(q,shared.auth.resolve(shared.tokens[lead])).entity_id
    clear_id=await client_run(shared,path,clear_drain)
    agent,_,state,third=await run_agent(p,r,path,case,resume=True,thread=thread)
    revised=histories(r,case['investigation_id']);assert revised['BLOCKAGE'][-1].assessment=='INCONCLUSIVE'
    assert clear_id in revised['BLOCKAGE'][-1].contradicting_evidence_ids and revised['BLOCKAGE'][-1].supporting_evidence_ids
    assert revised['BLOCKAGE'][:2]==after['BLOCKAGE']
    assert (await agent.graph.aget_state(new.config)).values==new.values
    revision_boundaries=await draft_boundaries(shared,r,case,revised)
    from app.services.complaints import ComplaintService
    from app.services.demo.definitions import load as world_definitions,intake,BASE
    payload=intake(world_definitions()['S01'],case['issue_type']);payload['external_record_id']='B20-independent-same-event-report';payload['reported_at']=AT
    duplicate=ComplaintService(r,clock=lambda:AT).intake(payload)
    assert duplicate.incident_id==case['incident_id']
    assert r._read('MATCH (i:Incident) RETURN count(i)')==[[1]]
    extra={'clear_drain_report_id':clear_id,'revised_assessments':proof_history(revised),'revision_boundaries':revision_boundaries,'supported_to_inconclusive_with_contradiction':True,'second_checkpoint_unchanged':True,'duplicate_complaint_same_incident':duplicate.model_dump(mode='json')}
   if scenario=='S03':
    assert not after['UTILITY_LEAK'][-1].contradicting_evidence_ids
    async def utility(c,s):
     scoped={**case,'asset_id':'PIPE-100','department_id':'DEPT-WATER'};view,lead=await inspection(shared,c,scoped,'B20-separate-utility')
     actor=shared.auth.resolve(shared.tokens[lead])
     q={'operation':'report_inspection','request_id':'B20-separate-utility-pressure','inspection_id':view['id'],'expected_hash':view['expected_hash'],'source_id':'B20-independent-synthetic-utility-survey','record_id':scenario+'-'+variant,'observations':[{'asset_id':'PIPE-100','code':'PRESSURE_TEST_NORMAL','statement':'Separately attributed synthetic utility pressure test normal; no road-survey inference','method':'SYNTHETIC_UTILITY_PRESSURE_TEST','observed_at':AT}], 'review':{'reviewer_id':'OP-ANALYST','role':'ANALYST','reviewed':True,'reason':'Explicit synthetic target-specific utility review'},'attribution':{'incident_ids':[case['incident_id']],'rationale':'Direct present episode utility pressure survey'}}
     receipt=EvidenceService(r,clock=lambda:AT).execute(q,actor);return receipt.entity_id
    utility_id=await client_run(shared,path,utility)
    agent,_,state,third=await run_agent(p,r,path,case,resume=True,thread=thread)
    final=histories(r,case['investigation_id']);assert final['UTILITY_LEAK'][-1].assessment=='CONTRADICTED' and utility_id in final['UTILITY_LEAK'][-1].contradicting_evidence_ids
    assert (await agent.graph.aget_state(new.config)).values==new.values
    extra={'separate_utility_report_id':utility_id,'assessments_after_independent_utility':proof_history(final),'second_checkpoint_unchanged':True}
   async def views(c,s):
    out={}
    for suffix in ['hypotheses','graph','trace']:
     res=await c.get('/api/v1/investigations/'+case['investigation_id']+'/'+suffix,headers=headers(shared));assert res.status_code==200,res.json();out[suffix]=res.json()['data']
    return out
   from app.api.__main__ import configured_app
   import httpx
   app=configured_app(path,shared.auth.path,path.parent/'memory.json','2026-10-18T14:00:00.000000Z')
   async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://local') as c:
    public=await views(c,app.state.services)
   assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[0]]
   assert r._read("MATCH ()-[r:MAINTAINED_BY]->() WHERE r.association_status<>'CANDIDATE' RETURN count(r)")==[[0]]
   reports=[r.get_node(id,'Evidence').properties for id in released['released_evidence_ids']]
   proof={'mode':'ISSUE_ONLY_SCRIPTED_CHOICES_REAL_B19_HTTP_MCP_LANGGRAPH_FALKORDB_SAVER','scenario':scenario,'variant':variant,'source_graph':p.graph,'case':case,'thread_id':thread,'baseline':baseline,'after_release':state,'assessment_history':proof_history(after),'released_evidence':reports,'boundaries':boundaries,'public_views':public,'baseline_checkpoint_id':old.config['configurable']['checkpoint_id'],'baseline_checkpoint_unchanged':True,'no_work_or_verified_owner_fabricated':True,'provider_requests':0,**extra}
   Path('docs/evidence/B20-'+scenario+'-'+variant+'.json').write_text(json.dumps(proof,indent=2)+'\n')
 asyncio.run(run())

def test_supported_action_and_stale_citation_real_boundary(shared):
 """Separate authored verified-owner control, not a promoted B19 scenario owner."""
 from tests.b12_fixtures import prepared
 directory=shared.directory/'positive-policy-control';directory.mkdir(mode=0o700)
 p,r,clock,path,inv,draft,service=prepared(shared.db,directory,shared.memory,'WATERLOGGING',remedial=True)
 from datetime import datetime,timedelta
 # Real SDK citation retrieval uses wall time; move the authored clock forward,
 # never rewrite the returned citation to evade the future-citation guard.
 clock.value=max(clock.value,datetime.fromisoformat(draft.tasks[0].procedure_citation.retrieved_at.replace('Z','+00:00')))+timedelta(seconds=1)
 async def run():
  with active_scope(p):
   invalid=draft.model_dump(mode='json');quote=invalid['tasks'][0]['procedure_citation']['quote_excerpt'];invalid['tasks'][0]['procedure_citation']['quote_excerpt']=('X' if quote[0]!='X' else 'Y')+quote[1:]
   with pytest.raises(PlanningBlocked,match='PROCEDURE_STALE_REVOKED_OR_UNAVAILABLE'):await service.create(invalid,request_id='B20-stale-citation-control',actor=ANALYST)
   assert r._read('MATCH (p:ResolutionPlan) RETURN count(p)')==[[0]]
   receipt=await service.create(draft.model_dump(mode='json'),request_id='B20-valid-sourced-control',actor=ANALYST)
   saved=service.store.get(receipt.id);proof=saved['proof']['tasks']['remedy']
   assert proof['owners'][0]['department_id']=='DEPT-DRAIN' and proof['procedure_status']=='PROPOSED'
   assert proof['remediation']['unmet_guards']==[] and not proof['remediation']['execution_authority']
   again=await service.create(draft.model_dump(mode='json'),request_id='B20-valid-sourced-control',actor=ANALYST)
   assert again==receipt and r._read('MATCH (p:ResolutionPlan) RETURN count(p)')==[[1]]
   Path('docs/evidence/B20-planning-control.json').write_text(json.dumps({'mode':'REAL_DOMAIN_DB_SDK_AUTHORED_VERIFIED_OWNER_CONTROL_NOT_B19_SCENARIO_READINESS','graph':p.graph,'stale_citation_rejected_before_plan':True,'receipt':receipt.model_dump(mode='json'),'saved':saved,'idempotent_single_plan':True,'provider_requests':0},indent=2)+'\n')
 asyncio.run(run())
