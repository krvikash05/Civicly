# B12-R2 exact focused commands

Working directory `/Users/vikashkumar/Desktop/Civicly`; isolated Python3.12 and retained local FalkorDB6.0.2. No installation, live model/provider, full regression, remedial scenario or container lifecycle command.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b12r2-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_planning_commit_recovery.py backend/tests/unit/test_planning_remediation.py::test_static_feedback_redaction_and_recovery backend/tests/unit/test_planning_remediation.py::test_planner_does_not_acknowledge_unsafe_failures_as_rejected -q > /tmp/b12r2-unit.txt 2>&1
```
16unitPASS/0FAIL/0SKIP0.98s:6new commit/replay/recovery cases +10directly affected existing feedback/recovery cases. No graph success claimed by stubs; sensitive sentinel inputs not copied into diagnostics.

```sh
CIVICLY_PLANNING_EVIDENCE_PREFIX=B12R2 CIVICLY_TEST_REQUEST_LOG=/tmp/b12r2-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_planning_postcommit_recovery.py 'backend/tests/integration/test_planning_runtime_store.py::test_actual_drafts_all_issues_version_replay_and_ack_loss[WATERLOGGING]' -q --durations=5 > /tmp/b12r2-real.txt 2>&1
```
Historical1healthyPASS/1newtest-assertionFAIL/0SKIP20.21s. The mismatch actually raised correct RecoveryRequired, but pytest's end-anchored regex included a LangGraph task note and failed. Relaxed only that test matcher and separately asserted exact exception string. Application unchanged. Earlier isolated plan/quarantine left intact; no failed wake retried or reset. Original healthy case passed unchanged, using its same B12-first request for injected acknowledgment loss and replay; its explicit v2 test is separate from the fault graph.

```sh
CIVICLY_PLANNING_EVIDENCE_PREFIX=B12R2 CIVICLY_TEST_REQUEST_LOG=/tmp/b12r2-mismatch-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_planning_postcommit_recovery.py -q --durations=5 > /tmp/b12r2-mismatch.txt 2>&1
```
1realPASS/0FAIL/0SKIP12.21s, only corrected failing case in a fresh isolated graph. Actual B11 SDK/citations, official MCP READ, scripted model, native draft commit, LangGraph/FalkorDBSaver and wake quarantine. Mismatch affects only returned ACK hash; stored payload untouched. Read-only Store.get inspection verifies retained native/companion/receipt binding; no create/replay/resume/repair/clear-quarantine call on that fault case.

```sh
make test-spec > /tmp/b12r2-spec.txt 2>&1
```
Both specification validatorsPASS once after final application/test changes; canonical source/schema/policy parity passes. No contract/schema/migration changed. Static validators are not runtime proof.

```sh
backend/.venv/bin/python /tmp/b12r2-snapshot.py
backend/.venv/bin/python /tmp/b12r2-audit.py
git diff --check
git apply --reverse --check docs/evidence/B12R2-changes.patch
```
Pre-edit public-file snapshot; final exact working-tree diff, accepted evidence/assertion/immutable-source retention, actual private-value scan (no values logged), zero-provider proof/unchanged accepted spending and no orphan MCP processes. HEAD predates accepted uncommitted phases, so B12R2 patch is intentionally against the immediate pre-B12-R2 working tree.

Final18distinctPASS(16unit/2real),0unresolvedFAIL/0SKIP. Initial failed test assertion retained, not counted as additional distinct coverage. Three inherited ordinary pytest/child provider interlock proofs show0external Gemini/countTokens/0unexpected attempts. No genuine LLM autonomy claim. For human reproduction use the exact single mismatch-case command above; each run creates a new isolated graph and leaves its quarantine set. Inspect B12R2-postcommit-recovery.json without any replay or DB reset.
