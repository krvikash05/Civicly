# Exact B08 changed-file inventory

**53 files: 10 modified, 43 created.**

Baseline: clean local accepted B07-R commit `6afdd09892502a8b47a7f840ced1491c38a002d3`.
B08 source uncommitted for human review; no push, ZIP/archive or B09 work.

Baseline prerequisite (already committed, outside this B08 source patch): `.gitignore`
adds archive exclusions; absent historical Archive.zip left absent. Accepted B07/B07-R
source/evidence committed as requested before implementation; all440 old tests unchanged.

Generated evidence bodies excluded from source patch, fully inventoried below. No file
deletion, dependency/lock/image/registry/migration/policy/algorithm/source dataset or
existing MCP/trace-envelope source change.

## Modified

| Repository-relative path | Purpose |
|---|---|
| `README.md` | Current B08 verified status and guide link; human review gate |
| `backend/README.md` | B08 implementation guide entrypoint |
| `blockers.md` | Required engineering current status/decisions/control flow/results/limits; append-only historical audit preserved |
| `decision.md` | Required engineering current status/decisions/control flow/results/limits; append-only historical audit preserved |
| `docs/backend/02_graph.md` | Normative architecture/data consumer documentation for implemented B08; existing contracts preserved |
| `docs/backend/03_data.md` | Normative architecture/data consumer documentation for implemented B08; existing contracts preserved |
| `flow.md` | Required engineering current status/decisions/control flow/results/limits; append-only historical audit preserved |
| `implementation_status.md` | Required engineering current status/decisions/control flow/results/limits; append-only historical audit preserved |
| `task_board.md` | Required engineering current status/decisions/control flow/results/limits; append-only historical audit preserved |
| `test_log.md` | Required engineering current status/decisions/control flow/results/limits; append-only historical audit preserved |

## Created

| Repository-relative path | Purpose |
|---|---|
| `backend/COMPLAINTS.md` | Architecture, normalization/grouping rules, atomic recovery, review interface, limits and reproduction |
| `backend/app/services/complaints/__init__.py` | Narrow typed domain service exports |
| `backend/app/services/complaints/models.py` | Strict Pydantic intake/measurement/claim/journal/receipt/reviewer models; original+canonical normalization and decimal units |
| `backend/app/services/complaints/reader.py` | Bounded RO references/context, accepted B03 histories/B05 topology and three issue validators |
| `backend/app/services/complaints/service.py` | Stable source intake/preview/idempotency/group classification/recovery and reviewed temporal regroup |
| `backend/app/services/complaints/writer.py` | Narrow registry/policy-validated single-query batches through unchanged B03 fence/intent/audit |
| `backend/tests/b08_evidence.py` | Operator-only retained real graph creation/fingerprints/idempotent replay/lifecycle verification |
| `backend/tests/b08_fixtures.py` | Authored synthetic infrastructure/history inputs, never city or hidden scenario repairs |
| `backend/tests/b08_server.py` | TEST ONLY actual SDK source-substitution harness for new incident compatibility |
| `backend/tests/integration/test_complaint_intelligence.py` | 34 real DB/MCP classification/provenance/concurrency/rollback/recovery/review/city cases |
| `backend/tests/unit/test_complaint_models.py` | 33 pure strict normalization/units/review/schema regressions |
| `contracts/complaint_intake.json` | Version1 typed service schemas, exact units/matching/writes/limits/receipt rules; no ontology migration |
| `docs/evidence/B08-B07R-regression-proof.json` | Fresh full-run output from unchanged B07-R tests, preserving accepted artifact separately |
| `docs/evidence/B08-COMMANDS.md` | Exact commands/progression/security/persistence and human verification |
| `docs/evidence/B08-FILES.md` | This exact changed-file inventory including generated evidence |
| `docs/evidence/B08-RESULTS.md` | Completion report, architecture/examples/results/remaining limits/B09 boundary |
| `docs/evidence/B08-baseline-audit.json` | Sanitized baseline secret/source/archive-absence audit before commit |
| `docs/evidence/B08-baseline-hashes.json` | All368 accepted baseline source/evidence file hashes, excluding ignored private/runtime files |
| `docs/evidence/B08-baseline-retained.json` | Pre-implementation retained city/B01/B05/schema/trace proof |
| `docs/evidence/B08-baseline-tests.txt` | Fresh440 PASS accepted full suite before source implementation |
| `docs/evidence/B08-changes.patch` | Git-format source/config/docs/tests diff from clean accepted B07-R baseline; generated evidence bodies excluded |
| `docs/evidence/B08-city-mcp-proof.json` | Fresh actual production-city discovery/all12 reads/no ERROR/15 persisted observations |
| `docs/evidence/B08-equivalent-unit-real.txt` | Actual interrupted equivalent-unit first-original resume PASS |
| `docs/evidence/B08-final-refinements.txt` | Final2 real equivalent-unit/mixed-subtype refinements PASS |
| `docs/evidence/B08-focused-tests.txt` | Interim57 unit+real cases PASS |
| `docs/evidence/B08-integration-first.txt` | First21 actual DB cases PASS |
| `docs/evidence/B08-post-lifecycle.json` | Unchanged city/B01/B05/schema and43 accepted MCP trace observations;1038 current traces |
| `docs/evidence/B08-regression-before-canonical-unit-fix.txt` | Explicit interim504 PASS full run before final corrections |
| `docs/evidence/B08-regression-tests.txt` | Final507 PASS complete suite and actual restart/recreation/Browser evidence |
| `docs/evidence/B08-retained-after-lifecycle.json` | Exact anchor survives actual restart/recreation,5 further retries no domain changes |
| `docs/evidence/B08-retained-before-lifecycle.json` | Five pre-lifecycle retries no domain changes; latest exact metadata anchor, no lifecycle claim |
| `docs/evidence/B08-retained-proof.json` | Retained real B08 graph before/after hashes,5 raw requests/receipts/actual graph chains |
| `docs/evidence/B08-runtime-configuration.json` | Sanitized existing scoped MCP ACL/migration restoration after lifecycle |
| `docs/evidence/B08-runtime-proof.json` | Real controlled-fixture and readonly-city outputs for classifications/all validators/recovery/MCP |
| `docs/evidence/B08-smoke-first.txt` | First actual compound intake/query/idempotency smoke PASS |
| `docs/evidence/B08-source-audit.json` | 358 accepted files/pins/tests/contracts preserved, current private-value/process audit PASS |
| `docs/evidence/B08-spec-validation.txt` | Both static specification validators PASS; separate from runtime tests |
| `docs/evidence/B08-strengthened-cases.txt` | Extra3 actual contradiction/missing-context/ambiguous-cluster cases PASS |
| `docs/evidence/B08-unit-first.txt` | First27 pure unit PASS |
| `docs/evidence/B08-unit-normalization-reproduction.txt` | Exact1 FAIL before equivalent-unit hash/decimal fix |
| `docs/evidence/B08-unit-tests.txt` | Final33 unit PASS |
| `scripts/audit_b08.py` | Accepted HEAD file/test/pin preservation, actual local-secret and child-process audit |
| `scripts/verify_b08.py` | Fresh city/B01/B05/schema and43 accepted MCP observation preservation checks |
