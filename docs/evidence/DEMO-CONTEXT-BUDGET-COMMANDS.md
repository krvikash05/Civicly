# Exact verification commands

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-context-budget-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_context_wire.py backend/tests/unit/test_agent_context.py backend/tests/unit/test_agent_read_validation.py backend/tests/unit/test_agent_provider.py backend/tests/unit/test_ai_provider_recovery.py backend/tests/unit/test_agent_count_billing.py -q
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-context-budget-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_agent_read_contract_runtime.py -q
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-context-budget-wire-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_context_wire_runtime.py -q
make test-spec
```
64unitPASS;2compatibilityrealPASS(19.80s)+1packedrealPASS(10.98s);bothvalidatorsPASS. Gemini is mocked in integrations; MCP/DB/Saver are real. No live paid commands were executed. Two initial new capture-wrapper failures are retained; no application policy relaxation.

Read-only measurement used3savedpresenter states, real discovered catalog and InvestigationAgent.context projection. Full-request proxy estimates with DEMO-2/plain versus DEMO-3/packed are in measurements.json; raw private context was not exported to public evidence. Retained checkpoint and ledger checks are in preservation.json. Nonbillable human demo readback remains:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json status
```
Expect unchanged water/roadPENDING_APPROVAL and wasteTOKEN_BUDGET. Do not resume waste or increase its budget as part of this verification.

Final rollout boundary: context packing is explicitly OFF by default (`CIVICLY_LLM_CONTEXT_WIRE=false`). Only the new integration/unit capture tests enable it. A new default-behavior unit proves that even repeated context is sent in its original plain layout. No private runtime config/environment was changed. Enable only for a separately reviewed fresh read-only live-format smoke; blocked cases remain untouched.
