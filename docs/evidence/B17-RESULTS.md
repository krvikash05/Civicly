# B17 — technically PASS; human review pending

B16/B16-R accepted. B17 only: all8deferred GET/stream operations implemented and exercised,52actualoperations/49paths;3B19demo operations remain deferred. All R01–R18 preserved. No B18/B19/frontend/live provider or full-backend completion. B10 genuine Gemini acceptance remains OPEN/PARTIAL.

## Verification

| Verification | Final result | Evidence |
|---|---|---|
| Focused new boundaries +7accepted API checks |45PASS/0FAIL/0SKIP,3.76s|B17-final-accepted-unit.log|
| One shared actual HTTP/FalkorDB/MCP/Saver +TCP SSE journey |1PASS/0FAIL/0SKIP; final story check includes explicit complaint/incident/cluster HTTP assertions|B17-story-real.log, B17-journey.json|
| Both specification validators, once after final app/contracts |PASS/PASS|B17-spec.log|
| Preservation/secrets/accounting audit |PASS|B17-audit.json/log|

**46distinct passing cases:45unit/1real.** Repeats are not additional cases. Unit policy tests use explicitly mocked inputs where documented; integration has actual graph persistence, actual official/domain MCP discovery/calls, official Saver and subprocess Uvicorn/httpx streaming. Model choices are SCRIPTED/DETERMINISTIC_FAKE_MODEL, not genuine provider evidence.20ordinary pytest/child interlock proofs:0external Gemini/countTokens requests,0unexpected attempts. Original paid ledger2requests exactly unchanged,0open sessions/holds. No broad770/313/APIworkflow rerun, lifecycle or paid smoke.

Earlier failed focused attempts and their corrections retained in B17logs/COMMANDS.md. One failed traceback contained a synthetic test session token; sanitized before final artifact scan, never displayed. No earlier-phase evidence altered. Final unit and application path tests green; metadata-only source_graph evidence field corrected and actual journey rerun. Two prior test files have compatible phase expectations (protected SSE401 vs formerly absent404, streaming content schema/current route count); all old test names and assertion counts preserved. Source boundary B16-R/POST logic unchanged.

## Implemented route/DTO matrix

| GET /api/v1 path | Actual DTO | Runtime proof |
|---|---|---|
| /dashboard/summary | DashboardSummary | Real scoped counts,0active ended incidents,1completed/1independently verified order |
| /investigations/{id}/trace | AgentTracePage |3actual persisted decisions/2real MCP tools; identity/status/latency/hash/source/revision, script label; actual Saver pause |
| /investigations/{id}/hypotheses | HypothesisPage |2competing hypotheses with assessment/evidence history; real exclusive ID pagination |
| /investigations/{id}/graph | GraphSubgraphDTO |33nodes/39edges/9persisted selected paths; exact canonical endpoints/evidence/authority |
| /map/features | MapFeatureCollection | Actual location point and authorized case/asset/incident references |
| /assets/{id} | AssetDTO | Actual D1 subtype/owner/location/condition availability |
| /assets/{id}/neighbors | GraphSubgraphDTO | Typed bounded neighborhood; candidate opt-in preserves CANDIDATE label |
| /events/stream | text/event-stream, closed SSEStream data | Actual localhost replay/later event/late discovery/reconnect/filter/expiry/revocation/refetch |

EvidenceDTO now supplies actual validated finding observations,0.0boolean follow-up measurement, method/time/target/source/independent reviewer/attribution rather than only generic summaries. Citations expose real source version/PROPOSED authority. Public planned DTO names/required identities retained; nullable optional canonical condition explicitly documented. PlanDTO legacy approval_status retains audited lifecycle value COMPLETED, actual ApprovalDTO.status is APPROVED; immutable draft_receipt.approved remainsfalse. Completed work and independently verified outcome are separate facts.

## Actual frontend-readiness journey (same isolated source)

Exact final source graph, checkpoint and full DTO outputs in B17-journey.json. Actual retained identities:

