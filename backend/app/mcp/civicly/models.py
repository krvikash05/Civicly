"""Shared invocation trace metadata; raw arguments/output bodies are never persisted."""
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_validator
from app.graph.schema import timestamp
from .contracts import Context

class TraceRecord(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True,frozen=True,hide_input_in_errors=True)
    context: Context
    phase: Literal['SERVER','BROKER']
    server_id: Literal['civicly-domain','official-falkordb']
    server_version: str
    tool_name: str=Field(max_length=80)
    schema_version: int=3
    inventory_version: str
    schema_sha256: str
    arguments_sha256: str
    arguments_summary: Literal['values withheld']='values withheld'
    output_sha256: str | None=None
    validated_output: bool=False
    started_at: str
    finished_at: str
    latency_ms: float=Field(ge=0)
    status: str=Field(max_length=80)
    error_code: str | None=None
    protocol_version: str | None=None
    graph_revision: int | None=Field(default=None,ge=0)
    source_evidence_ids: list[str]=Field(default_factory=list,max_length=200)
    graph_path_ids: list[str]=Field(default_factory=list,max_length=100)
    result_summary: dict[str,int | bool]=Field(default_factory=dict)
    simulation_mode: Literal[True]=True
    rationale_summary: None=None

    @field_validator('started_at','finished_at')
    @classmethod
    def time(cls,v):timestamp(v);return v
