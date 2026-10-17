# Product specification — Civicly

## Mission
A municipal team uses Civicly to **understand, investigate, plan, coordinate, monitor, and learn from recurring civic failures**, with FalkorDB graph relationships determining relevant evidence and candidate interventions. The AI leads the *information/decision workflow*; humans authorize material municipal work.

## Target issues
- `WATERLOGGING`: repeated unwanted standing rainwater in streets, junctions, underpasses or public low-lying areas where drainage is expected.
- `ROAD_DAMAGE`: recurring potholes, cracking, rutting, settlement, pavement breakup and similar repeated deterioration, including after repair.
- `WASTE_ACCUMULATION`: repeatedly overflowing collection points or recurring public garbage piles despite existing/expected service.

Each issue can be associated with other issues through **supported hypotheses**; no automatic causal link from geographic proximity.

## Primary users
1. Municipal operations analyst: investigate case, inspect evidence graph, approve/reject plans if authorized, track status.
2. Department lead: accept assigned work, report inspection and operational results.
3. Civic operations reviewer: review evidence, approve cross-department plans and waivers.
4. Resident/citizen: optional limited complaint intake; no ability to approve tasks or access sensitive operational information.

## Requirements — all must be implemented and tested
| ID | Objective | Acceptance criterion |
|---|---|---|
| R01 | Three categories | Each has an executable agent case and matching observations |
| R02 | Complaint intelligence | Normalizes, groups and attributes source reports |
| R03 | Recurrence | Separates duplicate reports, persistent incidents and distinct recurrent events |
| R04 | FalkorDB core | Multi-hop graph evidence changes decisions; no in-memory canned graph substitute |
| R05 | Cross-category | Related waste/drain/road incidents can be investigated together |
| R06 | Agent-led | Tool sequence can vary based on evidence and response |
| R07 | MCP runtime | Discover/call actual MCP tools with traces |
| R08 | Hypotheses | Alternatives, support, contradiction, uncertainty and revisions |
| R09 | Provenance | Claims cite source evidence ID and timestamp |
| R10 | Plans | Typed tasks, target assets, dependencies, expected verification |
| R11 | Coordination | Department, approval, work-order assignment and durable tracking |
| R12 | Monitoring | Agent wakes on evidence/events/overdue tasks, detects recurrence |
| R13 | Memory | Checkpoint restart + graph-based prior case retrieval |
| R14 | Company brain | Versioned responsibilities and procedures constrain decisions |
| R15 | Explainability | Evidence subgraph + run/tool/decision trace without hidden chain-of-thought |
| R16 | Functional app | Real API, frontend, graph DB and MCP integration |
| R17 | Verification | Completion of work and resolution of root issue are distinct |
| R18 | E2E scenarios | Waterlogging, road damage, waste, and cross-category scenarios pass |

## Definition of done
An operator creates/opens an incident; Civicly independently selects graph and history tools through MCP; the UI shows sourced alternative hypotheses; a user can provide a simulated inspection with provenance; the agent revises its belief, proposes an authorized plan, tracks executed simulated work, monitors for recurrence, and reuses its memory in a later case. All three issue types and the connected scenario work through *the same* implementation, not four scripted videos.

## Product exclusions
- Do not impersonate a municipal authority or silently place real operational orders.
- Do not claim reliable physical root-cause proof from graph topology alone.
- Do not imply synthetic data is official city infrastructure or real weather.
- No requirement for actual municipal API partnership or street-level automatic repair.
