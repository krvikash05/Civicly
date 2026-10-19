# F28 — completed work links open reports

Changed Work completed popup actions from View work to exact requested View Report. Completed-order URLs now select section=report for the same investigation. Verified outcomes still opens Monitoring & memory; pending plans/active-case links retain their existing destinations.

Source: frontend/components/metric-records.tsx and frontend/lib/read/dashboard.ts. Existing 26 workflow checks PASS, zero failures/skips; production build/API/contracts/types PASS. Actual local browser confirmed all six completed-order rows use View Report and section=report, then clicked the original road row and opened Stage1 Reports & recurrence. No new redundant tests or full backend rerun for this link/copy change.

Local production frontend rebuilt/reloaded; backend unchanged. AWS not updated. No provider calls, approval or domain mutations. App data and retained traces preserved. R15/R16; all18requirements preserved.

Human verification:refresh http://127.0.0.1:3100 → Work completed → View Report; confirm the selected case opens 01 Report. Screenshot popup-browser.png. Next:human review, then requested deployment or next UI task. Stop after F28.
