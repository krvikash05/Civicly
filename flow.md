# flow.md — Repository map and runtime data/control flow (update after every microtask)

## Intended architecture (NOT yet implemented)
Complaint/API/CLI -> validation/intake service -> FalkorDB graph and durable domain event -> worker -> LangGraph supervisor -> MCP client (`tools/list`, `tools/call`) -> [official read-only FalkorDB MCP | Civicly domain MCP] -> read graph / sourced data -> hypotheses -> plan -> approval -> work order -> simulated department event -> outcome evidence -> memory graph -> investigator resumes.

Organizational documents -> validated ingestion -> FalkorDB GraphRAG document graph (`civicly_docs`, isolated SDK-controlled schema) -> source-backed retrieval tool -> stable `Document`/`Evidence` references in canonical `civicly_knowledge`.

API -> versioned DTOs, sanitized graph subgraphs, trace and SSE -> FUTURE Next.js Investigation Studio / FalkorDB Canvas / map / plan DAG / approvals.

## File ownership and import rules (proposed)
- `backend/app/api/`: HTTP endpoints, auth dependency and SSE. Must not issue raw Cypher.
- `backend/app/domain/`: Pydantic models, state transitions and enums. No network calls.
- `backend/app/services/`: domain state-changing services, authorization, idempotency, event emission.
- `backend/app/graph/`: parameterized Cypher templates, migrations, read/write repository implementation.
- `backend/app/agents/`: LangGraph states/steps, decision policy, prompts, model adapters.
- `backend/app/mcp/`: MCP client broker, official server filters, custom MCP server and tools.
- `backend/app/knowledge/`: GraphRAG document store ingestion and cited retrieval.
- `backend/app/simulation/`: seeded world and causal test events, never imported into agent context.
- `backend/app/events/`: outbox, claim/ack/retry, SSE trace publication.
- `backend/cli/`: scripts that invoke same services as FastAPI, no separate business logic.
- `backend/tests/`: unit + real integration + behavioral scenario tests.

## Change template per task
### Bxx — Actual paths and call flow
- Files added/changed:
- Imports / outward dependencies:
- Input contract -> validation -> graph/API/tool state -> output:
- Persisted state / events / cache:
- Security boundary and failure behavior:
- Verified by test_log entries:

### B00 — Actual audit file/data/control graph | 2026-10-17
- Changed only six tracking files: decision.md, flow.md, implementation_status.md, test_log.md, blockers.md, task_board.md. No application paths created.
- Read chain: AGENTS/README/start prompt -> requirements/system/microtasks/vendor map -> current backend/contracts/frontend contract/demo docs -> tracking files. Generators inspected without execution.
- Actual flow: Python 3.12/jsonschema -> supplied validators -> registry/machines/MCP/API/events/seeds/scenario structure/document hashes -> stdout/exit status -> test_log. Additional inline JSON property audit -> confirmed seed defect -> decision/blocker records. Environment/version checks -> local capability baseline.
- No database writes, persistent events, MCP sessions or agent runs. Only selected environment-variable presence printed; no secret values. Hidden evaluator structures inspected only for development audit; future runtime exclusion still required.
- Debug from test_log reproductions -> blockers -> DEC-004 -> earliest affected microtask. Intended architecture above remains unimplemented.

