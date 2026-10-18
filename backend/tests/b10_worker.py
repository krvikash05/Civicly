"""TEST ONLY process-restart driver: deterministic fake model, actual MCP + Saver."""
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
from tests.b10_fixtures import ScriptedModel,choose
from tests.b09_fixtures import Clock

async def main():
    path,mode,input_path,output_path=sys.argv[1:];p=load(path);clock=Clock()
    with connect(Settings(_env_file='.env')) as db,active_scope(p):
        repo=GraphRepository(db,p.graph,lease_seconds=30)
        async with brokers(p,path) as tools:
            saved=json.loads(Path(input_path).read_text());thread=saved['thread_id']
            actions=[choose('READ',{'template':'node','id':'D1'},'official::query_graph_readonly'),choose()]
            agent=InvestigationAgent(p,repo,tools,ScriptedModel(actions),saver(p),clock=clock)
            if mode=='create':result=await agent.run(InvestigationState.model_validate(saved),thread_id=thread)
            else:result=await agent.run(thread_id=thread,resume=True)
            Path(output_path).write_text(json.dumps({'mode':'DETERMINISTIC_FAKE_MODEL_REAL_MCP_AND_SAVER','result':result},default=str,indent=2))
if __name__=='__main__':asyncio.run(main())
