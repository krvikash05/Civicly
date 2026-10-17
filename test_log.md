# test_log.md — Append-only verification record

## Current status — B07-R, 2026-10-17 (takes precedence over history)

B07 technically accepted. B07-R PASS — human review pending. Final440 PASS/0 FAIL/0 SKIP in368.60s (293 unit/147 real integration), adding5 unit+9 real cases; all426 accepted tests preserved. Both SPEC validators PASS. Independent maintenance provenance, pre-cap UTC history filtering/order/lookahead, and explicit unknown work-order fields verified through real MCP. Retained city/B01/B05/migrations/accepted+corrective traces preserved across actual restart/recreation. B08 TODO; no later work.

## Current status — B07, 2026-10-17 (takes precedence over history)

Final B01–B07 regression426 PASS/0 FAIL/0 SKIP in350.75s:288 unit/138 real integration. B07 adds33 unit+32 real cases; all original361 tests unchanged. Both SPEC validators PASS. Actual MCP proof after recreation, all retained fingerprints and13 preexisting trace records PASS. Unit/mock and AFTER-REAL-READ fault cases labeled; no live model rationale claimed.

## Current status — B06, 2026-10-17 (takes precedence over history)

Final B01–B06 regression361 PASS/0 FAIL/0 SKIP in329.97s:255 unit/106 real database/MCP integration. B06 adds37 unit+15 real cases; all original309 tests retained unchanged. Both SPEC validators PASS. Post-recreation MCP proof/independent read, full retained fingerprints and canonical readiness PASS. HTTP bearer auth not applicable to private stdio; no live model test.

## Current status — B05, 2026-10-17 (takes precedence over history)

Final B01–B05 regression309 PASS /0 FAIL /0 SKIP in246.23s:218 unit/91 real integration including real restart/recreation. B05 adds29 unit +22 real cases; all prior258 retained. Both SPEC validators PASS.260 measured read-only analyses and actual controlled/city outputs recorded; failed intermediate attempts retained below.

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

## TEST-20261017-B03-01 — Accepted B02 baseline / local Git
- User attachment accepts B02 and authorizes B03 only. Mandatory docs/registry/B02
  code reviewed. `backend/.venv/bin/civicly schema-status`: migration0001 READY,
  registry3,91 index groups/182 constraints OPERATIONAL. Fresh B01-PERSISTENCE MATCH
  retained. Canonical has0 domain nodes. Baseline safety scan46 B02 files excludes
  dotenv/venv/cache/runtime secrets and actual generated secret values.
- `git check-ignore .env backend/.venv/bin/python .uv-cache`: all ignored.
  `git diff --cached --check` flags whitespace context in retained B02-git-diff.txt;
  preserved historical evidence. `git add .` and `git commit -m "Baseline accepted B02 canonical schema and migrations"`:
  local baseline3db6d873fb494a5ce456cb5d04a84f2be50919d4; no remote push.
  B03 remains a reviewable working-tree diff against that baseline.

## TEST-20261017-B03-02 — Real runtime spikes / failed attempts
- Official docs + installed client inspected. Disposable graph spikes verified
  full-property equality CAS and actual multi-CREATE UNIQUE rollback; driver path
  nodes/edges retain ordered identities and physical source/destination; finite
  traversal, all(), zero-hop, parameter LIMIT execute on6.0.2. No canonical writes.
- `PYTHONPATH=backend backend/.venv/bin/python - <<'PY' ... PY` repository smoke:
  migrated B03 UUID graph; actual CREATE A/B and candidate DRAINS_TO AB; real read
  returned2 nodes/1 edge/1 path and revision3; graph removed in finally. Equivalent
  complete reproducible fixture/query spike is now `python -m tests.b03_evidence`.
- `backend/.venv/bin/python -m pytest backend/tests/integration/test_graph_access.py -x -q`:
  first1 PASS/1 FAIL: test supplied valid_to without required valid_from. Corrected
  test, existing B02 contract unchanged. Next17 PASS/1 FAIL: upstream metadata
  projection returned0 instead of actual52. Minimal real spike reproduced both
  values; changed query consistency mechanism as DEC-011. Next18 PASS in38.01s.
- Expanded integration attempt21 PASS/1 FAIL in46.65s: snapshot fixture used unknown
  condition_code rather than registry condition. Corrected fixture. No schema relaxed.
- `PYTHONPATH=backend backend/.venv/bin/python -m tests.b03_evidence > docs/evidence/B03-runtime.json`:
  initial FAIL TypeError (MigrationRunner requires explicit graph_name); corrected
  reporter call. Subsequent real report PASS with8 path examples and8 EXPLAIN plans.
- First combined `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence`:
  collection ERROR duplicate test_graph_access.py module basename (75 collected,
  no acceptance run). Renamed unit module to test_graph_access_models.py; retained
  output docs/evidence/B03-collection-failure.txt. Next combined run87 PASS in101.20s,
  including real lifecycle. Final review added candidate-pointer as_of exclusion
  and real native-point/temporal tests; targeted24 integration PASS in51.77s.
- Initial unit command `backend/.venv/bin/python -m pytest backend/tests/unit/test_graph_access.py -q`:
  12 PASS (before filename correction); current reproducible target uses _models.py.
  Fault injection only drops responses around actual DB statements, never returns
  mocked success. No fake model or live agent test was counted.

## TEST-20261017-B03-03 — Typed writes / integrity / concurrency
- Real tests cover strict unknown/type/enum/scope rejection; global node and cross-
  type edge IDs; actual endpoint existence/direction; property foreign references;
  evidence existence/reliability/attribution/date; immutable records; stale node/
  edge digests; point preservation; overlapping cardinality and disjoint history.
