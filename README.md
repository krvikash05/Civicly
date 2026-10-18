> **Current completed road demonstration — EXACT-ROAD-LIFECYCLE (18 Oct 2026).** The human-selected original incident `INC-B08-27a2cb5d89ae9ab9d86f999cf7b50472` now has a complete explicitly synthetic lifecycle. Original investigation `INV-B09-b9d4d66e130ed348c4f6a50e9d66a891`: real Gemini/MCP reads and supported assessments; analyst-assisted cited draft; exact human approval; three completed work orders; independent utility verification; monitoring; verified road outcome and retained case memory. This supersedes earlier road readiness descriptions below. Gemini stopped at its retained token limit before drafting; the planning/execution stages were authenticated operator assistance. Full B10/B20/B-END acceptance remains open. See [results](docs/evidence/EXACT-ROAD-LIFECYCLE-RESULTS.md).

> **Current presenter backend — DEMO-FIELD-REVIEW, PARTIAL (18 Oct 2026).** Actual Gemini/MCP/FalkorDB investigations, reviewed synthetic reports, water+road sourced drafts submitted for human review; waste report read then explicit token-budget stop. API localhost:8010,59operations/55paths/185schemas. No approval/work/resolution claimed. Current [judge walkthrough](backend/DEMO_WALKTHROUGH.md), [frontend handoff](backend/FRONTEND_HANDOFF.md), [results](docs/evidence/DEMO-FIELD-REVIEW-RESULTS.md) supersede historical status headers below. Frontend is being developed separately by explicit human authorization; full B10/B20/B-END acceptance remains open.

# Civicly — Backend-First Codex Build System (v2.0)

> **CURRENT B16 — TECHNICALLY PASS, HUMAN REVIEW PENDING.** B15 accepted.44typed authenticated operations/42paths over accepted services;8B17+3B19operations explicitly deferred.63distinct focusedPASS(62unit incl3existing service regressions/1real HTTP-service-DB-worker-MCP-Saver/TCP integration),0unresolvedFAIL/0SKIP. Both finalSPECvalidatorsPASS;12pytest/child interlock proofs0external Gemini/countTokens. Actual localhost health/readiness/docs/OpenAPI/auth verified. Source-bound request identity corrected after retained fail-closed trace collision; failed graphs/quarantines preserved. B10 genuine Gemini acceptanceOPEN/PARTIAL; all18requirements binding. No B17/SSE/frontend/live/backend-complete claim. This summary supersedes historical status headers. See docs/evidence/B16-RESULTS.md.

B16 local API startup and secure `/docs`: [backend/API.md](backend/API.md). Exact implemented/deferred routes: [B16-COVERAGE](docs/evidence/B16-COVERAGE.md).

> **CURRENT B13 — TECHNICALLY PASS, HUMAN REVIEW PENDING.** Demo authentication, exact-scope approvals and authorized work-order foundations; no B14 execution, API/frontend or live provider. Accepted B12/B12-R/B12-R2 preserved. See backend/OPERATIONS.md and six tracking files for current evidence; B10 full genuine acceptance remains OPEN/PARTIAL.

> **CURRENT B12 — PASS, HUMAN REVIEW PENDING.** Typed persistent DRAFT plans/PROPOSED tasks, verified responsibility + B11 citations, bounded DAG/version/hash/monitoring criteria and compatible planner/Saver path exercised.49distinct focused casesPASS(42unit/7real),0finalFAIL/0SKIP; both finalSPECvalidatorsPASS;0externalGemini/countTokens. Additive0004 tested isolated;0001–0003/retained city/checkpoints/evidence preserved. No approval/WorkOrder/monitoringexecution/API/frontend. B10 full live acceptance OPEN/PARTIAL. B13 not authorized; see docs/evidence/B12-RESULTS.md.


> **B11 — PASS, human review pending.** Actual SDK MD/PDF memory,19versioned sources, cited read-only MCP retrieval and recovery/persistence verified.308targeted regression+40B11-only cases (overlap;313distinct with lifecycle),0finalfail/skip, both SPEC validatorsPASS, zero Gemini calls. [Results](docs/evidence/B11-RESULTS.md), [memory guide](backend/MEMORY.md). B10 live acceptance explicitly deferred OPEN/PARTIAL; no B12/frontend. This summary supersedes historical status below.

> **B10-O-R2 — PASS, human review pending:** **770 PASS /0 FAIL /0 SKIP** (1206.63s), both specification validators PASS; zero external Gemini. New standard400000/complex800000 cumulative tokens and endpoint-specific zero count settlement; existing settings/history preserved. B10 genuine live acceptance remains OPEN/PARTIAL; no B11. [Results](docs/evidence/B10OR2-RESULTS.md), [provider/spending guide](backend/PROVIDER_ACCOUNTING.md), [runtime guide](backend/AGENTS_RUNTIME.md).

**Current status:** B10-O-R main corrections accepted at local baseline af42149. B10-O-R2 technical verification PASS; human review pending; B10 remains PARTIAL pending separately authorized genuine Gemini investigations. B11 has not started. All18 product requirements remain binding; this is not backend completion.
See [complaint intelligence guide](backend/COMPLAINTS.md), [algorithm guide](backend/ALGORITHMS.md) and [official MCP guide](backend/MCP.md) and [Civicly domain MCP guide](backend/CIVICLY_MCP.md) for scope and real evidence.

For the current Python 3.12/Docker setup, CLI health and verified persistence tests,
see [backend/README.md](backend/README.md) and [schema/recovery guide](backend/SCHEMA.md).
B00–B09-R are accepted; B10 is partial and awaits review of its remaining live acceptance gates. The 18 objectives, remaining B00
contract findings and backend-first gates remain binding.

