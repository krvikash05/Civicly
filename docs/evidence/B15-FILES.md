# B15 exact changed-file inventory

Patch baseline: accepted working tree before B15,1215public files, not stale Git HEAD. No accepted uncommitted changes swept into this patch.

## Existing paths modified

- `backend/app/agents/runtime.py`
- `backend/app/services/operations/storage.py`
- `blockers.md`
- `decision.md`
- `flow.md`
- `implementation_status.md`
- `scripts/validate_blueprint.py`
- `scripts/validate_handoff.py`
- `task_board.md`
- `test_log.md`

## New source, tests and contracts

- `backend/EVENTS.md`
- `backend/app/events/__init__.py`
- `backend/app/events/__main__.py`
- `backend/app/events/models.py`
- `backend/app/events/runtime.py`
- `backend/app/events/service.py`
- `backend/app/events/sources.py`
- `backend/app/events/store.py`
- `backend/app/events/worker.py`
- `backend/tests/b15_process.py`
- `backend/tests/b15_runtime.py`
- `backend/tests/integration/test_event_delivery.py`
- `backend/tests/integration/test_event_runtime.py`
- `backend/tests/unit/test_events.py`
- `contracts/event_delivery.json`
- `scripts/validate_events.py`

## New B15 review evidence

- `docs/evidence/B15-COMMANDS.md`
- `docs/evidence/B15-FILES.md`
- `docs/evidence/B15-RESULTS.md`
- `docs/evidence/B15-audit-initial.log`
- `docs/evidence/B15-audit-probe-field.log`
- `docs/evidence/B15-audit-script.py`
- `docs/evidence/B15-audit.json`
- `docs/evidence/B15-audit.log`
- `docs/evidence/B15-changes.patch`
- `docs/evidence/B15-claims-failures.json`
- `docs/evidence/B15-file-audit.json`
- `docs/evidence/B15-final-focused-zero-live.json`
- `docs/evidence/B15-final-focused.log`
- `docs/evidence/B15-final-spec.log`
- `docs/evidence/B15-final-unit-zero-live.json`
- `docs/evidence/B15-final-unit.log`
- `docs/evidence/B15-focused-zero-live.json`
- `docs/evidence/B15-focused.log`
- `docs/evidence/B15-last-runtime-zero-live.json`
- `docs/evidence/B15-last-runtime.log`
- `docs/evidence/B15-outcome-WATERLOGGING.json`
- `docs/evidence/B15-probe-zero-live.json`
- `docs/evidence/B15-probe.log`
- `docs/evidence/B15-process-restart.json`
- `docs/evidence/B15-quarantine-race.json`
- `docs/evidence/B15-real-initial.log`
- `docs/evidence/B15-real-zero-live.json`
- `docs/evidence/B15-real.log`
- `docs/evidence/B15-spec.log`
- `docs/evidence/B15-unit-zero-live.json`
- `docs/evidence/B15-unit.log`

Implementation purpose per module/imports: backend/EVENTS.md. Tests: tests/b15_process.py fresh-process crash/replay; tests/b15_runtime.py actual MCP/Saver proof; integration/test_event_delivery.py real lease/claims/retry/public/quarantine; integration/test_event_runtime.py one accepted recurrence setup extended; unit/test_events.py pure routing/validation/stop and direct mocked guard cases. Event contract/static parity: contracts/event_delivery.json and scripts/validate_events.py. Existing runtime change is optional host delivery markers only; operations storage change permits only DomainEvent delivery-status/time updates. Six trackers preserve historical bodies and add newest status/audit.

No old Python test file, registry, migration, dataset, dependency pin, MCP implementation or prior evidence modified. No credential/env/volume/cache/profile/Git internals included. B15 patch contains actual source/tests/contracts/docs/trackers; generated proof files are supplied separately alongside it. No new ZIP requested or created.
