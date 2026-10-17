# Judge-facing story and interactive demonstration controls (planned commands)

## Why these demonstrations work
The user sees three issue categories and one *confirmed-or-rejected* chain; FalkorDB paths show why particular assets/operations are related, MCP trace shows choices, memory demonstrates learning, GraphRAG shows municipal ownership/procedures, and authorization + monitoring prove action coordination. Use genuine backend queries and agent traces; never play pre-recorded mock output as if live.

## Setup flow
1. `docker compose up -d` (planned); inspect FalkorDB Browser on localhost:3000 and `GET /health/ready`.
2. `civicly demo reset --scenario S07 --confirm`; show source dataset count and fictional-city banner.
3. `civicly investigate --incident INC-FLOOD-02` or launch from Swagger route; show real MCP `tools/list` / `tools/call` and path to D18, related waste and road clusters.
4. Open trace view/CLI; explain H1/H2/H3, supporting evidence and why it requests an inspection.
5. Simulated inspector submits event stage 2; run resumes via persisted checkpoint; agent updates hypothesis and drafts plan.
6. Approver authenticates and approves exact plan hash; show disabled unauthorized action, then real simulated work-order state changes.
7. Simulated crews record work evidence; Civicly enters MONITORING and cannot say resolved prematurely.
8. Advance rainfall/pickup/pavement follow-up; show verified or reopened case. Start new case referencing prior repair; show case memory retrieval.
9. Run S08 counterfactual (nearby but disconnected drain) and S10 clear-drain contradiction to demonstrate the agent does **not** hallucinate causation.
10. Open one source-backed municipal SOP from GraphRAG retrieval; trace `GOVERNED_BY`, department ownership and source passage. Show Browser live graph and selected Cypher read-only query.

## Scope and authenticity labels
Every fake city/inspector/work order/weather fixture must be marked SYNTHETIC or SIMULATED. Use actual MCP call and actual graph traversal, not LLM storyboards. Present graph queries, source provenance and same-case history to judges. Do not claim real repairs.

## Evidence to preserve for final video
- `civicly demo verify` output with seed counts
- live graph query returning shared downstream asset path and evidence
- ToolExecution trace with discovered MCP tool names, args (redacted), outputs, durations
- alternate hypothesis after negative inspection
- versioned approved plan, task DAG and assignments
- simulated work order lifecycle plus explicit monitoring
- after restart, checkpoint + prior case memory retrieval
- GraphRAG source passage + procedure/owner relationship
- successful counterfactual graph perturbation
