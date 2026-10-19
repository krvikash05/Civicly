# F37 — Homepage headline

Replaced the homepage h1 in frontend/app/page.tsx with the exact human-selected text: Every civic problem has a story. Follow it to resolution.

npm --prefix frontend run build: PASS including API/contracts/types (build.txt).
make test-spec: both validators PASS (spec.txt).
Scoped git diff --check: PASS.
No new tests or full backend rerun for this copy-only edit. No listener was present on local port 3100, so no server was started or browser verification claimed. AWS unchanged.

Human verification: start the local frontend with npm --prefix frontend run start and open the homepage. Expect the exact headline above. Next: human review; deployment only when authorized. R15/R16; all eighteen requirements preserved. STOP.
