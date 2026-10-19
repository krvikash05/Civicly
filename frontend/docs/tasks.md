# Frontend microtasks

One task per review. Backend task sequencing stays independent in the root task board. Do not interpret frontend authorization as backend task acceptance. This priority order incorporates the agreed scope: a normal investigation application with visible graph evidence, rather than a presentation-led judge mode.

- [x] F00 — Isolated folder, compatibility baseline/check and integration agreement. Static contract verification only.
- [x] F01 — Local Next.js/React/TypeScript shell; Overview and Investigations navigation, in-case lifecycle sections, responsive accessible layout and clear unavailable states. Own pinned dependencies/lockfile; port 3100. Human accepted.
- [x] F02 — Generated TypeScript DTOs, validated REST client/proxy, automatic host-configured analyst demo session with no judge sign-in form, expiry/logout/reconnect and exact route query validation. Real isolated HTTP/browser proof; technical PASS, human review pending.
- [x] F03 — Overview with real dashboard reads, category filters, case lists and case selection.
- [x] F04 — Investigation Studio with real hypotheses, evidence/citations and bounded graph; official @falkordb/canvas compatibility spike and recorded-decision/path linkage. Explain question → graph result → recorded decision; mark unavailable influence explicitly.
- [x] F05 — Authenticated fetch SSE, persisted event and cursor frames, reconnect/refetch and session expiry. No synthetic thinking animations.
- [x] F06 — In-case inspections/plans/approvals/work: exact versions, idempotency/recovery, DAG, authorized progress and actual role controls.
- [x] F07 — In-case monitoring, recurrence and relevant memory/procedure citations, retaining distinction between work completion and verified resolution.
- [x] F08 — Integrated role/scenario journeys, accessibility/responsive checks and frontend handoff; backend acceptance remains separate.

Optional extensions after essential flow: standalone map/Intelligence Explorer, full Knowledge/Memory library, advanced analytics, isolated graph counterfactual comparison and presentation controls. Do not implement these before the essential flow unless the human changes priority. Relevant evidence and memory inside a case remain essential.

All essential frontend microtasks (F00 through F08) are fully implemented, tested, and verified. Frontend handoff documented in frontend/docs/HANDOFF.md.

- [x] F09 — Human-requested readable frontend and correct workflow presentation.100frontendunitPASS;real3categoryHTTP/viewmodel andbrowserreadjourneys;build/type/contracts/specPASS. No backend/domain/provider changes. Technical PASS, localhumanreviewpending. [Results](evidence/F09/RESULTS.md). Next: reviewlocalbuild, then separatelypublish/deployacceptedfrontend.

- [x] F10 — Scenario catalog left-shift correction: shared centered overlays restored; real catalog/role browser verification and build/contracts/spec PASS. Local human review pending. [Results](evidence/F10/RESULTS.md).

- [x] F11 — Replace visible Gemini branding with Civicly’s AI;100tests/build/contracts/spec and realbrowserPASS. Localhumanreviewpending. [Results](evidence/F11/RESULTS.md).

- [x] F12 — Shorten recorded activity description per human request;13focusedtests/build/contracts/spec/browserPASS. Localreviewpending.

- [x] F13 — Case workspace Next: section navigation;5realbrowsertransitions/finalboundary/build/contracts/specPASS. Localhumanreviewpending.

- [x] F14 — Choose a case directly in empty workspace using actual inline directory;realbrowser/build/contracts/specPASS. Localhumanreviewpending.


## F15 — 19 Oct 2026

[x] F15 — Plain-language “How this affects the plan”, faithful coverage/uncertainty, original note in Technical details;105tests/build/spec/actualbrowserPASS. Local review pending. [Results](evidence/F15/RESULTS.md).


## F16 — 19 Oct 2026

[x] F16 — Journey guide connects actual available investigations, completed first; separate12scenario catalog with no false launches, all connected cases accessible.105tests/build/spec/browser/readbackPASS. Localhumanreviewpending. [Results](evidence/F16/RESULTS.md). Actual12scenario backend completion remains open.


## F17 — 19 Oct 2026

[x] F17 — Incident-specific report and investigationfocus replace duplicate technicalheadermetadata; originalreports preserved;108tests/build/spec/real7caseHTTP/browserPASS. Localhumanreviewpending. [Results](evidence/F17/RESULTS.md).


## F18 — 19 Oct 2026

[x] F18 — Replace repeated investigationcategory with sourced Reported glimpse +actual location on directory/journeycards.110tests/build/spec/real7cardHTTP/browserPASS. Localhumanreviewpending. [Results](evidence/F18/RESULTS.md).


## F19 — 19 Oct 2026

[x] F19 — Compact cardtypography/spacing/statusbadge/footerdivider; contentunchanged,build/spec/browserPASS. Localhumanreviewpending. [Results](evidence/F19/RESULTS.md).