### B01 — Implemented foundation file graph | 2026-10-17
- Root: .git/ (main, no commits/remotes), .gitignore, .python-version, .env.example, ignored generated .env, compose.yaml, Makefile, updated README.md.
- backend/pyproject.toml + uv.lock -> isolated backend/.venv -> editable `app` and `cli` packages + console `civicly`.
- backend/app/config.py: Settings (Pydantic settings, FALKORDB_* environment fields, optional explicit env file, masked password, finite timeouts).
- backend/app/graph/connection.py imports Settings + official FalkorDB + redis retry policy; context opens client -> yields -> finally closes client and disconnects pool. No domain repositories, migrations or labels introduced into canonical graph.
- backend/app/services/health.py imports configuration/connection, defines typed foundation result; backend/cli/main.py imports Settings/check_health. CLI parser -> Settings validation -> service -> client -> PING/MODULE LIST/GRAPH.LIST -> existing graph only: GRAPH.RO_QUERY with parameterized scalar RETURN and LIMIT 1 -> typed JSON and exit 0/1/2. API/MCP can reuse service later; neither exists yet.
- Health never creates graph: absent canonical graph returns `uninitialized`, graph_read=null and only server/module foundation health. It never implies full-system readiness. Redis errors map to redacted GRAPH_UNAVAILABLE; config errors map to CONFIG_INVALID.
- scripts/configure_local.py reads .env.example -> exclusive create of ignored .env with random Browser keys and mode 0600, preserving existing file. `make setup` -> Python 3.12 venv -> pinned uv -> frozen sync. `make up` -> configure -> Compose wait.
- Compose -> pinned official single container (database + developer Browser) -> localhost ports 6379 and 3000. Healthcheck verifies PING, GRAPH.RO_QUERY command registration and Browser HTTP. Named civicly_falkordb_data -> /var/lib/falkordb/data (AOF + snapshots); civicly_browser_data -> /var/lib/falkordb/browser/.data (actual API-token store). Runtime source/evaluator files are not mounted into container.
- Tests: backend/tests/conftest.py gates disruptive persistence; unit/test_foundation.py tests invalid config/redaction/framework compatibility. integration/conftest.py only allows local DB, creates random civicly_b01_test_* graphs and cleans only those graphs. test_graph_smoke.py exercises real parameterized writes/reads, RO denial/no mutation, healthy/missing graph behavior and subprocess CLI. test_browser.py verifies live HTTP. test_persistence.py creates graph node + synthetic Browser volume marker, restarts then force-recreates only civicly service, asserts same/different container IDs respectively, and fresh read/settings/HTTP/marker after each. Volumes never deleted.
- A separate civicly_b01_runtime graph retains synthetic B01-PERSISTENCE node for human review; no canonical seed imported. Real Browser login and read of that node verified after recreation; screenshot in docs/evidence/B01-browser.jpg. Actual suite and CLI outputs in B01-tests.txt/B01-runtime.txt.
- Durability boundary: graceful lifecycle persistence verified; event atomicity/outbox, crash recovery, checkpoints, memory/GraphRAG and evaluator process isolation remain future work, with DEC-004 findings open.

#### B01 exact created/modified paths
Created source/config/docs/evidence files:
```text
.gitignore
.python-version
.env.example
Makefile
compose.yaml
scripts/configure_local.py
backend/README.md
backend/pyproject.toml
backend/uv.lock
backend/app/__init__.py
backend/app/config.py
backend/app/graph/__init__.py
backend/app/graph/connection.py
backend/app/services/__init__.py
backend/app/services/health.py
backend/cli/__init__.py
backend/cli/__main__.py
backend/cli/main.py
backend/tests/conftest.py
backend/tests/unit/test_foundation.py
backend/tests/integration/conftest.py
backend/tests/integration/test_browser.py
backend/tests/integration/test_graph_smoke.py
backend/tests/integration/test_persistence.py
docs/evidence/B01-tests.txt
docs/evidence/B01-runtime.txt
docs/evidence/B01-browser.jpg
```
Modified supplied files: README.md, decision.md, flow.md, task_board.md, implementation_status.md, test_log.md, blockers.md.
Generated local-only state: .git/, ignored .env, backend/.venv/, .uv-cache/, temporary clean environment /private/tmp/civicly-b01-locked-env and earlier temporary Compose spike /private/tmp/civicly-compose-spike.yaml. Named Docker volumes persist outside Git. No commit or remote created.

