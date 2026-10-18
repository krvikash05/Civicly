# F08 Implementation Plan: Integrated Role/Scenario Journeys, Accessibility & Frontend Handoff

## 1. Objectives & Scope
- **Task ID**: `F08`
- **Scope**: Final essential frontend microtask.
  - Deliver integrated scenario journeys covering all 12 seeded municipal scenarios (`S01` to `S12`) across WATERLOGGING, ROAD_DAMAGE, WASTE_ACCUMULATION, and cross-category investigations.
  - Deliver comprehensive municipal role governance context (`ANALYST`, `APPROVER`, `FIELD_LEAD`, `ADMIN`) explaining capabilities, boundaries, and the non-bypassable backend authorization model without a judge sign-in form.
  - Complete accessibility (a11y) and responsive design enhancements (WCAG AA contrast, keyboard navigation, visible focus rings, ARIA landmarks/roles, mobile navigation, touch targets).
  - Provide a complete, self-contained `frontend/docs/HANDOFF.md` documenting architecture, components, API protocol, and verification steps.

---

## 2. Invariants & Guardrails
- **Backend Isolation**: Zero changes to `backend/`, `contracts/`, or database fixtures.
- **FalkorDB Evidence Visibility**: Preserves the core 3-part trace connection (Question asked → Graph evidence returned → Recorded decision).
- **Distinction Retained**: Physical work completion is strictly distinguished from verified civic resolution.
- **Untrusted Sourced Evidence**: Municipal standard operating procedures remain untrusted evidence (`trusted_as_instructions: false`).
- **No Fabricated Data**: Displays real backend data from `GET /api/v1/demo/scenarios`, `GET /api/v1/dashboard/summary`, `GET /api/v1/incidents`, `GET /api/v1/investigations/{id}/*`.

---

## 3. Implementation Phases
1. **Scenario Journey Guide (`frontend/components/scenario-journey-guide.tsx`)**:
   - Quick-access catalog for all 12 scenarios (`S01`–`S12`).
   - Category filtering (`WATERLOGGING`, `ROAD_DAMAGE`, `WASTE_ACCUMULATION`, `CROSS_CATEGORY`).
   - Links directly to registered investigations or incidents with stage context.
2. **Municipal Role Governance Modal (`frontend/components/role-governance-modal.tsx`)**:
   - Interactive role inspector explaining current `OP-ANALYST` session, municipal department (`ENGINEERING`), and the 4 seeded roles with clear authority boundaries.
3. **Shell & Navigation Enhancements (`frontend/components/shell.tsx`, `frontend/app/page.tsx`, `frontend/components/demo-connection.tsx`)**:
   - Integrated Scenario Journey and Role Governance launchers.
   - Refined `ConnectionNotice` for active backend demo session.
4. **Accessibility & Responsive Styling (`frontend/app/globals.css`)**:
   - Mobile navigation header and responsive sidebar toggle.
   - Screen reader utility classes (`.sr-only`), focus visible indicators, and table overflow wrappers.
5. **Unit Tests (`frontend/tests/journeys.test.ts`)**:
   - Validates scenario catalog filtering, role model permissions, and accessibility attributes.
   - Ajv closed-schema compliance for scenario models.
6. **Integration Probe & Handoff Evidence**:
   - Update `integration_probe.ts` for F08 scenario and journey coverage.
   - Run `verify_integration.py` to produce `F08-integration.json`.
   - Write `frontend/docs/HANDOFF.md`.
