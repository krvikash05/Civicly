"""Presenter host boundaries; fake model/transport only, never live acceptance."""
from types import SimpleNamespace as NS
from contextlib import nullcontext
import asyncio
import pytest
from pydantic import ValidationError
from app.demo_host.config import HostConfig
from app.events.service import Delivery
from app.events.worker import Worker


def config():
 return {'mode':'LIVE_GEMINI','model':'gemini-3.8-flash','profile':'/private/profile','memory_profile':'/private/memory','auth_store':'/private/auth','cases':[{'scenario':s,'issue':i,'investigation_id':'INV'+s,'incident_id':'INC'+s,'thread_id':'THREAD'+s} for s,i in [('S01','WATERLOGGING'),('S04','ROAD_DAMAGE'),('S05','WASTE_ACCUMULATION')]]}


def test_exact_three_categories_and_no_budget_increase():
 assert len(HostConfig.model_validate(config()).cases)==3
 bad=config();bad['cases'][1]['issue']='WATERLOGGING'
 with pytest.raises(ValidationError):HostConfig.model_validate(bad)
 bad=config();bad['budget']={'max_iterations':32}
 with pytest.raises(ValidationError):HostConfig.model_validate(bad)


def test_selected_worker_does_not_claim_other_cases():
 now='2026-10-18T12:00:00Z'
 rows=[{'id':'OTHER','case_id':'OTHER-INV','action':'WAKE','status':'PENDING','due_at':now,'public':{'cursor':1}}]
 d=object.__new__(Delivery);d.clock=lambda:now;d.active=lambda:None
 d.repo=NS(_session=lambda:nullcontext(None));d.store=NS(rows=lambda kind:rows,write=lambda *a,**k:pytest.fail('Foreign case was mutated'))
 assert d.claim('HOST',case_id='SELECTED-INV') is None


def test_worker_forwards_case_filter_before_dispatch():
 calls=[]
 d=NS(store=NS(rows=lambda kind:[]),claim=lambda owner,**kw:calls.append(kw) or None)
 assert asyncio.run(Worker(d,None,'HOST').once(discover=False,case_id='SELECTED')) is None
 assert calls==[{'case_id':'SELECTED'}]


def test_provider_configuration_never_falls_back(monkeypatch):
 import app.demo_host.runtime as module
 settings=NS(model='wrong',provider='gemini',key=object())
 monkeypatch.setattr(module,'ProviderSettings',lambda **kw:NS(model_copy=lambda **kw:settings))
 with pytest.raises(module.HostBlocked,match='CONFIGURATION_MISMATCH'):module.provider_settings(NS(model='expected'))


def test_unknown_analytical_write_stops_before_another_model_selection():
 from app.agents.runtime import InvestigationAgent
 from app.graph.repository import OutcomeUnknown
 s=NS(selection=NS(action='PROPOSE'),errors=[],pause_reason=None)
 agent=object.__new__(InvestigationAgent);agent.decode=lambda channel:s;agent.output=lambda state,phase:state
 async def uncertain(*args):raise OutcomeUnknown('WRITE_OUTCOME_UNKNOWN')
 agent.domain_action=uncertain
 result=asyncio.run(agent.analyst({}))
 assert result.pause_reason=='RECOVERY_REQUIRED' and result.errors


def test_source_writer_rejects_concurrent_presenter():
 from app.demo_host.source import source_writer
 from app.demo_host.runtime import HostBlocked
 lock=NS(acquire=lambda **kw:False)
 repo=NS(graph=NS(name='DEMO'),client=NS(connection=NS(lock=lambda *a,**kw:lock)))
 with pytest.raises(HostBlocked,match='DEMO_SOURCE_BUSY'):
  with source_writer(repo):pytest.fail('Concurrent mutation entered')


def test_plan_reference_feedback_identifies_assessed_evidence_subset():
 from app.services.planning.feedback import feedback
 from app.services.planning.service import PlanningBlocked
 value=feedback(PlanningBlocked('EVIDENCE_OUTSIDE_ASSESSMENTS'))
 assert value.draft_committed=='NO' and value.field_paths==['evidence_ids']
 assert 'supporting or contradicting' in value.explanation


def test_official_catalog_expresses_required_template_without_unrelated_arguments():
 from app.agents.mcp import Tools
 official=NS(operator_inventory=[{'name':'query_graph_readonly','description':'read'}],tools=lambda:[{'name':'query_graph_readonly'}])
 tool=Tools(official,NS(tools=lambda:[]),None,[],'SOURCE').catalog()[0]
 assert tool['input_schema']['required']==['template','id']
 assert set(tool['input_schema']['properties'])=={'template','id','as_of'}
 assert 'template="node"' in tool['description']


def test_prior_tool_catalog_is_selected_only_by_exact_fingerprint():
 from app.agents.mcp import Tools
 from app.graph.models import digest
 official=NS(operator_inventory=[{'name':'query_graph_readonly','description':'read'}],tools=lambda:[{'name':'query_graph_readonly'}])
 tools=Tools(official,NS(tools=lambda:[]),None,[],'SOURCE');current=tools.inventory_hash
 legacy=digest(tools._legacy_catalog)
 assert current!=legacy
 tools.bind_inventory(legacy);assert tools.inventory_hash==legacy
 with pytest.raises(ValueError):tools.bind_inventory('unknown')
