# B20 exact changed-file inventory

Baseline:1534pre-B20 public files snapshotted under /tmp/b20-baseline. Prior accepted uncommitted Git changes excluded from this task diff. No commit/push. Patch includes new test source, audit helper, all six tracker appends and review Markdown; generated JSON/raw logs are standalone evidence listed below, not repeated in the patch. This inventory and patch are generated deliverables.

## Modified existing files

- `blockers.md` — append-only B20 decision/flow/status/testing/blocker/review history.
- `decision.md` — append-only B20 decision/flow/status/testing/blocker/review history.
- `flow.md` — append-only B20 decision/flow/status/testing/blocker/review history.
- `implementation_status.md` — append-only B20 decision/flow/status/testing/blocker/review history.
- `task_board.md` — append-only B20 decision/flow/status/testing/blocker/review history.
- `test_log.md` — append-only B20 decision/flow/status/testing/blocker/review history.

## New source files

- `backend/tests/b20_fixtures.py` — private shared runtime fixture and issue-only scripted model.
- `backend/tests/integration/test_scenario_behavior.py` — focused actual-service behavioral/boundary tests.
- `backend/tests/unit/test_scenario_behavior.py` — strict rejection/policy unit cases.

## New evidence files

- `docs/evidence/B20-COMMANDS.md` — review plan/matrix/gaps/results/walkthrough or baseline-relative patch.
- `docs/evidence/B20-FILES.md` — review plan/matrix/gaps/results/walkthrough or baseline-relative patch.
- `docs/evidence/B20-GAPS.md` — review plan/matrix/gaps/results/walkthrough or baseline-relative patch.
- `docs/evidence/B20-MATRIX.md` — review plan/matrix/gaps/results/walkthrough or baseline-relative patch.
- `docs/evidence/B20-PLAN.md` — review plan/matrix/gaps/results/walkthrough or baseline-relative patch.
- `docs/evidence/B20-RESULTS.md` — review plan/matrix/gaps/results/walkthrough or baseline-relative patch.
- `docs/evidence/B20-S01-NEGATIVE.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-S01-PRIMARY.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-S02-NEGATIVE.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-S02-PRIMARY.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-S03-NEGATIVE.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-S03-PRIMARY.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-S04-NEGATIVE.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-S04-PRIMARY.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-S05-NEGATIVE.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-S05-PRIMARY.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-S06-NEGATIVE.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-S06-PRIMARY.json` — sanitized actual scenario proof with state/assessments/provenance/API projections.
- `docs/evidence/B20-WALKTHROUGH.md` — review plan/matrix/gaps/results/walkthrough or baseline-relative patch.
- `docs/evidence/B20-audit-script.py` — read-only retention/private-value audit.
- `docs/evidence/B20-audit.json` — read-only retention/private-value audit.
- `docs/evidence/B20-audit.txt` — retained exact command output.
- `docs/evidence/B20-changes.patch` — review plan/matrix/gaps/results/walkthrough or baseline-relative patch.
- `docs/evidence/B20-final-spec-zero-live.json` — provider interlock evidence.
- `docs/evidence/B20-final-spec.txt` — retained exact command output.
- `docs/evidence/B20-planning-control.json` — review plan/matrix/gaps/results/walkthrough or baseline-relative patch.
- `docs/evidence/B20-planning-retry.txt` — retained exact command output.
- `docs/evidence/B20-planning-retry2.txt` — retained exact command output.
- `docs/evidence/B20-planning-zero-live.json` — provider interlock evidence.
- `docs/evidence/B20-planning2-zero-live.json` — provider interlock evidence.
- `docs/evidence/B20-real-attempt1.txt` — retained exact command output.
- `docs/evidence/B20-real-attempt2.txt` — retained exact command output.
- `docs/evidence/B20-real-attempt3.txt` — retained exact command output.
- `docs/evidence/B20-real-zero-live.json` — provider interlock evidence.
- `docs/evidence/B20-real2-zero-live.json` — provider interlock evidence.
- `docs/evidence/B20-real3-zero-live.json` — provider interlock evidence.
- `docs/evidence/B20-spec-zero-live.json` — provider interlock evidence.
- `docs/evidence/B20-spec.txt` — retained exact command output.
- `docs/evidence/B20-unit-zero-live.json` — provider interlock evidence.
- `docs/evidence/B20-unit.txt` — retained exact command output.
- `docs/evidence/B20-verified-spec-zero-live.json` — provider interlock evidence.
- `docs/evidence/B20-verified-spec.txt` — retained exact command output.

- `docs/evidence/B20-summary.json` — final distinct test counts, acceptance/blocker status and scope.

No production service, domain schema, migration, dependency/lock, imported data, scenario/world definition, old test or previous evidence changed. Private .runtime/b20-review profiles/auth/credentials and DB volumes are excluded from public evidence and patch. Earlier failed sources/checkpoints/quarantines retained; no destructive reset or volume removal.

Final generated evidence inventory additions:

- `docs/evidence/B20-audit-final.txt` — final generated audit/verification evidence.
