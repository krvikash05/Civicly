# B20-R-SERVICE-EVIDENCE operator verification

Preserve current proof/log files before rerunning tests. Use the exact focused commands in COMMANDS.md; the real test creates fresh isolated graphs and keeps all earlier graphs. No live provider call or real municipal work occurs.

For retained S06PRIMARY, graph `civicly_b10_test_6c0aa62f64c74300807568e892cb5ba7` / private profile reference `demo-runs/HTTP-B16-f1ce93f31326134a1f7c0e1c930a20e0`:
- Canonical pickup `PICKUP-B13-1404d30a33f51ef0c38bc10d406ec711`, collection point `WASTE-100`, route `ROUTE-C03`.
- Service source `SERVICE-SOURCE-B13-1404d30a33f51ef0c38bc10d406ec711`, report `EV-REPORT-B09-c63618f46465c66cbdccfc6798d44489`.
- Specific due `2026-10-18T11:58:00.000000Z`, actual `2026-10-18T11:59:00.000000Z`, service log checked `2026-10-18T11:59:00.000000Z`, recording `2026-10-18T12:00:00.000000Z`. Deposit/report observations are12:00Z and remain inside the actual inspection lifecycle. Source identities differ; no ordering inferred from equal timestamps.

Copy-paste read-only CLI commands with existing authorized private files (do not paste credentials into logs):

```sh
export CIVICLY_TEST_NO_LIVE=1
export PYTHONPATH=backend/test_guards:backend
# Set PROFILE/AUTH_STORE/MEMORY_PROFILE/SESSION to the returned retained private files.
backend/.venv/bin/python -m cli --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --session "$SESSION" --at 2026-10-18T12:00:00.000000Z evidence get --id SERVICE-SOURCE-B13-1404d30a33f51ef0c38bc10d406ec711
backend/.venv/bin/python -m cli --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --session "$SESSION" --at 2026-10-18T12:00:00.000000Z evidence get --id EV-REPORT-B09-c63618f46465c66cbdccfc6798d44489
```

Expected: validated optional service_record with actual earlier time and route/point IDs, independently reviewed source/report, then separate dated inspection findings. API equivalents are authenticated GET `/api/v1/evidence/<id>`. Actual MCP tools/list/tools/call proof for `get_pickup_execution_history` is in the same JSON: expect bounded PARTIAL plus gaps, canonical pickup/source IDs and explicit dates, not fabricated SUCCESS or verified absence. New unit tests also prove equal/reversed/unknown time, missing execution, candidate schedule alone and wrong source/target cannot satisfy the service rule.

S05PRIMARY proof: explicit reviewed MISSED source, no actual_at, one canonical execution; S05NEGATIVE: UNKNOWN and zero executions. S06NEGATIVE: completion only; no dumping evidence. Inspect new_assessments: qualified SUPPORTED/CONTRADICTED/INCONCLUSIVE as in RESULTS.md, no independently VERIFIED cause or resolved case. Check earlier assessment hashes and unchanged candidate hashes in each proof.0plans/0workorders.

Uncertain S06NEGATIVE retains graph `civicly_b10_test_0417d94ac6124353b093cd6b49dbbab7` and original request `HTTP-B16-0ac0c37f8ad56bbc1df75315e7787273`. Actual report/source/execution/event committed; deliberate readback ValueError produced409RECOVERY_REQUIRED/UNKNOWN. Exact original HTTP replay did not invoke service again. Native execution `PICKUP-B13-bd160b90f53c5f96b2d665df891ec555` and source `SERVICE-SOURCE-B13-bd160b90f53c5f96b2d665df891ec555` remain, transport intent/demo reservationDISPATCHING. Use original request/inspection/report/source/operation/event evidence for supported human reconciliation. Do not replace keys, retry, delete/repair records or clear quarantine/intent. A read-only successful read is not automatic reconciliation.

If verification fails, share only new sanitized proof/log/result files; retain failed graph/private config for operator inspection. No hidden controller packet is available through agent/MCP/read endpoints. Capacity/route/dumping interventions and B20/B10 genuine acceptance remain open. STOP for review.
