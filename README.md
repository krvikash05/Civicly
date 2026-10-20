# Civicly

### Understand the cause. Coordinate the response. Verify the outcome.

**Civicly is a FalkorDB-powered AI agent platform that investigates recurring civic problems like waterlogging, road damage and waste accumulation, and helps coordinate evidence-based action.** Its agent connects complaints to infrastructure, evidence and previous work, selects investigative tools and compares possible causes. The platform carries the findings through a reviewed plan, human approval, simulated work and follow-up verification.

Consider a road that keeps developing potholes. Should the road be repaired again—or is a leaking pipe damaging the ground beneath it? Civicly helps an investigator follow the connections, compare explanations and see what evidence is needed before acting.

**FalkorDB connects the investigation to the response.** Its domain graph links reports, infrastructure, inspection evidence, departments, tasks and outcomes. Civicly's AI investigates those records through runtime MCP; the FalkorDB GraphRAG SDK retrieves sourced procedures; FalkorDBSaver preserves the investigation thread. People review evidence and approve work, while the workspace makes the supporting graph paths inspectable.

Across the whole case journey, Civicly uses FalkorDB to connect a new report to relevant assets and past incidents, retrieve evidence and procedures for the agent, and track planned work across departments. After authorized work, dated follow-up and retained outcomes complete the episode’s history—so future investigations can retrieve what was tried and what happened.

