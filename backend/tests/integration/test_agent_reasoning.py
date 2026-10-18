"""Evidence perturbations with explicitly reactive fake model; actual B05/B09/MCP/Saver."""
import asyncio,json
from pathlib import Path
import pytest
from app.active import active_scope
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.agents.models import Selection
from app.services.evidence.policies import POLICIES
from tests.b10_fixtures import create,state,choose,ScriptedModel
from tests.b09_fixtures import Fixture,report
from tests.schema_examples import edge,NOW

pytestmark=pytest.mark.integration

class EvidenceReactiveFake:
    mode='DETERMINISTIC_REACTIVE_FAKE_MODEL'
    async def choose(self,c,remaining):
        s=c['state'];hs=c['hypotheses']
        if s['refresh_required'] or not s['observations']:
            return Selection.model_validate(choose('READ',{'template':'node','id':s['incident_ids'][0]},'official::query_graph_readonly')),0
        if len(hs)<2:
            cause=['BLOCKAGE','CAPACITY_DEFICIT'][len(hs)];rule=POLICIES['WATERLOGGING'][cause]
            args={'cause_code':cause,'asset_ids':['D1'],'statement':'Competing synthetic '+cause,'mechanism':'Requires discriminating field test','confirming_codes':rule['confirming'],'falsifying_codes':rule['falsifying']}
            return Selection.model_validate(choose('PROPOSE',args)),0
        latest=hs[0]['assessments'][-1] if hs[0]['assessments'] else None
        if latest is None or (s['wakes'] and __import__('app.graph.schema',fromlist=['timestamp']).timestamp(latest['assessed_at'])<__import__('app.graph.schema',fromlist=['timestamp']).timestamp(s['as_of'])):
            return Selection.model_validate(choose('ASSESS',{'hypothesis_id':hs[0]['id']})),0
        target='D1'
        inspection_type='CAPACITY_TEST' if latest['assessment']=='CONTRADICTED' else 'BLOCKAGE_INSPECTION'
        return Selection.model_validate(choose('INSPECT',{'asset_ids':[target],'department_id':'DEP','inspection_type':inspection_type})),0


def test_contradiction_changes_actual_b09_assessment_and_next_inspection(db,tmp_path):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path)
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                initial=state(p,r,tools,clock,receipt,inv);agent=InvestigationAgent(p,r,tools,EvidenceReactiveFake(),saver(p),clock=clock)
                first=await agent.run(initial,thread_id=initial.thread_id)
                assert len(first['data']['hypotheses'])==2
                # Authored reviewed evidence through the accepted full B09 inspection lifecycle.
                fixture=Fixture(r,clock,{'WATERLOGGING':receipt},p.graph,{})
                report(fixture,inv,ref='B10-clear-drain',codes=['DRAIN_CLEAR'],assets=['D1'])
                clock.advance()
                resumed=await InvestigationAgent(p,r,tools,EvidenceReactiveFake(),saver(p),clock=clock).run(thread_id=initial.thread_id,resume=True)
                a=first['data']['pending_inspections'][-1];b=resumed['data']['pending_inspections'][-1]
                first_assets={row[0] for row in r._read('MATCH (:Inspection {id:$id})-[:INSPECTS]->(a) RETURN a.id',{'id':a})}
                next_assets={row[0] for row in r._read('MATCH (:Inspection {id:$id})-[:INSPECTS]->(a) RETURN a.id',{'id':b})}
                Path('/tmp/civicly-b10-contradiction-debug.json').write_text(json.dumps({'first':first,'resumed':resumed},default=str,indent=2))
                assert first_assets==next_assets=={'D1'}
                assert r.get_node(a).properties['inspection_type']=='BLOCKAGE_INSPECTION'
                assert r.get_node(b).properties['inspection_type']=='CAPACITY_TEST'
                states=r._read('MATCH (:Hypothesis {id:$id})-[:HAS_ASSESSMENT]->(a) RETURN a.assessment',{'id':resumed['data']['hypotheses'][0]})
                assert {row[0] for row in states}=={'INCONCLUSIVE','CONTRADICTED'}
                Path('/tmp/civicly-b10-contradiction-proof.json').write_text(json.dumps({'mode':'REACTIVE_FAKE_MODEL_REAL_DOMAIN','first':first,'resumed':resumed,'before_target':sorted(first_assets),'after_target':sorted(next_assets)},default=str,indent=2))
    try:asyncio.run(run())
    finally:
        for name in [p.graph,p.checkpoints]:
            if name in db.list_graphs():db.select_graph(name).delete()
        db.connection.execute_command('ACL','DELUSER',p.read_user,p.checkpoint_user)


