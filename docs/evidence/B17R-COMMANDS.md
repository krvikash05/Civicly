# B17-R exact focused commands

Working directory /Users/vikashkumar/Desktop/Civicly. Existing Python3.12 isolated backend/.venv; no package/image changes. Ordinary pytest and children block external Gemini/countTokens.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b17r-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_http_query_parameters.py -q
```
Initial59cases:58PASS/1FAIL,8.20s. The approvals-list mock used ANALYST and correctly received403 instead of the query-boundary409sentinel. Application did not fail; fixture corrected to APPROVER (the role required by that existing route). Initial log/proof retained separately.

Only directly affected group rerun:
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b17r-unit-corrected-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_http_query_parameters.py::test_supported_queries_reach_projection_with_existing_types -q
```
13PASS,1.93s (12overlap +1corrected case). Final **59distinct unitPASS**,0unresolvedFAIL/0SKIP. Mock projection boundary409READ_CAPACITY is a deliberate sentinel, not fabricated database success. Units check rejected/accepted/typed/repeated parameters, exact OpenAPI/model/allowlist equality and bounds. Real functionality is exercised below.

Single real integration invocation after final application/test edits:
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b17r-real-provider.jsonl CIVICLY_FRONTEND_EVIDENCE_PREFIX=B17R backend/.venv/bin/python -m pytest backend/tests/integration/test_frontend_runtime.py::test_frontend_readiness_real_journey_and_tcp_sse -xq
```
Actual existing isolated journey retained with new assertions: reproduced hypotheses date422, status/pagination; dashboard unused pagination422 and meaningful filter metric changes; trace date window; resource filter changes; graph/SSE/MCP/Saver/HTTP/TCP full existing journey. New B17R-journey.json only; old B17proof unchanged. No full historical suite/lifecycle/provider.

Both validators once after final application/test/contracts:
```sh
CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/b17r-spec-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec
```
Make expands backend/.venv/bin/python scripts/validate_blueprint.py then validate_handoff.py; static PASS is not runtime proof.

Contract generation, audit and patch validation:
```sh
PYTHONPATH=backend backend/.venv/bin/python docs/evidence/B17R-export-contracts.py
PYTHONPATH=backend backend/.venv/bin/python docs/evidence/B17R-audit-script.py
git diff --check
git apply --reverse --check docs/evidence/B17R-changes.patch
```
Patch baseline is actual accepted uncommitted B17working tree `/tmp/b17r-baseline/files`; no Git commit/push/reset. No earlier evidence/exporter rewritten.

Manual startup unchanged (existing private exact source/auth/memory and explicit delivery cutover required):
```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.api --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --port 8000
```
Authenticate privately through /docs. Hypotheses before2020 and dashboard limit/cursor→422; hypotheses status/limit/cursor200; trace before2020→200empty; resource windows and dashboardissue actually filter. No bearer URLs/logs. See B17R-QUERY-COVERAGE.md for exact accepted parameters.
