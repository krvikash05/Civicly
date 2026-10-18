# B14-R exact file inventory

Against1174public-file pre-B14-R working-tree snapshot, preserving previously accepted uncommitted changes.18modified +6added source/test files.

## Modified

- `backend/AGENTS_RUNTIME.md` — Explicit validation/checkpoint/source-refresh behavior and boundaries.
- `backend/OPERATIONS.md` — Current corrected timing, history and same-investigation recurrence behavior.
- `backend/app/agents/runtime.py` — Explicit AwaitDependency refresh hook; existing lease/revision/read barrier preserved.
- `backend/app/services/operations/execution.py` — Atomic sourced new-incident investigation link, result/event identity and finite bound.
- `backend/app/services/operations/storage.py` — Whitelist existing normative INVESTIGATES edge for controlled recurrence batch.
- `backend/app/services/operations/verification.py` — Current B14-2 waste timer anchored to latest actual pickup observation.
- `backend/tests/integration/test_execution_runtime.py` — Preserve old assertions, extend recurrence scope/replay/checkpoint proof and evidence prefix/current VERSION.
- `backend/tests/unit/test_execution_policy.py` — Valid waste fixture now actually provides24hours; all old assertions intact.
- `blockers.md` — Current B14-R scope/decisions/flow/results/limits and review status; previous audit history retained.
- `contracts/agent_runtime.json` — Compatible validated explicit recurrence-refresh guarantee.
- `contracts/operations.json` — B14-2 semantics, preserved B14-1 metadata and recurrence scope/refresh contract.
- `decision.md` — Current B14-R scope/decisions/flow/results/limits and review status; previous audit history retained.
- `docs/backend/07_operations.md` — Current B14-R contract/decision pointers.
- `flow.md` — Current B14-R scope/decisions/flow/results/limits and review status; previous audit history retained.
- `implementation_status.md` — Current B14-R scope/decisions/flow/results/limits and review status; previous audit history retained.
- `scripts/validate_operations.py` — Historical policy/version and fixed scope-bound parity checks.
- `task_board.md` — Current B14-R scope/decisions/flow/results/limits and review status; previous audit history retained.
- `test_log.md` — Current B14-R scope/decisions/flow/results/limits and review status; previous audit history retained.

## Added source/tests

- `backend/app/agents/recurrence.py` — Validated bounded active-episode/source refresh on explicit owned resume.
- `backend/app/services/operations/verification_v1.py` — Exact pre-correction B14-1 implementation for historical interpretation.
- `backend/tests/b14r_runtime.py` — Scripted model/actual MCP/Saver same-thread checkpoint preservation and refresh proof.
- `backend/tests/integration/test_waste_post_pickup_runtime.py` — Real premature follow-up/later valid elapsed verification in one approved waste flow.
- `backend/tests/unit/test_recurrence_scope.py` — Mock bounded-read guard for historical ended-only reopen vs ordinary resume.
- `backend/tests/unit/test_waste_post_pickup.py` — One-hour reproduction,24hour boundaries and conservative multiple-pickup semantics.

## New sanitized evidence

- `docs/evidence/B14R-COMMANDS.md`
- `docs/evidence/B14R-FILES.md`
- `docs/evidence/B14R-RESULTS.md`
- `docs/evidence/B14R-audit-script.py`
- `docs/evidence/B14R-audit.json`
- `docs/evidence/B14R-audit.log`
- `docs/evidence/B14R-binding-unit-zero-live.json`
- `docs/evidence/B14R-binding-unit.log`
- `docs/evidence/B14R-changes.patch`
- `docs/evidence/B14R-evidence-plugin.py`
- `docs/evidence/B14R-file-audit.json`
- `docs/evidence/B14R-legacy-resume.json`
- `docs/evidence/B14R-legacy-zero-live.json`
- `docs/evidence/B14R-legacy.log`
- `docs/evidence/B14R-outcome-WATERLOGGING.json`
- `docs/evidence/B14R-real-zero-live.json`
- `docs/evidence/B14R-real.log`
- `docs/evidence/B14R-recurrence-zero-live.json`
- `docs/evidence/B14R-recurrence.log`
- `docs/evidence/B14R-spec.log`
- `docs/evidence/B14R-test-summary.json`
- `docs/evidence/B14R-unit-zero-live.json`
- `docs/evidence/B14R-unit.log`
- `docs/evidence/B14R-waste.json`

Actual source/contracts/docs/tracker diff in B14R-changes.patch (new runtime artifacts separately inventoried); SHA256 `f9f7ab8b3f8521fd362fac0bcd841d677cc112e40ff884ce9b821263e203dcc3`. All earlier evidence unchanged, all prior assertions retained except current VERSION expectation updates; old policy retained exactly. No migration/registry/data/dependency/MCP change, no B15/live provider. Private env/auth/.runtime/volumes/caches/Git internals excluded.
