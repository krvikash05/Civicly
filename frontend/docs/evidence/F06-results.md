# F06 Technical Verification & Results: Resolution Plans, Task DAG, Approvals & Work Orders

## Summary
Microtask **F06** is complete and verified:
- **In-case remediation plans and approvals**: Connected Stage 3 ("Plan & approval") backed by real backend data from `GET /api/v1/investigations/{id}/plans` and `POST /api/v1/plans/{id}/submit-approval`.
- **Topological Task DAG layout**: Implemented `computeTaskDag` in `frontend/lib/read/plans.ts`, organizing tasks into sequential dependency tiers (roots, intermediate remediation, post-work verifications) with cycle detection and fallback protection.
- **Municipal role separation & governance**: Enforced strict role controls where the connected analyst (`OP-ANALYST` / `ANALYST`) can draft and submit plans with client-generated `Idempotency-Key` headers and exact SHA-256 plan hashes, but cannot self-approve municipal intervention. An independent `APPROVER` role is required for approval decisions per safety invariants R13 and R15.
- **Dispatched work orders & field inspections**: Connected Stage 4 ("Work & inspections") backed by `GET /api/v1/work-orders` and `GET /api/v1/inspections/{id}`. Displays field inspection evidence links directly opening `EvidenceDetailModal`.
- **Work Completion vs Verified Resolution**: Implemented a mandatory operational callout distinguishing field task completion from long-term verified civic resolution (which requires subsequent post-intervention monitoring under comparable rainfall/traffic/collection conditions).

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
  - Total: **60 tests passed** (0 failing, 0 skipped, 0 cancelled).
  - Tests verify:
    - DAG topological tier sequencing (linear, diamond, cycle detection, task binding properties).
    - Status badge styles and hash formatters.
    - Ajv closed-schema validation of `PlanDTO` and `WorkOrderDTO` against backend `contracts/api_models.json`.
    - SSE client and transport assertions.

### 3. Production Compilation
- **Command**: `npm run build`
- **Result**:
  - Compiled successfully with Turbopack in 585ms.
  - Zero TypeScript compiler errors across all routes and components.

### 4. Real HTTP Isolated Integration Probe
- **Command**: `backend/.venv/bin/python frontend/scripts/verify_integration.py`
- **Result**:
  - `PASS`: Isolated backend FastAPI + Next.js proxy booted on fresh ephemeral ports with a disposable FalkorDB graph and clean auth store.
  - Verified 15 real API operations including:
    - `GET /api/v1/investigations/{id}/plans`
    - `GET /api/v1/work-orders`
    - `GET /api/v1/events/stream` (SSE stream & cursor recovery)
    - Zero provider leaks, zero credential leaks.
  - Recorded in `frontend/docs/evidence/F06-integration.json`.

---

## Live Verification Details
- **Preview URL**: `http://127.0.0.1:3100/investigations?investigation=INV-B09-8b006fb97aa2b908fc69addcf7ecd037`
- **Stage 3 ("Plan & approval")**:
  - Displays plan `PLAN-B12-da6d426cc7a42982a3dac6c8a76af2a6` (v1).
  - Content Hash: `1b04b300…a3a74286`.
  - Expected Hash: `64c961c2…764c5375`.
  - Status: `PENDING_APPROVAL`.
  - Task DAG: Shows `TASK-CLEAR-DRAIN-101` for target `DRAIN-101` assigned to `DEPT-DRAIN`, with procedure citation `D019_drain_blockage_clearance.md` and safety review prerequisites.
  - Role Governance: Prominently indicates awaiting independent municipal approver sign-off (`APPROVER`), preventing self-approval by `OP-ANALYST`.
- **Stage 4 ("Work & inspections")**:
  - Displays operational distinction callout: Work Completion is NOT Verified Resolution.
  - Confirms backend creation guard: work orders are created only after exact plan approval.
