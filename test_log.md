# test_log.md — Append-only verification record

## Current status — 2026-10-17 (takes precedence over historical entries)

B02 final acceptance: 53 PASS / 0 FAIL / 0 SKIP, including real DB and restart/recreation. Both SPEC validators PASS with explicit legacy warnings. Canonical 0001 READY: 91 index groups / 182 constraints OPERATIONAL. Prior failures/recovery preserved below; fixture import remains blocked.

---

No runtime tests have been run. Specification structure will be validated when the handoff is produced.

## Template
### TEST-YYYYMMDD-001 / Bxx
- Environment: OS, Python/Node/DB versions, image digests:
- Command (exact):
- Test class: SPEC / UNIT / INTEGRATION_DB / INTEGRATION_MCP / LIVE_AGENT / API / RESTART / SECURITY / E2E:
- Expected:
- Observed result and exit code:
- Evidence/log path / committed fixture:
- Status: PASS / FAIL / SKIP (reason):

### TEST-20261017-SPEC / blueprint generation (spec-only, not backend)
- Commands: `python scripts/validate_blueprint.py`; `python scripts/validate_handoff.py`; `python -m compileall -q scripts`.
- Expected: JSON/registry cross-references, expanded seed, scenario binding and document hashes valid.
- Observed: PASS (see final handoff README for counts), no FalkorDB/MCP/GraphRAG/agent runtime invoked.
- Status: PASS SPEC ONLY.

### TEST-20261017-B00-01 — Initial baseline / environment
- SPEC/environment: `python --version` FAIL (absent); `python3 --version` = 3.14.7.
- `python3 scripts/validate_blueprint.py`: FAIL exit 1, missing jsonschema. `python3 scripts/validate_handoff.py`: exit 0 but skipped meta-validation; script silently accumulates unavailable-jsonschema warning, so this is not full validation.
- `python3.12 --version` = 3.12.1; `python3.12 -c 'import importlib.metadata; print(importlib.metadata.version("jsonschema"))'` = 4.26.0.
- `node --version` = v24.21.0; `npm --version` = 12.2.0; `docker compose version` = v5.6.0; `uv --version` absent. `git status --short` FAIL exit 128, not a Git repo.
- `docker version`: initial sandbox permission denial; read-only escalated retry PASS exit 0, Desktop 4.95.0 (242831), Client/Engine 29.8.2, linux/arm64 server. No containers created.
- importlib.metadata in Python 3.12: jsonschema 4.26.0, pydantic 2.13.5, fastapi 0.141.1, httpx 0.27.0; falkordb/langgraph/langchain-falkordb/mcp/graphrag-sdk/pytest absent. Observations, not pins.
- Selected MODEL_PROVIDER/MODEL_ID/provider keys/MCP_API_KEY/AUTH_SECRET: UNSET in process; values not printed. Credentials elsewhere not searched.
### TEST-20261017-B00-02 — Full supplied validators / PASS SPEC
- `python3.12 scripts/validate_blueprint.py`: PASS exit 0, 42 nodes types; 47 edge types; 18 MCP tools; 9 machines; 4 scenario contracts; 40 base nodes/50 edges; 18 objectives traced.
- `python3.12 scripts/validate_handoff.py`: PASS exit 0, 42 entities/47 relationships/18 tools/43 routes/57 schemas/20 events; 838 expanded nodes/1245 edges/12 scenarios/18 source documents; logs/microtasks/WorkOrder initial approval invariant.
- No DB/MCP/AI runtime implied; unknown expanded properties not checked by these validators.
### TEST-20261017-B00-03 — Static source/integrity inspection / PASS
- Executed ast.parse on all five scripts; no generator executed. Parsed contract structures and scanned expanded node enums/node+edge property membership.
- All 73 manifest.json SHA256 entries matched before audit edits. Six tracking hashes intentionally stale after append-only audit; original handoff manifest preserved. data/documents manifest remains validated.
### TEST-20261017-B00-04 — Expanded property membership / FAIL
- Found 55 Observation.value_number unknown properties (OBS-0100–OBS-0154); no other unknown node/edge fields or invalid node enum values in this limited scan. Not a full schema-validity claim.
- Exact minimal reproduction (expected to fail until corrected):
```sh
python3.12 - <<'PY'
import json
from pathlib import Path
r = json.loads(Path('contracts/schema_registry.json').read_text())
s = json.loads(Path('contracts/seed_graph_expanded.json').read_text())
bad = [(n['properties']['id'], k) for n in s['nodes'] for k in n['properties']
       if k not in r['node_types'][n['label']]['properties']]
print('Unknown node properties:', len(bad), bad[:3])
assert not bad, 'Expanded seed has fields absent from schema registry'
PY
```
- Expected: 55, first entries OBS-0100/0101/0102 value_number, AssertionError exit 1. Other audited gaps in DEC-004.
- UNIT/mock, INTEGRATION_DB/MCP, RESTART, GraphRAG, LIVE_AGENT, API/E2E: NOT RUN, outside B00/no implementation. Exact planned compatibility commands in decision.md; no fake output substituted.

