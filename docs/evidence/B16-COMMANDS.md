# B16 exact commands and observed results

CWD `/Users/vikashkumar/Desktop/Civicly`. Existing Python3.12.1, FastAPI0.143.3/Pydantic2.14.1/Uvicorn0.54.0; no dependency install/pin/image changes. Read user authorization attachment and mandatory docs/contracts/trackers before code; DEC-060 recorded before implementation. Baseline:

```sh
sed 's/b15-baseline/b16-baseline/' /tmp/b15-snapshot.py > /tmp/b16-snapshot.py
python3 /tmp/b16-snapshot.py
```
1262public files snapshotted, ignored private/runtime files excluded. Patch compares actual accepted working tree, not stale HEAD; no commit/push. Official FastAPI response-model/security docs read and APIs exercised, not copied blindly. `PYTHONPATH=backend backend/.venv/bin/python -c 'from app.api.coverage import ROUTES; print(len(ROUTES))'` and generated OpenAPI spikes checked43then44operations as minimal hypothesis history route added. Contract generation: `PYTHONPATH=backend backend/.venv/bin/python /tmp/b16-contracts.py`; exact script retained as B16-export-contracts.py (run from repository root to reproduce schemas/coverage/OpenAPI).

## Exact focused pytest invocations (ordinary interlock, inherited children)

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_api.py -q --tb=short > docs/evidence/B16-unit.log 2>&1
```
47PASS/1FAIL2.91s: test treated a deferred GET path as forbidden for all methods, despite B16POST on same path. Corrected assertion to method+path; no placeholder endpoint introduced.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_api_runtime.py -q --tb=short > docs/evidence/B16-real.log 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-final-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_api.py -q --tb=short > docs/evidence/B16-final-unit.log 2>&1
```
Real1PASS30.46s; corrected unit48PASS2.79s. First actual ASGI/services/DB/worker/MCP/Saver/TCP host workflow passed, not proof all later changes were already verified.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-final-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_api_runtime.py -q --tb=short > docs/evidence/B16-final-real.log 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-extra-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_api.py -q --tb=short > docs/evidence/B16-extra-unit.log 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-latest-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_api_runtime.py -q --tb=short > docs/evidence/B16-latest-real.log 2>&1
```
Expanded unit53PASS2.79s. Two fresh actual fixtures FAIL17.04s/20.89s at first workerMCP call: CONFLICT, durable RECOVERY_REQUIRED/checkpoint/quarantine. Both retained, no repair/retry/clearance. Read-only checkpoint/shared trace inspection (`/tmp/b16-failed-proof.py`) proved identical execution ID already belonged to another source graph; sanitized evidence B16-worker-failed-diagnostic.json. B16 actor+key request IDs lacked source binding. Fixed new B16 host request digest to include exact configured source graph; opaque IDs only, no graph selector/exposure or changes to B15/MCP/SDK identity policy. This is an implementation defect caught by repeat testing, not a mocked/network error.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-fixed-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_api_runtime.py -q --tb=short > docs/evidence/B16-fixed-real.log 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-guard-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_api.py -q --tb=short > docs/evidence/B16-guard-unit.log 2>&1
```
Corrected actual workflow1PASS30.32s; expanded unit56PASS3.22s. Added stable/source-distinct request identity, missingsetup503, sanitized invalidoutput cases.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-final-checks-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_api.py backend/tests/unit/test_operations.py::test_signed_sessions_expiry_logout_revocation_and_forgery backend/tests/unit/test_operations.py::test_exact_scope_closed_and_canonical backend/tests/unit/test_operations.py::test_conditional_approval_is_not_execution_clearance -q --tb=short > docs/evidence/B16-final-checks.log 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-final-runtime-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_api_runtime.py -q --tb=short > docs/evidence/B16-final-runtime.log 2>&1
make test-spec > docs/evidence/B16-spec.log 2>&1
```
59unitPASS5.87s (56B16+3directly affected accepted auth/binding/gate regressions); actual1PASS29.64s. Both specification validatorsPASS before final projection/test audit refinements; retained as pre-final evidence, not concealed. Existing Swig/Pydantic dependency deprecation warnings, no application warning or provider call.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-projection-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_api.py::test_work_projection_uses_latest_recorded_assessment -q --tb=short > docs/evidence/B16-projection.log 2>&1
PYTHONPATH=backend/test_guards:backend CIVICLY_TEST_NO_LIVE=1 backend/.venv/bin/python /tmp/b16-projection-proof.py > docs/evidence/B16-final-projection.log 2>&1
make test-spec > docs/evidence/B16-final-spec.log 2>&1
```
3new mock-input projection unitsPASS0.25s: MONITORING/RESOLUTION_VERIFIED/RECURRENCE_DETECTED distinguished using latest actual time+ID. Additional real retainedDB read under a fresh private realAuth session validates final COMPLETED+MONITORING DTO, no graph writes. Both validatorsPASS after final application/schema change. This source-final static pass preceded the final test-only ACK-loss fixture correction below.

