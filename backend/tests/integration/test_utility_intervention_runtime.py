"""B20-R-UTILITY: real DB/GraphRAG/HTTP/CLI; explicit synthetic observations, no model."""
import asyncio,copy,json,os,subprocess,sys
from datetime import datetime
from pathlib import Path
import httpx,pytest
from app.active import load,active_scope
from app.api.__main__ import configured_app
from app.graph.repository import GraphRepository,PreconditionFailed
from app.services.evidence.service import EvidenceService
from app.services.evidence.reader import Reader
from app.services.evidence.policies import POLICIES
from app.services.operations.storage import Storage
from app.services.operations.execution import Execution
from app.services.planning.models import PlanDraft
from app.services.planning.policy import validate_remediation
from app.services.planning.service import PlanningBlocked
from app.memory.models import sources
from tests.b20_fixtures import shared
from tests.integration.test_demo_runtime import fresh,client_run,headers,inspection,AT
from tests.b12_fixtures import sample
from tests.b13_fixtures import binding
from tests.b14_fixtures import Run
from tests.b09_fixtures import Clock
pytestmark=pytest.mark.integration
T0='2026-10-19T12:00:00.000000Z'
class HTTPRun(Run):
 def __init__(self,r,clock,ops,tokens,c,shared):
  super().__init__(r,clock,ops,tokens,'ROAD_DAMAGE');self.c=c;self.shared=shared;self.lead='OP-WATER-LEAD';self.calls=[]
 def key(self):self.n+=1;return 'B20RU-work-'+str(self.n)
 async def call(self,q,operator=None,**kw):
  op=q['operation'];id=q.get('work_order_id');v={k:v for k,v in q.items() if k not in {'operation','request_id','work_order_id'}}
  if op=='inspect':v['command']={k:v for k,v in v['command'].items() if k!='request_id'}
  route={'order':'/api/v1/work-orders','update':f'/api/v1/work-orders/{id}/status','progress':f'/api/v1/work-orders/{id}/progress','inspect':f'/api/v1/work-orders/{id}/inspections','evaluate':f'/api/v1/work-orders/{id}/outcomes'}[op]
  h=headers(self.shared,operator or self.lead,q['request_id'],reviewer='OP-ANALYST' if kw.get('reviewer_token') else None)
  res=await self.c.post(route,json=v,headers=h);assert res.status_code==200,res.json();out=res.json()['data'];self.calls.append({'operation':op,'request_key':q['request_id'],'http':res.status_code})
  return {'entity_id':out['status']} if op=='inspect' else out
 async def select(self,index):
  self.assignment_index=index;a=self.b['assignments'][index];self.lead=a['assignee_id']
  self.w=await self.call({**self.b,'operation':'order','request_id':self.key(),'approval_id':self.approval,'task_id':a['task_id']},'OP-APPROVER')
  await self.call({'operation':'update','request_id':self.key(),'work_order_id':self.w['id'],'expected_hash':self.hash(),'new_status':'ASSIGNED','reason':'Assigned exact approved synthetic task'})
  await self.progress('START');return self.w

def test_s04_primary_utility_intervention_and_uncertainty(shared,monkeypatch):
 asyncio.run(journey(shared,'PRIMARY',monkeypatch))
def test_s04_negative_pressure_refuses_utility(shared):
 asyncio.run(journey(shared,'NEGATIVE',None))
