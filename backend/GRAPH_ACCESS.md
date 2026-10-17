# B03 typed graph access

This is a trusted internal graph adapter, not a public query endpoint or a complete
Civicly investigation engine. All 18 requirements remain in force. Registry v3
and migration 0001 are unchanged. B04 conversion/import is not implemented.

## Entry points and imports

`app.graph.repository.GraphRepository(client, graph_name='civicly_knowledge')`
uses the official FalkorDB client from `app.graph.connection.connect(Settings())`,
which disables automatic transport retries for uncertain mutations.
Construction checks actual migration/catalog readiness. Schema/repository tests may target only
`civicly_bNN_test_<lowercase RFC4122 UUIDv4 hex>` for NN02–25.
Both constructors use app.graph.targets; new_test_graph_name(NN) generates names.
B00/B01, arbitrary production graphs, documents/checkpoints and malformed names are
refused before client access. This internal naming guard is not database RBAC. No B01 graph is a repository target.

- `create_node(kind, properties)`, `get_node(id, expected_kind=None)` and
  `update_node(id, changes, expected_hash=record.content_hash)` return `NodeRecord`.
- `create_relationship(kind, source_id, target_id, properties,
  inspected_cycle_evidence_id=None)`, `get_relationship(id)` and
  `update_relationship(id, changes, expected_hash=record.content_hash, ...)`
  return `EdgeRecord`. Endpoints/type/identity cannot change during updates.
- `recover_pending()` reconciles an unchanged pre-state under the writer fence;
  inconsistent state raises `OutcomeUnknown` and preserves the intent.
- `GraphQueries(repository, ReadLimits(...)).run(QueryRequest(...))` returns
  `GraphResult`. There is no raw Cypher argument or caller-controlled scope.

Imports: `queries -> models + repository -> migration + schema`; `models -> schema`;
`migration + repository -> targets` (one shared target guard).
The immutable registry supplies fields, inherited labels, types, enums, timestamps,
mandatory properties and endpoint rules. `contracts/graph_access.json` declares
behavioral policy without changing public ontology. No dependencies were added.

## Validation and write flow

Node CREATE validates the exact registry shape before acquiring the graph writer
lease; all graph-dependent checks occur after acquisition and fence advancement.
Relationship CREATE retrieves actual endpoints, then validates its registry shape.
Both check global application identity against nodes and all relationship types,
fixed municipality scope and applicable property references. Updates compare an
expected digest with actual stored content, preserve origin/identity, validate
merged properties, then run graph policies. Unknown fields, coercion, null/missing
required values and invalid enums fail explicitly. Registry immutable records are
append-only; no deletion method is supplied. Read adapters validate stored labels,
properties, endpoints and scope before producing public records.

Conditional VERIFIED associations require an existing verified `Evidence`, dated
observed/recorded/created no later than relationship creation, attributed through
`source_kind` and `source_record_id`; AGENT-only evidence cannot establish a fact.
Existing evidence used by VERIFIED links cannot have provenance/reliability rewritten
through this adapter. Domain correction/versioning remains a later service concern.
Optional evidence pointers must exist even on candidate links.

Primary relationships are explicitly declared in `singleton_outgoing`:
REPORTS, OCCURRED_AT, LOCATED_AT, MAINTAINED_BY, COLLECTED_BY, ASSIGNED_TO,
IN_ZONE and PART_OF. IN_ZONE assigns a location to one active primary administrative
zone; PART_OF assigns an incident to one active primary recurring-problem cluster.
Many locations/incidents may share a zone/cluster; incoming cardinality is unrestricted.
The ontology has no primary flag; these edges are primary. Overlapping outgoing
assignments and duplicate same-kind/source/target edges are rejected. Nonoverlapping
history remains valid. Validity is half-open `[valid_from, valid_to)`; unknown/open
bounds are conservatively overlapping. Existing registry requires valid_from if
valid_to is supplied. DEPENDS_ON must be a DAG, including historical dependencies.
DRAINS_TO checks only cycles with a simultaneous validity intersection; an explicit
cycle request must cite a verified INSPECTION_REPORT via both the evidence pointer
and `inspected_cycle_evidence_id`. Other network types are not universally acyclic.
Policy scans cap at 2,000 same-type edges / 10,000 traversal states and fail closed.

HAS_SCHEDULE is exclusive per route and exact existing service_type over the
intersection of relationship validity and target ServiceSchedule validity. Empty
applicability is rejected. Simultaneous different service types and nonoverlapping
same-service date windows are valid. This is not a global route singleton. Timezone
changes alone do not distinguish services. schedule_spec remains opaque: overlapping
same-service free-text definitions cannot be assumed compatible; represent multiple
recurring windows in one definition. No parser or new ontology property is added.
Schedule service/date node edits revalidate all affected incoming assignments under
the writer fence, with the same10,000-comparison fail-closed cap; edge updates also
recheck. Arbitrary aliases of service_type are not semantically normalized here;
B04 must review source nomenclature before relying on it.

