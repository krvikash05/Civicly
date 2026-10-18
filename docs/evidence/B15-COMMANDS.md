# B15 exact commands and outcomes

Working directory `/Users/vikashkumar/Desktop/Civicly`; existing isolated Python3.12 environment/local FalkorDB. Baseline: `python3 /tmp/b15-snapshot.py`,1215 public repository files copied to `/tmp/b15-baseline`; ignored runtime/secrets excluded. Existing accepted work is uncommitted; B15 patch is relative to this actual baseline, not stale HEAD. No commit/push.

## Ordinary tests (provider interlock inherited by children)

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b15-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_events.py -q --tb=short > docs/evidence/B15-unit.log 2>&1
```
13PASS0.15s (initial pure unit selection).

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b15-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_event_delivery.py -q --tb=short > docs/evidence/B15-real-initial.log 2>&1
```
2setupERROR1.32s: sandbox denied localhost socket before test setup. No simulated pass. Retried the same command with local-network sandbox permission, changing output to `docs/evidence/B15-real.log`:1PASS/1FAIL11.67s. Real process-death/restart/public cursor PASS. Second test passed retry/replay then fixture `common()` positional-argument mistake; corrected only fixture call. First failed setup guard path reused by retry; subsequent retained proof is B15-real-zero-live.json, not a separate claim of first-run guard preservation.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b15-focused-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_event_delivery.py::test_claim_case_fencing_retries_invalid_and_uncertain_dispatch backend/tests/integration/test_event_runtime.py backend/tests/integration/test_agent_safety.py::test_concurrent_lease_denial_and_corrupt_checkpoint -q --tb=short > docs/evidence/B15-focused.log 2>&1
```
2PASS/1FAIL37.01s. Corrected retry/invalid test and existing lease/corrupt-checkpoint regression PASS. New actual recurrence/MCP/Saver case reached both wakes and reconciliation, but fixture compared public state view with complete SDK channel map. Corrected assertion to compare original saved SDK checkpoint (stronger byte/content preservation).

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b15-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_events.py backend/tests/integration/test_event_delivery.py::test_real_racing_claims_and_existing_quarantine backend/tests/integration/test_event_runtime.py -q --tb=short > docs/evidence/B15-final-focused.log 2>&1
```
16PASS33.41s:14then-current unit cases and2actual integrations. Concurrent DB claimants/retained quarantine, corrected recurrence checkpoint/ACK recovery/two resumes/coalescing PASS. Three existing dependency deprecation warnings.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b15-final-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_events.py -q --tb=short > docs/evidence/B15-final-unit.log 2>&1
make test-spec > docs/evidence/B15-spec.log 2>&1
```
20unitPASS0.88s; added routing cases and direct safe-vs-recovery consumption-marker cases. Both static validators PASS. This specification run preceded the final narrow checkpoint-read exception normalization below; final validators are run separately after that final source change.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b15-probe-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_events.py::test_probe_corrupt_checkpoint_is_sanitized_recovery -q --tb=short > docs/evidence/B15-probe.log 2>&1
```
1PASS0.95s. Mock SDK read failure becomes bounded RecoveryRequired inside existing ownership, not a raw exception escaping expired-claim reconciliation. Actual quarantine/ownership behavior separately exercised above. Does not claim mocked SDK is integration evidence.

Final affected-path recheck and both final validators are recorded below with observed results. No broad regression, other issue scenarios, lifecycle or live smoke runs. All external Gemini/countTokens prohibited by ordinary pytest and child sitecustomize. Provider proof files preserve zero-call counters; paid ledger compared read-only against accepted historical requests.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b15-last-runtime-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_event_runtime.py -q --tb=short > docs/evidence/B15-last-runtime.log 2>&1
make test-spec > docs/evidence/B15-final-spec.log 2>&1
```
Final affected real path1PASS27.55s,3existing dependency deprecation warnings. Both final specification validatorsPASS once after last application/test/contract/validator change. One earlier static pass is retained in B15-spec.log; total two invocations of each validator during B15, no hidden failed specification run. Final26distinctPASS(21unit/5real),0unresolvedFAIL/0SKIP; repeat invocations are not counted as distinct tests.

```sh
PYTHONPATH=backend/test_guards:backend CIVICLY_TEST_NO_LIVE=1 backend/.venv/bin/python docs/evidence/B15-audit-script.py > docs/evidence/B15-audit.log 2>&1
git diff --check
git apply --reverse --check docs/evidence/B15-changes.patch
```
Read-only runtime retention/security auditPASS. First audit rejected an attempted city-sized AnalysisLimits export (120/200 analytical caps); replaced audit-only export with explicit bounded administrative858node/1246edge reads without changing algorithm/runtime limits. Second audit used the wrong B01 probe property `phase`; corrected to the existing probe's documented `task`. Both failed audit logs retained (B15-audit-initial.log/B15-audit-probe-field.log); neither wrote DB data. Final audit verifies exact accepted city content hash, original B01 probe, B12R2 quarantine/singleplan and B14R2 episodes; migrations/data/pins/MCP/oldtests/oldevidence unchanged. No resets, graph repairs, volume deletion or container lifecycle.

Security scans include changed/new public source, evidence and generated patch, known actual private values plus private-key/session patterns; no credentials exported. Provider proof snapshots: B15-{unit,real,focused,final-focused,final-unit,probe,last-runtime}-zero-live.json.8pytest attempts total including original sandbox failure,7retained interlock snapshots (original denied setup path reused for its authorized retry).0external requests/0unexpected attempts in all retained proofs; readonly paid ledger exactly equals original2requests,0open sessions/holds. Scripted MCP choices are not live Gemini acceptance.
