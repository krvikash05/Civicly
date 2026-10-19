# F32-R2 — graph above its caption

Moved the What this graph shows caption below the actual FalkorDB Canvas/table stage. Graph toolbar and bounds stay above the visualization; caption, legend and technical metadata follow it. The larger guide's heading, wider default, lookup selection and subsequent question/connections/nextchoice stay intact.

Source:frontend/components/falkordb-canvas-view.tsx only. Localfrontend rebuilt/reloaded;AWSunchanged;backend/contracts/data/provider unchanged. Contractguard/build/API/typesPASS;bothspecvalidatorsPASS;scopedwhitespacePASS. ActualbrowserDOM/screenshot confirms Canvas before caption. No newunit/fullbackendtests for JSXblockreorder. Evidence:graph-above-caption-browser.png.

Humanverify:refreshlocalroadInvestigation;rightpanelgraphcomesbeforeWhatthisgraphshows. Next:F33stagetakeawaysafterreview;STOP.R15/R16;all18requirements preserved.
