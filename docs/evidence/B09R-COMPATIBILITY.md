# B00–B09 compatibility review

B09-R changes evidence assessment semantics only. Registryv3, municipality scope,
0001,0002, repository/writer, B04 artifacts/importer, B05 algorithms, B06/B07 runtime,
B08 intake and all582 original test sources are preserved against baseline688b893.
Exact source preservation is machine checked in B09R-source-audit.json. Verification
is not complete until the final regression/persistence report is PASS.

| Foundation | Preservation and exercised evidence |
|---|---|
| B00 contracts |18 objectives, scope, frozen legacy numeric defects and B04 conversion validated by both specification validators; designated DEC-004 findings remain open. |
| B01 |Full persistence test fresh connections, Browser HTTP200 and Browser file across actual restart/same container and recreate/new container/retained volumes. Original B01 probe independently read after lifecycle. |
| B02 |Actual schema readiness,91 index groups/182 operational constraints, registry/0001 checksums;0002 trace checksum unchanged. Full schema migration failure/recovery tests preserved. |
| B03/B03-R |Strict types/properties/endpoints/cardinality/temporal policies; bounded RO query templates and hop budgets; fence/lease/CAS/native rollback/recovery preserved. No arbitrary Cypher or mutation route added. |
| B04 |858-node/1246-edge source fingerprint/revision2104 unchanged, all42 drainage links CANDIDATE; converter/no-op import/hash tests preserved.55 original fixture defects remain frozen; converted values not repaired again or reassigned. |
| B05 |Full algorithms/case/counterfactual tests; candidate/verified and disconnected controls preserved. B09 utility source remains concerned WaterPipe -> affected RoadSegment. New B09-R test verifies required path expiry changes VERIFIED to SUPPORTED without erasing prior assessment; nearby same-coordinate pipe cannot substitute a path. |
| B06 |Actual official Node MCP initialization/discovery/approved RO calls, forbidden writes/admin/other keys, timeouts, outages/recovery and process cleanup rerun. Exact retained-city ACL unchanged. |
| B07/B07-R |Actual custom discovery12 read handlers, shared envelopes/schema/inventory, graph revisions, durable traces, per-event maintenance provenance, pre-cap chronological histories and explicit work-order unknowns rerun. New actual broker call reads a version2 attributed inspection report and retains distinct event evidence. No new tool or namespace.70 previously accepted trace observations verified read-only after lifecycle; new traces are additive. |
| B08 |Original tests for same event/continuing/persistent/recurrence/primary-cluster correction preserved. New controlled2027 fixture uses actual intake and records distinct January/August IDs with RECURRENT cluster after explicit February closure; no production source copy/merge. |
| B09 |All prior inspection, alternative-cause, topology, role, tamper, bounds, concurrent-CAS, journal replay, lost-response and actual constraint rollback tests unchanged. New explicit authority/meaning/occurrence categories, immutable v1 history/replay and appended v2 correction tested on real graphs. |

## History and consumer semantics

- Legacy assessment/rule1 remains readable with its original label, rationale, source
  lists, edges, hashes and receipt. Historically incorrect v1 causal relationships
  are historical claims; do not treat every old edge as a current verified assertion.
- New v2 assessments contain explicit classifications and previous-assessment ID;
  use the typed latest history result and its state, source/recording cutoff, revisions
  and reservations. No existing assessment is edited to conceal a correction.
- Optional absent attribution/classification fields do not enter v1 serialization or
  old command hashes. Explicit attribution reports are version2; generic MCP graph
  property/result schemas continue to carry their attributed JSON unchanged.
- Actual MCP maintenance history exposes inspection/report provenance; there is no
  new dedicated assessment-history MCP tool. New snapshots are JSON/Pydantic validated
  for future adapters, not a claim that B10 agents or B17 graph/API consumers exist.
- Read budgets fail closed; current mutable node versions cannot reconstruct past
  state. The cutoff fixture uses a March cutoff after the February closure version,
  excluding August/September evidence without reconstructing an overwritten January
  incident. This limitation remains explicit.

## Active graph gap

See B09R-ACTIVE-GRAPH.md. The intersection of existing B08/B09 writable targets is
canonical, currently unseeded. Production MCP points to retained B04 city. Disposable
B08-to-B09 source copies/test server injection prove interface compatibility, not a
coordinated production chain. Review and test one shared active graph/configuration
before B10 live-investigator acceptance. No silent seed promotion or guard widening.

## Remaining limitations

Demonstration domain criteria are deterministic and synthetic, not general hydraulic,
structural or causal science. Review/actor context is trusted internal, not B13 public
authentication or proof against colluding sources. Retrospective attribution requires
prior reviewed direct source evidence; unsupported recollection is insufficient.
20 total source references,100 related edges/history,300 metered reads/8s/1s per query,
B05 bounded traversals and inherited O(E) scans/O(N) audit/10k cap remain. Missing
history, source-document retrieval, clock/service mapping, hidden-evaluation isolation,
plan approval, events, memory/agents/GraphRAG/API/frontend retain their milestones.
No new product capability is claimed complete because these corrections pass.
