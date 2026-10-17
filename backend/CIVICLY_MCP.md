# B07 Civicly domain MCP and shared trace contract

B06 accepted. B07 implements only12 declared READ handlers and controlled trace
persistence. No6 write tools, complaint ingestion/recurrence engine, LLM agents,
GraphRAG, operations, API or frontend. All18 requirements and later gates remain.

## Reproduction and credentials

From repository root with existing Python3.12/Node24 and retained FalkorDB6.0.2:

```sh
make up
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly proof --output /tmp/civicly-b07-proof.json
backend/.venv/bin/python -m pytest backend/tests/unit/test_civicly_mcp_contracts.py backend/tests/integration/test_civicly_mcp.py -v -s
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence
make test-spec
```

The security incident prerequisite ran `PYTHONPATH=backend backend/.venv/bin/python
scripts/rotate_b07_mcp.py`: reset named MCP user to one replacement password hash,
revoked its current connections, atomic0600 credential replacement, verified old
password DENIED and new PING/RO read PASS. Values were never logged. Evidence is
B07-credential-rotation.json. Do not rerun rotation casually; configure reuses the
replacement and reprovisions volatile ACL after DB lifecycle. The archive exposure
was of ignored files: Git exclusions do **not** protect arbitrary full-folder ZIPs.
No B07 archive is produced. Future exports require explicit allowlisting and actual
local-secret/forbidden-path checks; never include.runtime/.env/node_modules/.venv,
volumes, Git internals or ignored backups. Do not redistribute the unsafe old archive.

`configure` is trusted local administration, not an MCP tool. It initializes a new
separate B07 trace graph once and stores its name/generated writer password in ignored
0600.runtime/civicly-mcp.json (0700 directory). Original rotated reader account remains
one exact city graph +PING/INFO/GRAPH.RO_QUERY/CLIENT SETINFO. Dedicated trace writer
can access only its graph and exact repository-lock key, with required graph read/
write/Redis lock commands. It cannot read/write city/canonical/docs/B01/B05 graphs.
No credentials in argv or traces; the server child starts in an empty cwd, explicit
PYTHONPATH, private stdio, no public listener or raw runtime client capability exposed
to model-facing interfaces. Source/writer clients disable automatic retries and use
finite socket/query/pool budgets. Same-user privileged code/default local developer
DB access remains outside the threat boundary; not B13 operator auth or an OS sandbox.

## Actual inventory and implementation

Public broker names `civicly::<name>`; actual custom MCP tool names remain normative
unprefixed names on identity `civicly-domain@1.0.0`. `official::<name>` routes separately
to unchanged official FalkorDB1.3.0/B06 broker. RuntimeBroker exposes16 approved tools:
12 domain +4 official. Neither interface exposes raw Cypher, graph selection, transport,
connection strings, privileged repositories or credentials. Official vendor results
retain B06 typed shape; Civicly results use shared domain envelope. Both routed
namespaces persist shared ToolExecution metadata. Direct legacy B06 tests remain valid.

| Registered READ tool | Actual B07 behavior |
|---|---|
| find_related_incidents | B05 chronological/factor/proof case retrieval; no recurrence classification |
| trace_infrastructure_dependencies | B05 drainage reachability or explicit forward typed DRAINS_TO/UNDERLIES/COLLECTED_BY; VERIFIED default; BOTH only drainage |
| get_maintenance_history | B03 asset-linked inspection/order/outcome context with requested time filtering; missing chains reported |
| get_pickup_execution_history | Fixed bounded PICKUP_FOR read, retained scheduled times/source warnings, no schedule reinterpretation |
| get_road_condition_history | Fixed bounded CONDITION_OF snapshots, typed dated evidence refs |
| get_decision_evidence_path | Direct recorded JUSTIFIED_BY proof only, no invented decisions or inferred transitive causality |
| get_work_order_status | Existing graph status only; absent seed records UNAVAILABLE; no state machine/work execution |
| retrieve_external_evidence | UNAVAILABLE: no source-backed Observation→Location relation/provider;55 unlinked measurements never reassigned |
| retrieve_case_memory | UNAVAILABLE pending B10; no fake checkpoint/episodic memory |
| get_organizational_procedures | UNAVAILABLE pending B11 sourced GraphRAG |
| get_source_document_excerpt | UNAVAILABLE pending B11 versioned source contracts; no filesystem/evaluator access |
| get_monitoring_status | UNAVAILABLE pending B14/B15; no invented monitoring state |

Six future write tools remain normative but unregistered/denied: assessment,
inspection/plan proposals, approval request, work-order creation and outcome recording.
All12 READ callbacks exist with actual strict input/output validation and explicit
results, including unavailable capabilities. This does not claim all18 tools' business
features implemented or all18 product requirements complete.

## Envelope, context and bounded evidence