- Concurrent node CAS yields exactly1 success/1 stale rejection. Concurrent same edge
  ID across types yields1 success/1 Conflict. Concurrent active assignment yields
  1 success/1 Conflict; opposing drainage writes yield1 success/1 cycle rejection.
  Expired writer after successor fence cannot create its node. Task cycle rejected;
  explicit inspected drainage cycle accepted; disjoint historical reversal accepted.
- Actual failing second CREATE rolls back first domain node and revision/audit;
  pending intent recovered only after unchanged pre-state is proven. Lost response
  before statement leaves no node; lost response after actual commit leaves exactly
  one node with COMMITTED audit. Changed external pre-state keeps pending and blocks
  queries; no automatic erase or uncertain retry.

## TEST-20261017-B03-04 — Real bounded reads / serialized examples
- All8 query families return real paths, including upstream original edge orientation,
  common downstream D2/D3 for I1/I2, inspection/work-order/outcome history, support+
  contradiction evidence and tasks. All results serialize with stable IDs, subtype
  labels, properties, evidence IDs, edge direction, validity, as_of and revision.
- Waste cross-category path: W → LW ← D1 → D2 → D3 → LR ← R (7 nodes/6 edges);
  NEARBY uses a distinct LN location with identical coordinates but no SERVES link
  to the physical network; it is excluded.
  This is candidate connection context, not verified causation.
- Whole-second/fractional as_of/after, future updates/evidence and half-open valid_to
  tested. Hop/request caps, whole-path node caps, limit truncation, rejected raw
  Cypher/injection strings and configured750ms on real RO call verified. A write
  method trap confirms queries only use real GRAPH.RO_QUERY; B01 server tests also
  deny actual CREATE/SET/DELETE through RO without state change.
- Runtime report command above captures actual EXPLAIN Index Scan + bounded traverse
  plans. Reporter migration rerun on its disposable populated graph preserves
  repository revision53 and domain contents. canonical0 domain nodes and B01 probe
  retained; report records packages/server module and Browser HTTP200.

## TEST-20261017-B03-05 — Final acceptance and previous regressions
- Final command (pipefail, stdout retained):
  `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence | tee docs/evidence/B03-all-tests.txt`.
- **89 PASS /0 FAIL /0 SKIP in94.16s**, exit0:45 unit +44 real integration
  (including1 lifecycle). New B03 tests:12 unit +24 integration; all prior53 regressions
  retained. After strengthening the nearby fixture to a distinct equal-coordinate
  location with no physical-network links, all8 template cases were rerun separately
  (B03-template-tests.txt); this is supplemental, not double-counted acceptance.
- Regression suite includes actual container restart (same ID) and force recreation
  (different ID), fresh parameterized reads, Browser HTTP200 and Browser volume marker.
  No volume deletion or B01/canonical graph removal. Old53 tests remain in the run.
- Not run / outside B03: full city import/conversion, behavioral simulation, live
  LLM/MCP/GraphRAG/checkpoints, domain auth/approvals/work orders/outbox, API/frontend.
  These are unimplemented later gates, not skipped tests relabeled as passing.

## TEST-20261017-B03-06 — Specifications / dependencies / review evidence
- `make test-spec | tee docs/evidence/B03-spec-validation.txt`: both validators PASS.
  Counts unchanged42 entities/47 relations/18 tools/18 objectives; expanded legacy
  838 nodes/1245 edges/12 scenarios/18 documents. Explicit55-defect warning remains;
  static structural validity does not mean canonical import eligibility.
- `backend/.venv/bin/python -m pip check`: PASS, no broken requirements.
  `UV_CACHE_DIR=.uv-cache backend/.venv/bin/uv lock --project backend --check`: PASS,
  34 resolved packages unchanged. No dependency upgrade or remote publishing.
- Review inventory/diff and audit: docs/evidence/B03-files.txt, B03-git-diff.txt,
  B03-review-audit.txt. Existing registry/plan/data/geometry/document source files
  unchanged from accepted baseline. B03 source and all6 tracking files updated.

- Supplemental exact command: `backend/.venv/bin/python -m pytest backend/tests/integration/test_graph_access.py::test_all_preapproved_templates_real_results_and_readonly -v | tee docs/evidence/B03-template-tests.txt`:8 PASS in18.91s, exit0. Production source unchanged after the89-test acceptance; only equal-coordinate disconnected fixture/negative assertions strengthened.
- Final `make test-spec` rerun after documentation edits: both PASS; same55 warning. Post-lifecycle evidence reporter and `backend/.venv/bin/civicly schema-status > docs/evidence/B03-canonical-status.txt` confirm retained canonical readiness/probe without domain writes.

## TEST-20261017-B03R-01 — Corrective review baseline and boundaries
- B03 provisionally accepted by external review; user authorizes B03-R only. Read
  mandatory docs, registry3/plan0001, graph-access contract and actual implementations.
  DEC-012 records choices before source changes. Snapshot of138 pre-correction source/
  evidence files retained temporarily for a precise corrective diff, without a new
  Git commit. Original review ZIP/evidence preserved; no push or B04 import/repair.
- Confirmed omissions: IN_ZONE/PART_OF absent from outgoing singleton list;
  HAS_SCHEDULE only checked duplicate edges, not route/service applicability;
  hop grammar used h drainage links plus connectors while total filter used same h,
  making default4 impossible for cross-category minimum5. Divergent test target
  regexes hardcoded B02/B03. No public registry or migration content modified.

