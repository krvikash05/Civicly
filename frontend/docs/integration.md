# Parallel development and integration agreement

## Sources and ownership

Requirements R01–R18 remain binding. F00 primarily supports R15/R16 and preserves the remaining requirements in the UI plan. Frontend owns `frontend/`; backend owns `backend/`, `contracts/`, dataset/graph state and backend evaluation. Shared tracking files receive append-only, task-labelled notes. Read shared files immediately before editing; do not restore, stage, commit or overwrite another worker's changes.

Frontend reads `contracts/api_endpoints.json`, `api_models.json`, `event_delivery.json`, `event_types.json` and backend/API.md. Never hand-edit backend contracts to satisfy a UI design. Raise a specific missing capability for a separately authorized backend task. Contract checker failures require review rather than automatic baseline acceptance. Root schema versions and success-envelope schema_version are separate values; do not equate them.

## Transport (implemented foundation in F02; lifecycle/SSE in later tasks)

Use relative `/api/v1` browser requests with a development reverse proxy to a host-configured local API origin. Configure the frontend proxy, avoiding backend CORS changes. Dev UI port 3100 avoids FalkorDB Browser port 3000. Select API origin from the backend operator runbook; do not assume a running instance or start one implicitly. Production routing remains a later integration decision.

Generate DTOs from current backend schemas; compare fresh runtime OpenAPI before client integration. Closed route query allowlists differ: dashboard has no pagination, hypotheses have no date filters. Validate error envelopes and request IDs; distinguish unauthorized, forbidden, conflict/stale approval, missing evidence, dependency unavailable and uncertain-write recovery. Preserve original request identity/idempotency key after an uncertain write; do not automatically retry mutations or create a replacement key.

Judges have no sign-in form. A server-configured existing OP-ANALYST account opens a temporary demo session automatically; its private password stays on the frontend server. Use Bearer authentication with session tokens held in memory; never tokens in URLs, fixtures, logs, repository files or browser persistent storage. Reconnect only through the same supported backend login; never grant a higher role implicitly. Reviewers/field actors require their own authenticated headers where specified; never derive authorization solely from UI role visibility. Server authorization remains authoritative. Do not pass graph/profile/tenant selectors from the browser; municipality is server-fixed demo-city.

SSE uses authenticated fetch, not native EventSource. Parse real data and cursor control frames, retain Last-Event-ID per session/source/filter context, and handle expired/future/conflicting cursors. Refetch authoritative GET state after reconnect; do not blindly loop on integrity/dependency errors. Clear old cursor/session data on logout or source change. No fabricated thinking steps.

## UI semantics

Agreed priority: Overview and Investigations navigation with evidence, graph, plans/approvals, work and monitoring/memory inside the case. Standalone Intelligence Explorer and full Knowledge/Memory workspaces are later extensions. Cover WATERLOGGING, ROAD_DAMAGE and WASTE_ACCUMULATION equally. Preserve SIMULATED/SYNTHETIC labels, unknown/unverified/null values, evidence dates, rejected hypotheses, revisions and source authority. Plan lifecycle, approval decision, work completion and verified resolution are different states. Never invent confidence percentages, citations, geometry or graph connections.

Backend-unavailable screens must say unavailable. Any future design fixture mode must be explicitly labelled and isolated from live clients; fixtures are not integration proof. No UI may bypass missing owner acquisition or unsupported action/evidence gates currently tracked by backend work.

## Integration acceptance

Static contract checks catch drift only. F02+ requires real HTTP checks on a disposable authorized source, with approved setup by the backend owner, not mutations of the running review instance. Final proof includes authentication/RBAC, read projections, graph provenance, real MCP-derived traces, SSE reconnect/cursor frames, exact plan/version/hash/assignee/scope approvals, idempotent writes and monitoring/recurrence. Deterministic/fake-model vs genuine live-agent evidence stays separately labelled. Final backend acceptance remains the backend owner's gate.

## Official Canvas direction — F01

Human requested use of official FalkorDB UI tooling. Official documentation https://docs.falkordb.com/browser/canvas describes @falkordb/canvas as a standalone web component with React/TypeScript usage, setData(nodes/links), layouts and interaction hooks. F04 will verify the installed release, client-only hydration, stable backend ID mapping, relationship provenance/verification styling, decision-path highlighting and accessible textual alternatives. F01 only reserves the graph panel; no Canvas dependency or fabricated graph is mounted.
