# B16-R exact changed paths

Patch baseline: actual accepted pre-B16-R working tree,1320public files; no earlier uncommitted changes included.

## Application source

- `backend/app/services/http/service.py` — request-local invocation/outcome boundary, safe recovery identities/metadata and replay classification.

## New focused tests

- `backend/tests/unit/test_http_boundary.py` —18mocked boundary/replay/HTTP guards; no mock DB success claim.
- `backend/tests/integration/test_http_recovery.py` —one actual HTTP/Auth/B09/FalkorDB setup; two injected postcommitfaults, records retained/replayblocked.

## Append-only trackers

- `decision.md`
- `flow.md`
- `implementation_status.md`
- `test_log.md`
- `blockers.md`
- `task_board.md`

## New sanitized evidence

- `docs/evidence/B16R-COMMANDS.md`
- `docs/evidence/B16R-FILES.md`
- `docs/evidence/B16R-RESULTS.md`
- `docs/evidence/B16R-accepted-zero-live.json`
- `docs/evidence/B16R-accepted.log`
- `docs/evidence/B16R-audit-script.py`
- `docs/evidence/B16R-audit.json`
- `docs/evidence/B16R-audit.log`
- `docs/evidence/B16R-changes.patch`
- `docs/evidence/B16R-checked-zero-live.json`
- `docs/evidence/B16R-checked.log`
- `docs/evidence/B16R-collection-zero-live.json`
- `docs/evidence/B16R-file-audit.json`
- `docs/evidence/B16R-final-corrected.log`
- `docs/evidence/B16R-final-unit-zero-live.json`
- `docs/evidence/B16R-final-unit.log`
- `docs/evidence/B16R-final-zero-live.json`
- `docs/evidence/B16R-final.log`
- `docs/evidence/B16R-pre-rename-spec.log`
- `docs/evidence/B16R-real-proof.json`
- `docs/evidence/B16R-real-zero-live.json`
- `docs/evidence/B16R-real.log`
- `docs/evidence/B16R-spec.log`
- `docs/evidence/B16R-unit-zero-live.json`
- `docs/evidence/B16R-unit.log`

No API schema/contract/model, migration, accepted business service/worker/agent/MCP, dataset/dependency or oldtest/evidence file changed. No network/live/full workflow run, no graph repair/cleanup, no secrets/profiles/authDB/env/cache/Git internals/volume data or ZIP. Patch contains actual source/tests/append-only trackers; generated evidence accompanies patch separately.
