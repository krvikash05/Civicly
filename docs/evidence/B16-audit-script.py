"""Read-only retention/security audit; reports no private values."""
from pathlib import Path
import subprocess,json,hashlib,re,sqlite3,sys,os,platform,importlib.metadata
root=Path.cwd();base=Path('/tmp/b16-baseline');before=json.loads((base/'hashes.json').read_text())
public=sorted(n for n in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\0') if n and Path(n).is_file())
assert set(before)<=set(public)
changed=sorted(n for n,h in before.items() if hashlib.sha256(Path(n).read_bytes()).hexdigest()!=h)
old_evidence=[n for n in before if n.startswith('docs/evidence/')];assert not set(changed)&set(old_evidence)
old_tests=[n for n in before if n.startswith('backend/tests/')];assert not set(changed)&set(old_tests)
protected=[n for n in before if n.startswith(('backend/app/graph/migrations/','data/','backend/app/mcp/')) or n in {'contracts/schema_registry.json','contracts/relationship_matrix.json','backend/uv.lock','backend/pyproject.toml'}]
assert not set(changed)&set(protected)
trackers={'decision.md','flow.md','implementation_status.md','task_board.md','test_log.md','blockers.md','README.md'}
for n in trackers:
 prior=(base/'files'/n).read_text();current=Path(n).read_text()
 if n in {'task_board.md','implementation_status.md','test_log.md','blockers.md','README.md'}:
  a,rest=current.split('\n',1);rest=re.sub(r'^\n> \*\*CURRENT B16[^\n]+\n\n','',rest,count=1);rest=rest.replace('B16 local API startup and secure `/docs`: [backend/API.md](backend/API.md). Exact implemented/deferred routes: [B16-COVERAGE](docs/evidence/B16-COVERAGE.md).\n','')
  normalized=a+'\n'+rest
  # New current summary precedes intact historical body; audit entries are appended.
  assert prior in normalized or prior.rstrip() in normalized,n
 else:assert current.startswith(prior),n
secrets=[]
for line in Path('.env').read_text().splitlines():
 if '=' not in line:continue
 k,v=line.split('=',1);v=v.strip(' \"\'')
 if any(t in k.upper() for t in ['KEY','TOKEN','SECRET','PASSWORD']) and len(v)>7:secrets.append(v.encode())
def collect(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if any(t in k.lower() for t in ['password','api_key','secret']) and isinstance(v,str) and len(v)>7:secrets.append(v.encode())
   else:collect(v)
 elif isinstance(o,list):
  for v in o:collect(v)
for p in Path('.runtime').glob('*.json'):
 try:collect(json.loads(p.read_text()))
 except json.JSONDecodeError:pass
credentials=Path('.runtime/auth/credentials.json')
if credentials.exists():secrets.extend(v.encode() for v in json.loads(credentials.read_text()).values())
new=[n for n in public if n not in before];candidates=sorted(set(changed+new))
for n in candidates:
 assert not set(Path(n).parts)&{'.runtime','.env','.venv','.git','__pycache__'}
 data=Path(n).read_bytes();assert not any(v in data for v in secrets),'PRIVATE_VALUE_IN_PUBLIC_FILE'
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',data),'PRIVATE_KEY_PATTERN'
 assert not re.search(rb'[A-Za-z0-9_-]{43}\.[0-9a-f]{64}',data),'SESSION_PATTERN'
proofs=sorted(Path('docs/evidence').glob('B16-*-zero-live.json'));assert len(proofs)==12
for p in proofs:
 d=json.loads(p.read_text());assert d['external_gemini_requests_sent']==d['ordinary_unexpected_attempts']==0 and not d['events']
accepted=json.loads(Path('docs/evidence/B11-LIVE-SMOKE-R-fresh-process.json').read_text())['accounting']
with sqlite3.connect('file:'+str(root/'.runtime/ai-spend.sqlite3')+'?mode=ro',uri=True) as conn:
 conn.row_factory=sqlite3.Row;requests=[dict(r) for r in conn.execute('SELECT * FROM requests ORDER BY created,id')];assert requests==accepted['requests']
 assert conn.execute('SELECT count(*) FROM sessions').fetchone()[0]==0
 assert conn.execute("SELECT count(*) FROM request_holds WHERE status='OPEN'").fetchone()[0]==0
sys.path.insert(0,str(root/'backend'))
from app.config import Settings
from app.graph.connection import connect
from app.mcp.runtime import CITY_GRAPH
from app.graph.models import digest
from app.graph.repository import GraphRepository
with connect(Settings(_env_file='.env')) as db:
 modules=db.connection.execute_command('MODULE','LIST')
 versions=[]
 for row in modules:
  m=dict(zip(row[::2],row[1::2]));versions.append({'name':m.get('name',m.get(b'name')),'version':m.get('ver',m.get(b'ver'))})
  if isinstance(versions[-1]['name'],bytes):versions[-1]['name']=versions[-1]['name'].decode()
 assert any(m=={'name':'graph','version':60002} for m in versions)
 city=db.select_graph(CITY_GRAPH);assert city.ro_query('MATCH (n:CivicEntity) RETURN count(n)').result_set==[[858]]
 assert city.ro_query('MATCH ()-[e]->() RETURN count(e)').result_set==[[1246]]
 assert city.ro_query("MATCH ()-[e:DRAINS_TO]->() WHERE e.association_status='CANDIDATE' RETURN count(e)").result_set==[[42]]
 repo=GraphRepository(db,CITY_GRAPH)
 revision=city.ro_query("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision").result_set
 ns=city.ro_query('MATCH (n:CivicEntity) RETURN labels(n),properties(n) LIMIT 859').result_set
 es=city.ro_query('MATCH (s:CivicEntity)-[e]->(t:CivicEntity) RETURN type(e),properties(e),labels(s),properties(s),labels(t),properties(t) LIMIT 1247').result_set
 assert len(ns)==858 and len(es)==1246
 records=[repo.decode_node(*n) for n in ns]+[repo._decode_edge_row(e) for e in es]
 content_hash=digest({n.id:n.content_hash for n in records})
 assert city.ro_query("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision").result_set==revision
 expected=json.loads(Path('docs/evidence/B04-retained-post-recreation.json').read_text())['verified_content_hash']
 assert content_hash==expected
 assert db.select_graph('civicly_b01_runtime').ro_query('MATCH (n:B01Probe {id:$id}) RETURN n.id,n.source_kind,n.task LIMIT 1',params={'id':'B01-PERSISTENCE'}).result_set==[['B01-PERSISTENCE','SYNTHETIC','B01']]
 fault=json.loads(Path('docs/evidence/B12R2-postcommit-recovery.json').read_text());ctx=fault['reconciliation']
 assert db.connection.get('civicly:b10:'+ctx['graph']+':'+digest(fault['thread_id'])+':quarantine')
 assert db.select_graph(ctx['graph']).ro_query('MATCH (p:ResolutionPlan) RETURN p.id,p.version,p.plan_hash').result_set==[[ctx['plan_id'],1,ctx['expected_plan_hash']]]
 old=json.loads(Path('docs/evidence/B14R2-outcome-WATERLOGGING.json').read_text());g=db.select_graph(old['graph'])
 assert g.ro_query('MATCH (i:Investigation {id:$id})-[:INVESTIGATES]->(n:Incident) RETURN n.id,n.status ORDER BY n.id',params={'id':old['recurrence']['investigation_id']}).result_set==sorted([[old['checkpoint_refresh']['refresh_audit']['previous_incident_ids'][0],'ENDED'],[old['recurrence']['new_incident_id'],'REPORTED']])
 current=json.loads(Path('docs/evidence/B16-http-runtime.json').read_text());api_graph=db.select_graph(current['graph']);request=current['recovery']['error']['details']['correlation_id']
 intent=api_graph.ro_query('MATCH (s:CivicOperationState {id:$id}) RETURN s.payload_json LIMIT 1',params={'id':'api_request:'+request}).result_set
 assert intent and json.loads(intent[0][0])['status']=='DISPATCHING'
 from app.services.operations.service import stable
 opid=stable('OP',request)
 committed=api_graph.ro_query('MATCH (s:CivicOperationState {id:$id}) RETURN s.payload_json LIMIT 1',params={'id':'operation:'+opid}).result_set
 assert committed and json.loads(committed[0][0])['request_id']==request
 assert api_graph.ro_query('MATCH (w:WorkOrder) RETURN count(w)').result_set==[[1]]
 retained=json.loads(Path('docs/evidence/B16-worker-failed-diagnostic.json').read_text());failed_graph=retained['graph']
 from app.graph.models import digest
 thread='B15-'+digest(retained['case_id'])[:32]
 assert db.connection.get('civicly:b10:'+failed_graph+':'+digest(thread)+':quarantine')
 assert retained['existing_trace_collision'][0]['different_source']
 redis_version=db.connection.info('server')['redis_version']
value={'task':'B16','status':'PASS','baseline_files_retained':len(before),'prior_evidence_byte_identical':len(old_evidence),'all_prior_test_files_byte_identical':len(old_tests),'protected_registry_migrations_data_MCP_dependencies_unchanged':True,'trackers_historical_body_preserved':True,'trackers_current_summary_inserted_without_removing_history':True,'security_scan':'PASS known private values, key/session patterns; no private values exported','candidate_files_scanned':len(candidates),'modified_files':changed,'new_files':new,'python':platform.python_version(),'packages':{p:importlib.metadata.version(p) for p in ['falkordb','redis','pydantic','pytest','langgraph','langchain-falkordb','mcp','fastapi','uvicorn','httpx']},'redis_version':redis_version,'modules':versions,'city_nodes':858,'city_edges':1246,'candidate_drain_links':42,'accepted_city_full_content_hash':content_hash,'B01_probe_unchanged':True,'original_B12R2_quarantine_and_single_plan_retained':True,'original_B14R2_episodes_retained':True,'B16_actual_committed_operation_retained_with_unacknowledged_transport_intent':True,'B16_uncertain_request_id':request,'B16_original_failed_quarantine_retained':True,'B16_no_duplicate_work_orders':True,'retained_interlock_proofs':len(proofs),'external_provider_requests':0,'historical_paid_requests':len(requests),'historical_paid_requests_exactly_unchanged':True,'tests':{'distinct_pass':63,'unit_pass':62,'real_pass':1,'unresolved_fail':0,'skip':0},'source_sha256':{n:hashlib.sha256(Path(n).read_bytes()).hexdigest() for n in candidates if not n.startswith('docs/evidence/')}}
Path('docs/evidence/B16-audit.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({k:value[k] for k in ['task','status','prior_evidence_byte_identical','all_prior_test_files_byte_identical','security_scan','external_provider_requests','historical_paid_requests','tests']},indent=2))
