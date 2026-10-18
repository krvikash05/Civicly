"""Explicit real provider + real MCP acceptance probe; separately invoked, billable."""
import asyncio,json,sys
from pathlib import Path
from app.active import active_scope,DEFAULT_PROFILE,load
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.agents.provider import Gemini,ProviderSettings
from app.agents.policy import Permit
from app.services.complaints import ComplaintService
from app.services.evidence import EvidenceService
from app.graph.schema import utc_now
from tests.b10_fixtures import create,state
from tests.b09_fixtures import ANALYST
from tests.b08_fixtures import payload

async def main():
    import os
    if len(sys.argv)<2 or sys.argv[1]!='create':raise RuntimeError('Use the explicit per-investigation app.agents --live CLI; fixture drivers are disabled by default')
    mode=sys.argv[1];out=Path(sys.argv[2]);profile_path=DEFAULT_PROFILE
    with connect(Settings(_env_file='.env')) as db:
        if mode=='create':
            p,repo,clock,receipt,inv=create(db,profile_path)
            value={'graph':p.graph,'checkpoint_graph':p.checkpoints,'cases':{'WATERLOGGING':{'receipt':receipt.model_dump(mode='json'),'investigation':inv}}}
            with active_scope(p):
                for issue in ['ROAD_DAMAGE','WASTE_ACCUMULATION']:
                    intake=ComplaintService(repo,clock=clock).intake(payload(issue,ref='B10-LIVE-'+issue))
                    id=EvidenceService(repo,clock=clock).execute({'operation':'open','request_id':'B10-open-'+issue,'incident_ids':[intake.incident_id],'cluster_id':intake.cluster_id},ANALYST).entity_id
                    value['cases'][issue]={'receipt':intake.model_dump(mode='json'),'investigation':id}
            out.write_text(json.dumps(value,indent=2));return
        p=load(profile_path);repo=GraphRepository(db,p.graph,lease_seconds=30)
        fixtures=json.loads(out.read_text());issue=sys.argv[3];case=fixtures['cases'][issue]
        with active_scope(p):
            async with brokers(p,profile_path) as tools:
                model=None
                # Test uses a fixed, explicit synthetic service clock after authored reports.
                from tests.b09_fixtures import Clock
                clock=Clock()
                if mode=='resume':
                    model=Gemini(ProviderSettings(_env_file='.env'),permit=Permit.explicit_live(approved=True,investigation_id=case['investigation'],thread_id=case['thread']))
                    agent=InvestigationAgent(p,repo,tools,model,saver(p),clock=clock)
                    result=await agent.run(thread_id=case['thread'],resume=True)
                else:
                    from app.services.complaints.models import IntakeResult
                    receipt=IntakeResult.model_validate_json(json.dumps(case['receipt']));initial=state(p,repo,tools,clock,receipt,case['investigation'],issue)
                    case['thread']=initial.thread_id;out.write_text(json.dumps(fixtures,indent=2))
                    model=Gemini(ProviderSettings(_env_file='.env'),permit=Permit.explicit_live(approved=True,investigation_id=case['investigation'],thread_id=initial.thread_id))
                    agent=InvestigationAgent(p,repo,tools,model,saver(p),clock=clock)
                    result=await agent.run(initial,thread_id=initial.thread_id)
                proof={'mode':'LIVE_GEMINI_REAL_MCP_REAL_FALKORDBSAVER','issue':issue,'result':result,'provider_usage':model.last_usage,'catalog_hash':tools.inventory_hash,'transport':tools.traces}
                Path('docs/evidence/B10-live-'+issue+('-resume' if mode=='resume' else '')+'.json').write_text(json.dumps(proof,default=str,indent=2))
                print(json.dumps({'issue':issue,'mode':proof['mode'],'errors':result['data']['errors'],'pause_reason':result['data']['pause_reason'],'decisions':len(result['data']['decisions']),'executions':len(result['data']['executions']),'hypotheses':len(result['data']['hypotheses'])}))

if __name__=='__main__':asyncio.run(main())