## TEST-20261017-B03R-02 — Unit and real corrective verification
- `backend/.venv/bin/python -m pytest backend/tests/unit -q`: initial45 PASS in0.41s
  (old units after source changes), then77 PASS in0.40s including32 new target/default
  budget cases. Invalid targets refused before client access; no mock success used.
- Exact real targeted command (pipefail):
  `backend/.venv/bin/python -m pytest backend/tests/integration/test_graph_review.py backend/tests/integration/test_graph_access.py -v -s | tee docs/evidence/B03-R-integration.txt`:
  **37 PASS in91.13s**, exit0 (13 initial corrective cases + all24 B03 integrations).
- Added fixed-template boundary test after counting exact branch lengths: maintenance
  branches1/2/2/3 edges (maximum3), hypothesis2 or3 according to root, ownership1/2.
  No recorded failing test attempt in B03-R; assertions/fixtures reviewed before runs.
- Real assertions cover primary zone/cluster overlapping rejection, nonoverlapping
  history, many incoming members; schedules with different services or nonoverlapping
  effective node+edge windows, conflicting/empty intervals, node/edge update safety,
  concurrent schedule conflict; five/six-edge default cross paths, seven-edge bounded
  negative, explicit too-small-budget errors and genuinely disconnected equal-
  coordinate assets; shared total1/zero-drain and total2/one-drain boundaries.
- Real migration and repository writes succeed in UUIDv4 milestone04 and25 disposable
  namespaces. These are authorization tests, not B04/B25 feature implementation or
  municipal ingestion. Cleanup deletes only each generated test graph.

## TEST-20261017-B03R-03 — Strengthened template acceptance
- Exact command (pipefail):
  `backend/.venv/bin/python -m pytest backend/tests/integration/test_graph_review.py backend/tests/integration/test_graph_access.py::test_all_preapproved_templates_real_results_and_readonly -v -s | tee docs/evidence/B03-R-template-tests.txt`.
- **22 PASS in55.64s**, exit0: all14 corrective integration cases plus eight original
  live template families. Typed requested/effective/min/max/connector/infrastructure
  budgets and search_limited match actual paths. Output truncation stays independent;
  bounded negatives do not claim global absence. Existing RO/parameterization/scope/
  temporal/evidence/revision checks remain. No fake DB or live agent claim.

## TEST-20261017-B03R-04 — Full regression / real lifecycle
- Exact command (pipefail):
  `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence | tee docs/evidence/B03-R-all-tests.txt`.
- **135 PASS /0 FAIL /0 SKIP in128.67s**, exit0:77 unit +58 actual integration
  (including1 opt-in lifecycle). All previous89 tests retained unchanged; additions
  are32 unit +14 real integration. Supplemental runs are not double-counted here.
- Real restart keeps container identity; force recreation changes it. Fresh MATCH,
  Browser HTTP200 and persisted Browser marker pass before/after both operations.
  No volume deletion or B01/canonical graph reset. Atomicity, lost replies, fence/CAS,
  duplicate IDs, failed migration/constraint recovery, strict schema, temporal/RO and
  original traversal regressions all pass. Graceful lifecycle is not crash/failover
  proof, domain event durability or agent memory verification.

## TEST-20261017-B03R-05 — SPEC, versions and final evidence
- `make test-spec | tee docs/evidence/B03-R-spec-validation.txt`: both validators PASS,
  exit0;42 types/47 relationships/18 tools/18 objectives; legacy838 nodes/1245 edges/
  12 scenarios/18 documents. Explicit55-defect warning remains; not canonical import.
- `backend/.venv/bin/python -m pip check`: PASS no broken requirements.
  `UV_CACHE_DIR=.uv-cache backend/.venv/bin/uv lock --project backend --check`: PASS,
  34 resolved packages unchanged. Python3.12.1, official falkordb1.8.0, redis8.1.0,
  Pydantic2.14.1, pytest9.1.1 retained; server6.0.2/module60002, Redis8.10.2 and
  Browser2.6.1/image digest unchanged. No dependency upgrades.
- Post-lifecycle commands:
  `PYTHONPATH=backend backend/.venv/bin/python -m tests.b03_evidence > docs/evidence/B03-R-runtime.json`;
  `backend/.venv/bin/civicly schema-status > docs/evidence/B03-R-canonical-status.txt`.
  Actual new budget DTOs, eight results/EXPLAIN plans and retained canonical/B01
  evidence captured. Canonical0001 READY, registry3,91 index groups/182 constraints
  OPERATIONAL,0 canonical domain nodes; B01-PERSISTENCE preserved.
- Snapshot audit/diff: B03-R-files.txt, B03-R-changes.patch, B03-R-review-audit.json.
  Registry/plan/fixtures/old tests/old evidence/review ZIP unchanged; secrets excluded.
  No B04 benchmark executed: backend/B04_BENCHMARK_PLAN.md is a future plan with
  explicit estimated costs and proposed targets, not measured ingestion performance.
- Not run (outside B03-R): full conversion/import, bulk optimization, live MCP/LLM/
  LangGraph/GraphRAG, operational workflows, API/frontend. BLOCK-B00-02 and deferred
  DEC-004 findings remain OPEN. Stop for human review before B04.

- Final snapshot audit first stopped on an additional untracked Civicly_B03_Review/
  directory appearing after the initial snapshot. Read-only comparison confirmed
  all87 entries match the original ZIP. Preserved this separate extracted review
  copy and explicitly excluded it from the corrective source diff; no application
  change or test failure resulted. Final source/secret/protected-file audit passed.

