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

### DEC-007 — B02 canonical schema and migration design | 2026-10-17 | ACCEPTED SCOPE BEFORE CODE
- User accepted B01; local baseline commit 426f6e1322dca9e83e470ee471b25b8df7f9e028 (synthetic local author Civicly Local Build), 102 files, no remote/push. Secret-value/private-key and excluded-file scan passed. Original supplied docs/demo/SCENARIOS.md trailing blank line triggered baseline diff whitespace warning; preserved original content. Git tree clean after commit.
- B02 foundations for R01/R04/R05/R09/R13/R15/R16; all R01–R18 remain binding, no product feature fulfilled merely by schema. No B03 repositories, algorithms, ingestion, agents, MCP/GraphRAG, operations or UI.
- Authorized scope correction: canonical registry v3 requires municipality_id=demo-city on every domain node/edge; tenant_id is not accepted as an alias. Framework tenant_id translation remains an explicit boundary mapping if a future verified framework requires it. Single demo namespace, no enterprise isolation claim. Update AGENTS and current architecture/contracts consistently per user override.
- Keep supplied v1/v2 fixtures unchanged (including 55 value_number defects). Static validators explicitly distinguish legacy structure from canonical eligibility, excluding only newly introduced v3 required fields from legacy presence checks. Strict application validation requires v3 and all mandatory fields, rejects unknown properties; it does NOT default legacy fields or discard measurements. B04 must explicitly convert source versions/scope/edge metadata and correct fixture defects before import.
- Preserve all 42 public node names, 47 relationship names and enum values. Add internal storage-only CivicEntity label for global node ID uniqueness across domain labels, without changing public ontology. Infrastructure subtypes retain base InfrastructureAsset label. Reserve CivicSchemaMigration for bookkeeping only, outside domain registry.
- Add stable edge id, municipality_id, created_at as mandatory scalar metadata; optional UTC validity interval and evidence pointer on every relation. Verified association needs nonempty evidence pointer; open/unknown validity permitted, no invented dates. Endpoint/direction, types/enums/unknown fields and temporal order enforced by pure registry validator and schema-only write compiler; graph-wide cycles/cardinality/reference existence/provenance authority stay B03+.
- Additive immutable migration plan version 1, compiled from registry snapshot with hash. Unique ID indexes/constraints per node label plus internal global ID label; mandatory grouped properties per label; relationship ID index/unique and mandatory common metadata per type; temporal/scope/status/point indexes where applicable. Poll db.indexes/db.constraints for OPERATIONAL; PENDING is not success.
- Real spike: FalkorDB 6.0.2 / client1.8.0 accepts CREATE INDEX FOR node/relationship, GRAPH.CONSTRAINT CREATE NODE/RELATIONSHIP MANDATORY/UNIQUE, multi-label CREATE and parameterized property maps. Native point works with expected float precision. Installed client lacks documented create_constraint helper; use official execute_command with separate arguments (not interpolated values). QueryResult lacks statistics attribute; use known result_set/header interface.
- Migration lock with finite lease, durable APPLYING/FAILED/READY record, definition/registry checksums/version guard and introspection on every rerun. Failure never deletes graph/volumes/data or operational constraints. Explicit retry-failed may recreate ONLY known FAILED constraints after operator data repair, never silently alter conflicting data. Tests exercise real partial state/failure/recovery, checksum/future-version rejection and lifecycle regression. No destructive down migration; roll forward.
- Planned paths: registry + scope metadata in normative contracts, current docs/AGENTS, validator scripts, app/graph/schema.py + migration plan/runner, services/schema.py, CLI/Makefile docs, unit + real integration tests, six tracking files and B02 evidence. Risk: DB constraints cannot enforce unknown/type/enum/endpoint/conditional semantics; application adapter validation is mandatory and limitation explicit. B01 probe and both volumes untouched.

### DEC-008 — Preserve asset_type vocabulary during B02 strictness review | 2026-10-17 | ACCEPTED BEFORE CORRECTION
- First B02 unit run: 31 passed, 1 failed. A new subtype-specific asset_type constant rule rejected five legacy DRAINAGE/ROAD/WASTE values in addition to the known 55 Observation defects. Original registry defines asset_type as a string, not a subtype enum.
- Decision: remove the premature constant restriction and derived storage mapping before canonical migration; use mandatory multi-label subtype identity as originally specified. Do not change existing asset_type vocabulary or fix fixtures in B02. Strictness means enforcing the normative contract, not inventing a new domain taxonomy. Test missing/unknown/primitive/declared-enum validation independently.
- Real B02 integration suite already passed all 8 tests on disposable graphs; canonical graph remains untouched. Update development migration registry hash before first canonical application; then freeze immutable plan. No applied canonical history rewritten.

### DEC-009 — B02 acceptance and operational limits | 2026-10-17 | ACCEPTED IMPLEMENTATION; HUMAN REVIEW PENDING
- Canonical migration 0001 applied then rerun using CLI; registry v3, municipality_id=demo-city, recorded READY. Immutable migration SHA256 94ab9fae6079fe7e87b41afd80701409db6bb51d529c2565dbd340896a5c923b; registry SHA256 12541990b58d65e8602bff77b93b735009616e7ee658b9e7582a7ae9f449aac6. Do not rewrite applied plan/hash; future changes require a new migration and runner support.
- Real catalog: 91 RANGE index groups (44 node +47 relationship, 304 property entries) and 182 constraints (91 UNIQUE, 91 grouped MANDATORY), all OPERATIONAL. All 42 public labels have id indexes/unique/mandatory constraints; storage CivicEntity enforces global node IDs, CivicSchemaMigration manages schema history. All 47 relationship types have indexed/unique IDs and mandatory id/municipality_id/created_at metadata.
- No packages upgraded: Python3.12.1, falkordb1.8.0, redis client8.1.0, Pydantic2.14.1, FastAPI0.143.3, pytest9.1.1. Same pinned image digest as B01, graph module60002/Redis8.10.2/Browser2.6.1. uv frozen-lock check and pip consistency PASS; package-data entry includes immutable JSON plan.
- Native enforcement limitation proven, not guessed: raw DB accepts an unknown property, while strict adapter rejects it. Database cannot enforce property types/enums/fixed scope/endpoint labels/conditional provenance/global cross-type edge IDs. B02 adapter implements structural rules; B03 controlled repositories must gate all writes and enforce graph-wide invariants. No claim that schema privileges authorize operational actions.
- Six infrastructure subtype labels + InfrastructureAsset + CivicEntity verified on real nodes. Native point index and parameterized native-point write/read verified (float precision tolerance); ID lookup EXPLAIN uses Index Scan. Node/edge duplicate IDs, grouped mandatory missing field, endpoint reversal, invalid temporal interval and evidence-free VERIFIED metadata refused as appropriate by DB or adapter.
- Failure recovery verified: actual duplicate data makes UNIQUE constraint FAILED; state remains non-ready and both records retained. After identifier repair in disposable test graph, normal rerun still refuses FAILED; explicit retry_failed recreates only that failed known constraint. Append-only scalar JSON state_history retains failures. Operational constraints never dropped by runner; readiness-drift test simulates external removal only in its disposable graph.
- Interrupted application after real index creation records FAILED and resumes additively. Preexisting partial index, held schema lease, registry drift, applied checksum tampering and future version checks tested. READY marker is insufficient if real catalog is incomplete.
- Final acceptance: 53 PASS /0 FAIL /0 SKIP, including all B01 tests and actual restart/recreation. Canonical schema status rechecked after lifecycle remains ready; zero domain nodes seeded; B01-PERSISTENCE unchanged; both named volumes retained.
- Scope finding in DEC-004 resolved by explicit user preference and synchronized contracts/docs. Remaining DEC-004 issues and all 55 value_number defects remain OPEN. Old fixtures retain hashes; static validators label their checks as legacy structure and report known defects rather than claiming canonical eligibility.
- Sources consulted: https://docs.falkordb.com/commands/graph.constraint-create (async constraints/readiness), https://docs.falkordb.com/cypher/indexing/range-index, https://docs.falkordb.com/cypher/known-limitations. Installed-version spikes take precedence: documented create_constraint helper absent, QueryResult.statistics absent, YIELD * unsupported. Use execute_command, result_set/header and explicit YIELD columns.
- Evidence: TEST-20261017-B02-01–06, docs/evidence/B02-all-tests.txt, B02-schema-catalog.json, B02-canonical-apply/rerun/status.txt and B02-spec-validation.txt. All 18 objectives preserved; B02 foundation is not product completion.

