# implementation_status.md — Current implementation truth

## Current status — B09-R, 2026-10-18 (takes precedence over every historical status)

B09-R PASS — human review pending. Local accepted B09 baseline `688b893`, no push.
Final617 PASS/0 FAIL/0 SKIP in746.62s:382 unit/235 real FalkorDB/MCP integration,
including all582 original tests unchanged plus19 unit/16 integration. Both SPEC
validators PASS. Actual restart/recreation and Browser persistence PASS. Original
B01/B04/B05/B08/B09 sources/history, registryv3/0001/0002 and101 accepted trace
observation checks preserved. Corrected v1->v2 fixture exact pre/post fingerprint/history
PASS. No B10 work or city/canonical promotion; all42 drainage links CANDIDATE.
Active-graph gate remains OPEN before B10 live investigator acceptance; details and
reproducible plan in docs/evidence/B09R-ACTIVE-GRAPH.md. All18 requirements binding.

## Current status — B09, 2026-10-17 (takes precedence over all history)

B08 externally accepted; local baseline00d98745. B09 PASS — human review pending.
Final582 PASS/0 FAIL/0 SKIP in705.39s:363 pure unit/219 integration; adds37 unit+38
real FalkorDB/MCP cases. All507 baseline tests rerun; one documented prerequisite
trace-test cap correction, no test removed. Both SPEC validators PASS. Retained B09
62-node/46-edge/revision82 graph, original B08 intake/source/city/B01/B05 and70 accepted
trace observations preserved across real restart/recreation. Fresh official/domain
MCP proofs PASS; source frozen, registry/0001/pins unchanged; no B10 work. All18
requirements remain binding; this is a domain foundation, not a complete agent app.


## Historical B09 in-progress summary | 2026-10-17

B08 externally accepted; local baseline00d98745. B09 evidence/hypothesis/inspection
services implemented; strengthened real verification running. No B10 or later work.
Baseline506 PASS/1 FAIL (trace-test unrelated-row cap), corrected target1 PASS; both
SPEC validators and retained fingerprints PASS. This is not a507-pass single run.
Final full regression/persistence/SPEC gates pending; all18 requirements remain binding.


## Current status — B08, 2026-10-17 (takes precedence over history)

B07-R accepted; clean local baseline6afdd09. B08 PASS — human review pending. Final507 PASS/0 FAIL/0 SKIP in438.89s (326 unit/181 real integration), adding33 unit+34 real cases; all440 accepted tests unchanged. Both SPEC validators PASS. Typed source-preserving intake, three validators, qualified incident/cluster rules, concurrent idempotence, atomic rollback/unknown-write recovery and reviewed temporal correction verified. Actual B08 journals/chains survive restart/recreation; city/B01/B05/migrations/accepted MCP traces unchanged. No B09+ work; all18 requirements remain mandatory.

## Current status — B07-R, 2026-10-17 (takes precedence over history)

B07 technically accepted. B07-R PASS — human review pending. Final440 PASS/0 FAIL/0 SKIP in368.60s (293 unit/147 real integration), adding5 unit+9 real cases; all426 accepted tests preserved. Both SPEC validators PASS. Independent maintenance provenance, pre-cap UTC history filtering/order/lookahead, and explicit unknown work-order fields verified through real MCP. Retained city/B01/B05/migrations/accepted+corrective traces preserved across actual restart/recreation. B08 TODO; no later work.

## Current status — B07, 2026-10-17 (takes precedence over history)

B07 implemented/verified: actual custom Python MCP,12 READ handlers, official/domain namespaces, synchronized envelopes and graph-backed ToolExecution observations via isolated compatible0002.426 PASS/0 FAIL/0 SKIP; both SPEC validators PASS. Credential rotation verified; city/0001/registry/B01/B05 evidence preserved. No agent/GraphRAG/operations/API/frontend capability claimed complete. STOP for B07 review.

## Current status — B06, 2026-10-17 (takes precedence over history)

B06 implemented and verified: official Node1.3.0/Python MCP2.3.0 private stdio, four allowlisted read tools, graph-scoped DB ACL, strict templates and sanitized traces.361 PASS/0 FAIL/0 SKIP; both SPEC validators PASS. B01/B04/B05 retained fingerprints and canonical0001 readiness unchanged. No agent/custom MCP/GraphRAG/operations/API/frontend feature claimed complete. STOP for B06 review.

## Current status — B05, 2026-10-17 (takes precedence over history)

