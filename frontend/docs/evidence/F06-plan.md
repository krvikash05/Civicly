# F06 Implementation Plan: Plans, Task DAG, Approvals, Inspections & Work Orders

## Objective
Implement frontend microtask **F06**:
"In-case inspections/plans/approvals/work: exact versions, idempotency/recovery, DAG, authorized progress and actual role controls."

This supports the essential lifecycle:
**Report &rarr; Investigation &rarr; Evidence &rarr; Plan & approval &rarr; Work &rarr; Monitoring & memory**
by making Stage 3 ("Plan & approval") and Stage 4 ("Work & inspections") fully interactive, backed by real backend data, exact cryptographic hashes, Directed Acyclic Graph (DAG) task structures, and strict municipal role separation.

## Invariants & Design Principles
1. **Truthful Exact Hashes & Versions**:
   - Plans are identified by `plan_id`, integer `version`, SHA-256 `content_hash`, and `expected_hash`.
   - Never forge or invent plan versions or hashes.
2. **Visual Task DAG & Topological Ordering**:
   - Each task has `id`, `action_type`, `department_id`, `target_ids`, `depends_on_task_ids`, `prerequisites`, `remediation`, `procedure_citation`, `expected_outcome`, `verification_criteria`, `risks`, and `uncertainties`.
   - Compute in-degrees and topological dependency levels (tiers) to present a clean visual DAG showing sequential and parallel execution paths.
   - Detect circular dependencies if present.
3. **Role Separation & Municipal Authorization**:
   - The demo session is `OP-ANALYST` (Role: `ANALYST`).
   - `ANALYST` can draft and submit plans for approval (`POST /api/v1/plans/{id}/submit-approval`).
   - Only `APPROVER` (e.g. `OP-APPROVER` / municipal department executive) has legal authority to approve or reject plans (`POST /api/v1/approvals/{id}/decision`).
   - The UI explicitly highlights this separation: an Analyst cannot approve their own plan, preventing bypass of municipal checks (R13, R15).
4. **Idempotency & Non-Duplication**:
   - All state mutations require client-generated UUID `Idempotency-Key` headers.
   - On 409 Conflict / Recovery Required, preserve error details without uncoordinated automatic retries.
5. **Work Completion vs Verified Resolution**:
   - Work orders represent physical execution tasks assigned to department operators.
   - Stage 4 explicitly emphasizes: **Work completion is NOT verified resolution**.
   - Physical clearance of a drain or patching of a pothole does not prove the civic defect has been resolved until independent post-intervention monitoring (Stage 5 / F07) confirms no recurrence under relevant conditions (e.g., rainfall).
6. **Inspections & Field Evidence Linkage**:
   - Field inspections link directly to collected evidence IDs.
   - Clicking an evidence ID opens the authoritative evidence modal (`EvidenceDetailModal`) for complete chain-of-custody inspection.

## Implementation Steps
1. Create `frontend/lib/read/plans.ts`:
   - Topological sort and tier layout calculation for Task DAGs.
   - Plan validation and hash verification helpers.
   - Work order and inspection data helpers.
2. Create `frontend/components/plan-approval-panel.tsx`:
   - Plan metadata and version/hash verification headers.
   - Interactive DAG visualizer displaying tiers, dependencies, and expandable task details (remediation conditions, prerequisites, citations, risks).
   - Plan basis summary (hypotheses addressed vs unaddressed).
   - Approval workflow and role boundary explanation.
3. Create `frontend/components/work-orders-panel.tsx`:
   - Field inspections listing with status and linked evidence.
   - Work orders listing with status badges, blocker alerts, and assigned departments/operators.
   - Informative notice explaining that work orders are created only after exact plan approval.
   - Clear distinction banner between physical work completion and long-term verified resolution.
4. Integrate into `frontend/components/investigation-workspace.tsx`:
   - Wire `plansRead` and `workOrdersRead` with live SSE refetching.
   - Mount `PlanApprovalPanel` in Stage 3 and `WorkOrdersPanel` in Stage 4.
5. Add unit tests in `frontend/tests/plans.test.ts`.
6. Update integration probe `frontend/scripts/integration_probe.ts` and verify with `frontend/scripts/verify_integration.py`.
