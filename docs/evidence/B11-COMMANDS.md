# B11 exact commands and observed attempts

Working directory `/Users/vikashkumar/Desktop/Civicly`; Python3.12.1,
FalkorDB6.0.2 pinned image unchanged. Model/provider requests prohibited.
Recorded B10-O-R2 baseline770PASS and source/security audit verified with
`backend/.venv/bin/python scripts/audit_b10or2.py` (PASS). Audited files then
committed locally with `git commit -m 'Record reviewed B10-O-R2 accounting and multistep verification baseline'`
→9f7ec1d; af42149 preserved. No push, ZIP or B12 work.

## SDK release and isolated spike

```sh
backend/.venv/bin/uv pip index versions graphrag-sdk
backend/.venv/bin/python -m pip index versions graphrag-sdk
backend/.venv/bin/python -m venv /tmp/civicly-b11-sdk-spike
/tmp/civicly-b11-sdk-spike/bin/python -m pip install 'graphrag-sdk[pdf]==1.4.0'
UV_CACHE_DIR=/tmp/civicly-b11-uv-cache backend/.venv/bin/uv pip install --python /tmp/civicly-b11-sdk-spike/bin/python 'graphrag-sdk[pdf,markdown]==1.4.0'
PYTHONPATH=backend/test_guards CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/civicly-b11-sdk-provider.jsonl /tmp/civicly-b11-sdk-spike/bin/python /tmp/civicly_b11_sdk_smoke.py
```

Pinned uv0.13.1 has no pip index subcommand; pip metadata inspection succeeds1.4.0.
Initial pip install interrupted after stalled torch package download; uv temporary
install succeeded, including mandatory SDK dependencies without model weights.
Original actual SDK smoke failed: legacy createNodeIndex arity incompatible with
server6.0.2, then SDK circuit breaker opened. Raw failure retained. Exact two fixed
DDL translations through injected Connection restore real SDK MD/PDF ingestion,
finalize and LocalRetrieval:1indexed chunk each,2retrieved chunk IDs. SDK not mocked.
Adapter and reproducible unit/integration tests are in repository source; smoke
script is a temporary early experiment, later actual tests supersede its coverage.

```sh
UV_CACHE_DIR=/tmp/civicly-b11-uv-cache backend/.venv/bin/uv add --project backend 'graphrag-sdk[pdf,markdown]==1.4.0'
UV_CACHE_DIR=/tmp/civicly-b11-uv-cache backend/.venv/bin/uv pip check --python backend/.venv/bin/python
```

Project lock121packages,100 installed, all75 baseline versions unchanged; checkPASS.
No model inference/weights. First pip check without explicit cache failed sandbox
cache creation; repeated with /tmp cache passed. Direct prior pins unchanged.

## Preflight retention

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10.py --reprovision --compare docs/evidence/B10-before-lifecycle.json --output docs/evidence/B11-before-B10.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09.py --output docs/evidence/B11-before-B01-B09.json --b08-anchor docs/evidence/B09-B08-after-final-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09r.py --output docs/evidence/B11-before-B09R.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b11_retained_history.py --output docs/evidence/B11-before-B09R.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10or_spending.py verify --anchor docs/evidence/B10OR-spending-before.json --output docs/evidence/B11-before-spending.json
```

B10six threads/source, B01–B09city/43+27traces, ledger5120PASS. Legacy B09R verifier
initially compared restored historical rolling proof and failed fingerprint;
accepted B10OR2-regression-B09R-runtime-proof selected via explicit new adapter,
all unchanged assertionsPASS incl v1/v2 readbacks31traces. No data/evidence rewritten.

## Focused tests and failures (overlapping; do not sum)

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_memory_sources.py -q --durations=10
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-integration-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_graphrag.py -q --durations=10
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-source-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_memory_sources.py backend/tests/integration/test_memory_graphrag.py -q --durations=10
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-mcp-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_mcp.py -q --durations=10
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-final-focused-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_memory_sources.py backend/tests/integration/test_memory_graphrag.py backend/tests/integration/test_memory_mcp.py backend/tests/integration/test_memory_case_history.py -q --durations=25
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-mcp-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_mcp.py backend/tests/integration/test_memory_case_history.py -q --durations=25
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-memory-case-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_case_history.py::test_actual_episodic_semantic_history_preserves_assessment_revisions -q --durations=10
```