[**Civicly Live ↗**](https://civicly-13-55-205-208.sslip.io) · [**Follow the completed road case**](https://civicly-13-55-205-208.sslip.io/investigations?investigation=INV-B09-b9d4d66e130ed348c4f6a50e9d66a891&section=report#case-workspace) · [Two-minute walkthrough](#one-investigation-six-connected-stages)

![Civicly: better coordination for more livable cities. A 40-second illustrated overview of how FalkorDB connects reports, evidence, departments, approved work, outcomes and memory.](docs/media/civicly-preview/civicly-explainer.gif)

[**Explore step by step ↗**](https://krvikash05.github.io/Civicly/) — pause, go back or advance through each scene.

*How FalkorDB powers Civicly—from connected evidence to coordinated action and verified outcomes. Illustrated workflow; municipal data and field work are simulated. [View all eight scenes](docs/media/civicly-preview/storyboard.png).*

> **About the demo:** municipal data, inspections and field work are synthetic. Civicly's AI, MCP, FalkorDB, GraphRAG retrieval and saved workflow records use actual services. The hosted site lets you explore retained results; browsing does not start a paid agent run. Hosting uses a temporary hostname.

## What can Civicly investigate?

The current demo explores three civic problem categories. The same investigation approach could be extended to issues such as broken streetlights, sewer overflows and damaged footpaths, with the relevant data, evidence and workflows added.

| Example civic problem | Questions Civicly’s AI may explore | Evidence Civicly’s AI seeks through MCP tools | How FalkorDB helps the investigation |
|---|---|---|---|
| **Waterlogging** | Is a drain blocked? Do several affected locations share a downstream restriction? Could capacity or a pump be involved? | Drainage connections, maintenance history, inspection findings and rainfall context | Connects affected locations through the drainage network, helping the AI find shared downstream assets and check their inspection and maintenance records. |
| **Road damage** | Is the subgrade failing? Is a verified underlying utility connection relevant? Which department must act first? | Road and pipe relationships, structural observations, leak tests and repair history | Links the road to sourced underlying-pipe relationships, repair history and inspection evidence, helping the AI assess possible causes. Department and task connections establish which work must happen first. |
| **Waste accumulation** | Was collection missed? Was capacity insufficient? Was waste deposited after collection? | Collection routes, scheduled versus actual pickups and dated field observations | Connects collection points, routes, scheduled pickups and actual service records, helping the AI compare missed collection with other explanations using dated observations. |

These are competing explanations to investigate, not causes inferred automatically from a complaint. The [demo status](#what-is-demonstrated) below distinguishes the current results for each category.

## One investigation, six connected stages

**Report → Investigation → Evidence → Plan & approval → Work → Monitoring & memory**

This is also the frontend navigation. A municipal analyst can start with the reported problem, follow the agent's tool choices, inspect evidence, review the proposed response and see whether later observations justify closing the episode.

**Two-minute judge walkthrough:** open the [completed Market Junction road case](https://civicly-13-55-205-208.sslip.io/investigations?investigation=INV-B09-b9d4d66e130ed348c4f6a50e9d66a891&section=report#case-workspace), then use the six stage buttons:

| Stage | What to look for |
|---|---|
| **Report** | Recurring road damage, low water pressure and the original location |
| **Investigation** | The agent's recorded questions, MCP results and next choices; inspect **How FalkorDB informed this step** |
| **Evidence** | Competing explanations, reviewed observations and what remains unproven |
| **Plan & approval** | The recommended response, responsible departments and utility-before-road prerequisites |
| **Work** | Three authorized simulated work orders and their recorded progress |
| **Monitoring & memory** | Separate follow-up verification and retained episode history |

Use **Focus on this path** to isolate an available recorded lookup and open its linked source. The response timeline connects recommendation, authorization, work and follow-up without treating them as the same event.


Three distinctions keep that story clear:

- **A report is not an incident:** several complaints may describe the same occurrence. Separate recurring occurrences can share a problem cluster.
- **A hypothesis is not a finding:** possible explanations are assessed against evidence, and previous assessments remain available.
- **Completed work is not verified resolution:** follow-up must establish what happened after the intervention.

## Graph data model

![Full Civicly schema overview in FalkorDB Browser](docs/images/civicly-browser-schema-overview.png)

*The full schema discovered from Civicly's retained demo graph in FalkorDB Browser: 48 node labels and 190 label-to-label connection patterns, including internal workflow records. The focused views below explain the core model and individual case relationships.*

Think of the graph as a connected case file: **what was reported, what infrastructure is involved, what the evidence says, and what happened next.** Nodes represent those records; named relationships explain how they connect.

For example, `Complaint → REPORTS → Incident` means a complaint describes an occurrence. `WorkOrder → IMPLEMENTS → ActionTask` means an authorized order carries out a planned task. The diagram uses actual names from the [canonical schema](contracts/schema_registry.json).

```mermaid
flowchart TB
    subgraph REPORTS["1 • Reports and affected infrastructure"]
        C[Complaint] -->|REPORTS| I[Incident]
        I -->|PART_OF| PC[ProblemCluster]
        I -->|AFFECTS| A[InfrastructureAsset]
        I -->|OCCURRED_AT| L[Location]
        A -->|MAINTAINED_BY| D[Department]
    end
    subgraph REASONING["2 • Investigation and evidence"]
        INV[Investigation] -->|INVESTIGATES| I
        INV -->|PROPOSES| H[Hypothesis]
        H -->|CONCERNS| A
        H -->|HAS_ASSESSMENT| HA[HypothesisAssessment]
        HA -->|SUPPORTED_BY| E[Evidence]
        HA -->|CONTRADICTED_BY| E
        INS[Inspection] -->|PRODUCED| E
        E -->|ESTABLISHES| F[Finding]
    end
    subgraph RESPONSE["3 • Plan, authorized work and outcome"]
        INV -->|PRODUCED_PLAN| P[ResolutionPlan]
        P -->|HAS_TASK| T[ActionTask]
        T -->|TARGETS| A
        T -->|ASSIGNED_TO| D
        T -->|DEPENDS_ON| T2[ActionTask]
        W[WorkOrder] -->|IMPLEMENTS| T
        W -->|AUTHORIZED_BY| AP[Approval]
        W -->|RESULTED_IN| O[InterventionOutcome]
    end
```

### The most important connections

| Relationship | Read it as | Why it matters |
|---|---|---|
| `DRAINS_TO` | This drainage asset flows toward that asset | Follow connected drainage and find shared downstream locations |
| `UNDERLIES` | This pipe lies beneath that road | Investigate a possible utility contribution and validate repair dependencies |
| `COLLECTED_BY` | This waste point is served by that route | Connect accumulation reports to collection records |
| `MAINTAINED_BY` | This department is responsible for the asset | Resolve reviewed responsibility before planning work |
| `SUPPORTED_BY` / `CONTRADICTED_BY` | This evidence supports or challenges an assessment | Explain conclusions and retain conflicting findings |
| `DEPENDS_ON` | This task requires another task first | Prevent work from proceeding before its prerequisites |

Location and physical connection are different: **a pipe being nearby does not prove it lies beneath the road or caused the damage.** Relationships distinguish candidate and verified associations and carry source references and time bounds where available.

**Why these connections matter:** in the road case, the sourced pipe-to-road relationship and the task prerequisites connect a utility investigation to coordinated repair. Application services read these relationships from FalkorDB to validate whether the planned road work can proceed. The graph supplies the connected evidence and dependencies; the services enforce the approval and execution rules.

Beyond this overview, the model includes collection schedules and actual pickup records, rainfall events, procedures, tool executions and status events. Assessments are versioned; evidence retains its source, date and review status. See [the full graph model](docs/backend/02_graph.md) and [evidence rules](backend/EVIDENCE.md).

### The model in a running database

**Schema view — how the case file is connected.** This view is discovered from Civicly's actual FalkorDB graph. Each square represents a node label, such as Incident or WorkOrder; arrows show the relationship patterns present between labels.

![Filtered FalkorDB Browser Schema view showing Civicly's investigation and response model](docs/images/civicly-browser-schema-focused.png)

*Follow the structure from complaints and incidents through investigation, evidence, plans, approvals, work orders and intervention outcomes. Display filters retain 14 core labels and hide infrastructure subtypes and internal bookkeeping labels. The Browser footer reports the full schema's 48 labels and 190 connection patterns, not the filtered subset. This is a schema view, not a count of incidents or proof of causation.*

[View the full schema image](docs/images/civicly-browser-schema-overview.png)

**Road-case graph — how those connections support a response.** Unlike the schema above, the following graph shows individual persisted records for the retained road investigation.

![FalkorDB Browser showing the road case assets, plan, tasks, departments and work orders](docs/images/falkordb-road-task-graph.jpg)

*An actual read-only query of the retained road case in FalkorDB Browser: **11 nodes and 15 relationships** connect the pipe and road (`UNDERLIES`), plan and tasks (`HAS_TASK`), task prerequisites (`DEPENDS_ON`), responsible departments (`ASSIGNED_TO`), target assets (`TARGETS`) and work orders (`IMPLEMENTS`). Browser node captions may show internal database IDs; Civicly keeps canonical IDs in technical details. These are persisted synthetic demo records, not a drawn mockup. Notice how the pipe-to-road connection and the task dependencies connect utility work to road repair; approval and safety checks are enforced separately by application services.*

[Read-only query and capture notes](docs/images/README.md) · [Reproduce the focused query](docs/images/road-task-graph.cypher)

## How FalkorDB helps at every stage

```mermaid
flowchart LR
    R[Report] --> Q[Investigate connected assets]
    Q --> H[Compare hypotheses]
    H --> X{Enough evidence?}
    X -->|No| IN[Request inspection]
    IN --> E[Reviewed dated findings]
    E --> H
    X -->|Evidence supports planning| P[Draft tasks with sources and prerequisites]
    P --> A[Human approves exact plan]
    A --> W[Authorized simulated work]
    W --> M[Independent follow-up]
    M --> V{Outcome assessment}
    V -->|Insufficient opportunity| M
    V -->|Verified outcome| C[Close episode and retain memory]
    V -->|Problem persists| Q
```

Each stage answers a practical question. The frontend uses readable labels and keeps canonical record IDs available in technical details:

| Stage | What the judge sees | How FalkorDB contributes |
|---|---|---|
| **Report** | What happened, where, and has it happened before? | Connects reports to occurrences, locations and persistent clusters |
| **Investigation** | What did the agent check, and why? | Retrieves actual infrastructure paths, maintenance history and related incidents |
| **Evidence** | Which explanation does the evidence support—and what is missing? | Links hypotheses to immutable assessment history and attributed evidence |
| **Plan & approval** | What should happen, in what order, and who approves it? | Resolves reviewed responsibility and validates task dependencies and their source references |
| **Work** | Who is assigned, what has happened, and what is blocked? | Connects approved tasks to authorized operations and durable status history |
| **Monitoring & memory** | Did the intervention help, and what should a later investigation remember? | Retains the episode's work/evidence/outcomes and retrieves historical context |

In the graph panel, judges can inspect entities and follow recorded decision paths alongside the case. The reasoning view connects **the question asked → returned graph evidence → recorded action**. It distinguishes a recorded decision path from a contextual read; visible adjacency alone does not prove the graph influenced a model decision.

Live updates use server-sent events (SSE) from persisted activity. They trigger a fresh read of the actual case, rather than animated or fabricated progress.

## Architecture

```mermaid
flowchart TB
    UI["Workspace • Next.js and FalkorDB Canvas"] -->|REST and live events| API["FastAPI • authentication and validated services"]
    API -->|Persist and read| KG["FalkorDB • connected case and infrastructure records"]
    API --> EVENTS["Durable events • authorized worker"]
    EVENTS --> AGENT["LangGraph • investigation roles"]
    AGENT <-->|Choose next action| CIVICLY_AI["Civicly's AI"]
    AGENT -->|Discover and call tools| MCP["MCP • official graph tools and Civicly tools"]
    MCP -->|Read connected evidence| KG
    AGENT -->|Validated analytical writes| API
    MCP --> DOCS["GraphRAG • sourced organizational documents in FalkorDB"]
    AGENT <-->|Save and resume| CHECKPOINTS["FalkorDBSaver • separate checkpoint graph"]
```

**Reading the diagram:** the workspace calls the backend; an explicitly authorized worker runs the investigation; Civicly's AI chooses an action; MCP retrieves graph evidence; validated services record the resulting findings or plans. The UI then reads those persisted records.

| Component | Its job |
|---|---|
| **Civicly's AI + LangGraph** | Select investigative actions and coordinate Supervisor, Investigator, RootCauseAnalyst, ResolutionPlanner and Coordinator roles |
| **Runtime MCP** | Discover available tools and execute validated reads through `tools/list` and `tools/call` |
| **FalkorDB domain graph** | Store infrastructure, incidents, evidence, assessments, plans, work and outcomes as connected records |
| **GraphRAG document memory** | Retrieve cited, versioned municipal guidance from a separate SDK-managed FalkorDB graph |
| **FalkorDBSaver** | Preserve the investigation thread so it can pause and resume |
| **FastAPI services and worker** | Enforce evidence rules, permissions, approval scope, task transitions and durable event handling |
| **Next.js + FalkorDB Canvas** | Present the six-stage case, inspectable graph, evidence and recorded decision paths |

**Three FalkorDB-backed stores serve different purposes:** the domain graph holds connected case and operational records; the SDK-managed document graph supports cited knowledge retrieval; the separate FalkorDBSaver graph preserves workflow checkpoints. Civicly's AI chooses investigative actions, and authenticated application services validate writes and operational transitions.

These are modules in a backend application with a single worker, not a fleet of independently deployed agent services. Private authentication and spending ledgers use SQLite. The browser never receives database credentials or unrestricted query access.

Agent graph reads are bounded and read-only. Analytical changes pass through validated services; work requires authenticated roles and approval of the exact plan. [Detailed architecture](docs/backend/01_system.md).

## Follow one case: the road that kept failing

**The report:** recurring potholes and subsidence at a junction, alongside low-pressure complaints.

**The investigation:** Civicly's AI reads road and utility history through MCP and compares two explanations: utility leakage and subgrade failure. Reviewed inspections provide evidence for both. Their assessments become **SUPPORTED**; this does not erase the remaining evidence gaps.

**The response:** coordinate utility work and road work so the road repair follows the required utility checks.

The graph contains a verified `PIPE-100 → UNDERLIES → ROAD-100` connection. The planning and execution services use it to enforce this order:

```mermaid
flowchart LR
    PIPE["PIPE-100 • verified UNDERLIES link"] --> ROAD[ROAD-100]
    ISO["Water Utilities • isolate pipe"] --> IP[Reviewed isolation proof]
    IP --> REPAIR[Repair leak]
    REPAIR --> UV["Independent follow-up • UTILITY_VERIFIED"]
    UV --> SUB["Roads • repair subgrade"]
    SUB --> MON["MONITORING • separate wear and pavement observations"]
    MON --> OUT["RESOLUTION_VERIFIED • close episode • retain memory"]
```

1. **Approve the precise response.** The human reviews the plan version, tasks, targets, departments and assignees. Its content hash binds approval to that scope.
2. **Isolate and repair the pipe.** Water Utilities must supply reviewed isolation proof before repair can proceed.
3. **Verify the utility result.** Separate follow-up checks support `UTILITY_VERIFIED`; this alone does not close the road case.
4. **Repair the road.** The Roads task can proceed after its utility prerequisite is satisfied.
5. **Observe before closing.** Completed work enters `MONITORING`. A separate synthetic wear and pavement follow-up supports `RESOLUTION_VERIFIED` and closes the episode.

This is where the graph becomes operational: the verified infrastructure connection and the task prerequisites determine **which work can proceed**, while evidence records explain **why**.

**Demonstration boundary:** the live run of Civicly's AI reached its retained token limit before drafting. The subsequent cited plan was analyst-assisted, explicitly approved by the human, and executed through authenticated simulated department workflows. This demonstrates the complete application lifecycle, not an autonomous end-to-end planning claim. All field work and observations are synthetic; verification follows the declared demo policy, not a claim of long-term municipal durability.

[Review the actual lifecycle evidence](docs/evidence/EXACT-ROAD-LIFECYCLE-RESULTS.md): three completed work orders, five outcome records, four recorded MCP decision paths and retained episode memory.

## Graph operations behind the investigation

| Function | What it answers | Interpretation |
|---|---|---|
| Directed drainage traversal | Which assets are connected upstream or downstream? | Returns bounded paths with provenance; connectivity alone is not obstruction proof |
| Shared bottleneck and impacted coverage | Do multiple incidents share a downstream asset? | Produces explainable coverage/count-based ranking, not hydraulic prediction |
| Typed infrastructure dependencies | Which reviewed utility connections matter to this road? | Uses explicit relationships; does not infer connections from distance |
| Temporal history and case retrieval | What happened here before, and what followed an intervention? | Retrieves dated context; similarity does not establish the present cause |
| Responsibility and procedure resolution | Who is accountable, and what guidance applies now? | Revalidates reviewed ownership and versioned source citations |
| Task dependency validation | Which prerequisite must be fulfilled before this work? | Checks cycles, scope and gates; deterministic ordering uses graph-fetched dependencies |
| Path explanation | Which returned nodes, edges and sources support a recorded step? | Exposes bounded, inspectable evidence paths and trace identity |
| Isolated graph ablation | What changes when a connection is removed? | Tested graph primitives change paths/rankings; the full genuine-agent ablation gate remains open |

Queries use parameterized, bounded templates and read-only execution for agent reads. Results disclose truncation and search limits; an empty result is not proof of global absence. [Implemented algorithms](backend/ALGORITHMS.md) · [Graph access controls](backend/GRAPH_ACCESS.md).

## How the agent remembers and uses knowledge

The investigation roles share a saved workflow. The model can choose to read, propose a hypothesis, assess evidence, request inspection, recommend a plan or pause. The host validates its structured output before executing an action. Limits on tools, iterations, tokens and spending make a pause an explicit outcome when the run cannot safely continue.

Memory serves different purposes:

- **Workflow continuity:** FalkorDBSaver checkpoints retain the investigation thread across pauses and resumes.
- **Episodic context:** graph retrieval exposes earlier incidents, repairs, outcomes and retained failed or uncertain attempts.
- **Organizational and procedural knowledge:** the FalkorDB GraphRAG SDK indexes versioned Markdown/PDF sources in an isolated document graph. Citations retain document/version, passage location, checksums and ownership; stale or revoked sources cannot silently authorize work.

Synthetic procedure assertions remain proposed guidance. Stored episode context is not automatically a generalized learned rule. [Runtime](backend/AGENTS_RUNTIME.md) · [Memory](backend/MEMORY.md) · [MCP](backend/CIVICLY_MCP.md).

## How Civicly connects to the three hackathon tracks

### 01 · Agents That Act on Connected Data

**Follow connections. Make informed choices.**

Civicly’s AI uses bounded MCP tools to retrieve drainage paths, underlying utility relationships and service records from FalkorDB. Inspectable graph paths show the evidence returned during the investigation.

### 02 · Agent Memory and Coordination

**Preserve context. Coordinate the next step.**

LangGraph coordinates investigation roles, while FalkorDBSaver saves the workflow across pauses and resumes. Previous assessments, interventions and outcomes remain connected in FalkorDB for later retrieval.

### 03 · Company Brain

**Bring organizational knowledge into the case.**

Civicly applies this track as a municipal operations brain. FalkorDB connects departments, reviewed asset responsibility, plans and decisions. The GraphRAG SDK retrieves cited procedures from a separate FalkorDB document graph to ground recommendations.

**One connected journey: investigation → continuity → organizational knowledge.** Demonstrated results and remaining acceptance limits follow below.

## What is demonstrated

Start with the [completed road case](https://civicly-13-55-205-208.sslip.io/investigations?investigation=INV-B09-b9d4d66e130ed348c4f6a50e9d66a891&section=report#case-workspace), move through all six tabs, and inspect the graph and supporting evidence at each step. The presenter-configured analyst session allows browsing without entering credentials; it does not grant approval authority.

| Category | Retained demonstration result |
|---|---|
| **Road damage** | Live investigation by Civicly's AI through MCP, reviewed findings, analyst-assisted plan, exact human approval, three completed simulated work orders, separate verification and episode memory |
| **Waterlogging** | Recorded drainage investigation, reviewed blockage evidence, approved drain clearance, completed simulated work, independent verified follow-up and episode memory |
| **Second road case** | Reviewed subgrade-repair plan, authorized completed work, separate verified follow-up and retained history |
| **Waste accumulation** | Reviewed missed-pickup response, human-approved plan and completed simulated collection; independent follow-up remains outstanding, so the case stays under monitoring |

**Verified deployed state, 19 October 2026:** three completed investigations, six completed work orders and three work orders with verified resolution outcomes. These counts describe different records; they are not interchangeable counts of solved problems. Three other cases retain recovery blocks.

**Explore the implementation:** [Completed road investigation](https://civicly-13-55-205-208.sslip.io/investigations?investigation=INV-B09-b9d4d66e130ed348c4f6a50e9d66a891&section=report#case-workspace) · [FalkorDB-backed workflow evidence](docs/evidence/EXACT-ROAD-LIFECYCLE-RESULTS.md) · [Verification details](docs/evidence/AWS-UI-20261019-01/RESULTS.md)

The scenario harness contains twelve scenarios with negative variants. A prepared scenario does not prove that an autonomous agent has solved it. Full live-provider, cross-category and comprehensive backend acceptance remain incomplete. Original failed attempts, uncertain operations and assessment history are retained.

Built with **FalkorDB, FalkorDB GraphRAG SDK, FalkorDBSaver, runtime MCP, Civicly's AI, LangGraph, FastAPI/Pydantic, Next.js/React/TypeScript and FalkorDB Canvas**.
