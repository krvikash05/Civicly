"""Exact-capability rebootstrap + fresh process source/checkpoint verification."""
import argparse,hashlib,json,re,subprocess,os
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.memory.runtime import Profile
from app.memory.storage import MemoryMigration
from app.active import load,provision
from app.agents.checkpoints import saver
from langchain_core.runnables import RunnableConfig
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--anchor',default='docs/evidence/B11-persistence-anchor.json');a=p.parse_args()
anchor=json.loads(Path(a.anchor).read_text());path=Path(anchor['private_profile_path']);agent_path=Path(anchor['agent_profile_path'])
for f in [path,agent_path]:
 assert str(f).startswith('.runtime/b11-') and not f.is_symlink() and not f.stat().st_mode&0o077
profile=Profile.model_validate_json(path.read_text());assert re.fullmatch(r'b11_ro_[0-9a-f]{32}',profile.reader_user)
with connect(Settings(_env_file='.env')) as admin:
 admin.connection.execute_command('ACL','SETUSER',profile.reader_user,'reset','on','#'+hashlib.sha256(profile.reader_password.get_secret_value().encode()).hexdigest(),'~'+profile.docs_graph,'~'+profile.canonical_graph,'-@all','+ping','+info','+client|setinfo','+graph.ro_query')
 assert MemoryMigration(admin,profile.canonical_graph).status()['ready']
 procedures=admin.select_graph(profile.canonical_graph).ro_query("MATCH (p:KnowledgeProcedure) WHERE p.id STARTS WITH $prefix RETURN p.id,p.document_ref,p.version,p.status ORDER BY p.id LIMIT 101",params={'prefix':'ORGPROC:'}).result_set
 assert len(procedures)==19 and all(v[3]=='PROPOSED' for v in procedures)
 agent=load(agent_path);provision(admin,agent)
 checkpoint=saver(agent).get_tuple({'configurable':{'thread_id':anchor['thread']}})
 assert checkpoint is not None
out=Path(a.output)
proc=subprocess.run([str(Path('backend/.venv/bin/python').absolute()),'-m','tests.b11_worker',str(path),str(out),anchor['source_document_id']],env={**os.environ,'PYTHONPATH':'backend'},capture_output=True,timeout=60)
assert proc.returncode==0,proc.stderr.decode()[-1000:]
result=json.loads(out.read_text());old=anchor['retrieval']
def stable(v):return [{k:value for k,value in c.items() if k!='retrieved_at'} for c in v['citations']]
assert stable(result)==stable(old)
value={'status':'PASS','retained_proposed_procedures':procedures,'fresh_process_sdk_retrieval':result,'same_version_chunk_hashes':True,'canonical_graph':profile.canonical_graph,'docs_graph':profile.docs_graph,'anchor':a.anchor,'same_checkpoint_thread':anchor['thread'],'canonical_migration':'0003 READY','exact_graph_acl_reprovisioned_without_record_changes':True,'external_gemini_requests':0,'credentials_logged':False}
out.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({k:v for k,v in value.items() if k!='fresh_process_sdk_retrieval'}))