Unit23PASS.81s; initial real SDK5PASS13.58s; stronger source batch34PASS25.60s.
MCP first1FAIL9.75s: new fixture requested15s, existing broker permits<=10. Fixture
corrected to10, exact rerun1PASS11.75s. No runtime budget/old test weakened.
Next overlapping batch36PASS/2FAIL42.67s because citation contract edited while
client processes retained prior schema; broker correctly rejected TOOL_SCHEMA_MISMATCH.
Source held fixed afterward, only2affected cases rerun:1PASS/1FAIL21.31s. Real memory
output missing exported Evidence nodes was rejected INVALID_OUTPUT. Corrected via
existing evidence projector+merge; exact case1PASS9.49s, no broker/schema weakening.
All these raw failures retained. Final targeted regression covers corrected source.

## Final targeted regression

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-regression-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_memory_sources.py backend/tests/unit/test_schema.py backend/tests/unit/test_graph_access_models.py backend/tests/unit/test_mcp_broker_policy.py backend/tests/unit/test_civicly_mcp_contracts.py backend/tests/unit/test_civicly_mcp_history_projection.py backend/tests/unit/test_agent_context.py backend/tests/unit/test_agent_models.py backend/tests/unit/test_agent_count_billing.py backend/tests/unit/test_agent_token_accounting.py backend/tests/unit/test_agent_ledger_recovery.py backend/tests/unit/test_ai_spending.py backend/tests/unit/test_ai_execution_policy.py backend/tests/integration/test_memory_graphrag.py backend/tests/integration/test_memory_mcp.py backend/tests/integration/test_memory_case_history.py backend/tests/integration/test_agent_active.py backend/tests/integration/test_agent_runtime.py backend/tests/integration/test_agent_safety.py backend/tests/integration/test_civicly_mcp.py backend/tests/integration/test_civicly_mcp_review.py backend/tests/integration/test_official_mcp.py -v --durations=25 > /tmp/civicly-b11-regression.txt 2>&1
make test-spec > /tmp/civicly-b11-spec.txt 2>&1
```

Selection justification DEC-047: affected memory/schema/MCP/context/accounting
modules + actual official/domain brokers/Saver. Registry0001/0002/direct package
pins unchanged; compatible isolated0003 and optional read handlers. No automatic
770-case regression; broaden only on demonstrated cross-cutting failure.

## Canonical setup and repeat

```sh
PYTHONPATH=backend CIVICLY_TEST_NO_LIVE=1 backend/.venv/bin/python -m app.memory setup --output docs/evidence/B11-canonical-setup.json
PYTHONPATH=backend/test_guards:backend CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/civicly-b11-setup-provider.jsonl backend/.venv/bin/python -m app.memory setup --output docs/evidence/B11-canonical-replay.json
```

First19registered,0replayed,0003READY; source-linked D001 example. Repeat result
recorded separately. Operator-only setup registers organizational references/five
owners, does not import city. Dedicated exact-key memory RO credential0600 excluded.

## Lifecycle and preservation

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-lifecycle-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_persistence.py -v -s --run-persistence --durations=10 > /tmp/civicly-b11-lifecycle.txt 2>&1
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b11_persistence.py --output docs/evidence/B11-after-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10.py --reprovision --compare docs/evidence/B10-before-lifecycle.json --output docs/evidence/B11-after-B10.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09.py --output docs/evidence/B11-after-B01-B09.json --b08-anchor docs/evidence/B09-B08-after-final-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b11_retained_history.py --output docs/evidence/B11-after-B09R.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10or_spending.py verify --anchor docs/evidence/B10OR-spending-before.json --output docs/evidence/B11-after-spending.json
```

