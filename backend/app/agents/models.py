"""Strict versioned runtime JSON; checkpoint data contains no credentials."""
import json
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,model_validator
from app.services.planning.feedback import Feedback
from .limits import DEFAULT_CUMULATIVE_TOKENS,MAX_CUMULATIVE_TOKENS,MAX_CHECKPOINT_TOKENS

class Model(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True,hide_input_in_errors=True)

class Selection(Model):
    action: Literal['READ','PROPOSE','ASSESS','INSPECT','RECOMMEND','PAUSE']
    summary: str=Field(min_length=1,max_length=512)
    tool_name: str=Field(max_length=100)
    arguments_json: str=Field(max_length=8000)
    pause_reason: Literal['NONE','MISSING_EVIDENCE','HUMAN_REVIEW','DEPENDENCY_UNAVAILABLE']
    @model_validator(mode='after')
    def shape(self):
        value=json.loads(self.arguments_json)
        if not isinstance(value,dict):raise ValueError('JSON object arguments required')
        if self.action=='READ' and not self.tool_name:raise ValueError('Discovered tool required')
        if self.action!='READ' and self.tool_name:raise ValueError('Only READ selects a tool')
        if self.action=='PAUSE' and self.pause_reason=='NONE':raise ValueError('Pause reason required')
        return self
    @property
    def arguments(self):return json.loads(self.arguments_json)

class Budget(Model):
    max_iterations: int=Field(default=16,ge=2,le=32)
    max_tools: int=Field(default=8,ge=1,le=16)
    max_tokens: int=Field(default=DEFAULT_CUMULATIVE_TOKENS,ge=2000,le=MAX_CUMULATIVE_TOKENS)
    max_seconds: int=Field(default=240,ge=10,le=600)
    max_wakes: int=Field(default=5,ge=1,le=10)

class InvestigationState(Model):
    version: Literal[1]=1
    graph: str
    investigation_id: str=Field(min_length=1,max_length=200)
    thread_id: str=Field(min_length=1,max_length=200)
    problem_cluster_id: str=Field(min_length=1,max_length=200)
    discovered_tool_names: list[str]=Field(default_factory=list,max_length=30)
    missing_evidence: list[str]=Field(default_factory=list,max_length=100)
    planning_feedback:Feedback|None=None
    current_plan_id: str | None=None
    current_plan_version: int | None=None
    current_plan_hash: str | None=None
    incident_ids: list[str]=Field(min_length=1,max_length=3)
    asset_ids: list[str]=Field(min_length=1,max_length=10)
    issue: Literal['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']
    graph_revision: int=Field(ge=0)
    phase: Literal['Supervisor','Investigator','RootCauseAnalyst','ResolutionPlanner','Coordinator','AwaitDependency']='Supervisor'
    hypotheses: list[str]=Field(default_factory=list,max_length=20)
    evidence: dict[str,str]=Field(default_factory=dict)
    inventory_hash: str
    selection: Selection | None=None
    decisions: list[str]=Field(default_factory=list,max_length=160)
    executions: list[str]=Field(default_factory=list,max_length=80)
    pending_inspections: list[str]=Field(default_factory=list,max_length=20)
    pending_approval: str | None=None
    errors: list[str]=Field(default_factory=list,max_length=160)
    observations: list[dict]=Field(default_factory=list,max_length=80)
    nodes: list[str]=Field(default_factory=list,max_length=500)
    pause_reason: str | None=None
    recommendation: dict | None=None
    budget: Budget=Field(default_factory=Budget)
    iterations: int=Field(default=0,ge=0,le=200)
    tool_calls: int=Field(default=0,ge=0,le=80)
    tokens: int=Field(default=0,ge=0,le=MAX_CHECKPOINT_TOKENS)
    wakes: int=Field(default=0,ge=0,le=10)
    refresh_required: bool=False
    as_of: str
