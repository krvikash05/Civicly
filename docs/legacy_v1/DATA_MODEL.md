# FalkorDB graph schema semantics & invariants

**Source of truth for exact labels/properties/enums/relationship endpoints:** `../contracts/schema_registry.json`.

## Canonical graph
Name: `civicly_knowledge`. Do not divide the three issues into separate graphs. Specialized assets carry labels `InfrastructureAsset` + subtype label (`DrainSegment`, `DrainInlet`, `RoadSegment`, `WaterPipe`, `WasteCollectionPoint`, `PumpStation`). Route and schedule are operational rather than physical assets.

Six logical domains: geography/assets; reports/incidents/problem clusters; inspections/evidence/causal assessments; agent runs/decisions/memory; departments/plans/actions/work orders; approvals/status events/outcome verification.

## Distinctions
- `Complaint` is a **source report**, not necessarily a distinct event.
- `Incident` is one occurrence (may have multiple complaints).
- `ProblemCluster` collects a recurring or persistent pattern (may span issue types only with explicit candidate links and evidence).
- `InfrastructureAsset` is a real or synthetic named physical asset.
- `Evidence` is an attributable observation/report/document extraction; `Finding` is a reviewed conclusion; `Hypothesis` is an explanation being investigated.
- `HypothesisAssessment` records each *versioned* evaluation at a particular time, with `SUPPORTED_BY` and `CONTRADICTED_BY` edges. Do not overwrite prior evaluations.
- `ActionTask` expresses a unit of planned work; `WorkOrder` is an authorized instance for execution; `InterventionOutcome` is an observed work result; long-term `ProblemCluster` control/resolution is a separate monitoring result.

## Physical topology
- Direct `DRAINS_TO` is the authoritative direction of water flow; multi-hop network paths are computed, not guessed from closeness.
- `UNDERLIES` is a verified/demonstrated pipe-road relation with source/validity; proximity alone is only a search candidate.
- `SERVES`, `COLLECTED_BY`, `MAINTAINED_BY` and `HAS_SCHEDULE` describe operations; require validity interval when assignments change.
- All topology edges have `valid_from`, optional `valid_to`, `association_status` (CANDIDATE/REPORTED/VERIFIED), and optional `source_evidence_id`. Queries for historical incidents should filter by effective time.
- Never label a causal relationship as physically verified without inspection or equally strong source evidence. Hypothesis edges `EXPLAINS` and `CONCERNS` are explanatory proposals, not physical facts.

## Spatial/temporal
- WGS84 location with latitude [-90,90], longitude [-180,180]; point-based candidate search indexed where supported. Maintain full road/pipe/drain geometry in GeoJSON referenced by asset ID.
- Timestamps are UTC ISO 8601 in API, stored consistently as numeric epoch milliseconds or FalkorDB-supported datetime/string; choose one, test range filters and document migration. Record `observed_at` separately from `recorded_at`; reports can arrive late.
- Historical validity applies to physical/organizational edges. `valid_from <= at_time < valid_to` when `valid_to` exists.
- No empty-string fake measurements. Numeric values must have defined unit and observation method; null means unknown at API boundary, absent property in graph.

## Provenance
Every evidence record links to >=1 `DataSource` by `DERIVED_FROM`, includes evidence origin (`SYNTHETIC`, `PUBLIC`, `MUNICIPAL`, `USER`, `AGENT`) and observed/recorded times. Files/photos referenced by URI/hash not pasted into graph. Synthetic fixture ground truth stored outside the agent-visible graph for tests.

## Integrity invariants
- Unique stable string ID for each label; `id` is globally unique in application registry, not internal FalkorDB ID.
- A valid accepted Complaint has exactly one current REPORTS Incident association; historic reassignments produce audit event.
- Incident has one primary OCCURRED_AT Location; ProblemCluster has at most one primary active membership per Incident.
- `AFFECTS` may be CANDIDATE; absence of evidence must not be mislabeled VERIFIED.
- Each `HypothesisAssessment` belongs to one Hypothesis; assessed evidence IDs must resolve to existing evidence.
- A plan has >=1 ActionTask and a **directed acyclic** DEPENDS_ON task graph.
- One accountable Department per active ActionTask; an unassigned proposed task can exist only before approval.
- A WorkOrder cannot enter ASSIGNED/IN_PROGRESS/COMPLETED without an APPROVED Approval bound to the exact plan version/hash and task.
- An agent may record an observation of work, but physical COMPLETED status requires attributable report plus authorization as enforced by service; agent cannot claim independent physical completion.
- A work order's COMPLETED status does not imply the ProblemCluster is CONTROLLED or investigation COMPLETED.
- Reopening after recurrence leaves previous interventions and hypothesis assessments intact.
- Ingesting the same `(source_id, external_record_id, source_version)` twice is idempotent.
- Changing immutable records creates a correction/superseding event, not silent deletion.

## FalkorDB migration strategy
- Registry generates label-specific ID indexes, unique/mandatory constraints only where **supported and verified** in current FalkorDB release. In case of conflict or unsupported features, enforce invariant in validated ingestion/services and record the tested result; no nonexistent Cypher or Neo4j syntax assumptions.
- Create indexes on `Incident.id`, `started_at`, `InfrastructureAsset.id`, `Location` point, `Investigation.id`, `Evidence.id`, `WorkOrder.id` after verifying exact supported syntax.
- Migrations are versioned and idempotent, include status checking for asynchronous constraint creation and data validity checks before enforcing constraints.

## Cypher patterns (illustrative, test on selected version)
```
MATCH (d:DrainSegment {id: $asset_id})-[:DRAINS_TO*1..5]->(other:DrainSegment)
RETURN DISTINCT other.id, other.condition
```
Variable length `1..5` is an example. Tools enforce lower/upper hop bounds and encode chosen bound using a validated literal if necessary; do not build query syntax from uncontrolled LLM strings.

## Open issue resolved from early discussion
Earlier notes suggested `SUPPORTED_BY` from Hypothesis directly to Evidence. Final contract uses `HypothesisAssessment -> Evidence`, so competing versions are auditable. Earlier `Drain` becomes `DrainSegment/DrainInlet`; earlier `RECURRENT` problem detection is recorded on ProblemCluster.pattern_type, not issue_type.
