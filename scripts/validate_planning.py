"""B12 strict schema parity and draft-only static checks, not runtime acceptance."""
import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from app.services.planning.models import PlanDraft,PlanReceipt
from app.services.planning.feedback import Feedback
from app.services.planning.policy import ACTIONS
from app.memory.models import sources
c=json.loads((ROOT/'contracts/resolution_planning.json').read_text())
assert c['draft_schema']==PlanDraft.model_json_schema() and c['receipt_schema']==PlanReceipt.model_json_schema()
p=json.loads((ROOT/'backend/app/graph/migrations/0004_plan_drafts.json').read_text())
assert p['requires_0001_sha256']==hashlib.sha256((ROOT/'backend/app/graph/migrations/0001.json').read_bytes()).hexdigest()
assert c['execution_authority'] is False
assert c['feedback_schema']==Feedback.model_json_schema() and c['action_policies']==ACTIONS
new=sources(ROOT/'data/documents/b12r/manifest.json')
utility=sources(ROOT/'data/documents/b20r_utility/manifest.json')
assert len(new)==3 and len(utility)==1 and {a for s in new+utility for a in s.action_types}==set(ACTIONS)
for source in utility:source.checked_path()
for s in new:s.checked_path()
print('PASS B12 STATIC: closed plan/task/monitoring schemas, draft-only receipt and compatible0004; not runtime/approval proof')