### DEC-010 — B03 repository/query design before implementation | 2026-10-17 | ACCEPTED TASK SCOPE
- User attachment accepts B02 and authorizes B03 only, including repositories, graph-aware integrity, eight query families, real concurrency/failure tests and local baseline. R04/R05/R08/R09/R13/R15/R16 foundations; all R01–R18 retained. No B04 import/fixture correction, agents/MCP/GraphRAG, operations/API/UI.
- Verified migration0001 READY with91 index groups/182 constraints OPERATIONAL, registry3 and B01-PERSISTENCE retained. Secret audit passed46 B02 files; local baseline3db6d873fb494a5ce456cb5d04a84f2be50919d4. Diff whitespace warnings are context markers in retained B02-git-diff evidence, not source edits; preserved. No remote/push.
- Preserve registry v3 and immutable migration0001 hashes. Declare B03 behavioral policy in separate graph-access contract/docs; no new public labels/relationships/enums/properties. Permit isolated civicly_b03_test_UUID targets in migration runner for tests only.
- Typed Pydantic node/edge/path/result records use stable public IDs, original edge orientation, path order, evidence IDs, municipality scope, as_of and application repository revision. Strict Registry validates every write/read, no property dropping. Mutable updates require expected content digest; ID/scope/version/created_at and immutable registry records cannot change. Future domain services remain responsible for auth/state-machine approval rules; repository is not an exposed dispatch API.
- Concurrency: one bounded Redis write lease per graph plus owner/epoch fence stored on existing internal CivicSchemaMigration record. Every domain mutation checks fence and repository revision in the same graph statement. New lease owner advances fence before validation; expired writers cannot commit after successor. Separate pending intent stores only IDs/hashes; domain mutation, audit append, revision and pending clear occur in one tested query. Lost replies raise explicit outcome-unknown; recovery only clears intent if unchanged pre-state is proven, otherwise fail closed. No automatic uncertain write retry, no cross-graph transaction claim.
- Real spike proves full-property CAS works and a two-node CREATE that hits UNIQUE rolls back the first new node too on6.0.2; not assumed from Neo4j. Single-query atomic mutation+metadata still needs dedicated failure tests. Ordered nodes(p)/relationships(p) return official client Node/Edge objects for explicit serialization.
- Graph-aware policies: actual endpoint existence/types/scope, verified evidence existence/reliability/date/attribution, unique edge IDs across types and domain IDs, duplicate temporal relationships, singleton active ownership/route/location/assignment cardinality, permanent task DAG acyclicity. Drainage cycles rejected unless explicitly inspected via verified inspection evidence; no universal ban on other network cycles. Bounded policy export fails closed when too large; no incomplete scan treated as proof.
- Read families: drainage_paths, shared_infrastructure, incident_history, maintenance_history, cross_category_paths, hypothesis_evidence, ownership_dependencies, temporal filtering throughout. All execute GRAPH.RO_QUERY via named templates; no raw query input. Validated hop/row/time/node/edge caps, parameterized IDs/times, actual source/target direction, explicit truncation. Cross-category path is a candidate association through recorded SERVES/LOCATED_AT/DRAINS_TO edges, never spatial proximity or causal proof. Historical node snapshots not reconstructed; future-updated records are excluded conservatively.
- Tests: isolated purpose-built canonical-v3 graphs; all requested rejection/traversal/shared/evidence/temporal/nearby/concurrency cases, stale fence/CAS/uncertain-reply recovery, atomic rollback, readonly cannot mutate, all53 B01/B02 regressions and SPEC validators. Human verifies named traversal example and full tests. BLOCK-B00-02 and all deferred DEC-004 findings remain OPEN.
- Planned files: graph models/repository/queries, graph-access contract, test fixtures/unit/integration, graph guide and Make target, small migration target whitelist update, six logs and B03 evidence. No dependency upgrade expected.

### DEC-011 — B03 installed-runtime results and limits | 2026-10-17
- Implemented DEC-010 with no dependency upgrades: Python3.12.1, FalkorDB client1.8.0,
  redis8.1.0, Pydantic2.14.1, pytest9.1.1; server6.0.2/module60002, Redis8.10.2,
  Browser2.6.1 and accepted image digest retained. No new public ontology values.
- Single-statement domain+metadata rollback, owner/epoch fencing, CAS, concurrent
  edge IDs/cardinality/cycle rejection, dropped response before/after actual commit
  and unchanged-prestate recovery are exercised against real DB. Inconsistent
  pending state remains intact and blocks reasoning; no fake success or automatic
  uncertain retry. Raw privileged DB writes remain outside the guarantee.
- Added eight named queries (including task_dependencies as operational dependency
  family) with real EXPLAIN plans. Fixed bounded grammar supports all()/nodes()/
  relationships(), zero-hop shared traversal, collect/UNWIND, relationship alternation,
  UNION ALL, parameter LIMIT and finite query timeout on installed server. Direction
  is derived from actual edge source/destination, not guessed from path order.
- Runtime deviation: projecting disconnected migration metadata with upstream
  variable-length path returned revision0 while separate read returned52; minimal
  spike reproduced in B03-runtime.json. Rather than trusting that projection,
  capture scalar repository revision before/after all retrieval validation and retry
  once on change. This is scoped to observed6.0.2 behavior, not an inferred universal
  bug or a new native transaction claim. No unsupported Neo4j procedures used.
- UTC registry parser allows fractions; query comparisons pad/truncate to Python
  datetime microseconds instead of unsafe raw lexical Z ordering. Historical node
  versions are not reconstructed. Future knowledge timestamps, including external
  source-evidence pointers on candidate relationships, exclude paths at as_of.
- Explicit singleton policy implements the ontology's primary location/owner/route/
  assignment semantics without adding a primary flag. DEPENDS_ON is permanently
  acyclic; drainage proof intersects validity intervals and allows explicitly
  inspected cycles only with verified attributed inspection evidence. Other network
  types remain unrestricted by a universal cycle ban. Missing bounds remain unknown.
- Limits:6 total path edges,100 paths,120 nodes,200 edges,1000ms; branch limit+1
  and result truncation, no claim that a bounded traversal proves no longer paths.
  Policy inspection2000 edges/10000 states and audit10000 entries fail closed.
  Audit archival, authorization, approval/state workflows and durable event delivery
  are later milestones. No API/MCP/agent/GraphRAG/seed/frontend scaffold added.
- Evidence samples: drainage3 nodes/2 edges/2 paths; shared5/4/4; incident3/2/2;
  maintenance6/5/4; cross-category7/6/1; hypothesis5/4/2 (support+contradiction);
  ownership3/2/2; task3/2/2. A nearby asset at a distinct location with identical coordinates and no
  physical-network link is excluded from the cross-category result.
- No mutation of canonical domain graph (0 nodes) or B01 probe. Same registry hash
  12541990b58d65e8602bff77b93b735009616e7ee658b9e7582a7ae9f449aac6 and migration
  checksum94ab9fae6079fe7e87b41afd80701409db6bb51d529c2565dbd340896a5c923b retained.
  No fixture/import repair; all55 defects and deferred DEC-004 findings remain open.

- B03 review packaging:9 tracked files modified /18 files created, exact inventory
  B03-files.txt and complete B03-git-diff.txt (self excluded). Final secret/ignored-file
  audit PASS; registry/migration/data/pins/Compose unchanged. Source acceptance89
  PASS (45 unit/44 real integration), plus8 strengthened-template rechecks PASS.
  All6 tracking files updated, B03 changes left uncommitted for review. No push.

### DEC-012 — B03-R corrective contract before coding | 2026-10-17
- User provisionally accepts B03 and requests B03-R only, before B04. Covers R03/R04/
  R05/R09/R15/R16 foundations; all R01–R18 remain mandatory. Immutable registry v3,
  migration0001,55 legacy defects and original review ZIP/evidence remain untouched.
- Cardinality gap confirmed: singleton_outgoing omitted IN_ZONE (primary location
  administrative zone) and PART_OF (primary incident cluster). Add both, preserving
  disjoint history and many incoming members. No primary flag/new ontology fields.
- HAS_SCHEDULE is not globally singleton: compare route + exact existing service_type
  over intersection of edge validity and schedule-node validity. Reject empty
  applicability and overlapping same-service definitions; permit disjoint date
  windows or simultaneous different services. schedule_spec is opaque, not a parsed
  recurrence language; multiple same-service recurring windows must be represented
  by one schedule definition, rather than claiming two free-text definitions are
  nonconflicting. Unknown bounds conservatively overlap; timezone differences alone
  cannot justify conflicting definitions. No service alias normalization in B03-R.
  Revalidate incoming schedule assignments on service_type/validity node changes,
  under the same writer fence, so mutable endpoint properties cannot bypass policy.
- max_hops means total path edges for every template, hard max6, default6 (formerly4).
  DRAINS_TO allowance is h for drainage, h-1 for shared (AFFECTS consumes1), h-4 for
  cross-category (four fixed connectors). Shared permits zero drainage hops; cross
  needs >=5 total. Reject requests below template/root-specific minimum. Fixed
  branches exceeding budget are omitted explicitly. No implicit cap increase or
  unbounded Cypher. Add typed result budget metadata and search_limited; truncated
  remains result-cap truncation. Bounded empty results never prove global absence.
- Unify GraphRepository/MigrationRunner target authorization: exact civicly_knowledge
  or civicly_bNN_test_<lowercase RFC4122 UUIDv4 hex>, NN02–25. Protect B01 runtime,
  document/checkpoint/other production graphs, arbitrary suffixes and malformed IDs.
  Naming is an internal target guard, not DB RBAC. This enables later isolated tests
  without implementing those milestones. Keep existing B02/B03 test names valid.
- Planned source: models.py/queries.py/repository.py/migration.py plus shared targets.py;
  graph_access contract v2, new corrective unit/integration tests, architecture/graph
  guide/benchmark plan and six tracking files. No dependency or database-plan upgrade.
- Tests: overlap/nonoverlap/multiple cardinality and schedule node/edge edits; default
  5/6-edge cross-category paths, insufficient budgets, longer bounded-negative paths,
  shared zero-hop/last-hop boundaries, disconnected assets, RO/revision/temporal
  regressions; accepted/rejected graph targets including real later-milestone UUID
  graphs. Run all previous89 tests including actual restart/recreation, strengthened
  templates and both SPEC validators. Human reviews these policies/results and the
  B04 benchmark plan; no bulk shortcut or city import is authorized here.

### DEC-013 — B03-R verified corrections and review boundary | 2026-10-17
- Implemented DEC-012 with graph-access contract v2; registry v3 and migration0001
  bytes unchanged. No node/edge property, entity name or enum invented/removed.
  Source/target existence, scope, strict fields, conditional evidence requirements,
  writer fence/CAS/pending audit, temporal checks and revision checks remain intact.
