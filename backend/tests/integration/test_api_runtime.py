"""B16 actual ASGI→accepted services→DB, worker/MCP/Saver and local network."""
import asyncio,json,secrets,copy,os,sys,subprocess,socket,time
from pathlib import Path
import httpx,pytest
from fastapi.testclient import TestClient
from app.active import active_scope
from app.api.application import create_app
from app.events.service import Delivery
from app.services.http.service import Services
from app.services.operations.auth import Auth,OPERATORS
from app.services.operations.service import Operations
from app.services.operations.models import OpsRecovery
from app.graph.repository import OutcomeUnknown
from tests.b14_fixtures import prepare,Run
from tests.b13_fixtures import binding
from tests.b08_fixtures import payload
from tests.integration.test_memory_graphrag import memory
pytestmark=pytest.mark.integration

def save(name,value):Path('docs/evidence/B16-'+name+'.json').write_text(json.dumps(value,indent=2)+'\n')

def test_http_workflow_rbac_idempotency_worker_and_network(db,tmp_path,memory,monkeypatch):
 p,r,clock,path,inv,draft,planning,_,_,_=prepare(db,tmp_path,memory,'WATERLOGGING')
 passwords={id:secrets.token_urlsafe(24) for id in OPERATORS};auth=Auth.provision(tmp_path/'http-auth.sqlite3',passwords)
 ops=Operations(planning,auth,clock=clock)
 with active_scope(p):
  delivery=Delivery(r,clock);delivery.activate(operator='B16-proof',reason='Only this exact fresh profile',authorize=True)
  services=Services(p,path,r,auth,ops,delivery,clock,memory=memory)
 app=create_app(services);c=TestClient(app,raise_server_exceptions=False);tokens={}
 for id in OPERATORS:
  response=c.post('/api/v1/auth/demo-login',json={'operator_id':id,'demo_password':passwords[id]});assert response.status_code==200,response.text
  tokens[id]=response.json()['data']['access_token']
 def call(method,url,body=None,who='OP-ANALYST',key=None,reviewer=None,expect=200):
  headers={'Authorization':'Bearer '+tokens[who]}
  if key:headers['Idempotency-Key']=key
  if reviewer:headers['X-Reviewer-Authorization']='Bearer '+tokens[reviewer]
  res=c.request(method,'/api/v1'+url,json=body,headers=headers)
  assert res.status_code==expect,(url,res.status_code,res.text)
  if expect!=200:return res.json()
  assert res.headers['Cache-Control']=='no-store' and res.json()['schema_version']==1
  return res.json()['data']
 # Role matrix exercises protected read and write paths before service dispatch.
 for who in ['OP-ADMIN','OP-DRAIN-LEAD','OP-APPROVER']:
  call('POST','/investigations',{'incident_ids':['missing'],'cluster_id':'missing'},who,key='wrong-role-'+who,expect=403)
 call('GET','/approvals',who='OP-DRAIN-LEAD',expect=403)
 # Public/error paths use the same closed normative envelopes.
 assert c.get('/api/v1/health/live').status_code==200
 assert c.get('/api/v1/complaints',headers={'Authorization':'Bearer invalid'}).status_code==401
 call('GET','/incidents/ABSENT',expect=404)
 # Actual B08 intake and explicit B09 case creation, no model inside HTTP.
 q=payload('WATERLOGGING',ref='B16-http-intake',reported_at=clock(),occurred_at=clock())
 complaint=call('POST','/complaints',{'complaint':q},key='complaint-1')
 assert call('POST','/complaints',{'complaint':q},key='complaint-1')==complaint
 call('POST','/complaints',{'complaint':{**q,'description':'Conflicting report'}},key='complaint-1',expect=409)
 incident=call('GET','/incidents/'+complaint['incident_id']);cluster=incident['cluster_id']
 case=call('POST','/investigations',{'incident_ids':[incident['id']],'cluster_id':cluster},key='open-1')
 assert case['id'] and case['runtime_status']=='DETERMINISTIC_DEVELOPMENT_ONLY_NO_LIVE_AUTHORIZATION'
 with active_scope(p):
  assert r.get_node(case['id'],'Investigation').properties.get('thread_id') is None
  pending=[v for v in delivery.store.rows('delivery') if v['case_id']==case['id']]
  assert len(pending)==1 and pending[0]['status']=='PENDING'
 # Worker executes after HTTP response, genuine broker/Saver, authored selections.
 from app.events.worker import Worker
 from app.events.runtime import Runtime
 from app.agents.checkpoints import saver
 from app.agents.models import InvestigationState
 from tests.b10_fixtures import ScriptedModel,choose
 models=[]
 def factory():
  m=ScriptedModel([choose('READ',{'template':'node','id':incident['id']},'official::query_graph_readonly'),choose()]);models.append(m);return m
 runtime=Runtime(p,path,r,clock,model_factory=factory)
 with active_scope(p):
  claim=asyncio.run(Worker(delivery,runtime,'B16-worker').once(discover=False));assert claim and delivery.store.get('delivery',pending[0]['id'])['status']=='DONE'
  first=saver(p).get_tuple({'configurable':{'thread_id':runtime.thread(case['id'])}});assert first
 resume=call('POST','/investigations/'+case['id']+'/resume',{'reason':'Explicit authenticated fresh context'},key='resume-1')
 assert call('POST','/investigations/'+case['id']+'/resume',{'reason':'Explicit authenticated fresh context'},key='resume-1')==resume
 call('POST','/investigations/'+case['id']+'/resume',{'reason':'Changed same request'},key='resume-1',expect=409)
 with active_scope(p):
  assert delivery.store.get('delivery',resume['event_id'])['status']=='PENDING'
  assert saver(p).get_tuple(first.config).checkpoint==first.checkpoint
  asyncio.run(Worker(delivery,runtime,'B16-resume-worker').once(discover=False))
  second=saver(p).get_tuple({'configurable':{'thread_id':runtime.thread(case['id'])}});state=InvestigationState.model_validate(second.checkpoint['channel_values']['data'])
  assert state.wakes==1 and state.tool_calls==2 and len(models)==2
  assert saver(p).get_tuple(first.config).checkpoint==first.checkpoint
 # The essential standalone B09 request/transition/report routes also use accepted
 # services; no JSON reviewer/actor substitute is allowed.
 generic=call('POST','/inspections',{'investigation_id':case['id'],'asset_ids':['D1'],'department_id':'DEPT-DRAIN','inspection_type':'B16-SYNTHETIC-READINESS'},key='generic-inspection')
 call('POST','/inspections/'+generic['id']+'/transitions',{'expected_hash':generic['expected_hash'],'status':'REQUESTED'},key='generic-request')
 for status in ['SCHEDULED','IN_PROGRESS']:
  clock.advance();current=call('GET','/inspections/'+generic['id'])
  v={'expected_hash':current['expected_hash'],'status':status}
  if status=='SCHEDULED':v['scheduled_at']=clock()
  call('POST','/inspections/'+generic['id']+'/transitions',v,'OP-DRAIN-LEAD','generic-'+status)
 clock.advance();current=call('GET','/inspections/'+generic['id'])
 authored={'expected_hash':current['expected_hash'],'source_id':'B16-standalone','record_id':'B16-standalone','observations':[{'asset_id':'D1','code':'DRAIN_CLEAR','statement':'Authored synthetic context','method':'DIRECT_SYNTHETIC_FIELD_TEST','observed_at':clock()}]}
 call('POST','/inspections/'+generic['id']+'/observations',{**authored,'review':{'reviewer_id':'OP-ANALYST','role':'ANALYST','reviewed':True,'reason':'Forged'}},'OP-DRAIN-LEAD','generic-forged',expect=422)
 generic_report=call('POST','/inspections/'+generic['id']+'/observations',authored,'OP-DRAIN-LEAD','generic-report')
 assert not generic_report['reviewed']
 h=call('POST','/investigations/'+case['id']+'/hypotheses',{'incident_ids':[incident['id']],'asset_ids':['D1'],'cause_code':'DRAIN_BLOCKAGE','statement':'Authored alternative requiring evidence','mechanism':'Candidate obstruction, not verified cause','confirming_codes':['DRAIN_BLOCKED'],'falsifying_codes':['DRAIN_CLEAR']},key='proposal-1')
 hypothesis=call('GET','/hypotheses/'+h['status'])
 call('POST','/hypotheses/'+h['status']+'/assessments',{'expected_hash':hypothesis['expected_hash'],'evidence_ids':[],'as_of':clock()},key='assessment-1')
 assessed=call('GET','/hypotheses/'+h['status']);assert assessed['current_assessment_id'] and assessed['assessment_history'][-1]['current']
 assert 'graph' not in assessed and 'graph' not in assessed['assessment_history'][-1]
 # Typed B12 draft/approval/order use prepared supported sources, no duplicate rules.
 plan=call('POST','/plans',{'draft':draft.model_dump(mode='json')},key='draft-1')
 assert plan['status']=='DRAFT' and plan['draft_receipt']['approved'] is False
 with active_scope(p):saved=planning.store.get(plan['plan_id']);b=binding(saved)
 submit={k:v for k,v in b.items() if k!='plan_id'}
 approval=call('POST','/plans/'+b['plan_id']+'/submit-approval',submit,key='submit-1')
 decision={**b,'expected_hash':approval['expected_hash'],'decision':'APPROVED','reason':'Authenticated exact-plan review'}
 call('POST','/approvals/'+approval['id']+'/decision',{**decision,'expected_hash':'0'*64},'OP-APPROVER','bad-hash',expect=409)
 approval=call('POST','/approvals/'+approval['id']+'/decision',decision,'OP-APPROVER','decision-1')
 orderbody={**b,'approval_id':approval['id'],'task_id':b['assignments'][0]['task_id']}
 order=call('POST','/work-orders',orderbody,'OP-APPROVER','order-1')
 assert call('POST','/work-orders',orderbody,'OP-APPROVER','order-1')==order
 wid=order['id'];url='/work-orders/'+wid
 # Scoped reads filter before totals/pages; another department cannot see the order/plan.
 assert call('GET','/work-orders',who='OP-ROAD-LEAD')['items']==[]
 assert call('GET','/work-orders',who='OP-ROAD-LEAD')['total_count']==0
 call('GET',url,who='OP-ROAD-LEAD',expect=403)
 call('GET','/work-orders/ABSENT',who='OP-ROAD-LEAD',expect=403)
 call('GET','/plans/'+b['plan_id'],who='OP-ROAD-LEAD',expect=403)
 assert call('GET',url,who='OP-DRAIN-LEAD')['department_id']=='DEPT-DRAIN'
 call('POST',url+'/status',{'expected_hash':order['expected_hash'],'new_status':'ASSIGNED','reason':'Wrong department'},'OP-ROAD-LEAD','denied-status',expect=403)
 order=call('POST',url+'/status',{'expected_hash':order['expected_hash'],'new_status':'ASSIGNED','reason':'Assigned synthetic work'},'OP-DRAIN-LEAD','assign-1')
 order=call('POST',url+'/progress',{'expected_hash':order['expected_hash'],'action':'START','reason':'Synthetic start'},'OP-DRAIN-LEAD','start-1')
 # Actual independent report via header, nested request identity is server-owned.
 def inspection(command,key,reviewer=None,expect=200,reason=None):
  q={'expected_hash':order['expected_hash'],'purpose':'COMPLETION','command':command}
  if reason:q['review_reason']=reason
  return call('POST',url+'/inspections',q,'OP-DRAIN-LEAD',key,reviewer,expect)
 made=inspection({'operation':'request_inspection','investigation_id':inv,'asset_ids':draft.tasks[0].target_ids,'department_id':'DEPT-DRAIN','inspection_type':draft.tasks[0].action_type},'inspect-request')
 iid=made['status']
 for status in ['REQUESTED','SCHEDULED','IN_PROGRESS']:
  clock.advance();current=call('GET','/inspections/'+iid)
  command={'operation':'transition_inspection','inspection_id':iid,'expected_hash':current['expected_hash'],'status':status}
  if status=='SCHEDULED':command['scheduled_at']=clock()
  inspection(command,'inspection-'+status)
 clock.advance();current=call('GET','/inspections/'+iid)
 report={'operation':'report_inspection','inspection_id':iid,'expected_hash':current['expected_hash'],'source_id':'B16-authored-simulator','record_id':'B16-completion','source_kind':'SYNTHETIC','observations':[{'asset_id':'D1','code':'ACTION_COMPLETED','statement':'Authored synthetic completed action','method':'DIRECT_SYNTHETIC_FIELD_TEST','observed_at':clock(),'result':'OBSERVED'}]}
 inspection(report,'report-invalid-review','OP-APPROVER',403,'Invalid authority')
 inspection(report,'report-no-review',None,403,'Missing authority')
 valid=inspection(report,'report-1','OP-ANALYST',200,'Independent authenticated synthetic field review')
 evidence=call('GET','/evidence/'+valid['status']);assert evidence['reviewed'] and evidence['reliability']=='VERIFIED'
 call('GET','/evidence/'+valid['status'],who='OP-ROAD-LEAD',expect=403)
 order=call('POST',url+'/progress',{'expected_hash':order['expected_hash'],'action':'COMPLETE','reason':'Recorded synthetic completion','evidence_ids':[valid['status']]},'OP-DRAIN-LEAD','complete-1')
 assert order['status']=='COMPLETED' and order['resolution_verified'] is False
 clock.advance();start=clock();clock.advance()
 outcome=call('POST',url+'/outcomes',{'expected_hash':order['expected_hash'],'evidence_ids':[],'window_start':start,'window_end':clock()},'OP-ANALYST','outcome-1')
 assert outcome['assessment_status']=='MONITORING' and not outcome['case_closed']
 # Complete bounded read families; secrets/journal properties never exported.
 for u in ['/complaints','/incidents','/problem-clusters','/departments','/monitoring','/procedures','/documents/'+draft.tasks[0].procedure_citation.canonical_document_id,'/cases/'+incident['id']+'/memory','/investigations/'+inv+'/plans','/problem-clusters/'+cluster+'/outcomes']:
  call('GET',u)
 call('GET','/work-orders?limit=51',expect=422)
 call('GET','/work-orders?graph=other',expect=422)
 # Revoked/invalid session cannot replay even an already successful command.
 old=tokens['OP-ANALYST'];auth.logout(old)
 assert c.get('/api/v1/auth/me',headers={'Authorization':'Bearer '+old}).status_code==401
 tokens['OP-ANALYST']=auth.login('OP-ANALYST',passwords['OP-ANALYST'])
 # New evaluation window forces an actual new committed operation before ACK loss.
 clock.advance()
 original=ops.execute
 async def lose(command,**kw):
  result=await original(command,**kw)
  raise OpsRecovery(p.graph,command['request_id'],result['id'],operation=command['operation'])
 monkeypatch.setattr(ops,'execute',lose)
 failure=call('POST',url+'/outcomes',{'expected_hash':order['expected_hash'],'evidence_ids':[],'window_start':start,'window_end':clock()},'OP-ANALYST','uncertain-1',expect=409)
 assert failure['error']['code']=='RECOVERY_REQUIRED' and failure['error']['details']['commitment']=='UNKNOWN'
 monkeypatch.setattr(ops,'execute',original)
 again=call('POST',url+'/outcomes',{'expected_hash':order['expected_hash'],'evidence_ids':[],'window_start':start,'window_end':clock()},'OP-ANALYST','uncertain-1',expect=409)
 assert again['error']['code']=='RECOVERY_REQUIRED'
 with active_scope(p):
  from app.services.operations.service import stable
  persisted=ops.store.get('operation',stable('OP',failure['error']['details']['correlation_id']))
  assert persisted and persisted['request_id']==failure['error']['details']['correlation_id']
  assert persisted['receipt']['work_order_id']==wid
 assert failure['error']['details']['correlation_id'].startswith('HTTP-B16-')
 assert p.graph not in json.dumps(failure) and 'password' not in json.dumps(failure)
 with active_scope(p):assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[1]]
 save('http-runtime',{'mode':'ASGI_HTTP_REAL_SERVICES_FALKORDB_SCRIPTED_MCP_SAVER','graph':p.graph,'case_id':case['id'],'plan_id':plan['plan_id'],'approval_id':approval['id'],'work_order_id':wid,'recorded_outcome':outcome,'recovery':failure,'worker':{'first_checkpoint':first.config['configurable']['checkpoint_id'],'resume_checkpoint':second.config['configurable']['checkpoint_id'],'wakes':state.wakes,'tool_calls':state.tool_calls,'executions':state.executions,'old_checkpoint_unchanged':True,'outside_HTTP':True},'work_order_count':1,'department_list_filtered_before_count':True,'reviewer_header_not_body':True,'provider_calls':0})
 # Actual localhost server, same private configured data. Never publish tokens/log bodies.
 network(db,tmp_path,p,path,auth,memory,clock,passwords)