### B02 — Actual schema architecture and data/control flow | 2026-10-17
- Baseline: accepted B01 local commit 426f6e1322dca9e83e470ee471b25b8df7f9e028; B02 edits remain reviewable/uncommitted; no remote push. Exact paths and diff in docs/evidence/B02-files.txt and B02-git-diff.txt.
- Registry v3 contracts/schema_registry.json -> app/graph/schema.py Registry: strict property shape, enums/bounds, UTC times, point adapter, scope constants, declared parent labels and directed endpoint types. Public ontology names/enums retained. Storage-only CivicEntity supplies global domain-node identity; metadata label does not enter domain reasoning.
- Registry -> frozen app/graph/migrations/0001.json (registry hash, explicit index/constraint plan). app/graph/migration.py imports Registry/utc_now + official Redis lease primitives; official FalkorDB connection passed from services/schema.py. No business repository/API/agent integration.
- CLI migrate/schema-status -> Settings -> services.schema.schema_operation -> connect -> MigrationRunner -> version/hash preflight -> exclusive renewed 60s lease -> bootstrap metadata index/constraints -> APPLYING -> additive missing index creation -> actual index OPERATIONAL polling -> constraint creation/readiness -> READY -> fresh full-catalog status. Errors persist FAILED + redacted code/audit; no destructive graph/data cleanup. Every rerun introspects live catalogs and verifies hashes.
- Dynamic data (IDs/maps/scope/timestamps/checksums) uses parameter arguments. Only registry/immutable-plan identifier tokens form DDL. GRAPH.CONSTRAINT uses separate Redis command arguments because installed client has no convenience helper. Catalog procedures have fixed explicit columns and bounded return count; no arbitrary query input.
- node_statement/edge_statement compile schema-validated one-entity writes with inherited labels and source/target typed MATCH. They are testable schema adapters, not operational repositories or authorized tools. Strict validation rejects unknown fields rather than filtering. geo_point map becomes parameterized native point; other complex property values rejected.
- Persistence: canonical graph now has only migration bookkeeping (zero CivicEntity domain nodes); constraints/indexes survive B01 restart+replacement-container regression on retained volume. B01 civicly_b01_runtime graph is intact. No fixture import, checkpoint/GraphRAG changes or new DB containers/volumes.
- Metadata: version1, registry3, checksums, current state, attempts, UTC times and append-only state_history JSON string. Lease is separate Redis key, scoped by graph name and released after migration; no workflow outbox claims.
- Legacy compatibility: validators explicitly check supplied v1/v2 fixture structure, skip only newly introduced required fields in legacy presence checks, flag the exact known 55 unknown fields, and reject new unknowns. Runtime canonical adapter accepts no implicit scope/version conversion. B04 must convert source/edge metadata and repair Observation fields; files unchanged.
- Scope flows identically through registry, state/MCP/API/event metadata and current architecture docs. Client cannot choose municipality. No current framework needs tenant_id; any future mapping is explicit at boundary.
- Tests: unit/test_schema.py covers strict types/unknowns/enums/scope/time and retained defects; integration/test_schema_migrations.py performs real DDL/constraints, subtype/point writes, failure/recovery/version/lease/drift tests and B01-probe protection. Existing B01 tests all retained. Synthetic examples in tests/schema_examples.py are isolated test records, not city seeding.
- Debug: make schema-status -> backend/SCHEMA.md recovery guide -> actual db.indexes/db.constraints -> test_log/blockers. Domain graph-wide cardinality/cycles/evidence existence, retrieval templates and typed repositories are B03, not implemented here.

### B03 — Actual repository/query file graph and control flow | 2026-10-17

```text
connection.connect(Settings) -> official FalkorDB client
  GraphRepository -> MigrationRunner.status (real catalog READY)
                  -> Registry v3 + contracts/graph_access.json
                  -> NodeRecord / EdgeRecord / digest
  GraphQueries -> QueryRequest + ReadLimits -> eight static templates
               -> GraphRepository read/validation -> GraphResult / PathRecord
  tests.graph_fixtures -> repositories -> disposable civicly_b03_test_UUID
  tests.b03_evidence -> real queries + EXPLAIN -> B03-runtime.json
```

- Actual added source: backend/app/graph/models.py, repository.py, queries.py;
  contract graph_access.json; test fixtures/unit/integration/evidence reporter;
  backend/GRAPH_ACCESS.md. Migration runner whitelist now admits B03 test graphs;
  immutable registry/migration0001 unchanged. Makefile adds test-repositories.
- Write flow: strict shape/identity/origin validation -> per-graph Redis lease ->
  metadata owner/epoch fence -> recover prior intent only if pre-state unchanged ->
  actual endpoints/scope/FKs/evidence -> bounded cardinality/cycle proof -> pending
  ID/hash journal -> one fenced graph statement updates domain record, audit,
  repo_revision and pending clear -> strict typed retrieval. Mutable updates need
  expected content hash. Failures preserve state/evidence and return explicit errors.
- Read flow: typed named request -> root type validation -> pre-read revision/no
  pending -> parameterized GRAPH.RO_QUERY (finite hop/result/time limits) -> validated
  driver nodes/edges mapped from internal IDs to public stable IDs -> original edge
  direction/path order/evidence metadata, node/edge caps -> post-read revision/no
  pending -> retry once on revision change -> serialized GraphResult. Disconnected
  metadata projection is avoided after its installed-runtime upstream-path failure.
- All eight query families and temporal checks are described in GRAPH_ACCESS.md;
  candidate source-evidence pointers are also filtered by as_of. Explicit edges
  connect waste, drainage and roads; matching coordinates alone adds no connection.
  Graph paths support investigation but do not declare causation or recurrence.
- Persisted state: existing graph AOF/volumes; internal migration record receives
  repo_owner/epoch/revision/pending/audit scalars only in graphs actually mutated by
  repositories. Canonical graph has zero domain data and no B03 repository mutations.
  Test graphs are deleted individually. B01 runtime graph/probe and both named
  volumes remain. Restart/recreation is real; durable domain events are still B15.
