# B10-O-R exact verification commands

Run from `/Users/vikashkumar/Desktop/Civicly`, Python3.12.1, ignored local Docker/ACL configuration. Every pytest invocation below uses the inherited HTTPX/DNS Gemini interlock. MockTransport responses are simulated, never billed or provider-confirmed. No Gemini/countTokens endpoint was contacted. Local baseline commit: `c16346a`; no push.

Dependency verification (only added package: SentencePiece0.2.1; existing pins retained):

```sh
UV_CACHE_DIR=/tmp/civicly-b10or-uv-cache backend/.venv/bin/uv pip install --python backend/.venv/bin/python sentencepiece==0.2.1
UV_CACHE_DIR=/tmp/civicly-b10or-uv-cache backend/.venv/bin/uv lock --project backend
UV_CACHE_DIR=/tmp/civicly-b10or-uv-cache backend/.venv/bin/uv sync --project backend --frozen
PYTHONPATH=backend backend/.venv/bin/python scripts/configure_tokenizer.py
```

The first install and the pinned public-asset download preceded lock/sync for API smoke verification. The setup command is repeatable with the existing SHA-verified asset and sends no Gemini request. Original installation/lock/sync output is retained under B10OR-dependency-*.txt.

Preflight (also run immediately before the final suite):

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10.py --reprovision --compare docs/evidence/B10-before-lifecycle.json --output docs/evidence/B10OR-before-lifecycle.json
```

Stage1 initial failure: **29 pass/1 fail**; retry was correctly denied, but stale SERVICE_UNAVAILABLE metadata masked TOKEN_BUDGET. Corrected failure classification, retained assertion and raw failure output. Focused rerun:58 pass.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or-stage1-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_agent_provider.py backend/tests/unit/test_ai_provider_recovery.py backend/tests/unit/test_ai_spending.py backend/tests/unit/test_ai_execution_policy.py -q > /tmp/civicly-b10or-stage1-first.txt 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or-stage1-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_agent_token_accounting.py backend/tests/unit/test_agent_ledger_recovery.py backend/tests/unit/test_agent_provider.py backend/tests/unit/test_ai_provider_recovery.py backend/tests/unit/test_ai_spending.py backend/tests/unit/test_ai_execution_policy.py -q > /tmp/civicly-b10or-stage1-second.txt 2>&1
```

Stage2 authored fixture corrections, not relaxed domain rules: first10 pass/1 fail (unrecognized support code); second59 pass/2 fail (graph-reactive selector treated CONTESTED like inconclusive; waste-history request included undeclared investigation_id). Correct canonical code/selector/arguments, preserve all earlier tests. Earlier failed source is shown in tracebacks; the final patch contains corrections.

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or-stage2-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_agent_accounting.py -q > /tmp/civicly-b10or-stage2-first.txt 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or-stage2-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_agent_accounting.py backend/tests/integration/test_agent_optimization.py backend/tests/integration/test_agent_runtime.py backend/tests/integration/test_agent_reasoning.py backend/tests/unit/test_agent_token_accounting.py backend/tests/unit/test_agent_ledger_recovery.py -q > /tmp/civicly-b10or-stage2-second.txt 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or-stage2-final-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_agent_accounting.py backend/tests/unit/test_agent_token_accounting.py backend/tests/unit/test_agent_ledger_recovery.py backend/tests/unit/test_agent_provider.py backend/tests/unit/test_ai_provider_recovery.py backend/tests/unit/test_ai_spending.py backend/tests/unit/test_ai_execution_policy.py -q > /tmp/civicly-b10or-stage2-final.txt 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or-extra-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_agent_ledger_recovery.py -q > /tmp/civicly-b10or-extra.txt 2>&1
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or-boundary-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_agent_accounting.py::test_token_budget_checkpoint_authorized_increase_preserves_counters backend/tests/integration/test_agent_accounting.py::test_reported_usage_overrun_persists_without_counter_overflow backend/tests/unit/test_agent_models.py backend/tests/unit/test_agent_ledger_recovery.py -q > /tmp/civicly-b10or-boundary.txt 2>&1
```

Final targeted batches:76 pass,10 pass,29 pass. They overlap; **do not sum these totals**. Last boundary batch includes final counter storage/wake-recovery correction. Source then frozen for Stage3.

Financial witnesses (create was run once, never overwrite an existing witness; verify is repeatable):

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10or_spending.py create --output docs/evidence/B10OR-spending-before.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10or_spending.py verify --anchor docs/evidence/B10OR-spending-before.json --output docs/evidence/B10OR-spending-after.json
```

Stage3 final complete regression, including Docker restart/recreation/Browser and both specifications:

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b10or-final-provider-requests.jsonl backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence > /tmp/civicly-b10or-final-tests.txt 2>&1
make test-spec > /tmp/civicly-b10or-final-spec.txt 2>&1
UV_CACHE_DIR=/tmp/civicly-b10or-uv-cache backend/.venv/bin/uv lock --project backend --check --offline
```

Post-lifecycle retained evidence (execute B09R verifier before restoring rolling proofs):

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10.py --reprovision --compare docs/evidence/B10-before-lifecycle.json --output docs/evidence/B10OR-post-retained.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09.py --output docs/evidence/B10OR-post-B01-B09.json --b08-anchor docs/evidence/B09-B08-after-final-lifecycle.json
PYTHONPATH=backend backend/.venv/bin/python -m tests.b09_evidence verify --proof docs/evidence/B09-retained-proof.json --lifecycle-log /tmp/civicly-b10or-final-tests.txt --output docs/evidence/B10OR-post-B09-retained.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b09r.py --output docs/evidence/B10OR-post-B09R-history.json
```

Full-suite rolling B07R/B08/B09/B09R proofs are saved as B10OR-regression-* and then their exact accepted c16346a bytes restored. Other historical evidence is never overwritten. Run source/security audit after those restores and after final documentation:

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/audit_b10or.py
 git diff --check
 git apply --reverse --check docs/evidence/B10OR-changes.patch
```

The audit scans actual private credential values without printing them, secret patterns, scope, all accepted tests/evidence, registry/migrations, leaked MCP children and zero-provider proof. Patch includes actual new source files and excludes generated logs/evidence; inventory separately lists everything. No ZIP is generated. Final counts and observed retention results appear in B10OR-RESULTS.md; the commands here do not claim unexecuted future live validation.


The direct retained B09 command above failed at its legacy summary regex (it does
not accept pytest warning fields). Real data/history checks preceded that failure.
Keep the raw log and all historical helpers unchanged; corrected proof command:

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10or_retained.py --log /tmp/civicly-b10or-final-tests.txt --guard /tmp/civicly-b10or-final-provider-requests.json --output docs/evidence/B10OR-post-B09-retained.json
```

PASS: adapter checks raw740-pass/2-warning summary, actual lifecycle markers,
exit0/zero-provider audit, and invokes the original graph/history verifier without
its incompatible formatting parser. No normalization/fake result. The failed
parser condition and raw-log SHA are preserved in B10OR-retention-parser-compatibility.json.
Final suite740pass/0fail/0skip,1249.98s;466unit/274integration.

Minimal original-guard reproduction is B10OR-minimal-reproduction.json:127331
byte/output arithmetic rejects a60000-token budget, whereas the pinned proxy plan
is30394 tokens and the existing mock-HTTP unit case passes. All three real context
cases and exact boundaries are in B10OR-token-benchmark.json.
