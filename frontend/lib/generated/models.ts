/* Generated from Civicly contracts. Run npm run generate:api. Do not edit. */

export type Status = string;
export type AccessToken = string;
export type ExpiresAt = string;
export type OperatorId = string;
export type Role = string;
export type Id = string;
export type DisplayName = string;
export type Role1 = "ANALYST" | "DEPARTMENT_LEAD" | "APPROVER" | "ADMIN";
export type DepartmentId = string;
export type Enabled = true;
export type Status1 = "ok" | "unavailable";
export type RuntimeMode = "DETERMINISTIC_DEVELOPMENT_NO_PROVIDER";
export type ActiveIncidents = number;
export type ActiveClusters = number;
export type PendingApprovals = number;
export type CompletedWorkOrders = number;
export type VerifiedWorkOrders = number;
export type GraphRevision = number;
export type AsOf = string;
export type Definitions = string[];
export type Limitations = string[];
export type OpenClusters = number;
export type ActiveInvestigations = number;
export type SimulationMode = true;
export type Id1 = string;
export type ExpectedHash = string;
export type Simulated = true;
export type Description = string;
export type IncidentId = string | null;
export type ReportedAt = string;
export type SourceKind = string;
export type Status2 = string;
export type IssueType = string;
export type Id2 = string;
export type ExpectedHash1 = string;
export type Simulated1 = true;
export type IssueType1 = string;
export type Subtype = string;
export type LocationId = string | null;
export type StartedAt = string;
export type EndedAt = string | null;
export type Status3 = string;
export type ClusterId = string | null;
/**
 * @maxItems 100
 */
export type ComplaintIds = string[];
export type Id3 = string;
export type ExpectedHash2 = string;
export type Simulated2 = true;
export type PatternType = string;
export type Status4 = string;
/**
 * @maxItems 100
 */
export type IncidentIds = string[];
/**
 * @maxItems 100
 */
export type RelatedAssetIds = string[];
export type MonitoringStatus = string;
export type Id4 = string;
export type ExpectedHash3 = string;
export type Simulated3 = true;
export type Status5 = string;
/**
 * @maxItems 3
 */
export type IncidentIds1 = string[];
/**
 * @maxItems 3
 */
export type HistoricalIncidentIds = string[];
export type ProblemClusterId = string | null;
export type CurrentAgentRole = string | null;
/**
 * @maxItems 100
 */
export type ActiveHypothesisIds = string[];
/**
 * @maxItems 100
 */
export type PendingInspectionIds = string[];
export type CurrentPlanId = string | null;
export type NextAction = "DURABLE_WORKER_OR_HUMAN_REVIEW";
export type GraphRevision1 = number;
export type RuntimeStatus = "DETERMINISTIC_DEVELOPMENT_ONLY_NO_LIVE_AUTHORIZATION";
export type InvestigationId = string;
export type Accepted = true;
export type EventId = string;
export type Status6 = string;
export type Id5 = string;
export type ExpectedHash4 = string;
export type Simulated4 = true;
export type Version = "B20-SERVICE-1";
export type Id6 = string;
export type PickupId = string | null;
export type ReportEvidenceId = string;
export type InvestigationId1 = string;
export type IncidentId1 = string;
export type TargetId = string;
export type RouteId = string;
export type ScheduledAt = string;
export type CheckedAt = string;
export type ActualAt = string | null;
export type RecordedAt = string;
export type Status7 = "COMPLETED" | "MISSED" | "UNKNOWN";
export type SourceKind1 = "SYNTHETIC";
export type SourceId = "B20-synthetic-service-log";
export type RecordId = string;
export type DepartmentId1 = "DEPT-SAN";
export type ObservedBy = string;
export type ReviewedBy = string;
export type Id7 = string;
export type EvidenceId = string;
export type AssetId = string;
export type Code = string;
export type Statement = string;
export type Method = string;
export type ObservedAt = string;
export type Result = "OBSERVED" | "UNKNOWN";
export type Value = number | null;
export type Unit = string | null;
export type VerificationStatus = string;
/**
 * @maxItems 10
 */
export type Findings = FindingDTO[];
export type InspectionId = string;
export type InspectorId = string;
export type DepartmentId2 = string;
export type SourceId1 = string;
export type RecordId1 = string;
export type ObservedAt1 = string;
export type RecordedAt1 = string;
export type Reviewed = boolean;
export type ReviewerId = string | null;
/**
 * @minItems 1
 * @maxItems 3
 */
export type IncidentIds2 = string[];
export type Mode = "OCCURRENCE" | "RETROSPECTIVE";
export type Rationale = string;
/**
 * @maxItems 5
 */
export type BasisEvidenceIds = string[];
/**
 * @maxItems 10
 */
export type Limitations1 = string[];
export type EvidenceType = string;
export type Summary = string;
export type SourceKind2 = string;
export type SourceRecordId = string | null;
export type Reliability = string;
export type ObservedAt2 = string | null;
export type RecordedAt2 = string;
export type DocumentId = string | null;
/**
 * @maxItems 100
 */
export type FindingIds = string[];
export type Reviewed1 = boolean;
export type Id8 = string;
export type ExpectedHash5 = string;
export type Simulated5 = true;
export type Status8 = string;
/**
 * @maxItems 100
 */
export type AssetIds = string[];
export type DepartmentId3 = string;
export type RequestedAt = string;
export type ScheduledAt1 = string | null;
export type CompletedAt = string | null;
export type AssignedInspectorId = string | null;
/**
 * @maxItems 100
 */
export type EvidenceIds = string[];
export type Id9 = string;
export type ExpectedHash6 = string;
export type Simulated6 = true;
export type Statement1 = string;
export type CauseCode = string;
export type Status9 = string;
export type CurrentAssessmentId = string | null;
export type Id10 = string;
export type PreviousAssessmentId = string | null;
export type Assessment = string;
export type AssessedAt = string;
/**
 * @maxItems 100
 */
export type SupportingEvidenceIds = string[];
/**
 * @maxItems 100
 */
export type ContradictingEvidenceIds = string[];
/**
 * @maxItems 100
 */
export type MissingEvidence = string[];
export type Current = boolean;
/**
 * @maxItems 100
 */
export type AssessmentHistory = AssessmentSummary[];
/**
 * @maxItems 100
 */
export type SupportingEvidenceIds1 = string[];
/**
 * @maxItems 100
 */
export type ContradictingEvidenceIds1 = string[];
/**
 * @maxItems 100
 */
export type MissingEvidence1 = string[];
/**
 * @maxItems 100
 */
export type SuspectedAssetIds = string[];
export type LocalTaskId = string;
export type TaskId = string;
export type ActionType = string;
/**
 * @minItems 1
 * @maxItems 5
 */
export type TargetIds = string[];
export type DepartmentId4 = string;
/**
 * @maxItems 12
 */
export type DependsOnTaskIds = string[];
export type Status10 = string;
export type ExpectedHash7 = string;
/**
 * @maxItems 7
 */
export type EligibleAssigneeIds = string[];
/**
 * Validated persisted task IDs and scope; eligible synthetic assignees are choices, never approval or execution authority
 *
 * @maxItems 12
 */
export type TaskBindings = PlanTaskBinding[];
export type PlanId = string;
export type InvestigationId2 = string;
export type Version1 = number;
export type ContentHash = string;
export type InvestigationId3 = string;
export type Issue = "WATERLOGGING" | "ROAD_DAMAGE" | "WASTE_ACCUMULATION";
export type Version2 = number;
export type PreviousPlanId = string | null;
export type SimulationMode1 = "SIMULATED";
export type HypothesisId = string;
export type AssessmentId = string;
export type Reason = string;
export type Addressed = boolean;
/**
 * @minItems 2
 * @maxItems 10
 */
export type Basis = Basis1[];
/**
 * @minItems 1
 * @maxItems 30
 */
export type EvidenceIds1 = string[];
export type Id11 = string;
export type ActionType1 =
  | "INSPECTION"
  | "DRAIN_BLOCKAGE_CLEARANCE"
  | "SUBGRADE_REPAIR"
  | "MISSED_PICKUP_RECOVERY"
  | "UTILITY_ISOLATION"
  | "UTILITY_LEAK_REPAIR";
export type Mode1 = "SUPPORTED_NOW" | "CONDITIONAL";
export type Kind = "CAUSAL_INSPECTION" | "SAFETY_REVIEW" | "ISOLATION_PROOF" | "UTILITY_VERIFICATION";
export type Status11 = "MET" | "UNMET";
/**
 * @maxItems 12
 */
export type EvidenceIds2 = string[];
export type DependsOnTaskId = string | null;
/**
 * @minItems 2
 * @maxItems 4
 */
export type Conditions = Prerequisite[];
/**
 * @minItems 1
 * @maxItems 5
 */
export type TargetIds1 = string[];
export type DepartmentId5 = string;
export type Priority = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
/**
 * @minItems 1
 * @maxItems 8
 */
export type Prerequisites = string[];
/**
 * @maxItems 12
 */
export type DependsOn = string[];
/**
 * @minItems 1
 * @maxItems 12
 */
export type EvidenceIds3 = string[];
/**
 * @minItems 1
 * @maxItems 10
 */
export type AssessmentIds = string[];
export type SourceDocumentId = string;
export type SourceVersion = number;
export type CanonicalDocumentId = string;
export type OwnerDepartmentId = string;
export type SourceUri = string;
export type ContentChecksum = string;
export type QuoteExcerpt = string;
export type PassageLocation = string;
export type ChunkSha256 = string;
export type ConfidenceLabel = "SOURCE_REVIEWED_SYNTHETIC" | "PROPOSED" | "DISPUTED";
export type AssertionStatus = "PROPOSED";
export type RetrievedAt = string;
export type EffectiveFrom = string;
export type DerivedFrom = string | null;
export type TrustedAsInstructions = false;
export type ExpectedOutcome = string;
export type VerificationCriteria = string;
/**
 * @minItems 1
 * @maxItems 8
 */
export type Risks = string[];
/**
 * @minItems 1
 * @maxItems 12
 */
export type Tasks = TaskDraft[];
/**
 * @minItems 1
 * @maxItems 8
 */
export type ExpectedOutcomes = string[];
/**
 * @minItems 1
 * @maxItems 8
 */
export type Risks1 = string[];
/**
 * @minItems 1
 * @maxItems 12
 */
export type Uncertainties = string[];
export type Issue1 = "WATERLOGGING" | "ROAD_DAMAGE" | "WASTE_ACCUMULATION";
/**
 * @minItems 2
 * @maxItems 7
 */
export type RequiredEvidence = (
  | "COMPARABLE_FOLLOWUP_RAINFALL"
  | "FOLLOWUP_WATERLOGGING"
  | "FOLLOWUP_PAVEMENT"
  | "WEAR_EXPOSURE"
  | "SCHEDULED_PICKUPS"
  | "ACTUAL_PICKUPS"
  | "REACCUMULATION_WINDOW"
)[];
export type ObservationOpportunity = string;
export type VerificationCriteria1 = string;
export type MissingOpportunity = "UNRESOLVED";
export type CompletionImpliesResolution = false;
export type Id12 = string;
export type Version3 = number;
export type PlanHash = string;
export type Status12 = "DRAFT";
export type SimulationMode2 = "SIMULATED";
export type Approved = false;
export type Executable = false;
export type Status13 = string;
export type ExpectedHash8 = string;
/**
 * Legacy audited plan lifecycle state; ApprovalDTO.status is the actual approval decision
 */
export type ApprovalStatus = string | null;
export type ExecutionGatesVerified = false;
export type Simulated7 = true;
/**
 * @maxItems 10
 */
export type Limitations2 = string[];
export type Id13 = string;
export type ExpectedHash9 = string;
export type Simulated8 = true;
export type PlanId1 = string;
export type PlanVersion = number;
export type PlanHash1 = string;
export type TaskId1 = string;
export type ActionType2 = string;
/**
 * @minItems 1
 * @maxItems 5
 */