- Future MCP/API/domain services consume typed methods, never raw Cypher inputs;
  auth, approvals, status transitions and trace envelopes remain their own gates.
  No agent/MCP/GraphRAG/API/frontend/importer was implemented. Tests use purpose-built
  synthetic fixtures, not hidden ground truth or full-city ingestion.

### B03-R — Actual corrective file/import/control flow | 2026-10-17
- targets.py provides exact canonical / milestone02–25 UUIDv4 name validation;
  MigrationRunner and GraphRepository import the same guard before selecting any
  graph. No registry/migration0001 change; no B01/document/checkpoint target admitted.
- graph_access.json v2 adds IN_ZONE/PART_OF outgoing singleton policies and route/
  service schedule applicability. Existing locked relationship policy invokes
  _schedule_policies on HAS_SCHEDULE writes; schedule service/date node updates
  inspect incoming edges and revalidate the affected routes before fenced commit.
  Effective interval = edge interval intersect schedule-node interval. Different
  services/date windows remain valid; opaque recurring text proves no compatibility.
- QueryRequest(default total6) -> policy per-template/root minimum/maximum -> typed
  QueryBudget -> fixed connectors subtracted from native bounded DRAINS_TO grammar
  -> total-path filter + existing scope/time/evidence/revision checks -> GraphResult
  search_budget/search_limited + independent output truncated. Fixed branches are
  selected by exact lengths (maintenance1/2/2/3, ownership1/1/2/1). Invalid budget
  yields explicit error; empty bounded search never asserts global absence.
- Actual changed runtime modules: targets.py (new), migration.py/repository.py,
  models.py/queries.py; normative graph-access policy + graph/runbook docs. New
  unit/integration correction modules exercise real isolated graph writes/queries.
  Existing B01/B02/B03 tests/evidence and review ZIP are retained unchanged.
- backend/B04_BENCHMARK_PLAN.md documents the future pilot/full/repeat benchmark,
  O(E_k²) repeated scans and O(N²) audit serialization costs. It performs no import
  and supplies no bulk path; current writer fence/intent/audit/strict policy remains.

## B04 implemented conversion/import flow | 2026-10-17

- `scripts/generate_demo_seed.py` -> distinct `data/generated/source_city_v2.json`
  (revision2.1); originals under contracts are immutable. It imports the registry for
  required legacy shape, does not connect to DB or read evaluator truth.
- `backend/app/ingestion/__main__.py` imports conversion, audit, settings, connection,
  MigrationRunner and GraphRepository. `audit.py` is offline-only and reads source/
  manifest/scenario inventory; `conversion.py` imports Registry, digest and temporal
  interval helpers. No scenario oracle is imported by converter or importer.
- prepare: allowlisted source envelope -> explicit field rules/quarantine -> node
  reference order -> relationship/temporal/cardinality/DAG preflight -> final strict
  Registry validation -> deterministic NodeRecord/EdgeRecord manifest. Actual source
  pointers/hashes and field deltas remain outside runtime graph in conversion reports.
 18 hash-verified Markdown references become Document nodes; no PDF/measurement added.
- `importer.py` imports validated bundle, repository errors and graph target guard.
  B04-only UUID target -> operational0001 -> explicit pending-intent reconciliation ->
  dependency-ordered create/get nodes -> create/get relationships -> equality/hash
  no-op or explicit changed-source conflict -> complete count/hash/revision audit.
  All mutations pass existing lock/fence/intent/atomic commit and policy validation.
  Whole-file import is not atomic: completed prefixes persist and resume safely.
- `benchmark.py` invokes the same importer/repository on one pilot and three fresh
  full targets, twice repeats each unchanged source, records wall/latencies/scans/
  parameter bytes/audit/AOF/memory. Instrumentation adds overhead; no bulk path exists.
  Only its successful scratch graphs are deleted; final and failed graphs retained.
- `tests/ingestion_examples.py` supplies synthetic test shapes. Unit conversion tests
  exercise all42/47 types and original55 numbers; real integration tests cover every
  type, interruption, uncertain replies, concurrent imports, exact hashes and paths.
  Both SPEC scripts invoke `scripts/validate_dataset.py` in addition to frozen-source
  structure checks. Their outputs remain distinct from live DB proof.
- `data/ingestion/`: runtime city-v3 bundle; external input/conversion/generator delta
  manifests; offline source audit, scenario-readiness and release references;
  legacy-conversion/legacy-v1 preserve rejected originals. Reports must not be mounted
  as agent inputs. `contracts/dataset_ingestion.json` fixes this boundary.
