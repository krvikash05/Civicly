"""B20 read-only retention/private-artifact audit. Never emits credential values."""
import hashlib,importlib.metadata,json,re,sqlite3,subprocess,sys
from pathlib import Path
root=Path.cwd();base=Path('/tmp/b20-baseline');before=json.loads((base/'hashes.json').read_text())
public=sorted(n for n in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\0') if n and Path(n).is_file())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert set(before)<=set(public)
changed=sorted(n for n,h in before.items() if sha(n)!=h);new=sorted(set(public)-set(before))
trackers={'decision.md','flow.md','implementation_status.md','test_log.md','blockers.md','task_board.md'}
assert set(changed)==trackers,(set(changed)^trackers)
for n in trackers:assert Path(n).read_bytes().startswith((base/'files'/n).read_bytes())
old_evidence=[n for n in before if n.startswith('docs/evidence/')];old_tests=[n for n in before if n.startswith('backend/tests/')]
assert not (set(old_evidence)|set(old_tests))&set(changed)
assert {n for n in new if not n.startswith('docs/evidence/B20-')}=={'backend/tests/b20_fixtures.py','backend/tests/integration/test_scenario_behavior.py','backend/tests/unit/test_scenario_behavior.py'}
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
guards=list(Path('docs/evidence').glob('B20-*-zero-live.json'))
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
value={'task':'B20','acceptance':'PARTIAL_BLOCKED','baseline_public_files_retained':len(before),'prior_evidence_byte_identical':len(old_evidence),'prior_test_files_unchanged':len(old_tests),'all_six_trackers_append_only':True,'changed':changed,'new':new,'all_production_data_contracts_migrations_unchanged':True,'private_value_scan':'PASS including patch','provider_guard_reports':len(guards),'external_provider_requests':0,'paid_requests_unchanged':len(requests),'retained_scenario_runs':runs,'B01_probe_unchanged':True,'B04_city_hash':city_hash,'candidate_drains':42,'B12R2_quarantine_single_plan_retained':True,'B19_quarantines_retained':True,'redis_version':server,'module_versions':module_versions,'versions':{n:importlib.metadata.version(n) for n in ['falkordb','mcp','langgraph','langchain-falkordb','fastapi','pydantic']}}
Path('docs/evidence/B20-audit.json').write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps(value,indent=2))
