# B16 exact changed-file inventory

Baseline:1262accepted public files snapshotted before B16. Patch relative to actual working tree; prior accepted uncommitted work is not swept into this patch.

## Modified existing paths

- `README.md`
- `blockers.md`
- `contracts/api_endpoints.json`
- `contracts/api_models.json`
- `decision.md`
- `docs/backend/08_api_frontend.md`
- `flow.md`
- `implementation_status.md`
- `scripts/validate_blueprint.py`
- `scripts/validate_handoff.py`
- `task_board.md`
- `test_log.md`

## New implementation/docs/test paths

- `backend/API.md`
- `backend/app/api/__init__.py`
- `backend/app/api/__main__.py`
- `backend/app/api/application.py`
- `backend/app/api/coverage.py`
- `backend/app/api/dependencies.py`
- `backend/app/api/models.py`
- `backend/app/services/http/__init__.py`
- `backend/app/services/http/reads.py`
- `backend/app/services/http/service.py`
- `backend/tests/integration/test_api_runtime.py`
- `backend/tests/unit/test_api.py`
- `scripts/validate_api.py`

## New B16 evidence

- `docs/evidence/B16-COMMANDS.md`
- `docs/evidence/B16-COVERAGE.md`
- `docs/evidence/B16-FILES.md`
- `docs/evidence/B16-RESULTS.md`
- `docs/evidence/B16-audit-initial.log`
- `docs/evidence/B16-audit-script.py`
- `docs/evidence/B16-audit.json`
- `docs/evidence/B16-audit.log`
- `docs/evidence/B16-changes.patch`
- `docs/evidence/B16-commit-proof-zero-live.json`
- `docs/evidence/B16-commit-proof.log`
- `docs/evidence/B16-export-contracts.py`
- `docs/evidence/B16-extra-unit-zero-live.json`
- `docs/evidence/B16-extra-unit.log`
- `docs/evidence/B16-file-audit.json`
- `docs/evidence/B16-final-checks-zero-live.json`
- `docs/evidence/B16-final-checks.log`
- `docs/evidence/B16-final-projection.json`
- `docs/evidence/B16-final-projection.log`
- `docs/evidence/B16-final-real-zero-live.json`
- `docs/evidence/B16-final-real.log`
- `docs/evidence/B16-final-runtime-zero-live.json`
- `docs/evidence/B16-final-runtime.log`
- `docs/evidence/B16-final-spec.log`
- `docs/evidence/B16-final-unit-zero-live.json`
- `docs/evidence/B16-final-unit.log`
- `docs/evidence/B16-fixed-real-zero-live.json`
- `docs/evidence/B16-fixed-real.log`
- `docs/evidence/B16-guard-unit-zero-live.json`
- `docs/evidence/B16-guard-unit.log`
- `docs/evidence/B16-http-runtime.json`
- `docs/evidence/B16-latest-real-zero-live.json`
- `docs/evidence/B16-latest-real.log`
- `docs/evidence/B16-network.json`
- `docs/evidence/B16-openapi.json`
- `docs/evidence/B16-pre-audit-http-runtime.json`
- `docs/evidence/B16-projection-zero-live.json`
- `docs/evidence/B16-projection.log`
- `docs/evidence/B16-real-zero-live.json`
- `docs/evidence/B16-real.log`
- `docs/evidence/B16-source-final-spec.log`
- `docs/evidence/B16-spec.log`
- `docs/evidence/B16-unit-zero-live.json`
- `docs/evidence/B16-unit.log`
- `docs/evidence/B16-worker-failed-diagnostic.json`

API purpose/imports/control flow and secure setup: backend/API.md. coverage.py provides exact route policy; models.py adapts accepted closed commands and explicit DTOs; dependencies.py binds server-owned Auth/services; application.py exposes typed transport/envelopes only; __main__.py hosts explicit localhost lifespan; service.py delegates existing domain services with durable idempotency; reads.py owns fixed bounded scoped projections. unit/test_api.py covers closed schemas/Auth/role/recovery/redaction/source identity/projection guards; integration/test_api_runtime.py one real DB/MCP/Saver/HTTP/TCP workflow. validate_api.py checks actual route/model/contract parity; existing validators invoke it. Contracts updated together per DEC-060; six trackers/README/API spec history retained.

Patch includes actual source/tests/contracts/docs/trackers. Generated B16runtime proofs/evidence are supplied separately alongside patch. No old test assertion, business/worker/agent/MCP implementation, migration, registry, dataset, dependency pin or prior evidence edited. No secrets/profiles/authDB/env/cache/Git internals/volume contents or ZIP included.
