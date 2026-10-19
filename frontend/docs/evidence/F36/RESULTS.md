# F36 — Calm loading states and less repeated clutter

Local PASS, 19 Oct 2026. R09/R15/R16/R17; all eighteen requirements preserved.

Connecting enabled reads now use loading, never unavailable. Disabled reads stay unselected. The visible read-state projection preserves the existing session identity/key fence; saved records from another session/case are never displayed. Current-scope cached data can remain visible during refresh; confirmed failures still surface as errors. Selected case loading uses neutral panel placeholders instead of Select an investigation/Data unavailable; graph loading no longer exposes raw investigation IDs. Dependent directory/journey reads show catalog loading rather than a disabled-read selection prompt. Dashboard accessibility labels say loading during startup.

Reduced repeated clutter: removed the homepage connected-account banner (header connection/session controls remain), duplicate in-stage next-action card, and large Work/Monitoring completion reminders. Stage takeaways, response timeline, panel explanations, simulated labels, outcomes and actual error/recovery controls retain the relevant distinctions. Monitoring waits for its initial reads before rendering empty-looking records. No backend or provider behavior changed.

Exact source/test paths:
- frontend/lib/read/read-state.ts (new)
- frontend/components/use-read.ts
- frontend/components/read-state.tsx
- frontend/components/demo-connection.tsx
- frontend/components/investigation-workspace.tsx
- frontend/components/work-orders-panel.tsx
- frontend/components/monitoring-memory-panel.tsx
- frontend/components/case-directory.tsx
- frontend/components/scenario-journey-guide.tsx
- frontend/app/page.tsx
- frontend/app/globals.css
- frontend/tests/transport.test.ts

Verification:
- python3 frontend/scripts/check_contracts.py — PASS before change, 59 operations / 55 paths / 185 schemas.
- npm --prefix frontend test — 136 PASS, 0 FAIL, 0 SKIP (tests.txt). Three new state-boundary cases cover connecting versus failed/ended, disabled selection, cached session/case mismatch, confirmed errors and current-scope refresh data.
- npm --prefix frontend run build — PASS including API/contracts/types (final build-verified.txt). Earlier successful builds retained; later builds checked dependent-loading presentation and dashboard accessibility correction.
- make test-spec — both validators PASS (spec.txt).
- git diff --check scoped changed source/test/trackers — PASS.
- Actual fresh local Work browser initially showed Connecting to the demo workspace in case/graph, not Select an investigation or Data unavailable. Loaded Work showed 3/3 completed, actual orders and verified follow-up without duplicate large reminders. Stage 6 kept evidenced closure. Homepage retained Demo connected and featured-case entry without connected-account banner. Final fresh homepage AX showed all four metrics labeled loading, not Unavailable. Screenshots captured and inspected.

No forced network failure/session-expiry browser drill, mobile audit, new live-agent/provider calls, backend integration rerun, worker wake or operational writes. Failure/session-isolation branches verified with unit cases and existing transport suite. Page reads/normal temporary demo sessions only; no case state changes. Existing backend acceptance/recovery/follow-up obligations remain; AWS unchanged.

Human verification: refresh a local selected case; expect neutral connecting/loading before actual records. Switch Work → Monitoring: takeaways, milestones and source details remain; repeated large reminder boxes are removed. Homepage keeps header connection status. If unexpected, share this file and screenshot.

Six root trackers and frontend/docs/tasks.md appended. All six planned judging improvements are implemented locally. Next: human review, then deployment of the reviewed frontend to existing AWS demo only after explicit authorization. STOP.
