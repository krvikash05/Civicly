# B16 route coverage (DEC-060)

Actual44B16operations/42paths. No501stubs. All paths have /api/v1 prefix. B17/B19 are absent from actual OpenAPI.

| Method | Path | Phase | Role | Typed request to response |
|---|---|---|---|---|
| POST | /api/v1/auth/demo-login | B16 | PUBLIC | LoginRequest to DemoSession |
| GET | /api/v1/auth/me | B16 | ANY | none to OperatorAccount |
| POST | /api/v1/auth/logout | B16 | ANY | EmptyRequest to Ack |
| GET | /api/v1/dashboard/summary | B17 | ANY | none to DashboardSummary |
| POST | /api/v1/complaints | B16 | ANALYST | ComplaintRequest to ComplaintDTO |
| GET | /api/v1/complaints | B16 | ANY | none to Page[ComplaintDTO] |
| GET | /api/v1/complaints/{id} | B16 | ANY | none to ComplaintDTO |
| GET | /api/v1/incidents | B16 | ANY | none to Page[IncidentDTO] |
| GET | /api/v1/incidents/{id} | B16 | ANY | none to IncidentDTO |
| GET | /api/v1/problem-clusters | B16 | ANY | none to Page[ProblemClusterDTO] |
| GET | /api/v1/problem-clusters/{id} | B16 | ANY | none to ProblemClusterDTO |
| POST | /api/v1/investigations | B16 | ANALYST | OpenRequest to InvestigationDTO |
| GET | /api/v1/investigations/{id} | B16 | ANY | none to InvestigationDTO |
| POST | /api/v1/investigations/{id}/resume | B16 | ANALYST | ResumeRequest to AgentResumeDTO |
| GET | /api/v1/investigations/{id}/trace | B17 | ANY | none to AgentTracePage |
| GET | /api/v1/investigations/{id}/hypotheses | B17 | ANY | none to HypothesisPage |
| GET | /api/v1/investigations/{id}/graph | B17 | ANY | none to GraphSubgraphDTO |
| GET | /api/v1/evidence/{id} | B16 | ANY | none to EvidenceDTO |
| GET | /api/v1/inspections/{id} | B16 | ANY | none to InspectionDTO |
| POST | /api/v1/inspections/{id}/observations | B16 | DEPARTMENT_LEAD | ReportRequest to EvidenceDTO |
| GET | /api/v1/plans/{id} | B16 | ANY | none to PlanDTO |
| POST | /api/v1/plans/{id}/submit-approval | B16 | ANALYST | SubmitRequest to ApprovalDTO |
| GET | /api/v1/approvals | B16 | APPROVER | none to Page[ApprovalDTO] |
| POST | /api/v1/approvals/{id}/decision | B16 | APPROVER | DecideRequest to ApprovalDTO |
| GET | /api/v1/work-orders | B16 | ANY | none to Page[WorkOrderDTO] |
| GET | /api/v1/work-orders/{id} | B16 | ANY | none to WorkOrderDTO |
| POST | /api/v1/work-orders/{id}/status | B16 | DEPARTMENT_LEAD | UpdateRequest to WorkOrderDTO |
| POST | /api/v1/work-orders/{id}/outcomes | B16 | ANALYST | EvaluateRequest to OutcomeDTO |
| GET | /api/v1/departments | B16 | ANY | none to Page[DepartmentDTO] |
| GET | /api/v1/procedures | B16 | ANY | none to Page[ProcedureDTO] |
| GET | /api/v1/documents/{id} | B16 | ANY | none to DocumentDTO |
| GET | /api/v1/cases/{id}/memory | B16 | ANY | none to Page[CaseMemoryDTO] |
| GET | /api/v1/map/features | B17 | ANY | none to MapFeatureCollection |
| GET | /api/v1/assets/{id} | B17 | ANY | none to AssetDTO |
| GET | /api/v1/assets/{id}/neighbors | B17 | ANY | none to GraphSubgraphDTO |
| GET | /api/v1/monitoring | B16 | ANY | none to Page[MonitoringDTO] |
| GET | /api/v1/problem-clusters/{id}/outcomes | B16 | ANY | none to Page[OutcomeDTO] |
| GET | /api/v1/events/stream | B17 | ANY | none to SSEStream |
| POST | /api/v1/demo/reset | B19 | ADMIN | demo_reset_Request to SeedReport |
| POST | /api/v1/demo/scenarios/{id}/advance | B19 | ADMIN | demo_scenarios_id_advance_Request to SimulationStepDTO |
| GET | /api/v1/demo/scenarios | B19 | ANY | none to ScenarioPage |
| GET | /api/v1/health/live | B16 | PUBLIC | none to HealthDTO |
| GET | /api/v1/health/ready | B16 | PUBLIC | none to HealthDTO |
| POST | /api/v1/investigations/{id}/hypotheses | B16 | ANALYST | ProposeRequest to Ack |
| POST | /api/v1/hypotheses/{id}/assessments | B16 | ANALYST | AssessRequest to Ack |
| POST | /api/v1/inspections | B16 | ANALYST | InspectionRequest to InspectionDTO |
| POST | /api/v1/inspections/{id}/transitions | B16 | ANALYST,DEPARTMENT_LEAD | TransitionRequest to InspectionDTO |
| POST | /api/v1/plans | B16 | ANALYST | DraftRequest to PlanDTO |
| POST | /api/v1/work-orders | B16 | APPROVER | OrderRequest to WorkOrderDTO |
| POST | /api/v1/work-orders/{id}/progress | B16 | DEPARTMENT_LEAD | ProgressRequest to WorkOrderDTO |
| POST | /api/v1/work-orders/{id}/inspections | B16 | DEPARTMENT_LEAD,ANALYST | WorkInspectionRequest to Ack |
| POST | /api/v1/work-orders/{id}/recurrence | B16 | ANALYST | RecurRequest to OutcomeDTO |
| GET | /api/v1/approvals/{id} | B16 | APPROVER | none to ApprovalDTO |
| GET | /api/v1/investigations/{id}/plans | B16 | ANY | none to Page[PlanDTO] |
| GET | /api/v1/hypotheses/{id} | B16 | ANY | none to HypothesisDTO |

Core basic bounded pagination/authorization is B16; comprehensive map/graph/trace/dashboard/SSE and richer filtering remain B17. Scenario reset/advance/list remains B19. New B16 routes fill missing draft access, authorized order creation, independent inspection lifecycle and typed execution gates; none grants automatic work/model authority.

Corrections: work-orders outcomes is analyst independent Evaluate, not caller-supplied outcome; status is B13 assignment/cancel only, B14 progress separate. Draft receipt/current lifecycle separated. Reviewer bearer token is header-only.
