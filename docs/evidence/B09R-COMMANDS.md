# B09-R commands and attempts

Run from `/Users/vikashkumar/Desktop/Civicly`, using the existing isolated Python3.12
and accepted retained Docker/FalkorDB/MCP runtime. No global installs or dependency
changes; no volume deletion, data promotion, remote push or ZIP.

## Accepted B09 baseline (before corrections)

```sh
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > /tmp/civicly-b09r-baseline-tests.txt 2>&1
make test-spec > /tmp/civicly-b09r-baseline-spec.txt 2>&1
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure --output /tmp/civicly-b09r-baseline-configuration.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09.py --output /tmp/civicly-b09r-baseline-retained.json --b08-anchor docs/evidence/B09-B08-after-final-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python -m tests.b09_evidence verify --proof docs/evidence/B09-retained-proof.json --lifecycle-log /tmp/civicly-b09r-baseline-tests.txt --output /tmp/civicly-b09r-baseline-B09-retained.json
PYTHONPATH=backend backend/.venv/bin/python /tmp/civicly-b09r-reproduce.py
PYTHONPATH=backend backend/.venv/bin/python /tmp/civicly-b09r-legacy.py
backend/.venv/bin/python scripts/audit_b09.py
git diff --cached --check -- . ':!docs/evidence'
git commit -m 'Accept B09 evidence and inspection foundation baseline'
```

Actual commit message used: `Accept B09 evidence and inspection foundation baseline`;
local commit688b893. The original temporary repro/legacy creation scripts are retained
as B09R-reproduce-before.py and B09R-create-legacy-before.py. They were executed
against the accepted pre-correction source, not against rule2. Legacy creation retains
only its new owned B08/B09 fixture; before repro deletes only its own graphs. Do not
rerun legacy creation to replace the supplied proof on corrected source.

Baseline582 PASS/0 FAIL/0 SKIP in724.05s; both SPEC validators PASS; original retained
records and70 prior trace observations PASS. Evidence files copied from temporary
outputs retain their actual content. The initial staged whitespace check without
path exclusion flagged original historical patch context/pytest-log trailing whitespace;
those original audit files were preserved verbatim and source-only check passed.

## Correction verification (actual command stages)

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_evidence_models.py backend/tests/unit/test_evidence_review.py -q > docs/evidence/B09R-unit-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_evidence_review.py -v -s > docs/evidence/B09R-integration-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_evidence_review.py -v -s > docs/evidence/B09R-integration-corrected.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/unit backend/tests/integration/test_evidence_domain.py -v -s > docs/evidence/B09R-compatibility-focused.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_evidence_review.py::test_january_repair_august_recurrence_and_retrospective_attribution -v -s > docs/evidence/B09R-chronology-strengthened.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_evidence_review.py::test_real_mcp_broker_reads_v2_report_provenance_without_contract_changes -v -s > docs/evidence/B09R-v2-mcp-focused.txt 2>&1
PYTHONPATH=backend backend/.venv/bin/python docs/evidence/B09R-reproduce-corrected.py > docs/evidence/B09R-reproduction-corrected.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests --collect-only -q > docs/evidence/B09R-test-collection-final.txt
backend/.venv/bin/civicly health > docs/evidence/B09R-health.json
backend/.venv/bin/civicly schema-status > docs/evidence/B09R-schema-status.json
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > docs/evidence/B09R-regression-tests.txt 2>&1
make test-spec > docs/evidence/B09R-spec-validation.txt 2>&1
```

The first unit filename was renamed to `test_evidence_review_models.py`: collecting
unit and integration files with the same basename caused one import-file mismatch
(597 other cases collected, no test executed in that failed collection). This fixes
only the new module name, not any old test. Corrected collection initially616, then617
after adding the explicit version2 real-MCP case. For a fresh focused rerun, use:

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_evidence_review_models.py backend/tests/integration/test_evidence_review.py -v -s
```

First real run13 PASS/1 FAIL: past-cutoff attribution unnecessarily read future mutable
cluster attributes while selecting incident identity. Corrected identity lookup validates
actual INVESTIGATES against the immutable open journal; incident/source visibility is
unchanged. Revised15 PASS; strengthened per-occurrence corroboration1 PASS; added actual
MCP version2 provenance1 PASS. All-unit + unchanged prior B09 integration420 PASS.
No mock replaces a real graph assertion. Negative fault-injection tests retain genuine
DB operations and explicitly simulated transport failures.

One ad hoc version-recording attempt referenced a nonexistent descriptive0001 filename
and stopped with FileNotFoundError before database access; corrected verified paths
are `backend/app/graph/migrations/0001.json` and `0002_mcp_traces.json`. Actual package,
module and migration hash output is B09R-versions.json. No migration was changed.

## Post-lifecycle and source checks

Execute sequentially after full regression finishes (ACL state is not in the AOF):

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure --output docs/evidence/B09R-post-configuration.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09.py --output docs/evidence/B09R-post-retained.json --b08-anchor docs/evidence/B09-B08-after-final-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python -m tests.b09_evidence verify --proof docs/evidence/B09-retained-proof.json --lifecycle-log docs/evidence/B09R-regression-tests.txt --output docs/evidence/B09R-post-B09-retained.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09r.py --output docs/evidence/B09R-post-corrected-history.json
backend/.venv/bin/python scripts/audit_b09r.py
git diff --check -- . ':!docs/evidence'
```

`configure` reuses existing private credentials and restores exact graph-scoped ACLs;
no values are printed. Original rolling B07R/B08/B09 test proofs are saved separately
as B09R regression proofs, then restored byte-for-byte from688b893. Logs retain actual
fresh outputs; original evidence is not overwritten. The audit verifies this and all582
old test sources plus migrations, dependencies, city artifacts, repository, writer,
algorithms and MCP implementation unchanged. Source hash freeze is verified again.

Full regression requires the established accepted retained local runtime; this is not
a clean-room bootstrap claim. Original retained graphs are not generated from hidden
scenario answers. For a separate fresh environment, restore accepted B01–B09 runtime
artifacts first; create the small v1 compatibility graph using the saved creation script
under baseline688b893, then return to corrected source and its proof path. Do not silently
replace a missing retained proof with fabricated rows or destructive resets.

The persistence test executes the existing project's exact Compose lifecycle:
`docker compose --project-directory /Users/vikashkumar/Desktop/Civicly -f /Users/vikashkumar/Desktop/Civicly/compose.yaml restart falkordb`, followed by the same prefix with
`up -d --wait --wait-timeout 120 falkordb` and
`up -d --force-recreate --wait --wait-timeout 120 falkordb`.
It verifies graph and Browser persistence with fresh connections and a new container ID.

Post-test read-only verifier first attempt stopped at receipt equality: the full regression
replayed the already committed correction, so its captured receipt has replayed=true;
`readback` defaults replayed=false. The verifier now passes the captured replay flag
explicitly. Application logic/DB records unchanged; no failed graph assertion was
masked. Corrected pre/post lifecycle verifier outputs record exact receipt readback.

Extended accepted-B09 trace probe initially walked arbitrary proof dictionaries and
matched JSON-schema `properties` as if they were result envelopes (same field names).
Those schema objects do not have execution IDs. Exact known result lists were then
checked:15 stored server records +15 city outputs +1 original fixture broker output,
all present with equal hashes/evidence. No trace was missing or recreated. The verifier
now selects these explicit artifact fields instead of recursively treating schemas as data.
