# Frontend requirements preserved while backend is built

**Do not build UI yet.** Backend must provide exact typed resources so a polished UI can be implemented without redesigning agent intelligence.

## Five coherent workspaces (later)
1. Command Center: active problem clusters, incident maps, agent activity, pending approvals, overdue simulated tasks and outcome trends.
2. AI Investigation Studio (flagship): live agent timeline from persisted SSE; tool selection and MCP traces; root-cause hypotheses + contradiction evidence; FalkorDB path graph; source inspector; next inspection or plan; operator action.
3. Civic Intelligence Explorer: geographic layers showing all three issue categories; FalkorDB Canvas shows actual bounded subgraph, filtered by asset/incident/case and evidence reliability; temporal relationship filter.
4. Resolution Operations: plan DAG, approvals with exact versions, department ownership, work-order history and monitoring status.
5. Knowledge & Memory: relevant past investigations, failed repair/corrections, municipal procedures with source excerpt and version, explanation of prior decisions.

## Reusable API-driven components
- `IssueBadge`, `CaseStatus`, `SourceCitation`, `EvidenceCard`, `HypothesisComparison`, `AgentActivityTimeline`, `ToolCallDetail`, `GraphEvidenceCanvas`, `CivicMap`, `ApprovalCard`, `ActionPlanDAG`, `WorkOrderTimeline`, `MonitoringCriteria`, `SimulationBadge`, `ScenarioSelector`.
- Every component must display `unknown`, `unverified`, `simulated`, `loading`, `empty`, `error`, `unauthorized`, `source unavailable` states correctly. Never show unsupported 93% confidence or fake agent activity.

## Essential backend DTOs
Refer to `docs/backend/08_api_frontend.md` and `contracts/api_endpoints.json`. `graph nodes/edges` include provenance, verification statuses, relationship valid times, decision path IDs; SSE includes persisted tool step IDs and cursor; hypotheses include assessment history and conflicting refs; plan includes tasks/dependencies/approval data; docs include source/version.

## Browser and Canvas
Use FalkorDB Browser at local port 3000 as developer inspector; future UI uses official FalkorDB Canvas npm component if compatible with Next.js hydration. Canvas receives backend `GraphSubgraphDTO`; frontend never queries DB. Verify component mapping in separate frontend spike after backend gate.

## Demo narrative fit
One click should follow complaint → graph evidence → hypothesis → inspection → plan approval → work-order progress → outcome and recurrence memory, without tab-hunting. Light-first professional aesthetic and optional dark mode; design detail follows backend acceptance, not needed to implement runtime.
