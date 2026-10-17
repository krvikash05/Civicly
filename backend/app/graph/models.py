"""Serializable public graph records; internal numeric IDs never leave the adapter."""

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

from app.graph.schema import timestamp


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


class GraphModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class NodeRecord(GraphModel):
    id: str
    kind: str
    labels: tuple[str, ...]
    properties: dict[str, JsonValue]

    @property
    def content_hash(self) -> str:
        return digest({"kind": self.kind, "properties": self.properties})


class EdgeRecord(GraphModel):
    id: str
    kind: str
    source: str
    target: str
    properties: dict[str, JsonValue]

    @property
    def content_hash(self) -> str:
        return digest(self.model_dump(mode="json"))


class PathRecord(GraphModel):
    node_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    directions: tuple[Literal["OUTGOING", "INCOMING"], ...]
    evidence_ids: tuple[str, ...]
    context: dict[str, JsonValue] = Field(default_factory=dict)


class QueryRequest(GraphModel):
    template: Literal["drainage_paths", "shared_infrastructure", "incident_history", "maintenance_history",
                      "cross_category_paths", "hypothesis_evidence", "ownership_dependencies", "task_dependencies"]
    id: str = Field(default="", max_length=512)
    incident_ids: tuple[str, ...] = ()
    as_of: str
    after: str | None = None
    direction: Literal["upstream", "downstream"] = "downstream"
    max_hops: int = Field(default=6, ge=1, le=6)
    limit: int = Field(default=40, ge=1, le=100)
    timeout_ms: int = Field(default=1000, ge=1, le=1000)
    include_candidates: bool = False

    @field_validator("as_of", "after")
    @classmethod
    def check_time(cls, value):
        if value is not None:
            timestamp(value)
        return value

    @field_validator("incident_ids")
    @classmethod
    def check_incidents(cls, value):
        if len(value) > 50 or any(not item.strip() or len(item) > 512 for item in value):
            raise ValueError("Incident list exceeds query budget")
        return value


class QueryBudget(GraphModel):
    requested_total_hops: int
    effective_total_hops: int
    template_min_hops: int
    template_max_hops: int
    fixed_connector_hops: int | None
    infrastructure_hops: int | None


class GraphResult(GraphModel):
    template: str
    municipality_id: Literal["demo-city"] = "demo-city"
    as_of: str
    graph_revision: int
    nodes: tuple[NodeRecord, ...]
    edges: tuple[EdgeRecord, ...]
    paths: tuple[PathRecord, ...]
    truncated: bool
    search_limited: bool
    search_budget: QueryBudget
    reservations: tuple[str, ...]
