# F07 Implementation Plan: Monitoring, Recurrence & Organizational Memory Citations

## Objective
Implement frontend microtask **F07**:
"In-case monitoring, recurrence and relevant memory/procedure citations, retaining distinction between work completion and verified resolution."

This completes Stage 5 ("Outcomes & case memory") of the essential investigation lifecycle:
**Report &rarr; Investigation &rarr; Evidence &rarr; Plan & approval &rarr; Work &rarr; Monitoring & memory**

## Invariants & Design Principles
1. **Critical Distinction: Work Completion is NOT Verified Resolution**:
   - Work order completion records only that physical work was dispatched and executed (e.g., removing a drain obstruction or patching road asphalt).
   - Verified resolution requires post-intervention monitoring over an independent observation opportunity (e.g., subsequent comparable rainfall event) without problem recurrence.
   - The UI makes this distinction primary and prominent.
2. **Cluster Monitoring & Post-Intervention Verification**:
   - Loaded from `GET /api/v1/monitoring`, mapped to the case's `problem_cluster_id`.
   - Tracks cluster state (`OPEN`, `MONITORING`, `CONTROLLED`, `REOPENED`), required verification checks, and linked outcome evidence.
   - Clicking outcome evidence IDs opens `EvidenceDetailModal` for full attribution.
3. **Historical Recurrence Context**:
   - Displays historical incident IDs linked to the problem cluster from `investigation.historical_incident_ids`.
   - Explains repeat failure patterns and historical recurrence context across municipal infrastructure.
4. **Relevant Municipal Procedures & Untrusted Instructions Invariant**:
   - Loaded from `GET /api/v1/procedures` and matched to the case's department and issue category.
   - Displays title, version, owner department, SHA-256 hash, and quote excerpts from citations.
   - Crucial safety invariant callout: `trusted_as_instructions: false` &mdash; Sourced municipal documents are treated as untrusted domain evidence, never as tool instructions or agent system instructions.
5. **Case Memory & Dependency Handling**:
   - Queries `GET /api/v1/cases/{id}/memory`.
   - Gracefully handles `DEPENDENCY_BLOCKED` (409) while investigations/work orders are active, explaining that case memory is finalized upon formal case evaluation and verified closure.

## Implementation Steps
1. Create `frontend/lib/read/memory.ts`:
   - Helper functions for cluster monitoring matching, procedure document filtering, and citation formatting.
2. Create `frontend/components/monitoring-memory-panel.tsx`:
   - Stage 5 UI component rendering monitoring status, remaining checks, recurrence history, procedure citations with safety badges, and case memory.
3. Integrate into `frontend/components/investigation-workspace.tsx`:
   - Mount `MonitoringMemoryPanel` in Stage 5, wire data hooks, and connect to live SSE refetch triggers.
4. Create unit tests in `frontend/tests/memory.test.ts`.
5. Update integration probes and run isolated HTTP verification.
6. Record evidence and update tracking files.