def test_planner_is_nonbinding_no_operational_nodes(db,tmp_path):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path)
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                initial=state(p,r,tools,clock,receipt,inv);actions=[]
                actions.append(choose('READ',{'template':'node','id':'D1'},'official::query_graph_readonly'))
                for cause in ['BLOCKAGE','CAPACITY_DEFICIT']:
                    rule=POLICIES['WATERLOGGING'][cause]
                    actions.append(choose('PROPOSE',{'cause_code':cause,'asset_ids':['D1'],'statement':'Synthetic '+cause,'mechanism':'Requires field confirmation','confirming_codes':rule['confirming'],'falsifying_codes':rule['falsifying']}))
                actions.append(choose('RECOMMEND',{'next_action':'Request human review of discriminating inspection','target_ids':['D1'],'basis_evidence_ids':[],'limitations':['No causal finding; inspection required']}))
                result=await InvestigationAgent(p,r,tools,ScriptedModel(actions),saver(p),clock=clock).run(initial,thread_id=initial.thread_id)
                assert set(['Supervisor','Investigator','RootCauseAnalyst','ResolutionPlanner','Coordinator'])<=set(result['data']['nodes'])
                assert result['data']['recommendation']['binding'] is False
                assert r._read('MATCH (n) WHERE n:Plan OR n:WorkOrder OR n:ActionTask RETURN count(n)')[0][0]==0
    try:asyncio.run(run())
    finally:
        for name in [p.graph,p.checkpoints]:
            if name in db.list_graphs():db.select_graph(name).delete()
        db.connection.execute_command('ACL','DELUSER',p.read_user,p.checkpoint_user)

class TopologyReactiveFake:
    mode='DETERMINISTIC_TOPOLOGY_REACTIVE_FAKE_MODEL'
    async def choose(self,c,remaining):
        s=c['state']
        if not s['observations']:
            return Selection.model_validate(choose('READ',{'investigation_id':s['investigation_id'],'asset_id':'P1','network':'TYPED_DEPENDENCIES','direction':'DOWNSTREAM','max_hops':3,'as_of':s['as_of'],'include_candidates':False},'civicly::trace_infrastructure_dependencies')),0
        edges=s['observations'][0].get('data',{}).get('edges',[])
        target='P1' if any(e['kind']=='UNDERLIES' and e['properties'].get('association_status')=='VERIFIED' for e in edges) else 'R1'
        if target=='P1' and not s['hypotheses']:
            rule=POLICIES['ROAD_DAMAGE']['UTILITY_LEAK']
            return Selection.model_validate(choose('PROPOSE',{'cause_code':'UTILITY_LEAK','asset_ids':['P1'],'statement':'Possible utility explanation, never established by topology alone','mechanism':'Leak could damage underlying road; pressure and infiltration observations required','confirming_codes':rule['confirming'],'falsifying_codes':rule['falsifying'],'topology':{'source_id':'P1','target_id':'R1','operation':'dependencies','max_hops':3}})),0
        return Selection.model_validate(choose('INSPECT',{'asset_ids':[target],'department_id':'DEP','inspection_type':'UTILITY_PRESSURE' if target=='P1' else 'ROAD_STRUCTURE'})),0

@pytest.mark.parametrize('topology,expected',[('VERIFIED','P1'),('CANDIDATE','R1'),('DISCONNECTED','R1'),('EXPIRED','R1')])
def test_topology_controls_next_inspection_without_causal_promotion(db,tmp_path,topology,expected):
    path=tmp_path/'profile.json';p,r,clock,receipt,inv=create(db,path,'ROAD_DAMAGE')
    with active_scope(p):
        if topology!='DISCONNECTED':
            props={**edge('B10-PIPE-ROAD'),'valid_from':NOW,'association_status':'CANDIDATE' if topology=='CANDIDATE' else 'VERIFIED','source_evidence_id':'EV'}
            if topology=='EXPIRED':props['valid_to']='2026-10-18T01:00:00Z'
            r.create_relationship('UNDERLIES','P1','R1',props)
    async def run():
        with active_scope(p):
            async with brokers(p,path) as tools:
                initial=state(p,r,tools,clock,receipt,inv,'ROAD_DAMAGE');initial.asset_ids=['P1','R1']
                result=await InvestigationAgent(p,r,tools,TopologyReactiveFake(),saver(p),clock=clock).run(initial,thread_id=initial.thread_id)
                inspection=result['data']['pending_inspections'][-1]
                targets=r._read('MATCH (:Inspection {id:$id})-[:INSPECTS]->(a) RETURN a.id',{'id':inspection})
                assert targets==[[expected]]
                assert result['data']['observations'][0]['search_limited'] is True
                assert not r._read("MATCH (h:Hypothesis {status:'VERIFIED'}) RETURN h.id LIMIT 1")
                Path('/tmp/civicly-b10-topology-'+topology+'.json').write_text(json.dumps({'mode':'REACTIVE_FAKE_MODEL_REAL_MCP','topology':topology,'target':expected,'result':result},default=str,indent=2))
    try:asyncio.run(run())
    finally:
        for name in [p.graph,p.checkpoints]:
            if name in db.list_graphs():db.select_graph(name).delete()
        db.connection.execute_command('ACL','DELUSER',p.read_user,p.checkpoint_user)
