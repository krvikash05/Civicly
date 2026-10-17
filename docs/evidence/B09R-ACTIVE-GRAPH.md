# Active graph integration gate — B09-R review

Status: **OPEN before B10 live investigator acceptance**, not hidden by isolated PASS.
No canonical promotion, graph merge, ACL widening or runtime source change occurred.

## Current source of truth

- Imported municipal source: retained B04 `civicly_b04_test_a84beda80da64aacbc367a9399e07a97`,858 nodes/1246 edges/revision2104,42 CANDIDATE drainage links. Frozen conversion/source provenance remains authoritative for that imported snapshot.
- `civicly_knowledge`: migration0001 READY, no municipal seed/domain records. Common allowed B08/B09 writable domain target, not an active integrated city yet.
- B08 intake: canonical or validated B08 disposable target; narrow batch writer also restricts phase prefix.
- B09: canonical or validated B09 disposable target; narrow writer rejects retained sources and B08 target writes.
- Official MCP and domain runtime: source exact retained B04 graph via `app.mcp.runtime.CITY_GRAPH`; read-only ACL grants only that exact graph. Domain ToolExecution storage is a separate explicitly scoped B07 trace graph with compatible0002.
- B09/B09-R tests: genuine B08 intake records copied with exact IDs/hashes into a newly owned B09 graph. Test-only MCP server explicitly injects that B09 source. This is real MCP readback, but is **not** same-graph complaint intake through production runtime.

## Verified incompatibilities

1. A new B08 complaint in an isolated B08 graph cannot be investigated by a B09 write service there; phase guard deliberately refuses it.
2. B08 intake cannot write to an isolated B09 graph. Copying records is a labeled fixture procedure, not application synchronization.
3. Production MCP cannot see those new complaint/investigation IDs because its read identity and ACL point to the retained city graph.
4. Canonical is the common write target, so the intended combined application is possible; its domain seed and MCP source binding still need review. No B10 LangGraph orchestration should mistake isolated test graphs for a coordinated active source.

## Reproducible acceptance plan (future, explicitly reviewed prerequisite)

Do not execute city promotion as part of B09-R. At the B10 integration prerequisite:

1. Record one explicit active-domain target and data origin. Prefer the existing canonical target after a separately reviewed additive, repeatable import using B04 converter/importer; preserve retained source fingerprints, IDs and all42 candidate links. Alternative: an explicit narrow shared disposable integration-target policy with new guard tests; do not simply widen all phase prefixes.
2. Make official/domain MCP source selection a single trusted application configuration and provision read-only credentials for that exact target. Keep trace graph/credential separate. No caller/agent-selectable graph or arbitrary Cypher. Verify old unrelated graph denial and admin/mutation denial.
3. In an explicitly owned graph under that reviewed policy, apply0001, verify indexes/constraints READY, import canonical B04 artifact, verify counts/hashes and repeat-import no-op. Do not move or reset retained data.
4. Call `ComplaintService(GraphRepository(db, active), clock=controlled_clock).intake(authored_payload)`; repeat identical intake and confirm same IDs. Submit ongoing and resolved-then-recurring variants; validate B08 classifications and primary cluster rules.
5. On the same repository call `EvidenceService.execute(open, typed_actor)`, `propose`, request/transition/report inspections, then `assess` with current CAS. Validate graph identity, explicit incident IDs, per-record provenance, v2 categories and immutable history. Do not assert verified root cause from city candidate links.
6. Initialize actual official and domain MCP clients through their brokers, tools/list then tools/call. Read the exact new IDs with existing complaint/history/evidence tools; verify source graph, revision progression, typed output, per-record evidence and durable ToolExecution trace. If a dedicated assessment-history read tool is needed, review inventory/schema change rather than pretend the existing tool returns the full v2 assessment.
7. Prove RO tools cannot mutate, cannot access original retained/counterfactual/trace graph keys, and reject unauthorized tools. Preserve budgets, candidate separation, hashes, scope and cutoff semantics.
8. Restart/recreate existing Compose service preserving volumes, restore exact-graph ACLs, re-read complaint/investigation/assessment/trace and verify idempotent replay/CAS. Only after this gate connect the B10 approved broker to a live agent checkpoint; API/SSE remains its later milestone.

Reproduce the present limitation from source guards in `app/services/complaints/service.py:write_target`, `complaints/writer.py:Writer.commit`, `evidence/writer.py:target` and `mcp/runtime.py:CITY_GRAPH`. Existing negative integration tests exercise protected write targets and exact graph-key ACL denial. `B09R-runtime-proof.json` and the unchanged B09 real MCP inspection test demonstrate labeled source-preserving fixture integration only.

Earliest gate: **B10 prerequisite, before live investigator end-to-end acceptance**. Requires human review of target/configuration policy and source promotion; no new authorization inferred here. All18 product requirements remain binding. This limitation does not negate the independently tested B09-R evidence semantics.