- Persistence: existing Compose named volumes unchanged. B01 probe and canonical
  knowledge graph preserved; B04 city is retained in its isolated graph, not promoted
  to canonical. Restart/recreation regression rechecks volume retention. Actual graph
  names/counts/hashes are recorded in evidence, not assumed from source counts.
- Current product reach: data support for R01–R05/R09/R14/R15; no end-to-end requirement
  is completed by ingestion. MCP, agents, GraphRAG, operations, API and frontend remain
  later tasks. B05 is proposed only after human B04 review.

## B05 implemented file/control flow | 2026-10-17

```text
analysis.models -> existing graph GraphModel/NodeRecord/EdgeRecord/PathRecord
analysis.engine -> reader -> official Graph.ro_query + strict repository decoder
                -> cases (actual factor/history paths + lexicographic ranking)
analysis.counterfactual -> bounded complete Snapshot + ingestion.check_graph
                        -> migration0001 -> capability-owned CloneWriter
                        -> existing lock/fence/intent/commit/audit
                        -> GraphAnalysis before/after + source/change fingerprints
analysis.evaluation -> accepted B04 bundle/readiness (no oracle/reveal/catalog)
                    -> actual retained city read-only analysis + dependency report
analysis.__main__ -> controlled test-only source/evidence or actual city evaluation
 tests.b05_benchmark ->10 real read-only runs/workload + unchanged fingerprints
```

- Eight analysis modules provide strict request/result models, fixed bounded path
  queries, deterministic coverage/weak components/Kahn/case ranking, owned clone
  ablation and offline review CLI/evaluation. New contract graph_algorithms.json
  adds response/budget semantics; no existing stored schema or0001 change.
- Reader checks READY/pending/revision before/after, validates graph labels/fields/
  endpoint directions/evidence, applies UTC knowledge/half-open validity/status,
  caches evidence within each request, meters shared64-query/10000-step/5s deadline
  and existing6-hop/100-path/120-node/200-edge/1000ms caps. Proof IDs derive from ordered
  real application node/edge IDs; evidence/source properties and direction survive.
- Source write flow: NONE for algorithms/evaluation/benchmark. No recover_pending
  fence changes on source. Administrative B04 full-manifest verification is separate
  from bounded algorithm exports; it uses accepted <=5000-record source contract.
- Counterfactual factory mints only new B05 UUID target; validates/copies complete
  <=120node/200edge snapshot via normal repository. Every inherited writer session
  checks capability/target. DELETE only verified DRAINS_TO with CAS and existing
  intent+atomic revision/audit commit. Candidate additions use normal proof policies.
  Ledger/fingerprint checks reject unrecorded changes; unknown outcomes retain named
  clone and require explicit recovery/review. Only owned scratch cleanup; no source/
  B01/canonical/volume reset. Public fingerprints hash writer metadata.
- Real city data remains858nodes/1246edges and revision/audit2104.42 drainage claims
  stay CANDIDATE. B05 runtime output/evidence contains sanitized source facts, separate
  verified/exploratory results and B08/B09/B11/B19 data dependencies; no hidden truth,
  expected actions or delayed payload imports. Staged release remains B19.
- Frontend/MCP consumers can later map typed nodes/edges/ProofPath IDs, statuses,
  sources, dates, graph revision, gaps and measured budgets. No API/server/agent
  runtime integration is implemented here; DEC-004 envelopes/traces remain pending.

## B06 implemented runtime/control flow | 2026-10-17

```text
backend/mcp_runtime/package.json + package-lock.json -> npm ci -> official Node1.3.0
app.mcp.runtime -> trusted configure -> named read-only DB ACL + ignored0600 credentials
                -> empty temporary cwd + explicit child env + pinned Node entrypoint
app.mcp.broker.open_broker -> Python MCP2.3.0 Client/private stdio child
 -> initialize/protocol2025-11-25 -> tools/list -> exact7 names + schema hashes
 -> ReadBroker.tools() safe template request schemas / ReadBroker.call(dict)
 -> policy.Request strict/deny graph/tool/unknown fields -> serialized call budget
 -> internal fixed READY/revision/pending read via official tools/call
 -> four approved tools + fixed parameterized node/drainage query or capped schema
 -> GRAPH.RO_QUERY under graph-key ACL -> bounded text JSON -> typed models/registry
 -> post revision read unchanged -> ReadResult(raw facts, limits/candidate status)
 -> sanitized actual trace metadata -> operator proof JSON (not graph-backed traces yet)
context exit -> close SDK streams/stdin -> bounded child process-tree termination
```

