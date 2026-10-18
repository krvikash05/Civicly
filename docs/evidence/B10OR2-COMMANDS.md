# B10-O-R2 commands and observations

Working directory: `/Users/vikashkumar/Desktop/Civicly`. Python3.12.1,
pytest9.1.1; existing frozen75-package environment and Docker FalkorDB6.0.2.
No dependency/lock/image change. All Gemini responses below are MockTransport
simulations; actual MCP, graph, B09, LangGraph and SDK checkpoint operations run.
All external Gemini calls prohibited, including countTokens. No ZIP or B11.
Local accepted B10-O-R baseline `af42149`; no remote push.

## Baseline and minimal reproduction

Before source edits: `backend/.venv/bin/python scripts/audit_b10or.py` PASS
(old740-case acceptance and zero-call/unchanged-history evidence verified).
Security exclusions verified; local baseline committed with
`git add <reviewed B10-O-R files>` and
`git commit -m 'Accept reviewed B10-O-R token accounting and recovery baseline'`.
This records accepted work, not B10-O-R2 acceptance.

Actual old provider was exercised with explicit MockTransport,120k-character
context, full Selection schema, plausible counted input plus512output/1536thinking
receipts and private temporary ledgers. With explicit legacy $.15 case it stopped
before first generation because count reservation stayed held; with $.50 and
old60000 tokens, decisions1–2 passed and decision3 stopped TOKEN_BUDGET.
Results: B10OR2-before-cost-reproduction.json /before-reproduction.json.
The $.15 reproduction is an explicit legacy allocation, not the new $.50 default.
No historical ledger was changed.

Corrected reproduction, eight consecutive decisions, zero uncertain count rows:

```sh
PYTHONPATH=backend backend/.venv/bin/python docs/evidence/B10OR2-reproduce.py
```

## Stage1 — focused, overlapping batches (do not add totals)

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or2-stage1-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_agent_count_billing.py backend/tests/unit/test_agent_token_accounting.py backend/tests/unit/test_agent_models.py backend/tests/unit/test_agent_ledger_recovery.py backend/tests/unit/test_agent_provider.py backend/tests/unit/test_ai_provider_recovery.py backend/tests/unit/test_ai_spending.py backend/tests/unit/test_ai_execution_policy.py -q --durations=25 > /tmp/civicly-b10or2-stage1.txt 2>&1
```

98PASS,4.37s; later added three malformed/unknown-version cases. Contract parity:
`backend/.venv/bin/python -m pytest backend/tests/unit/test_agent_count_billing.py::test_supported_capacity_profiles_and_saved_settings_are_distinct -q --durations=25` →1PASS,.18s.

Final policy/outcome refinement:

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or2-focused-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_agent_count_billing.py::test_count_rejection_is_not_generation_or_unknown_billing backend/tests/unit/test_agent_count_billing.py::test_count_timeout_has_unknown_completion_but_known_nonbilling backend/tests/unit/test_agent_count_billing.py::test_unknown_or_expired_count_billing_contract_retains_reservation backend/tests/unit/test_agent_count_billing.py::test_malformed_count_response_is_failed_but_endpoint_is_nonbillable backend/tests/unit/test_agent_token_accounting.py::test_invalid_provider_counts_fail_without_generation -q --durations=25 > /tmp/civicly-b10or2-focused-final.txt 2>&1
```

16PASS,.60s. No Stage1 failures. Existing assertions adjusted compatibly in
only test_agent_models.py (finite maximum) and test_agent_token_accounting.py
(known count billing zero and explicit new finite bounds). No old test removed.

## Stage2 — actual local runtime, simulated Gemini HTTP

Local DB/socket/Docker access requires escaping the desktop filesystem sandbox;
the first strengthened single-road check without that access errored at Redis
setup (1ERROR/0tests executed,1.12s), then the exact test passed with access.
This was not an application failure; no constraint/policy was weakened.

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10.py --reprovision --compare docs/evidence/B10-before-lifecycle.json --output docs/evidence/B10OR2-before-lifecycle.json
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or2-stage2-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_agent_multistep_budget.py -q --durations=25 > /tmp/civicly-b10or2-stage2-first.txt 2>&1
```

PASS6retained threads;8PASS in108.57s. After final count-outcome refinement,
exact waterlogging case1PASS11.46s. After strengthening road/drain/history and
waste-schedule context assertions:

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or2-context-final-provider.jsonl backend/.venv/bin/python -m pytest 'backend/tests/integration/test_agent_multistep_budget.py::test_six_real_context_decisions_with_plausible_usage[ROAD_DAMAGE-VERIFIED-None]' 'backend/tests/integration/test_agent_multistep_budget.py::test_six_real_context_decisions_with_plausible_usage[ROAD_DAMAGE-CANDIDATE-None]' 'backend/tests/integration/test_agent_multistep_budget.py::test_six_real_context_decisions_with_plausible_usage[WASTE_ACCUMULATION-VERIFIED-None]' -q --durations=25 > /tmp/civicly-b10or2-context-final.txt 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or2-assert-final-provider.jsonl backend/.venv/bin/python -m pytest 'backend/tests/integration/test_agent_multistep_budget.py::test_six_real_context_decisions_with_plausible_usage[ROAD_DAMAGE-VERIFIED-None]' -q --durations=25 > /tmp/civicly-b10or2-assert-final.txt 2>&1
```

