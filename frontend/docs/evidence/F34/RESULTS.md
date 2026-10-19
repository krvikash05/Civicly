# F34 — Approval, work and outcome timeline

Local PASS, 19 Oct 2026. R09/R10/R11/R15/R16/R17; all eighteen requirements preserved.

Added The response at a glance to Plan & approval, Work and Monitoring & memory. Four compact milestones connect recommended actions, human authorization, simulated work and independent follow-up. Expandable records show department/crew work status and actual dated follow-up with source links. Buttons navigate within the same selected case. Current-plan work only; foreign outcomes are excluded. Completed work and utility verification cannot imply overall resolution; a newer contrary assessment suppresses the closure summary. Null reads stay unavailable; loading and plan failures use explicit states.

Changed application paths:
- frontend/lib/read/response-timeline.ts (new pure projection)
- frontend/components/response-timeline.tsx (new UI)
- frontend/components/investigation-workspace.tsx
- frontend/app/globals.css
- frontend/tests/workflow.test.ts (five new boundary cases)

Authorization is inferred only from existing current-plan work orders referencing persisted approvals, not PlanDTO.approval_status. Approver-only endpoints are not queried or bypassed. The view does not claim actor identity or an approval timestamp. Work timestamps are not exposed by the current DTO; milestone numbers indicate conceptual stages, not fabricated event chronology. Dated follow-up retains actual evaluation times, earlier monitoring and utility-only results.

Verification:
- python3 frontend/scripts/check_contracts.py — PASS before implementation: 59 operations / 55 paths / 185 schemas.
- npm --prefix frontend test — final 130 PASS, 0 FAIL, 0 SKIP (tests-final.txt). Initial 129/130: foreign-work test accidentally used PENDING_APPROVAL while expecting draft state; fixture corrected to DRAFT, initial output retained in tests.txt.
- npm --prefix frontend run build — PASS, including API/contracts/types (build.txt).
- make test-spec — both validators PASS (spec.txt).
- git diff --check scoped changed paths — PASS.
- Actual browser with real retained API reads: original road 3 recommended actions, recorded authorization, 3/3 completed work and five dated assessments culminating in verified closure; expandable work/outcomes PASS. Evidence button opened actual source modal; work button navigated same selected case to Stage 5. Waste 1/1 completed work with two outcomes remains Verification still needed. Screenshots captured and inspected.

No provider calls, worker wake, operational writes or backend integration rerun. API reads remain bounded; this is not a complete historical audit or a new autonomous execution. Mobile not separately tested. AWS unchanged. All root trackers and frontend/docs/tasks.md appended.

Human verification: open original road Plan & approval, expand work progress and dated follow-up, review a supporting source, then use View work details. Open waste Monitoring & memory: verify completed work still requires verification. If unexpected, share this file and screenshot.

Next: F35 curated Scenario Journeys after human review. STOP.
