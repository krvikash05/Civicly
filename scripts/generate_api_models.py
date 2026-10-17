#!/usr/bin/env python3
"""Define minimum formal API JSON Schemas for implementation; generated Pydantic must validate these shapes."""
import json,pathlib,re
root=pathlib.Path(__file__).resolve().parents[1]
end=json.loads((root/'contracts/api_endpoints.json').read_text())
def S(**props):return {'type':'object','properties':props,'required':list(props),'additionalProperties':False}
def string():return {'type':'string'}
def optstr():return {'type':['string','null']}
def integer():return {'type':'integer'}
def bool_():return {'type':'boolean'}
def arr(item=None):return {'type':'array','items':item or string()}
def obj():return {'type':'object','additionalProperties':True}
def page(item):return S(items=arr({'$ref':f'#/$defs/{item}'}),next_cursor=optstr(),total_count=integer())
D={
 'Ack':S(status=string()),
 'DemoSession':S(access_token=string(),expires_at=string(),operator_id=string(),role=string()),
 'OperatorAccount':S(id=string(),display_name=string(),role=string(),department_id=string(),enabled=bool_()),
 'HealthDTO':S(status=string(),dependencies=obj()),
 'DashboardSummary':S(open_clusters=integer(),active_investigations=integer(),pending_approvals=integer(),recurrence_counts=obj(),simulation_mode=bool_()),
 'ComplaintDTO':S(id=string(),description=string(),incident_id=optstr(),reported_at=string(),source_kind=string(),status=string(),issue_type=string()),
 'IncidentDTO':S(id=string(),issue_type=string(),subtype=string(),location_id=string(),started_at=string(),status=string(),cluster_id=optstr(),complaint_ids=arr()),
 'ProblemClusterDTO':S(id=string(),pattern_type=string(),status=string(),incident_ids=arr(),related_asset_ids=arr(),monitoring_status=string()),
 'InvestigationDTO':S(id=string(),status=string(),incident_ids=arr(),problem_cluster_id=optstr(),current_agent_role=optstr(),active_hypothesis_ids=arr(),pending_inspection_ids=arr(),current_plan_id=optstr(),next_action=optstr(),graph_revision=string(),simulation_mode=bool_()),
 'AgentResumeDTO':S(investigation_id=string(),accepted=bool_(),event_id=string()),
 'EvidenceDTO':S(id=string(),evidence_type=string(),summary=string(),source_kind=string(),source_record_id=optstr(),reliability=string(),observed_at=optstr(),recorded_at=string(),document_id=optstr(),simulated=bool_()),
 'InspectionDTO':S(id=string(),status=string(),asset_ids=arr(),requested_at=string(),assigned_inspector_id=optstr(),evidence_ids=arr()),
 'HypothesisDTO':S(id=string(),statement=string(),cause_code=string(),status=string(),assessment_history=arr(obj()),supporting_evidence_ids=arr(),contradicting_evidence_ids=arr(),missing_evidence=arr(),suspected_asset_ids=arr()),
 'PlanDTO':S(plan_id=string(),investigation_id=string(),version=integer(),content_hash=string(),tasks=arr(obj()),dependencies=arr(obj()),status=string(),simulated=bool_(),monitoring_criteria=arr(obj()),supporting_evidence_ids=arr()),
 'ApprovalDTO':S(id=string(),plan_id=string(),plan_version=integer(),plan_hash=string(),status=string(),approved_by=optstr(),requested_at=string()),
 'WorkOrderDTO':S(id=string(),status=string(),task_id=string(),plan_id=string(),department_id=string(),execution_mode=string(),authorized_by=string(),status_event_ids=arr()),
 'OutcomeDTO':S(id=string(),work_order_id=string(),assessment_status=string(),result=string(),evidence_ids=arr(),evaluated_at=string()),
 'DepartmentDTO':S(id=string(),name=string(),department_type=string()),
 'ProcedureDTO':S(id=string(),title=string(),version=integer(),source_document_id=string(),effective_from=string(),owning_department_id=string(),excerpt=string()),
 'DocumentDTO':S(id=string(),title=string(),source_kind=string(),content_ref=string(),version=integer(),sha256=string(),excerpt=string()),
 'CaseMemoryDTO':S(id=string(),summary=string(),source_investigation_id=string(),outcome_ids=arr(),corrections=arr(obj()),memory_type=string()),
 'AssetDTO':S(id=string(),asset_type=string(),name=string(),location_id=optstr(),condition=string(),owner_department_id=optstr()),
 'GraphNodeDTO':S(id=string(),labels=arr(),display_label=string(),kind=string(),status=string(),source_kind=string(),evidence_ids=arr()),
 'GraphEdgeDTO':S(id=string(),type=string(),source=string(),target=string(),verification_status=string(),source_evidence_ids=arr(),valid_from=optstr(),valid_to=optstr()),
 'GraphSubgraphDTO':S(nodes=arr({'$ref':'#/$defs/GraphNodeDTO'}),edges=arr({'$ref':'#/$defs/GraphEdgeDTO'}),decision_path_ids=arr(),graph_revision=string(),truncated=bool_(),as_of=string()),
 'AgentTraceEvent':S(event_id=string(),investigation_id=string(),timestamp=string(),agent_role=string(),state=string(),tool_name=optstr(),rationale_summary=string(),status=string(),source_evidence_ids=arr(),graph_revision=string(),simulation_mode=bool_()),
 'SSEStream':S(event_id=string(),event_type=string(),timestamp=string(),payload=obj()),
 'MapFeatureCollection':S(type={'type':'string','const':'FeatureCollection'},features=arr(obj()),simulation_mode=bool_()),
 'MonitoringDTO':S(problem_cluster_id=string(),status=string(),verification_policy=string(),remaining_checks=arr(),outcome_evidence_ids=arr()),
 'SimulationStepDTO':S(scenario_id=string(),stage=string(),event_id=string(),revealed_evidence_ids=arr()),
 'SeedReport':S(nodes=integer(),relationships=integer(),source_documents=integer(),seed_fingerprint=string()),
 'ScenarioDTO':S(id=string(),title=string(),issue_types=arr(),stage=string())
}
for name,item in [('ComplaintPage','ComplaintDTO'),('IncidentPage','IncidentDTO'),('ClusterPage','ProblemClusterDTO'),('AgentTracePage','AgentTraceEvent'),('HypothesisPage','HypothesisDTO'),('ApprovalPage','ApprovalDTO'),('WorkOrderPage','WorkOrderDTO'),('DepartmentPage','DepartmentDTO'),('ProcedurePage','ProcedureDTO'),('CaseMemoryPage','CaseMemoryDTO'),('MonitoringPage','MonitoringDTO'),('OutcomePage','OutcomeDTO'),('ScenarioPage','ScenarioDTO')]: D[name]=page(item)
# requests for all POST routes. Explicit high-stakes fields; empty object only for logout.
REQ={
'/auth/demo-login':S(operator_id=string(),demo_password=string()),
'/auth/logout':{'type':'object','properties':{},'additionalProperties':False},
'/complaints':S(description=string(),issue_type=string(),location_id=string(),reported_at=string(),source_kind=string()),
'/investigations':S(incident_ids=arr(),problem_cluster_id=optstr(),requested_by=string()),
'/investigations/{id}/resume':S(reason=string(),expected_graph_revision=optstr()),
'/inspections/{id}/observations':S(asset_id=string(),observed_at=string(),observation_type=string(),value=obj(),source_kind=string(),submitted_by=string()),
'/plans/{id}/submit-approval':S(plan_id=string(),plan_version=integer(),plan_hash=string(),requested_by=string()),
'/approvals/{id}/decision':S(decision={'type':'string','enum':['APPROVED','REJECTED']},plan_id=string(),plan_version=integer(),plan_hash=string(),reason=optstr()),
'/work-orders/{id}/status':S(new_status=string(),expected_revision=string(),evidence_ids=arr(),note=optstr()),
'/work-orders/{id}/outcomes':S(result=string(),evidence_ids=arr(),observed_at=string()),
'/demo/reset':S(scenario_id=string(),seed=integer(),confirm=bool_()),
'/demo/scenarios/{id}/advance':S(stage=string(),expected_current_stage=string())
}
for route in end['routes']:
 if route['method']!='POST':continue
 path=route['path'].replace('/api/v1','')
 if path not in REQ:raise ValueError(f'missing POST request schema {path}')
 D[route['request_schema_id']]=REQ[path]
 if route['response_dto'] not in D:raise ValueError(f'unknown response {route["response_dto"]}')
for route in end['routes']:
 if route['response_dto'] not in D:raise ValueError(f'missing {route["response_dto"]}')
res={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Civicly REST contracts','description':'Machine-readable expected field contracts. Codex implements Pydantic models and generated OpenAPI, validates endpoints and extends optional fields via ADR and tests.','schema_version':2,'$defs':D,'error_envelope':S(error=S(code=string(),message=string(),retryable=bool_(),details=obj()),request_id=string()),'success_envelope':{'type':'object','required':['data','request_id','schema_version'],'properties':{'data':{},'request_id':string(),'schema_version':integer()}}}
(root/'contracts/api_models.json').write_text(json.dumps(res,indent=2)+'\n')
print('Created',len(D),'typed DTO/request shapes covering',len(end['routes']),'routes')
