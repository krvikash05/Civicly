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
