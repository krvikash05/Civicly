"""B19 static world/route parity; never agent behavioral proof."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from app.services.demo.definitions import load
from app.services.demo.inventory import ISSUES
from app.services.demo.models import ScenarioID
from typing import get_args
from app.api.coverage import ROUTES,DEFERRED_B19
from cli.main import ACTIONS
c=json.loads((ROOT/'contracts/scenarios/catalog.json').read_text());w=load()
assert set(w)==set(ISSUES)==set(get_args(ScenarioID))=={s['id'] for s in c['scenarios']}
for s in c['scenarios']:assert s['issue_types']==w[s['id']].issues==ISSUES[s['id']] and set(w[s['id']].release)==set(w[s['id']].negative)==set(s['issue_types'])
assert not DEFERRED_B19
for method,path in ACTIONS['demo'].values():assert any((r[0],r[1])==(method,path) for r in ROUTES)
policy=json.loads((ROOT/'contracts/scenarios/runtime.json').read_text());assert policy['reset_role']==policy['advance_role']=='ADMIN'
assert len(w)==12 and all(len(packet)<=10 for s in w.values() for p in [s.release,s.negative] for packet in p.values())
from app.services.service_evidence import ServiceRecord,VERSION
service=json.loads((ROOT/'contracts/service_evidence.json').read_text())
assert service['version']==VERSION and service['schema']==ServiceRecord.model_json_schema()
packet=json.loads((ROOT/'data/scenarios/service-evidence-v1.json').read_text())
assert packet['version']==1 and set(packet['scenarios'])=={'S05','S06'}
assert all(set(v)=={'PRIMARY','NEGATIVE'} for v in packet['scenarios'].values())
print('PASS B19 STATIC:12 definitions/24 variants, closed bounded source/stage contracts, actual CLI/API inventory; no behavioral/live claim')
