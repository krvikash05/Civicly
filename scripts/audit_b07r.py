"""B07-R accepted-working-tree preservation and sanitized local-secret audit.

No credentials/hashes are emitted. Checks Git candidates only, never declares an
external full-folder archive safe. Baseline manifest contains source file hashes.
"""
import hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
allowed={'README.md','backend/app/mcp/civicly/service.py','backend/app/mcp/civicly/server.py',
         'contracts/mcp_tools.json','backend/CIVICLY_MCP.md','decision.md','flow.md',
         'implementation_status.md','task_board.md','test_log.md','blockers.md'}
baseline=json.loads((ROOT/'docs/evidence/B07R-baseline-sha256.json').read_text())
unchanged=[]
for name,sha in baseline.items():
    if name in allowed:continue
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,'Unexpected accepted B07 file change: '+name
    unchanged.append(name)
wire=json.loads((ROOT/'docs/evidence/B07R-contract-baseline.json').read_text())
current=json.loads((ROOT/'contracts/mcp_tools.json').read_text())
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
assert {t['name']:{'permission':t['permission'],'input_sha256':digest(t['input_schema']),'output_sha256':digest(t['output_schema'])} for t in current['tools']}==wire,'Wire inventory changed'
secrets=[]
for line in (ROOT/'.env').read_text().splitlines():
    if '=' not in line:continue
    key,value=line.split('=',1);value=value.strip(' \"\'')
    if any(k in key.upper() for k in ('PASSWORD','SECRET','KEY','TOKEN')) and len(value)>=8:secrets.append(value.encode())
for name in ['mcp-credentials.json','civicly-mcp.json']:
    p=ROOT/'.runtime'/name;assert not p.is_symlink() and not p.stat().st_mode&0o077
    for key,value in json.loads(p.read_text()).items():
        if 'password' in key and isinstance(value,str):secrets.append(value.encode())
files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
files=sorted(set(files)-{''})
for name in files:
    assert not set(Path(name).parts)&{'.runtime','.env','.git','.venv','node_modules','__pycache__','.pytest_cache','.uv-cache','review_packages'}
    content=(ROOT/name).read_bytes()
    assert not any(secret in content for secret in secrets),'Private value in '+name
    assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',content),'Private pattern in '+name
leaked=[]
for row in subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines():
    parts=row.strip().split(None,2)
    if len(parts)!=3:continue
    executable,command=Path(parts[1]).name,parts[2]
    if ('python' in executable and any(s in command for s in ('-m app.mcp.civicly.server','-m tests.b07r_server'))) or (executable=='node' and 'node_modules/@falkordb/mcpserver/dist/index.js' in command):leaked.append(int(parts[0]))
assert not leaked,'MCP child left running'
report={'status':'PASS','accepted_b07_files_unchanged':len(unchanged),'intentional_modifications':sorted(allowed),
        'all_preexisting_tests_preserved':True,'all18_tool_wire_schemas_and_permissions_unchanged':True,'migrations_registry_dataset_algorithms_official_mcp_and_shared_envelopes_preserved':True,
        'candidate_files_scanned':len(files),'local_secret_scan':'PASS; values never logged','leaked_processes':leaked,
        'scope':'Git candidates only; no archive created or external archive sanitization claim'}
(ROOT/'docs/evidence/B07R-source-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
