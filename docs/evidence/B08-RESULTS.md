# B08 complete — await human review

B07-R accepted. Clean local baseline6afdd09892502a8b47a7f840ced1491c38a002d3;
B08 changes remain uncommitted for review. No push/archive/B09+ work. All18 requirements
remain mandatory; this is a deterministic backend foundation, not full AI application.
Exact files/patch in B08-FILES.md/B08-changes.patch; exact commands B08-COMMANDS.md.

## Architecture and implemented behavior

Five-file app.services.complaints package: strict normalization/unit/report/receipt/
review models; bounded RO context reader; narrow fenced batch writer; intake/preview/
regroup service; exports. Existing official FalkorDB client, registryv3, B03 repository/
policies, B03 histories and B05 topology reused. No dependency or migration change.
New complaint_intake machine contract mirrors schemas/rules. Existing MCP12 READ/
6 deferred writes, official/domain namespaces, envelopes and traces unchanged.

Source first-original/canonical payload/hash stored as bounded UNVERIFIED Evidence
journal. Actual graph stores Complaint→REPORTS→Incident→PART_OF→ProblemCluster plus
OCCURRED_AT/REPORTED AFFECTS. Primary issue assets allow appropriate secondary typed
infrastructure. Known inventory/source conflicts remain warnings, not false verification.

External identity stable across retries; equivalent decimal quantities/units/timezone/
whitespace normalize without overwriting first raw source. Changed actual data/version
conflicts. Independent complaints retain distinct evidence and can share one ongoing
incident; independent event references/disjoint intervals remain separate occurrences.
No complaint-count/proximity rule or work-order-completed resolution inference.

SINGLE_EVENT/PERSISTENT/RECURRENT/CROSS_CATEGORY explain actual incident IDs, times,
explicit assets/clusters, source Evidence dates and bounded paths/uncertainty. Persistence
provisional when termination unrecorded; recurrence requires a dated ENDED record.
Different categories stay separate; candidate links cannot establish verified topology.
Multiple eligible clusters get review alternatives rather than arbitrary assignment.

All three validators preserve supplied measurements/claims, correct units, missing data,
actual inspection/repair/outcome/route/schedule/pickup context and contradictions.
No fabricated rainfall/depth/volume/inspection/repair or root cause. Clock/source/history
warnings and unlinked55 observations preserved;42 city drainage links remain CANDIDATE.

## Atomicity, idempotence and correction

Two commits: durable PREPARED source journal, then single B03 fenced query atomically
creates domain batch/COMMITTED receipt/revision/audit. Actual native failure rolls back
the complete batch; unchanged-prestate pending recovery plus explicit retry resumes.
Lost reply after actual commit replays receipt without duplicates. Application stop
before domain commit leaves a discoverable journal; source/version conflict fails closed.
No B15 domain event/outbox or automatic uncertain-write retry claim.

Reviewed correction requires trusted typed reviewer/reason/CAS hashes, preserves old
PART_OF with closed interval, adds new primary membership and keeps review evidence.
Stale/unknown-start/overlapping assignment refused. This is not B13 authentication.
Replayed receipts are historical; current membership must be read separately.

## Real examples and evidence

B08-runtime-proof.json contains actual independent/ongoing/distinct/persistent/recurrent/
cross-category/disconnected/ambiguous examples, all three validators, missing/conflicting
facts, recovery and actual MCP read of new incidents. MCP source substitution explicitly
TEST ONLY, as in accepted B07-R harness; production city context/authorization unchanged.
B08-city-mcp-proof.json separately exercises actual production source after lifecycle.

Retained authored graph `civicly_b08_test_891b6aa292074c03a93c21451c7206f9`:
5 complaints /4 incidents /2 contextual clusters;26 nodes /23 edges/revision26.
Independent reports share one incident; separate unresolved event shares its pattern;
verified pipe→road context relates separate water/road incidents without asserting cause.
Full actual chain rows/before-after hashes/source requests/receipts in B08-retained-proof.
Five pre-lifecycle retries changed no domain content/revision/audit/counts; writer owner/
epoch changes expected and latest fingerprint used for subsequent lifecycle comparison.
All three issue cases are separately exercised against real controlled fixtures; city
preview is read-only and qualified, not a definitive classification of missing evidence.

## Tests and preservation

Accepted baseline440 PASS in386.74s. Initial27 unit/21 real PASS; strengthened57 PASS,
extra3 real PASS. Equivalent-unit repro1 FAIL in0.25s retained; corrected33 unit PASS,
real equivalent recovery PASS, mixed-asset refinement PASS. Interim full504 PASS in448.77s
retained. Final **507 PASS /0 FAIL /0 SKIP in438.89s**:326 unit/181 real integration;
adds33 unit+34 actual DB/MCP cases, all440 accepted tests unchanged. Both SPEC validators
PASS. Source compilation/whitespace and final patch reverse-application checks PASS.
Both specification validators PASS (STATIC only). Unit checks distinct from real DB/SDK
and explicit real-query interruption/fault injection. No live model/agent test claimed.

Historical audit absence of Archive.zip and raw evidence whitespace handled without
restoring archive or rewriting history. Old tests/source/evidence retained; generated
B07-R fixture proof from full run saved separately then accepted HEAD proof restored.
Fresh source fingerprints/native READY0001/0002/B01/B05 and43 accepted MCP observations
PASS. Production-city initialize/list12/call12/no ERROR/readback15 PASS;1038 total
ToolExecutions observed, not agent runs. Retained B08 exact fingerprint survived restart/
recreation;5 retries no domain changes (only owner/epoch).358 accepted files outside10
intentional documentation changes unchanged; existing app/tests/contracts/data/locks/
migrations/MCP/envelopes protected. Actual local-secret/process audit PASS. No data/volume reset or hidden evaluator access.

## Remaining limits and next boundary

24h/explicit-context matching is heuristic, not perfect event identity. Missing end,
resolution/source binding or physical proof can require review. Finite matching scans
fail closed; context paths/details capped, receipt journal64KiB, source32KiB. No historical
node reconstruction, load/SLA/archival guarantee; repository integrity/audit costs remain.
Canonical seed promotion not done; new writes tested on owned B08 graphs, accepted city
read-only. Later runtime working-graph policy must be explicit. Broader DEC-004/auth/
event/document/API/evaluator gaps retain designated tasks; frozen55 defects unchanged.

Proposed B09 only after human review: evidence/hypotheses, immutable assessments,
root-cause verification guards and inspection request/report lifecycle. No B09 started.
STOP after B08; await review.
