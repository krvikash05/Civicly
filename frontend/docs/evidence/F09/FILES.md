# F09 task-owned inventory

Exact diff in changes.patch is against captured task-start preimages, preserving preexisting Antigravity changes. Backend source, contracts, data and runtime/private configuration were not edited.

## Modified

- frontend/components/evidence-detail-modal.tsx
- frontend/components/shell.tsx
- frontend/components/role-governance-modal.tsx
- frontend/components/case-directory.tsx
- frontend/components/decision-trace-panel.tsx
- frontend/components/work-orders-panel.tsx
- frontend/components/plan-approval-panel.tsx
- frontend/components/read-state.tsx
- frontend/components/monitoring-memory-panel.tsx
- frontend/components/live-stream-panel.tsx
- frontend/components/investigation-workspace.tsx
- frontend/components/hypotheses-panel.tsx
- frontend/components/falkordb-canvas-view.tsx
- frontend/lib/read/display.ts
- frontend/lib/read/cases.ts
- frontend/lib/read/graph.ts
- frontend/lib/read/memory.ts
- frontend/lib/api/errors.ts
- frontend/components/use-read.ts
- frontend/app/globals.css
- frontend/package.json
- frontend/docs/tasks.md
- frontend/tests/canvas-adapter.test.ts
- frontend/tests/display.test.ts

## Added

- frontend/lib/read/workflow.ts
- frontend/tests/workflow.test.ts
- frontend/scripts/verify-readability.mjs

Also appended frontend/docs/tasks.md and sixroottrackers. Evidence is in thisdirectory. No commit/push/clouddeployment.
