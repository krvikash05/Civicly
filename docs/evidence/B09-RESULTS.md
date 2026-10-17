# B09 review results

Current: B09 PASS — human review pending. Final582 PASS/0 FAIL/0 SKIP705.39s
(363 unit/219 integration). Both SPEC validators PASS; real lifecycle/MCP/preservation
and source/secret/process gates PASS. Source frozen after DEC-038 topology correction. No B10 work. All18 objectives remain binding.

## Implemented source and behavior

New services.evidence models/policies/reader/writer/service/__init__: strict commands,
actual Incident/ProblemCluster investigation bindings, competing hypotheses/expected
observations, append-only assessments, supporting/contradicting evidence, inspection
requests/transitions/reports/findings and typed current/past-cutoff reads.
Existing registered fields only; no new dependency, registry change or migration.
Parameterization, B03 integrity/identity/temporal checks, fences/CAS/recovery and
B05 algorithms reused. Backend guide and machine contract specify actual behavior.

One prerequisite compatibility correction to an existing test is in local baseline
00d98745: filter exact trace parent before cap instead of arbitrary first1000 rows.
No test removed, no runtime contract weakened, all assertions retained and hash-checked
child readback added. Baseline initial506 PASS/1 FAIL457.46s and corrected target1
PASS4.36s are separate runs, honestly recorded. B09 full run repeats all507 baseline.
See B09-baseline-compatibility.patch and DEC-034.

## Actual retained assessment revision

Working graph `civicly_b09_test_9572cd3133264bf9a1471ee624a1ccca`; original authored B08 source `civicly_b08_test_001a925a1d5f4cdc8c82b9fcf99e4098`.
Copied actual B08 identities and fingerprints are recorded in B09-retained-proof.json.
Investigation `INV-B09-b6cf7fa7c17375dffa64ab323d26c566`; blockage hypothesis `HYP-B09-21ddd5f91e62c68fe556529762144190`, competing capacity `HYP-B09-d422f0d813b6690281f4577ed0d4cb38`.

- `ASSESS-B09-b5983373a99a3cdf975835870e423b0d`: VERIFIED at graph revision68; supporting `EV-REPORT-B09-6bc3a00e1f6acb0a120a365d700a2e59`, `EV-REPORT-B09-cad60653a3f2eea3e0e3c83339561782`; contradicting none.
- `ASSESS-B09-a4b10daaba674febe766657bd21d1d34`: INCONCLUSIVE at graph revision80; supporting `EV-REPORT-B09-6bc3a00e1f6acb0a120a365d700a2e59`, `EV-REPORT-B09-cad60653a3f2eea3e0e3c83339561782`; contradicting `EV-REPORT-B09-87574576b4fb24622f2756bd62691977`.
- `ASSESS-B09-466f1e22d215dc4d70fc0179f55f2143`: SUPPORTED at graph revision82; supporting `EV-REPORT-B09-87574576b4fb24622f2756bd62691977`; contradicting none.

Two independently authored reviewed inspection reports support the first VERIFIED
record. A later clear-drain/capacity finding is automatically discovered even when
omitted from the requested evidence list; new INCONCLUSIVE references the old
assessment. Old assessment hash/source references remain identical. Capacity stays
SUPPORTED from one reviewed report, without sufficient independent corroboration.
No complaint count, high model confidence, work completion or proximity created
these labels. No request generated a completed inspection or authored finding.

Before-lifecycle fingerprint:62 nodes/46 relationships/revision82/audit82, content
45c509caae2510a6dd43a6db1262bbe64ed9c95912e42691aa84c1e7d898579a. Read-only pre-lifecycle verification PASS.
Read-only after-lifecycle fingerprint/source/history verification PASS against the successful582-test lifecycle log.

## Paths and verified/candidate distinction

B09-runtime-proof.json contains actual B05 path IDs/directed edge IDs/as_of/revisions
and attributed Evidence references. Verified WaterPipe→RoadSegment dependency allows
UTILITY_LEAK verification only with reviewed independent confirming observations.
The same candidate edge yields SUPPORTED with an explicit missing verified-path gap.
An authored dated D2_TO_D1_FLOW_TRACED report sources a B03-validated DRAINS_TO edge;
closing that edge's validity changes later assessment paths while preserving original
VERIFIED snapshot. A nearby disconnected asset is refused as a causal subject.
Future-dated evidence is excluded at earlier cutoff; UNKNOWN findings stay insufficient.

Utility topology must originate at the concerned WaterPipe and end at affected
RoadSegment via B05 dependencies. Listing a pipe while substituting an unrelated
verified drain path is rejected in an actual negative graph test (DEC-038).

## Compatibility evidence

Pre-regression preservation PASS: city858 nodes/1246 edges/revision2104/all record
hashes/audit/writer state, B01 original probe, B05 source+counterfactual, canonical
0001/trace0002 readiness,43 accepted B07/B07R and27 B08 trace observations, retained
B08 five intake receipts/domain fingerprint. Source data/registry/0001/dependency
versions unchanged. Actual B09 fixture SDK discovery/call/broker/trace persistence
and distinct per-Inspection provenance PASS. Production MCP source/inventory/
permissions remain unchanged. Post-lifecycle proof PASS. Fresh official five reads/five denials and independent equality; domain initialize/list12/call12/no ERROR/15 server trace readbacks PASS.70 accepted trace observations preserved;1430 ToolExecutions observed.

