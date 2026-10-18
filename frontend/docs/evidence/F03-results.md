# F03 — Overview reads, category filters, case lists and selection

2026-10-18. Technical PASS; human review pending. F02 accepted. Primary objectives R01/R16; preserving R01–R18 and explainability R15.

## Implemented

1. **Real API-backed Overview (`app/page.tsx`)**:
   - Four exact backend metrics mapped without distortion: `active_investigations` (excludes completed/cancelled), `pending_approvals` (awaiting operator decision), `completed_work_orders` (work completed, explicitly distinguished from verified resolution), and `verified_work_orders` (orders with verified resolution outcome).
   - Three civic issue categories (Waterlogging, Road damage, Waste accumulation) displaying actual active incident counts (`issue_counts`) and recurrent cluster counts (`recurrence_counts`), with direct navigation links.
   - Metadata bar displaying `as_of` timestamp in IST, `graph_revision`, SIMULATED indicator, and collapsible backend metric definitions and data limitations (`definitions`, `limitations`).
   - Integrated Case Directory and event stream standby notice (confirming SSE delivery is scheduled for F05 without synthetic thinking steps).

2. **Case Directory (`components/case-directory.tsx`)**:
   - Registered demo investigations extracted from scenario catalog (`GET /api/v1/demo/scenarios`), filtering out `NOT_STARTED` scenarios and respecting active category filters.
   - Reported incidents listing (`GET /api/v1/incidents`) with server-supported cursor pagination (First page / Next page), status tags, timestamps, and location IDs.
   - Identification of incidents linked to registered demo investigations vs unlinked incidents (`uniqueCaseForIncident`).
   - Explicit display of list bounds and limitations (`limitations`, `truncated`).

3. **Investigation Workspace & Selection (`components/investigation-workspace.tsx`)**:
   - Deep-linked selection through URL query parameters (`investigation`, `incident`, `issue`), supporting browser back/forward history and direct case navigation.
   - Selected case loading via `loadSelectedCase`:
     - If investigation selected: loads `InvestigationDTO` and all linked incidents, displaying status, agent role, problem cluster, graph revision, and next required action.
     - If standalone incident selected without registered investigation link: displays incident report details with explicit disclaimer notice ("No exposed investigation link is registered for this incident in the demo catalog. Direct investigation listing is not supported by the current API; this is not proof that no investigation exists.").
     - Mismatched selection (wrong incident ID or conflicting issue filter) fails closed with sanitized `CONTRACT_MISMATCH` or `SELECTION_MISMATCH`.
   - In-case lifecycle stage navigation (Report, Investigation, Evidence, Plan & approval, Work, Monitoring & memory); selecting a section updates the active view without advancing backend state.
   - Suspense boundary in `app/investigations/page.tsx` for reliable searchParams consumption in Next.js App Router.

4. **Stale Read & Session Cancellation (`lib/read/latest.ts` & `components/use-read.ts`)**:
   - `LatestRead` abort controller increments version and aborts inflight requests on new queries or filters, ensuring late responses never publish over a new scope.
   - Session transition or logout immediately clears cached read state; no cross-session or stale resource leakage.

## Executed Checks

- `npm test` from `frontend/`: **40 distinct offline tests PASS** (30 transport + 10 cases), 0 fail, 0 skip.
- `npm run check:api`: **PASS** (183 generated model schemas / 58 route contracts current).
- `npm run contracts`: **PASS** (58 operations / 55 paths / 183 schemas match reviewed baseline).
- `npm run typecheck`: **PASS** (`tsc --noEmit`).
- `npm run build`: **PASS** (Next.js production build, TypeScript, static pages and route handlers compiled cleanly).
- Root specification validators (`validate_api.py`, `validate_blueprint.py`, `validate_handoff.py`): **PASS**.
- Real HTTP integration test (`backend/.venv/bin/python frontend/scripts/verify_integration.py`):
  - Fresh isolated profile and random graph in FalkorDB.
  - Fresh private SQLite auth store with generated operator passwords.
  - Isolated FastAPI service and Next.js proxy on dynamic loopback ports.
  - Verified `GET /api/v1/dashboard/summary` (active incidents, issue counts, revision).
  - Verified `GET /api/v1/incidents` with limit and issue filters.
  - Verified `GET /api/v1/incidents/{id}` direct incident read.
  - Verified `GET /api/v1/demo/scenarios` catalog read (12 scenarios).
  - Verified 401 unauthorized, 403 forbidden, 422 invalid query, and token revocation.
  - Output recorded in `frontend/docs/evidence/F03-integration.json`.
  - Zero unexpected provider attempts (`CIVICLY_TEST_NO_LIVE=1` interlock).
  - Backend code and contract hashes verified identical before and after run (`backend_code_contract_retention: true`).

## Retained Corrections

1. **Schema constraints in test fixtures**: Initial test fixtures used arbitrary strings for `expected_hash` and `null` for `subtype`; corrected to match exact schema rules (`^[0-9a-f]{64}$` pattern for sha256 hashes, string subtype).
2. **FalkorDB Incident node schema**: Seed incident creation in integration script originally included `location_id` and enum `severity: 'MEDIUM'`; corrected to match canonical graph registry (omitted `location_id` since location is an edge, and used valid enum `severity: 'HIGH'`).
3. **Socket timeout in integration script**: Adjusted `Settings` socket timeout to 10s to gracefully handle listing large graph catalogs during multi-run verification.

## Limitations & Dependencies

- There is currently no general `GET /investigations` list endpoint in the backend contract. The frontend uses `GET /api/v1/demo/scenarios` registered cases and lists accessible incidents via `GET /api/v1/incidents`.
- Standalone incident selection explicitly informs the user that direct investigation listing is not exposed by this API, without falsely implying no investigation exists.
- Graph evidence visualization remains reserved for F04 (official `@falkordb/canvas` integration).
- Real-time SSE streaming remains reserved for F05.

## Next Task

**F04** — Investigation Studio with real hypotheses, evidence/citations and bounded graph; official `@falkordb/canvas` compatibility spike and recorded-decision/path linkage.
