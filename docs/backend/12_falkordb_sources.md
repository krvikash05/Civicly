# FalkorDB implementation map — checked official references

References consulted 2026-10-17. Vendor APIs evolve: Codex **must check against the installed versions** and run a minimal proof before committing feature implementations. Linked docs indicate supported concepts; they do not guarantee Civicly's combination has been tested.

| Resource | Official URL | Civicly adoption | Integration proof |
|---|---|---|---|
| FalkorDB base docs | https://docs.falkordb.com/ | property graph, OpenCypher subset, indexing and full-text/vector, Docker and client | local query + migration B01/B02 |
| Core GitHub | https://github.com/FalkorDB/FalkorDB | Docker examples, server behavior, current limitations and integration examples | pinned image + version logs |
| FalkorDB Python client | https://docs.falkordb.com/getting-started/clients | canonical graph read/write repository; parameterized queries | create/read/restart B01 |
| Cypher support | https://docs.falkordb.com/cypher/ | multi-hop, read-only Cypher, aggregation; avoid unsupported Neo4j procedures | real Cypher/EXPLAIN B03/B04 |
| Integrations | https://docs.falkordb.com/integration | official client; optional bulk loader for large seed; REST not required alongside Python driver | seed import B04 |
| GenAI tools | https://docs.falkordb.com/genai-tools | choose LangGraph + MCP + GraphRAG, not every framework | version and smoke tests |
| LangGraph integration | https://docs.falkordb.com/genai-tools/langgraph | `langchain-falkordb[langgraph]` and `FalkorDBSaver` checkpoint | restart workflow B10 |
| Official MCP docs | https://docs.falkordb.com/genai-tools/mcpserver | graph schema discovery and read-only tool call | MCP client actual `tools/list`, `tools/call` B06 |
| MCP configuration | https://docs.falkordb.com/genai-tools/mcpserver/configuration | `MCP_TRANSPORT=http`, `MCP_API_KEY`, `FALKORDB_DEFAULT_READONLY` but **explicit allowlist mandatory** | disabled writes tests B06 |
| MCP server repo | https://github.com/FalkorDB/FalkorDB-MCPServer | official Node server and tool signatures incl `query_graph_readonly` | pin/check version B06 |
| GraphRAG SDK | https://docs.falkordb.com/genai-tools/graphrag-sdk | ingestion/retrieval of simulated org docs, cite exact source | MD+PDF ingest+retrieval B11 |
| GraphRAG detailed docs | https://docs.falkordb.com/graphrag/getting-started.md | `GraphRAG`, `ConnectionConfig`, `ingest`, retrieval; SDK-managed schema | isolated doc graph and citations B11 |
| FalkorDB Browser | https://docs.falkordb.com/browser | developer visual verification of live graph and Cypher | human check B02/B15 |
| FalkorDB Canvas | https://docs.falkordb.com/browser/canvas | future React evidence subgraph explorer fed from API, not browser DB credentials | contract test B17, later frontend |
| GraphRAG reliability | https://docs.falkordb.com/graphrag/reliability-and-grounding.md | abstention and cited source usage; never trust generated procedures without checks | negative evidence/retrieval tests B11 |
| MCP Protocol | https://modelcontextprotocol.io/ | real client/server discovery and tool calling | handshake/schema tests B06/B07 |
| Hackathon rules | https://www.wemakedevs.org/hackathons/falkordb/rules | central graph, allowed dataset, code explainability and disclosure | demo artifacts |

### Official MCP caveat
`FALKORDB_DEFAULT_READONLY=true` changes defaults, but public documentation/repository describes per-query `readOnly` overrides. We must not equate it to privilege separation. Broker must block `query_graph` and graph writes/delete; ideally separate read-only DB credentials and isolated endpoint. Test denial through actual server.

### Graph algorithms caveat
FalkorDB supports Cypher graph traversal; **do not assert** a native PageRank or centrality algorithm exists without verifying a specific function/procedure. Use verified Cypher for connected dependencies and Python deterministic analysis on bounded graph-returned networks for DAG/criticality, preserving graph dependence and provenance.

### GraphRAG caveat
GraphRAG SDK documents its own schema and graph storage. We deliberately isolate documentary index in `civicly_docs`, with canonical IDs linked into the core graph. This is purposeful, not a substitute for central graph reasoning. Document retrieval never directly writes confirmed physical graph edges without review.

### First technology spikes
1. FalkorDB Python query parameterization + read-only and durable volume.
2. Index/unique constraint syntax and asynchronous readiness; point index/time handling.
3. Cypher variable-length bounds/path identity and supported graph algorithms.
4. Official MCP transport/allowlisted tools, tools/list/tools/call, SQL/graph-write denial.
5. FalkorDBSaver with chosen LangGraph version: checkpoint+resume across process restart.
6. GraphRAG SDK markdown and PDF ingestion, extraction schema/citations in isolated graph.
7. Canvas data mapping later with sanitized stable graph subgraph DTO.

Write confirmed versions and compatibility decisions into `decision.md` with a `test_log.md` command. If incompatible, explore updated official adapter rather than silently switching to unrelated DB or omitting functionality.
