# Road investigation — technical verification and original audit

[Return to the plain-language case story](EXACT-ROAD-LIFECYCLE-RESULTS.md).

<details>
<summary><strong>Technical verification and local readback</strong></summary>

From a configured local checkout, verify the retained case without another provider request:

```sh
PYTHONPATH=backend backend/.venv/bin/python scripts/exact_road_lifecycle.py verify
```

The milestone expected the incident to be `ENDED`, the investigation and plan to be `COMPLETED`, three work orders, one own-episode memory entry with five outcomes, and a bounded graph projection of 61 nodes. This command uses authenticated reads and session lifecycle calls; it does not execute work or call the model.

Case: `INV-B09-b9d4d66e130ed348c4f6a50e9d66a891`

Plan: `PLAN-B12-11e6b8d220e7923a715f5cc0a371b993`, version 1.

Do not rerun preparation or execution on the completed plan. See the original record below for approval hash, reconciliation history, accounting and verification caveats.

</details>

<details>
<summary><strong>Original milestone record — detailed audit history</strong></summary>

The following record is preserved verbatim. Its pending-review instructions and descriptions of other cases reflect the milestone’s original recording time, rather than the current deployment status.

# EXACT-ROAD-LIFECYCLE — completed synthetic episode, human review pending

## Scope and actual outcome

Human selected exactly `INC-B08-27a2cb5d89ae9ab9d86f999cf7b50472`, LOC-JUNCTION, and explicitly authorized narrowly audited reconciliation and then exact-plan execution. No replacement incident was used. Requirement coverage advances R02/R04/R06–R17 and the road portion of R18; all eighteen requirements remain binding. Full three-category/B10/B20/B-END acceptance is not claimed.

Original investigation `INV-B09-b9d4d66e130ed348c4f6a50e9d66a891` and original thread `DEMO-a96d7432fed21ae4921aca5a55195feb` retained. Actual final state: incident ENDED, investigation/plan COMPLETED, cluster CONTROLLED. One plan, three tasks, three work orders. Five outcome records and five distinct completion/follow-up reports are now visible in own-episode memory.

## Proven flow

1. Complaint and reported road incident retained. Candidate links not promoted by assumption.
2. Earlier ambiguous PROPOSE had no mandatory dispatch journal, B09 journal, or native hypothesis. READY repository readback proved no effect. Authenticated admin wrote an immutable human-authorized attestation. Original checkpoint/hash, WRITE_OUTCOME_UNKNOWN error, decision and recovery history retained; no quarantine cleared and no original operation replayed.
3. Existing road inspection completed with reviewed attributed synthetic causal/safety findings. Analyst explicitly requested a separate utility differential inspection; its reviewed synthetic report supplies leak/infiltration/safety observations. This supplemental request was operator-assisted.
4. Same original thread resumed with actual Gemini, actual discovered runtime MCP reads and Saver persistence. It read road and pipe reports, created two SUPPORTED assessments and read source procedures. Four recorded graph decision paths remain. The existing cumulative token gate then stopped the model before drafting: 375,398 cumulative tokens, next count would exceed 400,000. No budget raised or extra wake attempted.
5. Analyst-assisted draft uses those current assessments, actual GraphRAG D020/D022 citations and reviewed ownership. Additional damage extent is retained as an explicit INCONCLUSIVE hypothesis, with no evidence or extra work claimed. Both observed mechanisms remain SUPPORTED with their original verification gaps.
6. Human approved exact plan `PLAN-B12-11e6b8d220e7923a715f5cc0a371b993`, v1, SHA256 `b0a730059b2339f87b24fa8434fe5f3706f9686d524ba47e746ee0c1f1c78c57`. OP-APPROVER recorded that exact scope through HTTP. OP-WATER-LEAD isolated PIPE-100, supplied reviewed isolation proof, repaired it and obtained separately reviewed POST_REPAIR_PRESSURE_NORMAL / POST_REPAIR_LEAK_ABSENT follow-up, classified UTILITY_VERIFIED without closing the case.
7. Verified UNDERLIES from PIPE-100 to ROAD-100 bound the road dependency. OP-ROAD-LEAD then performed simulated subgrade repair. All work completed first entered MONITORING (snapshot retained). Separate dated synthetic WEAR_EXPOSURE and FOLLOWUP_PAVEMENT=0 evidence produced RESOLUTION_VERIFIED and case closure. Crew completion alone did not close it.
8. Fresh-process and reloaded API readback confirms durable state. Own ended-episode memory projection now exposes five immutable outcomes and five report references. This is retained episodic context, not an automatically generalized lesson. No DTO/schema or frontend code change.

