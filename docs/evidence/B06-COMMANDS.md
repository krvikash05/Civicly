# B06 exact commands and reproduction

Run from repository root. No push, database volume deletion or data rewrite.
Private values never printed; configure/proof outputs contain status only.

## Baseline and package inspection

```sh
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > docs/evidence/B06-baseline-tests.txt 2>&1
make test-spec > docs/evidence/B06-baseline-spec.txt 2>&1
node --version
npm --version
npm view @falkordb/mcpserver version engines dist.integrity --json
backend/.venv/bin/python -m pip index versions mcp
```

Source/secret audit scanned263 existing files, excludes B06 evidence; report
B06-source-baseline.json. Historical B05 ZIP exact SHA verified. Git baseline:

```sh
git add --all -- . ':!docs/evidence/B06-*'
git diff --cached --check
git commit -m 'Baseline accepted B05 graph algorithms and real database review evidence'
git rev-parse HEAD
```

Result6550d31108c34db6bb0bd5c111c7a41d09953125. Whitespace warnings were retained
historical patch-context/failed-test-log bytes, not source errors. No push.
Baseline regression started before commit; completed before dependency installation.

Vendor source/isolated spike (temporary audit files, not runtime dependencies):

```sh
mkdir -p /tmp/civicly-b06-vendor
cd /tmp/civicly-b06-vendor
npm pack @falkordb/mcpserver@1.3.0 --silent
tar -xzf falkordb-mcpserver-1.3.0.tgz
npm install --ignore-scripts --no-audit --no-fund @falkordb/mcpserver@1.3.0
python3.12 -m venv /tmp/civicly-b06-vendor/venv
/tmp/civicly-b06-vendor/venv/bin/python -m pip install mcp==2.3.0 falkordb==1.8.0
```

Inspected actual dist/index.js, mcp/tools.js, config/index.js, services/falkordb.service.js,
logger.service.js; Node driver falkordb.js requires INFO for Sentinel detection.
Temporary Python spike used official Client(StdioServerParameters,mode='legacy')
initialize/list/call and parameterized DRAIN-D12 query. Separate disposable-account
ACL probe attempted city RETURN1, other-key RETURN1, CREATE through RO and GRAPH.QUERY;
all denials observed, account removed. First Python-client ACL probe needed INFO;
retried using raw Redis connection to test minimum commands. No graph data changed.

## Project install and actual runtime proof

```sh
npm install --prefix backend/mcp_runtime --ignore-scripts --no-audit --no-fund
UV_CACHE_DIR=.uv-cache backend/.venv/bin/uv lock --project backend
UV_CACHE_DIR=.uv-cache backend/.venv/bin/uv sync --project backend --frozen
backend/.venv/bin/python -m pip check
make mcp-setup
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp configure
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp proof --output docs/evidence/B06-runtime-proof.json
```

First authenticated proof FAILED TIMEOUT because Node client INFO denied. Added only
read-only INFO to named account; configure/proof then PASS. Actual four tools/fixed
query reads and independent Python result comparison in B06-runtime-proof.json.
Configure is required again after any database lifecycle restart/recreation.

## Tests and final evidence

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_mcp_broker_policy.py -v > docs/evidence/B06-unit-tests.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_official_mcp.py -v -s > docs/evidence/B06-integration-tests.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > docs/evidence/B06-regression-tests.txt 2>&1
make test-spec > docs/evidence/B06-spec-validation.txt 2>&1
backend/.venv/bin/civicly health
backend/.venv/bin/civicly schema-status
backend/.venv/bin/python -m compileall -q backend/app/mcp backend/tests/unit/test_mcp_broker_policy.py backend/tests/integration/test_official_mcp.py
git diff --check
```

Focused first iterations kept in B06-unit-first.txt (30 PASS) and
B06-integration-first.txt (13 PASS). Strengthened unit suite37 cases; real suite15 after fractional-time and after-real-read fault-injection additions.
Missing-auth test strengthened to ensure actual initialization never happened, rather
than allowing a broad exception block to catch its own assertion. Contract hashes
and schema-output strictness were added after initial real proof; final tests/proof
are rerun against final code. Malformed output/revision fault cases are labeled mocks;
real stalled-process timeout/auth/process-kill/read/write-denial use actual server.
HTTP bearer auth: NOT APPLICABLE to private stdio; not counted as a skipped passing test.

Retained verification uses verify_city against all2104 accepted record hashes, capture
fingerprints of retained B05 source/clone, original parameterized B01 probe MATCH and
MigrationRunner(client,'civicly_knowledge').status(). B06-baseline.json and
B06-post-lifecycle.json report exact hashes/readiness. Initial harness omitted the
explicit canonical graph argument and failed TypeError; corrected harness, not app.
Final audit JSON checks original source/data/tests/registry/0001 hashes and scans all
candidate source/evidence for actual local.env and.runtime secret values, keys and
forbidden paths. Review diff/file inventory are B06-changes.patch/B06-FILES.md.

## Two-minute human check

`make mcp-proof` then inspect B06-runtime-proof.json: actual falkordb1.3.0 initialize,
protocol2025-11-25,7 discovered/4 allowed, DRAIN-D12 and D12→D18 CANDIDATE, revision2104,
independent_client_equal=true, and denied query/delete/list/graph/raw-Cypher attempts.
Run `make test-mcp` for full focused tests. If failure, share redacted output and
blockers.md, never.env/.runtime credentials. For regression use full command above.
B07 custom typed Civicly MCP service is proposed only after human B06 acceptance.

Final retained/source verification commands (actual helper source included):

```sh
PYTHONPATH=backend backend/.venv/bin/python -m tests.b06_verify --output docs/evidence/B06-post-lifecycle.json
backend/.venv/bin/python scripts/audit_b06.py
```

The first command performs only official-client reads and verifies equality to
accepted B05 fingerprints. It runs after the lifecycle suite, not concurrently with
its temporary database disconnection. The audit checks local actual secret values
without printing them, protected files/old pins, ignored dependencies/runtime files,
unchanged B05 ZIP and absence of lingering official MCP child processes.

Additional focused fault test before final full regression:

```sh
backend/.venv/bin/python -m pytest backend/tests/integration/test_official_mcp.py::test_real_mcp_result_fault_injection_rejected_then_reconnect -v -s > docs/evidence/B06-output-fault-test.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/unit/test_mcp_broker_policy.py backend/tests/integration/test_official_mcp.py -v -s > docs/evidence/B06-focused-tests.txt 2>&1
```

The focused51 run preceded the last fault-injection test (1 PASS); final regression
collects361 = original309 +37 unit +15 real MCP/database integration cases.
