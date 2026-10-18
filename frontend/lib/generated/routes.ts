/* Generated from Civicly contracts. Run npm run generate:api. Do not edit. */
import type {ApiModels} from './models';
export const routes = {
  "POST /api/v1/auth/demo-login": {
    "method": "POST",
    "path": "/api/v1/auth/demo-login",
    "role": "PUBLIC",
    "response_dto": "DemoSession",
    "idempotency_key": false,
    "request_schema_id": "LoginRequest",
    "response_schema_id": "DemoSession",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "GET /api/v1/auth/me": {
    "method": "GET",
    "path": "/api/v1/auth/me",
    "role": "ANY",
    "response_dto": "OperatorAccount",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "OperatorAccount",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "POST /api/v1/auth/logout": {
    "method": "POST",
    "path": "/api/v1/auth/logout",
    "role": "ANY",
    "response_dto": "Ack",
    "idempotency_key": false,
    "request_schema_id": "EmptyRequest",
    "response_schema_id": "Ack",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "GET /api/v1/dashboard/summary": {
    "method": "GET",
    "path": "/api/v1/dashboard/summary",
    "role": "ANY",
    "response_dto": "DashboardSummary",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "DashboardSummary",
    "milestone": "B17",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "issue",
      "status",
      "department_id",
      "after",
      "before"
    ],
    "query_schema_id": "DashboardQuery"
  },
  "POST /api/v1/complaints": {
    "method": "POST",
    "path": "/api/v1/complaints",
    "role": "ANALYST",
    "response_dto": "ComplaintDTO",
    "idempotency_key": true,
    "request_schema_id": "ComplaintRequest",
    "response_schema_id": "ComplaintDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "GET /api/v1/complaints": {
    "method": "GET",
    "path": "/api/v1/complaints",
    "role": "ANY",
    "response_dto": "Page[ComplaintDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[ComplaintDTO]",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor",
      "issue",
      "status",
      "department_id",
      "after",
      "before"
    ],
    "query_schema_id": "ResourceQuery"
  },
  "GET /api/v1/complaints/{id}": {
    "method": "GET",
    "path": "/api/v1/complaints/{id}",
    "role": "ANY",
    "response_dto": "ComplaintDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "ComplaintDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "GET /api/v1/incidents": {
    "method": "GET",
    "path": "/api/v1/incidents",
    "role": "ANY",
    "response_dto": "Page[IncidentDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[IncidentDTO]",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor",
      "issue",
      "status",
      "department_id",
      "after",
      "before"
    ],
    "query_schema_id": "ResourceQuery"
  },
  "GET /api/v1/incidents/{id}": {
    "method": "GET",
    "path": "/api/v1/incidents/{id}",
    "role": "ANY",
    "response_dto": "IncidentDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "IncidentDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "GET /api/v1/problem-clusters": {
    "method": "GET",
    "path": "/api/v1/problem-clusters",
    "role": "ANY",
    "response_dto": "Page[ProblemClusterDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[ProblemClusterDTO]",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor",
      "issue",
      "status",
      "department_id",
      "after",
      "before"
    ],
    "query_schema_id": "ResourceQuery"
  },
  "GET /api/v1/problem-clusters/{id}": {
    "method": "GET",
    "path": "/api/v1/problem-clusters/{id}",
    "role": "ANY",
    "response_dto": "ProblemClusterDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "ProblemClusterDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "POST /api/v1/investigations": {
    "method": "POST",
    "path": "/api/v1/investigations",
    "role": "ANALYST",
    "response_dto": "InvestigationDTO",
    "idempotency_key": true,
    "request_schema_id": "OpenRequest",
    "response_schema_id": "InvestigationDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "GET /api/v1/investigations/{id}": {
    "method": "GET",
    "path": "/api/v1/investigations/{id}",
    "role": "ANY",
    "response_dto": "InvestigationDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "InvestigationDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "POST /api/v1/investigations/{id}/resume": {
    "method": "POST",
    "path": "/api/v1/investigations/{id}/resume",
    "role": "ANALYST",
    "response_dto": "AgentResumeDTO",
    "idempotency_key": true,
    "request_schema_id": "ResumeRequest",
    "response_schema_id": "AgentResumeDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "GET /api/v1/investigations/{id}/trace": {
    "method": "GET",
    "path": "/api/v1/investigations/{id}/trace",
    "role": "ANY",
    "response_dto": "AgentTracePage",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "AgentTracePage",
    "milestone": "B17",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor",
      "status",
      "after",
      "before"
    ],
    "query_schema_id": "TraceQuery"
  },
  "GET /api/v1/investigations/{id}/hypotheses": {
    "method": "GET",
    "path": "/api/v1/investigations/{id}/hypotheses",
    "role": "ANY",
    "response_dto": "HypothesisPage",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "HypothesisPage",
    "milestone": "B17",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor",
      "status"
    ],
    "query_schema_id": "HypothesesQuery"
  },
  "GET /api/v1/investigations/{id}/graph": {
    "method": "GET",
    "path": "/api/v1/investigations/{id}/graph",
    "role": "ANY",
    "response_dto": "GraphSubgraphDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "GraphSubgraphDTO",
    "milestone": "B17",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "depth",
      "include_candidates"
    ],
    "query_schema_id": "GraphQuery"
  },
  "GET /api/v1/evidence/{id}": {
    "method": "GET",
    "path": "/api/v1/evidence/{id}",
    "role": "ANY",
    "response_dto": "EvidenceDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "EvidenceDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "GET /api/v1/inspections/{id}": {
    "method": "GET",
    "path": "/api/v1/inspections/{id}",
    "role": "ANY",
    "response_dto": "InspectionDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "InspectionDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "POST /api/v1/inspections/{id}/observations": {
    "method": "POST",
    "path": "/api/v1/inspections/{id}/observations",
    "role": "DEPARTMENT_LEAD",
    "response_dto": "EvidenceDTO",
    "idempotency_key": true,
    "request_schema_id": "ReportRequest",
    "response_schema_id": "EvidenceDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "GET /api/v1/plans/{id}": {
    "method": "GET",
    "path": "/api/v1/plans/{id}",
    "role": "ANY",
    "response_dto": "PlanDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "PlanDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "POST /api/v1/plans/{id}/submit-approval": {
    "method": "POST",
    "path": "/api/v1/plans/{id}/submit-approval",
    "role": "ANALYST",
    "response_dto": "ApprovalDTO",
    "idempotency_key": true,
    "request_schema_id": "SubmitRequest",
    "response_schema_id": "ApprovalDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "GET /api/v1/approvals": {
    "method": "GET",
    "path": "/api/v1/approvals",
    "role": "APPROVER",
    "response_dto": "Page[ApprovalDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[ApprovalDTO]",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor",
      "issue",
      "status",
      "department_id",
      "after",
      "before"
    ],
    "query_schema_id": "ResourceQuery"
  },
  "POST /api/v1/approvals/{id}/decision": {
    "method": "POST",
    "path": "/api/v1/approvals/{id}/decision",
    "role": "APPROVER",
    "response_dto": "ApprovalDTO",
    "idempotency_key": true,
    "request_schema_id": "DecideRequest",
    "response_schema_id": "ApprovalDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "GET /api/v1/work-orders": {
    "method": "GET",
    "path": "/api/v1/work-orders",
    "role": "ANY",
    "response_dto": "Page[WorkOrderDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[WorkOrderDTO]",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor",
      "issue",
      "status",
      "department_id",
      "after",
      "before"
    ],
    "query_schema_id": "ResourceQuery"
  },
  "GET /api/v1/work-orders/{id}": {
    "method": "GET",
    "path": "/api/v1/work-orders/{id}",
    "role": "ANY",
    "response_dto": "WorkOrderDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "WorkOrderDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "POST /api/v1/work-orders/{id}/status": {
    "method": "POST",
    "path": "/api/v1/work-orders/{id}/status",
    "role": "DEPARTMENT_LEAD",
    "response_dto": "WorkOrderDTO",
    "idempotency_key": true,
    "request_schema_id": "UpdateRequest",
    "response_schema_id": "WorkOrderDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "POST /api/v1/work-orders/{id}/outcomes": {
    "method": "POST",
    "path": "/api/v1/work-orders/{id}/outcomes",
    "role": "ANALYST",
    "response_dto": "OutcomeDTO",
    "idempotency_key": true,
    "request_schema_id": "EvaluateRequest",
    "response_schema_id": "OutcomeDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "GET /api/v1/departments": {
    "method": "GET",
    "path": "/api/v1/departments",
    "role": "ANY",
    "response_dto": "Page[DepartmentDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[DepartmentDTO]",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor",
      "issue",
      "status",
      "department_id",
      "after",
      "before"
    ],
    "query_schema_id": "ResourceQuery"
  },
  "GET /api/v1/procedures": {
    "method": "GET",
    "path": "/api/v1/procedures",
    "role": "ANY",
    "response_dto": "Page[ProcedureDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[ProcedureDTO]",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor"
    ]
  },
  "GET /api/v1/documents/{id}": {
    "method": "GET",
    "path": "/api/v1/documents/{id}",
    "role": "ANY",
    "response_dto": "DocumentDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "DocumentDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "GET /api/v1/cases/{id}/memory": {
    "method": "GET",
    "path": "/api/v1/cases/{id}/memory",
    "role": "ANY",
    "response_dto": "Page[CaseMemoryDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[CaseMemoryDTO]",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor"
    ]
  },
  "GET /api/v1/map/features": {
    "method": "GET",
    "path": "/api/v1/map/features",
    "role": "ANY",
    "response_dto": "MapFeatureCollection",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "MapFeatureCollection",
    "milestone": "B17",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor",
      "issue",
      "status",
      "department_id",
      "after",
      "before",
      "investigation_id"
    ],
    "query_schema_id": "MapQuery"
  },
  "GET /api/v1/assets/{id}": {
    "method": "GET",
    "path": "/api/v1/assets/{id}",
    "role": "ANY",
    "response_dto": "AssetDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "AssetDTO",
    "milestone": "B17",
    "status": "IMPLEMENTED",
    "query_parameters": [],
    "query_schema_id": "AssetQuery"
  },
  "GET /api/v1/assets/{id}/neighbors": {
    "method": "GET",
    "path": "/api/v1/assets/{id}/neighbors",
    "role": "ANY",
    "response_dto": "GraphSubgraphDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "GraphSubgraphDTO",
    "milestone": "B17",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "depth",
      "include_candidates"
    ],
    "query_schema_id": "GraphQuery"
  },
  "GET /api/v1/monitoring": {
    "method": "GET",
    "path": "/api/v1/monitoring",
    "role": "ANY",
    "response_dto": "Page[MonitoringDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[MonitoringDTO]",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor"
    ]
  },
  "GET /api/v1/problem-clusters/{id}/outcomes": {
    "method": "GET",
    "path": "/api/v1/problem-clusters/{id}/outcomes",
    "role": "ANY",
    "response_dto": "Page[OutcomeDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[OutcomeDTO]",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor"
    ]
  },
  "GET /api/v1/events/stream": {
    "method": "GET",
    "path": "/api/v1/events/stream",
    "role": "ANY",
    "response_dto": "SSEStream",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "SSEStream",
    "milestone": "B17",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "cursor",
      "investigation_id"
    ]
  },
  "POST /api/v1/demo/reset": {
    "method": "POST",
    "path": "/api/v1/demo/reset",
    "role": "ADMIN",
    "response_dto": "SeedReport",
    "idempotency_key": true,
    "request_schema_id": "DemoResetRequest",
    "response_schema_id": "SeedReport",
    "milestone": "B19",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "POST /api/v1/demo/scenarios/{id}/advance": {
    "method": "POST",
    "path": "/api/v1/demo/scenarios/{id}/advance",
    "role": "ADMIN",
    "response_dto": "SimulationStepDTO",
    "idempotency_key": true,
    "request_schema_id": "DemoAdvanceRequest",
    "response_schema_id": "SimulationStepDTO",
    "milestone": "B19",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "GET /api/v1/demo/scenarios": {
    "method": "GET",
    "path": "/api/v1/demo/scenarios",
    "role": "ANY",
    "response_dto": "ScenarioPage",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "ScenarioPage",
    "milestone": "B19",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "GET /api/v1/health/live": {
    "method": "GET",
    "path": "/api/v1/health/live",
    "role": "PUBLIC",
    "response_dto": "HealthDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "HealthDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "GET /api/v1/health/ready": {
    "method": "GET",
    "path": "/api/v1/health/ready",
    "role": "PUBLIC",
    "response_dto": "HealthDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "HealthDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "POST /api/v1/investigations/{id}/hypotheses": {
    "method": "POST",
    "path": "/api/v1/investigations/{id}/hypotheses",
    "role": "ANALYST",
    "response_dto": "Ack",
    "idempotency_key": true,
    "request_schema_id": "ProposeRequest",
    "response_schema_id": "Ack",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "POST /api/v1/hypotheses/{id}/assessments": {
    "method": "POST",
    "path": "/api/v1/hypotheses/{id}/assessments",
    "role": "ANALYST",
    "response_dto": "Ack",
    "idempotency_key": true,
    "request_schema_id": "AssessRequest",
    "response_schema_id": "Ack",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "POST /api/v1/inspections": {
    "method": "POST",
    "path": "/api/v1/inspections",
    "role": "ANALYST",
    "response_dto": "InspectionDTO",
    "idempotency_key": true,
    "request_schema_id": "InspectionRequest",
    "response_schema_id": "InspectionDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "POST /api/v1/inspections/{id}/transitions": {
    "method": "POST",
    "path": "/api/v1/inspections/{id}/transitions",
    "role": "ANALYST,DEPARTMENT_LEAD",
    "response_dto": "InspectionDTO",
    "idempotency_key": true,
    "request_schema_id": "TransitionRequest",
    "response_schema_id": "InspectionDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "POST /api/v1/plans": {
    "method": "POST",
    "path": "/api/v1/plans",
    "role": "ANALYST",
    "response_dto": "PlanDTO",
    "idempotency_key": true,
    "request_schema_id": "DraftRequest",
    "response_schema_id": "PlanDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "POST /api/v1/work-orders": {
    "method": "POST",
    "path": "/api/v1/work-orders",
    "role": "APPROVER",
    "response_dto": "WorkOrderDTO",
    "idempotency_key": true,
    "request_schema_id": "OrderRequest",
    "response_schema_id": "WorkOrderDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "POST /api/v1/work-orders/{id}/progress": {
    "method": "POST",
    "path": "/api/v1/work-orders/{id}/progress",
    "role": "DEPARTMENT_LEAD",
    "response_dto": "WorkOrderDTO",
    "idempotency_key": true,
    "request_schema_id": "ProgressRequest",
    "response_schema_id": "WorkOrderDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "POST /api/v1/work-orders/{id}/inspections": {
    "method": "POST",
    "path": "/api/v1/work-orders/{id}/inspections",
    "role": "DEPARTMENT_LEAD,ANALYST",
    "response_dto": "Ack",
    "idempotency_key": true,
    "request_schema_id": "WorkInspectionRequest",
    "response_schema_id": "Ack",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "POST /api/v1/work-orders/{id}/recurrence": {
    "method": "POST",
    "path": "/api/v1/work-orders/{id}/recurrence",
    "role": "ANALYST",
    "response_dto": "OutcomeDTO",
    "idempotency_key": true,
    "request_schema_id": "RecurRequest",
    "response_schema_id": "OutcomeDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED"
  },
  "GET /api/v1/approvals/{id}": {
    "method": "GET",
    "path": "/api/v1/approvals/{id}",
    "role": "APPROVER",
    "response_dto": "ApprovalDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "ApprovalDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "GET /api/v1/investigations/{id}/plans": {
    "method": "GET",
    "path": "/api/v1/investigations/{id}/plans",
    "role": "ANY",
    "response_dto": "Page[PlanDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[PlanDTO]",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor"
    ]
  },
  "GET /api/v1/hypotheses/{id}": {
    "method": "GET",
    "path": "/api/v1/hypotheses/{id}",
    "role": "ANY",
    "response_dto": "HypothesisDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "HypothesisDTO",
    "milestone": "B16",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "POST /api/v1/responsibilities": {
    "method": "POST",
    "path": "/api/v1/responsibilities",
    "role": "DEPARTMENT_LEAD",
    "response_dto": "ResponsibilityDTO",
    "idempotency_key": true,
    "request_schema_id": "ResponsibilitySubmission",
    "response_schema_id": "ResponsibilityDTO",
    "milestone": "B20-R-OWNERSHIP",
    "status": "IMPLEMENTED"
  },
  "POST /api/v1/responsibilities/{id}/review": {
    "method": "POST",
    "path": "/api/v1/responsibilities/{id}/review",
    "role": "ANALYST",
    "response_dto": "ResponsibilityDTO",
    "idempotency_key": true,
    "request_schema_id": "ResponsibilityReview",
    "response_schema_id": "ResponsibilityDTO",
    "milestone": "B20-R-OWNERSHIP",
    "status": "IMPLEMENTED"
  },
  "GET /api/v1/responsibilities/{id}": {
    "method": "GET",
    "path": "/api/v1/responsibilities/{id}",
    "role": "ANY",
    "response_dto": "ResponsibilityDTO",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "ResponsibilityDTO",
    "milestone": "B20-R-OWNERSHIP",
    "status": "IMPLEMENTED",
    "query_parameters": []
  },
  "GET /api/v1/investigations": {
    "method": "GET",
    "path": "/api/v1/investigations",
    "role": "ANY",
    "response_dto": "Page[InvestigationDTO]",
    "idempotency_key": false,
    "request_schema_id": null,
    "response_schema_id": "Page[InvestigationDTO]",
    "milestone": "FRONTEND-BACKEND-DEMO",
    "status": "IMPLEMENTED",
    "query_parameters": [
      "limit",
      "cursor",
      "issue",
      "status",
      "department_id",
      "after",
      "before"
    ],
    "query_schema_id": "ResourceQuery"
  }
} as const;
export interface ApiRoutes {
  "POST /api/v1/auth/demo-login": {request: ApiModels["LoginRequest"]; response: ApiModels["DemoSession"]; query: Record<string, never>};
  "GET /api/v1/auth/me": {request: undefined; response: ApiModels["OperatorAccount"]; query: Record<string, never>};
  "POST /api/v1/auth/logout": {request: ApiModels["EmptyRequest"]; response: ApiModels["Ack"]; query: Record<string, never>};
  "GET /api/v1/dashboard/summary": {request: undefined; response: ApiModels["DashboardSummary"]; query: ApiModels["DashboardQuery"]};
  "POST /api/v1/complaints": {request: ApiModels["ComplaintRequest"]; response: ApiModels["ComplaintDTO"]; query: Record<string, never>};
  "GET /api/v1/complaints": {request: undefined; response: ApiModels["Page[ComplaintDTO]"]; query: ApiModels["ResourceQuery"]};
  "GET /api/v1/complaints/{id}": {request: undefined; response: ApiModels["ComplaintDTO"]; query: Record<string, never>};
  "GET /api/v1/incidents": {request: undefined; response: ApiModels["Page[IncidentDTO]"]; query: ApiModels["ResourceQuery"]};
  "GET /api/v1/incidents/{id}": {request: undefined; response: ApiModels["IncidentDTO"]; query: Record<string, never>};
  "GET /api/v1/problem-clusters": {request: undefined; response: ApiModels["Page[ProblemClusterDTO]"]; query: ApiModels["ResourceQuery"]};
  "GET /api/v1/problem-clusters/{id}": {request: undefined; response: ApiModels["ProblemClusterDTO"]; query: Record<string, never>};
  "POST /api/v1/investigations": {request: ApiModels["OpenRequest"]; response: ApiModels["InvestigationDTO"]; query: Record<string, never>};
  "GET /api/v1/investigations/{id}": {request: undefined; response: ApiModels["InvestigationDTO"]; query: Record<string, never>};
  "POST /api/v1/investigations/{id}/resume": {request: ApiModels["ResumeRequest"]; response: ApiModels["AgentResumeDTO"]; query: Record<string, never>};
  "GET /api/v1/investigations/{id}/trace": {request: undefined; response: ApiModels["AgentTracePage"]; query: ApiModels["TraceQuery"]};
  "GET /api/v1/investigations/{id}/hypotheses": {request: undefined; response: ApiModels["HypothesisPage"]; query: ApiModels["HypothesesQuery"]};
  "GET /api/v1/investigations/{id}/graph": {request: undefined; response: ApiModels["GraphSubgraphDTO"]; query: ApiModels["GraphQuery"]};
  "GET /api/v1/evidence/{id}": {request: undefined; response: ApiModels["EvidenceDTO"]; query: Record<string, never>};
  "GET /api/v1/inspections/{id}": {request: undefined; response: ApiModels["InspectionDTO"]; query: Record<string, never>};
  "POST /api/v1/inspections/{id}/observations": {request: ApiModels["ReportRequest"]; response: ApiModels["EvidenceDTO"]; query: Record<string, never>};
  "GET /api/v1/plans/{id}": {request: undefined; response: ApiModels["PlanDTO"]; query: Record<string, never>};
  "POST /api/v1/plans/{id}/submit-approval": {request: ApiModels["SubmitRequest"]; response: ApiModels["ApprovalDTO"]; query: Record<string, never>};
  "GET /api/v1/approvals": {request: undefined; response: ApiModels["Page[ApprovalDTO]"]; query: ApiModels["ResourceQuery"]};
  "POST /api/v1/approvals/{id}/decision": {request: ApiModels["DecideRequest"]; response: ApiModels["ApprovalDTO"]; query: Record<string, never>};
  "GET /api/v1/work-orders": {request: undefined; response: ApiModels["Page[WorkOrderDTO]"]; query: ApiModels["ResourceQuery"]};
  "GET /api/v1/work-orders/{id}": {request: undefined; response: ApiModels["WorkOrderDTO"]; query: Record<string, never>};
  "POST /api/v1/work-orders/{id}/status": {request: ApiModels["UpdateRequest"]; response: ApiModels["WorkOrderDTO"]; query: Record<string, never>};
  "POST /api/v1/work-orders/{id}/outcomes": {request: ApiModels["EvaluateRequest"]; response: ApiModels["OutcomeDTO"]; query: Record<string, never>};
  "GET /api/v1/departments": {request: undefined; response: ApiModels["Page[DepartmentDTO]"]; query: ApiModels["ResourceQuery"]};
  "GET /api/v1/procedures": {request: undefined; response: ApiModels["Page[ProcedureDTO]"]; query: {limit?: number; cursor?: string}};
  "GET /api/v1/documents/{id}": {request: undefined; response: ApiModels["DocumentDTO"]; query: Record<string, never>};
  "GET /api/v1/cases/{id}/memory": {request: undefined; response: ApiModels["Page[CaseMemoryDTO]"]; query: {limit?: number; cursor?: string}};
  "GET /api/v1/map/features": {request: undefined; response: ApiModels["MapFeatureCollection"]; query: ApiModels["MapQuery"]};
  "GET /api/v1/assets/{id}": {request: undefined; response: ApiModels["AssetDTO"]; query: ApiModels["AssetQuery"]};
  "GET /api/v1/assets/{id}/neighbors": {request: undefined; response: ApiModels["GraphSubgraphDTO"]; query: ApiModels["GraphQuery"]};
  "GET /api/v1/monitoring": {request: undefined; response: ApiModels["Page[MonitoringDTO]"]; query: {limit?: number; cursor?: string}};
  "GET /api/v1/problem-clusters/{id}/outcomes": {request: undefined; response: ApiModels["Page[OutcomeDTO]"]; query: {limit?: number; cursor?: string}};
  "GET /api/v1/events/stream": {request: undefined; response: ApiModels["SSEStream"]; query: {limit?: number; cursor?: string}};
  "POST /api/v1/demo/reset": {request: ApiModels["DemoResetRequest"]; response: ApiModels["SeedReport"]; query: Record<string, never>};
  "POST /api/v1/demo/scenarios/{id}/advance": {request: ApiModels["DemoAdvanceRequest"]; response: ApiModels["SimulationStepDTO"]; query: Record<string, never>};
  "GET /api/v1/demo/scenarios": {request: undefined; response: ApiModels["ScenarioPage"]; query: Record<string, never>};
  "GET /api/v1/health/live": {request: undefined; response: ApiModels["HealthDTO"]; query: Record<string, never>};
  "GET /api/v1/health/ready": {request: undefined; response: ApiModels["HealthDTO"]; query: Record<string, never>};
  "POST /api/v1/investigations/{id}/hypotheses": {request: ApiModels["ProposeRequest"]; response: ApiModels["Ack"]; query: Record<string, never>};
  "POST /api/v1/hypotheses/{id}/assessments": {request: ApiModels["AssessRequest"]; response: ApiModels["Ack"]; query: Record<string, never>};
  "POST /api/v1/inspections": {request: ApiModels["InspectionRequest"]; response: ApiModels["InspectionDTO"]; query: Record<string, never>};
  "POST /api/v1/inspections/{id}/transitions": {request: ApiModels["TransitionRequest"]; response: ApiModels["InspectionDTO"]; query: Record<string, never>};
  "POST /api/v1/plans": {request: ApiModels["DraftRequest"]; response: ApiModels["PlanDTO"]; query: Record<string, never>};
  "POST /api/v1/work-orders": {request: ApiModels["OrderRequest"]; response: ApiModels["WorkOrderDTO"]; query: Record<string, never>};
  "POST /api/v1/work-orders/{id}/progress": {request: ApiModels["ProgressRequest"]; response: ApiModels["WorkOrderDTO"]; query: Record<string, never>};
  "POST /api/v1/work-orders/{id}/inspections": {request: ApiModels["WorkInspectionRequest"]; response: ApiModels["Ack"]; query: Record<string, never>};
  "POST /api/v1/work-orders/{id}/recurrence": {request: ApiModels["RecurRequest"]; response: ApiModels["OutcomeDTO"]; query: Record<string, never>};
  "GET /api/v1/approvals/{id}": {request: undefined; response: ApiModels["ApprovalDTO"]; query: Record<string, never>};
  "GET /api/v1/investigations/{id}/plans": {request: undefined; response: ApiModels["Page[PlanDTO]"]; query: {limit?: number; cursor?: string}};
  "GET /api/v1/hypotheses/{id}": {request: undefined; response: ApiModels["HypothesisDTO"]; query: Record<string, never>};
  "POST /api/v1/responsibilities": {request: ApiModels["ResponsibilitySubmission"]; response: ApiModels["ResponsibilityDTO"]; query: Record<string, never>};
  "POST /api/v1/responsibilities/{id}/review": {request: ApiModels["ResponsibilityReview"]; response: ApiModels["ResponsibilityDTO"]; query: Record<string, never>};
  "GET /api/v1/responsibilities/{id}": {request: undefined; response: ApiModels["ResponsibilityDTO"]; query: Record<string, never>};
  "GET /api/v1/investigations": {request: undefined; response: ApiModels["Page[InvestigationDTO]"]; query: ApiModels["ResourceQuery"]};
}
