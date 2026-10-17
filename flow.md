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