## F20 — 19 Oct 2026

[x] F20 — Report incidentstoryfrom actualreports/currentassessments/authorizedtasks/independentoutcomes;duplicatehistorydisplayremoved.114tests/build/spec/realthreecategoryHTTP/browserPASS. Localhumanreviewpending. [Results](evidence/F20/RESULTS.md).


## F21 — 19 Oct 2026

F21 — Removed The incident at a glance heading and its introductory paragraph per exact human request. Report now starts with What happened; removed unused intro CSS and first-section top divider. R15/R16; all18requirements preserved. Source:frontend/components/investigation-workspace.tsx;frontend/app/globals.css. Build/API/contracts/typesPASS; make test-spec bothPASS; scopedwhitespacePASS. Actual localbrowser zero removedheading/paragraph matches, What happened and remainingcaseoverview visible; screenshot frontend/docs/evidence/F21/report-start.jpg. No newunit/fullbackendtests for simple copy/style removal. No domain/provider/state changes; localfrontend reloaded;AWSunchanged. Humanverify:refreshlocalcase→01Report. No blocker. Exactnext:humanreview then separatelyrequesteddeployment/nextUItask;STOP.


## F22 — 19 Oct 2026

F22 — Case-directory cards now say Open Reports and link to section=report. Workspace section is URL-derived; existing tabs/Next update section while retaining selectedcase/filter. This ensures reopening samecase from Evidence or Investigation selects Report, rather than retaining previous localtabstate. Missing/unknownsection retains prior Investigationdefault. Application paths:frontend/components/case-directory.tsx;frontend/components/investigation-workspace.tsx;frontend/lib/read/cases.ts; extendedcheckfrontend/tests/cases.test.ts. R15/R16; all18requirements preserved. npm --prefix frontend test114PASS/0FAIL/0SKIP;build/API/contracts/typesPASS;make test-spec bothPASS;scopedwhitespacePASS. Actualbrowser evidenceURL→samecaseOpenReports→Report, Next→Investigation→samecaseOpenReports→ReportPASS;7cards retainIDs/content andnewlabel. InitialWhat-happened check duringcasekeyreload false, explicitreadinesswait then reportLoadedtrue. Screenshotfrontend/docs/evidence/F22/open-reports.jpg. No domain/provider/approval/checkpoint changes. Localfrontend reloaded only;AWSunchanged. Humanverify:refreshlocaldirectory,OpenReports,thenNextInvestigationandreopencard. No blocker. Exactnext:humanreviewthen separatelyrequesteddeployment/nextUItask;STOP.


## F23 — 19 Oct 2026

F23 — Applied exact human-approvedhomepagecopy:CONNECTED EVIDENCE.INFORMED ACTION.;Understand why civic problems keep coming back.;Civicly’s AI connects reports,infrastructure and evidence to investigate recurring problems,guide coordinated action and verify what happened after the work. Application sourceonly:frontend/app/page.tsx. R15/R16;all18requirements preserved. Existing layout/actions retained. npm --prefix frontend run buildPASSincludingAPI/contracts/types;make test-specbothPASS;scopedwhitespacePASS. Actual localbrowser confirmednewcopy,connectedworkspace andreadablewrapping; screenshotfrontend/docs/evidence/F23/homepage.jpg visuallyinspected. No newunit/fullbackendrerunforcopy-onlychange. No domain/provider/approval/statechanges. Localfrontend reloaded;AWSunchanged. Humanverify:refreshlocalhost3100homepage. No blocker. Exactnext:humanreviewthen separatelyrequesteddeployment/nextUItask;STOP.


## F24 — 19 Oct 2026

[x] F24 — Fourdashboardcardsopenmatchingactualrecords,clearzero-stateandcorrectcase-sectionlinks;117tests/build/spec/realHTTP/browserPASS. Localhumanreviewpending. [Results](evidence/F24/RESULTS.md).


## F25 — 19 Oct 2026

[x] F25 — Workcardhierarchy,purpose,realprerequisitesandcompactfollowup;taskIDsexpandable.118tests/build/spec/browserPASS.Localhumanreviewpending.[Results](evidence/F25/RESULTS.md).


## F26 — 19 Oct 2026

[x] F26 — Monitoringconditions,memorypurpose,action-specificdatedoutcomecards,technicalmetadataexpandable;120tests/build/spec/realbrowser/source-readPASS.Localhumanreviewpending.[Results](evidence/F26/RESULTS.md).


## F27 — 19 Oct 2026

[x] F27 — Dashboard metrics reordered:Work completed→Verified outcomes→Active investigations→Awaiting a decision; native DOM/tab order follows array.120tests/buildPASS. Localonly;servers remain stopped;AWSunchanged.[Results](evidence/F27/RESULTS.md). Next:humanreviewthenrequesteddeployment.


