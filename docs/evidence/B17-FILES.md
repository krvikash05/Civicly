# B17 exact file inventory

Against accepted uncommitted B16/R working tree. Patch includes source/contracts/docs/sixtrackers; B17 evidence supplied alongside.

## Modified existing paths

- `backend/API.md`
- `backend/app/api/application.py`
- `backend/app/api/coverage.py`
- `backend/app/api/models.py`
- `backend/app/events/models.py`
- `backend/app/events/service.py`
- `backend/app/events/sources.py`
- `backend/app/services/http/reads.py`
- `backend/tests/integration/test_api_runtime.py`
- `backend/tests/unit/test_api.py`
- `blockers.md`
- `contracts/api_endpoints.json`
- `contracts/api_models.json`
- `contracts/event_delivery.json`
- `decision.md`
- `docs/backend/08_api_frontend.md`
- `docs/frontend_contract/FRONTEND_READINESS.md`
- `flow.md`
- `implementation_status.md`
- `scripts/validate_api.py`
- `scripts/validate_events.py`
- `task_board.md`
- `test_log.md`

## New source/test paths

- `backend/app/api/view_models.py`
- `backend/app/services/activity.py`
- `backend/app/services/http/stream.py`
- `backend/app/services/http/views.py`
- `backend/tests/integration/test_frontend_runtime.py`
- `backend/tests/unit/test_frontend_views.py`

## New B17 evidence artifacts

- `docs/evidence/B17-COMMANDS.md`
- `docs/evidence/B17-COVERAGE.md`
- `docs/evidence/B17-FILES.md`
- `docs/evidence/B17-PLAN.md`
- `docs/evidence/B17-RESULTS.md`
- `docs/evidence/B17-accepted-unit-zero-live.json`
- `docs/evidence/B17-accepted-unit.log`
- `docs/evidence/B17-audit-initial.log`
- `docs/evidence/B17-audit-script.py`
- `docs/evidence/B17-audit.json`
- `docs/evidence/B17-audit.log`
- `docs/evidence/B17-changes.patch`
- `docs/evidence/B17-checked-real-zero-live.json`
- `docs/evidence/B17-checked-real.log`
- `docs/evidence/B17-cursor-real-zero-live.json`
- `docs/evidence/B17-cursor-real.log`
- `docs/evidence/B17-delivery-real-zero-live.json`
- `docs/evidence/B17-delivery-real.log`
- `docs/evidence/B17-export-contracts.py`
- `docs/evidence/B17-final-accepted-unit-zero-live.json`
- `docs/evidence/B17-final-accepted-unit.log`
- `docs/evidence/B17-final-real-zero-live.json`
- `docs/evidence/B17-final-real.log`
- `docs/evidence/B17-final-unit-zero-live.json`
- `docs/evidence/B17-final-unit.log`
- `docs/evidence/B17-first-passing-journey.json`
- `docs/evidence/B17-journey.json`
- `docs/evidence/B17-openapi.json`
- `docs/evidence/B17-path-real-zero-live.json`
- `docs/evidence/B17-path-real.log`
- `docs/evidence/B17-real-zero-live.json`
- `docs/evidence/B17-real.log`
- `docs/evidence/B17-real2-zero-live.json`
- `docs/evidence/B17-real2.log`
- `docs/evidence/B17-real3-zero-live.json`
- `docs/evidence/B17-real3.log`
- `docs/evidence/B17-real4-zero-live.json`
- `docs/evidence/B17-real4.log`
- `docs/evidence/B17-real5-zero-live.json`
- `docs/evidence/B17-real5.log`
- `docs/evidence/B17-real6-zero-live.json`
- `docs/evidence/B17-real6.log`
- `docs/evidence/B17-real7-zero-live.json`
- `docs/evidence/B17-real7.log`
- `docs/evidence/B17-real8-zero-live.json`
- `docs/evidence/B17-real8.log`
- `docs/evidence/B17-spec.log`
- `docs/evidence/B17-story-real-zero-live.json`
- `docs/evidence/B17-story-real.log`
- `docs/evidence/B17-unit-zero-live.json`
- `docs/evidence/B17-unit.log`
- `docs/evidence/B17-unit2-zero-live.json`
- `docs/evidence/B17-unit2.log`
- `docs/evidence/B17-unit3-zero-live.json`
- `docs/evidence/B17-unit3.log`

No dependencies/locks/images/registry/migrations/accepted POST recovery code changed. Two existing test files have documented phase assertions adjusted; old tests/names/assertion counts retained. Audit verifies exact scope and earlier evidence byte-identical.
