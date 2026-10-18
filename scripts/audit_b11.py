"""B11 exact-scope, unchanged-history, zero-provider and secret audit."""
import difflib,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE='9f7ec1d'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
baseline=git('ls-tree','-r','--name-only',BASE).decode().splitlines()
allowed={'README.md','backend/AGENTS_RUNTIME.md','backend/CIVICLY_MCP.md','backend/pyproject.toml','backend/uv.lock','backend/app/agents/mcp.py','backend/app/agents/server.py','backend/app/mcp/civicly/server.py','backend/app/mcp/civicly/service.py','contracts/mcp_tools.json','docs/backend/06_memory_graphrag.md','scripts/validate_blueprint.py','scripts/validate_handoff.py','decision.md','flow.md','task_board.md','implementation_status.md','test_log.md','blockers.md'}
new={'backend/MEMORY.md','backend/app/graph/migrations/0003_document_memory.json','backend/tests/b11_worker.py','backend/tests/unit/test_memory_sources.py','backend/tests/integration/test_memory_graphrag.py','backend/tests/integration/test_memory_mcp.py','backend/tests/integration/test_memory_case_history.py','contracts/organizational_memory.json','data/documents/b11/manifest.json','data/documents/b11/D001_v1_derivative.pdf','scripts/validate_memory.py','scripts/verify_b11_retained_history.py','scripts/verify_b11_persistence.py','scripts/audit_b11.py'}
files=sorted(set(git('ls-files','-z').decode().split('\0')[:-1]+git('ls-files','--others','--exclude-standard','-z').decode().split('\0')[:-1]))
changed=[];unchanged=[]
for name in baseline:
    assert (ROOT/name).is_file(),'Baseline missing: '+name
    if (ROOT/name).read_bytes()!=git('show',BASE+':'+name):
        assert name in allowed,'Protected source/evidence changed: '+name
        changed.append(name)
    else:unchanged.append(name)
added=sorted(set(files)-set(baseline))
for n in added:assert n in new or n.startswith('backend/app/memory/') or n.startswith('docs/evidence/B11-'),'Outside B11 scope: '+n
for n in baseline:
    if n.startswith('backend/tests/') and n.endswith('.py'):
        prior=set(re.findall(r'^def (test_[A-Za-z0-9_]+)\(',git('show',BASE+':'+n).decode(),re.M))
        current=set(re.findall(r'^def (test_[A-Za-z0-9_]+)\(',(ROOT/n).read_text(),re.M))
        assert prior<=current,'Previous test removed: '+n
values=[]
for line in (ROOT/'.env').read_text().splitlines():
    if '=' not in line:continue
    k,v=line.split('=',1);v=v.strip(' \"\'')
    if any(t in k.upper() for t in ['KEY','SECRET','PASSWORD','TOKEN']) and len(v)>=8:values.append(v.encode())
def private(v):
    if isinstance(v,dict):
        for k,item in v.items():
            if any(t in k.lower() for t in ['password','secret','key','token']) and isinstance(item,str) and len(item)>=8:values.append(item.encode())
            else:private(item)
    elif isinstance(v,list):
        for item in v:private(item)
for p in (ROOT/'.runtime').glob('*.json'):
    assert not p.is_symlink() and not p.stat().st_mode&0o077,'Nonprivate runtime profile'
    private(json.loads(p.read_text()))
for name in files:
    assert not set(Path(name).parts)&{'.runtime','.env','.git','.venv','node_modules','__pycache__','.pytest_cache','review_packages'}
    assert not name.endswith(('.zip','.tar','.tgz','.pem','.key','.p12'))
    data=(ROOT/name).read_bytes();assert not any(v in data for v in values),'Private value found in '+name
    assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',data),'Secret pattern in '+name
    if name.startswith('backend/app/agents/') and name.endswith('.py'):assert not any(t in data for t in [b'contracts/scenarios',b'eval_hidden',b'delayed_reveal',b'hidden_truth'])
proof=json.loads((ROOT/'docs/evidence/B11-regression-zero-live.json').read_text());assert proof['exitstatus']==0 and proof['external_gemini_requests_sent']==0 and proof['ordinary_unexpected_attempts']==0
leaked=[]
for row in subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines():
    parts=row.strip().split(None,2)
    if len(parts)!=3:continue
    exe,cmd=Path(parts[1]).name,parts[2]
    if ('python' in exe.lower() and any(t in cmd for t in ['-m app.agents.server','-m app.mcp.civicly.server','-m tests.b07r_server','-m tests.b08_server','-m tests.b09_server'])) or (exe=='node' and 'node_modules/@falkordb/mcpserver/dist/index.js' in cmd):leaked.append(int(parts[0]))
assert not leaked,'Leaked MCP children'
source=sorted(n for n in changed+added if not n.startswith('docs/evidence/'));patch=[]
for name in source:
    if name.endswith('.pdf'):
        attrs=Path('/tmp/civicly-b11-audit-attributes');attrs.write_text('*.pdf binary\n')
        result=subprocess.run(['git','-c','core.attributesFile='+str(attrs),'diff','--no-index','--binary','--','/dev/null',name],cwd=ROOT,capture_output=True)
        assert result.returncode==1
        patch.append(result.stdout.decode());continue
    old=git('show',BASE+':'+name).decode().splitlines(keepends=True) if name in baseline else []
    patch.extend(difflib.unified_diff(old,(ROOT/name).read_text().splitlines(keepends=True),fromfile='a/'+name if old else '/dev/null',tofile='b/'+name))
(ROOT/'docs/evidence/B11-changes.patch').write_text(''.join(patch))
value={'status':'PASS','baseline':BASE,'baseline_files_unchanged':len(unchanged),'all_prior_test_files_unchanged':all(n in unchanged for n in baseline if n.startswith('backend/tests/')),'prior_test_files_unchanged':sum(n.startswith('backend/tests/') for n in unchanged),'all_prior_evidence_byte_identical':all(n in unchanged for n in baseline if n.startswith('docs/evidence/')),'candidate_files_scanned':len(files),'secrets':'Actual private values and secret patterns absent; no values printed','external_provider_requests':0,'leaked_mcp_children':leaked,'modified_files':changed,'new_files':added,'source_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in source},'patch_basis':'9f7ec1d reviewed B10-O-R2 local commit; source/contract/tracker diff includes actual new files, generated evidence listed separately'}
(ROOT/'docs/evidence/B11-source-audit.json').write_text(json.dumps(value,indent=2)+'\n')
(ROOT/'docs/evidence/B11-FILES.md').write_text('# B11 changed-file inventory\n\nAgainst local B10-O-R2 baseline9f7ec1d; no push or ZIP. All prior tests and evidence unchanged. Patch includes actual new source files and the binary PDF derivative; every source is hashed.\n\n## Modified\n\n'+''.join('- `'+n+'`\n' for n in changed)+'\n## Added\n\n'+''.join('- `'+n+'`\n' for n in sorted(set(added)|{'docs/evidence/B11-source-audit.json','docs/evidence/B11-changes.patch','docs/evidence/B11-FILES.md'})))
print(json.dumps({k:v for k,v in value.items() if k not in {'source_sha256','modified_files','new_files'}}))
