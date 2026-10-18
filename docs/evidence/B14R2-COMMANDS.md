# B14-R2 focused commands

CWD `/Users/vikashkumar/Desktop/Civicly`; existing isolated Python3.12.1/local
FalkorDB6.0.2. No dependency/image change or provider call. Pre-edit baseline:
`sed 's/b14r-baseline/b14r2-baseline/' /tmp/b14r-snapshot.py > /tmp/b14r2-snapshot.py`
then `python3 /tmp/b14r2-snapshot.py`:1204public files snapshotted, ignored runtime
excluded. Patch uses actual working-tree baseline, preserving prior uncommitted work.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14r2-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_recurrence_scope.py -q --tb=short > docs/evidence/B14R2-unit.log 2>&1
```
7PASS0.44s. Explicit MOCK bounded graph readers: repeat refresh, unknown ACTIVE/ENDED
additions rejected, changed journal hash/historical issue rejected, retained ordinary
resume and ended-only reopen guard.5new +2existing cases, no mocked integration claim.

```sh
CIVICLY_OPERATIONS_EVIDENCE_PREFIX=B14R2 CIVICLY_B14R_CHECKPOINT_PROOF=1 CIVICLY_TEST_REQUEST_LOG=/tmp/b14r2-real-provider.jsonl backend/.venv/bin/python -m pytest 'backend/tests/integration/test_execution_runtime.py::test_actual_three_issue_completion_verification_and_water_recurrence[WATERLOGGING]' -q --tb=short > docs/evidence/B14R2-real.log 2>&1
```
1PASS21.52s. Reuses one existing setup, old assertions retained. First recurrence
adoption, actual MCP reads new incident/report, then legitimate authored CONTEXT
Evidence update, second explicit same-thread resume with mandatory actual fresh
READ. Active episode correct, old and first-resume checkpoints unchanged via public
SDK ID reads; scope links/domain events unchanged, only one scope adoption audit.
Two wakes/three cumulative actual MCP executions. SCRIPTED selections, actual
FalkorDB/B08/B09/MCP/LangGraph/Saver; no genuine Gemini claim. Prior B14/B14R proofs
not overwritten (B14R2 evidence prefix). No graph repairs/quarantine clearance.

```sh
make test-spec > docs/evidence/B14R2-spec.log 2>&1
```
Both validatorsPASS once after final source/test change. Final8distinctPASS,
0FAIL/0SKIP.2ordinary pytest+inherited-child interlocks0external Gemini/countTokens/
0unexpected. No waste/remedial/B14/B13/full regression/live smoke/lifecycle rerun.

```sh
git diff --check
git apply --reverse --check docs/evidence/B14R2-changes.patch
```
Exact source/append-only tracker diff, retained evidence hashes/security/provider
proof checks recorded in B14R2-file-audit.json. No commit/push/archive/B15 work.
