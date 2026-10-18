"""Closed HTTP schemas adapted explicitly from accepted B08–B15 commands."""
from typing import Annotated,Literal,Generic,TypeVar
from pydantic import Field,create_model,SecretStr,model_validator
from app.services.evidence.models import Model,ID,Text,Hash,Time,OpenInvestigation,RequestInspection,TransitionInspection,ReportInspection,Propose,Assess,Observation,IncidentAttribution
from app.services.operations.models import Submit,Decide,Order,Update
from app.services.operations.execution_models import Progress,Evaluate,Recur
from app.services.planning.models import PlanDraft,PlanReceipt
from app.services.complaints.models import WaterIntake,RoadIntake,WasteIntake
from app.memory.models import Citation

def transport(cls,name,exclude):
 # Preserve nested accepted types and all constraints via original FieldInfo copies.
 from copy import deepcopy
 fields={k:(f.annotation,deepcopy(f)) for k,f in cls.model_fields.items() if k not in exclude}
 return create_model(name,__base__=Model,**fields)
OpenRequest=transport(OpenInvestigation,'OpenRequest',{'operation','request_id'})
InspectionRequest=transport(RequestInspection,'InspectionRequest',{'operation','request_id'})
TransitionRequest=transport(TransitionInspection,'TransitionRequest',{'operation','request_id','inspection_id'})
ReportRequest=transport(ReportInspection,'ReportRequest',{'operation','request_id','inspection_id','review'})
ProposeRequest=transport(Propose,'ProposeRequest',{'operation','request_id','investigation_id'})
AssessRequest=transport(Assess,'AssessRequest',{'operation','request_id','hypothesis_id'})
SubmitRequest=transport(Submit,'SubmitRequest',{'operation','request_id','plan_id'})
DecideRequest=transport(Decide,'DecideRequest',{'operation','request_id','approval_id'})
OrderRequest=transport(Order,'OrderRequest',{'operation','request_id'})
UpdateRequest=transport(Update,'UpdateRequest',{'operation','request_id','work_order_id'})
ProgressRequest=transport(Progress,'ProgressRequest',{'operation','request_id','work_order_id'})
EvaluateRequest=transport(Evaluate,'EvaluateRequest',{'operation','request_id','work_order_id'})
RecurRequest=transport(Recur,'RecurRequest',{'operation','request_id','work_order_id'})
Intake=Annotated[WaterIntake|RoadIntake|WasteIntake,Field(discriminator='issue_type')]
# Recurrence complaint uses the same strict accepted B08 union, not an open dict.
RecurRequest=create_model('RecurRequest',__base__=RecurRequest,complaint=(Intake,...))
class ComplaintRequest(Model):
 complaint:Intake
class DraftRequest(Model):
 draft:PlanDraft
class ResumeRequest(Model):
 reason:Text
class LoginRequest(Model):
 operator_id:ID
 demo_password:SecretStr=Field(min_length=1,max_length=256)
class EmptyRequest(Model):pass
WorkInspectionCreate=transport(RequestInspection,'WorkInspectionCreate',{'request_id'})
WorkInspectionTransition=transport(TransitionInspection,'WorkInspectionTransition',{'request_id'})
WorkInspectionReport=transport(ReportInspection,'WorkInspectionReport',{'request_id','review'})
WorkAssessment=transport(Assess,'WorkAssessment',{'request_id'})
class WorkInspectionRequest(Model):
 expected_hash:Hash
 purpose:Literal['COMPLETION','FOLLOWUP','ASSESSMENT']
 command:Annotated[WorkInspectionCreate|WorkInspectionTransition|WorkInspectionReport|WorkAssessment,Field(discriminator='operation')]
 review_reason:Text|None=None
class Ack(Model):status:ID
class OperatorAccount(Model):
 id:ID
 display_name:ID
 role:Literal['ANALYST','DEPARTMENT_LEAD','APPROVER','ADMIN']
 department_id:ID
 enabled:Literal[True]=True
class DemoSession(Model):
 access_token:str
 expires_at:Time
 operator_id:ID
 role:ID
class HealthDTO(Model):
 status:Literal['ok','unavailable']
 dependencies:dict[str,Literal['ready','unavailable','not_checked']]
 runtime_mode:Literal['DETERMINISTIC_DEVELOPMENT_NO_PROVIDER']='DETERMINISTIC_DEVELOPMENT_NO_PROVIDER'
