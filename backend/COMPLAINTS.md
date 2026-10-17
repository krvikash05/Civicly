# B08 complaint intelligence — trusted domain service

B07-R accepted at local baseline `6afdd09892502a8b47a7f840ced1491c38a002d3`.
All18 requirements remain mandatory. This implements deterministic intake/grouping,
not B09 evidence verification, agents, operations, events, API or frontend.

## Interface and graph ownership

```python
from app.services.complaints import ComplaintService, Review
service = ComplaintService(repository)  # existing GraphRepository, real UTC default
receipt = service.intake(payload)
proposal = service.preview(payload)    # read-only, proposed IDs explicitly preview=True
pending_journal_ids = service.incomplete()
```

Writes require `civicly_knowledge` or validated B08 test graphs, protecting retained
B01/B04/B05/B07 evidence. Repository constructor still uses the unchanged shared
canonical/test-target guard and operational0001. Tests operate isolated B08 graphs;
accepted city is exercised through read-only previews. No canonical seed promotion or
city mutation. Future phases may explicitly authorize their own working graph policy.
No new migration, node type, relationship, native constraint, dependency or MCP tool.

`contracts/complaint_intake.json` mirrors actual strict Pydantic input/result/reviewer
schemas and declares units/rules/budgets. Requests include issue_type, description,
source_id/external_record_id/channel/kind/version, reported_at/occurred_at, existing
location_id and optional end, explicit assets/evidence/event reference/issue details.
No free Cypher, graph/municipality selection or arbitrary node properties accepted.
Location is an existing canonical Location ID; this is not a geocoding service.
Explicit road/waste assets require at least one appropriate road/collection-point;
secondary infrastructure is allowed under the existing AFFECTS ontology. Location-only
reports remain accepted with explicit uncertainty.

IDs use case-sensitive NFKC+trim; descriptions collapse whitespace; timestamps must
have an explicit timezone and normalize to UTC. Numeric strings/bools/nonfinite/
negative values, unknown properties and incompatible units are rejected. Supported
decimal conversions also canonicalize retry identity and preserve original values/units; no quantities extracted from prose.
Raw first submission and canonical payload are retained. Measurements labeled OBSERVED
by a submitter still remain REPORTED/UNVERIFIED until later verification. Source text
is untrusted data, never instructions. No realistic citizen PII in demo fixtures.

## Reports, occurrences and patterns

Complaint.status RECEIVED acknowledges intake (open string vocabulary; imported
ACCEPTED statuses untouched). Incident starts at normative REPORTED; cluster OPEN.
`Complaint → REPORTS → Incident → PART_OF → ProblemCluster`, plus OCCURRED_AT and
REPORTED AFFECTS. Association validity starts when recorded, not a guessed physical
impact start; claimed occurrence/end times remain separately on Incident/source journal.

External identity hashes municipality/source_kind/source_id/external_record_id.
Channel/version are payload, not new identities: changed same-key data/version raises
Conflict; first original stays intact. Different independent complaints retain separate
source evidence. No free-text similarity or complaint-count threshold declares recurrence.

Same incident requires category/subtype/exact location/explicit asset set, overlapping
claimed intervals, compatible attributed event reference and <=24h start gap unless
that reference matches. With no asset, an explicit matching source event reference is
required. These are transparent heuristics, not perfect event identity; unknown independent
occurrences can require reviewed correction. Multiple compatible incidents are not
arbitrarily merged. Twenty reports alone never imply20 incidents or recurrence.

- SINGLE_EVENT: one reported occurrence without demonstrated prolonged duration.
- PERSISTENT: reported prolonged duration or related distinct occurrences with no
  qualifying recorded termination. Provisional context; unrecorded resolution remains possible.
- RECURRENT: distinct occurrence after an explicitly dated ENDED incident. Missing
  end dates remain indeterminate. This is recurrence after recorded end, not proof
  of root-cause resolution. Completed orders/outcomes alone cannot end an incident.
- CROSS_CATEGORY: separate category incidents share an explicitly reported asset or
  actual verified B05 dependency context. Connections are not proof of causation.

B05 forward dependencies/upstream drainage are reused; incoming utility lookup only
selects roots for the same forward algorithm, preserving actual edge direction.
Candidate links/proximity do not establish physical grouping. Same coordinates with
disconnected infrastructure remain separate. Multiple eligible clusters produce a
separate primary cluster with review alternatives, not an arbitrary reassignment.

Receipts contain stable IDs, actual graph/revision/as_of, typed history summaries,
dated Evidence references, graph paths, compared values/explanations/uncertainty and
explicit search/truncation flags. Path context preserves stable path_id where available.
Future MCP/agent/frontend consumers can resolve graph IDs; this is not an HTTP DTO or
implemented agent. Existing ComplaintDTO can later derive issue_type through REPORTS.

## Three validators and evidence gaps

