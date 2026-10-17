# B05 commands and human reproduction

Repository root; existing isolated Python3.12 environment; actual pinned Compose.
.env remains ignored and never shared. No remote push or volume reset.
Baseline:258 PASS/0 FAIL/0 SKIP in162.42s; both SPEC validators PASS.
Local baseline command after source/secret/full-city read verification:

```sh
git add --all
git commit -m 'Baseline accepted B04 conversion ingestion and real database evidence'
```

Accepted B04 local baseline8aaf17c. Core acceptance/evidence commands executed:

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_graph_algorithm_models.py -q
backend/.venv/bin/python -m pytest backend/tests/integration/test_graph_algorithms.py -v -s
PYTHONPATH=backend backend/.venv/bin/python -m app.graph.analysis controlled --retain --output docs/evidence/B05-controlled-results.json
PYTHONPATH=backend backend/.venv/bin/python -m app.graph.analysis city --output docs/evidence/B05-city-evaluation.json
PYTHONPATH=backend backend/.venv/bin/python -m tests.b05_benchmark
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence
make test-spec
backend/.venv/bin/civicly health
backend/.venv/bin/civicly schema-status
backend/.venv/bin/python -m compileall -q backend/app/graph/analysis scripts/package_b05_review.py
git diff --check
backend/.venv/bin/python scripts/package_b05_review.py
```

Full regression output used `set -o pipefail` and `2>&1 | tee docs/evidence/B05-regression-tests.txt`.
Initial unit filename was test_graph_algorithms.py, renamed to avoid pytest basename
collision with integration module; its29 tests retained. Exact targeted positive-proof
correction commands (same real runtime):

```sh
backend/.venv/bin/python -m pytest backend/tests/integration/test_graph_algorithms.py::test_positive_zone_proof_is_not_lost_when_later_context_truncates backend/tests/integration/test_graph_algorithms.py::test_case_ranking_dates_real_history_and_coverage_gaps -v -s
backend/.venv/bin/python -m pytest backend/tests/integration/test_graph_algorithms.py::test_clone_writer_redirect_and_unrecorded_changes_are_refused backend/tests/integration/test_graph_algorithms.py::test_dynamic_root_id_is_parameterized_not_executable -v -s
```

Run evaluation/benchmark separately from lifecycle tests:restart/recreation temporarily
refuses connections. One baseline read attempted during restart failed accordingly,
then succeeded after lifecycle ended. No automatic transport retry weakened.

Human verification:run both focused test modules; inspect B05-controlled-results.json
counterfactuals.criticality (D1,D4→D4,D1), removed CUT edge/proof paths and unchanged
source fingerprint. In Browser http://127.0.0.1:3000 select retained source/clone names
from that JSON. Source CUT remains; clone CUT absent, candidate replacement explicitly
CANDIDATE. City source stays candidate-only, not falsely verified. Exact differences,
limits and S01–S12 authoring dependencies are in B05-RESULTS.md/B05-scenario-dependencies.json.

If failing, share redacted test output/error JSON and blockers.md. Never.env or keys.
Focused ZIP can reproduce its B05 tests; full309-test/SPEC reproduction requires the
full repository and preserved B04 data/runtime. ZIP manifest documents setup/dependencies.
B06 is proposed only after human B05 review; no MCP implementation began.

Archive reproduction also exercised both focused modules from a clean extraction:
51 PASS/0 FAIL/0 SKIP in88.60s, with imports explicitly checked to resolve inside
extracted source. Preserve the .venv interpreter invocation path; resolving its
symlink switches to global Python and can lose installed dependencies. CRC, exact
source bytes and secret scans run before and after writing the archive.
