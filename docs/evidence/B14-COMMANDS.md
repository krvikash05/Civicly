# B14 exact significant commands and results

Working directory: `/Users/vikashkumar/Desktop/Civicly`. Python3.12.1 isolated
`backend/.venv`; no package/image changes. Local6379 tests require approved sandbox
network access. Every ordinary pytest invocation/child has Gemini/countTokens
interlock. Counts below overlap; deduplicated final total is41 (30unit/11real).
No full suites, container lifecycle, paid smoke, B15, API or frontend runs.

Pre-edit snapshot: `sed 's/b13-baseline/b14-baseline/' /tmp/b13-snapshot.py > /tmp/b14-snapshot.py`,
then `python3 /tmp/b14-snapshot.py`:1119public files copied/hashed, ignored runtime
excluded. Git HEAD is an older accepted baseline; B14 patch compares to this actual
pre-B14 working tree, preserving accepted uncommitted B11–B13 work.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_execution_policy.py -q > docs/evidence/B14-unit.log 2>&1
```
18PASS0.11s.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14-real1-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_execution_runtime.py -x -q > docs/evidence/B14-real1.log 2>&1
```
0PASS/1ERROR1.73s: sandbox blocked localhost socket, not mocked database success.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14-real2-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_execution_runtime.py -x -q > docs/evidence/B14-real2.log 2>&1
PYTHONPATH=/tmp:backend CIVICLY_TEST_REQUEST_LOG=/tmp/b14-debug-provider.jsonl backend/.venv/bin/python -m pytest -p b14_debug 'backend/tests/integration/test_execution_runtime.py::test_actual_three_issue_completion_verification_and_water_recurrence[WATERLOGGING]' -x -q --tb=short > docs/evidence/B14-debug.log 2>&1
```
Each1FAIL: first12.45s; diagnostic reproduces missing planned B09 journal reference.
Diagnostic prints exception type/frame names/lines only. B14 compiler corrected to
validate new unverified operation journal references atomically, without modifying
B03. Initial full pytest traceback contained an ephemeral isolated-test session;
public logs redact it. Subsequent runs use `--tb=short`, known secret/session audit
checks final public evidence. No private production credential recorded.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14-real3-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_execution_runtime.py -x -q --tb=short > docs/evidence/B14-real3.log 2>&1
```
1FAIL12.50s: reaches recurrence, B08 planner assumes persisted journal. Narrow strict
planned-journal input added; no recurrence/dedup semantics duplicated or relaxed.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14-real4-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_execution_runtime.py -x -q --tb=short > docs/evidence/B14-real4.log 2>&1
```
5PASS/1FAIL60.22s. Pass: three outcomes/water recurrence-memory, contradiction,
failed attempt. Failure: fault-injection fixture passed whole record to patch-only
update_node; fixture corrected to status patch, no application guard weakened.

Historical B13 tests run verbatim with Path.write_text adapter redirecting only
`docs/evidence/B13-*` output to `B14-regression-B13-*`. Plugin copied alongside this
record (`B14-evidence-plugin.py`); to reproduce this exact command copy it to
`/tmp/b14_evidence.py`. No old JSON/test log overwritten.

```sh
PYTHONPATH=/tmp:backend CIVICLY_TEST_REQUEST_LOG=/tmp/b14-focused-provider.jsonl backend/.venv/bin/python -m pytest -p b14_evidence backend/tests/integration/test_execution_runtime.py::test_actual_execution_denials_replay_and_uncertain_completion backend/tests/integration/test_execution_runtime.py::test_actual_road_water_dependency_progress_and_native_lifecycle backend/tests/integration/test_operations_runtime.py::test_actual_approval_order_scope_idempotency_and_competing_updates backend/tests/integration/test_operations_runtime.py::test_actual_stale_sources_assessments_owners_supersession_and_rejection backend/tests/integration/test_operations_runtime.py::test_actual_conditional_approval_retains_unmet_gate_no_order backend/tests/integration/test_operations_runtime.py::test_actual_b12_checkpoint_survives_approval_and_rejects_native_rollback -q --tb=short > docs/evidence/B14-focused.log 2>&1
```
6PASS65.38s. Two new B14 + four directly affected accepted B13/B12 cases.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14-auth-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_operations.py -q --tb=short > docs/evidence/B14-auth-unit.log 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/b14-unit-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_execution_policy.py backend/tests/unit/test_operations.py -q --tb=short > docs/evidence/B14-unit-final.log 2>&1
```
Initial10PASS/2FAIL10.56s: accepted role test assumed B13-only permissions while
iterating current registry. Expand only expected analyst/lead sets for explicit
B14 commands; retain all assertions/admin/approver denials and closed B13 Update.
Final30PASS11.45s. Also strengthen UNKNOWN/temporal policy branches.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14-recurrence-final-provider.jsonl backend/.venv/bin/python -m pytest 'backend/tests/integration/test_execution_runtime.py::test_actual_three_issue_completion_verification_and_water_recurrence[WATERLOGGING]' -q --tb=short > docs/evidence/B14-recurrence-final.log 2>&1
```
1PASS10.96s after final recurrence window+exact evidence binding and current memory
gap wording correction; includes actual completion/no-opportunity/verified/reopen.

```sh
make test-spec > docs/evidence/B14-spec.log 2>&1
```
Both validators PASS; preliminary pass before final review identified an additional
same-meaning assessment/gate interaction. Preserved rather than represented as final.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14-progress-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_execution_runtime.py::test_actual_execution_denials_replay_and_uncertain_completion -q --tb=short > docs/evidence/B14-progress-final.log 2>&1
make test-spec > docs/evidence/B14-spec-final.log 2>&1
```
Final targeted case checks same-meaning assessment→explicit blocked-work resume with
original immutable gates; truthful evidence-only proof; denials/ACK-loss/replay and
persistent outcome. Final results in B14-test-summary.json and raw logs. Final
validators run once each after last source edits; no test-suite broadening.

```sh
backend/.venv/bin/python /tmp/b14-audit.py > docs/evidence/B14-audit.log 2>&1
```
Read-only audit. First attempt assertion used wrong expected module encoding60200;
actual60002 = FalkorDB6.0.2. Correct audit expectation, preserve B14-audit-initial.log,
rerun read-only check. Source dataset, original B13 graph/B12R2 quarantine and actual
live-spend ledger checked unchanged. Script copied as B14-audit-script.py; its
pre-edit hash baseline requires `/tmp/b14-baseline`. Final file/diff checks recorded
in B14-file-audit.json.

```sh
git diff --check
git apply --reverse --check docs/evidence/B14-changes.patch
```
Final results in B14-file-audit.json. No commit/push/archive/reset/drop performed.

Final progress attempt: B14-progress-final.log1FAIL10.97s after the new legitimate
resume advanced the WorkOrder hash; stale denial fixture correctly hit CAS first.
Refresh only fixture expected_hash, then run:

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14-progress-corrected-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_execution_runtime.py::test_actual_execution_denials_replay_and_uncertain_completion -q --tb=short > docs/evidence/B14-progress-corrected.log 2>&1
```
1PASS11.63s. Same-meaning reassessment/resume, immutable gate identity, truthful
proof and actual uncertain-completion/replay all exercised. Final specification
command above follows this final test-source correction.12ordinary pytest/child
interlock proofs,0sent/0unexpected requests. Historical failures not counted as
passing test executions; final41distinct cases passing,0unresolvedFAIL/0SKIP.
