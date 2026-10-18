# B15 — bounded durable local delivery

B15 implements local deterministic delivery only. All R01–R18 remain binding; B10 full genuine Gemini acceptance remains OPEN/PARTIAL. There is no live-provider authority, HTTP/SSE route, municipal execution or backend-completion claim.

## Prerequisites and authorization

Use Python3.12 and the locked backend environment, running local FalkorDB6.0.2 and the accepted B06 official/B07 domain MCP integrations. An existing private `ActiveProfile` must authorize the **exact** source graph, graph-read account and separate Saver graph. Existing immutable migrations0001/0004/0005 must be READY. Delivery never installs migrations, creates profiles, enumerates proof graphs, adopts `civicly_knowledge`, rotates credentials or activates historical datasets automatically. No new dependency or migration.

Explicit activation stores current source repository revision, existing source identities, operator/reason and optional <=20 selected original event IDs. Later committed facts are admitted; older events require that explicit selection. Activation is immutable/idempotent, not an implicit rewind. Undelivered older events remain in their original stores. A PREPARED journal is not treated as COMMITTED; later completion above the cutover revision is discovered. Source scans are bounded (500 native events,500 accepted journals,100 plan drafts); exceeding a bound fails visibly and requires scoped operator reconciliation, never silent truncation or deletion. This is a finite demo, not an unlimited event broker.

## Actual file/import and control flow

`app.events.__main__` → private `app.active.load/active_scope` → Settings/connect → GraphRepository → Delivery(Store,Sources) → Worker(Runtime).

`models.py` imports canonical event inventory and strict B09 ID/time/model types, defines event validation/routing/backoff/coalesced identity/public projection. `sources.py` uses fixed bounded RO reads and accepted B08/B09/B12/B13/B14 readback services. `store.py` reuses OperationsMigration readiness and Operations.Storage. `service.py` owns activation/discovery/registration/claims/consumer receipts/public cursor/monitoring/operator controls. `worker.py` owns dispatch/recovery/heartbeat/bounded polling. `runtime.py` uses existing brokers, InvestigationAgent, ownership and public FalkorDBSaver.

Committed domain record → validate original envelope or derive supported journal fact → delivery companion + optional native DomainEvent + public cursor in one source-graph fenced write → case claim → RUNNING → release source writer fence → existing agent ownership/MCP/Saver execution → checkpoint host completion marker → receipt/DONE under a new short source fence.

Every companion transition includes fresh `Evidence(B15_DELIVERY_AUDIT)` as the existing repository mutation-intent subject. This prevents companion-only ambiguous writes being mistaken for unchanged subjects. Native DomainEvent delivery_status is a mirror; original payload_ref/envelope identity is immutable. Audit evidence contains transition hash/keys, not source text/model reasoning. No generic runtime Cypher write tool is exposed.

## Durable source adapters and trigger matrix

- **B08 INTAKE**: read back COMMITTED journal/receipt; deterministic new `ADAPT-B15-*` facts COMPLAINT_ACCEPTED and INCIDENT_LINKED. **B08 REGROUP**: committed receipt yields informational GRAPH_EVIDENCE_CHANGED because rebinding needs explicit review.
- **B09**: read back committed journal plus native nodes/edges; open→CASE_OPENED; report_inspection→INSPECTION_RESULT_RECORDED; assess→HYPOTHESIS_ASSESSED; other analytical facts→GRAPH_EVIDENCE_CHANGED. Agent actor `civicly-b10-analyst` is informational to prevent self-wake loops. Proposal/pending inspection/transition is informational; a completed external report can wake.
- **B10**: accepted analytical writes use B09 journals; no fabricated decision history. AGENT_DECISION_RECORDED remains informational. Existing checkpoints retain original identity/bytes.
- **B12**: verified draft companion/native plan yields a new informational GRAPH_EVIDENCE_CHANGED fact; creation alone confers no approval authority.
- **B13/B14 native DomainEvent**: resolve exact original event in hashed operation payload, check type/entity/time/idempotency against native record. Preserve original event ID, actor, revision, source and payload. The B09 journal and a B14 native event can describe distinct provenance views of one report; they retain different identities and compatible pending wakes may coalesce. No claim of a historic event that was never emitted.
- **Explicit local resume**: authorized idempotent AGENT_RESUME_REQUESTED, stable ID from investigation/request, source `explicit-resume:*`; never impersonates human approval. A failed/corrupt thread still fails closed.
- **MONITORING_DUE**: persisted controlled intent produces a single native event/consumer receipt `FOLLOWUP_REQUESTED_NO_OBSERVATION_OPPORTUNITY_ESTABLISHED`. No fabricated evidence, elapsed opportunity or resolution.

With a uniquely validated investigation, COMPLAINT_ACCEPTED/INCIDENT_LINKED/CASE_OPENED/GRAPH_EVIDENCE_CHANGED/INSPECTION_RESULT_RECORDED/PLAN_APPROVED/PLAN_REJECTED/INTERVENTION_OUTCOME_RECORDED/RECURRENCE_DETECTED/AGENT_RESUME_REQUESTED route to bounded WAKE unless an informational override applies. See machine-readable inventory for exact names. AGENT_TOOL_EXECUTED/PLAN_DRAFTED/PLAN_SUBMITTED/WORK_ORDER_CREATED/WORK_ORDER_STATUS_CHANGED/HYPOTHESIS_ASSESSED/AGENT_DECISION_RECORDED/SOURCE_DOCUMENT_UPDATED/EVENT_DELIVERY_FAILED are informational with durable reason. Unbound/ambiguous case is informational, never guessed. Agent-origin facts are informational. No handler approves plans, creates orders, operates departments or synthesizes findings.

