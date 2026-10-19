# AWS-UI-20261019-01 — Frontend deployment PASS

19 October 2026. User authorized deploying the latest reviewed version to the existing AWS demo.

Live: https://civicly-13-55-205-208.sslip.io
Instance: i-00e332036cd609ff0, ap-southeast-2.
Frontend: /opt/civicly-frontend-releases/ui-20261019-01/frontend.
Backend/data release unchanged: /opt/civicly → /opt/civicly-releases/update-20261019-02.
Systemd frontend override: /etc/systemd/system/civicly-frontend.service.d/50-ui-release.conf.

Deployed reviewed frontend improvements through F37, including exact new homepage headline, featured case, graph guide/default wider graph/caption order, six stage takeaways, response timeline, curated journeys and calmer loading states. Backend service PID290917 remained unchanged during cutover. No Docker/database restart, snapshot replacement, migration, scenario write, provider request or agent worker wake. Normal temporary public demo sessions were created/revoked for verification. Source archive contained 70 explicitly allowlisted public source/contract files, no .env/.runtime/credentials/private data. Archive SHA256: 9f30227a78f1c947964a4be3c32574e389cb2a91ccc310af59edd7ef4102d76c. Transferred directly through SSM with no S3 bucket, instance-role grant or new infrastructure.

Verification:
- npm --prefix frontend test — 136 PASS, 0 FAIL, 0 SKIP (frontend-tests.txt).
- make test-spec — both validators PASS (spec-tests.txt).
- Actual EC2 npm production build — PASS including API/contracts/types. First build failed because Turbopack disallows external symlinked dependencies; replaced staging symlink with independent copy of existing locked node_modules and rebuilt successfully. Failure retained in cloud build-attempt-01.log; production was unaffected.
- 70/70 cloud source hashes match source-manifest.json; cloud-source-proof.json.
- Cutover restarted frontend only, approximately 2.5seconds including one expected failed readiness probe before listening. Automatic rollback trap was installed but not exercised; public rollback not fault-injected. cutover.json.
- Public HTTPS/API/SSE/security acceptance passed before and after: automatic analyst session, dependency readiness, unauthorized/cross-origin denials, three completed cases, waste monitoring, all three recovery traces, graph, traces, procedures, memory, SSE frame and revoked-session denial. public-before.json/public-after.json.
- Preservation comparison PASS: graph revision remains1148, case summaries/dependencies/metrics unchanged: three completed cases, one monitoring, three open recovery cases, six completed work orders, three verified work orders, zero pending approvals. API-level checks, not a new byte-for-byte DB/quarantine dump audit.
- Actual public browser: new headline and connected homepage; curated 3 completed/4 ongoing journeys; suggested road opened Report; takeaway, wider graph guide with caption after Next recorded choice, current 3/3 work timeline, five dated follow-ups and source modal, Monitoring closure. Screenshots captured. Homepage final ready screenshot inspected.
- Local app servers left running. No full backend suite, reboot/container lifecycle or new live-model execution.

Human verification: open public homepage, confirm new headline and Demo connected; Scenarios → suggested road → Report → Investigation → Work → Monitoring. Confirm timeline, evidence links and verified episode. Waste remains monitored; existing backend B10/B20/B-END/recovery gates remain open. Report unexpected behavior with these result/proof files.

Rollback (frontend only, explicitly chosen): remove the new 50-ui-release.conf override, systemctl daemon-reload, systemctl restart civicly-frontend. This restores the existing /opt/civicly/frontend working directory while leaving backend/data unchanged. Retain the new release for diagnostics. No rollback performed.

Changed repository paths: deploy/aws/README.md, the evidence files in this directory and append-only six root trackers plus frontend/docs/tasks.md. Application code was not changed by deployment. Next: human public walkthrough; no further backend/paid run authorized. STOP.
