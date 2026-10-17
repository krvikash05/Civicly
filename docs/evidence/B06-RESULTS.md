# B06 completed — await human review

B05 externally accepted; local baseline6550d31108c34db6bb0bd5c111c7a41d09953125.
B06 changes remain uncommitted for review. No push; no separate B06 ZIP generated.
Exact paths/purposes: B06-FILES.md. Source/docs diff: B06-changes.patch (excludes
new generated evidence bodies, which are individually inventoried).

## Actual versions and boundary

Python3.12.1; official Node @falkordb/mcpserver1.3.0; Node24.21.0/npm12.2.0;
Python MCP/mcp-types2.3.0; Node FalkorDB client6.8.0/TS MCP SDK1.32.1. All original
Python direct pins and FalkorDB6.0.2 image/registryv3/immutable0001 unchanged.
Locked transitive versions/integrity hashes: B06-versions.json/uv.lock/package-lock.json.

Transport: official private stdio child, no TCP listener/API key. Local process/pipe
ownership is transport boundary. Dedicated DB ACL exact accepted B04 city key with
PING/INFO/GRAPH.RO_QUERY/CLIENT SETINFO only. INFO is an observed driver requirement,
not an assumed grant. Credentials remain ignored0600 in0700.runtime; never logged.
HTTP bearer authentication NOT APPLICABLE/unverified. No OS sandbox or enterprise
RBAC claim. Volatile ACL must be reprovisioned after database lifecycle.

## Inventory and observed data

Actual tools/list discovers7 names and exact observed schema hashes:
query_graph, query_graph_readonly, list_graphs, delete_graph, get_graph_schema,
get_node_schema, get_relationship_schema. Broker exposes only4: dedicated readonly
query +3 schema tools. Deny general query/delete/list_graphs and all other names,
other graph keys, extra arguments/arbitrary Cypher/internal labels. DB separately
blocks write/admin/list commands and other graph keys; official strict mode enabled.

Actual initialize protocol2025-11-25; real tools/call schema/node/edge results in
B06-runtime-proof.json. DRAIN-D12 and D12→D18 CANDIDATE, stable IDs/source/date metadata,
actual application revision2104. Independent official Python-client reads equal.
All42 city DRAINS_TO remain CANDIDATE. No invented physical evidence or agent choice.

Recorded sanitized example (final proof):falkordb1.3.0/query_graph_readonly,
SUCCESS, validated_rows1, revision2104, latency5.389ms,
argument SHA256 ac0d2ffc71d68bd5318b85672673f2e3c65ca45e81bc053b9566f38f9361c1a7;
actual UTC start/end and schema/inventory hashes present; selection_rationale=null.
This is an operator-requested MCP call, not an agent decision. Broader graph-backed
ToolExecution/common custom envelopes remain B07/B17 obligations.

## Tests and retained evidence

- Accepted baseline309 PASS/0 FAIL/0 SKIP in261.78s; both SPEC validators PASS.
- B06 adds37 unit tests +15 actual DB/MCP integration cases. Malformed outputs and
 revision faults labeled mocked units; one local corruption AFTER actual MCP read
 explicitly labeled integration fault injection, not an upstream response defect.
- Final full suite361 PASS/0 FAIL/0 SKIP in329.97s:255 unit/106 real integration.
 All original309 source tests retained unchanged. Both SPEC validators PASS (static).
- Actual CREATE/SET/DELETE RO refusal; strict-mode query/write/delete denial; graph/
 tool/schema/argument/list/admin/key denial; missing/wrong DB auth; parameter injection;
 process kill/restart, SIGSTOP timeout/recovery, session cleanup/budgets/serialization
 and equivalent fractional-UTC boundary PASS. No mock substitutes for live success.
- Same-container restart + different-container recreation with retained volumes,
 Browser HTTP200/storage and fresh graph MATCH PASS. Post-lifecycle configure/proof
 PASS. City858nodes/1246edges, content hash/revision/audit/writer state exactly retained;
 B05 source57/clone59 and original B01 probe unchanged. Canonical0001 READY with
 91 index groups/182 OPERATIONAL constraints; no domain seed/delete/volume reset.
-86 protected original app/test/contract/ingestion files unchanged; original pins/B05
 ZIP hash retained; actual-local-secret/excluded-path/process audit PASS. Final
 audit report: B06-source-audit.json. Compile/pip check/npm ci/whitespace PASS.

Failed attempts preserved in test_log: first authenticated startup TIMEOUT (INFO
missing, fixed); first ACL Python probe INFO denial (raw Redis probe used); retained
verification harness TypeError (explicit graph argument fixed); sandbox ps denied
(audit rerun with authorized process inspection). Intermediate passing test logs
retained. None represented as final success without rerun.

## Limits and exact next gate

No active B06 acceptance blocker. Client timeout does not prove DB query cancellation;
official query signature lacks timeout. Fixed templates/schema caps/call budget remain;
result-byte cap is after receipt. Snapshot revisions assume repository-mediated writes;
privileged raw local writes remain outside that guarantee. Schema samples/current
node lookups/one-hop raw edges do not replace B05 decision-grade temporal/evidence
analysis. No persisted trace/agent/model rationale or product-complete claim.

DEC-004 and B04/B05 data/performance/history/source/evaluator gaps remain OPEN at their
designated tasks. Numeric55 original defects frozen as evidence; B04 explicit
conversion remains valid, separate from55 unlinked-observation provenance gaps.

Proposed B07 ONLY after human acceptance: custom Civicly Python MCP for implemented
read capabilities, typed discovery/calls through shared graph/domain services,
common envelope and trace-contract synchronization, real transport/provenance/invalid
argument/timeout/permission tests. No B08 complaint ingestion, B10 agents, B11 GraphRAG,
operations, API or frontend work authorized here. All18 requirements remain binding.

Reproduce: make mcp-proof; make test-mcp. Exact full commands/observed failures in
B06-COMMANDS.md. Runtime architecture/auth/limits/import flow in backend/MCP.md/flow.md.
If failing, share sanitized output and blockers.md, never.env/.runtime keys.
STOP — human review required before B07.