All B01–B08 tests remain; one documented prerequisite test-cap correction. Unit
schemas are pure Python. DB/MCP cases perform actual queries; native-failure/lost-
response wrappers are labeled fault injection around real statements, not fake DB
success. No live LLM, model-selected rationale or agent/checkpoint capability claimed. Fixtures use explicitly injected2026-10-18 synthetic clocks and authored findings; database/MCP operations are real.

## Failure history

- Initial baseline506 PASS/1 FAIL457.46s, corrected trace target1 PASS4.36s.
- First33 units PASS0.20s. Smoke1 FAIL5.44s; first actual integration22 PASS/1 FAIL127.90s: fixture reused request IDs; corrected fixtures, preserved guards.
- Strengthened focused70 PASS/1 FAIL224.27s: wrong MCP event-ID expectation; corrected test only. Real target1 PASS9.77s.
- Final schema/inspection/tamper refinements40 PASS20.91s.
- Initial complete run interrupted at76 PASS162.29s/exit2 after final guard review; not a final PASS.
- Corrected topology-root guard and valid verified/candidate fixtures3 PASS15.61s.
- Final full582 PASS/0 FAIL/0 SKIP705.39s,363 unit/219 integration. Both SPEC validators PASS; original507 baseline rerun.37 new pure units+38 actual DB/MCP tests.

Exact commands and original logs are in B09-COMMANDS.md and named B09-* outputs.

## Remaining limits and B10 boundary

No source correction/municipal seed promotion. All42 city drainage edges CANDIDATE;
55 original Observation defects frozen and explicit B04 conversion preserved;55
unlinked observations, repair/inspection/decision/source-binding/local-clock/service/
S07/document/evaluator gaps remain at designated gates. Root rules cover explicit
synthetic mechanisms; unknown causes cannot auto-verify. Attribution/review is
trusted internal context, not B13 authentication or proof against collusion. Review
can accompany a report; separate retrospective report review/retraction/arbitration
is not supplied. Contradictions are preserved without automatic source selection.

Future-updated mutable source versions are unavailable at earlier cutoff, not
reconstructed. Bounded evidence/history/query/export/audit scans can fail closed;
existingO(E)/O(N)/10k-audit costs remain. A rejected operation can leave an inspectable
PREPARED journal. No B15 event delivery/outbox guarantee. No dispatch, work orders,
monitoring, LangGraph/GraphRAG, API/public auth/frontend.

Later active-graph gate must unify reviewed B08/B09/MCP/checkpoint/API target and
prove one real chain. Test-only source substitution is not that gate. Proposed B10
ONLY after human acceptance: bounded typed LangGraph supervisor/investigate/analyze/
plan/coordinate orchestration, real approved MCP selection, FalkorDBSaver checkpoint
pause/restart/resume, deterministic fake-model tests explicitly separate from live
LLM proof. Review any required read inventory/working-graph adapter through broker;
no unrestricted writes, operational execution or premature B11 GraphRAG.

STOP after B09; human review required. No ZIP or push.

## Final verification commands

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure --output docs/evidence/B09-runtime-configuration.json
backend/.venv/bin/civicly health > docs/evidence/B09-health.json
backend/.venv/bin/civicly schema-status > docs/evidence/B09-schema-status.json
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp proof --output docs/evidence/B09-official-mcp-proof.json
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly proof --output docs/evidence/B09-city-mcp-proof.json
PYTHONPATH=backend backend/.venv/bin/python -m tests.b09_evidence verify --proof docs/evidence/B09-retained-proof.json --lifecycle-log docs/evidence/B09-regression-tests.txt --output docs/evidence/B09-retained-after-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python -m tests.b08_evidence verify --proof docs/evidence/B08-retained-proof.json --anchor docs/evidence/B09-B08-after-lifecycle.json --lifecycle-log docs/evidence/B09-regression-tests.txt --output docs/evidence/B09-B08-after-final-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09.py --b08-anchor docs/evidence/B09-B08-after-final-lifecycle.json --output docs/evidence/B09-post-lifecycle.json
backend/.venv/bin/python -m pytest backend/tests --collect-only -q > docs/evidence/B09-test-collection.txt 2>&1
backend/.venv/bin/python -m compileall -q backend/app/services/evidence backend/tests/b09_evidence.py backend/tests/b09_fixtures.py backend/tests/b09_server.py scripts/audit_b09.py scripts/verify_b09.py
git diff --check -- . ':(exclude)docs/evidence/**'
git apply --reverse --check docs/evidence/B09-changes.patch
backend/.venv/bin/python scripts/audit_b09.py
make test-spec > docs/evidence/B09-spec-validation.txt 2>&1
```

All commands PASS. Accepted fixture proof restoration uses Git HEAD bytes, preserving
B07R-runtime-proof.json/B08-runtime-proof.json after saving fresh B09 regression copies.
Exact complete changed-file inventory and source diff: B09-FILES.md/B09-changes.patch.
The prerequisite test-only diff is separately B09-baseline-compatibility.patch.
401 earlier protected files unchanged; final Git-candidate secret/process scan PASS.
Frozen14 code/contract files match the582-test source hashes. Native canonical0001
remains READY91 indexgroups/182 OPERATIONAL constraints, zero domain nodes.
B09 source/working and original B08/B01/city/B05 evidence preserved. No archive/push.
