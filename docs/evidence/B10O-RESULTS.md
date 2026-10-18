# B10-O review — cost controls without capability reduction

**B10-O PASS — human review pending. B10 live acceptance remains PARTIAL/OPEN. No B11.** Final complete regression691 PASS/0 FAIL/0 SKIP; both specification validators PASS; retained graph/checkpoint/accounting witnesses PASS. No live Gemini request is authorized or performed; all B10-O live investigations are **NOT RUN**, not PASS or FAIL.

## Implemented source and preserved architecture

- `policy.Permit`: explicit investigation/thread-bound opt-in; a key does not authorize calls. Ordinary pytest denies LIVE permits and intercepts Gemini HTTP/DNS in parent and inherited Python children. A mock permit requires actual MockTransport. Separate `tests/live/` operator path delegates to genuine app.agents CLI; legacy paid batch probes cannot run inadvertently.
- `context.build`, B10-3: deterministic compact current state, latest authoritative B09 assessments, all material historical contradictions/classifications/exclusions/provenance/paths/time/uncertainty, recent results and budgets. Full source records and histories remain FalkorDB. Complete source facts and exact schemas are interned by content hash. All16 approved tools remain discovered and accessible, with accurate nested B09 schemas. No scenario-to-tool routing, negative evidence removal or fabricated confidence. Oversized contexts/journals pause explicitly.
- `mcp.Tools`: validated discovery memoization and bounded exact revision/as_of/arguments/permissions/inventory read cache. Hits reference original validated ToolExecution; no new fabricated execution. Original limited-negative status stays limited. Graph changes, including own audit writes, invalidate conservatively.
- `spending.Ledger/Pricing`: private SQLite WAL/FULL, atomic project/case reservation before every HTTP attempt/retry/repair. Defaults **$6 project, $.15 investigation, one concurrent live investigation**. Separate input/output/thinking/cached usage, request/thread/model/milestone/pricing version. Unknown billing stays reserved. Explicit operator cap changes preserve cost/audit. Warnings50/80/95/100; actual over-reservation cost creates a hold. No extra dependency or graph schema migration.
- Provider recovery distinguishes503, short-term429, daily/project/unknown quota, auth/config, unavailable model, invalid JSON, network/overall timeout. Retries are bounded, separately reserved, recheck token allowance and retain sanitized version/usage/failure traces. One JSON repair; no paid fallback. Sessions do not auto-expire into unsafe takeover.

Original actual LangGraph StateGraph, official/domain MCP brokers, read-only exact graph ACL, FalkorDBSaver checkpoints, B03/B05/B09 semantics, immutable migrations and source datasets remain. All18 requirements remain binding; no product feature is complete merely from these controls.

## Measured context and simulated cost

Final measured JSON bytes and simulated estimates are in `B10O-context-WATERLOGGING.json`, `B10O-context-ROAD_DAMAGE.json`, `B10O-context-WASTE_ACCUMULATION.json`. These authored complex states contain8 assessment versions,10 repeated source observations and16 tool interfaces, including negative/excluded/contextual/unreviewed evidence and temporal/path limitations. Separate `B10O-authority-*.json` compares actual B09 two-assessment states and records actual discovered tool names/schema preservation.

Measurements are deterministic serialized UTF8 bytes, not tokenizer output, live reasoning quality or billed savings. Context-only simulated allocation includes framing and output allowance; actual production reservations also include prompt/response schema. Provider-native caching is disabled; no paid caching experiment occurred. New managed ledger allocation is not a historical Google account balance.

## Actual context measurements

| Issue | Before JSON bytes | After JSON bytes | Reduction |
|---|---:|---:|---:|
| WATERLOGGING | 62913 | 56921 | 9.52% |
| ROAD_DAMAGE | 63308 | 57121 | 9.77% |
| WASTE_ACCUMULATION | 63762 | 57512 | 9.80% |

These use actual registry schemas, eight actual B09 assessments and real MCP reads, with all material classifications/paths/source histories checked unchanged. Stable-revision read window:1 actual MCP read+3 references to the original cached execution per case; no fabricated calls. Separate cache integration checks arguments, permission, cutoff and source revision invalidation. Small actual two-assessment cases changed by+28/+10/-2 bytes. The authored8-history/10-observation/shared-schema stress fixture reduces74.8%; it is a different, explicitly synthetic size experiment. None is a billed-token or universal savings claim.

