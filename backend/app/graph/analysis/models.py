"""Serializable B05 contracts; quantities and ranking factors are not confidence."""
from typing import Literal
from pydantic import Field, field_validator, model_validator
from app.graph.models import GraphModel, NodeRecord, EdgeRecord, PathRecord
from app.graph.schema import timestamp


class AnalysisLimits(GraphModel):
    max_hops: int = Field(default=6, ge=1, le=6)
    max_paths: int = Field(default=100, ge=1, le=100)
    max_nodes: int = Field(default=120, ge=1, le=120)
    max_edges: int = Field(default=200, ge=1, le=200)
    max_queries: int = Field(default=64, ge=1, le=64)
    max_steps: int = Field(default=10000, ge=1, le=10000)
    wall_seconds: float = Field(default=5.0, gt=0, le=5.0)
    timeout_ms: int = Field(default=1000, ge=1, le=1000)


class AnalysisRequest(GraphModel):
    operation: Literal['reachability','shared_downstream','impacted_assets','criticality',
                       'components','dependencies','task_dag']
    ids: tuple[str, ...] = ()
    incident_ids: tuple[str, ...] = ()
    plan_id: str | None = None
    as_of: str
    direction: Literal['upstream','downstream'] = 'downstream'
    include_candidates: bool = False
    max_hops: int = Field(default=6, ge=1, le=6)
    limit: int = Field(default=40, ge=1, le=100)
    threshold: int = Field(default=2, ge=2, le=20)

    @field_validator('as_of')
    @classmethod
    def date(cls, value):timestamp(value);return value

    @field_validator('ids','incident_ids')
    @classmethod
    def roots(cls, value):
        if not value or len(value)<=20:
            if len(set(value))==len(value) and all(x.strip() and len(x)<=512 for x in value):return value
        raise ValueError('At most20 distinct nonblank bounded IDs')

    @model_validator(mode='after')
    def scope(self):
        if self.operation=='shared_downstream' and (self.ids or self.plan_id):raise ValueError('Shared query uses incidents only')
        if self.operation!='shared_downstream' and self.incident_ids:raise ValueError('Incident roots only apply to shared query')
        if self.operation!='task_dag' and self.plan_id:raise ValueError('Plan only applies to task DAG')
        if self.operation=='task_dag' and self.plan_id and self.ids:raise ValueError('Select plan or task roots, not both')
        if self.operation!='reachability' and self.direction!='downstream':raise ValueError('Direction only applies to reachability')
        if self.operation!='shared_downstream' and self.threshold!=2:raise ValueError('Threshold only applies to shared query')
        if self.operation=='shared_downstream':
            if len(self.incident_ids)<self.threshold:raise ValueError('Not enough incidents for threshold')
        elif self.operation=='task_dag' and self.plan_id:
            if not self.plan_id.strip() or len(self.plan_id)>512:raise ValueError('Invalid plan ID')
        elif not self.ids:raise ValueError('Operation needs explicit roots')
        return self


class CaseRequest(GraphModel):
    as_of: str
    seed_incident_id: str | None = None
    asset_ids: tuple[str, ...] = ()
    zone_id: str | None = None
    issue_type: Literal['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION'] | None = None
    after: str | None = None
    before: str | None = None
    include_candidates: bool = False
    max_hops: int = Field(default=6, ge=1, le=6)
    limit: int = Field(default=40, ge=1, le=100)

    @field_validator('as_of','after','before')
    @classmethod
    def date(cls,value):
        if value is not None:timestamp(value)
        return value

    @field_validator('asset_ids')
    @classmethod
    def roots(cls,value):return AnalysisRequest.roots(value)

    @model_validator(mode='after')
    def scope(self):
        if not (self.seed_incident_id or self.asset_ids or self.zone_id or self.issue_type):raise ValueError('Case retrieval needs a factor')
        for value in (self.seed_incident_id,self.zone_id):
            if value is not None and (not value.strip() or len(value)>512):raise ValueError('Invalid root ID')
        if self.before and timestamp(self.before)>timestamp(self.as_of):raise ValueError('Future history window')
        if self.after and timestamp(self.after)>timestamp(self.before or self.as_of):raise ValueError('Reversed history window')
        return self


class ProofPath(PathRecord):
    id: str


class AnalysisRow(GraphModel):
    id: str
    related_ids: tuple[str, ...] = ()
    factors: dict[str, int | str | bool] = Field(default_factory=dict)
    path_ids: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()


class AnalysisResult(GraphModel):
    operation: str
    graph: str
    municipality_id: Literal['demo-city'] = 'demo-city'
    graph_revision: int
    as_of: str
    include_candidates: bool
    rows: tuple[AnalysisRow, ...]
    nodes: tuple[NodeRecord, ...]
    edges: tuple[EdgeRecord, ...]
    paths: tuple[ProofPath, ...]
    truncated: bool
    search_limited: bool
    gaps: tuple[str, ...]
    reservations: tuple[str, ...]
    budgets: dict[str, int | float]
    measurements: dict[str, int | float]
