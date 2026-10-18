# B18 exact verification commands

Working directory /Users/vikashkumar/Desktop/Civicly; existing Python3.12 isolated backend/.venv. No dependency/image/container lifecycle changes. Ordinary pytest/children interlock external Gemini/countTokens. No full historical suite.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b18-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_operator_cli.py -q
```
63PASS0FAIL0SKIP0.44s. Parsing/accepted route mapping/private bounded files/sanitized errors/exitcodes/legacy forwarding. No DBsuccess claims in units.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b18-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_operator_cli_runtime.py -xq
```
First actual shared journey1PASS129.07s,3dependencydeprecation warnings. No failed database/runtime acceptance. Added scoped evidence-path explanation, evidenceget mapping and global reset-key/destination conflict checks after inspection, then reran the same directly affected cases:

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b18-refined-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_operator_cli.py -q
CIVICLY_TEST_REQUEST_LOG=/tmp/b18-refined-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_operator_cli_runtime.py -xq
```
68unitPASS0.45s,1realPASS132.37s. The same isolated water journey executes71actualCLI child invocations: realAuth/API/service/graph, actual official/domain discovery/MCPcall/Saver with existing offlineReadPause, sourcecitations, inspection/plan/approval/order/completion/followup/outcome, unauthorized/replay/actualcommittedreadbackfault,2freshresetprofiles. This is1distinct integration case, not71testcases. Both runs retain graphs; no failed graph repair/reset/quarantineclearance.

Final exception-only refinement retains computedrequestIDs if initial advance/reset intent persistence is uncertain. Healthy dispatch/storage logic unchanged; new fault/replay units only:
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b18-final-boundary-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_operator_cli.py::test_uncertain_initial_intent_preserves_original_request_id backend/tests/unit/test_operator_cli.py::test_advance_replay_never_dispatches -q
```
5PASS0.26s (3overlap+2new). Final **70distinctunit+1real =71distinctPASS**,0FAIL/0SKIP. Existing real committed-domain uncertainty path exercised through CLI; initial-intent faults are explicitly mocked unit evidence. No full water journey rerun solely for exception wrapping.

Both specification validators after final application/tests/contracts, one invocation:
```sh
CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/b18-spec-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec
```
PASS/PASS; each chains existing validators plus new validate_cli.py static command/service parity. Static checks are not runtime/model proof.

Other exact checks:
```sh
PYTHONPATH=backend backend/.venv/bin/python -m cli --help
PYTHONPATH=backend backend/.venv/bin/python docs/evidence/B18-audit-script.py
git diff --check
git apply --reverse --check docs/evidence/B18-changes.patch
```
One development metadata utility initially used system python3 importing cli.main and failed ModuleNotFoundError:pydantic; corrected to locked backend/.venv/bin/python. No source/contract write occurred on that failed invocation; all real tests and validators used the proper venv. No test failure or skip concealed.

CLI child template actually executed:
```sh
PYTHONPATH=backend/test_guards:backend backend/.venv/bin/python -m cli --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --session "$PRIVATE_SESSION" --at "$CONTROLLED_UTC" GROUP ACTION --id "$ID" --payload "$JSON_FILE" --key "$EXPLICIT_KEY"
```
Use --query for accepted readfilters; only --reviewer-session privatepath for independent reviewer. No password/bearertoken in argv/logs/output. tests.b18_fault is a **test-only** child replacing EvidenceService.readback after actual commit; it invokes the same CLI and has no production flag. Child has60second timeout and expected exitcodes; no arbitrary user command/shell. Actual sanitizedcommandsequence/count/IDs in B18-cli-journey.json, short human walkthrough B18-WALKTHROUGH.md and full operator guide backend/OPERATOR_CLI.md.

One directly affected accepted foundation compatibility case (not fullfoundation suite):
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b18-legacy-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_foundation.py::test_invalid_cli_configuration_is_redacted -q
```
1PASS; verifies new entrypoint still exercises original health invalid-settings/redaction behavior. Final total supersedes prior subtotal: **71distinctunit +1real =72distinctPASS**. Six retained pytest/child guards, all0external/0unexpected.

Read-only audit first failed to find the integration profile through pytest-current after a later unit run (StopIteration, no DB mutation). Corrected the retained-profile lookup to match the proof source across pytest directories; same audit command then PASS. Final audit runs after patch generation and scans that patch too. No runtime/test acceptance failure resulted.