B05 implemented/tested:bounded graph algorithms, transparent historical case retrieval, factory-owned counterfactuals and actual-city/source-dependency reports.309 PASS/0 FAIL/0 SKIP; both SPEC validators PASS. B04 data/registry/0001 and original B01/canonical evidence preserved. No causal scenario, agent/MCP/GraphRAG/operations/API/frontend capability claimed complete. STOP for human B05 review.

---

As supplied: **specification only**. No backend/runtime functionality has been implemented or exercised as part of this package.

- Last completed task: None.
- Current task: B00 pending.
- Code written: Blueprint files and specification validators only.
- FalkorDB integration tested: NO.
- LangGraph checkpoint restart tested: NO.
- Runtime MCP client/server tested: NO.
- GraphRAG SDK ingestion tested: NO.
- End-to-end civic investigation tested: NO.
- Frontend built: NO; intentionally deferred.

Per task, update: implemented paths, exact tests, pass/fail/skip, screenshots/log traces, active blockers, known limitations, next single task.

## B00 result | 2026-10-17 (supersedes initial pending status)
- Last completed: B00 audit; human review pending. Next: B01 TODO, only after user continues.
- All R01–R18 preserved. No application code added; FalkorDB/MCP/LangGraph/GraphRAG/API/live-agent functionality NOT IMPLEMENTED / NOT TESTED.
- SPEC validators PASS on Python 3.12.1/jsonschema 4.26.0: 42 entities, 47 relationships, 18 MCP tools, 9 machines, 43 planned API routes, 57 schemas, 20 events, 838 expanded nodes/1245 edges, 12 scenarios, 18 documents. Legacy validator separately covers 4 scenarios and 40 nodes/50 edges.
- Extra property audit FAIL: 55 unknown Observation.value_number fields. Five scripts parse; original 73 manifest hashes matched. No overall semantic correctness claimed.
- Environment: macOS 26.5 arm64; Python 3.12.1/3.14.7; Node 24.21.0/npm 12.2.0; Docker Desktop 4.95.0/Engine 29.8.2 running; Compose 5.6.0. python alias/uv/redis-cli absent; no Git repo.
- Inspected Python 3.12 lacks falkordb/langgraph/langchain-falkordb/mcp/graphrag-sdk/pytest; selected provider/model/key variables unset. B01 setup and later live-provider configuration required.
- Open contract/fixture risks: DEC-004 and BLOCK-B00-02. B00 completion is audit completion, not backend acceptance.

## B01 result | 2026-10-17 (current; supersedes earlier pending statuses)
- B00 accepted by user. Last completed: B01 backend foundation/runtime setup; B01 human review pending. Next B02 TODO; STOP until user continues.
- Implemented: Git initialization, Python 3.12 isolated package/dependency lock, validated settings, official-client connection lifecycle, redacted typed CLI foundation health, pinned Compose FalkorDB+Browser with graph/Browser named volumes and generated persistent local Browser secrets.
- Verification: 15 automated tests PASS (7 unit/framework compatibility, 7 real DB/Browser/CLI integration, 1 real restart+recreation lifecycle); both supplied SPEC validators PASS; clean frozen-lock environment installs and compatibility checks PASS. Earlier two integration health failures fixed honestly and recorded in test_log.
- Real DB: parameterized CREATE/MATCH PASS; RO_QUERY CREATE/SET/DELETE denied and row unchanged. Persistence PASS after restart and replacement container; Browser volume/HTTP also PASS; real Browser logged-in query displays persisted synthetic node.
- Versions: Python 3.12.1; official client 1.8.0/redis client 8.1.0; graph server 6.0.2/Redis 8.10.2/Browser 2.6.1. Full pins and immutable image digest in DEC-006/uv.lock/compose.yaml.
- Canonical civicly_knowledge remains uninitialized; CLI reports this, not graph-read success. Only isolated B01 probe graph retained. No supplied domain data/schema/contracts modified.
- All R01–R18 retained, not completed. Migrations B02, repositories B03, fixture corrections/import B04, MCP B06/B07, checkpoint/agents B10, GraphRAG B11, approvals B13, durable events B15, API B16+ and full CLI B18 remain unimplemented/unverified. No frontend.
- BLOCK-B00-02 stays OPEN including all 55 value_number discrepancies and every DEC-004 finding. Provider credentials unset; live tests remain unverified. No active B01 blocker.