- IN_ZONE/PART_OF now temporal outgoing singletons. HAS_SCHEDULE compares exact
  route/service groups over edge∩node validity; conflicting/empty applicability
  rejected, different services/disjoint windows allowed. Node service/date edits
  also revalidate incoming assignments before commit. Concurrent schedule creation
  yields one success/one Conflict on real DB; no universal schedule singleton.
- QueryRequest default6 means total graph-path length; fixed connectors consume
  shared1/cross4 and grammar uses h-1/h-4 accordingly. Cross minimum5, shared minimum1
  (zero drain links valid); explicit errors replace too-small empty searches. Fixed
  branch lengths verified: maintenance1/2/2/3, ownership1/1/2/1, hypothesis2 or3.
  QueryBudget + search_limited are additive typed result metadata, not graph fields;
  truncated retains row/node/edge output-cap semantics. Negative results remain
  scoped to filters/bounds, never global disconnection or causal proof.
- Shared targets.py restricts both constructors to exact canonical or lower-case
  RFC4122 UUIDv4 milestone02–25 disposable names. Real04/25 graph tests prove reusable
  guarded operations; B01/docs/checkpoints/other production targets remain refused.
  This namespace is reserved for disposable tests, not production or DB RBAC.
- Verification:135 PASS (77 unit/58 real integration) including all previous89 and
  actual restart/recreation; strengthened templates22 PASS separately. Both SPEC
  validators and lock/dependency checks PASS. No B03-R test failure recorded.
- Performance work is only backend/B04_BENCHMARK_PLAN.md: expected scan/audit growth,
  pilot/full/repeat metrics, proposed timing/memory targets and preservation of every
  write guarantee. No full-data import, converter, bulk path, audit pruning or cap
  increase. B04 remains unauthorized pending review;55 fixture defects unchanged.
- Original B03 review ZIP/evidence remains unchanged. Corrective diff is against the
  pre-B03-R source snapshot, not a claim of a new Git commit. No push. R01–R18 remain
  mandatory; no product capability is declared complete by these corrections.

### DEC-014 — B04 authorization and conversion plan before ingestion | 2026-10-17
- B03-R accepted. Baseline135 tests PASS in131.08s including real lifecycle; catalog
  0001 READY. Secret scan152 files PASS; external review distributions/caches/env
  excluded. Local accepted baseline09482e2, no push. Source/registry/plan/fixture
  hashes recorded in B04-baseline-hashes.json. All18 requirements remain mandatory.
- B04 only: exhaustive offline audit, explicit legacy conversion, repository importer,
  dataset/scenario manifests, unit/real integration, pilot/full/repeat benchmarks.
  No B05 algorithms, MCP/agents/GraphRAG, operational workflows, API or frontend.
- Original seed_graph/expanded fixtures remain frozen evidence. Generator will emit
  a distinct corrected synthetic source revision to data/generated, never overwrite
  originals. It fixes value_number->value, missing version-aware required checks,
  MISSED timestamps and internally inconsistent pickup route construction. The old
  55-defect regression remains valid against the original fixture, not canonical data.
- Conversion maps all55 numeric values losslessly, preserves units and source JSON
  pointers/hashes, adds fixed scope/v3/stable hashed edge IDs. Canonical created/
  updated times describe materialization at explicit conversion_at; historical event/
  observation/recorded dates remain original. Actual DB import times/audit are separate.
- Legacy verified inventory evidence lacks observed_at; never synthesize a measurement
  date. Unsupported verification claims are explicitly downgraded to UNVERIFIED
  evidence/CANDIDATE edges, with original values retained in field reports. No hidden
  truth informs conversion. Missing dates/topology/history are gaps, not fabricated.
- Original pickup route disagreements and MISSED-with-actual_at are quarantined,
  not repaired by guessing actual execution. Corrected generator data is a new
  synthetic revision (declared differences), not a claim of recovered historical fact.
- Runtime bundle includes only canonical validated records and non-answer provenance;
  it never embeds catalog expected actions, hidden truth, delayed reveal text or
  scenario titles that reveal causes. Offline audit/readiness sees these files only
  to report availability/opaque hashes and counts; staged release manifest carries
  deterministic references, not payload text. Full runtime mount isolation remains B19.
- No invented physical connections: original SERVES is insufficient for S07's full
  waste/drain/road path. Preserve topology and report the gap for B19; use explicit
  purpose-built network fixtures to verify importer path preservation/disconnection.
- Importer targets only new B04 disposable names. All writes go through unchanged
  fence/intent/audit/policies; equal records no-op, changed records conflict explicitly,
  partial prefixes resume by stable IDs/hashes, uncertain outcomes stop for recovery.
  Native inline enum validation in schema adapter must also be enforced (no registry
  or migration change). No raw bulk shortcut or policy/audit-cap relaxation.

### DEC-015 — B04 additional preflight temporal findings | 2026-10-17
- REPORTS links whose report precedes the linked incident start are inconsistent and
  quarantined on legacy conversion. Corrected generator revision2.1 constructs new
  synthetic report times from their explicitly linked event start plus a declared
  offset, rather than cycling unrelated dates. This is new synthetic source authoring,
  not recovered historical fact; original dates stay frozen and revision deltas are
  reported. Observation/measurement dates and values are not changed.
- Converter preserves exact per-service names (WASTE_PICKUP/WASTE_COLLECTION); aliases
  are a reported nomenclature gap, not silently normalized. Schedule recurrence text
  is opaque; pickup time/schedule discrepancies are audit warnings, not invented
  execution corrections. Missing observation-to-asset links and scenario binding
  mismatches are explicitly reported for B08/B19.
- Materialization_at defaults to actual UTC at preparation. An early draft used a
  supplied demonstration timestamp; discarded before any DB import and rebuilt with
  the actual captured timestamp. Import repeats reuse that immutable bundle. File
  byte hashes and canonical-JSON source hashes are distinguished in input manifest.

### DEC-016 — B04 verified numeric wire precision | 2026-10-17
- First real pilot retained graph civicly_b04_test_407a845eafb843b7955dcc4bd00335e0
  stopped at LOC-004: source longitude82.96839999999999 returns82.9684. Real
  parameterized RO probes also return1.23456789012346 for1.2345678901234567.
  FalkorDB6.0.2 numeric responses expose15 significant decimal digits here.
- Converter explicitly normalizes only latitude/longitude to that verified decimal
  representation; every changed coordinate is recorded with its original value.
  This removes binary generator arithmetic residue, never supplies missing geography.
  Other non-roundtrippable floats are quarantined as unsupported precision, rather
  than rounding measurements or relaxing exact content-hash verification. All55
  original Observation measurements remain exactly unchanged. Registry/migration and
  accepted repository digest semantics stay unchanged. The failed pilot is retained.

### DEC-017 — B04 remaining source ambiguity and benchmark interpretation | 2026-10-17
- Preserve110 pickup scheduled timestamps even though local clocks differ from their
  linked schedule text. These are explicit warnings; recurrence expression/window
  interpretation is deferred to B08/B19, not silently guessed in conversion.
- Source has5 synthetic operators versus older4-operator prose; retain source IDs
  and report discrepancy for B13/B19. No authentication product capability claimed.
- Full import targets only isolated B04 graphs. Canonical promotion remains a future
  explicit review decision; retained final graph permits review without overwrites.
- Benchmark measures actual largest same-kind scans and query/parameter totals,
  not uninstrumented cycle comparison counts or lock-wait distribution. AOF snapshots
  are net server file size, not bytes written; actual rewrite logs retained. No claim
  that negative net AOF delta means negative I/O. The O(N²) audit rewrite remains a
  known scale limitation despite satisfying provisional small-demo timing targets.

### DEC-018 — B04 final input/report boundary checks | 2026-10-17
- Compiled bundles require exact node/relationship envelope keys as well as strict
  property validation. Unknown envelope metadata cannot hide behind a valid property
  hash. Malformed roots/record arrays fail explicitly before database mutations;
  source/bundle record counts remain bounded at5,000. No coercion/drop behavior.
- A final-verification connection loss is DATABASE_UNAVAILABLE with phase recorded,
  distinct from uncertain mutation replies. All confirmed writes remain intact;
  proof-driven unchanged rerun matches them without new domain mutations. Added real
  failure-after-writes test and malformed/unknown-envelope unit cases. No accepted
  repository, migration, query or graph-access-policy contract weakened.

### DEC-019 — B05 algorithms and counterfactual boundary before code | 2026-10-17
- B04 externally accepted; B05 ONLY. Baseline258 PASS/0 FAIL/0 SKIP in162.42s,
  both SPEC validators PASS,215-file secret/exclusion/source-hash scan PASS. Retained
  city858/1246 exact hashes and revision/audit2104 verified read-only. Local accepted
  B04 commit8aaf17c; no push. A verification read during baseline restart correctly
  refused connection; repeated only after lifecycle finished, no automatic retry.
- R04/R05/R09/R13/R15 graph primitives; all18 objectives preserved. No full memory,
  MCP/agents/GraphRAG, plans/approval/workflows/API/frontend or B06 implementation.
- New app/graph/analysis modules: typed models, fixed query reader, deterministic
  engine/case retrieval, isolated counterfactual runner and offline city evaluator;
  algorithm contract/guide, purpose-built fixtures/unit/real tests, evidence/review ZIP.
