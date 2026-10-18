# B13 exact commands and observations

Working directory /Users/vikashkumar/Desktop/Civicly; isolated Python3.12, actual local FalkorDB6.0.2/B11SDK/MCP/Saver. No package install, paid provider, container lifecycle, full regression or field execution. All ordinary pytest/children have inherited external Gemini/countTokens block.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b13-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_operations.py -q > /tmp/b13-unit.txt 2>&1
```
11unitPASS9.05s All skips0. Batch overlaps do not add distinct cases.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b13-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_operations_runtime.py -q --durations=5 > /tmp/b13-real.txt 2>&1
```
3realPASS27.75s All skips0. Batch overlaps do not add distinct cases.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b13-gates-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_operations.py::test_conditional_approval_is_not_execution_clearance backend/tests/integration/test_operations_runtime.py::test_actual_conditional_approval_retains_unmet_gate_no_order backend/tests/integration/test_operations_runtime.py::test_actual_b12_checkpoint_survives_approval_and_rejects_native_rollback backend/tests/unit/test_planning_commit_recovery.py -q --durations=5 > /tmp/b13-gates.txt 2>&1
```
8PASS/1FAIL21.10s. Lease check correctly refused decode outside wake. Test updated to acquire existing ownership context. All skips0. Batch overlaps do not add distinct cases.

```sh
CIVICLY_PLANNING_EVIDENCE_PREFIX=B13 CIVICLY_TEST_REQUEST_LOG=/tmp/b13-final-affected-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_operations_runtime.py::test_actual_stale_sources_assessments_owners_supersession_and_rejection backend/tests/integration/test_planning_postcommit_recovery.py -q --durations=5 > /tmp/b13-final-affected.txt 2>&1
```
2realPASS22.69s. Revoked-source approval/rejection and accepted B12R2 real recovery. All skips0. Batch overlaps do not add distinct cases.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b13-auth-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_operations.py::test_signed_sessions_expiry_logout_revocation_and_forgery backend/tests/unit/test_operations.py::test_no_implicit_role_bypass -q > /tmp/b13-auth-final.txt 2>&1
```
5unitPASS9.04s, overlapping auth cases after closed token syntax and DB connection-lifetime refinement. All skips0. Batch overlaps do not add distinct cases.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b13-checkpoint-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_operations_runtime.py::test_actual_b12_checkpoint_survives_approval_and_rejects_native_rollback -q --durations=5 > /tmp/b13-checkpoint.txt 2>&1
```
1FAIL10.92s. New graph authorization checked during construction before active scope; same cause as next batch. All skips0. Batch overlaps do not add distinct cases.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b13-final-write-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_operations_runtime.py::test_actual_approval_order_scope_idempotency_and_competing_updates backend/tests/integration/test_operations_runtime.py::test_actual_ack_loss_order_replay_without_duplicate -q --durations=5 > /tmp/b13-final-write.txt 2>&1
```
2FAIL19.05s. Dispatch authorization moved from constructor to operations/read/replay under existing active scope; no pattern-only active-B10 permission. All skips0. Batch overlaps do not add distinct cases.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b13-final-runtime-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_operations_runtime.py -q --durations=5 > /tmp/b13-final-runtime.txt 2>&1
```
5realPASS51.17s final B13 cases after scoped fixes. All skips0. Batch overlaps do not add distinct cases.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b13-ownership-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_operations_runtime.py::test_actual_approval_order_scope_idempotency_and_competing_updates -q --durations=5 > /tmp/b13-ownership-final.txt 2>&1
```
1realPASS11.04s; added wrong-department update denial, fresh-process authentication and temporal monotonicity checks. All skips0. Batch overlaps do not add distinct cases.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b13-cross-department-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_operations_runtime.py::test_accepted_road_water_dag_approval_and_dependency_boundary backend/tests/unit/test_operations.py::test_signed_sessions_expiry_logout_revocation_and_forgery -q --durations=5 > /tmp/b13-cross-department.txt 2>&1
```
2PASS11.70s(1real/1unit); specific accepted road→utility DAG required private utility lead seed. All skips0. Batch overlaps do not add distinct cases.

Final25distinctPASS(18unit/7real),0unresolvedFAIL/0SKIP:12B13units+6B12R2units;6B13real+1acceptedB12R2real. Four historical failed case executions retained (lease1+scope1+scope2); no deleted tests/assertions or hidden failures. Final runtime includes affected B13 cases only, not all B12 or remedial suites. Targeted road inspection DAG added for concrete missing assignee risk.

Specification commands:
```sh
make test-spec > /tmp/b13-spec.txt 2>&1
backend/.venv/bin/python scripts/validate_handoff.py > /tmp/b13-spec-handoff-corrected.txt 2>&1
```
BlueprintPASS once incl B13 parity. Initial handoff failed IndentationError in newly added hook (not domain/schema failure); fixed only indentation and reran handoff alonePASS. Both final validators pass; historical initial log retained. No redundant runtime rerun for text/hook correction.

Actual private setup, no credentials displayed:
```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.services.operations configure
backend/.venv/bin/python /tmp/b13-extend-auth.py
backend/.venv/bin/python /tmp/b13-auth-runtime.py
```
Initial6account setup; explicit additive missing utility lead extension preserved signing key/passwords/sessions. Final7accounts/fourroles, DB/credentials0600. Login/analyst-approval denial/logout verified, sanitized proof B13-auth-runtime.json. Runtime files ignored, never copied to review evidence. No canonical city writes.

Fresh child invoked by actual flow test (not separately rerun):
```sh
PYTHONPATH=backend backend/.venv/bin/python -m tests.b13_worker PRIVATE_PROFILE WORK_ORDER_ID OUTPUT_PATH
```
Auth path/token supplied through private stdin pipe, not command arguments or output; inherited provider interlock. Actual SQLite signed-session validation and native order/operation/events read in new interpreter. No lifecycle command needed: existing one-statement graph consistency and retained storage mechanism unchanged.

Audit:
```sh
backend/.venv/bin/python /tmp/b13-snapshot.py
backend/.venv/bin/python /tmp/b13-audit.py
git diff --check
git apply --reverse --check docs/evidence/B13-changes.patch
```
Exact patch against immediate pre-B13 working tree; HEAD predates accepted phases. Audit prior evidence/source fixtures/migrations/dependency locks, old assertions, actual private values (no values printed), accepted spend ledger, original quarantine, no MCP process leaks, real0005OPERATIONAL status/order events.

Human minimum reproduction: run only first real flow test from ownership-final command; expect exact approval/order/replay/department denials/CAS/fresh-process auth with no field execution. Or read B13-flow.json/B13-denials.json/B13-conditional.json/B13-checkpoint-compatibility.json without writes. No reset/clearing quarantine needed.
