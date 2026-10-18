# B19 two-minute human inspection

1. Read backend/DEMO.md for private host configuration and actual JSON payload sequence. Keep credentials/session/profile/memory/world files private. Use returned actual IDs, never evaluator answers.
2. ADMIN `cli demo scenarios`:12neutral numbered entries. `cli demo reset --payload reset.json --key review-s07-1` with {"scenario_id":"S07","seed":19,"confirm":true,"variant":"PRIMARY"}:new source/profile-reference,3actual category cases, baseline stage. Retain old profile. Select new private profile/memory and log in to fresh source-bound session files.
3. ANALYST requests inspection using returned case/asset/department. Assigned lead explicitly transitions REQUESTED→SCHEDULED→IN_PROGRESS with each current hash. ADMIN `cli demo advance --id S07 --payload release.json --key release-water-1 --field-session "$FIELD_SESSION" --reviewer-session "$ANALYST_SESSION"`:actual evidence ID; stage staysbaseline until other departments release their own case packets. `cli evidence get --id "$EVIDENCE"` shows actual source/date/target/review, not a diagnosis.
4. A stage jump/no-plan request returns409safe blocker; wrong role403. Exact completed release replay returns same receipt, no duplicate. An uncertain request stays409UNKNOWN and must be reconciled without redispatch/newkey/repair. No approval, work or outcome is created by advancing.
5. Inspect B19-mechanics.json, B19-hidden-isolation.json, B19-uncertain-release.json and B19-READINESS.md. Actual CLI/MCP/Saver/SDK/event execution is distinguished from scripted ReadPause/world content. The matrix identifies unsupported branches and historical/ownership gaps. B10 genuine remainsOPEN/PARTIAL.

Fresh representative real reproduction only (no full suites/lifecycle/provider):
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b19-human-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_demo_runtime.py::test_representative_real_cli_mcp_saver_events_and_hidden_isolation -xq
```
Expected1PASS, new retained isolated source, actual baseline→release proof and preserved checkpoints. This rerun writes new B19 proof; copy existing B19 artifacts first if preserving a review snapshot. If a failure occurs, share sanitized B19logs/RESULTS, never private runtime files. Full24mechanics selection/exact historical outcomes in B19-COMMANDS.md. STOPfor B19review; B20/frontend/live unauthorized.