- FalkorDB6.0.2 actual dbms.procedures lists BFS/PageRank/WCC/etc; installed client
  ro_query calls _query(read_only=True). Native presence is not evidence/time safety.
  Use bounded Cypher paths with scope, time/status/provenance filtering; Python
  aggregations/components/Kahn ordering/ranking only over validated bounded exports.
  No PageRank score used as causal confidence. Official references checked:
  https://docs.falkordb.com/algorithms/ ; /cypher/procedures ; /cypher/functions ;
  /commands/graph.ro-query. Native compatibility spike/test evidence will be retained.
- Keep existing read maxima6 total hops/100 paths/120 nodes/200 edges/1000ms per
  query; add64 total queries/10000 compute steps/5s analysis wall and20 input roots.
  Connector AFFECTS consumes1 hop. Physical traversal defaults VERIFIED; exploratory
  accepts explicit VERIFIED/CANDIDATE/REPORTED and labels qualifications. Geography
  links never imply physical connectivity. Empty bounded searches are not global
  disconnection proofs; truncation and missing proof remain explicit.
- Count-based criticality and shared coverage have transparent lexicographic ranks,
  not arbitrary scores. Components are induced bounded weak components, not proven
  global partitions. DEPENDS_ON points from dependent to prerequisite; Kahn returns
  prerequisites first. Case matching uses actual asset/dependency/zone/issue/cluster/
  time plus existing asset-linked inspection/work-order/outcome context; a shared
  asset does not prove a work order resolved that incident. Missing history is a gap.
- Counterfactual source is read-only. Factory mints a fresh B05 UUID graph and copies
  a complete bounded snapshot through existing repository/migration safeguards.
  Source metadata/hash fingerprint checked before/after. Only that owned clone may
  delete a selected DRAINS_TO using repository fence/CAS/intent/commit/audit, or add
  explicit candidate DRAINS_TO through normal repository validation. No general
  source deletion API, schema/0001 edit, bulk bypass or graph rename/promotion.
  Partial failures retain clone for inspection; no unproven mutation retry. Full
  city exceeds clone export cap; controlled evidenced fixtures prove ablations.
- Data remains frozen. Broader bindings require explicit actual-network rationale;
  incompatible/missing primary bindings need B19 author review, not B05 rewrites.
  Runtime algorithm modules never read catalog/oracle/reveal files. Machine dependency
  report uses only B04 sanitized readiness and actual city paths; deferred findings
  remain open. Human reviews before/after ranking/paths, read-only source fingerprints,
  evidence/negative/budget cases, actual city limitations and review ZIP source.

### DEC-020 — B05 verified behavior and source-quality interpretation | 2026-10-17
- Native bounded algo.BFS invocation on controlled fixture includes an expired edge;
  filtered Cypher excludes it. Use native presence/catalog as capability evidence,
  not proof of Civicly evidence/time semantics. No unsupported native algorithm claim.
- Counterfactual DELETE verified on6.0.2 through existing fenced intent/atomic commit:
  preserve removed stable ID in a map alias; node identities unchanged, audit/revision
  advance only in owned clone. Factory-issued process-local capability checks every
  inherited writer session; target redirection refused. Compare rejects unrecorded
  clone changes and uncertain interventions; pending writes prevent cleanup until
  recovery. Failures retain named clones, never retry an uncertain mutation.
- Public fingerprints hash audit and writer metadata; owner/epoch lease values are
  not returned as frontend/MCP data. Add real clone creation timing, stable proof
  path IDs and explicit recorded change ledger. No new stored ontology properties.
- Case filters explicitly supplied by caller (issue/zone/date) are enforced; seed-
  derived issue/zone are ranking context, permitting real cross-category neighbors.
  Asset-linked repair/outcome is contextual evidence, never inferred incident resolution.
- City data remains unchanged. Actual42 DRAINS_TO are CANDIDATE; verified-only physical
  drainage has no qualifying paths. Exploratory D12->D18 is a reported candidate,
  not verified hydraulics. Four asset sets (S01/S02/S05/S07) legitimately broaden
  recorded AFFECTS via explicit bounded candidate paths. Eight omit recorded starting
  assets and are source-binding conflicts requiring B19 author confirmation. Six
  cluster bindings conflict with recorded primary PART_OF; three leave context
  unspecified. A missing path beyond a budget is UNPROVEN, not a source defect.
- S07 remains missing its full cross-category topology;55 observations unlinked;
  no historical WorkOrder/AgentDecision/InterventionOutcome chain. One real supplied
  historical inspection is retrievable for ROAD-R08 in exploratory asset context.
  Historical context/time/caps may prevent it being relevant to a specific bound case.
  Machine report assigns B08/B09/B11/B19 remediation, not B05 data rewrites.

### DEC-021 — Preserve positive case proof under caps | 2026-10-17
- Review found asset/zone factors only used later context-branch output; when that
  branch hit a cap, already-fetched positive matches could be understated or an
  explicit zone filter could wrongly exclude them. Index all existing validated
  AFFECTS/PART_OF/OCCURRED_AT/IN_ZONE edges from the bounded reader, including earlier
  match paths. Do not expand caps or invent missing relationships. Add real capped-
  zone regression; retain partial/lower-bound flags and exact proof path references.
- Matching indexes O(E+C) before sorting/context association; extra work metered.
  Re-run final-code evidence/performance and complete regressions after this fix.

### DEC-022 — B06 runtime boundary before implementation | 2026-10-17
- B05 externally accepted; local baseline6550d31108c34db6bb0bd5c111c7a41d09953125,
 57 files committed after263-file secret/exclusion/source audit; no push. Historical
 patch/failed-test logs have whitespace warnings, preserved as exact evidence.
 Baseline regression running against unchanged B05; final observed result recorded
 separately before acceptance. B06 supports R04/R07/R09/R15, completes none of R01–R18.
- Official published @falkordb/mcpserver1.3.0 (Node>=18/npm>=8) inspected from npm
 tarball; Node24.21.0/npm12.2.0 tested. Python MCP2.3.0 isolated spike successfully
 negotiates2025-11-25, lists7 tools and reads parameterized DRAIN-D12 from real city.
 Upstream main documentation may differ from release; tested package source controls.
- Select official supported stdio child-process transport for the local monolith,
 instead of default planned Docker HTTP. No TCP MCP listener/API key; private OS
 pipes and process ownership are transport access boundary. HTTP bearer tests are
 NOT APPLICABLE to this transport, not claimed passing. HTTP remains a future choice
 requiring new authenticated/private-network evidence. No custom B07 server added.
- Add separate least-privilege DB account: one exact accepted B04 graph key, PING,
 GRAPH.RO_QUERY, CLIENT SETINFO only. Real spike proves key/GRAPH.QUERY denial and
 GRAPH.RO_QUERY rejects mutation. Provision via trusted setup, persist only generated
 mode0600 credential file in ignored.runtime; ACL must be reprovisioned after DB
 recreation (no change to existing volumes/default developer account).
- Enable BOTH official DEFAULT_READONLY and STRICT_READONLY. Broker denies general
 query/delete/list_graphs; list_graphs would leak unrelated key names. Only four
 read tools considered, parameterized query restricted to named fixed templates,
 sampled schema capped and registry-validated labels/types. No arbitrary Cypher,
 resource/prompt/session/credential capability exposed to future agent interface.
- Trace actual server/tool/schema/inventory identity, sanitized argument hash,
 start/end/latency/status/result counts/revision when observed. No fabricated model
 rationale; graph-backed common envelope/persistence remains B07/B17 per DEC-004.
- Risks: privileged local administrator still can bypass code; field-level metadata
 access and query complexity are broker-enforced; database account prevents writes
 and other graph keys even via raw official session. Local OS process is trusted,
 no sandbox claim. No dataset/core repository/registry/0001 modification. Tests:
 original309, new unit+real MCP discovery/calls/negatives/lifecycle/recovery/malformed
 handling, independent Python read/full city fingerprint, both SPEC validators.
 Human checks exact returned identities/candidate evidence, denied tool/graph/write,
 sanitized traces, process cleanup and unchanged retained B01/B04/B05 evidence.

### DEC-023 — B06 observed compatibility and temporal strictness | 2026-10-17
- Baseline309 PASS/0 FAIL/0 SKIP in261.78s; both SPEC validators PASS. Fresh full-city
  record/audit/writer hash, retained B05 source/clone and B01 probe equal B05 evidence;
  canonical0001 READY. Initial harness missing graph_name failed TypeError, corrected.
- First authenticated official startup timed out: both official Python and Node
  clients use INFO for Sentinel detection. Add only INFO to the planned ACL command
  set; no broader category grant. Reconfigured real proof PASS. Python2.3.0 SDK
  adds pinned MCP/types2.3.0 dependencies without changing original direct pins;
  Node lock resolves falkordb6.8.0 and @modelcontextprotocol/sdk1.32.1, actually tested
  against database6.0.2. INFO server metadata is not exposed through broker tools.
- Verify exact7 discovered names and all observed JSON-schema hashes against new
  official_mcp.json. Four tools exposed through strict broker shapes; never pass
  arbitrary Cypher. Raw received count differs from final validated-call count in
  traces. Unknown schema/property/scope/endpoint values fail closed. Only storage
  labels deliberately filtered; source records are not silently transformed.
- Review caught direct UTC string precision comparison in new B06 template before
  acceptance. Reuse existing B03 GraphQueries._time_key and normalize supplied as_of
  to microsecond precision. Actual retained edge tests equivalent .962Z/.962000Z and
  one microsecond earlier without changing data. No B03/B05 temporal contract weakened.
- Malformed output handling has mocked unit cases plus an explicitly labeled local
  fault injection AFTER actual official MCP read; this does not assert an upstream
  server defect or fabricate an integration success. Missing/wrong DB auth proven
  by no successful initialization; stdio has no HTTP bearer auth. No B07 work.

