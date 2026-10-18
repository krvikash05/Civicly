"""Explicit live controlled graph perturbation. No prerecorded choices or hidden answers."""
import asyncio,json
from pathlib import Path
from app.active import load,active_scope,DEFAULT_PROFILE
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.services.complaints import ComplaintService
from app.services.evidence import EvidenceService
from app.agents.provider import Gemini,ProviderSettings
from app.agents.policy import Permit
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.agents.mcp import brokers
from tests.b10_fixtures import state
from tests.b09_fixtures import Clock,ANALYST
from tests.b08_fixtures import payload
from tests.schema_examples import edge,NOW

async def main():
    # Historical batch cannot authorize paid cases; use the invocation-bound CLI.
    raise RuntimeError('Use the explicit per-investigation app.agents --live CLI; fixture drivers are disabled by default')
    p=load();clock=Clock();fixture_path=Path('docs/evidence/B10-live-fixture.json');fixture=json.loads(fixture_path.read_text());proof={}
    with connect(Settings(_env_file='.env')) as db,active_scope(p):
        r=GraphRepository(db,p.graph,lease_seconds=30)
        if r._edge_optional('B10-LIVE-UNDERLIES'):raise ValueError('Probe already run; prior evidence retained')
        relation=r.create_relationship('UNDERLIES','P1','R1',{**edge('B10-LIVE-UNDERLIES'),'valid_from':NOW,'association_status':'VERIFIED','source_evidence_id':'EV'})
        for variant in ['VERIFIED','DISCONNECTED']:
            if variant=='DISCONNECTED':
                old=r.get_relationship(relation.id)
                r.update_relationship(relation.id,{'valid_to':'2026-10-18T11:59:00Z'},expected_hash=old.content_hash)
            receipt=ComplaintService(r,clock=clock).intake(payload('ROAD_DAMAGE',ref='B10-live-topology-'+variant,asset_ids=['P1','R1'],event_reference='B10-live-'+variant))
            inv=EvidenceService(r,clock=clock).execute({'operation':'open','request_id':'B10-topology-'+variant,'incident_ids':[receipt.incident_id],'cluster_id':receipt.cluster_id},ANALYST).entity_id
            async with brokers(p,DEFAULT_PROFILE) as tools:
                initial=state(p,r,tools,clock,receipt,inv,'ROAD_DAMAGE');initial.asset_ids=['P1','R1']
                fixture['cases']['ROAD_TOPOLOGY_'+variant]={'receipt':receipt.model_dump(mode='json'),'investigation':inv,'thread':initial.thread_id}
                fixture_path.write_text(json.dumps(fixture,indent=2))
                model=Gemini(ProviderSettings(_env_file='.env'),permit=Permit.explicit_live(approved=True,investigation_id=inv,thread_id=initial.thread_id));agent=InvestigationAgent(p,r,tools,model,saver(p),clock=clock)
                result=await agent.run(initial,thread_id=initial.thread_id)
                proof[variant]={'mode':'LIVE_GEMINI_REAL_MCP_REAL_SAVER','result':result,'actual_provider_usage':model.last_usage,'transport':tools.traces}
                Path('docs/evidence/B10-live-topology.json').write_text(json.dumps(proof,default=str,indent=2))
                print(json.dumps({'variant':variant,'decisions':len(result['data']['decisions']),'executions':len(result['data']['executions']),'hypotheses':len(result['data']['hypotheses']),'pause_reason':result['data']['pause_reason'],'errors':result['data']['errors'],'next':result['data']['selection']}),flush=True)

if __name__=='__main__':asyncio.run(main())