mcp_tools.json schema3 adds required shared fields without removing tool-specific
payloads:status, trace_id,execution_id,server_id,tool_name,schema_version,inventory_version,
context,graph_revision,source_evidence_ids,simulation_mode,truncated,search_limited,
error,data. `simulation_mode` is canonical; old prose `simulated` alias is retired.
`context` carries trace/execution/parent IDs, correlation investigation_id, fixed
municipality/source graph, trusted host caller role and OPERATOR_REVIEW/APPLICATION
origin. A correlation ID does not claim an Investigation record exists. Broker adds
_context only after validating public arguments; agent-facing schemas omit it. Server
rejects forged graph/role/scope/extra fields. Local OS pipes authenticate process
ownership; caller roles are host context, not a claimed multi-user identity system.

Data includes strict nodes/edges/proof paths, actual UTC as_of, gaps and reservations.
Optional UTC as_of/include_candidates added to READ inputs. IDs bounded/nonblank,
input JSON16KiB, rows100+lookahead,6 hops/120nodes/200edges/100paths; B03/B05 query,
computation and temporal/provenance checks reused. Node history is not reconstructed.
BOTH merges obey shared output caps and remove orphan proof paths. Schema/registry,
node IDs/labels, edge endpoints/directions and response identity are validated again
by broker. Source revision observed before/after, never copied from vendor Graph
version. Raw privileged writes outside repository revisions remain out of guarantee.

Optional network=TYPED_DEPENDENCIES reuses forward B05 dependency analysis for
utility→road and waste→route as well as drains. Reverse/BOTH typed mode is rejected
explicitly; it is not silently approximated. Default DRAINAGE supports both directions.
Legacy paths.asset_ids lists InfrastructureAsset IDs only; typed paths preserve route
endpoints and ordered relation kinds. No new ontology field.

All42 city DRAINS_TO remain CANDIDATE. Verified default returns no qualifying paths
with PARTIAL/bounded-negative reservations; explicit candidate request returns dated
candidate context, never a verified cause. Full absence cannot be inferred from capped
searches. Case ranking remains transparent similarity, not diagnosis. One historical
ROAD-R08 inspection is retrievable; absent repairs/orders/decisions are evidence gaps.
Source warnings, S07/source-binding/history gaps and unlinked55 observations untouched.
No catalog/hidden truth/delayed payload/document filesystem is accessed at runtime.

Server serializes handlers and caps64 calls/session. Domain broker default32 (hard64),
8s timeout (hard10),512KiB result check after receipt, finite database I/O. Client timeout
cannot interrupt a running Python thread/database query; SDK shuts down owned child
with bounded waits. No retry of uncertain calls. Source has no mutation credentials.
UNAVAILABLE/ERROR are validated results, never empty SUCCESS. RPC/discovery/malformed
output failures are explicit broker errors; future agent pause/state handling is B10.

## Graph-backed traces and migration

ToolExecution core schema remains registryv3. Separate storage-family0002 adjunct
`backend/app/graph/migrations/0002_mcp_traces.json` requires exact immutable0001 hash.
It adds2 native node index groups and4 unique/mandatory constraints for internal
CivicMCPTraceDetail and CivicMCPTraceMigration, polling OPERATIONAL. Own checksum/
APPLYING/FAILED/READY ledger is separate from CivicSchemaMigration, so existing0001
readers and repositories remain compatible. It never runs on accepted source city or
canonical graph. Rerun is additive; checksum mismatch rejected before mutation.
Partial/failed migration preserves data and ledger; only explicit reviewed retry of
FAILED constraints may recreate those constraints after data repair. No rollback by
volume deletion or graph reset. Tests remove only graphs minted by that specific test.

TraceStore validates TraceRecord, compiles normative ToolExecution core fields, and
atomically creates core+same-ID sanitized detail JSON/hash via existing fenced
repository intent/revision/audit commit. It verifies durable read-back and core/detail
consistency; same-ID/same-payload repeats match, conflicting repeats reject. No general
trace update/delete MCP tool. Unknown write outcome is not retried: pending state
requires existing explicit reconciliation. Server traces must persist before reply;
broker checks output digest against persisted server record then appends a distinct
child observation. A transport-corrupted result cannot overwrite server history.

Shared mcp_envelopes.json trace fields include actual server/tool/schema/inventory
identity, sanitized argument hash, output hash/validated flag, graph revision/source/
path IDs, UTC start/end/latency, status/error, context and parent execution IDs. Raw
arguments/result bodies/errors/credentials are not persisted. Latency covers execution
up to that observation's persistence, excluding its own DB append. Server protocol
is null when not independently observed; broker records actual negotiated protocol.
Rationale is null, never a fabricated model decision. API AgentTraceEvent is aligned
for later B17 adaptation; no SSE/API persistence projection implemented here.

Trace service failure prevents acknowledged success. This is controlled durable
trace recording, not B15 domain-event outbox/exactly-once delivery. Audit grows with
trace appends (normally server+broker per domain call); existing10k audit cap and O(N)
audit-copy costs remain. Trace graphs need a later reviewed archival strategy; no
untested bypass/retention cleanup. Volumes retain traces across recreation; reprovision
ACL and verify proof execution IDs after restart. Actor auth and model agents remain
later tasks. Broader DEC-004 document/approval/event/API/evaluator findings stay open.