## B02 acceptance record | 2026-10-17
- B00/B01 human accepted. Last completed B02; human review pending. Next B03 TODO; STOP before starting.
- Implemented: canonical registry v3 scope/edge metadata, strict validation + multi-label/point schema adapter, frozen migration0001, additive checksummed lease-protected runner, durable status/audit, schema CLI/Make targets, real integration/failure/recovery tests and recovery guide.
- Canonical civicly_knowledge: migration version1 READY, registry3, 91 OPERATIONAL index groups/304 property entries, 182 OPERATIONAL constraints. Canonical domain nodes=0. B01 probe unchanged. Schema survives actual restart/recreation.
- Final tests 53 PASS/0 FAIL/0 SKIP; both specification validators PASS with explicit legacy/import-blocker warnings. Earlier spike/test failures recorded, not hidden. No dependency changes; real database/client versions remain B01 pins.
- Scope inconsistency resolved; all 42 node/47 relationship names/endpoints and enum values preserved. Registry additions are documented v3 requirements, not silent data coercion. All supplied fixtures/data and R01–R18 document unchanged.
- BLOCK-B00-02 remains OPEN for 55 Observation fields and other deferred findings. B03 graph-aware repositories/policies, B04 conversion/ingestion, runtime MCP, agents/memory/GraphRAG, approvals, durable events/API/SSE, E2E and frontend remain unimplemented/unverified. No product capability declared complete by schema alone.

## B03 result | 2026-10-17
- B02 accepted by user; local clean baseline3db6d873fb494a5ce456cb5d04a84f2be50919d4,
  no push. B03 implemented; human review pending. Next task B04 only after acceptance.
- Actual source: typed node/edge/path/query/result models; strict graph repository
  create/get/update/relationship methods; graph-aware references/evidence/scope/
  identity/temporal/cardinality/cycle policies; fenced per-graph writers, CAS and
  pending/audit/revision recovery; eight finite GRAPH.RO_QUERY templates. See
  backend/GRAPH_ACCESS.md and contracts/graph_access.json for limits/imports.
- All89 acceptance tests PASS (45 unit +44 real integration, including lifecycle);
  old53 B01/B02 regressions retained. B03 adds12 unit +24 real integration tests.
  Both SPEC validators, dependency consistency and lock check PASS. Failures and
  corrected fixture/test/runtime assumptions remain recorded in test_log.md.
- Installed upstream metadata projection issue avoided through pre/post monotonic
  revision checks; future source-evidence dates on candidate paths filtered. Real
  examples/EXPLAIN plans in B03-runtime.json. Equal coordinates without explicit
  network links yield no cross-category path; path context never asserts causation.
- Canonical registry3 / migration0001 still READY,91 index groups/182 constraints
  OPERATIONAL,0 domain nodes. Original B01 probe and graph/Browser volumes retained.
  No full city seed or hidden evaluation data consumed.
- Still unimplemented: full fixture conversion/import, behavioral agent decisions,
  MCP runtime, LangGraph/checkpoint memory, GraphRAG, operations/approval/outbox,
  API/SSE/frontend and B-END. Repository foundation completes no product objective
  by itself; all R01–R18 remain mandatory. BLOCK-B00-02 and deferred DEC-004 remain.

## B03-R corrective review implementation | 2026-10-17
- B03 provisionally accepted; B03-R is the only active work. Registry v3 and immutable
  migration0001 unchanged. Existing B01/B02/B03 tests are preserved.
- Implemented outgoing primary IN_ZONE/PART_OF, per-route/service effective schedule
  interval conflicts and guarded endpoint edits. Defaults/grammar now budget total
  path hops with explicit template minima and typed bounded-search result metadata.
  Shared milestone02–25 UUIDv4 target guard replaces divergent hardcoded B02/B03
  allowlists. B04 benchmark documentation only; no importer/bulk shortcuts.
- Verification pending final full regression; prior89 tests remain historical PASS.
  Original review package remains an immutable snapshot of pre-correction B03.
  All18 product requirements and deferred DEC-004 findings remain binding/open.

## B03-R acceptance result (supersedes in-progress entry) | 2026-10-17
- 135 PASS /0 FAIL /0 SKIP:77 unit and58 real integration, including real retained-
 volume restart/recreation. All previous89 tests unchanged;32 unit and14 integration
 added. Strengthened template suite22 PASS; both SPEC validators and package/lock
 checks PASS. No recorded B03-R test failure or skipped required runtime check.