### DEC-024 — B06 final evidence and review gate | 2026-10-17
- Final complete B01–B06 command361 PASS/0 FAIL/0 SKIP in329.97s,255 unit/106 real
  integration (B06 adds37 unit/15 real cases, including explicit local output-fault
  injection after real read). Original309 source tests unchanged. Both SPEC validators
  PASS; npm ci frozen install/pip check/compile/whitespace and actual-secret audit PASS.
- Actual DB same-container restart AND different-container recreation retain named
  volumes; Browser HTTP200/storage checks PASS. Reprovisioned volatile B06 ACL, reran
  real MCP proof afterwards PASS. Fresh full2104 city record hashes/revision/audit/
  writer fingerprint, original B01 probe and retained B05 source57/clone59 match
  accepted evidence. Canonical0001 remains READY,91 index groups/182 constraints
  OPERATIONAL; no seed/promote/delete/volume reset or immutable migration/registry edit.
- Exact source/files/diff/evidence in B06-FILES.md/B06-changes.patch/B06-RESULTS.md and
  command guide. No B06 ZIP generated; B05 ZIP unchanged. No B06 commit/push requested;
  B06 diff remains reviewable against accepted B05 local6550d31.
- B06 complete at official runtime/broker foundation only. Remaining DEC-004 findings
  retain designated tasks. Proposed B07: custom Civicly Python MCP for implemented
  typed read capabilities, shared service boundary/common envelope and trace-contract
  synchronization, real discovery/call/provenance/error/permission tests. No B08+
  complaint/agent/GraphRAG/operational/API/frontend features started. STOP for review.

### DEC-025 — B07 scope/security prerequisite before implementation | 2026-10-17
- B06 accepted; B07 ONLY. User reports exposed.runtime/mcp-credentials.json in an
 external full-project archive. Rotate that DB credential before integration, revoke
 active named-user connections, prove old auth denied/new read works; never log values.
 Existing B06 audit covered Git candidates, not arbitrary full-folder archives; do not
 equate its exclusions to proof that an external archive excluded ignored files.
- R04/R07/R09/R15 foundations; all18 objectives remain. Implement declared READ
 tools using B03/B05 interfaces only. Future write tools remain unregistered/denied;
 unavailable memory/GraphRAG/workflows/doc-version capabilities return explicit gaps,
 never scaffold their later business features or fabricate success.
- Preserve city/0001/registryv3. Separate B07 trace graph: existing normative
 ToolExecution node + storage-only companion detail, with explicit additive0002
 trace-storage migration/own bookkeeping. No extra domain ontology properties or
 modification of immutable0001. Controlled atomic trace writes use existing repository
 fence/revision/audit protocol; source DB credential remains read-only/one graph.
- Synchronize shared closed MCP envelope/trace schemas, retain public tool-specific
 payloads and simulation_mode (documented simulated alias retired). Namespaces official
 and civicly distinct. Future model interfaces receive typed broker tools only.
- Test actual server/list/call, strict args/output/permissions/graphs, provenance/time/
 candidate separation, unavailable data, malformed-output fault injection, timeout/
 restart, graph-backed traces and original361 regressions incl persistence; both SPEC
 validators. Human checks exposed-password denial, real inventory/results/trace IDs,
 exact retained fingerprints and limits. No model-selected rationale claim or B08+ work.

### DEC-026 — B07 contract/storage and runtime implementation choices | 2026-10-17
- Credential incident rotation: actual old password auth DENIED/new auth+city RO PASS;
 active named-user connections revoked, replacement0600 atomically written. No values
 or password hashes in evidence. Accepted B06 index52-file secret audit/local baseline
 24e80725ead2903516ecd36db2142f8fe36b2760; no push. Inherited361 PASS in305.72s.
- Keep registryv3 and0001 immutable. Add storage-family0002 adjunct only to separate
 capability-owned B07 trace graph, own CivicMCPTraceMigration ledger. Existing
 ToolExecution stores normative core properties; same-ID CivicMCPTraceDetail stores
 sanitized validated JSON/hash. Compatible native indexes/unique/mandatory readiness
 verified. Existing MigrationRunner still verifies0001; no migration downgrade or
 city trace pollution. Alternative adding fields to v3 would invalidate immutable
 checksum/all B02–B06 readers; companion isolates storage without changing ontology.
- Source uses rotated readonly city credential. Trace writer has only trace graph+
 exact repository lock key and required GRAPH.QUERY/RO_QUERY/INFO/PING/CLIENT SETINFO/
 SET/GET/DEL/EVAL/EVALSHA/SCRIPT LOAD commands. Trace writes reuse fenced intent,
 atomic record+detail+revision+audit and read-back verification. No auto Redis retry;
 uncertain trace writes fail closed with existing pending/recovery protocol. No
 cross-graph transaction/exactly-once claim or general mutation MCP interface.
- Two correlated observations: server execution persisted before reply; broker
 validates response and checks persisted output hash, then appends separate child
 observation (actual transport protocol/latency/denial). A corrupted output never
 overwrites server history. Trace failure prevents acknowledging successful calls.
 Invocation context roles/origin are operator/application, not model choice; rationale
 null. Same-user trusted process boundary remains, not B13 operator authentication.
- mcp_tools schema3 retains18 names/permissions/tool-specific fields; registers12
 READ and no6 future writes. Adds shared required context/data/revision/error/search
 bounds/server/execution/schema/inventory fields. simulation_mode is canonical;
 documented simulated alias retired. New mcp_envelopes holds shared TraceRecord.
 AgentTraceEvent synchronized identity/hash/latency fields; revision now integer|null
 and rationale nullable, optional new API metadata; no B17 route/SSE implementation
 or claim all future API discrepancies resolved. Other DEC-004 findings stay OPEN.
- B03 maintenance/graph decoding and B05 reachability/cases reused. Manual fixed
 bounded reads only for already registered pickup/road snapshots/direct decision
 evidence. No Observation->Location association exists: external tool reports gap,
 never assigns55 unlinked measurements. Memory/procedure/doc/monitor tools explicitly
 UNAVAILABLE until B10/B11/B14/B15; no filesystem source/evaluator exposure. Work-order
 lookup reads only existing status, no workflow implementation. Default physical
 traversal VERIFIED; include_candidates explicit, candidate context never causality.
- Bounded templates use parameter values, max100 rows +lookahead/120 nodes/200 edges/
 100 paths/6 hops and B03/B05 UTC rules. Wire schemas include trusted _context;
 public broker schemas exclude it. Namespace civicly:: vs official::, actual server/
 input+output schema identity checks. Private stdio with64 server calls/serialized
 handlers,32 default broker calls/8s client deadline; finite DB query/socket budgets.
- First all-handler proof surfaced maintenance duplicate evidence IDs: strict
 validation correctly returned ERROR. Deduplicate provenance/copy lists, rerun actual
 proof and assert no handler ERROR. First25 real cases PASS; final strengthened suite
 and full regressions follow. No source data repaired or later feature implemented.
- API compatibility refinement: AgentTraceEvent retains nullable tool_name for later
  non-tool state events and permits both official-falkordb/civicly-domain server IDs.
  This is shared metadata contract work only; no API/SSE handler is implemented.
- Typed dependency exposure refinement within the existing READ tool: optional RPC
  network=DRAINAGE(default) or TYPED_DEPENDENCIES. Reuse B05 dependencies for forward
  DRAINS_TO/UNDERLIES/COLLECTED_BY, rather than narrowing all infrastructure to drains.
  Reverse/BOTH typed mode rejected explicitly (B05 only implements forward typed
  dependency traversal). Legacy asset_ids contains only actual InfrastructureAsset
  IDs; full route/asset/edge path remains in typed data. No ontology property/enum
  change. Actual WASTE-W03→route and PIPE-P02→ROAD-R08 candidate proofs2 PASS in7.13s.
  Final full regression rerun after this bounded adapter/schema refinement.
- Final trace review ensures SERVER observations copy the validated domain error code
  (e.g. DATA_UNAVAILABLE/READ_FAILED), rather than only protocol/argument denial codes.
  BROKER SUCCESS means validated transport receipt, not domain capability success;
  the parent SERVER observation retains domain status/error. Added pure trace-contract
  unit regression; final complete suite rerun after this metadata correction.

### DEC-027 — B07 final evidence and review gate | 2026-10-17
- Final complete426 PASS/0 FAIL/0 SKIP in350.75s:288unit/138actual integration. B07
  adds33unit/32real; all original361 source tests preserved. Both SPEC validators
  PASS; actual operator MCP proof after recreation has initialize2025-11-25 /
  civicly-domain1.0.0 /12 actual tools-list schemas /all12 responses/no handler ERROR,
  plus explicit candidate exploration/waste→route/utility→road and15 server traces.
- Credential incident old AUTH DENIED/new scoped RO PASS; replacement persists in
  private file and volatile ACL reprovisioned after DB recreation, never reintroducing
  exposed value. No credentials in candidate source/logs; no B07 archive generated.
- Compatible trace family0002 READY:2 additive index groups/4 OPERATIONAL constraints;
  trace graph native totals93/186.482 ToolExecution records observed after final proof.
  Fresh connection verifies13 pre-final proof traces survived actual recreation.
  Source all2104 record hashes/content/revision/audit/writer state, B01 probe and B05
  source57/clone59 exactly retained. Canonical0001 still READY91/182; immutable sha
  and registryv3 unchanged. No source/canonical domain writes or volume removal.
