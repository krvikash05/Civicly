# Backend APIs and event contracts designed for strong frontend explainability

## Base
FastAPI `GET /openapi.json` generated from Pydantic models; `/api/v1` prefix. Contract inventory machine-readable in `contracts/api_endpoints.json`; all responses typed. Default success `{data, request_id, schema_version:1}`, error `{error:{code,message,details,retryable},request_id}`. No raw Cypher from web clients.

## Important routes / UI relationships
| Resource | Core routes (prefix /api/v1) | Frontend purpose |
|---|---|---|
| auth | `POST /auth/demo-login`, `GET /auth/me`, `POST /auth/logout` | Operator identity and role-controlled actions |
| command | `GET /dashboard/summary` | Top issue clusters, pending approvals, active case counts |
| complaints | `POST /complaints`, `GET /complaints`, `GET /complaints/{id}` | Submit/inspect original reports |
| incidents | `GET /incidents`, `GET /incidents/{id}`, `GET /problem-clusters`, `GET /problem-clusters/{id}` | Classification, recurrence, issue history |
| investigation | `POST /investigations`, `GET /investigations/{id}`, `POST /investigations/{id}/resume`, `GET /investigations/{id}/trace`, `GET /investigations/{id}/hypotheses`, `GET /investigations/{id}/graph` | AI Investigation Studio |
| evidence | `GET /evidence/{id}`, `POST /inspections/{id}/observations`, `GET /inspections/{id}` | Source viewer, missing evidence fulfillment |
| plans/approvals | `GET /plans/{id}`, `POST /plans/{id}/submit-approval`, `GET /approvals`, `POST /approvals/{id}/decision` | Plan DAG, approve/reject |
| work | `GET /work-orders`, `GET /work-orders/{id}`, `POST /work-orders/{id}/status`, `POST /work-orders/{id}/outcomes` | Coordination board |
| knowledge | `GET /departments`, `GET /procedures`, `GET /documents/{id}`, `GET /cases/{id}/memory` | Company brain and source citations |
| map/graph | `GET /map/features`, `GET /assets/{id}`, `GET /assets/{id}/neighbors` | Geographic map and FalkorDB Canvas explorer |
| monitoring | `GET /monitoring`, `GET /problem-clusters/{id}/outcomes` | Results / recurrence verification |
| streaming | `GET /events/stream?cursor=` | Live run trace, authorized events, reconnect |
| dev only | `POST /demo/reset`, `POST /demo/scenarios/{id}/advance`, `GET /demo/scenarios` | Reproducible presentation, never public production mode |

## Important data DTOs
**InvestigationSummary**: ID, affected issue types, cluster/incidents, phase, current agent role, missing evidence, candidate hypotheses, pending inspection/approval, last decision, graph revision, `simulation_mode`.

**HypothesisDTO**: id, cause code, suspected assets, supporting and contradiction evidence IDs, source citations, assessment history with changes, alternatives, next verification step, and confidence *label* only.

**GraphSubgraphDTO**: `{nodes:[{id, labels, display_label, kind, status, source_kind, evidence_ids}],edges:[{id,type,source,target,valid_from,valid_to,verification_status,source_evidence_ids}],decision_path_ids,graph_revision,truncated,as_of}`. Cap <=120 nodes / <=200 edges by default; depth <6, server-auth-filtered; stable IDs and explicit provenance so FalkorDB Canvas can map the data without querying DB from browser.

**AgentTraceEvent**: event_id, investigation_id, timestamp, agent_role, state, tool_name, sanitized input summary, input/output schemas, graph paths, source IDs, duration, decision rationale summary, result, error. Feed UI via SSE only from persisted events.

**PlanDTO**: version/hash, tasks, dependency DAG, required departments, procedures, evidence refs, approval and execution status, explicit simulated flag, monitoring criteria and blockers.

## SSE durability/reconnect
SSE `id` is durable event cursor; `event: case_tool_called|decision_recorded|inspection_requested|approval_needed|work_order_updated|case_reopened|error` with typed JSON payload. `Last-Event-ID` supported; reconnect replays bounded events or returns `CURSOR_EXPIRED` and frontend refetches authoritative case. The stream is not itself authoritative state. No automatic fake 'thinking' steps.

## HTTP errors
`VALIDATION_ERROR`(422), `UNAUTHORIZED`(401), `PERMISSION_DENIED`(403), `NOT_FOUND`(404), `CONFLICT`/`STALE_PLAN_VERSION`(409), `APPROVAL_REQUIRED`(403/409), `DEPENDENCY_BLOCKED`(409), `EVIDENCE_REQUIRED`(422/409), `EXTERNAL_UNAVAILABLE`(503), `GRAPH_UNAVAILABLE`(503), `MCP_TOOL_ERROR`(502), `RATE_LIMITED`(429). Generate real OpenAPI, validate example responses, use request ID, no stack traces to clients.