export type TargetIds2 = string[];
export type DepartmentId6 = string;
export type AssigneeId = string;
export type Assignments = Assignment[];
export type Status14 = string;
export type ApprovedBy = string | null;
export type RequestedAt1 = string;
export type ScopeHash = string;
export type Id14 = string;
export type ExpectedHash10 = string;
export type Simulated9 = true;
export type Status15 = string;
export type TaskId2 = string;
export type PlanId2 = string;
export type DepartmentId7 = string;
export type AssigneeId1 = string;
export type ExecutionMode = "SIMULATED";
export type AuthorizedBy = string;
/**
 * @maxItems 100
 */
export type StatusEventIds = string[];
export type ResolutionVerified = boolean;
export type LatestAssessmentStatus = string | null;
/**
 * @maxItems 10
 */
export type Limitations3 = string[];
export type Id15 = string;
export type WorkOrderId = string;
export type AssessmentStatus = string;
export type Result1 = string;
/**
 * @maxItems 20
 */
export type EvidenceIds4 = string[];
export type EvaluatedAt = string;
export type CaseClosed = boolean;
export type PolicyVersion = string | null;
export type Simulated10 = true;
export type Id16 = string;
export type ExpectedHash11 = string;
export type Simulated11 = true;
export type Name = string;
export type DepartmentType = string;
export type Id17 = string;
export type Title = string;
export type SourceKind3 = "SYNTHETIC";
export type Version4 = number;
export type Sha256 = string;
export type OwnerDepartmentId1 = string;
/**
 * @maxItems 5
 */
export type Citations = Citation[];
/**
 * @maxItems 100
 */
export type Gaps = string[];
export type AssertionStatus1 = "PROPOSED";
export type TrustedAsInstructions1 = false;
export type ProcedureId = string;
export type EffectiveFrom1 = string;
export type Id18 = string;
export type Title1 = string;
export type SourceKind4 = "SYNTHETIC";
export type Version5 = number;
export type Sha2561 = string;
export type OwnerDepartmentId2 = string;
/**
 * @maxItems 5
 */
export type Citations1 = Citation[];
/**
 * @maxItems 100
 */
export type Gaps1 = string[];
export type AssertionStatus2 = "PROPOSED";
export type TrustedAsInstructions2 = false;
export type Id19 = string;
export type SourceInvestigationId = string | null;
/**
 * @maxItems 100
 */
export type OutcomeIds = string[];
/**
 * @maxItems 100
 */
export type EvidenceIds5 = string[];
/**
 * @maxItems 100
 */
export type Gaps2 = string[];
export type Truncated = boolean;
export type MemoryType = "RECORDED_CASE_CONTEXT";
export type Summary1 = "Stored historical context; absent records are evidence gaps";
export type LocationId1 = string | null;
export type Condition = string | null;
export type OwnerDepartmentId3 = string | null;
export type Id20 = string;
export type Labels = string[];
export type AssetType = string;
export type Name1 = string;
export type OperationalStatus = string;
/**
 * @maxItems 100
 */
export type DepartmentIds = string[];
/**
 * @maxItems 100
 */
export type LocationIds = string[];
/**
 * @maxItems 100
 */
export type IncidentIds3 = string[];
export type GraphRevision2 = number;
export type AsOf1 = string;
export type GeometryStatus = "LOCATION_REFERENCES" | "UNAVAILABLE";
export type Id21 = string;
/**
 * @maxItems 120
 */
export type NodeIds = string[];
/**
 * @maxItems 200
 */
export type EdgeIds = string[];
/**
 * @maxItems 100
 */
export type EvidenceIds6 = string[];
export type ExecutionId = string;
/**
 * @maxItems 100
 */
export type DecisionPaths = DecisionPath[];
export type Id22 = string;
export type Labels1 = string[];
export type Kind1 = string;
export type DisplayLabel = string;
export type Status16 = string | null;
export type SourceKind5 = string | null;
/**
 * @maxItems 100
 */
export type EvidenceIds7 = string[];
export type ObservedAt3 = string | null;
/**
 * @maxItems 120
 */
export type Nodes = GraphNode[];
export type Id23 = string;
export type Type = string;
export type Source = string;
export type Target = string;
export type ValidFrom = string | null;
export type ValidTo = string | null;
export type ObservedAt4 = string | null;
export type VerificationStatus1 = string;
/**
 * @maxItems 10
 */
export type SourceEvidenceIds = string[];
/**
 * @maxItems 200
 */
export type Edges = GraphEdge[];
/**
 * @maxItems 100
 */
export type DecisionPathIds = string[];
export type GraphRevision3 = number;
export type AsOf2 = string;
export type Truncated1 = boolean;
export type SearchLimited = true;
/**
 * @maxItems 20
 */
export type Reservations = string[];
export type EventId1 = string;
export type InvestigationId4 = string;
export type Timestamp = string;
export type AgentRole = string;
export type Kind2 = "DECISION" | "TOOL";
export type ToolName = string | null;
export type ServerId = string | null;
export type Status17 = string;
export type RationaleSummary = string | null;
export type ArgumentsSha256 = string | null;
export type InputSummary = "values withheld";
export type OutputSha256 = string | null;
export type ValidatedOutput = boolean | null;
export type DurationMs = number | null;
/**
 * @maxItems 200
 */
export type EvidenceIds8 = string[];
/**
 * @maxItems 100
 */
export type GraphPathIds = string[];
export type GraphRevision4 = number | null;
export type ErrorCode = string | null;
export type ExecutionMode1 = string;
export type ParentExecutionId = string | null;
export type DecisionId = string | null;
export type EventId2 = string;
export type Timestamp1 = string;
export type Cursor = number;
export type Id24 = string;
export type EventType = string;
export type EntityId = string;
export type InvestigationId5 = string | null;
export type Revision = number;
export type OccurredAt = string;
export type SourceKind6 = string;
export type SimulationMode3 = "SIMULATED";
export type PayloadSchemaVersion = 1;
export type Operation = string | null;
export type ExecutionId1 = string | null;
export type DecisionId1 = string | null;
export type PlanId3 = string | null;
export type PlanVersion1 = number | null;
export type ApprovalId = string | null;
export type TaskId3 = string | null;
export type NewIncidentId = string | null;
export type ClusterId1 = string | null;
export type PriorOutcomeId = string | null;
export type InvestigatesRelationshipId = string | null;
export type SourceRef = string;
export type SimulationMode4 = true;
export type Type1 = "FeatureCollection";
export type Type2 = "Feature";
export type Id25 = string;
export type Type3 = "Point";
/**
 * @minItems 2
 * @maxItems 2
 */
export type Coordinates = number[];
export type LocationId2 = string;
export type IssueTypes = string[];
export type AssetIds1 = string[];
export type IncidentIds4 = string[];
export type InvestigationIds = string[];
/**
 * @maxItems 50
 */
export type Features = MapFeature[];
/**
 * @maxItems 500
 */
export type UnavailableIds = string[];
export type NextCursor = string | null;
export type TotalCount = number;
export type GraphRevision5 = number;
export type AsOf3 = string;
export type Truncated2 = boolean;
export type Limitations4 = string[];
export type ProblemClusterId1 = string;
export type Status18 = string;
export type VerificationPolicy = string;
/**
 * @maxItems 20
 */
export type RemainingChecks = string[];
/**
 * @maxItems 100
 */
export type OutcomeEvidenceIds = string[];
export type ScenarioId = "S01" | "S02" | "S03" | "S04" | "S05" | "S06" | "S07" | "S08" | "S09" | "S10" | "S11" | "S12";
export type Stage = "BASELINE_VISIBLE" | "EVIDENCE_REVEALED" | "PLAN_AND_APPROVAL" | "FOLLOW_UP";
export type EventId3 = string;
/**
 * @maxItems 3
 */
export type RevealedEvidenceIds = string[];
export type Id26 = "S01" | "S02" | "S03" | "S04" | "S05" | "S06" | "S07" | "S08" | "S09" | "S10" | "S11" | "S12";
export type Title2 = string;
export type IssueTypes1 = string[];
export type Stage1 = "NOT_STARTED" | "BASELINE_VISIBLE" | "EVIDENCE_REVEALED" | "PLAN_AND_APPROVAL" | "FOLLOW_UP";
export type CurrentStage = ("BASELINE_VISIBLE" | "EVIDENCE_REVEALED" | "PLAN_AND_APPROVAL" | "FOLLOW_UP") | null;
export type IssueType2 = "WATERLOGGING" | "ROAD_DAMAGE" | "WASTE_ACCUMULATION";
export type InvestigationId6 = string;
export type IncidentId2 = string;
export type ClusterId2 = string;
export type AssetId1 = string;
export type DepartmentId8 = string;
/**
 * @maxItems 3
 */
export type EvidenceIds9 = string[];
export type PlanId4 = string | null;
export type WorkOrderId1 = string | null;
/**
 * @maxItems 3
 */
export type Cases = ScenarioCase[];
export type NextOperatorSteps = string[];
export type Limitations5 = string[];
/**
 * @maxItems 3
 */
export type ReleasedEvidenceIds = string[];
export type StageAdvanced = boolean;
export type Simulated12 = true;
export type Nodes1 = number;
export type Relationships = number;
export type SourceDocuments = number;
export type SeedFingerprint = string;
export type SourceGraph = string;
export type ProfileReference = string;
export type BaselineContentHash = string;
export type PreviousSourcePreserved = true;
export type Simulated13 = true;
export type CheckpointGraphRevision = number | null;
export type RefreshRequired = boolean;
/**
 * @maxItems 160
 */
export type ErrorCodes = string[];
/**
 * @maxItems 50
 */
export type Items = AgentTraceEvent[];
export type NextCursor1 = string | null;
export type TotalCount1 = number;
export type GraphRevision6 = number;
export type AsOf4 = string;
export type Phase = string | null;
export type PauseReason = string | null;
export type RecoveryRequired = boolean;
export type CurrentAgentRole1 = string | null;
export type ActiveIncidentIds = string[];
export type HistoricalIncidentIds1 = string[];
export type Limitations6 = string[];
/**
 * @maxItems 50
 */
export type Items1 = HypothesisDTO[];
export type NextCursor2 = string | null;
export type TotalCount2 = number;
/**
 * @maxItems 100
 */
export type Limitations7 = string[];
export type Truncated3 = boolean;
/**
 * @maxItems 12
 */
export type Items2 = ScenarioDTO[];
export type NextCursor3 = null;
export type TotalCount3 = number;
export type DefinitionVersion = 1;
export type Simulated14 = true;
export type ExpectedHash12 = string;
/**
 * @maxItems 20
 */
export type EvidenceIds10 = string[];
export type AsOf5 = string;
export type Kind3 = string;
export type Statement2 = string;
export type SourceId2 = string;
export type SourceReference = string;
export type Complaint = WaterIntake | RoadIntake | WasteIntake;
export type Description1 = string;
export type SourceId3 = string;
export type ExternalRecordId = string;
export type SourceChannel = string;
export type SourceVersion1 = string;
export type SourceKind7 = "SYNTHETIC" | "PUBLIC" | "MUNICIPAL" | "USER" | "AGENT";
export type ReportedAt1 = string;
export type OccurredAt1 = string;
export type EndedAt1 = string | null;
export type LocationId3 = string;
/**
 * @maxItems 3
 */
export type AssetIds2 = string[];
/**
 * @maxItems 10
 */
export type EvidenceIds11 = string[];
export type EventReference = string | null;
export type Subtype1 = string;
export type Severity = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
export type IssueType3 = "WATERLOGGING";
export type Name2 =
  "water_depth" | "duration" | "rainfall" | "drain_capacity" | "pothole_depth" | "damage_area" | "waste_quantity";
export type Value1 = number;
export type Unit1 = string;
export type ObservedAt5 = string;
export type SourceId4 = string;
export type SourceReference1 = string;
export type Basis2 = "OBSERVED" | "REPORTED" | "DERIVED";
export type EvidenceId1 = string | null;
/**
 * @maxItems 10
 */
