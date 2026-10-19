# Civicly frontend

Independent frontend workspace inside Civicly. Parallel development authorized by the human on 2026-10-18, overriding the former B-END prerequisite for frontend work only. Backend acceptance, safety and live-provider gates remain binding.

F01 provides a local Next.js/React/TypeScript shell with Overview and Investigations pages. Case sections cover report, investigation, evidence, plan/approval, work and monitoring/memory. The graph evidence panel is reserved for actual API results in F04; it has no fabricated graph. F02 adds automatic demo sessions and a typed REST client/proxy. Judges do not sign in. Case data binding and live updates remain upcoming. F03 is next.

## Run the local frontend

From the `frontend/` folder:

```sh
npm ci
npm run dev
```

Open http://127.0.0.1:3100. The frontend binds to loopback and uses port 3100, leaving backend services and FalkorDB Browser port 3000 alone. F02 automatically attempts a demo connection; without presenter configuration it shows unavailable. See [demo connection setup](docs/API_CONNECTION.md). Stop with Ctrl+C.

```sh
npm run build
npm run typecheck
```

Use Node 22+; the recorded smoke test used Node 24.21.0. Dependencies are exact-pinned with a separate package-lock.json. No external font or image service is needed. Local Next.js setup follows https://nextjs.org/docs/app/getting-started/installation. No Sites hosting or publication was requested.

See [F02 verification](docs/evidence/F02-results.md) and [F01 verification](docs/evidence/F01-results.md) and saved screenshots for the actual checks and limits. Each later task is separately reviewed.

Run from the Civicly root:

```sh
python3 frontend/scripts/check_contracts.py
```

This reads current machine contracts and compares SHA-256 fingerprints against the reviewed baseline. It does not import backend code, connect to a service, mutate contracts or generate backend state. Contract changes intentionally fail the check, including additive changes; review the frontend impact, update affected code/types/tests, then explicitly record a new baseline:

```sh
python3 frontend/scripts/check_contracts.py --record
```

Recording a fingerprint is not a runtime integration test or proof of UI compatibility. Current generated `contracts/api_models.json` and `contracts/api_endpoints.json` take precedence over historical OpenAPI evidence; compare against fresh `/openapi.json` on an authorized review instance before integrating.

See [integration agreement](docs/integration.md). Frontend source, future package manifest/lockfile, configuration, tests and build output stay under this folder. Backend keeps its own dependencies and processes. Do not reset shared graphs, reconfigure Compose, edit backend contracts or run scenario mutations as part of frontend development.