3PASS33.87s; final stricter incident identity assertion1PASS13.46s. Overlapping
reruns were targeted, no unrelated ingestion/lifecycle regressions during debugging.

## Stage3 — one final complete regression

Final application/test sources stable before the completed run. The first attempt
was deliberately interrupted for the genuine timeout-metadata correction below. Preflight repeated the exact
verify_b10 command above (PASS) to restore scoped dynamic ACL after prior lifecycle.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or2-final-provider-requests.jsonl backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence --durations=25 > /tmp/civicly-b10or2-final-tests.txt 2>&1
make test-spec > /tmp/civicly-b10or2-spec.txt 2>&1
```

Final counts/durations: see B10OR2-RESULTS.md and untouched B10OR2-final-tests.txt.
Both validators PASS; these are static contracts, not live product acceptance.
No additional full regression solely for harness/documentation revisions.

## Post-regression preservation and review audit

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10.py --reprovision --compare docs/evidence/B10-before-lifecycle.json --output docs/evidence/B10OR2-post-retained.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09.py --output docs/evidence/B10OR2-post-B01-B09.json --b08-anchor docs/evidence/B09-B08-after-final-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09r.py --output docs/evidence/B10OR2-post-B09R-history.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10or_spending.py verify --anchor docs/evidence/B10OR-spending-before.json --output docs/evidence/B10OR2-spending-after.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10or2_retained.py --log docs/evidence/B10OR2-final-tests.txt --guard docs/evidence/B10OR2-zero-live-proof.json --expected-passed 770 --output docs/evidence/B10OR2-post-B09-retained.json
backend/.venv/bin/python scripts/audit_b10or2.py
backend/.venv/bin/python scripts/audit_b10or2.py
git diff --check
git apply --reverse --check docs/evidence/B10OR2-changes.patch
```

After verifying rolling proofs, copy fresh B07R/B08/B09/B09R-runtime-proof.json
under B10OR2-regression-*; restore original bytes from local baseline af42149.
Audit twice so generated inventory includes itself/patch/audit; no source changes
or new tests involved. The new evidence adapter accepts pytest's warning-bearing
summary, checks raw770PASS/exit0/lifecycle markers, then reuses every original B09
DB/history assertion. Earlier B10-O-R regex limitation is already documented; no
old verifier/test/log normalized or rerun full suite to change its formatting.


### Genuine timeout-reporting correction during first attempt

First attempt stopped with SIGINT after148PASS/0FAIL,688.36s, before lifecycle,
when review found outer-deadline count-only metadata still claimed retained
reservation despite the correct zero ledger settlement. Raw log and exit2 guard:
B10OR2-interrupted-regression.txt /interrupted-zero-live-proof.json.
No full run repeated just for test-harness comparison. Added two deadline cases:

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or2-deadline-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_agent_count_billing.py::test_outer_deadline_count_summary_matches_durable_billing backend/tests/unit/test_ai_provider_recovery.py -q --durations=25 > /tmp/civicly-b10or2-deadline.txt 2>&1
```

Final focused14PASS4.57s in B10OR2-deadline.txt; existing generation timeout/holds and
new count-only known/unknown billing summaries checked. Repeated source/SDK
preflight and actual MCP/Saver1PASS11.17s, both specs PASS; then the same full command above restarted with final770-case source.
All final counts refer only to the completed final run, not interrupted148 cases.

Evidence-only event export initially sorted by nonexistent seq and failed after the eight simulated decisions; actual ledger schema inspected, corrected to existing id, exact reproduction reran PASS with immutable events. No application/test/ledger format change; full regression unaffected. Sanitized record in B10OR2-failed-attempts.json.
