# B10 changed-file inventory

Baseline: `2d30550` (accepted B09-R). No pushes or review archive. All paths are repository-relative; actual sources remain in place. B10-changes.patch contains the source/contract/guide/tracking diff; runtime evidence/logs are listed here separately to avoid a recursive patch.

| File | Purpose |
|---|---|
| `.env.example` | Nonsecret configurable provider/model/timeout example; real credentials excluded |
| `README.md` | Current status, architecture, implementation decision, reproducibility or limitations documentation |
| `backend/AGENTS_RUNTIME.md` | Current status, architecture, implementation decision, reproducibility or limitations documentation |
| `backend/CIVICLY_MCP.md` | Current status, architecture, implementation decision, reproducibility or limitations documentation |
| `backend/EVIDENCE.md` | Current status, architecture, implementation decision, reproducibility or limitations documentation |
| `backend/MCP.md` | Current status, architecture, implementation decision, reproducibility or limitations documentation |
| `backend/app/active.py` | Private exact B10 active graph profile, scope guard and exact-key ACL provisioning |
| `backend/app/agents/__init__.py` | B10 typed orchestration, provider, tool routing, public checkpoint, controlled journal or versioned prompt source |
| `backend/app/agents/__main__.py` | B10 typed orchestration, provider, tool routing, public checkpoint, controlled journal or versioned prompt source |
| `backend/app/agents/checkpoints.py` | B10 typed orchestration, provider, tool routing, public checkpoint, controlled journal or versioned prompt source |
| `backend/app/agents/control.py` | B10 typed orchestration, provider, tool routing, public checkpoint, controlled journal or versioned prompt source |
| `backend/app/agents/mcp.py` | B10 typed orchestration, provider, tool routing, public checkpoint, controlled journal or versioned prompt source |
| `backend/app/agents/models.py` | B10 typed orchestration, provider, tool routing, public checkpoint, controlled journal or versioned prompt source |
| `backend/app/agents/prompts/B10-1.txt` | B10 typed orchestration, provider, tool routing, public checkpoint, controlled journal or versioned prompt source |
| `backend/app/agents/prompts/B10-2.txt` | B10 typed orchestration, provider, tool routing, public checkpoint, controlled journal or versioned prompt source |
| `backend/app/agents/provider.py` | B10 typed orchestration, provider, tool routing, public checkpoint, controlled journal or versioned prompt source |
| `backend/app/agents/runtime.py` | B10 typed orchestration, provider, tool routing, public checkpoint, controlled journal or versioned prompt source |
| `backend/app/agents/server.py` | B10 typed orchestration, provider, tool routing, public checkpoint, controlled journal or versioned prompt source |
| `backend/app/mcp/broker.py` | Compatible trusted graph binding and shared trace/rationale integration; safe defaults preserved |
| `backend/app/mcp/civicly/broker.py` | Compatible trusted graph binding and shared trace/rationale integration; safe defaults preserved |
| `backend/app/mcp/civicly/contracts.py` | Compatible trusted graph binding and shared trace/rationale integration; safe defaults preserved |
| `backend/app/mcp/civicly/models.py` | Compatible trusted graph binding and shared trace/rationale integration; safe defaults preserved |
| `backend/app/mcp/civicly/server.py` | Compatible trusted graph binding and shared trace/rationale integration; safe defaults preserved |
| `backend/app/mcp/civicly/service.py` | Compatible trusted graph binding and shared trace/rationale integration; safe defaults preserved |
| `backend/app/mcp/policy.py` | Compatible trusted graph binding and shared trace/rationale integration; safe defaults preserved |
| `backend/app/mcp/runtime.py` | Compatible trusted graph binding and shared trace/rationale integration; safe defaults preserved |
| `backend/app/services/complaints/service.py` | Only exact trusted shared-target exception; business/assessment rules unchanged |
| `backend/app/services/complaints/writer.py` | Only exact trusted shared-target exception; business/assessment rules unchanged |
| `backend/app/services/evidence/writer.py` | Only exact trusted shared-target exception; business/assessment rules unchanged |
| `backend/pyproject.toml` | Runtime-verified pinned dependencies and reproducible lock |
| `backend/tests/b10_fixtures.py` | New B10 validation, actual integration, controlled fixtures or separately invoked live/process driver; old tests unchanged |
| `backend/tests/b10_live.py` | New B10 validation, actual integration, controlled fixtures or separately invoked live/process driver; old tests unchanged |
| `backend/tests/b10_live_topology.py` | New B10 validation, actual integration, controlled fixtures or separately invoked live/process driver; old tests unchanged |
| `backend/tests/b10_worker.py` | New B10 validation, actual integration, controlled fixtures or separately invoked live/process driver; old tests unchanged |
| `backend/tests/integration/test_agent_active.py` | New B10 validation, actual integration, controlled fixtures or separately invoked live/process driver; old tests unchanged |
| `backend/tests/integration/test_agent_reasoning.py` | New B10 validation, actual integration, controlled fixtures or separately invoked live/process driver; old tests unchanged |
| `backend/tests/integration/test_agent_runtime.py` | New B10 validation, actual integration, controlled fixtures or separately invoked live/process driver; old tests unchanged |
| `backend/tests/integration/test_agent_safety.py` | New B10 validation, actual integration, controlled fixtures or separately invoked live/process driver; old tests unchanged |
| `backend/tests/unit/test_agent_models.py` | New B10 validation, actual integration, controlled fixtures or separately invoked live/process driver; old tests unchanged |
| `backend/tests/unit/test_agent_provider.py` | New B10 validation, actual integration, controlled fixtures or separately invoked live/process driver; old tests unchanged |
| `backend/uv.lock` | Runtime-verified pinned dependencies and reproducible lock |
| `blockers.md` | Current status, architecture, implementation decision, reproducibility or limitations documentation |
| `contracts/agent_runtime.json` | Compatible machine-readable MCP/agent runtime boundary |
| `contracts/mcp_envelopes.json` | Compatible machine-readable MCP/agent runtime boundary |
| `contracts/mcp_tools.json` | Compatible machine-readable MCP/agent runtime boundary |
| `decision.md` | Current status, architecture, implementation decision, reproducibility or limitations documentation |
| `docs/evidence/B10-COMMANDS.md` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-RESULTS.md` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-active-first.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-active-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-active-second.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-actual-decisions.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-after-lifecycle.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-baseline-B07R-runtime-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-baseline-B08-runtime-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-baseline-B09-retained.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-baseline-B09-runtime-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-baseline-B09R-history.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-baseline-configuration.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-baseline-retained-B01-B07.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-baseline-retained.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-baseline-spec.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-baseline-tests.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-before-lifecycle.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-contradiction-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-contradiction-second.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-contradiction-third.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-debug.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-discovery-and-readback.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-final-collection.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-final-focused-tests.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-final-retained.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-final-runtime-tests.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-final-units.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-focused-third.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-gemini-spike-first.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-gemini-spike-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-gemini-spike-second.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-health.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-ROAD_DAMAGE.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-WASTE_ACCUMULATION.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-WATERLOGGING-attempt-1.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-WATERLOGGING-resume.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-WATERLOGGING.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-decisions-latest.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-decisions.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-fixture.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-road.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-topology.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-topology.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-waste.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-water-first.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-water-resume.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-water-second.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-live-water-third.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-post-B09-retained.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-post-B09R-history.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-post-retained-B01-B07.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-post-retained.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-process-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-provider-units.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-reasoning-first.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-reasoning-fourth.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-regression-B07R-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-regression-B08-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-regression-B09-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-regression-B09R-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-regression-tests.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-runtime-ROAD_DAMAGE.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-runtime-WASTE_ACCUMULATION.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-runtime-WATERLOGGING.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-runtime-first.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-safety-first.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-saver-spike-proof.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-source-audit.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-spec-final.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-spec-first.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-test-summary.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-timeout-second.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-topology-CANDIDATE.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-topology-DISCONNECTED.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-topology-EXPIRED.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-topology-VERIFIED.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-units-first.txt` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `docs/evidence/B10-versions.json` | Sanitized actual runtime/test/provider/dependency/persistence/review evidence; see B10-RESULTS.md for status |
| `flow.md` | Current status, architecture, implementation decision, reproducibility or limitations documentation |
| `implementation_status.md` | Current status, architecture, implementation decision, reproducibility or limitations documentation |
| `scripts/audit_b10.py` | Read-only retained witness verification or source/security audit |
| `scripts/b10_discovery.py` | Read-only retained witness verification or source/security audit |
| `scripts/verify_b10.py` | Read-only retained witness verification or source/security audit |
| `task_board.md` | Current status, architecture, implementation decision, reproducibility or limitations documentation |
| `test_log.md` | Current status, architecture, implementation decision, reproducibility or limitations documentation |
