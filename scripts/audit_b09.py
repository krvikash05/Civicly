"""B09 source/secret audit against local accepted B08 baseline; values never logged."""
from pathlib import Path
import subprocess,json,re
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'README.md','backend/README.md','backend/CIVICLY_MCP.md','docs/backend/02_graph.md',
         'decision.md','flow.md','implementation_status.md','task_board.md','test_log.md','blockers.md'}
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')[:-1]
protected=0
for name in tracked:
    if name in ALLOWED:continue
    assert (ROOT/name).read_bytes()==subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT),'Accepted source/evidence changed: '+name
    protected+=1
secrets=[]
for line in (ROOT/'.env').read_text().splitlines():
    if '=' not in line:continue
    key,value=line.split('=',1);value=value.strip(' \"\'')
    if any(k in key.upper() for k in ('PASSWORD','SECRET','KEY','TOKEN')) and len(value)>=8:secrets.append(value.encode())
for name in ['mcp-credentials.json','civicly-mcp.json']:
    p=ROOT/'.runtime'/name;assert not p.is_symlink() and not p.stat().st_mode&0o077
    for key,value in json.loads(p.read_text()).items():
        if 'password' in key and isinstance(value,str):secrets.append(value.encode())
new=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')[:-1]
files=sorted(set(tracked+new))
for name in files:
    assert not set(Path(name).parts)&{'.runtime','.env','.git','.venv','node_modules','__pycache__','.pytest_cache','.uv-cache','review_packages'}
    assert not name.endswith(('.zip','.tar','.tar.gz','.tgz','.pem','.key','.p12'))
    raw=(ROOT/name).read_bytes();assert not any(secret in raw for secret in secrets),'Private value found in '+name
    assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',raw),'Private pattern found in '+name
leaked=[]
for row in subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines():
    parts=row.strip().split(None,2)
    if len(parts)!=3:continue
    executable,command=Path(parts[1]).name,parts[2]
    if ('python' in executable and any(s in command for s in ('-m app.mcp.civicly.server','-m tests.b07r_server','-m tests.b08_server','-m tests.b09_server'))) or (executable=='node' and 'node_modules/@falkordb/mcpserver/dist/index.js' in command):leaked.append(int(parts[0]))
assert not leaked,'MCP child left running'
report={'status':'PASS','baseline':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'accepted_files_unchanged':protected,'all507_baseline_tests_unchanged':True,
 'existing_migrations_registry_policies_algorithms_dataset_ingestion_mcp_and_envelopes_unchanged':True,
 'dependencies_and_locks_unchanged':True,'candidate_files_scanned':len(files),'actual_local_secret_scan':'PASS; values never logged',
 'leaked_processes':leaked,'archive':'No archive generated; Git-candidate audit does not claim external full-folder exports safe'}
(ROOT/'docs/evidence/B09-source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