## Verification evidence

**Final complete suite:691 PASS/0 FAIL/0 SKIP in951.17s —432 unit/259 real integration.** All659 previous unique tests retained;32 new. First full run687 PASS in940.94s is overlapping evidence. The intermediate post-recreation attempt failed24 authentication tests/1 Browser passed, was interrupted72.93s and is preserved as B10O-auth-failed-tests.txt. Existing ACL preflight restored authorization; final full rerun passed without code/test weakening. Both specification validators PASS; offline lock check PASS. Entire final suite:0 external Gemini requests,2 intentional blocked HTTP probes,0 unexpected attempts; benchmark also made0 model calls. `B10O-COMMANDS.md` records exact commands; `B10O-FILES.md` and `B10O-changes.patch` provide the incremental changes against the frozen B10 working-tree baseline. Earlier uncommitted B10 code is preserved; HEAD itself is the accepted B09-R baseline. Original B10 evidence is byte-identical after rolling proofs are saved under B10O and restored.

Real local DB/MCP/Saver integration is distinct from deterministic/fake model choice and mocked provider HTTP. SQLite concurrency tests use actual transactions and separate Python processes. HTTP/DNS negative probes deliberately attempt dummy endpoints but are blocked before network; ordinary unexpected attempts must be zero. All live investigations are NOT RUN (no authorization).

## Known limitations and next review boundary

B10 still requires separately authorized genuine three-issue competing-explanation/contradiction/topology-change acceptance and B10-3 live quality verification. Prior503/429 and earlier failures remain recorded unchanged. Internal accounting covers new managed requests; historical/external billing is unknown and not a Google billing hard cap. Unknown billing/stale session ownership needs stopped-process/operator reconciliation; journal/token overflow fails closed. Cache usefulness is deliberately restricted by graph-wide revision changes. Vendor Saver remains multi-query, with existing quarantine/recovery limitations.

Review zero-request proof, actual MCP/catalog and source-reference preservation, spending atomicity/durability, source patch and exact counts. **Stop after B10-O. Next: human review of B10-O and explicit B10 live-acceptance authorization if desired. B11 GraphRAG/memory remains future separately authorized work.**

## Persistence, source/security audit and two-minute review

Actual Docker restart/recreation/Browser verification PASS. B10 source revision103 (80 nodes/47 edges), all6 SDK threads and12 referenced executions match original lifecycle anchor exactly. Accepted B01–B09 sources,101 prior trace observations, immutable B09R history and registry3/migrations0001/0002 preserved. Financial probe's simulated $.020 uncertain+$.001 settled accounting matches exactly across process/container lifecycle. Auxiliary ledger contains no municipal knowledge or keys. Prior evidence hashes are checked after restoring four rolling artifacts.

Source/secret audit checks actual private values and key patterns without printing them; no owned MCP child process remains. See B10O-source-audit.json. Full exact file list: B10O-FILES.md. Patch is incremental against the frozen B10 working tree; older uncommitted B10 is preserved. No ZIP or remote push.

Quick independent verification from repository root (no live provider):

```sh
backend/.venv/bin/python -m pytest backend/tests/unit/test_ai_spending.py backend/tests/unit/test_ai_execution_policy.py backend/tests/unit/test_ai_provider_recovery.py backend/tests/unit/test_agent_context.py -q
make test-spec
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10.py --compare docs/evidence/B10-before-lifecycle.json --output /tmp/civicly-b10o-review-retained.json
PYTHONPATH=backend backend/.venv/bin/python scripts/verify_b10o_spending.py verify --anchor docs/evidence/B10O-spending-before.json --output /tmp/civicly-b10o-review-spending.json
git apply --reverse --check docs/evidence/B10O-changes.patch
```

For a new complete run, perform the documented trusted MCP configure preflight first; use `--run-persistence`. Full suite takes about16 minutes. Live CLI examples are future billable actions only and require separate particular-case approval. **B10 live gates remain OPEN; STOP after B10-O.**
