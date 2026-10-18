"""B17 closed public projections; no storage properties or runtime capabilities."""
from typing import Literal
from pydantic import Field,model_validator,field_validator
from app.services.evidence.models import Model,ID,Time,Text,Hash,Observation,IncidentAttribution
from app.graph.schema import timestamp

class QueryRules(Model):
 @field_validator('limit','depth',mode='before',check_fields=False)
 @classmethod
 def query_integer(cls,value):
  if isinstance(value,str) and value.isascii() and value.isdecimal():return int(value)
  return value
 @field_validator('include_candidates',mode='before',check_fields=False)
 @classmethod
 def query_boolean(cls,value):
  if value=='true':return True
  if value=='false':return False
  return value
 @model_validator(mode='after')
 def window(self):
  after,before=getattr(self,'after',None),getattr(self,'before',None)
  if after and before and timestamp(after)>timestamp(before):raise ValueError('REVERSED_WINDOW')
  return self

class ReadFilters(QueryRules):
 limit:int=Field(default=25,ge=1,le=50)
 cursor:ID|None=None
 issue:Literal['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']|None=None
 status:ID|None=None
 department_id:ID|None=None
 after:Time|None=None
 before:Time|None=None
 investigation_id:ID|None=None
 depth:int=Field(default=2,ge=1,le=5)
 include_candidates:bool=False

# Only these fields are public on each B17 projection; the service keeps the
# existing internal superset/defaults. Models and allowlists share one definition.
RESOURCE_FIELDS=('limit','cursor','issue','status','department_id','after','before')
VIEW_QUERY_FIELDS={
 'list:Investigation':RESOURCE_FIELDS,
 'list:Complaint':RESOURCE_FIELDS,'list:Incident':RESOURCE_FIELDS,
 'list:ProblemCluster':RESOURCE_FIELDS,'list:Approval':RESOURCE_FIELDS,
 'list:WorkOrder':RESOURCE_FIELDS,'list:Department':RESOURCE_FIELDS,
 'dashboard':('issue','status','department_id','after','before'),
 'map':(*RESOURCE_FIELDS,'investigation_id'),
 'hypotheses':('limit','cursor','status'),
 'trace':('limit','cursor','status','after','before'),
 'graph':('depth','include_candidates'),'neighbors':('depth','include_candidates'),
 'asset':(),
}

def query_model(name,fields):
 from copy import deepcopy
 from pydantic import create_model
 return create_model(name,__base__=QueryRules,**{key:(ReadFilters.model_fields[key].annotation,deepcopy(ReadFilters.model_fields[key])) for key in fields})

ResourceQuery=query_model('ResourceQuery',RESOURCE_FIELDS)
DashboardQuery=query_model('DashboardQuery',VIEW_QUERY_FIELDS['dashboard'])
MapQuery=query_model('MapQuery',VIEW_QUERY_FIELDS['map'])
HypothesesQuery=query_model('HypothesesQuery',VIEW_QUERY_FIELDS['hypotheses'])
TraceQuery=query_model('TraceQuery',VIEW_QUERY_FIELDS['trace'])
GraphQuery=query_model('GraphQuery',VIEW_QUERY_FIELDS['graph'])
AssetQuery=query_model('AssetQuery',())
VIEW_QUERY_MODELS={name:ResourceQuery for name in VIEW_QUERY_FIELDS if name.startswith('list:')}
VIEW_QUERY_MODELS.update(dashboard=DashboardQuery,map=MapQuery,hypotheses=HypothesesQuery,trace=TraceQuery,graph=GraphQuery,neighbors=GraphQuery,asset=AssetQuery)
class FindingDTO(Model):
 id:ID
 evidence_id:ID
 observation:Observation
 verification_status:ID
class ObservationSource(Model):
 inspection_id:ID
 inspector_id:ID
 department_id:ID
 source_id:ID
 record_id:ID
 observed_at:Time
 recorded_at:Time
 reviewed:bool
 reviewer_id:ID|None
 attribution:IncidentAttribution|None
class GraphNode(Model):
 id:ID
 labels:list[ID]
 kind:ID
 display_label:str=Field(max_length=512)
 status:ID|None
 source_kind:ID|None
 evidence_ids:list[ID]=Field(max_length=100)
 observed_at:Time|None
class GraphEdge(Model):
 id:ID
 type:ID
 source:ID
 target:ID
 valid_from:Time|None
 valid_to:Time|None
 observed_at:Time|None
 verification_status:ID
 source_evidence_ids:list[ID]=Field(max_length=10)
class DecisionPath(Model):
 id:ID
 node_ids:list[ID]=Field(max_length=120)
 edge_ids:list[ID]=Field(max_length=200)
 evidence_ids:list[ID]=Field(max_length=100)
 execution_id:ID