New modules:runtime.py trusted setup/lifecycle config; policy.py strict request and
3 fixed Cypher templates (including internal revision); models.py result projections;
broker.py discovery/schema verification/authorization/traces/budgets/result validation;
__main__.py configure/proof CLI; __init__.py namespace. contract official_mcp.json pins
observed inventory, hashes, scope and limits. Makefile commands and backend/MCP.md
explain reproduction. No existing graph algorithm/repository/schema/migration edit.

Credential material flows only local0600 file -> explicit subprocess environment ->
authenticated graph-scoped DB account, never public call/result/trace. No TCP MCP
listener, resources/prompts/raw client interface for agent selection. Node initialization
needs INFO; GRAPH.QUERY/DELETE/LIST/admin and other graph keys denied by DB. Schema
storage labels stripped; canonical unknown fields rejected. No hidden evaluator files
read at runtime. Upstream arbitrary-query/delete tools remain discovered for operator
evidence but absent/rejected at broker. DB default developer account remains privileged.

ReadResult is a B06 official-fact result, not a replacement for18 B07 custom contracts,
B05 decision-grade algorithms or later frontend DTO. Node current state; edge half-open
validity/as_of with explicit raw candidate statuses. Actual revision read, never vendor
Graph version. Errors/timeouts invalidate session as documented; fresh owned context
reconnects, no automatic replay. Trace list/operator JSON is current evidence storage;
B07/B17 graph-backed envelope/persistence remains open. No agent rationale fabricated.
Existing graph/Browser volumes and original B01/B04/B05 evidence retained; ACL account
must be reprovisioned after DB recreation, generated local credential reused.

B06 temporal query compilation imports the accepted B03 GraphQueries._time_key;
all supplied/recorded UTC values compare at the same microsecond precision. Actual
boundary tests read retained edge dates without modifying them. Integration fault
injection corrupts an actual returned record only in the test process, validating
fail-closed unknown-property handling and subsequent fresh-session recovery.

Final B06 post-lifecycle proof executes configure -> actual MCP initialize/list/call
-> independent official Python read -> clean session shutdown. Separate administrative
read helper verifies all retained fingerprints and migration readiness. Source audit
compares86 original protected file hashes/direct pins, scans actual private values
without emitting them and checks child-process absence. Source diff excludes generated
evidence bodies (exact evidence paths inventoried separately); no B06 review ZIP.

## B07 implemented file/import/control flow | 2026-10-17

```text
scripts.rotate_b07_mcp -> admin ACL password replacement/CLIENT KILL
                       -> atomic private file -> old AUTH denial/new RO verification
mcp.civicly.contracts/models -> normative12 READ + shared context/envelope/trace schemas
mcp.civicly.runtime.configure -> admin0001 on separate new B07 trace graph
 -> storage.TraceMigration0002 -> OPERATIONAL additive indexes/constraints/own ledger
 -> dedicated trace graph+lock-key ACL/private config (source city credential unchanged)
mcp.civicly.server -> SDK2.3 lowlevel Server -> real stdio initialize/list/call
 -> strict wire args/_context -> service.CivicReadService -> ScopedClient/read-only city
 -> existing B05 GraphAnalysis reachability/cases + B03 GraphQueries maintenance
 -> fixed bounded registered pickup/road/direct-decision reads or explicit UNAVAILABLE
 -> shared validated result -> TraceStore atomic fenced ToolExecution+detail append
mcp.civicly.broker -> actual discovery/identity/input+output schema compatibility
 -> agent-safe civicly:: args -> server call -> strict result graph/proof validation
 -> persisted server output-hash verification -> separate parented BROKER observation
mcp.civicly.router -> civicly:: domain broker | official:: unchanged B06 read broker
 -> shared persisted trace metadata for both; vendor/domain result shapes distinct
```

Runtime/new files:contracts.py,models.py,storage.py,runtime.py,service.py,server.py,
broker.py,router.py,__main__.py,__init__.py. Additional storage migration0002 and shared
mcp_envelopes plus synchronized mcp_tools/API AgentTraceEvent schemas; no registryv3/
0001/source-dataset change. __main__ configure/proof is operator CLI only. New unit
and real integration tests cover strict boundaries/data gaps/trace/migration failures.