class Resource(Model):
 id:ID
 expected_hash:Hash
 simulated:Literal[True]=True
class ComplaintDTO(Resource):
 description:str=Field(max_length=4000)
 incident_id:ID|None
 reported_at:Time
 source_kind:ID
 status:ID
 issue_type:ID
class IncidentDTO(Resource):
 issue_type:ID
 subtype:ID
 location_id:ID|None
 started_at:Time
 ended_at:Time|None
 status:ID
 cluster_id:ID|None
 complaint_ids:list[ID]=Field(max_length=100)
class ProblemClusterDTO(Resource):
 pattern_type:ID
 status:ID
 incident_ids:list[ID]=Field(max_length=100)
 related_asset_ids:list[ID]=Field(max_length=100)
 monitoring_status:ID
class InvestigationDTO(Resource):
 status:ID
 incident_ids:list[ID]=Field(max_length=3)
 historical_incident_ids:list[ID]=Field(max_length=3)
 problem_cluster_id:ID|None
 current_agent_role:ID|None=None
 active_hypothesis_ids:list[ID]=Field(max_length=100)
 pending_inspection_ids:list[ID]=Field(max_length=100)
 current_plan_id:ID|None
 next_action:Literal['DURABLE_WORKER_OR_HUMAN_REVIEW']='DURABLE_WORKER_OR_HUMAN_REVIEW'
 graph_revision:int
 runtime_status:Literal['DETERMINISTIC_DEVELOPMENT_ONLY_NO_LIVE_AUTHORIZATION']='DETERMINISTIC_DEVELOPMENT_ONLY_NO_LIVE_AUTHORIZATION'
class AgentResumeDTO(Model):
 investigation_id:ID
 accepted:Literal[True]=True
 event_id:ID
 status:ID
from .view_models import FindingDTO,ObservationSource
from app.services.service_evidence import ServiceRecord
class EvidenceDTO(Resource):
 service_record:ServiceRecord|None=Field(default=None,exclude_if=lambda value:value is None)
 findings:list[FindingDTO]=Field(default_factory=list,max_length=10)
 observation_source:ObservationSource|None=None
 limitations:list[Text]=Field(default_factory=list,max_length=10)
 evidence_type:ID
 summary:Text
 source_kind:ID
 source_record_id:ID|None
 reliability:ID
 observed_at:Time|None
 recorded_at:Time
 document_id:ID|None
 finding_ids:list[ID]=Field(default_factory=list,max_length=100)
 reviewed:bool
class InspectionDTO(Resource):
 status:ID
 asset_ids:list[ID]=Field(max_length=100)
 department_id:ID
 requested_at:Time
 scheduled_at:Time|None
 completed_at:Time|None
 assigned_inspector_id:ID|None
 evidence_ids:list[ID]=Field(max_length=100)
class AssessmentSummary(Model):
 id:ID
 previous_assessment_id:ID|None
 assessment:ID
 assessed_at:Time
 supporting_evidence_ids:list[ID]=Field(max_length=100)
 contradicting_evidence_ids:list[ID]=Field(max_length=100)
 missing_evidence:list[str]=Field(max_length=100)
 current:bool
class HypothesisDTO(Resource):
 statement:Text
 cause_code:ID
 status:ID
 current_assessment_id:ID|None
 assessment_history:list[AssessmentSummary]=Field(max_length=100)
 supporting_evidence_ids:list[ID]=Field(max_length=100)
 contradicting_evidence_ids:list[ID]=Field(max_length=100)
 missing_evidence:list[str]=Field(max_length=100)
 suspected_asset_ids:list[ID]=Field(max_length=100)
class PlanTaskBinding(Model):
 local_task_id:ID
 task_id:ID
 action_type:ID
 target_ids:list[ID]=Field(min_length=1,max_length=5)
 department_id:ID
 depends_on_task_ids:list[ID]=Field(max_length=12)
 status:ID
 expected_hash:Hash
 eligible_assignee_ids:list[ID]=Field(max_length=7)
class PlanDTO(Model):
 task_bindings:list[PlanTaskBinding]=Field(default_factory=list,max_length=12,description='Validated persisted task IDs and scope; eligible synthetic assignees are choices, never approval or execution authority')
 plan_id:ID
 investigation_id:ID
 version:int
 content_hash:Hash
 draft:PlanDraft
 draft_receipt:PlanReceipt
 status:ID
 expected_hash:Hash
 approval_status:ID|None=Field(description="Legacy audited plan lifecycle state; ApprovalDTO.status is the actual approval decision")
 execution_gates_verified:Literal[False]=False
 simulated:Literal[True]=True
 limitations:list[Text]=Field(max_length=10)
