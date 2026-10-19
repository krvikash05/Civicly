# F32 — recorded graph lookup → source trail → next choice

Implemented the second approved judging improvement only. The graph panel now opens with one matched saved lookup, the recorded question, plain-language connection descriptions and its next chronologically recorded choice. The original road case has two complete current source trails:road→inspection→report and pipe→inspection→report. Each focused view contains3returnednodes/2returnededges, with current source status retained; Show wider case graph restores61nodes/79edges. The earlier infrastructure dependency lookup references a historical path not present in the current bounded graph, so it is not substituted with a current unrelated path.

## Grounding and behavior

recordedGraphSteps admits only successful validated TOOL events bound by exact execution_id/path_id to an available full path and by exact decision_id to a READ decision of the same investigation, execution mode and normalized tool identity. Decision time must precede the lookup. Every node and connecting edge must exist in the returned graph; missing/foreign paths are excluded. The fullest linked path per lookup is preferred over its prefixes. The next choice is explicitly the next recorded decision by time, not a claimed causal inference or new model reasoning.

The guide preserves real edge direction when describing connections, while following the saved path's traversal order for focus membership. Inspection/report associations establish provenance, not causation; candidate and recorded-association qualifications stay visible. Causes still require reviewed findings. Original rationale, tool, decision/path identifiers, timestamp and activity attribution remain expandable. Evidence buttons open the existing source modal. No new arbitrary Cypher, model calls, domain writes, approvals, checkpoint changes or causal claims.

Trace cards with a match now have View this path in graph buttons that select and scroll to the guide. Path dropdown selects another saved trail. Default graph focus is the first chronological complete matched trail; missing matches show a clear bounded-context explanation and wider returned graph. All existing graph inspector/table/expand controls remain. Canvas update signature now includes projected content, so same-ID provenance/status changes refresh instead of retaining stale styling.

## Changed paths

New:frontend/lib/read/decision-paths.ts;frontend/components/recorded-decision-graph.tsx.
Modified:frontend/components/falkordb-canvas-view.tsx;frontend/components/decision-trace-panel.tsx;frontend/components/investigation-workspace.tsx;frontend/app/globals.css;frontend/tests/canvas-adapter.test.ts.
Evidence:frontend/docs/evidence/F32/. Tracking:frontend/docs/tasks.md plus six root trackers appended. Backend/contracts/dependencies/retaineddata unchanged. Localfrontend/backend running;AWS not updated.

## Verification

- Actual authenticated read-only HTTP graph+trace snapshot:road-graph-trace.json. Existing genuine model/MCP records were inspected, not newly executed. This operator read/login did not create an investigation or paid run.
- npm --prefix frontend test →121 PASS/0FAIL/0SKIP;tests-final.txt. One added meaningful adapter test validates real retained path bindings, next recorded ASSESS, exact focus subset/provenance, missing nodes/edges/path field, failed validation, mismatched investigation/execution/mode, candidate qualification.
- npm --prefix frontend run build →PASS API/contracts/types;build-verified.txt. Initial build.txt failure TS18048 optional decision_paths was corrected with an empty-array fallback, and optional-path behavior is tested. Failed output retained; no runtime corruption.
- make test-spec →both validatorsPASS;spec.txt. Scoped whitespace checkPASS.
- Actual localbrowser:defaultroad3nodes/2edges;tracebutton→pipeselection;wider61/79→focus3/2;linkedactualinspectionreportmodal with attributedsynthetic source and independentreview;accessible table3nodes/2edges;dropdown road→pipe samefocuscountsPASS. graph-guide-browser.png visually inspected. No fullbackend/provider rerun, no ablation or proof that this UI changes agent behavior. Broader/mobile and allcase browsermatrix not claimed.

## Human verification / next

Open http://127.0.0.1:3100/investigations?investigation=INV-B09-b9d4d66e130ed348c4f6a50e9d66a891&section=investigation. In the right graph panel, read How FalkorDB informed this step, switch road/pipe, open linked evidence, and toggle wider graph. In the saved trace use View this path in graph. R04/R09/R15/R16;all18requirements remainbinding;no backendacceptance gate advanced.

Next:F33 one clear takeaway per stage, after human review of F32. Remaining approved series:approval/work/outcome timeline,curated journeys,loading/clutter. Stop afterF32;AWS deployment remains separate.
