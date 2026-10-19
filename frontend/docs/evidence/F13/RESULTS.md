# F13 — Next section navigation

F13 — Added a small Next: <section> arrow button in the case workspace header (frontend/components/investigation-workspace.tsx). Uses existing section state only, available when a case is selected; hidden on final Monitoring & memory section. No workflow execution, approval or provider invocation. R15/R16 presentation; other requirements preserved.

Production build (includes generated API/contracts) PASS; both spec validators PASS; whitespace PASS. Actual browser clicked all five forward transitions Report→Investigation→Evidence→Plan & approval→Work→Monitoring & memory; final heading visible and0Nextbuttons. Existing stage tabs work returning to Report. No new unit tests for this low-impact UI navigation. Local frontend refreshed with unchanged settings. Publicsite/GitHub unchanged. Humanverify:openlocalcase, Report, click Next: Investigation then continue. No local blocker; next humanreview then separatelypublish/deploy.

Flow: headerbutton → existing setStage(stage+1) → existing stage panels/tabs; domainstate unchanged. Named Next rather than Start/Approve to describe browsing. Only application source changed is workspace component; build.txt/spec.txt and next-investigation.jpg retain verification.