### TEST-20261017-B00-05 — Post-edit verification
- Re-ran both Python 3.12 validators after tracking updates: PASS, exit 0, unchanged counts.
- Executed -04 minimal reproduction: FAIL as expected, exit 1; 55 unknown fields and AssertionError. Confirmed normative Observation.value type is number. Defect remains OPEN; no fixture correction attempted in B00.
- Initial audit-log append command failed at shell parsing (unmatched heredoc delimiter); corrected delimiter and successfully appended all six files. No application changes occurred.

### TEST-20261017-B01-01 — Setup and inspected versions / PASS (with recovered attempts)
- Python 3.12.1 macOS 26.5 arm64; Docker Desktop 4.95.0/Engine 29.8.2/Compose 5.6.0.
- `python3.12 -m venv backend/.venv`: PASS. Initial `backend/.venv/bin/python -m pip install falkordb fastapi pydantic-settings pytest httpx jsonschema` in sandbox: FAIL network/DNS. Escalated `backend/.venv/bin/python -m pip install --no-cache-dir falkordb fastapi pydantic-settings pytest httpx jsonschema uv`: PASS, isolated only.
- `git init -b main`: initial sandbox FAIL permission, escalated retry PASS (no commit/remote). `docker ps --format '{{.Names}} {{.Ports}}'` found no running containers; `docker image ls falkordb/falkordb --digests` found local 6.0.2 image.
- `docker image inspect falkordb/falkordb:6.0.2 --format '{{json .RepoDigests}} {{json .Config.Entrypoint}} {{json .Config.Cmd}} {{json .Config.Env}} {{.Architecture}}'`: official digest 107455e862a824e45e8e9f5a7fbfdf5e00a08b14e13eae2577c72fd9e3f59ba6, arm64, entrypoint /var/lib/falkordb/bin/run.sh. This image-only inspection occurred before any local secrets were configured.
- `docker run --rm --entrypoint sh falkordb/falkordb:6.0.2 -c 'cat /var/lib/falkordb/bin/run.sh; ls -la /var/lib/falkordb/bin; ls -la /var/lib/falkordb'`: PASS. An earlier attempt using /usr/local/bin/docker-entrypoint.sh and /FalkorDB/conf/redis.conf failed missing paths; corrected from actual image metadata.
- Temporary /private/tmp/civicly-compose-spike.yaml used project name civicly, image 6.0.2, loopback ports, AOF + named graph volume. `docker compose -f /private/tmp/civicly-compose-spike.yaml up -d --wait --wait-timeout 90`: PASS. Final compose.yaml replaced the spike configuration, retained graph volume, added Browser persistence/secrets and digest.
- Inspected installed Graph.query/ro_query signatures and source using inspect.signature/getsource; actual scalar params + timeout=1000 work. Spike created/read B01-SPIKE in isolated civicly_b01_spike, observed expected RO denial, then deleted only that disposable graph.
- Direct dependency versions and official sources in DEC-006. No model or agent compatibility inferred.

