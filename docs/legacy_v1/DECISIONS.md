# Architecture decision records

## Finalized design choices
- **ADR-001**: Name is Civicly, not CauseRoot.
- **ADR-002**: All three civic issues and their shared infrastructure/operational dependencies supported; no category-specific isolated graphs.
- **ADR-003**: One canonical `civicly_knowledge` graph in FalkorDB; checkpointer storage managed separately by its adapter.
- **ADR-004**: Python FastAPI/Pydantic + LangGraph runtime; TypeScript/React/Next.js frontend.
- **ADR-005**: MCP is a real runtime tool boundary: official read-only graph MCP and typed Civicly domain MCP. Codex's own tools do not count as app MCP.
- **ADR-006**: Agent-led investigation and coordination; human authorization for consequential actions; operational demo explicitly simulated when external systems are absent.
- **ADR-007**: Cases, facts, hypotheses, assessments, and outcomes are distinguishable, versioned and auditable.
- **ADR-008**: `HypothesisAssessment` owns evidence support/contradiction edges; subtype labels are `DrainSegment`, `DrainInlet`, etc.
- **ADR-009**: Case resolution is separate from work-order completion, with monitoring and reopening.
- **ADR-010**: Generated OpenAPI and registries are authoritative; no silent schema additions.
- **ADR-011**: Begin with single worker, idempotent events; concurrency expansion requires atomic claim strategy.

## Technical spikes that require execution-time verification
1. Confirm supported versions and exact async/sync behavior for `FalkorDBSaver`, official Python client and graph query parameterization; integration test checkpoint persistence after process restart.
2. Test the actual FalkorDB constraint/index syntax, geospatial point support and Cypher traversal; check supported semantics in the version installed.
3. Confirm official MCP service read-only security hardening; the service's default-readonly flag may be overrideable, so rely on tool exposure / database privileges / infrastructure isolation as well.
4. Confirm `@falkordb/canvas` web-component integration within chosen Next.js hydration setup; test bounded subgraph mapping and no direct DB exposure.
5. Validate durable graph event-outbox operation and edge updating under chosen FalkorDB version. Keep one worker until concurrency control proved.
6. Pin compatible package versions, image digests and lockfiles only **after** successful runtime smoke tests; avoid fabricated version claims.

## Change-control rule
If a technical spike forces a library substitution, preserve product invariants and capabilities. Record alternative, why it differs, contract changes, and passing regression tests. Switching away from FalkorDB's central reasoning role or removing runtime MCP is not an acceptable substitution.
