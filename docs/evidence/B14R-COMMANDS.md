# B14-R exact significant commands/results

CWD `/Users/vikashkumar/Desktop/Civicly`, isolated Python3.12.1, existing local
FalkorDB6.0.2. No dependencies/images changed, no live provider. Source baseline:
`sed 's/b14-baseline/b14r-baseline/' /tmp/b14-snapshot.py > /tmp/b14r-snapshot.py`
then `python3 /tmp/b14r-snapshot.py`:1174public files copied/hashed, ignored runtime
excluded. Patch compares actual pre-B14-R working tree, not older Git HEAD.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14r-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_waste_post_pickup.py backend/tests/unit/test_execution_policy.py -k 'post_pickup or WASTE_ACCUMULATION or temporal_target' -q --tb=short > docs/evidence/B14R-unit.log 2>&1
```
9PASS/14deselected0.12s (deselected are not skipped).5new pickup-time cases +4affected
existing policy cases. Preserve prior assertions; old valid waste fixture now places
actual pickup at hour2/window26, so its claimed24hours actually elapse. Separate new
test preserves and reproduces one-hour B14-1 false positive under frozen old policy.

```sh
CIVICLY_OPERATIONS_EVIDENCE_PREFIX=B14R CIVICLY_B14R_CHECKPOINT_PROOF=1 CIVICLY_TEST_REQUEST_LOG=/tmp/b14r-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_waste_post_pickup_runtime.py 'backend/tests/integration/test_execution_runtime.py::test_actual_three_issue_completion_verification_and_water_recurrence[WATERLOGGING]' -q --tb=short > docs/evidence/B14R-real.log 2>&1
```
1PASS/1FAIL31.51s. Real waste premature/valid flowPASS. Recurrence/validated resume/
actual2MCP reads executed; test asserted row.id instead of normative row.properties.id,
KeyError. Correct only test shape assertion and also assert actual report row.
Original B14 proof files preserved by environment evidence prefix, default staysB14.
Existing test current-policy assertion now imports VERSION, old B14-1 outcome/proof
and implementation unchanged. No old assertion removed.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14r-binding-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_recurrence_scope.py -q --tb=short > docs/evidence/B14R-binding-unit.log 2>&1
```
2PASS0.38s. Explicit MOCK graph-read facade: ordinary no-addition resume unaffected;
REOPENED with ended-only/missing-active scope fails closed. Does not count as real
DB/MCP proof. Guard added for historical pre-correction broken scopes; no retroactive
repair or quarantine clearance.

```sh
CIVICLY_OPERATIONS_EVIDENCE_PREFIX=B14R CIVICLY_B14R_CHECKPOINT_PROOF=1 CIVICLY_TEST_REQUEST_LOG=/tmp/b14r-recurrence-provider.jsonl backend/.venv/bin/python -m pytest 'backend/tests/integration/test_execution_runtime.py::test_actual_three_issue_completion_verification_and_water_recurrence[WATERLOGGING]' -q --tb=short > docs/evidence/B14R-recurrence.log 2>&1
```
1PASS26.13s. Actual B09/B08/FalkorDB/MCP/LangGraph/Saver: same investigation/new
incident sourced link; preserved old paths/outcomes; exact replay no duplicate
nodes/links/events; old checkpoint unchanged by domain write and after explicit
resume; new validated state has recurring episode/evidence; unbound state denied;
fresh actual READ new incident + READ new report before PAUSE. Model SCRIPTED,
not genuine Gemini or autonomous tool-selection proof.

New resume hook runs on ordinary source revision changes too: concrete compatibility
risk warrants exactly one accepted non-recurrence case, not its whole parameter set.
Evidence-only adapter redirects its existing `/tmp/civicly-b10-runtime-WATERLOGGING.json`
to `docs/evidence/B14R-legacy-resume.json`; test source/assertions unchanged. Adapter
is B14R-evidence-plugin.py, copied to `/tmp/b14r_evidence.py` for this command.

```sh
PYTHONPATH=/tmp:backend CIVICLY_TEST_REQUEST_LOG=/tmp/b14r-legacy-provider.jsonl backend/.venv/bin/python -m pytest -p b14r_evidence 'backend/tests/integration/test_agent_runtime.py::test_real_graph_pause_resume[WATERLOGGING-BLOCKAGE]' -q --tb=short > docs/evidence/B14R-legacy.log 2>&1
```
1PASS8.22s. Existing real analytical workflow/source refresh/MCP/Saver remains healthy;
its own new disposable graph cleanup is unchanged; retained prior graphs untouched.

```sh
make test-spec > docs/evidence/B14R-spec.log 2>&1
```
Both specification validators once after final source/contracts/tests. See final log.

Final14distinctPASS(11unit/3real),0unresolvedFAIL/0SKIP. Historical failed test attempt
retained; overlapping rerun is not another case.5ordinary pytest/child interlocks:
0sent/0unexpected Gemini/countTokens. No full B14/B13/B12/770/313 suites, live smoke,
container lifecycle, B15 worker/delivery/API/frontend. Read-only retention, policy
history, source/hash/secret scan and exact patch checks in B14R-audit.json.


Final read-only audit command:

```sh
backend/.venv/bin/python /tmp/b14r-audit.py > docs/evidence/B14R-audit.log 2>&1
```
Script copied as B14R-audit-script.py; pre-task working-tree hashes live in
`/tmp/b14r-baseline`. Checks earlier public files/evidence/assertions, exact frozen
B14-1 implementation/metadata, real corrected graph/outcomes, old B14 outcome,
city858/1246+42candidate links, original quarantine and paid ledger unchanged,
known secrets/key patterns/ephemeral sessions absent. No database mutation.

```sh
git diff --check
git apply --reverse --check docs/evidence/B14R-changes.patch
```
Exact final working-tree patch/inventory/hash checks in B14R-file-audit.json.
No commit/push/archive, record deletion, credential display or quarantine clearance.
