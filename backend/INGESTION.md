# B04 synthetic conversion and repository ingestion

All eighteen product requirements remain mandatory. This pipeline prepares and
imports data; it does not implement scenario decisions, agents, MCP, GraphRAG,
municipal operations or B05 algorithms. Canonical graph and original B01 evidence
remain untouched; B04 targets are disposable validated milestone04 UUIDv4 graphs.

## Source and preflight decisions

The accepted B03-R baseline is local commit09482e2 (no push). Original v1/v2 source
files remain byte-for-byte frozen, including55 historical value_number defects.
Baseline hashes are in docs/evidence/B04-baseline-hashes.json. No migration0001 or
registry v3 alteration. Inline enums (including PickupExecution.status) are now
actually checked by the schema adapter; their existing contract values are unchanged.

Run offline audit before any import. data/ingestion/source-audit.json inventories
all original node/edge types/versions, required/unknown fields, reference/date/
verification/cardinality issues, source/document hashes, missing geometry, missing
historical records and excluded evaluator files. Original data has109 route/point
ledger disagreements,8 MISSED rows with actual completion, unlinked observations,
report/event chronology issues and incomplete verification. Scenarios and documents
also lack complete historical WorkOrder/AgentDecision chains, owner IDs/PDF coverage,
and case-specific bindings/evidence. Reported gaps are not fabricated away.

Generator2.1 emits a distinct corrected synthetic revision in data/generated;
it never overwrites original source fixtures. It emits canonical numeric value,
uses actual point/route membership when authoring its fictional ledger, omits actual
completion for MISSED, and builds fictional report times relative to their linked
incidents. Original observational measurements/dates remain unchanged. These are
new synthetic-source records, not recovered facts about the ambiguous old ledger.
Generator deltas are recorded field by field. Canonical conversion of original
legacy data is separately retained under data/ingestion/legacy-conversion, including
quarantined originals and reasons. No legacy record is silently discarded.

## Conversion contract

contracts/dataset_ingestion.json specifies version1. Node schema/scope upgrades,
materialization metadata,55 lossless numeric renames, explicit verification changes
and deterministic edge IDs are reported per field. Original source payloads remain
in their frozen files; JSON pointers/canonical-source hashes identify every output.
Raw-byte hashes and semantic canonical-JSON hashes are distinct in input-manifest.
The bundle's manifest hashes every public NodeRecord/EdgeRecord identity/content.

created_at/updated_at describe actual captured conversion/materialization time.
Historical reported/observed/recorded/started/completed timestamps are preserved,
not guessed from metadata. Actual import start/end and mutation times are separate
in reports and repository audit. Reuse the same compiled bundle for repeat imports;
repreparing with a new materialization clock is a new version and conflicts with
existing same-ID content unless an explicit change policy is reviewed.

Incomplete VERIFIED inventory claims become explicitly CANDIDATE relationships /
UNVERIFIED Evidence, retaining originals in conversion reports. Missing observed_at
is not filled from recorded_at. Import receipts are UNVERIFIED provenance, never
physical evidence. Existing truly dated/attributed verified associations retain
status and must pass repository proof rules. No new physical link is derived from
coordinates or source text. Source cycle exceptions require separate domain review;
this importer does not grant inspection authority from fixture fields.

Document nodes refer to the18 actual hash-verified supplied Markdown files; no PDF
or inspection result is invented. GraphRAG indexing/owner-version policy is B11.
Observation source provenance is an external JSON pointer/receipt; the schema has
no arbitrary Observation.source_record_id field, so none is invented.

## Visibility and scenario readiness

Converter/importer never read catalogs, hidden truth or reveal payloads. Forbidden
answer keys and unknown envelope fields fail; noninitial/future observations and
undeclared inspection stages are quarantined. The supplied historical INS-ROAD-PAST
is retained as history. Offline audit/readiness tools read scenario files solely to
report IDs/counts/gaps and opaque release hashes/references, never import titles,
expected decisions, hidden causes or reveal text. release-manifest is not an injector.
Runtime mount/tool isolation and authorized release remain B19 and are not claimed
complete by this file separation. Untrusted evidence text is data, never executable.