async def journey(shared,variant,monkeypatch):
 receipt=await fresh(shared,'S04',variant,'B20RU-'+variant+'-setup');path=shared.path.parent/receipt['profile_reference']/'profile.json';p=load(path);case=receipt['scenario']['cases'][0]
 async def release(c,s):
  view,lead=await inspection(shared,c,case,'B20RU-'+variant+'-release')
  response=await c.post('/api/v1/demo/scenarios/S04/advance',json={'expected_current_stage':'BASELINE_VISIBLE','stage':'EVIDENCE_REVEALED','investigation_id':case['investigation_id'],'inspection_id':view['id'],'expected_hash':view['expected_hash']},headers=headers(shared,key='B20RU-'+variant+'-release',field=lead,reviewer='OP-ANALYST'));assert response.status_code==200,response.json();return response.json()['data']['released_evidence_ids']
 released=await client_run(shared,path,release)
 clock=Clock();clock.value=datetime.fromisoformat(T0.replace('Z','+00:00'))
 with active_scope(p):
  r=GraphRepository(shared.db,p.graph);ev=EvidenceService(r,clock=clock);analyst=shared.auth.resolve(shared.tokens['OP-ANALYST']);lead=shared.auth.resolve(shared.tokens['OP-WATER-LEAD']);hyp={}
  frozen={e.id:e.content_hash for e in r._edges('MAINTAINED_BY')};original_reports={id:r.get_node(id).content_hash for id in released}
  for cause,target in [('UTILITY_LEAK','PIPE-100'),('SUBGRADE_FAILURE','ROAD-100')]:
   rule=POLICIES['ROAD_DAMAGE'][cause]
   q={'operation':'propose','request_id':'B20RU-'+variant+'-'+cause,'investigation_id':case['investigation_id'],'incident_ids':[case['incident_id']],'asset_ids':[target],'cause_code':cause,'statement':'Explicit synthetic competing mechanism '+cause,'mechanism':'Independently inspect the concerned asset; topology alone is not proof','confirming_codes':rule['confirming'],'falsifying_codes':rule['falsifying']}
   if cause=='UTILITY_LEAK':q['topology']={'source_id':'PIPE-100','target_id':'ROAD-100','operation':'dependencies','max_hops':3}
   hyp[cause]=ev.execute(q,analyst).entity_id
  if variant=='NEGATIVE':
   assessed=ev.execute({'operation':'assess','request_id':'B20RU-negative-assess','hypothesis_id':hyp['UTILITY_LEAK'],'expected_hash':r.get_node(hyp['UTILITY_LEAK']).content_hash,'evidence_ids':released,'as_of':clock()},analyst).assessment
   assert assessed.assessment=='CONTRADICTED',assessed
   from tests.unit.test_utility_intervention import draft
   d=draft();t=d.tasks[0].model_copy(update={'assessment_ids':[assessed.id]});d=d.model_copy(update={'basis':[d.basis[0].model_copy(update={'assessment_id':assessed.id}),d.basis[1]]})
   with pytest.raises(PlanningBlocked,match='REMEDIAL_EVIDENCE_INSUFFICIENT'):validate_remediation(t,d,Reader(r,clock()),[assessed],PlanningBlocked)
   assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[0]] and r._read('MATCH (p:ResolutionPlan) RETURN count(p)')==[[0]]
   Path('docs/evidence/B20R-UTILITY-negative-proof.json').write_text(json.dumps({'source_graph':p.graph,'case':case,'released_ids':released,'assessment':assessed.model_dump(mode='json'),'utility_actions_blocked':True,'work_orders':0,'provider_requests':0},indent=2)+'\n');return
  # Additional explicitly authorized attributed survey, separate from B19 reveal.
  reports=[];assessments=[]
  for cause,target,dept,who,codes in [('UTILITY_LEAK','PIPE-100','DEPT-WATER','OP-WATER-LEAD',['LEAK_DETECTED','INFILTRATION_AT_DAMAGE','UTILITY_SAFETY_REVIEWED']),('SUBGRADE_FAILURE','ROAD-100','DEPT-ROAD','OP-ROAD-LEAD',['SUBGRADE_FAILURE_OBSERVED','STRUCTURAL_TEST_FAILED','SUBGRADE_REPAIR_SAFETY_REVIEWED'])]:
   actor=shared.auth.resolve(shared.tokens[who]);iid=ev.execute({'operation':'request_inspection','request_id':'B20RU-'+cause+'-survey','investigation_id':case['investigation_id'],'asset_ids':[target],'department_id':dept,'inspection_type':'EXPLICIT_SYNTHETIC_CAUSAL_SAFETY_SURVEY'},analyst).entity_id
   for status in ['REQUESTED','SCHEDULED','IN_PROGRESS']:
    ev.execute({'operation':'transition_inspection','request_id':'B20RU-'+cause+'-'+status,'inspection_id':iid,'expected_hash':r.get_node(iid).content_hash,'status':status,**({'scheduled_at':clock()} if status=='SCHEDULED' else {})},actor)
   rid=ev.execute({'operation':'report_inspection','request_id':'B20RU-'+cause+'-report','inspection_id':iid,'expected_hash':r.get_node(iid).content_hash,'source_id':'B20RU-explicit-synthetic-survey','record_id':cause,'observations':[{'asset_id':target,'code':code,'statement':'Explicit authorized synthetic observation '+code,'method':'DIRECT_SYNTHETIC_FIELD_TEST','observed_at':clock()} for code in codes],'review':{'reviewer_id':analyst.id,'role':analyst.role,'reviewed':True,'reason':'Independent review of explicit synthetic causal and safety survey'},'attribution':{'incident_ids':[case['incident_id']],'rationale':'Explicit current episode target observation'}},actor).entity_id;reports.append(rid)
   a=ev.execute({'operation':'assess','request_id':'B20RU-'+cause+'-assessment','hypothesis_id':hyp[cause],'expected_hash':r.get_node(hyp[cause]).content_hash,'evidence_ids':[rid]+(released if cause=='UTILITY_LEAK' else []),'as_of':clock()},analyst).assessment;assert a.assessment=='SUPPORTED',a;assessments.append(a)
  citations={}
  for manifest in ['data/documents/b20r_utility/manifest.json','data/documents/b12r/manifest.json']:
   source=next(s for s in sources(Path(manifest)) if s.document_id in {'D022','D020'});await shared.memory.ingest(source);citations[source.owner_department_id]=(await shared.memory.retrieve(as_of=clock(),document_id=source.document_id))['citations'][0]
  app=configured_app(path,shared.auth.path,path.parent/'memory.json',T0)
  async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://local') as c:
   s=app.state.services;s.clock=clock;s.ops.clock=clock;s.ops.planning.clock=clock;s.delivery.clock=clock;s.reads.clock=clock
   for target,dept,who in [('PIPE-100','DEPT-WATER','OP-WATER-LEAD'),('ROAD-100','DEPT-ROAD','OP-ROAD-LEAD')]:
    sub=await c.post('/api/v1/responsibilities',json={'asset_id':target,'department_id':dept,'source_id':'B20RU-synthetic-inventory','source_record_id':target,'source_kind':'SYNTHETIC','observed_at':AT,'valid_from':T0},headers=headers(shared,who,'B20RU-own-'+target));assert sub.status_code==200,sub.json();v=sub.json()['data']
    reviewed=await c.post('/api/v1/responsibilities/'+v['id']+'/review',json={'expected_hash':v['expected_hash'],'reviewed':True,'reason':'Independent review of explicit synthetic responsibility record'},headers=headers(shared,'OP-ANALYST','B20RU-own-review-'+target));assert reviewed.status_code==200,reviewed.json()
   value=sample();value.update(investigation_id=case['investigation_id'],issue='ROAD_DAMAGE',basis=[{'hypothesis_id':a.hypothesis_id,'assessment_id':a.id,'reason':'Reviewed distinct causal mechanism; retain alternative','addressed':True} for a in assessments],evidence_ids=reports+released)
   value['monitoring'].update(issue='ROAD_DAMAGE',required_evidence=['WEAR_EXPOSURE','FOLLOWUP_PAVEMENT'])
   base=value['tasks'][0];base.update(evidence_ids=reports,assessment_ids=[a.id for a in assessments])
   value['tasks']=[]
   for id,action,target,dept,index,dependency,guard in [('isolate','UTILITY_ISOLATION','PIPE-100','DEPT-WATER',0,None,None),('repair','UTILITY_LEAK_REPAIR','PIPE-100','DEPT-WATER',0,'isolate','ISOLATION_PROOF'),('road','SUBGRADE_REPAIR','ROAD-100','DEPT-ROAD',1,'repair','UTILITY_VERIFICATION')]:
    t=copy.deepcopy(base);t.update(id=id,action_type=action,target_ids=[target],department_id=dept,assessment_ids=[assessments[index].id],procedure_citation=citations[dept],depends_on=[dependency] if dependency else [],remediation={'mode':'CONDITIONAL' if guard else 'SUPPORTED_NOW','conditions':[{'kind':k,'status':'MET','evidence_ids':[reports[index]]} for k in ['CAUSAL_INSPECTION','SAFETY_REVIEW']]})
    if guard:t['remediation']['conditions'].append({'kind':guard,'status':'UNMET','depends_on_task_id':dependency})
    value['tasks'].append(t)
   # Retain an independently recorded scope/extent uncertainty using an existing
   # cause code. This is a hypothesis, not another asserted physical fact.
   alternative=ev.execute({'operation':'propose','request_id':'B20RU-alternative','investigation_id':case['investigation_id'],'incident_ids':[case['incident_id']],'asset_ids':['ROAD-100'],'cause_code':'SUBGRADE_FAILURE','statement':'Alternative extent of road damage remains uncertain','mechanism':'Possible independently unsupported extent; do not authorize extra work','confirming_codes':POLICIES['ROAD_DAMAGE']['SUBGRADE_FAILURE']['confirming'],'falsifying_codes':POLICIES['ROAD_DAMAGE']['SUBGRADE_FAILURE']['falsifying']},analyst).entity_id
   alt=ev.execute({'operation':'assess','request_id':'B20RU-alternative-assessment','hypothesis_id':alternative,'expected_hash':r.get_node(alternative).content_hash,'evidence_ids':[],'as_of':clock()},analyst).assessment
   value['basis'].append({'hypothesis_id':alt.hypothesis_id,'assessment_id':alt.id,'reason':'Retain assessed scope uncertainty without asserting new facts','addressed':False})
   # Explicit new synthetic pipe survey in this fresh isolated graph only.
   # B19 baseline/source records and all previously retained graphs stay intact.
   original_pipe=r.get_node('PIPE-100','WaterPipe')
   r.create_node('WaterPipe',{**original_pipe.properties,'id':'PIPE-B20R-UTILITY-R-2'})
   source_id='EV-B20R-UTILITY-R-TOPOLOGY'
   r.create_node('Evidence',{'id':source_id,'schema_version':3,'municipality_id':'demo-city','created_at':clock(),'updated_at':clock(),'evidence_type':'SYNTHETIC_TOPOLOGY_SURVEY','summary':'Explicit authorized synthetic survey: second test pipe underlies ROAD-100; no leak or intervention is inferred','reliability':'VERIFIED','recorded_at':clock(),'observed_at':clock(),'source_kind':'SYNTHETIC','source_record_id':'B20R-UTILITY-R:second-pipe-survey','basis':'OBSERVED'})
   edge_id='REL-B20R-UTILITY-R-UNDERLIES'
   r.create_relationship('UNDERLIES','PIPE-B20R-UTILITY-R-2','ROAD-100',{'id':edge_id,'municipality_id':'demo-city','created_at':clock(),'valid_from':clock(),'source_evidence_id':source_id,'association_status':'VERIFIED'})
   ambiguous=copy.deepcopy(value);extra_isolate=copy.deepcopy(value['tasks'][0]);extra_isolate.update(id='isolate2',target_ids=['PIPE-B20R-UTILITY-R-2'])
   extra_repair=copy.deepcopy(value['tasks'][1]);extra_repair.update(id='repair2',target_ids=['PIPE-B20R-UTILITY-R-2'],depends_on=['isolate2']);extra_repair['remediation']['conditions'][-1]['depends_on_task_id']='isolate2'
   # Road is checked first: this schema-valid proposal omits its second relevant
   # predecessor. Rejection precedes persistence and any later task qualification.
   ambiguous['tasks']=[copy.deepcopy(value['tasks'][2]),*copy.deepcopy(value['tasks'][:2]),extra_isolate,extra_repair]
   ambiguous_draft=PlanDraft.model_validate(ambiguous)
   with pytest.raises(PlanningBlocked,match='^UTILITY_MULTIPLE_REPAIR_PREDECESSORS$'):
    validate_remediation(ambiguous_draft.tasks[0],ambiguous_draft,Reader(r,clock()),assessments,PlanningBlocked)
   rejected=await c.post('/api/v1/plans',json={'draft':ambiguous},headers=headers(shared,'OP-ANALYST','B20R-UTILITY-R-ambiguous-plan'))
   assert rejected.status_code==409 and rejected.json()['error']['code']=='DEPENDENCY_BLOCKED',rejected.json()
   assert r._read('MATCH (p:ResolutionPlan) RETURN count(p)')==[[0]] and r._read('MATCH (d:CivicPlanDraft) RETURN count(d)')==[[0]] and r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[0]]
   ambiguity_proof={'draft':ambiguous_draft.normalized(),'schema_valid':True,'blocker_code':'UTILITY_MULTIPLE_REPAIR_PREDECESSORS','http':rejected.json(),'source_evidence_id':source_id,'topology_relationship_id':edge_id,'plans_after_rejection':0,'drafts_after_rejection':0,'work_orders_after_rejection':0}
   checked=PlanDraft.model_validate(value)
   for task in checked.tasks:
    validate_remediation(task,checked,Reader(r,clock()),assessments,PlanningBlocked)
    await s.ops.planning.resolve(task,Reader(r,clock()),clock())
   made=await c.post('/api/v1/plans',json={'draft':value},headers=headers(shared,'OP-ANALYST','B20RU-plan'));assert made.status_code==200,made.json();pid=made.json()['data']['plan_id'];saved=s.ops.planning.store.get(pid);b=binding(saved)
   pending=await c.post('/api/v1/plans/'+pid+'/submit-approval',json={k:v for k,v in b.items() if k!='plan_id'},headers=headers(shared,'OP-ANALYST','B20RU-submit'));assert pending.status_code==200,pending.json();pending=pending.json()['data']
   decision=await c.post('/api/v1/approvals/'+pending['id']+'/decision',json={**b,'expected_hash':pending['expected_hash'],'decision':'APPROVED','reason':'Independent exact synthetic utility and justified road DAG approval'},headers=headers(shared,'OP-APPROVER','B20RU-approve'));assert decision.status_code==200,decision.json()
   runner=HTTPRun(r,clock,s.ops,shared.tokens,c,shared);runner.b=b;runner.saved=saved;runner.approval=pending['id'];indices={t['id']:i for i,t in enumerate(saved['draft']['tasks'])};blocked=[]
   async def premature(which,key):
    a=b['assignments'][indices[which]];res=await c.post('/api/v1/work-orders',json={**b,'approval_id':pending['id'],'task_id':a['task_id']},headers=headers(shared,'OP-APPROVER',key));assert res.status_code==409,res.json();blocked.append({'task':which,'error':res.json()['error']})
   await premature('repair','B20RU-before-isolation');await premature('road','B20RU-before-repair')
   isolation_order=await runner.select(indices['isolate'])
   _,bad=await runner.report('COMPLETION',lambda at:[runner.observation('ACTION_COMPLETED',at)])
   with pytest.raises(PreconditionFailed,match='REVIEWED_ISOLATION_REQUIRED'):
    await s.ops.execute({'operation':'progress','request_id':'B20RU-status-alone','work_order_id':runner.w['id'],'expected_hash':runner.hash(),'action':'COMPLETE','reason':'Crew status alone must not prove isolation','evidence_ids':[bad['entity_id']]},token=shared.tokens['OP-WATER-LEAD'])
   _,isorep=await runner.report('COMPLETION',lambda at:[runner.observation(code,at) for code in ['ACTION_COMPLETED','UTILITY_ISOLATION_CONFIRMED']]);_,isocomp=await runner.progress('COMPLETE',[isorep['entity_id']]);assert isocomp['status']=='COMPLETED'
   repair_order=await runner.select(indices['repair']);_,repairrep,_,repaircomp=await runner.complete();assert repaircomp['latest_assessment_status']=='MONITORING'
   await premature('road','B20RU-before-independent-verification')
   clock.advance();start=clock();_,follow=await runner.report('FOLLOWUP',lambda at:[runner.observation(code,at) for code in ['POST_REPAIR_PRESSURE_NORMAL','POST_REPAIR_LEAK_ABSENT']]);clock.advance()
   q={'operation':'evaluate','request_id':runner.key(),'work_order_id':runner.w['id'],'expected_hash':runner.hash(),'evidence_ids':[follow['entity_id']],'window_start':start,'window_end':clock()}
   verified=await runner.call(q,'OP-ANALYST');assert verified['assessment_status']=='UTILITY_VERIFIED' and not verified['case_closed'];assert await runner.call(q,'OP-ANALYST')==verified
   # Record actual CLI service read, not a fabricated CLI response.
   from cli.private import write_private,scope
   session=path.parent/'utility-session.json';write_private(session,{'version':1,'scope':scope(p,shared.auth.path),'token':shared.tokens['OP-WATER-LEAD'],'operator_id':'OP-WATER-LEAD','login_key':'B20RU-session'})
   command=[sys.executable,'-m','cli','--profile',str(path),'--auth-store',str(shared.auth.path),'--memory-profile',str(path.parent/'memory.json'),'--session',str(session),'--at',clock(),'work','get','--id',repair_order['id']]
   cli=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'PYTHONPATH':str(Path('backend/test_guards').resolve())+os.pathsep+str(Path('backend').resolve())},timeout=60);assert cli.returncode==0,cli.stdout;cliout=json.loads(cli.stdout);assert cliout['data']['latest_assessment_status']=='UTILITY_VERIFIED'
   road_order=await runner.select(indices['road']);assert road_order['department_id']=='DEPT-ROAD'
   _,roadreport,_,roadcompletion=await runner.complete();assert roadcompletion['status']=='COMPLETED' and not roadcompletion['resolution_verified']
   # Actual new utility follow-up report commit; injected readback uncertainty.
   runner.assignment_index=indices['repair'];runner.lead='OP-WATER-LEAD';runner.w=repair_order
   real_get=Storage.get;real_execute=Execution.execute;invocations=[];captured={}
   async def counted(self,*a,**kw):invocations.append(a[0]);return await real_execute(self,*a,**kw)
   def fault(self,kind,id):
    out=real_get(self,kind,id)
    if kind=='operation' and out and out.get('command',{}).get('command',{}).get('record_id')=='uncertain-followup':raise ValueError('PRIVATE_INJECTED_UTILITY_ACK_READBACK')
    return out
   # Prepare normal report request/transitions using existing helper, intercept only
   # final report's response to preserve UNKNOWN without trying another mutation.
   call=runner.call
   async def uncertain_call(q,operator=None,**kw):
    if q['operation']=='inspect' and q['command']['operation']=='report_inspection':
     q['command']['record_id']='uncertain-followup';monkeypatch.setattr(Storage,'get',fault);monkeypatch.setattr(Execution,'execute',counted)
     v={k:v for k,v in q.items() if k not in {'operation','request_id','work_order_id'}};v['command']={k:v for k,v in v['command'].items() if k!='request_id'};h=headers(shared,'OP-WATER-LEAD',q['request_id'],reviewer='OP-ANALYST');route='/api/v1/work-orders/'+repair_order['id']+'/inspections'
     res=await c.post(route,json=v,headers=h);assert res.status_code==409,res.json();error=res.json()['error'];assert error['code']=='RECOVERY_REQUIRED' and error['details']['commitment']=='UNKNOWN'
     monkeypatch.setattr(Storage,'get',real_get)
     replay=await c.post(route,json=v,headers=h);assert replay.status_code==409 and replay.json()['error']['details']==error['details'];assert len(invocations)==1
     op=next(x for x in invocations);request=op['request_id'];persisted=s.ops.store.get('operation',__import__('app.services.operations.service',fromlist=['stable']).stable('OP',request));rid=persisted['receipt']['entity_id'];assert r._read('MATCH (e:Evidence {id:$id}) RETURN count(e)',{'id':rid})==[[1]];assert s.delivery.store.get('api_request',error['details']['request_id'])['status']=='DISPATCHING'
     captured.update(error=error,evidence_id=rid,domain_request_id=request,journal_state='COMMITTED',one_effect_no_redispatch=True);return {'entity_id':rid}
    return await call(q,operator,**kw)
   runner.call=uncertain_call
   await runner.report('FOLLOWUP',lambda at:[runner.observation(code,at) for code in ['POST_REPAIR_PRESSURE_NORMAL','POST_REPAIR_LEAK_ABSENT']])
   assert all(r.get_relationship(id).content_hash==hash for id,hash in frozen.items());assert all(r.get_node(id).content_hash==hash for id,hash in original_reports.items());assert s.ops.planning.store.get(pid)==saved
   assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[3]];assert r.get_node(pid).properties['status']=='MONITORING' and r.get_node(case['incident_id']).properties['status']!='ENDED'
   Path('docs/evidence/B20R-UTILITY-R-primary-proof.json').write_text(json.dumps({'mode':'REAL_FALKORDB_GRAPHRAG_HTTP_CLI_EXPLICIT_SYNTHETIC_OBSERVATIONS_NO_MODEL','ambiguous_plan_rejection':ambiguity_proof,'source_graph':p.graph,'profile_reference':receipt['profile_reference'],'case':case,'released_ids':released,'additional_survey_ids':reports,'draft':saved['draft'],'plan_id':pid,'binding':b,'approval':decision.json()['data'],'premature_denials':blocked,'isolation_order':isolation_order,'isolation_report_id':isorep['entity_id'],'repair_order':repair_order,'repair_completion':repaircomp,'utility_verification':verified,'utility_followup_id':follow['entity_id'],'road_order':road_order,'road_completion':roadcompletion,'road_completion_report_id':roadreport['entity_id'],'road_status':r.get_node(road_order['id']).properties['status'],'plan_status':r.get_node(pid).properties['status'],'recovery':captured,'cli_verification':cliout['data'],'http_calls':runner.calls,'original_sources_retained':True,'provider_requests':0},indent=2)+'\n')