class GraphSubgraphDTO(Model):
 decision_paths:list[DecisionPath]=Field(default_factory=list,max_length=100)
 nodes:list[GraphNode]=Field(max_length=120)
 edges:list[GraphEdge]=Field(max_length=200)
 decision_path_ids:list[ID]=Field(max_length=100)
 graph_revision:int=Field(ge=0)
 as_of:Time
 truncated:bool
 search_limited:Literal[True]=True
 reservations:list[Text]=Field(max_length=20)
class AssetDTO(Model):
 location_id:ID|None
 condition:ID|None
 owner_department_id:ID|None
 id:ID
 labels:list[ID]
 asset_type:ID
 name:str=Field(max_length=512)
 operational_status:ID
 department_ids:list[ID]=Field(max_length=100)
 location_ids:list[ID]=Field(max_length=100)
 incident_ids:list[ID]=Field(max_length=100)
 graph_revision:int
 as_of:Time
 geometry_status:Literal['LOCATION_REFERENCES','UNAVAILABLE']
class Point(Model):
 type:Literal['Point']='Point'
 coordinates:list[float]=Field(min_length=2,max_length=2)
class MapFeature(Model):
 type:Literal['Feature']='Feature'
 id:ID
 geometry:Point
 location_id:ID
 issue_types:list[ID]
 asset_ids:list[ID]
 incident_ids:list[ID]
 investigation_ids:list[ID]
class MapDTO(Model):
 simulation_mode:Literal[True]=True
 type:Literal['FeatureCollection']='FeatureCollection'
 features:list[MapFeature]=Field(max_length=50)
 unavailable_ids:list[ID]=Field(max_length=500)
 next_cursor:ID|None
 total_count:int=Field(ge=0,le=500)
 graph_revision:int
 as_of:Time
 truncated:bool
 limitations:list[Text]
class DashboardDTO(Model):
 active_incidents:int
 active_clusters:int
 pending_approvals:int
 completed_work_orders:int
 verified_work_orders:int
 issue_counts:dict[Literal['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION'],int]
 graph_revision:int
 as_of:Time
 definitions:list[Text]
 limitations:list[Text]
class AgentTraceEvent(Model):
 event_id:ID
 investigation_id:ID
 timestamp:Time
 agent_role:ID
 kind:Literal['DECISION','TOOL']
 tool_name:ID|None
 server_id:ID|None=None
 status:ID
 rationale_summary:Text|None
 arguments_sha256:Hash|None=None
 input_summary:Literal['values withheld']='values withheld'
 output_sha256:Hash|None=None
 validated_output:bool|None=None
 duration_ms:float|None=None
 evidence_ids:list[ID]=Field(default_factory=list,max_length=200)
 graph_path_ids:list[ID]=Field(default_factory=list,max_length=100)
 graph_revision:int|None
 error_code:ID|None=None
 execution_mode:ID
 parent_execution_id:ID|None=None
 decision_id:ID|None=None
class TraceDTO(Model):
 checkpoint_graph_revision:int|None
 refresh_required:bool
 error_codes:list[ID]=Field(max_length=160)
 items:list[AgentTraceEvent]=Field(max_length=50)
 next_cursor:ID|None
 total_count:int=Field(ge=0,le=500)
 graph_revision:int
 as_of:Time
 phase:ID|None
 pause_reason:ID|None
 recovery_required:bool
 current_agent_role:ID|None
 active_incident_ids:list[ID]
 historical_incident_ids:list[ID]
 limitations:list[Text]
class PublicPayload(Model):
 operation:ID|None=None
 execution_id:ID|None=None
 decision_id:ID|None=None
 plan_id:ID|None=None
 plan_version:int|None=None
 approval_id:ID|None=None
 task_id:ID|None=None
 new_incident_id:ID|None=None
 cluster_id:ID|None=None
 prior_outcome_id:ID|None=None
 investigates_relationship_id:ID|None=None
class SSEEvent(Model):
 event_id:ID
 timestamp:Time
 @model_validator(mode="before")
 @classmethod
 def legacy_identity(cls,value):
  if isinstance(value,dict):return {**value,"event_id":value.get("event_id",value.get("id")),"timestamp":value.get("timestamp",value.get("occurred_at"))}
  return value
 cursor:int=Field(ge=1)
 id:ID
 event_type:ID
 entity_id:ID
 investigation_id:ID|None
 revision:int=Field(ge=0)
 occurred_at:Time
 source_kind:ID
 simulation_mode:Literal['SIMULATED']
 payload_schema_version:Literal[1]
 payload:PublicPayload
 source_ref:ID

class DashboardSummary(DashboardDTO):
 open_clusters:int
 active_investigations:int
 recurrence_counts:dict[Literal['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION'],int]
 simulation_mode:Literal[True]=True
class AgentTracePage(TraceDTO):pass
class MapFeatureCollection(MapDTO):pass
class SSEStream(SSEEvent):pass
