"""Known undispatched-proposal reconciliation fails closed on any persisted effect."""
import json
from types import SimpleNamespace as N
import pytest
from app.demo_host.reconciliation import no_effect,reconcile
from app.demo_host.runtime import HostBlocked


def fixture():
 case=N(investigation_id='INV',thread_id='THREAD')
 decision=N(content_hash='hash',properties={'rationale':json.dumps({'metadata':{'investigation_id':'INV','thread_id':'THREAD'},'selection':{'action':'PROPOSE'}})})
 repo=N(get_node=lambda *a:decision,_node_optional=lambda id:None,_read=lambda *a:[["READY","",1]])
 return case,decision,repo


def test_absent_dispatch_domain_journal_and_effect_prove_narrow_no_effect():
 case,_,repo=fixture();p=no_effect(repo,case,'DEC-B10-original')
 assert len(p['absent_ids'])==3 and p['request_id']=='EV-B10-original'
 assert p['conclusion']=='NO_DISPATCH_JOURNAL_OR_DOMAIN_EFFECT'

@pytest.mark.parametrize('index',[0,1,2])
def test_any_persisted_effect_blocks_reconciliation(index):
 case,_,repo=fixture();id=no_effect(repo,case,'DEC-B10-original')['absent_ids'][index]
 repo._node_optional=lambda target:object() if target==id else None
 with pytest.raises(HostBlocked,match='EFFECT_EXISTS'):no_effect(repo,case,'DEC-B10-original')

@pytest.mark.parametrize('change',['foreign','not_propose','pending','not_ready'])
def test_scope_and_pending_or_nonready_repository_fail_closed(change):
 case,d,repo=fixture()
 if change=='foreign':case.investigation_id='OTHER'
 if change=='not_propose':d.properties['rationale']=d.properties['rationale'].replace('PROPOSE','ASSESS')
 if change=='pending':repo._read=lambda *a:[['READY','pending',1]]
 if change=='not_ready':repo._read=lambda *a:[['FAILED','',1]]
 with pytest.raises(HostBlocked):no_effect(repo,case,'DEC-B10-original')


def test_no_human_authorization_stops_before_auth_or_graph():
 with pytest.raises(HostBlocked,match='AUTHORIZATION_REQUIRED'):reconcile(None,None,None,'INV','DEC',authorized=False)


def attestation(monkeypatch):
 import app.demo_host.reconciliation as m
 from app.graph.models import digest
 case,_,repo=fixture();state={'errors':['WRITE_OUTCOME_UNKNOWN']}
 row={'version':1,'source_graph':'graph','investigation_id':'INV','thread_id':'THREAD','actor':{'role':'ADMIN'},'authorized_by_human':True,'original_checkpoint_or_error_modified':False,'quarantine_cleared':False,'original_operation_replayed':False,'unknown_error_count':1,'checkpoint_id':'OLD','checkpoint_sha256':digest(state),'proof':no_effect(repo,case,'DEC-B10-original')}
 monkeypatch.setattr(m,'Storage',lambda *a:N(get=lambda *a:row))
 monkeypatch.setattr(m,'saver',lambda *a:N(get_tuple=lambda *a:N(checkpoint={'channel_values':{'data':state}})))
 return m,case,repo,state,row


def test_attestation_preserves_original_checkpoint_and_accepts_only_proved_error(monkeypatch):
 m,case,repo,state,row=attestation(monkeypatch)
 assert m.valid_reconciliation(None,N(graph='graph'),repo,case,N(errors=state['errors']))
 assert row['original_checkpoint_or_error_modified'] is False

@pytest.mark.parametrize('change',['authorization','checkpoint','new_error','scope','replayed','decision'])
def test_changed_attestation_or_new_uncertainty_blocks(monkeypatch,change):
 m,case,repo,state,row=attestation(monkeypatch);errors=list(state['errors'])
 if change=='authorization':row['authorized_by_human']=False
 if change=='checkpoint':row['checkpoint_sha256']='changed'
 if change=='new_error':errors.append('WRITE_OUTCOME_UNKNOWN')
 if change=='scope':row['thread_id']='OTHER'
 if change=='replayed':row['original_operation_replayed']=True
 if change=='decision':row['proof']['decision_hash']='changed'
 with pytest.raises(HostBlocked):m.valid_reconciliation(None,N(graph='graph'),repo,case,N(errors=errors))
