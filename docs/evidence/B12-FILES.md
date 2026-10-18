# B12 exact changed-file inventory

Against pre-B12 working-tree snapshot; original GitHEAD predates B11. Actual narrow patch contains source/contracts/docs/tests/migration, generated evidence listed separately. Prior accepted patches/evidence byte-identical.

## Modified (17)

- `README.md`
- `backend/AGENTS_RUNTIME.md`
- `backend/app/agents/models.py`
- `backend/app/agents/provider.py`
- `backend/app/agents/runtime.py`
- `backend/tests/unit/test_live_smoke_harness.py`
- `blockers.md`
- `contracts/agent_optimization.json`
- `contracts/agent_runtime.json`
- `decision.md`
- `docs/backend/07_operations.md`
- `flow.md`
- `implementation_status.md`
- `scripts/validate_blueprint.py`
- `scripts/validate_handoff.py`
- `task_board.md`
- `test_log.md`

## Added source/contracts/docs/tests (14)

- `backend/PLANNING.md`
- `backend/app/agents/prompts/B12-1.txt`
- `backend/app/graph/migrations/0004_plan_drafts.json`
- `backend/app/services/planning/__init__.py`
- `backend/app/services/planning/models.py`
- `backend/app/services/planning/service.py`
- `backend/app/services/planning/storage.py`
- `backend/tests/b12_fixtures.py`
- `backend/tests/b12_worker.py`
- `backend/tests/integration/test_planning_agent.py`
- `backend/tests/integration/test_planning_runtime_store.py`
- `backend/tests/unit/test_planning.py`
- `contracts/resolution_planning.json`
- `scripts/validate_planning.py`

## Added sanitized evidence

- `docs/evidence/B12-COMMANDS.md`
- `docs/evidence/B12-FILES.md`
- `docs/evidence/B12-RESULTS.md`
- `docs/evidence/B12-ROAD_DAMAGE-draft.json`
- `docs/evidence/B12-WASTE_ACCUMULATION-draft.json`
- `docs/evidence/B12-WATERLOGGING-draft.json`
- `docs/evidence/B12-agent-fresh-process.json`
- `docs/evidence/B12-agent-invalid.json`
- `docs/evidence/B12-agent-valid.json`
- `docs/evidence/B12-changes.patch`
- `docs/evidence/B12-final-references-zero-live.json`
- `docs/evidence/B12-final-references.txt`
- `docs/evidence/B12-final-spec.txt`
- `docs/evidence/B12-foundation-zero-live.json`
- `docs/evidence/B12-foundation.txt`
- `docs/evidence/B12-initial-zero-live.json`
- `docs/evidence/B12-initial.txt`
- `docs/evidence/B12-legacy-zero-live.json`
- `docs/evidence/B12-legacy.txt`
- `docs/evidence/B12-resolver-denials.json`
- `docs/evidence/B12-runtime-zero-live.json`
- `docs/evidence/B12-runtime.txt`
- `docs/evidence/B12-source-audit.json`
- `docs/evidence/B12-spec.txt`
- `docs/evidence/B12-test-summary.json`

Only prior test change: preserved B11-1 prompt parity reads its historical file when B12-1 becomes current; all prior test functions/assertions retained. No credentials/cache/runtime/volume/archive included. All native migration0001–0003/source documents/fixtures/dependencies unchanged.
