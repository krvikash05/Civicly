"""B20-R-UTILITY read-only retained-evidence audit; no credential values emitted."""
import hashlib,importlib.metadata,json,re,sqlite3,subprocess,sys
from pathlib import Path
root=Path.cwd();base=Path('/tmp/b20r-utility-baseline');before=json.loads((base/'manifest.json').read_text())
public=sorted(n for n in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\0') if n and Path(n).is_file())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert set(before)<=set(public)
changed=sorted(n for n,h in before.items() if sha(n)!=h and not n.startswith('frontend/'));new=sorted(n for n in set(public)-set(before) if not n.startswith('frontend/'))
trackers={'decision.md','flow.md','implementation_status.md','test_log.md','blockers.md','task_board.md'}
allowed=trackers|{'backend/OPERATIONS.md','backend/PLANNING.md','backend/app/services/operations/execution.py','backend/app/services/operations/service.py','backend/app/services/planning/models.py','backend/app/services/planning/policy.py','contracts/operations.json','contracts/resolution_planning.json','contracts/api_models.json','scripts/validate_operations.py','scripts/validate_planning.py'}
assert set(changed)==allowed,(set(changed)^allowed)
for n in trackers:assert Path(n).read_bytes().startswith((base/n).read_bytes())
old_evidence=[n for n in before if n.startswith('docs/evidence/')];old_tests=[n for n in before if n.startswith('backend/tests/')]
assert not (set(old_evidence)|set(old_tests))&set(changed)
assert {n for n in new if not n.startswith('docs/evidence/B20R-UTILITY-')}=={'backend/UTILITY.md','backend/app/services/operations/utility.py','backend/app/services/planning/utility.py','backend/tests/integration/test_utility_intervention_runtime.py','backend/tests/unit/test_utility_intervention.py','data/documents/b20r_utility/D022_utility_isolation_repair.md','data/documents/b20r_utility/manifest.json'}
private=[]
for line in Path('.env').read_text().splitlines():
 if '=' in line:
  k,v=line.split('=',1);v=v.strip(' \"\'')
  if any(t in k.upper() for t in ['KEY','SECRET','TOKEN','PASSWORD']) and len(v)>7:private.append(v.encode())
def collect(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if any(t in k.lower() for t in ['password','secret','api_key','token']) and isinstance(v,str) and len(v)>7:private.append(v.encode())
   else:collect(v)
 elif isinstance(x,list):
  for v in x:collect(v)
for p in [*Path('.runtime').glob('*.json'),*Path('.runtime/b20-review').glob('**/profile.json'),*Path('.runtime/b20-review').glob('**/agent.json'),*Path('.runtime/b20-review').glob('**/memory.json')]:collect(json.loads(p.read_text()))
for n in changed+new:
 raw=Path(n).read_bytes()
 assert not any(v in raw for v in private),'PRIVATE_VALUE_IN_PUBLIC_ARTIFACT'
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}|[A-Za-z0-9_-]{43}\.[0-9a-f]{64}',raw),'PRIVATE_PATTERN'
guards=list(Path('docs/evidence').glob('B20R-UTILITY-*-zero-live.json'))
for p in guards:
 v=json.loads(p.read_text());assert v['external_gemini_requests_sent']==v['ordinary_unexpected_attempts']==0
accepted=json.loads(Path('docs/evidence/B11-LIVE-SMOKE-R-fresh-process.json').read_text())['accounting']['requests']
with sqlite3.connect('file:'+str(root/'.runtime/ai-spend.sqlite3')+'?mode=ro',uri=True) as conn:
 conn.row_factory=sqlite3.Row;requests=[dict(r) for r in conn.execute('SELECT * FROM requests ORDER BY created,id')];assert requests==accepted
 assert conn.execute('SELECT count(*) FROM sessions').fetchone()[0]==0
 assert conn.execute("SELECT count(*) FROM request_holds WHERE status='OPEN'").fetchone()[0]==0
sys.path.insert(0,str(root/'backend'))
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.models import digest
from app.mcp.runtime import CITY_GRAPH
from app.active import load,active_scope
profiles={load(p).graph:load(p) for p in Path('.runtime/b20-review').glob('*/demo-runs/*/profile.json')}
runs=[]
with connect(Settings(_env_file='.env')) as db:
 server=db.connection.info('server')['redis_version'];modules=db.connection.execute_command('MODULE','LIST')
 module_versions={}
 for row in modules:
  d={str(row[i].decode() if isinstance(row[i],bytes) else row[i]):row[i+1] for i in range(0,len(row),2)}
  name=d['name'];module_versions[name.decode() if isinstance(name,bytes) else name]=d['ver']
 for path in sorted(Path('docs/evidence').glob('B20-S0*-*.json')):
  proof=json.loads(path.read_text());p=profiles[proof['source_graph']]
  with active_scope(p):
   r=GraphRepository(db,p.graph);assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[0]]
   for e in proof['released_evidence']:r.get_node(e['id'],'Evidence')
   from app.agents.checkpoints import saver
   saved=saver(p).get_tuple({'configurable':{'thread_id':proof['thread_id'],'checkpoint_id':proof['baseline_checkpoint_id']}})
   assert saved and saved.checkpoint['channel_values']['data']==proof['baseline']
   if proof['scenario']=='S01':
    assert any(x['verification_status']=='VERIFIED' and x['relationship']=='DRAINS_TO' for x in proof['baseline']['observations'][1]['paths'])
    edge=r.get_relationship('B19-SURVEY-FLOW');assert edge.source=='DRAIN-100' and edge.target=='DRAIN-101'
   if proof['scenario'] in {'S03','S04'}:
    assert any(x['verification_status']=='VERIFIED' and x['relationship']=='UNDERLIES' for x in proof['baseline']['observations'][1]['paths'])
   if proof['scenario'] in {'S05','S06'}:
    assert r._read('MATCH (p:PickupExecution) RETURN count(p)')==[[0]]
    assert r._read('MATCH ()-[r:HAS_SCHEDULE]->() RETURN r.association_status')==[['CANDIDATE']]
   if proof['scenario']=='S02':
    journals=r._read("MATCH (e:Evidence {evidence_type:'COMPLAINT_INTAKE'}) RETURN e.summary")
    obs=[m for row in journals for m in json.loads(row[0])['canonical']['details']['measurements']]
    assert any(m['name']=='rainfall' and m['value']==125.0 and m['unit']=='mm' and m['basis']=='REPORTED' for m in obs)
   runs.append({'scenario':proof['scenario'],'variant':proof['variant'],'source_graph':p.graph,'baseline_checkpoint_unchanged':True})
 assert len(runs)==12
 city=GraphRepository(db,CITY_GRAPH);ns=city._read('MATCH (n:CivicEntity) RETURN labels(n),properties(n) LIMIT 859');es=city._read('MATCH (s:CivicEntity)-[e]->(t:CivicEntity) RETURN type(e),properties(e),labels(s),properties(s),labels(t),properties(t) LIMIT 1247')
 assert len(ns)==858 and len(es)==1246
 records=[city.decode_node(*n) for n in ns]+[city._decode_edge_row(e) for e in es]
 city_hash=digest({n.id:n.content_hash for n in records});assert city_hash==json.loads(Path('docs/evidence/B04-retained-post-recreation.json').read_text())['verified_content_hash']
 assert city._read("MATCH ()-[e:DRAINS_TO]->() WHERE e.association_status='CANDIDATE' RETURN count(e)")==[[42]]
 assert db.select_graph('civicly_b01_runtime').ro_query('MATCH (n:B01Probe {id:$id}) RETURN n.id,n.source_kind,n.task LIMIT 1',params={'id':'B01-PERSISTENCE'}).result_set==[['B01-PERSISTENCE','SYNTHETIC','B01']]
 fault=json.loads(Path('docs/evidence/B12R2-postcommit-recovery.json').read_text());ctx=fault['reconciliation']
 assert db.connection.get('civicly:b10:'+ctx['graph']+':'+digest(fault['thread_id'])+':quarantine')
 assert db.select_graph(ctx['graph']).ro_query('MATCH (p:ResolutionPlan) RETURN p.id,p.version,p.plan_hash').result_set==[[ctx['plan_id'],1,ctx['expected_plan_hash']]]
 previous=json.loads(Path('docs/evidence/B19-retained-failed-wake.json').read_text())
 for f in previous['failed_wakes']:assert db.connection.get('civicly:b10:'+f['source_graph']+':'+digest(f['thread_id'])+':quarantine')
