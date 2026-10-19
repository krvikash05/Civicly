# FalkorDB knowledge graph — data architecture and query semantics

**Canonical graph name:** `civicly_knowledge`; machine definitions in `contracts/schema_registry.json` (v1 plus v2 extensions; do not rename existing entities without migration). The original v1 fixture is a small bootstrap, not the complete demo.

## Domain model — normalized, not denormalized complaint tickets
- Physical: `Zone`, `Location`, `InfrastructureAsset` multi-label specialized nodes `DrainInlet`, `DrainSegment`, `RoadSegment`, `WaterPipe`, `WasteCollectionPoint`, `PumpStation`; operational route/schedule; `DrainageCatchment` in v2 for contributing area, `RainfallEvent` for observed storm condition, `PickupExecution` for actual collection record, `AssetConditionSnapshot` for time-varying condition.
- Events: `Complaint` (report) → `Incident` (actual occurrence) → `ProblemCluster` (persistent / recurrent pattern). **20 reports in same downpour != 20 incidents.** An Incident can affect multiple assets; primary location only 1. Cross-category links require separate Incident nodes with justified shared paths.
- Reasoning: `Investigation` → `Hypothesis` → append-only `HypothesisAssessment` with `SUPPORTED_BY`/`CONTRADICTED_BY` → `Evidence` → `DataSource` or `Document`; independent `Finding` for verified observations/causal assessment. No in-place deletion of bad hypotheses.
- Operations: `Department`, `KnowledgeProcedure`, `ResolutionPlan` vN, `ActionTask`, `Approval`, `WorkOrder`, `Inspection`, `InterventionOutcome`, `StatusEvent`; `ActionTask DEPENDS_ON ActionTask` acyclic, mandatory accountable department.
- Agent memory: `AgentRun`, `AgentDecision`, `ToolExecution`, `CaseMemory`, procedural links; checkpoints handled by `FalkorDBSaver` separate from domain schema.
- Users: v2 `OperatorAccount` with seeded fake identities and role/department; cryptographic auth session remains server-side, never expose password hashes as graph embeddings.

## Hard semantics
`DRAINS_TO` directed verified/candidate physical water pathway, not nearest drain; `COLLECTED_BY` waste-point to route; `UNDERLIES` pipe to road; `MAINTAINED_BY` authorized department; `AFFECTS` incident-to-asset includes association_status and evidence; `LOCATED_AT` geographic reference not proof of cause. Historical topology relationships have `valid_from`, `valid_to` and provenance. With incomplete topology return `unknown`, do not insert speculative edge. Candidate edges do not enter verified-only reachability unless query requests candidates and clearly labels results.

**Enforce in services**: asset cannot DRAINS_TO itself; no drainage loops unless explicitly modeled as a cycle and inspected; no invalid labels/endpoints; no `DEPENDS_ON` cycles; one active primary ownership/route within temporal validity; evidence required before marking association `VERIFIED`; no inference edge promoted to fact on spatial proximity; plan edits after approval supersede approval. Relationship temporal overlap and cardinality validated against existing graph.

## Type / geometry / index rules
- Stable ID string across graph; unique indexed node ID per base label. `created_at`/`observed_at`/`recorded_at` in UTC. For schema v2 additional missing fields are optional until migrations set them.
- FalkorDB scalar node/edge properties only; complex JSON blobs validated at service layer and either serialized explicitly or linked in document store. Relationship arrays in REST DTO are materialized edges in FalkorDB.
- For point and spatial retrieval follow actual current point syntax from docs and test; full lines/polygons in `data/geometries/*.geojson` with ID+checksum. Spatial proximity proposes candidate asset associations; physical topology validates them.
- Index `id` all frequently addressed types, occurrence time, issue_type/status, active plan/workorder, location point; verify exact FalkorDB index/constraint syntax and operational status in **real migrations**. Do not assume Neo4j-only procedures.
- Embedding/full text may support case similarity; retrieval proposes candidates only. Rerank by verified topology, temporal validity, outcomes.