### TEST-20261017-B04-01 — Accepted baseline / source protection
- `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence`:
 135 PASS/0 FAIL/0 SKIP in131.08s before B04; real restart/recreation included.
- `backend/.venv/bin/civicly schema-status`:0001 READY;91 index groups/182
  OPERATIONAL constraints;0 canonical domain nodes. Baseline hashes and test output
  in docs/evidence/B04-baseline-*. Local baseline commit09482e2 created after exclusion/
  secret scan; no push. Frozen registry/migration/access policy/benchmark plan and
  original v1/v2 fixtures rehashed unchanged at end. Review ZIP/extracted copy ignored
  and preserved; no database volume contents included.

### TEST-20261017-B04-02 — Audit, conversion and interim failures
- Exact preparation commands: docs/evidence/B04-COMMANDS.md. Original v1 conversion
 42nodes/51edges,0 quarantine. Expanded original:731nodes/1013edges,342 quarantines
  (109 pickup nodes,218 dependent links,15 REPORTS chronology errors). New generator
  revision:858nodes/1246edges including2 receipt/source nodes +18 real Document refs,
 0 quarantines. All55 original numeric measurements/units/observed dates preserved.
- Two intermediate unit test-fixture failures corrected: missing pickup membership
  in synthetic example; tamper test changed an undeclared property instead of a
  declared field. No passing prior tests removed. Final targeted units supersede them.
- First real importer run:1 FAIL in2.10s (B04-import-first-failure.txt), manifest edge
  digest omitted outer public id. Corrected to exact EdgeRecord serialization;
  rerun8 real tests PASS in21.09s (B04-import-tests.txt).
- First benchmark attempt FAIL at LOC-004:82.96839999999999 returns82.9684. Stopped
  on exact content conflict, retained graph407a845eafb843b7955dcc4bd00335e0. DEC-016
  records parameterized RO probes and explicit coordinate precision normalization;
  measurements never rounded. Progress preserved in B04-benchmark-first-failure.txt.

### TEST-20261017-B04-03 — Real full-dataset benchmarks
- Command: `PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion.benchmark --retain-last`
  (pipefail/tee progress wrapper in B04-COMMANDS.md). Real FalkorDB6.0.2/module60002,
  Redis8.10.2, official Python client1.8.0, redis8.1.0, Pydantic2.14.1, Python3.12.1.
  macOS26.5 arm64,8CPU/8GiB, existing pinned image/volumes, AOF/fsync always.
- Pilot106nodes/100edges:4.809s. Three fresh full imports:172.941/171.731/172.195s;
  median172.195s. Full repeats:12.092/12.063;11.864/11.590;11.848/11.929s.
  Every full create2104; every repeat create0/match2104. Revision2104/audit2104 and
  content hashes unchanged. Final audit560586bytes; peak Python~4.33MiB, max same-kind
  scan259. Proposed initial/repeat/memory targets met, not a production scale claim.
- Raw JSON/progress/AOF rewrite logs and B04-PERFORMANCE.md record latency quantiles,
  memory/AOF net snapshots, query/byte totals and limitations. Query counters include
  repeats; wall/latency/peak/storage are initial-only. Automatic rewrites explain
  negative net AOF deltas; cumulative disk I/O is not measured. Lock-wait and cycle/
  schedule comparison counters remain explicitly unverified.
- Later final hardening adds malformed-root/envelope rejection and verification-read
  failure classification; unchanged successful domain-write path. Final regression
  exercises those guards; quoted timing trials precede that report/input hardening.

### TEST-20261017-B04-04 — Regression and specification gates
- Interim complete run before last seven envelope-unit cases:251 PASS/0 FAIL/0 SKIP
  in152.14s (B04-regression-before-envelope-tests.txt), including all42/47 types through
  real importer, concurrent equal writers, interrupted prefix, lost reply before/
  after actual commit, final verification read failure/retry, real path preservation,
  invalid temporal source, coordinate hash roundtrip and actual restart/recreation.
- Final expanded complete command: `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence`.
  258 PASS/0 FAIL/0 SKIP in151.63s;189 unit/69 real integration. B04 adds112 unit/11 real integration cases. All prior135 tests retained.
- `make test-spec`: both SPEC validators PASS, including offline strict v3 bundle/hash
  and55 lossless values checks. SPEC is not MCP/agent/frontend proof. Exact output in
  B04-spec-validation.txt. `compileall` and `git diff --check` PASS.
- Secret scan: candidate source/tracked+untracked files exclude.env, virtual env/cache,
  Git internals/review distributions; no actual local-secret/private-key matches.
  B04-security-audit.json records counts, no secret values. Runtime MCP/live LLM/
  GraphRAG/API/frontend tests NOT IMPLEMENTED/NOT RUN; no mocked success substituted.

### TEST-20261017-B04-05 — Final review truth
- Final source suite:258 PASS/0 FAIL/0 SKIP in151.63s.189 unit/69 real integration;
  B04 adds112 unit +11 DB cases. Both SPEC validators PASS. No old passing tests removed.
- All six engineering tracking files updated; B04 exact file inventory/Git diff and
  source-security/protection audit provided under docs/evidence. No remote push.
- Human acceptance is pending. B05 remains TODO; no algorithms/counterfactual feature,
  MCP, agents, GraphRAG, operations, API or frontend implemented during B04.
- Post-recreation real CLI command:
  `PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion import --graph civicly_b04_test_a84beda80da64aacbc367a9399e07a97 --bundle data/ingestion/city-v3.json --report docs/evidence/B04-retained-post-recreation.json`
  PASS:0 created/2104 matched,858nodes/1246edges, revision/audit2104 and exact manifest
  content hash preserved. `civicly health`/`schema-status` PASS; fresh canonical count0
  and original B01-PERSISTENCE/SYNTHETIC/B01 row intact. Browser HTTP200/volume PASS in
  lifecycle tests. No preexisting graph/volume removed; final isolated city remains.