### TEST-20261017-B01-02 — Lock/install/config reproducibility / PASS
- `python3.12 scripts/configure_local.py`: created ignored .env mode 0600, values hidden. Repeated invocation preserves exact file SHA256; permissions asserted 0600. `git check-ignore .env backend/.venv/bin/python`: both ignored.
- `UV_CACHE_DIR=.uv-cache backend/.venv/bin/uv lock --project backend --python python3.12`: PASS, resolved 34 packages.
- `UV_CACHE_DIR=.uv-cache backend/.venv/bin/uv sync --project backend --frozen --python python3.12`: PASS, installed editable backend. `backend/.venv/bin/python -m pip check`: PASS, no broken requirements.
- `UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=/private/tmp/civicly-b01-locked-env backend/.venv/bin/uv sync --project backend --frozen --python python3.12`: PASS, new clean env installed 33 packages.
- `UV_CACHE_DIR=.uv-cache backend/.venv/bin/uv pip check --python /private/tmp/civicly-b01-locked-env/bin/python`: PASS, 33 packages compatible. `/private/tmp/civicly-b01-locked-env/bin/python -m pytest backend/tests/unit -v`: 7 PASS.
- `make setup`: PASS, documented venv + uv install + frozen sync. Pins/hashes in backend/pyproject.toml and backend/uv.lock. Clean install verified on this Mac, not other platforms or future integration dependencies.

### TEST-20261017-B01-03 — Unit and real integration / recovered FAIL then PASS
- UNIT/framework compatibility: `backend/.venv/bin/python -m pytest backend/tests/unit -v`: 7 PASS, exit 0. No fake LLM used. Temporary framework-only ASGI app validates FastAPI/Pydantic/httpx integration; no actual Civicly API implemented.
- INTEGRATION_DB/Browser/CLI: `backend/.venv/bin/python -m pytest backend/tests/integration -v -m 'not persistence'`: first run 2 FAIL (fresh canonical graph health + CLI), 4 PASS, 1 deselected, exit 1.
- Minimal error: missing graph RO_QUERY returns `Invalid graph operation on empty key`. DEC-006 documents observational correction, not a bypass via writes. Re-run: 7 PASS, 1 deselected, exit 0 (extra uninitialized-graph regression added).
- Real CREATE/MATCH stores quoted/injection-shaped synthetic string as parameter value and reads identical value. RO_QUERY attempts CREATE/SET/DELETE all return `graph.RO_QUERY is to be executed only on read-only queries`; final unchanged node read proves no mutation.
- CLI success, DB unavailable failure exit 1, invalid configuration exit 2 and redaction tested. No missing service silently skipped.

### TEST-20261017-B01-04 — Container lifecycle / real RESTART + INTEGRATION_DB / PASS
- `docker compose config --quiet`: PASS. `docker compose up -d --wait --wait-timeout 120`: PASS with both named volumes and Browser secrets.
- `backend/.venv/bin/python -m pytest backend/tests/integration/test_persistence.py -v -s --run-persistence`: 1 PASS in 13.54s.
- Test subprocess commands (real): `docker compose --project-directory /Users/vikashkumar/Desktop/Civicly -f /Users/vikashkumar/Desktop/Civicly/compose.yaml restart falkordb`; then same prefix `up -d --wait --wait-timeout 120 falkordb`; then `up -d --force-recreate --wait --wait-timeout 120 falkordb`.
- Same ID after restart; different nonempty ID after recreation. Before/after each: new client parameterized MATCH returned SYNTHETIC-B01, persistence configuration asserted dir=/var/lib/falkordb/data, appendonly=yes, appendfsync=always. Browser HTTP 200 and persisted synthetic .data marker both PASS. Test graph/marker cleaned; no volume deletion or canonical writes.
- Final consolidated command: `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence` (stdout recorded with pipefail/tee docs/evidence/B01-tests.txt): **15 PASS in 14.84s**, exit 0. Seven unit + seven ordinary real integration + one real lifecycle. No skipped tests in this acceptance run. Lifecycle ran on actual container again, not replayed output.

