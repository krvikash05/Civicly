# F02 — typed transport and operator sessions

Objective R16; preserve R01–R18, including R15 provenance/read contracts. F01 accepted by human. One frontend microtask only, with backend implementation continuing independently.

Planned files: frontend generated schemas/types/route inventory and generator/check; typed REST client, validation/error/session modules and offline tests; auth provider/sign-in panel and shell/unavailable wording; frontend proxy route/helper and configuration example; frontend-owned isolated Python integration harness and Node HTTP probe; docs and six root tracker appends. No backend or normative contract edits, lifecycle commands, graph reset or paid provider calls.

Risks: schema drift, unknown/repeated query fields, expired/revoked sessions, token exposure, out-of-order session responses, uncertain-write replay and proxy leaks. Store credentials/token in memory only; close/drop password after submission; no automatic mutation retry/new idempotency key; identity must match authenticated /auth/me. Deny browser-supplied backend origin or graph selectors. Default unconfigured API→sanitized503; host-only loopback origin, allowlisted contract routes, no redirect following or token forwarding to another origin.

Verification: generator check, contract guard, node offline client/proxy/session tests, npm build/typecheck, both specification validators. Real isolated HTTP API uses accepted FastAPI/Services/Auth/graph repository with a new exact active profile and private SQLite auth; no memory capability, worker, MCP, provider or broad readiness claim. Exercise frontend proxy + generated validation + login/me/read/logout/401 and bad query. Test-only random credentials never written to public output. New proof graph retained; no original sources changed. UI browser: sign-in/disconnected validation and responsive review. Human should see a sign-in action, clear unavailable error if no host configured, and no invented data. Next F03 real overview/case selection only after review.

## Human scope correction before auth implementation

The human explicitly rejected sign-in UI for judges. Replace the panel with one automatic temporary ANALYST demo session using server-only host-configured credentials and existing backend authentication. No browser credential fields, role claims or selectors; no default ADMIN/APPROVER identity. No invented successful connection. Reconnect/end-session controls retain expiry/revocation behaviour; higher-authority action flows remain later tasks.
