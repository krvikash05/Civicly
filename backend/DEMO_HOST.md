# Presenter backend host

This host runs genuine configured Gemini selections against runtime MCP and FalkorDB. Source material and field reports are explicitly synthetic. It is a bounded demonstration, not full B10/B20/B-END acceptance.

## Existing rehearsal

The API is running at http://127.0.0.1:8010. Private host configuration: `.runtime/demo-presenter/run-01/host-clean.json`. Credentials remain in private presenter files; the frontend server connection is `.runtime/demo-presenter/run-01/frontend-connection.env`. Never copy credentials into public artifacts or browser variables.

Restart only the backend API if necessary, from repository root:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-clean.json api --port 8010
```

Do not start a second listener if port 8010 is occupied. Do not use the offline worker for these live threads. The HTTP process does not run a paid background worker.

Readback without a provider request:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-clean.json status
```

## Judge story that is currently supported

Open waterlogging investigation `INV-B09-8b006fb97aa2b908fc69addcf7ecd037`. Start with its complaint and affected assets. In the investigation trace, show the actual Gemini-selected drainage traversal, history and organizational procedure calls. In graph view, select recorded decision paths: topology is evidence for investigation scope, not proof of obstruction. Show competing blockage/capacity assessments initially marked inconclusive. Show the independently attributed synthetic inspection report and its dates. The same saved thread refreshed evidence, reassessed blockage, and generated a sourced remedial draft. Show version/hash, ownership, safety/inspection conditions, citations and monitoring criteria. Stop at HUMAN_REVIEW: approval, work completion and verified resolution are separate stages and have not occurred in this case.

Road and waste category lists contain real cases and traces, but their live runs paused on tool/dependency errors. Show those only as honest failure boundaries, not successful end-to-end scenarios. Do not reconcile or retry blocked records. Original retained quarantines remain intact.

## Host controls

`setup` creates new isolated runtime graphs; do not rerun it over this rehearsal. `preflight` validates configuration, source/checkpoint binding, ledger and compatibility. The optional model-metadata flag uses Google's model endpoint without generation. `queue` explicitly requests a scoped wake. `worker --live --case ID --batches 1` is an explicit paid action; it never falls back to a scripted model. Do not issue more paid commands as part of frontend setup. `release` performs an authenticated, attributed synthetic inspection requested by the agent; uncertain dispatch markers require operator review. `discover` registers already-persisted activity for SSE, without executing a wake or acknowledging delivery.

A Redis writer fence serializes host wakes and source writes; case-specific claiming prevents accidentally waking a foreign case. All analytical/operational writes still use domain services. Existing per-case/project caps remain unchanged; no automatic retry or cap increase is authorized by this runbook.

## DEMO-READ-CONTRACT update

The newer private `host-rehearsal02.json` keeps the same graph/auth and retained water case, and selects one independent S03 road and S05 waste-service pair. Presenter `rehearsal` creates that pair once; rerunning it is rejected. Both genuine initial wakes completed and await requested field inspections. Do not fulfill/resume them as part of a frontend read. Use this manifest for latest nonbillable `status`. The previous `host-clean.json` remains available for historical paused-case inspection.

Model READ inputs now validate before dispatch and may use the provider's existing one-output correction. That correction is paid/accounted when live, and is never an uncertain-write retry. Future-output contracts do not rewrite saved selections/checkpoint inventories. Full results and task-only patch: docs/evidence/DEMO-READ-CONTRACT-RESULTS.md.

## Field/review stage

Latest host status includes real inspection/evidence and PlanDTO data. Current requested field lifecycles are COMPLETED; checkpoint request IDs remain history. Current supervisor context supplements them with scope-checked current statuses/report IDs, explicitly requiring MCP to read findings. Waste reached TOKEN_BUDGET; host preflight blocks another run. No budget change/retry is permitted by this runbook. Water/road plans are submitted PENDING, awaiting an actual human decision; no work executed. Use DEMO_WALKTHROUGH.md and the exact review packet.59routesoperations/55paths/185schemas; PlanDTO now includes native task_bindings for clients.


## Independent compact-format smoke

`context-smoke --live --case ID` is a presenter-only paid diagnostic: copy saved context, separate diagnostic thread, originalcaseledgercaps, at mostone model selection/one approved realMCPread. It never resumes the original workflow or dispatches domain actions. Existing marker prohibits repeat. Do not run it for frontend setup.

`context-smoke-verify` is nonbillable and was verified in a freshprocess. It checks existing paidattempt's trace/scope/argument/outputhashes, originalcheckpoint/source revision, noprobecheckpoint andSETTLEDledgerrecords. It never retries a provider/tool or clears recovery. The firstliveprobe's read succeeded but harness envelope checkfailed; correctedReadResultnormalization and durable readback established limitedPASS withoutanothercall. Cost$0.02192475;1count+1generation; actualinput28893/totaltokens28961. Packedformat remainsopt-in/offbydefault; onevalidREADselection is not fullscenario reasoning. See docs/evidence/DEMO-CONTEXT-SMOKE-RESULTS.md.
