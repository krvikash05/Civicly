# B18 exact changed-file inventory

Relative to /tmp/b18-baseline public pre-edit snapshot; earlier accepted uncommitted work excluded. No deleted files.

## Application, contracts, tests and tracking

- `backend/OPERATOR_CLI.md` — created
- `backend/app/services/operator.py` — created
- `backend/cli/advance.py` — created
- `backend/cli/legacy.py` — created
- `backend/cli/main.py` — modified
- `backend/cli/private.py` — created
- `backend/cli/reset.py` — created
- `backend/tests/b18_fault.py` — created
- `backend/tests/integration/test_operator_cli_runtime.py` — created
- `backend/tests/unit/test_operator_cli.py` — created
- `blockers.md` — modified
- `contracts/operator_cli.json` — created
- `decision.md` — modified
- `flow.md` — modified
- `implementation_status.md` — modified
- `scripts/validate_blueprint.py` — modified
- `scripts/validate_cli.py` — created
- `scripts/validate_handoff.py` — modified
- `task_board.md` — modified
- `test_log.md` — modified

## New sanitized review evidence

- `docs/evidence/B18-COMMANDS.md`
- `docs/evidence/B18-FILES.md`
- `docs/evidence/B18-PLAN.md`
- `docs/evidence/B18-RESULTS.md`
- `docs/evidence/B18-WALKTHROUGH.md`
- `docs/evidence/B18-audit-script.py`
- `docs/evidence/B18-audit.json`
- `docs/evidence/B18-audit.log`
- `docs/evidence/B18-changes.patch`
- `docs/evidence/B18-cli-journey.json`
- `docs/evidence/B18-final-boundary-unit-zero-live.json`
- `docs/evidence/B18-final-boundary-unit.log`
- `docs/evidence/B18-legacy-unit-zero-live.json`
- `docs/evidence/B18-legacy-unit.log`
- `docs/evidence/B18-real-zero-live.json`
- `docs/evidence/B18-real.log`
- `docs/evidence/B18-refined-real-zero-live.json`
- `docs/evidence/B18-refined-real.log`
- `docs/evidence/B18-refined-unit-zero-live.json`
- `docs/evidence/B18-refined-unit.log`
- `docs/evidence/B18-spec.log`
- `docs/evidence/B18-unit-zero-live.json`
- `docs/evidence/B18-unit.log`

Private host configurations, credential/session files, runtime databases, venv/caches and Git internals are excluded. Patch contains the 20 application/document/contract/test/tracker paths above; evidence files accompany it rather than recursively embedding themselves. Legacy source is byte-identical to pre-B18 main.py. Audit records source hashes, preservation and secret-scan checks.
