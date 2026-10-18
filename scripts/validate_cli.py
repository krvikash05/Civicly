"""B18 static CLI/service inventory parity; not runtime or autonomous AI proof."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from cli.main import ACTIONS,EXIT
from app.api.coverage import ROUTES
c=json.loads((ROOT/'contracts/operator_cli.json').read_text())
assert c['entrypoint']=='cli.main:main' and c['microtask']=='B18'
assert c['legacy_commands']==['health','migrate','schema-status']
assert c['no_live_provider'] and c['no_destructive_reset'] and c['no_automatic_recovery_clearance']
for actions in ACTIONS.values():
 for method,path in actions.values():assert any((row[0],row[1])==(method,path) for row in ROUTES)
assert c['commands']=={group:{action:{'method':method,'path':'/api/v1'+path} for action,(method,path) in actions.items()} for group,actions in ACTIONS.items()}
assert c['exit_codes']['recovery_required_unknown']==EXIT['RECOVERY_REQUIRED']==6
assert c['reset_fixture']=={'asset_id':'DRAIN-100','location_id':'LOC-005','node_count':4,'edge_count':2,'new_operational_records':0}
print('PASS B18 STATIC: closed operator inventory delegates accepted API/services, private configuration, fresh-only reset and offline bounded worker; not runtime/model proof')
