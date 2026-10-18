# B16 local authenticated service API

B15 is human accepted. B16 exposes accepted B08–B15 services through typed FastAPI HTTP, not new municipal business logic. All R01–R18 remain binding. B10 genuine Gemini acceptance remains OPEN/PARTIAL. No B17 complete dashboard/map/graph/trace/SSE, B19scenario harness, frontend, live authorization or backend-completion claim.

## Exact coverage and contract decisions

`docs/evidence/B16-COVERAGE.md` assigns every normative operation:44 implemented B16 operations/42paths,8B17 and3B19 deferred. Actual generated OpenAPI is `docs/evidence/B16-openapi.json`; there are no501stubs. `/api/v1` prefix; `/docs` and `/openapi.json` are developer documentation, not domain capability endpoints.

DEC-060 corrects stale request/response shapes in contracts/api_endpoints.json and api_models.json against actual accepted service models. Old original specification fields remain where deferred, not authority over B16 accepted lifecycle rules. Added essential draft creation/access, approval detail, authorized order creation, inspection request/transition, hypothesis proposal/assessment/detail, work progress/inspection/evaluation/recurrence. The minimal hypothesis detail returns actual versioned current/history summaries; rich investigation hypothesis feed remains B17 GET, distinct from implemented B16 POST on the same path.

Success `{data,request_id,schema_version:1}`; errors `{error:{code,message,details,retryable},request_id}`. Typed Pydantic closed input/output and finite list/page fields generate real OpenAPI. All command fields are derived from accepted models with authority/request/path IDs removed; nested work inspection discriminated commands forbid reviewer/actor/request injection. Recurrence complaint is the strict B08issue union. Exact normalized service command validation runs again. No arbitrary Cypher, graph name, server profile path, role or runtime/provider configuration in public models. Source excerpts are validated B11 citations, never raw files/journals or instructions.

## Actual files, imports and dependency flow

`app.api.__main__` parses host-only private profile/auth/memory config and optional controlled UTC clock/localhost port. Its lifespan loads existing exact ActiveProfile, checks memory capability for that graph, opens existing DB connections, constructs Auth→PlanningService→Operations, Delivery, and Services. No migrations/seed/activation/workers at startup.

`app.api.application.create_app(services)` → dependency-injected server-owned services and B13 Auth principal (`dependencies.py`) → closed route table (`coverage.py`) and schemas (`models.py`) → `app.services.http.service.Services` → accepted ComplaintService/EvidenceService/PlanningService/Operations/Delivery or read-only `Reads` projections (`reads.py`). API modules issue no Cypher or domain writes. Fixed bounded read queries are confined to service projections/repository; no caller query text/label selection. Existing immutable migrations0001–0005 and repository fences unchanged. No new dependency or storage engine.

