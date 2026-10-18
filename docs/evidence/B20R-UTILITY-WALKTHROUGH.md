# B20-R-UTILITY human verification

Use the retained isolated profile identified in primary-proof.json (`profile_reference`: demo-runs/HTTP-B16-a71625af14a0a7b7a6e67d69469d45c2, graph `civicly_b10_test_927efc195d8e4c05b7b3f4a95f7ddb93`). Keep its auth store, memory profile and session files private. No credentials are in this walkthrough. Run from project root; no live calls.

Copy/paste read-only verification with an existing appropriately authorized CLI session:

```sh
export CIVICLY_TEST_NO_LIVE=1
export PYTHONPATH=backend/test_guards:backend
# Set PROFILE, AUTH_STORE, MEMORY_PROFILE and SESSION to the retained private files.
backend/.venv/bin/python -m cli --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --session "$SESSION" --at 2026-10-19T12:00:30.000000Z work get --id WO-B13-13625fddbdeda5e2f9603c5087afbb42
backend/.venv/bin/python -m cli --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --session "$SESSION" --at 2026-10-19T12:00:30.000000Z plan get --id PLAN-B12-1bcc22ee8c062b85552355fd1b2213ad
```

Expected: utility work COMPLETED with latest_assessment_status UTILITY_VERIFIED and resolution_verifiedfalse; plan MONITORING. Use the ROAD lead or ANALYST session to inspect road work `WO-B13-02ebde25ee83616ad4f2fa17f194a4fe`: COMPLETED is not road/case resolution. Read `primary-proof.json` for exact approval, immutable assignments, citations, prerequisite task IDs and source evidence. The approved future guards remain UNMET bytes; persisted reviewed proofs fulfill them at authority checks.

For a fresh focused reproduction (writes only new isolated test graphs; retains evidence), use the exact real pytest command in COMMANDS.md. It creates S04 through accepted B19 setup/release, explicitly records additional attributed observations, acquires ownership with lead submission/distinct analyst review, ingests D022 via real SDK, drafts/approves the exact DAG, verifies rejected premature work and status-only isolation, then executes reviewed isolation→repair→independent utility verification→justified road completion. This is explicit synthetic operator behavior, no model solver/live provider.

The retained uncertainty is intentional: original HTTP/domain request `HTTP-B16-4927bc9e47fc63ab45635562c57bb4aa`, report `EV-REPORT-B09-1d242e11ce7537c62252319d076b8b74`, plan `PLAN-B12-1bcc22ee8c062b85552355fd1b2213ad`, utility order `WO-B13-13625fddbdeda5e2f9603c5087afbb42`. The existing HTTP intent is DISPATCHING and exact replay returns RECOVERY_REQUIRED/UNKNOWN without another service call. Inspect original operation/B09 COMMITTED journal/report and source-bound receipt under the supported operator recovery procedure. Do not replace the key, redispatch, delete a report or clear quarantine/intent. A read-only successful read is evidence for reconciliation, not authorization to repair the intent automatically.

Negative proof retains reviewed normal pressure→CONTRADICTED with zero plan/orders. Both validators are static checks, separate from runtime evidence. B20 other gaps and B10 genuine-provider acceptance remain open; STOP for review.
