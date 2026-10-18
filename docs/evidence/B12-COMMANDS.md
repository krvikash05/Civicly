# B12 exact commands and observed results

Working directory /Users/vikashkumar/Desktop/Civicly, isolated Python3.12 .venv,
actual retained local FalkorDB6.0.2. No package installation, live LLM or lifecycle.
Ordinary provider interlock inherited by Python MCP/fresh-worker children.

## Initial collection failure (0tests executed)
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b12-initial-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_planning.py backend/tests/integration/test_planning.py -q --durations=10 > /tmp/b12-initial.txt 2>&1
```
New test module basename collision. Renamed integration to test_planning_runtime_store.py.

## Foundation actual three-category/domain checks
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b12-foundation-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_planning.py backend/tests/integration/test_planning_runtime_store.py -q --durations=10 > /tmp/b12-foundation.txt 2>&1
```
18PASS/1newpromptFAIL28.11s. Version selected B12-1 but loader still B11-1; corrected
actual path. Test assertions retained. All4real foundation cases passed.

## Corrected affected runtime/schema/prompt checks
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b12-runtime-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_planning.py::test_current_prompt_closed_plan_schema_and_historical_state_defaults backend/tests/integration/test_planning_runtime_store.py::test_resolver_unknown_conflicting_owner_stale_revoked_and_reference_denials backend/tests/integration/test_planning_agent.py backend/tests/unit/test_agent_models.py backend/tests/unit/test_agent_context.py backend/tests/unit/test_agent_provider.py backend/tests/unit/test_live_smoke_harness.py::test_successor_only_replaces_stale_capability_guidance_and_preserves_safety -q --durations=10 > /tmp/b12-runtime.txt 2>&1
```
31PASS0FAIL0SKIP29.80s. Historical B11-1 parity test explicitly reads that preserved
file when B12-1 becomes current; no old test/assertion removed.

## One directly affected legacy recommendation regression
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b12-legacy-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_agent_reasoning.py::test_planner_is_nonbinding_no_operational_nodes -q --durations=10 > /tmp/b12-legacy.txt 2>&1
```
1PASS7.75s. Original test deletes only its own newly generated graphs/accounts.

## Final directly affected reference/runtime checks
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b12-final-references-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_planning_runtime_store.py backend/tests/integration/test_planning_agent.py -q --durations=10 > /tmp/b12-final-references.txt 2>&1
```
6PASS50.94s. Reuse B03 attribution/source-date rules, future-citation denial,
author-vs-executor distinction, source supersession/revocation. Same6cases overlap,
not added to49distinct final42unit/7real. Fresh child process invoked from test:
```sh
backend/.venv/bin/python -m tests.b12_worker PRIVATE_TEST_PROFILE THREAD_ID OUTPUT_PATH
```
Uses inherited PYTHONPATH=backend; actual Saver and plan/hash read only, no provider.

## Specification validators
```sh
make test-spec > /tmp/b12-spec.txt 2>&1
make test-spec > /tmp/b12-final-spec.txt 2>&1
```
BothPASS. Preliminary first pass before final current-contract description audit;
second final pass after required clarification of B12 draft writes vs still-absent
B13–B15 operations. Source/application tests not repeated for this text change.
Both source validators include static B04/B11 and B12 parity checks; not runtime proof.

## Convenient human focused reproduction (not an additional executed batch)
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b12-check-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_planning.py backend/tests/integration/test_planning_runtime_store.py backend/tests/integration/test_planning_agent.py -q --durations=10
```
Expect21newB12cases passing (15unit/6real), all3issues + actual fake-model/MCP/Saver,
no new WorkOrder/approval/execution. No reset/full suite/container restart required.

## Final artifact and retained-ledger audit
```sh
backend/.venv/bin/python /tmp/b12-audit.py
git diff --check
git apply --reverse --check docs/evidence/B12-changes.patch
```
Scans exact previous public-file hashes, immutable original migration/source/evidence,
actual private values/patterns without printing secrets, leaked MCP children and
accepted live ledger requests/cost unchanged. Actual model boundary is still zero
for B12. Patch against pre-B12 working tree includes actual source, tests, migration,
contracts/docs; generated raw evidence inventoried separately. No push/ZIP.
