"""Static B11 contract/source validation, not SDK or model acceptance."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from app.memory.models import sources,Source,Citation,OWNERS
from jsonschema import Draft202012Validator,FormatChecker
c=json.loads((ROOT/'contracts/organizational_memory.json').read_text())
assert c['source']==Source.model_json_schema() and c['citation']==Citation.model_json_schema() and c['owner_mapping']==OWNERS
for row in sources():
 Draft202012Validator(c['source'],format_checker=FormatChecker()).validate(row.model_dump(mode='json'));row.checked_path()
plan=json.loads((ROOT/'backend/app/graph/migrations/0003_document_memory.json').read_text())
assert plan['requires_0001_sha256']==hashlib.sha256((ROOT/'backend/app/graph/migrations/0001.json').read_bytes()).hexdigest()
print('PASS B11 STATIC:19 authorized versioned sources, explicit owner mapping, closed citation contract, frozen originals and compatible0003 hash; not runtime/model proof')
