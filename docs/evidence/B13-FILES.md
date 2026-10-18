# B13 exact changed-file inventory

Immediate pre-B13 working-tree snapshot; HEAD includes older accepted/uncommitted phases, intentionally excluded from narrow patch.

## Modified (12)

- `README.md`
- `backend/PLANNING.md`
- `backend/app/services/planning/storage.py`
- `backend/tests/integration/test_planning_postcommit_recovery.py`
- `blockers.md`
- `decision.md`
- `flow.md`
- `implementation_status.md`
- `scripts/validate_blueprint.py`
- `scripts/validate_handoff.py`
- `task_board.md`
- `test_log.md`

## Added source/contracts/docs/tests (15)

- `backend/OPERATIONS.md`
- `backend/app/graph/migrations/0005_operations.json`
- `backend/app/services/operations/__init__.py`
- `backend/app/services/operations/__main__.py`
- `backend/app/services/operations/auth.py`
- `backend/app/services/operations/migration.py`
- `backend/app/services/operations/models.py`
- `backend/app/services/operations/service.py`
- `backend/app/services/operations/storage.py`
- `backend/tests/b13_fixtures.py`
- `backend/tests/b13_worker.py`
- `backend/tests/integration/test_operations_runtime.py`
- `backend/tests/unit/test_operations.py`
- `contracts/operations.json`
- `scripts/validate_operations.py`

## New sanitized evidence

- `docs/evidence/B13-COMMANDS.md`
- `docs/evidence/B13-FILES.md`
- `docs/evidence/B13-RESULTS.md`
- `docs/evidence/B13-ack-recovery.json`
- `docs/evidence/B13-audit-attempts.md`
- `docs/evidence/B13-auth-final-zero-live.json`
- `docs/evidence/B13-auth-final.txt`
- `docs/evidence/B13-auth-runtime.json`
- `docs/evidence/B13-changes.patch`
- `docs/evidence/B13-checkpoint-compatibility.json`
- `docs/evidence/B13-checkpoint-zero-live.json`
- `docs/evidence/B13-checkpoint.txt`
- `docs/evidence/B13-conditional.json`
- `docs/evidence/B13-cross-department-zero-live.json`
- `docs/evidence/B13-cross-department.txt`
- `docs/evidence/B13-denials.json`
- `docs/evidence/B13-final-affected-zero-live.json`
- `docs/evidence/B13-final-affected.txt`
- `docs/evidence/B13-final-runtime-zero-live.json`
- `docs/evidence/B13-final-runtime.txt`
- `docs/evidence/B13-final-write-zero-live.json`
- `docs/evidence/B13-final-write.txt`
- `docs/evidence/B13-flow.json`
- `docs/evidence/B13-gates-zero-live.json`
- `docs/evidence/B13-gates.txt`
- `docs/evidence/B13-ownership-final-zero-live.json`
- `docs/evidence/B13-ownership-final.txt`
- `docs/evidence/B13-postcommit-recovery.json`
- `docs/evidence/B13-real-zero-live.json`
- `docs/evidence/B13-real.txt`
- `docs/evidence/B13-review-checks.json`
- `docs/evidence/B13-road-water.json`
- `docs/evidence/B13-source-audit.json`
- `docs/evidence/B13-spec-handoff-corrected.txt`
- `docs/evidence/B13-spec-initial.txt`
- `docs/evidence/B13-test-summary.json`
- `docs/evidence/B13-unit-zero-live.json`
- `docs/evidence/B13-unit.txt`

Only prior test change adds configurable B13 evidence prefix; all old assertions intact. Existing0001–0004/schema/source fixtures/dependency locks/evidence unchanged. Storage/recovery infrastructure unchanged. Three-source remedial policies unchanged. B14 documentation-only correction: the earlier “No B13 code” sentence was erroneous. B13 source code is included in this inventory and its patch; the recorded historical tests are unchanged.
