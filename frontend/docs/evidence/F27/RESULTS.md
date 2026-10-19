# F27 — dashboard card order

Human-requested order implemented in frontend/lib/read/cases.ts: Work completed → Verified outcomes → Active investigations → Awaiting a decision. The Overview maps this array directly, so DOM, visual and keyboard order agree. Existing field bindings, descriptions, icons and dialog actions remain attached to each metric. The existing metrics-order assertion in frontend/tests/cases.test.ts now checks this order.

Verification: npm --prefix frontend test →120 PASS/0FAIL/0SKIP; npm --prefix frontend run build →PASS including generated API, contract and type checks. Contract guard before change PASS. No new test cases or backend/full integration run needed for array reordering. No browser/live claim; local app servers remain stopped. AWS and GitHub have not been updated by this task.

Changed source: frontend/lib/read/cases.ts; frontend/tests/cases.test.ts. Tracking: frontend/docs/tasks.md plus decision.md, flow.md, implementation_status.md, test_log.md, blockers.md, task_board.md (append-only). Evidence: frontend/docs/evidence/F27/.

Human verification after the next frontend preview/deployment: homepage left-to-right should show Work completed, Verified outcomes, Active investigations, Awaiting a decision; each opens its existing records. R15/R16, all18requirements preserved. Next:human review and separately requested deployment; stop after F27.