## F28 — 19 Oct 2026

[x] F28 — Workcompletedpopup View Report label+section=report links;26focusedchecks/build/browserPASS. Localfrontend reloaded;AWSunchanged.[Results](evidence/F28/RESULTS.md). Next:reviewthenrequesteddeployment.


## F29 — 19 Oct 2026

[x] F29 homepageissuecards Waste accumulation→Road damage→Waterlogging;build/contract/browserPASS.Localfrontend reloaded;AWSunchanged.[Results](evidence/F29/RESULTS.md). Next:reviewthenrequesteddeployment.


## F30 — 19 Oct 2026

[x] F30 logo small right-aligned Powered by FalkorDB attribution;build/contract/desktopbrowserPASS.Localfrontend reloaded;AWSunchanged.[Results](evidence/F30/RESULTS.md).Next:reviewthenrequesteddeployment.


## F31 — 19 Oct 2026

[x] F31 — First judging improvement:featured complete-road walkthrough entry,six-stage preview,native completion gating,Report landing and existing Next navigation;120tests/build/browserPASS.Localonly.[Results](evidence/F31/RESULTS.md).

[ ] F32 — Next:explain how a selected FalkorDB path informed the recorded decision;focus relevant graph relationships. Review F31 first. Remaining approved-series ideas:stage takeaways,approval/work/follow-up timeline,curated journeys,loading/clutter.


## F32 — 19 Oct 2026

[x] F32 — Graph lookup/source trail/next recorded choice guide with exactsavedbinding,3nodefocus,widergraph,tracecontrols,evidencelinks;121tests/build/spec/browserPASS.Localonly.[Results](evidence/F32/RESULTS.md).

[ ] F33 — Next:oneclear takeaway per workspace stage;reviewF32first. Remainingseries:approval/work/outcometimeline,curatedjourneys,loading/clutter.


## F32-R — 19 Oct 2026

[x] F32-R humanrequested graphfirstwithinHowFalkorDBguide,widerdefault;build/spec/browser61/79→3/2→61/79PASS.Localonly.[Results](evidence/F32R/RESULTS.md).NextF33afterreview.


## F32-R2 — 19 Oct 2026

[x] F32-R2 actualgraphabovecaption;build/spec/browserPASS.Localonly.NextF33afterreview.[Results](evidence/F32R2/RESULTS.md).


## F32-R3 — 19 Oct 2026

[x] F32-R3 captionbelowNextrecordedchoice/Assesstheevidence;build/spec/browserPASS.Localonly.NextF33afterreview.[Results](evidence/F32R3/RESULTS.md).


## F33 — 19 Oct 2026

[x] F33 one clear takeaway per selected stage; 125 tests, build/contracts/types, both spec validators and actual six-stage road/waste-monitoring browser checks PASS. Local only; AWS unchanged. [Results](evidence/F33/RESULTS.md).

[ ] F34 — Next: approval/work/outcome timeline after human review.


## F34 — 19 Oct 2026

[x] F34 approval/work/outcome response timeline; 130 tests, build/API/contracts/types, both spec validators and actual road/waste browser checks PASS. Local only; AWS unchanged. [Results](evidence/F34/RESULTS.md).

[ ] F35 — Next: curated Scenario Journeys after human review.


## F35 — 19 Oct 2026

[x] F35 curated completed/ongoing journeys, suggested road entry and Report links; all 12 catalog entries preserved. 133 tests, build/API/contracts/types, both spec validators and real read-only browser checks PASS. Local only; AWS unchanged. [Results](evidence/F35/RESULTS.md).

[ ] F36 — Next: reduce loading flashes and visual clutter after human review.


## F36 — 19 Oct 2026

[x] F36 neutral connecting/loading, session/case-fenced cached reads, quiet panels and accurate loading accessibility labels. 136 tests, final build/API/contracts/types, both spec validators and real read-only browser checks PASS. Local only; AWS unchanged. [Results](evidence/F36/RESULTS.md).

[ ] Next: human review of six local judging improvements, then deployment only after explicit authorization.


## F37 — 19 Oct 2026

[x] F37 exact human-selected homepage headline; production build/API/contracts/types and both spec validators PASS. AWS unchanged. [Results](evidence/F37/RESULTS.md). Next: human review; deployment only when authorized.


## AWS-UI-20261019-01 — 19 Oct 2026

[x] F27–F37 reviewed frontend deployed to existing AWS demo;136tests,cloudbuild,sourcehash/publicchecks/browserPASS. Backend/data release02 retained. [Results](../../docs/evidence/AWS-UI-20261019-01/RESULTS.md). Next: human public walkthrough; STOP.
