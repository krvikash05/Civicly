"""Actual domain MCP server on one private B10 profile, source read-only."""
import asyncio,sys
from falkordb import FalkorDB
from mcp.server.stdio import stdio_server
from app.active import load,active_scope
from app.mcp.civicly.runtime import connections
from app.mcp.civicly.server import build
from app.mcp.civicly.service import CivicReadService
from app.mcp.civicly.storage import TraceStore

async def main(path):
    p=load(path)
    with active_scope(p),connections() as (_,writer,name):
        source=FalkorDB(host='127.0.0.1',port=6379,username=p.read_user,password=p.read_password.get_secret_value(),socket_timeout=3,socket_connect_timeout=2)
        try:
            server=build(CivicReadService(source,source_graph=p.graph),TraceStore(writer,name),expected_graph=p.graph)
            async with stdio_server() as streams:await server.run(*streams,server.create_initialization_options())
        finally:source.connection.close();source.connection.connection_pool.disconnect()

if __name__=='__main__':asyncio.run(main(sys.argv[1]))