- Post-lifecycle canonical0001 READY, registry3,91 index groups/182 constraints
 OPERATIONAL,0 domain nodes, original B01 probe retained; Browser HTTP200. Updated
 eight live query examples and EXPLAIN plans include actual budget metadata.
- No converter/importer/seed/bulk shortcut, MCP/agent/GraphRAG, business workflow,
 API/frontend implemented. B04 benchmark execution and all remaining product gates
 unverified. Original55 defects and remaining DEC-004 findings remain OPEN.
- B03-R complete for human review, not human-accepted. B04 remains TODO and blocked
 on explicit continuation. Source changes remain local/uncommitted; no push.

## B04 implementation delivered for review | 2026-10-17
- Implemented only dataset audit/versioned conversion, corrected independent synthetic
  generator revision, strict manifests, staged/evaluator exclusion, validated
  dependency-ordered repository import, deterministic identities, exact no-op/conflict
  behavior, resumable prefix/failure reports and real performance runner. Current
  source and originals are distinguishable and hash-attributed; no registry or0001 edit.
- 858node/1246edge reviewed runtime bundle; actual three full imports verified every
  hash/count, repeated twice without domain/revision/audit changes. Final isolated
  graph civicly_b04_test_a84beda80da64aacbc367a9399e07a97 retained for human review.
  Canonical promotion not performed. Both original B01 evidence and retained volumes
  remain intact, with lifecycle regressions exercised. See evidence for final checks.
- All42node/47edge types exercised by unit and real importer tests; all55 original
  measurements preserved. Inline enum validation now enforces existing registry enum
  declarations; no public entity, enum, relationship or migration changed.
- Runtime source has24node/23edge types; absence of other domain types is reported,
  not seeded with invented history.18 actual MD source references, no fake PDFs.
  Physical topology is unchanged and unsupported verification is explicitly qualified.
- R01–R18 remain mandatory. This phase supplies graph data support, not completed
  complaint/recurrence/agent/scenario behavior. B05 algorithms, MCP, agents/memory,
  GraphRAG, approval/operations/events/API/frontend remain unimplemented later gates.
- Final post-recreation CLI rerun matched2104/created0, exact full content hash and
  node858/edge1246 counts retained; revision/audit2104 unchanged. Fresh original
  B01-PERSISTENCE row preserved. Canonical0001 READY,91 index groups/182 constraints,
 0 domain nodes; Browser lifecycle HTTP200/storage checks PASS. Runtime evidence
  in B04-retained-post-recreation.json, B04-runtime.json and B04-canonical-status.json.

## B05 implemented and verified | 2026-10-17
- Eight new app/graph/analysis modules:typed models/fixed reader, deterministic
  reachability/shared/impact/criticality/components/dependencies/task DAG, historical
  retrieval, owned counterfactuals, city evaluator/review CLI. New algorithm contract,
  purpose-built fixture,29 unit +22 real integration cases, benchmark/review packager.
  Baseline8aaf17c local only; source changes uncommitted for review, no push.
- Existing physical registry v3, migration0001, graph access/ingestion contracts,
  B04 city/legacy fixtures/generator/pins and all prior258 tests unchanged. No source
  writes by algorithms/evaluation/benchmark; cloned mutations retain fence/CAS/intent/
  audit/proof safeguards. Exact clone ledger/source hashes checked before/after.
- Actual controlled source29nodes/28edges revision/audit57 preserved. Remove CUT:
  reachability D1:D2/D3/D5→D2; criticality D1(3),D4(2)→D4(2),D1(1); impact D2:D3/D5→none;
  shared bottlenecks D2/D3/D5→D2. Candidate replacement restores exploratory only;
  verified-only stays changed. Nearby/expired/future-proof negatives validated.
- City858nodes/1246edges revision/audit2104 unchanged. Verified physical drainage
  empty; all42 DRAINS_TO candidate. Exploratory D12→D18 and1 ROAD-R08 inspection
  context available. No historical WorkOrder/AgentDecision/InterventionOutcome chain.
  All12 provide some weak/exploratory context,0 verified causal scenario readiness.
- Actual-city dependency report:4 broader investigative asset sets;8 starting-asset
  conflicts requiring author confirmation;6 primary-cluster conflicts;3 unspecified
  contexts.55 Observations unlinked/S07 topology missing/schedule+document gaps remain
  for B08/B09/B11/B19. No automatic source correction or verification promotion.
- Final309 PASS (218 unit/91 real integration),0 FAIL/0 SKIP; both SPEC validators PASS.
 260 read-only benchmark analyses across26 workloads:internal wall medians2.743–27.628ms;
  complete small clone2.318s including migration/copy/verification. Not global-city
  centrality, statistical SLA, hydraulic proof, live agent latency or memory peak.
