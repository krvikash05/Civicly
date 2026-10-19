# F32-R3 — graph caption beneath next recorded choice

Moved What this graph shows from the Canvas block into the guide directly beneath Next recorded choice and its Assess the evidence rationale. Graph remains first/widerdefault;question→connections→nextchoice→caption→sourcequalifications/details. Extracted shared GraphCaption in falkordb-canvas-view.tsx;Canvas showCaption defaults true forstandaloneuse,guide disables it and renders the same caption once in the requested position. Focused/wider counts and absent-path qualifications use the actual currently displayed subgraph.

Source:frontend/components/falkordb-canvas-view.tsx;frontend/components/recorded-decision-graph.tsx. Localfrontend rebuilt/reloaded;AWSunchanged.Backend/contracts/data/providers untouched.

Verification:productionbuild/API/contracts/typesPASS;beforecontractguardPASS;bothspecvalidatorsPASS;scopedwhitespacePASS;actualbrowsercaptionfollowsNextrecordedchoice/Assesstheevidence,rendersonce,andwiderdefaultretained.No newunit/fullbackendtestforsmallrenderrelocation.

Humanverify:refreshlocaloriginalroadInvestigation,scrollbelowNextrecordedchoice/AssesstheevidenceforWhatthisgraphshows.NextF33stagetakeawaysafterreview;STOP.R15/R16;all18requirements preserved.
