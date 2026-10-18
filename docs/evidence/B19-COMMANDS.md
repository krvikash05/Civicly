# B19 exact focused commands and outcomes

CWD /Users/vikashkumar/Desktop/Civicly, Python3.12 backend/.venv, existing FalkorDB module60002. No dependency/image/migration/lifecycle changes, no full suites or live provider.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b19-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_demo_scenarios.py -q
```
42PASS0.77s, initial definition/contract units. Later extended units supersede/overlap, not additional distinct cases.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b19-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_demo_runtime.py -xq
```
3PASS/1FAIL35.00s, stopped on PRIMARY-S04. Road complaint initially referenced only pipe; actual B08 rejected missing road target after fresh provisioning, truthfully UNKNOWN. Correct new fixture composition; retain original failed source/transport intent, no repair/retry. Subsequent all variants covered in selection below.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b19-remaining-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_demo_runtime.py -xq -k 'not (PRIMARY and (S01 or S02))'
```
23PASS/1FAIL/2deselected192.51s.22mechanics+postcommit fault PASS, representative probe failed because test reused same execution ID for different actual MCPcalls; TraceStore rejected collision. Unique per-call IDs corrected. One PRIMARY-S03 overlaps initial pass. All24 variants now have passing mechanics evidence.

Final source refinements: scoped file isolation, authenticated field-journal recovery identity, existing-fence merge, Operations.validate for later-stage exact source/plan readiness. Relevant units and directly affected real cases only:

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b19-final-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_demo_scenarios.py backend/tests/unit/test_operator_cli.py::test_command_exact_accepted_api_mapping backend/tests/unit/test_operator_cli.py::test_closed_parser_does_not_echo_private_input backend/tests/unit/test_operator_cli.py::test_legacy_command_arguments_forwarded_unchanged -q
CIVICLY_TEST_REQUEST_LOG=/tmp/b19-boundary-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_http_boundary.py::test_value_error_after_invocation_is_unknown_even_without_observed_write backend/tests/unit/test_http_boundary.py::test_done_replay_and_conflicting_key_never_redispatch backend/tests/unit/test_http_boundary.py::test_retained_request_journal_prevents_false_rejection_without_new_revision -q
```
109PASS1.06s +3PASS0.23s =112distinctunit cases (62new scenario cases +47command/parser/legacy compatibility cases including dynamic demo mappings +3accepted recovery cases). Not DB/model proof. No old test removed/rewritten.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b19-final-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_demo_runtime.py -xq -k '(PRIMARY and (S04 or S07)) or postcommit or representative'
```
3PASS/1FAIL/22deselected41.07s. Final S04/S07 and postcommit recovery PASS; representative probe missing required external-evidence evidence_type; actual broker denied INVALID_ARGUMENTS. Test-only required argument corrected, no weakening tool schema.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b19-representative-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_demo_runtime.py::test_representative_real_cli_mcp_saver_events_and_hidden_isolation -xq
```
1PASS37.38s. Actual CLI children, real MCP initialization/list/calls, SDK-backed sourced procedures, real UNAVAILABLE external capability, bounded ReadPause event worker/Saver, graph/trace/report readback, scoped file denial, unreleased-category isolation and retained checkpoint bytes. Scripted offline choices and authored world evidence, not AI solve. Existing SDK Pydantic deprecation warning in each integration invocation; no lifecycle/full-suite rerun.

Final distinctpytest totals **138PASS:112unit +26real (24variant mechanics +1uncertainty +1representative),0unresolvedFAIL/0SKIP**. Historical failed attempts3, all documented above; deselection is deliberate scope control, not skipped acceptance. Repeated tests are not additional distinct passes. Full PLAN/FOLLOWUP success for every scenario not claimed; operator prerequisites/unsupported branches in readiness matrix. Seven pytest/child guard proofs0external/0unexpected.

```sh
CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/b19-spec-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec
```
Both validators PASS in one invocation after final executable/contract edits, includes55actualAPIoperations/52paths, CLI parity,12world/24variant validation. Later whitespace-at-EOF cleanup/docs/evidence only. Static, not runtime/behavior proof. Separate empty guarded spec audit file0attempts.

```sh
PYTHONPATH=backend backend/.venv/bin/python docs/evidence/B19-audit-script.py
git diff --check
git apply --reverse --check docs/evidence/B19-changes.patch
```
Read-only preservation/private-value/accounting checks and patch verification; no graph lifecycle or data repair. One early schema-generation utility KeyError('implementation') occurred before contract writes; corrected actual key, not a hidden test failure. git diff --check initially reported two new blank EOF lines in validator scripts; whitespace removed.

