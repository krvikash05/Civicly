> **CURRENT B17 — TECHNICALLY PASS, HUMAN REVIEW PENDING.** B16/B16-R human accepted. All8 B17 routes exercised;52operations/49paths. Final focused45unit PASS +1real HTTP/FalkorDB/MCP/Saver/TCP-SSE PASS; both specification validators PASS; no live provider. Earlier failed attempts retained and corrected. All18requirements remain binding; B10 genuine acceptance OPEN/PARTIAL. No B18/B19/frontend/live authorization. Current entry supersedes historical status headings; see docs/evidence/B17-RESULTS.md.

# decision.md — Append-only engineering decision log

> **CURRENT B14-R — TECHNICALLY PASS, HUMAN REVIEW PENDING.** Corrected waste B14-2 anchors24hours to latest actual pickup; B14-1 outcomes/implementation preserved. Recurrence includes original investigation/new incident sourced link and validated explicit same-thread active-episode refresh; old checkpoints retained, actual MCP/Saver reads exercised.14distinctPASS(11unit/3real),0unresolvedFAIL/0SKIP; both SPEC validatorsPASS once;5pytest/child guards0provider. B10 full genuine acceptance OPEN/PARTIAL. All18requirements binding; no B15/live/full-suite/lifecycle. This summary supersedes historical headers; docs/evidence/B14R-RESULTS.md.


> **CURRENT B14 — TECHNICALLY PASS, HUMAN REVIEW PENDING.** B13 accepted.41distinct focusedPASS(30unit/11real),0unresolvedFAIL/0SKIP; both final SPEC validatorsPASS. Authenticated simulated execution, actual B09 evidence/assessment history, independent3issue follow-up, failure/recurrence and existing memory verified.12pytest/child interlocks0external Gemini/countTokens; B10 full genuine acceptance OPEN/PARTIAL. Earlier data/migrations/history/quarantines preserved. No B15delivery/worker/API/frontend/live or full-backend completion. All18requirements binding. This current summary supersedes historical headers; docs/evidence/B14-RESULTS.md.


> **CURRENT B12 — PASS, HUMAN REVIEW PENDING.** Typed persistent DRAFT plans/PROPOSED tasks, verified responsibility + B11 citations, bounded DAG/version/hash/monitoring criteria and compatible planner/Saver path exercised.49distinct focused casesPASS(42unit/7real),0finalFAIL/0SKIP; both finalSPECvalidatorsPASS;0externalGemini/countTokens. Additive0004 tested isolated;0001–0003/retained city/checkpoints/evidence preserved. No approval/WorkOrder/monitoringexecution/API/frontend. B10 full live acceptance OPEN/PARTIAL. B13 not authorized; see docs/evidence/B12-RESULTS.md.


> **CURRENT B11-LIVE-SMOKE-R — PASS, HUMAN REVIEW PENDING.** Successor B11-1/actual-clock preflight corrected; genuine Gemini selected organizational READ,1count/1generation/1READ,5valid version1citations incl PDF. Fresh-process checkpoint/decision/server+broker traces/accounting PASS. Known$0.00571350/held$0 under existing$0.15casecap;16focused checksPASS(15unit/1real), both validatorsPASS once. Original failed case/quarantine/zero-call thread preserved. No further calls/B12. B10 full live acceptance remains OPEN/PARTIAL.


> **CURRENT B11-LIVE-SMOKE — BLOCKED before provider execution.** One attempted wake stopped on future-dated harness fixture/monotonic update precondition;0 count/0 generation calls,$0known/$0held, no checkpoint or model-selected trace.6 offline harness tests PASS; actual MCP/cited-memory preflight PASS, temporal preflight defect identified. Quarantine retained; no retry/resume/B12. B10 genuine acceptance remains OPEN/PARTIAL. See docs/evidence/B11-LIVE-SMOKE-RESULTS.md.


> **CURRENT B11-R STATUS — TECHNICALLY PASS, HUMAN REVIEW PENDING.** Three memory defects corrected;7 distinct real integration cases passing,0 final failures/0 skips; both SPEC validators PASS once, zero external Gemini/countTokens. Prior B11 evidence preserved. No full770/313 rerun or container lifecycle operation. B10 genuine Gemini acceptance remains OPEN/PARTIAL. No B12. This summary supersedes historical statuses; see docs/evidence/B11R-RESULTS.md.


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


## DEC-042 — B10 pre-implementation scope and runtime choices (2026-10-18)
B09-R accepted; clean local baseline `2d30550` (617 real regression tests PASS, both validators PASS). No remote push. Baseline tests regenerated the rolling B09R proof; dated matrix, episode, v1/v2 receipt and lifecycle artifacts remain unchanged. Fresh baseline retained checks anchor current writer lease state; immutable content/audit and v1 history hashes match.

B10 objectives: R01–R09, persistent investigation foundation R13, R15/R18; all 18 remain binding. Files planned: trusted active profile and three narrow B08/B09 target guards; B06/B07 trusted graph injection and compatible source/rationale envelopes; new agents modules, contracts, dependency pins, tests, guide and six trackers. Registry v3 and migrations 0001/0002 remain immutable. No B11+, city import, hidden evaluation input, operations or frontend.

Exactly one private B10 UUID profile is authorized in a trusted context; graph-name syntax alone grants no shared phase access. Separate read-only source ACL and checkpoint ACL. Existing city brokers retain defaults. Compatible envelope widening allows historical B10 source references and optional actual model summaries; old null rationale defaults remain. No ontology additions.

Public FalkorDBSaver from langchain-falkordb[langgraph] 0.2.0 + LangGraph 1.2.16 passed actual pause/fresh-process resume with existing Pydantic 2.14.1, Redis 8.1.0, FalkorDB client 1.8.0 on Python 3.12.1. Saver owns its separate graph/internal indexes. Its multi-query writes require fail-closed recovery, not schema edits or blind replay.

Gemini credentials are present privately. Actual generateContent structured JSON smoke passed on gemini-3.8-flash. Earlier old responseSchema attempt returned 400; responseJsonSchema plus gemini-2.5-flash returned 404. Those failures and successful replacement smoke are recorded separately; none is integrated agent proof. HTTPX 0.28.1 is reused with finite timeout and total token usage (including provider thought tokens). No OpenAI credential/live OpenAI claim.

Named StateGraph roles, typed versioned state and strict model selections; real discovered broker catalogs, no scenario/tool table. B09 remains sole assessment authority. Planner only nonbinding recommendations, Coordinator dependency pauses. Bounded repair/tool/iteration/token/time budgets; public short summaries only, no chain-of-thought. Checkpoint version/binding checks, per-thread exclusion and uncertain-write quarantine.

Acceptance commands: `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence`; `make test-spec`; focused B10 real MCP/checkpoint/provider tests and process/container restart probes; retained source/hash/trace checks. Human review: exact same graph IDs/revisions across B08/B09/MCP, ACL denial, model-selected calls, paused thread survival, no duplicated writes, candidate/verified and episode/authority protections. Mandatory gates remain incomplete until actual evidence exists.

Sources: https://docs.falkordb.com/genai-tools/langgraph ; https://pypi.org/project/langchain-falkordb/ ; https://docs.langchain.com/oss/python/langgraph/persistence ; https://docs.langchain.com/oss/python/langgraph/interrupts ; https://ai.google.dev/gemini-api/docs/structured-output .


### DEC-042 implementation verification notes
- Baseline local commit `2d30550` includes accepted B09-R only. Fresh baseline regression rewrote the untracked rolling B09R-runtime-proof; its dated matrix/episode/v1/v2/history artifacts are unchanged. Three earlier tracked rolling proofs were restored byte-for-byte after preserving new output under B10 evidence. This is artifact regeneration, not an assessment-history rewrite.
- Shared target implementation uses a private profile + ContextVar exact match. Only three B08/B09 guard exceptions changed; generic B03 migration/repository target policy, schema registry v3, 0001 and 0002 are untouched. Source read and SDK checkpoint accounts have separate exact-key ACLs. No full city activation/import.
- B06 Request validates an internally injected graph with explicit Pydantic context; caller graph mismatch still denied. Production domain server verifies exact source context. Existing test-only phase-substitution servers remain labeled test harnesses; B10 evidence uses actual production bootstrap and correct source identities.
- B07 optional `rationale_summary` now accepts bounded actual public summaries; historical null defaults and existing caller/origin enums remain. Context source references accept retained city or UUID4 B10 syntax for history decoding, while trusted source equality remains mandatory. Compatible envelope schema version 3 retained; tool inventory hashes naturally change. No invented agent rationale on server observations. B06 context manager now preserves consumer application exceptions rather than mislabeling them transport failures.
- StateGraph uses five named logical roles plus one interrupt helper. The planner emits a nonbinding recommendation only; B12–15 Plan/approval/task/work-order behavior remains excluded. The canonical free-text inspection_type uses authored test values (blockage inspection versus capacity test); no ontology property or enum was added.
- AgentDecision and B10_OPERATION Evidence journals use existing canonical properties. Source graph decisions reference actual execution IDs, provider mode, token usage, prompt version/SHA, inventory hash and graph revision. Large tool summaries are capped at 18KB and explicitly marked limited; full validated output hashes remain in B07 traces. B09 retains all assessment authority, source classification and incident-episode enforcement.
- FalkorDBSaver public API uses a separate graph and strict serializer, no internal schema edits. Multi-query SDK writes are not atomic; uncertain wakes quarantine the thread. The SDK lacks a public socket timeout constructor option: finite orchestration budgets do not constitute proof that vendor socket I/O can always be cancelled. Recovery requires stopping the old process and reconciling public checkpoints/journals, never dropping retained data. This limitation is explicit.
- Verified dependency pins: langgraph 1.2.16, langchain-falkordb[langgraph] 0.2.0, langgraph-checkpoint 4.3.0, langchain-core 1.6.12, existing falkordb 1.8.0/redis 8.1.0/Pydantic 2.14.1/Python 3.12.1; HTTPX 0.28.1 reused. Project lock is updated; no provider SDK required.
- Gemini 3.8-flash structured API works with responseJsonSchema. Initial 2048 output cap exhausted structured output under default model thinking; 4096 plus documented thinkingLevel LOW improved generation. Actual provider failures are preserved (503 then 429); no retry storm, alternate prerecorded output or fake-model substitution. Only Gemini adapter implemented.
- B10 cannot be marked complete: live water created two competing hypotheses and real MCP traces; road requested inspection; waste/perturbation runs remain incomplete. A real topology-positive attempt also had an analytical command rejected, then provider quota stopped the comparison. Deterministic negative controls and full old regressions do not resolve these live gates. Proposed next work remains B10 acceptance/recovery after review/provider availability, then separately authorized B11.


### DEC-042 live invalid-command correction (prompt B10-2)
The positive live utility attempt supplied an invented topology object (`asset_ids/relationship/verified`) instead of canonical B09 `source_id/target_id/operation/max_hops`; strict B09 validation rejected it without creating a hypothesis. Root cause: the model saw policy criteria and a prose action list, but not the full nested analytical input schemas. B10-2 now includes the actual B09 Propose/Assess/RequestInspection JSON schemas, with only host-controlled IDs/CAS/time fields removed. Topology schema is reused, not redefined or weakened. B10-1 text and actual failed selection are retained. This correction receives deterministic schema/real-runtime verification; provider quota prevents claiming live B10-2 success. The complete existing regression was already running; after it finishes, rerun all affected B10 tests on B10-2 and record both results explicitly.

### DEC-042 final trace observation guard
Official B10 broker calls now persist a shared host observation for both success and failure, with actual measured latency and error code, alongside unchanged B06 transport traces. No output hash/revision is claimed on a failed call. A mocked broker timeout unit verifies this envelope path separately from the actual stalled-domain MCP timeout integration. Re-run all B10 tests after this final guard; do not use earlier intermediate counts as final-source evidence.

### DEC-042 lease guard at asynchronous boundaries
The runtime rechecks wake ownership after model/tool waits and immediately before decision/journal/domain writes. A quarantine written by an uncertain previous owner is checked at each boundary as well as wake entry. B03 fencing/CAS and B09 native request IDs remain unchanged. Final B10 integration tests exercise this final source; no claim of arbitrary vendor-I/O crash recovery is added.

### DEC-042 trusted knowledge cutoff
The B10 host supplies missing domain as_of values from its trusted case clock and denies model-selected future cutoffs. Official B06 node templates intentionally expose current raw facts, so B10 reuses B05 Reader.visible to reject out-of-cutoff properties before model context/checkpoint observations. Raw successful official read traces remain accurate; the agent records OUTPUT_OUTSIDE_CUTOFF rather than presenting the rejected fact. Two real integration negatives cover a selected future cutoff and a current raw fact recorded after the investigation cutoff. No B03/B05/B06 temporal policy is changed.


## B10 final verification record (2026-10-18)
- Full regression: **655 PASS / 0 FAIL / 0 SKIP**, 824.63s, including all accepted 617 cases, actual official/domain MCP and container restart/recreation.
- Final B10 source: **42 PASS / 0 FAIL / 0 SKIP**, 126.05s: 23 unit (including mocked HTTP/broker errors, not live) and 19 actual FalkorDB/MCP/Saver integration cases (18 explicitly deterministic fake-model cases; one direct shared-graph boundary probe). Four new cases added after the full suite collected; unique cases covered across both runs: 659, not one 659-test invocation.
- Both specification validators PASS; separate static evidence. Exact commands/raw logs in B10-COMMANDS.md and B10-regression-tests.txt/B10-final-runtime-tests.txt.
- B10 pre/post-recreation source fingerprint: revision103, 80 nodes/47 relationships, immutable content/audit and writer state exactly matched. Six public SDK checkpoint threads and 12 referenced actual executions retained; B07 storage remains separate. Browser HTTP/volume and B01 retained probe PASS.
- Accepted B01/B04/B05/B08/B09 source checks PASS; 101 earlier B07/B08/B09 trace observations verified. Original B09-R v1 node/journal hashes and exact two-version history preserved. Native receipt replay changed only writer lease metadata, explicitly distinguished from immutable content/audit. Four rolling proofs restored after their fresh output was saved under B10-regression-*.
- Registry3, 0001 and 0002 remain byte-identical; source/security audit and exact changed inventory/patch are in docs/evidence/B10-*. No ZIP or push.
- Live acceptance remains PARTIAL: actual provider 503/429, incomplete full three-issue competing-cause/contradiction/perturbation proof, B10-2 live correction unverified. Deterministic controls do not close those gates.
- Stop for review. Exact next task remains B10 acceptance/recovery; B11 cited GraphRAG/multi-layer memory is proposed only after separate approval.


## DEC-043 — B10-O pre-code plan (2026-10-18)
Scope: optimize B10 only, preserve all18 requirements and actual graph/MCP/Saver architecture. B10 remains PARTIAL; no live Gemini request is authorized during this task. Baseline source/evidence frozen in B10O-baseline.json with private recovery copies; no baseline evidence overwritten. Hotfix reviewed as proposed code, not instructions or assumed installed. Its retry bounds are useful but undifferentiated429 and unreserved retries are rejected.

Files: agents provider/runtime/mcp + new execution-policy, compact-context, spend-ledger and read-cache helpers; prompt B10-3; explicit CLI/live harness opt-in; versioned pricing config and optimization contract; tests, runtime guide and all6 tracking files/evidence. No ontology or migrations. Objectives R01/R04–R09/R13/R15/R18 foundation, no capability removed and B11 not started.

Durable spending is auxiliary local SQLite (stdlib, WAL, synchronous FULL, BEGIN IMMEDIATE), private .runtime/ai-spend.sqlite3 shared across local processes and independent of database container restart. Alternative Redis/graph multi-write accounting adds unnecessary graph schema and atomicity risk. FalkorDB remains primary domain/evidence/checkpoint storage; SQLite stores only spending/concurrency metadata, not municipal knowledge. Default managed allocation $6, per-investigation $0.15, one live investigation; explicit trusted operator configuration permits a higher per-case cap, never model input. Unknown provider billing retains reservation; no automatic paid fallback. Prior B10 billing is unknown, not retroactively priced as zero; ledger controls new managed usage, not Google account billing.

Live policy requires an explicit invocation-bound permit plus normal tests block external Gemini HTTP/socket access, including inherited child-process guard. Mock HTTP permits require actual MockTransport. Compact context preserves latest authoritative assessments, material historical contradictions/classifications/provenance/paths/limits and source references; full records remain in FalkorDB. No silent cap on critical information; fail closed if it exceeds budget. All16 approved tool capabilities remain discoverable with exact schema references. Read cache only for identical source revision/as_of/arguments/permission scope, preserves bounded-negative flags and original execution references, no fabricated tool calls. Native provider caching disabled until measured support/benefit exists.

Official Google pricing checked https://ai.google.dev/gemini-api/docs/pricing : gemini-3.8-flash Standard text $0.75/M input and $3.75/M output including thinking through2026-12-31; cached input $0.075/M. Schedule is versioned, expires, and explicitly restricts model/tier/text; no unverified model switch. Retry classification uses structured quota details/RetryInfo, no raw errors/secrets in evidence.

Acceptance: entire ordinary pytest suite with external-provider interception/counts and real --run-persistence; both specification validators; actual multi-process atomic ledger reservations/restart durability, caps/uncertain billing, source/revision cache invalidation, context-size and decision-critical preservation checks, all3 difficult issue cases and existing contradiction/topology controls. Simulated costs labeled estimates. Human reviews zero external requests, schema completeness, preserved negatives and refs, exact budgeting/recovery evidence, unchanged protected files. Live B10 gates stay OPEN, live test NOT RUN.


### DEC-043 implementation details and limits
Pricing is operator-configurable/versioned and expires; default Standard text rates have separate input/output/thinking/cached categories. Every retry/JSON repair reserves separately; missing usage and network uncertainty are held. Conservative UTF8 input bytes plus framing and twice the output ceiling estimate is an upper planning allocation, not measured tokenizer output or a provider charge. Actual cost above reservation records the actual value and places a durable hold. Defaults remain project$6, case$.15, concurrency1; recorded warnings50/80/95/100 percent. Limit changes require trusted operator reason, no live sessions, audit history and preserved prior charges. Historical B10/provider billing is unknown; no claim that the ledger reflects Google's available credit.

B10-3 is a new prompt; B10-1/B10-2 remain unchanged as historical evidence. All16 tool names and exact schemas remain present, with shared schemas/source facts interned by full-content hash. No provider-native context cache spike was justified: local deduplication is measured without spending and supports exact provenance. Cache hits reference existing validated MCP execution, with revision/time/scope/parameter checks; own graph audit writes invalidate too, so no claim of universal cache hit rates.

The ordinary-suite HTTP guard adds no production monkeypatch. Explicit mock permits require httpx.MockTransport, and real live permits are rejected under the test sentinel; transport/DNS interception additionally blocks accidental provider requests and propagates into Python subprocesses. Existing provider tests needed an explicit mock permit/private simulated ledger but their assertions are preserved. Other previous tests/assertions remain byte-identical apart from global conftest interception. Legacy live batch drivers are disabled in favor of per-case CLI opt-in, preserving original source/proof and real runtime capability. No source data/migration/registry change.

SQLite is built into Python3.12.1; existing dependency pins and uv.lock remain unchanged. Runtime still uses actual LangGraph1.2.16, langchain-falkordb0.2.0/FalkorDBSaver, MCP2.3.0 and official Node MCP1.3.0, FalkorDB6.0.2. Mock and real runtime tests are separately classified. Human review must not treat zero paid calls as live B10 reasoning acceptance; those gates remain OPEN.

Final B10-O recovery checks additionally enforce the remaining token allowance before each transient retry, preserve model/prompt/pricing/accounting metadata on the overall async deadline, and test explicit project quota plus exhausted invalid-JSON repair. Complete final-source regression is required after the generic domain-history record interning refinement. Initial687-test run and final691-test run are distinct, overlapping evidence, never summed.

B10-O observed rerun prerequisite: actual force-recreation clears dynamic ACL users although AOF graph/Browser data persists. An automatically queued full rerun omitted the existing B07 trace-account configure step:24 auth failures/1 Browser pass, interrupted72.93s. Preserve failure evidence; no application/test expectation change. Existing verify_b10 --reprovision restored trusted trace + exact-key profile ACLs and confirmed retained source/all6 SDK threads exactly match before lifecycle. Runtime guide now places configure before pytest. This does not rotate/expose secrets or mutate domain records; final full rerun is required.


## B10-O final observed verification — 2026-10-18

- Final **691 PASS/0 FAIL/0 SKIP**,951.17s:432 unit/259 actual integration. All659 previous unique cases retained (including accepted617 B01–B09-R),32 new cases. First full687 PASS,940.94s; overlapping runs are not added. Both specification validators PASS; uv lock --check --offline PASS,74 unchanged packages. Python3.12.1,SQLite3.43.1; no new external dependency.
- Entire ordinary-suite interlock:0 external Gemini requests,2 intentional HTTP parent/child probes blocked before network,0 ordinary unexpected attempts. Real model/live acceptance **NOT RUN** (not authorized). Mock provider errors and deterministic/reactive model routing are distinct from actual graph/MCP/Saver calls.
- Real actual-schema/context benchmark:8 persisted B09 assessment versions,4 source read observations and all16 discovered tools per issue.

| Issue | Before JSON bytes | After JSON bytes | Reduction |
|---|---:|---:|---:|
| WATERLOGGING | 62913 | 56921 | 9.52% |
| ROAD_DAMAGE | 63308 | 57121 | 9.77% |
| WASTE_ACCUMULATION | 63762 | 57512 | 9.80% |

Small actual two-assessment cases changed by+28/+10/-2 bytes; no universal reduction claim. Authored large duplicate-schema/source fixtures reduce74.8%, separately labeled and not treated as production savings. Simulated allocations use versioned pricing/context bytes only, not tokenizer/billed usage. Native paid caching remains disabled.

- Exact source/audit fingerprints, all6 retained B10 SDK threads/12 executions, original B01/B04/B05/B08/B09 sources and immutable B09R v1/v2 history preserved.101 prior trace observations verified (43+27+31). Registry3/migrations0001/0002 unchanged. Actual container restart/recreation and Browser persistence PASS. Simulated financial ledger matches exact before/after state, including unknown reservation; no reset or retained-volume deletion.
- Preserved genuine failed attempt: after first recreation dynamic shared MCP trace-writer ACL was unavailable.24 authentication failures/1 Browser pass, interrupted72.93s; unexecuted remainder is NOT RUN for that attempt. Existing trusted configure/exact-key provisioning restored authorization without changing domain records. All6 retained threads/source matched before lifecycle; final full691 run then passed. Runtime guide now states configure before pytest. Raw failure/counters retained in B10O-auth-failed-*; no test weakened or removed.
- Four rolling proofs saved as B10O-regression-* before exact pre-task copies were restored. Previous B10 evidence remains byte-identical. B10O-FILES.md/source-audit.json and incremental B10O-changes.patch identify exact changes against frozen B10O-baseline.json, not a misleading HEAD-only diff.
- **STOP for human review.** B10-O verified; B10 remains PARTIAL pending separately authorized genuine three-issue/contradiction/topology/B10-3 acceptance. B11 cited GraphRAG/memory is proposed only after the B10 gate and explicit authorization, not implemented. All18 objectives remain binding.


## DEC-044 — B10-O-R pre-code plan
Reviewed baseline c16346a: B10-O691 PASS/0 FAIL/0 SKIP and zero external Gemini requests confirmed in recorded logs/counters. Clean local commit created after secret/source audit; ignored credentials/runtime/env/caches excluded, no push. Scope only token accounting, budget configuration/recovery, compatible runtime resume and controlled tests. R01/R04–R09/R13/R15/R18 remain binding with all18 objectives; no B11 or live request authorized.

Files: provider/token helper, spending/policy/CLI, runtime/models for additive token exposure and explicit budget resume, relevant configuration/contracts, tests, runtime guide and six trackers/evidence. Risks: unsupported exact3.8 local tokenizer, counted vs billed tokens, unknown retry consumption, old ledger migration and duplicate actions after resume. Use Stage1 focused units, Stage2 real MCP/B09/LangGraph/Saver with simulated Gemini HTTP, Stage3 one stable full regression with both validators and real lifecycle. Review exact boundary cases, old ledger immutability, per-request hold audit, all16 tool schemas/source evidence, zero external requests and retained fingerprints.

Official countTokens accepts full generateContentRequest including steering: https://ai.google.dev/api/tokens . Official local loader https://github.com/googleapis/python-genai/blob/main/google/genai/_local_tokenizer_loader.py does NOT map gemini-3.8-flash. Therefore local SentencePiece/Gemma3 counts are explicitly proxy ESTIMATES (not verified3.8 tokens), with a stated planning margin and complete prompt/schema text. Pinned public vocabulary/hash from Google's loader; no runtime auto-download. Authorized LIVE mode additionally requires separately accounted countTokens before generation; no counting endpoint called in ordinary tests. Count calls use the same exact-case permit and conservative dollar reservation; unknown counting billing is held, not declared free. Mock mode uses offline local counts unless explicitly exercising mocked countTokens. No claim of exact live tokenizer compatibility without later authorized evidence.

New ledger defaults8/.50/concurrency1 with configurable explicitly authorized case ceiling1.50; existing configurations/charges/reservations remain untouched. Add per-request token exposure and request-linked holds/reconciliation audit through additive private SQLite schema migration, never graph migration changes. Holds can be resolved only for exact settled requests after usage/pricing verification and cap checks with stopped sessions/operator reason; unknowns remain held. No blanket reset.

DEC-044 implementation choices: retain default60000-token Budget and B10-3 prompt,
use pinned SentencePiece0.2.1 with Google's published Gemma3 vocabulary as an
explicitly uncertain Gemini3.8 proxy (local SDK mappings do not establish3.8
compatibility), rather than reuse byte length or claim a guessed exact mapping.
Proxy input plan=ceil(tokens×1.25)+256 plus4096 output. LIVE mode requires a separately
permitted/accounted full-request countTokens check; ordinary tests never call it.
A count result is not billed usage, so its conservative dollar reservation remains
held pending verified reconciliation. Actual generation usage replaces only its
own token allowance; unknown attempts retain their own allowances. Integer dollar
reservations and cumulative token exposure are distinct ledgers/units. Legacy
checkpoint floors prevent resets. Compatible auxiliary SQLite tables only; no
FalkorDB schema, migration, causal or temporal policy changes.

New defaults8/.50/concurrency1/complex ceiling1.50 apply only to new accounting.
Existing caps/history stay intact; explicit config changes and single-request
settled-overage recovery are audited with immutable rows. No blanket clear exists.
Recovery requires exact usage hash/tariff/repriced charge/evidence/operator/reason
and cap checks; unknown billing fails closed. Authorized monotonic operational
Budget increases resume the same checkpoint and retain counters and source refresh.
Bad operator input is rejected before ownership instead of quarantining a valid
thread. No runtime budget default or global recursion limit increased.

DEC-044 compatible overrun representation: a valid reported usage total up to1M
plus a prior configured-budget baseline could exceed the previous1M checkpoint
counter validation ceiling. Increase only `InvestigationState.tokens` storage
ceiling to2M so an unexpectedly large receipt can be recorded exactly and paused
without failing checkpoint validation. Operational Budget.max_tokens remains at
most150000 (default60000); this adds no spending or inference allowance. Provider
usage fields above1M are invalid/unknown and retain reserved exposure. A real
Saver integration test simulates a1M-token receipt plus100000 prior tokens and
verifies an exact1100000 counter, no action or further HTTP, and durable pause.


## B10-O-R final observed verification | 2026-10-18

