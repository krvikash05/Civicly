# B09 exact changed-file inventory

Baseline: `00d98745d8d7bb1c8077f61c36f3779deab2b4c1`. 10 modified + 63 created = 73 files.

B09-changes.patch contains all 25 source/contract/documentation changes relative to baseline; generated evidence bodies are listed here and supplied as actual files, excluded from that patch to avoid recursive/self-containing diffs.

B09-baseline-compatibility.patch separately records the prerequisite old trace-test selection correction committed in the baseline. No old test changes after baseline; no remote push/archive.

| Change | Repository-relative file | Purpose |
|---|---|---|
| Modified | `README.md` | Domain/architecture documentation and scope/reproduction guidance |
| Modified | `backend/CIVICLY_MCP.md` | Domain/architecture documentation and scope/reproduction guidance |
| Modified | `backend/README.md` | Domain/architecture documentation and scope/reproduction guidance |
| Modified | `blockers.md` | Append-only engineering record and current B09 status |
| Modified | `decision.md` | Append-only engineering record and current B09 status |
| Modified | `docs/backend/02_graph.md` | Domain/architecture documentation and scope/reproduction guidance |
| Modified | `flow.md` | Append-only engineering record and current B09 status |
| Modified | `implementation_status.md` | Append-only engineering record and current B09 status |
| Modified | `task_board.md` | Append-only engineering record and current B09 status |
| Modified | `test_log.md` | Append-only engineering record and current B09 status |
| Created | `backend/EVIDENCE.md` | Domain/architecture documentation and scope/reproduction guidance |
| Created | `backend/app/services/evidence/__init__.py` | Public internal service exports |
| Created | `backend/app/services/evidence/models.py` | Strict command/result/journal/report schemas |
| Created | `backend/app/services/evidence/policies.py` | Deterministic three-issue verification criteria |
| Created | `backend/app/services/evidence/reader.py` | Bounded provenance, temporal, history and B05 reads |
| Created | `backend/app/services/evidence/service.py` | Investigation, hypothesis, assessment and inspection lifecycle |
| Created | `backend/app/services/evidence/writer.py` | Narrow atomic batches through B03 integrity/fence/recovery |
| Created | `backend/tests/b09_evidence.py` | Retained review graph and read-only lifecycle verification |
| Created | `backend/tests/b09_fixtures.py` | Authored observations and source-preserving real B08 copies |
| Created | `backend/tests/b09_server.py` | Explicit test-only real MCP source substitution |
| Created | `backend/tests/integration/test_evidence_domain.py` | 38 real FalkorDB/MCP integration tests and graph-state assertions |
| Created | `backend/tests/unit/test_evidence_models.py` | Pure schema/policy and machine-contract tests |
| Created | `contracts/evidence_hypotheses.json` | Machine-readable domain schemas, criteria, limits and boundaries |
| Created | `docs/evidence/B09-B07R-regression-proof.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-B08-after-final-lifecycle.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-B08-after-lifecycle.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-B08-before-lifecycle.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-B08-regression-proof.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-COMMANDS.md` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-FILES.md` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-RESULTS.md` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-baseline-B07R-proof.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-baseline-audit.json` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-baseline-compatibility.patch` | Review diff (source patch or prerequisite test-only compatibility correction) |
| Created | `docs/evidence/B09-baseline-configuration.json` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-baseline-retained.json` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-baseline-spec.txt` | Exact executed command/test/check output |
| Created | `docs/evidence/B09-baseline-tests-failed.txt` | Retained attempt/failure/interruption evidence; final gate separately recorded |
| Created | `docs/evidence/B09-baseline-trace-correction.txt` | Exact executed command/test/check output |
| Created | `docs/evidence/B09-changes.patch` | Review diff (source patch or prerequisite test-only compatibility correction) |
| Created | `docs/evidence/B09-city-mcp-proof.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-final-refinements.txt` | Exact executed command/test/check output |
| Created | `docs/evidence/B09-focused-tests.txt` | Exact executed command/test/check output |
| Created | `docs/evidence/B09-health.json` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-integration-first.txt` | Retained attempt/failure/interruption evidence; final gate separately recorded |
| Created | `docs/evidence/B09-interrupted-B07R-proof.json` | Retained attempt/failure/interruption evidence; final gate separately recorded |
| Created | `docs/evidence/B09-interrupted-B08-proof.json` | Retained attempt/failure/interruption evidence; final gate separately recorded |
| Created | `docs/evidence/B09-mcp-correction.txt` | Exact executed command/test/check output |
| Created | `docs/evidence/B09-official-mcp-proof.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-post-lifecycle-B01-B07.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-post-lifecycle.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-pre-regression-preservation-B01-B07.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-pre-regression-preservation.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-regression-interrupted.txt` | Retained attempt/failure/interruption evidence; final gate separately recorded |
| Created | `docs/evidence/B09-regression-tests.txt` | Exact executed command/test/check output |
| Created | `docs/evidence/B09-retained-after-lifecycle.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-retained-before-lifecycle.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-retained-proof.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-review-checks.txt` | Exact executed command/test/check output |
| Created | `docs/evidence/B09-runtime-configuration.json` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-runtime-proof.json` | Sanitized actual runtime/provenance/persistence evidence |
| Created | `docs/evidence/B09-runtime-summary.json` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-schema-status.json` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-smoke-first.txt` | Retained attempt/failure/interruption evidence; final gate separately recorded |
| Created | `docs/evidence/B09-source-audit.json` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-source-freeze.json` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `docs/evidence/B09-spec-validation.txt` | Exact executed command/test/check output |
| Created | `docs/evidence/B09-test-collection.txt` | Exact executed command/test/check output |
| Created | `docs/evidence/B09-topology-root-guard.txt` | Exact executed command/test/check output |
| Created | `docs/evidence/B09-unit-first.txt` | Retained attempt/failure/interruption evidence; final gate separately recorded |
| Created | `docs/evidence/B09-versions.json` | Review documentation, inventory, runtime summary or sanitized audit metadata |
| Created | `scripts/audit_b09.py` | Accepted-source/private-value/process audit |
| Created | `scripts/verify_b09.py` | Read-only predecessor graph and accepted trace preservation |

External dependencies not bundled: ignored Python3.12 virtual environment and pinned packages (existing backend/pyproject.toml/uv.lock); official Node MCP runtime node_modules (existing lockfile); running FalkorDB6.0.2/Browser2.6.1 Docker image and named volumes; private .env/.runtime credentials. No secrets or database volumes are included in source/evidence. Existing repository dependencies remain unchanged.

Retained DB graphs are named in runtime proof files; the evidence contains actual sanitized query results, not a database-volume dump. Both original and new retained evidence must be preserved.