Never delete retained volumes. Dynamic ACL reprovision only; graph/index/version/
checkpoint retention checked through fresh processes and original assertions.
Actual results and counts in B11-RESULTS.md; zero external guard JSON retained.
Source/secret/history audit generates exact inventory/patch against9f7ec1d; fresh
rolling B07R proof copied under B11 prefix before original bytes restored.

Final strict source checks: updates require explicit supersedes of latest registered
version; source unit+exact real version test27PASS4.40s. Exact-ID document excerpts
read the verified SDK source chunks directly so global semantic top-k cannot hide
a known requested source; three affected real MD/PDF/version/MCP cases rerun, final
log B11-excerpt-final.txt. No other regression source changed. Earlier B11 lifecycle
anchor retained separately so later test fixtures cannot overwrite its association.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-version-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_memory_sources.py backend/tests/integration/test_memory_graphrag.py::test_versions_supersession_revocation_and_missing_source -q --durations=10
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-excerpt-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_graphrag.py::test_real_md_pdf_citations_idempotency_and_migration_rerun backend/tests/integration/test_memory_graphrag.py::test_versions_supersession_revocation_and_missing_source backend/tests/integration/test_memory_mcp.py::test_real_sdk_domain_mcp_agent_checkpoint_and_fresh_process -q --durations=10
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b11_persistence.py --anchor docs/evidence/B11-lifecycle-anchor.json --output docs/evidence/B11-after-lifecycle.json
```

Audit exporter first treated PDF high-byte data as text even with --binary because
Git classified the small file as text. Fixed with temporary per-command PDF binary
attributes, preserving repository attributes. No application/data/test change.
Exact private-value/history/process audit and binary-inclusive patch regenerated.

Final canonical procedure identity correction DEC-048: five real source/version/
cross-graph/MCP casesPASS25.10s. Procedure IDs now reference existing normative
KnowledgeProcedure entities (ORGPROC IDs), with exact document_ref and PROPOSED
status. Trusted setup replay additively backfilled19registered sources; no0003
plan mutation, no source hash/chunk replacement or B12 implementation.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-procedure-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_graphrag.py::test_real_md_pdf_citations_idempotency_and_migration_rerun backend/tests/integration/test_memory_graphrag.py::test_versions_supersession_revocation_and_missing_source backend/tests/integration/test_memory_graphrag.py::test_cross_graph_interruption_recovery backend/tests/integration/test_memory_mcp.py::test_real_sdk_domain_mcp_agent_checkpoint_and_fresh_process -q --durations=10
PYTHONPATH=backend/test_guards:backend CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/civicly-b11-procedure-setup-provider.jsonl backend/.venv/bin/python -m app.memory setup --output docs/evidence/B11-canonical-procedure-replay.json
```

After DEC-048, repeated only the listed B01 lifecycle command:1PASS15.25s; earlier15.22s proof preserved under B11-earlier-*. The final lifecycle anchor has19PROPOSED procedure nodes and same Saver thread, verified after recreation through scripts/verify_b11_persistence.py. Repeated listed retained-data verifiers allPASS. Final deployed setup replay19/19 restores only exact-key ACL, proofs B11-final-canonical-replay.json /canonical-runtime-proof.json.

Supplemental final procedure-count query initially used MATCH(d:Document {id:p.document_ref}); FalkorDB rejected p variable scope in that pattern. Replaced only evidence probe with MATCH(p:KnowledgeProcedure),(d:Document) WHERE d.id=p.document_ref AND p.id STARTS WITH $prefix; real19bindings PASS. Application queries/tests unchanged. Final setup itself succeeded19/19 before the supplemental probe error.

Final UTC fractional boundary correction (string ordering replaced by existing timestamp parser): `CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-fractional-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_graphrag.py::test_fractional_effective_date_supersession_uses_utc_instants -q --durations=10` →1PASS. Actual earlier-invalid source version stayed unregistered; later valid revision reused indexed source safely. This is one additional real case, unique313total227unit/86integration, not a full rerun.
