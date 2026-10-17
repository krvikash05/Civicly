# B09 evidence, hypotheses and inspections

This is an internal typed domain service on FalkorDB, not an autonomous investigator,
dispatch simulation, public API, authentication system or durable event worker.
All18 objectives remain mandatory. Registryv3 and migration0001 remain unchanged;
no dependencies, MCP inventories, shared envelopes or city source records change.

## Actual interface and storage

`app.services.evidence.EvidenceService(repository, clock=utc_now)` accepts strict
JSON commands through `execute(payload, Actor(...))`. `parse_command` rejects unknown
fields, coercion, arbitrary Cypher, caller graph/scope and direct assessment/status
overrides. Commands: `open`, `propose`, `request_inspection`, `transition_inspection`,
`report_inspection`, `assess`. Read methods: `history(hypothesis_id, as_of)`,
`inspection(inspection_id, as_of)` and `context(incident_id, as_of, exploratory=False)`.
`incomplete()` lists PREPARED journals within its explicit100-journal bound.

Investigation INVESTIGATES actual Incident(s) and their one active ProblemCluster.
Investigation PROPOSES Hypothesis; Hypothesis EXPLAINS incidents and CONCERNS typed
assets. Statement stays readable; cause_code, proposed mechanism, confirming and
falsifying observations are retained in the PROPOSES source operation journal.
Multiple competing hypotheses are separate identities, not overwritten alternatives.

Inspection INSPECTS assets. The request source journal binds investigation,
department and actor; the registry has no direct investigation→inspection relation.
Inspection PRODUCED Evidence ESTABLISHES Finding. Reports have original inspector,
department/source/record identity, source kind, observation times, methods, optional
measured value+unit, explicit UNKNOWN observations and an optional independent
review. Source text stays untrusted data. Requesting never creates observations.
No legacy Observation.value_number fixture edits or guessed geographic binding.

Hypothesis HAS_ASSESSMENT append-only HypothesisAssessment SUPPORTED_BY /
CONTRADICTED_BY Evidence. Its rationale is explicitly serialized typed JSON:
previous assessment ID, mechanism/expectations, evidence and finding hashes,
attribution, exclusions/gaps, actual B05 path IDs/directions/provenance,
source/committed graph revisions, as_of, assessed_at, limits and state transitions.
Earlier assessments remain immutable even when later findings contradict them.
Domain reports/findings are also never edited by this service. Privileged lower-level
mutable writes remain outside that boundary; readers detect source/command/report
binding or finding disagreement and fail closed. Snapshots retain historical hashes.

`contracts/evidence_hypotheses.json` mirrors actual Pydantic schemas and policyv1;
unit tests compare it with implementation. All records use municipality_id=demo-city,
stable IDs and registered endpoints; no new ontology labels/properties/relationships.

## Verification and uncertainty

All five assessment values are used: POSSIBLE, SUPPORTED, CONTRADICTED, VERIFIED,
INCONCLUSIVE. They map explicitly to normative Hypothesis lifecycle states:
POSSIBLE→UNDER_REVIEW, SUPPORTED→SUPPORTED, CONTRADICTED→REJECTED,
VERIFIED→VERIFIED, INCONCLUSIVE→INCONCLUSIVE. A new assessment re-enters UNDER_REVIEW
from the previous state using legal transitions. The transition sequence is retained;
there is no invented persisted POSSIBLE/CONTRADICTED Hypothesis state.

Known cause policies cover water blockage/capacity/pump, road utility leak/subgrade,
waste missed pickup/capacity/dumping. Unknown explanations may be proposed and
supported, but no approved criterion means no automatic VERIFIED result. Known
policies require the appropriate infrastructure subtype. Caller expectations must
include the policy's full confirming and falsifying observation sets.

VERIFIED requires all confirming codes from reviewed, attributable actual reports,
two distinct inspections, inspectors, source IDs and source records, no qualifying
contradiction, and any required verified-only physical dependency path. Utility-leak
explanations require a dependencies path rooted at the concerned WaterPipe and ending at the affected RoadSegment. An optional topology requirement
on any explanation is also enforced. Candidate-inclusive B05 exploration can justify
investigating a proposed connection; it cannot satisfy verified-only assessment.
Path/result truncation prevents verification. This explicit synthetic demonstration
criterion is not a universal engineering diagnosis or proof against colluding authors.
Human review is trusted internal context, never an LLM-generated approval or B13 auth.

Assessment discovery unions explicit input references, previous assessment citations
and actual reports from concerned-asset inspections before scoring. A caller cannot
silently drop known counterevidence. All observations must be relevant to the asset,
after the explained incident start, and visible at as_of. Unreviewed/context evidence
cannot satisfy verification. Support plus contradiction yields INCONCLUSIVE, with
both retained; contradiction alone yields CONTRADICTED. Missing/UNKNOWN reports yield
INCONCLUSIVE. No numerical confidence is invented. A later report may correct the
assessment; it does not erase the prior version or automatically arbitrate conflicting
sources. Reviewed source retraction/arbitration is not implemented by this phase.

Geographic match, complaint counts, candidate drainage, model statements/confidence,
completed work orders and similar historical cases never establish verification.
B05 historical retrieval and verified/exploratory topology are reused, not duplicated.
All42 source-city drainage links remain CANDIDATE. Missing repairs/decisions,
unlinked55 observations, service/local-clock and scenario/source-binding gaps remain.

## Inspection lifecycle and authority

