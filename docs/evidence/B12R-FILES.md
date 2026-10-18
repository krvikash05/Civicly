# B12-R exact changed-file inventory

Actual narrow diff against pre-B12-R working-tree snapshot. HEAD predates B11, so accepted uncommitted earlier work is excluded. Source/test/contract/docs patch and generated proof inventory separate.

## Modified (18)

- `backend/PLANNING.md`
- `backend/app/agents/models.py`
- `backend/app/agents/runtime.py`
- `backend/app/memory/__main__.py`
- `backend/app/services/planning/models.py`
- `backend/app/services/planning/service.py`
- `backend/tests/b12_fixtures.py`
- `backend/tests/integration/test_planning_agent.py`
- `backend/tests/integration/test_planning_runtime_store.py`
- `blockers.md`
- `contracts/resolution_planning.json`
- `decision.md`
- `docs/backend/07_operations.md`
- `flow.md`
- `implementation_status.md`
- `scripts/validate_planning.py`
- `task_board.md`
- `test_log.md`

## Added source/test/source-manifest (8)

- `backend/app/services/planning/feedback.py`
- `backend/app/services/planning/policy.py`
- `backend/tests/integration/test_planning_remediation_runtime.py`
- `backend/tests/unit/test_planning_remediation.py`
- `data/documents/b12r/D019_drain_blockage_clearance.md`
- `data/documents/b12r/D020_subgrade_repair.md`
- `data/documents/b12r/D021_missed_pickup_recovery.md`
- `data/documents/b12r/manifest.json`

## New sanitized evidence

- `docs/evidence/B12R-COMMANDS.md`
- `docs/evidence/B12R-FILES.md`
- `docs/evidence/B12R-RESULTS.md`
- `docs/evidence/B12R-ROAD_DAMAGE-remedial.json`
- `docs/evidence/B12R-WASTE_ACCUMULATION-remedial.json`
- `docs/evidence/B12R-WATERLOGGING-draft.json`
- `docs/evidence/B12R-WATERLOGGING-remedial.json`
- `docs/evidence/B12R-affected-zero-live.json`
- `docs/evidence/B12R-affected.txt`
- `docs/evidence/B12R-agent-dependency.json`
- `docs/evidence/B12R-agent-fresh-process.json`
- `docs/evidence/B12R-agent-invalid.json`
- `docs/evidence/B12R-agent-valid.json`
- `docs/evidence/B12R-audit-attempts.md`
- `docs/evidence/B12R-changes.patch`
- `docs/evidence/B12R-real-zero-live.json`
- `docs/evidence/B12R-real.txt`
- `docs/evidence/B12R-recovery-zero-live.json`
- `docs/evidence/B12R-recovery.txt`
- `docs/evidence/B12R-remediation-zero-live.json`
- `docs/evidence/B12R-remediation.txt`
- `docs/evidence/B12R-resolver-denials.json`
- `docs/evidence/B12R-review-checks.json`
- `docs/evidence/B12R-road-zero-live.json`
- `docs/evidence/B12R-road.txt`
- `docs/evidence/B12R-source-audit.json`
- `docs/evidence/B12R-spec.txt`
- `docs/evidence/B12R-test-summary.json`
- `docs/evidence/B12R-unit-zero-live.json`
- `docs/evidence/B12R-unit.txt`

Existing valid MCP/Saver scenario extended to remedial draft, original assertions preserved; invalid scenario strengthened and one pre-write dependency case added. Existing store test output prefix now B12R by default; prior evidence preserved. Test fixtures optionally add new authored causal/safety context, old default behavior retained. No migrations, dependency locks, original corpus/manifests, city fixtures or earlier accepted evidence changed.