scenario-readiness.json covers S01–S12 with incidents/complaints, actual versus bound
assets/clusters, evidence, topology references and missing history. In particular,
S07 has no complete recorded waste/drain/road SERVES chain. Its creation requires
legitimate additional source authoring in B19, not spatial inference in B04. Importer
path tests use clearly marked, explicit purpose-built test networks, not invented
municipal evidence. No scenario behavior is claimed working.

## Import and failure flow

`__main__ -> conversion.validate_bundle -> check_graph + Registry -> dependency-
ordered nodes -> Importer -> GraphRepository.create/get -> fenced intent/commit +
audit/revision`. Equal hashes are no-ops, even under concurrent equal imports;
changed content conflicts explicitly. Source errors fail before writes. Commit
outcome uncertainty stops immediately with a separate error classification; never
automatically retry a possibly committed mutation. Explicit proof-driven repository
recovery followed by rerun reconciles an unchanged prefix. The graph itself, stable
IDs and hashes supply resumable progress; no whole-import atomic transaction is
claimed. Completed records persist if a later record fails. No bulk Cypher is used.

Complete imports verify every content hash, node/edge counts, pending state, audit
entries and revision. Unexpected extra graph records cause failure, never deletion.
A new source version must get an explicit conflict/update/version decision; B04
implements conflict only, not automatic overwrites. Framework/domain errors remain
redacted where credentials could appear. Target naming is not enterprise RBAC.

## Reproduction (repository root)

```sh
backend/.venv/bin/python scripts/generate_demo_seed.py
PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion audit
PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion prepare --documents
backend/.venv/bin/python -m pytest backend/tests/unit/test_ingestion_conversion.py -v
backend/.venv/bin/python -m pytest backend/tests/integration/test_ingestion.py -v -s
PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion.benchmark --retain-last
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence
make test-spec
```

For a particular already authorized B04 UUID graph, CLI import takes --graph,
--bundle and --report; no caller Cypher or canonical target is accepted. Use the
compiled bundle from data/ingestion rather than rerunning prepare between repeats.

## Benchmark interpretation

Follow B04_BENCHMARK_PLAN.md: one coherent pilot, three fresh full imports, two equal
repeats per graph. Instrumentation measures wall/latency/throughput, graph revision,
audit bytes/checkpoints, policy scan maxima, Python traced peak, server memory and
AOF byte growth. Instrumented timings include tracemalloc and parameter-byte-counting
overhead; storage growth is server-wide over each isolated measurement interval,
not a claim of per-record physical disk allocation. Failures retain their new graph.
Successful scratch graphs are cleaned individually; the last full graph may be
retained for review. No existing graph or volume is removed. Targets are provisional;
report slower results and bottlenecks instead of bypassing integrity or audit.

## Verified numeric transport boundary

DEC-016 records parameterized real `RETURN $x` probes: FalkorDB6.0.2 exposes15
significant decimal digits for floats here. Only generated latitude/longitude binary
residue is explicitly normalized, with original and converted fields retained in
reports. Non-coordinate precision that cannot roundtrip is quarantined; no measurement
rounding/tolerant content-hash comparison is introduced. All55 measurement values,
units and dates match the frozen source exactly. The first failed pilot graph is
retained as evidence; its original content is not silently rewritten.

Additional benchmark-plan counters (cycle visited-state/comparison totals, schedule
pair totals and lock-acquire wait distribution) are not instrumented in this B04
runner. Largest actual same-kind scans and graph query totals are measured; these
must not be represented as those unmeasured counters. No performance optimization
or audit-journal migration is included.

Graph-query call/parameter counters cover the complete trial including both repeats;
initial latency/wall/memory/storage fields cover the initial import only. Equal
records avoid domain mutations and keep revision/audit unchanged; explicit
recover_pending may still acquire a lock and advance the internal writer fence.
Neither “zero graph commands” nor “zero disk writes” is claimed for repeat runs.
