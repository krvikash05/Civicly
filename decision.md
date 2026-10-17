# decision.md — Append-only engineering decision log

Decisions are recorded chronologically. Codex must append an entry whenever a significant technical choice, vendor workaround, schema change, library/API version, security trade-off or deviation occurs. Never silently modify architecture.

## DEC-000 (2026-10-17) — Baseline
- Status: ACCEPTED BASELINE, runtime unverified.
- Context: Civicly is advanced hackathon-grade, backend-first, all three civic problems, FalkorDB as central graph, actual runtime MCP, graph-based memory + GraphRAG, supervisor workflow, controlled simulated civic actions.
- Choice: Python modular monolith, official FalkorDB client, LangGraph, Node FalkorDB MCP read-only, custom Python MCP tools, GraphRAG SDK isolated document graph, FastAPI + SSE; frontend designed against APIs and postponed.
- Alternatives: Enterprise microservices, generic SQL-centric storage, script-only pseudo-agent; rejected because excessive complexity or failure to demonstrate FalkorDB-native agency.
- Risks: Vendor API/version compatibility requires smoke tests, event delivery/transaction behavior must be validated, no actual demo implementation exists.
- Related: `docs/backend/01_system.md`, `docs/backend/12_falkordb_sources.md`.

## Template for future decisions
### DEC-XXX — Title | YYYY-MM-DD | PROPOSED / ACCEPTED / SUPERSEDED
- Task ID, scope and user requirement IDs:
- Context / measurable problem:
- Alternatives considered:
- Decision and rationale:
- API/schema/file changes:
- Risks and rollback plan:
- Evidence (links to test_log entries / source docs):
- User approval (when changing baseline requirements):

### DEC-001 — Resolve work-order lifecycle and MCP scope | 2026-10-17 | ACCEPTED SPECIFICATION
- Scope: R07, R10, R11, R15; B00 follow-up design audit.
- Context: legacy WorkOrder moved DRAFT→PENDING_APPROVAL, while intended domain workflow approved plans before creating work orders.
- Decision: WorkOrder initial state is AUTHORIZED after plan approval, no DRAFT WorkOrder; update `contracts/state_machines.json`. Expand read-only investigation tools to 18 with typed schemas, retain dedicated official FalkorDB MCP read-only allowlist.
- Evidence: static validators in `test_log.md`; runtime pending.
- Change control: Codex must verify and implement exact guard in B13, not bypass it.

### DEC-002 — GraphRAG document graph isolation | 2026-10-17 | ACCEPTED SPECIFICATION
- Scope: R09, R13, R14.
- Decision: SDK-managed `civicly_docs` for document extraction/retrieval; canonical `civicly_knowledge` holds versioned source references and verified/proposed organization assertions.
- Reason: avoid SDK ontology/index collisions and preserve auditable domain semantics.
- Risk: cross-graph reference consistency is application-managed, not a transactional join; B11 validates reconciliation.

### DEC-003 — B00 audit and runtime baseline | 2026-10-17 | ACCEPTED AUDIT
- Scope: B00, preserving R01–R18. Read mandated entrypoints, all current backend docs, frontend contract/demo docs, normative JSON structures, scripts, source documents and tracking files. Legacy v1 remains archival authority only for the legacy validator.
- Use existing Python 3.12.1 + jsonschema 4.26.0 for audit; default Python 3.14.7 lacks dependencies and `python` alias is absent. No global install needed. Isolated project dependency resolution and pins belong to B01 after smoke tests.
- Docker read-only escalation confirmed Desktop 4.95.0 / Engine 29.8.2 linux/arm64; initial sandbox socket denial is resolved. Compose 5.6.0, Node 24.21.0, npm 12.2.0. No image or library combination verified yet.
- No Git repository (`git status --short` fails); initialize during B01. Selected model/provider/auth/MCP variables unset in current process; no secrets displayed or searched elsewhere.
- Alternative of scaffolding now rejected: CODEX_START_HERE mandates audit-only B00. No application code, dependencies, containers or product objectives changed.
- Evidence: TEST-20261017-B00-01–04.

