"""Explicit B16 inventory; no placeholder routes for later phases."""
from . import models as m
# method, path without prefix, role(s), request schema, response schema, command
ROUTES=[
('POST','/auth/demo-login','PUBLIC',m.LoginRequest,m.DemoSession,'login'),
('GET','/auth/me','ANY',None,m.OperatorAccount,'me'),('POST','/auth/logout','ANY',m.EmptyRequest,m.Ack,'logout'),
('GET','/health/live','PUBLIC',None,m.HealthDTO,'live'),('GET','/health/ready','PUBLIC',None,m.HealthDTO,'ready'),
('POST','/complaints','ANALYST',m.ComplaintRequest,m.ComplaintDTO,'intake'),
('POST','/investigations','ANALYST',m.OpenRequest,m.InvestigationDTO,'open'),
('POST','/investigations/{id}/resume','ANALYST',m.ResumeRequest,m.AgentResumeDTO,'resume'),
('POST','/investigations/{id}/hypotheses','ANALYST',m.ProposeRequest,m.Ack,'propose'),
('POST','/hypotheses/{id}/assessments','ANALYST',m.AssessRequest,m.Ack,'assess'),
('POST','/inspections','ANALYST',m.InspectionRequest,m.InspectionDTO,'request_inspection'),
('POST','/inspections/{id}/transitions','ANALYST,DEPARTMENT_LEAD',m.TransitionRequest,m.InspectionDTO,'transition_inspection'),
('POST','/inspections/{id}/observations','DEPARTMENT_LEAD',m.ReportRequest,m.EvidenceDTO,'report_inspection'),
('POST','/plans','ANALYST',m.DraftRequest,m.PlanDTO,'draft'),
('POST','/plans/{id}/submit-approval','ANALYST',m.SubmitRequest,m.ApprovalDTO,'submit'),
('POST','/approvals/{id}/decision','APPROVER',m.DecideRequest,m.ApprovalDTO,'decide'),
('POST','/work-orders','APPROVER',m.OrderRequest,m.WorkOrderDTO,'order'),
('POST','/work-orders/{id}/status','DEPARTMENT_LEAD',m.UpdateRequest,m.WorkOrderDTO,'update'),
('POST','/work-orders/{id}/progress','DEPARTMENT_LEAD',m.ProgressRequest,m.WorkOrderDTO,'progress'),
('POST','/work-orders/{id}/inspections','DEPARTMENT_LEAD,ANALYST',m.WorkInspectionRequest,m.Ack,'inspect'),
('POST','/work-orders/{id}/outcomes','ANALYST',m.EvaluateRequest,m.OutcomeDTO,'evaluate'),
('POST','/work-orders/{id}/recurrence','ANALYST',m.RecurRequest,m.OutcomeDTO,'recur')]
for path,kind,dto,role in [('complaints','Complaint',m.ComplaintDTO,'ANY'),('incidents','Incident',m.IncidentDTO,'ANY'),('problem-clusters','ProblemCluster',m.ProblemClusterDTO,'ANY'),('approvals','Approval',m.ApprovalDTO,'APPROVER'),('work-orders','WorkOrder',m.WorkOrderDTO,'ANY'),('departments','Department',m.DepartmentDTO,'ANY')]:
 ROUTES.append(('GET','/'+path,role,None,m.Page[dto],'list:'+kind))
 if kind!='Department':ROUTES.append(('GET','/'+path+'/{id}',role,None,dto,'get:'+kind))
for path,kind,dto in [('investigations','Investigation',m.InvestigationDTO),('evidence','Evidence',m.EvidenceDTO),('inspections','Inspection',m.InspectionDTO),('plans','ResolutionPlan',m.PlanDTO)]:ROUTES.append(('GET','/'+path+'/{id}','ANY',None,dto,'get:'+kind))
ROUTES.extend([
('GET','/hypotheses/{id}','ANY',None,m.HypothesisDTO,'get:Hypothesis'),
('GET','/investigations/{id}/plans','ANY',None,m.Page[m.PlanDTO],'plans'),
('GET','/procedures','ANY',None,m.Page[m.ProcedureDTO],'procedures'),
('GET','/documents/{id}','ANY',None,m.DocumentDTO,'document'),
('GET','/cases/{id}/memory','ANY',None,m.Page[m.CaseMemoryDTO],'memory'),
('GET','/monitoring','ANY',None,m.Page[m.MonitoringDTO],'monitoring'),
('GET','/problem-clusters/{id}/outcomes','ANY',None,m.Page[m.OutcomeDTO],'outcomes')])
B17_PATHS=['/dashboard/summary','/investigations/{id}/trace','/investigations/{id}/hypotheses','/investigations/{id}/graph','/map/features','/assets/{id}','/assets/{id}/neighbors','/events/stream']
DEFERRED_B19=[]

DEFERRED_B17=[]
ROUTES.extend([
('GET','/dashboard/summary','ANY',None,m.DashboardSummary,'dashboard'),
('GET','/investigations/{id}/trace','ANY',None,m.AgentTracePage,'trace'),
('GET','/investigations/{id}/hypotheses','ANY',None,m.HypothesisPage,'hypotheses'),
('GET','/investigations/{id}/graph','ANY',None,m.GraphSubgraphDTO,'graph'),
('GET','/map/features','ANY',None,m.MapFeatureCollection,'map'),
('GET','/assets/{id}','ANY',None,m.AssetDTO,'asset'),
('GET','/assets/{id}/neighbors','ANY',None,m.GraphSubgraphDTO,'neighbors'),
('GET','/events/stream','ANY',None,m.SSEStream,'stream')])

ROUTES.extend([('GET','/demo/scenarios','ANY',None,m.ScenarioPage,'demo_catalog'),('POST','/demo/reset','ADMIN',m.DemoResetRequest,m.SeedReport,'demo_reset'),('POST','/demo/scenarios/{id}/advance','ADMIN',m.DemoAdvanceRequest,m.SimulationStepDTO,'demo_advance')])

ROUTES.extend([('POST','/responsibilities','DEPARTMENT_LEAD',m.ResponsibilitySubmission,m.ResponsibilityDTO,'responsibility_submit'),('POST','/responsibilities/{id}/review','ANALYST',m.ResponsibilityReview,m.ResponsibilityDTO,'responsibility_review'),('GET','/responsibilities/{id}','ANY',None,m.ResponsibilityDTO,'responsibility_get')])
ROUTES.append(('GET','/investigations','ANY',None,m.Page[m.InvestigationDTO],'list:Investigation'))
