# F02 demo connection and typed REST client

Judges do not sign in. A local presenter configures one existing backend demo analyst account once, and Civicly automatically opens a temporary session when the workspace loads. Browser tokens remain in memory; no passwords or tokens in URLs, browser persistent storage or tracked files. A refresh opens another temporary session; existing unused sessions expire under the backend's normal policy. No role promotion, approval or work starts automatically.

## Presenter configuration

Use an isolated, authorized API instance prepared through the backend's runbook. F02 does not provision, activate or change the running backend. The existing account must be OP-ANALYST; ADMIN/APPROVER identities are not accepted by the automatic demo endpoint.

Inside frontend, copy `.env.example` to the ignored `.env.local` and fill in the existing API origin and private analyst demo password. Use `CIVICLY_API_ORIGIN`, `CIVICLY_DEMO_OPERATOR_ID=OP-ANALYST` and `CIVICLY_DEMO_PASSWORD`. Do not prefix secrets with NEXT_PUBLIC_. Restart the frontend process after changing environment configuration. The initial implementation is local-only: the origin must be an explicit loopback HTTP origin/port, not port3100. Public hosting/auth policy is outside F02.

Run `npm run dev` and open http://127.0.0.1:3100. The header should change Connecting → Demo connected. The Demo workspace menu ends the session; Reconnect obtains another session without a form. If no account/API is configured, the app stays navigable and says the demo connection is unavailable. There is no silent fallback account or sample live data.

Presenter configuration is required for the persistent3100preview; temporary integration credentials are not installed into it. Do not use test credentials or point it at another worker's review source without agreement.

## Compatibility and transport

- `npm run generate:api` generates model types, runtime schema snapshot and route inventory from current `contracts/api_models.json`/`api_endpoints.json`. No backend imports at generation time.
- `npm run check:api` detects stale generated output; `npm run contracts` checks the reviewed source hashes. Both run before production builds. Review backend changes before regenerating/adapting consumers and explicitly recording a new baseline.
- JSON Schema2020-12 validation checks requests/responses without coercion/default insertion or unknown-field stripping. Types alone are not runtime validation. Schema validation does not replace backend business invariants, auth or source checks.
- Browser requests use relative `/api/v1`. Frontend route handlers forward allowlisted current routes to the server-configured local origin. They never follow upstream redirects, forward cookies, expose Set-Cookie or accept an origin/graph selector from a browser. Unsupported/repeated query parameters fail closed. Original Host is used to account for Next's internal localhost normalization; forwarded-host headers are ignored.
- Automatic session endpoint accepts no browser credential/body/role selectors, uses the existing backend login and then the browser client validates authenticated `/auth/me` before showing connected. The private password is used only by the server route.
- Requests retain request IDs and validated sanitized error details. Frontend-owned failures use neutral envelopes.401 clears the session;403 does not. Late responses from earlier sessions are discarded. Timeout is bounded; no automatic mutation retry or new idempotency key. RECOVERY_REQUIRED/UNKNOWN requires operator reconciliation with the original key.
- REST stream access is deliberately disabled until F05. No SSE parsing, live activity or fake thinking is implemented.
- Overview/case data binding is F03; full evidence/Canvas views are F04. Higher-authority independent reviewers and department actors are F06 scope. Existing endpoints for those capabilities remain server-authorized; F02 does not implement those action forms.

## Reproducible verification

From frontend: `npm test`, `npm run typecheck`, `npm run build`. Thirty offline tests use explicitly fake fetch responses; these are not DB/agent acceptance.

From Civicly root: `backend/.venv/bin/python frontend/scripts/verify_integration.py`. This explicitly creates a new random graph/profile plus private auth store under frontend/.runtime, starts temporary loopback API and frontend servers, checks current runtime schemas/route parity, and exercises the generated client through the real proxy. It uses actual backend Services/Auth/graph persistence, retained synthetic Department and no worker/MCP/model/memory capability. Only new migration namespaces are targeted, no existing graph reset or lifecycle command. Servers stop in finally; proof graphs/private failed attempts remain for review. Public proof contains no credentials. This is not the official full-readiness startup or complete backend acceptance.

The harness fails if backend source/contracts change during its retention check. Review concurrent changes instead of overwriting them. It installs the existing provider interlock and requires zero blocked/external requests; no live provider is configured. `--browser` is an agent QA option: it temporarily publishes a local origin/finish marker in ignored frontend/.runtime and waits at most55seconds for explicit browser verification.

If connection fails, share the safe message/request reference and F02-results.md. Never send `.env.local`, runtime profiles/auth stores or tokens. Initial connection failures do not automatically retry in a loop; use Reconnect after presenter correction.
