> **Hosted synchronization — 19 Oct 2026:** the latest local completion and frontend improvements are now verified on https://civicly-13-55-205-208.sslip.io. Three completed journeys, five completed work orders and no pending approvals. This supersedes the earlier “hosted snapshot not synchronized” note below. Waste and recovery cases retain their existing limitations. [AWS update proof](../docs/evidence/AWS-UPDATE-20261019/RESULTS.md).

> **Latest local completion — 19 Oct 2026.** Waterlogging `INV-B09-8b006fb97aa2b908fc69addcf7ecd037` and second road case `INV-B09-f663f7a1473c4a28a941d147633e08ad` now also have exact human approval, one completed work order each, separately reviewed synthetic follow-up, verified closure and case memory. This supersedes the older pending-approval counts below. The original road/utility journey remains complete. Waste `INV-B09-95e00a75e74b708c966db68bc595dca0` retains its token-budget pause and needs reviewed operator-assisted reassessment/planning; no live retry or cap increase. See [completion results](../docs/evidence/DEMO-LIFECYCLE-COMPLETION/RESULTS.md). These new results are local; the hosted snapshot has not been synchronized.

> **Current completed road demonstration — EXACT-ROAD-LIFECYCLE (18 Oct 2026).** The human-selected original incident `INC-B08-27a2cb5d89ae9ab9d86f999cf7b50472` now has a complete explicitly synthetic lifecycle. Original investigation `INV-B09-b9d4d66e130ed348c4f6a50e9d66a891`: real Gemini/MCP reads and supported assessments; analyst-assisted cited draft; exact human approval; three completed work orders; independent utility verification; monitoring; verified road outcome and retained case memory. This supersedes earlier road readiness descriptions below. Gemini stopped at its retained token limit before drafting; the planning/execution stages were authenticated operator assistance. Full B10/B20/B-END acceptance remains open. See [results](../docs/evidence/EXACT-ROAD-LIFECYCLE-RESULTS.md).

# Judge rehearsal — actual current backend

All municipal records/field work here are explicitly synthetic. Gemini tool selection, MCP execution, FalkorDB persistence, GraphRAG citations and Saver checkpoints are real. No broad B-END completion claim.

## Current session

API: http://127.0.0.1:8010. Presenter profile/auth/source unchanged. Antigravity owns frontend, currently previewed independently. Read backend/FRONTEND_HANDOFF.md for private server-only connection details and the latest contract addition. Do not reset this graph or run an offline scripted worker on its live threads.

## A five-minute demonstration

1. Overview: three issue categories, actual incident counts, **2 pending approvals**, no fabricated resolved count. Retained blocked cases are historical attempts, not preferred demo selections.
2. Waterlogging `INV-B09-8b006fb97aa2b908fc69addcf7ecd037`: start at complaint and affected drains. Show the actual selected MCP drainage traversal and its recorded decision path. Its three recorded paths can highlight exact graph edges. Explain that connection proves investigation scope, not physical blockage.
3. Open the competing assessments and reviewed inspection. Show obstruction/flow/safety observations, synthetic method, dates, field operator and independent reviewer. Show the same-thread fresh evidence and reassessment; retain earlier inconclusive/rejected history.
4. Open plan `PLAN-B12-da6d426cc7a42982a3dac6c8a76af2a6`: sourced DRAIN_BLOCKAGE_CLEARANCE, accountable drain department, exact task binding, safety conditions and rainfall-based monitoring. It is PENDING_APPROVAL. No work has been executed and no comparable follow-up proves resolution.
5. Road `INV-B09-f663f7a1473c4a28a941d147633e08ad`: show contextual road/maintenance/dependency reads, the retained rejected proposition, reviewed subgrade report, supported reassessment and SUBGRADE_REPAIR proposal `PLAN-B12-3a26fd93b1eb567bf101905dc4c43b76`. It also awaits approval. This case has **zero recorded MCP decision paths**; ordinary evidence relationships remain visible, but must not be presented as model-selected edge paths.
6. Waste `INV-B09-95e00a75e74b708c966db68bc595dca0`: show related-incident/pickup/maintenance paths (4 recorded paths), competing missed-pickup/capacity hypotheses, completed sanitation report and independently reviewed dated missed-service record. Explain the final TOKEN_BUDGET stop honestly. New findings are available, but no completed AI reassessment/draft or resolved claim exists. A malformed model READ was corrected before MCP dispatch; that correction was paid/accounted and did not redispatch an uncertain operation.
7. Return to review: 2 exact pending approvals. The human uses OP-APPROVER and checks immutable scope in docs/evidence/DEMO-FIELD-REVIEW-HUMAN-REVIEW.md. The assistant has not approved or executed either plan. After a human decision, existing backend operations support authorized order creation, department progress, independent observations and outcome monitoring; those stages have not been materialized for these presenter plans.

## UI source of truth

Use `/investigations` for presenter cases, not only B19 scenario catalog. Read `/investigations/{id}/trace`, `/hypotheses`, `/graph?depth=4&include_candidates=true`, `/inspections/{id}`, `/evidence/{id}`, `/plans/{id}` and pending `/approvals` in an authorized role. Subscribe to actual authenticated SSE, refetch on events/cursor recovery, and show a bounded-read/source-change error honestly if returned.

PlanDTO.task_bindings is the server-provided local-to-native mapping, scope, current task status/hash and enabled eligible synthetic assignees. It avoids guessing IDs; it is not approval authority. Regenerate the frontend client using its existing contract generator. The API still has59operations/55paths; models now185.

## Nonbillable check

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json status
```

Expected: all report lifecycles COMPLETED; water/road plans PENDING_APPROVAL; waste TOKEN_BUDGET; current plan task bindings; true hypotheses/typed evidence/paths. Whole-host preflight correctly refuses another live run because the waste case reached its budget. Do not increase budgets, clear quarantines, manufacture follow-up observations or claim work completed as resolution.
