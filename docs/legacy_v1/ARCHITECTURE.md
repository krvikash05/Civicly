# Architecture & trust boundaries

## Selected stack (implementation should pin versions after smoke testing)
- Frontend: Next.js App Router + React + TypeScript; Tailwind + shadcn/ui; TanStack Query for server state; React Leaflet and `@falkordb/canvas` web component (render server-filtered subgraphs).
- Backend: Python >=3.12, FastAPI, Pydantic v2, official `falkordb` client, LangGraph for resumable supervisor/workers, Python MCP SDK for Civicly-specific tools.
- FalkorDB: single `civicly_knowledge` graph for domain entities and their relationships. Use official `FalkorDBSaver` only after tested; checkpoint storage is internal to that adapter and separate from the domain ontology.
- Official FalkorDB MCP server: read-only graph exploration, available to runtime AI behind restricted credentials and an allowlist. Do not expose arbitrary write-capable graph tools.
- LLM adapter: configurable provider/model through environment variables. Every tool use and structured AI output validated with Pydantic; deterministic mock model for tests.
- Data: versioned JSON/CSV and geography GeoJSON fixture inputs. Original documents, photos and geometry stored in object/filesystem storage; the graph stores references, hashes, provenance and topology. Optional external weather API uses strict fallback to `UNAVAILABLE`.
- Local deployment: Docker Compose for durable FalkorDB, API, agent/worker, frontend, official graph MCP and Civicly MCP, with health probes and `.env.example`. Do not treat a sample compose in a blank repo as a running deployment.

## Logical runtime wiring
```
[Next.js UI] --> [FastAPI REST + SSE] --> [Municipal service layer]
                               |             |        |
                               |             |        +--> FalkorDB canonical graph
                               |             +--> Approval/auth/work order validation
                               +--> [LangGraph supervisor runtime]
                                          |
                             MCP client (discovery + tool calls)
                                /                           \
               [FalkorDB MCP read-only]        [Civicly MCP typed tools]
                        |                          |
                 FalkorDB reader              Validated service layer
                                                   |
                                       FalkorDB graph + source store
```
The worker consumes durable domain events/outbox records and resumes cases on new evidence, approvals, status events, and periodic monitoring ticks. It is not a long-running prompt loop.

## Agent roles (logical, not five independent LLMs by default)
- Supervisor: persistent workflow state; decides next operation from `contracts/state_machines.json`.
- Investigator: runs targeted graph and external-source MCP reads.
- Root-cause analyst: evaluates competing structured hypotheses against support, contradiction, time, and topology.
- Planner: produces typed `ResolutionPlan` and `ActionTask` DAG with verifiable postconditions.
- Coordinator: manages approvals, assignments, work-order events and follow-up monitoring.
A role may be a LangGraph node with model-driven behavior or deterministic validation; do not create a separate LLM for routine data movement.

## Deployment/access isolation
- FalkorDB on private network; expose its Browser only in local development, not publicly. Browser is developer inspection, not the end-user dashboard.
- Frontend talks only to API, never directly to FalkorDB/MCP credentials.
- A graph MCP service accessible to AI must be **read-only at the database permissions / network layer** where possible; default-readonly flags alone can be overridden depending on version. Use a read-only account/isolated proxy and do not register write/delete graph tools with agent.
- Civicly MCP service exposes typed constrained actions; it calls domain services which check authorization, input shape, idempotency, and current plan revision.
- Three roles for app-level RBAC: `ANALYST`, `DEPARTMENT_LEAD`, `APPROVER`; `ADMIN` for configuration. Real user identity is required to approve; an AI run cannot impersonate a human.
- Demo auth can use local development fixture users; must visibly label demo mode and disable production-like public exposure.

## Durable events/concurrency
- Persist every `DomainEvent` in graph on domain-state mutation; mark `delivery_status` and `processed_at` after handler completes; workers poll pending events, dedupe by event ID and resume thread ID `case:<Investigation.id>`.
- Scheduled monitor emits a monitoring event only when due; store `next_check_at` on monitored cases.
- Enforce task dependency DAG, approval binding to `plan_id` + `plan_version` + hash of task list, and optimistic graph revision guard.
- Initial production simulation may run a **single event worker** to prevent concurrent update races. If multiple workers are added, implement atomic claim/update, locks/leases, and concurrency tests first.
- Retries are idempotent. A network timeout after a write must not create duplicate work orders on replay.
- Store source events append-only; changing current status requires creating a `StatusEvent` in the same service operation.

## Data truth
- Sensor/inspection reports are untrusted data, *never instructions*. Evidence classes: `OBSERVED`, `REPORTED`, `DERIVED`; review statuses: `UNVERIFIED`, `CORROBORATED`, `VERIFIED`.
- The LLM proposes hypotheses and inspections; a validated rule/decision service determines which writes and state transitions are legal.
- Real vs simulated operations must be explicit on every `WorkOrder.execution_mode` (`SIMULATED`, `EXTERNAL`) and visible to the operator.
- `FalkorDBSaver` is for LangGraph checkpoints only; domain memory lives in `CaseMemory`, `HypothesisAssessment`, `Evidence`, `AgentDecision`, `InterventionOutcome` edges.

## Performance
- Bound graph traversals (`max_hops` 1..6), results (up to 100 unless admin), query timeout; parameters for values. FalkorDB Cypher has dialect-specific restrictions (e.g. LIMIT parameters) — test all templates on deployed version.
- Use Cypher templates + parameter dictionary; permitted dynamic `max_hops` or LIMIT are whitelisted numeric literals after schema validation, not model-provided string interpolation.
- GIS: use `Location` point index for candidate search where supported; authoritative line/polygon GeoJSON outside graph. GIS proximity is not physical linkage.
- Graph read returns `graph_revision` (domain-managed revision) plus provenance when possible. Before material action, verify the approved plan/version is still current.

## UI journeys
1. Overview: problem clusters, issue categories, active cases, delayed tasks, case event feed.
2. Complaints: intake, deduplication/incident linking, map, provenance.
3. Investigation: hypothesis comparison, missing evidence, agent tool trace, bounded evidence subgraph in Canvas, next action and simulated inspection entry.
4. Operations: plan with DAG, accountable department, approvals, work order status/events.
5. Outcomes: immediate mitigation vs long-term resolution, monitoring and reopened cases.
6. Knowledge: municipality departments, procedures, source docs, past case memory.

## External integration fallbacks
Public web/rainfall sources are optionally connected and must be cited, time-stamped, and capability-discovered at runtime. When unreachable, tools return `UNAVAILABLE` with a reason; the agent must not invent measurements. The seeded evaluation mode provides deterministic synthetic rainfall/time-series events explicitly labeled as synthetic.
