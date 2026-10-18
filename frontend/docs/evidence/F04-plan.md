# F04 Plan — Investigation Studio and FalkorDB Graph Evidence Experience

## Objective
Implement F04: Investigation Studio with real hypotheses, evidence/citations, bounded graph visualization via official `@falkordb/canvas`, and recorded-decision/path linkage.
Make FalkorDB's contribution visible:
1. Question asked: What did the agent need to establish?
2. Graph evidence: What did FalkorDB actually return?
3. Recorded decision: What did the agent do next, and what rationale was recorded?

## Key Requirements & Invariants
- Use official `@falkordb/canvas` web component package.
- Ensure client-only execution in Next.js (SSR safe).
- Map `GraphSubgraphDTO` to Canvas nodes and links without losing stable IDs or provenance.
- Style verified relationships (solid) vs candidate relationships (dashed) with an explicit visual legend.
- Highlight model-selected decision paths from `decision_paths` / `decision_path_ids`.
- Provide interactive inspector for clicked nodes and links.
- Provide pan, zoom, fit controls and layout mode toggling (force, tree, radial).
- Display truncation and search bounds metadata (`truncated`, `search_limited`, `reservations`, `graph_revision`, `as_of`).
- Provide textual/keyboard accessible alternative for screen readers.
- In Decision Trace, explicitly distinguish model-selected paths from contextual queries; where influence is unestablished, state so truthfully.
- Load real hypotheses (`HypothesisPage`), competing hypotheses, and evidence details (`EvidenceDTO`).
- Never invent graph paths, tool calls, citations, confidence percentages, physical connections, or agent activity.

## Files to Touch / Create
- `frontend/lib/read/graph.ts`
- `frontend/components/falkordb-canvas-view.tsx`
- `frontend/components/decision-trace-panel.tsx`
- `frontend/components/hypotheses-panel.tsx`
- `frontend/components/evidence-detail-modal.tsx`
- `frontend/components/investigation-workspace.tsx`
- `frontend/app/globals.css`
- `frontend/tests/canvas-adapter.test.ts`
- `frontend/scripts/integration_probe.ts`
- `frontend/scripts/verify_integration.py`
- `frontend/docs/evidence/F04-plan.md`
- `frontend/docs/evidence/F04-files.txt`
- `frontend/docs/evidence/F04-results.md`
- `frontend/docs/evidence/F04-integration.json`
- `frontend/docs/tasks.md`

## Verification Strategy
1. Unit tests in `frontend/tests/canvas-adapter.test.ts` covering mapping, styling, decision trace extraction, influence distinction, and schema validation.
2. Full test suite: `npm test` (all tests passing).
3. Static checks: `npm run check:api`, `npm run contracts`, `npm run typecheck`, `npm run build`.
4. Specification checks: `validate_blueprint.py`, `validate_handoff.py`.
5. Real integration run: `frontend/scripts/verify_integration.py` exercising real proxy, FastAPI, and FalkorDB.
