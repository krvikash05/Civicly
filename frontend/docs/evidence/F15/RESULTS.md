# F15 — Plain-language plan explanations

Human-requested Evidence/Possible causes readability correction. Objectives R15/R16; all18requirements remain binding.

Application paths: frontend/lib/read/display.ts; frontend/components/hypotheses-panel.tsx. Focused checks added to frontend/tests/display.test.ts. Existing concurrent changes preserved.

“How this affects the plan” replaces “Remediation plan consideration”. Known saved blockage/capacity/structural/pressure-test/conditional/uncertain-extent notes receive plain explanations. Actual addressed flag separately states plan coverage; explanations do not upgrade hypothesis confidence. Unknown coded notes get a neutral summary with original note retained in expandable Technical details. Saved records, backend and graph are unchanged.

Validation: npm --prefix frontend test:105PASS/0FAIL/0SKIP (five added cases). npm --prefix frontend run build:PASS including API freshness/contracts/TypeScript. make test-spec:both validatorsPASS. Scoped git diff --check:PASS. Actual local browser loaded the retained waterlogging case, verified blockage and inconclusive-capacity explanations, expanded Technical details and confirmed exact original assessment text. Screenshot:plain-plan-explanation.jpg. No paid provider requests or domain writes; no cloud deployment.

Human verification: open http://127.0.0.1:3100/investigations?investigation=INV-B09-8b006fb97aa2b908fc69addcf7ecd037 →03Evidence. Read “How this affects the plan” on both possible causes; expand Technical details for original source wording.

Known limits: unrecognized coded templates remain neutral rather than being guessed. AWS remains at prior accepted version until deployment is requested. Next task: human review of F15, then separately authorized publication/deployment or next readability request. Stop after F15.