Source reads use rotated one-city readonly account; ScopedClient substitutes restricted
GRAPH.LIST with actual fixed READY lookup, never invented catalog success. Normal
repository catalog/registry checks still execute via RO_QUERY. Trace writer is separate
and cannot access city. Trace writes use existing session/fence/intent/CAS/audit and
atomic core/detail creation, with zero Redis automatic retries. Persisted data is
metadata/hashes/references, not raw arguments/output bodies. No cross-graph atomicity
claim; no source mutation. Server append precedes reply, broker append follows actual
validated receipt. Distinct execution IDs/parent preserve failed/corrupted observations.

Transport is private Python stdio; no model credentials/raw clients exposed by tool
schemas. Session budgets, serialization/timeout/restart behavior explicit. Model
rationale remains null. Procedure/memory/document/monitor capability gaps remain
UNAVAILABLE; external55 measurements have no legitimate location link. All42 drainage
links stay CANDIDATE. Shared node/edge/path IDs and evidence dates retain future API/UI
compatibility without implementing either. Trace records persist in existing DB volume,
separate trace graph referenced only by private configuration. No B08+ work.

Typed dependency mode is an optional read-RPC field, not a stored ontology change.
DRAINAGE(default) -> B05 directed reachability/BOTH bounded merge;
TYPED_DEPENDENCIES -> existing B05 forward dependencies (DRAINS_TO/UNDERLIES/COLLECTED_BY).
Unsupported reverse typed traversal is rejected by input schema. Legacy asset_ids
lists actual infrastructure assets only; full typed route/asset paths retain all IDs.
B07 proof includes actual waste→route and utility→road paths, candidate qualified.

Final verification flow:full426 tests -> actual DB restart/recreation -> trusted ACL
reprovision (same replacement credentials) -> read-only verify_b07 helper checks all
retained source hashes/B01/B05/canonical readiness and13 preexisting trace IDs -> fresh
actual custom initialize/tools-list/calls -> verified-vs-candidate and typed dependency
proof ->15 persisted server observations read back -> native0002 status93indexes/
186constraints total (2/4 additive) -> final source/secret/process audit. No source
mutation or B07 archive. Actual normalized SDK discovery included in operator proof.

## B07-R corrected history projection and query flow | 2026-10-17

- service.py imports the existing GraphQueries._time_key; schema.timestamp supplies
  normalized UTC parameters. history_query selects one of two fixed label/relation/date
  triples. RO_QUERY MATCH + optional typed Evidence -> visibility + requested date
  WHERE -> normalized chronological ORDER BY/time+eventID+edgeID -> LIMIT101 -> strict
  repository decode ->100 rows -> atomic record/Evidence export within existing caps.
- maintenance_history still calls B03 GraphQueries; maintenance_evidence intersects
  each event's path prefix with validated edges/Evidence, extending Inspection through
  PRODUCED only. Aggregate project evidence stays at envelope level.
- result() records operational field gaps before WorkOrder lookup. server.py appends
  absence/failure gaps without replacing capability gaps. Normal SDK/broker validation,
  durable SERVER observation, hash read-back and child BROKER observation unchanged.
- New tests/unit/test_civicly_mcp_history_projection.py exercises pure projection with structural
  fakes. integration/test_civicly_mcp_review.py creates canonical-validated disposable
  fixtures -> tests.b07r_server build() real SDK stdio -> unchanged DomainBroker +
  actual TraceStore. Source substitution is explicitly test-only; production CITY_GRAPH
  and readonly ACL unchanged. No dataset/policy/migration/algorithm edits.
- docs/evidence/B07R-* preserves before/after output/commands/patch; audit_b07r.py checks
  accepted working-tree hashes and actual private values without printing secrets.
  Full existing lifecycle/official/domain tests and fresh retained-source checks follow.

B07-R final verification flow:440-test full regression -> actual restart/recreation
(including B01/Browser volume) -> existing ACL reprovision -> production CITY_GRAPH
SDK initialize/list/all12 calls/15 trace readbacks -> verify_b07.py all retained
source/metadata fingerprints +13 earlier traces -> verify_b07r_traces.py actual log
ordering and fresh readback of15 final B07 +4 before +11 corrected observations ->
audit_b07r.py333 preserved old files, unchanged wire contracts, actual local-secret/
process checks -> B07-R-only inventory/patch. No source/volume reset or new migration.

## B08 actual file/import and data/control flow | 2026-10-17

