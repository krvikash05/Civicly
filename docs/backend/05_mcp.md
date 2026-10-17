# Runtime MCP integration contract (not Codex's tools)

## Servers, clients and network boundary
- **Official FalkorDB MCP server**: documented `@falkordb/mcpserver`, Node-based stdio or HTTP. For local Docker use Streamable HTTP behind internal Docker network, API key plus read-only backend credentials when available; environment `FALKORDB_DEFAULT_READONLY=true`. Nevertheless `query_graph` may permit per-call readOnly override; **present only allowlisted** `list_graphs`, `get_graph_schema`, `get_node_schema`, `get_relationship_schema`, `query_graph_readonly` to the model and reject other tool calls at broker. The dedicated `query_graph_readonly` executes read-only query. Restrict graph name and query length/complexity; parameterize values.
- **Custom Civicly Python MCP server**: built using official Python MCP SDK/verified version, same protected private network. Typed civic read tools and proposal/write tools. Domain state-changing tools call service layer with caller actor context, never trust LLM-supplied identity or approval.
- **Runtime broker**: authenticated MCP sessions; calls `tools/list` and `tools/call` (check actual SDK APIs), accepts JSON Schema tool description, maps validation/authorization, applies <= N tool calls/budget and concurrent requests constraints, emits graph-backed ToolExecution trace. For demo, no public MCP URL without auth.

## Prevent unrestricted Cypher
The model may call the official graph server only through strict broker and query templates. Best choice: use custom Civicly `trace_infrastructure_dependencies` and `find_related_incidents` for decision-grade queries; retain `query_graph_readonly` for demonstrable schema-aware exploration under a read-only allowlist of query templates. Never pass arbitrary LLM-crafted Cypher directly to a privileged `GRAPH.QUERY`. Official server default read-only is NOT sufficient access policy. Tests must demonstrate `query_graph` and deletion/write tools absent and rejected even if called by name.

## Civicly tool inventory
Names, permissions, JSON request and response shapes remain defined in `contracts/mcp_tools.json` (18 custom tools). All must have actual server handlers, integration tests and trace coverage:
`find_related_incidents`, `trace_infrastructure_dependencies`, `get_maintenance_history`, `retrieve_external_evidence`, `retrieve_case_memory`, `get_organizational_procedures`, `record_hypothesis_assessment`, `propose_inspection`, `propose_resolution_plan`, `request_plan_approval`, `create_work_order`, `get_work_order_status`, `record_intervention_outcome`.

Five additional evidence-specific tools are now registered in `contracts/mcp_tools.json`: `get_pickup_execution_history`, `get_road_condition_history`, `get_source_document_excerpt`, `get_decision_evidence_path`, and `get_monitoring_status`. Use these for demonstrably useful evidence retrieval, not mandatory invocation in every case. `retrieve_case_memory` covers episodic/semantic/procedural retrieval categories. `get_organizational_procedures` uses GraphRAG retrieval with source citations/versions.

## Contract fields for every tool result
```
{
  status: "SUCCESS|PARTIAL|UNAVAILABLE|ERROR|PERMISSION_DENIED",
  trace_id: "...", investigation_id: "...",
  data: <tool-specific validated JSON>, source_evidence_ids: ["..."],
  graph_revision: <application revision>, simulated: true|false,
  truncated: true|false, error: {code, message, retryable}|null
}
```
The current v1 tool registry may include narrower `status` enum; expand registry and handlers together, preserve backward compatibility until all tests updated.

## Tool trace and explanation contract
Persist timestamp, agent role, tool name, input schema version, redacted normalized input hash, output summary, source IDs, graph path IDs, duration, error code, tool inventory revision, rationale summary, simulator flag. These fields power frontend agent activity timeline and diagnostics; no internal private reasoning transcript. All tools have explicit timeouts and result limits.

## MCP proof tests
- Integration uses actual client/server over HTTP/stdio; `tools/list` returns relevant tools, `tools/call` reads canonical graph and returns matching evidence.
- Change graph relation in isolated test graph -> agent tool choice/next action changes in a meaningful way.
- Injection/prompted tool spoofing cannot override allowlists; arbitrary write query refused; invalid arguments rejected.
- Unavailable MCP -> explicit degraded result and paused investigation; no fake success.
- Write tool stale version / duplicate Idempotency-Key -> no duplicate WorkOrder or outcome.

## Relevant official references
https://docs.falkordb.com/genai-tools/mcpserver ; https://docs.falkordb.com/genai-tools/mcpserver/configuration ; https://github.com/FalkorDB/FalkorDB-MCPServer ; https://modelcontextprotocol.io/ . Confirm exact version and transport with smoke test B06.
