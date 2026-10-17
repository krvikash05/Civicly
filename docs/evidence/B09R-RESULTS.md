# B09-R corrective review results

Current disposition: **PASS — human review pending**. All criteria A–J satisfied
with the expressly allowed documented active-graph gate before B10 live investigator
acceptance. All18 requirements remain mandatory. No B10 or later implementation.
Accepted baseline688b893; no push. Final **617 PASS/0 FAIL/0 SKIP** in746.62s:
**382 unit/235 real integration**, preserving582 prior tests plus19 unit/16 integration.
Both SPEC validators and actual restart/recreation, retained sources, immutable
history and101 accepted trace-observation checks PASS.

## Root causes and corrected persisted behavior

| Finding | Accepted B09 real reproduction | B09-R same real reproduction |
|---|---|---|
| A: asymmetric review authority |One unreviewed DRAIN_CLEAR -> CONTRADICTED assessment, REJECTED hypothesis and CONTRADICTED_BY edge. Falsifier collection did not check review. |INCONCLUSIVE, qualified unreviewed contradiction metadata/gap, no causal contradiction edge; reviewed domain-qualified falsifier can still contradict. |
| B: context recorded as support |AGENT LLM_STATEMENT -> POSSIBLE, supporting_evidence_ids and SUPPORTED_BY despite a context-only gap. |INCONCLUSIVE, explicit contextual reference with source/hash, empty supporting IDs and no support edge. |
| C: earliest start used for all occurrences |Inspection after recorded end -> SUPPORTED. Earliest start/asset/code matching ignored episode end and request association. |INCONCLUSIVE, explicit interval exclusion and no support edge. Actual per-incident request/proposal/affected-asset bindings and [start,end) replace minimum-start matching. |

Exact old/new IDs, persisted assessment/status/edge readback and gaps are in
B09R-before-results.json and B09R-after-results.json. These are actual DB operations
on newly owned fixtures, not mocked successes. Their temporary graphs were removed
only after recorded readback. The separate version1 compatibility fixture is retained.

## Complete rule-v2 decision matrix

| Evidence after provenance, subtype, occurrence and cutoff checks | Assessment | Hypothesis final state |
|---|---|---|
|Context only, excluded only, missing, or unreviewed contrary alone |INCONCLUSIVE |INCONCLUSIVE |
|Unreviewed discriminating positive alone |POSSIBLE |UNDER_REVIEW |
|Reviewed discriminating positive, incomplete criteria/independence/topology |SUPPORTED |SUPPORTED |
|Reviewed approved falsifier, no conflicting positive claim |CONTRADICTED |REJECTED |
|Any relevant positive/negative unresolved conflict, including unreviewed contrary |INCONCLUSIVE |INCONCLUSIVE |
|Approved complete confirming observations + independent reviewed corroboration for each explained incident + required verified untruncated topology + no contrary conflict |VERIFIED |VERIFIED |

The graph source lists/edges contain reviewed discriminating evidence only. Unreviewed
positive/negative, context and exclusions remain separate typed metadata. One report
with multiple observations can occupy several categories; each observation has one
category. No probabilities or invented state. Existing state-machine transitions through
UNDER_REVIEW remain enforced. Copied inspector/source records cannot verify, and a
retrospective derivative cannot be its own independent corroborating source.

## Controlled occurrence chronology

The2027 January–September chronology is authored synthetic data in real isolated
FalkorDB, not imported city data or a real municipal operational claim:

1. Actual B08 January road incident; January reviewed direct inspection and assessment.
2. February recorded completed authored repair WorkOrder/ActionTask and explicit
   Incident ACTIVE -> ENDED closure with timestamp, not automatic resolution inference.
3. Actual B08 August intake -> different incident, same primary cluster, RECURRENT.
4. August inspection supports August; excluded for January. January inspection supports
   January; excluded for August. Prior assessment hash unchanged.
5. A hypothesis explaining both occurrences cannot pool one source per occurrence into
   two-source VERIFIED; coverage and independence are checked separately for each.
6. September reviewed retrospective observation explicitly names January and cites its
   reviewed January direct source. It supports the named occurrence, retains basis
   hashes/provenance, and does not create artificial source independence.
7. March cutoff excludes August and September records, source references and future
   report contents, while using the visible February closure version and January source.
