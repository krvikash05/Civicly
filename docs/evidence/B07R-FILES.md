# Exact B07-R changed-file inventory

**36 files: 11 modified, 25 created.**

Baseline is accepted uncommitted B07 working tree (344 files), not older B06 Git HEAD24e8072.
No existing file deleted; all old tests/evidence preserved. Source-only patch excludes generated
evidence bodies listed here. No dependency/lock/image/registry/migration/policy/algorithm/dataset/
official MCP/shared-envelope changes, no commit/push/archive or B08 work.

## Modified

| Repository-relative path | Purpose |
|---|---|
| `README.md` | Current accepted B07/B07-R review status; B08 gate |
| `backend/CIVICLY_MCP.md` | Corrected history semantics, limits, fixture harness and reproduction guide |
| `backend/app/mcp/civicly/server.py` | Preserve capability gaps in absent/failed read envelopes |
| `backend/app/mcp/civicly/service.py` | Event-local provenance, pre-cap temporal/chronological history queries and work-order unknown gaps |
| `blockers.md` | Required engineering tracking/current review gate; historical audit retained |
| `contracts/mcp_tools.json` | Four result_semantics clarifications only; unchanged wire schemas/names/permissions |
| `decision.md` | Required engineering tracking/current review gate; historical audit retained |
| `flow.md` | Required engineering tracking/current review gate; historical audit retained |
| `implementation_status.md` | Required engineering tracking/current review gate; historical audit retained |
| `task_board.md` | Required engineering tracking/current review gate; historical audit retained |
| `test_log.md` | Required engineering tracking/current review gate; historical audit retained |

## Created

| Repository-relative path | Purpose |
|---|---|
| `backend/tests/b07r_server.py` | TEST-ONLY real SDK stdio harness with internal disposable source substitution; production startup unchanged |
| `backend/tests/integration/test_civicly_mcp_review.py` | Nine real DB/MCP cases: independent provenance, >100 dated records, lookahead, present/absent work-order gaps |
| `backend/tests/unit/test_civicly_mcp_history_projection.py` | Five pure structural/fake projection and contract checks; not integration proof |
| `docs/evidence/B07R-COMMANDS.md` | Exact executed commands, failure history and human reproduction |
| `docs/evidence/B07R-FILES.md` | This exact B07-R-only changed-file inventory |
| `docs/evidence/B07R-RESULTS.md` | Completion report, root causes, corrected examples, results/limits/B08 boundary |
| `docs/evidence/B07R-baseline-sha256.json` | 344 pre-edit nonignored Git-candidate source/evidence hashes; no credentials copied |
| `docs/evidence/B07R-before-correction.txt` | Initial4 fixture setup ERROR (valid_to needs valid_from), not product reproduction |
| `docs/evidence/B07R-before-outputs.json` | Actual pre-correction outputs; labeled disposable fixture source |
| `docs/evidence/B07R-changes.patch` | Source/config/docs Git-format diff against accepted uncommitted B07; generated evidence bodies excluded |
| `docs/evidence/B07R-city-proof.json` | Fresh production retained-city initialize/discovery/all12 calls/15 trace readbacks after lifecycle |
| `docs/evidence/B07R-collection-failure.txt` | Initial full-suite module-name collection error; corrected by new unit rename |
| `docs/evidence/B07R-contract-baseline.json` | All18 accepted tool input/output schema hashes and permissions |
| `docs/evidence/B07R-failure-reproduction.txt` | Four real MCP product FAIL before service corrections |
| `docs/evidence/B07R-focused-real.txt` | Nine actual SDK/FalkorDB/Broker tests PASS |
| `docs/evidence/B07R-post-lifecycle.json` | Unchanged city/B01/B05 fingerprints, READY migrations and13 earlier trace readbacks |
| `docs/evidence/B07R-regression-tests.txt` | Final440 PASS full original+corrective suite, actual DB restart/recreation/Browser evidence |
| `docs/evidence/B07R-runtime-configuration.json` | Sanitized post-lifecycle scoped ACL/trace migration configuration evidence |
| `docs/evidence/B07R-runtime-proof.json` | Corrected fixture source real MCP outputs, execution IDs/provenance/window/order boundaries |
| `docs/evidence/B07R-source-audit.json` | 333 preserved old files, unchanged wire schemas, private-value/process audit PASS |
| `docs/evidence/B07R-spec-validation.txt` | Both static specification validators PASS; distinct from runtime tests |
| `docs/evidence/B07R-trace-continuity.json` | 15 accepted final B07 +4 pre-correction +11 corrected trace observations preserved across lifecycle |
| `docs/evidence/B07R-unit-tests.txt` | Five pure unit PASS (historical pre-rename command) |
| `scripts/audit_b07r.py` | Accepted-working-tree preservation, wire/permission hashes, actual local-secret and child-process audit |
| `scripts/verify_b07r_traces.py` | Fresh accepted/pre-correction/corrected trace hash/evidence readback; actual lifecycle order assertion |