### TEST-20261017-B05-01 — Accepted B04 baseline and vendor inspection
- Baseline command:`backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence`:
 258 PASS/0 FAIL/0 SKIP in162.42s; both SPEC validators PASS. Source/exclusion/secret
 scan215 files PASS. Full city2104 records individually hashed read-only against B04
 manifest, revision/audit2104 and content unchanged. Baseline local8aaf17c, no push.
- A separate verification read attempted during the baseline lifecycle restart got
 ConnectionRefused; repeated after lifecycle finished and succeeded. This was an
 orchestration timing failure, not mocked DB success or weakened transport retries.
- Actual installed Graph.ro_query source uses _query(read_only=True). Real catalog
 lists native BFS/PageRank/WCC/etc as READ. Parameterized native BFS in controlled
 fixture includes EXPIRED; filtered Cypher excludes it. No native absence assumption.
 Python3.12.1/falkordb1.8.0/redis8.1.0/Pydantic2.14.1/pytest9.1.1; server6.0.2/module60002,
 Redis8.10.2, same pinned Compose/Browser2.6.1/volumes. Official refs in ALGORITHMS.md.

### TEST-20261017-B05-02 — Targeted tests and recorded failed attempts
- First real B05 integration command (same module, -v -s -x):1 setup ERROR in2.25s,
 missing required Zone.zone_type in new fixture. Corrected fixture only; schema kept.
 Fixture outcome authored as existing INCONCLUSIVE enum, not invented FAILED value.
 Re-run12 PASS in34.33s (B05-integration-second.txt).
- Strengthened real suite18 PASS in54.94s. Later expanded run19 PASS/1 FAIL in71.66s:
 redirection negative test supplied Location without required coordinates, so schema
 rejected before ownership assertion. Added valid fixture coordinates; targeted
 redirection/malicious-ID tests2 PASS in7.25s. Failure log retained; no source mutation.
- First combined run stopped collecting279 items/1 ERROR because new unit/integration
 basenames collided. Renamed unit file to test_graph_algorithm_models.py; same29
 cases retained, no global pytest import-mode change. Interim308 PASS in224.58s before
 final positive-proof correction; log retained as B05-regression-before-positive-proof-fix.txt.
- DEC-021 review identified previously fetched asset/zone proof could be overlooked
 when later context truncated. Indexed existing validated edges without expanding
 budgets; new real capped-zone + historical ranking regressions2 PASS in5.32s.
 Final-code controlled/city evidence and all260 measurements regenerated afterwards.

### TEST-20261017-B05-03 — Actual controlled/city/counterfactual proof
- Commands in B05-COMMANDS.md; controlled/city CLI real PASS. Native bounded BFS proof,
 all7 graph operations + cases, public proof IDs/source attrs and controlled ablation
 JSON recorded. Source29/28 and revision/audit57 unchanged; clone57→58→59. Criticality
 D1,D4→D4,D1 after CUT; candidate replacement changes exploratory only. Expired/future
 evidence/geographic negatives, complete ledgers, copied identities, source metadata
 hashes, stale/wrong/candidate mutation refusal and actual uncertainty recovery tested.
- City source exact858/1246/content hash/revision/audit2104 unchanged.42 CANDIDATE
 DRAINS_TO; verified-only no qualifying paths; exploratory D12→D18 and actual ROAD-R08
 inspection. S01–S12 classified from recorded paths and sanitized B04 readiness;
4 broader,8 source-conflicting asset sets;3 exact/6 conflicting/3 unspecified clusters.
 Missing histories/55 observation links/S07 topology stay OPEN, never fabricated.
- `PYTHONPATH=backend backend/.venv/bin/python -m tests.b05_benchmark`:26 workloads ×10
 =260 actual read-only analyses. Raw queries/steps/internal wall/caps and unchanged
 source hashes/audits in B05-performance.json; descriptive medians2.743–27.628ms,
 clone2.318s. Initial interpreter/repository setup/administrative manifest verification
 and final JSON serialization excluded from analysis timer; no native/process peak
 memory or robust latency-SLA claim. Partial case ranks explicitly lower bounds.

### TEST-20261017-B05-04 — Final complete regression / SPEC / review gate
- Final command:`backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence`
 with pipefail/tee:309 PASS/0 FAIL/0 SKIP in246.23s;218 unit +91 real integration.
 B05 adds29 unit/22 real cases; all prior258 unchanged. Real restart/recreation + fresh
 Browser HTTP200/volume and graph MATCH PASS; no retained graph/volume deletion.
- `backend/.venv/bin/python -m pytest backend/tests/unit -q`:218 PASS in3.98s.
 `make test-spec`:both validators PASS including B04 strict bundle/55 exact numbers;
 not an MCP/LLM/GraphRAG/agent/frontend test. Compile/diff whitespace checks PASS.
- Exact files/diff/review ZIP plus manifest/security audit in docs/evidence and
 review_packages. ZIP contains actual source/tests/contracts/data/evidence/tracking;
 excluded.env/credentials/private keys/Git/cache/venv/volumes and evaluator payloads.
 Runtime MCP/live LLM/LangGraph/GraphRAG/planning/operations/API/frontend NOT RUN/
 NOT IMPLEMENTED in B05; not counted as skipped required tests. STOP for human review.
