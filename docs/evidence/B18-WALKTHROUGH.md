# B18 short operator verification

Use existing private host configuration/session files; do not paste credentials into a shell command. The fresh accepted integration proof retained source `civicly_b10_test_4db45f24505941c88b4095d62ba1f5db`. It contains actual simulated case `INV-B09-ec6c020a3071cf902f9b3f18578c562e`, plan `PLAN-B12-c8e5593870da3a2eda117dfb20eed822`, work `WO-B13-795f203f67c97bb9d60827ed5d4c907a`. Private profile/auth/memory/session files remain in the local test directory, never this package. For another configured source, use its actual returned IDs.

```sh
cli() { PYTHONPATH=backend backend/.venv/bin/python -m cli --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --session "$SESSION" "$@"; }
cli auth login --credentials "$CREDENTIAL_FILE" --key review-login-1
cli auth whoami
cli investigate get --id INV-B09-ec6c020a3071cf902f9b3f18578c562e
cli investigate trace --id INV-B09-ec6c020a3071cf902f9b3f18578c562e
cli plan get --id PLAN-B12-c8e5593870da3a2eda117dfb20eed822
cli work get --id WO-B13-795f203f67c97bb9d60827ed5d4c907a
cat > /tmp/civicly-b18-graph-query.json <<'JSON'
{"depth":4,"include_candidates":true}
JSON
cli graph explain --id INV-B09-ec6c020a3071cf902f9b3f18578c562e --query /tmp/civicly-b18-graph-query.json
cli test
```

Expected: authenticated synthetic identity, paused actual MCP/Saver trace labelled offline deterministic, immutable draft vs current lifecycle, COMPLETED order with independently recorded verified outcome, bounded canonical graph plus qualified actual evidence paths. This is inspection, not a new wake. To drive fresh mutations use backend/OPERATOR_CLI.md exact accepted payload sequence with appropriate operator sessions/CAS/binding/explicit keys; no event/approval/state bypass. Actual executable fresh workflow reproduction:

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b18-human-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_operator_cli_runtime.py -xq
```

One case drives actual successive CLI subprocesses, not an HTTP server/UI; explicitly authored offline inputs/defaultReadPause, real DB/MCP/Saver/GraphRAG. Expected1PASS and fresh B18-cli-journey.json. Do not run full suites/lifecycle/live. If it fails, share sanitized B18logs/RESULTS only. New ADMIN reset is optional: `cli reset --output-dir "$NEW_PRIVATE_DIRECTORY" --key new-starter-1`; it creates a separate4node starter, preserves current source and CANDIDATE authority, and does not solve/seed the scenario. Never reset/retry a quarantined wake or change keys to bypass UNKNOWN.

STOP after B18review; B19/frontend/live unauthorized.
