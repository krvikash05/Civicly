# Exact B07 created/modified files

Accepted B06 baseline `24e80725ead2903516ecd36db2142f8fe36b2760`; B07 uncommitted for review, no push.

56 total files: 13 modified, 43 created.

Source/config/docs patch includes every non-evidence change; generated evidence bodies excluded and inventoried below. No ZIP.

## Modified

| Path | Purpose |
|---|---|
| `Makefile` | Runtime/architecture/reproduction/current-status documentation or Make targets |
| `README.md` | Runtime/architecture/reproduction/current-status documentation or Make targets |
| `backend/MCP.md` | Runtime/architecture/reproduction/current-status documentation or Make targets |
| `backend/README.md` | Runtime/architecture/reproduction/current-status documentation or Make targets |
| `blockers.md` | Required engineering tracking/current review status, append-only history preserved |
| `contracts/api_models.json` | Shared closed invocation/result/trace schemas and synchronized API metadata |
| `contracts/mcp_tools.json` | Shared closed invocation/result/trace schemas and synchronized API metadata |
| `decision.md` | Required engineering tracking/current review status, append-only history preserved |
| `docs/backend/05_mcp.md` | Runtime/architecture/reproduction/current-status documentation or Make targets |
| `flow.md` | Required engineering tracking/current review status, append-only history preserved |
| `implementation_status.md` | Required engineering tracking/current review status, append-only history preserved |
| `task_board.md` | Required engineering tracking/current review status, append-only history preserved |
| `test_log.md` | Required engineering tracking/current review status, append-only history preserved |

## Created

| Path | Purpose |
|---|---|
| `backend/CIVICLY_MCP.md` | Runtime/architecture/reproduction/current-status documentation or Make targets |
| `backend/app/graph/migrations/0002_mcp_traces.json` | Additive compatible trace-storage migration;0001 unchanged |
| `backend/app/mcp/civicly/__init__.py` | Custom read MCP namespace |
| `backend/app/mcp/civicly/__main__.py` | Trusted configure/actual proof CLI |
| `backend/app/mcp/civicly/broker.py` | Actual identity/schema discovery, safe namespace/args/results and persisted child observations |
| `backend/app/mcp/civicly/contracts.py` | Normative inventory, schemas, limits and invocation context |
| `backend/app/mcp/civicly/models.py` | Strict sanitized shared TraceRecord |
| `backend/app/mcp/civicly/router.py` | Separated official/domain dispatch and shared official trace records |
| `backend/app/mcp/civicly/runtime.py` | Separate graph-scoped credentials/configuration and private subprocess setup |
| `backend/app/mcp/civicly/server.py` | Actual SDK2.3 stdio discovery/calls/validation/serialized budgets and durable server observations |
| `backend/app/mcp/civicly/service.py` | Read projections over B03/B05 and bounded registered history; explicit future gaps |
| `backend/app/mcp/civicly/storage.py` | Compatible0002 and controlled fenced atomic trace service |
| `backend/tests/integration/test_civicly_mcp.py` | B07 structural/unit or actual MCP/DB/fault/migration regression tests |
| `backend/tests/unit/test_civicly_mcp_contracts.py` | B07 structural/unit or actual MCP/DB/fault/migration regression tests |
| `contracts/mcp_envelopes.json` | Shared closed invocation/result/trace schemas and synchronized API metadata |
| `docs/evidence/B07-COMMANDS.md` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-FILES.md` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-RESULTS.md` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-baseline-tests.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-canonical-status.json` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-changes.patch` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-credential-rotation.json` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-failure-boundary-tests.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-focused-tests.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-health.json` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-integration-first.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-post-lifecycle.json` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-regression-before-trace-metadata-fix.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-regression-before-typed-mode.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-regression-tests.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-runtime-configuration.json` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-runtime-proof-before-final-contract.json` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-runtime-proof.json` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-source-audit.json` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-spec-first.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-spec-validation.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-trace-schema-status.json` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-typed-dependency-tests.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-unit-first.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `docs/evidence/B07-unit-tests.txt` | Actual B07 commands/results/runtime/native schema/security/regression evidence or diff/inventory |
| `scripts/audit_b07.py` | Credential rotation, retained data/trace verification or actual-secret/source/process audit |
| `scripts/rotate_b07_mcp.py` | Credential rotation, retained data/trace verification or actual-secret/source/process audit |
| `scripts/verify_b07.py` | Credential rotation, retained data/trace verification or actual-secret/source/process audit |

Excluded from Git/export candidates:.env/.runtime credentials, Git internals, virtual environments, node_modules/caches, volumes and existing review ZIPs.

Source/secret audit scope is Git candidates; external reported full-folder archive is not claimed safe. Credential rotation evidence independently proves old denial/new scoped access.

Immutable0001/registryv3/source data/original361 tests/pins retained. Commands/results:B07-COMMANDS.md/B07-RESULTS.md. STOP for B07 review.
