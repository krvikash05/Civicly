# Commands and evidence

Executed from /Users/vikashkumar/Desktop/Civicly. Localhost/Redis commands used the approved local runtime. Private credentials were never emitted.

- `PYTHONPATH=backend backend/.venv/bin/python scripts/audit_case_completion.py --output docs/evidence/DEMO-WASTE-COMPLETION/recovery-audit-before.json` — seven cases, three quarantines, READY revision1056. Later `full-recovery-readback.json` validates all retained decisions/committed domain receipts plus read-only SQLite accounting.
- `PYTHONPATH=backend:scripts backend/.venv/bin/python scripts/prepare_waste_completion.py prepare` — initial HTTP503 retained in prepare-output.txt. Exact intent/journal/hash proof: failed-request-readback.json.
- After proof and local API reload: `PYTHONPATH=backend:scripts backend/.venv/bin/python scripts/prepare_waste_completion.py prepare --retry-proven-unstarted` — PASS, exact original request/payload retained; see manual-prewrite-reconciliation.json, manual-prewrite-attempt-output.txt, review.json. Do not rerun: immutable markers deliberately stop duplicate dispatch.
- After exact human approval: `PYTHONPATH=backend:scripts backend/.venv/bin/python scripts/prepare_waste_completion.py execute --approve-plan-hash ffa5dfa47fce1cfc43d348c2076cb88485decbe09e887cf01442516f8b762140` — PASS; execution-output.txt/execution.json. This is historical documentation, not a safe rerun command; immutable markers and plan state reject replay.
- `PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json discover` — durable event discovery only, no acknowledgment or worker/provider wake; event-discovery.json.
- `PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/unit/test_waste_post_pickup.py backend/tests/unit/test_planning_remediation.py backend/tests/unit/test_http_boundary.py -q` — 40 PASS, two dependency deprecation warnings; focused-tests.txt.
- `make test-spec` — both validators PASS; spec-tests.txt.
- Read-only fresh authenticated HTTP process plus audit comparison — fresh-http-readback.json, fresh-verification-output.txt, final-recovery-audit.json. Proves persisted completed work/MONITORING state, graph linkage, all seven checkpoint bindings and three quarantines preserved, accounting unchanged. No new agent execution.
- AST/whitespace and wrong approval-hash zero-HTTP guard — PASS, script-checks.txt.
- Actual browser Work and Monitoring inspected; completed-work-browser.png and monitoring-browser.png. The first work-browser.png captured the directory after scrolling and is retained; completed-work-browser.png is the verified work-order framing.

For safe reproducible verification, run the focused pytest/spec commands and the audit script with a NEW output filename, then open the local case. Never rerun a mutation helper to inspect state.
