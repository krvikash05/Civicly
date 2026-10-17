# Exact B06 file changes

Accepted B05 baseline `6550d31108c34db6bb0bd5c111c7a41d09953125`; no remote push. B06 source remains uncommitted for human review.

52 files: 15 modified, 37 created. Existing source/registry/0001/data/tests preserved.

B06-changes.patch includes every modified/new source/config/documentation file, excluding generated docs/evidence bodies. All evidence paths below remain actual repository files; no ZIP.

## Modified

| Path | Purpose |
|---|---|
| `.gitignore` | Dependency lock/setup or ignored private runtime files configuration |
| `Makefile` | Dependency lock/setup or ignored private runtime files configuration |
| `README.md` | Runtime/architecture/reproduction/current-status documentation |
| `backend/GRAPH_ACCESS.md` | Runtime/architecture/reproduction/current-status documentation |
| `backend/README.md` | Runtime/architecture/reproduction/current-status documentation |
| `backend/pyproject.toml` | Dependency lock/setup or ignored private runtime files configuration |
| `backend/uv.lock` | Dependency lock/setup or ignored private runtime files configuration |
| `blockers.md` | Required engineering tracking/current status with historical entries preserved |
| `decision.md` | Required engineering tracking/current status with historical entries preserved |
| `docs/backend/05_mcp.md` | Runtime/architecture/reproduction/current-status documentation |
| `docs/backend/12_falkordb_sources.md` | Runtime/architecture/reproduction/current-status documentation |
| `flow.md` | Required engineering tracking/current status with historical entries preserved |
| `implementation_status.md` | Required engineering tracking/current status with historical entries preserved |
| `task_board.md` | Required engineering tracking/current status with historical entries preserved |
| `test_log.md` | Required engineering tracking/current status with historical entries preserved |

## Created

| Path | Purpose |
|---|---|
| `backend/MCP.md` | Runtime/architecture/reproduction/current-status documentation |
| `backend/app/mcp/__init__.py` | B06 client namespace; no custom server |
| `backend/app/mcp/__main__.py` | Configure/live proof and independent Python read CLI |
| `backend/app/mcp/broker.py` | Actual discovery/calls/allowlist/schema hashes/revisions/traces/budgets |
| `backend/app/mcp/models.py` | Typed validated official-server projections |
| `backend/app/mcp/policy.py` | Strict requests/fixed parameterized templates/B03 UTC normalization |
| `backend/app/mcp/runtime.py` | Trusted credential/DB ACL setup and pinned child environment |
| `backend/mcp_runtime/package-lock.json` | Pinned official Node runtime dependency and exact transitive integrity lock |
| `backend/mcp_runtime/package.json` | Pinned official Node runtime dependency and exact transitive integrity lock |
| `backend/tests/b06_verify.py` | B06 unit/real MCP/fault-injection tests or retained-evidence verifier |
| `backend/tests/integration/test_official_mcp.py` | B06 unit/real MCP/fault-injection tests or retained-evidence verifier |
| `backend/tests/unit/test_mcp_broker_policy.py` | B06 unit/real MCP/fault-injection tests or retained-evidence verifier |
| `contracts/official_mcp.json` | Normative B06 observed signatures, graph/tool authorization and budgets |
| `docs/evidence/B06-COMMANDS.md` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-FILES.md` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-RESULTS.md` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-baseline-spec.txt` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-baseline-tests.txt` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-baseline.json` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-canonical-status.json` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-changes.patch` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-focused-tests.txt` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-health.json` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-integration-first.txt` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-integration-tests.txt` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-npm-ci.txt` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-output-fault-test.txt` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-post-lifecycle.json` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-regression-tests.txt` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-runtime-proof.json` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-source-audit.json` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-source-baseline.json` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-spec-validation.txt` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-unit-first.txt` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-unit-tests.txt` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `docs/evidence/B06-versions.json` | Actual B06 commands, results, versions, regression/runtime/security evidence or source diff/inventory |
| `scripts/audit_b06.py` | Protected original files/pins, actual-secret exclusions and process-cleanup audit |

Excluded: .env, .runtime credentials, node_modules, .venv, caches, Git internals, volumes and existing review ZIPs. No B06 ZIP created.

Protected originals/integrity checks: B06-source-audit.json. Exact commands: B06-COMMANDS.md. Human report: B06-RESULTS.md.
