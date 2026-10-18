# Exact B11-LIVE-SMOKE-R changed-file inventory

Basis: pre-correction working-tree snapshot; GitHEAD predates B11. Prior evidence/patches unchanged.

## Modified (14)

- `backend/AGENTS_RUNTIME.md`
- `backend/app/agents/provider.py`
- `backend/tests/b10_fixtures.py`
- `backend/tests/unit/test_ai_provider_recovery.py`
- `backend/tests/unit/test_live_smoke_harness.py`
- `blockers.md`
- `contracts/agent_optimization.json`
- `contracts/agent_runtime.json`
- `decision.md`
- `flow.md`
- `implementation_status.md`
- `scripts/b11_live_smoke.py`
- `task_board.md`
- `test_log.md`

## New source/tests (2)

- `backend/app/agents/prompts/B11-1.txt`
- `backend/tests/integration/test_live_smoke_temporal.py`

## New sanitized evidence

- `docs/evidence/B11-LIVE-SMOKE-R-COMMANDS.md`
- `docs/evidence/B11-LIVE-SMOKE-R-FILES.md`
- `docs/evidence/B11-LIVE-SMOKE-R-RESULTS.md`
- `docs/evidence/B11-LIVE-SMOKE-R-authorization.json`
- `docs/evidence/B11-LIVE-SMOKE-R-changes.patch`
- `docs/evidence/B11-LIVE-SMOKE-R-execution.json`
- `docs/evidence/B11-LIVE-SMOKE-R-execution.txt`
- `docs/evidence/B11-LIVE-SMOKE-R-fresh-process.json`
- `docs/evidence/B11-LIVE-SMOKE-R-fresh-process.txt`
- `docs/evidence/B11-LIVE-SMOKE-R-official-preflight.json`
- `docs/evidence/B11-LIVE-SMOKE-R-offline-zero-live.json`
- `docs/evidence/B11-LIVE-SMOKE-R-offline.txt`
- `docs/evidence/B11-LIVE-SMOKE-R-original-retention.json`
- `docs/evidence/B11-LIVE-SMOKE-R-preflight.json`
- `docs/evidence/B11-LIVE-SMOKE-R-preflight.txt`
- `docs/evidence/B11-LIVE-SMOKE-R-source-audit.json`
- `docs/evidence/B11-LIVE-SMOKE-R-spec.txt`
- `docs/evidence/B11-LIVE-SMOKE-R-summary.json`
- `docs/evidence/B11-LIVE-SMOKE-R-temporal-test.json`

Private replacement profiles/state/markers and existing-ledger accounting additions excluded; no credentials/volumes/cache/archives. All original failed runtime records remain. Fixture optional clock preserves defaults; existing timeout test only changes prompt version literal, all old assertions/test functions preserved.