- Local reviewed baseline c16346a; no push. Final **740 PASS/0 FAIL/0 SKIP** in1249.98s:466 unit/274 actual FalkorDB/MCP integration; all691 original cases unchanged plus34 unit/15 integration. Actual Gemini outputs/counts/costs **NOT RUN**; HTTP responses and returned usage are simulated. Both specification validators PASS; frozen offline lock75 packages, only SentencePiece0.2.1 added.
- Whole-suite external-request interlock:0 Gemini requests,2 intentional parent/child probes blocked,0 ordinary unexpected attempts. All new tests and original real official/domain MCP, B09 authority/episode rules, LangGraph/Saver and actual Docker restart/recreation/Browser checks passed. Targeted overlapping batches58/76/10/29 passed; do not sum overlapping totals. Initial unit1-failure and authored integration-fixture failures are preserved in B10OR-COMMANDS.md/raw logs.
- Bytes/token minimal reproduction: old byte+output guard127331 vs corrected proxy allowance30394 tokens under60000. Three real complex contexts preserve8 assessment versions/4 observations/2 alternatives/all16 schemas: complete request bytes66234/73621/81990; proxy input+output allowances37476/41089/46721. Exact/-1/+1 cases reject/pass/pass. These estimates and mock130-token receipts are not genuine Gemini usage or billed savings. Model mapping/framing uncertainty is explicit; LIVE requires separately authorized/accounted counting.
- New-ledger8/.50/concurrency1/explicit complex ceiling1.50; existing6/.15 history and reservations unchanged. Explicit audited upgrade demonstrated on a private SQLite backup, not the original. Exact-request hold recovery binds known usage/tariff/hash/evidence/operator/reason and caps, retains immutable audit, and cannot clear unknown billing. Reopen/fresh-process/lifecycle witness retains5120 token exposure. Same-thread authorized Budget increases preserve counters/source refresh; operational defaults unchanged. Only checkpoint counter storage widens to2M to retain an unexpected1100000-token simulated overrun exactly and pause.
- Retained B10 source revision103/80nodes/47edges/content/audit/writer state and all6 public SDK threads/12 executions match accepted evidence. B01 probe, B04 city858/1246 revision2104, B05/B08/B09 sources and B09R original v1/v2 history preserved;101 accepted trace observations checked43+27+31. Registryv3/0001/0002 and all prior evidence unchanged. Four fresh rolling proofs saved as B10OR-regression-* before restoring accepted bytes. No graph/volume deletion to pass tests.
- Supplemental legacy verifier rejected only pytest's ',2 warnings' summary formatting after real data assertions. New B10OR evidence adapter validates the untouched raw740-pass log, lifecycle markers and successful guard, then runs every unchanged original B09 graph/history assertion. PASS; no old tests or logs normalized. This genuine compatibility adjustment/failure is recorded in B10OR-retention-parser-compatibility.json.
- Current source inventory, actual patch, dependency/retention/financial/zero-request proofs and commands live under docs/evidence/B10OR-*. Final source/security audit checks exact accepted files, actual private values without printing them, secret patterns and leaked MCP children. Human review required; no ZIP or later milestone.

DEC-044 final acceptance basis:740 complete cases, not an aggregate of focused runs. The only post-suite compatibility addition is standalone evidence parsing for pytest warning fields; application logic and all prior tests remain unchanged after final source freeze. The old verifier's graph/history assertions are reused intact. No fabricated normalized success log or live-model closure. Baseline and exact source audit/patch are c16346a-relative. STOP for human review.

Final B10-O-R scope/security audit PASS:61 prior test files unchanged, all prior evidence byte-identical, actual private credential values/patterns absent, no leaked MCP children. No push or ZIP. Exact source inventory/patch is against c16346a; subsequent human review and separately authorized B10 live acceptance remain required.

## DEC-045 — B10-O-R2 pre-code scope and verification plan (2026-10-18)

Accepted B10-O-R baseline af42149 is a clean local commit, audited against the
740-pass/zero-external-call record; no push. This corrective pass supports
R01/R04–R09/R13/R15/R18; all18 requirements remain binding. No B11 or ZIP/live API.

Touch only provider/token/model/runtime/CLI/spending budget interfaces as needed,
versioned provider policy, affected tests, two agent contracts, README/runtime guide,
six trackers and R2 evidence tooling. Preserve graph services, migrations, city data,
source histories, original ledger rows/audits and all earlier evidence. Existing
assertions of count-uncertainty and obsolete numeric token ceilings require explicit
compatible adjustment, not removal of tests.

Google's current billing FAQ plus Firebase Count Tokens guide establish nonbilling
for this exact Google countTokens endpoint/model; generation remains billed. Record
endpoint-specific outcome/count/policy evidence and immutable settlement, zeroing
only new known-nonbillable count reservations. Unknown/expired billing policy remains
conservative; do not retroactively rewrite historical unknown rows. Count calls still
require live opt-in. No arbitrary endpoint-free assumption.

Separate published request capacity (1048576input/65536output for Gemini3.8 Flash),
configured output allowance, proxy/provider count, cumulative tokens and independent
integer dollar caps. Size new cumulative defaults using eight largest accepted real
B10-O-R complete-request plans, rounded upward to50000; complex profile twice that
allowance, finite configurable maximum. Preserve existing checkpoint Budget values;
explicit authorized increases retain counters and same thread. Dollar8/.50/1.50,
iteration/tool/time/wake defaults remain unchanged.

Risks: counting billing vs completion certainty; overrun storage; price/token
unit conflation; checkpoint decoding legacy defaults; source refresh and duplicate
actions after pause. Tests: Stage1 only affected provider/token/spending/model unit
cases, then exact failed case reruns; Stage2 real MCP/B09/LangGraph/Saver with >=3
consecutive realistic receipts per category, topology/evidence revisions, retries,
repair, money/token pauses and fresh-process resume. Stable final full pytest
--run-persistence --durations=25 exactly once, both SPEC validators, retained
fingerprints/accounting/secret and zero-provider checks. Human review: verify
endpoint-specific zero settlement and unchanged legacy accounting, benchmark-based
new defaults, real calls/checkpoints, pause/resume counters and separate live gates.


DEC-045 verification refinement: first full attempt deliberately interrupted after148PASS/688.36s when review identified an old count-only outer-deadline summary incorrectly inferring retained reservation/uncertain generation from any HTTP call. Ledger zero settlement was already correct. Derive summary from exact count-policy settlements/generation holds; count-only status NOT_GENERATED. Add two cancellation cases (known/unknown policy), retain all original generation-timeout tests; focused14PASS4.57s. Recheck actual MCP/Saver and specs, then restart final acceptance. Preserve interrupted raw log/exit2 guard separately; no completed regression discarded for harness comparison.


## B10-O-R2 final corrective verification | 2026-10-18

- **CURRENT B10-O-R2 STATUS — PASS, HUMAN REVIEW PENDING.** Final **770 PASS /0 FAIL /0 SKIP** in1206.63s (488 unit/282 real integration), both specification validators PASS;740 baseline cases retained plus30 new. Zero external Gemini,2 intentional blocked probes,0 unexpected attempts. Real MCP/B09/LangGraph/Saver, fresh-process token/dollar resume and retained-volume lifecycle PASS. Endpoint-specific count settlement zero; standard400000/complex800000 tokens with independent dollars and saved-setting preservation. B10 genuine live gates remain OPEN/PARTIAL; no B11, push or ZIP. Review: docs/evidence/B10OR2-RESULTS.md. This current summary supersedes historical headings.
- Root causes: count requests were left uncertain despite verified endpoint nonbilling;60000 cumulative tokens admitted only one or two realistic decisions. New endpoint-specific count audit/zero reconciliation, independent capacity/cumulative controls and safe explicit pause reasons; no historical ledger rewrite. Existing60000 checkpoints and money caps require explicit authorized upgrade; profiles do not grant money.
- Six-decision actual B09/MCP/Saver simulations cover allthree categories, competing hypotheses/dated contradiction, pipe+drain and candidate/verified topology, older incidents, pickup/schedule history, source revisions,503 and output repair. Plausible prompt counts/output/thinking receipts are simulations, not billed Gemini usage. Token and dollar limits each pause then resume the same checkpoint in two real processes, retaining counters/native writes.
- Compatible old-test changes limited to two unit files: new finite maximum bounds and known count billing zero. No previous test removed; all other tests and all prior evidence unchanged. New22 unit/8 integration cases. Focused/targeted overlapping batches and one sandbox setup error are documented without inflating totals. One completed final run after interrupted timeout-metadata correction, with --durations=25/--run-persistence; application/test code fixed throughout.
- Retention: original city858/1246 revision2104/all42 drain links CANDIDATE, B01 probe, B08/B09 source/history,101 accepted trace observations, B09R v1/v2 audit, B10 revision103/80nodes/47edges and all6 SDK threads/12 executions match; private ledger witnesses remain row-identical with5120 accounted tokens. Registryv3/migrations0001/0002 and dependency lock unchanged. Fresh rolling proofs retained separately before restoring accepted bytes.
- Exact source inventory/patch, raw tests, slowest25 durations, zero-provider interlock, simulated request/ledger histories and commands: docs/evidence/B10OR2-*. Remaining: genuine Gemini three-category/contradiction/topology/B10-3 gates, proxy/expiry/historical billing limits, existing SDK recovery/canonical activation and future DEC-004 findings. No product capability is declared complete. STOP for review, no B11.

## DEC-046 — B11 authorization, sequencing exception and SDK preflight | 2026-10-18

Human explicitly authorizes B11 while deferring B10 genuine Gemini acceptance to final integration. B10 remains PARTIAL/OPEN, not retroactively passed. B11 only R09/R13/R14 with all18 requirements preserved; no B12+, frontend, ZIP, live provider or remote push. Accepted B10-O-R2 source/security audit PASS (770 recorded cases, actual source fingerprints and zero-call proof); local baseline commit9f7ec1d created from audited files, preserving af42149.

Before application changes, inspect official GraphRAG SDK release and run real MD/PDF ingestion/retrieval in an isolated temporary Python3.12 environment and disposable SDK graph. SDK absent from existing75-package environment. Only pin after smoke success; no unnecessary LLM extras/model downloads. Deterministic test LLM/embedder is simulation, actual SDK/database pipeline must be exercised. Required docs/registry/manifest inspected: frozen18MD manifest uses owner_department_name; canonical Document lacks version/effective/review/owner metadata. Preserve old manifest/evidence, introduce explicit corrected metadata and any additive migration after supported SDK spike; never edit0001/0002.

Planned paths if compatible: app/memory source models/SDK adapter/reconciliation/retrieval; strict B11 contract and normalized manifest; additive document metadata migration; existing two organizational MCP handlers and case memory integration; targeted unit/integration tests and memory guide/evidence/six trackers. Risks: cross-graph partial ingestion, unsupported SDK version/APIs, unchecked citations, trust promotion, hidden-data leakage, source temporal supersession, checkpoint compatibility. Verify actual SDK ingestion/indexed chunks/citations for MD/PDF; repeat/version/revocation/error/recovery; fresh-process persistence; real MCP/Saver where integrated; original data/checkpoints/ledger before/after; unit metadata/security/absence/conflict tests and both spec validators. Do not run all770 unless demonstrated cross-cutting risk justifies it. Human reviews source-backed citations, retained history, zero-provider evidence and recovery. If SDK cannot run safely after minimal supported adaptation, record precise blocker and STOP, never substitute handwritten SDK success.

Preflight command `uv pip index versions` was unsupported by pinned uv0.13.1; `python -m pip index versions graphrag-sdk` succeeds, latest1.4.0. Official docs show new GraphRAG/ConnectionConfig API but published wheel must be inspected; no assumption of API parity.

B11 preflight details: `graphrag-sdk1.4.0` published wheel inspected. Real current API uses `Ontology` (GraphSchema deprecated), native async FalkorDB, mandatory `<docs>__ontology` companion graph, explicit per-ingest extractor/chunker and per-retrieve strategy. Initial pip download stalled; switched temporary environment to pinned uv0.13.1. SDK mandates gliner/torch/scipy/hnswlib even with deterministic strategy; no pretrained model weights loaded/downloaded. Actual smoke pending; project pyproject/lock untouched until success. PDF derivative of unchanged D001@v1 generated with original hash/path and synthetic disclaimer, rendered and visually inspected; initial bundled Poppler lacked font config, corrected with temporary writable fontconfig. No production source promoted.

Retention preflight: B01–B09 source/accepted traces and B10 six threads PASS; original ledger witness row-identical5120 accounted tokens. Original verify_b09r hardcodes restored historical rolling proof and failed its fingerprint comparison; unchanged assertions rerun via explicit accepted B10OR2-regression-B09R-runtime-proof adapter PASS including both original v1/v2 readbacks and31 accepted trace observations. No database/evidence edits; scripts/verify_b11_retained_history.py documents exact compatibility adaptation.

### DEC-047 — B11 verified SDK adaptation and canonical metadata strategy | 2026-10-18

Original SDK1.4.0 smoke failed on6.0.2: two legacy fulltext procedure arities rejected and opened SDK circuit breaker. Supported injected FalkorDBConnection subclass translates exactly those two fixed calls to documented CREATE FULLTEXT INDEX DDL. Adapted real SDK ingest MD+PDF, finalize, vector retrieval PASS(1chunk each/2cited chunk IDs); original failure retained. No server upgrade, SDK source patch, mock SDK, generated Cypher or model download. Pin SDK[pdf,markdown]1.4.0 only; all prior direct pins retained. Use SDK's built-in LocalRetrieval over typed GraphStore/VectorStore with explicit RO connection for runtime, not multi-path generated Cypher. Deterministic offline embedding/extraction strategy clearly labeled, not semantic model-quality proof; no paid fallback.

Preserve immutable registryv3/0001/0002 and frozen manifest. Canonical Document refs use existing fields(id version-bound,source_uri,content_hash,content_ref); explicit validated version/owner/effective/review/trust/SDK chunk hashes live in same-key companion CivicDocumentVersion with compatible additive0003 storage migration, as0002's companion pattern. Do not assert new public fields silently. Version IDs ORG:<document_id>:<version> prevent collision with physical D1 etc. Same canonical write transaction creates strict Document and companion only after actual SDK chunks verified. Application-managed journal phases STAGED→INDEXED→READY, no cross-graph transaction claim; retry verifies SDK chunk hashes before canonical commit, never authoritative lookup of nonREADY records. Retain old versions and metadata; correction/revocation is explicit version/status audit, no destruction.

Runtime retrieval is fixed municipal scope and trusted exact source/SDK config, bounded excerpts with document/version/hash/location/review labels; synthesized extracted assertions remain PROPOSED, never civic causal proof. Reuse accepted B05 case history/B09 immutable correction history for episodic/semantic memory, source-backed procedures separately. Two existing read MCP tools gain sourced implementations via optional trusted memory reader injection; absent config remains UNAVAILABLE. No new tool/action permission and no checkpoint/spending changes. Tests: source model/hash/path/owner/date/trust/injection boundaries; real SDK ingestion/version/idempotency/recovery/revocation; actual MCP retrieval and same-thread Saver; fresh-process + restart persistence and allbefore/after retained comparisons. Targeted regressions first; no automatic full770.

B11 final verification selection: target source/citation/SDK tests plus existing schema/graph models, MCP contracts/history/policy, B10 contexts/models/provider/token/spend/ledger, actual official/custom MCP, B10 runtime/safety/accounting and B01 lifecycle. No automatic full770 run: registry/0001/0002 and all previous direct pins remain unchanged,0003 is isolated compatible storage, and changed behavior is confined to read-source handlers/optional bootstrap/cache. Run broader full only if focused regressions demonstrate a cross-cutting failure. The schema-transition failures arose because the new citation schema was edited during an in-flight focused batch; preserve them, rerun only two affected cases after stable contracts. Actual episodic-memory INVALID_OUTPUT then exposed missing Evidence node context; fixed by reusing existing evidence projection/merge, exact case1PASS9.49s, without weakening broker/schema. Initial new MCP fixture timeout15 exceeded existing10 cap; corrected fixture only. All failures recorded.

B11 ingestion admission refinement: enforce a single host-controlled SDK-ingest lease per canonical/document graph,30s overall deadline within60s lease, and check lease before canonical commit. Reject >128×800 parsed characters before SDK graph writes. This makes the documented single-writer/bounded-ingestion policy executable rather than relying on operator convention. Changes confined to new B11 modules, with exact real tests for competing lease denial and pre-write chunk cap; affected B11 ingestion cases retested, no repetition of unrelated full770. Runtime read/checkpoint/spending source unchanged.


## B11 final implementation and verification | 2026-10-18

- **CURRENT B11 STATUS — PASS, HUMAN REVIEW PENDING.** Organizational memory and actual SDK1.4.0 MD/PDF ingestion/cited retrieval implemented; canonical19versions/SDK19chunks, repeat19/19,0003READY. Final targeted308PASS (226unit/82real), final B11-only40PASS (25unit/15real), strengthened three-graph MCP1PASS, lifecycle1PASS;313distinct cases total,0finalFAIL/0SKIP. Both SPEC validators/retained-data/accounting checksPASS; zero external Gemini/countTokens. No full770rerun, justified DEC-047. B10 genuine live gates remain OPEN/PARTIAL under explicit human sequencing deferral. No B12+, frontend, push or ZIP. Exact results/inventory/patch: docs/evidence/B11-RESULTS.md. This current summary supersedes historical headings.
- Sources: frozen18MD originals/manifest retained; canonical owner mapping and synthetic PDF derivative in data/documents/b11. Strict source/version/effective/review/authority/citation contract; unknown fields/scope/paths/hash/symlinks/evaluator instructions denied. No synthetic/LLM statement promoted to verified civic policy or cause.
- Actual SDK GraphRAG ingestion and LocalRetrieval; two fixed6.0.2 fulltext DDL adaptations, SDK document/ontology graphs isolated. Offline lexical hash64/proposed extraction is not genuine model-quality proof. Lock121packages/all75prior versions unchanged,100installed; frozen compatibilityPASS. New compatible0003companion storage,0001/0002/registry unchanged.
- STAGED/INDEXED/atomic canonicalREADY registration, source/chunk/vector verification, idempotency/version supersession/revocation with prior metadata audit. Tested two cross-graph failure boundaries, missing/invalid/unreviewed/disputed/tampered sources, single-writer lease/pre-write bounds. Internal SDK partial writes fail closed for explicit repair, no automatic success.
- Actual MCP organizational reads and8version B09 case memory, validated Evidence context, B05 semantic history projection. Scripted model context/real LangGraph/Saver pause/resume and fresh interpreter retrieval; separate civic/reference/SDK graph revocation proof with unchanged civic revision. Exact-key independent memory RO credential, original official/source/checkpoint/trace permissions preserved. No new autonomous write tool.
- Targeted regression308PASS305.13s; final B11-only40PASS56.82s; strengthened MCP1PASS14.96s; persistence1PASS15.22s. Overlapping unique313cases227unit/86integration; no full770required, no old test modified/removed. Slowest25 and both validators recorded. Failed SDK/API/fixture/schema-transition/evidence-context attempts retained with exact corrections; vendor deprecation warnings not hidden.
- Original B01probe/B04city858/1246rev2104/all42candidate drains/B05/B08/B09 sources/101accepted trace observations/B09R v1→v2/B10source103/80/47/all6threads12executions and ledger5120accounted tokens preserved after restart+recreation. New SDK/canonical19sources/19chunks/PROPOSED statuses/indices persisted; canonical0SDKchunks. Repeat setup19/19replayed. No volume reset or historical witness rewrite.
- Remaining: human review; B10 genuine Gemini gates explicitly deferred OPEN/PARTIAL; offline learned-semantic quality, SDK-internal partial repair, synthetic/history gaps and future DEC-004 approval/event/API/evaluation findings. All18 requirements binding, no backend/product-complete claim. Proposed next B12typed plan/DAG/owner/procedure/monitoring draft only after explicit approval. STOP.

Final source-admission/excerpt refinement: version>1 requires explicit supersession of latest registered version;26source unit+1real version testPASS4.40s. Exact-ID excerpts use verified indexed SDK source chunks, avoiding semantic top-k starvation; affected real MD/PDF/version/MCP cases retested. No old test/source behavior weakened. Distinct final cases312(227unit/85real), overlapping batches not summed. Earlier lifecycle anchor preserved separately.

### DEC-048 — B11 canonical procedure identity correction | 2026-10-18

Final normative review identified procedure_id projected from Document ID. Preserve Document identity and add existing registryv3 KnowledgeProcedure nodes, version-bound ORGPROC IDs, document_ref to exact Document, status PROPOSED regardless source review. Existing required fields/constraints suffice; no0001/0002/0003 mutation or ontology invention. New ingestion creates Document+procedure+companion in the same fenced commit. Previously registered B11 demo source refs get additive idempotent procedure backfill on trusted replay after verifying source/SDK chunks. KP.version remains normative string; MCP response version is integer from validated Source (explicit projection). Source ownership stays validated canonical Department ID in source companion; no invented relationship. Return real KnowledgeProcedure IDs, never claim verified policy. Recheck exact MD/PDF/idempotency/version and actual MCP cases, canonical replay/counts; all original B01–B10 histories remain unchanged. No B12 draft planning/resolver/approval/operations implementation.

Final procedure-state persistence verified: repeat only B01 lifecycle1PASS15.25s after DEC-048, earlier proof preserved under B11-earlier-*; fresh interpreter read exact final19PROPOSED procedure/document bindings, source/version/chunk hashes and same checkpoint thread. All original B01–B10/101traces/ledger witnesses rechecked unchanged. No additional full regression.

Source date normalization is explicit: original date-only effective_from values are retained in the frozen manifest and interpreted as UTC start-of-day validity for this synthetic demonstration. This is a policy-validity boundary, not an invented observation or review time. Canonical created/retrieved timestamps remain actual UTC.

Final UTC boundary verification: supersession compares canonical parsed instants, including optional fractional seconds, rather than string order. Exact real test rejects whole-second rollback from .1Z and accepts .2Z, retaining original and new procedure/document versions.1PASS, no earlier test or data changed. Final distinct coverage313(227unit/86integration), all final casesPASS; earlier overlapping batch counts remain historical.

### DEC-049 — B11-R eligible retrieval, replay validation and latest history | 2026-10-18

Authorized B11-R only, requirements R09/R13/R14 with R07/R15 boundaries; all18 remain binding. Installed SDK1.4.0 LocalRetrieval/VectorStore.search_chunks has global top_k and no source-filter argument. Choose the smallest bounded fallback over actual verified eligible SDK chunks, retaining actual SDK search, rather than extending vendor internals or increasing global top_k without completeness. At most20 eligible sources×128chunks,5citations×800characters. Fallback means source-applicability retrieval, not semantic relevance; disclose fallback and cap. Validate source eligibility and exact SDK chunk binding before citations, never metadata-only evidence.

Share required indexing validation across registered replay, complete SDK retry, new ingestion and retrieval. Check Chunk embedding VECTOR index OPERATIONAL/dimension64/cosine and Chunk text FULLTEXT index, exact chunk IDs and finite64 vectors matching deterministic embedder within float32 tolerance. Explicit SDK_PARTIAL_REQUIRES_REPAIR on invalid state; no automatic graph repair/rebuild. This verifies observable metadata/vectors, not ANN internal membership or cross-graph atomic integrity. Existing immutable migrations/data/credentials unchanged.

Case memory: temporal visibility in query before cap; newest assessed_at/id descending with requested limit+1 bounded101 lookahead; select newest budget, present selected chronological assessed_at/id ascending. Preserve predecessor ID as historical reference, add explicit OMITTED_PREDECESSOR gap when not selected; never export it as returned evidence. Existing envelope fields/outcome_summary string remain; compatible behavior contract documented without ontology/schema changes. Exact omitted total unknown from lookahead. No outcome inference or causal promotion.

Focused plan: one real19-source corpus scenario covering every department/action pair and demonstrated Water Utilities INSPECTION crowding; isolated healthy replay/missing vectors/wrong64vector/missingvector-index scenarios;8revision limit1 then104revision limit100 history with cutoff and links; existing supersession/revocation test and one actual MCP/Saver case only. New evidence B11R prefix, old evidence restored byte-identically after reused tests. Both validators once after final changes. No770/313 rerun, lifecycle restart or live provider. Risks: source eligibility, finite vector checks, temporal exclusion before cap and predecessor provenance; review exact outputs and zero-call guard.


## B11-R corrective verification | 2026-10-18

Authorized requirements R09/R13/R14 plus R07/R15; all18 preserved. DEC-049 records choices/alternatives.
- Real original-code reproduction: source crowding omitted eligible coordination source D018 and global INSPECTION top12 excluded both Water Utilities chunks. Deployed original-versus-corrected RO comparison confirms0→D005/D017 citations. Missing embeddings replayed successfully; limit1 returned oldest assessment. All three corrected and exercised on real code.
- Actual SDK global search retained; bounded fallback reads/verifies eligible SDK chunks (20sources×128chunks,5citations×800characters). Explicit ELIGIBLE_SOURCE_FALLBACK, never metadata-only evidence or learned relevance claim. Real19-source corpus covers10department/action pairs, including Water INSPECTION.
- Shared vector/index validator before replay/new registration/retrieval: actual OPERATIONAL Chunk embedding VECTOR64/cosine plus text FULLTEXT, exact IDs/count, finite64vectors matching offline embedding within float32 tolerance. Healthy replayPASS; missing embeddings/wrong64vector/missingvectorindex each explicitly SDK_PARTIAL_REQUIRES_REPAIR. No automatic repair/reset or ANN internal-membership guarantee.
- Latest visible assessment revisions selected DESC time/id before requested budget+1 (<=101), selected output ASC time/id. Truncation/OMITTED_PREDECESSOR gaps preserve omitted IDs as history references, not returned evidence.8revision limit1 and104revision limit100/latest1/historical-cutoff casesPASS; existing schema/envelope unchanged. No B09 guard weakened.
- Exact tests/logs: B11R-COMMANDS.md, B11R-RESULTS.md, B11R-test-summary.json. Initial3failed reproduction; corrected batch4PASS/1fixtureFAIL28.07s; isolated history rerun1PASS16.68s; existing version/revocation plus extended actual MCP/Saver/fresh-process2PASS16.36s.7 final distinct real integration cases,0 unresolvedFAIL/0SKIP. Overlapping reproduction not summed. No separate unit run; actual graph scenarios cover new validation logic. Both validatorsPASS once after final source/contract changes.
- Ordinary pytest interlock inherited by Python MCP children:0 external Gemini/countTokens,0 unexpected attempts; offline embedder/NoLLM and scripted agent are not genuine live model proof. New proof only B11R prefix; old B11/B00–B10 evidence unchanged. No dependency/migration/city/checkpoint/accounting changes; corruption only owned isolated graphs, deployed comparison read-only.
- Minimum selection suffices: all source applicability pairs; healthy and three damaged indexing states; small/overcap/temporal history; directly affected version/revocation and one actual broker/schema/trace/Saver/resume test. No full770/313 suite or lifecycle operation because no cross-cutting/persistence change.
- Remaining: human B11 acceptance, B10 genuine acceptance OPEN/PARTIAL, offline semantic quality, bounded citations/source/version caps, SDK manual partial repair and ANN internals not proved; historical mutable-node visibility still applies. B12+ approvals/events/API/frontend remain outside scope. STOP after B11-R.

### DEC-050 — one-wake B11-LIVE-SMOKE authorization and fences | 2026-10-18

Human explicitly authorizes one synthetic investigation/thread, one live wake, <=US$0.15 including unknown held reservations, <=2 generation attempts incl schema repair, <=1 count per generation. R06/R07/R09/R13/R14/R15; all18 preserved. No B12/full live acceptance, model switch, resume, cap increase or extra live campaign.

Installed existing Gemini adapter uses two schema attempts and configurable transient retries; set transient_retries0, retry_wait_budget0, output2048, cumulative60000, existing case cap0.15. Runtime Budget min_iterations2 alone cannot stop after one selection. Minimal harness recompiles the existing StateGraph using supported static interrupts: before RootCauseAnalyst/ResolutionPlanner/Coordinator, after Investigator. This prevents analytical writes, further model selection and post-READ execution; original handlers, provider/PROMPT/Selection/MCP/Saver stay unchanged. One-shot exclusive marker binds exact profile/investigation/thread before HTTP; no resume path. Test the static interrupt branches offline, not another real investigation. No new spending subsystem.

Normal `.runtime/ai-spend.sqlite3` absent at preflight; no real default ledger to reset/recreate. Normal first-use existing Ledger initialization is permitted for this first actual run, preserving all three retained probe ledgers and their rows/settings. Existing probes have zero sessions/open holds; their historical/external billing is not a provider balance. Initialize default existing implementation with unchanged defaults, allocate only the one new case0.15, no project-limit increase/hold clear/counter reset. Record first-use explicitly.

Official Google current model, GenerationConfig JSON schema/count request and standard pricing verified before calls; bundled schedule0.75input/3.75output+thinking per1M, valid until2027-01-01; count policy currently nonbillable. Existing B10-3 prompt explicitly says organizational/case-memory tools unavailable although B11 enables them. Do not silently change it during smoke. Encourage source guidance through normal missing-evidence context and allow Gemini's actual READ/PAUSE choice; graph-only read cannot establish live organizational retrieval. Nonbillable actual broker discovery/ACL/cited-memory preflight, bounded live wake, fresh-process checkpoint/trace/ledger read. No accepted test reruns or container lifecycle operations.


## B11-LIVE-SMOKE — BLOCKED | 2026-10-18