-94 protected original files unchanged; only explicitly authorized MCP/API trace
  contracts updated. Original dependency pins/18 tool names+permissions preserved;
  no leaked official/custom child process. Source patch/file inventory/evidence
  finalized under docs/evidence; B07 remains uncommitted for human review, no push.
- B07 completes runtime read/trace foundation only. Shared MCP/trace DEC-004 portion
  resolved; agent rationale/API projection/event durability/document/source/history/
  approval/evaluator findings retain designated gates. Proposed B08 ONLY after review:
  complaint normalization/de-duplication, Incident-vs-cluster recurrence grouping and
  three issue validators; no agents/GraphRAG/operations/API/frontend. STOP.

### DEC-028 — B07-R authorized corrective scope and compatibility | 2026-10-17
- B07 technically accepted; only B07-R authorized before B08. Supports R07/R09/R15,
  preserving graph reasoning R04/R05 and all18 binding requirements. No operational
  lifecycle, ingestion, agents, API or frontend implementation.
- Maintenance evidence must be attributed from each event's own validated B03 proof
  paths, never the response-wide union; aggregate evidence remains response-level.
- Fixed pickup/condition reads must apply UTC-normalized window/visibility predicates
  and deterministic chronological order before100+1 lookahead. Existing graph/output
  caps and RO_QUERY remain; no B03 policy or migration changes.
- Work-order empty blocking/latest-event lists represent unavailable B12–B15 facts,
  not verified absence. Preserve wire schemas and express limitations in existing
  gaps/reservations +PARTIAL envelope; document machine-contract semantics.
- Tests use disposable graphs through a test-only actual SDK server harness and the
  unchanged actual DomainBroker/TraceStore; harness source substitution is explicit
  fixture evidence, never production city evidence or caller-selectable graph access.
  Production fixed-city context/ACL/identity and existing real city tests unchanged.
- Before edits snapshot accepted uncommitted B07 Git candidates to /tmp for exact
  B07-R-only patch and original-file hash comparison; no credentials/ignored files.
  Verification: focused unit/real MCP+DB, full pytest --run-persistence, both SPEC
  validators, fresh retained city/B01/B05/trace proof and secret/source audit. Human
  checks independent event sources, >100 date-window ordering and explicit work gaps.

### DEC-029 — B07-R corrected semantics, final verification and stop | 2026-10-17
- Accepted B07 working-tree baseline retained (Git HEAD still accepted B06 baseline
  24e8072; no forced commit/push). Exact B07-R-only diff uses snapshot/hash manifest.
- Per-event evidence is its own validated prefix/supporting PRODUCED path, not response
  union. Later outcome evidence does not retroactively support an order event. Existing
  response-level union preserved. No new properties, entity types or relationships.
- Existing fixed pickup/condition templates apply inclusive requested window +node/edge/
  referenced-Evidence visibility before UTC-normalized time/eventID/edgeID ASC and
  LIMIT101. Existing GraphQueries._time_key reused unchanged.100 eligible false versus
  101 true truncation proven; graph export still capped with atomic citation context.
- Keep blocking/latest-status lists wire-compatible as explicit UNKNOWN placeholders,
  not verified absence. Existing data.gaps +PARTIAL suffice; no operational schema
  expansion. Server preserves these gaps on absence/failure. Only four machine
  result_semantics descriptions changed; all18 input/output schemas/permissions and
  inventory hashes unchanged. Future B12–B15 supplies facts, not this corrective pass.
- Actual4 product FAIL before fix; final focused5 structural/fake units +9 real SDK/
  FalkorDB cases PASS. Full440 PASS/0 FAIL/0 SKIP in368.60s (293 unit/147 integration),
  original426 tests unchanged; both SPEC validators PASS. Initial fixture validity and
  new test-module collision errors preserved separately, not passed off as product
  reproduction or hidden by weakening constraints. No live agent/model rationale.
- Fresh city fingerprints858/1246/revision2104/audit, B01 and B05 source57/clone59 and
  canonical0001/trace0002 retained.13 early B07 traces +15 final B07 traces unchanged;
  4 pre-correction +11 corrected fixture observations verified after actual lifecycle.
  Production-city initialize/list/all12 calls,15 server trace readbacks/no ERROR PASS.
-333 accepted B07 files unchanged outside11 deliberate edits; dependency pins/schema/
  migration/policies/algorithms/data/official broker/shared envelopes preserved. Actual
  local secret scan PASS/no child process leak; no archive/external ZIP safety claim.
- No B07-R acceptance blocker; human review gate remains. Proposed B08 ONLY after
  review: complaint normalization/same-event dedup, Incident-vs-ProblemCluster recurrence
  grouping and three issue validators. No B08+, operational workflows or ontology seed.

### DEC-030 — B08 authorized scope, normalization and consistency design | 2026-10-17
- B07-R accepted. Local clean baseline6afdd09892502a8b47a7f840ced1491c38a002d3 after440
  PASS/0 FAIL/0 SKIP in386.74s, retained data/migration/trace proof and actual secret scan.
  Historical audit references absent Archive.zip; leave absent, exclude archives from
  Git. Source whitespace check PASS; raw evidence patch/log whitespace preserved rather
  than rewriting history. No push/archive. B08 ONLY; all18 objectives remain binding.
- R02/R03 with R01/R04/R05/R09/R15 support. Typed app.services.complaints models/reader/
  writer/service; new complaint_intake contract, guide and focused real tests. Preserve
  schema registryv3, migrations0001/0002, source city/B01/B05, MCP and all old tests.
- Preserve raw submission in existing UNVERIFIED Evidence.summary as bounded validated
  JSON intake journal; no public ontology/migration change or competing storage. Existing
  Complaint source fields hold normalized source identity. Stable external key excludes
  delivery channel/version; changed payload/version conflicts rather than overwrites.
  IDs are case-sensitive NFKC+trim; description whitespace normalized; aware ISO offsets
  normalized UTC; unsupported units/types fail, optional missing facts yield gaps.
- Two durable phases: public repository creates PREPARED journal; one fenced _commit
  validates all new/update nodes/edges then atomically creates complaint/incident/cluster/
  REPORTS/PART_OF/OCCURRED_AT/REPORTED AFFECTS +COMMITTED journal receipt +revision/audit.
  Existing journal anchors before-hash recovery. No automatic unknown-write retries.
  Explicit retry resumes unchanged PREPARED journals or returns verified historical
  COMMITTED receipt; no B15 event/outbox claim. All values parameterized.
- Same-event matching requires same category/subtype/location/explicit asset set,
  overlapping declared interval, compatible attributed event reference and bounded
 24-hour start gap (or identical explicit event reference). No complaint-count rule.
  Repeated context after a dated ENDED record proposes RECURRENT; unresolved distinct
  occurrences propose PERSISTENT; reported long duration can propose persistence.
  Missing end/outcome dates remain uncertainty, never work-completion resolution.
- Cross-category occurrences stay separate; shared explicitly reported asset or actual
  verified B05 topology can support contextual CROSS_CATEGORY grouping, never cause.
  Candidate paths/proximity do not establish physical grouping. Ambiguous multiple
  eligible clusters get a separate primary cluster and review alternatives.
- Reviewed grouping correction requires trusted internal reviewer context, reason and
  expected hashes; closes known old PART_OF interval and adds new membership atomically,
  retains old edge/audit/evidence. No MCP writes/auth/approval/state-machine bypass.
- Tests: strict models/units/source preservation; real same-report/same-event/distinct/
  persistent/recurrent/cross-category/disconnected matching, all issue histories, temporal
  cardinality/CAS, concurrent intake, real statement failure/lost reply/recovery, city
  read-only preview and real MCP compatibility. Full regressions/persistence +SPEC.
  Risks: ambiguous/legacy source context, finite scan budgets, no historical node replay,
  O(N) audit, trusted local-write boundary. Human verifies graph IDs/paths/gaps and retries.

### DEC-031 — B08 implemented architecture and explicit limitations | 2026-10-17
- Python3.12.1/Pydantic2.14.1/FalkorDB client1.8.0/Redis8.1.0/MCP2.3.0 existing pins;
  no installs/lock/image changes. Actual native compound query smoke1 PASS in2.86s;
  first27 unit PASS/21 real PASS in60.11s; strengthened57 PASS in89.25s plus3 new real
  PASS in7.01s. Final source covered by complete504-test regression (running).
- Keep graph schema/migrations unchanged. Existing Evidence.summary is explicitly
  serialized, strict bounded journal JSON; graph remains source of complaint/incident/
  cluster identity/relationships. Journal anchors actual before-hash recovery. New
  writer permits only approved nodes/edges, REPORTED associations, cluster pattern
  updates (no lifecycle state changes), closing old PART_OF. Native rollback/lost
  response/concurrent source conflicts tested; no fake success or event-outbox claim.
- Complaint RECEIVED is intake acknowledgment within existing free string vocabulary;
  imported ACCEPTED remains unchanged. Incident initial REPORTED and cluster OPEN
  follow state contracts. Claimed end does not set ENDED; test source histories use
  explicit authored states/normative transition order, not new operational workflows.
- First external submission original preserved; same normalized retransmission returns
  historical receipt, independent source reports keep separate provenance. Matching
 24h heuristic can be ambiguous; explicit source event references/intervals and reviewed
  correction resolve uncertainty. Persistence provisional when termination unrecorded.
  Multiple eligible clusters produce review alternatives, not arbitrary selection.
- Typed history summaries retain dated status/outcome records and qualified source
  context. Conflicting quantities retained; unit conversion overflow/future rainfall
  rejected. Verified B05 context may relate separate categories in either arrival order
  without reversing an edge or promoting reported impact/cause to verified fact.
