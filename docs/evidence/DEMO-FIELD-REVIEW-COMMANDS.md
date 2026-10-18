# Exact verification commands/results

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-demo-field-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_plan_task_bindings.py backend/tests/unit/test_api.py backend/tests/unit/test_http_boundary.py -q
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-demo-field-extra-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_inspection_context.py backend/tests/unit/test_agent_context.py backend/tests/unit/test_demo_host.py -q
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-demo-field-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_plan_binding_http.py -q
make test-spec
```
Results:99unitPASS24.31s;16unitPASS2.73s;1realPASS11.57s; bothSPECvalidatorsPASS.115distinctunit+1real;0finalfailure/skip. One earlier new integration fixture temporal failure retained, then corrected. Ordinary pytest forbids live providers; real test uses actual FalkorDB/B11/HTTP with no live model.

Executed host prefix: `PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json`.

- `release --case INV-B09-f663f7a1473c4a28a941d147633e08ad --inspection INS-B09-44e1bceff4bc62bd8c87e8b45db92346` →COMMITTED reviewed synthetic report.
- `release --case INV-B09-95e00a75e74b708c966db68bc595dca0 --inspection INS-B09-907ca4d3b5f27ce4e529330100f3cff8` →COMMITTED report+independent service provenance.
- `queue --case INV-B09-f663f7a1473c4a28a941d147633e08ad --key DEMO-FIELD-RESUME-ROAD-01`, then `worker --live --case INV-B09-f663f7a1473c4a28a941d147633e08ad --batches 1` →DONE; persisted road draft/HUMAN_REVIEW.
- `queue --case INV-B09-95e00a75e74b708c966db68bc595dca0 --key DEMO-FIELD-RESUME-WASTE-01`, then matching `worker --live ... --batches 1` →DONE; stale pending-inspection pause retained.
- After status fix, `queue --case INV-B09-95e00a75e74b708c966db68bc595dca0 --key DEMO-FIELD-STATUS-CORRECTION-WASTE-01`, then matching `worker --live ... --batches 1` →DONE; real corrected read, final TOKEN_BUDGET.
- `preflight` after budget interlock →expected exit1 CASE_REQUIRES_OPERATOR_NO_RETRY,0providerrequests.
- `discover` after all mutations →registered persisted report/decision/plan/approval events; no model execution.
- `status` →safe nonbillable public packet, real reports/plans/graphs; no checkpoint mutation.

Actual loopback HTTP analyst submissions used Idempotency-Key DEMO-FIELD-REVIEW-WATERLOGGING and DEMO-FIELD-REVIEW-ROAD_DAMAGE; exact bodies/results retained. No approval decision or work creation sent. The old backend listener9393 alone was replaced by15298 on8010 after tested schema change; source/auth/profile unchanged. Full task-only source patch/inventory supplied. Do not rerun live commands as verification.