### TEST-20261017-B01-05 — Actual CLI, Browser and inspection node / PASS
- Explicit inspection-node creation (run once on a fresh setup; kept for human verification):
```sh
backend/.venv/bin/python - <<'PY'
from app.config import Settings
from app.graph.connection import connect
with connect(Settings(_env_file='.env')) as c:
    g = c.select_graph('civicly_b01_runtime')
    print(g.query('CREATE (n:B01Probe {id:$id, source_kind:$source, task:$task}) RETURN n.id,n.source_kind,n.task', params={'id':'B01-PERSISTENCE','source':'SYNTHETIC','task':'B01'}, timeout=1000).result_set)
PY
```
- Observed row: [['B01-PERSISTENCE', 'SYNTHETIC', 'B01']]. Isolated test graph, no domain fixture import. Don't repeat CREATE on the existing graph; use the read query below.
- `backend/.venv/bin/civicly health`: PASS exit 0; scope backend_foundation, graph civicly_knowledge, graph_state uninitialized, PING/module true, graph_read null.
- `FALKORDB_GRAPH=civicly_b01_runtime backend/.venv/bin/civicly health`: PASS exit 0; graph_state available, PING/module/read true.
- Final fresh `ro_query('MATCH (n:B01Probe {id:$id}) RETURN n.id,n.source_kind,n.task LIMIT 1', params={'id':'B01-PERSISTENCE'}, timeout=1000)` after recreation returned same inspection row; only civicly_b01_runtime graph exists. Exact observed outputs in docs/evidence/B01-runtime.txt, UTC 2026-10-17T00:58:35.
- `docker compose ps`: civicly-falkordb-1 healthy; only 127.0.0.1:6379/3000 published. `docker image inspect falkordb/falkordb:6.0.2 --format '{{json .RepoDigests}} {{.Architecture}}'`: same pinned digest, arm64. `docker compose exec -T falkordb node -e 'console.log("Browser version:", require("/var/lib/falkordb/browser/package.json").version)'`: Browser 2.6.1.
- CUA actual Browser at http://127.0.0.1:3000: logged in with local host 127.0.0.1 / internal port 6379; server v6.00.02 online. After recreation reload remained authenticated and graph view/table returned one B01Probe with id/source/task above. Persistent API-token file observed in mounted Browser .data (contents never printed). Screenshot docs/evidence/B01-browser.jpg. This is actual Browser verification, not just an HTTP landing-page check.

### TEST-20261017-B01-06 — Regression / limits
- `backend/.venv/bin/python -m compileall -q backend/app backend/cli backend/tests scripts/configure_local.py`: PASS.
- `make test-spec` invokes `backend/.venv/bin/python scripts/validate_blueprint.py` and `backend/.venv/bin/python scripts/validate_handoff.py`: both PASS, exit 0; unchanged counts (42/47/18, 838 nodes/1245 edges, 12 scenarios, 18 docs). No contract corrections implied.
- NOT RUN (outside B01): graph migrations/constraints, domain ingestion, actual runtime MCP/LLM/checkpoints/GraphRAG, approval/work-order tests, event durability/SSE/API/E2E. No mock counted as live integration. Persistence test is opt-in on default pytest runs; acceptance used explicit opt-in and passed.
- Known FAIL remains B00 expanded membership (55 value_number unknown fields); BLOCK-B00-02 OPEN and DEC-004 findings retained.
- Human verification: from repository root, run `make health`, `make test-graph`, `make test-persistence`, `make test-spec`; Browser host 127.0.0.1 / port 6379 -> civicly_b01_runtime -> bounded MATCH query in backend/README. Expected 7 ordinary integration PASS, 1 lifecycle PASS, both SPEC PASS; no provider key needed. Failure artifacts: test_log.md, blockers.md, failing output, redacted compose logs; never .env.

- Post-documentation check: repeated `make test-spec` PASS. Compared all original manifest entry hashes: only README and six tracking files changed; all original contracts/data and backend requirement docs unchanged. Expanded membership scan still has exactly 55 defects. `git check-ignore .env backend/.venv/bin/python .uv-cache` confirms local artifacts ignored.
- `/private/tmp/civicly-b01-locked-env/bin/civicly health`: PASS against actual local database using the clean environment's console entrypoint (status ok, canonical graph explicitly uninitialized).