DEC-050 records original authorized single-wake fences; R06/R07/R09/R13/R14/R15 and all18 preserved. One attempted run for INV-B09-d8b67c785a6aa6bdcf800dbefe0a4f2f/thread ae94b094ee9f4ad599f88789df4d959e, private profile .runtime/b11-live-smoke-agent.json. Actual provider attempts0count/0generate, known$0/held$0, no model version/selection/usage/checkpoint/live trace. No Gemini compatibility success claimed.

Actual official/domain discovery16tools, exactROpermissions and cited Drainage source preflight PASS;6offline static interrupt casesPASS1.28s,0fail/skip/providercalls. A real host ExceptionGroup occurred before thread binding/provider scope. Read-only diagnosis establishes fixture created12:00UTC vs wall06:25UTC; Control.bind would violate monotonic updated_at. Preflight incorrectly omitted temporal visibility. Original inner exception was not captured, precise temporal precondition documented without inventing captured stack. First diagnostic separately failed on relative profile paths; absolute-path discoveryPASS/sameinventory. No accepted source policy weakened.

Limits: case0.15USD incl holds; zero transient retries, at most2 schema generations/count<=1 each;2048output; one provider decision/one wake; static interrupts block analytical writes and stop after READ. Default live ledger absent and initialized once via existing implementation unchanged8USDproject defaults/newcase0.15, no historical probes altered, no counters/holds/caps reset or raised. Exclusive attempt marker/quarantine remain, no second live attempt. Existing B10-3 prompt still excludes memory despite B11 runtime; preserved and disclosed.

Evidence prefix B11-LIVE-SMOKE; exactcommands/IDs/results/limits in RESULTS.md. Fresh-process source/Saver/ledger/catalog reads confirm no checkpoint, no thread binding,0requests, quarantine. No full770/313/7case rerun/container restart; narrow harness tests only. B11/B11-R technical evidence preserved, all old source/data/checkpoints/dependencies/migrations unchanged. Next: human review, separately authorize valid fixture and exact recovery path before further live smoke. No B12. B10 three-category/contradiction/topology/end-to-end acceptance OPEN/PARTIAL.

### DEC-051 — B11-LIVE-SMOKE-R single authorized replacement | 2026-10-18

Human authorizes one replacement synthetic case/thread and one live retry only; preserve original failed graph/quarantine/markers/evidence/accounting. R06/R07/R09/R13/R14/R15; all18 binding. Optional keyword-only clock injection into existing fixture leaves deterministic default behavior unchanged, but smoke captures actual UTC and uses it consistently for intake/open. Temporal preflight uses canonical Reader visibility on investigation/incident/cluster/assets and actual connecting relationships, checks monotonic bind, exact profile, empty checkpoint, no quarantine/conflicting binding; repeat immediately before ownership/provider entry. Do not rewrite old case times or clear quarantine.

Versioned successor B11-1 changes only stale B10-3 capability guidance; original B10-3 bytes/hash preserved. Read discovered/authorized organizational/case-memory tools, report absent data/capability, maintain source untrust, version/revocation/citation/provenance and all investigation/approval safeguards. No provider framework/schema/function-call change. Existing retries0 + two schema attempts bound2generation/atmost1count each; existing Ledger case cap0.15 including holds. One-shot replacement marker, one selection/wake/READ; public static interrupts block other actions and stop after Investigator. Existing project cap/ledger/history untouched. Nested failure export includes only exception class/category/allowlisted code, never raw text/bodies. Observed versus inferred reasons distinguished.

Minimal tests: old6static fence branches; new temporal future rejection with no ownership/quarantine side effect and actual-clock isolated real bind; successor exact-preserved prefix/suffix safety test and directly affected provider unit cases. Both validators once after source edits. No770/313/7case or lifecycle rerun. Official model/pricing/API verified before the one retry; exact replacement ID/prompt/model/limits/original linkage recorded first. STOP after outcome, no further live call or B12.

B11-LIVE-SMOKE-R preflight nuance before HTTP: deterministic fixture request IDs produce the same local Investigation ID INV-B09-d8b67c785a6aa6bdcf800dbefe0a4f2f in distinct isolated source graphs. Replacement record identity is sourcegraph e924ed0c58b94d14a278202f0bb1ab15 + that ID; replacement thread57185be0ce624da5a8b69472c16f811a and checkpoint4412d2da051743eaaf1a0de67e92f706 are new. Existing ledger case_key is the local ID; deliberately retain its existing0.15cap/history/zero-call original rather than reset or replace. Thus the shared original+replacement case exposure remains bounded0.15, stronger than separate reset. Per-thread request evidence distinguishes original0calls from replacement. No third case or alternate ledger to bypass limits. This is isolated demo scope, not global cross-graph ID uniqueness.


## B11-LIVE-SMOKE-R — PASS, human review pending | 2026-10-18

Requirements R06/R07/R09/R13/R14/R15; all18 preserved. DEC-051 records alternatives/bounds and scoped ID reuse. Actual UTC optional clock injection corrects smoke preparation while retaining deterministic fixture defaults. Required investigation/incident/cluster/assets/connecting-edge visibility, monotonic binding, exactsource/profile/no checkpoint/binding conflict/owner/quarantine checked before READY and immediately before runtime ownership. Original failed case/profile/timestamps/zero-call thread/quarantine remain unchanged.

Versioned B11-1 changes only B10-3 stale capability sentence; original B10-3 bytes/hash preserved. Provider selects successor version, runtime/optimization contracts synchronized. Discovered/authorized organizational+case-memory READ permitted with explicit gaps, untrusted source/citation/version/revocation/authority/uncertainty and prior hypothesis/approval safeguards. Existing structured Selection/provider/MCP/Saver retained, no new framework/function calling. Sanitized nested exceptions expose class/allowlisted category/code only, no raw error strings or bodies.

Minimal offline16PASS0fail0skip7.15s=15unit+1realFalkorDB temporal/bind. Old6static interruption branches, successor safety/parity and nested error redaction,6direct provider request/repair/failure/budget tests plus one timeout-version compatibility check. Future clock rejected without ownership/quarantine/provider side effects; actualUTCbind/recheckPASS. Only existing timeout assertion adapted from literal B10-3 to currentPROMPT_VERSION; old behavior checks retained. Both specvalidatorsPASS once after final source/contract edits. No770/313/7case/lifecycle rerun.

One real authorized retry on .runtime/b11-live-smoke-r-agent.json/source e924ed0c58b94d14a278202f0bb1ab15, local investigation INV-B09-d8b67c785a6aa6bdcf800dbefe0a4f2f/thread57185be0ce624da5a8b69472c16f811a; original threadae94b094ee9f4ad599f88789df4d959e retained0requests. Existing ledger shares conservative0.15casecap for same local investigation ID, no reset/replacement ledger/project increase. Actual prompt B11-1 hash40316606a6d7189e273e14b7dbaaee7e016031a0ee73b3ca5cbb18e7a978a105; modelgemini-3.8-flash reported same version.

Genuine Gemini selected civicly::get_organizational_procedures {department_id:DEPT-DRAIN,action_type:INSPECTION}, concise rationale persisted.1count+1generation,0repair/0transientretry/1selection/1READ; no errors. Actual MCP discovery16tools and validated citations D001-PDF,D001,D002,D003,D012 version1(PROPOSED source-derived guidance, not verified causes) reached committed journal+workflow state. Static interrupt stopped after Investigator; no resume/second wake/analytical write. Fresh process verified native checkpoint1f1cabd8-07d6-60da-8002-032cf251731c, decisionDEC-B10-6db86522180a134fd3c9766e2a00e1e8, executionMCP-B10-6db86522180a134fd3c9766e2a00e1e8 and brokertraceaa34fccdf8eb4210b473a5e74f1e50a0. Exact output/trace digest matches, original source citations retained.

Provider usage prompt7123/candidates99/total7222; thinking not separately returned, prompt+candidates sumtotal; existing default0 absent thoughts documented. Count settled0 under verified nonbillable policy. Generation known5713500nanodollars=$0.00571350, held0, activeSessions0/openHolds0. Prior project8USD/case0.15 unchanged; reservations guarded before HTTP. Application cap not guaranteed Google cutoff/balance; no claim actual invoice. No fallback/model switch/other paid calls.

Exactsourceinventory/diff/commands/runtime/proofs under docs/evidence/B11-LIVE-SMOKE-R-*. Current status closes this small compatibility smoke only, not B10 three-category/contradiction/topology/end-to-end gates (OPEN/PARTIAL). SDKofflinelexicalquality/manualrepair/bounded-source/synthetic/history and future DEC-004 gates remain. STOP for human review before B12 or any further live call.

### DEC-052 — B12 typed drafts, responsibility and storage | 2026-10-18

Human authorizes B12 only; R10 advanced with R09/R11/R14/R15/R17 support, all18 remain. No live calls/B13/approvals/WorkOrders/events/API/frontend. Registryv3 already names ResolutionPlan DRAFT, ActionTask PROPOSED, PRODUCED_PLAN/HAS_TASK/DEPENDS_ON/ASSIGNED_TO/TARGETS. It has no complete draft payload field or cross-graph procedure edge. Keep registry/0001–0003 immutable; compatible additive0004 companion stores closed full draft/provenance/hash under version-bound plan ID. Canonical native plan/task/DAG/assignment/target edges remain actual source-graph records. External canonical B11 KnowledgeProcedure/Document references remain exact graph+ID+version/hash citation pointers in companion; do not invent impossible cross-graph GOV_BY edges or mirror authoritative procedures into investigation graph. No new ontology names/enums silently substituted.

Closed task action_type adopts documented action code INSPECTION (registry currently unconstrained string; other execution actions deferred until sourced/resolved), priority uses existing severity enum LOW/MODERATE/HIGH/CRITICAL rather than inventing MEDIUM. Monitoring is typed draft policy, no worker/evaluation/completion. Water comparable-rainfall evidence, road pavement+wear followup, waste scheduled+actual pickups and reaccumulation window; missing opportunity stays unresolved. No unsourced numeric cost/duration/confidence fields.

Resolver requires dated visible source-backed VERIFIED MAINTAINED_BY from each target to exactly one visible canonical Department. Candidate/multiple/unknown owners block; verified responsibility overrides document-derived assertions; document owner never grants execution responsibility. Proposed source-reviewed B11 procedures can guide a draft but stay PROPOSED. Validate actual B11 current/reviewed/version-bound retrieved citation and procedure, action applicability, rejection of revocation/supersession. Resolver uses existing memory/domain logic and SDK reads, not copied business extraction.

Plan domain checks investigation binding, latest immutable B09 assessments and two competing hypotheses with reasons, evidence membership, target links, owner/evidence temporal validity; whole validated batch through existing fenced repository single parameterized graph statement + audit. Readback+hash gate acknowledgment. Source graph lease serializes version/head/idempotency checks; external memory revision recheck before commit, no cross-graph transaction claim. Response-loss retry returns committed request-bound exact receipt even if later inputs revoked; that is historical acknowledgment, not approval or revalidation of executability. Old versions immutable in this service; no reset/drop on recovery.

Runtime retains legacy RECOMMEND shape and old checkpoints(defaultNone plan); compatible RECOMMEND {plan_draft:...} validated by the same domain service; adds plan ID/version/hash receipt to state. Invalid drafts explicitly pause without semantic auto-repair; existing bounded iterations/resume guards retained. Versioned B12-1 prompt and controlled_action_schemas supply actual closed plan schema; Selection wire shape unchanged. Optional trusted memory capability config only; no new arbitrary Cypher/MCP mutations. Tests smallest unit/DAG/hash/monitoring selection + three real issues/crossdept, ownership/citation denials/version/replay/recovery, actual scripted model/MCP/Saver freshprocess/resume + invalidruntime and affected state/provider/context regression. Bothspec once final,0external, no full770/313/accepted smoke rerun.

Final B12 contract audit corrects current agent_runtime descriptions (not historical evidence): domain_writes/reasoning/not_claimed now distinguish B12 DRAFT-only writes from still-absent B13–B15 execution. New planning_contract and optional plan-state compatibility explain actual behavior. Earlier first SPEC pass is retained; rerun final validators after this necessary current-contract correction, not a repeat for extra test evidence. No application/test change, live call or new migration behavior.


## B12 typed draft planning — PASS, human review pending | 2026-10-18

R10 advanced; R09/R11/R14/R15/R17 supporting, all18 mandatory, no full capability-complete claim. Closed PlanDraft/tasks/basis/monitoring/receipt models; version-bound cited procedures, immutable latest assessments, evidence/target/investigation references, reasons/alternatives/outcomes/risks/uncertainty, SIMULATED + deterministic normalizedSHA. Tasks admit sourced INSPECTION drafts currently; no invented cost/duration/confidence or repair authority. No approval or execution.

Bounded12task DAG rejects duplicates/unknown/self/cyclic dependencies and foreign basis refs. Actual verified/datelyattributed MAINTAINED_BY ownership resolves accountable department; B03 evidence/date rules reused. Unknown/candidate/conflicting/mismatched ownership blocks; document author separate (coordination source can guide actual Drainage owner). Actual B11 SDK source/version/hash/chunk/ref comparison and action applicability, future-citation/superseded/revoked rejection; PROPOSED remainsPROPOSED. Monitoring requires comparable rainfall/waterlogging, pavement+wear, or scheduled/actual pickups+reaccumulation window; absent opportunityUNRESOLVED, completionneverresolution.

Additive0004 companion, checked checksum/index/constraint readiness in isolated graphs. Registryv3/0001–0003 unchanged. One existing fenced/audited parameterized graph mutation creates native ResolutionPlanDRAFT/ActionTaskPROPOSED and PRODUCED_PLAN/HAS_TASK/DEPENDS_ON/ASSIGNED_TO/TARGETS plus fullcompanion/provenance/hash; external B11 graph IDs are pointers, no fake crossgraph edges. Request-safe acknowledgment, injectedpostcommitresponse-loss/retry, next-headversion/CAS and preservedpriorversionPASS. No WorkOrdercreated (existing fixturehistory remains), no B15platform scaffold. Accepted graphs not automatically migrated/seeded.

B12-1 successor prompt/currentruntimecontracts enable RECOMMEND{plan_draft}; originalSelection wire schema/framework unchanged. Narrow service called by ResolutionPlanner; invaliddraft→PLAN_CLARIFICATION_REQUIRED pause. CurrentplanID/version/hash receipt persisted and decode-bound; legacyRECOMMEND/Nonecheckpointdefaults retained. Actual scripted READ→modeldraft→domainvalidation→Saverpause, freshPython read sameplan/hash and resumedthread withoutduplicatePASS; cyclicinvaliddraft creates0plans. No genuine model-planning claim.

Focused final49distinctPASS/0unresolvedFAIL/0SKIP:42unit/7real; new15unit/6real + selected27unit/1legacyreal. Initialcollection error(newmodulebasename collision) and foundation18PASS/1promptloaderFAIL28.11s retained; corrected runtime/affected31PASS29.80s, legacy1PASS7.75s; finalB12references6PASS50.94s overlaps. No inflated batch sums. Both validatorsfinalPASS, preliminaryPASS retained before necessary stale domain-write/not-claimed contract text correction. Ordinary inherited providerguard all5batches0external/0unexpected; no livecalls.

No full770/313/accepted7/smoke rerun. Selection covers boundedDAG/hash/monitoring, allthreeissues/crossdept, source/owner/ref denials, version/replay/ackloss, actualMCP/Saver/freshprocess/resume/invaliddraft, legacyrecommend and changedstate/context/provider. No containerlifecycle: existingdurability protocol unchanged; additivegraphschema/singlemutation and freshprocess verified. Allpriorevidence/frozenfixtures/migrations/dependencies preserved; previousliveledgerhistory notreset/altered.

Review docs/evidence/B12-RESULTS.md/B12-COMMANDS.md/B12-FILES.md/B12-changes.patch and backend/PLANNING.md. Humanverify road planDRAFT/version/hash, Road→Waterdependency, ownerEvidence and PROPOSEDcitations, monitoring; inspect freshprocesscheckpoint. Remaining B10 genuine fullacceptance OPEN/PARTIAL; draft-only INSPECTIONscope/source action applicability and synthetic/manualSDKrepair/boundedhistory/DEC-004futuregates. ExactnextB13 approvals/auth/planbinding/idempotentWorkOrder only after newauthorization. STOP afterB12.


## DEC-053 — B12-R bounded remediation and rejection feedback (design before code)
Scope R01/R08/R09/R10/R13/R14/R15/R17; B13 not authorized. Registry ActionTask.action_type is an open string, and no existing normative remedial enum was found. Admit only DRAIN_BLOCKAGE_CLEARANCE (BLOCKAGE, DrainInlet/DrainSegment, Drainage), SUBGRADE_REPAIR (SUBGRADE_FAILURE, RoadSegment, Road), MISSED_PICKUP_RECOVERY (MISSED_PICKUP, WasteCollectionPoint, Sanitation). Retain INSPECTION. New codes are draft policy, not operational states. Require latest addressed SUPPORTED or VERIFIED B09 assessment, reviewed supporting physical report for each target, verified MAINTAINED_BY ownership and exact current B11 procedure citation/action. Documentary authority never supplies physical evidence.

Remediation adds optional typed conditions; absent conditions serialize exactly as old B12 drafts for historical hash compatibility. Supported-now requires MET causal inspection (all cause confirmation codes) and action-specific reviewed safety evidence. Conditional future proposals require explicit UNMET guards; an unmet causal inspection must depend on an INSPECTION task covering the target. Safety remains a typed unresolved gate; no text-only bypass. All proposals remain non-executable, unapproved, simulated DRAFT/PROPOSED. Insufficient/contradicted evidence permits inspection, not remediation. Existing source corpus is inspection guidance, so add exactly three newly authored synthetic demonstration MD policies D019–D021 with separate manifest, explicit author/owner/effective/review/checksum/action provenance. Preserve frozen original sources/manifests. No storage migration or durability mechanism changes.

Feedback: bounded closed schema, static messages/codes/categories, safe schema paths/task IDs, clarification/evidence-capability/operator-recovery distinctions. Never serialize exceptions or Pydantic inputs. Persist safe rejections and pre-write capability failures in workflow observations/state. Lease loss, uncertain writes and checkpoint errors propagate to existing quarantine; no false rejection or model retry. If no safe checkpoint can be written, operator recovery uses the last durable checkpoint, not a fabricated acknowledgment. Committed-acknowledgment loss remains native request-id replay.

Alternatives rejected: universally VERIFIED findings (prevents justified qualified proposals); arbitrary repair strings/free-text guards (unverifiable); rewriting inspection authority (false provenance); new rules/orchestration framework (unnecessary); catching all infrastructure faults as invalid drafts (unsafe). Focused tests only: three-category real SDK/DB remediation, guards, affected DAG/hash/replay/source/ownership cases, actual scripted MCP/LangGraph/Saver fresh-process and feedback, representative recovery/redaction. Both SPEC validators once final. No live provider, full suite, restart, or operational records.

Source refinement during focused verification: B11 intentionally omits Source.review_status=PROPOSED by default. New demo documents receive explicit **automated author self-review for policy/guard consistency**, not independent human review or municipal authority; reviewed_by identifies Codex B12-R automated self-review. Source metadata REVIEWED records that limited curation, while every KnowledgeProcedure/assertion stays PROPOSED. Preserve B11's reviewed-only retrieval and reject relaxing include_candidates to admit arbitrary unreviewed/disputed procedures. This metadata choice does not supply causal evidence or operational approval.


## B12-R corrective review gate | 2026-10-18

DEC-053 implementation verified: three specific remedial codes; latest addressed SUPPORTED/VERIFIED plus per-target reviewed physical support and current report/finding hashes; typed conditions, verified ownership, exact B11 source/version. No future dependencies for supported-now; conditional causal gap requires target inspection dependency. No approval/execution. Three new synthetic self-reviewed sources through real SDK, PROPOSED assertions retained. Feedback safely separates draft/evidence/capability from operator recovery, while uncertain writes/lease/checkpoint faults retain quarantine. Old normalized hashes unchanged.61distinct focusedPASS; both SPEC validatorsPASS once; six inherited zero-provider proofs. Initial source metadata and missing road fixture topology failures recorded; no application guard weakened. Alternative/final rationale, source inventory and actual narrow patch in B12R evidence. No migration/dependency/durability change; no lifecycle. Stop before B13.

Review docs/evidence/B12R-RESULTS.md, B12R-COMMANDS.md, B12R-FILES.md and B12R-changes.patch. Human: inspect3category gates/citations, actual native receipt/hash/checkpoint, safe invalid/recovery feedback and zero operational deltas. STOP for review; exact next task B13 only after explicit authorization.

## DEC-054 — B12-R2 commit-boundary recovery (before implementation)
Scope R09/R10/R13/R15; preserve all18 requirements and B12-R policies. A post-commit PLAN_READBACK mismatch was a PlanningBlocked and incorrectly yielded draft_committed NO. Saved-replay Pydantic/read failures can suffer the same mistake. Introduce a narrow PlanRecoveryRequired subclass of existing repository OutcomeUnknown, with static sanitized message and bounded graph/request/investigation/plan/version/hash/stage identifiers. Guard commit-attempt/readback and saved-replay verification separately from proven pre-write validation. No healthy receipt is returned until storage integrity/readback verifies. UNKNOWN means persisted/usable state requires reconciliation, never evidence of rollback. Existing intentional INJECTED_ACK_LOSS RuntimeError match and native exact-request healthy replay remain compatible.

Runtime carries that typed recovery context into existing RecoveryRequired, which triggers unchanged wake quarantine; no false rejection observation, automatic redraft/version/retry, reset or quarantine clearance. Generic legacy PlanningBlocked PLAN_READBACK must also fail closed in feedback. Last durable checkpoint, native decision and saved companion retain reconciliation identities; no promise of a newly persisted feedback/checkpoint after failure. Operator reads exact original request and plan, verifies integrity and pending write/wake ownership, then follows existing reviewed recovery procedure. Test deliberately leaves quarantine set and performs read-only inspection only; no reconciliation repair is invented.

Alternatives rejected: treating all PlanningBlocked as pre-write (original bug); returning an unverified receipt (unsafe); automatic replay/clearing quarantine (not authorized); new recovery storage/migration (unnecessary). Minimal tests: one actual isolated SDK/FalkorDB/MCP/LangGraph/Saver mismatch regression with one retained plan and quarantine, affected pure feedback/recovery unit branches including adjacent replay validation, one existing healthy ack-loss/idempotent replay case, both specification validators once final. No full suite, remedial scenarios, provider or lifecycle.


## B12-R2 corrective review gate | 2026-10-18

DEC-054 verified. Store.commit attempt/ACK verification and saved-replay read/receipt verification now raise narrow OutcomeUnknown-subtype PlanRecoveryRequired with bounded exact graph/request/investigation/plan/version/hash/stage context. Runtime carries it into existing RecoveryRequired/quarantine; no false rejection or unverified usable receipt. Legacy PLAN_READBACK feedback is UNKNOWN. Healthy INJECTED_ACK_LOSS RuntimeError matching/native same-request replay unchanged. No storage/schema/migration/policy/source redesign.16unit/2real distinctPASS, both SPEC validatorsPASS once,0provider. Initial new test matcher failed on LangGraph task note despite correct recovery; only matcher fixed and that isolated case rerun; first fault graph left untouched. B13 not authorized.

Review docs/evidence/B12R2-RESULTS.md, B12R2-COMMANDS.md, B12R2-postcommit-recovery.json, B12R2-FILES.md and B12R2-changes.patch. Human verification: inspect exact identities,1plan/version1, UNKNOWN/recovery diagnostic, last durable checkpoint with no false acknowledgment and retained quarantine. Reproduce only the isolated mismatch test; no reset/retry of stored fault wake. STOP for review; B13 requires explicit authorization.

## DEC-055 — B13 authentication, approval and order foundations (before code)
R09/R10/R11/R13/R15/R17; all18 remain mandatory. Accepted canonical source has5operators (analyst/approver/three department leads), although prose says4role seats. Preserve all5/source bytes and add OP-ADMIN only to private authentication registry;6small demo accounts cover four roles and all three categories. No public signup or enterprise tenancy. Passwords/signed30minute sessions/revocation in owner-only local SQLite; PBKDF2-HMAC-SHA256600000 with random16byte salt, constant-time comparison, random session nonce/HMAC, server-resolved role/department only. Stdlib API verified against Python3.12 hashlib docs and OWASP password-storage guidance (no dependency added). Private setup never prints passwords/tokens; no credential in graph/audit. ANALYST draft/submit; APPROVER decide/create approved scoped orders; department leads read/update only own assigned work; ADMIN read and audited session revocation only, no safety bypass. Existing internal planner actor remains a trusted host capability, never a human approver; authenticated draft gateway resolves identities.

Approval covers every immutable plan task/native ID/action/targets/department/assignee, plan/version/hash, submitter/approver/time, current proof/evidence references. Caller scope must match full plan exactly. Current assessments, B11 citation version/revocation, owner/evidence and remedial policy revalidated at submit/approval/order/update. Plan must be current head; stale/superseded never newly authorized. Rejection retains reason/history; revisions require new approval. Native lifecycle plus compatible005 companion state attestations, never rewrite immutable B12 payload/receipt. Store.get validates legitimate native lifecycle changes through audited lifecycle ledger while preserving old DRAFT receipts and checkpoint binding.

Conditional approval is proposal approval only: unmet causal/safety gates retained; any UNMET gate or unsatisfied dependency blocks order creation. No waivers synthesized. B13 work-order operation initial AUTHORIZED, exact approved assignment, deterministic plan/task identity plus request hash ledger. Native Approval/WorkOrder/StatusEvent/DomainEvent and required IMPLEMENTS/AUTHORIZED_BY/HAS_EVENT/EMITTED_EVENT links committed with immutable request/audit/event companion in one existing fenced mutation. Event envelopes meet current contracts; delivery remains B15. Monotonic CAS and normative state machines; assignment/cancellation only in B13, execution/completion deferred B14. ADMIN cannot bypass guards.

Additive0005 solely companion/index/unique/readiness metadata;0001–0004 unchanged. Post-write/readback uncertainty raises existing OutcomeUnknown-style bounded identity recovery, never false rejection/automatic retry/reset. Canonical memory graph revision checked around revalidation, no cross-graph transaction claim. Focused tests unit auth/gates/state/scope + shared real flow/denials/replay/staleness, competing CAS, ACK loss, affected B12 saved-checkpoint and B12-R2 recovery; both validators once final. Lifecycle only if demonstrated durability change warrants it; one-statement protocol reused, fresh-process persistence will verify native order/audit without automatic container restart. No live provider/B14/B15/API/frontend.

B13 rejection refinement: approving/creating/updating work revalidates current causal/source/ownership proof. A REJECTED decision still requires authenticated approver, exact immutable current plan/scope/hash, native projection and CAS binding, but does not require a revoked procedure or stale cause to become valid first. Its audit explicitly records binding-only rejection validation; it cannot authorize work. This permits attributable rejection of unsafe proposals without weakening approval guards.

B13 seed compatibility correction before finalization: accepted B12 ROAD_DAMAGE draft has a WaterPipe inspection owned by DEPT-WATER. The5source operators lack a water-utility lead; six-account initial auth choice would block that accepted cross-department scope. Add exactly OP-WATER-LEAD to private auth metadata alongside OP-ADMIN:7small synthetic accounts across4roles, all5original source records untouched. This is a required assignee gap, not enterprise identity expansion. Preserve existing private credentials/sessions while adding only the missing seeded operator through trusted host bootstrap. Run one targeted accepted road inspection DAG approval/dependency case (not all remedial scenarios). New auth setup/private audit and contract reflect7 rather than claiming4or6. Four describes role classes; original source itself already has5identities.


## B13 review gate | 2026-10-18

DEC-055 implemented and runtime verified. Final7private demo identities cover4roles; source5accounts untouched, private admin/read+revoke only and utility lead required accepted road DAG. Exact binding/current source validation/rejection reason, conditional approval vs execution gates, one fenced native+audit+event mutation, deterministic orders/request replay/CAS and UNKNOWNpostcommit recovery implemented. Existing B12payload/receipt/hash immutable; lifecycle0005attested; actual checkpoint and B12R2recoveryPASS.25distinctPASS(18unit/7real); no provider/lifecycle/full suites. Initial lease/outside-active-scope harness errors corrected without weakening guards; handoff hook indentation fixed, only affected validator rerun. Seven-account rationale supersedes initial six-account design; no canonical seed mutation.

Review backend/OPERATIONS.md, docs/evidence/B13-RESULTS.md/B13-COMMANDS.md/B13-FILES.md/B13-changes.patch. Human inspect B13-flow.json exact binding+audit/order, denials/conditional/checkpoint proof, run only isolated flowtest for reproduction. STOP for human review; exact next B14 simulated execution and independent outcome verification only after explicit authorization.

