# Live demo backend handoff to Antigravity

Backend source and frontend remain separate work areas. Do not reset the demo graph, run the offline development worker on these cases, or alter backend contracts to satisfy a UI assumption.

API: **http://127.0.0.1:8010**, loopback only. Real authentication, graph, hypotheses, citations, persisted trace and SSE. No fixtures presented as live data.

The presenter connection variables are saved privately in `.runtime/demo-presenter/run-01/frontend-connection.env` (0600). Use these three variables in the frontend server's private environment. Never print, track, expose with NEXT_PUBLIC_, or include the password in a browser bundle. The automatic identity is OP-ANALYST. Approvals and department actions require their independently authenticated presenter identities; do not promote the analyst.

Primary cases:

| Category | Investigation | Scenario |
|---|---|---|
| Waterlogging | INV-B09-8b006fb97aa2b908fc69addcf7ecd037 | S01 downstream restriction; genuine Gemini inspection/reassessment and sourced draft |
| Road damage | INV-B09-9d231c8718136a90974e19c6c9a77c47 | S03 road/subgrade versus a nearby healthy pipe; separate new assets |
| Waste accumulation | INV-B09-917765cbf8fef632bd0459640c64f26f | S06 reliable collection versus later dumping; separate new collection point |

The same graph also retains two **blocked earlier investigation attempts** (S04 `INV-B09-b9d4d66e130ed348c4f6a50e9d66a891`, S05 `INV-B09-a2fe3dbdecd03984033026c4d0856295`). Display their recovery/uncertainty honestly if listed; do not replay or hide them. Prefer the primary IDs above for the rehearsal. Live readiness of each primary case is recorded in the backend results; a case ID alone does not prove a completed live path.

## Bind the existing design

- Overview `/api/v1/dashboard/summary`: `active_investigations`, `pending_approvals`, category counts. Do not label completed work as work-in-progress. Derive work-in-progress from scoped work-order statuses with explicit bounds, or show unavailable until implemented. Monitoring likewise comes from actual monitoring records, not a fabricated count.
- Case picker: GET `/investigations?issue=...`, `/incidents?issue=...`; keep stable returned IDs and bounded pagination.
- Report: `/investigations/{id}`, linked `/incidents/{id}`, `/complaints/{id}`.
- Investigation: `/investigations/{id}/trace`, `/hypotheses`, `/graph?depth=4&include_candidates=true`. Use real `decision_paths`; ordinary graph adjacency alone does not establish model influence.
- Evidence: `/evidence/{id}`, source documents `/documents/{id}`. Preserve SYNTHETIC, reviewed, PROPOSED, missing evidence and dated attribution.
- Plans: current_plan_id is visible in trace runtime/checkpoint state; `/investigations/{id}/plans` and `/plans/{id}` expose persisted drafts. No frontend-generated plan or automatic approval.
- Work/outcome: accepted approvals/work/monitoring endpoints; absent work is an honest empty state.
- SSE: authenticated fetch `/events/stream?investigation_id=...`; handle both data and cursor control frames and refetch authoritative state. Separate explicit backend discovery registers persisted activity; stream reads do not execute the agent.

REST requests queue resumptions; a paid model runs only in the explicitly authorized backend presenter host. Never call the offline `advance run` for a live thread. The presenter serializes all source writes/wakes. During a wake, do not submit inspections or plans from another client.

Generate DTOs from the current contracts and compare live OpenAPI before binding. Additive responsibility/service evidence must retain older fields. Do not expose source/profile/password configuration in the browser. Backend handoff does not assert full B20/B-END acceptance or a complete model-evaluation matrix.

## Rehearsal readiness — 2026-10-18 final readback

**Use WATERLOGGING as the primary live investigation demonstration.** It has three persisted graph decision paths, a reviewed synthetic inspection, genuine Gemini reassessment and valid draft `PLAN-B12-da6d426cc7a42982a3dac6c8a76af2a6`. Current pause is HUMAN_REVIEW. Nothing has been approved or executed; resolution is not established.

The newer S03 road case also paused after real reads and a reviewed road inspection: the model supplied an invalid official-node read argument. The newer S06 waste case paused after real pickup history: external evidence lookup failed closed with the wrong location identifier. They are **not ready for a complete live demonstration**. Retain their visible dependency/recovery state. Together with the original S04/S05 attempts, all four paused cases remain intact. The user explicitly declined reconciliation of the blocked original waste case.

Authenticated localhost TCP dashboard/category-list requests and SSE have passed. There are now 59 API operations across 55 paths; regenerate client contracts for the additive GET `/investigations`. Agent execution is presenter-only and currently stopped. API reads and SSE do not spend tokens. See `docs/evidence/FRONTEND-BACKEND-DEMO-RESULTS.md` for the precise boundary.

## Updated three-category presenter selection — DEMO-READ-CONTRACT

Use this later selection; the API and private connection environment remain unchanged. Independent presenter cases are discoverable through **GET `/investigations`**; the B19 scenario catalog alone will not list them. Do not reset or replace the source graph.

