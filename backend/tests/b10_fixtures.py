"""Authored controlled B10 graph. Fake model tests never count as live AI evidence."""
from app.active import new_profile,save,provision,active_scope
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.services.complaints import ComplaintService
from app.services.evidence import EvidenceService
from app.agents.models import InvestigationState,Selection
from app.graph.queries import GraphQueries
from tests.b08_fixtures import populate,payload
from tests.b09_fixtures import Clock,ANALYST
from tests.schema_examples import common
from uuid import uuid4

class ScriptedModel:
    mode='DETERMINISTIC_FAKE_MODEL'
    def __init__(self,actions):self.actions=list(actions);self.contexts=[]
    async def choose(self,context,remaining_tokens):
        self.contexts.append(context)
        return Selection.model_validate(self.actions.pop(0)),0

def choose(action='PAUSE',args=None,tool='',summary='Authored deterministic model test selection',reason='MISSING_EVIDENCE'):
    import json
    return {'action':action,'arguments_json':json.dumps(args or {}),'tool_name':tool,'summary':summary,'pause_reason':reason if action=='PAUSE' else 'NONE'}

def create(db,path,issue='WATERLOGGING',*,clock=None):
    injected_clock=clock is not None
    p=new_profile();save(p,path);MigrationRunner(db,p.graph).apply();r=GraphRepository(db,p.graph,lease_seconds=30);clock=clock if injected_clock else Clock()
    with active_scope(p):
        populate(r);r.create_node('Department',{**common('DEP'),'name':'Synthetic inspection department','department_type':'ENGINEERING'})
        dates={'reported_at':clock(),'occurred_at':clock()} if injected_clock else {}
        receipt=ComplaintService(r,clock=clock).intake(payload(issue,ref='B10-controlled-'+issue,**dates))
        inv=EvidenceService(r,clock=clock).execute({'operation':'open','request_id':'B10-open','incident_ids':[receipt.incident_id],'cluster_id':receipt.cluster_id},ANALYST).entity_id
        provision(db,p)
    return p,r,clock,receipt,inv

def state(p,r,tools,clock,receipt,inv,issue='WATERLOGGING',thread=None):
    return InvestigationState(graph=p.graph,investigation_id=inv,thread_id=thread or uuid4().hex,problem_cluster_id=receipt.cluster_id,discovered_tool_names=[t['name'] for t in tools.catalog()],incident_ids=[receipt.incident_id],
        asset_ids=[{'WATERLOGGING':'D1','ROAD_DAMAGE':'R1','WASTE_ACCUMULATION':'W1'}[issue]],issue=issue,
        graph_revision=GraphQueries(r)._state(),inventory_hash=tools.inventory_hash,as_of=clock())
