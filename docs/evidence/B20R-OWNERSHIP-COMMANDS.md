# B20-R-OWNERSHIP exact commands and distinct results

Project root `/Users/vikashkumar/Desktop/Civicly`; existing Python3.12 virtual environment/locks unchanged. Every ordinary pytest invocation and Python child installs the existing no-live interlock. No full historical/lifecycle suite or external provider execution.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b20ro-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_responsibility.py backend/tests/unit/test_graph_access_models.py backend/tests/unit/test_http_boundary.py backend/tests/unit/test_operator_cli.py::test_command_exact_accepted_api_mapping -q
```
92PASS/1FAIL1.10s. New canonical-time identity test initially used an offset timestamp; accepted graph timestamp boundary requires UTC Z. Corrected test to whole/fractional Z aliases; production rule preserved.
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b20ro-unit-retry-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_responsibility.py::test_valid_authority_and_stable_scoped_source_identity -q
```
1PASS0.31s, overlaps original unit selection.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b20ro-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_responsibility_runtime.py -xq
```
1setupERROR6.96s, localRedis socket timeout before workflow execution. Failed fixture retained, no repair or old request retry. Read-only health and fresh-fixture retry:
```sh
PYTHONPATH=backend backend/.venv/bin/python -m cli health --env-file .env
CIVICLY_TEST_REQUEST_LOG=/tmp/b20ro-real2-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_responsibility_runtime.py -xq
```
HealthPASS;1realPASS38.65s. Real API/CLI/FalkorDB/SDK/MCP/LangGraph/Saver with scripted choices; no fake tool success. Prior passing proof retained separately.

After explicitly restricting staged review sources to MAINTAINED_BY, strengthening different-department overlap/source-conflict assertions and immutable assertion bytes:
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b20ro-real-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_responsibility_runtime.py -xq
```
1realPASS36.22s, same distinct case; original proof preserved as real-proof-final-before-readiness.json. Explicit existing0005 readiness gate then added to direct domain service (API bootstrap already checked it):
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b20ro-ready-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_responsibility_runtime.py -xq
```
Final1realPASS35.52s, same single journey;3existingSDK/PDF deprecation warnings. Actual candidate→submitted→reviewed→supported sourced draft, future/historical selection, stale exact approval denial, conflicting department, source identity/CAS conflict, authenticated CLI and real committed-readback UNKNOWN/no redispatch all exercised.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b20ro-unit-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_responsibility.py -q
CIVICLY_TEST_REQUEST_LOG=/tmp/b20ro-ready-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_responsibility.py::test_required_existing_operations_migration_not_bypassed -q
```
23PASS0.16s plus newly added readiness1PASS0.15s =24distinct focused responsibility units.71other selected graph-model/HTTP-boundary/CLI-mapping units passed in initial selection; includes three new CLI mappings. Total95distinctunitPASS. No old assertion/test removed. Final total96distinctPASS=95unit+1real,0unresolvedFAIL/0SKIP. Retain1historicalunitFAIL and1setupERROR, not counted as passing proof. Repeated real cases/overlapping units count once.

```sh
CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/b20ro-spec-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec
CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/b20ro-final-spec-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec
```
Both validatorsPASS in both invocations; final after last production/test edits. Static checks are not extra pytest cases. Generated OpenAPI/JSON contracts58operations/55paths, existing18MCPtools and9state machines unchanged. Ten pytest/child/spec zero-live reports,0external/0unexpected.

Pre-edit public snapshot command: Python/git ls-files SHA256/copy to `/tmp/b20r-ownership-baseline` (1581publicfiles); task diff generated with Python difflib relative to this snapshot, excluding previously accepted uncommitted Git work. No Git commit or push.

Final read-only audit:
```sh
PYTHONPATH=backend backend/.venv/bin/python docs/evidence/B20R-OWNERSHIP-audit-script.py
```
Audit checks prior public bytes/history, migrations/data/tests/evidence/accounting, retained city/B01probe/B12R2+B19 quarantines and actual new responsibility/recovery bindings. No graph/volume deletion, checkpoint rewrite or quarantine clearance. One initial registry-inspection utility used the wrong dictionary key and raised KeyError; corrected by reading actual node_types/relationship_types, no mutation or acceptance result attributed.

## Final directly related read compatibility verification (supersedes96subtotal)
Retained candidate+VERIFIED links exposed legacy read assumptions. Corrected only Reads/Views owner selection and lead scopes; added five focused selection units and a real lead asset GET to the existing journey. Candidate-only fallback remains read context; owner_department_id requires verified responsibility.
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b20ro-view-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_responsibility_runtime.py -xq
```
1setupERROR5.74s (constraint-list socket timeout), before the new projection path. Failed source retained; read-only healthPASS. Existing bounded socket configuration overridden only for the fresh test invocation and inherited children (default3seconds→10seconds); no file, broker10second or query1second budget changed:
```sh
FALKORDB_SOCKET_TIMEOUT_SECONDS=10 PYTHONPATH=backend backend/.venv/bin/python -m cli health --env-file .env
FALKORDB_SOCKET_TIMEOUT_SECONDS=10 CIVICLY_TEST_REQUEST_LOG=/tmp/b20ro-view-retry-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_responsibility_runtime.py -xq
CIVICLY_TEST_REQUEST_LOG=/tmp/b20ro-view-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_responsibility.py -q
CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/b20ro-view-spec-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec
```
Final real1PASS35.63s;29focusedunitPASS0.47s; final2SPECvalidatorsPASS. Final101distinctPASS=29focusedresponsibilityunits+71graph/HTTP/CLI-mappingunits+1sharedrealjourney.0unresolvedFAIL/0SKIP. Four passing real invocations are overlap, count once.1historicalunitFAIL+2setupERROR retained. Fourteen pytest/child/spec guard reports0external/0unexpected. No broad/lifecycle/live suite. Normal pytest query/transport budgets remain finite; readiness migration prerequisite and new source/tier semantics actually exercised.

## Read-only audit bookkeeping and preservation
First audit stopped because its whitelist omitted the authorized backend/cli/main.py change; retained audit-attempt1.txt. Second stopped on7concurrentnewfrontend paths not created/edited/executed by this task; retained audit-attempt2.txt. Corrected only audit bookkeeping, preserved/hash-listed external additions, excluded their source from ownership patch/inventory. No frontend tests/work performed. Final read-only auditPASS1581previouspublicfiles/1129byte-identicalevidence/119unchangedacceptedtests; original migrations/city/probe/quarantines/checkpoints/paidledger unchanged,14providerproofs0external/0unexpected; public patch/private-value scanPASS. Audit failures are metadata checks, not pytest passes/failures or application mutation.
```sh
FALKORDB_SOCKET_TIMEOUT_SECONDS=10 PYTHONPATH=backend backend/.venv/bin/python docs/evidence/B20R-OWNERSHIP-audit-script.py
```
Actual pinned runtime versions in audit: FalkorDBmodule60002(6.0.2), Redis8.10.2, falkordb1.8.0, mcp2.3.0, langgraph1.2.16, langchain-falkordb0.2.0, FastAPI0.143.3, Pydantic2.14.1. No dependency installation/change. Final patch scope verified relative to pre-task snapshot, nofrontenddiff.
