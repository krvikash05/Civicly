# F30 — small FalkorDB logo attribution

Added exact text Powered by FalkorDB beneath Civicly, aligned with the right edge of its wordmark. Uses9px muted text, compact3px top spacing and normal letter spacing. Existing graph icon, logo colors and home-link destination remain. Source:frontend/components/shell.tsx;frontend/app/globals.css (scoped brand classes).

Verification:before-change contractguardPASS;productionbuild/API/contracts/typesPASS. Actual local browser rendered Civicly./Powered by FalkorDB; desktop screenshot logo-browser.png visually inspected, attribution readable and correctly aligned. No bitmap/image generation, new dependencies or backend/provider changes. No newunit/fullbackendtests for this small styling/text change; no mobileaudit claimed.

Frontend rebuilt/reloaded locally;AWSunchanged. Humanverify:refresh http://127.0.0.1:3100 and inspect upper-leftlogo. R15/R16;all18requirements preserved. Next:humanreviewthenrequesteddeployment/nextUItask;STOP.
