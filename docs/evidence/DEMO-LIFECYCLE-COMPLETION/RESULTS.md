# DEMO-LIFECYCLE-COMPLETION — two more retained journeys complete locally

Technically PASS for the two exact human-approved cases; human review pending. Full B10/B20/B-END and all12scenario acceptance remain OPEN/PARTIAL. Supports R10/R11/R13/R15/R16/R17/R18; all18requirements remain binding.

## Persisted results

| Case | Exact plan | Approval | Work | Separate outcome | Memory |
|---|---|---|---|---|---|
| Waterlogging INV-B09-8b006fb97aa2b908fc69addcf7ecd037 | PLAN-B12-da6d426cc7a42982a3dac6c8a76af2a6 v1;1b04b300f41379529bd0e7b6667bf28c1fbaaec5f1bbe38f4cfb5803a3a74286 | APPROVED by OP-APPROVER after explicit human consent | OP-DRAIN-LEAD completed DRAIN_BLOCKAGE_CLEARANCE on DRAIN-101 | Comparable synthetic rainfall + no observed follow-up waterlogging; RESOLUTION_VERIFIED, episode closed |1returned episode |
| Road INV-B09-f663f7a1473c4a28a941d147633e08ad | PLAN-B12-3a26fd93b1eb567bf101905dc4c43b76 v1;a39f811a8913ba4c5870a6acff9a05b918027db1768c64146e32bc4f90a2c834 | APPROVED by OP-APPROVER after explicit human consent | OP-ROAD-LEAD completed SUBGRADE_REPAIR on ROAD-DEMO-SUBGRADE-02 | Synthetic wear exposure + no observed follow-up pavement damage; RESOLUTION_VERIFIED, episode closed |3returned relevant records; not3new episodes |

Original road/utility case INV-B09-b9d4d66e130ed348c4f6a50e9d66a891 remains complete with3workorders. Thus3completed journeys are now accessible locally. Original AI investigations/MCP traces, exact recommendation bytes/hashes, alternative hypotheses, prior checkpoints and recovery cases remain retained. This task did not run another model or MCP investigation. Approvals and field execution were authenticated operator assistance, not autonomous AI approval/work. All field observations and follow-up opportunities are explicitly synthetic; no actual rainfall, road wear or municipal repair is claimed.

Each new case passed through PENDING_APPROVAL→APPROVED→IN_EXECUTION→MONITORING→COMPLETED. Snapshot *-monitoring.json proves task completion left the plan MONITORING before separate follow-up. Independent review uses a separate authenticated OP-ANALYST identity; this is a demo role review, not a claim of independent government/physical verification. Conditional safety, ownership, assessment and procedure checks remain enforced by domain APIs.

## Actual checks

- Two real HTTP/FalkorDB operational journeys:43roadcalls and46watercalls in successful execution receipts (water includes3extra reconciliation read calls),16domainPOSTs each. Authentication login/logout calls are outside these counts.
- Fresh-process verification for each:exact approval, native completed plan/task/order, outcome closure, ended incident, graph and memory PASS.
- Two actual duplicate execute attempts refused at completed-plan read before domain mutation PASS. No duplicate workorder; one order per new plan.
- Seven-case comparison:existing plan content hashes and recovery flags preserved; other investigation statuses unchanged PASS. This is scoped preservation proof, not a new bytehash audit of every prior artifact.
- Real frontend typed-client three-category readback PASS, including after restoring standard API process. Water and originalroad show Review the verified outcome; waste remains Agent paused at its usage limit.
- Actual browser:both newly completed plans show approved/completed copy; water work card shows assigned lead,target,completed task and separate verified outcome. Monitoring/memory shows task-completion outcome separately from closure and retained evidence. Graph visualization includes actual new work/outcome nodes. Screenshots retained.
-100frontendunit tests PASS/0FAIL/0SKIP. Production build/generatedAPI/contracts PASS;bothspecvalidators PASS. Python compile and scoped whitespace checks PASS. No full backend suite/container lifecycle repeated for operator execution using existing accepted services.
-142newly discovered registrations entered the durable activity stream, including older retained undiscovered sources. Discovery did not acknowledge delivery or start a worker/model. These are not142new work actions.
- Provider ledger:0requests since2026-10-19T07:24:30.196Z;no cap changes/new wake. See provider-audit.json.

## Historical failures and reconciliation

Two water approval HTTP attempts returned503 GRAPH_UNAVAILABLE before a transport intent was persisted. Private diagnostics identified a socket-read TimeoutError; source initially remained revision818, approval unchanged. Original dispatch markers and failure outputs remain. A bounded manual same-key dispatch was allowed only after absent API intent, clean pending-source marker, original approval expectedhash unchanged, exact pending plan hash and0planorders were read back. No uncertain journal, recovery record or quarantine was cleared. Final same-key attempt succeeded after local API reload. The exact timeout root cause is not established; current real executions and post-restore reads passed. Temporary private exception diagnostics removed from the running API by restoring the original launcher/config. All logs remain private.

An earlier reload command was not executed because automatic approval review hit its usage limit; this was disclosed. After the user said continue and the limit reset, approved local reloads ran. No bypass was used.

## Changed scope

New scripts/complete_demo_lifecycles.py is a fixed-scope operator script. Durable exclusive dispatch/receipt files live only in ignored private .runtime. It refuses automatic mutation replays and only supports the two explicitly approved plan hashes/scopes. Do not run execute again as verification. Existing domain services, schemas, migrations, caps, city imports and state machines were not changed.

Frontend plan approval copy now explicitly says approved when the validated audited plan has progressed to completed work, keeping outcome evidence separate. The nonbillable readability verifier now expects the genuinely completed water state. Updated backend walkthrough supersedes stale pending counts; old history retained. Six root trackers appended. GitHub and hosted AWS snapshot remain unchanged.

## Human review

1. Open http://127.0.0.1:3100/investigations?investigation=INV-B09-8b006fb97aa2b908fc69addcf7ecd037 . Review Report→Investigation→Evidence→Plan&approval→Work→Monitoring&memory. The old saved agent pause remains historical; current case is completed.
2. Repeat for INV-B09-f663f7a1473c4a28a941d147633e08ad. Note supported subgrade explanation and rejected utility alternative; one repair task.
3. Nonbillable readback: PYTHONPATH=backend:scripts backend/.venv/bin/python scripts/complete_demo_lifecycles.py verify --case water (or road). Each invocation writes a fresh dated sanitized proof, no domain mutations/provider calls.
4. Frontend read verification: node --experimental-strip-types frontend/scripts/verify-readability.mjs . Expect completedwater/originalroad and pausedwaste, all3categories. Failure artifact:commandoutput plus sanitized requestID; never share runtime credentials.

## Remaining and exact next task

DEMO-WASTE-COMPLETION: use the clean waste case's existing reviewed inspection/report and dated MISSED service record to perform authenticated analyst reassessment, preserve original AI token-limit checkpoint, prepare an explicitly operator-assisted sourced pickup-recovery draft, obtain exact human approval, execute through existing controls, then independently monitor. Current waste24hour policy requires a dated post-pickup observation window; do not close immediately, backdate completion, fast-forward real timestamps or weaken the policy. If a shorter synthetic-time demonstration is desired, that needs a separately reviewed simulation-clock design.

Three other recoveryflagged cases remain blocked, including the case the human explicitly asked to leave blocked. No general recovery clearing was authorized. After local human review, separately synchronize approved code/data to the hosted snapshot so public visitors see these new results. No claim that all12scenarios are solved. STOP for human review of this bounded completion task.