```sh
PYTHONPATH=backend/test_guards:backend CIVICLY_TEST_NO_LIVE=1 backend/.venv/bin/python docs/evidence/B16-audit-script.py > docs/evidence/B16-audit.log 2>&1
```
Initial read-only audit caught a test defect: injected post-service error reused an existing idempotent evaluation receipt, so no **new operation** existed under uncertain requestID. Prior proof B16-pre-audit-http-runtime.json/failed B16-audit-initial.log retained; not claimed as new-commit evidence. Corrected fixture advances controlled evaluation window before fault, asserts correlated operation is actually stored, then confirms API replay stays recovery-required/no duplicate order. Application logic unchanged.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-commit-proof-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_api_runtime.py -q --tb=short > docs/evidence/B16-commit-proof.log 2>&1
```
Final observed result and final static/audit checks recorded below. Count distinct cases, never sum repeated invocations. All failed attempts and quarantines retained. No full service suite, other issue catalogs/scenario/lifecycle/paid smoke runs.11pytest/child zero-call proofs plus final commit-proof invocation archived separately; original historical spend ledger verified read-only.

Final commit-proof1PASS32.04s,3existing dependency deprecation warnings. Actual new operation exists under HTTP correlation, transport remainsDISPATCHING/recovery-required, client replay does not invoke service, exactly1workorder. B16-http-runtime.json/B16-network.json now refer to this corrected fixture. Earlier pre-audit proof remains separately identified.

```sh
make test-spec > docs/evidence/B16-final-spec.log 2>&1
PYTHONPATH=backend/test_guards:backend CIVICLY_TEST_NO_LIVE=1 backend/.venv/bin/python docs/evidence/B16-audit-script.py > docs/evidence/B16-audit.log 2>&1
git diff --check
git apply --reverse --check docs/evidence/B16-changes.patch
```
Both final validatorsPASS **once after the last test-only correction**. Total three `make test-spec` invocations during B16 (pre-final B16-spec.log, source-final B16-source-final-spec.log, final B16-final-spec.log); no hidden validator failures or repeated broad regression. Final63distinctPASS:59new B16unit+3existing auth/binding/gate unit+1real integrated fixture.0unresolvedFAIL/0SKIP. Actual TCPproof is part of the real test, not an extra pytest case. Administrative actual retainedDB/readAuth projection proof additional, not counted as another integration test.

12ordinary pytest+Python-child interlock proofs all0external Gemini/countTokens/0unexpected. Read-only spending ledger remains exactly the accepted2historicalrequests, no open holds/sessions. No live provider construction/authorization. AuditPASS1262prior files retained/858earlier evidence/104earlier testfiles byte-identical, registry/migrations/data/dependencies/MCP/runtime/services unchanged. Exact city full content hash, B01 probe, original B12R2quarantine/singleplan and B14R2episode history preserved. New failed B16quarantine retained. Secret scan covers changed/new public files including patch, known actual .env/private-runtime values and key/session patterns; no private values output.

For independent reproduction use commands in backend/API.md. No need to rerun every intermediate attempt or open old failed graphs. On failure share sanitized B16logs/providerproofs only; never .env/.runtime/private profiles/sessions. Actual server startup uses `PYTHONPATH=backend backend/.venv/bin/python -m app.api --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --port 8000`; host flags are private local capabilities, no API config endpoint. Ctrl-C stops API; worker remains separate and follows B15proof-aware stop/restart. STOP after B16.