## DEC-056 — B14 explicit simulated execution and independent verification (before code)
Scope R01/R03/R08–R13/R15/R17; all18 binding. B13 accepted. Reuse0005 hashed companion and existing fenced mutation; do not modify registryv3 or immutable migrations. Extend native lifecycle attestations through IN_EXECUTION/MONITORING/COMPLETED. WorkOrder has no FAILED: unsuccessful attempt maps IN_PROGRESS→BLOCKED, ActionTask→FAILED and immutable InterventionOutcome INCONCLUSIVE/assessment_status INTERVENTION_FAILED. Work completion is ACTION_COMPLETED, never root cause addressed. Independent deterministic monitor writes MITIGATION_VERIFIED + assessment_status RESOLUTION_VERIFIED only after every relevant task/dependency/gate and observation policy passes. Insufficient/no opportunity persists INCONCLUSIVE with explicit MONITORING/INCONCLUSIVE reason. No new ontology labels/enums; bounded metadata in0005 companion.

Synthetic demo policy B14-1: water requires a reviewed COMPARABLE_FOLLOWUP_RAINFALL observation (explicit authored comparability, not inferred meteorology) followed by FOLLOWUP_WATERLOGGING measured0/1 in unit boolean; road reviewed WEAR_EXPOSURE then FOLLOWUP_PAVEMENT0/1 damage in boolean; waste reviewed matching SCHEDULED_PICKUPS and ACTUAL_PICKUPS integer counts in unit pickups, at least one scheduled pickup, followed by REACCUMULATION_WINDOW in hours >=24 and WASTE_REACCUMULATION0/1 boolean at/after that window.24hours is a labeled synthetic demonstration minimum, not municipal/physical standard. Rain/wear opportunity is binary authored observation without fabricated physical thresholds. Each target requires complete coverage, completion precedes window, opportunity precedes final finding. Mixed positive/negative observations are contradictory, not averaged. Independent authenticated analyst review and separate post-completion report/source required; operator cannot submit a resolution label. Outcome includes policy, evidence, observation window and intervention. No root-cause verification inferred.

B09 planner/authorization/receipt/report integrity reused inside one operation compiler, with actual authenticated reviewer identity (caller-supplied Review forbidden). Command-bound request journal and native evidence/event/audit coupled, no duplicate inspection logic. Allowed explicit codes/units/time and exact work target/procedure checked. New report may be explicitly reassessed by authenticated analyst through same B09 planner; immutable old assessments retained. START/new orders require current causal proof; evidence recording/terminal result may truthfully finish an already-started intervention after contrary observations, but cannot authorize further remedial work. Same-label latest assessment with unchanged original support and contradictions may advance through legitimate progress; changed meaning requires existing revised PlanDraft version→new submission→fresh approval, never mutate approved gates.

Verified closure ends active incidents, controls cluster and completes monitoring plan/investigation using normative transitions. Recurrence requires qualifying new adverse follow-up after prior verified window, uses B08 normalization/plan/pattern with a distinct occurrence after recorded end; new incident joins original cluster, cluster/investigation REOPENED, old immutable outcome stays. Existing B05 maintenance/case memory traverses native plan/task/order/outcome paths. Explicit handlers only; no B15 delivery/worker, scheduler, generic hidden scenario engine, API or live call. UNKNOWN writes preserve existing pending/recovery identities; no automatic reset/retry/clearance.

Alternatives rejected: WorkOrder FAILED/new ontology or overwriting outcome (unnecessary); completion=resolution (false); whole graph revision freeze (rejects legitimate updates); relaxed causal gates or new autonomous repair (unsafe); parallel inspection service (duplicate provenance logic). Focused tests per authorization, both validators once final; no lifecycle as storage protocol unchanged.

B14 final review refinement: a latest same-meaning assessment can have a new ID,
while immutable remedial gates still cite the original assessment. After validating
latest status/cause, retained original reviewed support and unchanged contradictions,
validate original immutable gate references against current report/finding hashes.
Never substitute IDs in approved content. Added actual BLOCK→same-meaning reassess→
START regression. Evidence/result/monitor proof explicitly says immutable-binding
recording, not the inherited B13 rejection label. Preliminary validators retained;
final validators repeated once after this necessary final source correction.

## B14 review gate — 2026-10-18

DEC-056 implemented and exercised, including current same-meaning assessment guard with immutable original remediation references, truthful evidence-only audit proof, narrow planned journal sources and retained original B03 semantics. Native FAILED WorkOrder rejected as nonexistent; failed task/blocked work/immutable inconclusive outcome used. No root-cause verification inferred.41distinctPASS/both final validatorsPASS/0provider. Review source inventory, exact narrow patch and sanitized runtime evidence under B14.

Review backend/OPERATIONS.md and docs/evidence/B14-RESULTS.md, B14-COMMANDS.md, B14-FILES.md, B14-changes.patch. Human inspect retained3issue outcomes, contradiction/failure/recurrence-memory and ACK-loss proof; optional single isolated water test. STOP after B14 for review.

## DEC-057 — B14-R pickup-anchored verification and validated recurrence scope (before code)
Scope R03/R09/R12/R13/R15/R17; all18 binding. Only B14-R authorized. B14-1 incorrectly measured waste window from evaluation start; new B14-2 uses latest relevant actual pickup observed_at per target. Repeated equal aggregate pickup counts are not summed or interpreted as per-vehicle telemetry: conservatively latest actual observation anchors interval. Differing totals remain INCONCLUSIVE. Every supplied reaccumulation window must claim >=24hours and actually elapse at least its claimed duration after that anchor; final condition follows the window. Missing/too-short opportunity MONITORING; contradictory findings remain explicit. Preserve B14-1 implementation separately for historical interpretation and leave all old outcomes/checkpoints/proofs immutable. Fresh requests use B14-2; exact old-request replay remains historical acknowledgment only.

Reuse original investigation: recurrence write atomically adds sourced temporal INVESTIGATES(new incident) with original incident/cluster links retained. Response/event exposes investigation and link identities. Reject exceeding existing three-incident runtime bound rather than silently truncate or expand storage/state. On explicit resume under existing ownership, validate graph link, B08 COMMITTED journal/canonical hash/AFTER_RECORDED_END receipt, same cluster/issue and ended prior episode, and actual reviewed recurrence evidence. Only then project active incident/asset IDs and source hashes into a newly validated state, record host-generated scope-refresh audit, retain historical plan/hypothesis references as historical context, and require fresh MCP READ. No mutation of old checkpoints, arbitrary caller-supplied incident injection or automatic wake. Invalid/ambiguous scope fails closed through existing recovery/quarantine.

Alternatives: successor investigation (unnecessary identity/checkpoint handoff), blindly append graph IDs on decode (unvalidated silent injection), evaluation-start timer (reproduced false positive), summed duplicate aggregate counts (invented telemetry), rewrite B14-1 records (false provenance). Minimal tests: targeted waste policy boundaries/multiple pickups+affected old policies, one real waste flow, extended water recurrence with replay/history + same-thread actual MCP/Saver refresh and one direct legacy resume case if concrete binding risk warrants. Both validators once after final source edits, no provider/full suite/lifecycle/B15.

## B14-R corrective review — 2026-10-18

DEC-057 implemented/exercised. Latest actual pickup timestamp conservatively anchors repeated aggregate observations; insufficient duration cannot verify despite declared window/evaluation start. B14-1 retained exactly with historical contract/provenance. Original investigation gains new sourced temporal incident link in same fence. Explicit resume validates B08 receipt and reviewed source evidence before model-validating new active scope; mandatory MCP read remains. Successor investigation/telemetry/new delivery machinery rejected as unnecessary.14distinctPASS, both validatorsPASS once,0provider.

Review docs/evidence/B14R-RESULTS.md, B14R-COMMANDS.md, B14R-FILES.md, B14R-changes.patch and B14R-audit.json. Human inspect waste timestamps/versions and sourced new investigation link/checkpoint refresh; optional two-case isolated reproduction. STOP for human review before B15.

## DEC-058 — B14-R2 repeat-safe recurrence refresh (before code)
R03/R09/R13/R15; all18 preserved. Scope subtraction wrongly treated retained ENDED history as a new episode after first adoption. Use existing persisted host RECURRENCE_SCOPE_REFRESH proof and B08 receipt/link/journal hash to recognize previously validated historical IDs. Validate historical issue/cluster/end-before-adopted-episode and receipt relation; do not blanket-ignore unknown/ENDED records. Genuinely new additions retain original full validation, finite bound, fresh-read barrier and fail-closed recovery. No storage/state-schema/worker changes, old checkpoint edits, retained graph repairs or quarantine clearance. Files: agents/recurrence.py, tests/b14r_runtime.py, tests/unit/test_recurrence_scope.py, six trackers and new B14R2 evidence only. Tests: focused recurrence unit file, one existing real recurrence/MCP/Saver flow extended through source update + second explicit resume, both validators once final. No waste/full suites/live/lifecycle/B15.

## B14-R2 — 2026-10-18 | human review pending

DEC-058 implemented: recognize history only through retained host refresh proof, live scoped link/journal hash/B08 receipt hash+related IDs, issue/cluster and ended-before-adopted temporal checks. Subtract proven history from genuinely new additions; original new-episode validation retained. Unknown/ENDED additions not exempt. No state/storage/contract expansion. Real two-resume path and malformed/history-proof units PASS.

Review docs/evidence/B14R2-RESULTS.md, B14R2-COMMANDS.md, B14R2-FILES.md and B14R2-changes.patch. STOP for review.

## DEC-059 — B15 bounded durable delivery and explicit activation (before code)
R03/R07/R09/R12/R13/R15/R16/R17; all18 binding; B14/R/R2 human accepted, B10 full genuine acceptance OPEN/PARTIAL. Reuse0005 unique/hashed CivicOperationState companion with delivery/consumer/activation/monitor keys, plus immutable attributed B15 audit Evidence marker in every fenced transition (marker is repository intent subject; companion-only uncertain writes must not be mistaken for unchanged). No new migration/dependency/storage engine. Native DomainEvent statuses mirror authoritative delivery companion; operation payload identity/provenance stays unchanged. Legacy B08/B09 committed journals and B12 draft receipts become explicitly derived facts with deterministic new adapter IDs, never claims of a previously emitted event. Native B13/B14 identities preserved. Validate all envelopes/source bindings; invalid rows terminal/inspectable, never raw payload public.

Only explicit private exact ActiveProfile activation with operator/reason and current-revision cutover by default; optional bounded explicit historical event selection. Never enumerate/process retained proof graphs. Bounded source/delivery scans fail closed rather than silently truncate. Public event cursor is per-source monotonic registration sequence, distinct from domain identity and attempt number; redacted allowlisted projection persisted at registration for replay, no HTTP/SSE routes.

Claims + case serialization ledger use existing short repository fence, durable owner/expiry/attempt/CAS and immutable audit. No writer lock during dispatch. CLAIMED expiry before RUNNING can reclaim; RUNNING expiry is uncertain unless durable consumer receipt or host delivery-key checkpoint marker proves completion. Existing agent ownership/lease/quarantine remains authoritative and never cleared. Host delivery marker commits at safe paused checkpoint; coalesced event set digest binds one bounded wake. Crash after checkpoint before outbox ack reconciles from public Saver marker, not a guessed no-op. Unknown wake quarantines/recovery; no blind model retry. Known pre-dispatch unavailable errors alone retry finite exponential backoff; explicit replay increases bounded ceiling without resetting attempts/history. Deterministic READ→PAUSE local worker only, no reused live permit or human operational authority.

Monitoring intent uses controlled due time, deterministic FOLLOWUP_REQUESTED/missing-opportunity receipt; never fabricates observations/resolution. Informational classifications are durable with reason; self-generated analytical events do not trigger wake loops. One local worker, finite batches/coalescing and safe bounded stop/restart; B16/API/frontend/paid calls excluded. Minimal meaningful tests include actual process restart, claims/concurrency, committed discovery/ACK-loss/unknown recovery, actual MCP/Saver event/recurrence resumes, public cursor fresh-process read, invalid/exhausted/replay, unit validation/redaction/routing/backoff; both validators once final.

## B15 — DEC-059 implementation and verification, 2026-10-18

TechnicallyPASS, human review pending. Existing0005 companions chosen over new queue/migration; fresh immutable audit subject avoids ambiguous companion-write misclassification. Exact private profile + immutable activation cutover, optional20historical IDs, no all-graph scan. Original native events preserved; legacy committed facts carry new deterministic adapter IDs, not invented original event history. Short fenced/CAS source writes, <=4compatible wake coalescing, separate existing agent ownership/Saver, host exact-batch completion proof before durable receipt. Unknown wakes remain recovery-required/quarantined, no automatic retry or clearance; only proven pre-dispatch failures retry. Default authored READ→PAUSE, no live permit. Monitoring means requested follow-up/missing opportunity, not invented observations. Public registration cursor separate from event identity/attempts.

Actual26distinctPASS(21unit/5real), final both validatorsPASS; earlier localhost sandbox denial and two fixture-only assertion errors preserved in B15 logs/commands. Seven retained guard proofs0provider; no dependency/migration/registry/MCP/business policy change except narrow DomainEvent delivery-status update permission and optional host runtime markers. Newest source guard normalizes malformed Saver read to sanitized recovery inside ownership; directly affected real path rechecked1PASS27.55s. Existing request/plan/data/quarantines remain; accepted B10 full genuine Gemini gate OPEN/PARTIAL. Exact implementation, tradeoffs/limits, imports/consistency/recovery: backend/EVENTS.md; inventory/patch/evidence: docs/evidence/B15-*. STOP before B16.

## DEC-060 — B16 authenticated typed API boundary (before code)
R02/R03/R08–R17; all18 mandatory, B15 human accepted; B10 genuine Gemini OPEN/PARTIAL. Implement only B16, no B17 dashboard/map/subgraph/trace/SSE, B19scenario or live provider. FastAPI0.143.3/Pydantic2.14.1/Uvicorn0.54.0 already installed locked; exercise ASGI and actual localhost server. Routes invoke a service facade; fixed bounded projections remain in services, never route Cypher. Exact private ActiveProfile/0005/delivery activation, existing Auth+Planning/Operations/Memory configured explicitly; startup never activates/migrates/seeds/resumes. Separate B15worker consumes durable investigation/resume intent; deterministic only.

Contract corrections: accepted B08 discriminated intake, B09inspection transitions, B12typed draft, B13full exact plan/version/hash/assignments+CAS, B14progress/inspect/evaluate/recur replace stale underspecified transport inputs. Add essential draft creation/list, authorized work-order creation, work inspection/progress/evaluation/recurrence, inspection request/transition, hypothesis proposal/assessment paths; preserve public domain names and service invariants. Typed projections distinguish immutable draft receipt/current lifecycle, approval/unmet gates, completed work/verified outcome, current/historical assessment and proposed synthetic procedure authority. Public auth login/logout, health only per inventory; login returns session token only in its required response, never evidence/error/logs.

Independent report review: authenticated analyst session in X-Reviewer-Authorization header, not JSON; reject caller Review/Actor/reviewer identities. Same existing B14 service handles authenticated work reports. Generic inspection report without work authorization cannot claim reviewed operational authority. Role/department filtering applied before bounded pages/counts and detail/source/history; deny hidden records consistently, no totals leak. Bounded scan500 with explicit overflow; stable ID cursor/basic pagination now, rich cross-resource pagination/DTO completion B17.

Transport idempotency uses hashed0005 API request companion through existing fenced/audited store; bind authenticated operator+Idempotency-Key+path+canonical payload. Store sanitized projected receipt for exact replay; conflicting binding409. Uncertain dispatched/no-receipt state requires operator reconciliation and never automatically redispatches. Domain service request_id derived from same identity; caller cannot pass identity/auth/runtime/config. Need preserve recoverable safe request correlation without exposing graph/profile. Small service adapter rather than new business/storage subsystem.

Files: backend/app/api/{models,dependencies,application,__main__}.py; backend/app/services/http/{service,reads}.py; contracts/api_endpoints.json/api_models.json; backend/API.md; focused tests/unit/test_api.py and integration/test_api_runtime.py plus fixtures/network proof; scripts/validate_api.py+two validator hooks; six trackers and B16evidence. Risks: stale source readbacks, uncertain commit/output projection, cross-department existence leakage, reviewer token logging, open schema/runtime knobs, post-HTTP worker identity. Tests: closed OpenAPI/complete core coverage/error/redaction; parameterized actual session/RBAC; one real login→case→draft→approval→order→inspection/report→completion/outcome; same fixture durable B15resume→real MCP/Saver outside HTTP; exact/conflicting replay/CAS/revocation/department/invalid reviewer/unknown commit; actual localhost health/openapi/auth call; both validators once final. No broad suites/lifecycle/live. Human inspect generated docs, role-specific reads, safe recovery and separate worker evidence. STOP after B16.

### DEC-060 refinement — source-bound transport identity
The first real HTTP workflow passed; two fresh fixture repeats correctly failed closed with MCP CONFLICT/quarantine. B16 generated identical domain request/case IDs for the same actor+key across isolated source profiles; B15's deterministic new-case thread then produced an execution ID already retained in the shared trace store for another graph. Read-only retained checkpoint/trace evidence identifies that collision. Correct the B16 **host-side request digest** to bind the exact configured source graph as well as actor+key. The graph name remains private (only opaque hash leaves API); request identity/replay stays stable within the original source. Existing B15/runtime/trace semantics and historical records unchanged; no retry/clearance/repair of failed cases. Fresh isolated failing-path test only; add direct source-identity regression. This avoids a test-only randomized key workaround and preserves cross-phase identity contracts.

## B16 DEC-060 exercised outcome — 2026-10-18

44actual typed FastAPI operations/42paths, no stubs. Normative inventory55operations assigns8B17/3B19 deferred; compatible API model corrections preserve accepted strict service semantics. Full exact binding/CAS/idempotency, independent reviewer header, server roles/department source/history filtering, immutable draft/current lifecycle, actual assessment history and recorded outcome vs completion. Source+actor+key opaque request ID prevents cross-profile shared trace collisions without changing existing B15/MCP/Saver. Known pre-write rejection actionable; post-dispatch uncertainty409UNKNOWN/manual reconciliation, no implicit replay. Host-only private service config/startup, no migrations/seed/activation/worker/live.

FastAPI0.143.3/Pydantic2.14.1/Uvicorn0.54.0 from existing lock, actual ASGI and TCP localhost tests.63distinctPASS(62unit incl3accepted direct regressions/1real end-to-end fixture), final both validatorsPASS. First real workflow passed; two independent repeats exposed same-source-unbound request collision with shared old trace; retained errors/quarantines/read-only diagnostic, fixed B16 identity only. Corrected realpath1PASS30.32s and finalroutecheck1PASS29.64s; final outcome projection3unitPASS+actual retainedDB/auth readPASS.12ordinary guard proofs0provider, historical paid requests/data/oldtests/migrations/evidence retained. No B17/fullsuite/lifecycle/live. Exact files/patch/commands/limits in B16evidence and backend/API.md. STOP for review.

## DEC-061 — B16-R post-dispatch classification (before code)
R09/R11/R12/R13/R15/R16; all18 preserved. Only HTTP adapter boundary correction. B09 couples domain mutation+COMMITTED journal, then readback can raise ValueError; B08 similarly verifies receipt after commit. B12 wraps commit/replay verification as OutcomeUnknown, B13/B14 wrap commit/readback as OpsRecovery; HTTP projections occur after those calls return. Current ValueError→REJECTED is invalid across every dispatch branch.

Use explicit request-local PRE_WRITE/DISPATCHED/RETURNED phase around each existing domain invocation, with source revision/pending-state evidence for known no-write service rejections. Pure accepted command validation occurs before invocation; malformed transport/key/authorization/conflicting identity stay actionable. After invocation, ValueError/Pydantic alone never proves no commit. Returned-service projection/receipt failures always recovery-required. Known conflict/authorization/gate failures from an invocation are actionable only when unchanged audited source+no pending write establishes no domain mutation; otherwise recovery. Preserve B09 deterministic journal ID and validated committed receipt/entity IDs, existing source-bound HTTP correlation and underlying recovery identities. Best-effort sanitized metadata in existing api_request; if it cannot persist, retain last durable state, no claim of new feedback. DONE replay validation fault is also recovery; healthy DONE and conflicting-key behavior unchanged. No new storage/recovery subsystem, rollback, retry, graph repair or clearance.

Touched source: backend/app/services/http/service.py only; new focused backend/tests/unit/test_http_recovery.py and backend/tests/integration/test_http_recovery.py, six append-only tracker entries, B16R evidence/patch. No model/contract/migration/domain/runtime changes intended. Exact tests: pytest those two new files only (unit mocked boundary/store, real isolated HTTP/FalkorDB B10/B09 fixture+0004/0005, readback fault and post-service projection fault in one setup; replay/no duplication, pre-write422/403/stale409/DONE/conflicting key). Both spec validators once after final edits. No full API units/workflow/network/lifecycle/earlier suites/live calls. Human inspect COMMITTED journal/one inspection per request, 409UNKNOWN original correlation, preserved intent and zero redispatch, then STOP before B17.

## B16-R — DEC-061 exercised correction, 2026-10-18

CURRENT B16-R technicallyPASS, human review pending; supersedes earlier B16classification claims without removing history. HTTP ValueError/Pydantic classification was phase-blind: B09COMMITTED readback and in-dispatch DTOprojection could become422/REJECTED. Request-local CHECKING/DISPATCHED/RETURNED boundary now surrounds each accepted mutation; pure B08/B09/B13/B14command validation occurs before invocation. Any ValueError after invocation, every returned-service projection/receipt fault and invalidDONE replay is recovery-required. Known typed conflict/auth/gate (including accepted B12PlanningBlocked) remains actionable only with explicit pre-write phase or unchanged auditedsource/no pendingwrite/no existingrequestjournal; unprovable outcomes stayunknown. B09CAS precheck keeps established stalehash409 before journal creation; authoritative domain guard remains.

Existing source-bound HTTPidentity retained; B09request/journal/entity/investigation plus available plan/domain recovery IDs preserved as bounded metadata in existing api_request and existing sanitized envelope. Metadata persistence best effort, pending source left untouched; lastdurable intent remains if writefails. Exact uncertain replay blocked/no redispatch, healthyDONE/conflicting-key unchanged. No domain/API schema/migration/runtime/storage redesign.19distinctPASS(18mockboundary/Auth-transport units/1real combinedHTTP-B09-FalkorDBtest),0unresolvedFAIL/SKIP; finalbothvalidatorsPASS. One newtestbasename collectionerror retained/corrected, no DBfailure. Seven ordinarypytest/child guardproofs0provider. Only adapter/newfocusedtests/sixappendonlytrackers/B16Revidence changed. STOP before B17.

## DEC-062 — B17 read projections and durable stream (pre-implementation)
B16/R accepted. Scope/requirements, route-to-DTO matrix, touched paths, risks, recovery/auth/cursor decisions and exact focused tests recorded before code in docs/evidence/B17-PLAN.md. Reuse accepted services and B15 registration; no storage/migration/agent redesign, frontend or provider. Original recovery boundaries and all eighteen requirements preserved. Passing status requires actual shared HTTP/FalkorDB/MCP/Saver journey and TCP SSE; schemas/unit mocks alone insufficient.

### DEC-062 implementation and compatibility choices
Reuse pinned FastAPI0.143.3/Pydantic2.14.1/Uvicorn0.54.0, FalkorDB6.0.2/Python client1.8.0, MCP2.3.0 and existing official Saver/GraphRAG; no dependency, image or migration changes. All eight B17 routes actual, no frontend/scenario stubs. Bounded RO service projections reuse registry and B05 evidence/temporal guards; same-response revision readback and per-request batching instead of a new cache/snapshot storage. Conservative scoped graph projection rather than allowing connected foreign-department data. Current pagination has no cross-request snapshot guarantee; explicit limits/capacity errors remain.

Preserve planned DashboardSummary, AgentTracePage, HypothesisPage, GraphSubgraphDTO, MapFeatureCollection, AssetDTO, SSEStream names and required identity fields. Add closed actual schemas, singular asset aliases and event_id/timestamp aliases; nullable condition corrects planned required string against optional registry storage. Preserve accepted B16 PlanDTO.approval_status lifecycle value, explain its legacy name in schema/limitations and use actual ApprovalDTO.status for approval. No domain enum/name/mandatory property changes. EvidenceDTO extends with validated actual findings, measurements, attributed/reviewed source; no generic summary substituted for report meaning.

Persisted activity needs no new graph model: existing canonical AgentDecision and B07 TraceStore source/thread identities → B15 INFO facts/cutover/registration. Domain BROKER parents SERVER, then decision; direct official BROKER parent decision; missing server proof on a failed call remains unknown mode, never claimed model-selected. Selected-path body must match persisted trace ID, journal selection digest, canonical path-ID formats, ordered endpoints and exact evidence set; no path inference from proximity. Adapter shares existing configured delivery cutoff; using wall clock instead silently hid later synthetic-clock decisions in the first actual network check. Stream remains readonly and does not discover/acknowledge records.

Choose browser fetch Bearer header, equality for header/query cursor conflict, contiguous registration replay and explicit cursor-control advancement through hidden rows. No retention deletion exists; missing registrations are CURSOR_EXPIRED/refetch. No queue, fake thinking, startup activation, hidden historical replay, retry or quarantine clearance. Session/resource scope rechecked per poll and emit, bounded50rows/.25seconds/30second connection.

Necessary phase-expectation adjustments preserve earlier tests: B16 OpenAPI unit additionally verifies SSE text/event-stream (all ordinary JSON assertions retained); unauthenticated SSE now401 instead of404 because B17 implements it; prior network path count follows actual route inventory, independently fixed52/49 in new test. No earlier test removed or earlier evidence changed. Focused old API schema/session/latest-outcome/source-ID/redaction cases run; no broad earlier suite. B17 logs retain all failed attempts: harness run keyword, omitted maintenance interval, actual checkpoint Coordinator vs expected AwaitDependency, legacy plan lifecycle expectation; implementation query scalar parsing, configured activity cutoff, proof-reader meter and canonical UTC-Z cursor were corrected and re-exercised. Not counted as passing real integrations until actual journey passed.

### B17 final verification supersedes pending notes above
Both specification validators PASS in the single final make test-spec invocation. Final focused45unit+1real PASS,0unresolvedFAIL/0SKIP; repeated runs count as one distinct integration case. Delivery evidence separates source_graph from the public graph projection; failed-log session text sanitized without value disclosure. Final preservation/private-value/accounting audit and narrow patch recorded under B17-*. B16/R recovery paths unchanged; B10 genuine gate OPEN/PARTIAL. STOP for human B17review; exact proposed next B18 CLI, not authorized now.

## DEC-063 — B17-R truthful per-route query contracts (pre-edit)
R08/R09/R15/R16; all18requirements preserved. Reject undocumented hypotheses date semantics instead of inventing creation-versus-assessment interpretation; remove ignored dashboard pagination. One explicit per-route query allowlist drives closed transport models/OpenAPI and runtime rejection. Internal ReadFilters and actual Views filtering unchanged. Existing query validators retained on derived models; all previously consumed resource/map/trace/graph filters preserved. Unknown/repeated fields sanitized422. Scope/files/risks/exacttests/humanverification recorded before source edits in docs/evidence/B17R-PLAN.md. No domain/storage/migration/worker/auth/SSE/recovery redesign or B18/live.

## DEC-063 exercised B17-R correction — 2026-10-18
Explicit VIEW_QUERY_FIELDS and route-specific QueryRules-derived models are now the single transport allowlist/OpenAPI source. Preserve ReadFilters field definitions/validators and unchanged Views; reject rather than invent hypotheses creation/assessment-time semantics. Dashboard aggregates reject pagination; other consumed filters retained. Other B17handlers inspected: map/resource matches, trace actual timestamps/paging, graph bounds/candidate flag, asset no query, SSE existingcursor/casefilter. Shared superset no longer advertises irrelevant parameters. Legacy scalar repeated keys rejected consistently; no domain/storage/migration/worker/auth/recovery/SSE redesign or dependency changes.

Actual59distinctunitPASS +1realPASS28.03s,0unresolvedFAIL/0SKIP, bothSPECvalidatorsPASS once. One initial unit fixture used analyst against approver-only route; correctRBAC403, correctedfixture and13directlyaffected casesPASS; no realintegrationfailure/retry. Realcase run exactlyonce after finaledits, preserves originalB17assertions and TCPstream. New B17Rproof prefix prevents earlierartifact overwrite. All18requirementsbinding; genuineB10OPEN/PARTIAL; STOPafterB17-R, B18/frontend/liveunauthorized.

