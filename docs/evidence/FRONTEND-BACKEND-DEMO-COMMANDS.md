# Exact focused verification and host commands

Run from repository root. Live paid invocations already completed; do not rerun them for review.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-demo-host-final-units-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_demo_host.py backend/tests/unit/test_events.py backend/tests/unit/test_planning_remediation.py backend/tests/unit/test_api.py::test_openapi_exact_matrix_closed_models_and_no_deferred_stubs backend/tests/unit/test_http_query_parameters.py -q
```
Result: 109 PASS, 34.21s. Fake-model/unit checks, zero external provider requests.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-demo-host-real-guard-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_demo_host_runtime.py -q
make test-spec
```
Result: 1 real integration PASS, 20.23s; both validators PASS. The integration uses isolated actual FalkorDB and HTTP projections, not a live model.

Host entrypoint: `PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-clean.json`. Subcommands used: `preflight --authorize-model-metadata`, `queue --case ID --key UNIQUE_KEY`, `worker --live --case ID --batches 1`, `release --case ID --inspection ID`, `status`, `discover`, `api --port 8010`. Original three cases used host.json. Final clean manifest retains water and adds distinct S03/S06 assets. Paid worker calls were explicit, sequential and bounded; see persisted runtime and ledger proofs. This document does not reconstruct unavailable exact shell history as an asserted execution transcript.

Actual localhost probes authenticated from private credentials, fetched dashboard plus all category lists, and opened authenticated `/events/stream?investigation_id=INV-B09-8b006fb97aa2b908fc69addcf7ecd037`. Public proof contains no credential. `discover` registered 98 retained events without executing an agent.
