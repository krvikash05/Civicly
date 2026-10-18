# B20-R-UTILITY-R exact focused commands

Working directory `/Users/vikashkumar/Desktop/Civicly`. Existing Python3.12 isolated environment. Ordinary pytest installs the Gemini/countTokens interlock for itself/children. Local DB invocations use the existing bounded socket10second override; query/broker budgets unchanged. No lifecycle, negative journey, broad historical regression or live/provider call.

| Command | Evidence | Result |
|---|---|---|
| `CIVICLY_TEST_REQUEST_LOG=/tmp/B20R-UTILITY-R-repro-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_utility_intervention.py -k complete_road_binding -q` | review-repro.txt | Before correction:3FAIL/7PASS/41deselected. Two ambiguous drafts admitted; sole nonlinked substitution had TARGET instead of exact-binding rejection. Reproduction retained. |
| `CIVICLY_TEST_REQUEST_LOG=/tmp/B20R-UTILITY-R-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_utility_intervention.py -q` | units.txt |51PASS; no skips |
| `CIVICLY_TEST_REQUEST_LOG=/tmp/B20R-UTILITY-R-unit-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_utility_intervention.py -q` | units-final.txt |52PASS in1.20s after adding same-draft/fresh-topology regression;38accepted+14new |
| `FALKORDB_SOCKET_TIMEOUT_SECONDS=10 CIVICLY_TEST_REQUEST_LOG=/tmp/B20R-UTILITY-R-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_utility_intervention_runtime.py::test_s04_primary_utility_intervention_and_uncertainty -q` | real.txt |1FAIL in23.69s: new test survey omitted mandatory updated_at. Original source graph retained; no repair. |
| `FALKORDB_SOCKET_TIMEOUT_SECONDS=10 CIVICLY_TEST_REQUEST_LOG=/tmp/B20R-UTILITY-R-real-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_utility_intervention_runtime.py::test_s04_primary_utility_intervention_and_uncertainty -q` | real-final.txt | Final corrected real PRIMARY result in log/results. |
| `CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/B20R-UTILITY-R-spec-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec` | spec.txt |Both validatorsPASS; followed by fixture-only updated_at correction, final validator rerun below. |
| `CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/B20R-UTILITY-R-spec-final-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec` | spec-final.txt |Both final validators; exact result in log/results. |

Stdout/stderr redirected to `docs/evidence/B20R-UTILITY-R-<evidence> 2>&1`. Counts are distinct cases, not summed overlapping passes. Review-repro deselections are intentionally excluded by -k, not skipped. No unchanged NEGATIVE rerun. No MCP/Saver/model behavior changed; existing real PRIMARY uses DB/SDK GraphRAG/API/CLI with explicit authored synthetic observations and injected readback fault, no model solver.

Final read-only preservation command (no mutation/tests):
`FALKORDB_SOCKET_TIMEOUT_SECONDS=10 CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/B20R-UTILITY-R-retention-provider.jsonl PYTHONPATH=backend/test_guards:backend backend/.venv/bin/python docs/evidence/B20R-UTILITY-R-retention-script.py > docs/evidence/B20R-UTILITY-R-retention.txt 2>&1`
Result:PASS; versions, historical accounting/checkpoints/quarantines/city and new graph proof in retention.json. Review patch inventory generated against /tmp/b20r-utility-r-baseline; no earlier uncommitted changes included.
