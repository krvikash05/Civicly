# Actual commands

- PYTHONPATH=backend:scripts backend/.venv/bin/python scripts/complete_demo_lifecycles.py execute --case water —503pre-intent; retained water-command.txt.
- ... execute --case water --retry-unstarted-approval —503pre-intent; water-manual-prewrite-retry-command.txt retained.
- ... execute --case road —PASS; road-command.txt and road-execution.json.
- ... execute --case water --retry-unstarted-approval —PASS after bounded no-effect proof; water-final-prewrite-retry-command.txt and water-execution.json.
- ... verify --case road / --case water —freshprocessPASS.
- Two deliberate execute-on-completed invocations —expected refusal before mutation; preservation-and-duplicate-guards.json.
- PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json discover —142registrations,executionfalse.
- node --experimental-strip-types frontend/scripts/verify-readability.mjs —realHTTPPASS before/afterstandardAPIrestore.
- npm --prefix frontend test —100PASS/0FAIL/0SKIP.
- npm --prefix frontend run build —PASS inclgeneratedAPI/contracts.
- make test-spec —bothvalidatorsPASS.
- python3 -m py_compile scripts/complete_demo_lifecycles.py —PASS.
- git diff --check -- frontend/components/plan-approval-panel.tsx frontend/scripts/verify-readability.mjs —PASS.

Read-only initial audit, source/API-intent/approval readbacks, two no-domain fence diagnostic probes, SQLite ledger audit and actual browser checks are described in RESULTS.md. No fullbackendtests, agentwakes, provider requests, container resets, clouddeployment or GitHubpush. Local API/frontend were reloaded on their existing ports/configuration only.
