# F01 — application shell

2026-10-18. Technically PASS; human review pending. Requirement focus R15/R16; preserve R01–R18. User approved normal application navigation and visible graph evidence; standalone explorer/library/presentation features deferred.

## Scope and choices

Files: frontend app routes/layout/CSS, components/{shell,icons,unavailable,investigation-workspace}.tsx, package.json/package-lock.json, tsconfig.json, generated next-env.d.ts, next.config.ts, .gitignore, README, frontend task/integration docs, baseline and these review artifacts. Root six trackers append only. No backend/contract/dataset/runtime edits by F01. No tests or writes against active backend sources.

Next.js App Router with React/TypeScript; no backend connection or external assets. Node24.21.0/npm12.2.0; installed exact Next16.4.2, React/ReactDOM19.3.1, TypeScript7.0.2, @types/node26.6.5, @types/react19.3.0 and @types/react-dom19.3.0. Separate lockfile; npm install audit reported0 vulnerabilities. Do not claim this is a full security review.

Current contract baseline initially flagged api_models drift during parallel backend ownership work. Reviewed the current schema definitions and route/schema identities:58operations/55paths/182schemas. No API consumer/types exist yet; shell is unaffected. Explicitly recorded the current hash instead of changing backend files. This does not verify runtime compatibility.

Official Canvas documentation read: https://docs.falkordb.com/browser/canvas. Supports standalone web component, React/TypeScript example, data/layout/event APIs. F04 must exercise installed package and backend adapter; F01 does not claim Canvas runtime proof.

## Executed checks

- `npm run build`: PASS production compile, TypeScript, static generation for / and /investigations plus not-found.
- `npm run typecheck`: PASS.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_contracts.py` from frontend:4/4PASS offline guard tests.
- `python3 frontend/scripts/check_contracts.py`: initial drift detected; final PASS after review/explicit baseline recording.
- `backend/.venv/bin/python scripts/validate_blueprint.py`: PASS.
- `backend/.venv/bin/python scripts/validate_handoff.py`: PASS.
- `npm run start`: restricted attempt EPERM; approved loopback retry served127.0.0.1:3100. Production pages exercised through the real browser.
- Real browser: Overview rendered; Waterlogging category opened /investigations?issue=WATERLOGGING with selected filter; Plan & approval section changed panel without advancing backend state; graph explanation expanded; mobile category selection changed URL to ROAD_DAMAGE; navigation returned to Overview. Console error/warning inspection returned none.
- Responsive browser override390x844: both pages inspected; document clientWidth375/scrollWidth375, no document horizontal overflow. Lifecycle navigation intentionally scrolls inside its container. Override restored. Initial capture happened before resize settled; subsequent actual mobile screenshot/DOM inspection confirmed active breakpoint. This is sampled responsive verification, not an exhaustive device/accessibility audit.

Retained tooling issues: default npm metadata lookup ENOTFOUND; approved network install succeeded. One exact-label browser locator matched nothing; native accessible selection succeeded. One stale browser element after navigation was replaced with a fresh state-derived target. No application error hidden.

Live API, login/RBAC, DB/MCP, Canvas rendering, genuine agent, SSE and full case lifecycle: NOT RUN/NOT IMPLEMENTED in F01. Unavailable panels are explicit; no quantitative confidence, fake case statistics or fabricated graph paths.

## Human verification

From frontend: `npm ci` then `npm run dev`; open http://127.0.0.1:3100. Visit Investigations, change the category and switch case sections. Expand the graph explanation. Resize to mobile and check navigation/stacked panels. Counts must remain dashes and graph must say no evidence loaded until later real integration. Share this results file and terminal error if setup fails. Production preview process is stopped after QA; run dev to reopen.

Screenshots: F01-overview.png and F01-investigations.png. Next task F02 — typed client/auth integration, after review. No backend completion claimed.