Measured latest passing mechanics:48fresh setup calls,2.8234–3.9651s each; typed release0.0672–0.1759s per case. These are local measured observations, not reliability promises or model-latency metrics. Bootstrap/MCP/Saver costs appear in whole-test timings above. Initial+remaining+final passing proof files retained separately; consolidated B19-mechanics.json selects latest passing result per scenario/variant.

A trailing ad-hoc metadata snippet after successful documentation appends contained invalid Python import syntax and failed before executing any Python/file/database action. Replaced by the proper venv OpenAPI generation below; not a pytest/spec failure:
```sh
PYTHONPATH=backend backend/.venv/bin/python - <<'PY'
from pathlib import Path
import json
from app.api.application import create_app
Path('docs/evidence/B19-openapi.json').write_text(json.dumps(create_app().openapi(),indent=2)+'\n')
PY
```

## Final retention, identity and normative contract correction (supersedes subtotals above)

Read-only audit found older pytest temporary profiles auto-cleaned while graphs remained. Review fixture now writes private .runtime/b19-review/<random>/ profiles instead; earlier graphs untouched, old failing audit log retained. Focused retention recheck:
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b19-retained-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_demo_runtime.py -xq
```
25PASS/1FAIL210.80s. Actual representative worker hit shared trace collision because direct baseline case creation reused investigation IDs across fresh graphs. Fixed new scenario case requests through existing source/actor-bound request_identity; no old wake retry/quarantine clearance. Existing failed source/checkpoint/quarantine preserved. Initial deferred normative fields also reconciled explicitly in DEC-065: seed/confirm, expected_current_stage, required original DTO fields and actual durable event_id, additive safe details only.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b19-contract-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_demo_scenarios.py backend/tests/unit/test_operator_cli.py::test_command_exact_accepted_api_mapping backend/tests/unit/test_operator_cli.py::test_closed_parser_does_not_echo_private_input backend/tests/unit/test_operator_cli.py::test_legacy_command_arguments_forwarded_unchanged -q
CIVICLY_TEST_REQUEST_LOG=/tmp/b19-final-contract-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_demo_runtime.py -xq
CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/b19-final-spec-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec
```
118unitPASS1.32s (71scenario units +47CLI compatibility), plus the directly affected3accepted Boundaryunits above =121distinctunit. Final complete focused B19real selection **26PASS226.85s**,1existing SDKdeprecation warning,0FAIL/0SKIP. Both finalspecvalidatorsPASS; earlier spec invocation retained as historical overlap. Latest48setup calls2.6940–4.5487s, release0.0809–0.1995s. Final **147distinctPASS:121unit/26real**,0unresolvedFAIL/0SKIP. Four failed pytest attempts total, documented above; audit lookup/metadata utilities separate. Tenpytest/child guards+two guarded spec reports0external/0unexpected. No fullhistorical/lifecycle/live. Failed B19quarantine auditproof separate; final actual profiles retained privately, no repair/retry. B19-mechanics.json consolidates final24variants from a unique retained per-invocation artifact; original artifacts preserved.

## Final replay identity commands (supersedes147 subtotal)

`CIVICLY_TEST_REQUEST_LOG=/tmp/b19-replay-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_demo_scenarios.py::test_uncertain_replay_preserves_verified_entity_over_route_label backend/tests/unit/test_http_boundary.py::test_value_error_after_invocation_is_unknown_even_without_observed_write backend/tests/unit/test_http_boundary.py::test_done_replay_and_conflicting_key_never_redispatch backend/tests/unit/test_http_boundary.py::test_retained_request_journal_prevents_false_rejection_without_new_revision -q`
4PASS0.35s,1new+3overlap.

`CIVICLY_TEST_REQUEST_LOG=/tmp/b19-replay-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_demo_runtime.py::test_real_postcommit_release_failure_no_redispatch -xq`
1setupERROR4.40s sockettimeoutbeforefaultpath.

`docker ps --format '{{.Names}} {{.Status}}'` and `PYTHONPATH=backend backend/.venv/bin/python -m cli health --env-file .env`: containerhealthy/CLIhealthok, read-only/no lifecycle.

`CIVICLY_TEST_REQUEST_LOG=/tmp/b19-replay-retry-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_demo_runtime.py::test_real_postcommit_release_failure_no_redispatch -xq`
Freshfixture1PASS25.17s,1existingwarning, actual committedreport andexactreplayidentitiesequal/no duplicate; nooldrequestretry/repair/quarantineclearance.

`CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/b19-replay-spec-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec`
BothfinalvalidatorsPASS afterlast executablechange. Final148distinctPASS122unit/26real,0unresolvedFAIL/0SKIP;4historicalfailedassertions+1setupERROR recorded.13pytestchild+3guardedspecproofs0external/0unexpected. No further broad/lifecycle/providercalls. One attempted documentation tool wrapper syntax error occurred before execution/writes; corrected same append command, not acceptance-test failure.
