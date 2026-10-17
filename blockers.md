# blockers.md — Current blockers and verification spikes

No active implementation blocker is claimed. Verification spikes (NOT defects) are tracked in `docs/backend/12_falkordb_sources.md`.

## Template
### BLOCK-XXX / Bxx
- Symptom + minimal repro:
- Exact command + error:
- Impacted requirements:
- Attempts (non-destructive):
- Root cause hypothesis / needed human action:
- Workaround considered and why it preserves all objectives:
- State: OPEN / RESOLVED:

## B00 findings | 2026-10-17
### BLOCK-B00-01 — Environment | RESOLVED FOR AUDIT; B01 setup pending
- `python --version`: absent. `python3 scripts/validate_blueprint.py`: missing jsonschema, exit 1. Existing `python3.12` with jsonschema runs both validators successfully, no installs needed.
- `docker version`: sandbox socket denial; read-only escalated retry confirms running Engine 29.8.2. No Docker-start action needed.
- `git status --short`: not a git repository. Initialize local Git and isolated project dependencies in B01. No public account required.
- Selected provider/model/auth/MCP key variables unset in inspected process. Configure chosen model/provider locally before live tests; never paste keys into chat. Not a B00 blocker.
### BLOCK-B00-02 — Contract/fixture discrepancies | OPEN
- Confirmed: 55 expanded Observation nodes use unregistered value_number. Generator repeats it; supplied validators miss it. Reproduce with TEST-20261017-B00-04. Blocks trustworthy B04 import until aligned.
- DEC-004 details scope schema (B02), MCP envelope/traces (B07), source version/owner/PDF (B11), approval binding (B12/B13), event durability (B15), API mapping (B17), historical scenario records/evaluator isolation (B19).
- Human action needed now: review B00 and say continue for B01. No decision or credential needed to finish audit; later tasks must correct gaps before consuming affected contracts.
- Runtime proofs deferred by task boundary, not replaced by mocks: graph persistence, RO_QUERY, MCP, checkpoint restart, GraphRAG, durable recovery and live LLM.

## B01 follow-up | 2026-10-17
### BLOCK-B01-01 — Isolated dependency/Git sandbox access | RESOLVED
- Initial sandbox pip install failed DNS/network resolution; repeated authorized network install succeeded in backend/.venv only. Initial git init got Operation not permitted; approved escalation initialized main. Docker socket access used authorized escalation. No auto-review rejection occurred.
- Initial wrong image-entrypoint paths returned file-not-found; docker image inspect identified /var/lib/falkordb/bin/run.sh, then actual entrypoint/storage inspected successfully. No unsupported version workaround needed.
### BLOCK-B01-02 — Fresh graph health assumption | RESOLVED
- Repro: official client select_graph('civicly_knowledge').ro_query('RETURN $probe LIMIT 1', params={'probe':'health'}, timeout=1000) before initialization -> `Invalid graph operation on empty key`.
- First integration suite: 2 FAIL, 4 PASS (health and CLI failed). Fixed observational health with explicit uninitialized/null-read state; existing graph still requires real RO_QUERY. Final 15-test suite PASS. No sentinel inserted into canonical graph; B02 unchanged.
### BLOCK-B00-02 — Continued OPEN (not waived by B01)
- All 55 Observation.value_number defects remain; contracts and fixtures untouched. Same scope naming, MCP traces, approval binding, document ownership/version/PDF, historical records, event metadata/revision mapping and evaluator isolation findings in DEC-004 remain scheduled before consumption.
- Dependency compatibility with MCP/LangGraph/FalkorDBSaver/GraphRAG and live provider is still UNVERIFIED; not required for B01. Local graceful persistence does not resolve event durability or checkpoint recovery.
- Human action now: review B01; say continue for B02 when accepted. No active B01 environment blocker. If tests fail, share test output + test_log/blockers and redacted compose logs; never .env/full config containing secrets.
