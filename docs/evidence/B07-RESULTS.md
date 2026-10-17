# B07 complete — await human review

Accepted B06 local baseline24e80725ead2903516ecd36db2142f8fe36b2760. B07 source remains
uncommitted for review; no push, no B07 ZIP. Exact files/purposes in B07-FILES.md;
source/config/docs diff B07-changes.patch. Generated evidence bodies are inventoried
separately and excluded from that source patch.

## Security prerequisite

Actual exposed named-reader credential invalidated before integration; old AUTH
DENIED, replacement PING/authorized RO read PASS. Active named-user connections
revoked; same readonly graph scope retained; replacement atomically stored0600 in
ignored.runtime. No value/hash logged. B07-credential-rotation.json is sanitized
observed evidence. Volatile ACL reprovisioned from replacement after DB recreation.
The reported unsafe full-folder archive is external/not inspected or declared safe;
Git-ignore never implied its contents excluded private files. No B07 archive created.

## Real runtime inventory and examples

Official Python MCP SDK/types2.3.0, Python3.12.1; actual custom server
civicly-domain1.0.0 initialized protocol2025-11-25 over private stdio. Pinned official
FalkorDB MCP1.3.0/Node24.21.0/npm12.2.0 and FalkorDB6.0.2 remain unchanged; no new
package installs/pin changes. Actual initialize and tools/list response schemas
recorded in B07-runtime-proof.json, then actual tools/call/results/read-back traces.

12 declared READ handlers:
find_related_incidents, trace_infrastructure_dependencies, get_maintenance_history,
retrieve_external_evidence, retrieve_case_memory, get_organizational_procedures,
get_work_order_status, get_pickup_execution_history, get_road_condition_history,
get_source_document_excerpt, get_monitoring_status, get_decision_evidence_path.

Seven adapters perform existing graph reads (including absent order/decision lookups).
Five return explicit capability/source gaps (external association, memory, GraphRAG,
versioned documents, monitoring). Operator proof has5 PARTIAL fact responses and7
UNAVAILABLE responses, never fake provider success; no handler ERROR. Six declared
future writes remain unregistered/denied. All18 names/permissions preserved.

Namespaced broker offers12 civicly:: tools +4 official:: tools (dedicated readonly
query and3 schema tools). Actual official server still advertises7; general query,
delete and list_graphs remain denied. Wire schemas/identity/outputs checked, arbitrary
Cypher/graphs/roles/context/extra fields refused; source native account cannot mutate,
trace account cannot access city. Same-user administrative access remains privileged;
stdio is local process ownership boundary, not B13 authentication or an OS sandbox.

Examples from actual calls:
- trace_infrastructure_dependencies asset DRAIN-D12/max_hops4/default verified-only:
  PARTIAL,0 paths with bounded/missing-proof reservations. Explicit candidates:
  DRAIN-D12→DRAIN-D18, CANDIDATE.42 city drainage links remain CANDIDATE.
- network=TYPED_DEPENDENCIES,DOWNSTREAM,include_candidates=true: WASTE-W03→ROUTE-C03
  via COLLECTED_BY; PIPE-P02→ROAD-R08 via UNDERLIES. Both CANDIDATE; uses B05, no new
  physical connection or reverse approximation. Reverse/BOTH typed mode rejected.
- get_maintenance_history ROAD-R08 returns recorded inspection context, retaining
  missing repair/order/decision-chain gap. Pickup/road histories return typed dated
  records with provenance; no schedule-clock reinterpretation or inferred resolution.

B03/B05 algorithms remain authoritative; validated snapshot source revision2104 where
available, null for failed/absent-record snapshots. Bounded/truncated flags and evidence
qualifications retained. Source/evaluator/doc files and delayed payloads inaccessible.

## Shared contracts and persistent traces

Custom mcp_tools schema3/mcp_envelopes synchronizes context/scope, result/error,
source/proof references/revision, server/tool/schema/inventory identity, execution/
parent IDs, argument/output hash/validation and latency. Canonical simulation_mode;
AgentTraceEvent metadata compatible with both namespaces/null non-tool names. No API,
SSE or model-selected rationale implemented; rationale null/operator origin explicit.

