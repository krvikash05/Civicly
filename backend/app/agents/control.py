"""Narrow B10 analytical record service. No arbitrary model-controlled writes."""
import json
from app.active import is_shared_target
from app.graph.models import digest
from app.graph.schema import utc_now
from .models import Selection


def identity(prefix,thread,index,wake):return prefix+'-B10-'+digest([thread,index,wake])[:32]
def common(id,at):return {'id':id,'municipality_id':'demo-city','schema_version':3,'created_at':at}

class Control:
    def __init__(self,repo,clock=utc_now):
        if not is_shared_target(repo.graph.name):raise ValueError('Trusted B10 active scope required')
        self.repo,self.clock=repo,clock
    def decision(self,id,selection,metadata):
        old=self.repo._node_optional(id)
        value={'version':1,'selection':selection.model_dump(mode='json'),'metadata':metadata}
        if old:
            if old.kind!='AgentDecision':raise ValueError('Decision ID collision')
            saved=json.loads(old.properties['rationale'])
            if saved!=value:raise ValueError('Decision replay conflict')
            return old
        at=self.clock();kind={'READ':'GATHER_EVIDENCE','PROPOSE':'REASSESS_HYPOTHESES','ASSESS':'REASSESS_HYPOTHESES','INSPECT':'REQUEST_INSPECTION','RECOMMEND':'REQUEST_APPROVAL','PAUSE':'GATHER_EVIDENCE'}[selection.action]
        return self.repo.create_node('AgentDecision',{**common(id,at),'decided_at':at,'decision_type':kind,'rationale':json.dumps(value,sort_keys=True)})
    def selected(self,id):
        n=self.repo._node_optional(id)
        if n is None:return None
        if n.kind!='AgentDecision':raise ValueError('Decision identity collision')
        value=json.loads(n.properties['rationale'])
        if value['version']!=1:raise ValueError('Decision format incompatible')
        return Selection.model_validate(value['selection']),value['metadata']
    def journal(self,id):
        n=self.repo._node_optional(id)
        if n is None:return None,None
        if n.kind!='Evidence' or n.properties['evidence_type']!='B10_OPERATION':raise ValueError('Journal identity collision')
        return n,json.loads(n.properties['summary'])
    def prepare(self,id,decision_id,selection):
        old,value=self.journal(id)
        expected={'version':1,'decision_id':decision_id,'selection_sha256':digest(selection.model_dump(mode='json'))}
        if old:
            if any(value.get(k)!=v for k,v in expected.items()):raise ValueError('Journal replay mismatch')
            return old,value
        at=self.clock();value={**expected,'status':'PREPARED','result':None}
        n=self.repo.create_node('Evidence',{**common(id,at),'updated_at':at,'recorded_at':at,'source_kind':'AGENT','source_record_id':decision_id,
            'evidence_type':'B10_OPERATION','reliability':'UNVERIFIED','summary':json.dumps(value)})
        return n,value
    def commit(self,node,value,result):
        value={**value,'status':'COMMITTED','result':result}
        raw=json.dumps(value,sort_keys=True,allow_nan=False)
        if len(raw.encode())>90000:raise ValueError('Journal budget exceeded')
        self.repo.update_node(node.id,{'summary':raw,'updated_at':self.clock()},expected_hash=node.content_hash)
    def bind(self,inv,thread):
        n=self.repo.get_node(inv,'Investigation');bound=n.properties.get('thread_id')
        if bound and bound!=thread:raise ValueError('Investigation already bound to another thread')
        if not bound:self.repo.update_node(inv,{'thread_id':thread,'updated_at':self.clock()},expected_hash=n.content_hash)
