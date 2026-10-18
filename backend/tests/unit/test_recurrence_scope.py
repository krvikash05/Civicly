"""Mock bounded graph read only: historical incoherent scope fails closed."""
from types import SimpleNamespace
import pytest
from app.agents.checkpoints import RecoveryRequired
from app.agents import recurrence
@pytest.mark.parametrize('status,blocked',[('OPEN',False),('REOPENED',True)])
def test_no_new_binding_preserves_ordinary_resume_but_blocks_ended_only_reopen(monkeypatch,status,blocked):
 nodes={'INV':SimpleNamespace(properties={'status':status}), 'OLD':SimpleNamespace(kind='Incident',properties={'status':'ENDED'})}
 class Read:
  def __init__(self,*a):pass
  def edges(self,*a,**kw):return [SimpleNamespace(target='OLD')]
  def node(self,id,*a):return nodes[id]
 monkeypatch.setattr(recurrence,'Reader',Read)
 state=SimpleNamespace(as_of='2026-10-18T00:00:00Z',investigation_id='INV',incident_ids=['OLD'])
 if blocked:
  with pytest.raises(RecoveryRequired,match='MISSING_ACTIVE_EPISODE'):recurrence.refresh(None,state)
 else:assert recurrence.refresh(None,state) is state

@pytest.fixture
def validated_history(monkeypatch):
 from app.graph.models import digest
 receipt={'incident_id':'NEW','classification':'AFTER_RECORDED_END','cluster_id':'PC','graph':'G','related_incident_ids':['OLD']}
 nodes={'INV':SimpleNamespace(properties={'status':'REOPENED'}),
  'OLD':SimpleNamespace(id='OLD',kind='Incident',properties={'status':'ENDED','issue_type':'WATERLOGGING','ended_at':'2026-10-18T01:00:00Z'}),
  'NEW':SimpleNamespace(id='NEW',kind='Incident',properties={'status':'REPORTED','issue_type':'WATERLOGGING','started_at':'2026-10-18T02:00:00Z'}),
  'J':SimpleNamespace(kind='Evidence',content_hash='H',properties={'summary':'journal'})}
 links=[SimpleNamespace(id='L0',target='OLD',properties={}),SimpleNamespace(id='L1',target='NEW',properties={'source_evidence_id':'J'})]
 class Read:
  def __init__(self,*a):pass
  def node(self,id,*a):return nodes[id]
  def edges(self,kind,**kw):return links if kind=='INVESTIGATES' else [SimpleNamespace(target='PC')]
 class Intake:
  def __init__(self,*a):pass
  def load(self,*a):return None,None
  def receipt(self,*a):return SimpleNamespace(**receipt,model_dump=lambda **kw:receipt)
 monkeypatch.setattr(recurrence,'Reader',Read);monkeypatch.setattr(recurrence,'ComplaintService',Intake)
 monkeypatch.setattr(recurrence,'Journal',SimpleNamespace(model_validate_json=lambda raw:SimpleNamespace(original={})))
 monkeypatch.setattr(recurrence,'normalize',lambda raw:(None,SimpleNamespace(request_hash='hash')))
 audit={'operation':'RECURRENCE_SCOPE_REFRESH','host_generated':True,'investigation_id':'INV','previous_incident_ids':['OLD'],'active_incident_ids':['NEW'],'historical_incident_ids':['OLD'],'scope_proofs':[{'incident_id':'NEW','investigates_relationship_id':'L1','journal_id':'J','receipt_hash':digest(receipt)}]}
 state=SimpleNamespace(as_of='2026-10-18T03:00:00Z',investigation_id='INV',incident_ids=['NEW'],observations=[audit],evidence={'J':'H'},problem_cluster_id='PC',issue='WATERLOGGING',graph='G')
 return state,nodes,links

def test_repeat_refresh_recognizes_proven_historical_episode(validated_history):
 state,_,_=validated_history
 assert recurrence.refresh(None,state) is state
 assert recurrence.refresh(None,state) is state

@pytest.mark.parametrize('status',['ENDED','ACTIVE'])
def test_unknown_addition_not_ignored_by_status(validated_history,status):
 state,nodes,links=validated_history
 nodes['BAD']=SimpleNamespace(id='BAD',kind='Incident',properties={'status':status})
 links.append(SimpleNamespace(id='BAD-LINK',target='BAD',properties={}))
 with pytest.raises(RecoveryRequired,match='SCOPE_PROVENANCE'):recurrence.refresh(None,state)

@pytest.mark.parametrize('damage',['journal_hash','historical_issue'])
def test_historical_proof_is_revalidated(validated_history,damage):
 state,nodes,_=validated_history
 if damage=='journal_hash':state.evidence['J']='CHANGED'
 else:nodes['OLD'].properties['issue_type']='ROAD_DAMAGE'
 with pytest.raises(RecoveryRequired,match='HISTORY_PROOF_INVALID'):recurrence.refresh(None,state)