Water: occurrence/location, depth/duration/rainfall/capacity units and attribution;
station/interval gaps; blockage claims and candidate drainage qualification.
Road: distress/measurements, actual B03 inspection/repair/outcome context, suspected
water/drain/pipe causes remain claims. Missing historical chains stay visible.
Waste: quantity/unit/ambiguous prose, actual route/schedule/pickup states and dated
records; completed logs can contradict missed-pickup claims without proving which
source is correct. Local-clock/service aliases remain warnings; no schedule parsing
or dumping diagnosis. Conflicting same-time measurements are retained, not averaged.

Histories are source context as_of intake time, not a reconstruction of prior node
versions or proof an asset-linked repair resolved a specific incident. City42 drainage
links remain CANDIDATE; unlinked55 observations and source-binding/history gaps are
not repaired or reassigned. No hidden scenario/evaluator/delayed payload read.

## Atomicity, retry and recovery

1. Public B03 repository persists an UNVERIFIED Evidence COMPLAINT_INTAKE journal:
   bounded validated JSON summary with original/canonical input/hash and PREPARED state.
2. Under a new graph lease/fence, read actual matching state; validate registry,
   existing and within-batch identities/endpoints/temporal cardinality/evidence.
3. One `_commit` query resolves all existing endpoints before writes, creates the
   complaint/optional incident/cluster +relationships, updates cluster pattern and
   COMMITTED journal receipt, then revision/audit/pending metadata atomically.
4. Strict readback checks actual path endpoints/evidence before acknowledgment.

Journal preparation is a separate commit; whole intake is not a multi-query transaction.
Normally two revision/audit commits; one domain batch can contain multiple records.
A crash before step3 leaves PREPARED and no partial chain. Actual constraint failure
rolls back that single statement. Existing unchanged-prestate recovery aborts pending
intent under the fence; explicit same-canonical-payload retry re-plans against current graph from the first stored original.
Lost reply after real commit returns OutcomeUnknown; retry reads COMMITTED receipt
without duplicate data. No Redis automatic mutation retry or cross-graph transaction.
Uncertain/inconsistent pre-state fails closed for operator reconciliation.

`incomplete()` lists PREPARED own-type journals within a100-journal scan; exceeding
that bound fails explicitly rather than returning a false empty list. Inspect journal
original and call intake again for unchanged INTAKE. Changed external-key payloads
need explicit reviewed versioning, not overwrite. Stale REGROUP requires a new review
request/hash; old prepared evidence remains historical. Never clear intents/delete
nodes/volumes to force a retry. A receipt-size/budget failure can leave PREPARED for
review. No durable domain event/outbox/worker/replay implemented; B15 remains required.

Replay returns a verified **historical intake receipt**, not current membership after
reviewed correction. It may advance writer owner/epoch; domain revision/audit/counts do
not change. For a current binding, read the graph at current as_of.

## Reviewed correction and limits

`regroup(Review(...))` is a trusted internal operator interface requiring explicit
review, reviewer/role/reason and expected incident/membership/target hashes. It is
not B13 authentication and is unavailable through MCP. One fenced query closes the
known old PART_OF interval and creates its replacement, updates patterns and stores
review evidence/receipt. Old edge and audit remain. Unknown old validity start,
empty interval, stale hashes and overlapping primary assignment are refused.
Cluster lifecycle state is not automatically changed; empty historical clusters retained.

Matching caps100 incidents/400 context edges/200 source journals,9 dependency roots,
4 infrastructure hops,96 metered reads/8s context/1s individual query; fail closed on
incomplete matching exports. Result paths100, detailed related explanations20 and
journal64KiB/input32KiB. Finite strict readback can add per-path node/edge fetches.
Integrity scans/audit serialization remain O(E)/O(N) per operation; normally two writes
per intake. No bulk shortcut, archival or load/SLA claim. Later reviewed optimization
must preserve all write guarantees and frozen source data.

## Reproduce and review

From project root with retained local runtime:

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_complaint_models.py backend/tests/integration/test_complaint_intelligence.py -v -s
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence
make test-spec
PYTHONPATH=backend backend/.venv/bin/python -m tests.b08_evidence create --proof /tmp/civicly-b08-proof.json
```

Create refuses overwrite and retains only its own new B08 graph; no reset/delete.
See docs/evidence/B08-COMMANDS.md for exact before/after lifecycle proof commands,
operator Browser MATCH, source audit and failed-attempt history. Controlled fixture
MCP uses explicitly labeled test-only source substitution (same accepted B07-R pattern),
actual SDK/server/broker/trace persistence; production source/context/namespaces unchanged.
All previous tests retained. No B08 ZIP. STOP for human review before B09.

Final B08 gate:507 PASS/0 FAIL/0 SKIP in438.89s (326unit/181real), both SPEC validators
PASS. Retained B08 journals/chains and5 retries, original city/B01/B05/native migrations
and43 accepted trace observations verified after actual restart/recreation. Production
city MCP all12 reads/no ERROR +15 trace readbacks PASS. Existing B05 case-retrieval
reservation about recurrence is operation-local: that reader ranks candidates, while
B08 receipts own classification. No old algorithm or MCP contract changed.