def network(db,tmp_path,p,path,auth,memory,clock,passwords):
 from app.memory.runtime import Profile
 from uuid import uuid4
 import hashlib
 user='b16_memory_'+uuid4().hex;password=secrets.token_urlsafe(48)
 db.connection.execute_command('ACL','SETUSER',user,'reset','on','#'+hashlib.sha256(password.encode()).hexdigest(),'~'+memory.repo.graph.name,'~'+memory.config.graph_name,'-@all','+ping','+info','+client|setinfo','+graph.ro_query')
 mp=Profile(docs_graph=memory.config.graph_name,canonical_graph=memory.repo.graph.name,source_graphs=[p.graph],reader_user=user,reader_password=password);mpath=tmp_path/'memory.json';mp.json_private(mpath)
 sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
 env={**os.environ,'PYTHONPATH':str(Path('backend/test_guards').resolve())+os.pathsep+str(Path('backend').resolve())}
 cmd=[sys.executable,'-m','app.api','--profile',str(path),'--auth-store',str(auth.path),'--memory-profile',str(mpath),'--at',clock(),'--port',str(port)]
 log=tmp_path/'server.log'
 with log.open('w') as f:
  proc=subprocess.Popen(cmd,env=env,stdout=f,stderr=f)
  try:
   with httpx.Client(base_url=f'http://127.0.0.1:{port}',timeout=15) as net:
    for _ in range(60):
     try:res=net.get('/api/v1/health/live');break
     except httpx.ConnectError:
      if proc.poll() is not None:raise AssertionError('B16 local server stopped; inspect private log without exporting secrets')
      time.sleep(.1)
    else:raise AssertionError('B16 local startup deadline')
    assert res.status_code==200
    ready=net.get('/api/v1/health/ready');assert ready.status_code==200,ready.text
    openapi=net.get('/openapi.json');assert openapi.status_code==200 and len(openapi.json()['paths'])==len({path for _,path,*_ in __import__('app.api.coverage',fromlist=['ROUTES']).ROUTES})
    assert net.get('/docs').status_code==200
    session=net.post('/api/v1/auth/demo-login',json={'operator_id':'OP-ADMIN','demo_password':passwords['OP-ADMIN']});assert session.status_code==200
    token=session.json()['data']['access_token'];me=net.get('/api/v1/auth/me',headers={'Authorization':'Bearer '+token});assert me.status_code==200
    assert token not in log.read_text() and not any(v in log.read_text() for v in passwords.values())
    save('network',{'mode':'ACTUAL_LOCALHOST_UVICORN_SERVER','health_status':res.status_code,'readiness':ready.json()['data'],'openapi_status':openapi.status_code,'path_count':len(openapi.json()['paths']),'docs_status':200,'authenticated_me_status':me.status_code,'identity':me.json()['data'],'token_logged':False,'provider_calls':0})
  finally:proc.terminate();proc.wait(timeout=15)
