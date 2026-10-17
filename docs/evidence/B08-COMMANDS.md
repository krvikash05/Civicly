# B08 exact commands, observations and human reproduction

Project root `/Users/vikashkumar/Desktop/Civicly`. Python3.12.1, Pydantic2.14.1,
FalkorDB Python1.8.0/Redis8.1.0/MCP2.3.0/FalkorDB6.0.2 unchanged; no installs/push/ZIP.

## Accepted baseline before implementation

```sh
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > /tmp/civicly-b08-baseline-tests.txt 2>&1
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure --output /tmp/civicly-b08-baseline-configuration.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b07.py --output /tmp/civicly-b08-baseline-retained.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b07r_traces.py
backend/.venv/bin/python scripts/audit_b07r.py
```

440 PASS/0 FAIL/0 SKIP in386.74s, native migrations/source/B01/B05/traces verified.
Historical audit stopped only on absent non-source Archive.zip (recorded, not recreated).
Fresh private-value/source audit passed368 Git candidates,331 historical protected
files unchanged; archive patterns added to.gitignore. Source-only whitespace check
used because raw saved patches/pytest tracebacks contain meaningful context whitespace:

```sh
git add -A
backend/.venv/bin/python /tmp/civicly-b08-audit-baseline.py
git diff --cached --check
git diff --cached --check -- . ':(exclude)docs/evidence/**'
git commit -m 'Baseline accepted B07 and B07-R MCP runtime, history corrections and evidence'
git rev-parse HEAD
git status --porcelain
```

Initial all-file whitespace command exit2 on historical evidence only; source-only
PASS. Local clean baseline `6afdd09892502a8b47a7f840ced1491c38a002d3`, no push. Sanitized
baseline audit/hashes/retained/full log copied into B08-baseline-* evidence. Existing
B07-R fixture tests regenerate their proof; baseline contains refreshed real proof,
all earlier database trace observations retained. No application change before commit.

## B08 unit / actual DB-MCP progression

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_complaint_models.py -v > docs/evidence/B08-unit-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_complaint_intelligence.py::test_same_report_stable_retry_and_raw_source_preservation -v -s > docs/evidence/B08-smoke-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_complaint_intelligence.py -v -s > docs/evidence/B08-integration-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/unit/test_complaint_models.py backend/tests/integration/test_complaint_intelligence.py -v -s > docs/evidence/B08-focused-tests.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_complaint_intelligence.py::test_conflicting_measurements_retained_without_arbitrary_choice backend/tests/integration/test_complaint_intelligence.py::test_missing_asset_context_does_not_merge_location_only_reports backend/tests/integration/test_complaint_intelligence.py::test_multiple_eligible_clusters_require_review_instead_of_arbitrary_assignment -v -s > docs/evidence/B08-strengthened-cases.txt 2>&1
```

First27 pure unit PASS in0.16s; actual single-query smoke1 PASS in2.86s; first21 real
PASS in60.11s; strengthened57 (28unit/29real) PASS in89.25s; extra3 real PASS in7.01s.
Interruption hooks are labeled: real journal retained before an injected app stop;
real native UNIQUE error rolls back actual batch; before/after-real-query dropped
response never returns fake success. Actual MCP SDK/broker validates new incident
reads with explicitly labeled test-only source substitution; production unchanged.

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_complaint_models.py::test_equivalent_measurements_have_one_canonical_request_identity -v > docs/evidence/B08-unit-normalization-reproduction.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/unit/test_complaint_models.py -v > docs/evidence/B08-unit-tests.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_complaint_intelligence.py::test_prepared_equivalent_unit_retry_preserves_first_raw_measurement -v -s > docs/evidence/B08-equivalent-unit-real.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_complaint_intelligence.py::test_prepared_equivalent_unit_retry_preserves_first_raw_measurement backend/tests/integration/test_complaint_intelligence.py::test_issue_primary_asset_allows_secondary_cross_category_infrastructure -v -s > docs/evidence/B08-final-refinements.txt 2>&1
```