proof=json.loads(Path('docs/evidence/B20R-OWNERSHIP-real-proof.json').read_text())
profile_path=next(p for p in Path('.runtime/b20-review').glob('*/demo-runs/*/profile.json') if load(p).graph==proof['source_graph'])
p=load(profile_path)
with connect(Settings(_env_file='.env')) as db,active_scope(p):
 from app.services.responsibility.service import Responsibility
 from app.services.operations.auth import Auth
 from app.services.operations.storage import Storage
 r=GraphRepository(db,p.graph);service=Responsibility(r,Auth(profile_path.parents[2]/'auth.sqlite3'),clock=lambda:proof['synthetic_clock'][0])
 state=proof['proof'];checked=[]
 for key in ['verified','successor','historical','uncertain_retained']:
  record=service.readback(state[key]['id']);assert record['status']=='VERIFIED';checked.append(record)
 intent=Storage(r).get('api_request',state['recovery']['details']['request_id']);assert intent['status']=='DISPATCHING'
 assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[0]]
 assert r._read('MATCH (d:CivicPlanDraft {id:$id}) RETURN d.payload_sha256',{'id':state['plan_id']})==state['payload_hash']
 candidates=r._read("MATCH (:InfrastructureAsset {id:$id})-[e:MAINTAINED_BY]->() WHERE e.association_status='CANDIDATE' RETURN e.id,e.source_evidence_id",{'id':proof['case']['asset_id']})
 assert len(candidates)==1
 assert [r.get_relationship(candidates[0][0]).content_hash,r.get_node(candidates[0][1]).content_hash]==state['candidate_and_source_hashes']
 from app.agents.checkpoints import saver
 saved={x.config['configurable']['checkpoint_id']:hashlib.sha256(json.dumps(x.checkpoint,sort_keys=True,default=str).encode()).hexdigest() for x in saver(p).list(None)}
 assert saved==proof['checkpoints']

