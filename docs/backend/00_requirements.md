# Civicly — scope, product invariants, measurable requirements

## Product boundary
An **advanced hackathon AI agent** in a deliberately synthetic municipal district, with actual FalkorDB persistence, real MCP client/server calls, autonomous evidence gathering, justified next steps, multi-actor handoffs, approvals, simulated field-work outcomes and persistent memory. Not an enterprise SaaS, public complaint site or real dispatch system. The frontend is built later, but all DTOs and trace events must be provided by the backend.

## Domain definitions
- **Recurring waterlogging:** repeated rainwater accumulation at locations expected to drain adequately. Distinguish anomalous rainfall, insufficient drainage capacity, blockage, pump failure, road grade and downstream bottleneck.
- **Recurring potholes / road damage:** repeated pavement deterioration, cracks, rutting, settlement and failed repairs. Distinguish infiltration, utilities, structure/subgrade, excavation, vehicle load and maintenance quality.
- **Repeated waste accumulation:** repeatedly overflowing collection points, recurrent dumping or piles despite expected service. Distinguish missed pickups, route constraints, peak-day demand, inadequate capacity and dumping.

## Binding requirements (do not delete or silently downgrade)
| ID | Requirement | Concrete passing observation |
|---|---|---|
| R01 | All three civic issue categories | Backend case runner independently solves or requests justified inspection for each category |
| R02 | Complaint intelligence | Input normalized, source retained, same-event complaints de-duplicated |
| R03 | Recurrence detection | Duplicate reports, ongoing incidents and resolved-then-recurring cases distinguished |
| R04 | Graph-native investigation | Real FalkorDB paths influence hypotheses and next tool choice |
| R05 | Cross-category reasoning | Graph connects waste, drainage, waterlogging and road damage with clearly qualified causes |
| R06 | AI-led investigation | LLM supervisor dynamically chooses actions; no hardcoded tool script disguised as autonomy |
| R07 | Runtime MCP selection | Agent lists/calls genuine official graph and domain MCP tools with trace and failure handling |
| R08 | Evidence-grounded hypotheses | Alternatives, contradiction, inspection, revision, cannot invent verified causes |
| R09 | Provenance | Every finding/cited procedure has source ID, time, verification status |
| R10 | Targeted planning | Typed task DAG, ownership, evidence, dependencies, success criteria |
| R11 | Municipal coordination | Authorized simulated inspections/work orders, valid state machine, department actor |
| R12 | Proactive monitoring | Durable event wakeup, overdue/failed task and recurrence reopen logic |
| R13 | Persistent multi-layer memory | Workflow restart + episodic, semantic, procedural memory and corrections |
| R14 | Organizational knowledge | GraphRAG ingest and retrieve sourced procedures, owners, tickets and decisions |
| R15 | Explainability | Trace of tool inputs, graph path, hypothesis changes, causal reservations and next action |
| R16 | Functional backend/frontend-ready app | API + SSE + CLI, authenticated operator flows and later UI-ready DTOs |
| R17 | Outcome verification | Work completed != root cause solved; condition-specific monitoring verifies outcome |
| R18 | End-to-end demonstration | Standalone 3 issue scenarios + cross-category scenario + negative variants; real backend |

## Track-specific demonstration
- Track 1: FalkorDB Cypher traversal, shared-dependency and criticality algorithms, MCP selection, plan action changes under graph perturbation.
- Track 2: checkpoint, role handoffs, persistent episodic/semantic/procedural memory, retry/limited concurrent action tests, logically scoped demo-city records.
- Track 3: company-brain analogue = **municipal operations brain**; departments, tickets, procedures, ownership, sourced cross-document knowledge and decisions.

## Acceptance definition
- Demonstration/agent traces are from the live integrated system; generated fixtures are clearly labeled. Eval ground truth kept separate and never available through agent tools.
- ``Backend complete`` = all acceptance tests in `docs/backend/10_evaluation.md` and all B-END gates in `docs/backend/11_microtasks.md` executed and green; no frontend required for that gate.
- Developer must be able to explain source of every non-obvious relationship and why graph dependence changed a choice.