### DEC-004 — Specification gaps, corrections deferred to relevant task | 2026-10-17 | ACCEPTED FINDINGS; UNRESOLVED
- B02/B04, R02/R09: 55 expanded Observation records OBS-0100–OBS-0154 use `value_number`; registry defines `value` (number). Generator repeats defect. Handoff validator omits unknown-field validation for expanded seed. Align fixture/generator with registry and strengthen checks before import; never drop measurements silently.
- B02/B03, R13: AGENTS.md requires tenant_id=demo-city; memory doc uses municipality_id; registry/seed define neither. Follow AGENTS intent with synchronized schema/migration/doc changes before repositories.
- B07/B17, R07/R09/R15/R16: closed MCP schemas omit documented common graph_revision/error/context fields; docs use simulated versus registry simulation_mode. ToolExecution and AgentTraceEvent lack portions of required server identity/schema/inventory/latency/path/redacted-arguments trace. Extend contracts and tests before handlers.
- B12/B13, R10/R11: Approval has version/hash/requester/decider but lacks direct plan ID/assignee/scope, with no plan-to-approval edge registered. AUTHORIZED WorkOrder initial state is already correctly resolved; association, immutable payload hashing, stale scope and reassignment guards still need contracts and runtime tests. API requested_by/submitted_by must be checked against authenticated identity, never trusted as authority.
- B12/B14, R10/R17: operations prose says ActionTask READY; machine uses APPROVED/QUEUED. RESOLUTION_VERIFIED is a resolution result, not ProblemCluster status (CONTROLLED) or Investigation status (COMPLETED). Runtime error/pause phases need explicit mappings; do not invent persisted states.
- B11, R09/R14: Document registry lacks required version/effective/source metadata; source manifest has owner_department_name rather than canonical owner_department_id. Only MD sources supplied; sourced PDF must be added for B11/B-END.
- B04/B19, R09/R18: seed has five operators (three department leads, analyst, approver), no ADMIN, one Inspection, no WorkOrder/AgentDecision records; target >=20 historical decisions/repairs is not supplied. Pickup actual_at is populated for MISSED and route cycles independently of point membership; validate semantics before decision-grade use. Counts do not demonstrate complete scenarios.
- B15/B17, R12/R16: DomainEvent/EventDelivery miss parts of documented revision/source/payload/lease metadata; API graph_revision strings differ from graph integers. Explicit serialization and recovery contracts required.
- Security, R06–R09/R18: legacy demo_scenarios.json contains hidden_ground_truth; scenario catalog exposes evaluation expectations. Future agent/API/MCP/GraphRAG runtime must exclude all evaluator and answer-bearing artifacts, including legacy contracts and delayed reveals. Repository presence and false visibility flag do not prove isolation.
- Alternatives: silently repair all contracts now or ignore gaps because supplied validators pass; rejected. Resolve in earliest relevant microtask with ADR plus synchronized docs/contracts/generators/tests. No objective waived.
- All 73 root manifest hashes matched before edits. Preserve manifest.json as original handoff snapshot; tracking-file hashes now differ intentionally. Source-document manifest is separate and remains validated.