Default model is authored `ReadPause`: one actual approved MCP read of current active incident then pause; explicitly not autonomous LLM reasoning. Tests may inject ScriptedModel in trusted Python construction only. CLI has no live model/provider configuration or reusable paid permit. Existing runtime budgets, source revision checks, schema/evidence validation, same-thread fresh-read barrier and B14-R2 recurrence proofs remain authoritative.

## Consistency, retries and recovery

At-least-once delivery and idempotent consumers; **not exactly-once**, no source/Saver cross-graph transaction. Source writes use existing Redis writer lease, repository owner/epoch/revision CAS and single parameterized graph mutation. A <=4-event compatible case batch is claimed atomically with a random owner token, expiry and monotonic attempts. Competing owners cannot claim that active case. Agent execution holds existing thread ownership, not the source writer lock. Delivery heartbeat renews every10seconds to60seconds; existing agent heartbeat retains independent90second ownership. Source/receipt transitions validate claim token and lease. SIGINT/SIGTERM requests bounded shutdown after current handler, before next poll.

PENDING→CLAIMED→RUNNING→DONE. Expired **CLAIMED** may be reclaimed (no dispatch began). Expired **RUNNING** must reconcile exact coalesced batch key with durable consumer receipt or host `B15_DELIVERY_CONSUMED` in an integrity-validated, non-recovery public Saver checkpoint under original thread ownership. No redispatch to obtain that proof. No proof, malformed checkpoint, existing quarantine, lost ownership or uncertain transport/write→RECOVERY_REQUIRED; case remains blocked. Checkpoint/plan recovery/dependency-unavailable pauses cannot emit completion markers. Fresh markers are appended only to new safe checkpoints; old checkpoint bytes are not rewritten.

Only an established pre-dispatch unavailable failure is retryable: delays1,2,4seconds at initial ceiling3. Explicit operator replay of FAILED with valid envelope can raise total ceiling to<=8 without resetting attempts/history; invalid records and RECOVERY_REQUIRED cannot replay this way. Unknown write outcomes preserve last durable state; the existing repository pending intent and agent quarantine require operator reconciliation. A failed checkpoint cannot guarantee a new durable feedback record. No exception text/source/provider body is emitted by CLI failure output.

**Operator recovery:** stop old worker and investigate its exact graph/event IDs, case key, batch key, owner, original thread/checkpoint and source repository pending intent. `inspect` shows bounded status/attempt/history/receipt; `reconcile CASE_KEY` only checks existing proof and acknowledges it. It does not rerun, redraft, reset counters, clear quarantine or fabricate completion. If quarantined, use the already accepted manual checkpoint reconciliation procedure; leave the graph/quarantine intact until integrity is independently established. Missing proof stays recovery-required. This package adds no automatic repair command.

## Public event replay

`Delivery.public(after=0,limit=50)` returns <=100 redacted committed events, next_cursor and has_more. Cursor is an atomic source-local registration sequence, **not** domain event ID or attempt number. Order is registration cursor, original occurred_at and aggregate revision retained; late discovered events therefore do not disappear behind a time cursor. Read/reconnect is independent of delivery status and does not mutate data. Invalid events have an inspectable failure record but no unvalidated public projection. Source/identity/case references, schema version and allowlisted compact metadata only; no raw payload, private reasoning, provider bodies, tokens or authorization capabilities. Existing500-record scan limit is explicit/fail-closed. HTTP/SSE belongs to B16+, not implemented here.

## Reproduce tests and local demonstration

Run from repository root; `.env` and private profiles stay local/ignored. All ordinary tests/children activate the existing Gemini/countTokens interlock.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b15-unit.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_events.py -q --tb=short
CIVICLY_TEST_REQUEST_LOG=/tmp/b15-db.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_event_delivery.py -q --tb=short
CIVICLY_TEST_REQUEST_LOG=/tmp/b15-runtime.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_event_runtime.py -q --tb=short
CIVICLY_TEST_REQUEST_LOG=/tmp/b15-legacy.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_agent_safety.py::test_concurrent_lease_denial_and_corrupt_checkpoint -q --tb=short
backend/.venv/bin/python scripts/validate_blueprint.py
backend/.venv/bin/python scripts/validate_handoff.py
```

Choose an explicitly approved existing private profile with0005 READY and a paused investigation; shell examples use `PROFILE` and `INVESTIGATION` placeholders, never credential strings. `PYTHONPATH=backend` enables root module invocation. Controlled `--at` accepts canonical UTC timestamps; use nondecreasing simulated time.

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.events --profile "$PROFILE" activate --operator demo-operator --reason 'B15 isolated demonstration only' --authorize
PYTHONPATH=backend backend/.venv/bin/python -m app.events --profile "$PROFILE" resume "$INVESTIGATION" --request-id demo-b15-1 --operator demo-operator --reason 'Explicit deterministic refresh' --authorize
PYTHONPATH=backend backend/.venv/bin/python -m app.events --profile "$PROFILE" run --owner local-b15-1 --batches 10 --poll-seconds 1
PYTHONPATH=backend backend/.venv/bin/python -m app.events --profile "$PROFILE" public --after 0 --limit 10
```

Ctrl-C/SIGTERM requests clean bounded stop; restart the same command/profile under a new owner. Forceful process death after claim is reproduced in `tests.b15_process` (exit71), then deterministic clock advances61seconds; replacement uses same graph/request IDs. Mid-handler death instead requires checkpoint proof/reconciliation and may remain RECOVERY_REQUIRED. Never delete volumes/graphs or clear quarantine to make a demonstration pass. Review exact observed commands/results in docs/evidence/B15-COMMANDS.md and B15-RESULTS.md.
