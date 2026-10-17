# Exact B09-R changed-file inventory

Baseline: local accepted B09 commit688b893. **68 files: 12 modified, 56 new.**
All582 accepted test sources, registry/0001/0002, repository, domain writer, B04
artifacts, B05, B06/B07, B08, dependency pins and original audit evidence unchanged.
Old rolling B07R/B08/B09 proofs restored byte-for-byte; their fresh regression versions
are separate B09R files below. No files deleted, ZIP created or remote push performed.

Patch contains26 source/contract/tracking/review-prose files.
Large captured JSON/TXT evidence and this generated inventory are supplied as actual
files rather than duplicated in the patch. Patch itself is excluded from its contents.
`git apply --reverse --check docs/evidence/B09R-changes.patch` passes on this worktree.

| Change | Repository-relative file | Purpose |
|---|---|---|
| M | `backend/EVIDENCE.md` | Current rule2 semantics, legacy compatibility and reproduction/consumer boundary. |
| NEW | `backend/app/services/evidence/classification.py` | Per-observation meaning/authority, discovery, per-incident coverage and bounded references. |
| M | `backend/app/services/evidence/models.py` | Version-aware assessment/report/attribution/category schemas; exact v1 serialization retained. |
| M | `backend/app/services/evidence/policies.py` | Authority-symmetric rule2 decision matrix; safe legacy classifier adapter. |
| M | `backend/app/services/evidence/reader.py` | Bind explicit attribution to original report operation; retain old absent-field compatibility. |
| NEW | `backend/app/services/evidence/relevance.py` | Actual request/open bindings, occurrence intervals, retrospective source basis and disjoint lineage. |
| M | `backend/app/services/evidence/service.py` | Emit reviewed-only causal edges and version2 snapshots through unchanged writer/CAS/journal path. |
| NEW | `backend/tests/b09r_fixtures.py` | Explicit owned B08 source copies, actual intake and attributed report fixture helper. |
| NEW | `backend/tests/integration/test_evidence_review.py` | 16 real DB/MCP integration tests; persisted matrix, recurrence, legacy replay, topology and actual broker. |
| NEW | `backend/tests/unit/test_evidence_review_models.py` | 19 pure unit tests; matrix, strict attribution and exact v1 shape compatibility. |
| M | `blockers.md` | Corrective disposition, open active-graph gate and preserved designated findings. |
| M | `contracts/evidence_hypotheses.json` | Current contract2/generated strict schemas, authority/occurrence/version policies; registry unchanged. |
| M | `decision.md` | DEC-040 pre-code choice and DEC-041 observed implementation/runtime decisions. |
| NEW | `docs/evidence/B09R-ACTIVE-GRAPH.md` | Review evidence, exact commands, findings or future active-graph acceptance plan. |
| NEW | `docs/evidence/B09R-B07R-regression-proof.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-B08-regression-proof.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-B09-regression-proof.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-COMMANDS.md` | Review evidence, exact commands, findings or future active-graph acceptance plan. |
| NEW | `docs/evidence/B09R-COMPATIBILITY.md` | Review evidence, exact commands, findings or future active-graph acceptance plan. |
| NEW | `docs/evidence/B09R-FILES.md` | This exact repository-relative changed-file inventory; no self-referential hash. |
| NEW | `docs/evidence/B09R-RESULTS.md` | Review evidence, exact commands, findings or future active-graph acceptance plan. |
| NEW | `docs/evidence/B09R-after-results.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-assessment-matrix.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-baseline-B09-retained.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-baseline-configuration.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-baseline-retained-B01-B07.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-baseline-retained.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-baseline-spec.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-baseline-tests.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-before-lifecycle-corrected-history.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-before-results.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-changes.patch` | B09-R-only patch for source/contract/tracking/review prose; reverse applicability checked. |
| NEW | `docs/evidence/B09R-chronology-strengthened.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-compatibility-focused.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-create-legacy-before.py` | Retained minimal real reproduction/legacy creation script; execution phase documented in COMMANDS. |
| NEW | `docs/evidence/B09R-episode-attribution.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-health.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-integration-corrected.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-integration-first.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-post-B09-retained.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-post-configuration.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-post-corrected-history.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-post-retained-B01-B07.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-post-retained.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-regression-tests.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-reproduce-before.py` | Retained minimal real reproduction/legacy creation script; execution phase documented in COMMANDS. |
| NEW | `docs/evidence/B09R-reproduce-corrected.py` | Retained minimal real reproduction/legacy creation script; execution phase documented in COMMANDS. |
| NEW | `docs/evidence/B09R-reproduction-corrected.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-runtime-proof.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-schema-status.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-source-audit.json` | Final actual source/secret/preservation audit result; no credential values. |
| NEW | `docs/evidence/B09R-source-freeze.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-spec-first.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-spec-validation.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-test-collection-corrected.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-test-collection-final.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-test-collection.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-test-summary.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-unit-first.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-v1-proof.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| NEW | `docs/evidence/B09R-v2-mcp-focused.txt` | Actual captured command/test output; failed/interim/final stage named in file. |
| NEW | `docs/evidence/B09R-versions.json` | Sanitized actual runtime/result/fingerprint/schema/version/proof artifact; source/phase named in file. |
| M | `flow.md` | Actual B09-R imports, provenance/relevance/assessment/write/read/persistence flow. |
| M | `implementation_status.md` | Current implemented scope and compatibility limits. |
| NEW | `scripts/audit_b09r.py` | Scope, source freeze, accepted-file preservation, secret and MCP-child audit. |
| NEW | `scripts/verify_b09r.py` | Read-only v1/v2 history/fingerprint/receipt checks and accepted B09 trace verification. |
| M | `task_board.md` | Authoritative B09-R status and human gate; B10 not started. |
| M | `test_log.md` | Exact counts, failures, real vs unit, lifecycle and commands. |

Runtime dependencies are unchanged and are not bundled as generated internals: ignored
Python venv/cache, installed Node MCP node_modules, Docker image/volumes, local private
.env/runtime credential files and existing retained graphs. Reproduce with accepted
local environment and committed uv/npm locks/compose configuration. No database
volume contents, secrets, Git internals or hidden evaluator data are exported here.
