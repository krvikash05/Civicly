# B02 canonical graph foundation

The registry is `contracts/schema_registry.json` version **3**. Its 42 public node
types, 47 directed relationship types and existing enums retain their names and
values. B02 implements schema infrastructure, not a civic investigation or action.

## Scope and identity

Every canonical domain node and edge requires `municipality_id='demo-city'`.
Strict validation rejects `tenant_id`, another municipality, unknown fields,
missing fields, incorrect primitive types, invalid declared enums, null scalar
values, and unsupported numeric values (integers must fit signed 64-bit storage).
Scope is server-selected, never an LLM/API argument. No framework currently
requires a tenant adapter; future integrations must map explicitly at their
boundary rather than introduce a second domain scope name.

Canonical node `schema_version` is exactly 3. Supplied v1/v2 fixtures remain
unaltered archival source inputs: B04 must explicitly convert scope/version and
edge metadata, retaining original source provenance. The 55 Observation
`value_number` defects are rejected, not coerced or discarded. Supplied spec
validators report legacy structural checks and the known import blocker; their
PASS is not canonical ingestion acceptance.

The schema compiler adds storage-only `CivicEntity` to each public node label.
`DrainSegment`, `DrainInlet`, `RoadSegment`, `WaterPipe`, `WasteCollectionPoint`
and `PumpStation` also carry `InfrastructureAsset`. Global domain node IDs are
unique through the common label, with per-public-label ID constraints as defense
in depth. `asset_type` retains its original string vocabulary; subtype labels are
the type identity. Future Canvas DTOs must keep stable application IDs and expose
public labels while filtering storage-only labels and migration records.

Every relationship requires stable nonempty `id`, fixed `municipality_id`, and
UTC `created_at`. ID uniqueness is enforced per relationship type. Global edge-ID
allocation/cross-type checks belong to future validated repositories/services;
native FalkorDB has no cross-type relationship constraint. This does not waive
the stable application-ID requirement. Native internal numeric IDs are not API IDs.

## Temporal and evidence conventions

`valid_from`, `valid_to` and `source_evidence_id` are typed optional metadata on all
relationships, preserving existing relationship-specific fields. Times use UTC
ISO 8601 `Z` strings. Validity is half-open `[valid_from, valid_to)`; an end requires
a start and must be later. Absent bounds mean unknown/open, not a guessed date.
`created_at` is recording time, not physical observation/validity time. A
`VERIFIED` association requires a nonempty evidence reference. Source existence,
authority, graph-wide overlap/cardinality/cycles and causal verification require
B03+ domain validation. B02 does not declare an evidence pointer a verified cause.

Direction/endpoints are checked against the registry before compiling a
parameterized statement; for example, `WaterPipe UNDERLIES RoadSegment` is valid
and its reversal is rejected. The compiler is a schema adapter, not an exposed
write API or operational repository. No agent gets arbitrary Cypher.

## Migration 0001

`app/graph/migrations/0001.json` is the immutable reviewed plan for registry v3.
It contains the exact registry SHA256, **91 RANGE index groups**, and **182
constraints**. Index groups are catalog rows per label/type, often containing
multiple separately indexed properties; they are not 91 composite indexes.

- 42 domain node labels plus `CivicEntity` and `CivicSchemaMigration`: 44 node
  index groups and 88 constraints (unique `id` + grouped mandatory properties).
- 47 relationship types: 47 index groups and 94 constraints (unique `id` +
  mandatory `id`, `municipality_id`, `created_at`).
- Domain index fields where registered: `id`, `municipality_id`, `status`,
  `issue_type`, `started_at`, `reported_at`, `observed_at`, `recorded_at`,
  `next_check_at`, `graph_revision`, and native `geo_point`.
- Relationship indexes: `id`, `municipality_id`, `valid_from`, `valid_to`.

The runner uses the official FalkorDB Python client. Version 1.8.0 lacks the
documentation's `create_constraint` helper, so it calls `execute_command` with
separate `GRAPH.CONSTRAINT` arguments. Identifiers are reviewed registry/plan
tokens; all dynamic property values are parameters. Actual 6.0.2 syntax is
`CREATE INDEX FOR ... ON (...)` and `GRAPH.CONSTRAINT CREATE ... PROPERTIES ...`.
It polls explicit-column `db.indexes()`/`db.constraints()` results until
`OPERATIONAL`; `PENDING`, `FAILED` or timeout cannot pass readiness.

Run from the repository root:

```sh
make migrate
make schema-status
make health
backend/.venv/bin/python -m pytest backend/tests/integration/test_schema_migrations.py -v -s
make test-spec
```

Canonical schema readiness is independent of full application readiness. The
graph contains only its migration record until later data ingestion. Native
constraints enforce existence and uniqueness, not unknown fields, primitive
types, enum values, endpoint labels, scope values or conditional evidence rules.
Tests prove this limitation as well as adapter rejection. Future services must
always use strict validation and restricted write paths; raw developer DB access
can bypass application policies.

## Additive failure and recovery protocol

1. One runner holds a 60-second renewed Redis schema lease. Each command has a
   finite query/socket timeout; readiness polls have a five-second per-item limit.
2. Before mutation it checks migration ID/version/checksum and registry hash.
   Unknown/future versions or drift fail closed. Existing indexes/constraints are
   inspected rather than blindly re-created. Never edit 0001 after application.
3. `CivicSchemaMigration` persists APPLYING/FAILED/READY, attempt count, timestamps,
   checksums and append-only state-history entries encoded as scalar JSON.
   Interrupted APPLYING/FAILED runs may safely rerun. Audit growth stops at 1000
   state transitions for explicit review rather than deleting old history.
4. On failed constraints, first inspect the real catalog and conflicting data.
   Migration never deletes records, changes IDs, or drops OPERATIONAL constraints.
   Repair real data only after reviewing provenance; tests repair an identifier
   in their disposable graph without deleting either conflicting record.
5. After repair, `backend/.venv/bin/civicly migrate --retry-failed` explicitly
   recreates only plan-listed constraints whose catalog state is FAILED. A normal
   rerun intentionally refuses failed constraints, even after data repair.
6. Rerun `make schema-status`. It rechecks actual operational objects and recorded
   version, so a READY marker alone is insufficient. Never delete volumes, reset
   graphs or edit recorded checksums to force success. Later upgrades require a
   new immutable plan and runner support. No destructive down migration exists.

The B01 `civicly_b01_runtime` graph and both retained volumes are preserved.
The runner refuses B01, document and checkpoint graphs; tests use only random
`civicly_b02_test_<uuid>` names. Document GraphRAG and saver schemas stay isolated.

In Browser select `civicly_knowledge` and inspect:

```cypher
CALL db.constraints() YIELD type,label,properties,entitytype,status
RETURN type,label,properties,entitytype,status LIMIT 200
```

Expected 182 OPERATIONAL constraints. For bookkeeping:

```cypher
MATCH (m:CivicSchemaMigration)
RETURN m.id,m.version,m.state,m.attempts LIMIT 10
```

Expected 0001 / 1 / READY. If verification fails, share `test_log.md`, `blockers.md`
and the failing command's output, excluding `.env` and other secrets.

Official references: [constraint creation/readiness](https://docs.falkordb.com/commands/graph.constraint-create),
[range indexes](https://docs.falkordb.com/cypher/indexing/range-index),
[Cypher limitations](https://docs.falkordb.com/cypher/known-limitations).
