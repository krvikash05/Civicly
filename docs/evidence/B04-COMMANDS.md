# B04 reproduction and executed acceptance commands

Run from repository root, using the accepted isolated Python3.12 environment and
existing Compose deployment. Local credentials come from ignored.env, never logs.
Baseline local commit:09482e241470a93bded38ad11a974f2c846aa046; no push.
The full regression includes actual Docker restart/recreation; run after benchmark,
never concurrently with an active import. No volume deletion/reset command is used.

```sh
# Accepted baseline (135 PASS); then clean local baseline commit after secret scan.
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence
backend/.venv/bin/civicly schema-status
# Recorded commit command:
git commit -m 'Baseline accepted B03-R graph access and corrective contracts'

backend/.venv/bin/python scripts/generate_demo_seed.py
PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion audit
PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion prepare --documents
PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion prepare --source contracts/seed_graph_expanded.json --output-dir data/ingestion/legacy-conversion
PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion prepare --source contracts/seed_graph.json --output-dir data/ingestion/legacy-v1
backend/.venv/bin/python -m pytest backend/tests/unit/test_ingestion_conversion.py -q
backend/.venv/bin/python -m pytest backend/tests/integration/test_ingestion.py -v -s
backend/.venv/bin/python -m pytest backend/tests/unit -q

# Benchmark command was attempted once before precision correction (FAIL), then
# rerun exactly as below for pilot +3 fresh full trials +2 repeats per trial.
set -o pipefail
PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion.benchmark --retain-last | tee docs/evidence/B04-benchmark-progress.txt

backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence
make test-spec
backend/.venv/bin/civicly health
backend/.venv/bin/civicly schema-status
backend/.venv/bin/python -m compileall -q backend/app/ingestion scripts/validate_dataset.py
git diff --check
```

Important: rerunning prepare changes actual materialization time and therefore content
hashes. Reuse the checked-in compiled bundle for repeats against the retained graph;
new source/time is an explicit version conflict. The benchmark always uses fresh
UUIDv4 B04 graphs and cleans only its successful scratch targets. Final and failed
trial targets are retained. CLI reproduction of the retained graph's no-op import:

```sh
# Retained final trial graph; never substitute canonical.
PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion import --graph civicly_b04_test_a84beda80da64aacbc367a9399e07a97 --bundle data/ingestion/city-v3.json --report /tmp/civicly-b04-review-import.json
```

Source preparation and real DB acceptance are different checks. B04 numerical
probes used parameterized `RETURN $x` in GRAPH.RO_QUERY, never fixture Cypher.
Further read-only runtime/hardware/hash/security inventories are recorded separately.
