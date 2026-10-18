# B10-O exact commands and evidence classes

Cwd `/Users/vikashkumar/Desktop/Civicly`. No live Gemini call, ZIP, push, B11 implementation or retained-volume deletion authorized/performed. Commands below are nonbillable; only the runtime guide contains future paid CLI examples, explicitly NOT RUN.

## Frozen working-tree baseline

`/tmp/b10o-baseline.py` captured Git base2d30550483197e23ce9e2802403b161d6f04b145 and SHA256 of638 current source/evidence candidates in B10O-baseline.json, with private recovery copies at `.runtime/b10o-baseline/`. This is the actual uncommitted B10 baseline, not an assumption that HEAD contains B10. The user-supplied provider hotfix was read and hashed; only bounded transient recovery was adopted with additional quota distinction and cost reservation. It was not blindly applied.

## Focused controls and actual runtime

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_agent_provider.py backend/tests/unit/test_agent_models.py -q > /tmp/civicly-b10o-units-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/unit/test_ai_spending.py backend/tests/unit/test_ai_execution_policy.py backend/tests/unit/test_ai_provider_recovery.py -v -s > /tmp/civicly-b10o-controls-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/unit/test_ai_spending.py backend/tests/unit/test_ai_execution_policy.py backend/tests/unit/test_ai_provider_recovery.py backend/tests/unit/test_agent_provider.py backend/tests/unit/test_agent_models.py -q > /tmp/civicly-b10o-controls-second.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/unit/test_agent_context.py -q > /tmp/civicly-b10o-context-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_agent_optimization.py backend/tests/integration/test_agent_runtime.py backend/tests/integration/test_agent_reasoning.py -v -s > /tmp/civicly-b10o-integration-first.txt 2>&1
```

Observed first runs:23 unit PASS;18 initial controls PASS; final expanded controls/provider/models43 PASS; context3 PASS; actual MCP/graph/Saver12 PASS. These overlap; do not add them to regression totals. Three further real B09 classification projection cases were added to the same new integration file before the complete regression collected. MockHTTP and deterministic/reactive models are labeled and do not count as live reasoning or billed-cost evidence.

## Entire suite, specification and lifecycle

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10o_spending.py create --anchor docs/evidence/B10O-spending-before.json --output docs/evidence/B10O-spending-before.json
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10o-full-provider-requests.jsonl backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > /tmp/civicly-b10o-full-tests.txt 2>&1
make test-spec > /tmp/civicly-b10o-spec-first.txt 2>&1
```

The probe refuses to overwrite its private SQLite file. On subsequent reproductions use `verify`, not `create`. The full suite uses actual Docker restart and force-recreation on existing volumes; its retained B01 probe and Browser file/HTTP tests run unchanged. Per-test B10 graphs are disposable owned UUIDs; original retained B10/B04/B01 graphs remain intact. Default pytest without `--run-persistence` intentionally skips that one lifecycle test, not any model gate.

## Post-lifecycle independent witnesses

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10.py --reprovision --compare docs/evidence/B10-before-lifecycle.json --output docs/evidence/B10O-post-retained.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10o_spending.py verify --anchor docs/evidence/B10O-spending-before.json --output docs/evidence/B10O-spending-after.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09.py --output docs/evidence/B10O-post-B01-B09.json --b08-anchor docs/evidence/B09-B08-after-final-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python -m tests.b09_evidence verify --proof docs/evidence/B09-retained-proof.json --lifecycle-log /tmp/civicly-b10o-full-tests.txt --output docs/evidence/B10O-post-B09-retained.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09r.py --output docs/evidence/B10O-post-B09R-history.json
make test-spec > /tmp/civicly-b10o-spec-final.txt 2>&1
backend/.venv/bin/python scripts/audit_b10o.py
git diff --check
```

Run `verify_b09r.py` before restoring its rolling proof. Preserve four freshly generated B07R/B08/B09/B09R rolling files as B10O-regression-* then restore exact frozen B10 copies; historical artifacts must not be overwritten. B10 verify independently checks exact immutable B09R history even after restoration. Save full test output, suite-wide provider interception audit and context/authority/cache/cap proofs under B10O-*; generated sensitive files are never evidence candidates. The audit creates an incremental unified source patch from private frozen B10 copies, checks all other baseline files/evidence byte-for-byte, scans candidate contents against actual private values without printing them, and checks no owned MCP processes remain. Older audit_b10.py remains historical and unchanged; it cannot represent B10-O's intentionally new controls.

Full observed totals/status and reproducible human review are in B10O-RESULTS.md. Real live acceptance remains OPEN and all live B10-O tests NOT RUN.

## Final-source follow-up

The first full suite collected687 tests before the final generic history-record interning and four recovery assertions were added. Final source is verified in a second complete suite, not only a focused substitute:

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10o-context-final-provider-requests.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_agent_context.py -q > /tmp/civicly-b10o-context-final.txt 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10o-recovery-final-provider-requests.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_ai_provider_recovery.py -q > /tmp/civicly-b10o-recovery-final.txt 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10o-recovery-final2-provider-requests.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_ai_provider_recovery.py -q > /tmp/civicly-b10o-recovery-final2.txt 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10o-final-provider-requests.jsonl backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > /tmp/civicly-b10o-final-tests.txt 2>&1
UV_CACHE_DIR=/tmp/civicly-b10o-uv-cache backend/.venv/bin/uv lock --project backend --check --offline > /tmp/civicly-b10o-lock-check.txt 2>&1
```

