# Engineering uncertainties the specification deliberately exposes (not missing objectives)

The specification fixes project goals, data model, behavior, trust boundaries, state transitions, API expectations, and test gates. It does **not** claim a backend has been built or that any installed version of FalkorDB/SDK works with every example. These are runtime verification tasks, not excuses to omit features.

1. Exact installed FalkorDB Cypher parser, index/constraint syntax, `GRAPH.RO_QUERY` and parameterization, point behavior and graph persistence must be confirmed in B01–B05.
2. Official MCP server's version, transport, schema and permissions must be confirmed in B06; environment read-only defaults alone cannot substitute broker allowlist.
3. LangGraph `FalkorDBSaver` dependency compatibility and persistence must be proven in B10 with process restart.
4. GraphRAG SDK PDF/MD ingestion, schema isolation, citation mapping and deterministic source resolution must be proven in B11.
5. Domain-event atomicity/idempotency under concurrent updates must be tested; use durable single worker and recovery, never claim exactly-once without proof.
6. Scenario-specific dated inspection/repair events will be produced as stage fixtures by B19 and evaluated against hidden ground truth; the supplied 838-node expansion is a meaningful city substrate, not a fully executed simulation or agent result.
7. Live LLM behavior requires configured provider credentials and real test runs; fake model is acceptable only for unit tests.
8. Future Next.js FalkorDB Canvas hydration compatibility is tested during frontend phase; the backend DTO design is fixed now.

Any technical correction must be logged in `decision.md`, linked to a test, reflected in contracts/docs. No requirement may be silently removed, and no unsupported conclusion about municipal reality may be asserted.
