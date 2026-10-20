# Why did the potholes keep coming back?

At Market Junction, the road kept developing potholes despite earlier repairs. Residents also reported low water pressure. Another surface repair might leave the underlying problem unresolved, so Civicly brought the road and water-utility records into the same investigation.

**The recorded demo outcome:** Water Utilities and Roads carried out an approved, coordinated response. Separate follow-up observations then supported closing the incident, with its evidence and work history saved for future investigations.

[**Follow the case in Civicly ↗**](https://civicly-13-55-205-208.sslip.io/investigations?investigation=INV-B09-b9d4d66e130ed348c4f6a50e9d66a891&section=report#case-workspace)

> **About this demonstration:** the AI investigation and database services were real. Municipal records, inspections, repairs and follow-up observations were synthetic. The final repair plan was analyst-assisted and approved by a human.

## 1. Understand what was reported

Civicly preserved the original complaint and the history of repeated road damage. Low water pressure raised a question worth checking: could a utility problem be contributing to the damage, or was the ground beneath the road failing for another reason?

A complaint started the investigation. It did not establish the cause.

**How FalkorDB supports this step:** the domain graph links the complaint to an incident, location and problem cluster. Related infrastructure and earlier occurrences can be retrieved through those relationships, while the original report remains distinct from verified findings.

## 2. Connect the clues

FalkorDB connected the road with a documented underlying water pipe, previous work and inspection records. Civicly’s AI used those connections to retrieve relevant information and compare possible explanations.

**How FalkorDB supports this step:** Civicly’s AI selects bounded MCP tools that run approved, parameterized graph reads. A sourced `UNDERLIES` relationship connects the pipe to the road; linked history and inspections provide further context. Recorded graph decision paths make the returned connections inspectable alongside the agent’s next choice.

The relationship guides the investigation. It does not prove that the pipe caused the damage merely because it lies beneath the road.

## 3. Check the evidence

Reviewed road and utility inspection findings supported both leakage and ground failure as contributing explanations. The case kept those findings alongside their sources and retained an unresolved question about the extent of additional damage.

The inspection findings were supplied and reviewed through simulated operator workflows. The AI did not perform a physical inspection or invent the observations.

**How FalkorDB supports this step:** inspection and evidence records connect to the relevant assets and hypothesis assessments, retaining their source, date and review status. Versioned assessments link supporting or contradicting evidence to each explanation, preserving earlier conclusions as findings change. Validated application services record these analytical changes; the agent cannot bypass evidence rules.

## 4. Agree on the response

An analyst helped prepare a plan using the reviewed findings, relevant procedures and responsible departments. A human approved that specific plan before work began.

The response had a clear order:

1. **Water Utilities isolated the pipe** so the repair could proceed safely.
2. **Water Utilities repaired the leak.** Separate checks recorded normal pressure and no observed leak.
3. **The Roads team repaired the ground beneath the road**, after the required utility verification.

**How FalkorDB supports this step:** the FalkorDB GraphRAG SDK retrieves cited, versioned procedures from a separate document graph. In the domain graph, the plan links to its tasks, target assets and reviewed department responsibility. `DEPENDS_ON` relationships represent the task order, and the approval binds the exact plan version and scope.

Authenticated application services revalidate these records and prerequisites before authorizing work. The graph supplies the connected context; the services enforce the rules.

**How FalkorDB tracks execution:** authorized work orders link back to approved tasks. Simulated operator actions produce durable status history and completion evidence. Utility verification remains a prerequisite for the road task; completion of one department’s work does not silently complete another department’s task.

## 5. Verify what happened after the work

Finishing the repairs moved the case into monitoring; it did not immediately close it.

Separate dated follow-up observations recorded the road’s condition after the demonstration’s simulated wear exposure. Reviewed follow-up supported a verified resolution outcome under the demo policy, allowing the incident to close.

**Completed work and a verified outcome are different records.** The simulated follow-up demonstrates that distinction; it does not establish long-term road durability in a real city.

**How FalkorDB supports this step:** work orders connect to intervention outcomes and attributed follow-up evidence. Monitoring checks read those records against the plan’s declared conditions. Validated services record the resolution outcome and close the episode only when the required evidence supports that transition. Persisted events make changes available for replay and workspace updates.

## 6. Keep the history for the next investigation

FalkorDB retained what was reported, which explanations were considered, what work was performed and what follow-up found. The saved investigation thread could also be paused and resumed.

A later investigation can retrieve that history instead of starting from an empty case file. Retaining a past outcome does not automatically turn it into a general rule for every road.

**How FalkorDB supports this step:** three separate stores serve complementary purposes:

| Store | What it preserves or retrieves |
|---|---|
| **Domain graph** | Connected reports, assessments, work and outcomes form the episode’s history for later case retrieval. |
| **GraphRAG document graph** | Sourced organizational procedures provide cited guidance for future planning. |
| **FalkorDBSaver checkpoint graph** | Saved workflow state lets the investigation pause and resume without treating the thread as a new case. |

LangGraph coordinates the investigation roles around this saved state. Checkpoints preserve workflow continuity; the domain graph remains the source of case and operational records.

## What you can inspect

Open the case and follow **Report → Investigation → Evidence → Plan & approval → Work → Monitoring & memory**.

You can inspect the recorded AI activity, supporting graph connections, reviewed findings, approved response, completed work and separate follow-up outcome.

The verification included passing unit checks, a real journey through the application and database services, and a fresh-process read confirming that the records persisted.

<details>
<summary><strong>Supporting records and technical verification</strong></summary>

These links contain machine-readable evidence and reproduction details for readers who want to examine the implementation:

- [Recorded AI investigation](EXACT-ROAD-LIFECYCLE-live-wake.json)
- [Coordinated work execution](EXACT-ROAD-LIFECYCLE-execution.json)
- [Monitoring before closure](EXACT-ROAD-LIFECYCLE-monitoring.json)
- [Persisted outcome verification](EXACT-ROAD-LIFECYCLE-verified-2026-10-18T164629615Z.json)
- [Technical verification and original audit history](EXACT-ROAD-LIFECYCLE-TECHNICAL.md)

</details>