### B00 — Planned exact compatibility commands (NOT RUN)
- B01: `python3.12 -m venv backend/.venv`; `backend/.venv/bin/python -m pip install falkordb fastapi pydantic pytest httpx`; `backend/.venv/bin/python -m pip check`; `backend/.venv/bin/python -m pip freeze`. Exploratory resolution, then smoke-tested pins/lock.
- After B01 creates Compose/tests: `docker compose config --quiet`; `docker compose up -d falkordb`; `docker compose ps`; `docker compose exec -T falkordb redis-cli MODULE LIST`; `docker image inspect falkordb/falkordb --format '{{json .RepoDigests}}'` (use actual selected tested tag); `backend/.venv/bin/python -m pytest backend/tests/integration/test_graph_smoke.py -v`; `docker compose restart falkordb`; `backend/.venv/bin/python -m pytest backend/tests/integration/test_graph_persistence.py -v`. Prove parameterized CREATE/MATCH, RO_QUERY denial, restart AND recreation with retained volume. No volume deletion on retained evidence.
- B02/B03: `backend/.venv/bin/python -m pytest backend/tests/integration/test_migrations.py backend/tests/integration/test_query_templates.py -v` for constraints/index readiness, multi-label/point syntax and bounded temporal verified paths.
- B06/B07: `npm view @falkordb/mcpserver version engines --json`; `backend/.venv/bin/python -m pytest backend/tests/integration/test_official_mcp.py backend/tests/integration/test_civicly_mcp.py -v` for real discovery/call/auth and denied writes.
- B10/B11: `backend/.venv/bin/python -m pip install 'langchain-falkordb[langgraph]' langgraph mcp graphrag-sdk`; `backend/.venv/bin/python -m pip check`; `backend/.venv/bin/python -m pytest backend/tests/integration/test_checkpoint_restart.py backend/tests/integration/test_graphrag_sources.py -v` for process restart and cited MD/PDF in isolated graph.
- These service/test paths are planned, not existing runnable deliverables. Verify installed APIs against official references in 12_falkordb_sources.md during each spike; record actual versions and adapted commands. No vendor compatibility asserted by B00.

### DEC-005 — B01 foundation design | 2026-10-17 | ACCEPTED IMPLEMENTATION SCOPE
- User accepted B00 and authorized B01 only. R04/R13/R16 foundation; all R01–R18 remain binding, none declared fulfilled. BLOCK-B00-02 and every DEC-004 finding remain OPEN.
- Implement only backend/app configuration + official-client lifecycle, services foundation-health check, backend/cli health entrypoint, tests, pyproject/uv lock, Compose, local setup helper, Makefile and documentation. No domain models/migrations, seed ingestion, API resource routes, MCP, agents or frontend.
- Preliminary runtime spike: official falkordb 1.8.0 + redis 8.1.0 on Python 3.12.1, ARM64 server module 60002 (6.0.2) / Redis 8.10.2. Parameterized CREATE/MATCH passes; ro_query rejects CREATE with server ResponseError. This is genuine DB verification, not a mock.
- Use official bundled Browser in the same verified image (digest to pin after automated acceptance), loopback-only 6379/3000, named graph and Browser volumes. Actual entrypoint uses REDIS_ARGS and /var/lib/falkordb/data. Use AOF appendfsync always plus snapshots for tiny demo; slower than everysec but minimizes acknowledged-write loss. Crash consistency across domain events is still B15, not proven by restart tests.
- Persist Browser session/encryption secrets in ignored local .env generated by helper; never hardcode or print them. Browser .data persistence requires image-specific path verification. Plain local DB connection is development-only; runtime MCP/agent privilege separation remains B06/B07.
- Use static read-only RETURN health template; do not expose arbitrary Cypher or write helpers to CLI. Smoke writes run only in isolated test graphs, never canonical graph. CLI reports foundation scope and checks only implemented dependencies; no claim full agent readiness.
- Pin resolved B01 dependencies after observed smoke compatibility and lock transitive packages with uv 0.13.1. Retain FastAPI/Pydantic as foundation dependencies with isolated TestClient proof; HTTP domain routes wait for B16. Later LangGraph/MCP/GraphRAG packages deferred to their own spikes, not omitted.
- Risks: vendor API changes, Browser storage path, container restart permission/network, finite connection/query timeouts. Tests cover real health/CREATE/MATCH/RO denial/no mutation/Browser backend query and persistence under restart+recreation, plus invalid config/unavailable DB redaction.
- Alternatives: separate Browser image, global installs, domain scaffolding or default read-only flag; rejected as unnecessary moving parts or beyond B01. No normative contract edits.