### TEST-20261017-B02-01 — Baseline and official-version spikes
- Environment unchanged: Python3.12.1 macOS26.5 arm64; official falkordb1.8.0/redis8.1.0; Docker Engine29.8.2/Compose5.6.0; graph60002 (6.0.2), Redis8.10.2, Browser2.6.1, immutable B01 image digest retained.
- Baseline scan command: Python Path/git ls-files --others --exclude-standard -z + ignored dotenv secret values/private-key marker scan. PASS102 candidate files, no secret values/.env/venv/caches. `git check-ignore .env backend/.venv/bin/python .uv-cache`: all ignored.
- `git add .`; `git diff --cached --check`: original docs/demo/SCENARIOS.md trailing blank-line warning, preserved source content. `git -c user.name='Civicly Local Build' -c user.email='civicly-local@example.invalid' commit -m 'Baseline accepted B01 backend foundation and specification'`: PASS root commit426f6e1322dca9e83e470ee471b25b8df7f9e028,102 files. `git status --short`: clean. No remote/push.
- Official pages read: graph.constraint-create, cypher/indexing/range-index, cypher/known-limitations. Incorrect graph.constraint-list URL inaccessible; readiness documented as db.constraints().
- Real disposable spike failures: `inspect.signature(FalkorDB.create_constraint)` -> AttributeError (helper absent); attempted QueryResult.statistics -> AttributeError. Corrected to execute_command and result_set/header, preserving installed versions.
- Exact accepted DDL patterns: `CREATE INDEX FOR (n:Spike) ON (n.id)`; `CREATE INDEX FOR ()-[r:SPIKE_EDGE]-() ON (r.id)`; `client.execute_command('GRAPH.CONSTRAINT','CREATE',graph_name,'UNIQUE','NODE','Spike','PROPERTIES',1,'id')`; analogous MANDATORY node/relationship and UNIQUE relationship calls. Returned PENDING; actual db.indexes/db.constraints rows OPERATIONAL. Multi-label CREATE, parameter map SET and native point writes PASS. Only random spike graph removed.
- First runner spike `CALL db.indexes() YIELD * RETURN * LIMIT 513` -> ResponseError invalid '*'; corrected to explicit verified columns. Disposable full apply/rerun then PASS91 indexes/182 constraints. No canonical data touched during spikes.

### TEST-20261017-B02-02 — Strict validation and preserved fixture blocker
- `backend/.venv/bin/python -m pytest backend/tests/unit -v`: first31 PASS/1 FAIL because added asset_type constants rejected five legacy values beyond55 known defects. DEC-008 removed premature taxonomy change; no fixtures changed. Next32 PASS. Added oversized numeric guard, yielding final33 unit tests.
- Canonical validator rejects unknown fields, absent required values, wrong primitive types (including bool masquerading as integer/number), bad enums, nonfinite/oversized numeric values, invalid scope/alias/version/ID, malformed/non-UTC times and temporal intervals.
- Explicit test-only conversion of legacy node scope/version preserves every source property; all55 OBS-0100–OBS-0154 value_number records remain rejected, remaining783 fixture nodes validate. Original unconverted source is rejected. This is not an importer or permission to ingest data.
- Normative scope metadata equality tested across registry/state/MCP/API/event contracts; public names/endpoints/enums checked against baseline unchanged. Existing mandatory requirements retained and v3 scope/edge metadata additions documented.

### TEST-20261017-B02-03 — Real DB migrations/constraints and recovery / PASS
- `backend/.venv/bin/python -m pytest backend/tests/integration/test_schema_migrations.py -v -s`: initial8 PASS in20.90s. Added limitation/preexisting-index/missing-support tests; combined unit/integration command below44 PASS.
- `backend/.venv/bin/python -m pytest backend/tests/unit backend/tests/integration/test_schema_migrations.py -v -s` (tee docs/evidence/B02-schema-tests.txt):44 PASS in22.58s, exit0. All DB assertions use actual FalkorDB.
- Verified 91 index groups/182 constraints OPERATIONAL, safe rerun, zero domain seed nodes, six typed infrastructure subtypes with both parent labels, cross-subtype duplicate ID rejected, grouped mandatory missing-field rejected, native-point index/readback and ID Index Scan EXPLAIN.
- Real relationship writes preserve id/scope/time/evidence metadata. DB refuses duplicate edge ID and missing mandatory metadata. Adapter refuses invalid endpoints, UNDERLIES reversal, self-drain, unknown fields/enums and invalid time/evidence-free VERIFIED. No physical causal verification claimed; reference-existence checks remain B03+.
- Failure tests: interruption injected only after real successful index operations (no fake DB responses); partial schema retained, FAILED audit preserved, fresh runner finishes. Actual duplicate rows cause asynchronous constraint FAILED; both records retained; normal rerun refuses until explicit retry after non-destructive identifier repair. Constraint recreation reaches OPERATIONAL.
- Schema lease contention, registry hash drift, applied checksum tampering/future version rejected. Supporting-index absence produces actual server error. Native raw unknown-property acceptance proven to document application validation requirement.

