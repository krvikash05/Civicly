# B07 commands and observed evidence

All commands from repository root. No push, source-data changes or volume deletion.
Python/Node/server/client/package/database pins remain accepted B06 versions.

## Credential incident and accepted baseline

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/rotate_b07_mcp.py
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > docs/evidence/B07-baseline-tests.txt 2>&1
```

Rotation report:old auth DENIED, replacement PING/graph RO PASS, named-user connections
revoked, scope/permissions preserved, no credential values logged. Old secrets were
not stored for test replay. Private file replaced atomically0600. Inherited baseline
361 PASS/0 FAIL/0 SKIP in305.72s. B06 source index assembled from accepted patch and
B06 evidence, excluding new B07 files/ADR.52-file index secret/exclusion scan PASS:

```sh
git apply --cached docs/evidence/B06-changes.patch
git add docs/evidence/B06-*
git commit -m 'Baseline accepted B06 official MCP runtime and real integration evidence'
git rev-parse HEAD
```

Local24e80725ead2903516ecd36db2142f8fe36b2760. No remote push. Archive incident was
external full-folder inclusion of ignored runtime files; Git candidate audit does not
claim that such an archive is safe. No B07 ZIP generated.

## Actual runtime and tests

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure --output docs/evidence/B07-runtime-configuration.json
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly proof --output docs/evidence/B07-runtime-proof.json
backend/.venv/bin/python -m pytest backend/tests/unit/test_civicly_mcp_contracts.py -q > docs/evidence/B07-unit-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_civicly_mcp.py -v -s > docs/evidence/B07-integration-first.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/unit/test_civicly_mcp_contracts.py backend/tests/integration/test_civicly_mcp.py -v -s > docs/evidence/B07-focused-tests.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_civicly_mcp.py::test_unavailable_custom_server_fails_closed backend/tests/integration/test_civicly_mcp.py::test_trace_write_failure_prevents_acknowledged_success -v -s > docs/evidence/B07-failure-boundary-tests.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > docs/evidence/B07-regression-tests.txt 2>&1
make test-spec > docs/evidence/B07-spec-validation.txt 2>&1
backend/.venv/bin/python -m compileall -q backend/app/mcp/civicly scripts/rotate_b07_mcp.py
git diff --check
```

First32 unit PASS in0.73s. First25 real PASS in49.73s. Strengthened focused60 PASS
in49.55s (32 unit/28 real); extra2 real failure-boundary PASS in7.18s. Revoked only
trace-writer permissions in the expected negative case; restored in finally.
PermissionError stderr is deliberate fault evidence, not a failed passing test.
Final suite collects423 = original361 +32 unit +30 real custom MCP integration.

Initial all-handler CLI returned a maintenance ERROR:duplicate evidence IDs in
record projection correctly failed uniqueItems validation. Direct readonly service
repro showed ['EVD-B04-IMPORT','EVD-B04-IMPORT','EVD-PRIOR-REPAIR']; deduplicated/copy
provenance lists and reran proof, now rejecting any handler ERROR. Valid existing
LOC-004 replaced an absent operator proof ID to exercise the legitimate unlinked-
measurement gap; source data unchanged. New proof shows all12 actual responses,
verified0 vs exploratory candidate edge(s), persisted server trace read-back.

Date scope validation rejects non-UTC offsets, excessive/boolean hop budgets. Source
and trace Redis clients disable retries; serialized server64 and broker32 finite
calls. Invalid graph/role/write/server tools are denied, timeout/downtime/malformed
AFTER-REAL-READ corruption explicit; no mock substitutes for real success.

After full persistence run, reprovision ACL (`configure`), verify existing proof trace
IDs through fresh connections, and record retained source/B01/B05 fingerprints.
Helper/audit commands and resulting reports are included in final evidence inventory.

## Human check

Run configure, then proof to /tmp/civicly-b07-proof.json and `make test-civicly-mcp`.
Inspect12 names, PARTIAL current facts/explicit UNAVAILABLE capabilities, zero verified
city drainage paths, explicit CANDIDATE exploration, and real ToolExecution IDs with
source revision2104. In Browser select trace graph from operator configuration report;
no user secrets are in report/traces. Confirm city stays858/1246 and original graph
probe unchanged. If failing share redacted output/blockers.md; never.env/.runtime.
Stop for B07 review; proposed B08 is complaint normalization/dedup/recurrence only.

Post-lifecycle verification/security helper commands:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure --output docs/evidence/B07-runtime-configuration.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b07.py --output docs/evidence/B07-post-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly proof --output docs/evidence/B07-runtime-proof.json
backend/.venv/bin/python scripts/audit_b07.py
```

Pre-final-contract proof preserved separately before regeneration. Verify helper
compares every2104 city record hash plus audit/writer fingerprint, original B01 and
B05 source/clone, immutable canonical readiness and all13 preexisting persisted
server traces. It runs after lifecycle tests, never during temporary DB downtime.
Audit validates old source/tests/pins, two intentional contract updates,18 stable names/
permissions, all current local secret values/exclusions and absent child processes.
It explicitly does not claim an external full-folder archive was sanitized.

Final typed-network refinement reuses existing B05 forward dependency algorithm:

```sh
backend/.venv/bin/python -m pytest backend/tests/integration/test_civicly_mcp.py::test_existing_b05_typed_cross_category_dependencies_exposed -v -s > docs/evidence/B07-typed-dependency-tests.txt 2>&1
```

2 real PASS in7.13s (waste→route COLLECTED_BY, utility→road UNDERLIES; reverse/BOTH
typed mode rejected). Interim full423 PASS in374.07s saved to
B07-regression-before-typed-mode.txt. Final full command rerun after this change,
collecting425 = original361 +32 unit +32 real custom MCP integration cases.

Final metadata correction retains DATA_UNAVAILABLE/READ_FAILED in SERVER traces,
separate from BROKER receipt status;33 B07 unit PASS in0.84s. Final operator proof
also captures actual initialized identity/protocol/tools/list. Final complete suite
collects426 =361 inherited +33 unit +32 real custom MCP cases. Any earlier full log
is retained under its explicit interim filename; final B07-regression-tests.txt is
rerun against final source after this correction.

Intermediate425 PASS/0 FAIL/0 SKIP in370.65s retained in
B07-regression-before-trace-metadata-fix.txt. Final426 full command is run after the
trace-domain error regression and actual discovery evidence/root guard refinements.
No original source test was removed or altered; additions are isolated B07 tests.
