"""B17 one shared real DB/service/MCP/Saver journey plus actual TCP SSE."""
import asyncio,hashlib,json,os,secrets,socket,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
import httpx,pytest
from fastapi.testclient import TestClient
from app.active import active_scope
from app.api.application import create_app
from app.events.service import Delivery
from app.services.http.service import Services
from tests.b14_fixtures import prepare,Run
from tests.integration.test_memory_graphrag import memory
pytestmark=pytest.mark.integration

def test_frontend_readiness_real_journey_and_tcp_sse(db,tmp_path,memory,monkeypatch):
 p,r,clock,path,inv,draft,planning,auth,tokens,ops=prepare(db,tmp_path,memory,'WATERLOGGING')
 with active_scope(p):
  delivery=Delivery(r,clock);delivery.activate(operator='B17-proof',reason='Fresh isolated source before actual activity and work',authorize=True)
  services=Services(p,path,r,auth,ops,delivery,clock,memory=memory)
 c=TestClient(create_app(services),raise_server_exceptions=False)
 def get(url,who='OP-ANALYST',expect=200):
  response=c.get('/api/v1'+url,headers={'Authorization':'Bearer '+tokens[who]})
  assert response.status_code==expect,(url,response.status_code,response.text)
  return response.json()['data'] if expect==200 else response.json()
 # Actual accepted services produce one plan/approval/work/outcome on same case.
 run=Run(r,clock,ops,tokens,'WATERLOGGING')
 with active_scope(p):
  asyncio.run(run.begin(planning,draft));_,report,_,_=asyncio.run(run.complete())
  q,followup=asyncio.run(run.followup())
  outcome=asyncio.run(run.call(q,'OP-ANALYST'))
  assert outcome['assessment_status']=='RESOLUTION_VERIFIED'
  # Actual broker discovery/call, StateGraph and persisted SDK checkpoint; model
  # choices explicitly scripted, never represented as genuine provider behavior.
  from app.agents.mcp import brokers
  from app.agents.runtime import InvestigationAgent
  from app.agents.checkpoints import saver
  from app.agents.models import InvestigationState
  from app.graph.queries import GraphQueries
  from tests.b10_fixtures import ScriptedModel,choose
  incidents=services.reads.targets('INVESTIGATES',inv)
  incident=next(i for i in incidents if r.get_node(i).kind=='Incident')
  cluster=next(i for i in incidents if r.get_node(i).kind=='ProblemCluster')
  thread='B17-'+uuid4().hex
  async def actual_agent():
   async with brokers(p,path,memory_path=None) as tools:
    model=ScriptedModel([choose('READ',{'template':'node','id':incident},'official::query_graph_readonly'),choose('READ',{'asset_id':'D1','from_time':'2026-10-17T00:00:00Z','to_time':clock()},'civicly::get_maintenance_history'),choose()])
    state=InvestigationState(graph=p.graph,investigation_id=inv,thread_id=thread,problem_cluster_id=cluster,incident_ids=[incident],asset_ids=['D1'],issue='WATERLOGGING',graph_revision=GraphQueries(r)._state(),discovered_tool_names=[v['name'] for v in tools.catalog()],inventory_hash=tools.inventory_hash,as_of=clock())
    agent=InvestigationAgent(p,r,tools,model,saver(p),clock=clock)
    return await agent.run(state,thread_id=thread)
  result=asyncio.run(actual_agent())
  saved=saver(p).get_tuple({'configurable':{'thread_id':thread}});assert saved
  original_checkpoint=saved.checkpoint
  from tests.schema_examples import edge
  r.create_relationship('DRAINS_TO','D1','D2',{**edge('B17-CANDIDATE-LINK'),'source_evidence_id':'EV','association_status':'CANDIDATE'})
  delivery.discover()
 query_proof={'unsupported':{},'supported':{}}
 # Journey 1: overview/map/counts scoped before pages, actual coordinates only.
 dashboard=get('/dashboard/summary');assert dashboard['completed_work_orders']==1 and dashboard['verified_work_orders']==1
 assert get('/dashboard/summary','OP-ROAD-LEAD')['completed_work_orders']==0
 for query in ['limit=1','cursor=PRIVATE-INPUT','issue=WATERLOGGING&issue=ROAD_DAMAGE']:
  response=get('/dashboard/summary?'+query,expect=422);assert response['error']['code']=='VALIDATION_ERROR' and 'PRIVATE-INPUT' not in json.dumps(response)
  query_proof['unsupported']['dashboard?'+query]=response['error']['code']
 filtered_dashboard=get('/dashboard/summary?issue=ROAD_DAMAGE');assert filtered_dashboard['completed_work_orders']==0
 assert get('/dashboard/summary?before=2020-01-01T00:00:00Z')['completed_work_orders']==0
 query_proof['supported']['dashboard_completed_order_counts']=[dashboard['completed_work_orders'],filtered_dashboard['completed_work_orders']]
 assert get('/work-orders?department_id=DEPT-DRAIN&status=COMPLETED&issue=WATERLOGGING')['total_count']==1
 assert get('/work-orders?department_id=DEPT-DRAIN','OP-ROAD-LEAD')['total_count']==0
 assert get('/work-orders?status=ASSIGNED')['total_count']==0
 assert get('/incidents?issue=ROAD_DAMAGE')['total_count']==0
 assert get('/incidents?department_id=DEPT-DRAIN','OP-DRAIN-LEAD')['total_count']==1
 assert get('/incidents?department_id=DEPT-DRAIN','OP-ROAD-LEAD')['total_count']==0
 assert get('/incidents?before=2026-10-18T00:00:00Z')['total_count']==0
 assert get('/incidents?after=2026-10-18T00:00:00Z')['total_count']==1
 page=get('/incidents?limit=1');assert len(page['items'])<=1
 get('/incidents?limit=51',expect=422);get('/incidents?depth=3',expect=422)
 get('/incidents?issue=UNKNOWN',expect=422);get('/incidents?token=secret',expect=422)
 get('/incidents?after=2026-10-19T00:00:00Z&before=2026-10-18T00:00:00Z',expect=422)
 mapdata=get('/map/features?investigation_id='+inv)
 assert mapdata['features'] and all(len(f['geometry']['coordinates'])==2 for f in mapdata['features'])
 assert any(incident in f['incident_ids'] for f in mapdata['features'])
 assert get('/map/features?investigation_id='+inv,'OP-ROAD-LEAD',expect=403)['error']['code']=='PERMISSION_DENIED'
 # Journey 2: exact case, competing hypotheses, typed finding, sources and graph.
 case=get('/investigations/'+inv)
 incident_detail=get('/incidents/'+incident);cluster_detail=get('/problem-clusters/'+cluster)
 assert incident_detail['cluster_id']==cluster_detail['id'] and incident in cluster_detail['incident_ids']
 complaints=[get('/complaints/'+cid) for cid in incident_detail['complaint_ids']]
 assert complaints and all(q['incident_id']==incident for q in complaints)
 hypotheses=get('/investigations/'+inv+'/hypotheses');assert hypotheses['total_count']>=2
 assert any(h['assessment_history'] for h in hypotheses['items'])
 for query in ['before=2020-01-01T00:00:00Z','after=2020-01-01T00:00:00Z','limit=1&limit=1']:
  rejected=get('/investigations/'+inv+'/hypotheses?'+query,expect=422);assert rejected['error']['code']=='VALIDATION_ERROR'
  query_proof['unsupported']['hypotheses?'+query]=rejected['error']['code']
 status=hypotheses['items'][0]['status'];status_page=get('/investigations/'+inv+'/hypotheses?status='+status)
 assert status_page['items'] and all(h['status']==status for h in status_page['items'])
 assert get('/investigations/'+inv+'/hypotheses?status=UNAVAILABLE')['total_count']==0
 query_proof['supported']['hypothesis_status_counts']=[status_page['total_count'],0]
 hpage=get('/investigations/'+inv+'/hypotheses?limit=1');assert hpage['next_cursor']
 hnext=get('/investigations/'+inv+'/hypotheses?limit=1&cursor='+hpage['next_cursor'])
 assert hpage['items'][0]['id']!=hnext['items'][0]['id'] and hnext['total_count']==hpage['total_count']
 evidence=get('/evidence/'+followup['entity_id']);assert evidence['reviewed']
 assert evidence['observation_source']['reviewer_id']=='OP-ANALYST'
 assert any(f['observation']['value']==0.0 and f['observation']['unit']=='boolean' for f in evidence['findings'])
 assert all(f['evidence_id']==evidence['id'] for f in evidence['findings'])
 get('/evidence/'+followup['entity_id'],'OP-ROAD-LEAD',403)
 graph=get('/investigations/'+inv+'/graph?depth=4&include_candidates=true')
 assert graph['decision_path_ids'] and graph['decision_paths']
 assert graph['nodes'] and graph['edges'] and len(graph['nodes'])<=120 and len(graph['edges'])<=200
 ids={n['id'] for n in graph['nodes']};assert all(e['source'] in ids and e['target'] in ids for e in graph['edges'])
 with active_scope(p):
  for e in graph['edges']:
   native=r.get_relationship(e['id']);assert (e['type'],e['source'],e['target'])==(native.kind,native.source,native.target)
 neighbors=get('/assets/D1/neighbors?depth=2');candidate_neighbors=get('/assets/D1/neighbors?depth=2&include_candidates=true')
 assert 'B17-CANDIDATE-LINK' not in {e['id'] for e in neighbors['edges']}
 assert next(e for e in candidate_neighbors['edges'] if e['id']=='B17-CANDIDATE-LINK')['verification_status']=='CANDIDATE'
 asset=get('/assets/D1')
 assert 'InfrastructureAsset' in asset['labels'] and asset['department_ids']==['DEPT-DRAIN']
 get('/assets/D1','OP-ROAD-LEAD',403)
 get('/assets/D1/neighbors','OP-ROAD-LEAD',403)
 get('/investigations/'+inv+'/graph','OP-ROAD-LEAD',403)
 get('/investigations/'+inv+'/hypotheses','OP-ROAD-LEAD',403)
 get('/assets/D1/neighbors?depth=6',expect=422)
 trace=get('/investigations/'+inv+'/trace')
 tools=[v for v in trace['items'] if v['kind']=='TOOL'];decisions=[v for v in trace['items'] if v['kind']=='DECISION']
 assert tools and decisions and tools[0]['validated_output'] is True
 assert all(v['execution_mode']=='DETERMINISTIC_FAKE_MODEL' for v in trace['items'])
 assert trace['phase']=='Coordinator' and not trace['recovery_required']
 assert trace['pause_reason']=='MISSING_EVIDENCE'
 tpage=get('/investigations/'+inv+'/trace?limit=1');assert tpage['next_cursor']
 tnext=get('/investigations/'+inv+'/trace?limit=1&cursor='+tpage['next_cursor'])
 assert tpage['items'][0]['event_id']!=tnext['items'][0]['event_id']
 assert get('/investigations/'+inv+'/trace?status=SUCCESS')['total_count']==2
 assert get('/investigations/'+inv+'/trace?before=2020-01-01T00:00:00Z')['total_count']==0
 assert get('/investigations/'+inv+'/trace?after=2020-01-01T00:00:00Z')['total_count']==trace['total_count']
 query_proof['supported']['trace_before2020_count']=0
 for url in ['/assets/D1?limit=1','/assets/D1/neighbors?cursor=A','/investigations/'+inv+'/graph?limit=1','/investigations/'+inv+'/trace?issue=WATERLOGGING','/map/features?depth=2']:
  assert get(url,expect=422)['error']['code']=='VALIDATION_ERROR'
  query_proof['unsupported'][url]='VALIDATION_ERROR'
 get('/investigations/'+inv+'/trace','OP-ROAD-LEAD',403)
 # Journey 3: immutable draft vs current approval/execution, exact DAG/citations,
 # actual recorded verification and memory are reconstructable through HTTP.
 plan=get('/plans/'+run.b['plan_id']);assert not plan['draft_receipt']['approved'] and plan['approval_status']=='COMPLETED'
 assert plan['draft']['tasks'][0]['procedure_citation']['source_version']>=1
 docid=plan['draft']['tasks'][0]['procedure_citation']['canonical_document_id']
 doc=get('/documents/'+docid);assert doc['citations'] and doc['assertion_status']=='PROPOSED' and not doc['trusted_as_instructions']
 approval=get('/approvals','OP-APPROVER')['items'][0];assert approval['status']=='APPROVED'
 get('/approvals/'+approval['id'],'OP-APPROVER')
 work=get('/work-orders/'+run.w['id']);assert work['status']=='COMPLETED' and work['resolution_verified']
 outcomes=get('/problem-clusters/'+cluster+'/outcomes');assert any(o['id']==outcome['id'] for o in outcomes['items'])
 get('/cases/'+incident+'/memory');get('/monitoring')
 # SSE malformed/future/unknown query/conflicting resume handled BEFORE headers.
 for query,header,code in [('cursor=01',None,'CURSOR_INVALID'),('cursor=999999',None,'CURSOR_FUTURE'),('cursor=0','1','CURSOR_CONFLICT')]:
  h={'Authorization':'Bearer '+tokens['OP-ANALYST']}
  if header:h['Last-Event-ID']=header
  response=c.get('/api/v1/events/stream?'+query,headers=h)
  assert response.status_code in {409,422} and response.json()['error']['code']==code,response.text
 # Same retained source, real subprocess Uvicorn and streaming TCP client.
 network=network_sse(db,tmp_path,p,path,auth,tokens,memory,clock,services,inv,run,monkeypatch)
 with active_scope(p):assert saver(p).get_tuple(saved.config).checkpoint==original_checkpoint
 proof={'mode':'SCRIPTED_MODEL_REAL_HTTP_FALKORDB_MCP_SAVER_TCP_SSE','source_graph':p.graph,'investigation_id':inv,'incident_id':incident,'cluster_id':cluster,'plan_id':run.b['plan_id'],'work_order_id':run.w['id'],'outcome_id':outcome['id'],'checkpoint_id':saved.config['configurable']['checkpoint_id'],'all_eight_B17_routes_exercised':True,'complaints':complaints,'incident':incident_detail,'cluster':cluster_detail,'dashboard':dashboard,'map':mapdata,'evidence':evidence,'graph':graph,'neighbors':neighbors,'trace':trace,'network':network,'provider_requests':0,'query_parameters':query_proof}
 prefix=os.environ.get('CIVICLY_FRONTEND_EVIDENCE_PREFIX','B17')
 assert prefix in {'B17','B17R'}
 Path('docs/evidence/'+prefix+'-journey.json').write_text(json.dumps(proof,indent=2)+'\n')


