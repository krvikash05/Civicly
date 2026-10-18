# B14-R — technically passing, human review pending

Only B14-R.14distinct focused casesPASS(11unit/3real),0unresolvedFAIL/0SKIP;
14unit cases deselected, not skipped. Both specification validatorsPASS once each
after final code/contracts/tests.5pytest/child interlocks0sent/0unexpected Gemini/
countTokens. No B15, live provider, full suite, lifecycle, infrastructure or frontend.
All18requirements preserved; B10 full genuine Gemini acceptance remains OPEN/PARTIAL.

## Root causes and corrections

Waste B14-1 measured elapsed time from evaluation start, allowing actual pickup at
hour25 + window at26 to claim24hours after pickup. B14-2 measures each supplied
window from latest relevant ACTUAL_PICKUPS observed_at for each target. Claimed
hours>=24 and actual elapsed seconds>=claimed hours×3600; final condition follows
window. Insufficient opportunity MONITORING; conflicting totals/conditions explicit
INCONCLUSIVE. Equal repeated aggregate counts not summed or interpreted as vehicle
telemetry; conservatively latest actual timestamp resets observation. All original
coverage, targets, attribution/review, units, chronological and contradiction checks
remain. Unit checks reproduce original false positive and just below/exactly/above
24hour boundary plus multiple-pickup/ambiguous totals.

Original B14-1 implementation retained byte-for-byte as verification_v1.py and
contract metadata under historical_verification. Old outcomes/proofs/checkpoints and
exact old-request historical acknowledgments untouched; new evaluations/signatures
use B14-2. No assertion historical B14-1 success satisfies corrected policy, and no
retroactive outcome rewrite. Old valid fixture corrected to an actual24hour interval;
new explicit historical-policy test preserves the defective one-hour interpretation.

Recurrence previously changed investigation status without adding its new incident
scope. Corrected existing fenced recurrence write atomically adds sourced temporal
INVESTIGATES→new incident to same investigation, preserving original incident/cluster
links and all repair/approval/outcome/assessment/history. Link source is COMMITTED
B08 intake journal, validity begins recurrence recording. Result/event exposes
investigation_id/investigates_relationship_id. Same B08 AFTER_RECORDED_END semantic;
no successor identity or new subsystem. Existing finite3bound incident limit enforced
before write; no silent truncation/unbounded state expansion.

Explicit same-thread resume now validates added links, B08 original/canonical hash,
COMMITTED receipt/classification, cluster/issue/targets, earlier ended episode and
actual reviewed recurrence reports. New closed state projects active incident/asset
IDs and source hashes, records host RECURRENCE_SCOPE_REFRESH; original ended graph
links and old public Saver checkpoint unchanged. Old plan/hypothesis references
remain earlier-episode context, not causal authority for recurrence. No source IDs
silently injected on decode; unbound caller state rejected. Existing revision/hash
refresh and mandatory fresh MCP READ remain. Invalid or legacy ended-only REOPENED
scope fails closed via existing recovery/quarantine; no automatic repair or clear.

## Actual evidence

- B14R-waste.json: real approved work/completion; pickup report + premature follow-up
  remains MONITORING; later reviewed interval verifies B14-2, original premature
  outcome retained. Same-request verification replay unchanged.
- B14R-outcome-WATERLOGGING.json: preserved completion/no-opportunity/verified/history
  assertions plus new incident linked to original investigation; graph/events
  unchanged on exact recurrence replay. Existing B05 memory still returns original
  intervention and outcome. Contains checkpoint_refresh proof.
- Same retained investigation/thread paused before recurrence. Domain write leaves
  checkpoint untouched; new owned explicit resume updates active episode through
  validated refresh. SCRIPTED model READ new incident→READ new report→PAUSE uses
  actual tools/list/tools/call/brokers/FalkorDB/LangGraph/Saver. Two durable MCP
  executions; first context contains active incident/source hashes and READ barrier;
  public SDK ID-specific read confirms original checkpoint unchanged afterward.
- B14R-legacy-resume.json: exactly one accepted ordinary non-recurrence source-change
  workflow still passes real MCP/Saver resume. Its own disposable graph cleanup is
  unchanged. No prior retained graph/evidence deleted or overwritten.

## Tests, failure history and focused rationale

11unit =5new pickup-time +4affected old policy +2explicit MOCK graph-read binding
branches.3real =1new waste +1extended recurrence/MCP/checkpoint +1accepted ordinary
resume. Ordinary-resume case is justified because new refresh helper is called on
all source-revision changes. No full B14/B13/B12/770/313 or all-scenario runs.
Initial real batch1PASS/1test-onlyFAIL31.51s: official node output assertion expected
row.id, actual normative shape row.properties.id. Corrected fixture assertion;
recurrence alone1PASS26.13s. Unit9PASS0.12s + mock2PASS0.38s; accepted real1PASS8.22s.
No failed application runtime left unresolved. Exact commands/raw outputs in
B14R-COMMANDS.md. Actual DB/MCP/Saver distinct from scripted model and mock units.

## Human verification

From project root, optional isolated no-provider reproduction:

```sh
CIVICLY_OPERATIONS_EVIDENCE_PREFIX=B14R CIVICLY_B14R_CHECKPOINT_PROOF=1 CIVICLY_TEST_REQUEST_LOG=/tmp/b14r-human-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_waste_post_pickup_runtime.py 'backend/tests/integration/test_execution_runtime.py::test_actual_three_issue_completion_verification_and_water_recurrence[WATERLOGGING]' -q --tb=short
```

Expect2PASS; creates new isolated graphs and B14R proofs. Inspect B14R-waste.json:
actual pickup time, premature MONITORING, later verification window/evidence B14-2.
In Browser select graph from B14R-outcome-WATERLOGGING.json and run bounded read:

```cypher
MATCH (i:Investigation)-[r:INVESTIGATES]->(n:Incident)
RETURN i.id,i.status,r.id,r.source_evidence_id,n.id,n.status LIMIT 10
```

Expect same REOPENED investigation, original ENDED incident and new REPORTED incident,
sourced new link. checkpoint_refresh shows same thread/new checkpoint, old checkpoint
unchanged, only recurring incident active and actual report read. For failures share
sanitized B14R test log/provider proof, never private .runtime/.env/password/session.

## Remaining limits/operator steps

Explicit handler/resume only; PENDING events require future separately authorized
B15 delivery. Synthetic24hour policy/report-level aggregate pickups, no telemetry or
physical forecasting. Historical pre-B14-R incoherent reopened scopes are preserved
as evidence; missing active link fails closed and needs operator reconciliation of
original recurrence journal/receipt before any separately authorized resume. No bulk
repair/migration/checkpoint rewrite/quarantine clearance performed. Three-incident
bound rejects larger scopes for explicit future design. Prior B12R2 quarantines,
B04 dataset/frozen55legacy defects,42candidate drain links and B10 full genuine
acceptance limitation unchanged. STOP for human B14-R review; B15 not authorized.
