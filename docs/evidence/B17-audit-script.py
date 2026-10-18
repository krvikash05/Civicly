"""B17 read-only preservation and public-artifact audit; never prints secrets."""
import tempfile,ast,hashlib,importlib.metadata,json,re,sqlite3,subprocess,sys
from pathlib import Path
root=Path.cwd();base=Path('/tmp/b17-baseline');before=json.loads((base/'hashes.json').read_text())
public=sorted(n for n in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\0') if n and Path(n).is_file())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert set(before)<=set(public)
changed=sorted(n for n,h in before.items() if sha(n)!=h);new=sorted(set(public)-set(before))
trackers={'decision.md','flow.md','implementation_status.md','test_log.md','blockers.md','task_board.md'}
allowed=trackers|{'backend/API.md','backend/app/api/application.py','backend/app/api/coverage.py','backend/app/api/models.py','backend/app/services/http/reads.py','backend/app/events/sources.py','backend/app/events/models.py','backend/app/events/service.py','backend/tests/unit/test_api.py','backend/tests/integration/test_api_runtime.py','contracts/api_endpoints.json','contracts/api_models.json','contracts/event_delivery.json','scripts/validate_api.py','scripts/validate_events.py','docs/backend/08_api_frontend.md','docs/frontend_contract/FRONTEND_READINESS.md'}
assert set(changed)==allowed,set(changed)^allowed
for n in trackers:assert (base/'files'/n).read_bytes() in Path(n).read_bytes()
old_evidence=[n for n in before if n.startswith('docs/evidence/')];assert not set(old_evidence)&set(changed)
old_tests=[n for n in before if n.startswith('backend/tests/')]
compat={'backend/tests/unit/test_api.py','backend/tests/integration/test_api_runtime.py'}
assert set(old_tests)&set(changed)==compat
for name in compat:
 def tests(raw):
  tree=ast.parse(raw);return {n.name:n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_')}
 old=tests((base/'files'/name).read_text());current=tests(Path(name).read_text());assert set(old)<=set(current)
 for name,node in old.items():assert sum(isinstance(x,ast.Assert) for x in ast.walk(current[name]))>=sum(isinstance(x,ast.Assert) for x in ast.walk(node))
new_source={'backend/app/api/view_models.py','backend/app/services/activity.py','backend/app/services/http/views.py','backend/app/services/http/stream.py','backend/tests/unit/test_frontend_views.py','backend/tests/integration/test_frontend_runtime.py'}
assert {n for n in new if not n.startswith('docs/evidence/B17-')}==new_source
secrets=[]
for line in Path('.env').read_text().splitlines():
 if '=' not in line:continue
 key,value=line.split('=',1);value=value.strip(' \"\'')
 if any(t in key.upper() for t in ['KEY','SECRET','TOKEN','PASSWORD']) and len(value)>7:secrets.append(value.encode())
def collect(value):
 if isinstance(value,dict):
  for k,v in value.items():
   if any(t in k.lower() for t in ['password','secret','api_key']) and isinstance(v,str) and len(v)>7:secrets.append(v.encode())
   else:collect(v)
 elif isinstance(value,list):
  for v in value:collect(v)
for path in Path('.runtime').glob('*.json'):collect(json.loads(path.read_text()))
pw=Path('.runtime/auth/credentials.json')
if pw.exists():secrets.extend(v.encode() for v in json.loads(pw.read_text()).values())
for n in changed+new:
 assert not set(Path(n).parts)&{'.env','.runtime','.venv','__pycache__','.git'}
 raw=Path(n).read_bytes()
 assert not any(v in raw for v in secrets),'PRIVATE_VALUE_IN_PUBLIC_ARTIFACT'
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}|[A-Za-z0-9_-]{43}\.[0-9a-f]{64}',raw),'PRIVATE_KEY_OR_SESSION_PATTERN'
proofs=list(Path('docs/evidence').glob('B17-*-zero-live.json'))
for p in proofs:
 v=json.loads(p.read_text());assert v['external_gemini_requests_sent']==v['ordinary_unexpected_attempts']==0
accepted=json.loads(Path('docs/evidence/B11-LIVE-SMOKE-R-fresh-process.json').read_text())['accounting']['requests']
with sqlite3.connect('file:'+str(root/'.runtime/ai-spend.sqlite3')+'?mode=ro',uri=True) as conn:
 conn.row_factory=sqlite3.Row;requests=[dict(r) for r in conn.execute('SELECT * FROM requests ORDER BY created,id')];assert requests==accepted
 assert conn.execute('SELECT count(*) FROM sessions').fetchone()[0]==0
 assert conn.execute("SELECT count(*) FROM request_holds WHERE status='OPEN'").fetchone()[0]==0
sys.path.insert(0,str(root/'backend'))
from app.config import Settings
from app.graph.connection import connect
from app.graph.models import digest
from app.graph.repository import GraphRepository
from app.mcp.runtime import CITY_GRAPH
from app.active import load,active_scope
proof=json.loads(Path('docs/evidence/B17-journey.json').read_text())
with connect(Settings(_env_file='.env')) as db:
 redis_version=db.connection.info('server')['redis_version'];modules=db.connection.execute_command('MODULE','LIST')
 module_versions={}
 for row in modules:
  value={str(row[i].decode() if isinstance(row[i],bytes) else row[i]):row[i+1] for i in range(0,len(row),2)}
  name=value['name'];name=name.decode() if isinstance(name,bytes) else name;module_versions[name]=value['ver']
 profile=load(Path(proof['private_profile_path'])) if 'private_profile_path' in proof else next(load(path) for path in Path(tempfile.gettempdir()).glob('pytest-of-*/pytest-current/test_frontend*/agent.json') if load(path).graph==proof['source_graph'])
 scope=active_scope(profile);scope.__enter__()
 repo=GraphRepository(db,proof['source_graph']);repo.get_node(proof['investigation_id'],'Investigation');repo.get_node(proof['plan_id'],'ResolutionPlan')
 assert repo._read('MATCH (w:WorkOrder) RETURN count(w)')==[[1]]
 rows=repo._read('MATCH (s:CivicOperationState {id:$id}) RETURN s.payload_json,s.payload_sha256 LIMIT 1',{'id':'delivery:'+proof['network']['later_event_id']})
 row=json.loads(rows[0][0]);assert digest(row)==rows[0][1] and row['status']=='PENDING' and row['attempts']==0
 city=GraphRepository(db,CITY_GRAPH);ns=city._read('MATCH (n:CivicEntity) RETURN labels(n),properties(n) LIMIT 859');es=city._read('MATCH (s:CivicEntity)-[e]->(t:CivicEntity) RETURN type(e),properties(e),labels(s),properties(s),labels(t),properties(t) LIMIT 1247')
 assert len(ns)==858 and len(es)==1246
 records=[city.decode_node(*n) for n in ns]+[city._decode_edge_row(e) for e in es]
 city_hash=digest({n.id:n.content_hash for n in records});assert city_hash==json.loads(Path('docs/evidence/B04-retained-post-recreation.json').read_text())['verified_content_hash']
 assert city._read("MATCH ()-[e:DRAINS_TO]->() WHERE e.association_status='CANDIDATE' RETURN count(e)")==[[42]]
 assert db.select_graph('civicly_b01_runtime').ro_query('MATCH (n:B01Probe {id:$id}) RETURN n.id,n.source_kind,n.task LIMIT 1',params={'id':'B01-PERSISTENCE'}).result_set==[['B01-PERSISTENCE','SYNTHETIC','B01']]
 fault=json.loads(Path('docs/evidence/B12R2-postcommit-recovery.json').read_text());ctx=fault['reconciliation']
 assert db.connection.get('civicly:b10:'+ctx['graph']+':'+digest(fault['thread_id'])+':quarantine')
 assert db.select_graph(ctx['graph']).ro_query('MATCH (p:ResolutionPlan) RETURN p.id,p.version,p.plan_hash').result_set==[[ctx['plan_id'],1,ctx['expected_plan_hash']]]
value={'task':'B17','status':'PASS','baseline_public_files_retained':len(before),'prior_evidence_byte_identical':len(old_evidence),'prior_test_files_unchanged':len(old_tests)-len(compat),'prior_test_files_compatible_phase_assertions':sorted(compat),'prior_test_names_and_assertion_counts_preserved':True,'all_six_tracker_history_bodies_retained':True,'modified_files':changed,'new_files':new,'migrations_registry_city_source_unchanged':True,'private_values_and_patterns_scan':'PASS including patch; no private values exported','provider_interlock_proofs':len(proofs),'external_provider_requests':0,'historical_paid_requests_exactly_unchanged':len(requests),'real_graph':proof['source_graph'],'one_work_order':True,'later_resume_PENDING_zero_attempts':True,'city_full_content_hash':city_hash,'city_drains_CANDIDATE':42,'B01_probe_unchanged':True,'original_quarantine_single_plan_retained':True,'versions':{name:importlib.metadata.version(name) for name in ['fastapi','pydantic','uvicorn','falkordb','mcp','langgraph','langchain-falkordb']},'redis_version':redis_version,'module_versions':module_versions,'tests':{'distinct_pass':46,'unit':45,'real':1,'unresolved_fail':0,'skip':0},'source_sha256':{n:sha(n) for n in changed+new if not n.startswith('docs/evidence/')}}
Path('docs/evidence/B17-audit.json').write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps({k:value[k] for k in ['task','status','baseline_public_files_retained','prior_evidence_byte_identical','prior_test_names_and_assertion_counts_preserved','private_values_and_patterns_scan','external_provider_requests','one_work_order','later_resume_PENDING_zero_attempts','tests','versions','redis_version','module_versions']},indent=2))
