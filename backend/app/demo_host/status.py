"""Safe presenter readback through the same public API used by the frontend."""
import httpx
from app.api.__main__ import configured_app
from app.agents.spending import Ledger
from app.agents.checkpoints import saver
from app.services.operations.auth import Auth
from cli.private import read_json
from pathlib import Path

async def status(config,profile,repo):
 credentials=read_json(Path(config.auth_store).parent/'presenter-credentials.json',private=True)
 app=configured_app(config.profile,config.auth_store,config.memory_profile)
 async with app.router.lifespan_context(app):
  token=app.state.services.auth.login('OP-ANALYST',credentials['OP-ANALYST'])
  try:
   async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://local',headers={'Authorization':'Bearer '+token}) as c:
    async def get(path):
     response=await c.get('/api/v1'+path)
     return {'http_status':response.status_code,**response.json()}
    cases=[]
    for case in config.cases:
     saved=saver(profile).get_tuple({'configurable':{'thread_id':case.thread_id}})
     state=saved.checkpoint['channel_values']['data'] if saved else None
     inspections=[await get('/inspections/'+id) for id in (state.get('pending_inspections',[]) if state else [])]
     evidence_ids=sorted({id for row in inspections for id in row.get('data',{}).get('evidence_ids',[])})
     cases.append({**case.model_dump(),'checkpoint_id':saved.config['configurable']['checkpoint_id'] if saved else None,'runtime':{k:state.get(k) for k in ['phase','pause_reason','iterations','tool_calls','tokens','errors','pending_inspections','current_plan_id']} if state else None,'investigation':await get('/investigations/'+case.investigation_id),'trace':await get('/investigations/'+case.investigation_id+'/trace'),'hypotheses':await get('/investigations/'+case.investigation_id+'/hypotheses'),'graph':await get('/investigations/'+case.investigation_id+'/graph?depth=4&include_candidates=true'),'inspections':inspections,'inspection_evidence':[await get('/evidence/'+id) for id in evidence_ids],'plan':await get('/plans/'+state['current_plan_id']) if state and state.get('current_plan_id') else None,'accounting':Ledger().summary(case.investigation_id)})
    return {'mode':'PERSISTED_PUBLIC_READBACK','source_graph':profile.graph,'dashboard':await get('/dashboard/summary'),'cases':cases}
  finally:app.state.services.auth.logout(token)