Error types distinguish `SchemaError`, `NotFound`, `Conflict`, `ScopeError`,
`PreconditionFailed` and `OutcomeUnknown`. Native client/runtime failures can also
propagate; future APIs must redact them into their error envelope.

## Concurrency, atomicity and recovery

One Redis lease serializes repository writers per graph. A new owner first increments
`repo_epoch` and sets `repo_owner` on the existing internal CivicSchemaMigration
record. Every preparation/mutation checks owner, epoch, READY and expected revision
inside its graph statement. Lease expiry alone cannot authorize an old writer after
a successor advances the fence. CAS hashes reject stale mutable-record updates.
The metadata has no public entity label and is excluded from results.

A separate fenced preparation persists `repo_pending` with a request UUID, target
ID/kind, pre-state digest, request digest and time. A single graph query applies the
domain mutation, appends a COMMITTED audit entry, increments `repo_revision` and
clears the pending intent. On the installed 6.0.2, a deliberately failing second
CREATE rolls back the first CREATE and metadata, verified with real UNIQUE errors.
This is a tested single-graph/single-query guarantee, not multi-query transactions.

A lost response never causes an automatic mutation retry. After an acknowledged
or uncertain failure, `recover_pending()` (also called by the next writer) reads
actual state. An unchanged pre-state allows ABORTED_UNCHANGED and intent clearance;
a different state fails closed for human reconciliation. A commit with a lost reply
already has its COMMITTED audit and cleared intent. Verify target/hash/audit before
retrying; repeated creates return Conflict rather than duplicating data. Pending
writes block reasoning reads. Audit retains IDs/hashes and no raw source text; it
caps at 10,000 entries and requires a future reviewed archival migration to grow.

All these guarantees require writes through this adapter. Privileged raw DB access
can bypass scope, relationship identity, temporal and policy rules, or revision
tracking. This is a local demonstration, not enterprise isolation or database RBAC.
No authentication, approval binding, work-order state machines, domain outbox/event
replay, durable worker or runtime MCP authorization is implemented by B03.
AOF remains `appendfsync always`; restart/recreation retains graph/Browser volumes.
Power-loss guarantees and replicated failover are not claimed.

## Named read templates

| Template | Root / result |
|---|---|
| drainage_paths | Asset; actual upstream or downstream DRAINS_TO paths |
| shared_infrastructure | At least two incident IDs; shared downstream assets and incident IDs |
| incident_history | Location or asset; related incidents with after/as_of filtering, not a recurrence verdict |
| maintenance_history | Asset; inspections/evidence and task/work-order/outcome history |
| cross_category_paths | Waste point → location ← drain → downstream drain → location ← road; candidate connection, not causation |
| hypothesis_evidence | Investigation or hypothesis; assessments with SUPPORTED_BY and CONTRADICTED_BY evidence |
| ownership_dependencies | Asset/point/task; department, collection route/schedule, assignment |
| task_dependencies | ActionTask; explicit directed dependency paths |

Every template applies scope, knowledge-time and half-open relationship validity
filters. UTC fractional seconds are compared at Python datetime microsecond
precision, matching the existing schema parser; raw lexical `Z` comparison is unsafe.
Evidence pointers outside a path also exclude that path when their knowledge dates
exceed as_of, including candidate associations. Future-updated node records are
excluded rather than pretending to reconstruct an
old snapshot. Missing relationship start dates remain explicitly unknown. Incident
retrieval does not classify distinct reports into incidents or declare recurrence.

Only static templates run, with all values parameterized and the validated integer
hop bound inserted into fixed grammar. GRAPH.RO_QUERY is used throughout. Configure
ReadLimits downward: maximum6 total path edges,100 paths,120 nodes,200 edges,
1,000ms per query. max_hops counts every edge, including non-infrastructure
connectors; default6. Requests exceeding configured limits or below the template's
minimum fail explicitly. No implicit expansion of the caller's budget occurs.

| Template | Minimum / maximum useful total hops | Infrastructure-only DRAINS_TO allowance |
|---|---|---|
| drainage_paths | 1 /6 | total |
| shared_infrastructure | 1 /6 | total-1; zero permitted after AFFECTS |
| cross_category_paths | 5 /6 | total-4; at least1 |
| incident_history | 1 /1 | none |
| maintenance_history | 1 /3 | none; branches have1,2,2,3 edges |
| hypothesis_evidence | hypothesis2 /2; investigation3 /3 | none |
| ownership_dependencies | 1 /2 | none; branch lengths1,1,2,1 |
| task_dependencies | 1 /6 | none; DEPENDS_ON uses the total budget |