### DEC-006 — B01 verified versions, empty-graph health and persistence | 2026-10-17 | ACCEPTED IMPLEMENTATION
- Task B01 only; human acceptance pending. Foundations for R04/R13/R16, no complete product requirement claimed. DEC-004 unchanged; BLOCK-B00-02 OPEN.
- Tested Python 3.12.1 on macOS 26.5 arm64. Direct pins: falkordb 1.8.0, redis 8.1.0, FastAPI 0.143.3, Pydantic 2.14.1, pydantic-settings 2.16.0; dev pytest 9.1.1, httpx 0.28.1, jsonschema 4.26.0, uv 0.13.1. Build backend setuptools 80.9.0. uv.lock resolves 34 entries (33 installed in this platform); transitive versions/hashes retained. Independent clean-environment frozen install and uv pip check passed, not just the original pip environment.
- Image: falkordb/falkordb:6.0.2@sha256:107455e862a824e45e8e9f5a7fbfdf5e00a08b14e13eae2577c72fd9e3f59ba6, inspected architecture arm64. Running graph module version 60002, Redis 8.10.2, bundled Browser 2.6.1. Other architectures unverified.
- Actual installed API: FalkorDB(...).select_graph(name).query(query, params=..., timeout=milliseconds); ro_query uses GRAPH.RO_QUERY in inspected source. Server rejects CREATE, SET and DELETE with `graph.RO_QUERY is to be executed only on read-only queries`; original row unchanged. No unrestricted query surface is exposed through CLI.
- Real incompatibility with first health assumption: RO_QUERY on a missing graph returns `Invalid graph operation on empty key`. Health now checks PING + graph module, lists existing graph names, and runs bounded parameterized RO_QUERY only when configured graph exists. Fresh state explicitly reports uninitialized and graph_read=null; no bootstrap writes. Existing graph reports available/read=true. Alternatives: materialize canonical sentinel node or report every fresh install broken; rejected because B02 owns canonical initialization and health must be observational.
- Connection timeouts 2s connect/3s socket, query timeout 1000ms; validated finite settings and zero automatic Redis retries. Owned socket pool closed/disconnected after each context. Password uses SecretStr; CLI suppresses connection/config exception text.
- Redis persistence uses named volume /var/lib/falkordb/data, AOF appendfsync always and save 60 1. Observed fresh reads after same-container restart AND different-container recreation pass. Browser storage confirmed at process.cwd()/.data = /var/lib/falkordb/browser/.data, not entrypoint's separate /app/.data directory; named volume mounted at actual store. Browser marker survived and real logged-in Browser session/query worked after recreation.
- Ignored mode-0600 .env holds generated persistent AUTH_SECRET/ENCRYPTION_KEY for Browser only. No hardcoded secret; setup preserves existing file. Database is unauthenticated local developer access with loopback-only host ports, not runtime MCP authorization. Browser has its own default DB-user session; no Civicly operator RBAC implemented.
- FastAPI dependency smoke first used TestClient successfully but Starlette 1.8.0 emitted httpx deprecation. Final compatibility test uses httpx.AsyncClient/ASGITransport directly, validates Pydantic request rejection and OpenAPI; no project API routes implemented. This does not prove compatibility with future model adapters.
- Source verification: official https://github.com/FalkorDB/falkordb-py and installed package source; https://docs.falkordb.com/getting-started/clients; https://github.com/FalkorDB/FalkorDB (README persistence path); https://docs.falkordb.com/browser. Several guessed legacy docs/raw paths returned 404/inaccessible; actual installed image/driver inspection plus runtime tests controlled implementation.
- Git initialized on main, no commit or remote created. No contract or fixture changes; root manifest remains original handoff snapshot. Reversal: stop Compose without deleting volumes, remove B01 package/config artifacts if needed; don't delete supplied specs or stored evidence. Later dependency changes require new lock and affected integration smoke tests.
- Evidence: TEST-20261017-B01-01–06; docs/evidence/B01-tests.txt, B01-runtime.txt, B01-browser.jpg.
