# task_board.md — Human-reviewed task queue

## Current status — B05, 2026-10-17 (takes precedence over history)

B04 externally accepted. B05 PASS — human review pending.309 tests PASS (218 unit/91 real integration),0 FAIL/0 SKIP; both SPEC validators PASS. Controlled ablation, actual-city diagnostics and260 read-only performance runs recorded. Next B06 TODO; no MCP implementation started.

---

**Rule:** one task per Codex turn. `TODO` → `IN_PROGRESS` → `PASS` (evidence in test_log) or `BLOCKED`.

Current: **B00 TODO**. See `docs/backend/11_microtasks.md` for ordered task list and exact gates. Codex must populate per-task ledger here and never pre-mark tasks as passed.

| Task | State | Test log ID | Human accepted? | Note |
|---|---|---|---|---|
| B00 | TODO | — | No | Audit specifications and local runtime |

## B00 review ledger | 2026-10-17 (supersedes initial TODO)
Current: **B00 PASS — audit delivered; human acceptance pending**. Next: **B01 TODO**, only after user continues.

| Task | State | Test log | Human accepted? | Note |
|---|---|---|---|---|
| B00 | PASS | TEST-20261017-B00-01–04 | No | Audit exercised; validators pass; fixture/contract risks remain open |
| B01 | TODO | — | No | Backend skeleton, isolated dependency spike, Docker FalkorDB/Browser persistence, CLI health; real CREATE/MATCH/restart proof |

B00 PASS means audit acceptance criteria met, not specification perfection or a running backend. No subsequent task started.

## B01 review ledger | 2026-10-17 (current; supersedes prior ledger)
Current: **B01 PASS — human review pending**. B00 explicitly accepted by user. Next: **B02 TODO**, only after user continues.

| Task | State | Test log | Human accepted? | Note |
|---|---|---|---|---|
| B00 | PASS | TEST-20261017-B00-01–05 | Yes | User accepted audit and preserved open contract findings |
| B01 | PASS | TEST-20261017-B01-01–06 | No | 15 tests PASS; real CREATE/MATCH, RO denial, restart/recreation, Browser, locked dependencies |
| B02 | TODO | — | No | Formal migrations, unique/mandatory constraints and indexes, multi-label adapter, registry mapping, rollback/upgrade policy; real idempotence/readiness/invalid-ID tests |

No B02 work or frontend started. B01 foundation evidence does not fulfill B-END or resolve BLOCK-B00-02.

## B02 review ledger | 2026-10-17

| Task | State | Test log | Human accepted? | Note |
|---|---|---|---|---|
| B00 | PASS | TEST-20261017-B00-* | Yes | Remaining findings preserved |
| B01 | PASS | TEST-20261017-B01-* | Yes | Local baseline commit426f6e1; full regression retained |
| B02 | PASS | TEST-20261017-B02-01–06 | No | Canonical0001 READY;91 index groups/182 constraints OPERATIONAL;53 tests PASS |
| B03 | TODO | — | No | Typed repositories, endpoint/temporal/cardinality/verified-path policies and bounded preapproved query templates; actual traversal and invalid-edge rejection |

No B03 implementation, seed import or frontend started. B02 is schema foundation only, not B-END.

## B03 review ledger | 2026-10-17

| Task | State | Test log | Human accepted? | Note |
|---|---|---|---|---|
| B00–B02 | PASS | Historical logs | Yes | Baseline3db6d87; original findings preserved |
| B03 | PASS | TEST-20261017-B03-01–06 | No | Typed repositories, declared integrity policies,8 bounded RO families;89 acceptance PASS; review pending |
| B04 | TODO | — | No | Explicit v1/v2→v3 conversion,55 value_number corrections with evidence, provenance-safe duplicate-resistant ingest; only after review |

STOP at B03. No ingestion, agents, MCP/GraphRAG, operations, domain API or frontend
started. No completion of a product capability is inferred from graph access tests.

## B03-R corrective review ledger | 2026-10-17

| Task | State | Human accepted? | Scope |
|---|---|---|---|
| B03 | PASS | Provisionally | External review requests contract corrections before B04 |
| B03-R | IN_PROGRESS | No | Cardinality, total-path budgets, reusable isolated target guard, B04 benchmark plan; real corrective + full regressions |
| B04 | TODO | No | No conversion/import/fixture repair started; blocked on human B03-R review |

## B03-R final review gate (supersedes in-progress ledger) | 2026-10-17

| Task | State | Test log | Human accepted? | Note |
|---|---|---|---|---|
| B03-R | PASS | TEST-20261017-B03R-01–05 | No |135 tests PASS,22 template checks PASS,both SPEC validators PASS; corrected contracts/source ready for review |
| B04 | TODO | — | No | Explicit conversion/55-defect correction/ingestion/provenance/idempotence + documented benchmark, only after review |

STOP here. A test graph named for milestone04/25 verifies namespace authorization;
it does not implement that milestone. No city graph ingestion or B04 repair started.

## B04 review ledger | 2026-10-17
| Task | State | Human accepted? | Evidence / boundary |
|---|---|---|---|
| B03-R | PASS | Yes | Accepted in B04 authorization |
| B04 | PASS — review pending | No | Explicit conversion/import;3 real full trials +6 no-op repeats; source-quality gaps retained |
| B05 | TODO | No | Algorithms/case retrieval and isolated counterfactual clone only after human authorization |

Review source audit, field deltas/quarantines, scenario-readiness matrix, retained
isolated graph and real test/benchmark output. Do not interpret data ingestion as
working scenario, agent, MCP or operations capability. STOP for human B04 review.

## B05 final review ledger | 2026-10-17

| Task | State | Human accepted? | Evidence / exact next boundary |
|---|---|---|---|
| B04 | PASS | Yes | User external review accepted; baseline8aaf17c,258 regression PASS |
| B05 | PASS — review pending | No |309 PASS; bounded algorithms/cases, owned ablation, actual city/source gaps,260 measurements, focused source ZIP |
| B06 | TODO | No | Official FalkorDB MCP runtime dependency + real client tools/list/tools/call, auth and explicit read-only tool filtering; only after human review |

Human checks before/after criticality/paths/source fingerprints, city verified vs
exploratory distinction, data dependency matrix, exact test counts and ZIP manifest.
No full product requirement is completed just by graph primitives. STOP after B05.
