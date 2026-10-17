# task_board.md — Human-reviewed task queue

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
