# B01 backend foundation

Implemented: validated configuration, official FalkorDB connection lifecycle,
foundation CLI health, and real database/Browser/persistence integration tests.
Domain services, migrations, MCP, agents, memory, GraphRAG, API routes and frontend
remain future microtasks. All 18 requirements remain binding.

From the repository root, with Python 3.12 and Docker Desktop running:

```sh
make setup
make up
make health
make test-unit
make test-graph
make test-persistence
make test-spec
```

`make setup` installs uv 0.13.1 inside `backend/.venv`, then synchronizes the exact
`backend/uv.lock`. No global packages. `make up` creates an ignored, mode-0600
`.env` once, including random Browser session/encryption secrets, and waits for
Redis, the graph command and Browser HTTP. Existing `.env` is never overwritten.
Keep it across recreation; it is local credential material and must not be shared.

CLI success exits 0. An unavailable database exits 1 (`GRAPH_UNAVAILABLE`);
invalid configuration exits 2 (`CONFIG_INVALID`). Raw exceptions/passwords are
not printed. Run `backend/.venv/bin/civicly health --env-file /path/to/local.env`
to select another settings file; process environment takes precedence.

A fresh database reports `status: ok`, `scope: backend_foundation`,
`graph_state: uninitialized`, `graph_read: null`: server/module are available,
but B02 has not initialized `civicly_knowledge`. Health does not create graphs.
For an existing graph, it executes a static parameterized `GRAPH.RO_QUERY` and
reports `graph_read: true`. This is not full agent-system readiness.

## Local developer Browser

Open [FalkorDB Browser](http://127.0.0.1:3000), enter host `127.0.0.1`, port `6379`,
and leave username/password blank for this loopback-only development setup.
The Browser backend shares the database container; its connection port is always
the internal `6379`, even if `FALKORDB_PORT` changes the host-side published port.
The graph client is accessible at `127.0.0.1:6379` by default.

An actual B01 verification run left graph `civicly_b01_runtime`, one synthetic
`B01Probe` node, for review. Select it and run:

```cypher
MATCH (n:B01Probe {id:'B01-PERSISTENCE'})
RETURN n.id, n.source_kind, n.task LIMIT 1
```

Expected row: `B01-PERSISTENCE`, `SYNTHETIC`, `B01`. This isolated test graph is not
the canonical domain schema, and no supplied civic seed was imported. On a fresh
machine it appears only after the explicit inspection-node creation command in
`test_log.md`; the automated tests create and clean their own random test graphs.

## Storage and test boundaries

Compose pins the tested official 6.0.2 image by digest, including Browser 2.6.1.
`civicly_falkordb_data` mounts `/var/lib/falkordb/data`; AOF is enabled with
`appendfsync always`, plus `save 60 1` snapshots. `civicly_browser_data` mounts
`/var/lib/falkordb/browser/.data` (verified from the installed image). Only
loopback ports are published. This local developer database has no Redis password;
authenticated application roles and MCP restrictions remain later tasks.

`make test-persistence` opts into restarting and force-recreating only this
project's `falkordb` container. It verifies container identity changes, fresh
parameterized reads, Redis persistence settings, Browser HTTP and a Browser-volume
marker before/after. Run it when no other Civicly work is active; it briefly
interrupts connections. It never deletes volumes or canonical graph data.

`make down` retains both volumes. `docker compose down -v` destroys them; it is
not part of verification. Graceful restart/recreation does not prove crash
consistency, exactly-once events, migrations or checkpoint recovery.

Integration tests fail when required services are unavailable. The disruptive
persistence test is explicitly skipped without `--run-persistence`. Unit tests
include a temporary FastAPI/Pydantic/httpx compatibility app; it is not a Civicly
API or live agent. Later agent/MCP/GraphRAG acceptance is unverified.

If verification fails, share `test_log.md`, `blockers.md`, the failing test output
and `docker compose logs --tail 100`. Do not share `.env` or full Compose config
output, which can contain generated secrets.
