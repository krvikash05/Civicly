"""Validated official-server projections; no B07 domain-result envelope change."""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True, hide_input_in_errors=True)


class NodeRow(Model):
    labels: list[str]
    properties: dict[str, Any]


class EdgeRow(Model):
    source_id: str
    source_labels: list[str]
    target_id: str
    target_labels: list[str]
    relationship: Literal['DRAINS_TO']
    properties: dict[str, Any]


class RevisionRow(Model):
    revision: int = Field(ge=0)
    pending: str | None
    state: Literal['READY']


class QueryPayload(Model):
    metadata: list[str]
    data: list[dict[str, Any]]


class Connection(Model):
    source: list[str]
    relationship: str
    target: list[str]


class GraphSchema(Model):
    nodeLabels: list[str]
    relationshipTypes: list[str]
    connections: list[Connection]
    connectionSampleSize: int = Field(ge=1, le=100)


class PropertyFrequency(Model):
    property: str
    frequency: int = Field(ge=1, le=100)


class NodeSchema(Model):
    label: str
    requestedSampleSize: int = Field(ge=1, le=100)
    sampledCount: int = Field(ge=0, le=100)
    properties: list[PropertyFrequency]


class RelationshipSchema(Model):
    relationshipType: str
    requestedSampleSize: int = Field(ge=1, le=100)
    sampledCount: int = Field(ge=0, le=100)
    properties: list[PropertyFrequency]


class ReadResult(Model):
    graph: str
    tool: str
    template: str | None
    graph_revision: int
    rows: list[NodeRow] | list[EdgeRow] | None = None
    schema_data: GraphSchema | NodeSchema | RelationshipSchema | None = None
    truncated: bool = False
    search_limited: bool = True
    semantics: str = 'Raw recorded synthetic facts; no causal finding. Schema samples are incomplete; node lookup is current-state, edge validity is half-open with unknown/open dates.'
