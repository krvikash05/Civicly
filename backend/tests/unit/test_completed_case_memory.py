"""Completed episode memory uses graph identity and recorded outcome evidence."""
from types import SimpleNamespace as N
import pytest
from app.services.http.reads import Reads
from app.graph.repository import PreconditionFailed


def fixture(status='ENDED'):
 nodes={'INC':N(id='INC',properties={'status':status}),'INV':N(id='INV'),'WO':N(id='WO'),'OUT':N(id='OUT'),'EV':N(id='EV',content_hash='hash')}
 value={'id':'OUT','work_order_id':'WO','plan_id':'PLAN','evidence_references':[{'id':'EV','content_hash':'hash'}]}
 r=Reads(N(_read=lambda *a:[['INV','PLAN','WO','OUT']],get_node=lambda id:nodes[id]),N(store=N(get=lambda *a:value)),None,None)
 r.node=lambda id,*a:nodes[id];r.allowed=lambda *a:True
 return r,value,nodes


def test_completed_episode_exposes_persisted_outcome_and_source_not_generated_lesson():
 r,_,_=fixture();out=r.completed_case_context('INC',None,None)
 assert out['outcome_ids']==['OUT'] and out['evidence_ids']==['EV']
 assert out['source_investigation_id']=='INV' and 'not an automatically generalized lesson' in out['gaps'][0]


def test_open_case_does_not_become_historical_memory():
 r,_,_=fixture('REPORTED');r.repo._read=lambda *a:pytest.fail('Should not read outcomes')
 assert r.completed_case_context('INC',None,None) is None

@pytest.mark.parametrize('fault',['scope','hash','overflow','redaction'])
def test_invalid_or_hidden_completed_context_fails_closed(fault):
 r,value,nodes=fixture()
 if fault=='redaction':
  r.allowed=lambda *a:False
  assert r.completed_case_context('INC',None,None) is None
  return
 if fault=='scope':value['plan_id']='OTHER'
 if fault=='hash':nodes['EV'].content_hash='changed'
 if fault=='overflow':r.repo._read=lambda *a:[['INV','PLAN','WO','OUT']]*101
 with pytest.raises(PreconditionFailed):r.completed_case_context('INC',None,None)
