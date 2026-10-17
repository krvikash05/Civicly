"""Structural/mock unit checks, not real MCP acceptance evidence."""
import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from jsonschema.exceptions import ValidationError as JSONError
from app.mcp.civicly.contracts import READ,CONTRACT,context,input_schema,validate,bounded
from app.mcp.civicly.models import TraceRecord
from app.mcp.civicly.broker import validate_result
from app.mcp.civicly.service import CivicReadService
from app.mcp.civicly.storage import trace_target


def test_declared_inventory_is_read_only_twelve_and_write_six_deferred():
 assert len(READ)==12 and len(CONTRACT['tools'])==18
 assert all(t['b07_runtime']=='NOT_REGISTERED_FUTURE_WRITE' for t in CONTRACT['tools'] if t['permission']!='READ')
 for name in READ:
  assert '_context' not in input_schema(name)['properties']
  assert '_context' in input_schema(name,True)['required']

@pytest.mark.parametrize('extra',[{'query':'CREATE (:X)'},{'graph':'civicly_docs'},{'_context':{}},{'tenant_id':'evil'},{'role':'ADMIN'}])
def test_agent_arguments_cannot_inject_authority(extra):
 with pytest.raises(JSONError):validate(input_schema('find_related_incidents'),{'incident_id':'I','max_results':5,**extra})

@pytest.mark.parametrize('value',[{'x':' '},{'x':'a'*513},{'x':list(range(101))},{'x':'a'*17000}])
def test_finite_argument_budgets(value):
 with pytest.raises(ValueError):bounded(value)

@pytest.mark.parametrize('name',['civicly_knowledge','civicly_docs','civicly_b01_runtime','civicly_b07_test_bad','civicly_b06_test_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'])
def test_trace_storage_cannot_target_source_or_internal_graphs(name):
 with pytest.raises(ValueError):trace_target(name)

@pytest.mark.parametrize('changes',[{'source_graph':'civicly_docs'},{'municipality_id':'other'},{'caller_role':'ADMIN'},{'invocation_origin':'AGENT'}])
def test_context_rejects_unimplemented_authority_or_model_origin(changes):
 with pytest.raises(ValidationError):type(context()).model_validate({**context().model_dump(),**changes})

@pytest.mark.parametrize('tool',sorted(READ))
def test_common_result_is_closed_and_identity_checked(tool):
 c=context();service=CivicReadService.__new__(CivicReadService)
 r=service.result(tool,c,'2026-10-17T00:00:00Z');r.update(status='UNAVAILABLE',error={'code':'NOT_AVAILABLE','message':'Unavailable','retryable':False})
 validate_result(tool,r,c)
 with pytest.raises(Exception):validate_result(tool,{**r,'invented':True},c)
 with pytest.raises(Exception):validate_result(tool,{**r,'execution_id':'spoof'},c)


def test_0001_and_registry_are_immutable_and_trace_schema_does_not_add_domain_fields():
 import hashlib
 assert hashlib.sha256(Path('backend/app/graph/migrations/0001.json').read_bytes()).hexdigest()=='94ab9fae6079fe7e87b41afd80701409db6bb51d529c2565dbd340896a5c923b'
 assert hashlib.sha256(Path('contracts/schema_registry.json').read_bytes()).hexdigest()=='12541990b58d65e8602bff77b93b735009616e7ee658b9e7582a7ae9f449aac6'
 assert 'rationale_summary' not in json.loads(Path('contracts/schema_registry.json').read_text())['node_types']['ToolExecution']['properties']


def test_shared_trace_retains_validated_domain_error_code_without_raw_body():
 import time
 from app.mcp.civicly.server import trace
 c=context();r=CivicReadService.__new__(CivicReadService).result('retrieve_case_memory',c,'2026-10-17T00:00:00Z')
 r.update(status='UNAVAILABLE',error={'code':'DATA_UNAVAILABLE','message':'Unavailable','retryable':False})
 t=trace(c,'retrieve_case_memory','2026-10-17T00:00:00Z',time.perf_counter(),'a'*64,r)
 assert t.status=='UNAVAILABLE' and t.error_code=='DATA_UNAVAILABLE' and t.validated_output
 assert t.rationale_summary is None and 'data' not in t.model_dump()