## DEC-064 — B18 operator CLI boundary (pre-implementation)
B17/R accepted. Requirements, exact command→acceptedservice mapping, touchedfiles, risks, tests and humanverification in docs/evidence/B18-PLAN.md. Reuse configured in-processAPI/service adapters to preserveRBAC/idempotency/B16-RUNKNOWN instead of secondbusinessimplementation. Explicit boundedofflineadvance only; resetfreshisolatedsmallvalidatedB04subset preserving CANDIDATEfacts, neverdestructivecityreset/B19generator. Privatefiles/secureinput, nonzerofailurestatus; testboundedreadiness only. No liveprovider/frontend/B19, oldevidence/data/quarantine preserved. RuntimePASS requires actualsuccessiveCLIprocessjourney andisolatedresetproof.

### DEC-064 focused refinement after first real journey
First actualCLIjourneyPASS129.07s. Inspection beforefinaldelivery: bind resetidempotencykey source/operator globally through existingcompanion, with destination in payloadhash, so changingdirectory under samekeyconflicts rather thancreatinganotherfreshsource. Preserve privateSTARTED/DONEmanifest andunknownblocking; no storage redesign. Graph explain should include actual B03hypothesis-evidence PathRecords as qualified analysis, not onlyB17neighborhood; existingfixedGraphQueries service filters to already-authorized publicgraph endpoint/evidenceIDs and same revision, neverrawproperties or inventedmodel-selectedpaths. Add evidenceget read mapping. Directtests and samefocusedjourney recheck thesechangedboundaries only; no broad/lifecycle/live.

## DEC-064 B18 exercised implementation — 2026-10-18
B17/R humanaccepted. Installed civicly entrypoint delegates originalfoundationcode byte-identically to cli.legacy for health/migrate/schema-status, and newoperatorinterface to explicitlyconfigured in-processFastAPI→acceptedServices. No duplicatedapproval/CAS/provenance/inspection/monitoringrules or arbitraryURL/graph/query/shell/providerflags. Privatecredentials/sessionfiles and exactsource/authstorebinding; domainmutations require explicitkey/acceptedtypedpayload, existingUNKNOWN/replay preserved. Stableexits0/2/3/4/5/6; outputSIMULATED/offline, bounded safeIDs/errors. No newpackages/images/migrations.

Explicitadvance uses existingDelivery/Worker/Runtime.ReadPause, no productionhardcodedsolver or paidpermit: discoveryseparatefromconsumption, max4batches, source/actor/key/action/boundshash+existingcompanion/fence gives replayreceipt or UNKNOWNblocking. Resetuses generatedfreshActiveProfile/source/Saver and fixed strictB04subset4nodes2edges; CANDIDATEowner preserved, existingmigrations/ACL/freshcutoveronlynewtarget, previousdomainhistoryunchanged. Existingcompanionbindsdestinationhash/privateSTARTEDmanifest; uncertaininitial/finalintent neverautomaticretry/repair, exactDONEreplayhistorical. Candidateownerstarter lacks verifiedplanningprerequisites bydesign; no newowner-verificationAPI/B19engine or solvedscenario claim. Administrativeauditmetadata additional tofixturecounts. Graph explain combines authorizedB17view with actualB03hypothesis-evidencepaths atsamerevision; qualifiedanalysis, not inventedmodel-selectedcausation, no rawproperties.

Final71distinctunit+1real=72PASS,0FAIL/0SKIP; actual71CLIchildinvocations across onesharedwatercase, defaultofflinechoices and actualDB/MCP/Saver/SDK/sourcecitations/auth. TwooverlappingrealrunsPASS129.07/132.37s (1distinctcase); exception-onlyinitialintentIDretention checked with2mockfaultunits afterlasthealthyjourney, samehealthylogicunchanged. ExistingfoundationredactioncasePASS. BothfinalSPECvalidatorsPASSonce;6guards0externalGemini/countTokens. One metadatautility wronginterpreter failedbeforewrites, correctedtovenv; no testfailurehidden. All18requirementsbinding, genuineB10OPEN/PARTIAL; STOPB18review, B19/frontend/liveunauthorized.

## DEC-065 B19 authorized scope and pre-code design — 2026-10-18
B18 accepted. Scenario controller releases synthetic world observations, never solver choices. Preserve evaluator catalog/hidden truth; neutral public inventory, strict versioned host packets, bounded source-bound reset/advance using existing API intents/B18 fresh isolation/B08+B09 typed services and actual separate field/reviewer authentication. No candidate promotion, fabricated past orders/procedures, automatic approval or verified outcome. See docs/evidence/B19-PLAN.md for exact files/tests/R01–R18/readiness/risks. Unsupported remedial branches remain explicit capability gaps. B20–B23/frontend/live unauthorized; B10 genuine OPEN/PARTIAL.

### DEC-065 early real fixture correction
First mechanics selection:3PASS then S04 reset correctly failed closed UNKNOWN because ROAD_DAMAGE intake referenced only a pipe and requires an explicit RoadSegment. Retain failed source/parent intent unchanged. Correct new S04 intake to reference road+pipe, while utility field inspection remains pipe/DEPT-WATER. No weakening of B08. Explicit new synthetic UNDERLIES surveys for S03/S04 are context, not leak causation; S08 uses a new authored nearby location (~20m from drain), with no flow edge, only in fresh fixture composition. Imported city records/retained candidate statuses unchanged. Earlier observed schema-generator KeyError happened before writing contracts; corrected actual metadata key. No failure hidden.

### DEC-065 scoped runtime isolation and inspection feedback
Accepted evaluation contract explicitly requires agent-process file-read denial, beyond tool-output checks. Add scoped Python audit guard around InvestigationAgent.run, brokers and domain MCP server: block world/evaluator/playbook/evidence directories and private world.json while runtime executes; host controller remains allowed outside that scope. This is defense against accidental Python reads, not an OS sandbox against arbitrary hostile code; agent has no filesystem/shell tool. Actual read denial, tool discovery/results and public projections must be tested. Domain field-report journal actor differs from ADMIN transport actor; request-local Boundary records authenticated expected journal actor and known inspection/investigation IDs, reusing existing recovery readback rules, no new recovery subsystem. Merge public stage under existing write fence. Later stage reads reuse exact Operations.validate (including latest plan/source checks), not weaker status-only approval.

### DEC-065 runtime probe correction and final focused boundary selection
Second mechanics selection23PASS/1FAIL/2deselected: all remaining world variants and real postcommit report fault passed; representative MCP probe incorrectly reused one Context.execution_id for different calls, and durable TraceStore correctly rejected its payload collision. Correct test-only execution IDs; retain failed trace/source/log. Final affected selection: PRIMARY S04/S07, postcommit recovery and representative CLI/MCP/Saver/isolation only. New scoped file guard has focused units plus actual broker read-denial assertions. Per-case later-stage receipts merge under existing fence; global stage requires every scenario case, Operations.validate reuses current exact approval/source rules. No new domain approval or recovery infrastructure.

## DEC-065 B19 exercised delivery — 2026-10-18
B18 accepted.12strict host definitions/24variants, neutral runtime catalog, small deterministic fresh-source setup, explicit reviewed typed release, matching3API/CLI controls and scoped evaluator-file denial. ExistingB18fresh primitive reused rather than duplicate provisioning/storage; existingB08/B09domainservices and B16intent/recovery reused. No migration/ontology/dependency changes or candidate promotion. Explicit new synthetic topology/context surveys carry separate evidence IDs, not city-list verification. Reset hash is stable physical+normalized baseline composition, not byte-identical graph journals/audit. Parent administrative intents append; prior domain history retained.

138distinctPASS(112unit/26real),0unresolvedFAIL/0SKIP.24mechanicsvariants plus1actualpostcommitUNKNOWN/replay plus1actualCLI/MCP/Saver/events/isolation case; choices authored/offline, not model-success.3failed attempts documented/retained: S04missingroadtarget, test execution-ID collision, test missing external evidence_type. BothSPECvalidatorsPASS once after executable/contracts;8zero-live proofs0providers. Actual setup2.8234–3.9651s/release0.0672–0.1759s, local observations only. Oldprivateconfigs/accounting/data/quarantines preserved. Utility repair/capacity/route redesign/dumping action gaps, candidate owners, incomplete historical operational chains and separate pressure inspection limitation remain explicit. See B19-READINESS/RESULTS/COMMANDS/FILES/patch/hidden-isolation. B10 genuineOPEN/PARTIAL; STOPB19review, nextproposedB20 onlyafterauthorization.

### DEC-065 normative DTO reconciliation before final contract correction
Final comparison with pre-B19 deferred schemas found required planned transport fields omitted by the first draft. Preserve them rather than silently redefine them: reset requires scenario_id/seed/confirm (version1 supports explicit integer seed19 and boolean confirmtrue only); advance uses expected_current_stage; ScenarioDTO retains stage, ScenarioPage retains next_cursor/total_count; SeedReport retains actual nodes/relationships/source_documents/seed_fingerprint; SimulationStepDTO retains scenario_id/stage/event_id/revealed_evidence_ids. New safe identity/readiness fields are additive. event_id must reference an actual durable B15 event derived from the committed inspection journal, not a transport request masquerading as an event. Register only that source event via existingDelivery, never auto-consume. Later stages reference actual approval/outcome events. Update current contracts/OpenAPI/tests/runbook together and re-exercise focused B19mechanics, not historical suites. Prior draft artifacts remain audit history, not final schema authority.

### DEC-065 fresh runtime identity correction
Retained-profile full B19 selection25PASS/1FAIL210.80s: repeated representative wake hit a real shared trace identity conflict. Baseline direct B09open used stable world/issue request across fresh graphs, generating identical investigation IDs; existing B15thread/B10execution IDs then correctly collided in globalTraceStore. Bind baseline investigation requests through existing HTTP request_identity(newsource,actor,logicalcasekey). Preserve stable logical assets/reports/fingerprint, but runtime investigations/threads/traces must be disjoint per fresh source. No runtime identity/storage redesign. Retain failed wake/checkpoints/quarantine and originalintent, no retry/clearance/repair. Add disjoint-case reset assertion and final focused B19selection after normative DTO correction. pytest cleanup loss was test-only temporary profiles; private current host configs, retained graphs/city/checkpoints/accounting unaffected. New review harness uses private .runtime/b19-review rather than pytest-autocleanup.

## CURRENT B19 final normative/retention verification — 2026-10-18
Thisappend supersedes prior B19subtotals withoutremovingaudithistory. Final147distinctPASS=121unit/26real,0unresolvedFAIL/0SKIP; finalwholefocused B19selection26PASS226.85s, contract/guard/CLIunits118PASS1.32s plus3acceptedrecoveryunitsPASS0.23s. BothfinalSPECvalidatorsPASS;10pytestchild+2specguardproofs0external/0unexpected. Fourhistoricalpytestfailedattempts retained: S04missingroadasset, probeexecutionIDreuse, probe missingevidence_type, and actualcross-sourcebaselineINV/tracecollision. Newlygeneratedcase requests nowuseexisting source/actor-boundrequest_identity; logicalasset/reportidentityandbaselinehash stable, actualINV/thread/tracesdisjoint. FailedB19wake/quarantine remainsintact, no retry/repair/clearance.

PreservedrequirednormativeDemoDTOfields; explicitseed19/confirmtrue and expected_current_stage, additiveprivateprofile/case/readiness only. Release event_id nowactualdurableB15PENDINGinspectionevent derivedfromCOMMITTEDB09journal; registrationnotdelivery. OriginalSeedReportactualcanonicalcounts/seed_fingerprint, ScenarioDTO.stage andPagecursor/count retained. ExistingOperationsvalidation forlaterstages unchanged. Test-onlypytest-autocleanup lossofoldtemporaryprofiles caughtbyread-onlyaudit; finalall24variantprofilesretainedunderprivate.runtime/b19-review, previousgraphsneverremoved. Actualsetup2.6940–4.5487s/release0.0809–0.1995s; authoredqualitativeworld vsrealDB/API/CLI/MCP/Saver/SDK/eventI/Oexplicit.

S03pressurecontextneedsseparateutilityinspection; historicalwork/recurrence/currentcandidateownership andunsupportedutility/capacity/routeredesign/dumpingactiongaps remain B20–B23matrixitems, no fullscenario/AI/backend-completeclaim. B19RESULTS/READINESS/COMMANDS/FILES/patch/WALKTHROUGH/hiddenproof/audit arecurrentreviewevidence. AllR01–R18binding, B10genuineOPEN/PARTIAL. STOPafterB19review; nextproposedB20S01–S06behaviorandprecisecapabilitycorrections requiresseparateauthorization, nofrontend/live.

### DEC-065 final uncertain replay identity precedence
Inspection of the actual postcommit error vs replay found Recovery constructor preferred route entity label over persisted verified reconciliation.entity_id. For demo route idS01 that can overwrite the actual committed report ID on exact replay. Preserve recorded verified identity by making route entity only a fallback (one dictionary ordering change), not a recovery redesign. Add direct unit plus strengthened existing B19realfault assertion for identical original/replay report/investigation/request identities; run only affected fault and selectedacceptedBoundaryunits, preserve previousproof andquarantines. FinalSPECvalidators follow this last executablechange.

### B19 final UNKNOWN replay identity check — current superseding total
Final148distinctPASS122unit/26real,0unresolvedFAIL/0SKIP. One new unit verifies committed reconciliation.entity_id precedes route label on UNKNOWN replay;3acceptedBoundaryunits overlapPASS0.35s. Strengthenedreal reportfault/replayPASS25.17s with original/replayrequest/report/investigationIDs identical, COMMITTEDjournal/oneeffect andDISPATCHINGreservation retained. Firstattempt1setupERROR4.40s sockettimeoutbeforefaultpath; read-onlycontainerhealthy/CLIhealthok, freshfixture-onlyretry, nooldrequestredispatch/lifecycle/quarantineclearance. Fourpriorfailedassertionattempts+onesetupERROR recorded. BothfinalSPECvalidatorsPASS afterlast executablechange;13pytestchild+3specguards0external/0unexpected. Prior147subtotal superseded. B19RESULTS/COMMANDS/FILES/patch/audit current; retainedfailedwake/all18requirements/B10genuineOPEN unchanged. STOPB19review; B20/frontend/liveunauthorized.


## DEC-066 — B20 qualified evaluation and explicit capability gates (2026-10-18)
Decision recorded before coding in docs/evidence/B20-PLAN.md. Preserve accepted architecture and allR01–R18; add only new evaluation helpers/tests and review evidence. Issue-policy scripts receive current public runtime context and never scenario ID, hidden expected answers or fabricated results. Real services determine classification; the evaluator-only expected map stays outside the model. Alternatives considered: broad action/ownership implementation would require new provenance, permission, procedure, safety and outcome contracts; automatic candidate promotion or unrelated remedies violate accepted contracts. Therefore report PARTIAL/BLOCKED with bounded proposed corrective tasks rather than claiming full acceptance through pauses. No dependency, schema, migration or production behavior changed.

Use existing B19 host reset/release and actual authenticated department/reviewer controls. S03 separate utility report is a new explicitly synthetic target-specific service operation by an authenticated water-department actor; preserve road pressure as context. S01 later independent clear survey retains earlier support and therefore revises to INCONCLUSIVE, not falsely erasing prior evidence to force a clean contradiction label. Distinct authored phase clocks establish chronological assessments; the separate existing B12-R control advances its new clock past the actual SDK citation retrieved_at rather than altering a source citation to bypass time validation. The same-length citation mismatch reaches the actual stale-source resolver. These are harness compatibility choices, not production/recovery changes.

27distinct testsPASS14unit/13real, four retained failed attempts and final2SPECvalidatorsPASS. Actual source-backed positive drainage policy control remains DRAFT/non-executable with synthetic PROPOSED procedure and explicit reviewed causal/safety prerequisites. It does not cure missing scenario owner acquisition. BLOCK-B20-01..05 in B20-GAPS.md retain mandatory ownership, utility, capacity/route, dumping and independent pickup/dumping sequence gaps. S02 partial capacity support from clear drain is a configured discriminator, not measured or VERIFIED capacity failure. No recurrence/outcome manufactured. B10 genuineOPEN/PARTIAL; STOPB20review, noB21/live/frontend.


### B20 final retention evidence — 2026-10-18
Read-only auditPASS: all1534pre-B20 public files retained,1085earlier evidence files byte-identical,116accepted test files unchanged, allsix tracker histories append-only. Production logic/contracts/migrations/data unchanged; original city858nodes/1246relationships/fullcontenthash and42CANDIDATE drainage links intact, B01probe and original B12R2singleplan/quarantine + B19quarantines retained. Historical2paidrequests unchanged with no active sessions/holds. Finalpublicartifact/patchprivate-value scanPASS;9guardreports0external/0unexpected. Actual FalkorDBmodule60002(6.0.2); installed falkordb1.8.0,mcp2.3.0,langgraph1.2.16,langchain-falkordb0.2.0,fastapi0.143.3,pydantic2.14.1; no dependency changes. Exact inventory/patch use pre-B20 snapshot, excluding earlier accepted uncommitted Git work. No old failed graph repaired. B20acceptance remainsPARTIAL/BLOCKED; STOPforreview.


## F00 frontend decision — parallel isolation (2026-10-18)
Human explicitly authorized frontend in parallel with ongoing backend work, superseding the former B-END prerequisite for frontend only. Preserve all R01–R18/backend acceptance gates. Choose independent frontend/ workspace and separate frontend/docs/tasks.md sequence; root backend sequencing unchanged. Alternative of editing backend APIs or sharing its dependency lifecycle rejected because it disrupts concurrent ownership. F00 implements foundation only; Next.js/React/TS shell deferred to F01, typed client to F02. No framework dependencies selected/installed in F00.
Read current contracts instead of frozen B19 OpenAPI: concurrent ownership work already added routes. Captured 58operations/55paths/182schemas and four SHA256 fingerprints. Read-only checker validates route identities and referenced request/response/query schema existence and detects any source drift; explicit --record requires impact review, never automatic acceptance. Static fingerprints do not prove UI or runtime compatibility. Proxy/auth/SSE/approval semantics documented for later implementation; not claimed implemented.


## DEC-067 — explicit reviewed synthetic responsibility (B20-R-OWNERSHIP,2026-10-18)
Pre-edit authority/provenance/risk/tests in B20R-OWNERSHIP-PLAN.md. Reuse existing Evidence/MAINTAINED_BY/DomainEvent/0005companions and writer fence; add no ontology, migration, role or storage subsystem. DEPARTMENT_LEAD attests only its own department's synthetic inventory source/record/version and effective interval; distinct ANALYST independently reviews immutable source hash with explicit consent. ADMIN/APPROVER cannot submit/review or gain execution bypass. Source and reviewer identities resolved from existing Auth, not input labels.

Candidate and verified ownership occupy distinct cardinality tiers: immutable unaccepted claims cannot block explicit reviewed responsibility, while overlaps within accepted VERIFIED intervals reject. Other B03 relationship policies unchanged. Alternative candidate promotion/deletion would destroy provenance; choosing newest owner or expanding to ownership administration/revocation would violate scope. Therefore append immutable source/review/relationship records only, permit explicit half-open succession, reject open-ended overlap. Staged source support is restricted to MAINTAINED_BY with validated responsibility review evidence; existing causal/source checks retained. Existing0005 readiness required;0001–0005bytes unchanged.

Draft owner proof records edge/evidence hashes; operations compare persisted proof IDs/hashes before new approval/work, preserving compatible older ID-only proof bindings. Reads/Views must select one verified owner before candidate context; otherwise candidate+reviewed rows duplicate a department and break legacy scopes. Candidate-only owner field stays absent; no unrelated frontend/filter redesign. Same-department successor still requires revised plan/approval; old hashes/checkpoints unchanged.

101distinctfocused testsPASS(100unit/1realsharedjourney),2finalSPECvalidatorsPASS,14guards0providers. One unit timestamp expectation corrected,2setup timeouts retained. Final new fixture uses accepted bounded socket setting10seconds only in test environment, no production/.env/query/broker change. Real commit/readback fault retains one responsibility and UNKNOWN/DISPATCHING/no redispatch. No automatic recovery or other B20 corrective feature. Full B20PARTIAL/BLOCKED; B10genuineOPEN/PARTIAL. STOPhumanreview.


### B20-R-OWNERSHIP final preservation/security evidence
Read-only auditPASS:1581pre-task public files retained,1129earlier evidence files byte-identical,119accepted test files unchanged; allsix tracker histories append-only. Original migrations0001–0005/schema registry/city/scenario/evaluator data/dependency files unchanged. B04fullcityhash/858nodes/1246edges/42candidate drainage links, B01probe, B12R2singleplan/quarantine and B19quarantines retained; original candidate/source/submission and draft/receipt/checkpoint hashes intact. Historical2paidrequests exactly unchanged;14guards0external/0unexpected; public-artifact/patchprivate-value scanPASS. ActualFalkorDB6.0.2/Redis8.10.2 and pinnedpackageversions recorded in audit; no dependency changes.

Two audit utility bookkeeping stops retained separately (missing authorized CLI path in allowlist, then concurrentnewfrontend additions). Corrected the task allowlist/exclusion; no application/evidence/data repair. Seven concurrentfrontend files were not created/edited/executed by this task, preserved and excluded from ownership patch/inventory; hashes recorded separately. No frontend work performed here. Final task101distinctPASS100unit/1real,0unresolvedFAIL/0SKIP; full B20PARTIAL/BLOCKED, B10genuineOPEN/PARTIAL. STOPforhumanreview; proposed next B20-R-UTILITY only after separateauthorization, noB21/live/frontend.


## CURRENT B20-R-UTILITY — technically passing; human review pending (2026-10-18)
B20-R-OWNERSHIP is human accepted. Implemented only closed synthetic UTILITY_ISOLATION/UTILITY_LEAK_REPAIR with typed future ISOLATION_PROOF/UTILITY_VERIFICATION dependencies over existing B12–B14 services. Reviewed pipe causal+safety evidence, current independently acquired verified ownership, current D022 PROPOSED procedure, exact approval and assigned operator remain mandatory. Existing B05 verified-only bounded traversal scopes road dependency; no B09 allowlist weakening. Immutable approved prerequisites are fulfilled from persisted attributable independently reviewed completion/follow-up proof, not task/DAG status.

Actual real S04 primary: ownership→sourced approved WATER isolation→reviewed isolation proof→WATER repair→independent UTILITY_VERIFIED→separately sourced/qualified ROAD repair completed. Three completed work orders; plan MONITORING, incident not ENDED, case_closed=false. Utility component outcome never substitutes for road pavement/wear verification. Negative normal-pressure S04 contradicts leak and refuses utility work,0plans/0orders. Additional safety/road surveys are explicit new synthetic observations; original B19 claims/candidate/source bytes retained. D022 author/self-review and PROPOSED authority honest; no physical engineering standard asserted.

Actual committed utility follow-up report plus injected readback ValueError returns409RECOVERY_REQUIRED/UNKNOWN; original request/work/plan/correlation IDs retained, one durable report, exact replay no redispatch, transport intentDISPATCHING. No retry/delete/new version/replacement key/rollback/quarantine clearance. Operator must inspect original domain operation/journal/evidence and obtain supported reconciliation review; safe status reads do not clear intent.

Final75distinctPASS=38newutility+35directcompatibilityunits+2realS04cases;0unresolvedFAIL/0SKIP/0setupERROR. Both specification validatorsPASS once after final source edits. Historical13failedtestexecutions retained:10unit frozen-model fixture errors,3primary failures (B09 read-family restriction twice, then unsupported ProofPath field); corrected without graph repair. Final real primaryPASS27.37s, initial negativePASS retained; passing journey rerun only for final changed completion boundary/road proof, no broad/lifecycle/live tests. Explicit synthetic commands, real DB/GraphRAG SDK/HTTP/CLI; no fake or autonomous model claimed. MCP/Saver unchanged/not rerun. Provider interlocks and children0external/0unexpected; historical paid accounting retained.

Evidence: docs/evidence/B20R-UTILITY-RESULTS.md, COMMANDS.md, FILES.md, changes.patch, primary-proof.json, negative-proof.json, audit.json and WALKTHROUGH.md; operator design backend/UTILITY.md. Old migrations/schema/source/city/earlier evidence/quarantines preserved. BLOCK-B20-02 technically addressed pending this review; BLOCK-B20-03..05 remainOPEN. Full B20PARTIAL/BLOCKED and B10genuineOPEN/PARTIAL. No B21/frontend/other corrective phase/live authorization. STOPforhumanreview; exact next task is review B20-R-UTILITY and separately authorize one remaining B20 correction.

### DEC-068 — utility component proof, compatible closed extension
Alternative status-only DAG rejected: task completion cannot prove isolation or resolution. Reuse existing fenced0005 operation/inspection/completion/verification/outcome companions rather than new storage/migrations. Add typed UNMET future gates with exact predecessor identity; revalidate persisted target/operator/citation/review/time/hash proofs at order/assignment/START. Retain old two-condition/hash normalization and old B14-2 outcome semantics. Utility component evaluation during IN_EXECUTION avoids blocking the road dependency on all-tasks-completed monitoring; UTILITY_VERIFIED is MITIGATION_VERIFIED for the component only, case_closedfalse. Isolation cannot independently evaluate/close a case. Closed field codes are qualitative synthetic checks, no numeric units. Additional road survey is explicit; no mandatory road repair without own support. Dependency topology uses actual B05 ProofPath.edge_ids + validated EdgeRecord.kind/directions; no assumed edge_types API. No dependencies or package versions changed. D022 is separately ingested, source REVIEWED means disclosed automated author self-review; canonical procedure remainsPROPOSED. New fields documented in contracts/resolution_planning.json, operations.json and generated api_models.json; no endpoint/CLI inventory change.


### B20-R-UTILITY final read-only retention/security evidence
AuditPASS: all1642pre-task public files retained;1176earlier evidence files byte-identical;121accepted test files unchanged; allsix tracker histories append-only. Migrations0001–0005/schema registry/city/scenarios/dependencies unchanged. Original B04fullcityhash/858nodes/1246edges/42candidate drainage links and B01probe retained;12previous B20scenario checkpoints, B12R2singleplan/quarantine, B19quarantines, accepted OWNERSHIP sources/checkpoints and UNKNOWN intent retained. Utility graph retains3COMPLETEDorders, MONITORINGplan, UTILITY_VERIFIEDcomponent with case_closedfalse, one actual COMMITTEDreport and original UNKNOWNtransportintent. Historical2paidrequests unchanged/no active sessions or holds;11provider reports0external/0unexpected; publicartifact/patchprivate-value scanPASS. ActualFalkorDB6.0.2/Redis8.10.2, existing pinnedpackages recorded in audit; no dependency changes. FullB20PARTIAL/BLOCKED; STOPforhumanreview.


## CURRENT B20-R-UTILITY-R — technically passing; human review pending (2026-10-18)
Only the road/utility binding correction is implemented. AllR01–R18 remain binding; directly protects R04/R05/R09/R10/R11/R17/R18. planning/utility.py now rejects more than one utility-repair task linked through existing bounded verified-only UNDERLIES topology to any road-task target, with stable sanitized UTILITY_MULTIPLE_REPAIR_PREDECESSORS. With exactly one linked task, UTILITY_VERIFICATION and depends_on must identify that exact task, and all road targets must be covered. No linked repair preserves existing independently qualified road behavior. Duplicate references/unsupported shapes remain rejected. No prerequisite schema expansion, default/hash/migration/storage/approval/recovery change.

Existing Operations.validate reuses this same remediation policy with current Reader/B05 topology before new order/assignment/START authority. Fresh topology cannot select one of several predecessors. Multiple relevant tasks are unsupported under the single-predecessor contract; do not omit repairs or treat approval as a workaround. Historical draft/receipt/approval bytes untouched; no graph repair/retry/quarantine clearance.

Focused final53distinctPASS=52utilityunits(38accepted+14new)+1realS04PRIMARY;0unresolvedFAIL/0SKIP. Actual schema-valid two-distinct-pipe draft with sourced verified UNDERLIES→same road rejected by real planning/API before0plans/0draftcompanions/0workorders. Existing actual isolation→reviewedproof→repair→independentUTILITY_VERIFIED→justifiedroadcompletion and committed-readbackUNKNOWN/no-redispatch assertions retained/passed. Utility remains component-only; planMONITORING/caseopen. No unchangedNEGATIVE or35earliercompatibilityunits/broad/lifecycle/live rerun. No model solver/MCP/Saver changes or claim. Both final specification validatorsPASS;0externalGemini/countTokens in ordinarypytest/children. Review reproduction retained3FAIL/7PASS/41deselected before fix; one realfixtureFAIL missing mandatoryupdated_at retained/corrected in new fixture, failed graph not repaired; finalrealPASS29.47s.