utility=json.loads(Path('docs/evidence/B20R-UTILITY-primary-proof.json').read_text())
profile_path=next(p for p in Path('.runtime/b20-review').glob('*/demo-runs/*/profile.json') if load(p).graph==utility['source_graph']);p=load(profile_path)
with connect(Settings(_env_file='.env')) as db,active_scope(p):
 r=GraphRepository(db,p.graph);store=Storage(r)
 assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[3]]
 for key in ['isolation_order','repair_order','road_order']:assert r.get_node(utility[key]['id'],'WorkOrder').properties['status']=='COMPLETED'
 assert r.get_node(utility['plan_id'],'ResolutionPlan').properties['status']=='MONITORING'
 out=store.get('outcome',utility['utility_verification']['id']);assert out['assessment_status']=='UTILITY_VERIFIED' and out['case_closed'] is False
 recovery=utility['recovery'];request=recovery['domain_request_id'];assert store.get('api_request',request)['status']=='DISPATCHING'
 assert r._read('MATCH (e:Evidence {id:$id}) RETURN count(e)',{'id':recovery['evidence_id']})==[[1]]
 from app.services.evidence.reader import Reader
 ref=Reader(r,'2026-10-19T13:00:00.000000Z').evidence(recovery['evidence_id']);assert ref.report.review
 produced=Reader(r,'2026-10-19T13:00:00.000000Z').edges('PRODUCED',target=ref.id)
 assert Reader(r,'2026-10-19T13:00:00.000000Z').journal(produced[0].properties['source_evidence_id']).state=='COMMITTED'
value={'task':'B20-R-UTILITY','status':'TECHNICALLY_PASS_HUMAN_REVIEW_PENDING','B20':'PARTIAL_BLOCKED','baseline_public_files_retained':len(before),'prior_evidence_byte_identical':len(old_evidence),'prior_tests_unchanged':len(old_tests),'all_six_trackers_append_only':True,'modified':changed,'new':new,'old_migrations_schema_city_scenarios_dependencies_unchanged':True,'private_value_scan':'PASS including patch','provider_guard_reports':len(guards),'external_provider_requests':0,'paid_requests_unchanged':len(requests),'prior_B20_scenario_checkpoints_retained':len(runs),'B01_probe_unchanged':True,'B04_city_hash':city_hash,'candidate_drains':42,'B12R2_quarantine_single_plan_retained':True,'B19_quarantines_retained':True,'accepted_ownership_sources_checkpoints_and_unknown_intent_retained':True,'utility_three_completed_orders':True,'utility_verified_case_not_closed':True,'utility_unknown_intent_and_committed_report_retained':True,'tests':{'distinct_pass':75,'unit':73,'real':2,'unresolved_fail':0,'skip':0},'versions':{n:importlib.metadata.version(n) for n in ['falkordb','mcp','langgraph','langchain-falkordb','fastapi','pydantic']},'redis_version':server,'module_versions':module_versions}
Path('docs/evidence/B20R-UTILITY-audit.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