Request creates PROPOSED. Explicit REQUESTED→SCHEDULED→IN_PROGRESS transitions require
CAS; a departmental actor must match the original request department. Scheduling must
follow request; work cannot start before its schedule. A submitted report can complete
only IN_PROGRESS, with observations after the current start update/schedule and no
later than the recording clock. Failed inspections may return to REQUESTED; cancelled
or completed ones are terminal. Reports may be reviewed or unreviewed; UNKNOWN
findings do not become verified observations. Duplicate source records cannot be
repackaged as independent reports. Self-review is refused.

Typed inspection reads distinguish missing/time-unavailable, pending/no report and
completed/actual finding IDs. These are recorded facts, not autonomous field work.
ANALYST/ADMIN can open/propose/assess; an appropriate DEPARTMENT_LEAD/ADMIN submits
reports and scheduling/progress/failure/cancellation. ANALYST can request an inspection.
Typed actor/reviewer objects represent a trusted local boundary; caller-provided roles
are not public authentication. B13 must bind real authenticated identities. B14 owns
actual simulated departmental dispatch/progress/monitoring; B15 owns event delivery.
No work order is created. Existing AUTHORIZED-only creation contract is unchanged.

## Temporal and persistence guarantees

Inputs use canonical ISO UTC Z; comparisons parse fractions at microsecond precision.
Evidence created/updated/observed/recorded after as_of is excluded. Future-updated
inspection versions are unavailable, not guessed historical states. The original
hypothesis definition comes from its validated immutable-by-service proposal source;
history does not mistake current status for a past status. Assessments are recorded
now with a separate evidence cutoff. History orders by assessed_at, graph_revision,
then stable ID, and fails above100 rather than hiding a latest assessment.

Each actor request ID is global across B09 commands; assessment request IDs must also be unique per hypothesis. Changed same-key input conflicts.
Two durable phases: persist an UNVERIFIED PREPARED operation Evidence journal, then
under the unchanged B03 graph lease/fence validate current references, identities,
CAS/state/temporal rules and persisted/batch policies. One parameterized graph query
resolves all existing endpoints before writing approved nodes/edges, updates the
Hypothesis or Inspection, stores COMMITTED receipt, increments revision/audit and
clears the pending intent. Readback verifies actual assessment and evidence paths.
Whole operation is not a multi-query transaction; a rejected/stopped request may
retain PREPARED journal only, explicitly inspectable with incomplete().

Native constraint failure rolls back the single domain statement. Lost replies never
trigger automatic mutation retries. Existing unchanged-prestate recovery aborts the
pending intent; explicit unchanged-request retry re-plans from its original command.
An already committed command returns a verified historical receipt. Later mutable
status is not reset. Stale CAS needs a new reviewed request; inconsistent pre-state
requires operator reconciliation. Never clear records, intents or volumes to pass.
No event-outbox or exactly-once delivery claim. AOF persistence is inherited from B01.

Bounds:32KiB request,128KiB journal;20 evidence references after union;100 relationships
per source-filtered scan/history/journal list;300 metered reads/8s reader/1s per DB
read;12 new nodes/35 edges/one updated entity per batch. B05 retains its own finite
hop/path/query/export budgets. Limits fail closed or carry B05 truncation/search
reservations. ExistingO(E) policy scans, O(N) audit serialization and10k audit ceiling
remain; no bulk shortcut or production performance claim.

## Active graph and future consumers

B09 writes only canonical or validated B09 UUID test targets. Canonical remains
unseeded; retained B04 city, B01 probe, B05 source/clone, B07 traces and B08 proof
graphs are protected. Tests explicitly copy source-preserving records made by genuine
B08 intake into owned B09 graphs and verify hashes/source fingerprints. They preserve
actual B08 Incident/ProblemCluster IDs without changing B08's phase guard. Retained
B09 proof also retains its small original B08 source. Existing-city evaluation is
read-only, bounded and explicitly names that graph.

Later active-graph gate: review canonical seed promotion/working-target policy, then
prove B08 intake→B09 investigation/assessment→MCP→agent checkpoint→API uses one explicit
graph and shared revisions, without silently swapping sources. That gate is not green
merely because isolated foundation tests pass. Production official/domain MCP remain
fixed to accepted city context. B09 fixture MCP substitution is test-only and labeled.

Future approved read adapters can consume history/inspection/context and existing
B03 hypothesis_evidence paths, preserving snapshots, actual IDs, evidence hashes,
revisions/as_of, candidate flags and limits. No new MCP write handler is exposed;
the12 existing READ tools remain unchanged. B10 must use the approved broker and
explicitly review any required read inventory/active-target extension. No LangGraph,
GraphRAG, operational workflows, HTTP API, frontend or evaluator answers used here.

## Reproduce

From project root, retained local Docker/MCP runtime configured:

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_evidence_models.py backend/tests/integration/test_evidence_domain.py -v -s
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence
make test-spec
PYTHONPATH=backend backend/.venv/bin/python -m tests.b09_evidence create --proof /tmp/civicly-b09-proof.json
```

Create retains its new small B08 source/B09 working graph and refuses overwrite.
For supplied proof, run verify, never recreate/reset it. Exact lifecycle commands,
failed attempts, runtime outputs, patch and file inventory are in docs/evidence/B09-*.
STOP after B09; human review is required before B10.

Tests/retained demo use an explicitly injected2026-10-18 synthetic clock; DB operations
are real, observations are authored SYNTHETIC records. Production default is utc_now,
not caller-controlled time. No claim of real municipal inspection or live-agent action.
