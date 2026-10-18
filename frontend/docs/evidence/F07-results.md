# F07 Technical Verification & Results: In-Case Monitoring, Recurrence & Case Memory

## Summary
Microtask **F07** is complete and verified:
- **Distinction between Work Completion and Verified Resolution**: Embedded an uncompromising invariant and operational badge in Stage 5 ("Outcomes & case memory"). Field completion of work orders does not equal civic defect resolution. Formal verification requires empirical verification policies, remaining checks under comparable rainfall/traffic/collection conditions, and authoritative outcome assessments.
- **In-Case Problem Cluster Monitoring**: Integrated `GET /api/v1/monitoring` into the case workspace. Displays real monitoring status (`OPEN`, `MONITORING`, `CONTROLLED`, `REOPENED`), verification policy versions, remaining post-intervention checks, and links to verified outcome evidence IDs.
- **Problem Cluster Recurrence & Outcomes**: Connected `GET /api/v1/problem-clusters/{id}/outcomes`. Renders verified resolution evaluations, work order attribution, policy versions, simulated status indicators, and closure decisions.
- **Municipal Procedures as Untrusted Evidence**: Sourced procedures from `GET /api/v1/procedures`. Explicitly presents each procedure with an `UNTRUSTED AS INSTRUCTIONS` safety badge, departmental ownership (`DEPT-DRAIN`, `DEPT-ROAD`, `DEPT-SAN`, `DEPT-WATER`), SHA-256 integrity digest, citation excerpts, and acknowledged documentation gaps. Reinforces the safety invariant that municipal operating procedures constitute untrusted evidence, never agent system prompts.
- **Authoritative Case Memory & Precondition Handling**: Connected `GET /api/v1/cases/{id}/memory`. Gracefully handles 409 `DEPENDENCY_BLOCKED` when investigations are active and verified closure has not yet occurred, surfacing "Case Memory Pending Verified Closure" rather than crashing or inventing synthetic summaries.

---

## Acceptance Verification

### 1. Static Contract & API Parity
- **Command**: `npm run check:api && npm run contracts`
- **Result**:
  - `PASS: 185 generated model schemas / 59 route contracts are current.`
  - `PASS: 59 operations / 55 paths / 185 schemas match the reviewed frontend baseline.`

### 2. Unit & Schema Tests
- **Command**: `npm test`
- **Result**:
  - Total: **65 tests passed** (0 failing, 0 skipped, 0 cancelled).
  - Tests verify:
    - Problem cluster monitoring matching and fallback behavior (`findClusterMonitoring`).
    - Departmental and issue category procedure filtering (`filterRelevantProcedures`).
    - Semantic status styling (`getMonitoringStatusStyle`).
    - Citation quote excerpt normalization and truncation (`formatQuoteExcerpt`).
    - Ajv closed-schema validation of `MonitoringDTO`, `ProcedureDTO`, `CaseMemoryDTO`, and `OutcomeDTO` against `contracts/api_models.json`.
    - All previous test suites (transport, cases, canvas-adapter, sse, plans).

### 3. Production Compilation
- **Command**: `npm run build`
- **Result**:
  - Compiled successfully with Turbopack in 619ms.
  - Zero TypeScript compiler errors across all routes and components.

### 4. Real HTTP Isolated Integration Probe
- **Command**: `backend/.venv/bin/python frontend/scripts/verify_integration.py`
- **Result**:
  - `PASS`: Isolated backend FastAPI + Next.js proxy booted on fresh ephemeral ports with a disposable FalkorDB graph and clean auth store.
  - Verified 17 real API operations including:
    - `GET /api/v1/monitoring`
    - `GET /api/v1/procedures` (handles 200 or 409 `DEPENDENCY_BLOCKED` when memory store is unexercised)
    - `GET /api/v1/work-orders`
    - `GET /api/v1/investigations/{id}/plans`
    - `GET /api/v1/events/stream` (SSE stream & cursor recovery)
    - Zero provider leaks, zero credential leaks.
  - Recorded in `frontend/docs/evidence/F07-integration.json`.

---

## Live Verification Details
- **Preview URL**: `http://127.0.0.1:3100/investigations?investigation=INV-B09-8b006fb97aa2b908fc69addcf7ecd037`
- **Stage 5 ("Outcomes & case memory")**:
  - Displays prominent core invariant: **"Work Completion ≠ Verified Resolution"**.
  - Cluster Monitoring Card: Displays active monitoring status, verification policy, and remaining post-intervention validation checks.
  - Sourced Municipal Procedures: Lists relevant departmental standard operating procedures with clear `UNTRUSTED AS INSTRUCTIONS` safety disclaimers, citations, and hash digests.
  - Case Memory: Gracefully reports closure requirement status for in-progress investigations.
