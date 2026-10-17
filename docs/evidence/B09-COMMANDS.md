# B09 exact commands and reproduction

Project root: /Users/vikashkumar/Desktop/Civicly. No push, new installs or archive.

## Accepted B08 baseline and genuine test compatibility correction

```sh
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > /tmp/civicly-b09-baseline-tests.txt 2>&1
make test-spec > /tmp/civicly-b09-baseline-spec.txt 2>&1
PYTHONPATH=backend backend/.venv/bin/python -m tests.b08_evidence verify --proof docs/evidence/B08-retained-proof.json --anchor docs/evidence/B08-retained-after-lifecycle.json --output /tmp/civicly-b09-B08-before-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure --output /tmp/civicly-b09-baseline-configuration.json
backend/.venv/bin/python -m pytest backend/tests/integration/test_civicly_mcp.py::test_trace_nodes_persist_after_session_shutdown_and_idempotence -v -s > /tmp/civicly-b09-baseline-trace-correction.txt 2>&1
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b08.py --output /tmp/civicly-b09-baseline-retained.json
PYTHONPATH=backend backend/.venv/bin/python -m tests.b08_evidence verify --proof docs/evidence/B08-retained-proof.json --anchor /tmp/civicly-b09-B08-before-lifecycle.json --output /tmp/civicly-b09-B08-after-lifecycle.json
backend/.venv/bin/python /tmp/civicly-b09-baseline-audit.py
git diff --check -- . ':(exclude)docs/evidence/**'
git add -A
git commit -m 'Baseline accepted B08 complaint intelligence with retained evidence and bounded trace-test correction'
git status --short
git rev-parse HEAD
```

Initial full run506 PASS/1 FAIL in457.46s; target after correction1 PASS4.36s.
The old trace test searched arbitrary first1000 rows for a new child after the retained
trace graph grew beyond1000. Changed only that test: exact serialized parent ID filter
before LIMIT2, same assertions plus typed child/hash readback. No trace deletion or
runtime change. DEC-034 precedes correction. This is not a507-pass single baseline run.
Full B09 regression reruns all507. Both baseline SPEC validators and retained checks
PASS; actual lifecycle completed. Logs copied into B09-baseline-* and B09-B08-*.

Local baseline00d98745d8d7bb1c8077f61c36f3779deab2b4c1; working tree clean at creation.
B08 fixture tests refresh their generated runtime proof; baseline includes that fresh
proof. B07R-runtime-proof restored from previous Git HEAD after saving fresh B09 proof.
Audit temporarily derived from audit_b08.py with explicit allowed trace-test adjustment
and output under/tmp;357 earlier protected files unchanged,411 candidates secret-safe,
no MCP children. No sensitive value printed. No external full-folder export claim.

