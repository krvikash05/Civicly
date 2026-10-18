"""B10 source scope, old-test immutability and secret candidate audit; no secret values logged."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE='2d30550'
ALLOWED={'README.md','backend/CIVICLY_MCP.md','backend/MCP.md','backend/EVIDENCE.md','.env.example','backend/app/mcp/broker.py','backend/app/mcp/policy.py','backend/app/mcp/runtime.py',
 'backend/app/mcp/civicly/broker.py','backend/app/mcp/civicly/contracts.py','backend/app/mcp/civicly/models.py',
 'backend/app/mcp/civicly/server.py','backend/app/mcp/civicly/service.py','backend/app/services/complaints/service.py',
 'backend/app/services/complaints/writer.py','backend/app/services/evidence/writer.py','backend/pyproject.toml','backend/uv.lock',
 'contracts/mcp_envelopes.json','contracts/mcp_tools.json','decision.md','flow.md','implementation_status.md','task_board.md','test_log.md','blockers.md'}
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')[:-1]
protected=0;tests=0
for name in tracked:
 if name in ALLOWED:continue
 expected=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
 assert (ROOT/name).read_bytes()==expected,'Accepted file modified: '+name
 protected+=1;tests+=name.startswith('backend/tests/')
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')[:-1]
for name in untracked:
 assert name=='backend/app/active.py' or name.startswith(('backend/app/agents/','backend/tests/b10_','backend/tests/unit/test_agent_','backend/tests/integration/test_agent_','docs/evidence/B10-')) or name in {'backend/AGENTS_RUNTIME.md','contracts/agent_runtime.json','scripts/audit_b10.py','scripts/verify_b10.py','scripts/b10_discovery.py'},'Outside B10 scope: '+name
values=[]
for line in (ROOT/'.env').read_text().splitlines():
 if '=' not in line:continue
 key,value=line.split('=',1);value=value.strip(' \"\'')
 if any(t in key.upper() for t in ['KEY','SECRET','PASSWORD','TOKEN']) and len(value)>=8:values.append(value.encode())
for path in (ROOT/'.runtime').glob('*.json'):
 assert not path.is_symlink() and not path.stat().st_mode&0o077,'Nonprivate runtime profile'
 def secrets(value):
  if isinstance(value,dict):
   for k,v in value.items():
    if any(t in k.lower() for t in ['password','secret','key','token']) and isinstance(v,str) and len(v)>=8:values.append(v.encode())
    else:secrets(v)
  elif isinstance(value,list):
   for v in value:secrets(v)
 secrets(json.loads(path.read_text()))
files=sorted(set(tracked+untracked))
for name in files:
 assert not set(Path(name).parts)&{'.runtime','.env','.git','.venv','node_modules','__pycache__','.pytest_cache','.uv-cache','review_packages'}
 assert not name.endswith(('.zip','.tar','.tar.gz','.tgz','.pem','.key','.p12'))
 data=(ROOT/name).read_bytes()
 assert not any(value in data for value in values),'Private value in '+name
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',data),'Secret pattern in '+name
leaked=[]
for row in subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines():
 parts=row.strip().split(None,2)
 if len(parts)!=3:continue
 exe,command=Path(parts[1]).name,parts[2]
 if ('python' in exe.lower() and any(term in command for term in ['-m app.agents.server','-m app.mcp.civicly.server','-m tests.b07r_server','-m tests.b08_server','-m tests.b09_server'])) or (exe=='node' and 'node_modules/@falkordb/mcpserver/dist/index.js' in command):leaked.append(int(parts[0]))
assert not leaked,'Owned MCP process left running'
new_python=[name for name in untracked if name.startswith('backend/app/') and name.endswith('.py')]
for name in new_python:
 data=(ROOT/name).read_text()
 assert not any(term in data for term in ['hidden_truth','delayed_reveal','contracts/scenarios','eval_hidden']),'Evaluator reference in application source'
source=[name for name in files if (name in ALLOWED or name in untracked) and not name.startswith('docs/evidence/')]
proof={'status':'PASS','baseline':subprocess.check_output(['git','rev-parse',BASE],text=True).strip(),'accepted_files_unchanged':protected,
 'accepted_test_files_unchanged':tests,'candidate_files_scanned':len(files),'secret_values_and_patterns':'PASS; values never logged',
 'registry_0001_0002_B03_B04_B05_sources_unchanged':True,'new_application_has_no_hidden_evaluator_references':True,'leaked_mcp_processes':leaked,
 'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in source}}
(ROOT/'docs/evidence/B10-source-audit.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({k:v for k,v in proof.items() if k!='source_sha256'}))
