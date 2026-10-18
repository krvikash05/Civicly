"""Verify raw pytest/lifecycle proof, then reuse unchanged B09 graph/history verifier.

The historical CLI regex accepts 'N passed in' but not 'N passed, W warnings in'.
No test result or historical file is rewritten to work around that presentation gap.
"""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--log',type=Path,required=True);p.add_argument('--guard',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
raw=a.log.read_bytes();text=raw.decode();guard=json.loads(a.guard.read_text())
match=re.search(r'^=+ (\d+) passed(?:, (\d+) warnings?)? in ([\d.]+)s[^\n]*=+$',text,re.M)
assert match and int(match[1])==740 and ' failed,' not in text
assert 'after restart (same container)' in text and 'after recreation (different container, retained volume)' in text
assert guard['exitstatus']==0 and guard['external_gemini_requests_sent']==0 and guard['ordinary_unexpected_attempts']==0
# All original data/fingerprint/history assertions execute against the real database.
subprocess.run([sys.executable,'-m','tests.b09_evidence','verify','--proof','docs/evidence/B09-retained-proof.json','--output',str(a.output)],check=True)
v=json.loads(a.output.read_text());v['real_lifecycle_log']=str(a.log);v['lifecycle_proof']={'validation':'Warning-aware raw-summary adapter; unchanged B09 data/history verifier; no log normalization','raw_log_sha256':hashlib.sha256(raw).hexdigest(),'passed':int(match[1]),'warnings':int(match[2] or 0),'elapsed_seconds':float(match[3]),'guard_exitstatus':guard['exitstatus'],'actual_external_gemini_requests':0}
a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':'PASS','raw_lifecycle_verified':True,'original_B09_assertions_reused':True,'log_rewritten':False}))
