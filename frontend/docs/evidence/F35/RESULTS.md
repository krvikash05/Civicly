# F35 — Curated Scenario Journeys

Local PASS, 19 Oct 2026. R01/R15/R16/R18; all eighteen requirements preserved.

Choose a journey now separates returned completed investigations, still-in-progress cases, and retained cancelled cases if present. The original Market Junction road case is suggested first only when actually returned as COMPLETED; it is never inserted when missing. Cards show the source-linked report glimpse, location and what to explore. Links start at Report. The complete S01–S12 catalog remains in a collapsed secondary section, retaining no-connected-run labels and setup limitations. All issues replaces the misleading All Scenarios (12) filter label for the combined investigation/catalog view.

Changed source paths:
- frontend/components/scenario-journey-guide.tsx
- frontend/lib/read/journeys.ts
- frontend/app/globals.css
- frontend/tests/journeys.test.ts

Commands:
- python3 frontend/scripts/check_contracts.py — PASS before change, 59 operations / 55 paths / 185 schemas.
- npm --prefix frontend test — 133 PASS / 0 FAIL / 0 SKIP (tests.txt); three added cases exercise grouping/suggestion state, category/dedup/cross-category semantics and report links/no-run absence. Updated existing link assertion for deliberate Report landing.
- npm --prefix frontend run build — PASS incl API/contracts/types (build.txt).
- make test-spec — both validators PASS (spec.txt).
- git diff --check scoped to changed source/test/tracker paths — PASS.

Actual local browser, retained API reads: 3 completed and 4 ongoing investigations; original road first; full report glimpse/location; waste filter only 3 unfinished waste cases; suggested first link kept exact case and opened Stage 1 Reports & recurrence. Secondary catalog default collapsed; expanding All issues exposed S01–S12 and 11 No connected run labels. Screenshot captured and inspected; browser-proof.txt retains read-only visible proof.

Limits: grouping uses native investigation state, not a claim of verified resolution. Outcome review remains in the case. Reads remain bounded, with the existing next-cursor qualification. Existing catalog source definitions are not promoted to solved scenarios. Suggested original-road narrative is curated for the retained demo case only and gated on its presence/completed status. No mobile-specific audit, new provider/agent execution, worker wake, backend integration rerun or operational write. AWS unchanged.

Human verification: local homepage → Scenarios → completed group first; open suggested road card at Report; reopen → Waste Accumulation → only unfinished waste cases; expand full catalog → unavailable scenarios remain clearly labeled. If unexpected, share this file and screenshot.

All six root trackers and frontend/docs/tasks.md appended. Next F36: reduce loading flashes and visual clutter after human review. STOP.
