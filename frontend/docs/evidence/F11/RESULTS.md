# F11 — Civicly AI frontend wording

Technical PASS; local human review pending. R15/R16 presentation only.

Application copy changed in frontend/lib/read/workflow.ts: all explicit Gemini text becomes Civicly’s AI wording, including recorded and mixed activity and development-only explanation. LIVE_GEMINI contract identifiers and backend/provider identity remain unchanged. Matching expectations updated in frontend/tests/workflow.test.ts and frontend/scripts/verify-readability.mjs. Historical evidence/docs are retained unchanged.

Verification: npm --prefix frontend test:100PASS/0FAIL/0SKIP. npm --prefix frontend run build:PASS, including generated API/contract checks. make test-spec:both validatorsPASS. git diff --check for changed source/test/script:PASS. Actual browser after local frontend reload: new label visible and no Gemini text in rendered waterlogging page. Screenshot civicly-ai.jpg. No domain write/provider request initiated; backend unchanged. Scripted-vs-live distinction remains.

Human verify: refresh http://127.0.0.1:3100/investigations?investigation=INV-B09-8b006fb97aa2b908fc69addcf7ecd037 and check recorded activity summary. Publicsite/GitHub notupdated. No blocker to local copy change. Next: humanreview then separatelypublish/deploy approvedfrontend.