- Writes restricted canonical/B08 test targets; accepted city read-only previews and
  original source/B01/B05/trace evidence retained. Canonical seed promotion not performed.
  Future working graph integration remains explicit; no competing datastore.
- Actual MCP read of new incidents uses explicitly labeled test-only source substitution
  while production fixed context/official+domain namespaces,12 READ/6 deferred writes,
  envelopes/traces untouched. No agent-selected rationale.
- Retained small B08 graph created for real lifecycle proof. Before-lifecycle operator
  verification replays5 receipts with no domain changes; owner/epoch alone advances.
  Post-lifecycle uses latest fingerprint anchor. Corrected generic harness wording
  before final proof: no lifecycle claim without actual successful lifecycle log.
- Source/receipt/journal bounds, O(E)/O(N) integrity/audit costs and finite readback
  explicit. No bulk bypass, generalized auth, event delivery, root-cause verification,
  complaint HTTP route, LLM/GraphRAG or frontend. All18 objectives retain later gates.

### DEC-032 — B08 equivalent-unit idempotency correction before acceptance | 2026-10-17
- New exact regression exposed one canonicalization defect: normalized request hash
  still included input unit representation, so0.29m vs29cm conflicted; float conversion
  could also produce28.999999999999996. Preserve failure evidence, fix before review.
- Canonical request hashes now use converted quantity/value/unit with decimal
  arithmetic, while raw first input and assessment original values/units remain.
  PREPARED resume plans from first stored original rather than retransmission spelling.
  Changed actual measurement/source-version still conflicts. No ontology/schema/migration
  change or accepted B01–B07-R data rewrite. Initial504 run retained as interim; final
  complete suite rerun after this fix and a real interrupted equivalent-unit retry.

- B08 contract refinement before final regression: require an appropriate primary
  road/collection-point when explicit assets supplied, while allowing secondary pipe/
  drain infrastructure. The registry permits Incident AFFECTS any InfrastructureAsset;
  do not narrow cross-category context to homogeneous asset lists. Waste pickup reads
  apply only to actual collection points. Added real mixed-asset acceptance test.

### DEC-033 — B08 final acceptance evidence and human gate | 2026-10-17
- Final507 PASS/0 FAIL/0 SKIP in438.89s:326 unit/181 actual DB-MCP integration; adds
 33 pure unit+34 real cases, all440 accepted tests untouched. Both SPEC validators
 PASS; compilation/source whitespace checks PASS. Unit repro failure/interim504 run
 retained, final full rerun includes decimal-unit/mixed-asset corrections.
- Retained actual B08 graph891b6aa292074c03a93c21451c7206f9:5 complaints/4 incidents/
 2 clusters,26 nodes/23 edges/revision26. Exact complete fingerprint including writer
 state survived actual restart/recreation versus latest pre-lifecycle anchor. Five
 explicit replays preserved domain content/revision/audit/counts; only owner/epoch
 advanced as documented. All source/receipt/relationship evidence real, no mock success.
- Actual city858/1246/revision2104/audit/writer fingerprint, original B01 probe, B05
 source/clone and READY0001/0002 preserved.43 accepted B07/B07-R observations hash-/
 evidence-verified from committed baseline proof IDs.1038 ToolExecutions observed
 after new production-city proof, not agent runs. Actual initialize/list12/call12/
 readback15 PASS with no handler ERROR; candidate42 links unchanged.
-358 accepted files outside10 explicit documentation edits unchanged, including all
 existing app code/tests/contracts/data/locks/migrations. Generated B07-R fixture proof
 saved separately then accepted HEAD bytes restored; no history lost. Actual local
 secret scan/no leaked process PASS. No review ZIP/archive or external-export claim.
- Source package/contract/guide/tests/evidence and all six trackers finalized for human
 review. B08 uncommitted relative clean local6afdd09 baseline; no push. Only baseline
 prerequisite.gitignore archive exclusions committed alongside accepted B07-R source.
- Known limits remain explicit: heuristics/ambiguous/end-date/source gaps, provisional
 patterns, finite context/journal/receipt bounds, O(N) audit, local trusted review not
 B13 auth; no canonical seed promotion or B15 event delivery. All18 requirements bind.
 Proposed B09 ONLY after review: evidence/hypotheses/immutable assessments, root-cause
 verification guards and inspection request/report lifecycle. STOP.

### DEC-034 — B09 baseline trace-test compatibility correction | 2026-10-17
B08 externally accepted; B09 ONLY authorized. Before B09 application changes, fresh
507-test baseline:506 PASS/1 FAIL in457.46s. Existing B07 trace-persistence test
searched arbitrary first1000 detail rows for a new child; retained trace count now
exceeds1000. Preserve all records and the same test assertions. Replace its unrelated
row cap with parameterized exact serialized parent_execution_id filtering before
LIMIT2, then validate actual typed child/hash readback. No runtime/envelope/schema
change or trace deletion. This genuine compatibility adjustment is included in the
local B08 baseline after rerun; record both attempts. Do not push or archive.

Correction target PASS:1 test in4.36s; remaining506 passed unchanged in full baseline.
Both SPEC validators PASS; baseline complete-suite failure retained, not relabeled
a507-pass single run. Full B09 regression will repeat all507 tests after additions.
Retained B08 five receipts/domain/revision/audit and source/B01/B05/migrations/traces
verified after actual restart/recreation. Old B07-R proof restored; B08 fixture tests
refresh their generated proof during baseline, included in baseline snapshot.

### DEC-035 — B09 evidence/hypothesis/inspection design before coding | 2026-10-17
- Clean local B08 baseline00d98745d8d7bb1c8077f61c36f3779deab2b4c1, no push.
  Prior baseline attempt506 PASS/1 FAIL; corrected trace test1 PASS; all507 covered
  across those runs, not claimed as one clean full run. B09 full regression required.
- B09 only: R08/R09 plus R04/R05/R11/R13/R15 foundations; all18 remain binding.
  New services.evidence models/policies/reader/writer/service, evidence_hypotheses
  contract, EVIDENCE.md, focused unit/real DB/MCP fixtures/evidence and six trackers.
  Exact tests: pytest backend/tests/unit/test_evidence_models.py and
  backend/tests/integration/test_evidence_domain.py; full pytest backend/tests -v -s
  --run-persistence; make test-spec; retained fingerprint and production MCP proof.
- Registryv3/0001 unchanged. Existing Evidence.summary holds strict versioned proposal,
  report and operation-journal JSON. Existing Hypothesis.statement remains readable
  text; proposed mechanism/confirming/falsifying observations live in proposal source.
  Append-only HypothesisAssessment.rationale serializes typed assessment snapshot,
  previous ID, evidence/finding digests, actual paths/revision/limits/state-transition
  sequence. No new ontology fields/relationships or shadow database.
- Inspection→INSPECTS→asset, Inspection→PRODUCED→Evidence→ESTABLISHES→Finding;
  request source references investigation/department/actor because no registered
  direct investigation→inspection edge exists. Proposed/requested inspections do not
  create report/finding records. Explicit machine transitions and CAS; completed only
  with actual submitted observations and chronology. No dispatch, work orders/outbox.
- Deterministic versioned domain criteria: known cause requires its complete confirming
  observation codes, two reviewed reports from distinct inspections, inspectors AND
  independent source records, no qualifying contradiction, and verified-only B05 path
  for any required topology. Unknown cause can be proposed but never auto-verified.
  Expected observations cannot weaken the rule. Inspection findings are observations,
  not causal facts; review is explicit trusted internal context, not public B13 auth.
  Conflicting support/contradiction -> INCONCLUSIVE; contradiction only -> CONTRADICTED;
  weaker support -> SUPPORTED/POSSIBLE; missing -> INCONCLUSIVE. No model confidence,
  proximity, candidate link/count, similarity or completed order satisfies verification.
- Two durable phases like B08: PREPARED UNVERIFIED Evidence journal then one fenced
  atomic domain batch +COMMITTED receipt +revision/audit. Reuse B03 validation, policies,
  lease/CAS/pending recovery; no blind retries. Every dynamic value parameterized.
  Domain evidence/findings are new versions, never overwritten by this service.
- Writes only canonical or validated B09 UUID targets; retained B01/B04/B05/B07/B08
  protected. Tests copy records created by actual B08 intake into explicit B09 fixtures
  with stable IDs/hashes, preserving source. Read-only city B05 evaluation permitted.
  Later active-graph gate must unify reviewed B08/B09/MCP/checkpoint/API target and
  prove same-chain end-to-end operation; no canonical promotion now.
- Risks/human checks: source independence cannot be proven beyond attributed records;
  reviewed synthetic findings must be authored, never generated by requests. Temporal
  validity/knowledge cutoffs precede scoring; future-updated versions unavailable, not
  reconstructed. Bounded scans fail closed. Test two alternatives/contradictions, actual
  paths, history hashes, candidate rejection, concurrency/native rollback/lost replies.
  ExistingO(E) integrity/O(N) audit costs and10k limit persist; B15 events remain absent.

### DEC-036 — B09 verification refinements and real attempt history | 2026-10-17
- First33 pure model tests PASS0.20s. First real smoke1 FAIL5.44s: fixture reused one
  global actor request ID across proposal/assessment. Corrected fixture keys; guard
  intentionally retains conflicts. First23 integration run22 PASS/1 FAIL127.90s: same
  fixture-key error across repeated rejected/changed state requests; unique retry keys
  fixed without weakening command identity. Preserve both logs.
- Assessments automatically union requested IDs, prior immutable support/contradiction
  references and actual concerned-asset inspection reports.20-reference cap fails closed;
  caller omission cannot erase known contradiction. Temporal filters still apply.