## Required graph operations (bounded, parameterized templates)
| Operation | Inputs | Result / interpretation |
|---|---|---|
| 1. reachability | asset_id, direction, max_hops<=6, as_of | actual connected DRAINS_TO paths, edge provenance |
| 2. shared-bottleneck | incident_ids, threshold | common downstream nodes reached by >1 incident; not causal proof |
| 3. impacted-assets | potential failure asset, max_hops | possible downstream coverage and criticality count; not flood prediction |
| 4. incident history | asset/zone, after, before | distinct canonical incidents and interventions chronologically |
| 5. path explanation | incident, hypothesis, evidence | serialized graph subgraph with supported/contradicted links |
| 6. plan DAG | plan_id | unmet dependencies, blocked tasks; topological order validated in service |
| 7. memory neighbors | asset + issue + temporal overlap | past failures, resolved/reopened cases and outcomes |
| 8. asset ownership | asset, effective instant | responsible department and applicable procedures |

### Graph algorithms and actual implementation location
- Bounded reachability, common ancestors/dependencies, component membership, distinct path queries: Cypher matching/traversal in FalkorDB if supported; required query registry + EXPLAIN/PROFILE inspection where safe. Aggregate result in Python if FalkorDB Cypher lacks a specific aggregation.
- Dependency DAG topological ordering and cycle validation: Python deterministic graph library using FalkorDB-fetched validated edges, results/lineage stored back in canonical graph.
- Criticality: start with explainable count of distinct serviced/impacted assets through directed verified dependency links; avoid arbitrary PageRank on hydraulic networks. Optional centrality metrics computed in Python over bounded export, and **only** if they improve tested decisions.
- Counterfactual: clone fixture into separate test graph, alter an edge/inspection and compare agent-selected next_action/evidence_paths without contaminating canonical demo data.

## Cypher templates to implement and runtime-verify
```
MATCH (a:DrainSegment {id:$asset_id})-[:DRAINS_TO*1..6]->(d:DrainSegment)
RETURN DISTINCT d.id, d.condition LIMIT 100
```
```
MATCH (i:Incident)-[:AFFECTS]->(a:InfrastructureAsset {id:$asset_id})
RETURN i.id,i.issue_type,i.started_at ORDER BY i.started_at DESC LIMIT 40
```
The examples show intended operations and are **not claimed to have been executed**. Use supported syntax and explicit read-only query executor, static query templates, parameterize IDs (note `LIMIT` may require safe integer literal after validation), guard timeouts, result size, `association_status`, historical edge validity. Never let the LLM provide executable write Cypher.

## Data-version requirements
`graph_revision` is **application managed**, not a built-in FalkorDB feature; increment on affected investigation/entity mutations with consistency tests. All agent evidence/path outputs carry provenance IDs + `as_of` and graph_revision. Store `source_kind`/verification and actor in typed status or evidence event; no mutation without audit.

## Compatibility checks
`B02` migration syntax; `B03` verified/candidate path semantics; `B04` temporal queries; `B05` graph perturbation; test `GRAPH.RO_QUERY`, accepted OpenCypher subset, supported point indexes. Preserve both return path and sources for future FalkorDB Canvas explainability.

## B02 canonical scope contract (v3)
Canonical domain records use `municipality_id='demo-city'`, fixed by the server.
`tenant_id` is not a domain alias or caller-controlled input. Framework integration
may translate the same fixed value explicitly if its verified API requires it.
All normative machine contracts reference this same municipality_scope policy.
This is one synthetic municipality, not enterprise tenant isolation. Legacy v1/v2
fixtures require explicit conversion before canonical import; no implicit scope,
unknown-field dropping, or invented temporal evidence is permitted.

B02 implements the current strict rules in `backend/SCHEMA.md`: migration 0001
establishes all declared node IDs/required-property constraints and common edge
metadata constraints, with index/constraint readiness verified on server 6.0.2.
Canonical v3 supersedes the earlier optional-extension import convention above:
new records must supply all required fields and schema_version 3. Source v1/v2
fixtures retain their original shape until explicit B04 conversion. Storage-only
`CivicEntity` provides cross-label node-ID uniqueness; `CivicSchemaMigration`
bookkeeping is excluded from domain/MCP/Canvas data. UTC Z validity bounds are
optional (unknown/open), with typed evidence pointers and no inferred dates.
Graph-wide cardinality/cycle/reference checks and query repositories remain B03.

## B03 implemented access foundation (supersedes B03 TODO above)

`backend/GRAPH_ACCESS.md` documents the implemented repositories, declared integrity
policy (`contracts/graph_access.json`), eight typed read templates, fixed scope,
CAS/fenced writers, query budgets and recovery. Registry v3 and migration 0001
remain unchanged; no public ontology fields or names were added or dropped.
Canonical migration readiness is checked before repository construction. Future
MCP/domain/API services must use typed methods and preapproved read requests; this
adapter does not authorize operations or deliver durable events. B04 fixture
conversion/import remains blocked by the 55 value_number defects. Product R01–R18
capabilities remain mandatory and are not declared complete by this foundation.


