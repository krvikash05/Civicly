# Official technical references (verified 2026-10-16)

Consult these during implementation and pin working dependencies after smoke tests:

- FalkorDB docs / Python client usage: https://docs.falkordb.com/
- FalkorDB integrations: https://docs.falkordb.com/integration
- FalkorDB GenAI integrations: https://docs.falkordb.com/genai-tools/
- LangGraph + `FalkorDBSaver` (`langchain-falkordb[langgraph]`): https://docs.falkordb.com/genai-tools/langgraph
- Official FalkorDB MCP server docs: https://docs.falkordb.com/genai-tools/mcpserver
- Official FalkorDB MCP GitHub (stdio / streamable HTTP / query_graph_readonly): https://github.com/FalkorDB/FalkorDB-MCPServer
- FalkorDB Browser: https://docs.falkordb.com/browser
- FalkorDB Canvas React/TS usage: https://docs.falkordb.com/browser/canvas
- FalkorDB main repository: https://github.com/FalkorDB/FalkorDB
- MCP documentation and spec: https://modelcontextprotocol.io/

Important: documented existence of an integration does **not** establish that a particular combination of versions has been exercised for Civicly. Tests must verify versions, security settings, migrations and API contracts.
