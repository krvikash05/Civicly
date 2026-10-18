from pathlib import Path
import subprocess,json,hashlib,re,sqlite3,sys,ast,collections
root=Path.cwd();base=Path('/tmp/b14r-baseline');before=json.loads((base/'hashes.json').read_text())
public=sorted(n for n in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\0') if n and Path(n).is_file())
assert set(before)<=set(public)
changed=sorted(n for n,h in before.items() if hashlib.sha256(Path(n).read_bytes()).hexdigest()!=h)
old_evidence=[n for n in before if n.startswith('docs/evidence/')];assert not set(changed)&set(old_evidence)
assert hashlib.sha256(Path('backend/app/services/operations/verification_v1.py').read_bytes()).hexdigest()==before['backend/app/services/operations/verification.py']
assert not any(n in changed for n in before if n.startswith(('backend/app/graph/migrations/','contracts/schema_registry','data/','backend/app/mcp/')) or n.endswith(('uv.lock','pyproject.toml','package-lock.json','compose.yaml')))
oldtests=[n for n in before if n.startswith('backend/tests/') and n.endswith('.py')]
assert set(oldtests)&set(changed)=={'backend/tests/unit/test_execution_policy.py','backend/tests/integration/test_execution_runtime.py'}
for name in set(oldtests)&set(changed):
 prior=collections.Counter(ast.unparse(n.test).replace("'B14-1'",'VERSION') for n in ast.walk(ast.parse((base/'files'/name).read_text())) if isinstance(n,ast.Assert))
 current=collections.Counter(ast.unparse(n.test) for n in ast.walk(ast.parse(Path(name).read_text())) if isinstance(n,ast.Assert))
 assert not prior-current,name
old_contract=json.loads((base/'files/contracts/operations.json').read_text())['verification']
assert json.loads(Path('contracts/operations.json').read_text())['historical_verification']['B14-1']==old_contract
secrets=[]
for line in Path('.env').read_text().splitlines():
 if '=' not in line:continue
 k,v=line.split('=',1);v=v.strip(' \"\'')
 if any(t in k.upper() for t in ['KEY','TOKEN','SECRET','PASSWORD']) and len(v)>7:secrets.append(v.encode())
def collect(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if any(t in k.lower() for t in ['password','secret','key','token']) and isinstance(v,str) and len(v)>7:secrets.append(v.encode())
   else:collect(v)
 elif isinstance(o,list):
  for v in o:collect(v)
for p in Path('.runtime').glob('*.json'):collect(json.loads(p.read_text()))
secrets.extend(v.encode() for v in json.loads(Path('.runtime/auth/credentials.json').read_text()).values())
for name in public:
 assert not set(Path(name).parts)&{'.env','.runtime','.git','.venv','__pycache__','node_modules','review_packages'}
 data=Path(name).read_bytes();assert not any(v in data for v in secrets),'Private value in '+name
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',data),name
 if name.startswith('docs/evidence/B14R-'):assert not re.search(rb'[A-Za-z0-9_-]{43}\.[0-9a-f]{64}',data),name
proofs=sorted(Path('docs/evidence').glob('B14R-*-zero-live.json'));assert len(proofs)==5
for p in proofs:
 d=json.loads(p.read_text());assert d['external_gemini_requests_sent']==d['ordinary_unexpected_attempts']==0 and not d['events']
accepted=json.loads(Path('docs/evidence/B11-LIVE-SMOKE-R-fresh-process.json').read_text())['accounting']
with sqlite3.connect('file:'+str(root/'.runtime/ai-spend.sqlite3')+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row;requests=[dict(r) for r in db.execute('SELECT * FROM requests ORDER BY created,id')];assert requests==accepted['requests']
 assert db.execute('SELECT count(*) FROM sessions').fetchone()[0]==0
 assert db.execute("SELECT count(*) FROM request_holds WHERE status='OPEN'").fetchone()[0]==0
sys.path.insert(0,str(root/'backend'))
from app.config import Settings
from app.graph.connection import connect
from app.mcp.runtime import CITY_GRAPH
from app.graph.models import digest
water=json.loads(Path('docs/evidence/B14R-outcome-WATERLOGGING.json').read_text());recur=water['recurrence']
waste=json.loads(Path('docs/evidence/B14R-waste.json').read_text())
with connect(Settings(_env_file='.env')) as db:
 city=db.select_graph(CITY_GRAPH);assert city.ro_query('MATCH (n:CivicEntity) RETURN count(n)').result_set==[[858]]
 assert city.ro_query('MATCH ()-[e]->() RETURN count(e)').result_set==[[1246]]
 assert city.ro_query("MATCH ()-[e:DRAINS_TO]->() WHERE e.association_status='CANDIDATE' RETURN count(e)").result_set==[[42]]
 old=json.loads(Path('docs/evidence/B14-outcome-WATERLOGGING.json').read_text());g=db.select_graph(old['graph'])
 raw=g.ro_query('MATCH (s:CivicOperationState {id:$id}) RETURN s.payload_json',params={'id':'outcome:'+old['verified']['id']}).result_set[0][0]
 assert json.loads(raw)==old['verified'] and json.loads(raw)['policy_version']=='B14-1'
 g=db.select_graph(water['graph']);links=g.ro_query('MATCH (i:Investigation {id:$id})-[e:INVESTIGATES]->(n:Incident) RETURN i.status,n.id,n.status,e.id,e.source_evidence_id,e.valid_from ORDER BY n.id',params={'id':recur['investigation_id']}).result_set
 assert len(links)==2 and {row[2] for row in links}=={'ENDED','REPORTED'}
 assert any(row[1]==recur['new_incident_id'] and row[3]==recur['investigates_relationship_id'] and row[4] and row[5] for row in links)
 g=db.select_graph(waste['graph'])
 for label in ['premature','verified']:
  value=waste[label];row=g.ro_query('MATCH (s:CivicOperationState {id:$id}) RETURN s.payload_json',params={'id':'outcome:'+value['id']}).result_set
  assert json.loads(row[0][0])==value and value['policy_version']=='B14-2'
 fault=json.loads(Path('docs/evidence/B12R2-postcommit-recovery.json').read_text());ctx=fault['reconciliation']
 assert db.connection.get('civicly:b10:'+ctx['graph']+':'+digest(fault['thread_id'])+':quarantine')
 assert db.select_graph(ctx['graph']).ro_query('MATCH (p:ResolutionPlan) RETURN p.id,p.version,p.plan_hash').result_set==[[ctx['plan_id'],1,ctx['expected_plan_hash']]]
result={'task':'B14-R','status':'PASS','baseline_public_files_retained':len(before),'earlier_evidence_files_byte_identical':len(old_evidence),'old_python_test_files_retained':len(oldtests),'old_assertions_preserved':'PASS; only current VERSION expectation updated, valid waste fixture uses real24hour interval','legacy_policy_bytes_equal_pre_B14R':True,'historical_contract_equal':True,'registry_migrations_dataset_MCP_pins_unchanged':True,'known_private_values_key_patterns_ephemeral_sessions_scan':'PASS','provider_interlock_invocations':5,'external_gemini_countTokens_requests':0,'unexpected_attempts':0,'historical_paid_requests_unchanged':len(requests),'accepted_city_nodes':858,'accepted_city_edges':1246,'candidate_drain_links':42,'original_quarantine_retained':True,'original_B14_verified_outcome_equal':True,'corrected_investigation_scope':links,'new_waste_premature_and_verified_outcomes_retained':True,'checkpoint_refresh':water['checkpoint_refresh']}
Path('docs/evidence/B14R-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