Official FastAPI docs consulted for response validation/filtering and security dependency behavior, then checked against installed FastAPI0.143.3/Pydantic2.14.1/Uvicorn0.54.0:
[response models](https://fastapi.tiangolo.com/tutorial/response-model/), [security dependencies](https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/).
Actual local runtime evidence, not documentation examples, is the acceptance proof.

## Authentication and scope

B13 private Auth database is explicitly configured; no public signup/seeding. Seven previously accepted synthetic operators/four server-owned roles unchanged. `POST /auth/demo-login` takes operator_id/demo_password, returns required short-lived session token; only this login response carries bearer token. Invalid credentials and missing/invalid/expired/revoked sessions401. `/auth/me` shows public server-owned identity; `/auth/logout` revokes real session. Tokens, credentials, private paths, raw exceptions and JSON input are not logged/exported in errors/evidence. Local access logging disabled; no wildcard credentialed CORS middleware. Login/body validation uses SecretStr and sanitized error handler, never Pydantic raw input errors.

ANALYST: intake/open/resume/propose/assess/draft/submit, independent outcome evaluation/recurrence. APPROVER: exact approval/rejection/order creation and approval views. DEPARTMENT_LEAD: assigned departmental reads, assignment/cancel/progress and authorized inspections/reports. ADMIN: accepted read/admin identity only; no automatic approval or work authority. `ANY` means a valid session, not anonymous. Roles never accepted from body/query.

Lead work scope uses accepted Operations.read_work_order, requires exact department+assignee. Plans require all task departments within lead scope; inspections derive department from committed request journal; report access follows producing inspection. Incident/cluster/investigation context requires explicitly owned assets/incidents; unowned or mixed scope fails conservatively. Knowledge source/procedure lists filter owner. Authorization precedes counts/cursors/projections. Missing vs forbidden restricted detail yields the same403 to leads; no hidden totals. Richer cross-department collaborative views need a later reviewed projection, not unfiltered property export.

Independent **operational** report review uses `X-Reviewer-Authorization: Bearer <analyst-session>` plus review_reason; actor session remains normal Authorization. Header credentials stay out of JSON/OpenAPI examples/logs. Existing B14 inspect service revalidates independent authenticated analyst and exact work/task/procedure/purpose/evidence/temporal bindings. A forged JSON Review is rejected422. Wrong reviewer role403; invalid reviewer session401. Standalone B09 reports are explicitly **unreviewed**, cannot manufacture reviewed work verification; use B14 work inspections for operational evidence.

## Durable commands, idempotency and recovery

`Idempotency-Key` required for every domain mutation. Server combines exact configured source+authenticated actor+key into HTTP-B16request ID, hashes template path+entity ID+canonical validated body+reviewer identity. Caller cannot supply request/actor identity. Existing hashed0005 companion `api_request` stores bounded transport intent and closed projected receipt through B15 Store's short repository fence/immutable audit marker. No secrets stored in this receipt; raw input is hashed, not journaled by transport. Service journals retain their accepted provenance separately.

Exact same-request replay returns saved projected receipt; conflicting key/path/entity/payload/reviewer409. Receipt is historical acknowledgment, not current authority; GET reflects current audited lifecycle. Concurrent/incomplete DISPATCHING or uncertain committed/no-receipt request returns409RECOVERY_REQUIRED with safe correlation and commitmentUNKNOWN, never automatic redispatch or false definitely-uncommitted claim. Successful service followed by projection/schema/ack failure also remains recovery-required. Known pre-write validation/stale/auth errors are classified normally; B09 post-dispatch readback preconditions conservatively require recovery. A failed recovery write/checkpoint cannot promise fresh feedback persistence.

Investigation creation first verifies active delivery setup, delegates B09open, then persists B15 explicit request. If interrupted between steps, COMMITTED B09 CASE_OPENED adapter remains discoverable; transport returns uncertainty rather than silently losing the persisted case or redrafting it. Explicit resume stores intent only; no long model/MCP work/background task inside HTTP. Separate B15worker uses original case/thread and budgets, default authored deterministic READ→PAUSE. Live Gemini is unavailable from API/startup. No retries, quarantine clearance, budget increases, automatic plan changes or worker activation endpoint.

Recovery operator: stop implicated worker, retain request/event/case/plan/thread/source pending intent/quarantine. Inspect `api_request:HTTP-B16-*` and accepted domain journal/receipt using trusted local tools. Reconcile exact original IDs through existing supported procedures. API deliberately offers no reset/automatic repair endpoint; no new request merely to evade uncertainty. B15CLI reconcile verifies existing completion evidence, never reruns an uncertain wake. Missing proof remains operator-required.

## Read projections and limitations

Finite candidate scan500, relationship projection100, pages1..50 with stable ID cursor and authorized total. Overflow fails explicitly rather than silently discarding candidates. Basic cursor/count is needed for secure B16lists; richer indexed filters and graph/map/trace/SSE pagination are B17. Reads use fixed current host UTC/simulated time; future/invisible nodes fail closed.

Complaint/incident/recurring cluster are separate DTOs. Hypothesis summary labels each actual historical assessment and current assessment ID, source IDs and missing evidence without whole journal/graph internals. Plan includes immutable DRAFT receipt and actual audited current status/hash separately; approval never asserts execution gates. WorkOrder completion never sets resolution_verified true; independent Outcome records expose assessment/policy/evidence and case_closed. Monitoring remains unresolved absent independent observation opportunity. B11 citations/procedures retain SYNTHETIC/PROPOSED/trusted_as_instructions:false. B05case memory preserves bounded-history gaps and traversal limitations; asset-linked context is not proof that an intervention resolved an incident. Raw provider/checkpoint/decision rationale, source journals and hidden scenario data are not serialized.

Bounded reads are current projections, not cross-graph snapshots. Existing source/procedure/integrity guards fail if state changes during validation. Transport receipts may be historical; refetch current GET after commands. Existing finite repository mutation audit10000 and B15source/delivery limits still apply. No pruning/deletion to bypass them.

## Explicit local startup and docs

Run from repository root using existing locked Python3.12 environment/local FalkorDB/MCP. Provisioning/migrations/activation and memory source authorization must have been explicitly approved already. `PROFILE`, `AUTH_STORE`, `MEMORY_PROFILE` below are trusted local file paths, not bearer credentials. Keep private mode0600 and never upload .env/.runtime/profiles/authDB.

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.api \
  --profile "$PROFILE" --auth-store "$AUTH_STORE" \
  --memory-profile "$MEMORY_PROFILE" --port 8000
```

Server binds127.0.0.1 only, one process, no automatic worker. Optional `--at` is a canonical controlled UTC timestamp for deterministic simulation, host-only. Missing/inconsistent/private setup fails startup with sanitized diagnostic, no fabricated fallback.

Visit http://127.0.0.1:8000/docs and http://127.0.0.1:8000/openapi.json. `/api/v1/health/live` checks process; `/health/ready` actually probes graph, explicit delivery activation, auth, MCP tools/list, public Saver read and configured memory metadata. Missing dependencies yield503 with bounded health statuses. These health reads do not run a model or clear state. Actual network evidence B16-network.json distinguishes running-server proof from ASGI tests.

Log in locally with existing synthetic credential; use Swagger Authorize with returned bearer token. Never paste real values into evidence. Inspect `/auth/me`, a scoped work-order list, draft/current lifecycle and monitoring. B15worker remains a separate explicit CLI (`backend/EVENTS.md`). Ctrl-C/SIGTERM stops API; it cannot erase pending domain events or stop/retry investigations. Stop/restart the worker using B15documented commands/proof-aware recovery; no new API scheduler.

## Focused reproduction

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-human-unit.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_api.py -q --tb=short
CIVICLY_TEST_REQUEST_LOG=/tmp/b16-human-real.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_api_runtime.py -q --tb=short
make test-spec
```

Ordinary pytest and spawned MCP/Uvicorn children inherit Gemini/countTokens blocking. Real test authors model choices but uses actual DB, HTTP service calls, MCP transport/LangGraph/Saver and TCP localhost Uvicorn. See exact observed commands/failures/counts in B16-COMMANDS.md and B16-RESULTS.md; static models or ASGI success alone are not network/live-AI acceptance.

STOP after B16 for review. Proposed next B17: complete dashboard/map/graph/trace DTOs, richer filters/cursors and durable authorized SSE reconnect; no frontend or live calls without separate authorization.

## Current B17 transport and frontend-readiness — DEC-062

This section takes precedence over B16's historical B17-deferred statements above. B16/R accepted; B17 adds all eight read/stream operations:52actual operations/49paths. Only3B19scenario operations remain deferred. No frontend/B18/B19/live provider or backend-completion claim. Actual current matrix/OpenAPI: `docs/evidence/B17-COVERAGE.md`, `B17-openapi.json`.

API → closed `ReadFilters` → `services.http.views.Views` → bounded parameterized `GRAPH.RO_QUERY` through the existing repository. Six canonical resource lists (complaints/incidents/problem-clusters/approvals/work-orders/departments), dashboard and map accept issue/status/department_id/after/before where meaningful; unsupported/decorative parameters are rejected. Resource list limit1..50, default25, strict issue enum/UTC window; dates filter the first applicable reported/start/request/create timestamp, inclusive endpoints; future upper cutoff rejected. Authorization and filters precede count/page. Stable ID cursor is exclusive; trace uses normalized UTC timestamp+stable eventID. A response checks source revision/pending before/after; changing sources fail closed, subsequent pages reflect current state and are not snapshot-isolated. Other accepted plans/procedures/memory/monitoring/outcome lists retain their explicitly bounded B16 parameters; no silently accepted unused filter.

Candidate scans501 detect >500; two per-request adjacency batches each5001 detect >5000 and replace incident/ownership N+1 reads. Per-root relationship cap100 is retained. No shared cache or storage subsystem. Inspection lookup now restricts candidates to actual case incident/hypothesis asset context before readback. Overflow returns sanitized READ_CAPACITY for B17 projection limits; source/pending/integrity failures remain fail closed.

Graph/asset neighbors: depth1..5(default2),120nodes/200edges; fixed relationship inventory, stable registry labels/types/endpoints, accepted B05 temporal/provenance proof validation (64 proof-query/5second budget). `include_candidates=false` excludes nonverified physical associations; explicit true includes CANDIDATE/REPORTED with their actual status. All associations remain context, not causal proof. Graph/root/edge/provenance scope checked; leads conservatively see only records covered by existing department policies. Source IDs and validity dates remain explicit. Selected paths are read from the actual COMMITTED B10 tool journal, linked through validated broker/server/decision identities, input-selection digest and trace pathIDs, then admitted only when ordered endpoints/edges/evidence remain visible in this projection. Missing/nonpersisted paths are not reconstructed. Graph negative results/truncation never imply global absence.

Map: canonical Location numeric lon/lat only, actual scoped incident/asset/case references; unavailable geometry IDs are explicit; no artifact loading, invented coordinates or proximity links. Features are paged by stable locationID. Asset singular location/owner fields preserve planned contracts alongside typed label/plural references; absent canonical condition is null, not invented.

Trace: exact canonical investigation/thread binding, validated MCP TraceStore BROKER records, actual parent SERVER/decision chain and public Selection.summary only. Official and Civicly namespaces/server identities remain separate. Official Saver get_tuple is read-only; return stored checkpoint phase/pause/recovery, current canonical active/historical scope, sanitized error codes and revision/fresh-read requirement. An interrupted checkpoint can store phase Coordinator while paused at the following AwaitDependency interrupt; do not invent a newer phase. Scripted mode `DETERMINISTIC_FAKE_MODEL` is explicitly distinct from genuine provider behavior. No raw tool args/results/journals/provider bodies/private reasoning. Department leads get filtered evidence/path references and no unproven department-scoped free-text rationale.

Evidence: existing EvidenceDTO compatibly adds validated per-finding Observation (code, statement, method, target, date, result, measured value/unit) and attributed inspection/source/reviewer/occurrence binding. Reader verifies actual report hash, producing relationship, committed request/report and finding bindings. Non-report records explicitly state that validated observations are unavailable; raw journals stay private. Source citations remain versioned SYNTHETIC/PROPOSED and untrusted as instructions. PlanDTO.approval_status retains B16's legacy audited **plan lifecycle** meaning, documented in schema and limitations; actual approval is ApprovalDTO.status. A COMPLETED plan can therefore have an APPROVED approval and immutable draft_receipt.approved=false; execution gates and verified outcome remain separate.

### SSE guarantees and limits

`GET /api/v1/events/stream` uses `Authorization: Bearer` header (browser fetch stream, not unauthenticated native EventSource). No bearer URL parameters. Optional `investigation_id` is authorized before headers and each poll. `cursor` and Last-Event-ID are nonnegative decimal source-local registration cursors, default0; if both given they must match (409 CURSOR_CONFLICT). Malformed/unsupported422 CURSOR_INVALID, future409 CURSOR_FUTURE, missing registration409 CURSOR_EXPIRED and refetch. No retention deletion policy exists: expired means a detected unavailable registration, not a fabricated time window. Midstream dependency/integrity failure emits sanitized `error`/STREAM_UNAVAILABLE and closes; no automatic retry/repair.

Each data event has durable cursor SSEid, explicitly mapped event name and closed SSEStream JSON. Canonical `id/occurred_at` also have planned `event_id/timestamp` aliases. Mapping in contracts/event_delivery.json: actual tool→case_tool_called, decision→decision_recorded, request-inspection source→inspection_requested (intent, not field execution), report→inspection_recorded, plan submission→approval_needed, order/status→work_order_updated, recurrence→case_reopened; remaining normative facts→case_updated or error. There are no invented thinking/status events.

Every registered row is inspected in contiguous cursor order, including unauthorized/nonmatching rows. `event: cursor` with same durable last-inspected id and data `{cursor}` advances transport position without exposing hidden event fields. Clients persist this cursor too. Filtering/scope changes do not authorize replay of previously hidden history; refetch newly authorized resources. Heartbeats are comments only. Per-poll and immediate per-emit authentication/resource scope; revoked/expired sessions get sanitized UNAUTHORIZED stream error then close. Buffer50, poll.25s, connection30s then reconnect/refetch; dependency read bounds still apply. No domain ack, worker, discovery, checkpoint write, per-client lease or queue in the stream. Disconnect cancels its generator; domain delivery state is untouched.

The existing separately operated B15 worker/discovery registers new source facts. B17's narrow source adapter additionally validates actual AgentDecision/TraceStore facts and registers INFO events using existing cutover/cursor/fence; one decision scan, one trace connection, finite100bound cases/500decisions/500activity facts/160traces per thread. Uses existing configured delivery cutoff, not a different wall-clock cutoff. No historical autoactivation. Late discovery appends a new cursor even when source revision/time predates already streamed events. Original source decisions/traces, attempts and checkpoints remain intact. Shared-graph/cross-graph writes are not claimed atomic or exactly once.

### Reproduce startup and inspect

Use existing private host setup (do not copy credentials into evidence):

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.api --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --port 8000
```

Existing immutable migrations, MCP credentials/ACL, memory capability, auth accounts and explicit B15activation must already exist for this exact source. Startup never provisions/migrates/seeds/activates/runs an agent. The separate existing worker `python -m app.events --profile "$PROFILE" run --owner local-demo --batches 10` performs discovery/INFO registration and only already authorized durable work. Do not use a worker command merely to inspect a retained recovery case. `/docs` covers52routes; login privately and use Bearer header for REST/SSE. Cursor/refetch protocol and actual retained IDs: docs/evidence/B17-RESULTS.md and B17-journey.json. No new packages or images; existing pinned runtime only.

## B17-R query contract correction — DEC-063

This section supersedes any broad shared-filter wording above. Each route's OpenAPI query list is its exact allowlist; unknown, irrelevant or repeated parameters return the existing sanitized422 VALIDATION_ERROR. Internal ReadFilters remains a service superset, not a public route schema. Route-specific closed query models reuse the existing scalar/boolean/date/bounds validators and convert into the unchanged service model only after validation. No domain filter, auth, storage, recovery or SSE redesign.

| Read route | Accepted parameters |
|---|---|
| Investigation hypotheses | status, limit, cursor |
| Dashboard summary | issue, status, department_id, after, before |
| Investigation trace | status, after, before, limit, cursor |
| Map features | issue, status, department_id, after, before, investigation_id, limit, cursor |
| Six resource lists | issue, status, department_id, after, before, limit, cursor |
| Investigation graph / asset neighbors | depth, include_candidates |
| Asset detail | none |
| Durable SSE | cursor, investigation_id; Last-Event-ID remains a header |

Hypothesis status filters current native hypothesis status; pages use stable exclusive ID cursor and limit. **after/before are rejected**: creation time versus assessment time is not normatively defined, so no new history meaning is invented. Dashboard filters apply to each authorized metric's resource before aggregate calculation using existing status/issue/department and inclusive reported/start/request/create timestamp semantics; **limit/cursor are rejected**, because aggregate metrics have no pages. Trace after/before retain inclusive actual decision-decided/tool-finished timestamp filtering before chronological timestamp+stable eventID paging. Resource/map filtering, graph budgets and authenticated stream replay remain unchanged. Legacy paginated GETs also reject repeated scalar keys instead of selecting one silently.

Exact all-GET query coverage/generated OpenAPI and verification: docs/evidence/B17R-QUERY-COVERAGE.md, B17R-openapi.json and B17R-RESULTS.md. No B18/frontend/live authorization.

## Current B19 scenario controls — 2026-10-18
This section supersedes earlier B19-deferred statements without removing history.55operations/52paths now include authenticated GET /demo/scenarios, ADMIN POST /demo/reset and ADMIN POST /demo/scenarios/{id}/advance. Strict generated schemas and neutral public inventory; no query parameters or graph/file selectors. Release requires actual in-progress bound inspection plus authenticated X-Field-Authorization department lead and independent X-Reviewer-Authorization analyst. Idempotency/UNKNOWN recovery use the existing transport adapter. Safe optional ErrorDetails.blocker_code identifies allowlisted scenario prerequisites only; no raw exception text. Full runbook/limitations: backend/DEMO.md; actual OpenAPI docs/evidence/B19-openapi.json. B19 mechanics are not agent-success or backend-complete acceptance; B20/frontend/live require review/authorization.

B20-R-OWNERSHIP adds only POST /responsibilities (DEPARTMENT_LEAD), POST /responsibilities/{id}/review (independent ANALYST) and GET /responsibilities/{id} (seeded read roles, lead department scope). Closed typed schemas, existing source-bound keys and sanitized UNKNOWN recovery. No query parameters or graph selectors. Full contract/operator semantics: backend/RESPONSIBILITY.md.


## Frontend backend demo additive picker
Authenticated GET `/api/v1/investigations` returns Page[InvestigationDTO] using scoped query/filter/pagination validation. Current contract exposes 59 operations across 55 paths. Paused/recovery cases remain visible; client must not infer model success from a listed case. See FRONTEND_HANDOFF.md.


## Exact task scope for approval UI — DEMO-FIELD-REVIEW

PlanDTO adds `task_bindings`: server-stored local/native task mapping, native current status/hash, action/targets/department/dependency IDs and enabled eligible synthetic assignees. It is validated against persisted HAS_TASK/ASSIGNED_TO/TARGETS/DEPENDS_ON/native action; drift fails closed. It is metadata, not authority. Existing immutable draft/hash and operational permission checks remain unchanged. Revalidate plan/version/hash and current approval hash before mutations. Regenerate closed-schema clients;59operations/55paths/185schemas. No new route or migration.
