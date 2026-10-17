"""Git-candidate secret/source/process audit; never claims full-folder archives safe."""
from pathlib import Path
import subprocess,hashlib,json,re
root=Path(__file__).resolve().parents[1];secret_values=[]
for line in (root/'.env').read_text().splitlines():
 if '=' in line:
  k,v=line.split('=',1);v=v.strip(' \"\'')
  if any(w in k.upper() for w in ['PASSWORD','SECRET','KEY','TOKEN']) and len(v)>=8:secret_values.append(v.encode())
for name in ['mcp-credentials.json','civicly-mcp.json']:
 p=root/'.runtime'/name;assert not p.is_symlink() and not p.stat().st_mode&0o077
 for k,v in json.loads(p.read_text()).items():
  if 'password' in k and isinstance(v,str):secret_values.append(v.encode())
tracked=subprocess.check_output(['git','ls-files','-z'],text=True).split('\0')[:-1]
new=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],text=True).split('\0')[:-1]
protected=0;intentional={'contracts/mcp_tools.json','contracts/api_models.json'}
for name in tracked:
 if name.startswith(('backend/app/','backend/tests/','contracts/','data/ingestion/')) and name not in intentional:
  assert (root/name).read_bytes()==subprocess.check_output(['git','show','HEAD:'+name]),'Protected original changed:'+name
  protected+=1
for name in ['backend/pyproject.toml','backend/uv.lock','backend/mcp_runtime/package.json','backend/mcp_runtime/package-lock.json']:
 assert (root/name).read_bytes()==subprocess.check_output(['git','show','HEAD:'+name]),'Accepted dependency pin changed'
for name in sorted(set(tracked+new)):
 assert not set(Path(name).parts)&{'.runtime','.env','.git','.venv','node_modules','__pycache__','.pytest_cache','.uv-cache','review_packages'}
 data=(root/name).read_bytes();assert not any(v in data for v in secret_values),'Actual private value included:'+name
 assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',data),'Private key pattern:'+name
old=json.loads(subprocess.check_output(['git','show','HEAD:contracts/mcp_tools.json']));current=json.loads((root/'contracts/mcp_tools.json').read_text())
assert [(t['name'],t['permission']) for t in old['tools']]==[(t['name'],t['permission']) for t in current['tools']]
assert subprocess.run(['git','check-ignore','.env','.runtime/mcp-credentials.json','.runtime/civicly-mcp.json','backend/.venv','backend/mcp_runtime/node_modules','review_packages'],capture_output=True).returncode==0
leaked=[]
for row in subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines():
 p=row.strip().split(None,2)
 if len(p)==3 and ((Path(p[1]).name=='node' and 'node_modules/@falkordb/mcpserver/dist/index.js' in p[2]) or ('python' in Path(p[1]).name and '-m app.mcp.civicly.server' in p[2])):leaked.append(int(p[0]))
assert not leaked,'Leaked runtime process'
report={'status':'PASS','protected_original_files':protected,'original_tests_and_domain_code_preserved':True,
 'intentional_contract_changes':sorted(intentional),'all18_tool_names_permissions_preserved':True,'accepted_dependency_pins_preserved':True,
 'candidate_files_scanned':len(set(tracked+new)),'actual_local_credentials_scan':'PASS; no values logged','leaked_processes':leaked,
 'archive_scope':'Git candidates only; external reported full-folder archive not inspected or claimed safe; no B07 archive created',
 'rotation_report':json.loads((root/'docs/evidence/B07-credential-rotation.json').read_text())}
(root/'docs/evidence/B07-source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
