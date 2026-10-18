"""Preapproved bounded raw-fact templates; not B05 decision-grade analysis."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator, ValidationInfo
from app.graph.schema import Registry, timestamp
from app.graph.queries import GraphQueries
from .runtime import CITY_GRAPH

ALLOWED = frozenset({'query_graph_readonly', 'get_graph_schema', 'get_node_schema', 'get_relationship_schema'})
NODE_QUERY = 'MATCH (n:CivicEntity {id:$id,municipality_id:$scope}) RETURN labels(n) AS labels,properties(n) AS properties LIMIT 1'
_key = GraphQueries._time_key  # Reuse accepted B03 UTC precision normalization.
EDGE_QUERY = f'''MATCH (a:InfrastructureAsset {{id:$id,municipality_id:$scope}})-[r:DRAINS_TO]->(b:InfrastructureAsset {{municipality_id:$scope}})
WHERE r.municipality_id=$scope AND {_key('r.created_at')}<=$as_of
AND (r.valid_from IS NULL OR {_key('r.valid_from')}<=$as_of) AND (r.valid_to IS NULL OR $as_of<{_key('r.valid_to')})
RETURN a.id AS source_id,labels(a) AS source_labels,b.id AS target_id,labels(b) AS target_labels,type(r) AS relationship,properties(r) AS properties LIMIT 101'''
REVISION_QUERY = 'MATCH (m:CivicSchemaMigration {id:$id}) RETURN m.repo_revision AS revision,m.repo_pending AS pending,m.state AS state LIMIT 1'


class Request(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True, hide_input_in_errors=True)
    tool: Literal['query_graph_readonly', 'get_graph_schema', 'get_node_schema', 'get_relationship_schema']
    graph: str = CITY_GRAPH
    template: Literal['node', 'drainage_edges'] | None = None
    id: str | None = Field(default=None, min_length=1, max_length=200)
    as_of: str | None = None
    label: str | None = None
    relationship_type: str | None = None
    sample_size: int = Field(default=20, ge=1, le=100)

    @model_validator(mode='after')
    def exact_arguments(self, info: ValidationInfo):
        if self.graph != (info.context or {}).get('authorized_graph', CITY_GRAPH):
            raise ValueError('Graph is not authorized')
        registry = Registry()
        if self.tool == 'query_graph_readonly':
            if self.template is None or self.id is None or self.label is not None or self.relationship_type is not None:
                raise ValueError('Template arguments required')
            if self.template == 'drainage_edges':
                if self.as_of is None: raise ValueError('Explicit UTC as_of required')
                timestamp(self.as_of)
            elif self.as_of is not None: raise ValueError('Node lookup is current-state only')
        elif self.template is not None or self.id is not None or self.as_of is not None:
            raise ValueError('Schema tool does not accept query arguments')
        if self.tool == 'get_node_schema':
            if self.label not in registry.nodes or self.relationship_type is not None: raise ValueError('Invalid public node type')
        elif self.label is not None: raise ValueError('Unexpected node label')
        if self.tool == 'get_relationship_schema':
            if self.relationship_type not in registry.edges: raise ValueError('Invalid public relationship type')
        elif self.relationship_type is not None: raise ValueError('Unexpected relationship type')
        return self

    def arguments(self):
        args = {'graphName': self.graph}
        if self.tool == 'query_graph_readonly':
            args.update(query=NODE_QUERY if self.template == 'node' else EDGE_QUERY,
                        params={'id': self.id, 'scope': 'demo-city'})
            if self.as_of is not None: args['params']['as_of'] = timestamp(self.as_of).strftime('%Y-%m-%dT%H:%M:%S.%f')
        elif self.tool == 'get_graph_schema':
            args.update(includeConnections=True, connectionSampleSize=100)
        elif self.tool == 'get_node_schema':
            args.update(label=self.label, sampleSize=self.sample_size)
        else: args.update(relationshipType=self.relationship_type, sampleSize=self.sample_size)
        return args
