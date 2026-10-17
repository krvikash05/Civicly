# Agent workflows, MCP tool selection, memory and authorization

## 1. Event-driven investigation workflow
`ComplaintSubmitted -> NormalizeAndResolve -> LinkIncident -> FindProblemCluster -> OpenOrResumeInvestigation -> GatherGraphContext -> CompareHypotheses -> {GatherMoreData|RequestInspection|DraftPlan} -> HumanApproval -> AuthorizeWork -> TrackWork -> VerifyOutcome -> {Monitor|Reopen|Complete}`.

Transitions must use `../contracts/state_machines.json` and be recorded as events; never advance to completion because a prompt says so.

## 2. Tool selection
Supervisor receives structured `InvestigationState`:
```
{
  investigation_id, active_incident_ids, phase, hypothesis_ids,
  evidence_ids, pending_inspections, active_plan_id, pending_approval_ids,
  recent_tool_call_ids, last_graph_revision, next_check_at, loop_budget_remaining
}
```
Run MCP `tools/list` during client initialization or refresh. Selection must be **conditional**:
- Physical topology uncertainty -> `trace_infrastructure_dependencies`.
- Suspected recurrence -> `find_related_incidents`, `retrieve_case_memory`.
- Questionable prior repair -> `get_maintenance_history`.
- Flooding vs rainfall intensity -> `retrieve_external_evidence` (may return UNAVAILABLE).
- Missing decisive field evidence -> `propose_inspection`; pause and await observation event.
- Justified intervention -> `propose_resolution_plan` (draft), `request_plan_approval` (pending).
- Approved task -> `create_work_order` only after versioned approval and identity checks.
- Intervention finished -> `get_work_order_status`, `record_intervention_outcome`, then monitoring.

A genuine tool-selection test removes/changes one graph edge or inspection finding, reruns from the same intake, and expects a different hypothesis/next action in at least one fixture. Tool calls must be actual MCP requests at runtime; a local Python function named after an MCP tool is insufficient.

## 3. Controlled turns
The supervisor may repeatedly choose read tools until enough evidence exists, but each run has tool-count, token, query time and recursion budgets. If exhausted, yield a `NEEDS_REVIEW` or `AWAITING_EVIDENCE` state; do not spin indefinitely.
Reasoning summaries visible to UI: problem, leading alternatives, supporting/contradicting evidence IDs, relevant paths, missing evidence, selected next action. Do not reveal or store raw chain-of-thought.

## 4. Hypothesis scoring
Never have an LLM invent an uncalibrated numerical probability. Compare hypotheses using declared dimensions: evidence strength, contradiction, timing compatibility, topology validity, previous intervention outcomes and missing corroboration. Produce ordinal assessment `POSSIBLE`, `SUPPORTED`, `CONTRADICTED`, `VERIFIED`, `INCONCLUSIVE` plus `rationale`, supporting evidence IDs, opposing evidence IDs and required next check. A 'VERIFIED' causal explanation requires a defensible explicitly reviewed verification rule; a blocked drain inspection alone verifies obstruction, not necessarily the entire downstream causal chain.

## 5. Human-in-the-loop
- AI can add validated hypotheses/assessments and draft plans without operator approval.
- AI cannot auto-approve. Only a session-authenticated actor with `APPROVER` role can set Approval=APPROVED for `plan_id`, `plan_version`, `plan_hash`, scope, expiry.
- `create_work_order` executes only if approval is still valid, target exists, task dependencies satisfied or waiver is expressly approved, and idempotency key is unused.
- If plan/version/graph-revision materially changes, old approval is invalid, a revised plan must be approved.
- Department-lead simulated execution updates require authenticated department identity and evidence of action/inspection. Reject arbitrary agent completion.

## 6. Monitoring/reopening
- After task completion, classify immediate result (`MITIGATION_VERIFIED`, `ROOT_CAUSE_ADDRESSED`, `INCONCLUSIVE`) separately from long-term resolution (`MONITORING`, `RESOLUTION_VERIFIED`, `RECURRENCE_DETECTED`).
- Waterlogging follow-up preferably after comparable rainfall, road damage after later inspections, waste after several collection cycles. If observational opportunity hasn't occurred, remain MONITORING, not RESOLUTION_VERIFIED.
- On recurrence/negative verification: create event, reopen cluster/investigation, retrieve previous case memory and rejected hypotheses, propose changed next action. Avoid reflexive repeat work order.

## 7. Agent memory
- Execution checkpoint: FalkorDBSaver bound to stable `thread_id=case:<investigation_id>`; verify documented API and retention on restart.
- Long-term structured memory: graph `CaseMemory` linked to Investigation, relevant assets, evidence, findings, intervention outcomes. Link correction to prior findings; never erase original failure.
- Municipal knowledge: `Department`/`KnowledgeProcedure`/`ServiceSchedule` with version and validity; actual organizational rules constrain work-order planning.
- Ingest evidence/approval/work status generates `DomainEvent`; worker resumes the thread. Events deduped by event ID.

## 8. Error semantics
All MCP tools have `{status: SUCCESS|UNAVAILABLE|ERROR, ...}` envelope. `UNAVAILABLE` = external source missing/disabled, `ERROR` = invalid input/dependency failure. Authorization failure uses `PERMISSION_DENIED`/`APPROVAL_REQUIRED` coded error, not success. Never silently fill missing measurements. Tool outputs always include `trace_id`, `source_evidence_ids` or explicit empty with reason, and `simulation_mode` where relevant.
