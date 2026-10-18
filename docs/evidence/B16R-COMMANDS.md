# B16-R focused commands/results

CWD `/Users/vikashkumar/Desktop/Civicly`. Required reads and accepted commit/readback boundaries inspected; DEC-061 before coding. Existing isolated Python3.12.1/FalkorDB6.0.2, no package/image change. Baseline:

```sh
sed 's/b16-baseline/b16r-baseline/' /tmp/b16-snapshot.py > /tmp/b16r-snapshot.py
python3 /tmp/b16r-snapshot.py
```
1320public files snapshotted; ignored credentials/runtime excluded. Patch uses actual accepted working tree, preserves earlier uncommitted work.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16r-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_http_recovery.py -q --tb=short > docs/evidence/B16R-unit.log 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/b16r-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_http_recovery.py -q --tb=short > docs/evidence/B16R-real.log 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/b16r-final-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_http_recovery.py -q --tb=short > docs/evidence/B16R-final-unit.log 2>&1
```
Initial9unitPASS0.17s; real combinedfault1PASS6.19s; expanded16unitPASS0.54s. These units originally used the basename later changed to test_http_boundary.py.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16r-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_http_recovery.py backend/tests/integration/test_http_recovery.py -q --tb=short > docs/evidence/B16R-final.log 2>&1
make test-spec > docs/evidence/B16R-spec.log 2>&1
```
Combined selection1collectionERROR0.32s: same basename in non-package unit/integration directories. No test/DB mutation ran in this attempt. Renamed only **new** unit file to test_http_boundary.py; oldtests/cache/harness untouched. Pre-final both static validatorsPASS, retained as B16R-pre-rename-spec.log. Collection provider snapshot preserved separately before reused log path.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16r-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_http_boundary.py backend/tests/integration/test_http_recovery.py -q --tb=short > docs/evidence/B16R-final-corrected.log 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/b16r-checked-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_http_boundary.py backend/tests/integration/test_http_recovery.py -q --tb=short > docs/evidence/B16R-checked.log 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/b16r-accepted-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_http_boundary.py backend/tests/integration/test_http_recovery.py -q --tb=short > docs/evidence/B16R-accepted.log 2>&1
```
17PASS12.79s,18PASS6.92s with retainedjournal guard, final19PASS5.56s with accepted B12prewrite PlanningBlocked regression. Reran only directly affected focusedcases. No ordinary runtime testfailure/graphrepair/quarantineclearance. Finaldistinct19(18unit/1real),0unresolvedFAIL/0SKIP; repeatcounts not added. Unit store/revision/dispatch mocked and explicitly labeled. Realtest invokes actual ASGI HTTP/Auth/B09/repository/FalkorDB; exceptions alone injected. No model/MCP/server/network workflow claimed or run.

```sh
make test-spec > docs/evidence/B16R-spec.log 2>&1
```
Both final validatorsPASS once after final application/test edits. Earlier pre-final pair retained separately (two `make test-spec` invocations total during task, no failed static run). No API contracts/models changed.

Final preservation/security/patch checks:

```sh
PYTHONPATH=backend/test_guards:backend CIVICLY_TEST_NO_LIVE=1 backend/.venv/bin/python docs/evidence/B16R-audit-script.py > docs/evidence/B16R-audit.log 2>&1
git diff --check
git apply --reverse --check docs/evidence/B16R-changes.patch
```
Seven archived ordinarypytest/childinterlock snapshots, all0externalGemini/countTokens/0unexpected; original paidledger2requests unchanged. No fullAPIworkflow/networkserver/all59units/earlierphase/fullregression/lifecycle/livesmoke. Administrative audit only reads original data and new retainedfaultrecords; no repair or acknowledgment. Exactresults B16R-audit.json.