- B06 is proposed official MCP read-only client/server/tool allowlist/auth verification
  only after human acceptance. No MCP, LangGraph/GraphRAG, full memory, planning,
  approvals, operations, domain API/frontend implemented. All18 requirements retained.
- Post-final-recreation verification PASS:accepted city full content/audit/writer-state
  hashes identical to B05 baseline;2104 records/revision/audit. Retained controlled
  source57 unchanged and owned clone59 retained. Original B01-PERSISTENCE row intact;
  canonical0 domain nodes/0001 READY/91 index groups/182 OPERATIONAL constraints.
  See B05-post-lifecycle.json and B05-canonical-status.json. Review ZIP integrity/
  actual-source bytes/secret audit PASS; isolated extraction imports its own source
  and reproduces51 focused B05 tests PASS in88.60s. No source/volume reset.

## B06 implemented scope | 2026-10-17
- Actual official @falkordb/mcpserver1.3.0 dependency locked with npm; Python SDK2.3.0
  pinned/uv-locked. Node24.21.0/npm12.2.0; Node client6.8.0/TS MCP SDK1.32.1. Existing
  FalkorDB6.0.2, all original direct Python pins/registry0001 preserved.
- Real private stdio initialize negotiates2025-11-25, tools/list7 signatures checked,
 4 approved read tools with strict safe request schema and fixed query templates.
  No list_graphs/query_graph/delete_graph or arbitrary Cypher agent surface.
- DB ACL exact accepted B04 city graph; PING/INFO/GRAPH.RO_QUERY/CLIENT SETINFO only.
  Real mutation/admin/other-key denial. No HTTP listener; bearer auth not applicable.
- Raw current node/validity-filtered one-edge records preserve IDs/source/status/date
  context; candidate-only city not promoted. Actual revision2104 before/after, typed
  projections and independent Python equality. B05 decision-grade algorithms unchanged.
- Owned child/session cleanup, downtime/fresh reconnect, actual stalled-server timeout,
  invalid arguments/auth and bounded calls tested. Unit malformed outputs/revision
  injection clearly labeled; local corruption after a real MCP read separately tested.
- Sanitized process-local tool metadata and operator JSON; graph-backed common traces
  deferred B07/B17. No live model/agent choice or complete product capability claimed.

B06 final verification:361 PASS/0 FAIL/0 SKIP in329.97s (255 unit/106 real integration);
all original309 tests unchanged. Both SPEC validators PASS. Live proof after actual
recreation and ACL reprovision PASS; full city2104 record/revision/audit/writer hashes,
original B01 row and retained B05 source57/clone59 unchanged. Canonical0001 READY with
91 index groups/182 OPERATIONAL constraints. Security/source/process audit PASS.
Exact paths/diff/commands in B06-FILES.md/B06-changes.patch/B06-COMMANDS.md. No B06 ZIP
or remote push. STOP — human review required before B07.

## B07 implemented read/runtime foundation | 2026-10-17
- Verified credential rotation before integration; accepted B06 local baseline24e8072.
-12 actual custom READ handlers;6 future write handlers unregistered/denied. B05
  cases/reachability +B03 maintenance reused; fixed bounded registered-history reads.
  Unsupported later capabilities/unlinked observations explicit UNAVAILABLE/gaps.
- Actual Python SDK2.3.0 server civicly-domain1.0.0/private stdio. Domain/official
  namespace router, strict discovery/input/output/scope/budget/permission checks.
- Shared MCP schema3/context/result/provenance/revision/error/limits; AgentTraceEvent
  metadata aligned without API implementation. rationale null, no model selected tool.
- Separate B07 trace graph, immutable0001/registryv3 compatibility; storage adjunct0002
  adds2 indexes/4 constraints with own checksummed ledger and operational readiness.
  Controlled fenced atomic ToolExecution+detail/hash and parented broker observations;
  source credentials cannot write, trace credentials cannot access city.
- Unit/real negatives, transient/partial/failed migration, trace idempotence/persistence
  and failure refusal tested. Final full regression/review pending; no B08+ work.

