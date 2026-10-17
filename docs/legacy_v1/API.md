# Proposed FastAPI boundary contract

API prefix: `/api/v1` (JSON, UTC timestamps, explicit `schema_version`). Routes below must generate an OpenAPI document through FastAPI/Pydantic; frontend TypeScript client types generated from OpenAPI. This doc is a route inventory, not a misleading claim of complete OpenAPI implementation.

## Envelope
Success: `{ "data": <typed response>, "request_id": "...", "schema_version": 1 }`.
Error: `{ "error": {"code":"...", "message":"...", "details":{}}, "request_id":"..." }`.
Codes include: `NOT_FOUND`, `VALIDATION_ERROR`, `CONFLICT`, `UNAUTHORIZED`, `PERMISSION_DENIED`, `APPROVAL_REQUIRED`, `STALE_PLAN_VERSION`, `DEPENDENCY_BLOCKED`, `EVIDENCE_REQUIRED`, `EXTERNAL_UNAVAILABLE`, `MCP_TOOL_ERROR`, `GRAPH_UNAVAILABLE`.

## Mandatory routes
| Verb | Route | Purpose / access |
|---|---|---|
| POST | `/complaints` | Authenticated intake, classify + link / queue investigation |
| GET | `/complaints/{id}` | Complaint with source and incident link |
| GET | `/incidents` | Filter by issue, zone, date, status |
| GET | `/incidents/{id}` | Canonical event and related reports |
| GET | `/problem-clusters` | Active/recurrent problem index |
| GET | `/problem-clusters/{id}` | Cluster incident history, monitoring |
| POST | `/investigations` | Open investigation on incident/cluster, idempotent |
| GET | `/investigations/{id}` | Status, hypotheses, current action, missing evidence |
| POST | `/investigations/{id}/resume` | Resume/wake agent (idempotency) |
| GET | `/investigations/{id}/trace` | Sanitized run/decision/MCP tool calls |
| GET | `/investigations/{id}/graph` | Bounded evidence subgraph (no raw Cypher) |
| GET | `/investigations/{id}/hypotheses` | Versioned assessments and source IDs |
| POST | `/inspections/{id}/observations` | Role-authenticated inspection observation and evidence |
| GET | `/plans/{id}` | Versioned plan DAG, tasks, justification |
| POST | `/plans/{id}/submit-approval` | Propose authorization (not approve) |
| POST | `/approvals/{id}/decision` | APPROVE/REJECT with role and exact plan hash |
| GET | `/work-orders` | Task board; filter department/status |
| GET | `/work-orders/{id}` | Work order, event history, outcome |
| POST | `/work-orders/{id}/status` | Department-lead operation with evidence |
| POST | `/work-orders/{id}/outcomes` | Reviewable outcome observation |
| GET | `/departments` | Org structure and current responsibilities |
| GET | `/procedures` | Versioned operational knowledge |
| GET | `/events/stream` | Authenticated SSE for statuses and agent activity |
| GET | `/health/live` | Process liveness |
| GET | `/health/ready` | FalkorDB, MCP and critical dependencies readiness |

## API security
- Authenticated session/token for operations. `APPROVER` role required for plan approval; `DEPARTMENT_LEAD` assigned to department for completion; analysts may draft but not authorize.
- Every non-idempotent POST requiring retry uses `Idempotency-Key` and returns same result for identical key + body, conflict for changed body.
- No endpoint exposes credentials or general-purpose graph mutation. `graph` route returns `nodes`, `links`, `evidence_ids`, `graph_revision`, `truncated`; it is sanitized, bounded and authorization-filtered.
- Requests must validate enum + referential IDs from registry and state rules. Return 409 CONFLICT for stale plan version and illegal status transitions.
- `GET /events/stream` is an update transport, not authoritative state: on reconnect UI refreshes canonical API resources.

## UI minimal pages
`/dashboard`, `/complaints`, `/incidents`, `/investigations/[id]`, `/operations`, `/approvals`, `/knowledge`, `/outcomes`.

## Work order action semantics
`POST /approvals/{id}/decision` does not itself mean the physical work started. Only after validation may coordination create simulated or external work orders. `POST /work-orders/{id}/status` can mark simulated completion only with attributable mock department event; problem remains monitoring.