Allsix histories appended. New evidence docs/evidence/B20R-UTILITY-R-RESULTS.md, COMMANDS.md, FILES.md, changes.patch, primary-proof.json, review-repro.txt and retention.json; single-predecessor limit documented backend/UTILITY.md and contracts/resolution_planning.json. Earlier utility evidence/tests/assertions/data/accounting/quarantines preserved. FullB20 remainsPARTIAL/BLOCKED for remaining capacity/route/dumping/chronology corrections; B10genuineOPEN/PARTIAL. STOPforhumanreview; exact nexttask is reviewB20-R-UTILITY-R, then separately authorize further work. NoB21/frontend/otherB20/live authorization.

### DEC-069 — fail closed on multiple road utility predecessors
The existing condition holds one depends_on_task_id and duplicate kinds are forbidden. Selecting the first linked repair can omit required utility work. Reject multiple linked repair tasks across the union of road targets instead of expanding schemas or rewriting historical bindings. Exactly-one requires identity equality to the discovered task before target-coverage checks. Stable sanitized blocker UTILITY_MULTIPLE_REPAIR_PREDECESSORS is a domain PlanningBlocked code; the existing HTTP envelope remains sanitized409DEPENDENCY_BLOCKED, without exposing raw exceptions or topology contents. No route/error-schema expansion. Existing order/update/START source revalidation calls the corrected policy; frozen source/hash/owner/safety/independent-verification rules remain. No package/runtime versions changed.


### B20-R-UTILITY-R final retention evidence
Read-only auditPASS: 1685pre-task public files retained;1212earlier evidence files byte-identical;121other accepted test files unchanged, only two authorized utility test extensions. Six histories append-only. Original migrations/schema/city858nodes1246edges42candidate drains, B01probe,12B20checkpoints, B12R2/B19quarantines, accepted ownership/utility records and UNKNOWNintents retained. Historical2paidrequests/no active sessions or holds unchanged. 7interlock reports0external/0unexpected; publicartifact/patchsecret scanPASS. ActualFalkorDB6.0.2/Redis8.10.2; no dependency changes. Final53distinctPASS52unit/1real,0unresolvedFAIL/0SKIP. STOPforreview; fullB20PARTIAL/BLOCKED/B10genuineOPEN/PARTIAL.


## F01 — frontend shell and agreed essential scope (2026-10-18)
Human accepted a clean application rather than a judge-guided presentation. Choose two main destinations (Overview/Investigations) and in-case report/investigation/evidence/plan/work/monitoring-memory sections; standalone explorer/library/analytics deferred. Preserve all18requirements. Frontend-only Next16.4.2/React19.3.1/TypeScript7.0.2 exact pins + own lockfile after actual production/type smoke PASS, Node24.21.0/npm12.2.0. Alternative custom graph implementation deferred in favour of official Canvas evaluation at F04 per human direction; https://docs.falkordb.com/browser/canvas reviewed, no package/runtime compatibility claim yet. F01 deliberately implements no API client. Current api_models drift reviewed (current ownership schema and route identities; no consumers exist in shell);58operations/55paths/182schemas baseline explicitly refreshed without backend edits. Planned client-only graph mapping must preserve provenance, candidate/verified styles, actual recorded paths and accessible evidence narrative. Dependency/network failures corrected with approved frontend-only install; no backend lifecycle change.

### B20-R-SERVICE-EVIDENCE pre-edit compatibility refinement
Inspecting accepted B12/B14 fixtures shows generic reviewed field evidence uses rule2 without a canonical service-log writer. This correction is specifically S05/S06 controller service chronology, so rule3 is selected by the existing hashed demo/current investigation binding (S05/S06), not by caller labels or generic cause alone. Other investigations retain rule2 and its qualified observation semantics; rule2 does not establish pickup-before-later-deposit history. Stored rule1/2 histories are not rewritten. This avoids redesigning every historical evidence/execution path while requiring actual service provenance for the authorized S05/S06 correction. Missing service records in that controlled scope remain insufficient. Existing B14 monitoring stays unchanged. Initial real failures exposed an exact semantic-version2 coupling and a test assumption that an empty bounded MCP history returns SUCCESS; actual PARTIAL-with-gaps is retained, never replaced with fake success.


## CURRENT B20-R-SERVICE-EVIDENCE — technically passing; human review pending (2026-10-18)
Ownership and utility/dependency correction are human accepted. Implemented only dated S05/S06 controller evidence: canonical PickupExecution/PICKUP_FOR, specific synthetic service-log due/actual/checked/recorded times, attributed reviewed source and actual route/point references; separate lifecycle-valid field/deposit report. Candidate recurring schedules/routes/owners and original runtime-v1 definitions remain unchanged. UNKNOWN service creates no execution; explicit MISSED has no actual_at. No quantities invented. No capacity/route/dumping intervention, plan, approval or resolution manufactured.

Controller-only writes reuse existing0005 fenced Storage, hashed provenance/receipt, durable native event and source-bound HTTP recovery; no generic ledger/endpoint/migration/role/dependency. Rule3 is scoped by hashed demo/current S05/S06 investigation binding for new missed-pickup/dumping assessments. It validates source/target/route/report/journal/native hashes and strict pickup-before-deposit timing, not labels, codes, record counts or equal dates. Generic rule2 semantics and old rule1/2 assessment bytes retained; rule2 is not service chronology. B14-2 monitoring unchanged. Validated source DTO adds optional service_record to existing evidence API/CLI; actual MCP pickup history retains PARTIAL/gaps and current provenance checks. Runtime/agent reads cannot access the new controller packet.

Final43distinctPASS=37newfocusedunits+2directAPI/CLI-schema compatibilityunits+4realS05/S06PRIMARY/NEGATIVE.0unresolvedFAIL/0SKIP. Final focused39PASS3.62s; shared four-realPASS99.74s; only affected uncertain S06NEGATIVE recheckedPASS26.76s after removing unnecessary duplicate-source probe from uncertain path. Both finalSPECvalidatorsPASS once. Historical9failedtestexecutions retained:1unit expectation about parse-only body vs bound state,4real exact version2 coupling,4real incorrect SUCCESS-only assumption for actual PARTIAL history. Failed graphs never repaired. Explicit authored synthetic facts, actual FalkorDB/SDK/HTTP ASGI/CLI/runtime MCP; no model solver or live provider.

S05PRIMARY actual MISSED→qualified MISSED_PICKUP SUPPORTED; capacity observation remains separate SUPPORTED, no capacity intervention. S05NEGATIVE UNKNOWN/no execution→INCONCLUSIVE. S06PRIMARY actual pickup11:59Z→separate deposit12:00Z→ILLEGAL_DUMPING SUPPORTED/MISSED_PICKUP CONTRADICTED. S06NEGATIVE completion only→dumpingINCONCLUSIVE. No independently VERIFIED root cause or resolution asserted. Actual service-commit+injected readback ValueError returns409RECOVERY_REQUIRED/UNKNOWN; one execution/source retained, exact original HTTP replay no redispatch, intent/demo reservation remainDISPATCHING. No retry/replacementkey/delete/rollback/clearance; original IDs and committed report/source/event support human reconciliation only.

Evidence/guidance: backend/SERVICE_EVIDENCE.md; docs/evidence/B20R-SERVICE-EVIDENCE-RESULTS.md/COMMANDS.md/FILES.md/changes.patch/WALKTHROUGH.md and fourdated proofs/retention.json. Allsix logs append-only; earlier artifacts/data/approvals/accounting/quarantines retained; ordinarypytest/children0externalGemini/countTokens. BLOCK-B20-05 technically addressed pending human review, fullB20PARTIAL/BLOCKED for capacity/route/dumping interventions; B10genuineOPEN/PARTIAL. NoB21/frontend/live authorization. Exactnext: human reviewB20-R-SERVICE-EVIDENCE, then separately authorize further work. STOP.

### DEC-070 — specific service occurrence, compatible rule3 and controller-only write
Reuse canonical PickupExecution rather than narrative completion or a parallel ledger. No existing runtime execution writer existed. Narrow S05/S06 release compiles typed SERVICE_EXECUTION_SOURCE + optional canonical execution/PICKUP_FOR + hashed source/report/native/receipt companion + native event under existing0005 fence. The staged source exception in Storage is restricted to PICKUP_FOR and validates typed source/pickup/target/route before preserving original B03 policy checks; no arbitrary write Cypher or general staged verified-source relaxation. Report commits through original B09 before the service batch; later uncertainty is not rollback and retains original intent/reservation/records. Readback/recovery failures remain UNKNOWN through existing HTTP boundary.

Explicit synthetic log occurrence is earlier than recording, separate from the current inspection; no inspection is backdated. Specific due occurrence attestation is not promotion of a candidate recurring schedule. UNKNOWN cannot produce a canonical execution; MISSED requires explicit reviewed result and has no actual_at. Qualitative capacity remains separate, no invented quantities. Source/reviewer authority derives from authenticated B19 field/analyst plus validated B09 journal and hashed state; caller labels cannot grant it. Safe readers revalidate source/native/relationship/report scope. Format2 accepts rule3 only for admitted service causes; existing rule1/2 retained. Controller scope selects rule3, generic workflows retain rule2 without service-order inference. A single log/report is qualified support, never sufficient independent cause verification or resolution. No migration/package/role/route/CLI-command changes; compatible optional typed evidence.service_record requires future client type regeneration, no frontend work here.


### B20-R-SERVICE-EVIDENCE final compatibility verification
CURRENT final45distinctPASS=39newunit+2directcompatibilityunit+4real,0unresolvedFAIL/0SKIP. Two final unit cases ensure optionalservice_record is omitted when absent, preserving legacy EvidenceDTO/DONE replay response shape; populated sources unchanged from actual runtime proof. Focused final41PASS; actual duration in focused-final.txt. Both finalSPEC validatorsPASS after finalsource edit. Earlier43-case summary is superseded by this45-case total, not additional runtime journeys. Duplicate generated static-check blocks removed and JSON formatting minimized; no behavior/schema-name change. No real journeys repeated for documentation/legacy-null serialization-only edits. All earlier evidence preserved; fullB20/B10 genuine gates remain open.


## F02 — automatic judge entry with authenticated typed transport (2026-10-18)
F01 accepted; human explicitly rejected a sign-in panel. Implement server-only presenter-configured existing OP-ANALYST login, temporary browser-memory token, authenticated /auth/me identity check, expiry/logout/reconnect; no ADMIN/APPROVER default or bypass. Alternatives public unauthenticated backend or browser-embedded password rejected because existing auth/state machines remain binding. No human approval/work/agent execution occurs on entry. F02 planning/scope correction recorded before auth implementation in frontend/docs/evidence/F02-plan.md.
Generate183models/58routes from current machinecontracts using pinned json-schema-to-typescript16.0.0; validate requests/query/response via ajv8.20.0 (no coercion/default insertion/field removal). Existing Next16.4.2/React19.3.1/TS7.0.2 unchanged. Exact pins+frontend lockfile after actual build/type/runtime smoke. Contract drift183vs182 reviewed/generated/runtimeconsumedparity, frontend baseline only updated. Local loopbackproxy allowlist; originalHost vs Next internal localhost normalization fixed with regression, forwardedHost ignored; no redirect/cookies/caller-origin selector. Wrap global browser fetch rather than invoking native fetch with a class receiver. Late responses/logout cannot erase replacement sessions; uncertain writes preserve original key and never retry automatically. No domain/schema/backend edits. Detailed failures/alternatives/commands and current limits in frontend/docs/evidence/F02-results.md; next F03 only after review.


### B20-R-SERVICE-EVIDENCE final read-only preservation
AuditPASS: all1728pre-task public files retained;1236earlier evidence files byte-identical;123accepted test files unchanged. Allsix histories append-only. Original registries/migrations0001–0005/city858nodes1246edges42candidate drains, runtime-v1 definitions, B01probe,12previousB20checkpoints, B12R2/B19quarantines and accepted ownership/utility records/UNKNOWNintents retained. Newfourvariant service source/report/native/candidate/oldassessment integrityPASS; uncertain intent+release reservationDISPATCHING retained. Historical2paidrequests/noactive sessions or holds unchanged. 12interlockreports0external/0unexpected; final publicartifact/patchprivate-value scanPASS. ActualFalkorDB6.0.2/Redis8.10.2 and pinnedpackages recorded, no version changes. Final45distinctPASS41unit/4real;0unresolvedFAIL/0SKIP. FullB20PARTIAL/BLOCKED/B10genuineOPEN/PARTIAL; STOPforhumanreview.

## F03 — real overview reads, category filters, case lists and selection (2026-10-18)
F02 accepted. Scope: R01, R16; preserving R01–R18 and explainability R15.
- Implemented real API-backed Overview: four backend metrics (`active_investigations`, `pending_approvals`, `completed_work_orders`, `verified_work_orders`), active incident counts and recurrent cluster counts across all three issue categories (`WATERLOGGING`, `ROAD_DAMAGE`, `WASTE_ACCUMULATION`), metadata bar with `as_of` and `graph_revision`, and collapsible backend metric definitions and data limitations.
- Case directory & selection: Registered demo investigations from scenario catalog (`GET /api/v1/demo/scenarios`), filtering out `NOT_STARTED` scenarios. Reported incidents from `GET /api/v1/incidents` with server cursor-based pagination. Selected case loads `InvestigationDTO` and linked incidents, or standalone incident with explicit disclaimer notice of the current API listing gap.
- Safety & correctness: `LatestRead` (AbortController) cancels inflight requests on query/filter changes to prevent stale publication. Session changes immediately clear read state. Selecting a stage does not advance backend state. Closed schema validation on responses; mismatches fail closed with `CONTRACT_MISMATCH` or `SELECTION_MISMATCH`.
- Executed checks: 40 offline tests PASS (30 transport + 10 cases), 0 fail, 0 skip; typecheck PASS; production build PASS; root specification validators PASS; real isolated HTTP/FastAPI/FalkorDB integration PASS (`F03-integration.json`).
- Next: F04 official `@falkordb/canvas` integration and investigation studio.



## FRONTEND-BACKEND-DEMO — PARTIAL, focused review (2026-10-18)
Human reprioritized backend alongside Antigravity frontend. R01–R18 remain binding; no B-END/B10/B20 completion claim. Real Gemini/MCP/FalkorDB/Saver waterlogging investigation reached sourced DRAFT and HUMAN_REVIEW (3 recorded graph paths), not approval or resolution. Road/waste live paths paused; all original and new recovery records retained. User explicitly declined blocked-waste reconciliation. Scoped claiming, source-write fence, host preflight/live controls, field release/readback, unknown-write stop, truthful tool catalog with exact legacy hash compatibility, actionable draft feedback and additive authenticated GET /investigations implemented. API running localhost:8010; frontend untouched.
109 focused unit PASS + 1 real isolated integration PASS; actual localhost category/dashboard HTTP and SSE PASS; both specification validators PASS. Intentional live accounting $0.39389925 across five distinct cases; all settled, zero open sessions/holds, caps unchanged. Ordinary tests sent zero external requests. Retained harness/live failures and no baseline preservation limitation documented in docs/evidence/FRONTEND-BACKEND-DEMO-RESULTS.md. Flow: authenticated frontend→HTTP scoped reads/SSE→FalkorDB/Saver projections; explicit host wake→selected case delivery→serialized source/MCP→Gemini selection→validated domain write→checkpoint/durable event→discover→SSE. Private credentials never enter browser/public evidence. Exact next: frontend water-case rehearsal; clean road/waste contract rehearsal only after authorization, no blocked-record reconciliation. Stop for review.

## F04 — Investigation Studio: Hypotheses, Evidence/Citations, FalkorDB Graph & Decision Links (2026-10-18)
F03 accepted. Scope: R02, R06, R07, R15, R16; preserving R01–R18 and explainability invariants.
- Official FalkorDB Canvas integration: Installed `@falkordb/canvas` (0.3.3) in frontend. Implemented client-only React wrapper `FalkorDBCanvasView` mounting `<falkordb-canvas>` with Pan, Zoom, Fit controls, layout switcher (`force`, `tree`, `radial`), and slide-over Inspector Drawer for node and edge properties and temporal provenance. Styled verified associations (solid teal) vs candidate/unverified associations (dashed amber) with decision-path highlighting. Provided accessible keyboard/screen-reader tabular fallback.
- Graph model & decision traces (`lib/read/graph.ts`): Bounded mapping of `GraphSubgraphDTO` to Canvas nodes/links. Extracted 3-part trace connecting Question Asked → FalkorDB Graph Evidence → Recorded Decision. Implemented strict causal attribution guarantee: categorized steps into `MODEL_SELECTED_PATH` (explicit backend path bound), `CONTEXTUAL_GRAPH_QUERY` (contextual read without isolated path), or `UNESTABLISHED_INFLUENCE` (*"Graph query executed as contextual background; no causal influence trace established for this step."*). Never invent graph paths, tool calls, citations, confidence percentages, or agent activity.
- Differential hypotheses (`components/hypotheses-panel.tsx`): Rendered competing hypotheses with cause codes, status tags (`SUPPORTED`, `CONTRADICTED`, `INCONCLUSIVE`), suspected assets, supporting/contradicting evidence chips, missing evidence checklist, and assessment revisions.
- Authoritative evidence inspector (`components/evidence-detail-modal.tsx`): Detailed modal displaying typed evidence attributes, reliability, review attestation, source records, and data limitations.
- Workspace integration: Reactive selection links entity clicks in hypotheses or trace panel directly to Canvas highlight and inspector drawer.
- Executed checks: 45 offline unit tests PASS (30 transport + 10 cases + 5 canvas-adapter); `check:api` PASS; `contracts` baseline PASS (59 operations / 55 paths / 184 schemas); `typecheck` PASS (`tsc --noEmit` zero errors); Next.js production build PASS (Turbopack 4.4s); root specification validators PASS; real isolated HTTP/FalkorDB integration PASS (`F04-integration.json`).
- Next: F05 live update stream and optimistic state synchronization.

## F05 — Authenticated Fetch SSE, Persisted Event Streaming, Cursor Handling & Refetch (2026-10-18)
F04 accepted. Scope: R01, R15, R16; preserving R01–R18 and explainability invariants.
- SSE Proxy & Streaming (`lib/api/proxy.ts`): Allowed `/api/v1/events/stream` through local Next.js proxy, forwarding `Last-Event-ID` header and allowlisted query params `cursor` and `investigation_id`. Streamed response with `Cache-Control: no-cache, no-transform` and `Content-Type: text/event-stream`.
- SSE Client (`lib/api/sse.ts`): Built fetch-based SSE streaming client with chunk parser. Parsed standard frames (`id:`, `event:`, `data:`) and ignored comments (`: heartbeat`, `: reconnect`). Cursor tracking updates `lastEventId` on frame dispatches. Handled 401: calls `onUnauthorized()` and aborts cleanly without infinite loops. Handled 409 (`CURSOR_FUTURE` / `CURSOR_EXPIRED` / `CURSOR_CONFLICT`): resets cursor to `null` and triggers authoritative refetch callback. Handled 30s cycle: triggers authoritative GET sync and reconnects with exponential backoff.
- React Hook & Component (`components/use-event-stream.ts`, `components/live-stream-panel.tsx`): Bounded in-memory event buffer (last 50 events). Integrated into Overview (`app/page.tsx`) and Investigation Workspace (`components/investigation-workspace.tsx`). Prominent architectural notice: *"Persisted event stream over authenticated SSE. Stream events signal state changes; authoritative state is continuously re-synchronized via validated GET endpoints. Zero simulated or fabricated reasoning steps."*
- Executed checks: 52 offline unit tests PASS (30 transport + 10 cases + 5 canvas-adapter + 7 sse); `check:api` PASS; `contracts` baseline PASS (59 operations / 55 paths / 184 schemas); `typecheck` PASS (`tsc --noEmit` zero errors); Next.js production build PASS (Turbopack 3.8s); real isolated HTTP/FastAPI/FalkorDB integration PASS (`F05-integration.json`).
- Next: F06 in-case inspections/plans/approvals/work orders DAG and state machines.




## DEMO-READ-CONTRACT — technically PASS, review pending (2026-10-18)
[x] Authorized next bounded backend demo correction while Antigravity continues frontend. ScopeR01/R04/R06/R07/R08/R09/R13/R15/R16/R18; all18requirements retained. Provider validates discovered READschemas/official cross-field rules/known asset-vs-location/time before tool dispatch; static sanitized feedback uses existing single accounted output correction, no argument rewriting/domain redispatch or budget increase. DEMO-2 prompt version preserved alongside DEMO-1. New presenter rehearsal uses distinct road/waste assets and source-bound responsibility/service policy; priorfivecheckpoints unchanged, no quarantine reconciled.
59unit+2realMCP/FalkorDB/LangGraph/SaverPASS;bothSPECvalidatorsPASS;0externalproviderrequests in ordinary tests. Initial2mock-permit fixture failures corrected without weakening applicationpolicy. Genuine newroad7selections/4reads→inspection (one retained PRECONDITION_FAILED,0recordeddecisionpaths); newwaste8selections/3reads→2INCONCLUSIVEalternatives/2recordedpaths→sanitationinspection.15count+15generationrequestsSETTLED;$0.244815375knowncost,0opensessions/holds,unchangedcaps. Waterdraft/HUMAN_REVIEW intact. Actuallocalhost9HTTPreads200 andwasteSSEPASS. Initialreadbackduringdiscovery409retained;stablepostdiscoveryrepeatPASS.
Flow:GeminiJSON→Selection→discovered-schema+typed/cross-fieldREADvalidator→(oneexistingreservedcorrectionorvalidatedselection)→decisionjournal→MCPbroker→FalkorDB→Saver→durableactivity→SSE. Invalidselectionneverdispatches. Files:backend/app/agents/selection_validation.py,provider.py,prompts/DEMO-2.txt;demo_host/alternatives.py,__main__.py;twofocusedtestfiles;handoff/runbook;docs/evidence/DEMO-READ-CONTRACT-* task-onlypatch/results/proofs. Frontend/APIcontracts untouched. Exactnext:authorized synthetic fieldfulfilment and bounded same-thread reassessment for new pendingroad/wasteinspections. No verifiedcause/approval/work/resolution orfullB10/B20/B-ENDclaim. Stopforreview.


## DEMO-FIELD-REVIEW — technically PASS, human review pending (2026-10-18)
[x] Authorized field fulfilment/same-thread rehearsal plus discovered frontend backend gaps. R01/R04/R06/R07/R08/R09/R10/R11/R13/R14/R15/R16/R17/R18 advanced; all18binding. Two authenticated synthetic field reports+independent waste service provenanceCOMMITTED. Genuine road resume produced SUBGRADE_REPAIR draft; water/road exact analyst HTTP submissions now2PENDINGapprovals,0approval decisions/work. Corrected supervisor's stale inspection request context with scope/provenance-checked current status/report pointers (metadata only; real MCP finding read still required). Waste genuine corrected READ fetched report, then TOKEN_BUDGET380551; host interlock now blocks another retry, no raised cap/hidden new case. Live malformed READ correction observed/accounted before dispatch; no uncertain operation replay.
Added authoritative PlanDTO.task_bindings (local/native scope/dependencies/status/hash/enabled fake assignees) validated against native graph; rejected client-side ID recreation/ambiguous graph inference. Closed schema additive:59operations/55paths/185models; frontend must regenerate. Historical draft hashes preserved; no newroute/migration/frontendcode. Hoststatus now includes real reports/evidence/plans. Backendlistener alone reloaded same8010source/auth.
115distinctunitPASS+1real sourcedDB/B11/HTTP exact-submission/replay/role/payload testPASS;bothSPECvalidatorsPASS;3ordinarytestinterlocks0externalproviderrequests. Initialnew fixture future-citation failure corrected by clock alignment, retained. ActualTCP9detail/trace/graphreads+SSEPASS; currentpacket all200; graphpathcountswater3/road0(contextonly)/waste4. Earlier5checkpoints unchanged including4earlierpausedcases; no quarantine cleared.11count+10generationrequests this taskSETTLED;$0.177408075knownadditionalcost;0opensessions/holds/unknowncharges,unchangedcaps.
Flow:requestedinspection→authenticatedfieldtransitions→attributedreport+independentreview/log→newsourceevents→same-threadfreshMCP→authoritativeassessment→draft→validatednative-taskreadmapping→analystexactscopeSUBMIT→PENDINGhumanreview→durableSSErefetch. No invented resolution. Exact source/inventory/patch/commands/results/approvalscopes in docs/evidence/DEMO-FIELD-REVIEW-*; judgeguide backend/DEMO_WALKTHROUGH.md. Nextdemo step:humanapprove/reject exactpending scopes, then authorizedsimulatedwork/independentoutcome. Nextengineering:contextbudget efficiency +remainingcapacity/route/dumping/liveacceptance. B10/B20/B-END remainPARTIAL;STOPforreview.

## F06 — In-case Inspections, Plans, Approvals & Work Orders (2026-10-18)
F05 accepted. Scope: R12, R13, R14, R15, R16; preserving R01–R18 and municipal role separation invariants.
- Plan DAG & Topological Sequencing (`frontend/lib/read/plans.ts`, `frontend/components/plan-approval-panel.tsx`):
  - Structured remediation plans loaded via `GET /api/v1/investigations/{id}/plans`.
  - Implemented `computeTaskDag` calculating topological levels (tiers) based on prerequisite dependencies (`depends_on_task_ids` / `depends_on`). Discovered roots run in Tier 1; dependent remediations run in subsequent tiers. Cycle detection provided with graceful fallback.
  - Rendered task cards showing target infrastructure assets, assigned department, status tags, and expandable task specifications including causal/safety conditions, sourced procedure citations (`D019_drain_blockage_clearance.md`), expected outcomes, risks, and verification criteria.
  - Linked plan basis hypotheses (addressed vs unaddressed) with recorded agent reasoning.
- Municipal Authorization & Role Controls:
  - Analyst demo session (`OP-ANALYST` / `ANALYST`) can draft and submit plans via `POST /api/v1/plans/{id}/submit-approval` with client-generated `Idempotency-Key` headers and exact SHA-256 plan hashes.
  - Explicit safety invariant callout (R13, R15): analysts cannot self-approve municipal intervention. An independent `APPROVER` role is required for approval decisions (`POST /api/v1/approvals/{id}/decision`).
- Work Orders & Field Inspections (`frontend/components/work-orders-panel.tsx`):
  - Field inspections loaded via `GET /api/v1/inspections/{id}` with status, department, and evidence links directly opening `EvidenceDetailModal`.
  - Work orders loaded via `GET /api/v1/work-orders`. Displays status badges (`AUTHORIZED`, `ASSIGNED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETED`), assigned operators, and blocker alerts.
  - Enforced backend creation guard: work orders cannot exist in draft state; they are created only after exact plan approval.
  - Critical distinction callout: **Work completion is NOT verified resolution**. Physical field task completion records work execution only; long-term resolution requires post-intervention monitoring across relevant conditions (Stage 6 / F07).
- Executed checks: 60 offline unit tests PASS (30 transport + 10 cases + 5 canvas-adapter + 7 sse + 8 plans); `check:api` PASS; `contracts` baseline PASS (59 operations / 55 paths / 185 schemas); `typecheck` PASS (`tsc --noEmit` zero errors); Next.js production build PASS (Turbopack 585ms); real isolated HTTP/FastAPI/FalkorDB integration PASS (`F06-integration.json`).
- Next: F07 in-case monitoring, recurrence and relevant memory/procedure citations.


## DEMO-CONTEXT-BUDGET — technically PASS, live-format acceptance pending (2026-10-18)
[x] Authorized next bounded backend context-budget improvement. ScopeR06/R08/R09/R13/R15/R16;all18binding. Provider-only lossless repeated-value encoding with short wire_ref/wire_values, exact reconstruction, source-tag literal escapes, unknown/cycle/depth fail-closed, plain fallback on size/proxytoken regression. DEMO-3guidance+safeencodingmetadata; oldprompts/context/MCPvalidation/checkpoints unchanged. No summarization, source/hash/contradiction loss, budget reset/capchange or blocked-case resume.
63focusedunit+3realMCP/FalkorDB/SavercasesPASS;providerresponses mocked,0externalGemini/countTokensrequests. BothSPECvalidatorsPASS. Newcapturetest2failedattempts corrected canonicalJSONcomparison/transportrestore; discardedprototypefailedstringordercheck andhelperglobfailure documented. Actual retained3contexts exactroundtrip; fullrequestlocalproxy reductionswater10.95%,road11.60%,waste4.77%,notproviderbilling/livequality.3currentpresentercheckpoints unchanged;ledger0sessions/unknowncharges/unchangedcaps.2pendingapprovals remain;frontend/API unchanged. Flow:runtimeoriginalcontext→losslessproviderwire/check→actualcountTokens/reservation→GeminiJSON→originalcatalogselectionvalidator→realMCP→Saver. Task-onlypatch/files/commands/results/measurement in docs/evidence/DEMO-CONTEXT-BUDGET-*; guide backend/PROVIDER_ACCOUNTING.md. Exactnext:freshboundedread-onlyliveformatcomprehensionsmoke,neverresumeTOKEN_BUDGETwaste;orremaininginterventiongaps afterreview. Humanapproval/authorizedwork stillpending;B10/B20/B-ENDPARTIAL.STOPforreview.