8. Independent tests cover unrelated same-asset investigation, late observations for an
   unresolved occurrence, known ended interval, nearby disconnected pipe, candidate-only
   path, actual verified utility path and its expiry. B05 counterfactual removal tests
   remain part of the complete unchanged regression suite.

See B09R-runtime-proof.json for explicit actual IDs, per-observation classifications,
incident lists, edges, revisions, paths, source hashes and state readback. No full city
seed, subtype/ontology invention, or change to B08 grouping policies.

## Version and provenance compatibility

New assessment/rule2 classification is in existing immutable rationale JSON. Optional
explicit-attribution reports use format2. Absent new fields do not appear in v1
serialization or old command hashes. No registry property, relationship, enum or
migration change. Legacy v1 data keeps its historical interpretation, even when its
conclusion was wrong. New correction is an appended assessment referencing previous ID.

The retained B09R compatibility graph starts with a real pre-fix v1 unreviewed rejection;
original receipt and journal replay, then appended v2 INCONCLUSIVE, are exercised and
hashed. The original accepted B09 graph/history is separately verified without mutation.
Real custom MCP discovery and maintenance call validate a v2 report, per-event evidence,
existing schema and durable trace. No dedicated assessment-history MCP tool or agent
selection is invented; typed assessment JSON is ready for a later reviewed adapter.

## Compatibility, scope and limitations

See B09R-COMPATIBILITY.md for B00–B09 checks and B09R-ACTIVE-GRAPH.md for verified target
restrictions and the concrete earliest B10 prerequisite. Canonical is still empty;
production MCP reads retained city. The one-active-graph application chain remains an
explicit gate, not an end-to-end success claim. No source promotion or guard widening.

All42 city drainage links remain CANDIDATE.55 original legacy numeric defects remain
frozen, B04 canonical conversion still validated and55 unlinked observations not
assigned invented locations. Historical source/documents, clock/service/evaluator,
authenticated approval, durable domain events and API findings retain their phases.
Trusted actor/review/independence is conservative demo reasoning, not B13 authentication
or general causal proof. Current mutable versions do not reconstruct historical state;
missing/expired provenance remains unavailable. Finite reader/query/reference budgets,
O(E) integrity scans/O(N) audit and10k audit cap remain; no performance/SLA claim.

B10 readiness is conditional on human approval and the active-graph prerequisite before
live investigator acceptance. B10/LangGraph/checkpoints/memory, B11/GraphRAG, planning,
dispatch/monitoring/events/API/frontend were not implemented in B09-R.

## Final acceptance record

| Criterion | Result | Evidence |
|---|---|---|
|A authority |PASS |Persisted seven-case matrix; unreviewed contrary cannot reject |
|B meaning |PASS |AGENT/narrative/candidate context retains source/hash without causal edge |
|C occurrence |PASS |Actual January/February/August/September fixture and per-incident corroboration |
|D time |PASS |March cutoff excludes August/September knowledge; validated retrospective source |
|E assessment |PASS |All five labels, immutable v1 hashes/replay, appended linked v2 |
|F graph |PASS |Actual bindings, utility root guard, candidate/verified/expired/nearby/counterfactuals, bounded RO |
|G compatibility |PASS |582 old tests/source unchanged; original registry/migrations/city/history/trace checks |
|H verification |PASS |617 tests in746.62s, both validators, actual lifecycle |
|I traceability |PASS |Exact inventory, source diff, raw failures/results, commands/fingerprints/audit |
|J scope |PASS |No B10 or later implementation |

Post-lifecycle original B01/B04/B05/B08/B09 sources preserved. The corrected legacy
fixture has39 nodes/28 edges/revision58, exact identical content/audit/writer fingerprint
and v1/v2 history before/after actual lifecycle. All15 accepted B09 server traces,15
city output hashes and1 fixture broker output survive in addition to70 predecessor
trace observations. These are101 observation checks, not a claim of101 unique executions.

Review entrypoints: B09R-FILES.md, B09R-changes.patch, B09R-test-summary.json,
B09R-regression-tests.txt, B09R-spec-validation.txt and B09R-post-*.json.
B10 foundation is ready for review; live-investigator readiness remains conditional
on human approval and the explicit shared-active-graph prerequisite. STOP after B09-R.
