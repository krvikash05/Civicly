# B17-R exact query coverage

Unknown/irrelevant/repeated parameters return sanitized422. No hypothesis date filtering semantics invented.

| GET /api/v1 route | Accepted query parameters |
|---|---|
| /api/v1/auth/me | none |
| /api/v1/dashboard/summary | issue, status, department_id, after, before |
| /api/v1/complaints | limit, cursor, issue, status, department_id, after, before |
| /api/v1/complaints/{id} | none |
| /api/v1/incidents | limit, cursor, issue, status, department_id, after, before |
| /api/v1/incidents/{id} | none |
| /api/v1/problem-clusters | limit, cursor, issue, status, department_id, after, before |
| /api/v1/problem-clusters/{id} | none |
| /api/v1/investigations/{id} | none |
| /api/v1/investigations/{id}/trace | limit, cursor, status, after, before |
| /api/v1/investigations/{id}/hypotheses | limit, cursor, status |
| /api/v1/investigations/{id}/graph | depth, include_candidates |
| /api/v1/evidence/{id} | none |
| /api/v1/inspections/{id} | none |
| /api/v1/plans/{id} | none |
| /api/v1/approvals | limit, cursor, issue, status, department_id, after, before |
| /api/v1/work-orders | limit, cursor, issue, status, department_id, after, before |
| /api/v1/work-orders/{id} | none |
| /api/v1/departments | limit, cursor, issue, status, department_id, after, before |
| /api/v1/procedures | limit, cursor |
| /api/v1/documents/{id} | none |
| /api/v1/cases/{id}/memory | limit, cursor |
| /api/v1/map/features | limit, cursor, issue, status, department_id, after, before, investigation_id |
| /api/v1/assets/{id} | none |
| /api/v1/assets/{id}/neighbors | depth, include_candidates |
| /api/v1/monitoring | limit, cursor |
| /api/v1/problem-clusters/{id}/outcomes | limit, cursor |
| /api/v1/events/stream | cursor, investigation_id |
| /api/v1/health/live | none |
| /api/v1/health/ready | none |
| /api/v1/approvals/{id} | none |
| /api/v1/investigations/{id}/plans | limit, cursor |
| /api/v1/hypotheses/{id} | none |