class ApprovalDTO(Resource):
 plan_id:ID
 plan_version:int
 plan_hash:Hash
 assignments:list[__import__('app.services.operations.models',fromlist=['Assignment']).Assignment]
 status:ID
 approved_by:ID|None
 requested_at:Time
 scope_hash:Hash
class WorkOrderDTO(Resource):
 status:ID
 task_id:ID
 plan_id:ID
 department_id:ID
 assignee_id:ID
 execution_mode:Literal['SIMULATED']='SIMULATED'
 authorized_by:ID
 status_event_ids:list[ID]=Field(max_length=100)
 resolution_verified:bool=False
 latest_assessment_status:ID|None=None
 limitations:list[Text]=Field(default_factory=lambda:['Work completion alone does not establish resolution'],max_length=10)
class OutcomeDTO(Model):
 id:ID
 work_order_id:ID
 assessment_status:ID
 result:ID
 evidence_ids:list[ID]=Field(max_length=20)
 evaluated_at:Time
 case_closed:bool
 policy_version:ID|None
 simulated:Literal[True]=True
class DepartmentDTO(Resource):
 name:ID
 department_type:ID
class DocumentDTO(Model):
 id:ID
 title:ID
 source_kind:Literal['SYNTHETIC']='SYNTHETIC'
 version:int
 sha256:Hash
 owner_department_id:ID
 citations:list[Citation]=Field(max_length=5)
 gaps:list[str]=Field(max_length=100)
 assertion_status:Literal['PROPOSED']='PROPOSED'
 trusted_as_instructions:Literal[False]=False
class ProcedureDTO(DocumentDTO):
 procedure_id:ID
 effective_from:Time
class CaseMemoryDTO(Model):
 id:ID
 source_investigation_id:ID|None
 outcome_ids:list[ID]=Field(max_length=100)
 evidence_ids:list[ID]=Field(default_factory=list,max_length=100)
 gaps:list[str]=Field(default_factory=list,max_length=100)
 truncated:bool=False
 memory_type:Literal['RECORDED_CASE_CONTEXT']='RECORDED_CASE_CONTEXT'
 summary:Literal['Stored historical context; absent records are evidence gaps']='Stored historical context; absent records are evidence gaps'
class MonitoringDTO(Model):
 problem_cluster_id:ID
 status:ID
 verification_policy:ID
 remaining_checks:list[str]=Field(max_length=20)
 outcome_evidence_ids:list[ID]=Field(max_length=100)
T=TypeVar('T')
class Page(Model,Generic[T]):
 items:list[T]=Field(max_length=50)
 next_cursor:ID|None
 total_count:int=Field(ge=0,le=500)
 limitations:list[str]=Field(default_factory=list,max_length=100)
 truncated:bool=False
class Success(Model,Generic[T]):
 data:T
 request_id:ID
 schema_version:Literal[1]=1
class ErrorDetails(Model):
 blocker_code:ID|None=None
 correlation_id:ID|None=None
 commitment:Literal['UNKNOWN']|None=None
 entity_id:ID|None=None
 investigation_id:ID|None=None
 plan_id:ID|None=None
 request_id:ID|None=None
class ErrorBody(Model):
 code:ID
 message:Text
 details:ErrorDetails=Field(default_factory=ErrorDetails)
 retryable:bool=False
class ErrorEnvelope(Model):
 error:ErrorBody
 request_id:ID

# B17 projections share the same closed, strict public model base.
from .view_models import (ReadFilters,FindingDTO,ObservationSource,GraphSubgraphDTO,AssetDTO,MapDTO,DashboardDTO,AgentTraceEvent,TraceDTO,SSEEvent)

from .view_models import DashboardSummary,AgentTracePage,MapFeatureCollection,SSEStream
class HypothesisPage(Page[HypothesisDTO]):pass

# B19 closed scenario controls/projections.
from app.services.demo.models import DemoResetRequest,DemoAdvanceRequest,SeedReport,SimulationStepDTO,ScenarioPage

# Explicit operator-only responsibility acquisition; no MCP write tool.
from app.services.responsibility.models import Submission as ResponsibilitySubmission,Review as ResponsibilityReview,ResponsibilityDTO