- Journal/report readers verify command hash, receipt graph/ID and actual produced/
  establishes paths, original actor/source/observations/review plus actual finding text/
  status. Assessment tie order uses native recording time, graph revision then stable ID.
  Historical snapshots retain hashes even if privileged low-level mutable data changes.
- Known domain criteria also require registered primary asset subtype. UTILITY_LEAK
  explicitly requires verified physical dependency to affected road; reported AFFECTS
  alone insufficient. New criteria are service policy, not ontology property additions.
- Pydantic Literal[True] spike accepts integer1 despite strict model mode. Add explicit
  before-validator requiring actual bool; tests1/1.0/string rejected. No dependency swap.
- Physical-link demonstration uses authored dated D2_TO_D1_FLOW_TRACED finding, distinct
  from blockage confirmation; no inspection request creates it automatically.

### DEC-037 — B09 final source freeze and verification scope | 2026-10-17
- New typed inspection views distinguish unavailable/pending/actual report/finding IDs,
  with graph/as_of/revision and honest gaps. No registered state or MCP tool added.
- Focused run70 PASS/1 FAIL224.27s; new MCP assertion used report IDs where existing
  contract returns Inspection event IDs. Real records already carried distinct report
  provenance. Corrected test only; target1 PASS9.77s. Final models/three added tests
 40 PASS20.91s. No preceding test removed or runtime behavior changed.
- Source frozen for full581-test run:507 baseline +37 pure unit +37 real DB/MCP cases.
  Fault cases wrap actual statement/lost replies, never fake success. Both SPEC
  validators PASS before full run; final tracking/SPEC/source audit still required.
- Retained operator demonstration has two competing explanations and verified→
  inconclusive immutable revision with omitted contradiction rediscovered. Separate
  explicit source B08 and working B09 fingerprints retained. No canonical promotion.
- Read-only preservation verified43 accepted B07/B07R +27 B08 trace observations,
  original city/B01/B05/migrations and accepted B08 intake. No new package versions:
  Python3.12.1/Pydantic2.14.1/falkordb1.8.0/redis8.1.0/MCP2.3.0/pytest9.1.1/FastAPI0.143.3.
  Registry/0001 hashes unchanged. Actual database health/version evidence follows
  real full regression lifecycle; no live agent/LLM claim.

### DEC-038 — Bind required utility topology to the actual primary pipe | 2026-10-17
Final guard inspection found an input could list WaterPipe P1 but use another concerned
drain as the topology root, while that unrelated drain also affected the road incident.
Existing subtype presence alone did not bind the mechanism to its primary asset.
Strengthen utility criterion: dependencies operation must originate at the concerned
WaterPipe and end at the affected RoadSegment. Record an actual negative graph test
with extra REPORTED impacts and a separate verified drain path. No ontology/data/
B03/B05 change. Stopped initial full run cleanly at76 PASS/162.29s (exit2 interrupt),
retained log/fresh old fixture proofs and restored accepted artifacts. This interrupted
run is not a final PASS. Restart complete582-test regression after focused guard proof.

### DEC-039 — B09 final runtime gate and human boundary | 2026-10-17
- Complete582 PASS/0 FAIL/0 SKIP705.39s:363 pure unit/219 integration;37 new unit+38
  real DB/MCP cases plus all507 baseline. No earlier test removed. Baseline trace-test
  correction recorded separately; interrupted/failed attempts retained. Full source
  freeze14 files unchanged. Both static validators PASS; final rerun after logs below.
- Actual restart and recreation retained graph/Browser volumes (HTTP200). Read-only
  retained B09/source fingerprint comparison PASS:62 nodes/46 edges/revision82/audit82,
  original VERIFIED→INCONCLUSIVE snapshots unchanged; competing capacity SUPPORTED.
  Original B08 five retries retain domain/revision/audit; only owner/epoch advances.
- Post-life source2104 record hashes/city858/1246/revision2104/audit/writer, original
  B01 probe, B05 source/clone, READY0001/0002 and70 accepted B07/B08 trace observations
  PASS.1430 ToolExecutions observed, not agents. Canonical0 domain nodes;91 index
  groups/182 native constraints OPERATIONAL. FalkorDBmodule60002/Redis8.10.2 unchanged.
- Fresh official MCP actual initialization/list/five read calls/five denials/independent
  client equality PASS. Domain initialize/list12/call12/no ERROR +15 persisted server
  trace readbacks PASS after restoring the same ACL credentials, no rerotation.
- Accepted B07R/B08 fixture proof files regenerated by tests; fresh snapshots saved as
  B09-*-regression-proof and accepted HEAD artifacts restored byte-for-byte. Existing
  app/tests/schema/migrations/data/locks/MCP/envelopes untouched after baseline.
- Source/secret/process audit PASS; final inventory/patch and audit finalized below.
  No ZIP/push, canonical promotion, B10 agent/GraphRAG/dispatch/outbox/API/frontend.
  Remaining limitations/gates in EVIDENCE.md/B09-RESULTS.md/blockers.md are binding.
  Proposed B10 only after review: bounded typed LangGraph/approved MCP and controlled
  analytical-service integration, FalkorDBSaver pause/restart/resume, fake/live model
  evidence separated; explicit active-graph/read-adapter review. STOP.

### DEC-040 — B09-R authority, meaning and occurrence semantics before coding | 2026-10-18
- Scope: B09-R only, R01/R03/R04/R05/R08/R09/R11/R15/R17; preserve all18. Local accepted B09 baseline `688b893`, no push;582/582 regression passed in724.05s, both specification validators and retained B01–B09 readback passed.
- Reproduced on real isolated graphs: unreviewed falsifier -> CONTRADICTED/REJECTED; AGENT context -> POSSIBLE/SUPPORTED_BY; post-end inspection -> SUPPORTED. See B09R-before-results.json.
- Decision: rule-v2 assessment snapshots explicitly classify every use as reviewed/unreviewed support/contradiction, context or excluded. Only reviewed discriminating evidence creates causal edges; mixed positive/negative claims are INCONCLUSIVE. Preserve all five labels and hypothesis state machine.
- Occurrence relevance: actual EXPLAINS/CONCERNS plus INSPECTS request journal -> investigation/incident, asset subtype, observation/recording visibility and individual [start,end) interval. No earliest-start shortcut. Per-incident confirming-code and independent-source coverage required for VERIFIED. Ambiguous attribution remains qualified.
- Optional typed attribution in existing report/journal JSON: named occurrences, reason, mode and prior reviewed direct evidence basis for retrospective claims. No new ontology property, relationship, state or migration. Disjoint source lineage prevents derivative corroboration.
- Compatibility: v1 assessments/reports/journals/receipts retain original shape and historical meaning; omitted new defaults never enter old hashes. Newly authored assessment/rule version2, explicit-attribution report version2. Alternatives (rewrite v1 records, new graph edge, chronology-only matching) rejected.
- Files to touch: evidence models/policies/reader/service; focused classification/relevance modules; evidence contract; new tests/fixtures; EVIDENCE.md; six trackers and B09R evidence. Repository/writer/B08/B05/MCP/registry/migrations/dependencies unchanged.
- Risks: immutable-v1 decoding/hash compatibility, over-attribution across recurrence, false independence, reader budgets, shared active-graph gap. Fail closed and preserve retained source records; application rollback uses baseline source, never rewrites new/old assessments.
- Tests: focused unit + real persisted decisions/edges/status; January repair/August recurrence; retrospective/as_of; legacy replay/append; existing full regression including actual restart/recreation and both spec validators; retained fingerprint/trace/secret/source audit.
- Human verifies categorized source lists against persisted edges/status, v1/v2 history and provenance, conservative bounded topology, unchanged municipal data and explicit B10 active-graph gate. No B10 implementation.

### DEC-041 — B09-R final compatibility and runtime evidence | 2026-10-18
- Rule-v2 corrections PASS;617 tests (382 unit/235 integration) in746.62s,0 failures/skips; both specification validators PASS.582 original tests preserved,19 unit/16 real integration added.
- Runtime unchanged: Python3.12.1, Pydantic2.14.1, FalkorDB client1.8.0, Redis client8.1.0, MCP2.3.0, pytest9.1.1, FastAPI0.143.3; FalkorDB60002/6.0.2 on Redis8.10.2. No pins/locks/migrations/registry changes. Canonical91 index groups/182 constraints operational, domain nodes0.
- Real chronology initially13 PASS/1 FAIL exposed an unnecessary future mutable-cluster read while selecting identities; fixed by exact immutable opening-journal/INVESTIGATES binding. No relaxation of incident/source as_of visibility. New-test basename collection collision corrected by renaming only the new unit module.
- Read-only verification harness fixes: preserve replay metadata during equality checks; select actual trace result lists instead of JSON-schema property dictionaries. Actual accepted trace records were never missing or rewritten;31 B09 observations and70 prior observations rechecked. All attempt details retained.
- Old v1 assessment/journal hashes and original accepted B09 graph unchanged; new correction appends v2 and legitimate state transitions. New39-node/28-edge/revision58 legacy compatibility graph exact fingerprint and history survive lifecycle; original city858/1246/revision2104 and42 candidate drainage links unchanged.
- Human B09-R review next. Active-graph policy/configuration remains a B10 prerequisite before live investigator acceptance; explicit source promotion or shared disposable policy needs review. B09-R does not claim a full one-graph agent chain. B10 not started. Evidence: B09R-RESULTS/COMMANDS/COMPATIBILITY/ACTIVE-GRAPH, test summary, raw logs, source audit and patch.
