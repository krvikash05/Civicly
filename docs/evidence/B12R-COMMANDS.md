# B12-R exact executed test commands

Working directory `/Users/vikashkumar/Desktop/Civicly`. Python3.12 isolated backend/.venv; existing local FalkorDB6.0.2/GraphRAG SDK1.4.0. No installs, paid providers, container lifecycle, retained-city changes or automatic canonical source import.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b12r-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_planning_remediation.py backend/tests/unit/test_planning.py -q > /tmp/b12r-unit.txt 2>&1
```
29PASS/0FAIL/0SKIP,0.86s. New closed guards/feedback + directly affected existing DAG/hash/monitoring/schema checks.

```sh
CIVICLY_PLANNING_EVIDENCE_PREFIX=B12R CIVICLY_TEST_REQUEST_LOG=/tmp/b12r-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_planning_remediation_runtime.py backend/tests/integration/test_planning_agent.py backend/tests/integration/test_planning_runtime_store.py::test_resolver_unknown_conflicting_owner_stale_revoked_and_reference_denials 'backend/tests/integration/test_planning_runtime_store.py::test_actual_drafts_all_issues_version_replay_and_ack_loss[WATERLOGGING]' -q --durations=10 > /tmp/b12r-real.txt 2>&1
```
Historical6PASS/3FAIL/0SKIP,68.73s. Water/waste new-source citations absent because B11 correctly excludes unreviewed sources; road fixture lacked explicit utility topology for its alternative. Existing ownership/version/revocation/replay and invalid/recovery MCP cases passed. Metadata corrected to truthful automated author self-review (not human/government approval). B11 retrieval filter retained. Road later fixed by explicit authored isolated test edge, never proximity inference.

```sh
CIVICLY_PLANNING_EVIDENCE_PREFIX=B12R CIVICLY_TEST_REQUEST_LOG=/tmp/b12r-remediation-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_planning_remediation_runtime.py::test_supported_remediation_conditional_and_guards backend/tests/integration/test_planning_agent.py -q --durations=10 > /tmp/b12r-remediation.txt 2>&1
```
Historical5PASS/1roadfixtureFAIL/0SKIP,49.00s. Source cases corrected; directly affected report/finding hash guards and supervisor policy context exercised, including valid/invalid/dependency actual MCP+Saver. Road failure retained, then only road rerun.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b12r-affected-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_planning_remediation.py backend/tests/unit/test_agent_models.py backend/tests/unit/test_agent_context.py -q > /tmp/b12r-affected.txt 2>&1
```
34PASS/0FAIL/0SKIP,0.82s;14 overlap earlier new cases. Bounded Feedback type/state/context compatibility.

```sh
CIVICLY_PLANNING_EVIDENCE_PREFIX=B12R CIVICLY_TEST_REQUEST_LOG=/tmp/b12r-road-provider.jsonl backend/.venv/bin/python -m pytest 'backend/tests/integration/test_planning_remediation_runtime.py::test_supported_remediation_conditional_and_guards[ROAD_DAMAGE]' -q --durations=5 > /tmp/b12r-road.txt 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/b12r-recovery-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_planning_remediation.py::test_planner_does_not_acknowledge_unsafe_failures_as_rejected -q > /tmp/b12r-recovery.txt 2>&1
```
1realPASS/0FAIL/0SKIP7.11s;3unitPASS/0FAIL/0SKIP0.81s. Unit deliberate uncertain-write/lease/storage faults propagate sanitized RecoveryRequired, never false PLAN_DRAFT_REJECTED acknowledgment; not real injected DB write failures.

```sh
make test-spec > /tmp/b12r-spec.txt 2>&1
```
Both blueprint and handoff validatorsPASS once, including canonical data/source/planning static checks. Static validation never replaces runtime proof.

Fresh child invoked by actual MCP test (not separately rerun):
```sh
PYTHONPATH=backend backend/.venv/bin/python -m tests.b12_worker PRIVATE_TEST_PROFILE THREAD_ID OUTPUT_PATH
```
Actual Saver/current-plan receipt/hash/source proof read after fresh interpreter, then bounded resume retaining one plan. Python child inherits ordinary provider interlock.

Audit commands:
```sh
backend/.venv/bin/python /tmp/b12r-snapshot.py
backend/.venv/bin/python /tmp/b12r-evidence.py
backend/.venv/bin/python /tmp/b12r-audit.py
git diff --check
git apply --reverse --check docs/evidence/B12R-changes.patch
```
Public snapshot/audit includes source hashes, unchanged accepted evidence/migrations/frozen fixtures/locks, preserved old test assertions, actual private-value scan (never printed), zero-provider proofs and unchanged accepted live ledger. Exact narrow patch compares pre-B12-R working tree: GitHEAD predates B11, so a broad HEAD diff would mix accepted phases.

Final61distinctPASS:52unit/9real;0unresolvedFAIL/0SKIP. Historical4failed case executions across2batches retained, not concealed or counted as extra distinct cases. No full regression, paid call, lifecycle or B13 action. Initial B11 SDK repeated-index log warnings are vendor idempotent-index probes; readiness/runtime tests determine success.
