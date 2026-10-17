# Test and objective traceability

## Architectural package validation
Run `python scripts/validate_blueprint.py`. It checks JSON structure, tool JSON Schemas, reference integrity, edge endpoint types, enum references, state transitions, synthetic seed-record properties and relationships, core contract coverage and scenario enumeration. It **does not** claim FalkorDB queries or the application have been runtime-tested.

## R01–R18 required acceptance mapping
| Objective | Test implementation | Expected evidence |
|---|---|---|
| R01 | `test_issue_specific_scenarios` | All 3 category cases complete supported flow |
| R02 | `test_complaint_ingest_dedup` | Same event multiple complaints -> one Incident |
| R03 | `test_recurring_vs_persistent` | Distinct chronology/repair history -> correct cluster |
| R04 | `test_graph_dependency_effect` | Removing verified edge changes path/next action |
| R05 | `test_cross_category` | Cross-category graph evidence connects cases |
| R06 | `test_agent_conditional_tools` | Model selects different next tool with modified observations |
| R07 | `test_mcp_runtime` | Actual MCP tools/list/call visible in trace |
| R08 | `test_hypothesis_revision` | Contradictory result creates new assessment; earlier preserved |
| R09 | `test_evidence_provenance` | Every relied-on observation traces source/time |
| R10 | `test_plan_dag` | Cycle rejected; tasks have target, department, postcondition |
| R11 | `test_work_order_approval` | Approval binds exact plan version/hash; no unauthorized order |
| R12 | `test_event_monitor` | New outcome/event resumes case; overdue task flagged |
| R13 | `test_memory_restart` | Checkpoint survives process restart; prior failed repair retrieved |
| R14 | `test_org_procedure` | Ownership and procedure changes alter plan validation |
| R15 | `test_trace_graph_ui` | UI shows real tool calls + evidence subgraph |
| R16 | `test_fullstack_browser` | Browser UI drives persisted actual API state |
| R17 | `test_outcome_separation` | Work done ≠ verified long-term resolution |
| R18 | `test_all_four_scenarios` | Fixture scripts run from fresh seed end-to-end |

## Required negative/security tests
- `test_no_unrestricted_cypher_write_from_agent`: malicious prompt cannot mutate FalkorDB.
- `test_no_prompt_injection_from_document`: untrusted document cannot change tool/approval policy.
- `test_invalid_edge_endpoint`: reject incompatible topology edge.
- `test_cycle_in_task_dependencies`: reject task DAG cycle.
- `test_duplicate_event_delivery`: work order created exactly once under retries.
- `test_old_approval_rejected`: plan change invalidates old approval.
- `test_external_source_unavailable`: no guessed rainfall/measurements.
- `test_inspection_missing`: no supported 'verified root cause' claim.
- `test_graph_history_validity`: historical incident doesn't use newly created pipe connection.
- `test_data_isolation`: synthetic ground truth absent from agent-visible nodes.
- `test_dept_assignment_access`: unauthorized department cannot report another team's completion.
- `test_work_completion_not_case_resolution`: case remains MONITORING until criteria satisfied.

## Seed fixtures
Load exact cases in `../contracts/demo_scenarios.json`: one each for waterlogging, road damage, waste accumulation and a linked waste→drain→road scenario. Ground-truth labels belong in hidden evaluator file only. Every fixture has a negative variation.

## Demo acceptance checklist
1. Reset synthetic seed; record resulting graph node/relationship counts.
2. File a waterlogging complaint. Observe accepted Complaint linked to Incident & ProblemCluster.
3. Start agent. View real MCP tool names and graph query evidence IDs. Show at least two hypotheses.
4. Submit contradictory inspection result. Observe new assessment, preserved prior assessment, and changed next step.
5. Submit an inspection that supports a target repair; approve exact plan version as fixture APPROVER.
6. Create persistently stored SIMULATED work orders assigned to different departments; complete prerequisite tasks; block out-of-order work.
7. Record simulated completion, but keep case MONITORING until follow-up.
8. Submit recurrence; observe case reopen with historical memory and changed proposal.
9. Repeat for road damage, waste accumulation and interconnected case.
10. Fail the graph service or weather source and verify honest errors/fallbacks. Do not use pre-rendered fake traces.

## Measurement
Track: scenario pass rate (4/4 required), tool-call schema success, provenance coverage, graph sensitivity tests (positive and negative), unauthorized write rejection, re-ingestion idempotence, restart recovery, and UI E2E pass rate. Never report unmeasured numerical root-cause confidence as fact.
