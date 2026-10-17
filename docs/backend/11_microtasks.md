# Codex microtask runbook — backend-first, human-reviewed, executable gates

**Contract:** one task per Codex chat turn. No automatic continuation. For each task Codex must list touched files, actual test commands/output, the requirement IDs covered, a 2-minute human verification instruction, screenshots/trace where relevant and STOP. Mark `PASS` only on real verification. Store updates in `task_board.md`, `decision.md`, `flow.md`, `implementation_status.md`, `test_log.md`, `blockers.md`.

## B00–B05 — foundation and graph
| Task | Deliverable and exact work | Acceptance gate |
|---|---|---|
| **B00** | Audit blueprint, validation, local Python/Docker/Node/LLM options; identify inconsistent schema/approval cases. No application code. | validator runs; B00 logs and environment list recorded |
| **B01** | Backend project skeleton, Python dependency/version spike, Docker FalkorDB+Browser persistent volumes and Compose health; CLI health. | actual graph `CREATE/MATCH`, server restart retains node; version/digest noted |
| **B02** | Formal graph migrations, unique/mandatory constraints, indexes, node multi-label adapter, schema registry mapping, rollback/upgrade policy. | migrations idempotent, constraints OPERATIONAL where supported, invalid ID rejected |
| **B03** | Relationship validators and typed graph repositories, graph query templates, verified vs candidate flags, temporal validity and bounded query. | real graph traversal and invalid edge rejected; no unbounded write Cypher |
| **B03-R** | External corrective review: primary zone/cluster and schedule cardinality; explicit total-path budgets; shared disposable graph-target guards; B04 performance plan only. | real overlap/boundary/target tests + all regressions/SPEC validators; STOP for review before B04 |
| **B04** | Seed ingest from canonical fixture + generator/importer, stable provenance, duplicate-safe upserts; synthetically expanded city. | seed twice yields same node/edge identities; count/invariant reports |
| **B05** | Graph algorithms / case retrieval: downstream reachability, shared bottleneck, criticality, DAG; isolated counterfactual graph clone. | removing verified `DRAINS_TO` changes returned path and ranking; provenance displayed |

## B06–B11 — MCP, issue engine, agent/memory
| Task | Deliverable and exact work | Acceptance gate |
|---|---|---|
| **B06** | Official FalkorDB MCP server as runtime dependency, Python MCP client `tools/list`/`tools/call`, read-only denylist tests and auth. | real MCP query returns seed edges, forbidden write refused |
| **B07** | Custom Civicly MCP Python server with read tools and typed schemas, service-call broker/traces. | real transport tests tool discovery, valid/invalid args, provenance, timeout |
| **B08** | Complaint normalization, dedup, distinct Incident/ProblemCluster models, recurrence grouping; 3 issue validators and pickup/road/water evidence. | duplicate and separate recurring events correctly classified; all categories tested |
| **B09** | Evidence, hypotheses, immutable assessments, root-cause verification guards; inspection request/report lifecycle. | contradictory inspection revises hypothesis and preserves original assessment |
| **B10** | LangGraph Supervisor/Investigate/Analyze/Plan/Coordinate states, tool selection prompts + structured outputs + FalkorDBSaver checkpoint, bounded loops. | real MCP-connected LangGraph run; pause/restart/resume same case; live LLM separately recorded |
| **B11** | GraphRAG SDK isolated `civicly_docs`, versioned municipal MD/PDF fixture ingest, cited procedure retrieval, memory episodic/semantic/procedural. | sourced procedure retrieved; stale doc and prompt injection rejected, restart/memory retrieval tests |

## B12–B17 — action lifecycle, durable events, API
| Task | Deliverable and exact work | Acceptance gate |
|---|---|---|
| **B12** | Draft plan Pydantic contracts, responsible department/procedure resolver, dependency DAG and monitoring criteria. | invalid DAG/unknown owner rejected; alternatives/citations shown |
| **B13** | Authentication/roles, exact-plan approvals, plan revisions/hashes, idempotent work-order creation and state transitions. | stale/unauthorized approvals refused, one work order on retries |
| **B14** | Simulated inspector/department actor workflows, inspection evidence, work-order progress, outcome monitor and reopen logic. | completion doesn't imply resolution; recurrence reopens with memory |
| **B15** | Durable event outbox + single worker, resume triggers, case lease, retry/reconciliation, SSE event persistence. | stop after write, restart recovers one event; duplicates no double orders |
| **B16** | FastAPI typed route groups auth/intake/incidents/investigations/evidence/plans/work/orders/org/monitor. | OpenAPI generated, all endpoints meet contract and RBAC tests |
| **B17** | Frontend-ready dashboard/map/graph subgraph/trace DTO, paginated API filters, SSE Last-Event-ID, auth redaction. | graph DTO corresponds to real query, SSE reconnect/refetch works |

## B18–B-END — demo harness and proof
| Task | Deliverable and exact work | Acceptance gate |
|---|---|---|
| **B18** | CLI `civicly` entrypoint: investigate, inspect, approve, advance, reset, test, graph explain; same services as API. | water scenario can be driven without web UI |
| **B19** | Thoughtful scenario generator: all 12 catalog scenarios, delayed evidence release, hidden truth isolated, source docs and fixture validation. | scenario reset deterministic, agent cannot read hidden truth |
| **B20** | Unit/integration tests for scenarios S01–S06, issue-specific negative/contradiction variants. | expected decisions and evidence paths, no invented fact |
| **B21** | Cross-category S07/S08 and graph ablation, genuine MCP-selected tool-path change. | connection edits change evidence and defensible next action |
| **B22** | S09–S12: outcome memory, failed repair, external failure, restart/dup event/unauthorized action. | stale approval fails; recurrence/learning and error recovery correct |
| **B23** | Real LLM and MCP live evaluation matrix, measured token/time, trace snapshots + safety checks. | honest live vs fake model test evidence, gaps filed not concealed |
| **B24** | Reproducible Docker local setup, README, Mermaid architecture, demo script, evidence graphic data, code explainability and source disclosure. | fresh machine steps and reset work with no manual DB edits |
| **B25 / B-END** | Consolidate all R01–R18 evidence, run all integrated tests and source citations, verify frontend-ready API contracts. | comprehensive test matrix green; unfinished requirements explicitly noted; **human approval required before frontend** |

## Human verification protocol
For every task after B01, Codex should supply: `Command to run`, `What you should see`, `What can go wrong`, `Which file to share back here if something fails`. Human should inspect FalkorDB Browser for graph stages, API `/docs` for calls and CLI for the latest task (depending on task). No need to become a backend expert: the checkpoints demand visible proof.

## Required per-turn Codex reply format
```
Task: Bxx — summary
Files changed (exact): ...
Implementation behavior (not promises): ...
Commands executed & results: ... (unit vs integration vs live agent)
Human verification: 1. ... 2. ...
Logs updated: decision.md, flow.md, task_board.md, implementation_status.md, test_log.md, blockers.md
Known issues: ...
Proposed next: Byy — ...
STOP — await user approval.
```
