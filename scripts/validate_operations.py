"""B13 static schema/policy/migration parity; not runtime/auth proof."""
import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from app.services.operations.auth import OPERATORS,PERMISSIONS
from app.services.operations.models import Submit,Decide,Order,Update
c=json.loads((ROOT/'contracts/operations.json').read_text())
assert c['commands']=={v.__name__:v.model_json_schema() for v in [Submit,Decide,Order,Update]}
assert c['operators']=={k:{'role':v[0],'department_id':v[1]} for k,v in OPERATORS.items()}
assert c['permissions']=={k:sorted(v) for k,v in PERMISSIONS.items()}
p=json.loads((ROOT/'backend/app/graph/migrations/0005_operations.json').read_text())
assert p['requires_0001_sha256']==hashlib.sha256((ROOT/'backend/app/graph/migrations/0001.json').read_bytes()).hexdigest()
s=json.loads((ROOT/'contracts/state_machines.json').read_text())
assert s['machines']['WorkOrder']['initial']=='AUTHORIZED'
assert c['permissions']['decide']==['APPROVER'] and 'ADMIN' not in c['permissions']['order']
from app.services.operations.execution_models import COMMANDS
from app.services.operations.verification import VERSION,CODES,REQUIRED
assert c['execution_commands']=={v.__name__:v.model_json_schema() for v in COMMANDS.values()}
assert c['verification']['version']==VERSION and c['verification']['units']==CODES
assert c['verification']['required_codes']=={k:list(v) for k,v in REQUIRED.items()}
assert c['verification']['synthetic_waste_minimum_hours']==24
from app.services.operations.verification_v1 import VERSION as HISTORICAL_VERSION
assert c['historical_verification'][HISTORICAL_VERSION]['version']==HISTORICAL_VERSION
assert c['recurrence_scope']['maximum_bound_incidents']==3
from app.services.operations import utility
assert c['utility_policy']['version']==utility.VERSION
assert c['utility_policy']['isolation_code']==utility.ISOLATION
assert c['utility_policy']['followup_codes']==sorted(utility.FOLLOWUP)
assert c['utility_policy']['verified_status']=='UTILITY_VERIFIED' and c['utility_policy']['case_closed'] is False
print('PASS B14 STATIC: execution schemas/policy parity; B13 STATIC: closed commands, exact seven-account/four-role demo permissions, AUTHORIZED initial state and compatible0005; not execution/provider/runtime proof')