## B03-R clarified cardinality, budgets and isolated targets

IN_ZONE and PART_OF are outgoing primary assignments with no concurrent overlapping
zone/cluster; disjoint history and many incoming members are valid. HAS_SCHEDULE
permits multiple services/date windows but refuses overlapping definitions for the
same exact service on one route. Applicability intersects edge and schedule-node
validity; schedule edits revalidate incoming assignments. Opaque schedule_spec text
cannot establish that overlapping definitions are compatible. No registry v3 fields,
labels, enums or immutable migration0001 content changed; behavioral contract is
contracts/graph_access.json v2.

max_hops is total path edges, default6/hard max6; drainage-only allowance subtracts
fixed connectors (shared1, cross-category4). Cross-category needs minimum5 total;
insufficient requests fail. Result search_budget/search_limited distinguish bounded
negative searches from truncated output and global absence. Detailed per-template
minima/branch lengths are in backend/GRAPH_ACCESS.md. Both repository/migration
constructors now share a guarded milestone02–25 UUIDv4 test namespace; canonical
and B01/document/checkpoint protections remain. See backend/INGESTION.md for conversion, import and repeat performance verification.

## B05 implemented primitives (supersedes B05 TODO above)

backend/ALGORITHMS.md and contracts/graph_algorithms.json define the implemented
bounded directed drainage paths, shared/impacted coverage, count-based criticality,
induced weak components, typed infrastructure dependencies, prerequisite-first task
DAG and transparent historical case retrieval. Real fixture ablation changes paths
and ranking while preserving original identities/revision/audit/data. Counterfactuals
are owned B05 disposable clones, not canonical mutations or source corrections.
Actual city verified-only and exploratory results are separate;42 DRAINS_TO remain
candidate-level, source-binding/history/S07 gaps explicitly tracked. No agent/MCP,
memory/GraphRAG, planning/approval/operations/API/frontend implementation by B05.

## B08 complaint intelligence consumer

app.services.complaints reuses immutable registryv3, existing B03 policies/fenced
write protocol and B05 topology. Complaint→REPORTS→Incident→PART_OF→ProblemCluster
with OCCURRED_AT/REPORTED AFFECTS; no public ontology or migration changes. Existing
UNVERIFIED Evidence stores bounded validated intake/review journal JSON. Primary
assignment corrections retain nonoverlapping old/new memberships and source evidence.
See backend/COMPLAINTS.md/contracts/complaint_intake.json. All18 requirements remain;
no B09 evidence verification/operations/agents/API/frontend claimed.

## B09 evidence/hypothesis service consumer

services.evidence implements registered Investigation/PROPOSES/EXPLAINS/CONCERNS,
append-only HypothesisAssessment with actual supporting/contradicting Evidence, and
Inspection/PRODUCED/ESTABLISHES/Finding. Strict versioned source commands/reports and
assessment snapshots serialize explicitly into existing summary/rationale fields;
registryv3/migration0001 unchanged. Domain rulev1 uses reviewed independent findings
and actual verified-only B05 topology, never candidate/proximity/count/model claims.
Corrections append history; no dispatch/work orders/outbox/agent/API implementation.
Active graph stays explicit; no seed promotion. See backend/EVIDENCE.md.

## B20-R-OWNERSHIP — reviewed responsibility versus inventory claims (DEC-067)
`MAINTAINED_BY` CANDIDATE/REPORTED inventory claims remain immutable and cannot authorize planning. Explicit department-lead submission and independent analyst review add a distinct synthetic reviewed Evidence source and VERIFIED responsibility interval. Claims and accepted responsibility occupy separate temporal cardinality tiers; existing unverified exclusivity is retained, and overlapping VERIFIED assignments reject regardless of department or timestamp recency. No candidate is promoted, automatically closed or deleted. Half-open intervals permit historical/future succession without overlap; knowledge time still bounds visibility. New plan proofs bind reviewed evidence and relationship identities/hashes; changed active ownership requires revised plan/approval before new work. See contracts/responsibility.json and backend/RESPONSIBILITY.md. Migration0001 and canonical property names unchanged.