Separate B07 trace graph, unchanged normative ToolExecution core +same-ID sanitized
internal detail. Compatible storage-family0002 adjunct/own ledger;0001/registryv3
immutable. Actual2 added index groups/4 unique+mandatory constraints OPERATIONAL;
trace totals93 index groups/186 constraints. TraceStore uses existing fenced atomic
intent/revision/audit commit, idempotent identical ID and conflicting-ID refusal,
core/detail/hash/read-back verification; no automatic Redis retry or mutation tool.

Server trace persists before reply. Broker validates and checks persisted output hash,
then appends a distinct child observation. SERVER status/error is domain outcome;
BROKER SUCCESS is validated receipt, not provider/agent success. Corruption cannot
rewrite server history. Write outage prevents acknowledged success. No cross-graph
transaction/exactly-once domain-event or guaranteed outage replay claim (B15 deferred).

Fresh post-recreation verification preserved all13 pre-final proof trace records
exactly. Final actual proof read back15 server observations, including typed examples;
482 total ToolExecution records observed after proof (test/operator/error observations,
not agent runs). Native readiness in B07-trace-schema-status.json.

## Exact tests and retained evidence

Final complete426 PASS/0 FAIL/0 SKIP in350.75s =288 unit/138 actual integration.
B07 adds33 unit+32 real custom MCP/database cases; all original361 tests unchanged.
Both SPEC validators PASS (STATIC only). Mocked/structural unit tests separate from
actual transports/queries and explicit AFTER-REAL-READ local corruption injection.

Real tests cover all12 callbacks/discovery, valid/invalid input, provenance/revision,
verified/candidate/time bounds, graph/role/write/admin/namespace denial, missing data,
server unavailability/kill/restart/SIGSTOP timeout/reconnect/cleanup, corruption,
trace durability/idempotence/conflict/write failure,0002 operational rerun/checksum,
failed constraint preserving records and partial-migration recovery. Original official
MCP and actual container restart/recreation/Browser storage tests remain passing.

After lifecycle:all2104 source city record hashes/content/revision/audit/writer state,
original B01 probe and retained B05 source57/clone59 unchanged. Canonical0001 READY,
91 index groups/182 constraints OPERATIONAL. No source data/volume reset.
94 protected original files/pins preserved; all18 tool names/permissions retained.
Actual local reader/writer/Browser secrets absent from Git candidate files/logs;
no leaked official/custom process. No claim an external unsafe archive was sanitized.

Interim/failed attempts retained in test_log:initial proof transport PASS masked a
maintenance ERROR from duplicate evidence IDs; strict schema exposed it, fixed and
proof now refuses any handler ERROR. Intermediate423/425 complete passes retained;
final426 rerun follows typed-network/trace metadata refinements. Expected trace ACL
fault emits NoPermissionError stderr and passes explicit fail-closed assertion.
No fake output substituted for unavailable data or failed verification.

## Limits and next boundary

No active B07 acceptance blocker. Later memory/GraphRAG/versioned-source/monitoring
capabilities intentionally UNAVAILABLE; absent order/decision history not fabricated.
55 unlinked measurements/S07/source-binding/clock/history issues remain at designated
milestones. Original55 numeric defects frozen; B04 explicit conversion still valid.

Client timeout does not guarantee thread/DB cancellation; result size cap after
receipt, no streaming-memory/SLA claim. Trace audit grows O(N), cap10k; later reviewed
archival required, no untested shortcut. Privileged raw writes bypass app revisions.
Trace failure fails closed; not B15 event delivery. Shared MCP/trace DEC-004 portion
resolved; remaining source/document/approval/event/API/evaluator findings OPEN.

Proposed B08 only after human review:complaint normalization/same-event deduplication,
Incident-vs-ProblemCluster recurrence grouping and3 issue validators. No B08+ work
started, no live agent/GraphRAG/operations/API/frontend capability claimed complete.

Reproduce configure +proof to /tmp and make test-civicly-mcp; full exact commands in
B07-COMMANDS.md. If failing share sanitized output/blockers.md, never.env/.runtime.
STOP — await human review before B08. All18 requirements remain mandatory.
