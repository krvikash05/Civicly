# B17-R — technically PASS, human review pending

Narrow correction only: truthful per-route query parameters. All18requirements preserved; no B18/frontend/live provider or domain/storage/migration/worker/authentication/SSE/recovery redesign.

## Root cause and correction

The shared public ReadFilters exposed every possible query field. application.py's grouping accepted after/before for hypotheses, but Views.hypotheses only consumed status/limit/cursor; dashboard accepted unused pagination. The same broad model advertised irrelevant parameters even where a later guard rejected them.

Explicit VIEW_QUERY_FIELDS now drives closed route-specific query models and the HTTP allowlist. Existing ReadFilters field definitions, strict scalar/boolean/bounds/date-window validators and service defaults are retained; unchanged Views receives the validated subset. OpenAPI and normative per-GET query_parameters/query_schema_id use exactly those models. scripts/validate_api checks equality among contract, model fields and generated OpenAPI. Unknown, unsupported or repeated fields return existing sanitized422 VALIDATION_ERROR without invoking the projection.

| Route | Accepted query parameters |
|---|---|
| Hypotheses | status, limit, cursor |
| Dashboard | issue, status, department_id, after, before |
| Trace | status, after, before, limit, cursor |
| Map | resource filters/pagination plus investigation_id |
| Six resource lists | issue, status, department_id, after, before, limit, cursor |
| Graph / neighbors | depth, include_candidates |
| Asset detail | none |
| SSE | existing cursor, investigation_id; Last-Event-ID remains header |

Hypothesis dates are rejected: no normative creation-versus-assessment timestamp semantics exist; none invented. Dashboard filters each authorized metric's resource using existing issue/status/department/inclusive resource timestamp semantics; aggregate output has no pagination. Trace retains inclusive actual decision/tool timestamps before chronological timestamp+ID pagination. Existing resource/map/filter/graph/SSE behavior remains unchanged. Other route families were inspected; no other accepted-but-unconsumed B17parameter found. Legacy paginated scalar repeated keys also fail422 consistently.

## Exact verification and failures

**60distinct final passing cases:59unit +1real,0unresolvedFAIL/0SKIP.**

- Initial focused unit invocation:58PASS/1FAIL8.20s. A mocked approvals-list case used ANALYST; existing RBAC correctly returned403 before the query-boundary409sentinel. Corrected fixture to APPROVER; only13directlyaffected supported-query cases rerun13PASS1.93s. Twelve overlap, one corrected case:59distinct units, not71. This was a fixture failure, not hidden application success.
- Existing real journey extended, run **once** after final application/test edits:1PASS28.03s,3existing dependency deprecation warnings. Real FalkorDB/services, actual official/domain MCPclient discovery/call, official Saver, HTTP projections and actual localhost Uvicorn/httpx SSE. Model selections explicitly SCRIPTED/DETERMINISTIC_FAKE_MODEL, not genuine provider evidence. Alloldassertions retained.
- Both specification validators:PASS/PASS, one final guarded make test-spec invocation. Static schema validation does not replace real integration.
- Three ordinary pytest/child interlock proofs:0external Gemini/countTokens requests,0unexpected attempts. Original paid ledger2requests unchanged;0open sessions/holds.
- Preservation/private-value audit:PASS;983earlier evidence files byte-identical, all earlier test names/assertion counts retained, other test files unchanged, six trackers append-only. Retained city fullhash/858nodes1246edges/42CANDIDATEdrains, B01probe, immutablemigrations and originalB12R2quarantine/singleplan preserved. Existing POST/recovery code unchanged.

Exact commands/logs: B17R-COMMANDS.md, B17R-unit-initial.log, B17R-unit-corrected.log, B17R-real.log, B17R-spec.log, B17R-*-zero-live.json and B17R-audit.json. Only new B17Rartifacts; no previousB17proof overwritten.

## Actual corrected HTTP proof

Retained fresh source `civicly_b10_test_995367c6e4684981b3928a8a8df08e24`, investigation `INV-B09-d8b67c785a6aa6bdcf800dbefe0a4f2f`; source/case IDs, full query proof and unchanged graph/SSE journey in B17R-journey.json.

- `/investigations/{id}/hypotheses?before=2020-01-01T00:00:00Z` →422 VALIDATION_ERROR, also after/repeated limit422. Base response still has the two2026hypotheses; supported status yields1matching record, nonexistent status0. Existing exclusive cursor pages return different IDs.
- `/dashboard/summary?limit=1` and `?cursor=PRIVATE-INPUT` →422; repeated issue422. Actual completed order count1→0 with ROAD_DAMAGE issue filter; before2020 also0. No untrusted query value in response.
- `/investigations/{id}/trace?before=2020-01-01T00:00:00Z` →200,total0; after2020 retains all actual traces. StatusSUCCESS still2actualtoolrecords and chronological cursor stays correct.
- Assetlimit, neighborscursor, graphlimit, traceissue and mapdepth422. Existing resourceissue/department/date/count/page tests and department scope remain passing.
- Original9selected paths/typed observations/citations/current planapprovalworkoutcome distinctions, TCPstream initial replay33/later34/late discovery35, scope filter, real sessionexpiry/revocation/disconnect and authoritative refetch all pass. One workorder, existing checkpoint bytes/registered delivery rows unchanged; explicit later resume remainsPENDING0attempts, never acknowledged by stream.

## Human verification and remaining limits

Use unchanged startup command in B17R-COMMANDS.md with the existing private profile/auth/memory configuration; no startup migration/seed/activation. Authenticate privately via /docs. Confirm hypotheses advertises **only status/limit/cursor**, dashboard **only metric filters**. Try the reproduced before2020 request and dashboardlimit: expect422; try hypothesesstatus and tracebefore2020: expect actualfiltered200results. Never put bearer values in URLs/logs. To reproduce from fresh fixtures, run the exact focused unit command and one integration selector with CIVICLY_FRONTEND_EVIDENCE_PREFIX=B17R; share only sanitized B17Rlogs if a check fails.

No hypothesis date filtering until normative timestamp meaning is separately agreed. Existing B17finite bounds/current-page-not-snapshot behavior/conservative department redaction/point-only map/cutover/stream limits remain. Genuine B10acceptanceOPEN/PARTIAL, original quarantines require existing operator reconciliation, candidate drainage/history/source authority/frozen55legacy defects and DEC-004future gates unchanged. No automatic retry/clearance/provider.

Exact changed paths and patch against accepted B17working snapshot: B17R-FILES.md and B17R-changes.patch. **STOP for B17-Rreview. B18CLI requires separate authorization; frontend and live calls remain unauthorized.**