- Final post-lifecycle verification PASS:actual city full record hashes/audit/fence
  hash equal accepted B04/B05 baseline, revision/audit2104; controlled source unchanged
  revision/audit57, clone59 retained; original B01 row intact; canonical0 domain nodes,
  migration0001 READY,91 index groups/182 OPERATIONAL constraints. Fresh client reads,
  not cached success. B05-post-lifecycle.json captures actual checks after recreation.

### TEST-20261017-B05-05 — Focused external review ZIP reproduction
- Package byte/CRC/actual-local-secret/private-key/path exclusions PASS. Includes
 actual source,51 focused B05 tests/helpers, normative contracts, actual city bundle+
 23node/21edge read-only extract, real outputs/measurements and all6 tracking files.
- Extracted ZIP to an isolated temporary directory; explicitly asserted imports use
 extracted app.graph.analysis source. Focused command from extraction:
 `backend/.venv/bin/python -m pytest backend/tests/unit/test_graph_algorithm_models.py backend/tests/integration/test_graph_algorithms.py -v -s`
 using the original isolated interpreter as an external dependency:51 PASS/0 FAIL/
 0 SKIP in88.60s against real FalkorDB, no original checkout source dependency.
- Initial verification harness resolved the venv Python symlink to global Python,
 which lacked redis; corrected to preserve the venv invocation path and canonicalize
 temporary directory aliases. No archive/application dependency or source change.
- Full repository remains309 PASS; focused51 are a reproducibility recheck, not
 additional unique tests. Final manifest lists every included file's purpose/SHA256
 and omitted dependencies. All prior B01–B04 tests/source/data/pins remain unchanged.

### TEST-20261017-B06-01 — Accepted B05 baseline / source / dependency spike
- Baseline `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence`:
 309 PASS/0 FAIL/0 SKIP in261.78s. Both SPEC validators PASS.263-file existing-source
 secret/exclusion/hash audit PASS; B05 ZIP SHA unchanged. Local commit6550d31108c34db6bb0bd5c111c7a41d09953125,
 no push. Historical patch/failed-log whitespace warnings retained unchanged.
- Fresh full-city record/hash/audit/writer checks, retained B05 source/clone, original
 B01 probe and canonical0001 READY PASS (B06-baseline.json). First harness omitted
 required graph_name and failed TypeError; corrected harness, no application change.
- Official published1.3.0 package source inspected; Node24.21.0/npm12.2.0, Python
 MCP/types2.3.0. Isolated actual handshake2025-11-25/list7/readD12 PASS. First raw ACL
 Python-client probe required INFO; retried raw Redis command probe; no graph writes.
 Node dependency lock6.8.0/TS SDK1.32.1 verified against6.0.2. Frozen npm ci and pip
 check PASS; full version/lock/integrity evidence B06-versions.json.

### TEST-20261017-B06-02 — Real MCP and strengthened negative tests
- First authenticated project proof failed TIMEOUT because minimum ACL omitted INFO,
 required by Node Sentinel detection. Added only INFO, reran configure/proof PASS.
 Real node/schema/relationship reads match independent official Python client, actual
 revision2104.7 discovered/4 allowed;42 city drainage links remain CANDIDATE.
- Initial30 unit PASS in2.06s; strengthened37 unit PASS in0.62s. Mocked malformed
 outputs/schema/scope/property/endpoint/revision/pending faults explicitly labeled.
- First real integration13 PASS in45.18s; strengthened signatures/auth test13 PASS
 in48.90s. Missing/wrong auth test ensures initialization never succeeds; no own-assert
 false-positive accepted. Actual kill/fresh reconnect, SIGSTOP timeout/cleanup,
 CREATE/SET/DELETE RO denial, strict-mode/general/delete rejection, ACL/write/key/list/
 admin denials, invalid args, spoofed tools, parameter injection and call budgets PASS.
- Temporal review reused B03 UTC normalization. Actual retained edge equivalent
 fractional dates and prior-microsecond boundary PASS; focused37unit+14real=51 PASS
 in49.92s. Additional AFTER-REAL-READ local unknown-property corruption/reconnect1
 PASS in5.38s; explicit fault injection, not claim of malformed upstream response.
- HTTP bearer authentication NOT APPLICABLE to selected private stdio; not reported
 passing/skipped. No live model/agent/custom MCP server test exists in B06.
- First final-audit invocation under the filesystem sandbox could not execute ps
  (PermissionError); rerun with authorized local process inspection PASS. This was a
  tool-permission failure, not a passed cleanup check or application regression.
 86 protected original app/test/contract/ingestion files unchanged; no local secret
 values included; original dependency pins and B05 ZIP hash retained.

### TEST-20261017-B06-03 — Complete final regression, persistence and source safety
- Final `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence`:
 **361 PASS/0 FAIL/0 SKIP in329.97s**.255 unit/106 real integration. B06 adds37 unit/
 15 real DB/MCP cases; all prior309 tests/source unchanged. Two lifecycle PASS lines
 are standalone because tests emit actual restart/recreation output;106 integration
 count includes them. Full log B06-regression-tests.txt; no mock counted as real proof.
- Both SPEC validators PASS after final docs, explicitly STATIC checks. npm ci lock
 reinstall110 packages PASS, pip check PASS, compile/whitespace PASS. Python/Node
 lock/package/version/integrity evidence B06-versions.json; no original direct-pin change.
- Actual persistence: same-container restart + different-container recreation,
 Browser HTTP200/store and fresh graph MATCH PASS, no volume removal. Reprovision
 B06 ACL after recreation; real configure/proof PASS again, independent official
 Python read equal, DRAIN-D12 and D12→D18 CANDIDATE at actual revision2104.
