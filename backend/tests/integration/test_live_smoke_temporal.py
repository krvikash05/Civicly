"""Actual isolated binding/time checks; no model, MCP call or ownership acquisition."""
import importlib.util,json
from pathlib import Path
from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
from uuid import uuid4
import pytest
from app.active import active_scope
from app.agents.models import InvestigationState
from app.agents.control import Control
from app.agents.checkpoints import saver
from app.graph.schema import utc_now
from app.graph.models import digest
from app.services.evidence.reader import Reader
from tests.b10_fixtures import create
spec=importlib.util.spec_from_file_location('smoke',Path(__file__).resolve().parents[3]/'scripts/b11_live_smoke.py');smoke=importlib.util.module_from_spec(spec);spec.loader.exec_module(smoke)
pytestmark=pytest.mark.integration

def initial(p,r,receipt,inv):
 return InvestigationState(graph=p.graph,investigation_id=inv,thread_id=uuid4().hex,problem_cluster_id=receipt.cluster_id,incident_ids=[receipt.incident_id],asset_ids=['D1'],issue='WATERLOGGING',graph_revision=0,inventory_hash='non-model-temporal-test',as_of=utc_now())

def test_future_rejected_and_actual_utc_binding_preserves_temporal_guards(db,tmp_path):
 future=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat().replace('+00:00','Z')
 p,r,clock,receipt,inv=create(db,tmp_path/'future.json',clock=lambda:future)
 state=initial(p,r,receipt,inv);key='civicly:b10:'+p.graph+':'+digest(state.thread_id)
 with active_scope(p):
  before=r.get_node(inv).content_hash
  with pytest.raises(Exception,match='reference type/time unavailable'):smoke.temporal_preflight(r,p,state,utc_now())
  assert r.get_node(inv).content_hash==before
  assert not db.connection.get(key) and not db.connection.get(key+':quarantine')
  assert saver(p).get_tuple({'configurable':{'thread_id':state.thread_id}}) is None
 prepared_at=utc_now();p,r,clock,receipt,inv=create(db,tmp_path/'actual.json',clock=lambda:prepared_at);state=initial(p,r,receipt,inv)
 with active_scope(p):
  first=smoke.temporal_preflight(r,p,state,utc_now())
  Control(r).bind(inv,state.thread_id)
  assert r.get_node(inv).properties['thread_id']==state.thread_id
  second=smoke.temporal_preflight(r,p,state,utc_now())
  assert first['status']==second['status']=='PASS'
 Path('docs/evidence/B11-LIVE-SMOKE-R-temporal-test.json').write_text(json.dumps({'mode':'REAL_ISOLATED_FALKORDB_NO_MODEL','future_rejected_no_owner_quarantine_write':True,'actual_preflight':first,'actual_bind_and_recheck':second,'external_provider_calls':0},indent=2)+'\n')
