"""TEST ONLY fresh Python process with mock HTTP and real MCP/FalkorDBSaver."""
import asyncio,json,sys
from pathlib import Path
from app.active import load,active_scope
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.agents.models import InvestigationState
from tests.b09_fixtures import Clock
from tests.b10or_http import ReactiveHTTP,ReadPause
from tests.integration.test_agent_accounting import model
async def main():
    path,phase,src,out=sys.argv[1:];p=load(path);s=InvestigationState.model_validate_json(Path(src).read_text());clock=Clock()
    with connect(Settings(_env_file='.env')) as db,active_scope(p):
        r=GraphRepository(db,p.graph,lease_seconds=30)
        async with brokers(p,path) as tools:
            a=InvestigationAgent(p,r,tools,model(s,Path(src).parent,ReactiveHTTP(ReadPause())),saver(p),clock=clock)
            result=await a.run(s if phase=='create' else None,thread_id=s.thread_id,resume=phase!='create')
            Path(out).write_text(json.dumps(result,default=str))
if __name__=='__main__':asyncio.run(main())
