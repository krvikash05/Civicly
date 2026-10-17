# Civicly data design: source inventory, ingestion, synthetic municipal environment

## Source-of-truth classification
1. **Canonical verified infrastructure** — schema-checked asset inventory and directed drainage/collection dependencies imported from allowed datasets or controlled synthetic ground truth. Never infer a physical connection from an LLM summary.
2. **Reported observations** — citizen complaint, field report, weather observations, service logs. Distinguish fact vs claim; every measurement carries `observed_at`, `recorded_at`, time window, unit, source ID and verification status.
3. **Agent conclusions** — hypotheses/assessments and plans with cited evidence. Not interchangeable with verified asset fields.
4. **Organizational documents** — signed-off simulated department procedures, task logs and inspection memos; GraphRAG-ingested documents + canonical references. Unsupported extracted claims must remain unverified.
5. **Evaluation-only ground truth** — hidden physical causes and rule-based scenario oracle in `data/scenarios/hidden_truth.json`; must NEVER be mounted or readable by agent workers/API/MCP/GraphRAG at demo runtime.

## Data sources and adapters
| Adapter | Input | Ingestion behavior | Offline behavior |
|---|---|---|---|
| Synthetic fixtures | JSON/GeoJSON/MD | Validate stable IDs/types, seed graph and source refs deterministically | Always available |
| Complaint POST / CLI | free text, issue, location, timestamp, source | dedup candidate reports, classify issue, create or attach Incident | Reject/queue with explicit error |
| Inspection submission | authorized inspector + measurements + source | input validation, append-only evidence, outcome event | locally works |
| Waste pickup log | scheduled pickup vs actual completion, route, crew, timestamp | distinguish missed, partial, completed; link to route, point and task | seed/simulated |
| Maintenance ticket import | CSV/JSON, location, asset, intervention | validate chronological repair chain and result source | fixture fallback clearly synthetic |
| Weather observation | public API/CSV with source/time/units | not generic web guessing; bounded fetched source, cached with TTL and provenance | `EXTERNAL_UNAVAILABLE`, fixture substitution only in explicitly SIMULATED scenario |
| Org docs | Markdown/PDF, version, organization, effective dates | hash original, GraphRAG schema-guided ingest, verify extracted references and source citations | bundled fixture docs |
| GIS asset lines | GeoJSON lines/polygons | valid geometry/ref, structured topology edges separate from spatial closeness | bundled fixture geojson |

## Ingestion pipeline
1. Read source manifest (`origin`, license/right-to-use, `source_kind`, SHA256, timezone, imported_at).
2. Validate JSON Schema/Pydantic shape and units. Quarantine malformed records with explicit report; never silently coerce missing evidence.
3. Canonicalize times to UTC and duplicate-safe stable source IDs. Preserve original source payload outside graph if large.
4. Spatial candidate resolution (distance/time/issue) and asset ID mapping; uncertain matches `CANDIDATE`, not verified.
5. Incident matching: same issue category and temporally overlapping observation window and location/asset correlation; classification can propose only, deterministic matcher applies threshold; human correction auditable.
6. Recurrence grouping: separate incidents that reappear after resolution or independent events; no fixed '3 complaints' rule; derive ProblemCluster `PERSISTENT`/`RECURRENT`/`CROSS_CATEGORY` with explanation and evidence IDs.
7. Write validated graph upserts by external source version; create edges only from allowlisted registry; emit ingestion status and event.
8. Check referential integrity, graph invariant scans and imported counts. Save idempotency report (`created`, `matched`, `rejected`, `quarantined`).

## Measurements
Waterlogging: rainfall mm + interval/observed station, depth cm, drain obstruction yes/no + severity, standing-water duration min, drain design capacity with correct unit. Road: pothole depth cm, distress area m2, repair method, material, subgrade condition, pipe pressure/leak test observations, traffic load if available. Waste: waste volume liters/m3, bin capacity, service expected/completed/missed, route time, dumped vs authorized location. No manufactured sensors. Differentiate observed and estimated values.