DEMO-CONTEXT-BUDGET final rollout:64unitPASS target (includes plain-default proof),3real integration cases; wire packing explicit opt-in CIVICLY_LLM_CONTEXT_WIRE=false by default pending live semantics acceptance. Existing live/demo private settings unchanged; original plain context remains default.

DEMO-CONTEXT-BUDGET final verified:64unit+3realPASS;bothvalidatorsPASS;defaultplain+explicitpackedtested. APIlistener absent at finalcheck, presenterAPIonly restored same8010source/auth; actual9HTTPreads+SSEPASS.0liveproviderrequests;pendingapprovals and blockedcasesunchanged.


## DEMO-CONTEXT-SMOKE — limited live format PASS, review pending (2026-10-18)
[x] Authorized next backend task. R06/R07/R09/R13/R15/R16;all18binding. Frontendconnection checkedfirst:privateconfig matchespresenter;directlogin200/Nextsession200/frontendincidents200. Userconfirmedworking; transient/stalebanner plausible, exactearlierreferenceunproven. Nofrontendedit/restart.
Presentercontext-smoke isindependentreadonlyprobe usingactualsavedwatercontext+separatediagnosticthread,sourcefence/originalcasecaps,atmost1selection/1MCPread; nonREAD/write/unknown/replaydenied. Genuinegemini-3.8-flash processedpackedcontext→officialnodeREAD DRAIN-101→durableBROKERSUCCESSvalidatedhash/scope.1count+1generation200SETTLED;28893prompt+68candidate=28961tokens;$0.02192475knowncost;0sessions/holds/unknowncharges,capsunchanged. No path/connectivity/causalproof fromnodeREAD. No liveplaincomparison/savingsclaim. Formatremainsoffbydefault.
InitialharnessfailedafterreadbecauseofficialReadResulthasnodomainstatus;fixedexactvalidation/normalization+unitregression. Retainedfailure+selection; no paidretry/MCPredispatch. Freshprocesscontext-smoke-verifyPASSchecksoriginalsource627/checkpointID+hashunchanged,noprobecheckpoint,trace/ledger. Neverworkflowresume,blockedcase/quarantineclearance,fieldwrite,approvaldecision ornewcase.33unitPASS+genuineGoogle/MCP/FalkorDBreadproof;bothSPECvalidatorsPASS;ordinaryinterlock0externalrequests. Sourcepatch/files/commands/receipts in docs/evidence/DEMO-CONTEXT-SMOKE-*; guidesDEMO_HOST/PROVIDER_ACCOUNTING updated. Nextboundedbackenddemo:ownedisolatedgraph-ablationproof,sourcepreserved. Actualpendingapproval/work/outcomegates andfullB10/B20/B-ENDremainopen.STOPforreview.

## F07 — In-case Monitoring, Recurrence & Case Memory Citations (2026-10-18)
F06 accepted. Scope: R12, R14, R16, R17, R18; preserving R01–R18 and untrusted evidence invariants.
- Distinction between Work Completion and Verified Resolution (`frontend/components/monitoring-memory-panel.tsx`, `frontend/components/investigation-workspace.tsx`):
  - Elevated core municipal invariant: physical field completion of work orders does not equal verified civic defect resolution.
  - Verification requires empirical verification policy checks across relevant conditions (e.g. comparable precipitation/traffic/waste collection cycles).
- Problem Cluster Monitoring & Recurrence (`frontend/lib/read/memory.ts`):
  - In-case monitoring loaded via `GET /api/v1/monitoring`. Displays cluster status (`OPEN`, `MONITORING`, `CONTROLLED`, `REOPENED`), verification policy versions, remaining post-intervention validation checks, and outcome evidence references.
  - Problem cluster outcomes loaded via `GET /api/v1/problem-clusters/{id}/outcomes`. Renders verified resolution evaluations, work order attribution, policy versions, simulated status indicators, and closure decisions.
- Municipal Procedures as Untrusted Evidence:
  - Loaded departmental procedures via `GET /api/v1/procedures`.
  - Prominently displays safety invariant: procedures are municipal evidence with an `UNTRUSTED AS INSTRUCTIONS` safety badge, never agent system instructions.
  - Renders owner department IDs (`DEPT-DRAIN`, `DEPT-ROAD`, `DEPT-SAN`, `DEPT-WATER`), SHA-256 integrity digests, citation excerpts, and acknowledged documentation gaps.
- Authoritative Case Memory:
  - Loaded case memory via `GET /api/v1/cases/{id}/memory`. Gracefully handles 409 `DEPENDENCY_BLOCKED` when cases are in-progress and verified closure has not yet occurred, surfacing "Case Memory Pending Verified Closure".
- Executed checks: 65 offline unit tests PASS (30 transport + 10 cases + 5 canvas-adapter + 7 sse + 8 plans + 5 memory); `check:api` PASS; `contracts` baseline PASS (59 operations / 55 paths / 185 schemas); `typecheck` PASS (`tsc --noEmit` zero errors); Next.js production build PASS (Turbopack 619ms); real isolated HTTP/FastAPI/FalkorDB integration PASS (`F07-integration.json`).
- Next: F08 integrated role/scenario journeys, accessibility/responsive checks and frontend handoff.


## EXACT-ROAD-LIFECYCLE — 2026-10-18, technical PASS; human review pending

Human explicitly selected original road incident INC-B08-27a2cb5d89ae9ab9d86f999cf7b50472 and authorized narrowly proved no-effect reconciliation; subsequently approved exact plan PLAN-B12-11e6b8d220e7923a715f5cc0a371b993/v1/hash b0a730059b2339f87b24fa8434fe5f3706f9686d524ba47e746ee0c1f1c78c57 and its three assigned tasks. This single focused demo task advances R02/R04/R06–R17/road R18, preserving all18requirements and broader B10/B20/B-END partial gates.

Real same-thread Gemini/MCP reads created two SUPPORTED assessments and four path proofs, then TOKEN_BUDGET before drafting (375398 cumulative tokens). No raised cap/new wake. Analyst-assisted sourced conditional draft and exact human approval → water isolation/proof → leak repair → independent reviewed utility follow-up UTILITY_VERIFIED (case stays open) → road subgrade repair → MONITORING → separate synthetic wear/pavement follow-up RESOLUTION_VERIFIED → incident ENDED/investigation+plan COMPLETED/cluster CONTROLLED. Three tasks/work orders, five outcomes, own-episode case memory with five source report references. All physical actions explicitly simulated/synthetic; not an autonomous planner or long-term real municipal outcome claim.

45 distinct final units PASS/0FAIL/0SKIP; one real retained-graph TCP HTTP/FalkorDB/GraphRAG/MCP/Gemini/Saver journey (101 execution HTTP calls, not 101 tests), fresh-process/reloaded API readback PASS; both final spec validators PASS. Paid wake 10count/9generation,275638 additional reported tokens,$0.20620095 known cost; cumulative case$0.28464795, retained$0.50cap and no outstanding reservations. Unit/operational verification zero external requests. Historical scope/import harness failures and initially empty own-memory read retained and corrected; no failed/uncertain work-order mutation. 1368 prior evidence files unchanged; original checkpoint/hash/error and all unrelated quarantines retained. Frontend untouched; backend API reloaded only.

Evidence: docs/evidence/EXACT-ROAD-LIFECYCLE-{RESULTS,COMMANDS,FILES}.md, review/execution/monitoring/fresh-readback/audit/accounting/patch. User verify: refresh `/investigations?investigation=INV-B09-b9d4d66e130ed348c4f6a50e9d66a891`, inspect six stages; nonbillable `PYTHONPATH=backend backend/.venv/bin/python scripts/exact_road_lifecycle.py verify`. Expected ENDED/COMPLETED, three orders, five outcomes, one episode memory. Agent trace retains TOKEN_BUDGET/null checkpoint-plan; operational current plan comes from graph. Legacy static runtime_status is not live provenance. Bounded historical search/truncation retained; no fabricated generalized memory lesson. Original waste blocked; other plans remain pending. Next: human review and frontend walkthrough; no automatic B21/live continuation.

Decision: prefer immutable scoped no-effect attestation over deleting a historical error or cloning the incident; prefer an openly analyst-assisted plan over raising the live token cap or disguising deterministic output as model choice. Expose completed seed memory from validated outcome/evidence records rather than inventing a lesson or changing related-case ranking.

## F08 — Integrated Role/Scenario Journeys, Accessibility & Frontend Handoff (2026-10-18)
F07 accepted. Scope: R12, R14, R15, R16, R17, R18; all essential frontend microtasks complete.
- Scenario Journeys (`frontend/components/scenario-journey-guide.tsx`, `frontend/lib/read/journeys.ts`):
  - Created interactive scenario browser covering all 12 pre-seeded municipal scenarios (`S01` to `S12`) across WATERLOGGING, ROAD_DAMAGE, WASTE_ACCUMULATION, and cross-category defect cascades.
  - Category filters, stage status badges, next operator actions, and direct links to registered investigations/incidents.
- Municipal Role Governance & RBAC (`frontend/components/role-governance-modal.tsx`, `frontend/lib/read/roles.ts`):
  - Created interactive modal detailing the 7 municipal operators (`OP-ANALYST`, `OP-APPROVER`, `OP-DRAIN-LEAD`, `OP-ROAD-LEAD`, `OP-WASTE-LEAD`, `OP-WATER-LEAD`, `OP-ADMIN`).
  - Reinforces core governance invariant: no judge sign-in form is required, but authorization boundaries are strictly enforced. Analysts can draft/submit plans, but cannot self-approve municipal intervention.
- Accessibility & Responsive Enhancements:
  - Visible focus indicators (`:focus-visible`), ARIA landmarks/dialogs/roles, screen reader announcements, and mobile-friendly layouts.
- Technical Handoff (`frontend/docs/HANDOFF.md`):
  - Comprehensive architectural guide detailing Next.js App Router, FalkorDB Canvas integration, SSE event/cursor protocol, role boundaries, and reproducible verification steps.
- Executed checks: 70 offline unit tests PASS (30 transport + 10 cases + 5 canvas-adapter + 7 sse + 8 plans + 5 memory + 5 journeys); `check:api` PASS; `contracts` baseline PASS (59 operations / 55 paths / 185 schemas); `typecheck` PASS (`tsc --noEmit` zero errors); Next.js production build PASS (Turbopack 452ms); real isolated HTTP/FastAPI/FalkorDB integration PASS (`F08-integration.json`).
- All essential frontend microtasks F00–F08 are fully complete and verified. Frontend handoff complete.


## GITHUB-PUBLISH — 2026-10-18

Human explicitly authorized upload and selected PUBLIC `krvikash05/Civicly`. Repository publishing only; no application/frontend implementation, provider call, graph reset, or requirement acceptance change. GitHub account authenticated; target absent before creation. Source snapshot includes both backend and separately developed frontend. Existing `.gitignore` rules exclude `.env`, frontend `.env.local`, `.runtime`, dependencies/build artifacts and archives. Scan of 2000 candidate files (69.21 MiB), 2137 historical blobs and 10 locally configured credential values found zero secret-pattern/exact-secret matches and zero private/generated upload candidates. This is a focused check, not a guarantee against every possible sensitive value. Existing history retained. Repository-local author uses GitHub noreply email. No fresh runtime/regression tests required for upload-only operation; prior application evidence retained. Upload success and GitHub URL must be confirmed by actual push/readback, not inferred from preparation. README remains editable in later commits. Next: review the public repository and, if desired, prepare a concise judge-facing README.

## DEMO-CONNECTION-RESTORE — 2026-10-18

Reported frontend DEMO_UNAVAILABLE reproduced: private frontend/host connection configuration matched, but API8010 connection refused and no backend process existed. Restored same host-rehearsal02.json API as detached PID33196 with private appended runtime log; frontend process/files untouched, no graph reset, no agent wake or Gemini calls. Six real checks PASS: backend live/ready, frontend demo-session+authenticated dashboard proxy for localhost and127.0.0.1 (allHTTP200). Diagnostic sessions logged out. Initial host Python lacked httpx; reran with installed backend virtualenv, no application failure. No application source/contract change or regression tests warranted for runtime restart. Evidence docs/evidence/DEMO-CONNECTION-RESTORE-runtime.json. Human verify: refresh localhost3100 and reopen original road case. Remaining full acceptance gaps unchanged. GitHub publish remains stopped; existing remote empty at last confirmed readback, no further push performed. Next: human frontend demo review.


