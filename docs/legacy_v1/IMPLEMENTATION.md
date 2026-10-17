# Implementation plan and gates

The specification is comprehensive; implementation occurs in verifiable vertical slices. **Do not narrow the product to a static presentation or deadline-driven mock.** Each completed milestone must pass acceptance tests; failures are recorded and fixed.

## M0 — Compatibility & environment
- Pin supported versions after testing Python FalkorDB client, Docker image, LangGraph/FalkorDBSaver, official FalkorDB MCP server, Python MCP SDK, Next.js/Canvas.
- Set up monorepo layout:
```
apps/web/                     # Next.js frontend
services/api/                # FastAPI and domain services
services/agent/              # LangGraph state machine + MCP client
services/civicly_mcp/        # Python MCP server: typed civic tools
services/worker/             # durable events + scheduling
graph/migrations/            # idempotent constraints/indexes/queries
data/seed/                   # realistic labeled synthetic data
contracts/                   # this package's immutable starting schemas
tests/unit/ tests/integration/ tests/e2e/
docs/                        # this specification
```
- Compose: FalkorDB with durable `/var/lib/falkordb/data` volume; avoid upstream compose configuration that places AOF/RDB files outside persisted volume; implement Docker health check.
- Verification: `docker compose up` plus Python client query smoke test, native Browser at local `:3000` or mapped dev port, MCP initialize/tools/list/tools/call, checkpoint restart, Canvas rendering one graph.

## M1 — Canonical data & graph operations
- Import Pydantic models from `contracts/schema_registry.json` or generate equivalent validated class code; use explicit enum serializers.
- Implement `GraphRepository` with *named* query methods, parametrized Cypher, bound traversal limits, stable ID records, relational edge validators, tests against actual FalkorDB.
- Implement migrations, seed generator with four scenarios and hidden fixtures; no ground truth in agent-readable storage.
- Implement complaint normalization/dedup, Incident/ProblemCluster association, event audit, source provenance and canonical graph tests.
- Verify migration idempotency, duplicate complaint grouping, wrong-direction graph not traversed, historical edges time-filtered.

## M2 — MCP runtime and AI investigation
- Implement official graph MCP read-only connection, disable agent access to write/delete tools; implement custom Civicly MCP server per `contracts/mcp_tools.json` with real SDK registration/schema.
- Agent connects as MCP client and observes `tools/list`; log `tools/call` metadata, sanitized arguments and results. Use a deterministic structured model for offline tests, real configurable LLM for interactive behavior.
- LangGraph supervisor with bounded conditional branching, investigator/analyst nodes, checkpoint persistence.
- Structured hypotheses + append-only assessments and cited source evidence. `UNAVAILABLE` external evidence does not block best-effort investigation or induce hallucinations.
- Verify that changed graph paths/inspection evidence produce changed selected tools, hypotheses and recommendations.

## M3 — Resolution planning / human approval / coordination
- Plan DAG with targets, department, dependency, verification criteria, immutable version/hash; verify version changes invalidate older approvals.
- Approval endpoints with authenticated approver and status events; WorkOrder creation only after valid approval and dependency checks; `execution_mode=SIMULATED` for demo.
- Simulated department reporting (authenticated fixture actors) records actual operation events and inspection evidence. Never treat an AI-written task as a completed work order.
- Verify authorization denial, duplicate idempotency requests, blocked dependencies, invalid plan hash and plan revision.

## M4 — Persistent memory and monitoring
- Use `FalkorDBSaver` or verified compatible adapter for persisted LangGraph checkpoints, with case id mapping.
- Create graph-linked CaseMemory for previous failures/corrections and retrieval logic comparing topology and chronology.
- Durable DomainEvent outbox and worker; monitoring rules by issue category; new evidence triggers resume; tasks overdue trigger coordinator.
- Verify restart recovery and reopening from new recurrence, preserving rejected hypotheses and failed interventions.

## M5 — Operational UI
- Dashboard, intake, incident map, investigation timeline, hypothesis comparison, live MCP tool trace, source links, evidence subgraph visualization, plan DAG, approvals and operations, monitoring + outcomes and organization knowledge.
- Canvas: render only bounded sanitized subgraph returned by API. No direct FalkorDB access from browser.
- All buttons wired to actual API results; loading/empty/error/simulation states visible. UI must not pretend a work order is completed if it has only been proposed.
- Verify key flows with Playwright against live API and graph seed.

## M6 — All-category cross-case acceptance
- Run every fixture in `contracts/demo_scenarios.json` with a real graph, MCP transport and agent runner; record observable tool trace and graph query results.
- Run negative variants (clear drain, removed edge, stale approval, failed repair, unavailable rainfall API).
- Run requirements matrix `docs/VALIDATION.md`, security/auth controls, lint/typecheck, backend and end-to-end regression tests.
- Produce demo readme, seed reset command, failure-handling instructions and a recorded test matrix. Do not mark complete unless all R01–R18 pass.

## Implementation status artifact
At each milestone maintain:
```
# IMPLEMENTATION_STATUS.md
Milestone: Mx
Implemented components:
Commands executed:
Test results (pass/fail/skip):
Vendor compatibility confirmed:
Known limitations:
Next executable step:
```
When a library API differs from the blueprint, document verified behavior and update the specific contract + test, not product objectives.
