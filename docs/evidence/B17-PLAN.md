# B17 pre-implementation boundary — DEC-062

B16/R accepted. R04/R05/R07–R17 read-side support, all R01–R18 preserved; B10 genuine acceptance remains OPEN. B17 only, no frontend/B18/B19/provider.

| Route | DTO | Data/authorization |
|---|---|---|
| dashboard/summary | DashboardDTO | authorized current incidents/clusters/approvals/orders, defined counts |
| investigations/{id}/trace | TraceDTO | exact source/thread persisted decisions, validated broker traces, readonly Saver |
| investigations/{id}/hypotheses | Page[HypothesisDTO] | existing validated assessments/provenance |
| investigations/{id}/graph | GraphSubgraphDTO | fixed bounded temporal neighborhood, stable canonical IDs |
| map/features | MapDTO | actual Location coordinates and scoped incident/asset/case associations |
| assets/{id} | AssetDTO | typed labels, ownership/location/provenance |
| assets/{id}/neighbors | GraphSubgraphDTO | same bounded authorized graph projector |
| events/stream | SSEEvent | existing B15 registration cursor, replay/filter/re-auth, no ack/discovery |

Touched: backend/app/api/{models,coverage,application}.py; services/http/{reads,service,views,activity,stream}.py; events/sources.py; API/event contracts; scripts/validate_api.py; new focused unit/integration tests; backend/API.md, frontend readiness/API docs, six trackers, B17 evidence.

Decisions: no migrations/storage redesign. Snapshot consistency via before/after canonical revision; lists stable ID ordering with explicit intervening-write reservation, closed issue/status/department/date filters. Finite 500 candidate scans fail closed on overflow; graph <=120 nodes/200 edges/depth1..5 and explicit bounded-negative/truncation. No raw node properties, journals, arguments or model reasoning. Actual public Selection.summary only, exact source/thread validated; scripted mode distinct from genuine model. Trace/source adapter publishes only actual persisted facts through existing B15 INFO registration, never fabricates attempts/actions. Cursor is nonnegative decimal source-local registration sequence, header/query equality required if both supplied; future/unsupported rejected, no retention deletion currently so expired cursor unsupported unless persisted gap detected. SSE advances transport cursor through filtered rows; control cursor frames carry no hidden event data, heartbeat comments no IDs; bearer header only, per-poll auth/scope, bounded connection duration/poll/batch, cancellation read-only. Browser uses fetch with Authorization.

Exact planned tests: backend/.venv/bin/python -m pytest backend/tests/unit/test_frontend_views.py backend/tests/integration/test_frontend_runtime.py -q (provider guard + fresh B17 request log); make test-spec once final. Tests cover all eight routes, typed evidence/source/citations, real graph/mutation lifecycle, actual MCP/Saver scripted tool and decision, filtered pages/counts, localhost SSE replay/later discovery/reconnect/revocation/expiry/disconnect. No full API/earlier suites/lifecycle/live. Human verifies B17 journey IDs and trace/event cursors from retained evidence, then refetches resources via authenticated docs/stream. STOP for review.