def network_sse(db,tmp_path,p,path,auth,tokens,memory,clock,services,inv,run,monkeypatch):
 from app.memory.runtime import Profile
 user='b17_memory_'+uuid4().hex;password=secrets.token_urlsafe(48)
 db.connection.execute_command('ACL','SETUSER',user,'reset','on','#'+hashlib.sha256(password.encode()).hexdigest(),'~'+memory.repo.graph.name,'~'+memory.config.graph_name,'-@all','+ping','+info','+client|setinfo','+graph.ro_query')
 mp=Profile(docs_graph=memory.config.graph_name,canonical_graph=memory.repo.graph.name,source_graphs=[p.graph],reader_user=user,reader_password=password)
 mpath=tmp_path/'network-memory.json';mp.json_private(mpath)
 sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
 env={**os.environ,'PYTHONPATH':str(Path('backend/test_guards').resolve())+os.pathsep+str(Path('backend').resolve())}
 cmd=[sys.executable,'-m','app.api','--profile',str(path),'--auth-store',str(auth.path),'--memory-profile',str(mpath),'--at',clock(),'--port',str(port)]
 # Explicit real auth clock is held by parent for deterministic session expiry.
 log=tmp_path/'server.log';headers={'Authorization':'Bearer '+tokens['OP-ANALYST']}
 with log.open('w') as f:
  proc=subprocess.Popen(cmd,env=env,stdout=f,stderr=f)
  try:
   with httpx.Client(base_url=f'http://127.0.0.1:{port}',timeout=10) as net:
    for _ in range(60):
     try:
      if net.get('/api/v1/health/live').status_code==200:break
     except httpx.ConnectError:pass
     if proc.poll() is not None:raise AssertionError('Local server failed; inspect private log')
     time.sleep(.1)
    else:raise AssertionError('Local server startup deadline')
    assert len(net.get('/openapi.json').json()['paths'])==49
    # Decode complete frames only; no buffering entire infinite body or ASGI stand-in.
    def frames(response):
     record={}
     for line in response.iter_lines():
      if not line:
       if record:yield record;record={}
      elif not line.startswith(':'):
       k,_,v=line.partition(':');record[k]=v.lstrip()
    with active_scope(p):
     before=services.delivery.store.rows('delivery');cursor=services.delivery.store.get('delivery_stream','root')['cursor']
     work_before=r_count=services.repo._read('MATCH (w:WorkOrder) RETURN count(w)')[0][0]
    late=net.post('/api/v1/inspections',headers={**headers,'Idempotency-Key':'B17-late-inspection'},json={'investigation_id':inv,'asset_ids':['D1'],'department_id':'DEPT-DRAIN','inspection_type':'B17-SYNTHETIC-CONTEXT'})
    assert late.status_code==200,late.text
    late_inspection=late.json()['data']['id']
    received=[]
    with net.stream('GET','/api/v1/events/stream?investigation_id='+inv,headers=headers) as response:
     assert response.status_code==200 and response.headers['content-type'].startswith('text/event-stream')
     for item in frames(response):
      if item['event']=='cursor':break
      received.append(item)
    assert any(v['event']=='case_tool_called' for v in received) and any(v['event']=='decision_recorded' for v in received)
    ids=[int(v['id']) for v in received];assert len(ids)==len(set(ids))
    # Register a genuinely later source fact only through the accepted explicit
    # host service; stream itself never discovers, acknowledges or runs a case.
    with active_scope(p):
     later=services.delivery.request_resume(inv,'B17-later',operator='B17-proof',reason='Persisted explicit source update, no execution',authorize=True)
    later_cursor=later['public']['cursor']
    with net.stream('GET','/api/v1/events/stream?investigation_id='+inv,headers={**headers,'Last-Event-ID':str(cursor)}) as response:
     item=next(v for v in frames(response) if v['event']!='cursor')
     assert int(item['id'])==later_cursor and json.loads(item['data'])['id']==later['id']
    # This source committed BEFORE the resume event, but discovery is later.
    # Registration cursor must still deliver it after the saved resume cursor.
    with active_scope(p):services.delivery.discover()
    with net.stream('GET','/api/v1/events/stream?investigation_id='+inv,headers={**headers,'Last-Event-ID':str(later_cursor)}) as response:
     late_frame=next(v for v in frames(response) if v['event']!='cursor')
     late_payload=json.loads(late_frame['data'])
     assert late_frame['event']=='inspection_requested' and late_payload['entity_id']==late_inspection
     assert int(late_frame['id'])>later_cursor and late_payload['revision']<later['event']['aggregate_revision']
    latest_cursor=int(late_frame['id'])
    # Filtered unauthorized rows advance only a transport cursor, no data leak.
    with net.stream('GET','/api/v1/events/stream',headers={'Authorization':'Bearer '+tokens['OP-ROAD-LEAD']}) as response:
     hidden=next(frames(response));assert hidden['event']=='cursor'
     assert set(json.loads(hidden['data']))=={'cursor'}
     assert inv not in hidden['data'] and late_inspection not in hidden['data']
    # Real session expiry is rechecked after stream headers, using the persisted
    # session store; no fake authentication transport or provider call.
    with net.stream('GET','/api/v1/events/stream?cursor='+str(latest_cursor),headers={'Authorization':'Bearer '+tokens['OP-APPROVER']}) as response:
     with auth.db() as authdb:authdb.execute('UPDATE session SET expires=? WHERE id=?',(auth.clock()-1,hashlib.sha256(tokens['OP-APPROVER'].encode()).hexdigest()))
     expired=next(frames(response));assert expired['event']=='error' and json.loads(expired['data'])['code']=='UNAUTHORIZED'
    # Disconnect and exact reconnect: original rows untouched, later cursor excluded.

    with net.stream('GET','/api/v1/events/stream?cursor='+str(latest_cursor),headers=headers) as response:
     auth.logout(tokens['OP-ANALYST'])
     event=next(frames(response));assert event['event']=='error' and json.loads(event['data'])['code']=='UNAUTHORIZED' and 'id' not in event
    with active_scope(p):
     after=services.delivery.store.rows('delivery')
     old={v['id']:v for v in before}
     assert all(v==old[v['id']] for v in after if v['id'] in old)
     assert services.repo._read('MATCH (w:WorkOrder) RETURN count(w)')[0][0]==work_before==1
     assert services.delivery.store.get('delivery',later['id'])['status']=='PENDING'
    refetch=net.get('/api/v1/investigations/'+inv,headers={'Authorization':'Bearer '+tokens['OP-ADMIN']});assert refetch.status_code==200 and refetch.json()['data']['id']==inv
    assert not any(token in log.read_text() for token in tokens.values()) and password not in log.read_text()
    return {'mode':'ACTUAL_LOCALHOST_UVICORN_TCP_SSE','replay_event_cursors':ids,'later_cursor':later_cursor,'later_event_id':later['id'],'late_discovery_event_id':late_payload['id'],'late_discovery_cursor':latest_cursor,'late_source_revision':late_payload['revision'],'later_registered_resume_revision':later['event']['aggregate_revision'],'expired_stream_stopped':True,'filtered_stream_exposes_only_cursor':True,'authoritative_refetch_status':refetch.status_code,'revoked_stream_stopped':True,'disconnect_changed_existing_delivery_rows':False,'work_order_count':1,'later_event_status':'PENDING','credentials_logged':False}
  finally:proc.terminate();proc.wait(timeout=15)
