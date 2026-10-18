"""TEST ONLY fresh-process simulated provider with real MCP and checkpoints."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime
from app.active import load,active_scope
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.agents.models import InvestigationState,Budget
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.agents.mcp import brokers
from tests.b09_fixtures import Clock
from tests.b10or2_fixtures import SimulatedHTTP,model
async def main():
 path,phase,src,out=sys.argv[1:];p=load(path);data=json.loads(Path(src).read_text());s=InvestigationState.model_validate(data['state']);clock=Clock();clock.value=datetime.fromisoformat(data['clock'].replace('Z','+00:00'))
 with connect(Settings(_env_file='.env')) as db,active_scope(p):
  r=GraphRepository(db,p.graph,lease_seconds=30)
  async with brokers(p,path) as tools:
   cap='.12' if data['kind']=='dollar' and phase=='create' else '.50';http=SimulatedHTTP(clock);m=model(s,Path(src).parent,http,cap)
   agent=InvestigationAgent(p,r,tools,m,saver(p),clock=clock)
   kwargs={'budget_increase':{**s.budget.model_dump(),'max_tokens':400000},'authorized':True,'operator_reason':'Explicit simulated token allocation upgrade; preserve cumulative receipt accounting'} if phase=='resume' and data['kind']=='token' else {}
   result=await agent.run(s if phase=='create' else None,thread_id=s.thread_id,resume=phase=='resume',**kwargs)
   with m.ledger.db() as sql:rows=[dict(row) for row in sql.execute('SELECT * FROM requests ORDER BY created')]
   Path(out).write_text(json.dumps({'result':result,'summary':m.ledger.summary(s.investigation_id),'requests':rows,'receipts':http.receipts},default=str))
if __name__=='__main__':asyncio.run(main())