**Purpose:** Implement a genuinely agentic, FalkorDB-native, MCP-connected civic investigation system covering recurring WATERLOGGING, ROAD_DAMAGE and WASTE_ACCUMULATION, including interlinked failures, persistent memory, municipal knowledge, approved actions, progress tracking, and verifiable outcomes. Backend first; frontend last, but its data requirements are fixed now.

## Quick start (human)
1. Create/open a Git repository `civicly`, extract **the contents** of this package into its root (retain all paths).
2. Run `python scripts/validate_blueprint.py` and `python scripts/validate_handoff.py`. These validate specifications only, not runtime software.
3. Give Codex the exact prompt in `CODEX_START_HERE.md`.
4. Codex must work **one numbered microtask per turn**; after each task you inspect tests/evidence and say to continue.
5. Send ChatGPT `decision.md`, `flow.md`, `implementation_status.md`, `test_log.md`, and `blockers.md` whenever a problem arises. Include the failing command's output.
6. Backend must be shown working from CLI, `/docs`, actual MCP calls and FalkorDB Browser before any frontend code is implemented.

## Spec precedence
1. `contracts/schema_registry.json`, `contracts/state_machines.json`, `contracts/mcp_tools.json`, `contracts/api_endpoints.json`, `contracts/event_types.json` for normative machine-valued names and rules.
2. `docs/backend/*.md` for domain semantics and system behavior; `docs/frontend_contract/*.md` for API/UX outputs.
3. `docs/backend/00_requirements.md` for non-negotiable objectives.
4. `docs/legacy_v1/*` is archival context ONLY; it is not normative and may contain superseded choices. Follow `docs/backend/*` and v2 contracts instead.
5. Conflicts must become an ADR entry **before** code changes, and all affected contracts + tests updated together. No silent substitutions.

## Key entrypoints
- `AGENTS.md`: enforceable working rules for Codex.
- `CODEX_START_HERE.md`: exact first prompt.
- `docs/backend/00_requirements.md`: 18 objectives, success gates, scope.
- `docs/backend/01_system.md`: modules, runtime architecture, dataflow and boundaries.
- `docs/backend/02_graph.md`: entity ontology, semantics, temporal/spatial graph, queries and algorithms.
- `docs/backend/03_data.md`: datasets, ingestion, source trust and de-duplication.
- `docs/backend/04_agents.md`: orchestration, decision policy, checkpoints and proofs.
- `docs/backend/05_mcp.md`: official FalkorDB MCP and custom MCP integration/security.
- `docs/backend/06_memory_graphrag.md`: FalkorDBSaver, organizational documents and GraphRAG SDK.
- `docs/backend/07_operations.md`: inspections, approvals, work orders, monitors, durable events.
- `docs/backend/08_api_frontend.md`: versioned routes, SSE, graph DTO and future UI contracts.
- `docs/backend/09_security_deploy.md`: auth, threat model, runtime and test environment.
- `docs/backend/10_evaluation.md`: reproducible dataset, hidden truth and adversarial evaluation.
- `docs/backend/11_microtasks.md`: incremental Codex implementation steps and evidence gates.
- `docs/backend/12_falkordb_sources.md`: checked official sources and feature-adoption matrix.
- `docs/demo/SCENARIOS.md`, `contracts/scenarios/catalog.json`: detailed demonstration playbooks.
- `decision.md`, `flow.md`, `implementation_status.md`, `test_log.md`, `blockers.md`: living audit/control files.

## Stack choices (verify actual compatibility during microtasks)
Python 3.12+, FastAPI/Pydantic v2, FalkorDB official Python client, LangGraph and FalkorDBSaver integration, MCP Python SDK, official FalkorDB Node MCP read-only, FalkorDB GraphRAG SDK for sourced organizational documents, Redis-compatible FalkorDB via Docker. CLI + pytest + real integration suites. Event-driven worker, SSE. Later Next.js/React/TS, FalkorDB Canvas, Leaflet; **no frontend implementation yet**.

## Completion rule
A task is not complete merely because files exist. Mark complete only after its acceptance criteria, commands, passing actual tests and the relevant FalkorDB/MCP traces appear in the logs. The agent may simulate municipal field work, never fabricate graph queries, tool calls, inspection evidence, or backend outcomes.

## Non-negotiables
- FalkorDB is essential: a topology perturbation must change the agent's evidence-based decision; removing FalkorDB breaks the investigation.
- Runtime MCP `tools/list` and `tools/call` with trace and role permissions; connecting MCP to Codex itself does not satisfy this.
- Model observed facts, unverified claims, hypotheses, historical assessments, causal findings separately.
- All three civic issues have full independent scenarios and a cross-category case.
- Case memory survives restart; corrections preserved; graph-backed organizational procedures are sourced.
- AI can inspect/plan; execution requires exact-version human approval; completion is separate from resolution.
- Synthetic/public/rightfully used data only; no actual government dispatch. Clear `SIMULATED` badges in future UI.

B09 domain guide: [EVIDENCE.md](backend/EVIDENCE.md). Explicit evidence criteria, immutable assessment revisions, actual inspection lifecycle, active-graph boundaries and reproduction commands; no agent/dispatch/event delivery claim.

B10 workflow, exact shared source boundary, real MCP/Saver behavior and limitations: [agent runtime guide](backend/AGENTS_RUNTIME.md), [current B10 evidence](docs/evidence/B10-RESULTS.md). No product capability is marked complete merely by these foundations.

Final UTC boundary verification: supersession compares canonical parsed instants, including optional fractional seconds, rather than string order. Exact real test rejects whole-second rollback from .1Z and accepts .2Z, retaining original and new procedure/document versions.1PASS, no earlier test or data changed. Final distinct coverage313(227unit/86integration), all final casesPASS; earlier overlapping batch counts remain historical.