Useful maxima below the request clamp the executed budget downward, never upward.
Fixed branches longer than the effective budget are omitted. QueryBudget reports
requested/effective/min/max totals, fixed connectors (null for mixed branches),
and infrastructure_hops (null without DRAINS_TO). shared at total1 can return two
incidents directly affecting one asset; total2 permits one additional drainage link.
Cross-category at total5 finds a one-drain-link path; default6 also finds two links.
A longer connected path can produce an empty bounded result.

search_limited is true for all variable-length families, and for fixed families
when longer branches were omitted. It deliberately does not assert global graph
exhaustion. Empty results mean no qualifying path returned within this budget and
filters, including for truly disconnected fixtures. A causal conclusion or proof
of global disconnection cannot be inferred. Result reservations state this limit.
truncated independently flags row/node/edge output-cap omissions. Individual branches
fetch at most limit+1 rows; merged outputs stop at overall caps and return whole
paths. Selection within a limit has no sorting guarantee. Aggregation may explore
more intermediate rows; the DB timeout bounds that work, not a fixed expansion
count. Strict scope/provenance/time/revision checks and GRAPH.RO_QUERY remain.

Reads capture repository revision before and after retrieval/validation and retry
once if it changed. The installed runtime misprojects a disconnected metadata
property alongside upstream variable-length paths (0 versus a nonzero actual revision).
The implementation avoids that projection, annotates with the captured scalar
revision and checks monotonic pre/post state. The reproducible runtime report
records this observation; no general undocumented DB bug diagnosis is claimed.
Out-of-band raw writes are outside this snapshot guarantee.

Results carry stable IDs, subtype labels, all validated properties, actual directed
edge source/target, ordered path node/edge IDs, traversal-relative direction, temporal
metadata, evidence IDs, as_of, repository revision and interpretive reservations.
Internal numeric IDs only map driver objects locally. These DTOs can feed later
Canvas/MCP/API adapters; they are not the final REST/MCP envelope. Supporting
Evidence referenced outside a path can be retrieved by its stable pointer. Causal
conclusions, historical snapshot reconstruction and product completion are not claimed.

## Reproduce

From repository root, with the accepted local runtime running:

```sh
make test-repositories
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence
make test-spec
PYTHONPATH=backend backend/.venv/bin/python -m tests.b03_evidence
backend/.venv/bin/civicly schema-status
```

Tests construct small disposable migrated graphs, clean only their UUID graph, and
never import the city/evaluation fixture. Fault injection wraps real DB operations:
responses are dropped before/after actual statements; it never returns fake success.
The original persistence probe and zero-domain-node canonical graph remain intact.
`docs/evidence/B03-runtime.json` includes eight real result examples, EXPLAIN plans,
versions, canonical readiness, metadata spike and B01 probe. See test_log.md for
counts, failed attempts and later-stage exclusions.

Primary references verified alongside installed APIs:
[FalkorDB functions](https://docs.falkordb.com/cypher/functions),
[GRAPH.RO_QUERY](https://docs.falkordb.com/commands/graph.ro-query),
[official Python Graph implementation](https://github.com/FalkorDB/falkordb-py/blob/main/falkordb/graph.py).
Runtime evidence on pinned 6.0.2 takes precedence over current upstream examples.


## B03-R performance boundary

See [B04_BENCHMARK_PLAN.md](B04_BENCHMARK_PLAN.md) for the proposed pilot/full/repeat
import benchmark, metrics and correctness gates. Same-type integrity scans repeat
O(E_k²) aggregate work during ingestion; global relationship-ID checks may scan all
edges. The scalar JSON audit grows O(N) and is parsed/rewritten per mutation, yielding
O(N²) cumulative serialization/transport. Schedule grouping adds bounded comparison
and target-read costs. No performance claim, full-data import, bulk writer, policy
bypass or audit truncation was implemented during B03-R. Later optimization needs
separate measured justification and the same real atomicity/recovery guarantees.

## B04 ingestion consumer

`app.ingestion.Importer` uses this repository unchanged for every accepted create.
Equal exact public-record hashes no-op; changed values require explicit review.
Only validated milestone04 disposable graphs are currently authorized for its data
imports. See INGESTION.md and contracts/dataset_ingestion.json for provenance,
precision, quarantine, interruption and staged-data boundaries. No raw bulk write,
policy cap relaxation, new migration or canonical promotion is implemented.

## B05 graph-analysis consumer

See ALGORITHMS.md and contracts/graph_algorithms.json. Typed GraphAnalysis uses
bounded GRAPH.RO_QUERY paths with actual revision/time/proof checks; count-based
ranking is not causal confidence. Case history remains explicitly coverage-limited.
Factory-owned B05 counterfactual clones use existing migration/repository fencing,
CAS/intent/audit for edge ablation; original graphs remain read-only. No general
source deletion method or schema/0001 change. Current city candidate links are not
promoted to VERIFIED; unresolved scenario-source gaps remain B08/B09/B11/B19.
