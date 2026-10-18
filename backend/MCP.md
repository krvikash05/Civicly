# B06 official FalkorDB MCP runtime

B05 accepted; B06 only. This is a Python client of the actual official Node server,
not a Codex connector and not the B07 custom domain server. No model/agent selection,
GraphRAG, operations, API or frontend is implemented here. All18 requirements remain.

## Reproduce locally

Repository root, Python3.12.1 isolated environment and existing pinned FalkorDB6.0.2
Compose/Browser. Preserve volumes and retained city/B01/B05 graphs. Tested
Node24.21.0/npm12.2.0; project engines require the tested Node24/npm12 family.

```sh
UV_CACHE_DIR=.uv-cache backend/.venv/bin/uv sync --project backend --frozen
make up
make mcp-setup
make mcp-configure
make mcp-proof
make test-mcp
backend/.venv/bin/python -m pytest backend/tests -v -s --run-persistence
make test-spec
```

`mcp-setup` uses npm ci against committed integrity hashes; no npx/latest resolution
at runtime. Official package1.3.0 declares Node>=18/npm>=8; verified Python SDK2.3.0,
mcp-types2.3.0 and negotiated legacy initialization protocol2025-11-25. Full Python
and Node transitive versions/hashes are in backend/uv.lock and
backend/mcp_runtime/package-lock.json. Existing direct B01 package pins retained.

`configure` is a trusted local administrator command, not an agent tool. It creates
or reuses ignored `.runtime/mcp-credentials.json` (0600, directory0700) and provisions
only `civicly_mcp_b06` via ACL SETUSER reset. One exact graph key:
`civicly_b04_test_a84beda80da64aacbc367a9399e07a97`. Allowed Redis commands PING,
INFO (required by actual Node client Sentinel detection), GRAPH.RO_QUERY and CLIENT
SETINFO. No GRAPH.QUERY/DELETE/LIST, CONFIG, ACL or other graph keys. Password hashes
are sent to ACL SETUSER; credentials never appear in command-line arguments or
operator output. Default local developer access is unchanged and remains privileged.

ACL state is not persisted in the current database image's AOF. Run `make mcp-configure`
after database restart/recreation; the generated credential stays local. No migration,
volume, dataset or canonical graph modification is needed. Missing/wrong credentials
fail initialization; the upstream connection retry can continue until client timeout,
after which SDK closes/kills the child. Do not share `.runtime`, `.env` or keys.

## Transport and authorization

Selected transport: official supported **stdio**, with a broker-owned Node child and
private parent pipes. No MCP TCP/HTTP endpoint or public port is opened; no bearer key
is applicable to this transport. The documented Docker HTTP topology is deliberately
deferred for this local monolith. HTTP bearer authentication has NOT been tested and
is NOT claimed. Switching requires authenticated private-network tests and a new
recorded decision. OS user/process ownership is the transport boundary; no isolation
from arbitrary privileged code running as the same user is claimed.

The child starts in a new empty temporary working directory so upstream dotenv cannot
read repository.env; only explicit DB account variables and SDK's OS environment
basics are inherited. NODE_ENV=production/ENABLE_FILE_LOGGING=false prevent upstream
file logs; its logging notifications are discarded because they may contain raw
queries/errors. BOTH FALKORDB_DEFAULT_READONLY and FALKORDB_STRICT_READONLY are true.
Release1.3.0 strict mode rejects general-query readOnly=false and delete_graph;
dedicated readonly uses GRAPH.RO_QUERY. DB ACL separately blocks write commands and
other graph keys. Neither strict/default flags alone are the broker policy.

| Official tools/list inventory | Broker availability | Restriction |
|---|---|---|
| query_graph_readonly | Yes | fixed named templates; no caller Cypher/params/readOnly |
| get_graph_schema | Yes | one graph; topology sample100; public registry labels/types |
| get_node_schema | Yes | registry node labels; sample1–100 |
| get_relationship_schema | Yes | registry relation types; sample1–100 |
| query_graph | No | arbitrary query/per-call override |
| delete_graph | No | mutation/admin |
| list_graphs | No | unrelated graph inventory leakage; DB command also denied |

Exact tool names, input schemas and observed hashes are in official_mcp.json and the
operator proof. Seven expected signatures are checked on actual tools/list, rejecting
duplicate/new/missing/spoofed inventories. Agent-facing `tools()` returns safe broker
Request schemas, never arbitrary-query vendor input or raw session methods. No
resource/prompt/connection-string/credential/raw-session interface is exposed. Future
agent adapters must call only `ReadBroker.call`; constructing runtime clients is a
trusted application capability. The same-process Python module is not an OS sandbox.

Only the explicitly accepted retained B04 city is authorized. Repository's broader
B02–B25 disposable naming policy does not authorize any graph to this MCP broker.
Canonical empty graph, B01 probes, B05 clone/source, docs/checkpoint/evaluator graphs
and all arbitrary names are denied. Runtime modules do not read scenario catalogs,
expected answers, source documents, hidden truth or delayed reveals. Template reads
only CivicEntity/domain edges; no audit/owner/credential payload is exposed. Revision
bookkeeping uses a fixed internal template, returning only revision/pending/READY.

## Queries, result limits and semantics

Public requests use the Request model (strict, extra=forbid) and never accept query
text or caller params. Dynamic ID/scope/as_of values are separately parameterized.

```python
async with open_broker(traces) as broker:
    print(broker.tools())  # safe broker request schemas after actual tools/list
    result = await broker.call({
        "tool": "query_graph_readonly", "template": "node", "id": "DRAIN-D12"
    })
```