export type Measurements = Measurement[];
/**
 * @maxItems 10
 */
export type Claims = Claim[];
export type RainfallStationReference = string | null;
export type RainfallFrom = string | null;
export type RainfallTo = string | null;
export type Description2 = string;
export type SourceId5 = string;
export type ExternalRecordId1 = string;
export type SourceChannel1 = string;
export type SourceVersion2 = string;
export type SourceKind8 = "SYNTHETIC" | "PUBLIC" | "MUNICIPAL" | "USER" | "AGENT";
export type ReportedAt2 = string;
export type OccurredAt2 = string;
export type EndedAt2 = string | null;
export type LocationId4 = string;
/**
 * @maxItems 3
 */
export type AssetIds3 = string[];
/**
 * @maxItems 10
 */
export type EvidenceIds12 = string[];
export type EventReference1 = string | null;
export type Subtype2 = string;
export type Severity1 = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
export type IssueType4 = "ROAD_DAMAGE";
/**
 * @maxItems 10
 */
export type Measurements1 = Measurement[];
/**
 * @maxItems 10
 */
export type Claims1 = Claim[];
export type DistressDescription = string | null;
export type Description3 = string;
export type SourceId6 = string;
export type ExternalRecordId2 = string;
export type SourceChannel2 = string;
export type SourceVersion3 = string;
export type SourceKind9 = "SYNTHETIC" | "PUBLIC" | "MUNICIPAL" | "USER" | "AGENT";
export type ReportedAt3 = string;
export type OccurredAt3 = string;
export type EndedAt3 = string | null;
export type LocationId5 = string;
/**
 * @maxItems 3
 */
export type AssetIds4 = string[];
/**
 * @maxItems 10
 */
export type EvidenceIds13 = string[];
export type EventReference2 = string | null;
export type Subtype3 = string;
export type Severity2 = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
export type IssueType5 = "WASTE_ACCUMULATION";
/**
 * @maxItems 10
 */
export type Measurements2 = Measurement[];
/**
 * @maxItems 10
 */
export type Claims2 = Claim[];
export type QuantityDescription = string | null;
export type ReportedPickupStatus = "MISSED" | "PARTIAL" | "COMPLETED" | "UNKNOWN";
export type IllegalDumpingClaim = boolean | null;
export type PlanId5 = string;
export type PlanVersion2 = number;
export type PlanHash2 = string;
/**
 * @minItems 1
 * @maxItems 12
 */
export type Assignments1 = Assignment[];
export type ExpectedHash13 = string;
export type Decision = "APPROVED" | "REJECTED";
export type Reason1 = string;
export type Code1 = string;
export type Message = string;
export type BlockerCode = string | null;
export type CorrelationId = string | null;
export type Commitment = "UNKNOWN" | null;
export type EntityId1 = string | null;
export type InvestigationId7 = string | null;
export type PlanId6 = string | null;
export type RequestId = string | null;
export type Retryable = boolean;
export type RequestId1 = string;
export type ExpectedHash14 = string;
/**
 * @maxItems 10
 */
export type EvidenceIds14 = string[];
export type WindowStart = string;
export type WindowEnd = string;
export type InvestigationId8 = string;
/**
 * @minItems 1
 * @maxItems 3
 */
export type AssetIds5 = string[];
export type DepartmentId9 = string;
export type InspectionType = string;
export type OperatorId1 = string;
export type DemoPassword = string;
/**
 * @minItems 1
 * @maxItems 3
 */
export type IncidentIds5 = string[];
export type ClusterId3 = string;
export type Priority1 = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
export type PlanId7 = string;
export type PlanVersion3 = number;
export type PlanHash3 = string;
/**
 * @minItems 1
 * @maxItems 12
 */
export type Assignments2 = Assignment[];
export type ApprovalId1 = string;
export type TaskId4 = string;
/**
 * @maxItems 50
 */
export type Items3 = ApprovalDTO[];
export type NextCursor4 = string | null;
export type TotalCount4 = number;
/**
 * @maxItems 100
 */
export type Limitations8 = string[];
export type Truncated4 = boolean;
/**
 * @maxItems 50
 */
export type Items4 = CaseMemoryDTO[];
export type NextCursor5 = string | null;
export type TotalCount5 = number;
/**
 * @maxItems 100
 */
export type Limitations9 = string[];
export type Truncated5 = boolean;
/**
 * @maxItems 50
 */
export type Items5 = ComplaintDTO[];
export type NextCursor6 = string | null;
export type TotalCount6 = number;
/**
 * @maxItems 100
 */
export type Limitations10 = string[];
export type Truncated6 = boolean;
/**
 * @maxItems 50
 */
export type Items6 = DepartmentDTO[];
export type NextCursor7 = string | null;
export type TotalCount7 = number;
/**
 * @maxItems 100
 */
export type Limitations11 = string[];
export type Truncated7 = boolean;
/**
 * @maxItems 50
 */
export type Items7 = IncidentDTO[];
export type NextCursor8 = string | null;
export type TotalCount8 = number;
/**
 * @maxItems 100
 */
export type Limitations12 = string[];
export type Truncated8 = boolean;
/**
 * @maxItems 50
 */
export type Items8 = MonitoringDTO[];
export type NextCursor9 = string | null;
export type TotalCount9 = number;
/**
 * @maxItems 100
 */
export type Limitations13 = string[];
export type Truncated9 = boolean;
/**
 * @maxItems 50
 */
export type Items9 = OutcomeDTO[];
export type NextCursor10 = string | null;
export type TotalCount10 = number;
/**
 * @maxItems 100
 */
export type Limitations14 = string[];
export type Truncated10 = boolean;
/**
 * @maxItems 50
 */
export type Items10 = PlanDTO[];
export type NextCursor11 = string | null;
export type TotalCount11 = number;
/**
 * @maxItems 100
 */
export type Limitations15 = string[];
export type Truncated11 = boolean;
/**
 * @maxItems 50
 */
export type Items11 = ProblemClusterDTO[];
export type NextCursor12 = string | null;
export type TotalCount12 = number;
/**
 * @maxItems 100
 */
export type Limitations16 = string[];
export type Truncated12 = boolean;
/**
 * @maxItems 50
 */
export type Items12 = ProcedureDTO[];
export type NextCursor13 = string | null;
export type TotalCount13 = number;
/**
 * @maxItems 100
 */
export type Limitations17 = string[];
export type Truncated13 = boolean;
/**
 * @maxItems 50
 */
export type Items13 = WorkOrderDTO[];
export type NextCursor14 = string | null;
export type TotalCount14 = number;
/**
 * @maxItems 100
 */
export type Limitations18 = string[];
export type Truncated14 = boolean;
export type ExpectedHash15 = string;
export type Action = "START" | "BLOCK" | "FAIL" | "COMPLETE";
export type Reason2 = string;
/**
 * @maxItems 10
 */
export type EvidenceIds15 = string[];
/**
 * @minItems 1
 * @maxItems 3
 */
export type IncidentIds6 = string[];
/**
 * @minItems 1
 * @maxItems 3
 */
export type AssetIds6 = string[];
export type CauseCode1 = string;
export type Statement3 = string;
export type Mechanism = string;
/**
 * @minItems 1
 * @maxItems 10
 */
export type ConfirmingCodes = string[];
/**
 * @minItems 1
 * @maxItems 10
 */
export type FalsifyingCodes = string[];
export type SourceId7 = string;
export type TargetId1 = string;
export type Operation1 = "reachability" | "dependencies";
export type MaxHops = number;
export type ExpectedHash16 = string;
/**
 * @maxItems 10
 */
export type EvidenceIds16 = string[];
export type WindowStart1 = string;
export type WindowEnd1 = string;
export type VerifiedOutcomeId = string;
export type Complaint1 = WaterIntake | RoadIntake | WasteIntake;
export type ExpectedHash17 = string;
export type SourceId8 = string;
export type RecordId2 = string;
export type SourceKind10 = "SYNTHETIC" | "MUNICIPAL" | "PUBLIC";
/**
 * @minItems 1
 * @maxItems 10
 */
export type Observations = Observation[];
export type Reason3 = string;
export type PlanVersion4 = number;
export type PlanHash4 = string;
/**
 * @minItems 1
 * @maxItems 12
 */
export type Assignments3 = Assignment[];
export type RequestId2 = string;
export type SchemaVersion = 1;
export type RequestId3 = string;
export type SchemaVersion1 = 1;
export type RequestId4 = string;
export type SchemaVersion2 = 1;
export type RequestId5 = string;
export type SchemaVersion3 = 1;
export type RequestId6 = string;
export type SchemaVersion4 = 1;
export type RequestId7 = string;
export type SchemaVersion5 = 1;
export type RequestId8 = string;
export type SchemaVersion6 = 1;
export type RequestId9 = string;
export type SchemaVersion7 = 1;
export type RequestId10 = string;
export type SchemaVersion8 = 1;
export type RequestId11 = string;
export type SchemaVersion9 = 1;
export type RequestId12 = string;
export type SchemaVersion10 = 1;
export type RequestId13 = string;
export type SchemaVersion11 = 1;
export type RequestId14 = string;
export type SchemaVersion12 = 1;
export type RequestId15 = string;
export type SchemaVersion13 = 1;
export type RequestId16 = string;
export type SchemaVersion14 = 1;
export type RequestId17 = string;
export type SchemaVersion15 = 1;
export type RequestId18 = string;
export type SchemaVersion16 = 1;
export type RequestId19 = string;
export type SchemaVersion17 = 1;
export type RequestId20 = string;
export type SchemaVersion18 = 1;
export type RequestId21 = string;
export type SchemaVersion19 = 1;
export type RequestId22 = string;
export type SchemaVersion20 = 1;
export type RequestId23 = string;
export type SchemaVersion21 = 1;
export type RequestId24 = string;
export type SchemaVersion22 = 1;
export type RequestId25 = string;
export type SchemaVersion23 = 1;
export type RequestId26 = string;
export type SchemaVersion24 = 1;
export type RequestId27 = string;
export type SchemaVersion25 = 1;
export type RequestId28 = string;
export type SchemaVersion26 = 1;
export type ExpectedHash18 = string;
export type Status19 = "REQUESTED" | "SCHEDULED" | "IN_PROGRESS" | "FAILED" | "CANCELLED";
export type ScheduledAt2 = string | null;
export type ExpectedHash19 = string;
export type NewStatus = "ASSIGNED" | "CANCELLED";
export type Reason4 = string;
export type Operation2 = "assess";
export type HypothesisId1 = string;
export type ExpectedHash20 = string;
/**
 * @maxItems 20
 */
export type EvidenceIds17 = string[];
export type AsOf6 = string;
export type Operation3 = "request_inspection";
export type InvestigationId9 = string;
/**
 * @minItems 1
 * @maxItems 3
 */
export type AssetIds7 = string[];
export type DepartmentId10 = string;
export type InspectionType1 = string;
export type Operation4 = "report_inspection";
export type InspectionId1 = string;
export type ExpectedHash21 = string;
export type SourceId9 = string;
export type RecordId3 = string;
export type SourceKind11 = "SYNTHETIC" | "MUNICIPAL" | "PUBLIC";
/**
 * @minItems 1
 * @maxItems 10
 */
export type Observations1 = Observation[];
export type ExpectedHash22 = string;
export type Purpose = "COMPLETION" | "FOLLOWUP" | "ASSESSMENT";
export type Command = WorkInspectionCreate | WorkInspectionTransition | WorkInspectionReport | WorkAssessment;
export type Operation5 = "transition_inspection";
export type InspectionId2 = string;
export type ExpectedHash23 = string;
export type Status20 = "REQUESTED" | "SCHEDULED" | "IN_PROGRESS" | "FAILED" | "CANCELLED";
export type ScheduledAt3 = string | null;
export type ReviewReason = string | null;
/**
 * @maxItems 50
 */
export type Items14 = ComplaintDTO[];
export type NextCursor15 = string | null;
export type TotalCount15 = number;
/**
 * @maxItems 100
 */
