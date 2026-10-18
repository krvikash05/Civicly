# B11-R exact commands and outcomes

Run from `/Users/vikashkumar/Desktop/Civicly`, Python3.12 isolated existing .venv.
No package install, container restart/recreation, graph reset or live provider.
Ordinary pytest installs the inherited provider guard for Python child processes.

## Before-correction reproduction
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11r-repro-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_review.py -k 'all_seeded or missing] or latest_assessment' -q > /tmp/civicly-b11r-repro.txt 2>&1
```
3failed/2deselected16.44s on original application source. Current code should pass
these cases; the preserved original failure output is B11R-repro.txt.

## Focused fixes, failure and directly affected rerun
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11r-focused-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_review.py -q --durations=10 > /tmp/civicly-b11r-focused.txt 2>&1
```
First run4PASS/1fixtureFAIL28.07s: B09 assessment guard rejects >100 per hypothesis.
The corrected fixture uses8+96 across two hypotheses,104 per investigation.
No production guard/old assertion weakened. Reproduce final5cases with this same
command; recorded successful per-case results are the original4PASS plus rerun:
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11r-history-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_review.py::test_latest_assessment_budget_and_history_beyond_hard_cap -q --durations=10 > /tmp/civicly-b11r-history.txt 2>&1
```
1PASS16.68s; no repetition of unchanged four cases.

## Existing affected version/revocation and actual MCP/Saver
```sh
CIVICLY_MEMORY_TEST_EVIDENCE_PREFIX=B11R CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11r-compat-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_graphrag.py::test_versions_supersession_revocation_and_missing_source backend/tests/integration/test_memory_mcp.py::test_real_sdk_domain_mcp_agent_checkpoint_and_fresh_process -q --durations=10 > /tmp/civicly-b11r-compat.txt 2>&1
```
2PASS16.36s. B11R prefix prevents overwriting original B11 proof. Existing assertions
retained, Water Utilities call added. No duplicate checkpoint test.

## Final specification validators (executed once)
```sh
make test-spec > /tmp/civicly-b11r-spec.txt 2>&1
```
Both PASS including static B11/B04 validations. Not runtime/model proof.

## Read-only SDK metadata spike
Initial same snippet with `from app.db import connect` failed ModuleNotFoundError
before database use. Corrected exact command:
```sh
PYTHONPATH=backend backend/.venv/bin/python - <<'PY'
from app.config import Settings
from app.graph.connection import connect
with connect(Settings(_env_file='.env')) as db:
 g=db.select_graph('civicly_docs')
 for q in ['CALL db.indexes() YIELD label,properties,types,status,options RETURN label,properties,types,status,options', 'MATCH (c:Chunk) RETURN c.embedding LIMIT 1']:
  try: print(repr(g.ro_query(q).result_set)[:1800])
  except Exception as e: print(type(e).__name__,str(e))
PY
```
Actual OPERATIONAL grouped metadata includes VECTOR dimension64/cosine and FULLTEXT;
returned vectors are finite float32-rounded numeric lists. No credential output.

## Original versus corrected deployed Water lookup (read only)
```sh
PYTHONPATH=backend/test_guards:backend CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/civicly-b11r-water-provider.jsonl backend/.venv/bin/python - <<'PY'
import asyncio,importlib.util,json
from pathlib import Path
from app.memory.runtime import Profile,PROFILE
spec=importlib.util.spec_from_file_location('app.memory.b11r_original_service','/tmp/civicly-b11r-baseline/backend/app/memory/service.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
db,current=Profile.model_validate_json(PROFILE.read_text()).connect()
async def run():
 old=module.Memory(current.repo,current.config)
 before=await old.retrieve(as_of='2026-10-18T00:00:00Z',department_id='DEPT-WATER',action_type='INSPECTION')
 after=await current.retrieve(as_of='2026-10-18T00:00:00Z',department_id='DEPT-WATER',action_type='INSPECTION')
 assert not before['citations'] and {c['source_document_id'] for c in after['citations']}=={'D005','D017'}
 Path('docs/evidence/B11R-deployed-water-comparison.json').write_text(json.dumps({'mode':'Actual read-only retained graphs; original source snapshot versus corrected source','before':before,'after':after,'gemini_requests':0},indent=2)+'\n')
 print('PASS read-only deployed comparison: original0 citations, corrected D005/D017; no writes')
try:asyncio.run(run())
finally:db.connection.close();db.connection.connection_pool.disconnect()
PY
```
PASS. Requires the original source snapshot retained locally in /tmp; not a normal
human reproduction dependency. The review patch shows the original code and actual
before/after proof is retained. Use passing current tests for durable reproduction.

## Final artifact checks
```sh
backend/.venv/bin/python /tmp/civicly-b11r-audit.py
git diff --check
git apply --reverse --check docs/evidence/B11R-changes.patch
```
Audit output B11R-source-audit.json contains exact file/hash preservation, public
secret/exclusion scan and no leaked MCP children. Private values never printed.
No770/313 regression or lifecycle command executed. Final7distinct real integration
cases;0 unresolved failures/skips, unit batch not run. Historical failures preserved,
not added to final passing totals.