```text
services.complaints.models -> strict Pydantic union/normalization/units/original/hash
services.complaints.reader -> existing GraphRepository.RO +B03 GraphQueries histories
                          -> B05 GraphAnalysis verified forward/upstream topology
services.complaints.service -> normalize +references +stable external ID
 -> repo.create_node(Evidence PREPARED journal) [separate fenced commit]
 -> repo._session -> actual bounded context +three validators +event/cluster plan
 -> complaints.writer -> exact registry +identity/endpoints/evidence/cardinality
 -> repo._commit -> one atomic approved domain batch +COMMITTED receipt +revision/audit
 -> strict actual relationship/evidence readback -> typed historical receipt
retry -> same journal hash -> PREPARED resumes current plan | COMMITTED verified replay
regroup -> trusted Review+CAS -> close old PART_OF/add replacement+review receipt atomically
preview -> bounded RO plan +preview flag/proposed IDs; no source write
```

New package has models.py,reader.py,writer.py,service.py,__init__.py; no broad scaffold.
New complaint_intake contract mirrors models/rules; no registry/0001/0002 changes.
No MCP module changes: actual fixture server tests.b08_server calls same SDK build()
with test-only source substitution; production scope/broker/TraceStore remain unchanged.
New b08_fixtures and tests exercise real DB failure/concurrency/typed history;
tests.b08_evidence creates retained synthetic graph and verifies exact fingerprint/
receipt replay after real container lifecycle. Source City/B01/B05/traces independently
verified. audit_b08.py checks all accepted files/pins/tests against baseline and
local-secret/process exclusions; exact source patch/file inventory under docs/evidence.
No domain-event worker/outbox, public API, agent, hypothesis lifecycle or frontend.

B08 final verification:507-test complete regression -> real restart/recreation +Browser
volume -> fresh retained B08 fingerprint against pre-retry owner/epoch anchor ->5
receipt replays no domain changes -> re-provision same MCP ACL credentials -> actual
production-city initialize/list/all12 reads/15 server trace readbacks -> verify_b08.py
all2104 city records/B01/B05/native schemas +43 accepted trace hashes -> preserve fresh
B07-R regression proof/restore accepted artifact -> audit_b08.py358 original files and
private-value/process check -> exact B08 source patch/file inventory. No later feature.

## B09 actual file/import and data/control flow | 2026-10-17

```text
services.evidence.models -> strict command union/Actor/Review/Report/Assessment/Receipt
services.evidence.policies -> versioned3-issue verification criteria/typed primary assets
services.evidence.reader -> GraphRepository.GRAPH.RO_QUERY +B03 microsecond time keys
                        -> B05 GraphAnalysis topology/historical cases (unchanged)
services.evidence.service -> typed command/role/target -> PREPARED Evidence journal
 -> repo._session fence/recovery -> current CAS +normative state transitions
 -> bounded actual references +report/original-command/finding provenance checks
 -> requested/prior/discovered evidence union -> as_of filter -> deterministic label
 -> evidence.writer -> registry/endpoints/B03 policies/global+batch IDs -> repo._commit
 -> one atomic nodes/edges/entity update +COMMITTED receipt +revision/audit/clear intent
 -> actual receipt/assessment/path readback -> typed historical acknowledgment
history -> validated proposal source -> append-only snapshots ordered time/revision/ID
inspection -> typed pending/unavailable/conducted/findings view +pre/post revision check
```

New package: __init__.py,models.py,policies.py,reader.py,writer.py,service.py.
New evidence_hypotheses contract mirrors runtime models/policies; EVIDENCE.md documents
limits, trust and active-graph gate. No schema/migration/dependency changes.
Tests.b09_fixtures creates actual B08 intake then explicitly copies stable records
into owned B09 graphs and verifies source hashes; no source guard bypass.
Tests.b09_server only substitutes disposable source in real SDK/broker/TraceStore,
production unchanged. b09_evidence retains a small source/working graph and immutable
verification→contradiction history for real restart/recreation read-only fingerprint
comparison. verify_b09.py checks city/B01/B05/native schemas plus accepted B07/B08
traces/intake; audit_b09.py protects accepted source/tests/data/pins and checks secrets.
No B10 agent/checkpoint, B11 GraphRAG, dispatch/monitor/worker/API/frontend.

B09 final verification flow:582 regression -> actual FalkorDB restart/recreation and
Browser volume/HTTP200 -> same-credential ACL provisioning -> fresh official MCP
5 reads/5 denials +independent equality; production domain list12/call12/15 readbacks
-> read-only retained B09/source exact fingerprints/history -> original B08 fingerprint
+five historical replays -> verify_b09.py with latest B08 owner/epoch anchor -> city/
B01/B05/native schemas +70 accepted trace observations -> restore accepted generated
B07R/B08 proof bytes/save fresh B09 copies -> frozen source/secret/process audit ->
file inventory/source patch and both SPEC validators. Canonical domain nodes remain0.
No B10 or later phase; full results and failures remain reviewable in docs/evidence.
