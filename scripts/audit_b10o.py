"""B10-O incremental source/evidence audit against the frozen B10 working tree."""
import difflib,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
baseline=json.loads((ROOT/'docs/evidence/B10O-baseline.json').read_text())['files']
ALLOWED={'.env.example','README.md','backend/AGENTS_RUNTIME.md','backend/pyproject.toml','backend/tests/conftest.py',
 'backend/app/agents/provider.py','backend/app/agents/runtime.py','backend/app/agents/mcp.py','backend/app/agents/__main__.py',
 'contracts/agent_runtime.json','backend/tests/unit/test_agent_provider.py','backend/tests/b10_live.py','backend/tests/b10_live_topology.py',
 'decision.md','flow.md','task_board.md','implementation_status.md','test_log.md','blockers.md'}
NEW={
 'backend/app/agents/context.py','backend/app/agents/policy.py','backend/app/agents/spending.py',
 'backend/app/agents/pricing/gemini-3.8-flash-standard-2026-10.json','backend/app/agents/prompts/B10-3.txt',
 'backend/test_guards/civicly_no_live.py','backend/test_guards/sitecustomize.py',
 'backend/tests/unit/test_ai_spending.py','backend/tests/unit/test_ai_execution_policy.py','backend/tests/unit/test_ai_provider_recovery.py','backend/tests/unit/test_agent_context.py',
 'backend/tests/integration/test_agent_optimization.py','backend/tests/live/README.md','backend/tests/live/run_investigation.py',
 'contracts/agent_optimization.json','scripts/measure_b10o_context.py','scripts/audit_b10o.py','scripts/verify_b10o_spending.py'}
files=sorted(set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')[:-1]+subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')[:-1]))
changed=[];unchanged=[]
for name,expected in baseline.items():
    path=ROOT/name;assert path.is_file(),'Baseline file removed: '+name
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        assert name in ALLOWED,'Protected B10 baseline modified: '+name
        changed.append(name)
    else:unchanged.append(name)
added=sorted(set(files)-set(baseline))
for name in added:assert name in NEW or name.startswith('docs/evidence/B10O-'),'Outside B10-O scope: '+name
# Compare every earlier source/helper/assertion to the frozen B10; only explicit provider setup and global interception changed.
assert all(n in unchanged for n in baseline if n.startswith('backend/tests/') and n not in ALLOWED)
values=[]
for line in (ROOT/'.env').read_text().splitlines():
    if '=' not in line:continue
    k,v=line.split('=',1);v=v.strip(' \"\'')
    if any(t in k.upper() for t in ['KEY','SECRET','PASSWORD','TOKEN']) and len(v)>=8:values.append(v.encode())
def secrets(v):
    if isinstance(v,dict):
        for k,item in v.items():
            if any(t in k.lower() for t in ['password','secret','key','token']) and isinstance(item,str) and len(item)>=8:values.append(item.encode())
            else:secrets(item)
    elif isinstance(v,list):
        for item in v:secrets(item)
for p in (ROOT/'.runtime').glob('*.json'):
    assert not p.is_symlink() and not p.stat().st_mode&0o077,'Nonprivate runtime profile';secrets(json.loads(p.read_text()))
for name in files:
    assert not set(Path(name).parts)&{'.runtime','.env','.git','.venv','node_modules','__pycache__','.pytest_cache','review_packages'}
    assert not name.endswith(('.zip','.tar','.tgz','.pem','.key','.p12'))
    data=(ROOT/name).read_bytes()
    assert not any(v in data for v in values),'Private value found in '+name
    assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',data),'Secret pattern in '+name
    if name.startswith('backend/app/agents/') and name.endswith('.py'):
        assert not any(t in data for t in [b'contracts/scenarios',b'eval_hidden',b'delayed_reveal',b'hidden_truth']),'Hidden evaluation reference: '+name
proof=json.loads((ROOT/'docs/evidence/B10O-zero-live-proof.json').read_text())
assert proof['external_gemini_requests_sent']==0 and proof['ordinary_unexpected_attempts']==0
leaked=[]
for row in subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines():
    parts=row.strip().split(None,2)
    if len(parts)!=3:continue
    exe,cmd=Path(parts[1]).name,parts[2]
    if ('python' in exe.lower() and any(t in cmd for t in ['-m app.agents.server','-m app.mcp.civicly.server','-m tests.b07r_server','-m tests.b08_server','-m tests.b09_server'])) or (exe=='node' and 'node_modules/@falkordb/mcpserver/dist/index.js' in cmd):leaked.append(int(parts[0]))
assert not leaked,'Leaked MCP child processes'
source=sorted(n for n in changed+added if not n.startswith('docs/evidence/'))
patch=[]
for name in source:
    old=(ROOT/'.runtime/b10o-baseline'/name).read_text().splitlines(keepends=True) if name in baseline else []
    new=(ROOT/name).read_text().splitlines(keepends=True)
    patch.extend(difflib.unified_diff(old,new,fromfile='a/'+name if old else '/dev/null',tofile='b/'+name))
(ROOT/'docs/evidence/B10O-changes.patch').write_text(''.join(patch))
value={'status':'PASS','baseline':'B10O-baseline.json frozen B10 working tree, Git base '+json.loads((ROOT/'docs/evidence/B10O-baseline.json').read_text())['base_git'],
 'baseline_files_unchanged':len(unchanged),'prior_test_files_unchanged':sum(n.startswith('backend/tests/') for n in unchanged),
 'all_prior_B10_evidence_byte_identical':all(n in unchanged for n in baseline if n.startswith('docs/evidence/')),
 'candidate_files_scanned':len(files),'secrets':'Actual private values and key patterns absent; values never printed',
 'zero_external_provider_requests':True,'leaked_mcp_processes':leaked,'modified_files':sorted(changed),'new_files':added,
 'source_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in source},'patch_basis':'Frozen pre-optimization B10, excludes generated evidence/logs; old Git diff also includes uncommitted B10'}
(ROOT/'docs/evidence/B10O-source-audit.json').write_text(json.dumps(value,indent=2)+'\n')
manifest='# B10-O changed-file inventory\n\nIncremental against frozen B10O-baseline.json; earlier uncommitted B10 changes are preserved. No ZIP or push.\n\n## Modified\n\n'+''.join('- `'+n+'`\n' for n in sorted(changed))+'\n## Added\n\n'+''.join('- `'+n+'`\n' for n in sorted(set(added)|{'docs/evidence/B10O-source-audit.json','docs/evidence/B10O-changes.patch','docs/evidence/B10O-FILES.md'}))+'\nProvider test setup now requires explicit MockTransport permission/private simulated ledger; original assertions retained. Global conftest adds interception; no old test removed. Legacy paid batch helpers disabled in favor of exact-case live CLI. All prior evidence is byte-identical.\n'
(ROOT/'docs/evidence/B10O-FILES.md').write_text(manifest)
print(json.dumps({k:v for k,v in value.items() if k not in {'source_sha256','modified_files','new_files'}}))
