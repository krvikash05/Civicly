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