B07 final gate:426 PASS/0 FAIL/0 SKIP in350.75s (288unit/138real); both SPEC validators
PASS. Actual post-recreation MCP proof initializes civicly-domain1.0.0/protocol2025-11-25,
lists12 schemas and reads all12 handlers plus candidate/typed examples.15 server
observations verified;13 preexisting traces survived recreation. Isolated trace0002
READY (2 index groups/4 constraints added;93/186 total). Source city2104 record hashes/
audit/writer state, original B01 and retained B05 source/clone unchanged; canonical
0001 READY91/182. Credential rotation/source/secret/process audit PASS. No B07 ZIP,
remote push or later work. STOP — human review required before B08.

## B07-R narrow corrective implementation | 2026-10-17

B07 technically accepted. Corrected per-event maintenance evidence, chronological
windowed pickup/condition retrieval before cap, and explicit unknown work-order
relationship placeholders. Preserved wire schemas/shared envelopes/trace architecture.
New5 structural unit and9 real DB/MCP cases PASS focused; full regression pending.
Only service/server projections, contract semantic descriptions and review evidence
changed; all B03–B06 source/algorithms/policies/migrations/dataset remain protected.
No B08 business logic or product completion claim. All18 requirements remain binding.

### B07-R final gate (supersedes pending entry)

440 PASS/0 FAIL/0 SKIP in368.60s;293 unit/147 real DB/MCP integration. Adds5 unit+9
real tests;426 previous tests unchanged. Both SPEC validators PASS. Fresh actual-city
MCP proof12 tools/no ERROR +15 readback observations; all retained city/B01/B05 hashes
and migrations unchanged. Accepted and corrective trace persistence after lifecycle
verified;333 old files outside11 deliberate modifications unchanged, wire schemas/
permissions/pins preserved and actual local-secret/process audit PASS. All six tracking
files +guide/contracts/evidence updated. B07-R PASS, awaiting human review; B08 unstarted.

## B08 implemented scope (verification running)

Strict typed intake +first raw/canonical source preservation, supported UTC/decimal
units, three evidence-aware validators, deterministic complaint/incident/cluster rules
with dated explanations/uncertainty. Safe two-phase journal +single atomic domain batch,
source identity retries/conflicts, CAS reviewed temporal regrouping and explicit recovery.
B03/B05 reused; B04 city read-only previews; B06/B07 read tools/traces untouched.
No new dependency/migration/public ontology or B09+ feature. Final507 regression pending.

### B08 final gate (supersedes in-progress entry)

507 PASS/0 FAIL/0 SKIP in438.89s (326unit/181real), all440 prior tests unchanged; new
33 unit/34 actual DB-MCP cases. Both SPEC validators PASS. Actual retained B08 graph
5 complaints/4 incidents/2 clusters (26nodes/23edges/rev26) and journals survive
restart/recreation;5 replays no domain changes. Qualified city preview/production
MCP12 tools/no ERROR/15 traces and43 accepted observations/source fingerprints PASS.
358 old files/locks/registry/migrations/algorithms/MCP preserved; private-value/process
audit PASS. No B09+, canonical seed promotion, public API/auth, agents or event outbox.
Human review pending; limitations in COMPLAINTS.md and B08-RESULTS.md remain binding.

## B09 verified implementation | 2026-10-17
Typed evidence/hypothesis/inspection service, explicit rulev1 and append-only histories
implemented through unchanged B03 persistence/B05 reads. Actual independent synthetic
reports verify all3 categories; contradictions/unknowns/future evidence/candidate and
substituted topology fail safely; native rollback/concurrency/uncertain-write and real
SDK/broker provenance pass.582 PASS/0 FAIL/0 SKIP705.39s; both SPEC validators PASS.
Retained source/B09/old B08/B01/city/B05/native migrations/accepted traces survive real
restart/recreation. Fresh official/domain MCP proofs PASS. No schema/pin/data/MCP
implementation changes; accepted tests retained, one baseline test-cap correction.
Active-graph integration/public auth/dispatch/events/agent/memory/GraphRAG/API remain
future gates. B09 human review pending; B10 not begun.

## B09-R implemented boundary | 2026-10-18
Implemented: rule-v2 authority/meaning categories and per-occurrence coverage, strict
version-aware models, explicit retrospective source basis and disjoint source lineage;
immutable v1 decode/replay and appended correction. Domain write/fence/CAS/journal
path unchanged. Actual MCP reads v2 reports without inventory/envelope change.
No registry/migration/dependency/repository/algorithm/B08/MCP runtime modification.
See B09R-FILES.md for exact inventory and B09R-changes.patch for source/document diff.
No B10 orchestration/memory/GraphRAG/planning/API/frontend implementation.
