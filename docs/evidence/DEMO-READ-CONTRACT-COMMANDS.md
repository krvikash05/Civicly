# Reproducible commands

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-demo-read-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_agent_read_validation.py backend/tests/unit/test_agent_provider.py backend/tests/unit/test_ai_provider_recovery.py backend/tests/unit/test_agent_count_billing.py backend/tests/unit/test_demo_host.py -q
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-demo-read-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_agent_read_contract_runtime.py -q
make test-spec
```
59unitPASS(9.98s),2realPASS(21.51s);bothSPECvalidatorsPASS. Model responses in pytest are mocked; DB/MCP/Saver are real in integration. Ordinary tests send0providerrequests. Initial2fixture failures documented in RESULTS.

Already executed presenter commands (do not replay for verification):

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-clean.json rehearsal
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json preflight --authorize-model-metadata
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json queue --case INV-B09-f663f7a1473c4a28a941d147633e08ad --key DEMO-READ-CONTRACT-ROAD-INITIAL
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json worker --live --case INV-B09-f663f7a1473c4a28a941d147633e08ad --batches 1
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json queue --case INV-B09-95e00a75e74b708c966db68bc595dca0 --key DEMO-READ-CONTRACT-WASTE-INITIAL
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json worker --live --case INV-B09-95e00a75e74b708c966db68bc595dca0 --batches 1
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json discover
```
Both paid wakes returned retained DONE, not just dispatch success. Safe nonbillable verification:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json status
```
Expect water HUMAN_REVIEW with current plan; road/waste MISSING_EVIDENCE with pending inspections. Actual localhost TCP proof and private-credential-free SSE frame are in DEMO-READ-CONTRACT-http-sse.json. Private credentials remain in presenter files and frontend server environment only.