export type Limitations19 = string[];
export type Truncated15 = boolean;
/**
 * @maxItems 50
 */
export type Items15 = IncidentDTO[];
export type NextCursor16 = string | null;
export type TotalCount16 = number;
/**
 * @maxItems 100
 */
export type Limitations20 = string[];
export type Truncated16 = boolean;
/**
 * @maxItems 50
 */
export type Items16 = ProblemClusterDTO[];
export type NextCursor17 = string | null;
export type TotalCount17 = number;
/**
 * @maxItems 100
 */
export type Limitations21 = string[];
export type Truncated17 = boolean;
/**
 * @maxItems 50
 */
export type Items17 = ApprovalDTO[];
export type NextCursor18 = string | null;
export type TotalCount18 = number;
/**
 * @maxItems 100
 */
export type Limitations22 = string[];
export type Truncated18 = boolean;
/**
 * @maxItems 50
 */
export type Items18 = WorkOrderDTO[];
export type NextCursor19 = string | null;
export type TotalCount19 = number;
/**
 * @maxItems 100
 */
export type Limitations23 = string[];
export type Truncated19 = boolean;
/**
 * @maxItems 50
 */
export type Items19 = DepartmentDTO[];
export type NextCursor20 = string | null;
export type TotalCount20 = number;
/**
 * @maxItems 100
 */
export type Limitations24 = string[];
export type Truncated20 = boolean;
/**
 * @maxItems 50
 */
export type Items20 = PlanDTO[];
export type NextCursor21 = string | null;
export type TotalCount21 = number;
/**
 * @maxItems 100
 */
export type Limitations25 = string[];
export type Truncated21 = boolean;
/**
 * @maxItems 50
 */
export type Items21 = ProcedureDTO[];
export type NextCursor22 = string | null;
export type TotalCount22 = number;
/**
 * @maxItems 100
 */
export type Limitations26 = string[];
export type Truncated22 = boolean;
/**
 * @maxItems 50
 */
export type Items22 = CaseMemoryDTO[];
export type NextCursor23 = string | null;
export type TotalCount23 = number;
/**
 * @maxItems 100
 */
export type Limitations27 = string[];
export type Truncated23 = boolean;
/**
 * @maxItems 50
 */
export type Items23 = MonitoringDTO[];
export type NextCursor24 = string | null;
export type TotalCount24 = number;
/**
 * @maxItems 100
 */
export type Limitations28 = string[];
export type Truncated24 = boolean;
/**
 * @maxItems 50
 */
export type Items24 = OutcomeDTO[];
export type NextCursor25 = string | null;
export type TotalCount25 = number;
/**
 * @maxItems 100
 */
export type Limitations29 = string[];
export type Truncated25 = boolean;
export type RequestId29 = string;
export type SchemaVersion27 = 1;
export type RequestId30 = string;
export type SchemaVersion28 = 1;
export type RequestId31 = string;
export type SchemaVersion29 = 1;
export type RequestId32 = string;
export type SchemaVersion30 = 1;
export type RequestId33 = string;
export type SchemaVersion31 = 1;
export type RequestId34 = string;
export type SchemaVersion32 = 1;
export type RequestId35 = string;
export type SchemaVersion33 = 1;
export type Limit = number;
export type Cursor1 = string | null;
export type Issue2 = ("WATERLOGGING" | "ROAD_DAMAGE" | "WASTE_ACCUMULATION") | null;
export type Status21 = string | null;
export type DepartmentId11 = string | null;
export type After = string | null;
export type Before = string | null;
export type Depth = number;
export type IncludeCandidates = boolean;
export type Limit1 = number;
export type Cursor2 = string | null;
export type Status22 = string | null;
export type Issue3 = ("WATERLOGGING" | "ROAD_DAMAGE" | "WASTE_ACCUMULATION") | null;
export type Status23 = string | null;
export type DepartmentId12 = string | null;
export type After1 = string | null;
export type Before1 = string | null;
export type Limit2 = number;
export type Cursor3 = string | null;
export type Status24 = string | null;
export type After2 = string | null;
export type Before2 = string | null;
export type Limit3 = number;
export type Cursor4 = string | null;
export type Issue4 = ("WATERLOGGING" | "ROAD_DAMAGE" | "WASTE_ACCUMULATION") | null;
export type Status25 = string | null;
export type DepartmentId13 = string | null;
export type After3 = string | null;
export type Before3 = string | null;
export type InvestigationId10 = string | null;
export type Id27 = "S01" | "S02" | "S03" | "S04" | "S05" | "S06" | "S07" | "S08" | "S09" | "S10" | "S11" | "S12";
export type Title3 = string;
export type IssueTypes2 = string[];
export type CurrentStage1 = ("BASELINE_VISIBLE" | "EVIDENCE_REVEALED" | "PLAN_AND_APPROVAL" | "FOLLOW_UP") | null;
/**
 * @maxItems 3
 */
export type Cases1 = ScenarioCase[];
export type NextOperatorSteps1 = string[];
export type Limitations30 = string[];
export type ScenarioId1 = "S01" | "S02" | "S03" | "S04" | "S05" | "S06" | "S07" | "S08" | "S09" | "S10" | "S11" | "S12";
export type Seed = 19;
export type Confirm = true;
export type Variant = "PRIMARY" | "NEGATIVE";
export type ExpectedCurrentStage = "BASELINE_VISIBLE" | "EVIDENCE_REVEALED" | "PLAN_AND_APPROVAL" | "FOLLOW_UP";
export type Stage2 = "EVIDENCE_REVEALED" | "PLAN_AND_APPROVAL" | "FOLLOW_UP";
export type InvestigationId11 = string | null;
export type InspectionId3 = string | null;
export type ExpectedHash24 = string | null;
export type PlanId8 = string | null;
export type WorkOrderId2 = string | null;
export type AssetId2 = string;
export type DepartmentId14 = string;
export type SourceId10 = string;
export type SourceRecordId1 = string;
export type SourceVersion4 = number;
export type SourceKind12 = "SYNTHETIC";
export type ObservedAt6 = string;
export type ValidFrom1 = string;
export type ValidTo1 = string | null;
export type ExpectedHash25 = string;
export type Reviewed2 = true;
export type Reason5 = string;
export type Id28 = string;
export type AssetId3 = string;
export type DepartmentId15 = string;
export type SourceId11 = string;
export type SourceRecordId2 = string;
export type SourceVersion5 = number;
export type SourceKind13 = "SYNTHETIC";
export type ObservedAt7 = string;
export type ValidFrom2 = string;
export type ValidTo2 = string | null;
export type SubmittedBy = string;
export type ReviewedBy1 = string | null;
export type Status26 = "SUBMITTED" | "VERIFIED";
export type Applicability = "UNREVIEWED" | "HISTORICAL" | "FUTURE" | "CURRENT";
export type ExpectedHash26 = string;
export type SourceEvidenceId = string;
export type ReviewEvidenceId = string | null;
export type RelationshipId = string | null;
export type EventId4 = string;
export type AsOf7 = string;
export type SimulationMode5 = true;
/**
 * @maxItems 50
 */
export type Items25 = InvestigationDTO[];
export type NextCursor26 = string | null;
export type TotalCount26 = number;
/**
 * @maxItems 100
 */
export type Limitations31 = string[];
export type Truncated26 = boolean;