- `PYTHONPATH=backend backend/.venv/bin/python -m tests.b06_verify --output docs/evidence/B06-post-lifecycle.json`:
 PASS all2104 city record hashes/content/revision/audit/writer state, B05 source57/
 clone59 and original B01 probe exactly retained. Fresh CLI health/schema-status PASS;
 canonical0001 READY,91 index groups/182 OPERATIONAL constraints. No raw data edit.
- Actual-local.env/.runtime secret/excluded-path/old-file/old-pin/B05-ZIP/process audit
 PASS;86 original protected files unchanged, no leaked official child processes. No
 B06 ZIP created or remote push. Reviewable source patch/file inventory produced.
- HTTP bearer tests NOT APPLICABLE to stdio; live LLM, custom domain MCP, agents,
 GraphRAG, operations/API/frontend NOT IMPLEMENTED/NOT RUN in B06; not skipped runtime
 acceptance tests. Remaining source/DEC-004 findings stay OPEN. STOP for human review.

### TEST-20261017-B07-01 — Incident rotation / accepted baseline
- `PYTHONPATH=backend backend/.venv/bin/python scripts/rotate_b07_mcp.py`: PASS old
  credential AUTH DENIED, replacement PING/RO read PASS; named-user connections killed,
  graph-scoped readonly commands retained, file atomic0600. No values or password
  hashes logged. Report B07-credential-rotation.json. No graph record/migration edit.
- Accepted B06 baseline361 PASS/0 FAIL/0 SKIP in305.72s.52-file staged secret/exclusion
  audit PASS; local24e80725ead2903516ecd36db2142f8fe36b2760, no push. User's reported
  unsafe full-folder archive is external/not inspected here; Git candidate audit does
  not claim it excluded ignored.runtime. No B07 archive generated.

### TEST-20261017-B07-02 — Actual handlers / strict contracts / negative faults
- Initial32 unit PASS in0.73s (structural/pure/mock only), first25 actual custom MCP
  integration PASS in49.73s. Strengthened60 PASS in49.55s (32unit/28real); extra2 real
  unavailable-server/trace-write-failure boundaries PASS in7.18s. Trace permission
  revocation is deliberate fault; SDK stderr NoPermissionError is retained evidence,
  not a failed passing test. Permissions restored in finally.
- First operator all-handler proof surfaced maintenance ERROR: duplicate provenance
  IDs correctly rejected by uniqueItems. Direct readonly service reproduction failed
  schema validation; deduplicate/copy lists, then proof rerun with explicit no-ERROR
  assertion PASS. Valid LOC-004 operator request exercises unlinked-observation gap;
  no fixture repair. Prior proof preserved before final schema/hash regeneration.
- Actual12 registered READ names /6 forbidden write names, unknown tools/query/admin/
  graph/scope/role arguments, strict input/date/hop/byte limits, namespace separation,
  real metadata/provenance/revision, no candidate promotion, unavailable capabilities,
  durable server+parented broker traces, idempotence/conflict, timeout/SIGSTOP, kill/
  reconnect, AFTER-REAL-READ local corruption/recovery PASS. No live model rationale.
- Compatible0002 actual indexes/unique/mandatory readiness, safe rerun, checksum
  mismatch no overwrite, duplicate constraint failure preserving2 records+FAILED
  ledger, partial migration finish PASS. Only test-minted graphs cleaned up.
- Typed forward B05 mode actual WASTE-W03→route/COLLECTED_BY and PIPE-P02→ROAD-R08/
  UNDERLIES2 PASS in7.13s; reverse/BOTH typed requests rejected, no invented reverse
  physical connection. Default drainage still verified-only/no city qualifying path.

### TEST-20261017-B07-03 — Full regression progression
- Interim complete423 PASS/0 FAIL/0 SKIP in374.07s, retained as
  B07-regression-before-typed-mode.txt. Final full425 rerun after typed-mode adapter/
  input schema/proof additions; original361 tests unchanged. Final result pending.
- Both SPEC validators PASS after shared custom/API trace metadata changes; STATIC,
  not a replacement for live MCP/DB tests. API tool_name remains nullable for later
  state events, server IDs cover both namespaces; no B17 route/SSE implementation.
- Final metadata review copied validated domain error codes into SERVER trace records;
  BROKER receipt SUCCESS is explicitly distinct from domain status. Added pure trace
  regression;33 B07 unit PASS in0.84s. Operator proof now records actual SDK initialize
  identity/protocol and tools/list schemas, not only safe broker inventory. Final full
 426 run follows this correction (33 unit+32 real additions to accepted361).
- Intermediate425 PASS/0 FAIL/0 SKIP in370.65s retained as
  B07-regression-before-trace-metadata-fix.txt. Final426 rerun against final code with
  trace-domain error codes/actual initialize+tools-list proof and typed InfrastructureAsset
  root guard (existing2 real typed tests also reject Incident as asset root).
- Clarification: the very first CLI proof exited PASS despite its maintenance result
  containing ERROR because that early proof harness only checked transport return.
  Manual status inspection exposed it; the harness now rejects any handler ERROR,
  and subsequent real integration tests assert actual inspection records/provenance.
  No initial transport-only PASS is used as final domain acceptance evidence.

### TEST-20261017-B07-04 — Final complete acceptance / persistence / safety
- Final `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence`:
 **426 PASS/0 FAIL/0 SKIP in350.75s**.288 unit/138 real integration, including2
 lifecycle tests whose PASS prints on standalone lines. B07 adds33 unit/32 real;
 all original361 source tests unchanged. Intermediate423/425 logs preserved.
