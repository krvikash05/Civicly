"""Presenter read-only smoke authorization; never a live provider test."""
import asyncio
from types import SimpleNamespace as NS
import pytest
from app.agents.models import Selection
from app.demo_host.context_smoke import read_only_selection,smoke
from app.demo_host.runtime import HostBlocked
from tests.b10_fixtures import choose

@pytest.mark.parametrize('action',['PROPOSE','ASSESS','INSPECT','RECOMMEND','PAUSE'])
def test_probe_rejects_every_non_read_action(action):
 s=Selection.model_validate(choose(action))
 with pytest.raises(HostBlocked,match='DID_NOT_SELECT_READ'):read_only_selection(s,[])

@pytest.mark.parametrize('name',['official::query_graph','civicly::approve_plan','civicly::write_data'])
def test_even_advertised_write_tool_is_refused(name):
 s=Selection.model_validate(choose('READ',{},name))
 with pytest.raises(HostBlocked,match='NOT_READ_ONLY'):read_only_selection(s,[{'name':name}])


def test_known_discovered_read_allowed_and_unknown_name_refused():
 s=Selection.model_validate(choose('READ',{'template':'node','id':'A'},'official::query_graph_readonly'))
 read_only_selection(s,[{'name':s.tool_name}])
 with pytest.raises(HostBlocked,match='NOT_DISCOVERED'):read_only_selection(s,[])


def test_no_live_flag_stops_before_any_source_or_provider_access():
 with pytest.raises(HostBlocked,match='LIVE_REQUIRED'):asyncio.run(smoke(None,None,None,'I'))


def test_existing_probe_marker_blocks_replay_before_preflight(tmp_path):
 (tmp_path/'context-wire-smoke.json').write_text('{}')
 c=NS(auth_store=str(tmp_path/'auth.sqlite3'),cases=[NS(investigation_id='I')])
 with pytest.raises(HostBlocked,match='ALREADY_ATTEMPTED'):asyncio.run(smoke(c,None,None,'I',live=True))


def test_unknown_case_stops_before_source_access():
 c=NS(cases=[])
 with pytest.raises(HostBlocked,match='NOT_HOST_AUTHORIZED'):asyncio.run(smoke(c,None,None,'I',live=True))


def test_official_read_result_has_no_domain_status_field_and_is_validated():
 from app.demo_host.context_smoke import read_status
 from pydantic import ValidationError
 value={'graph':'SOURCE','tool':'query_graph_readonly','template':'node','graph_revision':1,'rows':[]}
 assert read_status('official::query_graph_readonly',value)=='SUCCESS'
 assert read_status('civicly::get_maintenance_history',{})=='ERROR'
 assert read_status('civicly::get_maintenance_history',{'status':'PARTIAL'})=='PARTIAL'
 with pytest.raises(ValidationError):read_status('official::query_graph_readonly',{'status':'SUCCESS'})
