# F02 — typed REST and automatic demo sessions

2026-10-18. Technical PASS; human review pending. F01 accepted. Primary objectiveR16, preserveR01–R18 and explainabilityR15. Human explicitly rejected a judge sign-in form: the implementation uses an automatic presenter-configured existing ANALYST session, retaining backend authentication and role gates.

## Implemented

Generated183 model schemas/types and58 route contracts from current backend machine contracts. Exact request/query/response validation; no coercion, unknown-field dropping or automatic mutation retry. Runtime checks distinguish401/403, incompatible responses, uncertain writes and operator recovery. Session tokens remain in memory; late responses cannot restore old sessions or clear replacements. Expiry, explicit logout, manual reconnect and failed server-revocation messaging are implemented. Reviewer/field credentials and operational forms remain F06, SSE F05.

Local Next proxy forwards only allowlisted routes to a host-configured loopback API origin, with bounded request bodies, no cookies, no redirects or caller-supplied origin/graph. Server-only demo password authenticates OP-ANALYST through the existing backend login; browser verifies /auth/me before showing connected. No password/role selectors or sign-in panel. No automatic agent wake/approval/work. F03 will bind overview/case resources; current case panels remain unavailable rather than pretending live results.

Own pinned dependencies added: ajv8.20.0 and json-schema-to-typescript16.0.0. Existing Next16.4.2/React19.3.1/TypeScript7.0.2 unchanged; Node24.21.0/npm12.2.0. npm install audit reported0 vulnerabilities (not a full security audit). Separate frontend lockfile. Package type module; prebuild checks generated files and reviewed contract baseline.

Concurrent backend change added a schema (182→183) while route inventory stayed58/55. Generated current183 definitions, checked static validators/runtime consumed schemas and explicitly updated only frontend baseline. No backend contract edit by this task.

## Final executed checks

- `npm test` fromfrontend:30distinct offline transport/proxy/session testsPASS,0FAIL/0SKIP. Fakes explicitly labelled in test code; no backend/agent proof from these.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_contracts.py` fromfrontend:4/4PASS unchanged guard tests.
- `npm run typecheck`:PASS.
- `npm run build`:PASS production compile, TypeScript, static pages and dynamic /api/demo-session + /api/v1/[...path]. Prebuild generated/baseline checksPASS58operations/55paths/183schemas.
- Both root specification validators using backend/.venv/bin/python:PASS static checks.
- `backend/.venv/bin/python frontend/scripts/verify_integration.py`: real NextHTTPproxy→acceptedFastAPI/Services/Auth→freshFalkorDB source. Actual automatic session, authenticated identity, Department read, query422, unauthenticated401, analyst admin-action403 and logout-token401. Runtime58route parity and consumed schema parityPASS. Final proof F02-integration.json. Full memory/worker/MCP readiness deliberately not supplied; not a backend-complete deployment or genuine agent test.
- Actual browser against isolated configured API: opensDemoConnected with no form; menuEndDemoSession→SessionEnded; Reconnect→DemoConnected; browser error/warning inspection[]. ScreenshotF02-connected.png captured during successful flow before final informational copy refinement. Existing3100preview separately verified unavailable when no presenter configuration is provided. No automatic test credential installation into3100.

Final code changes after the successful browser flow were covered by30offline tests, final production build/typecheck and final realHTTPprobe. They include query-null omission, stale logout feedback guard, UNKNOWN detail tagging and nontechnical preview copy; no new domain/storage behavior.

## Retained failures and corrections

1. Early typecheck caught comparison of schema literaltrue withfalse; removed redundant comparison (runtime schema validator already rejects disabled identities).
2. One root npm invocation used the wrong directory. One test-writing invocation also targeted the wrong relative folder; its0test output was not counted. Corrected frontend paths and explicit test file script prevent a missing-glob false pass. Final30tests are actual executed cases.
3. One test-only Record inference failed TypeScript; corrected explicit record annotation. Module-type warning resolved by explicit package type.
4. First isolated integration stopped because OpenAPI uses #/components/schemas while JSONSchema uses #/$defs. Normalized only reference prefixes in comparison; no backend change.
5. Browser-origin regression: Next internal URL may use localhost when external Host is127.0.0.1. Compare against validated original loopbackHost; ignore forwardedHost. Add regression and browser-style Origin headers to realHTTPprobe. An affected probe failed; original failed graph/auth/private logs retained.
6. Browser still failed before contacting the proxy: storing native fetch as a class member supplied an invalid receiver in this browser. Wrap the global fetch call; add receiver regression. Browser auto-connect/logout/reconnect then passed. Temporary safe host/status diagnostics were removed. No credentials were logged/exported.

All fresh proof/failed graphs and private runtime artifacts retained. Integration harness never resets/deletes an existing source or starts a worker/provider. Backend/app, backend/tests and contracts hashes match at the start/end of each successful real check; read-only preservation evidence in final integrationJSON. Provider interlock shows no external/blocked attempts; no paid permit/model is constructed. Public artifacts contain no credentials.

## Limits and human verification

No unresolved F02 runtime failure. Persistent preview still needs presenter-only environment configuration of an existing authorized isolated API/demo analyst account, per frontend/docs/API_CONNECTION.md. Judges never enter credentials. Without configuration, navigate and use Reconnect to see the explicit unavailable state. A configured presenter should see DemoConnected, end the temporary session and reconnect without any form. Share the safe request reference/results file on failure, never private env/profile/auth contents.

Current backend feature gaps remain under backend ownership. Case data/countersF03, evidence/CanvasF04, SSEF05 and operational action formsF06 are not implemented by F02. Full graph/agent/backend acceptance not claimed. Exact next frontend taskF03: real overview/case list and selection. STOPforreview.
