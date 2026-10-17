"""Shared machine contracts, finite arguments and normalized JSON types."""
import hashlib,json
from pathlib import Path
from uuid import UUID,uuid4
from jsonschema import Draft202012Validator,FormatChecker
from pydantic import BaseModel,ConfigDict,Field
from typing import Literal
from app.mcp.runtime import ROOT,CITY_GRAPH

SERVER='civicly-domain';VERSION='1.0.0';SCHEMA_VERSION=3
CONTRACT=json.loads((ROOT/'contracts/mcp_tools.json').read_text())
READ={t['name']:t for t in CONTRACT['tools'] if t['permission']=='READ'}
PAYLOADS={t['name']:next(k for k in t['output_schema']['required'] if k not in {'status','trace_id','source_evidence_ids','simulation_mode','graph_revision','truncated','error','context','data','search_limited','execution_id','server_id','tool_name','schema_version','inventory_version'}) for t in CONTRACT['tools']}


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
INVENTORY_HASH=digest([{'name':k,'input':t['input_schema'],'output':t['output_schema']} for k,t in sorted(READ.items())])


class Context(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True,frozen=True,hide_input_in_errors=True)
    trace_id: str=Field(min_length=1,max_length=80)
    execution_id: str=Field(min_length=1,max_length=80)
    parent_execution_id: str | None=None
    investigation_id: str | None=Field(default=None,max_length=200)
    municipality_id: Literal['demo-city']='demo-city'
    source_graph: Literal[CITY_GRAPH]=CITY_GRAPH
    caller_role: Literal['READ_ONLY','OPERATOR_REVIEW']='OPERATOR_REVIEW'
    invocation_origin: Literal['OPERATOR_REVIEW','APPLICATION']='OPERATOR_REVIEW'


def context(investigation_id=None):
    return Context(trace_id=uuid4().hex,execution_id=uuid4().hex,investigation_id=investigation_id)


def validate(schema,value):
    Draft202012Validator(schema,format_checker=FormatChecker()).validate(value)


def input_schema(name,wire=False):
    schema=json.loads(json.dumps(READ[name]['input_schema']))
    if wire:
        schema['properties']['_context']=Context.model_json_schema()
        schema['required']=[*schema['required'],'_context']
    return schema


def bounded(value):
    # JSON shapes only; schema validators additionally reject unknown fields.
    if len(json.dumps(value,allow_nan=False).encode())>16384:raise ValueError('Input budget')
    def walk(x):
        if isinstance(x,str) and (len(x)>512 or not x.strip()):raise ValueError('String budget')
        if isinstance(x,list):
            if len(x)>100:raise ValueError('List budget')
            for v in x:walk(v)
        if isinstance(x,dict):
            for v in x.values():walk(v)
    walk(value)