New unit repro1 FAIL in0.25s (0.29m/29cm canonical hashes differed). Fixed decimal
conversion/canonical request identity and first-original resume.33 unit PASS in0.52s;
new real recovery1 PASS in2.55s; final2 real refinements PASS in4.82s. No dataset or
old test repair. Mixed road+pipe+drain assets allowed with appropriate primary type.

## Full regression and specification

```sh
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > docs/evidence/B08-regression-tests.txt 2>&1
make test-spec > docs/evidence/B08-spec-validation.txt 2>&1
```

Interim504 PASS/0 FAIL/0 SKIP in448.77s retained as
B08-regression-before-canonical-unit-fix.txt. Same full command rerun against final
source with507 tests (440 accepted +33 new unit +34 actual integration). Both static
validators run separately; no live model/agent or B09 operational claim.

## Actual retained B08 proof and lifecycle

```sh
PYTHONPATH=backend backend/.venv/bin/python -m tests.b08_evidence create --proof docs/evidence/B08-retained-proof.json
PYTHONPATH=backend backend/.venv/bin/python -m tests.b08_evidence verify --proof docs/evidence/B08-retained-proof.json --output docs/evidence/B08-retained-before-lifecycle.json
```

Created one small owned B08 graph and5 real intakes; full before/after fingerprints,
actual REPORTS/PART_OF chains and receipts retained. Five retries changed no domain
counts/revision/audit; owner/epoch changes are expected. Before-lifecycle report makes
no lifecycle claim. After final real full-suite restart/recreation:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m tests.b08_evidence verify --proof docs/evidence/B08-retained-proof.json --anchor docs/evidence/B08-retained-before-lifecycle.json --lifecycle-log docs/evidence/B08-regression-tests.txt --output docs/evidence/B08-retained-after-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure --output docs/evidence/B08-runtime-configuration.json
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly proof --output docs/evidence/B08-city-mcp-proof.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b08.py --output docs/evidence/B08-post-lifecycle.json
backend/.venv/bin/python scripts/audit_b08.py
backend/.venv/bin/python -m compileall -q backend/app/services/complaints backend/tests/b08_fixtures.py backend/tests/b08_server.py backend/tests/b08_evidence.py scripts/audit_b08.py scripts/verify_b08.py
git diff --check -- . ':(exclude)docs/evidence/**'
git apply --reverse --check docs/evidence/B08-changes.patch
```

After full regression, copy regenerated B07-R fixture proof to
B08-B07R-regression-proof.json, then restore accepted B07R-runtime-proof.json from
Git HEAD bytes. Old source/tests/evidence remain untouched; fresh-run proof retained.
Accepted trace verification reads HEAD proof IDs/hashes, not a rolling proof artifact.
All source city record/revision/audit/writer fingerprints, original B01 and B05 source/
clone, migration readiness and accepted trace observations checked by fresh clients.
Actual private values scanned only in memory, never logged. No external archive claim.

## Two-minute human review

Run focused B08 tests or select stable-retry, concurrency and uncertain-write cases.
Inspect B08-runtime-proof.json for all three validators, reported quantities, missing/
contradictory evidence and qualified classifications. Browser use retained graph from
B08-retained-proof.json and this fixed read query:

```cypher
MATCH (c:Complaint)-[:REPORTS]->(i:Incident)-[:PART_OF]->(p:ProblemCluster)
RETURN c.id,i.id,i.issue_type,p.id,p.pattern_type ORDER BY c.id LIMIT 100
```

Expect5 complaints,4 incidents,2 contextual clusters in that authored fixture; inspect
recorded counts in proof rather than assuming full municipal dataset. Retried source
records do not duplicate, independent reports can share one incident, different events
remain distinct. Cross-category links remain context, not cause. If rerunning verify,
use latest verification output as --anchor (its after_retry fingerprint). Create refuses
overwrite; use a new /tmp proof path for a fresh graph. On failure share sanitized test
log +blockers.md, never.env/.runtime. STOP after B08; B09 requires human review.
