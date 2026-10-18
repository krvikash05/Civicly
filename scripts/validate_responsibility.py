"""Static responsibility contract parity; not authority/runtime evidence."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from app.services.responsibility.models import Submission,Review,ResponsibilityDTO,SubmissionRecord,ReviewRecord
v=json.loads((ROOT/'contracts/responsibility.json').read_text())
assert v['models']=={c.__name__:c.model_json_schema() for c in [Submission,Review,ResponsibilityDTO,SubmissionRecord,ReviewRecord]}
assert not v['authority']['admin_bypass']
assert set(Submission.model_fields)=={'asset_id','department_id','source_id','source_record_id','source_version','source_kind','observed_at','valid_from','valid_to'}
assert set(Review.model_fields)=={'expected_hash','reviewed','reason'}
assert 'ownership_cardinality' in json.loads((ROOT/'contracts/graph_access.json').read_text())
print('PASS B20-R-OWNERSHIP STATIC: closed source/review/status contracts, operator-only independent review, compatible existing storage; not runtime authority proof')
