# F10 — Scenario catalog overlay correction

Technical PASS; human review pending. Supports R15/R16 presentation while preserving all other requirements.

## Reproduction and cause
The shared `.modal-overlay`, `.modal-card`, header, close-button and footer CSS definitions were absent. Real browser measurement showed the dialog position `static`, left 0, top2725.75px: it rendered below the page, rather than overlaying it. Both scenario and role components use these shared classes.

## Change and scope
Only application source changed: frontend/app/globals.css. Added shared fixed viewport overlay, centered bounded card, backdrop, header/close/footer styles. Catalog remains internally scrollable. Grid minimum is bounded to its container for narrower screens. No component/state logic, scenario activation, backend, auth, data or provider changes. Existing F09 and concurrent changes preserved; changes.patch compares with the task-start preimage.

## Actual verification
- npm --prefix frontend run build — PASS (includes generated API and contract checks).
- npm --prefix frontend run contracts — PASS before and after;59operations/55paths/185schemas.
- make test-spec — both specification validators PASS.
- git diff --check -- frontend/app/globals.css — PASS.
- Real browser/local production build, actual retained catalog:12cards, overlay fixed at x0/y0 across1289x984viewport; card960px wide at x164.5/y59.05, centered; scroll region524px high with881px content. Road Damage filter returned4matching cards, including a cross-category scenario. Close/reopen via toolbar works. Shared roles dialog centered880px wide at x204.5. No new unit tests for reversible CSS-only correction; no fake integration proof.
- Only local frontend process reloaded using its unchanged connection configuration. Backend graph revision remained818. No domain mutation or model request initiated.

## Human verification and limits
Open http://127.0.0.1:3100, click Scenario Journeys from sidebar or Scenarios toolbar, scroll catalog, choose a category, close and reopen. Screenshot scenarios-centered.jpg shows corrected layout. No remote deployment/GitHub push. Narrow-screen grid rule added but mobile viewport not separately exercised. Existing keyboard focus-management behavior was not expanded in this layout correction. Next: human review, then separately publish/deploy approved frontend.