### TEST-20261017-B02-04 — Canonical apply and rerun / PASS
- `make migrate` -> official-client additive canonical migration0001: PASS exit0; registry3, municipality_id demo-city, ready=true,91 index groups/182 constraints, attempts1. Output docs/evidence/B02-canonical-apply.txt.
- `make migrate` repeated: PASS exit0, attempts2, same checksums/counts, no domain nodes created. Output B02-canonical-rerun.txt.
- `make schema-status`: PASS exit0, ready=true and every expected object verified, output B02-canonical-status.txt. `make health`: graph_state available, PING/module/read true.
- Migration checksum94ab9fae6079fe7e87b41afd80701409db6bb51d529c2565dbd340896a5c923b; registry checksum12541990b58d65e8602bff77b93b735009616e7ee658b9e7582a7ae9f449aac6.
- Direct post-restart catalog read (MigrationRunner.status/_catalog via official client) saved docs/evidence/B02-schema-catalog.json:91 OPERATIONAL RANGE groups/304 property entries;182 OPERATIONAL constraints; canonical domain nodes0; B01 probe [['B01-PERSISTENCE','SYNTHETIC','B01']]. Only civicly_b01_runtime and civicly_knowledge graphs remain. No volumes deleted.

### TEST-20261017-B02-05 — Final complete regression / PASS
- Exact command: `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence` (pipefail + tee docs/evidence/B02-all-tests.txt).
- **53 PASS /0 FAIL /0 SKIP in41.79s**, exit0:33 unit/framework tests +19 ordinary real DB/Browser/CLI integration tests +1 real restart/recreation lifecycle test.
- Existing B01 PING/health/parameterized CREATE/MATCH/RO denial/CLI redaction/Browser/volume behavior PASS. Same-container restart and replacement-container recreation retained data; canonical schema readiness confirmed after lifecycle. Added READY-marker-with-missing-constraint test shows real catalog drift detected and additive rerun restores missing constraint.
- No fake LLM used. Fault injection is an interruption after actual DDL, not mocked integration success. MCP/LLM/GraphRAG/checkpoint/domain operations/API/E2E remain NOT RUN, outside B02.

### TEST-20261017-B02-06 — Specification, dependency and diff checks
- `make test-spec` -> `backend/.venv/bin/python scripts/validate_blueprint.py` and `backend/.venv/bin/python scripts/validate_handoff.py`: PASS exit0;42 types/47 relationships/18 tools/9 machines;43 routes/57 schemas/20 events;838 nodes/1245 edges/12 scenarios/18 documents. Explicit legacy structure and55 known import defects warning, not canonical fixture acceptance. Results docs/evidence/B02-spec-validation.txt.
- Handoff validator now rejects new unknown expanded properties while explicitly tracking the exact55 B04 defect records; new v3 required fields are not invented for old source fixtures. JSON Schema meta-validation available and executed.
- `backend/.venv/bin/python -m pip check`: PASS no broken requirements. `UV_CACHE_DIR=.uv-cache backend/.venv/bin/uv lock --project backend --check`: PASS34 resolved entries unchanged.
- `backend/.venv/bin/python -m compileall -q backend/app backend/cli backend/tests scripts`: PASS. `git diff --check`: PASS for B02 diff. A documentation patch initially had an unmatched context and applied no changes; corrected patch succeeded.
- Baseline comparisons assert all supplied fixtures/data and R01–R18 requirement file unchanged, all public node/relationship names/endpoints and enum values retained. Exact B02 file list and diff recorded in docs/evidence/B02-files.txt and B02-git-diff.txt. Root manifest remains original handoff snapshot, not silently regenerated.
- Human verification: `make schema-status` -> ready true/version1/registry3; `make migrate` -> same schema and a new audit attempt only; `make health` -> existing canonical graph read true; run full command in -05 and `make test-spec`. Browser queries/recovery instructions in backend/SCHEMA.md. If failure, share test_log/blockers + command output, excluding .env.
