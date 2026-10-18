"""One fresh B19 journey: real API/CLI/DB/SDK/MCP/Saver, scripted model only."""
import asyncio,copy,hashlib,json,os,subprocess,sys
from pathlib import Path
import httpx,pytest
from app.active import load,active_scope
from app.api.__main__ import configured_app
from app.agents.checkpoints import saver
from app.services.evidence import EvidenceService
from app.services.evidence.reader import Reader
from app.services.planning.models import PlanDraft
from app.services.planning.service import PlanningService,PlanningBlocked
from app.services.responsibility.service import Responsibility
from app.graph.repository import GraphRepository
from tests.b20_fixtures import shared
from tests.integration.test_demo_runtime import fresh,client_run,headers,inspection,AT
from tests.integration.test_scenario_behavior import run_agent,histories
from tests.b12_fixtures import sample
from tests.b13_fixtures import binding
pytestmark=pytest.mark.integration
T0='2026-10-19T12:00:00.000000Z';T1='2026-10-19T13:00:00.000000Z';T2='2026-10-19T14:00:00.000000Z'
async def api(shared,path,at,fn):
 app=configured_app(path,shared.auth.path,path.parent/'memory.json',at)
 async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://local') as c:return await fn(c,app.state.services)
def checkpoints(p):return {x.config['configurable']['checkpoint_id']:hashlib.sha256(json.dumps(x.checkpoint,sort_keys=True,default=str).encode()).hexdigest() for x in saver(p).list(None)}
def test_acquire_review_plan_stale_binding_and_uncertain_replay(shared,monkeypatch):
 async def run():
  receipt=await fresh(shared,'S01','PRIMARY','B20RO-source');path=shared.path.parent/receipt['profile_reference']/'profile.json';p=load(path);case=receipt['scenario']['cases'][0]
  with active_scope(p):
   r=GraphRepository(shared.db,p.graph);candidate=r.get_relationship(next(x[0] for x in r._read("MATCH (:InfrastructureAsset {id:$id})-[e:MAINTAINED_BY]->() RETURN e.id",{'id':case['asset_id']})))
   evidence=r.get_node(candidate.properties['source_evidence_id']);original=(candidate,evidence)
   agent,thread,baseline,old=await run_agent(p,r,path,case)
   async def release(c,s):
    view,lead=await inspection(shared,c,case,'B20RO-release')
    q={'expected_current_stage':'BASELINE_VISIBLE','stage':'EVIDENCE_REVEALED','investigation_id':case['investigation_id'],'inspection_id':view['id'],'expected_hash':view['expected_hash']}
    out=await c.post('/api/v1/demo/scenarios/S01/advance',json=q,headers=headers(shared,key='B20RO-release',field=lead,reviewer='OP-ANALYST'));assert out.status_code==200,out.json()
   await client_run(shared,path,release)
   agent,_,state,new=await run_agent(p,r,path,case,resume=True,thread=thread);frozen=checkpoints(p)
   from app.memory.models import sources
   src=next(s for s in sources(Path('data/documents/b12r/manifest.json')) if s.owner_department_id=='DEPT-DRAIN');await shared.memory.ingest(src)
   citation=(await shared.memory.retrieve(as_of=T0,document_id=src.document_id))['citations'][0]
   # Explicit new synthetic safety/causal inspection through existing accepted domain service.
   ev=EvidenceService(r,clock=lambda:T0);actor=shared.auth.resolve(shared.tokens['OP-DRAIN-LEAD']);analyst=shared.auth.resolve(shared.tokens['OP-ANALYST'])
   ins=ev.execute({'operation':'request_inspection','request_id':'B20RO-safety-request','investigation_id':case['investigation_id'],'asset_ids':[case['asset_id']],'department_id':'DEPT-DRAIN','inspection_type':'SYNTHETIC_CAUSAL_SAFETY_SURVEY'},analyst).entity_id
   for status in ['REQUESTED','SCHEDULED','IN_PROGRESS']:
    ev.execute({'operation':'transition_inspection','request_id':'B20RO-safety-'+status,'inspection_id':ins,'expected_hash':r.get_node(ins).content_hash,'status':status,**({'scheduled_at':T0} if status=='SCHEDULED' else {})},actor)
   report=ev.execute({'operation':'report_inspection','request_id':'B20RO-safety-report','inspection_id':ins,'expected_hash':r.get_node(ins).content_hash,'source_id':'B20RO-synthetic-field-team','record_id':'causal-safety-1','observations':[{'asset_id':case['asset_id'],'code':code,'statement':'Explicit authored synthetic field observation '+code,'method':'SYNTHETIC_FIELD_SURVEY','observed_at':T0} for code in ['OBSTRUCTION_OBSERVED','FLOW_RESTRICTED','DRAIN_CLEARANCE_SAFETY_REVIEWED']],'review':{'reviewer_id':analyst.id,'role':analyst.role,'reviewed':True,'reason':'Independent review of synthetic causal/safety survey'},'attribution':{'incident_ids':[case['incident_id']],'rationale':'Direct current episode survey'}},actor).entity_id
   hs={r.get_node(e.target).properties['cause_code']:e.target for e in Reader(r,T0).edges('PROPOSES',source=case['investigation_id'])};assessments=[]
   for cause in ['BLOCKAGE','CAPACITY_DEFICIT']:
    h=hs[cause];a=ev.execute({'operation':'assess','request_id':'B20RO-assess-'+cause,'hypothesis_id':h,'expected_hash':r.get_node(h).content_hash,'evidence_ids':[report],'as_of':T0},analyst).assessment;assessments.append(a)
   assert assessments[0].assessment=='SUPPORTED'
   value=sample();value['investigation_id']=case['investigation_id'];value['basis']=[{'hypothesis_id':a.hypothesis_id,'assessment_id':a.id,'reason':'Preserve reviewed evidence and competing mechanism','addressed':i==0} for i,a in enumerate(assessments)];value['evidence_ids']=[report]
   value['tasks'][0].update(action_type='DRAIN_BLOCKAGE_CLEARANCE',target_ids=[case['asset_id']],procedure_citation=citation,evidence_ids=[report],assessment_ids=[assessments[0].id],remediation={'mode':'SUPPORTED_NOW','conditions':[{'kind':k,'status':'MET','evidence_ids':[report]} for k in ['CAUSAL_INSPECTION','SAFETY_REVIEW']]})
   draft=PlanDraft.model_validate(value)
   private=path.parent;from cli.private import write_private,scope
   sessions={}
   for who in ['OP-DRAIN-LEAD','OP-ANALYST']:
    sessions[who]=private/(who+'.ownership-session.json');write_private(sessions[who],{'version':1,'scope':scope(p,shared.auth.path),'token':shared.tokens[who],'operator_id':who,'login_key':'B20RO-host-session'})
   calls=[]
   def cli(args,who='OP-DRAIN-LEAD'):
    env={**os.environ,'PYTHONPATH':str(Path('backend/test_guards').resolve())+os.pathsep+str(Path('backend').resolve())}
    done=subprocess.run([sys.executable,'-m','cli','--profile',str(path),'--auth-store',str(shared.auth.path),'--memory-profile',str(path.parent/'memory.json'),'--session',str(sessions[who]),'--at',T0,*args],capture_output=True,text=True,env=env,timeout=60)
    out=json.loads(done.stdout);assert done.returncode==0,out;assert all(t not in done.stdout+done.stderr for t in shared.tokens.values());calls.append({'command':' '.join(args[:2]),'status':out['status']});return out['data']
   body={'asset_id':case['asset_id'],'department_id':'DEPT-DRAIN','source_id':'B20RO-synthetic-inventory','source_record_id':'asset-responsibility','source_version':1,'source_kind':'SYNTHETIC','observed_at':AT,'valid_from':T0,'valid_to':T1}
   async def journey(c,s):
    blocked=await c.post('/api/v1/plans',json={'draft':value},headers=headers(shared,'OP-ANALYST','candidate-plan'));assert blocked.status_code==409
    for who in ['OP-ADMIN','OP-ANALYST','OP-APPROVER','OP-ROAD-LEAD']:
     denied=await c.post('/api/v1/responsibilities',json=body,headers=headers(shared,who,'wrong-submit-'+who));assert denied.status_code==403,denied.json()
    payload=private/'ownership-submit.json';payload.write_text(json.dumps(body));submitted=cli(['responsibility','submit','--payload',str(payload),'--key','B20RO-submit'])
    assert submitted['status']=='SUBMITTED' and submitted['applicability']=='UNREVIEWED'
    replay=await c.post('/api/v1/responsibilities',json=body,headers=headers(shared,'OP-DRAIN-LEAD','B20RO-submit'));assert replay.status_code==200 and replay.json()['data']==submitted
    conflict_source=await c.post('/api/v1/responsibilities',json={**body,'valid_to':T2},headers=headers(shared,'OP-DRAIN-LEAD','same-source-changed'));assert conflict_source.status_code==409
    rid=submitted['id'];submission_bytes=r.get_node(rid);review={'expected_hash':submitted['expected_hash'],'reviewed':True,'reason':'Independent authenticated synthetic inventory review'}
    for who in ['OP-DRAIN-LEAD','OP-ADMIN','OP-APPROVER']:
     denied=await c.post('/api/v1/responsibilities/'+rid+'/review',json=review,headers=headers(shared,who,'wrong-review-'+who));assert denied.status_code==403
    stale=await c.post('/api/v1/responsibilities/'+rid+'/review',json={**review,'expected_hash':'0'*64},headers=headers(shared,'OP-ANALYST','stale-review'));assert stale.status_code==409
    payload=private/'ownership-review.json';payload.write_text(json.dumps(review));verified=cli(['responsibility','review','--id',rid,'--payload',str(payload),'--key','B20RO-review'],'OP-ANALYST')
    assert r.get_node(rid)==submission_bytes
    assert verified['status']=='VERIFIED' and verified['applicability']=='CURRENT' and verified['reviewed_by']!=verified['submitted_by']
    replay=await c.post('/api/v1/responsibilities/'+rid+'/review',json=review,headers=headers(shared,'OP-ANALYST','B20RO-review'));assert replay.status_code==200 and replay.json()['data']==verified
    read=cli(['responsibility','get','--id',rid],'OP-ANALYST');assert read==verified
    asset=await c.get('/api/v1/assets/'+case['asset_id'],headers=headers(shared,'OP-DRAIN-LEAD'));assert asset.status_code==200,asset.json();assert asset.json()['data']['owner_department_id']=='DEPT-DRAIN' and asset.json()['data']['department_ids']==['DEPT-DRAIN']
    assert r.get_relationship(candidate.id)==original[0] and r.get_node(evidence.id)==original[1]
    made=await c.post('/api/v1/plans',json={'draft':value},headers=headers(shared,'OP-ANALYST','verified-plan'));assert made.status_code==200,made.json();planid=made.json()['data']['plan_id'];saved=s.ops.planning.store.get(planid);payload_hash=r._read('MATCH (d:CivicPlanDraft {id:$id}) RETURN d.payload_sha256',{'id':planid})
    assert saved['proof']['tasks']['inspect']['owners'][0]['relationship_id']==verified['relationship_id']
    # Ownership never satisfies a missing safety guard or a mismatching procedure.
    from app.services.planning.policy import validate_remediation
    bad=draft.model_copy(deep=True);bad.tasks[0].remediation.conditions[1].evidence_ids[:]=['MISSING']
    with pytest.raises(PlanningBlocked):validate_remediation(bad.tasks[0],bad,Reader(r,T0),assessments,PlanningBlocked)
    bad_task=draft.tasks[0].model_copy(update={'procedure_citation':draft.tasks[0].procedure_citation.model_copy(update={'quote_excerpt':'Not the actual source quote'})})
    with pytest.raises(PlanningBlocked,match='PROCEDURE_STALE'):await s.ops.planning.resolve(bad_task,Reader(r,T0),T0)
    # Same asset overlapping verified interval is rejected; the claim remains auditable.
    async def acquire(source,begin,end,department='DEPT-DRAIN'):
     lead='OP-DRAIN-LEAD' if department=='DEPT-DRAIN' else 'OP-ROAD-LEAD'
     sub=await c.post('/api/v1/responsibilities',json={**body,'department_id':department,'source_record_id':source,'valid_from':begin,'valid_to':end},headers=headers(shared,lead,source+'-submit'));assert sub.status_code==200,sub.json();data=sub.json()['data'];q={'expected_hash':data['expected_hash'],'reviewed':True,'reason':'Independent synthetic interval review'}
     return data,q
    conflict,q=await acquire('overlap',T0,T2,'DEPT-ROAD')
    rejected=await c.post('/api/v1/responsibilities/'+conflict['id']+'/review',json=q,headers=headers(shared,'OP-ANALYST','overlap-review'));assert rejected.status_code==409,rejected.json()
    future,q=await acquire('successor',T1,T2)
    reviewed=await c.post('/api/v1/responsibilities/'+future['id']+'/review',json=q,headers=headers(shared,'OP-ANALYST','successor-review'));assert reviewed.status_code==200,reviewed.json();assert reviewed.json()['data']['applicability']=='FUTURE'
    historical,q=await acquire('history','2026-10-18T12:00:00.000000Z','2026-10-18T13:00:00.000000Z')
    old=await c.post('/api/v1/responsibilities/'+historical['id']+'/review',json=q,headers=headers(shared,'OP-ANALYST','history-review'));assert old.status_code==200 and old.json()['data']['applicability']=='HISTORICAL',old.json()
    b=binding(saved);submitted_plan=await c.post('/api/v1/plans/'+planid+'/submit-approval',json={k:v for k,v in b.items() if k!='plan_id'},headers=headers(shared,'OP-ANALYST','submit-plan'));assert submitted_plan.status_code==200,submitted_plan.json();approval=submitted_plan.json()['data']
    decision={**b,'expected_hash':s.repo.get_node(approval['id']).content_hash,'decision':'APPROVED','reason':'Explicit independently approved exact synthetic plan'}
    res=await c.post('/api/v1/approvals/'+approval['id']+'/decision',json=decision,headers=headers(shared,'OP-APPROVER','decide-plan'));assert res.status_code==200,res.json()
    # Fault is an actual committed review followed by an injected readback error.
    uncertain,q=await acquire('fault-future',T2,'2026-10-19T15:00:00.000000Z')
    real=Responsibility.readback;invocations=[];execute=Responsibility.execute
    def counted(self,*a,**kw):invocations.append(a[0]);return execute(self,*a,**kw)
    def fault(self,id):
     out=real(self,id)
     if id==uncertain['id'] and out['status']=='VERIFIED':raise ValueError('PRIVATE_INJECTED_READBACK')
     return out
    monkeypatch.setattr(Responsibility,'execute',counted);monkeypatch.setattr(Responsibility,'readback',fault)
    response=await c.post('/api/v1/responsibilities/'+uncertain['id']+'/review',json=q,headers=headers(shared,'OP-ANALYST','uncertain-review'));assert response.status_code==409,response.json();error=response.json()['error'];assert error['code']=='RECOVERY_REQUIRED' and error['details']['commitment']=='UNKNOWN' and error['details']['entity_id']==uncertain['id']
    monkeypatch.setattr(Responsibility,'readback',real)
    replay=await c.post('/api/v1/responsibilities/'+uncertain['id']+'/review',json=q,headers=headers(shared,'OP-ANALYST','uncertain-review'));assert replay.status_code==409 and replay.json()['error']['details']==error['details']
    assert invocations==['review']
    retained=Responsibility(r,shared.auth,clock=lambda:T0).get(uncertain['id'],token=shared.tokens['OP-ANALYST']);assert retained['status']=='VERIFIED' and retained['applicability']=='FUTURE'
    assert r._read('MATCH ()-[e:MAINTAINED_BY {id:$id}]->() RETURN count(e)',{'id':retained['relationship_id']})==[[1]]
    intent=s.delivery.store.get('api_request',error['details']['request_id']);assert intent['status']=='DISPATCHING'
    events=s.delivery.discover();assert events # Includes the actual committed responsibility native events.
    assert s.delivery.store.get('delivery',retained['event_id'])['event']['type']=='GRAPH_EVIDENCE_CHANGED'
    assert checkpoints(p)==frozen and r.get_relationship(candidate.id)==candidate and r.get_node(evidence.id)==evidence
    return {'plan_id':planid,'binding':b,'approval_id':approval['id'],'saved_draft':saved,'payload_hash':payload_hash,'verified':verified,'successor':reviewed.json()['data'],'historical':old.json()['data'],'recovery':error,'uncertain_retained':retained,'same_key_no_redispatch':True,'candidate_and_source_hashes':[candidate.content_hash,evidence.content_hash],'checkpoints_preserved':True,'cli_calls':calls}
   proof=await api(shared,path,T0,journey)
   async def expired(c,s):
    current=await s.ops.planning.resolve(draft.tasks[0],Reader(r,T1),T1);assert current['owners'][0]['relationship_id']==proof['successor']['relationship_id']
    request={**proof['binding'],'approval_id':proof['approval_id'],'task_id':proof['binding']['assignments'][0]['task_id']}
    denied=await c.post('/api/v1/work-orders',json=request,headers=headers(shared,'OP-APPROVER','stale-owner-order'));assert denied.status_code==409,denied.json();assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[0]]
    with pytest.raises(Exception,match='OWNERSHIP_BINDING_CHANGED'):await s.ops.validate(proof['binding'],T1)
    now=s.ops.planning.store.get(proof['plan_id']);assert now['draft']==proof['saved_draft']['draft'] and now['receipt']==proof['saved_draft']['receipt']
    assert r._read('MATCH (d:CivicPlanDraft {id:$id}) RETURN d.payload_sha256',{'id':proof['plan_id']})==proof['payload_hash']
    return {'old_approval_cannot_authorize_new_work':True,'exact_half_open_successor_selected':True,'historical_draft_receipt_hash_unchanged':True,'work_orders':0}
   proof['stale_binding']=await api(shared,path,T1,expired)
   assert checkpoints(p)==frozen
   Path('docs/evidence/B20R-OWNERSHIP-real-proof.json').write_text(json.dumps({'mode':'REAL_B19_HTTP_CLI_FALKORDB_SDK_MCP_LANGGRAPH_SAVER_SCRIPTED_MODEL_NOT_GENUINE_AI','source_graph':p.graph,'case':case,'thread_id':thread,'baseline_checkpoint_id':old.config['configurable']['checkpoint_id'],'checkpoints':frozen,'synthetic_clock':[T0,T1,T2],'proof':proof,'provider_requests':0},indent=2)+'\n')
 asyncio.run(run())
