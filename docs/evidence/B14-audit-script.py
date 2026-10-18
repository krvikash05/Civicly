from pathlib import Path
import subprocess,hashlib,json,difflib,re,sqlite3,sys,platform,importlib.metadata
root=Path.cwd();base=Path('/tmp/b14-baseline');hashes=json.loads((base/'hashes.json').read_text())
public=sorted(n for n in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\0') if n and Path(n).is_file())
assert set(hashes)<=set(public),'Earlier public file missing'
changed=sorted(n for n,h in hashes.items() if hashlib.sha256(Path(n).read_bytes()).hexdigest()!=h)
new=sorted(set(public)-set(hashes));sources=[n for n in new if not n.startswith('docs/evidence/')]
prior_evidence=[n for n in hashes if n.startswith('docs/evidence/')]
assert set(prior_evidence)&set(changed)=={'docs/evidence/B13-FILES.md'}
assert all(n in sources or n.startswith('docs/evidence/B14-') for n in new)
assert not any(n in changed for n in hashes if n.startswith(('backend/app/graph/migrations/','contracts/schema_registry','data/','backend/app/agents/','backend/app/mcp/')))
oldtests=[n for n in hashes if n.startswith('backend/tests/') and n.endswith('.py')]
assert set(oldtests)&set(changed)=={'backend/tests/unit/test_operations.py'}
old=(base/'files/backend/tests/unit/test_operations.py').read_text()
assert Path('backend/tests/unit/test_operations.py').read_text()==old.replace("('OP-ANALYST',{'draft','submit','read'})","('OP-ANALYST',{'draft','submit','read','inspect','evaluate','recur'})").replace("('OP-DRAIN-LEAD',{'read','update'})","('OP-DRAIN-LEAD',{'read','update','progress','inspect'})").replace("reason='B14 not authorized'", "reason='B13 Update remains closed; B14 uses separate Progress command'")
values=[]
for line in Path('.env').read_text().splitlines():
 if '=' not in line:continue
 k,v=line.split('=',1);v=v.strip(' \"\'')
 if any(t in k.upper() for t in ['KEY','TOKEN','SECRET','PASSWORD']) and len(v)>7:values.append(v.encode())
def private(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if any(t in k.lower() for t in ['password','secret','key','token']) and isinstance(v,str) and len(v)>7:values.append(v.encode())
   else:private(v)
 elif isinstance(o,list):
  for v in o:private(v)
for p in Path('.runtime').glob('*.json'):private(json.loads(p.read_text()))
values.extend(v.encode() for v in json.loads(Path('.runtime/auth/credentials.json').read_text()).values())
for n in public:
 assert not set(Path(n).parts)&{'.runtime','.env','.git','.venv','__pycache__','node_modules','review_packages'}
 data=Path(n).read_bytes();assert not any(v in data for v in values),'Private value found in '+n
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',data),n
 if n.startswith('docs/evidence/B14-'):assert not re.search(rb'[A-Za-z0-9_-]{43}\.[0-9a-f]{64}',data),'Ephemeral session in '+n
proofs=sorted(Path('docs/evidence').glob('B14-*-zero-live.json'));assert len(proofs)==12
for p in proofs:
 d=json.loads(p.read_text());assert d['external_gemini_requests_sent']==d['ordinary_unexpected_attempts']==0 and not d['events']
accepted=json.loads(Path('docs/evidence/B11-LIVE-SMOKE-R-fresh-process.json').read_text())['accounting']
with sqlite3.connect('file:'+str(root/'.runtime/ai-spend.sqlite3')+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row;requests=[dict(r) for r in db.execute('SELECT * FROM requests ORDER BY created,id')]
 assert requests==accepted['requests'];exposure=db.execute('SELECT coalesce(sum(coalesce(charged,reserved)),0) FROM requests').fetchone()[0];assert exposure==5713500
 assert db.execute('SELECT count(*) FROM sessions').fetchone()[0]==0
 assert db.execute("SELECT count(*) FROM request_holds WHERE status='OPEN'").fetchone()[0]==0
sys.path.insert(0,str(root/'backend'))
from app.config import Settings
from app.graph.connection import connect
from app.mcp.runtime import CITY_GRAPH
from app.graph.models import digest
fault=json.loads(Path('docs/evidence/B12R2-postcommit-recovery.json').read_text());ctx=fault['reconciliation'];runtime=[]
with connect(Settings(_env_file='.env')) as db:
 city=db.select_graph(CITY_GRAPH);counts={'domain_nodes':city.ro_query('MATCH (n:CivicEntity) RETURN count(n)').result_set[0][0],'edges':city.ro_query('MATCH ()-[e]->() RETURN count(e)').result_set[0][0]};assert counts=={'domain_nodes':858,'edges':1246}
 assert city.ro_query("MATCH ()-[e:DRAINS_TO]->() WHERE e.association_status='CANDIDATE' RETURN count(e)").result_set==[[42]]
 g=db.select_graph(ctx['graph']);assert g.ro_query('MATCH (p:ResolutionPlan) RETURN p.id,p.version,p.plan_hash').result_set==[[ctx['plan_id'],1,ctx['expected_plan_hash']]]
 assert db.connection.get('civicly:b10:'+ctx['graph']+':'+digest(fault['thread_id'])+':quarantine')
 old=json.loads(Path('docs/evidence/B13-flow.json').read_text());g=db.select_graph(old['graph']);assert g.ro_query('MATCH (w:WorkOrder {id:$id}) RETURN w.status',params={'id':old['order']['id']}).result_set==[['ASSIGNED']]
 for issue in ['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']:
  proof=json.loads(Path('docs/evidence/B14-outcome-'+issue+'.json').read_text());g=db.select_graph(proof['graph']);v=proof['verified']
  assert g.ro_query('MATCH (o:InterventionOutcome {id:$id}) RETURN o.result,o.assessment_status',params={'id':v['id']}).result_set==[['MITIGATION_VERIFIED','RESOLUTION_VERIFIED']]
  assert g.ro_query('MATCH (p:ResolutionPlan {id:$id}) RETURN p.status',params={'id':proof['binding']['plan_id']}).result_set==[['COMPLETED']]
  runtime.append({'issue':issue,'graph':proof['graph'],'retained_verified_outcome':v['id'],'case_closed_then_reopened':issue=='WATERLOGGING'})
 modules=db.connection.execute_command('MODULE','LIST');versions={}
 for row in modules:
  d=dict(zip(row[::2],row[1::2]));name=d.get(b'name',d.get('name'));ver=d.get(b'ver',d.get('ver'));versions[name.decode() if isinstance(name,bytes) else name]=ver
 assert versions.get('graph')==60002,versions
out={'task':'B14','earlier_public_files_retained':len(hashes),'prior_evidence_files_unchanged':len(prior_evidence)-1,'documented_exception':'B13-FILES.md erroneous sentence only','prior_test_files_retained':len(oldtests),'only_prior_test_adjustment':'B13 expected allowlists extended for B14; no assertion removed','registry_migrations_sources_agents_mcp_unchanged':True,'secret_scan':'PASS; known runtime/.env/private-auth values, key patterns and ephemeral sessions excluded; initial pytest traceback sanitized','provider_interlock_invocations':len(proofs),'external_gemini_requests':0,'unexpected_provider_attempts':0,'live_ledger_requests_unchanged':len(requests),'known_exposure_nanodollars':exposure,'accepted_city':counts,'candidate_drain_links':42,'original_quarantine_retained':True,'retained_B13_order_unchanged':True,'runtime_proofs':runtime,'versions':{'python':platform.python_version(),'falkordb_module':versions.get('graph'),'falkordb_client':importlib.metadata.version('falkordb'),'mcp':importlib.metadata.version('mcp'),'pydantic':importlib.metadata.version('pydantic'),'graphrag-sdk':importlib.metadata.version('graphrag-sdk'),'langgraph':importlib.metadata.version('langgraph')}}
Path('docs/evidence/B14-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