The final full invocation is queued sequentially after the first pytest process exits, preserving its original log/audit separately. Focused final context3 PASS and recovery12 PASS. Actual final counts and any failure are recorded after execution. No live authorization is requested or inferred.

## Observed authorization preflight failure and corrected rerun

First complete run:687 PASS in940.94s, zero external Gemini requests,2 intentional blocked probes. After its actual Docker force-recreation, the automatically queued final-source run omitted the existing trusted ACL configure preflight. The shared B07 MCP trace-writer account was unavailable (AuthenticationError), so24 B10 integrations failed before any model request;1 Browser test passed. The run was interrupted after72.93s; remaining cases were NOT RUN in that attempt. This is not silently counted as a passing suite. No data/schema/volume repair or weaker permission was used.

```sh
kill -INT 95782
cp /tmp/civicly-b10o-final-tests.txt /tmp/civicly-b10o-auth-failed-tests.txt
cp /tmp/civicly-b10o-final-provider-requests.json /tmp/civicly-b10o-auth-failed-provider-proof.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10.py --reprovision --compare docs/evidence/B10-before-lifecycle.json --output docs/evidence/B10O-after-first-retained.json
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10o-final-provider-requests.jsonl backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > /tmp/civicly-b10o-final-tests.txt 2>&1
```

The interrupted PID above is historical evidence, not a command to repeat against a new process. `--reprovision` invokes existing trusted MCP configure plus exact-key retained-profile provisioning, then confirms all6 checkpoints/source fingerprint match before lifecycle. The normal portable preflight before a new suite is `PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure --output /tmp/civicly-mcp-preflight.json`. Run retained-profile verification separately when those private retained credentials exist. Runtime guide now states this prerequisite before pytest, and post-lifecycle verification restores it again. Actual failed logs/counters are retained, sanitized if necessary; zero Gemini requests occurred in the interrupted run too.

## Actual real-context benchmark and final retained witnesses

After final full691 PASS/0 FAIL/0 SKIP, the queued sequential checks executed:

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10.py --reprovision --compare docs/evidence/B10-before-lifecycle.json --output docs/evidence/B10O-pre-benchmark-retained.json
CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/civicly-b10o-benchmark-provider-requests.jsonl PYTHONPATH=backend/test_guards:backend backend/.venv/bin/python scripts/measure_b10o_context.py > /tmp/civicly-b10o-real-context-benchmark.txt 2>&1
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10.py --compare docs/evidence/B10-before-lifecycle.json --output docs/evidence/B10O-post-retained.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10o_spending.py verify --anchor docs/evidence/B10O-spending-before.json --output docs/evidence/B10O-spending-after.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09.py --output docs/evidence/B10O-post-B01-B09.json --b08-anchor docs/evidence/B09-B08-after-final-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python -m tests.b09_evidence verify --proof docs/evidence/B09-retained-proof.json --lifecycle-log /tmp/civicly-b10o-final-tests.txt --output docs/evidence/B10O-post-B09-retained.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09r.py --output docs/evidence/B10O-post-B09R-history.json
```

All PASS; benchmark3 actual source cases, no model calls; all6 retained SDK threads exact; financial logical state exact;101 prior traces/immutable history preserved. Final proof/log copies are B10O-* in this directory. New retained source fingerprint matches before and after the benchmark, which deletes only its owned disposable graphs/accounts. Four rolling proof files were then copied to B10O-regression-* and restored byte-for-byte from the frozen pre-task copies. Source audit/patch generation and reverse patch check run last. No failed attempt is reclassified as PASS.