export interface ApiModels {
  Ack: Ack;
  DemoSession: DemoSession;
  OperatorAccount: OperatorAccount;
  HealthDTO: HealthDTO;
  DashboardSummary: DashboardSummary;
  ComplaintDTO: ComplaintDTO;
  IncidentDTO: IncidentDTO;
  ProblemClusterDTO: ProblemClusterDTO;
  InvestigationDTO: InvestigationDTO;
  AgentResumeDTO: AgentResumeDTO;
  EvidenceDTO: EvidenceDTO;
  InspectionDTO: InspectionDTO;
  HypothesisDTO: HypothesisDTO;
  PlanDTO: PlanDTO;
  ApprovalDTO: ApprovalDTO;
  WorkOrderDTO: WorkOrderDTO;
  OutcomeDTO: OutcomeDTO;
  DepartmentDTO: DepartmentDTO;
  ProcedureDTO: ProcedureDTO;
  DocumentDTO: DocumentDTO;
  CaseMemoryDTO: CaseMemoryDTO;
  AssetDTO: AssetDTO;
  GraphNodeDTO: GraphNodeDTO;
  GraphEdgeDTO: GraphEdgeDTO;
  GraphSubgraphDTO: GraphSubgraphDTO;
  AgentTraceEvent: AgentTraceEvent;
  SSEStream: SSEStream;
  MapFeatureCollection: MapFeatureCollection;
  MonitoringDTO: MonitoringDTO;
  SimulationStepDTO: SimulationStepDTO;
  SeedReport: SeedReport;
  ScenarioDTO: ScenarioDTO;
  ComplaintPage: ComplaintPage;
  IncidentPage: IncidentPage;
  ClusterPage: ClusterPage;
  AgentTracePage: AgentTracePage;
  HypothesisPage: HypothesisPage;
  ApprovalPage: ApprovalPage;
  WorkOrderPage: WorkOrderPage;
  DepartmentPage: DepartmentPage;
  ProcedurePage: ProcedurePage;
  CaseMemoryPage: CaseMemoryPage;
  MonitoringPage: MonitoringPage;
  OutcomePage: OutcomePage;
  ScenarioPage: ScenarioPage;
  "auth_demo-login_Request": AuthDemoLogin_Request;
  auth_logout_Request: AuthLogout_Request;
  complaints_Request: Complaints_Request;
  investigations_Request: Investigations_Request;
  investigations_id_resume_Request: InvestigationsIdResume_Request;
  inspections_id_observations_Request: InspectionsIdObservations_Request;
  "plans_id_submit-approval_Request": PlansIdSubmitApproval_Request;
  approvals_id_decision_Request: ApprovalsIdDecision_Request;
  "work-orders_id_status_Request": WorkOrdersIdStatus_Request;
  "work-orders_id_outcomes_Request": WorkOrdersIdOutcomes_Request;
  demo_reset_Request: DemoReset_Request;
  demo_scenarios_id_advance_Request: DemoScenariosIdAdvance_Request;
  AssessRequest: AssessRequest;
  Assignment: Assignment;
  Basis: Basis1;
  Citation: Citation;
  Claim: Claim;
  ComplaintRequest: ComplaintRequest;
  DecideRequest: DecideRequest;
  DraftRequest: DraftRequest;
  EmptyRequest: EmptyRequest;
  ErrorBody: ErrorBody;
  ErrorDetails: ErrorDetails;
  ErrorEnvelope: ErrorEnvelope;
  EvaluateRequest: EvaluateRequest;
  IncidentAttribution: IncidentAttribution;
  InspectionRequest: InspectionRequest;
  LoginRequest: LoginRequest;
  Measurement: Measurement;
  Monitoring: Monitoring;
  Observation: Observation;
  OpenRequest: OpenRequest;
  OrderRequest: OrderRequest;
  Page_ApprovalDTO_: PageApprovalDTO;
  Page_CaseMemoryDTO_: PageCaseMemoryDTO;
  Page_ComplaintDTO_: PageComplaintDTO;
  Page_DepartmentDTO_: PageDepartmentDTO;
  Page_IncidentDTO_: PageIncidentDTO;
  Page_MonitoringDTO_: PageMonitoringDTO;
  Page_OutcomeDTO_: PageOutcomeDTO;
  Page_PlanDTO_: PagePlanDTO;
  Page_ProblemClusterDTO_: PageProblemClusterDTO;
  Page_ProcedureDTO_: PageProcedureDTO;
  Page_WorkOrderDTO_: PageWorkOrderDTO;
  PlanDraft: PlanDraft;
  PlanReceipt: PlanReceipt;
  Prerequisite: Prerequisite;
  ProgressRequest: ProgressRequest;
  ProposeRequest: ProposeRequest;
  RecurRequest: RecurRequest;
  Remediation: Remediation;
  ReportRequest: ReportRequest;
  ResumeRequest: ResumeRequest;
  RoadDetails: RoadDetails;
  RoadIntake: RoadIntake;
  SubmitRequest: SubmitRequest;
  Success_Ack_: SuccessAck;
  Success_AgentResumeDTO_: SuccessAgentResumeDTO;
  Success_ApprovalDTO_: SuccessApprovalDTO;
  Success_ComplaintDTO_: SuccessComplaintDTO;
  Success_DemoSession_: SuccessDemoSession;
  Success_DocumentDTO_: SuccessDocumentDTO;
  Success_EvidenceDTO_: SuccessEvidenceDTO;
  Success_HealthDTO_: SuccessHealthDTO;
  Success_IncidentDTO_: SuccessIncidentDTO;
  Success_InspectionDTO_: SuccessInspectionDTO;
  Success_InvestigationDTO_: SuccessInvestigationDTO;
  Success_OperatorAccount_: SuccessOperatorAccount;
  Success_OutcomeDTO_: SuccessOutcomeDTO;
  Success_Page_ApprovalDTO__: SuccessPageApprovalDTO;
  Success_Page_CaseMemoryDTO__: SuccessPageCaseMemoryDTO;
  Success_Page_ComplaintDTO__: SuccessPageComplaintDTO;
  Success_Page_DepartmentDTO__: SuccessPageDepartmentDTO;
  Success_Page_IncidentDTO__: SuccessPageIncidentDTO;
  Success_Page_MonitoringDTO__: SuccessPageMonitoringDTO;
  Success_Page_OutcomeDTO__: SuccessPageOutcomeDTO;
  Success_Page_PlanDTO__: SuccessPagePlanDTO;
  Success_Page_ProblemClusterDTO__: SuccessPageProblemClusterDTO;
  Success_Page_ProcedureDTO__: SuccessPageProcedureDTO;
  Success_Page_WorkOrderDTO__: SuccessPageWorkOrderDTO;
  Success_PlanDTO_: SuccessPlanDTO;
  Success_ProblemClusterDTO_: SuccessProblemClusterDTO;
  Success_WorkOrderDTO_: SuccessWorkOrderDTO;
  TaskDraft: TaskDraft;
  Topology: Topology;
  TransitionRequest: TransitionRequest;
  UpdateRequest: UpdateRequest;
  WasteDetails: WasteDetails;
  WasteIntake: WasteIntake;
  WaterDetails: WaterDetails;
  WaterIntake: WaterIntake;
  WorkAssessment: WorkAssessment;
  WorkInspectionCreate: WorkInspectionCreate;
  WorkInspectionReport: WorkInspectionReport;
  WorkInspectionRequest: WorkInspectionRequest;
  WorkInspectionTransition: WorkInspectionTransition;
  "Page[ComplaintDTO]": PageComplaintDTO1;
  "Page[IncidentDTO]": PageIncidentDTO1;
  "Page[ProblemClusterDTO]": PageProblemClusterDTO1;
  "Page[ApprovalDTO]": PageApprovalDTO1;
  "Page[WorkOrderDTO]": PageWorkOrderDTO1;
  "Page[DepartmentDTO]": PageDepartmentDTO1;
  "Page[PlanDTO]": PagePlanDTO1;
  "Page[ProcedureDTO]": PageProcedureDTO1;
  "Page[CaseMemoryDTO]": PageCaseMemoryDTO1;
  "Page[MonitoringDTO]": PageMonitoringDTO1;
  "Page[OutcomeDTO]": PageOutcomeDTO1;
  AssessmentSummary: AssessmentSummary;
  Success_HypothesisDTO_: SuccessHypothesisDTO;
  DecisionPath: DecisionPath;
  FindingDTO: FindingDTO;
  GraphEdge: GraphEdge;
  GraphNode: GraphNode;
  MapFeature: MapFeature;
  ObservationSource: ObservationSource;
  Point: Point;
  Success_AgentTracePage_: SuccessAgentTracePage;
  Success_AssetDTO_: SuccessAssetDTO;
  Success_DashboardSummary_: SuccessDashboardSummary;
  Success_GraphSubgraphDTO_: SuccessGraphSubgraphDTO;
  Success_HypothesisPage_: SuccessHypothesisPage;
  Success_MapFeatureCollection_: SuccessMapFeatureCollection;
  PublicPayload: PublicPayload;
  ResourceQuery: ResourceQuery;
  GraphQuery: GraphQuery;
  HypothesesQuery: HypothesesQuery;
  DashboardQuery: DashboardQuery;
  AssetQuery: AssetQuery;
  TraceQuery: TraceQuery;
  MapQuery: MapQuery;
  ScenarioCase: ScenarioCase;
  ScenarioSummary: ScenarioSummary;
  DemoResetRequest: DemoResetRequest;
  DemoAdvanceRequest: DemoAdvanceRequest;
  ResponsibilitySubmission: ResponsibilitySubmission;
  ResponsibilityReview: ResponsibilityReview;
  ResponsibilityDTO: ResponsibilityDTO;
  ServiceRecord: ServiceRecord;
  "Page[InvestigationDTO]": PageInvestigationDTO;
  PlanTaskBinding: PlanTaskBinding;
}
export interface Ack {
  status: Status;
}
export interface DemoSession {
  access_token: AccessToken;
  expires_at: ExpiresAt;
  operator_id: OperatorId;
  role: Role;
}
export interface OperatorAccount {
  id: Id;
  display_name: DisplayName;
  role: Role1;
  department_id: DepartmentId;
  enabled?: Enabled;
}
export interface HealthDTO {
  status: Status1;
  dependencies: Dependencies;
  runtime_mode?: RuntimeMode;
}
export interface Dependencies {
  [k: string]: "ready" | "unavailable" | "not_checked";
}
export interface DashboardSummary {
  active_incidents: ActiveIncidents;
  active_clusters: ActiveClusters;
  pending_approvals: PendingApprovals;
  completed_work_orders: CompletedWorkOrders;
  verified_work_orders: VerifiedWorkOrders;
  issue_counts: IssueCounts;
  graph_revision: GraphRevision;
  as_of: AsOf;
  definitions: Definitions;
  limitations: Limitations;
  open_clusters: OpenClusters;
  active_investigations: ActiveInvestigations;
  recurrence_counts: RecurrenceCounts;
  simulation_mode?: SimulationMode;
}
export interface IssueCounts {
  [k: string]: number;
}
export interface RecurrenceCounts {
  [k: string]: number;
}
export interface ComplaintDTO {
  id: Id1;
  expected_hash: ExpectedHash;
  simulated?: Simulated;
  description: Description;
  incident_id: IncidentId;
  reported_at: ReportedAt;
  source_kind: SourceKind;
  status: Status2;
  issue_type: IssueType;
}
export interface IncidentDTO {
  id: Id2;
  expected_hash: ExpectedHash1;
  simulated?: Simulated1;
  issue_type: IssueType1;
  subtype: Subtype;
  location_id: LocationId;
  started_at: StartedAt;
  ended_at: EndedAt;
  status: Status3;
  cluster_id: ClusterId;
  complaint_ids: ComplaintIds;
}
export interface ProblemClusterDTO {
  id: Id3;
  expected_hash: ExpectedHash2;
  simulated?: Simulated2;
  pattern_type: PatternType;
  status: Status4;
  incident_ids: IncidentIds;
  related_asset_ids: RelatedAssetIds;
  monitoring_status: MonitoringStatus;
}
export interface InvestigationDTO {
  id: Id4;
  expected_hash: ExpectedHash3;
  simulated?: Simulated3;
  status: Status5;
  incident_ids: IncidentIds1;
  historical_incident_ids: HistoricalIncidentIds;
  problem_cluster_id: ProblemClusterId;
  current_agent_role?: CurrentAgentRole;
  active_hypothesis_ids: ActiveHypothesisIds;
  pending_inspection_ids: PendingInspectionIds;
  current_plan_id: CurrentPlanId;
  next_action?: NextAction;
  graph_revision: GraphRevision1;
  runtime_status?: RuntimeStatus;
}
export interface AgentResumeDTO {
  investigation_id: InvestigationId;
  accepted?: Accepted;
  event_id: EventId;
  status: Status6;
}
export interface EvidenceDTO {
  id: Id5;
  expected_hash: ExpectedHash4;
  simulated?: Simulated4;
  service_record?: ServiceRecord | null;
  findings?: Findings;
  observation_source?: ObservationSource | null;
  limitations?: Limitations1;
  evidence_type: EvidenceType;
  summary: Summary;
  source_kind: SourceKind2;
  source_record_id: SourceRecordId;
  reliability: Reliability;
  observed_at: ObservedAt2;
  recorded_at: RecordedAt2;
  document_id: DocumentId;
  finding_ids?: FindingIds;
  reviewed: Reviewed1;
}
export interface ServiceRecord {
  version?: Version;
  id: Id6;
  pickup_id: PickupId;
  report_evidence_id: ReportEvidenceId;
  investigation_id: InvestigationId1;
  incident_id: IncidentId1;
  target_id: TargetId;
  route_id: RouteId;
  scheduled_at: ScheduledAt;
  checked_at: CheckedAt;
  actual_at: ActualAt;
  recorded_at: RecordedAt;
  status: Status7;
  source_kind?: SourceKind1;
  source_id?: SourceId;
  record_id: RecordId;
  department_id?: DepartmentId1;
  observed_by: ObservedBy;
  reviewed_by: ReviewedBy;
}
export interface FindingDTO {
  id: Id7;
  evidence_id: EvidenceId;
  observation: Observation;
  verification_status: VerificationStatus;
}
export interface Observation {
  asset_id: AssetId;
  code: Code;
  statement: Statement;
  method: Method;
  observed_at: ObservedAt;
  result?: Result;
  value?: Value;
  unit?: Unit;
}
export interface ObservationSource {
  inspection_id: InspectionId;
  inspector_id: InspectorId;
  department_id: DepartmentId2;
  source_id: SourceId1;
  record_id: RecordId1;
  observed_at: ObservedAt1;
  recorded_at: RecordedAt1;
  reviewed: Reviewed;
  reviewer_id: ReviewerId;
  attribution: IncidentAttribution | null;
}
/**
 * Optional explicit occurrence binding; retrospective claims require prior source basis.
 */