## Scenario dataset strategy
- A **purposefully constructed visible seed**, not randomly connected blobs. Each case has 4 logical data stages: incoming complaint, historical patterns/topology, targeted inspection outcome, municipal action+follow-up.
- At least 10 distinct scenarios in `contracts/scenarios/catalog.json` and `docs/demo/SCENARIOS.md`; at minimum 4 rich flagship scenarios with detailed graph evidence, counterfactual variants, plan dependencies, outcomes and hidden truth.
- Target expanded seed: >=5 zones, >=50 locations, >=120 infrastructure assets/routes, >=90 canonical incidents, >=250 complaints, >=20 clusters, >=100 inspection/maintenance/pickup events, >=15 organizational source documents, >=20 historical decisions/repairs. **Meaningful seeded fixtures must control the conclusions**; automated expansion may add believable non-causal background only, with stable IDs and invariant validation.
- Seed city is fictional **Civicly Demo City**. Any approximate map coordinates are synthetic demonstration positions, not an assertion that real infrastructure exists there. Public weather must be attributed and separated from fabricated local records.
- Pre-seed only information the agent is legitimately allowed to know; delayed inspection findings appear only after simulator event/authorized submission. If fixture already reveals cause via a graph edge label, redesign.
- Generate negative controls: similar complaint with independent asset, adjacent but disconnected drain, unusually high rainfall without blockage, previous false positive pipe leak, skipped pickups vs illegal dumping, early completion without verification, stale plan approval.

## Deterministic demo reset
`civicly demo reset --seed <seed> --scenario <id> --confirm` resets demo-only graphs, checkpoint namespace, org doc graph, simulation clock, event outbox and task state. Refuse reset outside demo mode. Use deterministic random seed, `clock.now()` injectable, event ids derived from fixture. Must produce checksums/counts and scenario starting state.

## Evaluation leakage guard
Evaluation harness stores hidden truth outside the backend's runtime data mount. CLI `civicly evaluate` can query it in a separate process after the agent produces result; no MCP tool or agent prompt sees that file. Unit test verifies agent containers lack that path and cannot access evaluation labels.

## B02 canonical scope contract (v3)
Canonical domain records use `municipality_id='demo-city'`, fixed by the server.
`tenant_id` is not a domain alias or caller-controlled input. Framework integration
may translate the same fixed value explicitly if its verified API requires it.
All normative machine contracts reference this same municipality_scope policy.
This is one synthetic municipality, not enterprise tenant isolation. Legacy v1/v2
fixtures require explicit conversion before canonical import; no implicit scope,
unknown-field dropping, or invented temporal evidence is permitted.

## B04 executable fixture boundary (2026-10-17)

See `backend/INGESTION.md` and `contracts/dataset_ingestion.json`. Original sources
remain frozen. Generator2.1 authors a distinct corrected synthetic revision; actual
field deltas and converted manifests are in `data/ingestion`. Strict B04 importer
uses accepted repository policies on isolated B04 graphs only, with exact hash-based
no-ops and changed-source conflicts. Original55 measurements are losslessly mapped.
Missing physical proof remains CANDIDATE; missing dates/histories/geometries are not
invented. Offline reports and evaluator release references are not runtime inputs.
Complaint/recurrence services, durable domain events, source ownership/version RAG,
scenario release and evaluator process isolation remain designated later milestones.

## B08 typed intake and original-source preservation

contracts/complaint_intake.json +backend/COMPLAINTS.md define implemented strict source/
UTC/unit normalization and first-original preservation in an UNVERIFIED intake journal.
Independent reports remain distinct; same external ID/content matches, changed content
or source version conflicts. Actual intervals/explicit asset context determine same
occurrence, provisional persistence, recurrence after dated end or cross-category context.
No fixed complaint-count rule, proximity-cause inference or automatic resolution from
completed work. B04 city/fixtures stay frozen; read-only previews expose candidate links,
missing dates/history/source binding and unlinked measurements. Domain batch/receipt is
atomic after separate durable preparation; event delivery remains B15.
