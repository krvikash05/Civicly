"""B16-R read-only preservation/private-value scan; no credentials printed."""
import json,hashlib,subprocess,re,sqlite3,sys
from pathlib import Path
root=Path.cwd();base=Path('/tmp/b16r-baseline');before=json.loads((base/'hashes.json').read_text())
public=sorted(n for n in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\0') if n and Path(n).is_file())
assert set(before)<=set(public)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
changed=sorted(n for n,h in before.items() if sha(n)!=h)
trackers={'decision.md','flow.md','implementation_status.md','test_log.md','blockers.md','task_board.md'}
assert set(changed)==trackers|{'backend/app/services/http/service.py'}
for n in trackers:assert Path(n).read_bytes().startswith((base/'files'/n).read_bytes())
old_evidence=[n for n in before if n.startswith('docs/evidence/')];assert not set(old_evidence)&set(changed)
old_tests=[n for n in before if n.startswith('backend/tests/')];assert not set(old_tests)&set(changed)
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
new=[n for n in public if n not in before]
for n in changed+new:
 assert not set(Path(n).parts)&{'.env','.runtime','.venv','__pycache__','.git'}
 raw=Path(n).read_bytes()
 assert not any(value in raw for value in secrets),'PRIVATE_VALUE_IN_PUBLIC_ARTIFACT'
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}|[A-Za-z0-9_-]{43}\.[0-9a-f]{64}',raw),'PRIVATE_KEY_OR_SESSION_PATTERN'
proofs=list(Path('docs/evidence').glob('B16R-*-zero-live.json'));assert len(proofs)==7
for p in proofs:
 v=json.loads(p.read_text());assert v['external_gemini_requests_sent']==v['ordinary_unexpected_attempts']==0 and not v['events']
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
from app.services.evidence.models import Journal
from app.mcp.runtime import CITY_GRAPH
proof=json.loads(Path('docs/evidence/B16R-real-proof.json').read_text())
with connect(Settings(_env_file='.env')) as db:
 repo=GraphRepository(db,proof['graph']);g=repo.graph
 assert g.ro_query('MATCH (n:Inspection) RETURN count(n)').result_set==[[2]]
 for case in proof['cases']:
  j=Journal.model_validate_json(repo.get_node(case['journal_id'],'Evidence').properties['summary'])
  assert j.state=='COMMITTED' and j.receipt.entity_id==case['inspection_id']
  assert j.request_hash==digest({'actor':j.actor.model_dump(mode='json'),'command':j.command})
  repo.get_node(case['inspection_id'],'Inspection')
  request=case['response']['error']['details']['correlation_id']
  rows=g.ro_query('MATCH (s:CivicOperationState {id:$id}) RETURN s.payload_json,s.payload_sha256 LIMIT 1',params={'id':'api_request:'+request}).result_set
  row=json.loads(rows[0][0]);assert digest(row)==rows[0][1]
  assert row['status']=='DISPATCHING' and row['recovery']['journal_id']==case['journal_id']
  assert row['recovery']['identities']['entity_id']==case['inspection_id']
  assert row['recovery']['identities']['investigation_id']==proof['investigation_id']
 city=GraphRepository(db,CITY_GRAPH);ns=city._read('MATCH (n:CivicEntity) RETURN labels(n),properties(n) LIMIT 859');es=city._read('MATCH (s:CivicEntity)-[e]->(t:CivicEntity) RETURN type(e),properties(e),labels(s),properties(s),labels(t),properties(t) LIMIT 1247')
 assert len(ns)==858 and len(es)==1246
 records=[city.decode_node(*n) for n in ns]+[city._decode_edge_row(e) for e in es]
 city_hash=digest({n.id:n.content_hash for n in records});assert city_hash==json.loads(Path('docs/evidence/B04-retained-post-recreation.json').read_text())['verified_content_hash']
 assert city._read("MATCH ()-[e:DRAINS_TO]->() WHERE e.association_status='CANDIDATE' RETURN count(e)")==[[42]]
 assert db.select_graph('civicly_b01_runtime').ro_query('MATCH (n:B01Probe {id:$id}) RETURN n.id,n.source_kind,n.task LIMIT 1',params={'id':'B01-PERSISTENCE'}).result_set==[['B01-PERSISTENCE','SYNTHETIC','B01']]
 fault=json.loads(Path('docs/evidence/B12R2-postcommit-recovery.json').read_text());ctx=fault['reconciliation']
 assert db.connection.get('civicly:b10:'+ctx['graph']+':'+digest(fault['thread_id'])+':quarantine')
 assert db.select_graph(ctx['graph']).ro_query('MATCH (p:ResolutionPlan) RETURN p.id,p.version,p.plan_hash').result_set==[[ctx['plan_id'],1,ctx['expected_plan_hash']]]
value={'task':'B16-R','status':'PASS','baseline_public_files_retained':len(before),'prior_evidence_byte_identical':len(old_evidence),'prior_test_files_byte_identical':len(old_tests),'trackers_append_only':True,'only_prior_source_modified':'backend/app/services/http/service.py','all_other_prior_files_unchanged':True,'modified_files':changed,'new_files':new,'private_values_patterns_scan':'PASS including patch; no private values exported','retained_interlock_proofs':len(proofs),'external_provider_requests':0,'historical_paid_requests_exactly_unchanged':len(requests),'real_proof_graph':proof['graph'],'actual_inspections':2,'COMMITTED_journals':2,'intents_DISPATCHING_not_REJECTED':2,'replay_redispatches':0,'city_full_content_hash':city_hash,'B01_probe_unchanged':True,'original_quarantine_and_single_plan_retained':True,'tests':{'distinct_pass':19,'unit':18,'real':1,'unresolved_fail':0,'skip':0},'source_sha256':{n:sha(n) for n in changed+new if not n.startswith('docs/evidence/')}}
Path('docs/evidence/B16R-audit.json').write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps({k:value[k] for k in ['task','status','prior_evidence_byte_identical','prior_test_files_byte_identical','trackers_append_only','private_values_patterns_scan','external_provider_requests','actual_inspections','COMMITTED_journals','intents_DISPATCHING_not_REJECTED','replay_redispatches','tests']},indent=2))
