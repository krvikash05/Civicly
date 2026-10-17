# Exact B04 file inventory and diff

Accepted local baseline:09482e241470a93bded38ad11a974f2c846aa046. No push. All paths below are repository-relative.

B04-changes.patch contains tracked and new implementation/contracts/data/documentation changes relative to that baseline. Generated evidence under docs/evidence is listed here but omitted from the patch to avoid self-inclusion/recursive evidence. Actual evidence files remain in the repository. No application logic from B05 or later is introduced.

| State | Path |
|---|---|
| CREATED | `backend/B04_REVIEW.md` |
| MODIFIED | `backend/GRAPH_ACCESS.md` |
| CREATED | `backend/INGESTION.md` |
| MODIFIED | `backend/app/graph/schema.py` |
| CREATED | `backend/app/ingestion/__init__.py` |
| CREATED | `backend/app/ingestion/__main__.py` |
| CREATED | `backend/app/ingestion/audit.py` |
| CREATED | `backend/app/ingestion/benchmark.py` |
| CREATED | `backend/app/ingestion/conversion.py` |
| CREATED | `backend/app/ingestion/importer.py` |
| CREATED | `backend/tests/ingestion_examples.py` |
| CREATED | `backend/tests/integration/test_ingestion.py` |
| CREATED | `backend/tests/unit/test_ingestion_conversion.py` |
| MODIFIED | `blockers.md` |
| CREATED | `contracts/dataset_ingestion.json` |
| CREATED | `data/generated/source_city_v2.json` |
| CREATED | `data/ingestion/DATA_QUALITY.md` |
| CREATED | `data/ingestion/city-v3.json` |
| CREATED | `data/ingestion/conversion-report.json` |
| CREATED | `data/ingestion/generator-revision-changes.json` |
| CREATED | `data/ingestion/input-manifest.json` |
| CREATED | `data/ingestion/legacy-conversion/city-v3.json` |
| CREATED | `data/ingestion/legacy-conversion/conversion-report.json` |
| CREATED | `data/ingestion/legacy-conversion/input-manifest.json` |
| CREATED | `data/ingestion/legacy-conversion/release-manifest.json` |
| CREATED | `data/ingestion/legacy-conversion/scenario-readiness.json` |
| CREATED | `data/ingestion/legacy-conversion/selected-source-audit.json` |
| CREATED | `data/ingestion/legacy-v1/city-v3.json` |
| CREATED | `data/ingestion/legacy-v1/conversion-report.json` |
| CREATED | `data/ingestion/legacy-v1/input-manifest.json` |
| CREATED | `data/ingestion/legacy-v1/release-manifest.json` |
| CREATED | `data/ingestion/legacy-v1/scenario-readiness.json` |
| CREATED | `data/ingestion/legacy-v1/selected-source-audit.json` |
| CREATED | `data/ingestion/release-manifest.json` |
| CREATED | `data/ingestion/scenario-readiness.json` |
| CREATED | `data/ingestion/selected-source-audit.json` |
| CREATED | `data/ingestion/source-audit.json` |
| MODIFIED | `decision.md` |
| MODIFIED | `docs/backend/03_data.md` |
| CREATED | `docs/evidence/B04-COMMANDS.md` |
| CREATED | `docs/evidence/B04-FILES.md` |
| CREATED | `docs/evidence/B04-PERFORMANCE.md` |
| CREATED | `docs/evidence/B04-aof-activity.txt` |
| CREATED | `docs/evidence/B04-baseline-hashes.json` |
| CREATED | `docs/evidence/B04-benchmark-first-failure.txt` |
| CREATED | `docs/evidence/B04-benchmark-progress.txt` |
| CREATED | `docs/evidence/B04-benchmarks.json` |
| CREATED | `docs/evidence/B04-canonical-status.json` |
| CREATED | `docs/evidence/B04-changes.patch` |
| CREATED | `docs/evidence/B04-hardware.txt` |
| CREATED | `docs/evidence/B04-health-before-regression.json` |
| CREATED | `docs/evidence/B04-health.json` |
| CREATED | `docs/evidence/B04-images.json` |
| CREATED | `docs/evidence/B04-import-first-failure.txt` |
| CREATED | `docs/evidence/B04-import-tests.txt` |
| CREATED | `docs/evidence/B04-legacy-prepare.txt` |
| CREATED | `docs/evidence/B04-legacy-v1-prepare.txt` |
| CREATED | `docs/evidence/B04-prepare.txt` |
| CREATED | `docs/evidence/B04-regression-before-envelope-tests.txt` |
| CREATED | `docs/evidence/B04-regression-tests.txt` |
| CREATED | `docs/evidence/B04-retained-post-recreation.json` |
| CREATED | `docs/evidence/B04-runtime.json` |
| CREATED | `docs/evidence/B04-security-audit.json` |
| CREATED | `docs/evidence/B04-spec-validation.txt` |
| CREATED | `docs/evidence/B04-unit-tests.txt` |
| MODIFIED | `flow.md` |
| MODIFIED | `implementation_status.md` |
| MODIFIED | `scripts/generate_demo_seed.py` |
| MODIFIED | `scripts/validate_blueprint.py` |
| CREATED | `scripts/validate_dataset.py` |
| MODIFIED | `scripts/validate_handoff.py` |
| MODIFIED | `task_board.md` |
| MODIFIED | `test_log.md` |
| CREATED | `docs/evidence/B04-source-hashes.json` |

Total:74 files (12 modified; 62 created).

No dependency lock/image/registry/migration0001/graph-access policy/original fixture or prior test file modified. Existing B03 review package/extracted source, secrets, virtual environments, caches, Git internals and database volumes are excluded. New generated source/converted data are directly relevant B04 artifacts, with originals retained.

Purpose map:app/ingestion contains offline conversion/audit, strict importer and real benchmark/CLI; ingestion_examples and ingestion tests supply synthetic fixtures + real DB verification; dataset_ingestion.json fixes new input/provenance/visibility rules; generator/spec scripts prevent reintroduced numeric defects; data/ingestion records original/corrected manifests/quarantines/readiness; docs/evidence records actual commands/results/diff/runtime/security; six tracking files preserve decisions/status/history. See backend/INGESTION.md and B04_REVIEW.md for details.
