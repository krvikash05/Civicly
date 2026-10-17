# B07-R complete — await human review

B07 technically accepted; only B07-R authorized. No B08+ work, push or ZIP. Exact
changed-file inventory B07R-FILES.md, working-tree-baseline patch B07R-changes.patch.
All18 requirements remain binding; read foundations do not complete product features.

## Root causes and corrections

1. Maintenance events inherited response-wide source_evidence_ids. The adapter now
   derives references from each event's own validated B03 prefix/evidence paths;
   inspection paths extend through their own PRODUCED link. WorkOrder prefixes do
   not inherit later outcome evidence. Aggregate source IDs remain response-level.
2. Pickup/road reads applied arbitrary LIMIT101 before Python date filtering. Fixed
   GRAPH.RO_QUERY templates now apply inclusive UTC-normalized window, node/edge/
   referenced-Evidence visibility, chronological time ASC/event ID ASC/edge ID ASC,
   then LIMIT101.100 eligible rows returned with one lookahead; export caps remain.
   Atomic event+Evidence export prevents citations referencing omitted context.
3. Empty blocking_task_ids/latest_status_event_ids implied unjustified operational
   completeness. Result construction now declares them UNKNOWN pending B12–B15 in
   data.gaps; existing status PARTIAL, absent status UNAVAILABLE. SDK error/absence
   handling appends gaps so capability limitations survive. No operations implemented.

Compatible contract adjustment: only four result_semantics descriptions clarified.
Input/output schemas, inventory hash/version,18 names/permissions, shared envelopes,
source graph authorization/namespaces and trace architecture unchanged. No migration,
B03 identity/direction/temporal policy, B04 dataset or B05 algorithm edits.

## Actual corrective outputs

Disposable canonical synthetic source, actual SDK stdio/discovery/DomainBroker and
real graph-backed TraceStore. TEST-ONLY source substitution is explicit in report;
fixed production Context/ACL/startup unchanged. Not represented as retained-city facts.

- INS-A on2026-10-02 cites only EV-INS-A; INS-B on2026-10-03 cites only EV-INS-B.
  Aggregate response cites both. Actual before result cited both on each event.
- Each history contains110 older records,107 relevant records, one future and one
  expired-link record. The returned100 start NEW-000,TIE-A,TIE-B,NEW-001...NEW-097;
  fractions normalize and equal times use stable ID. truncated=true.
- Narrow inclusive window retrieves NEW-103 and NEW-104 despite older rows;
  truncated=false. Exactly100 eligible rows false,101 true, both tool families.
- WO-REVIEW recorded PENDING with PARTIAL, empty placeholders explicitly not verified
  empty relationships; absent order UNAVAILABLE retaining the same limitations.

Full bodies and real execution IDs B07R-runtime-proof.json; pre-correction bodies
B07R-before-outputs.json. Actual retained-city proof separately B07R-city-proof.json.

## Verification

Focused5 pure structural/fake unit PASS in0.51s;9 actual DB/MCP PASS in14.33s.
Final complete **440 PASS /0 FAIL /0 SKIP in368.60s**:293 unit/147 actual integration.
All426 accepted B07 tests unchanged. Both SPEC validators PASS (STATIC only).
Actual official/domain MCP, B03 policies/B05 counterfactuals/B04 importer and real
restart/recreation/Browser volume regressions PASS. Expected trace ACL denial is a
passing fault assertion; no mocked replacement for real acceptance.

Fresh retained-city proof initializes civicly-domain1.0.0/protocol2025-11-25, lists12
actual tools, calls all12 without ERROR and reads back15 server observations. Source
858 nodes/1246 edges, all2104 record fingerprints/revision/audit/writer state, B01 probe,
B05 source/clone, canonical0001 and trace0002 unchanged.13 early B07 +15 final accepted
B07 observations preserved, plus4 before-correction and11 corrected fixture observations
with validated output/evidence hashes across actual restart/recreation.666 total traces
observed after proof; not live agent runs.

Source audit PASS:333 accepted B07 files outside11 intentional edits unchanged;
all18 input/output schemas/permissions and dependency pins preserved. Actual local
secret scan PASS/no MCP process leak. No archive made/external ZIP safety claim.
Both static specification validators PASS. No live model/agent or operational claims.

Failure history retained:4 fixture setup ERROR (valid_to without valid_from), fixed
before meaningful reproduction;4 actual product FAIL in9.18s before corrections;
first full collection1 ERROR from new duplicate module basenames, fixed by renaming
only the new unit file. Old tests preserved; no fake success or weakened validation.

## Remaining limits and B08 boundary

No operational blocking/latest-event implementation until B12–B15. Bounded queries
cannot establish global absence or rebuild historical node versions. Pickup clock/
service warnings retained; missing historical chains not fabricated.42 drainage
links CANDIDATE; source/evaluator/history/55 unlinked measurements/remaining DEC-004
findings remain designated later tasks. Original55 numeric defects and explicit B04
conversion unchanged. Existing timeout cancellation, local privilege and O(N)/10k
trace audit limits remain. No new dependency/version or ontology changes.

Proposed B08 ONLY after review: complaint normalization/same-event dedup, Incident
versus ProblemCluster recurrence grouping and validators for all three issue categories.
No agents/GraphRAG/operations/API/frontend in this pass. STOP for human review.
