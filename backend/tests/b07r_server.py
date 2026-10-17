"""TEST ONLY: real SDK stdio with disposable fixture source, never runtime config.

Fixed production Context still describes the approved city capability. This harness
substitutes the source internally solely to exercise history edge cases unavailable
in the retained city. Its outputs are labeled fixture proofs, not city snapshots.
"""
import asyncio
import sys
from mcp.server.stdio import stdio_server
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.analysis.engine import GraphAnalysis
from app.graph.targets import is_allowed_graph_target
from app.mcp.civicly.runtime import connections
from app.mcp.civicly.service import CivicReadService
from app.mcp.civicly.server import build
from app.mcp.civicly.storage import TraceStore


async def main():
    name=sys.argv[1]
    assert name.startswith('civicly_b07_test_') and is_allowed_graph_target(name)
    with connect(Settings(_env_file='.env')) as source, connections() as (_,writer,trace_graph):
        service=CivicReadService.__new__(CivicReadService)
        service.repo=GraphRepository(source,name)
        service.analysis=GraphAnalysis(service.repo)
        server=build(service,TraceStore(writer,trace_graph))
        async with stdio_server() as streams:
            await server.run(*streams,server.create_initialization_options())


if __name__=='__main__':asyncio.run(main())
