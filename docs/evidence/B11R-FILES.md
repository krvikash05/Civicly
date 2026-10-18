# B11-R exact changed-file inventory

Basis: pre-B11-R working-tree snapshot; B11 was already uncommitted against9f7ec1d. B11R-changes.patch isolates only this correction; original B11 diff/evidence unchanged.

## Modified source/contracts/docs (12)

- `backend/app/memory/sdk.py`
- `backend/app/memory/service.py`
- `backend/app/mcp/civicly/service.py`
- `backend/tests/integration/test_memory_mcp.py`
- `contracts/organizational_memory.json`
- `backend/MEMORY.md`
- `decision.md`
- `flow.md`
- `implementation_status.md`
- `test_log.md`
- `blockers.md`
- `task_board.md`

## New integration scenario (1)

- `backend/tests/integration/test_memory_review.py`

## New review evidence

- `docs/evidence/B11R-COMMANDS.md`
- `docs/evidence/B11R-FILES.md`
- `docs/evidence/B11R-RESULTS.md`
- `docs/evidence/B11R-changes.patch`
- `docs/evidence/B11R-compat-zero-live.json`
- `docs/evidence/B11R-compat.txt`
- `docs/evidence/B11R-corpus.json`
- `docs/evidence/B11R-deployed-water-comparison.json`
- `docs/evidence/B11R-focused-zero-live.json`
- `docs/evidence/B11R-focused.txt`
- `docs/evidence/B11R-fresh-process-proof.json`
- `docs/evidence/B11R-history-zero-live.json`
- `docs/evidence/B11R-history.json`
- `docs/evidence/B11R-history.txt`
- `docs/evidence/B11R-index-missing.json`
- `docs/evidence/B11R-index-missing_index.json`
- `docs/evidence/B11R-index-wrong_vector.json`
- `docs/evidence/B11R-mcp-agent-proof.json`
- `docs/evidence/B11R-mcp-water-proof.json`
- `docs/evidence/B11R-persistence-anchor.json`
- `docs/evidence/B11R-repro-zero-live.json`
- `docs/evidence/B11R-repro.txt`
- `docs/evidence/B11R-source-audit.json`
- `docs/evidence/B11R-spec.txt`
- `docs/evidence/B11R-test-summary.json`

No dependency, migration, source data, credentials, native checkpoint or original evidence files changed. Test MCP file adds Water lookup/assertions and opt-in B11R proof destination; all original test functions/assertions retained.
