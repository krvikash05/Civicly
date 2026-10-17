# System architecture — modular monolith with load-bearing FalkorDB

## Concrete deployment topology
```
Operator / CLI / Swagger                         (later) Next.js + FalkorDB Canvas
         |                                            ^   (SSE + REST + graph DTO)
         v                                            |
FastAPI API (Pydantic, demo RBAC, SSE, auth, typed DTOs)
         |-- validated domain services ---------------------------|
         |       | graph repository (official Python client)     |
         |       | workflow events / idempotency / audit         |
         |       `- approved actions / simulation                |
         |-- durable event worker (single process) --------------|
         |       `- LangGraph supervisor / specialists / checkpoint
         |             `- MCP client broker -- tools/list + tools/call
         |                    | official FalkorDB MCP (safe readonly allowlist)
         |                    ` Civicly Python MCP (typed domain tools)
         |-- GraphRAG ingestion/retrieval adapter (sourced organizational docs)
         |-- graph/simulation engine (separate hidden ground truth)
         v
FalkorDB server
  - `civicly_knowledge`: canonical physical, incident, evidence, action, organization graph
  - `civicly_docs`: SDK-managed document GraphRAG index; pointers linked by stable IDs
  - checkpoint graph/storage: FalkorDBSaver-managed internal layout, never custom-mutated
local artifact store: source PDF/MD, geometries (GeoJSON), photos; SHA256 refs in canonical graph
```

## Dependency boundaries
- `api` only invokes `services`; it never sends Cypher nor directly calls MCP.
- `services` owns invariants, authorization, idempotency, lifecycle guards, audit and entity revisions; `graph` owns persistence/query templates.
- Agent nodes own investigation **decisions** and use `MCPClientBroker` for read and draft actions. Only validated domain MCP services can write.
- Domain MCP tools call **the same services** as FastAPI. No duplicate business logic.
- GraphRAG document index is SDK-managed and **isolated** to avoid collisions with canonical `Document`/`Evidence` ontology. Every accepted extracted assertion gets canonical evidence pointers; raw SDK entities are not treated as verified facts.
- Simulated field-world controller knows hidden truth; no API/tool/model access to it except through authorized staged events (inspections/observations).
- UI reads only redacted API DTOs with provenance, correct `SIMULATED` origin; never FalkorDB credentials or raw Cypher.

## Storage & consistency
- FalkorDB is primary knowledge and operations graph. **Do not assume ACID cross-graph transactions**, rollback, or `SELECT FOR UPDATE` equivalents. At runtime verify write atomicity and supported Cypher features.
- Every state-changing operation: validate input -> check actor/plan version -> require idempotency key -> make graph change and durable event representation under a tested consistency protocol -> return persisted ID. Fail closed on uncertain partial outcome; reconciliation task detects orphan events/work orders.
- Prefer first release with one worker, claim records with durable lease/retry count, idempotent consumers, monotonic revisions; guarded compare-and-swap or serialization must be verified in a real concurrency test. If FalkorDB cannot atomically couple all required event writes, use an explicit graph-backed recovery/reconciliation workflow with failure-injection tests; do not pretend exactly-once delivery.
- Human approvals are bound to plan_id, immutable version + sha256 of normalized payload, exact action scope, and authenticated actor.
- Timestamps UTC, time-window and origin timezone explicit; client local display only later.
- Retain `SYNTHETIC` vs `PUBLIC` etc source kind. No real citizen PII.

## Agent runtime and message sequences
1. POST complaint (Idempotency-Key) -> canonical Complaint -> Incident candidate -> ProblemCluster -> `CASE_OPENED` domain event.
2. Worker claims event -> resumes LangGraph thread `investigation_id` via checkpointer -> tool discovery.
3. Supervisor selects one valid next tool with rationale; MCP call returns structured evidence, bounded graph paths and reference IDs.
4. Investigator/Analyst evaluate hypotheses, request inspection if needed or draft plan.
5. `AWAITING_EVIDENCE` checkpoint; inspection event may later resume the *same* thread, preserving history.
6. Approved plan -> work orders created through domain service -> simulated operator updates -> `TASK_COMPLETED`/`OUTCOME_OBSERVED` triggers monitor.
7. Recurrence -> new incident linked to prior ProblemCluster -> agent retrieves prior failed repair and updates assessment; archived reasoning preserved.

## API response support for eventual frontend
SSE must stream only actual committed events, `id`, `event_type`, `entity_id`, `revision`, `timestamp`, `simulation_mode`, payload. Consumers refetch resources on reconnect. Graph DTO bounded nodes/edges with ID, type, label, evidenceIds, observed/valid times, source reliability and highlight/decision-path role. Hypothesis DTO has alternatives, supporting/contradicting IDs, missing evidence and revision history. Tasks include DAG dependencies; plans expose approval gates and monitoring.

## Engineering path
Repo layout defined in `flow.md`. Native backend `pyproject.toml` with dependency groups, lockfile after compatibility spikes; Docker Compose FalkorDB + MCP Node service + FastAPI + worker (later UI); unit fake-LLM tests, real integration tests; CLI source of demo commands. No Kafka, Snowflake, microservice mesh, public signup, or complex GIS engine necessary.

## B02 canonical scope contract (v3)
Canonical domain records use `municipality_id='demo-city'`, fixed by the server.
`tenant_id` is not a domain alias or caller-controlled input. Framework integration
may translate the same fixed value explicitly if its verified API requires it.
All normative machine contracts reference this same municipality_scope policy.
This is one synthetic municipality, not enterprise tenant isolation. Legacy v1/v2
fixtures require explicit conversion before canonical import; no implicit scope,
unknown-field dropping, or invented temporal evidence is permitted.