All physical actions/observations are explicitly SYNTHETIC, using the bounded demo policy. Follow-up sources/inspection records are separate from completion and independently authenticated analyst reviewed; the field leads are the assigned simulated operators. The road wear observation is an explicit synthetic demonstration, not a claim of actual long-term road durability or municipal-standard acceptance.

## Tests and measured usage

45 distinct final unit checks PASS; zero final failures/skips. One actual retained-graph lifecycle journey through real TCP HTTP/FalkorDB/GraphRAG/MCP/Gemini/Saver, with 101 execution HTTP calls and additional fresh-process reads; these are one journey, not hundreds of independent test cases. Final spec validators both PASS. Unit interlock: zero external requests. Actual paid wake: 10 countTokens requests, 9 generation attempts, 275,638 additional reported total tokens, calculated known cost $0.20620095; cumulative case cost $0.28464795, no outstanding request uncertainty/reservations and unchanged $0.50 case cap. COUNT requests are not generation usage. Scripted field execution is not a live autonomous planner proof.

Historical harness corrections retained: preparation first failed before draft at missing active-graph scope (alternative hypothesis/assessment had already committed and were safely retained); corrected scope proceeded without repeating that assessment. Initial read-only audit imported a nonexistent State module; corrected to the required read-only errors attribute and reran. First full lifecycle readback had zero own-memory items because related-case retrieval excluded the seed; narrow completed-episode projection corrected this and the final fresh read shows one own-memory row. Earlier verification files are preserved, not rewritten. No failed work-order/unknown operational mutation occurred in this task.

## Reproduce and review

Refresh http://localhost:3100/investigations?investigation=INV-B09-b9d4d66e130ed348c4f6a50e9d66a891 . Inspect Report → Investigation → Evidence → Plan & Approval → Work → Monitoring & Memory. Backend proves those records; browser visual QA remains with the separately developed frontend. The completed incident is historical, so its mapping is in historical_incident_ids. Show true LIVE_GEMINI trace events and decision paths, then explicitly explain the analyst-assisted planning and simulated operations.

Nonbillable verification: `PYTHONPATH=backend backend/.venv/bin/python scripts/exact_road_lifecycle.py verify`. Expected ENDED/COMPLETED/COMPLETED, one own episode memory with five outcomes, three work orders and 61 graph nodes (bounded projection). It makes authenticated reads and auth session lifecycle calls, never provider requests or domain mutations. Do not rerun prepare/execute on the completed plan; execution requires an exact approved hash, PENDING_APPROVAL state and a private exclusive execution marker.

Known limits: bounded reads and historical case-search truncation remain explicit; last agent checkpoint retains TOKEN_BUDGET/null current_plan_id because a later analyst draft is operationally separate; legacy InvestigationDTO.runtime_status remains a static development-era label and is not live provenance. Use trace execution_mode and actual InvestigationDTO/plan lifecycle state. Original waste remains blocked and unreconciled. Other water/clean-road plans remain pending. No recurrence scenario or autonomous end-to-end planner acceptance established. All 1,368 baseline evidence files unchanged; frontend untouched; only backend API reloaded to serve memory correction.

Exact next: human review and frontend walkthrough of this completed incident. Further live work, unrelated reconciliation and B21 remain outside this task. STOP.

</details>
