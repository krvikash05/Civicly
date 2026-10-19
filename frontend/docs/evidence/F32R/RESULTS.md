# F32-R — graph first and wider default

Applied exact human correction. Within How FalkorDB informed this step:lookup selector→official graph→focus/wider control→What was being checked→What the graph connected→Next recorded choice→source/reservation/technical references. The Canvas now sits inside the guide before the explanatory blocks. Wider case graph is the initial mode; a focused path is an explicit choice. Changing to another path returns to wider mode unless that path is the currently focused selection. Same case trace selection still highlights its actual saved path within the wider graph.

Source:frontend/components/recorded-decision-graph.tsx;frontend/app/globals.css (scoped graph-guide-visual wrapper). No adapter/backend/contract/data change. Existing path grounding and qualification unchanged. Localfrontend rebuilt/reloaded;AWSunchanged.

Verification:production build/API/contracts/typesPASS;beforechangecontractguardPASS;both make test-spec validatorsPASS;scoped whitespacePASS. Realbrowserinitial61nodes/79edges + Focus on this path,focus3nodes/2edges,restore61/79PASS. DOM order shows graph before question/connection/nextchoice. Screenshots graph-first-final-browser.png and wider-graph-browser.png; first graph-first-browser.png captured the later explanation and is retained. No new redundant unit/fullbackend suite for this layout/default toggle change. R04/R09/R15/R16;all18requirements preserved.

Humanverify:refresh localoriginalroadInvestigation;graphpanel openswide,and question/explanation/nextchoice followbelowtheCanvas. OptionalFocusonthispathnarrowsit. No blocker. Next:F33 stage takeaways after review of this correction;STOP.
