"""B06 local source/exclusion audit. Never emit discovered secret values."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import tomllib

ROOT=Path(__file__).resolve().parents[1]
BASE=json.loads((ROOT/'docs/evidence/B06-source-baseline.json').read_text())
secret_values=[]
for line in (ROOT/'.env').read_text().splitlines():
    if '=' in line:
        name,value=line.split('=',1);value=value.strip(' \"\'')
        if any(word in name.upper() for word in ('PASSWORD','SECRET','KEY','TOKEN')) and len(value)>=8:
            secret_values.append(value.encode())
private=ROOT/'.runtime/mcp-credentials.json'
if private.exists():
    assert not private.is_symlink() and not private.stat().st_mode & 0o077
    secret_values.append(json.loads(private.read_text())['password'].encode())
for path,expected in BASE['source_files'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,'Protected source changed:'+path
old=tomllib.loads(subprocess.check_output(['git','show','HEAD:backend/pyproject.toml'],text=True))
current=tomllib.loads((ROOT/'backend/pyproject.toml').read_text())
assert set(old['project']['dependencies']) <= set(current['project']['dependencies'])
tracked=subprocess.check_output(['git','ls-files','-z'],text=True).split('\0')[:-1]
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],text=True).split('\0')[:-1]
for path in sorted(set(tracked+untracked)):
    parts=set(Path(path).parts)
    assert not parts & {'.git','.venv','.runtime','node_modules','__pycache__','.pytest_cache','.uv-cache','review_packages'}
    assert Path(path).name!='.env'
    data=(ROOT/path).read_bytes()
    assert not any(value in data for value in secret_values),'Actual local secret match:'+path
    assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',data),'Key pattern:'+path
assert subprocess.run(['git','check-ignore','.env','.runtime/mcp-credentials.json','backend/.venv','backend/mcp_runtime/node_modules','review_packages'],capture_output=True).returncode==0
assert hashlib.sha256((ROOT/'review_packages/Civicly_B05_Review.zip').read_bytes()).hexdigest()==BASE['b05_zip_sha256']
rows=subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines()
processes=[]
for row in rows:
    parts=row.strip().split(None,2)
    if len(parts)==3 and Path(parts[1]).name=='node' and 'node_modules/@falkordb/mcpserver/dist/index.js' in parts[2]:
        processes.append(int(parts[0]))
assert not processes,'Leaked official MCP child process'
report={'status':'PASS','baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'protected_original_files':len(BASE['source_files']),'original_code_tests_contracts_data_unchanged':True,
        'original_direct_dependency_pins_preserved':True,'candidate_files_scanned':len(set(tracked+untracked)),
        'actual_local_env_and_mcp_secret_scan':'PASS; no values logged','excluded_runtime_venv_git_caches_volumes':'PASS',
        'b05_review_zip_unchanged':True,'leaked_official_mcp_processes':processes,'b06_zip_created':False}
(ROOT/'docs/evidence/B06-source-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
