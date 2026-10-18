# B17 exact commands and observed results

Working directory: /Users/vikashkumar/Desktop/Civicly. Existing Python3.12 isolated backend/.venv; no dependency/image changes. Real commands require local FalkorDB and localhost subprocess access; provider guard mandatory and inherited by children. No full earlier suite or container lifecycle/live smoke run.

Final focused units (45PASS,3.76s):
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b17-final-accepted-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_frontend_views.py backend/tests/unit/test_api.py::test_openapi_exact_matrix_closed_models_and_no_deferred_stubs backend/tests/unit/test_api.py::test_expired_session_and_unknown_routes_are_closed backend/tests/unit/test_api.py::test_work_projection_uses_latest_recorded_assessment backend/tests/unit/test_api.py::test_request_identity_is_stable_source_bound_and_not_graph_disclosure backend/tests/unit/test_api.py::test_response_validation_is_sanitized_not_raw_data -q
```
Real shared journey (1PASS,20.55s before evidence-key-only correction; final B17-delivery-real.log records regenerated delivery proof):
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b17-path-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_frontend_runtime.py -xq
CIVICLY_TEST_REQUEST_LOG=/tmp/b17-delivery-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_frontend_runtime.py -xq
CIVICLY_TEST_REQUEST_LOG=/tmp/b17-story-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_frontend_runtime.py -xq
```
Both specification validators, once after final application/contracts edits (PASS):
```sh
CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/b17-spec-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec
```
Actual make expands backend/.venv/bin/python scripts/validate_blueprint.py then scripts/validate_handoff.py. Static checks are not substituted for integration.

Contract export and readonly audit:
```sh
PYTHONPATH=backend backend/.venv/bin/python docs/evidence/B17-export-contracts.py
PYTHONPATH=backend backend/.venv/bin/python docs/evidence/B17-audit-script.py
git diff --check
git apply --reverse --check docs/evidence/B17-changes.patch
```
The patch is against the actual accepted uncommitted B16/R working tree snapshot `/tmp/b17-baseline/files`, not the older Git HEAD. No commit/push/reset.

Earlier directly affected attempts used the same single integration selector and guard with `/tmp/b17-{real,real2,real3,real4,real5,real6,real7,real8,final-real,checked-real,cursor-real}-provider.jsonl`; corresponding B17 logs/zero-live proofs retained. First7real attempts failed, real8PASS; final-real and checked-real failed new meter/pagination checks, cursor-realPASS; path-realPASS. These are repetitions of one case, not extra distinct passing tests. Unit attempts used test_frontend_views.py alone with unit/unit2/unit3 guard names (initial1FAIL19PASS, then20PASS); final-unit40PASS/accepted-unit43PASS/final-accepted-unit45PASS progressively added directly affected checks. Failed real7traceback session value sanitized, never printed. Audit initial private-pattern check and source-graph evidence-key mismatch retained; corrected audit must PASS before delivery.

Runtime test subprocess exact entry:
```sh
PYTHONPATH=backend/test_guards:backend backend/.venv/bin/python -m app.api --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --at "$CONTROLLED_UTC" --port "$LOCAL_EPHEMERAL_PORT"
```
Test uses actual httpx streaming TCP, not buffered ASGI stream; cleans up Uvicorn subprocess in finally. Host configuration remains private. Manual server startup without test clock: see backend/API.md current B17 section. No bearer values in commands/evidence.
