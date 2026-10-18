# B17-R exact changed paths

Patch baseline: accepted uncommitted B17working snapshot /tmp/b17r-baseline/files, not older Git HEAD. No commit/push/reset.

## Modified existing files

- `backend/API.md`
- `backend/app/api/application.py`
- `backend/app/api/view_models.py`
- `backend/tests/integration/test_frontend_runtime.py`
- `blockers.md`
- `contracts/api_endpoints.json`
- `contracts/api_models.json`
- `decision.md`
- `docs/backend/08_api_frontend.md`
- `flow.md`
- `implementation_status.md`
- `scripts/validate_api.py`
- `task_board.md`
- `test_log.md`

## New source/test files

- `backend/tests/unit/test_http_query_parameters.py`

## New review evidence

- `docs/evidence/B17R-COMMANDS.md`
- `docs/evidence/B17R-PLAN.md`
- `docs/evidence/B17R-QUERY-COVERAGE.md`
- `docs/evidence/B17R-RESULTS.md`
- `docs/evidence/B17R-audit-script.py`
- `docs/evidence/B17R-audit.json`
- `docs/evidence/B17R-audit.log`
- `docs/evidence/B17R-export-contracts.py`
- `docs/evidence/B17R-journey.json`
- `docs/evidence/B17R-openapi.json`
- `docs/evidence/B17R-real-zero-live.json`
- `docs/evidence/B17R-real.log`
- `docs/evidence/B17R-spec.log`
- `docs/evidence/B17R-unit-corrected-zero-live.json`
- `docs/evidence/B17R-unit-corrected.log`
- `docs/evidence/B17R-unit-initial-zero-live.json`
- `docs/evidence/B17R-unit-initial.log`
- `docs/evidence/B17R-unit.log`
- `docs/evidence/B17R-FILES.md`
- `docs/evidence/B17R-changes.patch`

Purpose: application.py/view_models.py enforce and advertise exact query fields; new unit file tests rejection/typed passthrough/OpenAPI; existing journey adds actual response assertions/new prefix only; API contracts/exporter/validator/docs synchronize semantics; six trackers append audit history. Audit, raw focused logs, provider interlocks and actual journey support review. No Views/domain/storage/migration/worker/auth/SSE/recovery/dependency code changed.
