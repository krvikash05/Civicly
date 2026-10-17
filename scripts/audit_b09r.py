"""Audit B09-R scope and Git-candidate secrets without logging private values."""
import json
import hashlib
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE='688b893'
freeze=json.loads((ROOT/'docs/evidence/B09R-source-freeze.json').read_text())
for name,expected in freeze['files'].items():
 assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,'Tested source changed after freeze: '+name
NEW_SOURCE={'backend/app/services/evidence/classification.py','backend/app/services/evidence/relevance.py',
 'backend/tests/b09r_fixtures.py','backend/tests/integration/test_evidence_review.py',
 'backend/tests/unit/test_evidence_review_models.py','scripts/audit_b09r.py','scripts/verify_b09r.py'}
ALLOWED={'backend/app/services/evidence/models.py','backend/app/services/evidence/policies.py',
 'backend/app/services/evidence/reader.py','backend/app/services/evidence/service.py',
 'contracts/evidence_hypotheses.json','backend/EVIDENCE.md','decision.md','flow.md',
 'task_board.md','implementation_status.md','test_log.md','blockers.md'}
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')[:-1]
protected=0
for name in tracked:
 if name in ALLOWED:continue
 assert (ROOT/name).read_bytes()==subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT),'Accepted file changed: '+name
 protected+=1
secret_values=[]
for line in (ROOT/'.env').read_text().splitlines():
 if '=' not in line:continue
 key,value=line.split('=',1);value=value.strip(' \"\'')
 if any(word in key.upper() for word in ('PASSWORD','SECRET','KEY','TOKEN')) and len(value)>=8:
  secret_values.append(value.encode())
for name in ['mcp-credentials.json','civicly-mcp.json']:
 path=ROOT/'.runtime'/name
 assert not path.is_symlink() and not path.stat().st_mode&0o077
 for key,value in json.loads(path.read_text()).items():
  if 'password' in key and isinstance(value,str):secret_values.append(value.encode())
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')[:-1]
assert all(name in NEW_SOURCE or name.startswith('docs/evidence/B09R-') for name in untracked),'Unapproved new source outside B09-R'
files=sorted(set(tracked+untracked))
for name in files:
 assert not set(Path(name).parts)&{'.runtime','.env','.git','.venv','node_modules','__pycache__','.pytest_cache','.uv-cache','review_packages'}
 assert not name.endswith(('.zip','.tar','.tar.gz','.tgz','.pem','.key','.p12'))
 raw=(ROOT/name).read_bytes()
 assert not any(secret in raw for secret in secret_values),'Private value in '+name
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',raw),'Private pattern in '+name
leaked=[]
for row in subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines():
 parts=row.strip().split(None,2)
 if len(parts)!=3:continue
 exe,command=Path(parts[1]).name,parts[2]
 if ('python' in exe and any(s in command for s in ('-m app.mcp.civicly.server','-m tests.b07r_server','-m tests.b08_server','-m tests.b09_server'))) or (exe=='node' and 'node_modules/@falkordb/mcpserver/dist/index.js' in command):leaked.append(int(parts[0]))
assert not leaked,'MCP child left running'
value={'status':'PASS','baseline':subprocess.check_output(['git','rev-parse',BASE],text=True).strip(),
 'accepted_files_unchanged':protected,'tested_source_freeze_matches':True,'existing582_test_sources_unchanged':True,
 'registry_migrations_B03_B04_B05_B06_B07_B08_writer_dependencies_unchanged':True,
 'candidate_files_scanned':len(files),'local_secret_values_and_private_key_patterns':'PASS; values never logged',
 'leaked_processes':leaked,'archive':'None generated; external full-folder exports not audited'}
(ROOT/'docs/evidence/B09R-source-audit.json').write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps(value))
