# F29 — homepage issue-card order

Reordered the homepage Recurring problems cards to Waste accumulation → Road damage → Waterlogging. Source:frontend/app/page.tsx only. DOM and keyboard order match visual order; category labels/icons/count bindings and investigation filters remain attached to each card.

Verification:npm --prefix frontend run build PASS including API/contracts/types. Contract guard before change PASS. Actual local browser shows the requested order and the correct category-specific URLs. No new unit test or full backend rerun for this simple array reorder. Local frontend rebuilt/reloaded, backend unchanged, no domain/provider writes. AWS not updated.

Tracking:frontend/docs/tasks.md and six root trackers appended. Humanverify:refresh http://127.0.0.1:3100 and check Recurring problems left-to-right Waste accumulation, Road damage, Waterlogging. R15/R16;all18requirements preserved. Next:humanreviewthenrequesteddeployment/nextUItask;STOP.
