# B11-LIVE-SMOKE — BLOCKED before provider execution

One authorized execution attempted; no retry/resume/model switch or B12.

## Exact bound scope

- Profile `.runtime/b11-live-smoke-agent.json` (private, excluded).
- Investigation `INV-B09-d8b67c785a6aa6bdcf800dbefe0a4f2f`.
- Thread `ae94b094ee9f4ad599f88789df4d959e`.
- Source `civicly_b10_test_9099c5d03dfd45559ffcaa7b70e9ec31`.
- Saver `civicly_b10_checkpoints_e05f9201988146b1aa043078f208e240`.
- Configured Gemini `gemini-3.8-flash`; actual reported version UNAVAILABLE (no response).

## Nonbillable verification and failure

Official Google docs checked: model supports structured outputs and LOW thinking;
GenerationConfig.responseJsonSchema and countTokens.generateContentRequest are
supported. Standard prices0.75input/3.75output+thinking per1M through2026-12-31 match
unexpired bundled schedule; count endpoint documented nonbillable.
Sources: https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash,
https://ai.google.dev/api/generate-content,
https://ai.google.dev/api/tokens,
https://ai.google.dev/gemini-api/docs/pricing,
https://firebase.google.com/docs/ai-logic/count-tokens.
No model endpoint or credential validation call was made during preflight.

Actual official+domain MCP discovery PASS,16catalog entries. Source reader exact-key
RO ACL PASS. Actual Drainage INSPECTION preflight returned validated source citations;
this was host-selected, **not live Gemini organizational retrieval**. Offline6 harness
interrupt cases PASS1.28s;0fail/skip, ordinary inherited provider guard0requests.

Execution recorded sanitized host ExceptionGroup before provider scope. Read-only
fresh process found no thread binding, no checkpoint, no model decision/execution,
and retained wake quarantine. Root cause established by deterministic precondition:
fixture create() uses2026-10-18T12:00:00Z, while wall UTC was06:25:41 during diagnosis.
Control.bind's current updated_at would move backwards and violate repository policy.
Preflight omitted temporal visibility verification; this is a harness defect, not
Gemini incompatibility or a permission failure. Exact inner original exception was
not captured; do not confuse read-only reproduction of precondition with a captured
original stack. Subsequent diagnostic had a separate relative-profile-path failure;
corrected to absolute path for read-only discovery, catalog matches exactly.

Existing B10-3 prompt still prohibits organizational memory tools. Preserved; future
approved smoke must disclose/resolve this compatibility issue before claiming B11
live retrieval. No accepted prompt or application logic changed by this smoke.

## Limits and accounting

Case cap$0.15; output2048; zero transient retries; one provider decision; at most2
schema-generation attempts/2count attempts; runtime budget2iterations/1tool/60000tokens/
120seconds/1wake. Public LangGraph interrupts before analytical/planning/coordinator
handlers and after Investigator prevent out-of-scope writes or another selection.
Exclusive start marker prevents repeat execution. Initial generation estimate
$0.03395325; this was not charged or reserved because provider scope was never reached.

Actual count attempts **0**, generation attempts **0**. Known cost$0; held unknown
reservations$0; active sessions0; open holds0. Default live ledger did not exist:
initialized once through existing Ledger implementation, unchanged default project
cap$8/defaultcase$0.50, explicit new smoke case$0.15. No prior ledger recreated,
project limit raised, historical hold cleared or counters reset. Three accepted
accounting-probe files remain byte-identical. Application cap is not a Google
billing hard cutoff or an account balance verification.

No selected tool/argument summary/provider usage/returned model version or durable
model-selected trace/checkpoint IDs exist. Host preflight trace ID and citations are
in preflight.json, clearly separate from missing live proof. Earlier evidence/data/
checkpoints/tests are preserved; no container restart or full regression.

## Exact commands

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-live-harness-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_live_smoke_harness.py -q > /tmp/civicly-b11-live-harness.txt 2>&1
PYTHONPATH=backend backend/.venv/bin/python scripts/b11_live_smoke.py prepare > /tmp/civicly-b11-live-preflight.txt 2>&1
PYTHONPATH=backend backend/.venv/bin/python scripts/b11_live_smoke.py execute --live > /tmp/civicly-b11-live-execution.txt 2>&1
```
6offlinePASS; actual MCP/source preflightPASS except missed temporal prerequisite;
single attempted execution BLOCKED,0providercalls. No accepted7cases/full313/770
rerun. No final SPEC rerun: application/contract sources unchanged; only narrow
manual harness and static-fence unit tests added. Read-only fresh-process source,
checkpoint, catalog and accounting diagnostics recorded in host-diagnostic.json and
execution.json; no live verify command possible because checkpoint absent.

## Review and next action

Human verification is nonbillable: inspect authorization.json, execution.json,
host-diagnostic.json and source-audit.json; expect0requests/$0exposure/no checkpoint/
future fixture time/quarantine retained. Do not run prepare/execute again: exclusive
markers intentionally deny retries. No missing provider evidence is substituted.

Proposed corrective action for separate authorization: use valid host-clock synthetic
fixture before binding, validate all referenced record times before first attempt,
and review exact original thread/quarantine recovery without deleting records or
bypassing monotonic policies. Improve sanitized nested exception categorization.
No automatic retry, replacement case, resume, cap increase or quarantine clear.
B10 three-category, contradiction, topology perturbation and full end-to-end live
acceptance remain OPEN/PARTIAL. B11/B11-R technical evidence unchanged. STOP for review.
