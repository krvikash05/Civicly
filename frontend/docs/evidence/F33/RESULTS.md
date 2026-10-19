# F33 — One clear takeaway per workspace stage

Local PASS, 19 Oct 2026. Requirements R09/R15/R16/R17; all eighteen requirements remain binding.

Each selected stage has one compact Key takeaway above the detailed records. Report uses the linked report and location; Investigation summarizes validated completed checks or uncertain-operation review; Evidence uses current assessments; Plan summarizes actual task actions and recorded work authorization; Work counts only orders for the current plan; Monitoring requires an evidenced, closed RESOLUTION_VERIFIED outcome attached to completed current-plan work and scopes retained memory to the investigation. Missing/loading/error states are explicit. A legacy approval label alone is not treated as authorization. A newer contrary outcome for the same order suppresses the closure takeaway.

Changed application paths:
- frontend/lib/read/stage-takeaway.ts (added)
- frontend/components/investigation-workspace.tsx
- frontend/app/globals.css
- frontend/tests/workflow.test.ts (four added boundary cases)

Commands and results:
- python3 frontend/scripts/check_contracts.py — PASS before change; reviewed 59 operations / 55 paths / 185 schemas.
- npm --prefix frontend test — 125 PASS, 0 FAIL, 0 SKIP (tests-final.txt).
- npm --prefix frontend run build — PASS including API generation check, contract guard and TypeScript (build-final.txt).
- make test-spec — both validators PASS (spec.txt).
- git diff --check scoped to changed tracked application/test paths — PASS.

Actual read-only browser: all six original-road stages PASS; report description/location, eight validated tool results, two supported explanations, recorded authorization, 3/3 completed orders, evidenced closure plus retained memory. Waste monitoring correctly remains unverified. Screenshots inspected. These are real API reads of retained records, not a new live-agent/integration execution. No provider requests, workers, database changes or backend test rerun. No mobile browser audit. Earlier frontend/backend acceptance limitations remain; AWS unchanged.

Human verification: open the local original road case, use the six stage buttons and read each Key takeaway above the details. Open the waste case Monitoring & memory and confirm it does not claim resolution. If unexpected, share this result file and a screenshot.

Root six trackers and frontend/docs/tasks.md appended. Next: F34 approval/work/outcome timeline, after human review. STOP.
