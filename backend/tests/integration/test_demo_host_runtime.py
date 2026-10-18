"""Real isolated DB claim scoping/source serialization/API listing; no provider."""
import secrets
import pytest
from fastapi.testclient import TestClient
from app.active import active_scope
from app.api.application import create_app
from app.events.service import Delivery
from app.demo_host.source import source_writer
from app.demo_host.runtime import HostBlocked
from app.services.evidence import EvidenceService,Actor
from app.services.evidence.reader import Reader
from app.services.operations.auth import Auth,OPERATORS
from app.services.operations.service import Operations
from app.services.planning.service import PlanningService
from app.services.http.service import Services
from tests.integration.test_event_delivery import setup

pytestmark=pytest.mark.integration

def test_case_claim_filter_and_live_source_fence_and_case_picker(db,tmp_path):
 p,r,clock,path,first=setup(db,tmp_path)
 with active_scope(p):
  linked=[r.get_node(e.target) for e in Reader(r,clock()).edges('INVESTIGATES',source=first)]
  incident=next(n.id for n in linked if n.kind=='Incident');cluster=next(n.id for n in linked if n.kind=='ProblemCluster')
  second=EvidenceService(r,clock=clock).execute({'operation':'open','request_id':'DEMO-HOST-SECOND','incident_ids':[incident],'cluster_id':cluster},Actor(id='DEMO-ANALYST',role='ANALYST')).entity_id
  delivery=Delivery(r,clock);delivery.activate(operator='TEST',reason='Fresh isolated presenter test',authorize=True)
  a=delivery.request_resume(first,'FIRST',operator='TEST',reason='Explicit first',authorize=True)
  b=delivery.request_resume(second,'SECOND',operator='TEST',reason='Explicit second',authorize=True)
  claim=delivery.claim('SELECTED-HOST',case_id=second)
  assert claim['case_id']==second and claim['ids']==[b['id']]
  assert delivery.store.get('delivery',a['id'])['status']=='PENDING'
  with source_writer(r):
   with pytest.raises(HostBlocked,match='DEMO_SOURCE_BUSY'):
    with source_writer(r):pytest.fail('Concurrent writer entered')
  passwords={id:secrets.token_urlsafe(24) for id in OPERATORS};auth=Auth.provision(tmp_path/'auth.sqlite3',passwords)
  token=auth.login('OP-ANALYST',passwords['OP-ANALYST'])
  services=Services(p,path,r,auth,Operations(PlanningService(r),auth,clock=clock),delivery,clock)
  client=TestClient(create_app(services),raise_server_exceptions=False)
  response=client.get('/api/v1/investigations?issue=WATERLOGGING',headers={'Authorization':'Bearer '+token})
  assert response.status_code==200,response.text
  assert {row['id'] for row in response.json()['data']['items']}=={first,second}
  response=client.get('/api/v1/investigations?issue=ROAD_DAMAGE',headers={'Authorization':'Bearer '+token})
  assert response.status_code==200 and response.json()['data']['total_count']==0