`node`: one current-state domain record by ID; full public properties and labels
strictly validated against registryv3. No historical node reconstruction claim.
`drainage_edges`: one directed DRAINS_TO edge from selected asset, scoped and
created/as_of + half-open validity predicates. Limit101 gives100 rows plus truncation
lookahead; unknown validity is open/unknown. Stable endpoint/relationship IDs, typed
labels, recorded status/source/evidence/date properties retained and validated. These
are raw facts, including CANDIDATE/REPORTED when present, **not decision-grade verified
causal paths**. No candidate promotion. Use accepted B05 analysis through later B07
custom tools for filtered proof/evidence reasoning; no B05 semantic replacement.

Schema tools are bounded samples and may be incomplete. Storage-only labels are
filtered deliberately; unknown domain labels/properties are rejected. `search_limited`
is always true; absence within a bounded query is not global disconnection proof.

Each public read first and last calls official query_graph_readonly for actual READY
application repo_revision/pending state. Pending/revision change fails closed; no
retry quietly changes snapshots. Upstream metadata `Graph version` is not Civicly
application revision. Revision protection assumes repository-mediated writes;
privileged raw mutations may not advance it, as in the accepted B03/B05 boundary. Calls serialized per broker;32 actual wire tool calls/session
(default, configurable3–64) include internal revision reads. Client call timeout4s
(configurable0.01–10); timeouts/transport/malformed output invalidate session, requiring
exit and a fresh owned context. JSON result limit262144bytes checked after transport
receipt; not a network streaming memory cap. Templates are bounded but upstream query
tool has **no query timeout argument**; client timeout/cancellation is not claimed to
interrupt database execution. No arbitrary expensive Cypher accepted.

## Traces and errors

Process-local sanitized trace list records actual initialize/discovery/server/version,
protocol/tool-schema/inventory SHA256, argument hash, withheld-value summary,
UTC start/end/latency, received versus validated row counts, outcome/denial code and
application revision when verifiably observed. It never copies server error strings,
raw arguments, passwords or model rationale. selection_rationale=null with operator/
application origin because no agent exists. B07/B17 must still implement common domain
envelope/graph-backed ToolExecution persistence; DEC-004 stays open.

Representative actual calls/responses/trace rows are in
`docs/evidence/B06-runtime-proof.json`; operator diagnostics contain vendor schemas
for review only. Raw server TOOL_ERROR is distinguished from broker DENIED_TOOL,
DENIED_GRAPH, INVALID_ARGUMENTS, INVALID_OUTPUT, TIMEOUT, TRANSPORT_FAILURE,
SESSION_UNAVAILABLE, CALL_BUDGET, GRAPH_WRITE_PENDING and GRAPH_REVISION_CHANGED.
No error becomes empty success; no automatic tool replay after a transport failure.
SDK shutdown closes stdin, waits and terminates owned process tree with bounded waits.

## Evidence boundaries

The proof retrieves actual DRAIN-D12 and D12→D18 CANDIDATE with stable properties,
compares both to independent official Python-client queries, and checks revision2104.
Tests separately prove live CREATE/SET/DELETE refusal via official readonly tool,
general query/delete strict-mode refusal, ACL/admin/graph-list/key denial, malformed
arguments, missing/wrong DB auth, kill/restart, real SIGSTOP timeout/reconnect, cleanup,
serialization and bounded calls. Malformed **outputs**, schema/property/revision
injection use clearly labeled mocked unit tests. A separate integration fault test
corrupts a result locally AFTER an actual official MCP read and verifies rejection/
reconnection; this is not an upstream defect. No fabricated official response is
reported as integration success. HTTP auth is not applicable; no live LLM test.
Full regression preserves B01/B02/B03/B03-R/B04/B05 tests and original retained data.

Official sources verified against installed release:
- https://github.com/FalkorDB/FalkorDB-MCPServer
- https://docs.falkordb.com/genai-tools/mcpserver/configuration
- https://github.com/modelcontextprotocol/python-sdk
- https://py.sdk.modelcontextprotocol.io/
- Installed official dist/index.js, dist/mcp/tools.js, dist/config/index.js,
  dist/services/falkordb.service.js and Node falkordb Sentinel detection source.

## B07 integration and credential incident
B06 accepted. B07 rotated the reported exposed MCP password, verified old denial/new
read-only access and preserved this official client/server/allowlist. See
[CIVICLY_MCP.md](CIVICLY_MCP.md) for separate namespaces/custom12 READ tools and shared
graph-backed traces. B06 process-local trace evidence below is historical; future
runtime callers use the B07 namespace router for controlled durable observations.
Git-ignore checks do not sanitize full-folder archives; ignored.runtime credentials
must be excluded explicitly from any future export. No B07 ZIP is generated.


## B10 compatible integration update (partial agent acceptance)
The retained-city default remains unchanged. An explicit private B10 ActiveProfile now supplies one narrowly authorized disposable source graph to B08/B09 readers, official MCP and the actual Civicly MCP production bootstrap. Model arguments cannot select a graph or Cypher. B07 source references can decode that B10 UUID, but broker and server still require exact trusted graph equality; separate source-read, trace-write and SDK-checkpoint accounts remain enforced. Optional host rationale summaries contain actual short public model summaries; old null defaults are preserved. Actual B10 source IDs/revisions, CLI and integration proof are documented in `AGENTS_RUNTIME.md` and `docs/evidence/B10-*`. No final canonical-city activation, B11 organizational retrieval, operational workflow or frontend claim.
