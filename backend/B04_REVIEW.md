# B04 review entrypoint

B04 only. B03-R accepted baseline09482e2 is local, unpushed. Original source,
registry v3, migration0001, graph-access policies, benchmark plan, prior tests,
B01 probe, canonical graph and persistent volumes preserved. B05 is not started.

- Implementation and exact reproduction: INGESTION.md and ../docs/evidence/B04-COMMANDS.md.
- Exact source/file inventory and diff: ../docs/evidence/B04-FILES.md and ../docs/evidence/B04-changes.patch.
- Source audit: ../data/ingestion/source-audit.json; selected-source-audit.json.
- Explicit original-source conversion/quarantine: ../data/ingestion/legacy-conversion/
  and legacy-v1/. Original inputs stay under contracts; no silent rewrite.
- Corrected synthetic revision deltas: ../data/ingestion/generator-revision-changes.json.
- Runtime manifest/field provenance: ../data/ingestion/city-v3.json,
  input-manifest.json and conversion-report.json. All55 numerical observations
  remain exactly equal to original values/units/dates.
- Scenario matrix and missing evidence: ../data/ingestion/DATA_QUALITY.md and
  scenario-readiness.json. Opaque release-manifest.json has no reveal payload.
- Actual imports/performance: ../docs/evidence/B04-benchmarks.json and B04-PERFORMANCE.md.
- Test/SPEC evidence: ../docs/evidence/B04-regression-tests.txt and B04-spec-validation.txt.
- Remaining gaps and partial B00 resolutions: ../blockers.md and DEC-014–018.

Human verification (repository root):run `make test-spec`; inspect the retained
B04 graph named in B04-benchmarks.json in http://127.0.0.1:3000. Expected858 domain
nodes/1246 edges, revision2104/audit2104. To verify an unchanged import, use the
concrete CLI command in B04-COMMANDS.md; expected0 created/2104 matched with unchanged
hash/revision/audit. Do not rerun prepare before that check: a new materialization
clock is a new source version and must conflict. If anything fails, share the
redacted import report or B04-regression-tests.txt, never.env or credentials.

No product scenario capability is claimed complete by seeded schema/data. Proposed
next B05:bounded graph algorithms/case retrieval and isolated counterfactual clones,
with verified-vs-candidate provenance and removal/ablation tests; no MCP/agents or
operations. Await explicit human review before implementing it.
