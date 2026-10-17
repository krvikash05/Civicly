# Exact B05 file inventory and diff

Accepted B04 local baseline:8aaf17cee7aa428539f77f1c8915924117782bf6. No remote push. B05 changes remain uncommitted for human review.

B05-changes.patch includes all tracked and new source/contract/test/data/documentation changes against that baseline. Generated docs/evidence artifacts are listed here but omitted from the patch to avoid recursive evidence. Actual files, not summaries, are included in the focused review ZIP as specified by its manifest.

Total:57 changed/new files (9 modified; 48 created).

| State | Repository-relative file |
|---|---|
| MODIFIED | `README.md` |
| CREATED | `backend/ALGORITHMS.md` |
| MODIFIED | `backend/GRAPH_ACCESS.md` |
| CREATED | `backend/app/graph/analysis/__init__.py` |
| CREATED | `backend/app/graph/analysis/__main__.py` |
| CREATED | `backend/app/graph/analysis/cases.py` |
| CREATED | `backend/app/graph/analysis/counterfactual.py` |
| CREATED | `backend/app/graph/analysis/engine.py` |
| CREATED | `backend/app/graph/analysis/evaluation.py` |
| CREATED | `backend/app/graph/analysis/models.py` |
| CREATED | `backend/app/graph/analysis/reader.py` |
| CREATED | `backend/tests/b05_benchmark.py` |
| CREATED | `backend/tests/b05_fixtures.py` |
| CREATED | `backend/tests/integration/test_graph_algorithms.py` |
| CREATED | `backend/tests/unit/test_graph_algorithm_models.py` |
| MODIFIED | `blockers.md` |
| CREATED | `contracts/graph_algorithms.json` |
| CREATED | `data/review/B05-city-extract.json` |
| MODIFIED | `decision.md` |
| MODIFIED | `docs/backend/02_graph.md` |
| CREATED | `docs/evidence/B05-COMMANDS.md` |
| CREATED | `docs/evidence/B05-FILES.md` |
| CREATED | `docs/evidence/B05-RESULTS.md` |
| CREATED | `docs/evidence/B05-REVIEW_MANIFEST.md` |
| CREATED | `docs/evidence/B05-baseline-spec.txt` |
| CREATED | `docs/evidence/B05-baseline-tests.txt` |
| CREATED | `docs/evidence/B05-baseline.json` |
| CREATED | `docs/evidence/B05-canonical-status.json` |
| CREATED | `docs/evidence/B05-changes.patch` |
| CREATED | `docs/evidence/B05-city-before-positive-proof-fix.json` |
| CREATED | `docs/evidence/B05-city-evaluation.json` |
| CREATED | `docs/evidence/B05-controlled-results.json` |
| CREATED | `docs/evidence/B05-final-boundary-tests.txt` |
| CREATED | `docs/evidence/B05-frontend-example.json` |
| CREATED | `docs/evidence/B05-health.json` |
| CREATED | `docs/evidence/B05-integration-final.txt` |
| CREATED | `docs/evidence/B05-integration-first.txt` |
| CREATED | `docs/evidence/B05-integration-second.txt` |
| CREATED | `docs/evidence/B05-integration-strengthened.txt` |
| CREATED | `docs/evidence/B05-package-audit.json` |
| CREATED | `docs/evidence/B05-package-focused-tests.txt` |
| CREATED | `docs/evidence/B05-performance-before-positive-proof-fix.json` |
| CREATED | `docs/evidence/B05-performance.json` |
| CREATED | `docs/evidence/B05-positive-proof-tests.txt` |
| CREATED | `docs/evidence/B05-post-lifecycle.json` |
| CREATED | `docs/evidence/B05-regression-before-positive-proof-fix.txt` |
| CREATED | `docs/evidence/B05-regression-collection-error.txt` |
| CREATED | `docs/evidence/B05-regression-tests.txt` |
| CREATED | `docs/evidence/B05-scenario-dependencies.json` |
| CREATED | `docs/evidence/B05-source-audit.json` |
| CREATED | `docs/evidence/B05-spec-validation.txt` |
| CREATED | `docs/evidence/B05-unit-tests.txt` |
| MODIFIED | `flow.md` |
| MODIFIED | `implementation_status.md` |
| CREATED | `scripts/package_b05_review.py` |
| MODIFIED | `task_board.md` |
| MODIFIED | `test_log.md` |

Separate ignored deliverable:review_packages/Civicly_B05_Review.zip. It is intentionally outside Git and is verified by B05-package-audit.json.

Actual source:8 backend/app/graph/analysis modules; tests/b05_fixtures.py +b05_benchmark.py;29-unit model/contract checks and22 real algorithm/counterfactual/city integrations; graph_algorithms.json; review packager. Existing graph/migration/ingestion/source data/dependency pins and all prior tests are byte-identical to baseline (B05-source-audit.json).

Purposes/dependency boundaries:backend/ALGORITHMS.md; full per-included-file purpose/SHA256 table in REVIEW_MANIFEST.md inside ZIP (also B05-REVIEW_MANIFEST.md). Source topology and city are read-only; no B06 implementation.