export interface IncidentAttribution {
  incident_ids: IncidentIds2;
  mode?: Mode;
  rationale: Rationale;
  basis_evidence_ids?: BasisEvidenceIds;
}
export interface InspectionDTO {
  id: Id8;
  expected_hash: ExpectedHash5;
  simulated?: Simulated5;
  status: Status8;
  asset_ids: AssetIds;
  department_id: DepartmentId3;
  requested_at: RequestedAt;
  scheduled_at: ScheduledAt1;
  completed_at: CompletedAt;
  assigned_inspector_id: AssignedInspectorId;
  evidence_ids: EvidenceIds;
}
export interface HypothesisDTO {
  id: Id9;
  expected_hash: ExpectedHash6;
  simulated?: Simulated6;
  statement: Statement1;
  cause_code: CauseCode;
  status: Status9;
  current_assessment_id: CurrentAssessmentId;
  assessment_history: AssessmentHistory;
  supporting_evidence_ids: SupportingEvidenceIds1;
  contradicting_evidence_ids: ContradictingEvidenceIds1;
  missing_evidence: MissingEvidence1;
  suspected_asset_ids: SuspectedAssetIds;
}
export interface AssessmentSummary {
  id: Id10;
  previous_assessment_id: PreviousAssessmentId;
  assessment: Assessment;
  assessed_at: AssessedAt;
  supporting_evidence_ids: SupportingEvidenceIds;
  contradicting_evidence_ids: ContradictingEvidenceIds;
  missing_evidence: MissingEvidence;
  current: Current;
}
export interface PlanDTO {
  task_bindings?: TaskBindings;
  plan_id: PlanId;
  investigation_id: InvestigationId2;
  version: Version1;
  content_hash: ContentHash;
  draft: PlanDraft;
  draft_receipt: PlanReceipt;
  status: Status13;
  expected_hash: ExpectedHash8;
  approval_status: ApprovalStatus;
  execution_gates_verified?: ExecutionGatesVerified;
  simulated?: Simulated7;
  limitations: Limitations2;
}
export interface PlanTaskBinding {
  local_task_id: LocalTaskId;
  task_id: TaskId;
  action_type: ActionType;
  target_ids: TargetIds;
  department_id: DepartmentId4;
  depends_on_task_ids: DependsOnTaskIds;
  status: Status10;
  expected_hash: ExpectedHash7;
  eligible_assignee_ids: EligibleAssigneeIds;
}
export interface PlanDraft {
  investigation_id: InvestigationId3;
  issue: Issue;
  version: Version2;
  previous_plan_id?: PreviousPlanId;
  simulation_mode?: SimulationMode1;
  basis: Basis;
  evidence_ids: EvidenceIds1;
  tasks: Tasks;
  expected_outcomes: ExpectedOutcomes;
  risks: Risks1;
  uncertainties: Uncertainties;
  monitoring: Monitoring;
}
export interface Basis1 {
  hypothesis_id: HypothesisId;
  assessment_id: AssessmentId;
  reason: Reason;
  addressed: Addressed;
}
export interface TaskDraft {
  id: Id11;
  action_type: ActionType1;
  remediation?: Remediation | null;
  target_ids: TargetIds1;
  department_id: DepartmentId5;
  priority: Priority;
  prerequisites: Prerequisites;
  depends_on?: DependsOn;
  evidence_ids: EvidenceIds3;
  assessment_ids: AssessmentIds;
  procedure_citation: Citation;
  expected_outcome: ExpectedOutcome;
  verification_criteria: VerificationCriteria;
  risks: Risks;
}
export interface Remediation {
  mode: Mode1;
  conditions: Conditions;
}
export interface Prerequisite {
  kind: Kind;
  status: Status11;
  evidence_ids?: EvidenceIds2;
  depends_on_task_id?: DependsOnTaskId;
}
export interface Citation {
  source_document_id: SourceDocumentId;
  source_version: SourceVersion;
  canonical_document_id: CanonicalDocumentId;
  owner_department_id: OwnerDepartmentId;
  source_uri: SourceUri;
  content_checksum: ContentChecksum;
  quote_excerpt: QuoteExcerpt;
  passage_location: PassageLocation;
  chunk_sha256: ChunkSha256;
  confidence_label: ConfidenceLabel;
  assertion_status?: AssertionStatus;
  retrieved_at: RetrievedAt;
  effective_from: EffectiveFrom;
  derived_from?: DerivedFrom;
  trusted_as_instructions?: TrustedAsInstructions;
}
export interface Monitoring {
  issue: Issue1;
  required_evidence: RequiredEvidence;
  observation_opportunity: ObservationOpportunity;
  verification_criteria: VerificationCriteria1;
  missing_opportunity?: MissingOpportunity;
  completion_implies_resolution?: CompletionImpliesResolution;
}
export interface PlanReceipt {
  id: Id12;
  version: Version3;
  plan_hash: PlanHash;
  status?: Status12;
  simulation_mode?: SimulationMode2;
  approved?: Approved;
  executable?: Executable;
}
export interface ApprovalDTO {
  id: Id13;
  expected_hash: ExpectedHash9;
  simulated?: Simulated8;
  plan_id: PlanId1;
  plan_version: PlanVersion;
  plan_hash: PlanHash1;
  assignments: Assignments;
  status: Status14;
  approved_by: ApprovedBy;
  requested_at: RequestedAt1;
  scope_hash: ScopeHash;
}
export interface Assignment {
  task_id: TaskId1;
  action_type: ActionType2;
  target_ids: TargetIds2;
  department_id: DepartmentId6;
  assignee_id: AssigneeId;
}
export interface WorkOrderDTO {
  id: Id14;
  expected_hash: ExpectedHash10;
  simulated?: Simulated9;
  status: Status15;
  task_id: TaskId2;
  plan_id: PlanId2;
  department_id: DepartmentId7;
  assignee_id: AssigneeId1;
  execution_mode?: ExecutionMode;
  authorized_by: AuthorizedBy;
  status_event_ids: StatusEventIds;
  resolution_verified?: ResolutionVerified;
  latest_assessment_status?: LatestAssessmentStatus;
  limitations?: Limitations3;
}
export interface OutcomeDTO {
  id: Id15;
  work_order_id: WorkOrderId;
  assessment_status: AssessmentStatus;
  result: Result1;
  evidence_ids: EvidenceIds4;
  evaluated_at: EvaluatedAt;
  case_closed: CaseClosed;
  policy_version: PolicyVersion;
  simulated?: Simulated10;
}
export interface DepartmentDTO {
  id: Id16;
  expected_hash: ExpectedHash11;
  simulated?: Simulated11;
  name: Name;
  department_type: DepartmentType;
}
export interface ProcedureDTO {
  id: Id17;
  title: Title;
  source_kind?: SourceKind3;
  version: Version4;
  sha256: Sha256;
  owner_department_id: OwnerDepartmentId1;
  citations: Citations;
  gaps: Gaps;
  assertion_status?: AssertionStatus1;
  trusted_as_instructions?: TrustedAsInstructions1;
  procedure_id: ProcedureId;
  effective_from: EffectiveFrom1;
}
export interface DocumentDTO {
  id: Id18;
  title: Title1;
  source_kind?: SourceKind4;
  version: Version5;
  sha256: Sha2561;
  owner_department_id: OwnerDepartmentId2;
  citations: Citations1;
  gaps: Gaps1;
  assertion_status?: AssertionStatus2;
  trusted_as_instructions?: TrustedAsInstructions2;
}
export interface CaseMemoryDTO {
  id: Id19;
  source_investigation_id: SourceInvestigationId;
  outcome_ids: OutcomeIds;
  evidence_ids?: EvidenceIds5;
  gaps?: Gaps2;
  truncated?: Truncated;
  memory_type?: MemoryType;
  summary?: Summary1;
}
export interface AssetDTO {
  location_id: LocationId1;
  condition: Condition;
  owner_department_id: OwnerDepartmentId3;
  id: Id20;
  labels: Labels;
  asset_type: AssetType;
  name: Name1;
  operational_status: OperationalStatus;
  department_ids: DepartmentIds;
  location_ids: LocationIds;
  incident_ids: IncidentIds3;
  graph_revision: GraphRevision2;
  as_of: AsOf1;
  geometry_status: GeometryStatus;
}
export interface GraphNodeDTO {
  id: string;
  labels: string[];
  display_label: string;
  kind: string;
  status: string;
  source_kind: string;
  evidence_ids: string[];
}
export interface GraphEdgeDTO {
  id: string;
  type: string;
  source: string;
  target: string;
  verification_status: string;
  source_evidence_ids: string[];
  valid_from: string | null;
  valid_to: string | null;
}
export interface GraphSubgraphDTO {
  decision_paths?: DecisionPaths;
  nodes: Nodes;
  edges: Edges;
  decision_path_ids: DecisionPathIds;
  graph_revision: GraphRevision3;
  as_of: AsOf2;
  truncated: Truncated1;
  search_limited?: SearchLimited;
  reservations: Reservations;
}
export interface DecisionPath {
  id: Id21;
  node_ids: NodeIds;
  edge_ids: EdgeIds;
  evidence_ids: EvidenceIds6;
  execution_id: ExecutionId;
}
export interface GraphNode {
  id: Id22;
  labels: Labels1;
  kind: Kind1;
  display_label: DisplayLabel;
  status: Status16;
  source_kind: SourceKind5;
  evidence_ids: EvidenceIds7;
  observed_at: ObservedAt3;
}
export interface GraphEdge {
  id: Id23;
  type: Type;
  source: Source;
  target: Target;
  valid_from: ValidFrom;
  valid_to: ValidTo;
  observed_at: ObservedAt4;
  verification_status: VerificationStatus1;
  source_evidence_ids: SourceEvidenceIds;
}
export interface AgentTraceEvent {
  event_id: EventId1;
  investigation_id: InvestigationId4;
  timestamp: Timestamp;
  agent_role: AgentRole;
  kind: Kind2;
  tool_name: ToolName;
  server_id?: ServerId;
  status: Status17;
  rationale_summary: RationaleSummary;
  arguments_sha256?: ArgumentsSha256;
  input_summary?: InputSummary;
  output_sha256?: OutputSha256;
  validated_output?: ValidatedOutput;
  duration_ms?: DurationMs;
  evidence_ids?: EvidenceIds8;
  graph_path_ids?: GraphPathIds;
  graph_revision: GraphRevision4;
  error_code?: ErrorCode;
  execution_mode: ExecutionMode1;
  parent_execution_id?: ParentExecutionId;
  decision_id?: DecisionId;
}
export interface SSEStream {
  event_id: EventId2;
  timestamp: Timestamp1;
  cursor: Cursor;
  id: Id24;
  event_type: EventType;
  entity_id: EntityId;
  investigation_id: InvestigationId5;
  revision: Revision;
  occurred_at: OccurredAt;
  source_kind: SourceKind6;
  simulation_mode: SimulationMode3;
  payload_schema_version: PayloadSchemaVersion;
  payload: PublicPayload;
  source_ref: SourceRef;
}
export interface PublicPayload {
  operation?: Operation;
  execution_id?: ExecutionId1;
  decision_id?: DecisionId1;
  plan_id?: PlanId3;
  plan_version?: PlanVersion1;
  approval_id?: ApprovalId;
  task_id?: TaskId3;
  new_incident_id?: NewIncidentId;
  cluster_id?: ClusterId1;
  prior_outcome_id?: PriorOutcomeId;
  investigates_relationship_id?: InvestigatesRelationshipId;
}
export interface MapFeatureCollection {
  simulation_mode?: SimulationMode4;
  type?: Type1;
  features: Features;
  unavailable_ids: UnavailableIds;
  next_cursor: NextCursor;
  total_count: TotalCount;
  graph_revision: GraphRevision5;
  as_of: AsOf3;
  truncated: Truncated2;
  limitations: Limitations4;
}
export interface MapFeature {
  type?: Type2;
  id: Id25;
  geometry: Point;
  location_id: LocationId2;
  issue_types: IssueTypes;
  asset_ids: AssetIds1;
  incident_ids: IncidentIds4;
  investigation_ids: InvestigationIds;
}
export interface Point {
  type?: Type3;
  coordinates: Coordinates;
}
export interface MonitoringDTO {
  problem_cluster_id: ProblemClusterId1;
  status: Status18;
  verification_policy: VerificationPolicy;
  remaining_checks: RemainingChecks;
  outcome_evidence_ids: OutcomeEvidenceIds;
}
export interface SimulationStepDTO {
  scenario_id: ScenarioId;
  stage: Stage;
  event_id: EventId3;
  revealed_evidence_ids: RevealedEvidenceIds;
  scenario: ScenarioDTO;
  released_evidence_ids?: ReleasedEvidenceIds;
  stage_advanced: StageAdvanced;
  simulated?: Simulated12;
}
export interface ScenarioDTO {
  id: Id26;
  title: Title2;
  issue_types: IssueTypes1;
  stage: Stage1;
  current_stage?: CurrentStage;
  cases?: Cases;
  next_operator_steps: NextOperatorSteps;
  limitations: Limitations5;
}
export interface ScenarioCase {
  issue_type: IssueType2;
  investigation_id: InvestigationId6;
  incident_id: IncidentId2;
  cluster_id: ClusterId2;
  asset_id: AssetId1;
  department_id: DepartmentId8;
  evidence_ids?: EvidenceIds9;
  plan_id?: PlanId4;
  work_order_id?: WorkOrderId1;
}
export interface SeedReport {
  nodes: Nodes1;
  relationships: Relationships;
  source_documents: SourceDocuments;
  seed_fingerprint: SeedFingerprint;
  scenario: ScenarioDTO;
  source_graph: SourceGraph;
  profile_reference: ProfileReference;
  baseline_content_hash: BaselineContentHash;
  previous_source_preserved?: PreviousSourcePreserved;
  simulated?: Simulated13;
}
export interface ComplaintPage {
  items: ComplaintDTO[];
  next_cursor: string | null;
  total_count: number;
}
export interface IncidentPage {
  items: IncidentDTO[];
  next_cursor: string | null;
  total_count: number;
}
export interface ClusterPage {
  items: ProblemClusterDTO[];
  next_cursor: string | null;
  total_count: number;
}
export interface AgentTracePage {
  checkpoint_graph_revision: CheckpointGraphRevision;
  refresh_required: RefreshRequired;
  error_codes: ErrorCodes;
  items: Items;
  next_cursor: NextCursor1;
  total_count: TotalCount1;
  graph_revision: GraphRevision6;
  as_of: AsOf4;
  phase: Phase;
  pause_reason: PauseReason;
  recovery_required: RecoveryRequired;
  current_agent_role: CurrentAgentRole1;
  active_incident_ids: ActiveIncidentIds;
  historical_incident_ids: HistoricalIncidentIds1;
  limitations: Limitations6;
}
export interface HypothesisPage {
  items: Items1;
  next_cursor: NextCursor2;
  total_count: TotalCount2;
  limitations?: Limitations7;
  truncated?: Truncated3;
}
export interface ApprovalPage {
  items: ApprovalDTO[];
  next_cursor: string | null;
  total_count: number;
}
export interface WorkOrderPage {
  items: WorkOrderDTO[];
  next_cursor: string | null;
  total_count: number;
}
export interface DepartmentPage {
  items: DepartmentDTO[];
  next_cursor: string | null;
  total_count: number;
}
export interface ProcedurePage {
  items: ProcedureDTO[];
  next_cursor: string | null;
  total_count: number;
}
export interface CaseMemoryPage {
  items: CaseMemoryDTO[];
  next_cursor: string | null;
  total_count: number;
}
export interface MonitoringPage {
  items: MonitoringDTO[];
  next_cursor: string | null;
  total_count: number;
}
export interface OutcomePage {
  items: OutcomeDTO[];
  next_cursor: string | null;
  total_count: number;
}
export interface ScenarioPage {
  items: Items2;
  next_cursor: NextCursor3;
  total_count: TotalCount3;
  definition_version?: DefinitionVersion;
  simulated?: Simulated14;
}
export interface AuthDemoLogin_Request {
  operator_id: string;
  demo_password: string;
}
export interface AuthLogout_Request {}
export interface Complaints_Request {
  description: string;
  issue_type: string;
  location_id: string;
  reported_at: string;
  source_kind: string;
}
export interface Investigations_Request {
  incident_ids: string[];
  problem_cluster_id: string | null;
}
export interface InvestigationsIdResume_Request {
  reason: string;
  expected_graph_revision: string | null;
}
export interface InspectionsIdObservations_Request {
  asset_id: string;
  observed_at: string;
  observation_type: string;
  value: {
    [k: string]: unknown;
  };
  source_kind: string;
}
export interface PlansIdSubmitApproval_Request {
  plan_id: string;
  plan_version: number;
  plan_hash: string;
}
export interface ApprovalsIdDecision_Request {
  decision: "APPROVED" | "REJECTED";
  plan_id: string;
  plan_version: number;
  plan_hash: string;
  reason: string | null;
}
export interface WorkOrdersIdStatus_Request {
  new_status: string;
  expected_revision: string;
  evidence_ids: string[];
  note: string | null;
}
export interface WorkOrdersIdOutcomes_Request {
  result: string;
  evidence_ids: string[];
  observed_at: string;
}
export interface DemoReset_Request {
  scenario_id: string;
  seed: number;
  confirm: boolean;
}
export interface DemoScenariosIdAdvance_Request {
  stage: string;
  expected_current_stage: string;
}
export interface AssessRequest {
  expected_hash: ExpectedHash12;
  evidence_ids?: EvidenceIds10;
  as_of: AsOf5;
}
export interface Claim {
  kind: Kind3;
  statement: Statement2;
  source_id: SourceId2;
  source_reference: SourceReference;
}
export interface ComplaintRequest {
  complaint: Complaint;
}
export interface WaterIntake {
  description: Description1;
  source_id: SourceId3;
  external_record_id: ExternalRecordId;
  source_channel: SourceChannel;
  source_version?: SourceVersion1;
  source_kind?: SourceKind7;
  reported_at: ReportedAt1;
  occurred_at: OccurredAt1;
  ended_at?: EndedAt1;
  location_id: LocationId3;
  asset_ids?: AssetIds2;
  evidence_ids?: EvidenceIds11;
  event_reference?: EventReference;
  subtype?: Subtype1;
  severity?: Severity;
  issue_type: IssueType3;
  details?: WaterDetails;
}
export interface WaterDetails {
  measurements?: Measurements;
  claims?: Claims;
  rainfall_station_reference?: RainfallStationReference;
  rainfall_from?: RainfallFrom;
  rainfall_to?: RainfallTo;
}
export interface Measurement {
  name: Name2;
  value: Value1;
  unit: Unit1;
  observed_at: ObservedAt5;
  source_id: SourceId4;
  source_reference: SourceReference1;
  basis?: Basis2;
  evidence_id?: EvidenceId1;
}
export interface RoadIntake {
  description: Description2;
  source_id: SourceId5;
  external_record_id: ExternalRecordId1;
  source_channel: SourceChannel1;
  source_version?: SourceVersion2;
  source_kind?: SourceKind8;
  reported_at: ReportedAt2;
  occurred_at: OccurredAt2;
  ended_at?: EndedAt2;
  location_id: LocationId4;
  asset_ids?: AssetIds3;
  evidence_ids?: EvidenceIds12;
  event_reference?: EventReference1;
  subtype?: Subtype2;
  severity?: Severity1;
  issue_type: IssueType4;
  details?: RoadDetails;
}
export interface RoadDetails {
  measurements?: Measurements1;
  claims?: Claims1;
  distress_description?: DistressDescription;
}
export interface WasteIntake {
  description: Description3;
  source_id: SourceId6;
  external_record_id: ExternalRecordId2;
  source_channel: SourceChannel2;
  source_version?: SourceVersion3;
  source_kind?: SourceKind9;
  reported_at: ReportedAt3;
  occurred_at: OccurredAt3;
  ended_at?: EndedAt3;
  location_id: LocationId5;
  asset_ids?: AssetIds4;
  evidence_ids?: EvidenceIds13;
  event_reference?: EventReference2;
  subtype?: Subtype3;
  severity?: Severity2;
  issue_type: IssueType5;
  details?: WasteDetails;
}
export interface WasteDetails {
  measurements?: Measurements2;
  claims?: Claims2;
  quantity_description?: QuantityDescription;
  reported_pickup_status?: ReportedPickupStatus;
  illegal_dumping_claim?: IllegalDumpingClaim;
}
export interface DecideRequest {
  plan_id: PlanId5;
  plan_version: PlanVersion2;
  plan_hash: PlanHash2;
  assignments: Assignments1;
  expected_hash: ExpectedHash13;
  decision: Decision;
  reason: Reason1;
}
export interface DraftRequest {
  draft: PlanDraft;
}
export interface EmptyRequest {}
export interface ErrorBody {
  code: Code1;
  message: Message;
  details?: ErrorDetails;
  retryable?: Retryable;
}
export interface ErrorDetails {
  blocker_code?: BlockerCode;
  correlation_id?: CorrelationId;
  commitment?: Commitment;
  entity_id?: EntityId1;
  investigation_id?: InvestigationId7;
  plan_id?: PlanId6;
  request_id?: RequestId;
}
export interface ErrorEnvelope {
  error: ErrorBody;
  request_id: RequestId1;
}
export interface EvaluateRequest {
  expected_hash: ExpectedHash14;
  evidence_ids?: EvidenceIds14;
  window_start: WindowStart;
  window_end: WindowEnd;
}
export interface InspectionRequest {
  investigation_id: InvestigationId8;
  asset_ids: AssetIds5;
  department_id: DepartmentId9;
  inspection_type: InspectionType;
}
export interface LoginRequest {
  operator_id: OperatorId1;
  demo_password: DemoPassword;
}
export interface OpenRequest {
  incident_ids: IncidentIds5;
  cluster_id: ClusterId3;
  priority?: Priority1;
}
export interface OrderRequest {
  plan_id: PlanId7;
  plan_version: PlanVersion3;
  plan_hash: PlanHash3;
  assignments: Assignments2;
  approval_id: ApprovalId1;
  task_id: TaskId4;
}
export interface PageApprovalDTO {
  items: Items3;
  next_cursor: NextCursor4;
  total_count: TotalCount4;
  limitations?: Limitations8;
  truncated?: Truncated4;
}
export interface PageCaseMemoryDTO {
  items: Items4;
  next_cursor: NextCursor5;
  total_count: TotalCount5;
  limitations?: Limitations9;
  truncated?: Truncated5;
}
export interface PageComplaintDTO {
  items: Items5;
  next_cursor: NextCursor6;
  total_count: TotalCount6;
  limitations?: Limitations10;
  truncated?: Truncated6;
}
export interface PageDepartmentDTO {
  items: Items6;
  next_cursor: NextCursor7;
  total_count: TotalCount7;
  limitations?: Limitations11;
  truncated?: Truncated7;
}
export interface PageIncidentDTO {
  items: Items7;
  next_cursor: NextCursor8;
  total_count: TotalCount8;
  limitations?: Limitations12;
  truncated?: Truncated8;
}
export interface PageMonitoringDTO {
  items: Items8;
  next_cursor: NextCursor9;
  total_count: TotalCount9;
  limitations?: Limitations13;
  truncated?: Truncated9;
}
export interface PageOutcomeDTO {
  items: Items9;
  next_cursor: NextCursor10;
  total_count: TotalCount10;
  limitations?: Limitations14;
  truncated?: Truncated10;
}
export interface PagePlanDTO {
  items: Items10;
  next_cursor: NextCursor11;
  total_count: TotalCount11;
  limitations?: Limitations15;
  truncated?: Truncated11;
}
export interface PageProblemClusterDTO {
  items: Items11;
  next_cursor: NextCursor12;
  total_count: TotalCount12;
  limitations?: Limitations16;
  truncated?: Truncated12;
}
export interface PageProcedureDTO {
  items: Items12;
  next_cursor: NextCursor13;
  total_count: TotalCount13;
  limitations?: Limitations17;
  truncated?: Truncated13;
}
export interface PageWorkOrderDTO {
  items: Items13;
  next_cursor: NextCursor14;
  total_count: TotalCount14;
  limitations?: Limitations18;
  truncated?: Truncated14;
}
export interface ProgressRequest {
  expected_hash: ExpectedHash15;
  action: Action;
  reason: Reason2;
  evidence_ids?: EvidenceIds15;
}
export interface ProposeRequest {
  incident_ids: IncidentIds6;
  asset_ids: AssetIds6;
  cause_code: CauseCode1;
  statement: Statement3;
  mechanism: Mechanism;
  confirming_codes: ConfirmingCodes;
  falsifying_codes: FalsifyingCodes;
  topology?: Topology | null;
}
export interface Topology {
  source_id: SourceId7;
  target_id: TargetId1;
  operation?: Operation1;
  max_hops?: MaxHops;
}
export interface RecurRequest {
  expected_hash: ExpectedHash16;
  evidence_ids?: EvidenceIds16;
  window_start: WindowStart1;
  window_end: WindowEnd1;
  verified_outcome_id: VerifiedOutcomeId;
  complaint: Complaint1;
}
export interface ReportRequest {
  expected_hash: ExpectedHash17;
  source_id: SourceId8;
  record_id: RecordId2;
  source_kind?: SourceKind10;
  observations: Observations;
  attribution?: IncidentAttribution | null;
}
export interface ResumeRequest {
  reason: Reason3;
}
export interface SubmitRequest {
  plan_version: PlanVersion4;
  plan_hash: PlanHash4;
  assignments: Assignments3;
}
export interface SuccessAck {
  data: Ack;
  request_id: RequestId2;
  schema_version?: SchemaVersion;
}
export interface SuccessAgentResumeDTO {
  data: AgentResumeDTO;
  request_id: RequestId3;
  schema_version?: SchemaVersion1;
}
export interface SuccessApprovalDTO {
  data: ApprovalDTO;
  request_id: RequestId4;
  schema_version?: SchemaVersion2;
}
export interface SuccessComplaintDTO {
  data: ComplaintDTO;
  request_id: RequestId5;
  schema_version?: SchemaVersion3;
}
export interface SuccessDemoSession {
  data: DemoSession;
  request_id: RequestId6;
  schema_version?: SchemaVersion4;
}
export interface SuccessDocumentDTO {
  data: DocumentDTO;
  request_id: RequestId7;
  schema_version?: SchemaVersion5;
}
export interface SuccessEvidenceDTO {
  data: EvidenceDTO;
  request_id: RequestId8;
  schema_version?: SchemaVersion6;
}
export interface SuccessHealthDTO {
  data: HealthDTO;
  request_id: RequestId9;
  schema_version?: SchemaVersion7;
}
export interface SuccessIncidentDTO {
  data: IncidentDTO;
  request_id: RequestId10;
  schema_version?: SchemaVersion8;
}
export interface SuccessInspectionDTO {
  data: InspectionDTO;
  request_id: RequestId11;
  schema_version?: SchemaVersion9;
}
export interface SuccessInvestigationDTO {
  data: InvestigationDTO;
  request_id: RequestId12;
  schema_version?: SchemaVersion10;
}
export interface SuccessOperatorAccount {
  data: OperatorAccount;
  request_id: RequestId13;
  schema_version?: SchemaVersion11;
}
export interface SuccessOutcomeDTO {
  data: OutcomeDTO;
  request_id: RequestId14;
  schema_version?: SchemaVersion12;
}
export interface SuccessPageApprovalDTO {
  data: PageApprovalDTO;
  request_id: RequestId15;
  schema_version?: SchemaVersion13;
}
export interface SuccessPageCaseMemoryDTO {
  data: PageCaseMemoryDTO;
  request_id: RequestId16;
  schema_version?: SchemaVersion14;
}
export interface SuccessPageComplaintDTO {
  data: PageComplaintDTO;
  request_id: RequestId17;
  schema_version?: SchemaVersion15;
}
export interface SuccessPageDepartmentDTO {
  data: PageDepartmentDTO;
  request_id: RequestId18;
  schema_version?: SchemaVersion16;
}
export interface SuccessPageIncidentDTO {
  data: PageIncidentDTO;
  request_id: RequestId19;
  schema_version?: SchemaVersion17;
}
export interface SuccessPageMonitoringDTO {
  data: PageMonitoringDTO;
  request_id: RequestId20;
  schema_version?: SchemaVersion18;
}
export interface SuccessPageOutcomeDTO {
  data: PageOutcomeDTO;
  request_id: RequestId21;
  schema_version?: SchemaVersion19;
}
export interface SuccessPagePlanDTO {
  data: PagePlanDTO;
  request_id: RequestId22;
  schema_version?: SchemaVersion20;
}
export interface SuccessPageProblemClusterDTO {
  data: PageProblemClusterDTO;
  request_id: RequestId23;
  schema_version?: SchemaVersion21;
}
export interface SuccessPageProcedureDTO {
  data: PageProcedureDTO;
  request_id: RequestId24;
  schema_version?: SchemaVersion22;
}
export interface SuccessPageWorkOrderDTO {
  data: PageWorkOrderDTO;
  request_id: RequestId25;
  schema_version?: SchemaVersion23;
}
export interface SuccessPlanDTO {
  data: PlanDTO;
  request_id: RequestId26;
  schema_version?: SchemaVersion24;
}
export interface SuccessProblemClusterDTO {
  data: ProblemClusterDTO;
  request_id: RequestId27;
  schema_version?: SchemaVersion25;
}
export interface SuccessWorkOrderDTO {
  data: WorkOrderDTO;
  request_id: RequestId28;
  schema_version?: SchemaVersion26;
}
export interface TransitionRequest {
  expected_hash: ExpectedHash18;
  status: Status19;
  scheduled_at?: ScheduledAt2;
}
export interface UpdateRequest {
  expected_hash: ExpectedHash19;
  new_status: NewStatus;
  reason: Reason4;
}
export interface WorkAssessment {
  operation?: Operation2;
  hypothesis_id: HypothesisId1;
  expected_hash: ExpectedHash20;
  evidence_ids?: EvidenceIds17;
  as_of: AsOf6;
}
export interface WorkInspectionCreate {
  operation?: Operation3;
  investigation_id: InvestigationId9;
  asset_ids: AssetIds7;
  department_id: DepartmentId10;
  inspection_type: InspectionType1;
}
export interface WorkInspectionReport {
  operation?: Operation4;
  inspection_id: InspectionId1;
  expected_hash: ExpectedHash21;
  source_id: SourceId9;
  record_id: RecordId3;
  source_kind?: SourceKind11;
  observations: Observations1;
  attribution?: IncidentAttribution | null;
}
export interface WorkInspectionRequest {
  expected_hash: ExpectedHash22;
  purpose: Purpose;
  command: Command;
  review_reason?: ReviewReason;
}
export interface WorkInspectionTransition {
  operation?: Operation5;
  inspection_id: InspectionId2;
  expected_hash: ExpectedHash23;
  status: Status20;
  scheduled_at?: ScheduledAt3;
}
export interface PageComplaintDTO1 {
  items: Items14;
  next_cursor: NextCursor15;
  total_count: TotalCount15;
  limitations?: Limitations19;
  truncated?: Truncated15;
}
export interface PageIncidentDTO1 {
  items: Items15;
  next_cursor: NextCursor16;
  total_count: TotalCount16;
  limitations?: Limitations20;
  truncated?: Truncated16;
}
export interface PageProblemClusterDTO1 {
  items: Items16;
  next_cursor: NextCursor17;
  total_count: TotalCount17;
  limitations?: Limitations21;
  truncated?: Truncated17;
}
export interface PageApprovalDTO1 {
  items: Items17;
  next_cursor: NextCursor18;
  total_count: TotalCount18;
  limitations?: Limitations22;
  truncated?: Truncated18;
}
export interface PageWorkOrderDTO1 {
  items: Items18;
  next_cursor: NextCursor19;
  total_count: TotalCount19;
  limitations?: Limitations23;
  truncated?: Truncated19;
}
export interface PageDepartmentDTO1 {
  items: Items19;
  next_cursor: NextCursor20;
  total_count: TotalCount20;
  limitations?: Limitations24;
  truncated?: Truncated20;
}
export interface PagePlanDTO1 {
  items: Items20;
  next_cursor: NextCursor21;
  total_count: TotalCount21;
  limitations?: Limitations25;
  truncated?: Truncated21;
}
export interface PageProcedureDTO1 {
  items: Items21;
  next_cursor: NextCursor22;
  total_count: TotalCount22;
  limitations?: Limitations26;
  truncated?: Truncated22;
}
export interface PageCaseMemoryDTO1 {
  items: Items22;
  next_cursor: NextCursor23;
  total_count: TotalCount23;
  limitations?: Limitations27;
  truncated?: Truncated23;
}
export interface PageMonitoringDTO1 {
  items: Items23;
  next_cursor: NextCursor24;
  total_count: TotalCount24;
  limitations?: Limitations28;
  truncated?: Truncated24;
}
export interface PageOutcomeDTO1 {
  items: Items24;
  next_cursor: NextCursor25;
  total_count: TotalCount25;
  limitations?: Limitations29;
  truncated?: Truncated25;
}
export interface SuccessHypothesisDTO {
  data: HypothesisDTO;
  request_id: RequestId29;
  schema_version?: SchemaVersion27;
}
export interface SuccessAgentTracePage {
  data: AgentTracePage;
  request_id: RequestId30;
  schema_version?: SchemaVersion28;
}
export interface SuccessAssetDTO {
  data: AssetDTO;
  request_id: RequestId31;
  schema_version?: SchemaVersion29;
}
export interface SuccessDashboardSummary {
  data: DashboardSummary;
  request_id: RequestId32;
  schema_version?: SchemaVersion30;
}
export interface SuccessGraphSubgraphDTO {
  data: GraphSubgraphDTO;
  request_id: RequestId33;
  schema_version?: SchemaVersion31;
}
export interface SuccessHypothesisPage {
  data: HypothesisPage;
  request_id: RequestId34;
  schema_version?: SchemaVersion32;
}
export interface SuccessMapFeatureCollection {
  data: MapFeatureCollection;
  request_id: RequestId35;
  schema_version?: SchemaVersion33;
}
export interface ResourceQuery {
  limit?: Limit;
  cursor?: Cursor1;
  issue?: Issue2;
  status?: Status21;
  department_id?: DepartmentId11;
  after?: After;
  before?: Before;
}
export interface GraphQuery {
  depth?: Depth;
  include_candidates?: IncludeCandidates;
}
export interface HypothesesQuery {
  limit?: Limit1;
  cursor?: Cursor2;
  status?: Status22;
}
export interface DashboardQuery {
  issue?: Issue3;
  status?: Status23;
  department_id?: DepartmentId12;
  after?: After1;
  before?: Before1;
}
export interface AssetQuery {}
export interface TraceQuery {
  limit?: Limit2;
  cursor?: Cursor3;
  status?: Status24;
  after?: After2;
  before?: Before2;
}
export interface MapQuery {
  limit?: Limit3;
  cursor?: Cursor4;
  issue?: Issue4;
  status?: Status25;
  department_id?: DepartmentId13;
  after?: After3;
  before?: Before3;
  investigation_id?: InvestigationId10;
}
export interface ScenarioSummary {
  id: Id27;
  title: Title3;
  issue_types: IssueTypes2;
  current_stage?: CurrentStage1;
  cases?: Cases1;
  next_operator_steps: NextOperatorSteps1;
  limitations: Limitations30;
}
export interface DemoResetRequest {
  scenario_id: ScenarioId1;
  seed: Seed;
  confirm: Confirm;
  variant?: Variant;
}
export interface DemoAdvanceRequest {
  expected_current_stage: ExpectedCurrentStage;
  stage: Stage2;
  investigation_id?: InvestigationId11;
  inspection_id?: InspectionId3;
  expected_hash?: ExpectedHash24;
  plan_id?: PlanId8;
  work_order_id?: WorkOrderId2;
}
export interface ResponsibilitySubmission {
  asset_id: AssetId2;
  department_id: DepartmentId14;
  source_id: SourceId10;
  source_record_id: SourceRecordId1;
  source_version?: SourceVersion4;
  source_kind?: SourceKind12;
  observed_at: ObservedAt6;
  valid_from: ValidFrom1;
  valid_to?: ValidTo1;
}
export interface ResponsibilityReview {
  expected_hash: ExpectedHash25;
  reviewed: Reviewed2;
  reason: Reason5;
}
export interface ResponsibilityDTO {
  id: Id28;
  asset_id: AssetId3;
  department_id: DepartmentId15;
  source_id: SourceId11;
  source_record_id: SourceRecordId2;
  source_version: SourceVersion5;
  source_kind?: SourceKind13;
  observed_at: ObservedAt7;
  valid_from: ValidFrom2;
  valid_to: ValidTo2;
  submitted_by: SubmittedBy;
  reviewed_by: ReviewedBy1;
  status: Status26;
  applicability: Applicability;
  expected_hash: ExpectedHash26;
  source_evidence_id: SourceEvidenceId;
  review_evidence_id: ReviewEvidenceId;
  relationship_id: RelationshipId;
  event_id: EventId4;
  as_of: AsOf7;
  simulation_mode?: SimulationMode5;
}
export interface PageInvestigationDTO {
  items: Items25;
  next_cursor: NextCursor26;
  total_count: TotalCount26;
  limitations?: Limitations31;
  truncated?: Truncated26;
}
