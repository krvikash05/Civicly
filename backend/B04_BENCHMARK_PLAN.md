# B04 ingestion benchmark plan — defined in B03-R, NOT executed

B03-R imports no municipal data and implements no bulk writer/importer. B04 must
first review explicit legacy-to-v3 conversion and all 55 Observation.value_number
corrections. Original sources/hidden evaluation data remain untouched. These are
proposed acceptance targets and workload estimates, not measured B04 performance.

## Current expected costs and limits

Use one official-client connection/repository per import, not a newly constructed
repository per entity (construction verifies real migration catalogs). Repository
writes serialize per graph, advance a fence, inspect pre-state and policies, persist
an intent, commit domain+revision+audit atomically, and retrieve a typed record.
There are at least three graph writes per successful logical mutation (fence,
intent, commit), plus reads, Redis lock commands and AOF fsync-always costs.

- Node lookup uses common-label ID indexing. Cross-type relationship-ID lookup has
  no global edge-label index: MATCH over all relationship types can scan O(E) edges.
  Node-first ordering limits this cost during initial node CREATE; repeat ingestion
  must still account for global edge checks rather than claiming O(1) upserts.
- Every relationship write exports and strictly decodes up to 2,000 same-kind edges
  with endpoint properties. For E_k inserted edges of kind k this repeats O(E_k²)
  aggregate inspection. Duplicate/cardinality scans are O(E_k) per write. Drain/task
  cycle BFS scans that edge list for each visited state; max10,000 states is a
  fail-closed safety cap, not a throughput optimization or fixed edge-exam count.
- HAS_SCHEDULE also reads target schedule definitions (cached only within one check),
  groups affected route/service assignments, and checks interval pairs. Worst case
  O(S²) comparisons, capped at10,000, plus target reads. Schedule service/date edits
  revalidate all affected incoming assignments under the same writer fence.
- repo_audit is a single scalar JSON array: parse the previous n entries, serialize
  n+1, transmit/rewrite the full audit on each commit. Aggregate CPU/transport/AOF
  serialization grows O(N² × mean_entry_bytes), while retained audit is O(N).
  As an illustration only, 2,083 entries averaging300 bytes means ~625KB final JSON
  and ~651MB cumulative JSON serialization. Actual bytes/AOF amplification must be
  measured; this estimate is not observed disk usage. There is a10,000-entry cap.
- The unconverted supplied fixture has838 nodes/1,245 edges (2,083 logical initial
  creates before any conversion additions). These counts are static source counts,
  not an ingestion acceptance result. Count all conversion-added evidence/metadata
  and writes, largest per-kind populations and audit headroom before starting.
- Keep existing1,000ms per-query timeout, socket limits, writer fencing, policy caps
  and uncertain-outcome handling. Long overall ingestion does not justify disabling
  any limit or directly bypassing repository policies.

## Workloads and measurements (B04 only after review)

1. Preflight conversion offline: report invalid/unknown/mandatory fields, IDs,
   provenance, temporal bounds and schedule service names. Resolve the55 defects
   explicitly; do not drop values or invent dates/sources. Exclude evaluator answers.
2. Use a dedicated new_test_graph_name(4) and operational migration0001. Record
   runtime/image/package versions, machine/CPU/RAM, AOF settings and input hash/counts.
   Keep canonical and B01 graphs/volumes untouched. Exclude migration/pull/setup from
   ingestion timing and record their time separately.
3. Pilot a coherent, dependency-ordered subset (about100 nodes and100 relationships),
   including all policy families. Then benchmark the reviewed complete converted
   fixture. Use the same repository guarantees for every write. Start with one writer.
   Do three independent fresh-graph trials, not three imports into the same graph.
4. Record initial wall time, throughput, per-operation p50/p95/p99, query/command
   counts, largest same-kind scan and cycle/schedule comparison counts, lock waits,
   rejected writes, unknown outcomes/recovery attempts, peak Python memory, server
   used memory, audit entry count/JSON bytes at0/25/50/75/100%, and AOF byte growth.
   Record bytes/counts only, never credential or source-text dumps.
5. Repeat identical ingestion twice in each graph: exact stable node/edge IDs,
   properties and provenance must remain unchanged. Proposed B04 importer should
   treat equal records as no-ops; verify no revision/audit increase for those no-ops.
   Any mutation requires existing hash/fence/intent/audit semantics. Changed source
   inputs need explicit update/version rules and a separate measured workload.
6. Include contention (two import attempts), duplicate/global edge IDs, invalid
   endpoints/scope/evidence, primary assignment/schedule conflicts, task/drain cycles,
   injected lost replies and interrupted importer/resume. Verify no partial domain
   structure, no silently lost/duplicated mutation, revision correctness, preserved
   failure evidence and unchanged B01/canonical state. Re-run relevant B03-R tests.

## Proposed acceptance gates and response to slow results

On the recorded reference machine: initially target <=5min for the complete initial
fixture and <=2min per identical repeat, with <=256MiB incremental peak Python memory.
These are provisional demo usability targets, not published performance claims.
Report all three raw trial results and medians, correctness failures separately,
and confirm policy/audit headroom (suggest <=50% of audit cap for the intended demo
lifecycle). A pilot predicts whether the full run fits before spending its budget.

Correctness is mandatory even if timing fails. A slow/over-budget run must produce
a measured bottleneck report and a separately reviewed optimization proposal. A
future batching/identity index/audit-journal migration may be appropriate, but cannot
be assumed equivalent. It needs additive versioning plus real rollback, fence/CAS,
recovery, provenance, rerun and concurrent-conflict tests before adoption. No unchecked
bulk loader, raw CREATE bypass, policy suppression, audit truncation or volume reset
is authorized. Audit archival is a future reviewed design, not implemented here.

B04 scope is conversion/import/provenance/idempotence plus this benchmark. MCP,
agents, GraphRAG, operational workflows, API/frontend and evaluation machinery remain
later gates. B03-R stops at defining this plan.
