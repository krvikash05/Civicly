# B16-R — technically passing; human review pending

Corrected only HTTP post-dispatch failure classification. All18requirements and accepted B00–B16 behavior remain binding. No B17, live provider, API network/full workflow rerun, unrelated service refactor or storage subsystem.

## Root cause and correction

`Services.command` treated ValueError (including Pydantic validation) anywhere inside dispatch as proof of uncommitted input rejection. B09execute atomically persists inspection+COMMITTEDjournal, then calls readback; DTO projections also ran inside dispatch after services returned. Both could therefore incorrectly produce422/REJECTED despite actual persistence.

Only `backend/app/services/http/service.py` changes application code. Request-local Boundary explicitly marks PRE_WRITE/CHECKING/DISPATCHED/RETURNED around all accepted mutation calls; pure accepted command validators run before invocation. ValueError after invocation is always recovery-required, even if no write was observed. Returned-service projection/response validation/receipt persistence failures always recovery. A malformed savedDONE receipt now also returns recovery without dispatch; healthyDONE replay and conflicting-key409 unchanged.

Known conflict/authorization/gate exceptions remain actionable only before invocation or with unchanged audited source revision, no pending write and no retained request journal. An existing journal prevents wrongly inferring non-commit from no **new** revision. Accepted B12PlanningBlocked remains a known pre-write gate with evidence; its post-commit PlanRecoveryRequired stays unknown. B09CAS check runs before creating journal, with authoritative domain checks retained under its fence. B08/B09/B12/B13/B14 commit/readback boundaries inspected; all post-service branches now pass through the same explicit boundary without modifying domain services.

Original source-bound HTTPrequest/correlation is unchanged. Available safe domain/entity/investigation/plan identities propagate through existing recovery envelope. Deterministic B09journal hint and validated committed receipt IDs are retained in existing api_request recovery metadata; no journal text/exception/provider/credential export. Metadata write is best effort, skipped for pending source write; failure preserves last durable intent and immediate sanitized correlation, not a false guarantee of new feedback. No automatic retry/rollback/delete/repair/quarantine clearance or fabricated acknowledgment.

## Focused observed evidence

**19distinctPASS:18unit +1real combined fault test;0unresolvedFAIL/0SKIP.** Final both specification validatorsPASS. Seven ordinary pytest/child interlock proofs0external Gemini/countTokens/0unexpected; historical paid ledger unchanged. Unit repository/store/dispatch stubs explicitly labeled, not database evidence. Real test uses actual ASGI HTTP, B13Auth, accepted B09service and FalkorDB; only readback/projection exceptions injected. No model/MCP/network-server claim.

`B16R-real-proof.json` records two separate legitimate requests in one isolated setup:

| Fault | HTTP | Domain evidence | Transport | Exact replay |
|---|---|---|---|---|
| Injected ValueError after real B09commit, inside readback |409 RECOVERY_REQUIRED / UNKNOWN |1inspection + COMMITTEDjournal retained |DISPATCHING, phaseDISPATCHED; neverREJECTED |0additional service invocations/effects |
| Injected ValueError in DTO projection after service returns |409 RECOVERY_REQUIRED / UNKNOWN |1inspection + COMMITTEDjournal retained |DISPATCHING, phaseRETURNED; neverREJECTED |0additional service invocations/effects |

Actual total2inspections/2COMMITTEDjournals independently verified by read-only audit. Error body exposes original stable HTTP-B16correlation/request and inspection/investigation IDs; excludes graph name and injected private sentinel. Per-HTTP envelope request_id remains its normal fresh request correlation, distinct from persisted original HTTP-B16domain request identity.

Final proof reconciliation IDs (see JSON for graph/investigation and full response):

- Readback request `HTTP-B16-8f10a11ad97ce5dc771b7efc4690090a`; journal `EV-JOURNAL-B09-38b280751befdedfa2e30656b3a54b83`; inspection `INS-B09-68f4f9304a2473a75daa775c0698c869`.
- Projection request `HTTP-B16-0f748e612bcbc2d8fce5a55371ead8df`; journal `EV-JOURNAL-B09-98cc825a995983318c2f403f5daba504`; inspection `INS-B09-8ae6a6cee660e0bdfd3973d3e904fa24`.

Units verify proven pre-write422/403/stale409, known gates including B12, no-mutation vs changed audit/journal evidence, healthyDONE replay, conflicting key, invalid savedDONE receipt, uncertain ValueError without observed write, post-mutation typed errors, and recovery-metadata failure retaining last durable state. Combined selector initially hit same new-file basename collision; renamed new unit file only, preserved collection log. No DB/application assertion failure. Final19PASS5.56s; exact intermediate commands/results in B16R-COMMANDS.md, no repeated-case count inflation.

## Preservation and operator steps

B16R-audit.json verifies1320prior public files retained,903prior evidence and106prior testfiles byte-identical. All six trackers append-only. No prior file outside adapter/trackers changed; API schemas/contracts, migrations, business services, worker/agent/MCP, dataset and pins unchanged. Original city full hash and42CANDIDATE drainage links, B01probe and original B12R2quarantine/singleplan retained. Scan covers actual known private values and key/session patterns, including generated patch.

Intentionally retained B16Rrecords remain DISPATCHING/operator-required. Stop any implicated worker, inspect original request plus journal/receipt/entity/investigation under existing trusted recovery procedure, verify integrity and determine acknowledgment without rerunning the mutation. This task does **not** reconcile/markDONE, create a replacement request or clear any quarantine. A pending/failed metadata write may leave only the last durable intent; use the immediate safe correlation and existing journal. Historical incorrectly rejected records are not migrated or repaired by this task; reconcile those original records manually rather than assuming old feedback was true. Concurrent source changes conservatively require recovery even if no commit can be established.

## Brief human reproduction

From repository root, with existing local FalkorDB and locked environment:

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16r-human-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_http_boundary.py backend/tests/integration/test_http_recovery.py -q --tb=short
```

Expect19PASS, actual2COMMITTED inspection/journal pairs with409UNKNOWN,0exact-replay redispatch and no provider requests. This creates a new isolated fixture; do not repair old failed graphs. If failing, share sanitized B16Rtest log/interlock proof, never .env/.runtime/private session/profile. Exact paths/patch: B16R-FILES.md/B16R-changes.patch. Both final specification validatorsPASS once after final source/test changes; earlier pre-final pair retained separately.

**STOP after B16-R for human review. Proposed next task remains B17 only after separate authorization; no live calls authorized. B10full genuine Gemini acceptance stays OPEN/PARTIAL.**
