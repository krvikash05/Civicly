"""B16-R injected ACK/projection faults, actual HTTP/B09/FalkorDB persistence."""
import json,secrets
from pathlib import Path
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from app.active import active_scope
from app.api.application import create_app
from app.services.http.service import Services,request_identity
from app.services.evidence.service import EvidenceService
from app.services.evidence.writer import stable
from app.services.evidence.models import Journal
from app.services.operations.auth import Auth,OPERATORS
from app.services.operations.service import Operations
from app.services.planning.service import PlanningService
from app.events.service import Delivery
from tests.integration.test_event_delivery import setup
pytestmark=pytest.mark.integration

def test_committed_readback_and_projection_faults_preserve_records_and_block_replay(db,tmp_path,monkeypatch):
 p,r,clock,path,inv=setup(db,tmp_path)
 passwords={i:secrets.token_urlsafe(24) for i in OPERATORS};auth=Auth.provision(tmp_path/'auth.sqlite3',passwords)
 token=auth.login('OP-ANALYST',passwords['OP-ANALYST'])
 with active_scope(p):
  delivery=Delivery(r,clock);delivery.activate(operator='B16R-proof',reason='Explicit isolated corrective test only',authorize=True)
  s=Services(p,path,r,auth,Operations(PlanningService(r,clock=clock),auth,clock=clock),delivery,clock)
 c=TestClient(create_app(s),raise_server_exceptions=False);body={'investigation_id':inv,'asset_ids':['D1'],'department_id':'DEP','inspection_type':'B16R_AUTHORED_SYNTHETIC'}
 original_readback=EvidenceService.readback;original_get=s.reads.get;original_execute=EvidenceService.execute
 calls=[]
 def counted(self,payload,actor):calls.append(payload['request_id']);return original_execute(self,payload,actor)
 monkeypatch.setattr(EvidenceService,'execute',counted)
 proofs=[]
 for fault in ['readback','projection']:
  key='B16R-'+fault;request=request_identity(p.graph,'OP-ANALYST',key);journal_id=stable('EV-JOURNAL','OP-ANALYST',request)
  with active_scope(p):before=r._read('MATCH (n:Inspection) RETURN count(n)')[0][0]
  def broken_readback(self,receipt,replayed=False):
   # This is called after real B09 atomic mutation+journal commit, not a mock DB.
   if receipt.operation=='request_inspection':raise ValueError('PRIVATE_SOURCE_OR_CREDENTIAL_SENTINEL')
   return original_readback(self,receipt,replayed)
  def broken_projection(id,kind,actor,session):
   if kind=='Inspection':raise ValueError('PRIVATE_SOURCE_OR_CREDENTIAL_SENTINEL')
   return original_get(id,kind,actor,session)
  monkeypatch.setattr(EvidenceService,'readback',broken_readback if fault=='readback' else original_readback)
  monkeypatch.setattr(s.reads,'get',broken_projection if fault=='projection' else original_get)
  h={'Authorization':'Bearer '+token,'Idempotency-Key':key}
  res=c.post('/api/v1/inspections',json=body,headers=h)
  assert res.status_code==409,res.text
  error=res.json()['error'];assert error['code']=='RECOVERY_REQUIRED' and error['details']['commitment']=='UNKNOWN'
  assert error['details']['correlation_id']==error['details']['request_id']==request
  assert 'PRIVATE_SOURCE_OR_CREDENTIAL_SENTINEL' not in res.text and p.graph not in res.text
  with active_scope(p):
   journal=Journal.model_validate_json(r.get_node(journal_id,'Evidence').properties['summary'])
   assert journal.state=='COMMITTED' and journal.command['request_id']==request
   entity=journal.receipt.entity_id;assert r.get_node(entity,'Inspection')
   assert error['details']['entity_id']==entity and error['details']['investigation_id']==inv
   assert r._read('MATCH (n:Inspection) RETURN count(n)')==[[before+1]]
   row=delivery.store.get('api_request',request);assert row['status']=='DISPATCHING' and row['status']!='REJECTED'
   assert row['recovery']['journal_id']==journal_id and row['recovery']['identities']['entity_id']==entity
   phase=row['recovery']['phase'];assert phase==('DISPATCHED' if fault=='readback' else 'RETURNED')
  prior_calls=len(calls)
  monkeypatch.setattr(EvidenceService,'readback',original_readback);monkeypatch.setattr(s.reads,'get',original_get)
  replay=c.post('/api/v1/inspections',json=body,headers=h)
  assert replay.status_code==409 and replay.json()['error']['code']=='RECOVERY_REQUIRED'
  assert replay.json()['error']['details']['entity_id']==entity and len(calls)==prior_calls
  with active_scope(p):
   assert r._read('MATCH (n:Inspection) RETURN count(n)')==[[before+1]]
   assert Journal.model_validate_json(r.get_node(journal_id).properties['summary']).state=='COMMITTED'
  proofs.append({'fault':fault,'http_status':res.status_code,'response':res.json(),'journal_id':journal_id,'journal_state':'COMMITTED','inspection_id':entity,'new_inspections':1,'phase':phase,'intent_status':row['status'],'replay_service_invocations':0,'no_duplicate_effects':True})
 Path('docs/evidence/B16R-real-proof.json').write_text(json.dumps({'mode':'ACTUAL_ASGI_HTTP_B09_FALKORDB_WITH_INJECTED_FAILURES_NO_MODEL','graph':p.graph,'investigation_id':inv,'cases':proofs,'total_inspections':2,'provider_calls':0,'operator_reconciliation_required':True},indent=2)+'\n')