## Review evidence and sources

B07-runtime-proof.json contains actual tool inventory, all12 responses, verified vs
candidate comparison and read-back persisted traces. B07 tests label mocked units and
AFTER-REAL-READ output corruption separately from genuine transport/query success.
Original361 regression tests retained; final results/commands/files/patch under
B07-RESULTS.md/B07-COMMANDS.md/B07-FILES.md/B07-changes.patch. No review ZIP generated.
Official SDK2.3.0 installed low-level Server on_list_tools/on_call_tool, stdio_server,
Client/StdioServerParameters and protocol initialization APIs inspected and exercised:
https://github.com/modelcontextprotocol/python-sdk and https://py.sdk.modelcontextprotocol.io/ .

SERVER trace status/error is the validated domain outcome (including DATA_UNAVAILABLE
or READ_FAILED). BROKER status is the receipt/validation outcome: SUCCESS may accompany
a valid UNAVAILABLE domain response, never a claim the unavailable capability ran.
Their parent IDs distinguish these observations; raw response bodies remain excluded.
For maintenance windows, the records payload satisfies requested from/to; graph paths
retain dated contextual assets/evidence needed to explain those records. Context is
not a claim that every exported node is a matching historical event.

Stable trace server_id official-falkordb maps to verified MCP server name falkordb;
civicly-domain maps directly to its actual server name. The shared contract records
this mapping; schema/inventory hashes and protocol are observed during discovery.

## B07-R history accuracy and compatible corrections

Maintenance records cite evidence from their own validated B03 path prefix. Inspection
prefixes may extend through their own PRODUCED→Evidence link. An order does not inherit
a later outcome's evidence merely because both occur on one path. Response-level
source_evidence_ids remains the aggregate union. No relationship/ontology change.

Pickup history uses scheduled_at (preserving source local-clock warnings); road history
uses observed_at. Both apply inclusive [as_of-days,as_of] and current node/relationship/
source-evidence visibility in GRAPH.RO_QUERY before the result cap. UTC seconds/fractions
normalize via unchanged B03 GraphQueries._time_key; order is time ASC, event ID ASC, then
relationship ID ASC. LIMIT101 supplies one lookahead for100 returned rows. Exactly100
eligible rows alone does not imply truncation. Graph export caps may stop earlier; row
plus Evidence context is admitted atomically, so caps cannot leave missing citations.
A capped search is never evidence of absence. Historical node versions are not rebuilt.

WorkOrder status remains recorded state only. blocking_task_ids/latest_status_event_ids
are unknown empty placeholders until B12–B15 implement operational retrieval. Existing
visible records return PARTIAL and explicit data.gaps; absent records UNAVAILABLE. Server
error/absence handling preserves these capability gaps. No operation or inferred result.

Wire schemas/versions, inventory hash,18 names/permissions and shared envelopes unchanged;
only four result_semantics descriptions in mcp_tools.json clarified. No migration changes.
New tests: tests/unit/test_civicly_mcp_history_projection.py (structural fakes explicitly labeled),
tests/integration/test_civicly_mcp_review.py (actual FalkorDB/SDK stdio/DomainBroker/TraceStore).
The test-only tests.b07r_server harness injects a disposable synthetic source internally
to cover histories absent from city; its evidence is labeled fixture substitution, not
a retained-city snapshot. It does not add a production graph selector, change fixed
Context, credentials, broker or runtime server startup. Fixture setup validates canonical
properties/endpoints then parameterizes bounded test-only CREATE statements; it is not
an ingestion shortcut or repository write-guarantee claim. Real retained-city/official
MCP regressions separately verify the unchanged production path.

Reproduce: python pytest commands in docs/evidence/B07R-COMMANDS.md; corrected outputs,
real failures before correction, complete regression/SPEC evidence, exact file inventory
and B07-R-only patch are in docs/evidence/B07R-*. No B08 work; stop for human review.

## B09 compatibility and future read adapter boundary

B09 services.evidence owns typed investigations/hypotheses/append-only assessments
with source snapshots and inspection requests/reports. No B07 handler, inventory,
namespace, scope, envelope, broker or trace storage changes. Existing maintenance
reads return actual B09 inspections/reports with distinct per-event provenance in
explicitly labeled B09 test-only source substitution; production remains accepted
city. get_decision_evidence_path still needs an actual AgentDecision; B09 does not
fabricate one. No new writes exposed.

Future reviewed read adapters should use EvidenceService.history/inspection/context
and B03 hypothesis_evidence, preserving immutable histories, source hashes/IDs,
as_of/revision, verified/candidate and budget metadata. B10 must review any read-tool
inventory or source-target extension through approved broker interfaces, never expose
repository writes. A separate active-graph integration gate must align B08/B09/MCP/
checkpoint/API to one explicit reviewed working graph. No silent city/canonical/test
switch or canonical promotion. See EVIDENCE.md and contracts/evidence_hypotheses.json.
