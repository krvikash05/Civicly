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
