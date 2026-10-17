# test_log.md — Append-only verification record

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
