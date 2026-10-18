"""Real B19/FalkorDB/API/CLI/MCP service evidence; explicit synthetic facts, no model."""
import asyncio,hashlib,json,os,subprocess,sys
from pathlib import Path
from uuid import uuid4
import httpx,pytest
from app.active import active_scope,load
from app.api.__main__ import configured_app
from app.graph.repository import GraphRepository,Conflict,PreconditionFailed
from app.services.evidence.service import EvidenceService
from app.services.evidence.policies import POLICIES
from app.services.evidence.reader import Reader
from app.services.service_evidence import ServiceEvidence,ServiceRecord,validate,parse_source
from app.services.operations.storage import Storage
from app.agents.mcp import brokers
from app.mcp.civicly.contracts import Context
from tests.b20_fixtures import shared
from tests.integration.test_demo_runtime import fresh,client_run,headers,inspection,AT
pytestmark=pytest.mark.integration

@pytest.mark.parametrize('scenario,variant',[('S05','PRIMARY'),('S05','NEGATIVE'),('S06','PRIMARY'),('S06','NEGATIVE')])
def test_dated_service_evidence(shared,scenario,variant,monkeypatch):
 asyncio.run(journey(shared,scenario,variant,monkeypatch))

async def journey(shared,scenario,variant,monkeypatch):
 tag='B20RSE-'+scenario+'-'+variant;receipt=await fresh(shared,scenario,variant,tag+'-reset');path=shared.path.parent/receipt['profile_reference']/'profile.json';p=load(path);case=receipt['scenario']['cases'][0]
 with active_scope(p):
  r=GraphRepository(shared.db,p.graph);ev=EvidenceService(r,clock=lambda:AT);analyst=shared.auth.resolve(shared.tokens['OP-ANALYST']);hyp={};old={}
  candidates={e.id:e.content_hash for kind in ['HAS_SCHEDULE','COLLECTED_BY','MAINTAINED_BY'] for e in r._edges(kind)}
  for cause in ['MISSED_PICKUP','CAPACITY_SHORTFALL','ILLEGAL_DUMPING']:
   rule=POLICIES['WASTE_ACCUMULATION'][cause]
   hid=ev.execute({'operation':'propose','request_id':tag+'-hyp-'+cause,'investigation_id':case['investigation_id'],'incident_ids':[case['incident_id']],'asset_ids':[case['asset_id']],'cause_code':cause,'statement':'Explicit test competing '+cause,'mechanism':'Synthetic evidence must establish scoped dated mechanism','confirming_codes':rule['confirming'],'falsifying_codes':rule['falsifying']},analyst).entity_id;hyp[cause]=hid
   a=ev.execute({'operation':'assess','request_id':tag+'-baseline-'+cause,'hypothesis_id':hid,'expected_hash':r.get_node(hid).content_hash,'evidence_ids':[],'as_of':AT},analyst).assessment;old[a.id]=r.get_node(a.id).content_hash
  async def mcp_read():
   async with brokers(p,path,timeout=10,memory_path=path.parent/'memory.json') as tools:
    assert any(t['name']=='civicly::get_pickup_execution_history' for t in tools.catalog())
    c=Context(trace_id=uuid4().hex,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=case['investigation_id'])
    return await tools.call('civicly::get_pickup_execution_history',{'collection_point_id':case['asset_id'],'days':1,'as_of':AT},c,'Read actual dated service execution; absence is not missed pickup',cutoff=AT)
  before=await mcp_read();assert before['status'] in {'SUCCESS','PARTIAL'} and not before['pickup_executions'];assert r._read('MATCH (n:PickupExecution) RETURN count(n)')==[[0]]
  app=configured_app(path,shared.auth.path,path.parent/'memory.json',AT)
  async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://local') as c:
   s=app.state.services;view,lead=await inspection(shared,c,case,tag+'-survey');q={'expected_current_stage':'BASELINE_VISIBLE','stage':'EVIDENCE_REVEALED','investigation_id':case['investigation_id'],'inspection_id':view['id'],'expected_hash':view['expected_hash']};route='/api/v1/demo/scenarios/'+scenario+'/advance'
   if scenario=='S05' and variant=='PRIMARY':
    for who,field,reviewer in [('OP-ANALYST',lead,'OP-ANALYST'),('OP-ADMIN','OP-ROAD-LEAD','OP-ANALYST'),('OP-ADMIN',lead,'OP-APPROVER')]:
     denied=await c.post(route,json=q,headers=headers(shared,who,tag+'-denied-'+who+field+reviewer,field=field,reviewer=reviewer));assert denied.status_code==403,denied.json()
    assert r._read('MATCH (n:PickupExecution) RETURN count(n)')==[[0]]
   # One actual controller/service commit with deliberate acknowledgement fault.
   recovery=None;real=ServiceEvidence.readback;calls=[];execute=ServiceEvidence.record
   if scenario=='S06' and variant=='NEGATIVE':
    def counted(self,*a,**kw):calls.append(a[0]);return execute(self,*a,**kw)
    def fault(self,id):
     real(self,id);raise ValueError('PRIVATE_SERVICE_POST_COMMIT_READBACK')
    monkeypatch.setattr(ServiceEvidence,'record',counted);monkeypatch.setattr(ServiceEvidence,'readback',fault)
   h=headers(shared,key=tag+'-release',field=lead,reviewer='OP-ANALYST');response=await c.post(route,json=q,headers=h)
   if scenario=='S06' and variant=='NEGATIVE':
    assert response.status_code==409,response.json();recovery=response.json()['error'];assert recovery['code']=='RECOVERY_REQUIRED' and recovery['details']['commitment']=='UNKNOWN'
    monkeypatch.setattr(ServiceEvidence,'readback',real)
    replay=await c.post(route,json=q,headers=h);assert replay.status_code==409 and replay.json()['error']['details']==recovery['details'];assert len(calls)==1
    record=calls[0];released=[record.report_evidence_id,record.id];assert s.delivery.store.get('api_request',recovery['details']['request_id'])['status']=='DISPATCHING'
   else:
    assert response.status_code==200,response.json();released=response.json()['data']['released_evidence_ids'];assert len(released)==2
    replay=await c.post(route,json=q,headers=h);assert replay.status_code==200 and replay.json()['data']==response.json()['data']
    record=validate(r,released[0],AT)
   assert record and record.id==released[1];assert len(set(released))==2
   native_source=r.get_node(record.id,'Evidence');assert native_source.properties['source_record_id']!=r.get_node(record.report_evidence_id).properties['source_record_id']
   report=Reader(r,AT).evidence(record.report_evidence_id).report;assert report.review and report.inspector_id!=report.review.reviewer_id
   assert all(ob.observed_at>=r.get_node(report.inspection_id).properties['requested_at'] for ob in report.observations)
   assert record.checked_at<record.recorded_at and record.scheduled_at<record.checked_at
   if record.actual_at:
    from app.graph.schema import timestamp
    assert timestamp(record.actual_at)<min(timestamp(ob.observed_at) for ob in report.observations)
   expected_count=0 if record.status=='UNKNOWN' else 1
   assert r._read('MATCH (n:PickupExecution) RETURN count(n)')==[[expected_count]]
   if record.pickup_id:
    n=r.get_node(record.pickup_id,'PickupExecution');assert n.properties['route_id']==record.route_id and n.properties['status']==record.status
    if record.status=='MISSED':assert 'actual_at' not in n.properties
    assert r._read('MATCH (n:PickupExecution {id:$id})-[:PICKUP_FOR]->(p:WasteCollectionPoint) RETURN p.id',{'id':record.pickup_id})==[[case['asset_id']]]
   source=await c.get('/api/v1/evidence/'+record.id,headers=headers(shared,'OP-ANALYST'));assert source.status_code==200,source.json();assert source.json()['data']['reviewed'] and source.json()['data']['service_record']==record.model_dump(mode='json')
   after={}
   for cause,hid in hyp.items():
    a=ev.execute({'operation':'assess','request_id':tag+'-after-'+cause,'hypothesis_id':hid,'expected_hash':r.get_node(hid).content_hash,'evidence_ids':released,'as_of':AT},analyst).assessment;after[cause]=a
    assert a.previous_assessment_id in old and r.get_node(a.previous_assessment_id).content_hash==old[a.previous_assessment_id]
   expected={('S05','PRIMARY'):('SUPPORTED','INCONCLUSIVE'),('S05','NEGATIVE'):('INCONCLUSIVE','INCONCLUSIVE'),('S06','PRIMARY'):('CONTRADICTED','SUPPORTED'),('S06','NEGATIVE'):('CONTRADICTED','INCONCLUSIVE')}[(scenario,variant)]
   assert (after['MISSED_PICKUP'].assessment,after['ILLEGAL_DUMPING'].assessment)==expected,{k:v.model_dump(mode='json') for k,v in after.items()}
   assert after['MISSED_PICKUP'].rule_version==after['ILLEGAL_DUMPING'].rule_version==3
   if scenario=='S06' and variant=='PRIMARY':assert record.id in {ref.id for ref in after['ILLEGAL_DUMPING'].evidence_references}
   # Strict duplicate source identity without adding a second canonical execution.
   if not recovery:
    with pytest.raises(Conflict):ServiceEvidence(s).record(record,tag+'-duplicate-source')
   assert r._read('MATCH (n:PickupExecution) RETURN count(n)')==[[expected_count]]
   events=s.delivery.discover();assert events;state=s.ops.store.get('service_evidence',record.report_evidence_id)
   assert s.delivery.store.get('delivery',state['receipt']['event_id'])['event']['type']=='GRAPH_EVIDENCE_CHANGED'
   assert r._read('MATCH (n:ResolutionPlan) RETURN count(n)')==[[0]] and r._read('MATCH (n:WorkOrder) RETURN count(n)')==[[0]]
   assert all(r.get_relationship(id).content_hash==sha for id,sha in candidates.items())
   # Real CLI delegates the accepted API read/service projection, no private logs.
   cli=None
   if scenario=='S06' and variant=='PRIMARY':
    from cli.private import write_private,scope
    session=path.parent/'service-session.json';write_private(session,{'version':1,'scope':scope(p,shared.auth.path),'token':shared.tokens['OP-ANALYST'],'operator_id':'OP-ANALYST','login_key':'B20RSE'})
    command=[sys.executable,'-m','cli','--profile',str(path),'--auth-store',str(shared.auth.path),'--memory-profile',str(path.parent/'memory.json'),'--session',str(session),'--at',AT,'evidence','get','--id',record.id]
    done=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'PYTHONPATH':str(Path('backend/test_guards').resolve())+os.pathsep+str(Path('backend').resolve())},timeout=60);assert done.returncode==0,done.stdout;cli=json.loads(done.stdout);assert cli['data']['service_record']['actual_at']==record.actual_at
  got=await mcp_read();assert got['status'] in {'SUCCESS','PARTIAL'},got;assert len(got['pickup_executions'])==expected_count
  if record.pickup_id:assert record.id in got['source_evidence_ids']
  Path('docs/evidence/B20R-SERVICE-EVIDENCE-'+scenario+'-'+variant+'-proof.json').write_text(json.dumps({'mode':'REAL_B19_FALKORDB_HTTP_CLI_MCP_EXPLICIT_SYNTHETIC_OBSERVATIONS_NO_MODEL','source_graph':p.graph,'profile_reference':receipt['profile_reference'],'case':case,'service_record':record.model_dump(mode='json'),'report':report.model_dump(mode='json'),'baseline_assessment_hashes':old,'new_assessments':{k:v.model_dump(mode='json') for k,v in after.items()},'candidate_hashes_retained':candidates,'pickup_count':expected_count,'runtime_mcp_before':before,'runtime_mcp_after':got,'api_source':source.json()['data'],'cli':cli,'recovery':recovery,'committed_once_no_redispatch':bool(recovery),'plans':0,'work_orders':0,'provider_requests':0},indent=2)+'\n')
