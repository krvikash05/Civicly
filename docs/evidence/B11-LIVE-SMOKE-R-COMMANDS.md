# B11-LIVE-SMOKE-R exact commands and results

All commands from /Users/vikashkumar/Desktop/Civicly. No container lifecycle/package
install/full suite or additional live retry executed. Timing/vendor warnings in logs.

## Minimal offline and real local check
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b11lsr-offline-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_live_smoke_harness.py backend/tests/integration/test_live_smoke_temporal.py backend/tests/unit/test_agent_provider.py backend/tests/unit/test_ai_provider_recovery.py::test_overall_deadline_retains_reservation_and_trace_versions -q --durations=10 > /tmp/b11lsr-offline.txt 2>&1
```
16PASS(15unit/1real local)/0FAIL/0SKIP7.15s; no external provider requests. Static fence
cases use InMemorySaver; provider tests MockTransport. Temporal case actual FalkorDB.

## Both spec validators once after source edits
```sh
make test-spec > /tmp/b11lsr-spec.txt 2>&1
```
BothPASS. Static source contracts, not live proof.

## Nonbillable replacement preparation
```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/b11_live_smoke.py prepare > /tmp/b11lsr-preflight.txt 2>&1
```
PASS actual UTC/source references/monotonic binding/no ownership/quarantine/checkpoint;
actual MCP catalog/citations/ROpermissions, existing ledger cap/session/holds.
Recorded authorization before first HTTP. No Gemini request during prepare.

## Exactly one authorized live wake
```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/b11_live_smoke.py execute --live > /tmp/b11lsr-execution.txt 2>&1
```
PASS genuine count1/generation1/selection1/MCPREAD1, no retries/repairs/errors.
$0.00571350known/$0held, halted after Investigator. Marker denies repeated execution.
No second wake/resume/model switch/cap increase or replacement ledger.

## Fresh-process verification (read only, safe for human repeat)
```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/b11_live_smoke.py verify > /tmp/b11lsr-fresh-process.txt 2>&1
```
PASS Saver/decision/journal/server+brokertrace/digest/citations/accounting, no model
invocation/resume. The evidence files contain sanitized actual outputs.

## Read-only original-attempt retention
A separate Python diagnostic loaded the original ActiveProfile and read its original
Investigation properties, quarantine key and SQLite SELECT count by original thread.
Original timestamps12:00Z/thread_bindingNone/quarantineTrue/profileSHAmatching,
original0requests/sharedcasecap150000000nanodollars/projectcap8000000000 unchanged.
No mutation. Exact proof: B11-LIVE-SMOKE-R-original-retention.json.

## Artifact validation
```sh
backend/.venv/bin/python /tmp/b11lsr-audit.py
git diff --check
git apply --reverse --check docs/evidence/B11-LIVE-SMOKE-R-changes.patch
```
Scope/preservation/actual private-value scan, no credential/cache/runtime/volume
payloads in evidence. Review patch is against the pre-correction working-tree
snapshot, since previous milestones were already uncommitted against GitHEAD.
Original B11/B11R/smoke patches/evidence unchanged. No push or archive.

Official documentation checked before HTTP: model/API/count/pricing sources in
B11-LIVE-SMOKE-R-official-preflight.json. Initial pricing fetch cache miss followed
by successful direct official fetch before live. No tariff/model changes.
