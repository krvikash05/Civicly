# AI orchestration, tool-selection intelligence and reasoning contract

## Roles (logical first; discrete LLM agents only where beneficial)
- **Supervisor**: orchestrates investigation, chooses next *allowed* action and specialist, enforces budget and pause reasons; outputs typed `Decision`.
- **Investigator**: selects/read-only graph, maintenance, weather, source and memory MCP tools; records trace, graph paths and gaps.
- **RootCauseAnalyst**: at least two causal hypotheses where plausible, compare support/contradictions, chronological/asset dependency checks, recommends discriminating evidence; never self-verifies causal facts.
- **ResolutionPlanner**: action alternatives, priority and task DAG including responsible department, verified facts, required inspections, dependency validation, cost/time as *optional estimates only if sourced*, expected outcome and monitoring plan.
- **Coordinator**: submits proposals, requests approval, tracks authorized work, reacts to failed/blocked events, reopens if new evidence.

A single LangGraph `StateGraph` with named typed nodes and conditional routing is preferable to five unconstrained conversational loops. Shared state is checkpointed by investigation ID. Specialist outputs are validated Pydantic objects and canonical graph entities; avoid fragile natural language handoffs.

## Typed minimum state
```
InvestigationState = {
  investigation_id, thread_id, current_phase, incident_ids, problem_cluster_id,
  issue_types, graph_revision, tool_inventory_hash, discovered_tool_names,
  hypotheses:[id], evidence_ids:[id], missing_evidence:[text],
  candidate_next_steps:[NextAction], chosen_next_step,
  current_plan_id, pending_approval_id, outstanding_inspection_ids,
  token_budget_remaining, tool_call_budget_remaining, iteration_count,
  last_agent_decision_id, pause_reason, error_code, timestamp
}
```
Store only stable references to large graph/document content in checkpoint, not huge blobs. On resume check graph revision and re-fetch stale evidence. Agent loops are bounded (e.g., <=12 read calls and <=4 reasoning cycles per wake; values configurable), respond `NEEDS_HUMAN_REVIEW` rather than infinite retry.

## Tool selection actually agentic
1. MCP client `tools/list` at session startup; only safe allowlisted tools presented to the model, names + descriptions + JSON input schemas.
2. Model chooses next action/tool based on active hypotheses, missing evidence, provenance, graph path strength, temporal plausibility, cost/impact and next-action usefulness; include concise **decision summary** (not private chain-of-thought).
3. Runtime validates tool name/arguments/permission and enforces budgets; invokes real MCP `tools/call`; normalizes result to `{status, source_refs, graph_revision, structured_data, error}`; adds `ToolExecution` graph trace.
4. Supervisor decides whether observation discriminates hypotheses or additional lookup needed. Tool selection changes under topology/inspection counterfactual.
5. If crucial evidence absent, request inspection rather than guess; if adequate, draft plan and suspend for approval.

## Hypothesis model and assessment rubric
Every hypothesis has `cause_code`, affected incident(s), candidate asset(s), proposed mechanism, expected confirming and falsifying observations, provenance, temporal consistency, alternative explanations, latest assessment and missing evidence. Assessment labels: `POSSIBLE`, `SUPPORTED`, `CONTRADICTED`, `VERIFIED`, `INCONCLUSIVE`. **Verified cause requires domain-defined inspection/finding and sufficient corroboration**, not just model judgment. Evidence reliability and method recorded; do not present fabricated numerical confidence.

Examples of discriminating tests:
- Water: blockage hypothesis vs capacity deficit -> downstream inspection + rain-intensity context; if drain clear, downgrade obstruction and consider grade/capacity.
- Road: pipe leak vs weak subgrade -> utility pressure inspection vs pavement/subgrade tests; location under road alone is not leak proof.
- Waste: missed collection vs peak demand -> compare scheduled and actual pickup executions and volume; a cleanup alone is mitigation.

## Planner contract
Return `PlanDraft` with `investigation_id`, `basis_evidence_ids`, `hypotheses_addressed`, `alternatives_rejected_with_reason`, `tasks:[{task_id, action_code, asset_ids, department_id, prerequisites, requires_approval, simulated, verification_protocol}]`, `monitoring_conditions`, `risk_notes`, `version`, `content_hash`. Deterministic DAG validator, procedure validation and exact-owner resolver run *after* LLM draft; if invalid route to clarification/replan rather than silently fix meaning.

## Controlled terminal/paused conditions
`AWAITING_EVIDENCE`, `AWAITING_APPROVAL`, `MONITORING`, `COMPLETED`, `NEEDS_HUMAN_REVIEW`, `BLOCKED_EXTERNAL`, `BUDGET_EXHAUSTED`, `ERROR_RETRYABLE`. Only validation services mutate domain state; LangGraph emits intended next actions.

## Handling error and contradiction
- Tool timeout -> bounded retry with jitter and idempotency; persistent failure -> pause and explicit source unavailable.
- Contradicting evidence -> new immutable `HypothesisAssessment` linked to both new and old evidence, preserve prior decision; may reroute to investigation.
- Invalid LLM JSON -> single schema-repair attempt, deterministic rejection if invalid again.
- Stale approval/graph revision -> refuse work order, create reapproval request.
- Prompt injection embedded in retrieved doc -> treat as content/evidence, no tool policies changed, record security observation.

## Cost/reproducibility
Configurable provider and model ID via env, temperature/seed where supported, token + call budgets; minimal structured prompts versioned as files with SHA; test fake model for deterministic branches and separately run live LLM scenario suite with recorded actual tool traces. Fake model test MUST NOT count as proof of live agent intelligence.