## B09 pure schemas / actual FalkorDB / actual MCP

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_evidence_models.py -v > docs/evidence/B09-unit-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_evidence_domain.py::test_two_competing_hypotheses_supported_and_contradicted -v -s > docs/evidence/B09-smoke-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_evidence_domain.py -v -s > docs/evidence/B09-integration-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/unit/test_evidence_models.py backend/tests/integration/test_evidence_domain.py -v -s > docs/evidence/B09-focused-tests.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/unit/test_evidence_models.py backend/tests/integration/test_evidence_domain.py::test_typed_inspection_read_distinguishes_pending_missing_and_actual_findings backend/tests/integration/test_evidence_domain.py::test_known_domain_cause_requires_appropriate_primary_asset backend/tests/integration/test_evidence_domain.py::test_proposal_journal_tampering_cannot_weaken_verification -v -s > docs/evidence/B09-final-refinements.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_evidence_domain.py::test_real_mcp_broker_reads_b09_inspections_with_distinct_event_provenance -v -s > docs/evidence/B09-mcp-correction.txt 2>&1
```

Initial33 pure units PASS0.20s. Smoke1 FAIL5.44s; first23 integration22 PASS/1 FAIL127.90s:
fixtures reused global actor request IDs for changed operations/state requests. Guards
correctly refused; fixture keys corrected. Strengthened71 tests70 PASS/1 FAIL224.27s:
new MCP assertion expected Evidence IDs as maintenance events; contract returns actual
Inspection IDs with their own Evidence refs. Assertion corrected; actual SDK/broker/
TraceStore target1 PASS9.77s. Final schemas/three added cases40 PASS20.91s.
All failures retained. No old runtime contract changed to accommodate tests.

Pure tests use no model/DB. Integration tests use actual FalkorDB; fault wrappers drop
responses before/after actual statements or inject an actual UNIQUE failure, never
return mocked success. Fixture MCP substitutes B09 source internally, explicitly
labeled test-only; production graph context,12 READ tools and ACLs unchanged.

## Retained proof / complete regression / validators

```sh
PYTHONPATH=backend backend/.venv/bin/python -m tests.b09_evidence create --proof docs/evidence/B09-retained-proof.json
PYTHONPATH=backend backend/.venv/bin/python -m tests.b09_evidence verify --proof docs/evidence/B09-retained-proof.json --output docs/evidence/B09-retained-before-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09.py --output docs/evidence/B09-pre-regression-preservation.json
make test-spec > docs/evidence/B09-spec-validation.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > docs/evidence/B09-regression-tests.txt 2>&1
```

Retained proof genuinely creates/copies real B08 intake and retains source+working
small graphs. Two independent reviewed inspections verify a blockage; later authored
clear-drain/capacity evidence yields INCONCLUSIVE and supports a competing capacity
explanation. Original assessment hash/history retained. Verify is read-only and compares
complete fingerprints including owner/epoch. No import of full city or hidden answers.
Preservation helper PASS:43 accepted B07/B07R +27 accepted B08 trace observations,
city/B01/B05/migrations and retained B08 intake fingerprint unchanged.

Final full/persistence results and post-lifecycle commands follow in B09-RESULTS.md.

## Human review without reset

```sh
backend/.venv/bin/python -m pytest backend/tests/integration/test_evidence_domain.py::test_second_inspection_corrects_assessment_and_preserves_immutable_history -v -s
PYTHONPATH=backend backend/.venv/bin/python -m tests.b09_evidence verify --proof docs/evidence/B09-retained-proof.json --output /tmp/civicly-b09-human-verification.json
```

Browser at http://localhost:3000, select graph named in B09-retained-proof.json and run:

```cypher
MATCH (i:Investigation)-[:PROPOSES]->(h:Hypothesis)-[:HAS_ASSESSMENT]->(a:HypothesisAssessment)
RETURN i.id,h.id,h.cause_code,h.status,a.id,a.assessment,a.assessed_at
ORDER BY h.id,a.assessed_at,a.id LIMIT 100
```

Expect two competing hypotheses, three immutable assessments; original VERIFIED plus
later INCONCLUSIVE on blockage, SUPPORTED on capacity. Inspect SUPPORTED_BY/
CONTRADICTED_BY paths and Evidence→Finding chains. Do not interpret current hypothesis
status as the historical status at each assessment. Verify output must say PASS with
source/working fingerprints preserved. Do not recreate supplied proof, delete graphs,
clear intents or remove volumes. On failure share sanitized test log/blockers.md,
never.env/.runtime. STOP after B09; proposed B10 requires human review.

## Final code-review correction before complete rerun

First complete run interrupted at76 PASS162.29s (exit2), retained as
B09-regression-interrupted.txt. Utility mechanism could list a pipe but use another
concerned asset as topology root. Added strict pipe→affected-road dependency binding
and a real negative graph test; no schema/B03/B05 change. Source frozen afterward.

```sh
backend/.venv/bin/python -m pytest backend/tests/integration/test_evidence_domain.py::test_utility_mechanism_cannot_substitute_another_assets_topology backend/tests/integration/test_evidence_domain.py::test_topology_candidate_boundary_and_actual_path_provenance -v -s > docs/evidence/B09-topology-root-guard.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > docs/evidence/B09-regression-tests.txt 2>&1
```

Guard proof3 PASS15.61s. Final suite582 tests (507 baseline +37 pure units +38 real),
with no fake model/agent proof. Interrupted fixture proofs saved then accepted HEAD
B07R-runtime-proof.json/B08-runtime-proof.json restored; final run snapshots handled
the same way after tests. All original tests retained.

Post-lifecycle commands are copied verbatim in B09-RESULTS.md. Final582 PASS/0 FAIL/
0 SKIP705.39s,363 unit/219 integration, both SPEC validators PASS. All post-lifecycle
source/MCP/schema/persistence and source/secret/process checks PASS. No B10 work.