- Both specification validators PASS after final contracts/docs (STATIC only).
 Compile and whitespace/source-patch checks PASS. Dependency pins unchanged from
 accepted B06 (Python3.12.1/MCP2.3.0/FalkorDB6.0.2/officialMCP1.3.0/Node24.21.0).
- Actual same-container restart +different-container recreation retained graph and
 Browser volumes, fresh MATCH/HTTP200/storage PASS. Trusted configure reprovisions
 volatile ACL using replacement credentials. `scripts/verify_b07.py` PASS all2104
 city record hashes/content/revision2104/audit/writer state, original B01 probe,
 B05 source57/clone59 and canonical0001 readiness91/182.13 preexisting server traces
 exactly preserved across recreation. No source data or immutable0001 edit.
- Final actual operator proof PASS:SDK initialize civicly-domain1.0.0/protocol2025-11-25,
 actual tools/list12 schemas, tools/call all12 results without ERROR; explicit gaps/
 UNAVAILABLE as appropriate, no fabricated provider success. Candidate drainage and
 WASTE-W03→ROUTE-C03/COLLECTED_BY, PIPE-P02→ROAD-R08/UNDERLIES remain CANDIDATE.
 15 persisted server observations read back. Trace migration0002 READY;native totals
 93 index groups/186 constraints,2/4 additive specs OPERATIONAL.482 trace nodes observed.
- Final Git candidate audit PASS94 protected original files/old tests/pins intact,
 18 names/permissions unchanged, intentional MCP/API trace contract updates recorded.
 Actual local.env/reader/writer secrets absent from candidate source/logs; no leaked
 official/custom MCP process. Audit explicitly excludes any claim about external unsafe
 full-folder archive. No B07 ZIP or push. Credential old denial/new scoped auth proven.
- Live LLM/agent selection, GraphRAG/memory/operational workflows/API/frontend NOT RUN/
 NOT IMPLEMENTED by B07; not skipped real acceptance tests. Remaining designated
 DEC-004/source/history/approval/event/evaluator findings OPEN. STOP for human review.

### TEST-20261017-B07R-01 — Real failure reproductions, then corrected focus
- New fixture setup first failed strict registry: valid_to requires valid_from.
  B07R-before-correction.txt records4 setup ERROR in6.21s, not product reproductions.
  Corrected the test fixture; setup now validates before initializing its source.
- Actual DB +SDK stdio +unchanged DomainBroker/TraceStore harness then reproduced
 4 FAIL in9.18s: per-record evidence incorrectly unioned; pickup/condition windows
 starved by older limited rows; work-order gap absent. B07R-failure-reproduction.txt
 and B07R-before-outputs.json preserve actual failures/results. No source city writes.
- Corrected initial4 real PASS in10.51s; strengthened final9 real PASS in14.33s.
  Tests exercise110 out-of-window +107 relevant dated rows per history, fractions/ID
  tie order, future/expired records,100/101 lookahead, narrow inclusive lower bound,
  two independent dated inspection sources, present/absent work-order limitations.
 5 new pure structural/fake projection unit PASS in0.51s; not runtime acceptance.
- Full-suite initial collection stopped: unit/integration new modules shared basename.
  B07R-collection-failure.txt retains1 ERROR in0.81s; renamed new unit module to
  test_civicly_mcp_history_projection.py, no preexisting test/source removal. Full rerun.
- Test harness source substitution is explicit fixture-only, not retained-city evidence;
  server callbacks, discovery, wire schemas, broker checks and trace writes are real.
  All production/source/authorization paths remain covered by unchanged regressions.

### TEST-20261017-B07R-02 — Final full regression / retained runtime / security
- Exact command: `backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > docs/evidence/B07R-regression-tests.txt 2>&1`.
- Actual440 PASS/0 FAIL/0 SKIP in368.60s;293 unit/147 real integration. Adds5 unit/9
  real tests; all426 old tests unchanged. Expected revoked trace ACL emits
  NoPermissionError stderr and passes fail-closed assertion; not a regression failure.
- `make test-spec > docs/evidence/B07R-spec-validation.txt 2>&1`: both SPEC validators
  PASS (STATIC only). Python compilation/whitespace checks PASS. No live-model claim.
- After real restart/recreation: `PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure --output docs/evidence/B07R-runtime-configuration.json`; same replacement credentials/ACL, no rotation rollback.
- Actual production-city `... -m app.mcp.civicly proof --output docs/evidence/B07R-city-proof.json`: PASS,12 discovered tools/all12 calls/no handler ERROR;15 persisted observations.
- `PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b07.py --output docs/evidence/B07R-post-lifecycle.json`: PASS; all2104 city record hashes/revision/audit/writer state, B01 probe, B05 source/clone, READY0001/0002 unchanged;13 early proof traces preserved.666 total ToolExecutions observed after final proof, not agent runs.
- `PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b07r_traces.py`: PASS;15 accepted final B07 records exactly unchanged,4 pre-correction +11 corrected fixture output/evidence hashes preserved. Actual log proves corrected calls preceded successful restart/recreation; no unsupported persistence claim.
- `backend/.venv/bin/python scripts/audit_b07r.py`: PASS;333 original files unchanged
  outside11 intended edits, all18 wire schemas/permissions stable, private values absent
  from Git candidates/logs; no leaked MCP process. No external ZIP sanitization claim.
- Commands/results/file inventory/working-tree patch under docs/evidence/B07R-*; no
  B08 work, no push/archive. Remaining capabilities/gaps remain designated later gates.
