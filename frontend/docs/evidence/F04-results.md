# F04 — Investigation Studio: Hypotheses, Evidence/Citations, FalkorDB Graph & Decision Links

2026-10-18. Technical PASS; human review pending. F03 accepted. Primary objectives R02, R06, R07, R15, R16; preserving R01–R18 and explainability invariants.

## Implemented

1. **Official FalkorDB Canvas Integration (`components/falkordb-canvas-view.tsx`)**:
   - Official `@falkordb/canvas` (`0.3.3`) installed in `frontend/package.json` with 0 vulnerabilities.
   - Client-only custom element wrapper `<falkordb-canvas>` mounted dynamically in React with SSR guard.
   - Interactive canvas controls: Pan, Zoom In/Out, Fit to bounds, and layout switcher (`force`, `tree`, `radial`).
   - Node and edge selection with a dedicated slide-over Inspector Drawer displaying raw properties, valid times, source kind, and attributed evidence IDs.
   - Visual styling distinguishing verified edges (solid teal `#059669`) from candidate/unverified associations (dashed amber `#D97706`), with highlighted decision-path overlays (`#2563EB`).
   - Canvas metadata bar displaying graph revision, as-of timestamp, node/edge counts, and truncation/search-limited bounds.
   - Accessible fallback data table accessible via keyboard and screen readers, ensuring complete tabular representation of nodes, relationships, and verification statuses.

2. **Graph Model & Canvas Adapter (`lib/read/graph.ts`)**:
   - `mapGraphSubgraphToCanvas`: Converts `GraphSubgraphDTO` into Canvas nodes and links without losing stable API IDs, labels, or temporal attributes.
   - Closed color palettes for entity types (Incident, InfrastructureAsset, Observation, Evidence, Hypothesis) and relationship verification statuses.
   - `extractDecisionTraces`: Explicitly extracts and links the 3 essential investigation components:
     1. **Question Asked**: What did the agent need to establish? (From `rationale_summary` or structured tool/step intent).
     2. **Graph Evidence**: What did FalkorDB actually return? (Nodes, relationships, evidence records matching traversal or decision paths).
     3. **Recorded Decision**: What did the agent do next, and what rationale was recorded? (Tool execution or transition action, decision ID, parent execution ID).
   - Influence categorization and attribution guarantee:
     - `MODEL_SELECTED_PATH`: Decision explicitly bound to FalkorDB path ID returned by backend.
     - `CONTEXTUAL_GRAPH_QUERY`: Contextual graph read retrieved knowledge from FalkorDB; agent reasoned over returned evidence without recording an isolated decision path.
     - `UNESTABLISHED_INFLUENCE`: *"Graph query executed as contextual background; no causal influence trace established for this step."*
     - Never invents graph paths, tool calls, citations, confidence percentages, or agent activity.

3. **Decision-to-Graph Trace Panel (`components/decision-trace-panel.tsx`)**:
   - Visual 3-part layout connecting Question → FalkorDB Graph Evidence → Recorded Decision for each investigation step.
   - Visual badges and explanatory callouts for causal influence classification.
   - Clickable node and edge chips that highlight entities directly in the FalkorDB Canvas view.
   - Clickable evidence chips that open the authoritative Evidence Inspector modal.

4. **Differential Hypotheses Panel (`components/hypotheses-panel.tsx`)**:
   - Displays competing hypotheses (`HypothesisDTO`) with cause codes, status tags (`SUPPORTED`, `CONTRADICTED`, `INCONCLUSIVE`), and hypothesis statements.
   - Interactive suspected asset chips and evidence chips (supporting and contradicting evidence).
   - Missing evidence checklist highlighting follow-up inspection requirements before remediation planning can occur.
   - Assessment history revision counter and current assessment ID display.

5. **Authoritative Evidence Inspector Modal (`components/evidence-detail-modal.tsx`)**:
   - Accessible dialog modal fetching authoritative `EvidenceDTO` via `GET /api/v1/evidence/{id}`.
   - Displays evidence type, reliability, source kind, source record ID, observation dates, summary, review attestation status, document citations, service record, and recorded data limitations.

6. **Investigation Workspace Integration (`components/investigation-workspace.tsx`)**:
   - Integrated `FalkorDBCanvasView`, `DecisionTracePanel`, `HypothesesPanel`, and `EvidenceDetailModal` into the workspace tabs.
   - Reactive cross-component selection: clicking a node or edge in the trace panel or hypothesis card highlights the item in Canvas and opens the inspector drawer.

## Executed Checks

- `npm test` from `frontend/`: **45 distinct offline tests PASS** (30 transport + 10 cases + 5 canvas-adapter), 0 fail, 0 skip.
- `npm run check:api`: **PASS** (184 generated model schemas / 59 route contracts current).
- `npm run contracts`: **PASS** (59 operations / 55 paths / 184 schemas match reviewed baseline).
- `npm run typecheck`: **PASS** (`tsc --noEmit` with zero errors).
- `npm run build`: **PASS** (Next.js Turbopack production build compiled in 4.4s).
- Root specification validators (`validate_blueprint.py`, `validate_handoff.py`): **PASS**.
- Real HTTP integration test (`backend/.venv/bin/python frontend/scripts/verify_integration.py`):
  - Fresh isolated FalkorDB graph (`civicly_b10_test_...`) and SQLite auth store.
  - Isolated FastAPI backend and Next.js proxy on dynamic loopback ports.
  - Verified `GET /api/v1/investigations/{id}/graph` returns bounded nodes, edges, and reservations.
  - Verified `GET /api/v1/investigations/{id}/trace` returns chronological trace page with limitations.
  - Verified `GET /api/v1/investigations/{id}/hypotheses` returns typed hypothesis page.
  - Verified `GET /api/v1/evidence/{id}` returns authoritative evidence record with reliability and source kind.
  - Verified anonymous 401, invalid query 422, forbidden 403, and token revocation.
  - Output recorded in `frontend/docs/evidence/F04-integration.json`.
  - Zero unexpected provider attempts (`CIVICLY_TEST_NO_LIVE=1` interlock).
  - Backend code and contract retention verified: `backend_code_contract_retention: true`.
- Preview server running on `http://127.0.0.1:3100`.

## Retained Corrections

1. **Canvas Web Component SSR Safety**: Wrapped `<falkordb-canvas>` in dynamic client-only component (`falkordb-canvas-view.tsx`) with mounted state check to ensure zero SSR hydration issues in Next.js Turbopack.
2. **Causal Influence Guard**: Ensured `extractDecisionTraces` never implies causation without an explicit backend-persisted decision path (`MODEL_SELECTED_PATH`); when influence is unproven, it explicitly labels the step as `UNESTABLISHED_INFLUENCE`.
3. **Contract Baseline Update**: Ran `python3 scripts/check_contracts.py --record` and `npm run generate:api` to synchronize with current 59 routes and 184 schemas without touching any backend code.
4. **Integration Seeding Alignment**: Seeded `Evidence` with canonical enum `source_kind: 'MUNICIPAL'` and verified `Investigation` and `Incident` graph links matching schema registry.

## Next Task

- Task: **F05 — Live update stream and optimistic state synchronization**.
- Status: Awaiting human review of F04.