## AWS-DEPLOY — deployment preparation (2026-10-18)
Human explicitly requested deployment of the current Civicly demo to AWS, selected ap-southeast-2/new AWS experience, temporary hostname and HIGH guidance. Treat this as one scoped deployment task, not acceptance of remaining B21–B-END work. Preserve current uncommitted frontend work and all retained cases. R04/R07/R12–R16/R18 deployment continuity; all18 remain binding. Files planned: deploy/aws/*, scripts/aws_demo_snapshot.py, narrow frontend public-origin guard/routes/tests/env example, five tracking files/task board. Risks: local-only origin guards, absolute private profile paths, Redis ACLs not persisted with graph data, SQLite consistent backups, retained quarantine/ledger continuity, ARM/x86 image support, public analyst access and credit depletion. Tests: both spec validators, full frontend offline suite/typecheck/build, real snapshot/restore into isolated FalkorDB, authenticated dashboard/graph/trace/memory/SSE readback, cloud readiness and restart continuity. No paid Gemini wake or automatic original-case retry. Human verifies actual HTTPS workspace and known partial gates.
Decision: use ordinary EC2 with Docker FalkorDB + host services rather than Launch with AWS migration: this custom stateful Python/MCP/GraphRAG application is outside that skill’s static-export/platform patterns; migration to AWS Blocks would change required runtime boundaries. The pinned FalkorDB index supports both linux/arm64 and linux/amd64 (actual imagetools inspect). Candidate c7i-flex.large 4GiB is Free-plan-eligible; t4g.medium is not. Existing local DB ~2.184GiB including review namespaces; migrate only exact presenter source/checkpoint/memory/trace and associated durable keys. No graph reset or lost uncertainty markers. AWS MCP read checks confirm FREE/ACTIVE,100USDcredit, noEC2instances, existing public defaultVPC. Launch requires presenting final configuration/cost first per retrieved EC2 launch skill.


## AWS-DEPLOY — 2026-10-18

Human approved the exact c7i-flex.large / encrypted30GB / Sydney / temporaryHTTPS configuration at about$2.87/day beforecredits. Use SSM, not publicSSH; temporarydeploymentrole can GetObject only the exact privatearchive. Instance i-00e332036cd609ff0 / public13.55.205.208 launched with idempotentClientToken,IMDSv2 andterminationprotection. No paidplanupgrade or modelwake. Uploaded private14,398,917-byte bundle (source2013files + snapshot04) into encryptedpublicblockedS3; no secrets inuser-data or SSMparameters. Server downloads through its instance role. Bootstrap completed on Ubuntu24.04; application install is pending real verification. HIGH guidance retained for this task.


### AWS-DEPLOY final verification — 2026-10-18

Cloud deployment verified: https://civicly-13-55-205-208.sslip.io, instance i-00e332036cd609ff0/Sydney, human-approved4GiB/30GB encrypted configuration. Public acceptance12checks PASS and same12checks PASS after full EC2reboot; real readback has COMPLETED roadcase,61graphnodes,one retained memoryepisode,procedures and actualSSEframe. Browser confirmsDemoConnected andeventcursor52. APIready:graph/delivery/MCP/checkpoint/memory/auth allready; supervisedservices recoverautomatically. Node22.23.3/Python3.12.3/Docker29.9.1/Compose5.6.0/Caddy2.6.2; pinnedFalkorDB6.0.2 amd64. Initialcompilerfailure fixed withbuild-essential/pythonheaders; firstpublicSSEbodytimeout fixed withuncompressedupstream andSSEexcludedCaddyencoding. RedisACLfile persisted beforecontainerrecreation; fullreboot retainsread/checkpoint/memory/trace accounts. InitialMCPsmoke assertion expectedSUCCESS butgotvalidPARTIAL; correctedrequirement preservesPARTIAL with3validatedcitations. Officialnode1row anddomainprocedureactualMCPreadPASS,catalog16tools; operatorselection,notLLM. ZeroGemini/countTokens/paidworkerstarts. TemporaryS3archive/bucket andexactobjectrolepolicy removed;localprivateartifacts retained. Existingapproval/quarantine/tokenlimits andB10/B20/B-ENDgaps unchanged. Deploymenttask technicallyPASS;humanreviewpending.
Decisions: persist exact ACLs in an ACL file on the existing encrypted data volume rather than reprovision unrestricted accounts at API startup; retain the application’s bounded PARTIAL procedure status instead of changing retrieval semantics. Compression belongs at Caddy with SSE excluded. Current limits are a hosted retained demonstrator and explicit live authorization, not an autonomous always-on agent.

## F09-READABILITY — Human-Readable Display Nomenclature & Machine Code Elimination (2026-10-19)
- Scope: R01, R04, R07, R10, R11, R12, R14, R16, R17, R18; user request to eliminate confusing machine IDs, 32-character hex hashes, and raw uppercase code tokens across the entire Civicly frontend.
- Working Philosophy & Constraints: Work strictly in `frontend/` only. No backend modifications, no schema changes, no contract mutations, no weakening of authorization or audit hash verification. Canonical IDs remain 100% available with copy buttons in expandable `<TechnicalDetails>`.
- Decision & Implementations:
  1. Case Directory (`frontend/components/case-directory.tsx`, `frontend/lib/read/cases.ts`):
     - Added `scenarioTitle` from catalog.json scenarios (`SCENARIO_TITLES`) so cards display human-readable scenario names (e.g. "Market waste demand plus missed pickup") as primary titles instead of raw 32-character hex hashes like `Investigation Case B09-a2fe3dbdecd03984033026c4d0856295`.
     - Shortened case references to `#B09-a2fe3d` (6-char hash) and fixed incident title spacing: `Waste accumulation Incident (#B08-15be20)`.
     - Translated incident locations with `translateLocation` (e.g. `LOC-WASTE-DEMO-DUMPING` -> "Commercial Waste Disposal Zone").
  2. Investigation Workspace & Reports (`frontend/components/investigation-workspace.tsx`):
     - Shortened case reference in header: `Case reference: #B09-95e00a`.
     - Translated Problem Cluster to "Active recurrence cluster (#B08-60be41)".
     - Translated Next required action with `translateNextAction`: "DURABLE_WORKER_OR_HUMAN_REVIEW" -> "Supervisory review or field action pending".
     - In Stage 0 Linked Incidents: replaced raw `INC-...` header with "Citizen Incident Report #1", translated locations with `translateLocation`, and formatted complaint IDs as "Citizen complaints: Complaint #B08-282585".
  3. Hypotheses Panel (`frontend/components/hypotheses-panel.tsx`):
     - Expanded `CAUSE_CODE_TRANSLATIONS` to cover `CAPACITY_SHORTFALL`, `MISSED_PICKUP`, `BIN_CAPACITY_EXCEEDED`, `EXPECTED_PICKUPS_COMPLETED`, etc.
     - Removed redundant "Possible cause: " prefix from title so titles read naturally (e.g. "Solid Waste Container Capacity Shortfall", "Missed Municipal Collection Cycle").
     - Translated suspected assets with `translateAsset` (e.g. `WASTE-DEMO-SERVICE-02` -> "Commercial Waste Collection Route #02").
     - Transformed raw comma-separated uppercase tokens and hex hashes in missing evidence checklist with `formatMissingEvidence`: "Audit of container capacity vs. peak disposal volume; Verification of municipal sanitation collection logs" and "Pending physical evidence inspection (#B08-282585)".
  4. Decision Traces (`frontend/components/decision-trace-panel.tsx`, `frontend/lib/read/graph.ts`):
     - Translated tool actions with `translateToolAction`: "civicly::get_pickup_execution_history" -> "Query sanitation pickup execution history", "official::query_graph_readonly" -> "Execute readonly FalkorDB graph traversal".
     - Sanitized questions and rationales with `cleanTextIdentifiers` so questions refer to human asset names ("Commercial Waste Collection Route #02") instead of raw machine tokens.
     - Preserved canonical raw action in the underlying data model so `canvas-adapter` tests and domain audit contracts pass strictly.
  5. Work Orders Panel (`frontend/components/work-orders-panel.tsx`):
     - Passed `plan` into `WorkOrdersPanel` to resolve each work order's `task_id` against `plan.draft.tasks`, resolving the true action title ("Conduct recovery waste collection") instead of falling back to the raw task ID (`Task-b12-8a158819baf845e296daf7a45a4e4065`).
     - Added clean task reference `#b12-8a1588` and department subtitle.
  6. Testing & Quality Gate:
     - 87 frontend tests PASS (0 failures, 87 passes).
     - `tsc --noEmit` PASS (0 errors).
     - `check_contracts.py` PASS (59 operations / 55 paths / 185 schemas match).
     - Next.js production build PASS in 749ms. Production preview server running on port 3100.

## README-SUBMISSION — 2026-10-19, documentation task ready for human review

Human authorized a submission-focused README, preservation of the existing README, review of concurrent Antigravity readability changes, and graph data model before architecture. Reviewed current six-stage workspace, display translations, graph/trace presentation and source contracts; frontend files left untouched. Root README now explains the problem, three categories, canonical graph model, architecture, runtime MCP/agent roles, graph functions at every lifecycle stage, GraphRAG/checkpoints/episode memory, completed road dependency, demo navigation, bounded local setup and honest acceptance limits. Four GitHub Mermaid diagrams; graph model above architecture. No screenshots of superseded UI added. Original README archived in docs/DEVELOPMENT_HISTORY.md with only backend/docs Markdown destinations rebased; reverse-link transformation SHA256 proves every original paragraph/content retained.

Coverage: documents R01–R18 without changing implementation or claiming new acceptance. Checks PASS:55local Markdown targets;21graph diagram relationships/endpoints match canonical schema;4diagramblocks;archive retention/order;public demo homepageHTTP200;both specification validators. One initial docs checker saw display text “Prerequisite task” rather than canonical ActionTask; clarified diagram label and reran PASS. No Mermaid visual renderer, full runtime/frontend regressions or provider calls run (documentation-only). No graph/state/budget/credentials/deployment changes. Concurrent frontend edits remain outside task. Existing dated historical docs are explicitly linked as development context rather than treated as current readiness. Next: human README review, then publish the approved documentation; GitHub was not pushed by this task.

Decision: preserve historical README content with corrected relative link destinations instead of deleting or mixing milestone claims into the judge entrypoint. Explain actual Gemini-assisted investigation and operator-assisted approved lifecycle separately; no autonomous/full-acceptance claim. Link retained detailed runbooks instead of claiming public Git clone recreates private hosted runtime state.

## README-REFINEMENT — 2026-10-19, human review pending

Human requested a clearer and more understandable submission README. Rewrote opening around the recurring-road example and practical purpose; added category/questions/evidence comparison, report-vs-incident/hypothesis-vs-finding/completion-vs-resolution explanation, grouped canonical graph diagram into three stages, explained relationship names in plain language, simplified architecture and added component/job table, turned lifecycle stage descriptions into judge questions, and expanded exact road flow into five readable steps. Added explicit current three-category result table. Graph model remains before architecture; four Mermaid diagrams retained. Existing docs/DEVELOPMENT_HISTORY.md untouched; all original knowledge still preserved. No frontend/application/runtime change; concurrent Antigravity edits excluded.

Validation:56local Markdown targets exist;21canonical diagram relationship endpoint checks PASS;4diagramblocks/section order/archive retention PASS;both specification validators PASS. No Mermaid visual renderer or runtime/regression/provider execution for documentation-only change. Prior public-homepageHTTP200 check retained as historical, not rerun. Proof docs/evidence/README-REFINEMENT-{checks.json,spec.txt}. README-SUBMISSION proof remains its original55linkcheck, not replaced by new count. No commit/push. Next: human readability review and publication after acceptance.

## README-GRAPH-VISUALS — 2026-10-19, ready for human review

Human authorized actual Civicly Canvas and FalkorDB Browser visuals for the README. Captured local retained road case's Evidence-stage Canvas/contextual graph plus focused actual Browser query11nodes/15edges (assets/plan/tasks/departments/work orders). UI reports17nodes/20edges bounded contextual graph; no selected decision path and no fabricated highlight. Screenshots original JPEG, no generated/edited page content; visual inspection excludes credentials and private configuration. Added hero evidence/Canvas image and Browser image within graph model, before stage contributions/architecture. captions distinguish synthetic domain state, contextual versus model-selected evidence, internal versus canonical IDs, and bounded views. Old history and concurrent frontend implementation untouched.

Paths:README.md;docs/images/{civicly-evidence-canvas.jpg,falkordb-road-task-graph.jpg,road-task-graph.cypher,README.md};sixroottrackers append-only. Actual read-only Browser queries and UI views exercised; no application/graph/approval writes, provider calls or deployment changes. Initial previous Browser query had no drainage rows; exact presenter UNDERLIES read returned2nodes/1edge, focused snapshot11/15. Source/UI matches screenshots; local visuals may differ from cloud revision. Checks:readme/image references exist, 4Mermaid diagrams retained, section order retained, both static specification validators PASS. No full runtime/frontend suite warranted for docs/images-only task. Human verify README images/captions and graph query provenance. Next: human review then publish the screenshots if accepted. No GitHub push performed by this task.

## F09 — readable frontend and correct workflow presentation, 2026-10-19

Human explicitly requested wholefrontendreadability and truthful goodworkflow, beginning with legacy runtime metadata appearing as DETERMINISTIC_DEVELOPMENT_ONLY_NO_LIVE_AUTHORIZATION. Implemented one bounded frontend semantic/read-integration microtask covering R15/R16 and preserving R08/R09/R10/R11/R13/R17 and all18requirements. Main UI uses real trace execution_mode and authoritative operational plans/outcomes: water Gemini investigation recorded/Awaiting plan approval; closedroad Investigation complete/Review verified outcome; waste usage-limitpause explicit. Rawruntimecode stays in technicaldetails, not relabelled as liveexecution. Saved traces do not prove currentlyrunningagent.

Fixed directory categoryguessing from missingissuefield; fetches linkedincidentcategories including endedhistory. Closedreports/memory nowuse IncidentIDs, native taskbindings map worktitles/targets, and source-scopedorders preventforeignworkdisplay. Typed evidencefindings/dates/fieldreviewer visible; optionalreaderrors no longerswallowed. Neutral assessment/recurrence/completion labels, roles/permissions, graphpathexplanations and outcome/history semantics. Approval submission neverguesses assignees/nativeIDs; uncertainresponse blocks componentresubmission undernewkey. Fullwidthrecordedactivityrow improvesreadability. Backend/contracts/privateprofiles/deployment untouched; preexistingAntigravity changes captured/preserved in /tmpbaseline and task-onlypatch.

100distinct frontend testsPASS/0FAIL/0SKIP (87existingretained+13new); typecheck/build/generatedAPIguard/contracts59operations55paths185schemas and bothspecvalidatorsPASS. One real threecategory generatedclient/viewmodel HTTP readjourney and one actual browser walkthroughverify retainedFalkorDB-backeddata, report/work/memory/evidence/plan/permissions/categoryfilter. 3roadcards/0wrongwatercards underroadfilter; closedroad3orders/1memoryrow/5outcomes. Screenshot evidence frontend/docs/evidence/F09. Initial optional-typechecks/copyexpectationfailures, a shortIDfixture typo, a wholecodeprefixtranslationbug and narrowstatuslayout corrected and documented; no testremoved. Domainrevision818unchanged; managedproviderledger0requests sincebaseline. Onlylocalfrontendproduction reloaded and diagnosticlogin/logout sessions; no agentwake, domainwrite, graphreset, quarantineclear, raisedbudget or backend/cloudrestart.

Human verify localhost3100 with water INV-B09-8b006fb97aa2b908fc69addcf7ecd037; expect recordedGemini/pendingapproval with rawmetadatahidden. Closedroad INV-B09-b9d4d66e130ed348c4f6a50e9d66a891 has propercategory/report/tasks/memory; waste INV-B09-95e00a75e74b708c966db68bc595dca0 stayspaused. Nonbillable domain-read check `node --experimental-strip-types frontend/scripts/verify-readability.mjs`. README/history unchanged by this task. Remaining limits: boundedreads/no crossrequestsnapshot, staticlegacybackendlabel, partialB10/B20/B-END and nofullmobile/a11yscenarioacceptance. GitHub and hostedAWSfrontend notupdated. Exactnext: humanreviewlocalfrontend then separatelypublish/deployacceptedbuild. STOP.

F09 decision: derive run provenance from saved trace rather than reinterpret the legacy constant; use current graph plan/outcome for next action instead of overwriting old checkpoints. Prefer explicit missing/error/bounded-result language over invented first occurrence/absence/verification. No backend schema change needed.


## F10 — Scenario dialog layout (2026-10-19)

Missing shared modal CSS reproduced with actual computed position static. Restore common fixed overlay/card styling instead of duplicating component-specific positioning; preserve component logic and backend state. [Evidence](frontend/docs/evidence/F10/RESULTS.md).


## F11 — Civicly’s AI wording (2026-10-19)

Use Civicly’s AI as frontend product name while retaining LIVE_GEMINI execution identifiers, provenance and live-versus-development behavior. Historical evidence unchanged. [Evidence](frontend/docs/evidence/F11/RESULTS.md).


## F12 — Recorded activity copy (2026-10-19)

F12 — Removed the requested second sentence from recorded activity description in frontend/lib/read/workflow.ts; updated frontend/tests/workflow.test.ts exact-copy expectation. Still describes saved activity, without asserting a current run.13focusedworkflowtestsPASS/0FAIL/0SKIP;productionbuild/API/contractsPASS;bothspecvalidatorsPASS;actualbrowser shortenedcopyvisible. Localfrontendrefreshed; no backend/domain/provider changes or publicdeployment. Humanverify:refreshlocalwaterlogginginvestigation, openInvestigation andreadRecordedagentactivity. Next:humanreviewthen separatelypublish/deploy. [Evidence](frontend/docs/evidence/F12/RESULTS.md).


## F13 — Next section navigation (2026-10-19)

F13 — Added a small Next: <section> arrow button in the case workspace header (frontend/components/investigation-workspace.tsx). Uses existing section state only, available when a case is selected; hidden on final Monitoring & memory section. No workflow execution, approval or provider invocation. R15/R16 presentation; other requirements preserved. Production build (includes generated API/contracts) PASS; both spec validators PASS; whitespace PASS. Actual browser clicked all five forward transitions Report→Investigation→Evidence→Plan & approval→Work→Monitoring & memory; final heading visible and0Nextbuttons. Existing stage tabs work returning to Report. No new unit tests for this low-impact UI navigation. Local frontend refreshed with unchanged settings. Publicsite/GitHub unchanged. Humanverify:openlocalcase, Report, click Next: Investigation then continue. No local blocker; next humanreview then separatelypublish/deploy. [Evidence](frontend/docs/evidence/F13/RESULTS.md).


## F14 — Empty workspace case chooser (2026-10-19)

F14 — Added Choose a case to the unselected case workspace, opening the existing real CaseDirectory inline. Shared across all six sections; removes misleading Data unavailable inside the unselected case panel. Directory respects existing issue filter/loading/error/read-bound behavior. Bottom directory mounts only for selected cases to avoid duplicate element IDs/duplicate directory requests. Only application source:frontend/components/investigation-workspace.tsx. SupportsR15/R16; backend/domain/provider state unchanged. Production build/generatedAPI/contracts PASS;bothspecvalidatorsPASS;whitespacePASS. Actual browser:Report empty CTA→inline directory with14real links (7investigations+7incidents), single directory ID→waterlogging selection→linkedreportloaded/Nextbutton→Clear→closechooser→CTArestored. Initial immediate report-visible probe false while loading; explicit wait then passed. No scenario activation/mutation/provider request initiated. No new unit tests for low-impact UI composition reusing existing tested directory. Localfrontendrefreshed only. Humanverify:openlocal/investigations,Chooseacase,selectavailablecase. No local blocker;GitHub/publicsite unchanged;next humanreviewthen separatelypublish/deploy. [Evidence](frontend/docs/evidence/F14/RESULTS.md).


## DEMO-LIFECYCLE-COMPLETION — 19 Oct 2026

Explicit human approval received for exact waterlogging and secondroad plan bindings. Both now APPROVED→authorized/assigned work→completion→MONITORING→separate RESOLUTION_VERIFIED→COMPLETED with endedincident/memory. Original road/utility complete;3complete localjourneys total. All18requirements remainbinding; B10/B20/B-END/all12acceptance notdeclaredcomplete. [Evidence](docs/evidence/DEMO-LIFECYCLE-COMPLETION/RESULTS.md). Use existing authenticated domain APIs and exact immutable AI-generated plans rather than rewrite statuses or script an AI decision. New fixed-scope operator runner persists exclusive private dispatchmarkers/receipts; no automaticretry. Two original water503 sockettimeouts occurred before APIintent; explicit samekey retries required absentintent,originalapprovalhash unchanged,noorders,clean source. Do not extend this exception to existing quarantines. Synthetic field/review identities and dates explicit; no physicalrainfall/wear claim. Source/runtimecaps and original agentcheckpoints unchanged. Next waste requires operator-assistedreassessment/newexactapproval and24hourfollowup, not capbypass.


## AWS-UPDATE-20261019 — deployed and verified

The existing AWS demo now serves the current frontend and retained graph revision1056: three completed journeys, five completed work orders, three verified work orders and zero pending approvals. Public URL: https://civicly-13-55-205-208.sslip.io . All18requirements remain binding; B10/B20/B-END and unfinished cases are not declared complete. [Evidence](docs/evidence/AWS-UPDATE-20261019/RESULTS.md). Chose a staged application and fresh Docker volume rather than restoring over a populated database. Reused libraries only after frozen lockfile equality. Preserved hosted auth/session SQLite, prior release/runtime and prior database volume. Used a temporary private encrypted exact-object S3 grant to the existing role; grant/object/bucket removed. Two explicit phase resumes corrected pre-cutover harness failures without repeated DB import. Existing infrastructure, caps, TLS and account plan remain.


## F15 — 19 Oct 2026

F15: Use exact known saved-note templates for plain explanations, with neutral fallback for unknown coded text. Alternative generic code substitution cannot reliably explain causal meaning. Preserve original reason in Technical details and derive plan inclusion only from structured addressed flag.


## F16 — 19 Oct 2026

F16: actual completed presenter investigations are separate from B19 scenario registration. Load typed investigation/incident directory in journey menu rather than assigning existing cases to S01/S03/S04 by similarity. Missing case returns null instead of generic workspace launch. Preserve all catalog definitions and expose each connected case. No domain writes or fake scenario completion.


## F17 — 19 Oct 2026

F17: show incident narrative from exact linked ComplaintDTO records plus possible-cause titles. Chose bounded3 direct complaint reads instead of guessing a story from category/ID or loading global complaints. Validate both complaint ID and incident binding; source claims remain reported, original text preserved. Graph revision/group/role moved to technical disclosure; location/start/status/shortreference/nextstep stay visible.


## F18 — 19 Oct 2026

F18: casecards should explain reported symptoms and location, not repeat category. Shared directory loads first linked complaint perincident (bounded60), checks sourcebinding, produces short explicitly Reported text plus actual translatedlocation. Preserve unverified leak and schedule claims; no diagnoses/statuses inferred. Unknown prose bounded110chars, originalheaderrecords retained.


## F19 — 19 Oct 2026

F19: use scoped card typography hierarchy (category12px, report13px, location12px, reference11px, status10px), compact gaps and footer divider. Remove inline styles for predictable component styling. Preserve allcontent/status/links; no domain logic changes.


## F20 — 19 Oct 2026

F20: Report should summarize savedincident→investigationquestion→currentevidenceassessment→recordedplan/authorizedwork→independentoutcome. Preserve claims/evidence/work/outcome distinctions. Actualreadback showed PlanDTO.approval_status is legacy lifecycle; use scopedorder.authorized_by for historicalauthorization text, not infer approvaldecision. Currentassessmentrevision precedes hypothesisstatus; deduplicate equalcause summaries. No newbackendrequests/domainwrites.


## F21 — 19 Oct 2026

F21 — Removed The incident at a glance heading and its introductory paragraph per exact human request. Report now starts with What happened; removed unused intro CSS and first-section top divider. R15/R16; all18requirements preserved. Source:frontend/components/investigation-workspace.tsx;frontend/app/globals.css. Build/API/contracts/typesPASS; make test-spec bothPASS; scopedwhitespacePASS. Actual localbrowser zero removedheading/paragraph matches, What happened and remainingcaseoverview visible; screenshot frontend/docs/evidence/F21/report-start.jpg. No newunit/fullbackendtests for simple copy/style removal. No domain/provider/state changes; localfrontend reloaded;AWSunchanged. Humanverify:refreshlocalcase→01Report. No blocker. Exactnext:humanreview then separatelyrequesteddeployment/nextUItask;STOP.


## F22 — 19 Oct 2026

F22 — Case-directory cards now say Open Reports and link to section=report. Workspace section is URL-derived; existing tabs/Next update section while retaining selectedcase/filter. This ensures reopening samecase from Evidence or Investigation selects Report, rather than retaining previous localtabstate. Missing/unknownsection retains prior Investigationdefault. Application paths:frontend/components/case-directory.tsx;frontend/components/investigation-workspace.tsx;frontend/lib/read/cases.ts; extendedcheckfrontend/tests/cases.test.ts. R15/R16; all18requirements preserved. npm --prefix frontend test114PASS/0FAIL/0SKIP;build/API/contracts/typesPASS;make test-spec bothPASS;scopedwhitespacePASS. Actualbrowser evidenceURL→samecaseOpenReports→Report, Next→Investigation→samecaseOpenReports→ReportPASS;7cards retainIDs/content andnewlabel. InitialWhat-happened check duringcasekeyreload false, explicitreadinesswait then reportLoadedtrue. Screenshotfrontend/docs/evidence/F22/open-reports.jpg. No domain/provider/approval/checkpoint changes. Localfrontend reloaded only;AWSunchanged. Humanverify:refreshlocaldirectory,OpenReports,thenNextInvestigationandreopencard. No blocker. Exactnext:humanreviewthen separatelyrequesteddeployment/nextUItask;STOP.


## F23 — 19 Oct 2026

F23 — Applied exact human-approvedhomepagecopy:CONNECTED EVIDENCE.INFORMED ACTION.;Understand why civic problems keep coming back.;Civicly’s AI connects reports,infrastructure and evidence to investigate recurring problems,guide coordinated action and verify what happened after the work. Application sourceonly:frontend/app/page.tsx. R15/R16;all18requirements preserved. Existing layout/actions retained. npm --prefix frontend run buildPASSincludingAPI/contracts/types;make test-specbothPASS;scopedwhitespacePASS. Actual localbrowser confirmednewcopy,connectedworkspace andreadablewrapping; screenshotfrontend/docs/evidence/F23/homepage.jpg visuallyinspected. No newunit/fullbackendrerunforcopy-onlychange. No domain/provider/approval/statechanges. Localfrontend reloaded;AWSunchanged. Humanverify:refreshlocalhost3100homepage. No blocker. Exactnext:humanreviewthen separatelyrequesteddeployment/nextUItask;STOP.


## F24 — 19 Oct 2026

F24: dashboardmetrics become keyboard-accessible buttons opening read-only native dialogs. Match sourcecountdefinitions; pendinguses analyst-readable pendingplans ratherthan forbiddenapproverlist. Completedwork neverimpliesresolution; verifieduses actualresolution_verifiedprojection. Boundedpagination failsvisiblyoncap/repeatedcursor. No domainwrites/privilegechanges.


## F25 — 19 Oct 2026

F25: show actionpurpose from validatedplanbinding, realdependencies andreadfollowup;technicaltaskIDsremainexpandable. Purposeis intendedscope,not completedfact. Scopedtypography/cards/neutralassetchipsreduceclutter;no newdomainlogic.


## F26 — 19 Oct 2026

F26: monitoringpresentsconditionchecks,datedaction-specificassessmentsandmemoryreusepurposebeforeguidance. Keeporiginalmemorysummary/gaps/procedureversionsintechnicaldisclosures. Currentplanorderbindingsscopeoutcomes;noinventedrootcause/followupmeasurements. Historicalcompletionwordingmustnotimplycurrentunresolvedafterlaterclosure;showchronologicalhistory.


## DEMO-WASTE-COMPLETION — 19 Oct 2026

Use existing reviewed inspection to reassess and prepare bounded pickup recovery as authenticated operator-assisted activity, rather than restarting the budget-exhausted AI or claiming autonomous recommendation. Exact human approval was obtained before work. Retain the capacity alternative and mandatory 24-hour follow-up. One proven pre-intent HTTP503 was reconciled by absent-intent/journal + unchanged hash; unchanged-profile API reload and one same-key/same-payload attempt succeeded. Quarantined wakes are audit-only because the current reconciliation contract does not support their saved states; preserve all originals pending a tested extension. See docs/evidence/DEMO-WASTE-COMPLETION/RESULTS.md, COMMANDS.md and FILES.md. Human verification: open the local waste investigation and inspect Plan & approval → Work → Monitoring & memory. R08–R11/R13/R17/R18; all18requirements preserved.


## AWS-UPDATE-20261019-02 — 19 Oct 2026

Deploy reviewed working-tree frontend F15–F26 and current synthetic runtime snapshot on the existing EC2, retaining previous release/volume rather than overwriting its populated database. Add optional CIVICLY_EXPECTED_OLD_REVISION guard after stopping app services and before cutover; a mismatched or pending hosted graph aborts and restarts old services. Preserve cloud auth independently. Strict private encrypted transfer, temporary one-object IAM access removed. Rollback failure path not fault-injected. R15–R18; all18requirements preserved. Exact files/commands/evidence:docs/evidence/AWS-UPDATE-20261019-02/{FILES,COMMANDS,RESULTS}.md. Humanverify:https://civicly-13-55-205-208.sslip.io →Work completed(6)→wastepickup→Work/Monitoring.


## F27 — 19 Oct 2026

F27:reorder the shared metric array so visual and keyboard order agree; keep each metric bound to its original field/icon/description/dialog. Update the existing order assertion rather than adding redundant tests. R15/R16;all18requirements preserved. Source:frontend/lib/read/cases.ts;frontend/tests/cases.test.ts. Evidence:frontend/docs/evidence/F27/RESULTS.md. Humanverify:homepagecardorder;nextreview/deployment;STOP.


## F28 — 19 Oct 2026

Completed-work popup label View Report must match its destination:Report stage of the same investigation. Keep other metric destinations intact. R15/R16;all18requirements preserved. Source:frontend/components/metric-records.tsx;frontend/lib/read/dashboard.ts. Evidence:frontend/docs/evidence/F28/RESULTS.md. Humanverify:homepage→Workcompleted→ViewReport→01Report;STOP.


## F29 — 19 Oct 2026

Reorder the homepage issue-card array directly so visual,DOM and keyboard order match the human request;retain all category bindings. R15/R16;all18requirements preserved.Source:frontend/app/page.tsx.Evidence:frontend/docs/evidence/F29/RESULTS.md.Humanverify:localhomepageRecurringproblemsorder;STOP.


## F30 — 19 Oct 2026

Use text beneath the existing Civicly wordmark,9px muted/right-aligned, keeping the repo-native graph icon. No rasterasset or dependency needed. R15/R16;all18requirements preserved.Source:frontend/components/shell.tsx;frontend/app/globals.css.Evidence:frontend/docs/evidence/F30/RESULTS.md.Humanverify:localhomepageupperleftlogo;STOP.


## F31 — 19 Oct 2026

Implement only the first approved judging improvement:one curated recorded-road entry,not a new agent run. Gate completion language on current native investigation+plan COMPLETED states;otherwise generic recorded-case wording. Distinguish recorded AI work,analyst-assisted planning and synthetic field work. Keep browsing as secondary action and start the walkthrough at Report. R15/R16/R18;all18requirements preserved.Source:frontend/components/featured-investigation.tsx;frontend/app/page.tsx;frontend/app/globals.css.Evidence:frontend/docs/evidence/F31/RESULTS.md.Humanverify:localhomepagefeaturedcase→Report→NextInvestigation;STOP.


## F32 — 19 Oct 2026

F32:use only exact saved successful validated lookup/decision/execution/path bindings with complete current returned nodes/edges. Prefer full source trail over prefixes;do not substitute missing historic dependency path. Explain recorded source association separately from causal findings. Next recorded choice is chronological attribution,not inferredprivate reasoning. Firstmatchedtrail defaultfocus;widercontext onebuttonaway. R04/R09/R15/R16;all18requirements preserved.Exactfiles/commands/limits:frontend/docs/evidence/F32/RESULTS.md.Humanverify:localoriginalroadInvestigation→rightgraphguide→switchpath/openreport/widergraph;STOP.


## F32-R — 19 Oct 2026

Humanrequested widergraphdefault and Canvas before question/connection/nextchoice. Track focusedpath instead of widerpath so unselected/default state stayswide;retainactualpathhighlight. R04/R09/R15/R16;all18requirements preserved.Source:frontend/components/recorded-decision-graph.tsx;frontend/app/globals.css.Evidence:frontend/docs/evidence/F32R/RESULTS.md.Humanverify:localroadInvestigationgraphfirst/widerdefault;STOP.


## F32-R2 — 19 Oct 2026

HumanrequestedactualgraphbeforeWhatthisgraphshows:Canvas toolbar/bounds→visualization→caption→legend/technicalmetadata;widerdefaultandguideexplanationsunchanged.Source:frontend/components/falkordb-canvas-view.tsx.Localbuild/API/contracts/types,specvalidators,scopedwhitespaceandbrowserPASS.No newunit/fullbackendrunforsmallJSXreorder.No blocker;AWSunchanged;backendacceptancepreserved.R15/R16;all18requirements preserved.Evidence:frontend/docs/evidence/F32R2/RESULTS.md.Humanverify:refreshlocalroadInvestigationrightgraphpanel.NextF33stagetakeawaysafterreview;STOP.


## F32-R3 — 19 Oct 2026

HumanrequestedWhatthisgraphshowsbelowAssesstheevidence:guidegraph→question→connections→nextrecordedchoice+rationale→sharedGraphCaption→qualifications/sources/details.Canvascaptiondisabledonlyinguide,standalonedefaultretained.Source:frontend/components/falkordb-canvas-view.tsx;frontend/components/recorded-decision-graph.tsx.Build/API/contracts/types,specvalidators,scopedwhitespace/browserPASS.No newunit/fullbackendrunforsmallrenderrelocation.Localonly;AWSunchanged;noblocker.R15/R16;all18requirements preserved.Evidence:frontend/docs/evidence/F32R3/RESULTS.md.Humanverify:localroadInvestigationcaptionbelowassessment.NextF33afterreview;STOP.


## F33 — 19 Oct 2026

Use deterministic summaries of existing read DTOs rather than generated narrative or new backend state. Alternative static stage slogans would not explain the selected case. Current assessment, plan scope, recorded authorization, evidenced closure and matching memory guards preserve the distinctions between hypotheses, work and outcome. R09/R15/R16/R17; all eighteen requirements preserved. Exact files, commands, verification and limitations: frontend/docs/evidence/F33/RESULTS.md. Human verify: local road case → six stage buttons → Key takeaway; waste monitoring remains unverified. STOP for review.


## F34 — 19 Oct 2026

Use existing authorized read DTOs for a four-milestone response view instead of requesting approver-only records or inventing event dates. Authorization is evidenced by approval references on current-plan work orders. Only follow-up supplies dates; numbers denote conceptual stages. Legacy plan approval_status is not used as an approval decision. R09/R10/R11/R15/R16/R17; all eighteen requirements preserved. Exact files, commands, limitations and human verification: frontend/docs/evidence/F34/RESULTS.md. Verify local road Plan/Work/Monitoring response timeline; waste remains unverified. STOP for review.


## F35 — 19 Oct 2026

Curate actual returned investigation records rather than relabeling twelve scenario definitions as completed journeys. Keep completed, ongoing and cancelled groups distinct; suggest the known road case only when returned as COMPLETED. Collapsed full catalog preserves all definitions and explicit missing runs. All journey links start at Report. R01/R15/R16/R18; all eighteen requirements preserved. Exact paths, commands, limitations and human verification: frontend/docs/evidence/F35/RESULTS.md. Verify local Scenarios completed/ongoing grouping, Report links and preserved catalog. STOP for review.


## F36 — 19 Oct 2026

Distinguish connecting/loading from unavailable while preserving session identity and case-key ownership of cached data. Prefer explicit quiet placeholders over delaying all content or pretending records are absent. Remove duplicate connection/next-action/completion banners, retaining actual errors, recovery controls, stage takeaways and outcome distinctions. R09/R15/R16/R17; all eighteen requirements preserved. Exact files, commands, limitations and verification: frontend/docs/evidence/F36/RESULTS.md. Human verify: fresh local case load → Work/Monitoring, and homepage connection state. STOP for review.


## F37 — 19 Oct 2026

Human-selected homepage headline implemented in frontend/app/page.tsx: Every civic problem has a story. Follow it to resolution. Existing homepage h1 → new exact copy; no data/control-flow change. Production build/API/contracts/types and both spec validators PASS; no redundant unit/full backend rerun. Local port 3100 had no listener; server/browser not started. AWS unchanged. R15/R16; all eighteen requirements preserved. Evidence and verification: frontend/docs/evidence/F37/RESULTS.md. Next: human review, then deployment only when authorized. STOP.


## AWS-UI-20261019-01 — 19 Oct 2026

Deploy reviewed frontend only as an isolated EC2 release and WorkingDirectory override; preserve backend/data release02. This avoids unnecessary snapshot replacement or API/DB restart. SSM direct source transfer avoids new staging buckets/IAM permissions. Correct staged Turbopack external-symlink restriction using independent locked-dependency copy. R09/R15/R16/R17/R18; all eighteen requirements preserved. Exact paths, commands, failures, limitations and human verification: docs/evidence/AWS-UI-20261019-01/RESULTS.md. Public URL https://civicly-13-55-205-208.sslip.io. STOP for review.


## README-JUDGE-REFRESH — 19 Oct 2026

Make FalkorDB the central explanatory thread of the submission README: road story, domain relationships, six-stage contribution, SDK knowledge graph, Saver checkpoints and Canvas. Distinguish graph retrieval/persistence from LLM choices and service-enforced rules. Preserve prior full README in README_TECHNICAL_REFERENCE.md rather than discard detail. Use actual captures/proof, not fabricated impact or video. All eighteen requirements preserved. Exact files, commands, limitations and verification: docs/evidence/README-JUDGE-REFRESH/RESULTS.md. Human verify: README story → Report link → graph model before architecture → current result/evidence table. STOP for review.


## README-JUDGE-REFRESH-REVERT — 19 Oct 2026

Human requested reverting the README rewrite. README.md restored byte-for-byte from the preserved pre-rewrite body; SHA256 verified against docs/evidence/README-JUDGE-REFRESH/previous-readme.sha256. No application/data changes, GitHub push or AWS deployment. Archive/images/evidence and audit history retained. Next: human review; no further README changes without direction. STOP.


## README-TARGETED-REFINEMENT — 19 Oct 2026

Applied human-requested suggestions in place to restored README.md, preserving every original section/order and four Mermaid diagrams. Improved FalkorDB opening/store roles, graph-versus-service explanation, judge walkthrough, Report links, real overview image, current water/waste results and scoped proof links.44local targets/4anchors, unchanged diagram/section checks, both spec validators and scoped whitespace PASS. No new application/provider/runtime changes;136test count points to prior actual deployment evidence. Existing docs/images/civicly-overview.png must accompany future push. GitHub/AWS unchanged. All18requirements preserved. Exact verification/limitations: docs/evidence/README-TARGETED-REFINEMENT/RESULTS.md. Next: human review; push only when requested. STOP.


## README-FALKORDB-OVERVIEW — 19 Oct 2026

Human requested a short overall FalkorDB explanation after the third paragraph. Added one paragraph in README.md connecting report/assets/history → evidence/procedures → departmental work → dated follow-up/retained outcomes. Existing wording and diagram/section order unchanged. Text-placement and scoped whitespace checks PASS; no app tests or runtime/provider calls for prose-only edit. No GitHub push/AWS change. All18requirements preserved. Human verify README opening, immediately after FalkorDB paragraph. Next: human review; STOP.


## README-BROWSER-GRAPHS — 19 Oct 2026

Human-authorized real Browser schema/case pair added to README: conceptual diagram → filtered14label discovered schema → optional full48label/190placement overview → existing road-case graph. Native Browser display filters/fit/zoom/pan only; actual screenshot visually inspected, no domain writes/provider calls. README.md, docs/images/README.md, focused screenshot and evidence updated; full overview newly referenced.46local links/images, both spec validators and whitespace PASS. Road image/query unchanged; GitHub rendering not separately run. No push/AWS change. All18requirements preserved. Exact files/limits/verification: docs/evidence/README-BROWSER-GRAPHS/RESULTS.md. Next human review, push when requested; STOP.


## README-REMOVE-SETUP-DOCS — 19 Oct 2026

Human requested removing local setup and technical documentation sections. Removed both sections and their top navigation anchors from README.md; retained Built with footer. Underlying technical/runbook files and preserved README reference unchanged. Exact section/anchor absence and scoped whitespace checks PASS. Prose-only; no app/runtime tests needed. No GitHub push/AWS change. Next human review; STOP.


## README-ISSUE-GRAPH-ROLE — 19 Oct 2026

Added human-requested FalkorDB role to What can Civicly investigate table as a per-category column: drainage traversal/history, sourced road/utility and task dependencies, waste route/schedule/pickup evidence. README.md only content change; preserves qualified questions and evidence distinction. Table shape/three categories and scoped whitespace PASS; no app tests for prose. No push/AWS change. Next human review; STOP.


## README-DEMONSTRATED-HEADING — 19 Oct 2026

Human-requested removal of today from README.md heading: What is demonstrated. Updated matching internal anchor. Heading/anchor check and scoped whitespace PASS; copy-only, no app tests. No push/AWS change. Next human review; STOP.


## README-COMPACT-EVIDENCE — 19 Oct 2026

Human approved replacing the README engineering verification table with a compact Explore the implementation line linking completed road Report, FalkorDB-backed lifecycle evidence and verification details. Removed the adjacent table-specific test-batch explanation; substantive demonstration boundaries remain. Link existence and scoped whitespace PASS; prose-only/no app tests. Underlying proof files preserved; no GitHub push/AWS change. Next human review; STOP.


## README-FOOTER-LINKS — 19 Oct 2026

Removed human-specified final Requirements / Current task board / Known blockers / Road-case proof link row from README.md. Underlying files and other requested evidence links preserved. Exact-row absence and scoped whitespace PASS; prose-only/no app tests. No push/AWS change. Next human review; STOP.


## README-TRACKS — 19 Oct 2026

Added human-requested concise three-track explanation to README.md before demonstrated results. Uses project track definitions from docs/backend/00_requirements.md: graph/MCP investigation; coordinated roles/Saver/retained memory; municipal operations/GraphRAG knowledge. Descriptive labels, no claim of official track titles or completed acceptance. Existing limits retained. Three-track presence/placement and scoped whitespace PASS; no runtime/tests for prose-only change. No push/AWS change. Next human review; STOP.


## README-TRACK-NAMES — 19 Oct 2026

Corrected README track headings to exact human-provided names: Agents That Act on Connected Data; Agent Memory and Coordination; Company Brain. Company Brain explanation explicitly describes municipal operations application. Exact names and scoped whitespace checks PASS; no runtime change, push or AWS deployment. Next human review; STOP.


## README-FULL-SCHEMA — 19 Oct 2026

Embedded existing full schema overview immediately below README Graph data model heading, per human request. Caption identifies discovered48labels/190connection patterns including internal records; existing conceptual/focused/case views retained. Image existence/placement and scoped whitespace PASS; no runtime/test/push/AWS change. Next human review; STOP.


## GITHUB-FULL-UPDATE-20261019 — 19 Oct 2026

Human explicitly authorized publishing whole pending project to existing public krvikash05/Civicly main. Included source/frontend/deployment-demo helpers/docs/screenshots/evidence; excluded ignored runtime/secrets/dependencies/builds.136frontend tests/build/API/contracts/types/both spec validators/script syntax/whitespace PASS;391pending files scanned with no credential pattern/suspicious DB/key findings. No full backend/model run. Evidence: docs/evidence/GITHUB-FULL-UPDATE-20261019/RESULTS.md. Next remote commit verification and human review; STOP.