1. Overview `/dashboard/summary`; `/map/features?investigation_id=INV-B09-d8b67c785a6aa6bdcf800dbefe0a4f2f` shows locationL1, incident `INC-B08-3b169d9dcd081279142900a44b96e6ff`, assetD1. Complaint is linked through the incident's complaint_ids and `/complaints/{id}`; case includes cluster/history.
2. `/investigations/INV-B09-d8b67c785a6aa6bdcf800dbefe0a4f2f`, `/hypotheses`, `/trace`, `/graph?depth=4&include_candidates=true` expose actual case/alternatives/decisions/tool latency and9selected path bodies. `/evidence/{id}` IDs from hypotheses/follow-up show typed observations and reviewed source; `/documents/{canonical_document_id}` from plan citation gives real versioned excerpt. Raw journals/provider bodies withheld.
3. `/plans/PLAN-B12-0cceb341285ac43da7c23f9295ca3ba2`, `/approvals` (APPROVER), `/approvals/{id}`, `/work-orders/WO-B13-d6ae9b9b1304ef0d0d0acdd8e1b36a98`, cluster `/outcomes` and `/monitoring` distinguish immutable draft/taskDAG/citations, actual approval, completed work and verified outcome `OUTCOME-B13-9d00c7ddaebe0d065055577a4a9cfbd7`. These accepted service mutations really persisted; B17projections inspected through actual HTTP.
4. Actual network SSE initial replay cursor1..33 includes real decision_recorded/case_tool_called. Saved33→explicit persisted resume34. Inspection committed at source revision108 before resume109, discovered later→registration35 and inspection_requested; no gap from ordering by source time/revision. Filtered other-department stream emits only `{cursor}`, no hidden IDs/data.
5. Reconnect using Last-Event-ID and authoritative GET refetch200. Real persisted session expiry and logout terminate streams with sanitized UNAUTHORIZED. Existing delivery rows and historical checkpoint bytes unchanged,1workorder; explicit later resume remainsPENDING,0attempts. Stream never acknowledges or dispatches it.

All public routes require actual existing Auth sessions, role and department scope. Other department denied map/case/graph/trace/hypotheses/asset/neighbors/evidence, receives0filtered counts; authorization before pages/counts. No source/profile/query selectors. B16-R source-bound intent/UNKNOWN recovery and exact replay unchanged.

## SSE contract and remaining limits

Durable B15registration cursor is SSEid. Header/query cursors must agree; malformed422, conflict/future409, gapsCURSOR_EXPIRED/refetch; no retention deletion exists. Registered rows traversed contiguously, hidden/nonmatching rows advance only transport cursor controls. Explicit20event mapping, no fabricated thinking. Browser fetchAuthorizationBearer header, no URLtoken. Perpoll/peremit auth/scope, .25s/50rowbuffer/30sconnection, commentheartbeat; readonly disconnect, no lease/queue/ack/discovery/agent. Existing separately operated B15 discovery registers new committedfacts; narrow source/thread-validated decisions/traces becomeINFO events through existingcutover. Late discovery is registration-ordered and proved with older source revision.

Read caps500families/5000adjacency/100perroot; graph120nodes/200edges/depth5 and B05proof64queries/5s; stream500retainedrows, activity100cases/500facts/160traces perthread. Capacity errors explicit. Response revision checked; later pages are not snapshots. Conservative departmentredaction may omit globally available connected records; only actualLocationpoints, no geometryartifact/GISinference. Histories/source authority/candidate facts remain qualified. Original858/1246city fullhash and42CANDIDATE drains, B01probe, originalB12R2quarantine/singleplan, immutablemigrations and earlier evidence all retained. Frozen55legacy defects/DEC-004 futuregates unchanged. B10fullgenuine OPEN/PARTIAL. No new package/image/storage/migration.

## Human reproduce

Run exact focused commands in B17-COMMANDS.md; expect45unitPASS +1realPASS and fresh B17-journey.json. To inspect manually, use existing private setup:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.api --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --port 8000
```

Open localhost8000/docs; authenticate privately, follow IDs above (use source profile from final evidence), and stream using Bearer header + Last-Event-ID. Save cursor-control IDs too; reconnect then refetch GETs. Startup never migrates/seeds/activates/starts worker. Existing explicit setup/cutover is required. Do not run/resume retained quarantine or test pending request merely to inspect. If a check fails, share sanitized B17logs/RESULTS/audit—not `.env`, profiles, authstore or bearer values.

Exact inventory/patch: B17-FILES.md/B17-changes.patch against accepted B16/R working snapshot. **STOP for human review. Proposed next: B18 operator CLI over the same accepted services, only with separate authorization.** Frontend/B19/furtherlive unauthorized.
