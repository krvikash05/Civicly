# B17 actual route/DTO coverage

52 operations,49 paths; all eight B17 GETs implemented. B19 only remains deferred.

| Method | Path | Phase/status | Role | Request → response |
|---|---|---|---|---|
| POST | /api/v1/auth/demo-login | B16 / IMPLEMENTED | PUBLIC | LoginRequest → DemoSession |
| GET | /api/v1/auth/me | B16 / IMPLEMENTED | ANY | none → OperatorAccount |
| POST | /api/v1/auth/logout | B16 / IMPLEMENTED | ANY | EmptyRequest → Ack |
| GET | /api/v1/dashboard/summary | B17 / IMPLEMENTED | ANY | none → DashboardSummary |
| POST | /api/v1/complaints | B16 / IMPLEMENTED | ANALYST | ComplaintRequest → ComplaintDTO |
| GET | /api/v1/complaints | B16 / IMPLEMENTED | ANY | none → Page[ComplaintDTO] |
| GET | /api/v1/complaints/{id} | B16 / IMPLEMENTED | ANY | none → ComplaintDTO |
| GET | /api/v1/incidents | B16 / IMPLEMENTED | ANY | none → Page[IncidentDTO] |
| GET | /api/v1/incidents/{id} | B16 / IMPLEMENTED | ANY | none → IncidentDTO |
| GET | /api/v1/problem-clusters | B16 / IMPLEMENTED | ANY | none → Page[ProblemClusterDTO] |
| GET | /api/v1/problem-clusters/{id} | B16 / IMPLEMENTED | ANY | none → ProblemClusterDTO |
| POST | /api/v1/investigations | B16 / IMPLEMENTED | ANALYST | OpenRequest → InvestigationDTO |
| GET | /api/v1/investigations/{id} | B16 / IMPLEMENTED | ANY | none → InvestigationDTO |
| POST | /api/v1/investigations/{id}/resume | B16 / IMPLEMENTED | ANALYST | ResumeRequest → AgentResumeDTO |
| GET | /api/v1/investigations/{id}/trace | B17 / IMPLEMENTED | ANY | none → AgentTracePage |
| GET | /api/v1/investigations/{id}/hypotheses | B17 / IMPLEMENTED | ANY | none → HypothesisPage |
| GET | /api/v1/investigations/{id}/graph | B17 / IMPLEMENTED | ANY | none → GraphSubgraphDTO |
| GET | /api/v1/evidence/{id} | B16 / IMPLEMENTED | ANY | none → EvidenceDTO |
| GET | /api/v1/inspections/{id} | B16 / IMPLEMENTED | ANY | none → InspectionDTO |
| POST | /api/v1/inspections/{id}/observations | B16 / IMPLEMENTED | DEPARTMENT_LEAD | ReportRequest → EvidenceDTO |
| GET | /api/v1/plans/{id} | B16 / IMPLEMENTED | ANY | none → PlanDTO |
| POST | /api/v1/plans/{id}/submit-approval | B16 / IMPLEMENTED | ANALYST | SubmitRequest → ApprovalDTO |
| GET | /api/v1/approvals | B16 / IMPLEMENTED | APPROVER | none → Page[ApprovalDTO] |
| POST | /api/v1/approvals/{id}/decision | B16 / IMPLEMENTED | APPROVER | DecideRequest → ApprovalDTO |
| GET | /api/v1/work-orders | B16 / IMPLEMENTED | ANY | none → Page[WorkOrderDTO] |
| GET | /api/v1/work-orders/{id} | B16 / IMPLEMENTED | ANY | none → WorkOrderDTO |
| POST | /api/v1/work-orders/{id}/status | B16 / IMPLEMENTED | DEPARTMENT_LEAD | UpdateRequest → WorkOrderDTO |
| POST | /api/v1/work-orders/{id}/outcomes | B16 / IMPLEMENTED | ANALYST | EvaluateRequest → OutcomeDTO |
| GET | /api/v1/departments | B16 / IMPLEMENTED | ANY | none → Page[DepartmentDTO] |
| GET | /api/v1/procedures | B16 / IMPLEMENTED | ANY | none → Page[ProcedureDTO] |
| GET | /api/v1/documents/{id} | B16 / IMPLEMENTED | ANY | none → DocumentDTO |
| GET | /api/v1/cases/{id}/memory | B16 / IMPLEMENTED | ANY | none → Page[CaseMemoryDTO] |
| GET | /api/v1/map/features | B17 / IMPLEMENTED | ANY | none → MapFeatureCollection |
| GET | /api/v1/assets/{id} | B17 / IMPLEMENTED | ANY | none → AssetDTO |
| GET | /api/v1/assets/{id}/neighbors | B17 / IMPLEMENTED | ANY | none → GraphSubgraphDTO |
| GET | /api/v1/monitoring | B16 / IMPLEMENTED | ANY | none → Page[MonitoringDTO] |
| GET | /api/v1/problem-clusters/{id}/outcomes | B16 / IMPLEMENTED | ANY | none → Page[OutcomeDTO] |
| GET | /api/v1/events/stream | B17 / IMPLEMENTED | ANY | none → SSEStream |
| POST | /api/v1/demo/reset | B19 / DEFERRED_NOT_IMPLEMENTED | ADMIN | demo_reset_Request → SeedReport |
| POST | /api/v1/demo/scenarios/{id}/advance | B19 / DEFERRED_NOT_IMPLEMENTED | ADMIN | demo_scenarios_id_advance_Request → SimulationStepDTO |
| GET | /api/v1/demo/scenarios | B19 / DEFERRED_NOT_IMPLEMENTED | ANY | none → ScenarioPage |
| GET | /api/v1/health/live | B16 / IMPLEMENTED | PUBLIC | none → HealthDTO |
| GET | /api/v1/health/ready | B16 / IMPLEMENTED | PUBLIC | none → HealthDTO |
| POST | /api/v1/investigations/{id}/hypotheses | B16 / IMPLEMENTED | ANALYST | ProposeRequest → Ack |
| POST | /api/v1/hypotheses/{id}/assessments | B16 / IMPLEMENTED | ANALYST | AssessRequest → Ack |
| POST | /api/v1/inspections | B16 / IMPLEMENTED | ANALYST | InspectionRequest → InspectionDTO |
| POST | /api/v1/inspections/{id}/transitions | B16 / IMPLEMENTED | ANALYST,DEPARTMENT_LEAD | TransitionRequest → InspectionDTO |
| POST | /api/v1/plans | B16 / IMPLEMENTED | ANALYST | DraftRequest → PlanDTO |
| POST | /api/v1/work-orders | B16 / IMPLEMENTED | APPROVER | OrderRequest → WorkOrderDTO |
| POST | /api/v1/work-orders/{id}/progress | B16 / IMPLEMENTED | DEPARTMENT_LEAD | ProgressRequest → WorkOrderDTO |
| POST | /api/v1/work-orders/{id}/inspections | B16 / IMPLEMENTED | DEPARTMENT_LEAD,ANALYST | WorkInspectionRequest → Ack |
| POST | /api/v1/work-orders/{id}/recurrence | B16 / IMPLEMENTED | ANALYST | RecurRequest → OutcomeDTO |
| GET | /api/v1/approvals/{id} | B16 / IMPLEMENTED | APPROVER | none → ApprovalDTO |
| GET | /api/v1/investigations/{id}/plans | B16 / IMPLEMENTED | ANY | none → Page[PlanDTO] |
| GET | /api/v1/hypotheses/{id} | B16 / IMPLEMENTED | ANY | none → HypothesisDTO |
