# B07-R exact commands and evidence classes

Run from `/Users/vikashkumar/Desktop/Civicly`. No push/credential rotation/volume deletion.
Python3.12.1; pinned B07 MCP2.3.0/FalkorDB6.0.2 and dependencies unchanged.

Accepted uncommitted B07 Git candidates were copied to `/tmp/civicly-b07r-baseline`
using `git ls-files --cached --others --exclude-standard -z`;344 source/evidence SHA256
entries retained in B07R-baseline-sha256.json. Ignored credentials/caches never copied.
Source-only B07-R patch compares that accepted working tree, not the older B06 HEAD.

## Failure reproduction / corrective focus

```sh
backend/.venv/bin/python -m compileall -q backend/tests/b07r_server.py backend/tests/integration/test_civicly_mcp_review.py
backend/.venv/bin/python -m pytest backend/tests/integration/test_civicly_mcp_review.py -v -s > docs/evidence/B07R-before-correction.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_civicly_mcp_review.py -v -s > docs/evidence/B07R-failure-reproduction.txt 2>&1
backend/.venv/bin/python -m pytest backend/tests/integration/test_civicly_mcp_review.py -v -s > docs/evidence/B07R-focused-real.txt 2>&1
```

First command sequence exposed4 test setup errors (strict temporal registry), fixed
fixture valid_from before actual reproductions. Actual old service4 FAIL; corrected
initial4 PASS; final strengthened9 PASS. All attempts retained, not treated as success.
Before outputs copied to B07R-before-outputs.json before rerunning corrected service.

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_civicly_mcp_review.py -v > docs/evidence/B07R-unit-tests.txt 2>&1
```

Historical command:5 pure structural/fake unit PASS. New file was then renamed to
`backend/tests/unit/test_civicly_mcp_history_projection.py` to resolve a full-suite
module-name collision with the new integration file; no existing test was modified.

## Complete regression / specification

```sh
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > docs/evidence/B07R-regression-tests.txt 2>&1
make test-spec > docs/evidence/B07R-spec-validation.txt 2>&1
```

First full attempt1 collection ERROR (B07R-collection-failure.txt); same exact full
command rerun after renaming. Lifecycle tests use the retained local Compose database,
actual restart/recreation; no mock substitutions. Static specification validators are
separate from runtime proof.

## Post-lifecycle / safety / human reproduction

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly configure --output docs/evidence/B07R-runtime-configuration.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b07.py --output docs/evidence/B07R-post-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python -m app.mcp.civicly proof --output docs/evidence/B07R-city-proof.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b07r_traces.py
backend/.venv/bin/python scripts/audit_b07r.py
backend/.venv/bin/python -m compileall -q backend/app/mcp/civicly backend/tests/b07r_server.py backend/tests/unit/test_civicly_mcp_history_projection.py backend/tests/integration/test_civicly_mcp_review.py scripts/audit_b07r.py
make test-spec > docs/evidence/B07R-spec-validation.txt 2>&1
git diff --check
git apply --reverse --check docs/evidence/B07R-changes.patch
```

Additional fresh readback checks all15 accepted B07 final proof server traces and all
current B07-R fixture proof execution IDs against actual TraceStore records, preserving
output digests; sanitized result in B07R-trace-continuity.json. Source verify checks city
2104 record fingerprints/revision/audit, B01 probe, B05 source/clone and operational
migrations0001/0002. Audit checks every preexisting non-authorized file/hash and all
18 input/output schemas/permissions, actual local secret values and child processes.
No external full-folder archive safety claim, no new ZIP.

For a short review rerun both new test files together. Expect5 unit +9 actual DB/MCP
PASS; examine B07R-runtime-proof.json for independent inspection evidence and100/101
history boundaries. This file explicitly labels a test-only disposable source backend;
B07R-city-proof.json separately proves actual retained-city runtime. Empty operational
lists are explicitly UNKNOWN, not verified empty. If failing share sanitized test
output plus blockers.md; never `.env`/`.runtime`. STOP before B08.