| Category | Preferred investigation | Actual current stage |
|---|---|---|
| Waterlogging | INV-B09-8b006fb97aa2b908fc69addcf7ecd037 | Genuine investigation/reviewed inspection/reassessment/draft; HUMAN_REVIEW,3 recorded graph paths |
| Road damage | INV-B09-f663f7a1473c4a28a941d147633e08ad | Genuine4reads/subgrade hypothesis/requested road inspection; MISSING_EVIDENCE. Historical domain rejection retained;0 recorded decision paths—contextual reads only |
| Waste accumulation | INV-B09-95e00a75e74b708c966db68bc595dca0 | Genuine3reads/competing missed-pickup and capacity hypotheses/2 recorded graph paths/requested sanitation inspection; MISSING_EVIDENCE |

All earlier paused cases remain visible and unchanged. Do not mistake their presence for preferred rehearsal selection.9actual TCP detail/trace/graph requests and new wasteSSE passed. A read concurrent with source changes may return409; refetch after the committed event rather than fabricate or cache a success. More field/approval/execution stages have not been run for these new cases. No more paid calls run in the HTTP server. Current host manifest for nonbillable readback: `.runtime/demo-presenter/run-01/host-rehearsal02.json`.

## IMPORTANT latest backend update — DEMO-FIELD-REVIEW

The API is still http://127.0.0.1:8010, same source/auth/private connection. **Regenerate the client for additive PlanDTO.task_bindings before rendering/submitting plans**.59operations/55paths;185schemas. No frontend source was edited by backend work.

`task_bindings` gives authoritative `local_task_id`, native `task_id`, `action_type`, `target_ids`, `department_id`, native `depends_on_task_ids`, current task `status`/`expected_hash`, and enabled `eligible_assignee_ids`. Use these fields for the exact submission assignment scope; do not reproduce backend hashes or infer task IDs from the graph. Re-read version/content_hash before submission and use unique stable idempotency keys. This metadata grants no approval or execution authority.

Current preferred cases remain the last table's IDs. Water and road now both have **PENDING_APPROVAL** plans; the dashboard shows2pendingapprovals. Water uses DRAIN_BLOCKAGE_CLEARANCE; road uses SUBGRADE_REPAIR. Actual OP-ANALYST submitted both with exact scope, but neither is approved/executed. Approval IDs and review hashes: docs/evidence/DEMO-FIELD-REVIEW-HUMAN-REVIEW.md. No role bypass: OP-APPROVER decides; department lead operates only authorized work.

All3requested inspections are now COMPLETED; fetch actual InspectionDTO/evidence. Checkpoint pending_inspections retains historical request IDs—do not label completed work as pending from that cache. The live supervisor now receives checked current-status metadata and must retrieve report contents through MCP. Road has0recordedMCPdecisionpaths (contextual graph/evidence only); water3; waste4. Preserve these distinct labels.

Waste completed a genuine report read after a bounded malformed-output correction, then reached TOKEN_BUDGET. No final draft/new completed assessment exists; show its completed field report plus truthful budget pause. Do not keep retrying, raise a budget or clear a quarantine from the UI. Public reads/SSE remain healthy. No further live worker runs automatically in the HTTP process.

Judge story: backend/DEMO_WALKTHROUGH.md. Full public packet: docs/evidence/DEMO-FIELD-REVIEW-public-readback.json. These are persisted real reads, not fake live execution or verified resolution.

## EXACT-ROAD-LIFECYCLE — selected original road now completed

Use `INV-B09-b9d4d66e130ed348c4f6a50e9d66a891` / incident `INC-B08-27a2cb5d89ae9ab9d86f999cf7b50472` as the primary complete lifecycle. API/source/auth remain unchanged; only API reloaded, frontend untouched. Current investigation and plan COMPLETED, incident ENDED, cluster CONTROLLED. Three work orders, five outcomes, five work/follow-up reports, one recorded own-episode memory row are real persisted synthetic state. `/cases/{incident_id}/memory` now includes the ended selected episode as well as any related historical cases; DTO unchanged. One row does not imply an automatically learned general rule. Bounded/truncated flags remain meaningful.

The completed incident moves to `historical_incident_ids`; selector must retain that mapping. Open `/investigations?investigation=INV-B09-b9d4d66e130ed348c4f6a50e9d66a891`. `/investigations/{id}/plans` and InvestigationDTO.current_plan_id identify the authoritative operational plan. The last agent checkpoint intentionally retains TOKEN_BUDGET and null current_plan_id: the later draft was analyst-assisted. Trace contains genuine LIVE_GEMINI events and four recorded decision paths. Legacy InvestigationDTO.runtime_status is a static development-era label; consult trace execution_mode, not that field, for actual live provenance. Do not conceal the agent budget pause or relabel the assisted plan as model-generated.

Exact plan `PLAN-B12-11e6b8d220e7923a715f5cc0a371b993`, v1, hash `b0a730059b2339f87b24fa8434fe5f3706f9686d524ba47e746ee0c1f1c78c57`. Human explicitly approved water-lead PIPE-100 isolation/repair then road-lead ROAD-100 subgrade repair, with prerequisite verification. The verified UNDERLIES link supplies the road dependency; proximity alone is not used. Immutable review/execution/monitoring/readback/audit proofs: `docs/evidence/EXACT-ROAD-LIFECYCLE-*`. Water and separate clean-road pending plans, original waste quarantine and other paused cases remain unchanged. No new paid wake authorized by frontend reads.