## Frontend compatibility gates
Even backend-first, tests must verify an operator can reconstruct the full story without reading server logs: complaint -> merged incident/recurrence -> agent choices -> exact graph traversal -> evidence and counterfactual -> plan DAG -> approval -> work progress -> monitoring -> memory. Every key UI action has at least one API endpoint and relevant event; any gap requires API contract revision before frontend.

## B02 canonical scope contract (v3)
Canonical domain records use `municipality_id='demo-city'`, fixed by the server.
`tenant_id` is not a domain alias or caller-controlled input. Framework integration
may translate the same fixed value explicitly if its verified API requires it.
All normative machine contracts reference this same municipality_scope policy.
This is one synthetic municipality, not enterprise tenant isolation. Legacy v1/v2
fixtures require explicit conversion before canonical import; no implicit scope,
unknown-field dropping, or invented temporal evidence is permitted.

## B16 implemented transport correction (DEC-060, 2026-10-18)

B15 accepted; B16actual44operations/42paths. Normative contracts/api_endpoints.json marks each operation B16implemented, B17deferred or B19deferred; API schemas generated from accepted B08–B15services supersede stale transport fields above. Exact bindings/CAS/assignments and typed progress/inspection/evaluation commands are mandatory. Work-order outcomes is independently authenticated ANALYSTevaluation, not caller declared success. Essential draft creation/list, authorized order creation, inspection request/transitions, work progress/inspection/recurrence, hypothesis proposal/assessment/minimalcurrent-historydetail and approvaldetail added; no business gate weakened. `X-Reviewer-Authorization` header authenticates separate analyst, never JSON Review/token. Plain B09reports remain unreviewed.

B16basic bounded scoped lists/cursors are implemented; full B17dashboard/map/graph/trace/hypothesisstudio/SSE/richerfilters are absent, not stubs. SSEtransport will use B15registration cursor independent of domainID/attempt. Actualread DTOs include immutable draft receipt/current lifecycle, approval vs gates, dated current/history assessments and latest recorded outcome vs completion. Independent missing opportunity remainsunresolved. Only host-configured private source/auth/memorycapabilities and prior explicitdeliveryactivation, no callergraph/runtime/roles or autoactivation. HTTPinvestigation/resume storesB15intent; separateworker runsdeterministically with existingMCP/Saver/ownership, no livepermit.

Exact coverage/sourceflow/security/startup/recovery and tested limitations: backend/API.md, docs/evidence/B16-COVERAGE.md/B16-RESULTS.md. This is not B17/SSE/frontend/fullbackendcompletion.

## B17 actual implementation (DEC-062)
B16/R accepted. All eight previously deferred read/stream routes now implemented,52operations/49paths, only B19demo routes deferred. Closed generated contractsv4 preserve planned DTO names/required identity fields, add typed actual observations, strict bounded graph/path/map/trace and source-local authorized SSE. Nullable asset condition corrects the planned mandatory string against optional canonical storage; no invented condition. B16legacy PlanDTO.approval_status is explicitly audited plan lifecycle, actual approval decision from ApprovalDTO.status. API clients must display these separately.

Actual runtime/query/control flow, metric/filter definitions, limits, cursor errors/auth and operator startup in backend/API.md current B17 section. Current evidence/matrix/OpenAPI and shared real HTTP/FalkorDB/MCP/Saver/TCP-SSE journey in docs/evidence/B17-*. Scripted model selections are labelled; B10 full genuine acceptance OPEN/PARTIAL. No frontend/B18/B19/live completion.

## B17-R exact query parameters (DEC-063)
Public query models are route-specific, not the shared internal ReadFilters. Hypotheses accept status/limit/cursor only; after/before rejected422 because creation-versus-assessment timestamp semantics are unspecified. Dashboard accepts only issue/status/department_id/after/before, rejects limit/cursor. Trace retains actual persisted decision/tool timestamp window before pagination; resource/map/graph filters unchanged. Unsupported/unknown/repeated keys return sanitized422. Exact current all-GET allowlists in contracts/api_endpoints.json query_parameters/query_schema_id and docs/evidence/B17R-QUERY-COVERAGE.md; OpenAPI generated from the same closed models. No business/storage/recovery/SSE redesign; all18requirements preserved, B18/frontend/live unauthorized.

### B19 current compatible demo contract — DEC-065
B18 accepted. All three previously deferred demo routes implemented; total55operations/52paths. Public catalog uses neutral numbered titles and current released state, never evaluator criteria or future observations. Source-bound keyed ADMIN fresh reset/advance plus independently authenticated field/reviewer sessions, actual inspection lifecycle, bounded typed reports and existing recovery adapter. Safe optional blocker_code is a compatible error detail. API models v5/generated OpenAPI are authoritative; detailed host controls and limitations in backend/DEMO.md. No automatic approval, solver, successful outcome, frontend or live-provider claim. B20–B23 remain behavioral acceptance gates.
