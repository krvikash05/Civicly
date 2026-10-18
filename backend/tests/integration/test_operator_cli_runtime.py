"""One real water case across actual CLI processes; authored payloads, no LLM."""
import asyncio,copy,hashlib,json,os,secrets,subprocess,sys
from pathlib import Path
from uuid import uuid4
import pytest
from app.active import active_scope,load
from app.services.operations.auth import Auth,OPERATORS
from app.services.evidence.reader import Reader
from tests.b14_fixtures import prepare
from tests.b13_fixtures import binding
from tests.integration.test_memory_graphrag import memory
pytestmark=pytest.mark.integration

def test_operator_subprocess_water_journey_reset_and_recovery(db,tmp_path,memory):
 p,r,clock,path,oldinv,draft,planning,_,_,_=prepare(db,tmp_path,memory,'WATERLOGGING')
 passwords={id:secrets.token_urlsafe(24) for id in OPERATORS};auth=Auth.provision(tmp_path/'operator-auth.sqlite3',passwords)
 from app.memory.runtime import Profile
 user='b18_memory_'+uuid4().hex;pw=secrets.token_urlsafe(48)
 db.connection.execute_command('ACL','SETUSER',user,'reset','on','#'+hashlib.sha256(pw.encode()).hexdigest(),'~'+memory.repo.graph.name,'~'+memory.config.graph_name,'-@all','+ping','+info','+client|setinfo','+graph.ro_query')
 mp=Profile(docs_graph=memory.config.graph_name,canonical_graph=memory.repo.graph.name,source_graphs=[p.graph],reader_user=user,reader_password=pw)
 mpath=tmp_path/'memory.json';mp.json_private(mpath)
 from app.events.service import Delivery
 with active_scope(p):delivery=Delivery(r,clock);delivery.activate(operator='B18-test',reason='Explicit fresh isolated workflow cutover',authorize=True)
 env={**os.environ,'PYTHONPATH':str(Path('backend/test_guards').resolve())+os.pathsep+str(Path('backend').resolve())};counter=0;calls=[];sessions={id:tmp_path/(id+'.session.json') for id in OPERATORS}
 def call(group,action=None,*,who='OP-ANALYST',body=None,id=None,query=None,key=None,reviewer=None,expect=0,fault=False,extra=None):
  nonlocal counter
  counter+=1;argv=['--profile',str(path),'--auth-store',str(auth.path),'--memory-profile',str(mpath),'--session',str(sessions[who]),'--at',clock(),group]
  if action:argv.append(action)
  if id:argv+=['--id',id]
  if key:argv+=['--key',key]
  if reviewer:argv+=['--reviewer-session',str(sessions[reviewer])]
  for field,value in [('payload',body),('query',query)]:
   if value is not None:
    f=tmp_path/(str(counter)+'-'+field+'.json');f.write_text(json.dumps(value));argv+=['--'+field,str(f)]
  argv+=extra or []
  command=[sys.executable,'-m','tests.b18_fault' if fault else 'cli',*argv]
  result=subprocess.run(command,env=env,capture_output=True,text=True,timeout=60)
  # No secret value may escape even on a failing child; never print raw stderr.
  assert not any(secret in result.stdout+result.stderr for secret in [pw,*passwords.values()])
  value=json.loads(result.stdout)
  calls.append({'command':group+(' '+action if action else ''),'exit':result.returncode,'status':value['status'],'id':value.get('data',{}).get('id') if isinstance(value.get('data'),dict) else None})
  assert result.returncode==expect,{'command':group+' '+str(action),'exit':result.returncode,'sanitized_output':value}
  if expect:return value
  return value['data']
 for id in ['OP-ANALYST','OP-APPROVER','OP-DRAIN-LEAD','OP-ROAD-LEAD','OP-ADMIN']:
  credentials=tmp_path/(id+'.credentials.json');credentials.write_text(json.dumps({'operator_id':id,'demo_password':passwords[id]}));credentials.chmod(0o600)
  call('auth','login',who=id,key='login-'+id,extra=['--credentials',str(credentials)])
 assert call('auth','whoami')['role']=='ANALYST'
 # Existing accepted physical evidence/citations are fixture setup. All following
 # case decisions and lifecycle commands execute through independent CLI children.
 with active_scope(p):
  targets=delivery.sources.repo._read('MATCH (i:Investigation {id:$id})-[:INVESTIGATES]->(n) RETURN n.id,labels(n)',{'id':oldinv})
 incident=next(row[0] for row in targets if 'Incident' in row[1]);cluster=next(row[0] for row in targets if 'ProblemCluster' in row[1])
 opened=call('investigate','open',body={'incident_ids':[incident],'cluster_id':cluster},key='open')
 assert call('investigate','open',body={'incident_ids':[incident],'cluster_id':cluster},key='open')==opened
 inv=opened['id'];assert not opened['current_plan_id']
 resume=call('investigate','resume',id=inv,body={'reason':'Explicit offline operator wake'},key='resume');assert resume['accepted'] and resume['status']=='PENDING'
 advanced=call('advance','run',key='advance-1',extra=['--batches','1']);assert advanced['batches'] and advanced['batches'][0]['status']=='DONE'
 assert call('advance','run',key='advance-1',extra=['--batches','1'])==advanced
 trace=call('investigate','trace',id=inv)
 assert any(v['kind']=='TOOL' and v['validated_output'] for v in trace['items'])
 assert all(v['execution_mode']=='B15_DETERMINISTIC_DEVELOPMENT_NO_PROVIDER' for v in trace['items'])
 assert trace['phase']=='Coordinator' and not trace['recovery_required']
 # Explicit authored hypotheses reuse actual prior incident evidence, never hidden
 # truth. New proposal and assessment identities belong to this CLI-opened case.
 fresh=copy.deepcopy(draft.model_dump(mode='json'));fresh['investigation_id']=inv
 for i,basis in enumerate(fresh['basis']):
  with active_scope(p):_,definition=Reader(r,clock()).definition(basis['hypothesis_id'])
  proposal=definition.model_dump(mode='json')
  for field in ['operation','request_id','investigation_id']:proposal.pop(field)
  made=call('hypothesis','propose',id=inv,body=proposal,key='hyp-'+str(i));hid=made['status']
  h=call('hypothesis','get',id=hid);clock.advance()
  call('hypothesis','assess',id=hid,body={'expected_hash':h['expected_hash'],'evidence_ids':fresh['evidence_ids'],'as_of':clock()},key='assessment-'+str(i))
  h=call('hypothesis','get',id=hid);basis.update(hypothesis_id=hid,assessment_id=h['current_assessment_id'])
 fresh['tasks'][0]['assessment_ids']=[b['assessment_id'] for b in fresh['basis']]
 # Standalone inspection through CLI is correctly UNREVIEWED, no authority spoof.
 inspection=call('inspect','request',body={'investigation_id':inv,'asset_ids':['D1'],'department_id':'DEPT-DRAIN','inspection_type':'B18_CONTEXT'},key='context-request')
 iid=inspection['id']
 for status in ['REQUESTED','SCHEDULED','IN_PROGRESS']:
  clock.advance();current=call('inspect','get',id=iid)
  body={'expected_hash':current['expected_hash'],'status':status}
  if status=='SCHEDULED':body['scheduled_at']=clock()
  call('inspect','transition',id=iid,body=body,key='context-'+status,who='OP-DRAIN-LEAD')
 clock.advance();current=call('inspect','get',id=iid)
 unreviewed=call('inspect','report',id=iid,who='OP-DRAIN-LEAD',key='context-report',body={'expected_hash':current['expected_hash'],'source_id':'B18-context','record_id':'context','observations':[{'asset_id':'D1','code':'OPERATOR_CONTEXT','statement':'Authored synthetic context; cause is not asserted','method':'DIRECT_SYNTHETIC_FIELD_TEST','observed_at':clock()}]})
 assert not unreviewed['reviewed'] and unreviewed['findings']
 assert call('evidence','get',id=unreviewed['id'])['findings']==unreviewed['findings']
 plan=call('plan','create',body={'draft':fresh},key='draft');assert plan['status']=='DRAFT' and not plan['draft_receipt']['approved']
 with active_scope(p):saved=planning.store.get(plan['plan_id']);b=binding(saved)
 submit={k:v for k,v in b.items() if k!='plan_id'}
 approval=call('plan','submit',id=b['plan_id'],body=submit,key='submit')
 decision={**b,'expected_hash':approval['expected_hash'],'decision':'APPROVED','reason':'Exact authenticated synthetic plan review'}
 decided=call('approve','decide',id=approval['id'],body=decision,key='approve',who='OP-APPROVER');assert decided['status']=='APPROVED'
 orderbody={**b,'approval_id':approval['id'],'task_id':b['assignments'][0]['task_id']}
 denied=call('work','create',body=orderbody,key='denied-order',who='OP-ROAD-LEAD',expect=3);assert denied['error']['code']=='PERMISSION_DENIED'
 work=call('work','create',body=orderbody,key='order',who='OP-APPROVER')
 assert call('work','create',body=orderbody,key='order',who='OP-APPROVER')==work
 wid=work['id']
 work=call('work','status',id=wid,body={'expected_hash':work['expected_hash'],'new_status':'ASSIGNED','reason':'Explicit synthetic assignment'},key='assign',who='OP-DRAIN-LEAD')
 work=call('work','progress',id=wid,body={'expected_hash':work['expected_hash'],'action':'START','reason':'Explicit synthetic start'},key='start',who='OP-DRAIN-LEAD')
 def work_report(purpose,codes):
  nonlocal counter
  request=call('work','inspect',id=wid,who='OP-DRAIN-LEAD',key='wi-'+str(counter),body={'expected_hash':work['expected_hash'],'purpose':purpose,'command':{'operation':'request_inspection','investigation_id':inv,'asset_ids':['D1'],'department_id':'DEPT-DRAIN','inspection_type':fresh['tasks'][0]['action_type'] if purpose=='COMPLETION' else 'B14_FOLLOWUP'}})
  iid=request['status']
  for state in ['REQUESTED','SCHEDULED','IN_PROGRESS']:
   clock.advance();view=call('inspect','get',id=iid)
   c={'operation':'transition_inspection','inspection_id':iid,'expected_hash':view['expected_hash'],'status':state}
   if state=='SCHEDULED':c['scheduled_at']=clock()
   call('work','inspect',id=wid,who='OP-DRAIN-LEAD',key='wi-'+str(counter),body={'expected_hash':work['expected_hash'],'purpose':purpose,'command':c})
  clock.advance();view=call('inspect','get',id=iid)
  observations=[]
  for code in codes:
   clock.advance();observations.append({'asset_id':'D1','code':code,'statement':'Authored synthetic '+code,'method':'DIRECT_SYNTHETIC_FIELD_TEST','observed_at':clock(),'value':0.0 if code=='FOLLOWUP_WATERLOGGING' else None,'unit':'boolean' if code=='FOLLOWUP_WATERLOGGING' else None})
  return call('work','inspect',id=wid,who='OP-DRAIN-LEAD',reviewer='OP-ANALYST',key='wi-'+str(counter),body={'expected_hash':work['expected_hash'],'purpose':purpose,'review_reason':'Independent authenticated review of synthetic measurements','command':{'operation':'report_inspection','inspection_id':iid,'expected_hash':view['expected_hash'],'source_id':'B18-field','record_id':'B18-'+str(counter),'observations':observations}})['status']
 completed_report=work_report('COMPLETION',['ACTION_COMPLETED'])
 work=call('work','progress',id=wid,who='OP-DRAIN-LEAD',key='complete',body={'expected_hash':work['expected_hash'],'action':'COMPLETE','reason':'Attributed synthetic completion','evidence_ids':[completed_report]})
 assert work['status']=='COMPLETED' and not work['resolution_verified']
 clock.advance();start=clock();clock.advance()
 monitoring=call('work','evaluate',id=wid,key='no-opportunity',body={'expected_hash':work['expected_hash'],'evidence_ids':[],'window_start':start,'window_end':clock()});assert not monitoring['case_closed']
 followup=work_report('FOLLOWUP',['COMPARABLE_FOLLOWUP_RAINFALL','FOLLOWUP_WATERLOGGING']);clock.advance()
 outcome=call('work','evaluate',id=wid,key='verify',body={'expected_hash':work['expected_hash'],'evidence_ids':[followup],'window_start':start,'window_end':clock()})
 assert outcome['assessment_status']=='RESOLUTION_VERIFIED' and outcome['case_closed']
 work=call('work','get',id=wid);assert work['resolution_verified']
 graph=call('graph','explain',id=inv,query={'depth':4,'include_candidates':True});assert graph['nodes'] and graph['edges'] and graph['analysis_paths']
 source=call('source','document',id=fresh['tasks'][0]['procedure_citation']['canonical_document_id']);assert source['citations'] and source['assertion_status']=='PROPOSED'
 # Actual committed B09inspection then injected readback ValueError inside CLIchild.
 body={'investigation_id':inv,'asset_ids':['D1'],'department_id':'DEPT-DRAIN','inspection_type':'B18_FAULT_CONTEXT'}
 with active_scope(p):before=r._read('MATCH (n:Inspection) RETURN count(n)')[0][0]
 failure=call('inspect','request',body=body,key='uncertain',fault=True,expect=6)
 assert failure['error']['code']=='RECOVERY_REQUIRED' and failure['error']['details']['commitment']=='UNKNOWN'
 again=call('inspect','request',body=body,key='uncertain',expect=6);assert again['error']['details']['correlation_id']==failure['error']['details']['correlation_id']
 with active_scope(p):
  assert r._read('MATCH (n:Inspection) RETURN count(n)')[0][0]==before+1
  assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[1]]
  assert delivery.store.get('api_request',failure['error']['details']['correlation_id'])['status']=='DISPATCHING'
  from app.services.evidence.models import Journal
  journal=next(Journal.model_validate_json(n[0]) for n in r._read('MATCH (e:Evidence {evidence_type:$kind}) RETURN e.summary',{'kind':'B09_OPERATION'}) if json.loads(n[0]).get('command',{}).get('request_id')==failure['error']['details']['correlation_id'])
  assert journal.state=='COMMITTED'
 # Two fresh starters have equal validated content and disjoint graph/profile IDs.
 first=call('reset',who='OP-ADMIN',key='reset-a',extra=['--output-dir',str(tmp_path/'reset-a')])
 replay=call('reset',who='OP-ADMIN',key='reset-a',extra=['--output-dir',str(tmp_path/'reset-a')]);assert replay==first
 call('reset',who='OP-ADMIN',key='reset-a',extra=['--output-dir',str(tmp_path/'conflicting-destination')],expect=4)
 second=call('reset',who='OP-ADMIN',key='reset-b',extra=['--output-dir',str(tmp_path/'reset-b')])
 assert first['fixture_hash']==second['fixture_hash'] and first['source_graph']!=second['source_graph']!=p.graph
 call('reset',who='OP-ADMIN',key='reset-other',extra=['--output-dir',str(tmp_path/'reset-a')],expect=4)
 for directory,receipt in [(tmp_path/'reset-a',first),(tmp_path/'reset-b',second)]:
  new=load(directory/'profile.json')
  with active_scope(new):
   from app.graph.repository import GraphRepository
   rr=GraphRepository(db,new.graph);assert rr._read('MATCH (n:CivicEntity) WHERE NOT n:Evidence RETURN count(n)')==[[3]]
   assert rr._read('MATCH ()-[e:MAINTAINED_BY]->() RETURN e.association_status')==[['CANDIDATE']]
 call('test')
 discovered=call('advance','discover',key='discover');assert not discovered['execution_completed']
 proof={'mode':'REAL_SUCCESSIVE_CLI_PROCESSES_FALKORDB_MCP_SAVER_AUTHORED_OFFLINE_INPUTS','source_graph':p.graph,'investigation_id':inv,'prior_source_investigation_id':oldinv,'incident_id':incident,'plan_id':b['plan_id'],'approval_id':approval['id'],'work_order_id':wid,'outcome':outcome,'advance':advanced,'trace':trace,'graph':graph,'source_citation':source['citations'][0],'uncertain':failure,'uncertain_committed_journal_id':journal.receipt.journal_id,'uncertain_replay_inspection_count_change':1,'work_order_count':1,'resets':[first,second],'reset_replay_unchanged':True,'subprocess_count':counter,'calls':calls,'provider_calls':0}
 Path('docs/evidence/B18-cli-journey.json').write_text(json.dumps(proof,indent=2)+'\n')
