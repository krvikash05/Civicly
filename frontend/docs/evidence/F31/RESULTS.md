# F31 — first judging improvement: a complete investigation entry point

Implemented only the first approved improvement. Homepage now features Why did the potholes keep coming back? with a short Market Junction introduction, a six-stage walkthrough preview and one prominent entry link. Browse all investigations remains available as a secondary action.

FeaturedInvestigation reads the retained road investigation INV-B09-b9d4d66e130ed348c4f6a50e9d66a891 and its current plan through authenticated GETs. Completed investigation / Follow a complete investigation are shown only when both native statuses are COMPLETED. Otherwise the ready case is labelled Recorded investigation / Follow this investigation. Loading and unavailable/error states use the existing read handling; the actionable entry appears only after a successful read. The featured case is deliberately curated for this demo, not a dynamic ranking or newly launched investigation.

The link opens that same case at section=report. Existing Next navigation carries it through the workspace. Copy explicitly says Recorded AI investigation, Analyst-assisted plan and Simulated field work. No invented live activity, new recommendation, domain mutation, provider request or agent wake. Current completion labels reflect service state, not a new independent outcome evaluation.

## Changed paths

- frontend/components/featured-investigation.tsx (new)
- frontend/app/page.tsx
- frontend/app/globals.css (scoped featured-investigation styles)
- frontend/docs/tasks.md and this evidence folder
- Append-only:decision.md,flow.md,implementation_status.md,test_log.md,blockers.md,task_board.md

R15/R16/R18;all18requirements preserved. Backend/contracts/dependencies/data unchanged. Local frontend rebuilt/reloaded; AWS not updated.

## Actual verification

- python3 frontend/scripts/check_contracts.py →PASS before implementation.
- npm --prefix frontend test →120 PASS/0FAIL/0SKIP; existing offline tests, not a new live-agent evaluation.
- npm --prefix frontend run build →PASS, including API/contract/type checks.
- Actual local browser →Demo connected, native completed case/plan admitted CTA; six-stage preview and attribution visible; featured link opened original road Report; Next changed to Investigation with the same case ID and offered Next:Evidence. Screenshot featured-browser.png visually inspected.
- No new redundant unit case for presentation wiring. Unavailable/incomplete-case fallback and narrow viewport CSS are not claimed as separately exercised browser scenarios. No full backend or genuine-provider rerun.

## Human verification / next

Refresh http://127.0.0.1:3100. Click Follow a complete investigation →Report, then Next:Investigation. Review the recorded evidence, approval, work and monitoring using the existing stage navigation.

Next approved-series item:F32 graph-to-decision explanation with a focused supporting path, only after review of this entry point. Later items remain stage takeaways, approval-to-outcome timeline, curated journeys and loading/clutter improvements. Stop after F31.
