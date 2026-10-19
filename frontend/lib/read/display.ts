/**
 * Civicly Frontend Readability & Display Mapping Module
 *
 * Implements human-readable translations for machine identifiers, statuses,
 * cause codes, actions, departments, and entity names while strictly preserving
 * the underlying API contracts and exact canonical identifiers in technical details.
 */

// --- Status Translations ---
export const STATUS_TRANSLATIONS: Record<string, string> = {
  // Plan & Approval Statuses
  PENDING_APPROVAL: 'Awaiting approval',
  PENDING: 'Pending',
  APPROVED: 'Approved',
  REJECTED: 'Rejected',
  DRAFT: 'Draft proposed',
  PROPOSED: 'Proposed',
  HUMAN_REVIEW: 'Awaiting human review',
  SUPERSEDED: 'Superseded by newer plan',
  CANCELLED: 'Cancelled',

  // Investigation & Incident Statuses
  ACTIVE: 'Active investigation',
  OPEN: 'Open',
  IN_PROGRESS: 'In progress',
  COMPLETED: 'Completed',
  VERIFIED: 'Verified',
  CLOSED: 'Case closed',
  ENDED: 'Incident ended',
  NOT_STARTED: 'Not started',
  BLOCKED: 'Blocked by prerequisite',
  FAILED: 'Failed',

  AUTHORIZED: 'Work authorized',
  ASSIGNED: 'Assigned to a department lead',
  REQUESTED: 'Inspection requested',
  SCHEDULED: 'Inspection scheduled',
  REPORTED: 'Reported',
  POSSIBLE: 'Possible explanation',
  UNVERIFIED: 'Not verified',
  CORROBORATED: 'Corroborated by sources',
  TOKEN_BUDGET: 'Agent usage limit reached',
  MISSING_EVIDENCE: 'Waiting for evidence',
  DEPENDENCY_UNAVAILABLE: 'Required service unavailable',
  RECOVERY_REQUIRED: 'Operator review required',
  RESOLUTION_VERIFIED: 'Resolution verified by follow-up',
  UTILITY_VERIFIED: 'Utility repair verified; case outcome is separate',
  PROBLEM_PERSISTS: 'Problem persists after work',
  INTERVENTION_FAILED: 'Intervention did not succeed',
  ACTION_COMPLETED: 'Task completion recorded',
  MITIGATION_VERIFIED: 'Mitigation verified by follow-up',
  SUCCESS: 'Tool read completed',
  READ: 'Read supporting records',
  PROPOSE: 'Propose a possible cause',
  ASSESS: 'Assess the evidence',
  INSPECT: 'Request an inspection',
  RECOMMEND: 'Recommend an action plan',
  PAUSE: 'Pause for review',
  BASELINE_VISIBLE: 'Initial reports available',
  EVIDENCE_REVEALED: 'Inspection evidence available',
  SYNTHETIC: 'Synthetic demo data',
  AGENT: 'Agent-generated record',

  LEAK_DETECTED: 'Leak observed',
  INFILTRATION_AT_DAMAGE: 'Water infiltration observed at the damaged area',
  UTILITY_SAFETY_REVIEWED: 'Utility safety review recorded',
  SUBGRADE_REPAIR_SAFETY_REVIEWED: 'Road repair safety review recorded',
  DRAIN_CLEARANCE_SAFETY_REVIEWED: 'Drain clearance safety review recorded',
  PICKUP_RECOVERY_SAFETY_REVIEWED: 'Waste pickup safety review recorded',
  OBSTRUCTION_OBSERVED: 'Obstruction observed',
  WEAR_EXPOSURE: 'Follow-up wear exposure recorded',
  FOLLOWUP_PAVEMENT: 'Pavement damage present at follow-up',
  FOLLOWUP_WATERLOGGING: 'Waterlogging present at follow-up',
  POST_REPAIR_PRESSURE_NORMAL: 'Post-repair pressure test normal',
  POST_REPAIR_LEAK_ABSENT: 'No leak observed in the post-repair test',
  SYNTHETIC_PRESENTER_FIELD_SURVEY: 'Synthetic field survey',
  DIRECT_SYNTHETIC_FIELD_TEST: 'Direct synthetic field test',
  OBSERVED: 'Observed',
  CAUSAL_INSPECTION: 'Inspection evidence for this explanation',
  SAFETY_REVIEW: 'Safety review',
  ISOLATION_PROOF: 'Proof that the pipe was isolated',
  UTILITY_VERIFICATION: 'Independent verification of the utility repair',
  MET: 'Evidence supplied',
  UNMET: 'Still required',

  // Technical Observation & Test Statuses
  STRUCTURAL_TEST_FAILED: 'Structural test failed',
  SUBGRADE_FAILURE_OBSERVED: 'Failure observed in the ground beneath the road',
  PRESSURE_TEST_NORMAL: 'Pressure test was normal',
  FLOW_RESTRICTED: 'Flow restricted',

  // Hypothesis Assessments (strictly separated from plan coverage)
  SUPPORTED: 'Evidence supports this explanation',
  CONTRADICTED: 'Evidence challenges this explanation',
  INCONCLUSIVE: 'Inconclusive (pending evidence)',

  // Monitoring Statuses
  MONITORING: 'Under post-intervention monitoring',
  CONTROLLED: 'Problem controlled',
  REOPENED: 'Reopened',

  // Verification & Edge Statuses
  CANDIDATE: 'Candidate (unverified)',
  REVISION_PENDING: 'Revision pending',
};

export function translateStatus(status?: string | null): string {
  if (!status) return 'Not recorded';
  const upper = status.trim().toUpperCase();
  if (STATUS_TRANSLATIONS[upper]) {
    return STATUS_TRANSLATIONS[upper];
  }
  // Clean fallback: capitalize words instead of raw underscore
  return upper
    .split('_')
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(' ');
}

// --- Cause Codes & Technical Observations ---
export interface CauseCodeTranslation {
  title: string;
  explanation: string;
}

export const CAUSE_CODE_TRANSLATIONS: Record<string, CauseCodeTranslation> = {
  BLOCKAGE: {title:'Drain blockage',explanation:'Check whether an obstruction is restricting flow through connected drainage assets.'},
  CAPACITY_DEFICIT: {title:'Insufficient drainage capacity',explanation:'Check whether drainage capacity is insufficient for the observed conditions; a clear drain alone does not establish this cause.'},
  UTILITY_LEAK: {title:'Water pipe leak',explanation:'Check whether a leak and an attributed physical connection support an explanation for the road damage.'},
  SUBGRADE_FAILURE: {title:'Ground beneath the road has failed',explanation:'Subgrade is the supporting ground beneath the pavement; inspect its condition before selecting repair work.'},
  STRUCTURAL_TEST_FAILED: {
    title: 'Structural test failed',
    explanation: 'Core load-bearing capacity test failed under mechanical measurement.',
  },
  SUBGRADE_FAILURE_OBSERVED: {
    title: 'Failure observed in the ground beneath the road',
    explanation: 'Subgrade refers to the foundational soil and aggregate layers directly supporting the road pavement.',
  },
  PRESSURE_TEST_NORMAL: {
    title: 'Pressure test was normal',
    explanation: 'Utility water pressure met standard operating range at time of testing.',
  },
  'HYP-SUBGRADE': {
    title: 'Subgrade Failure',
    explanation: 'Subgrade refers to the ground and foundational soil layers directly supporting the road pavement.',
  },
  'HYP-DRAIN-CLOG': {
    title: 'Drainage Inflow Blockage',
    explanation: 'Accumulation of sediment, silt, and urban debris obstructing inlet grates.',
  },
  'HYP-WATER-MAIN-LEAK': {
    title: 'Pressurized Water Main Leak',
    explanation: 'Subsurface leak from pressurized water utility pipe undermining road foundation.',
  },
  DRAIN_BLOCKED: {
    title: 'Drainage inlet obstructed',
    explanation: 'Stormwater inlet is physically obstructed by accumulated debris and silt.',
  },
  INLET_OBSTRUCTION: {
    title: 'Stormwater inlet obstructed',
    explanation: 'Flow restriction caused by solid waste or sediment build-up at drainage grate.',
  },
  PIPE_BURST: {
    title: 'Underground water pipe damaged',
    explanation: 'Pressurized water supply line breach leaking into adjacent subgrade layers.',
  },
  OVERFLOW_OBSERVED: {
    title: 'Surface stormwater overflow observed',
    explanation: 'Runoff volume exceeded local drainage capture capacity.',
  },
  DEBRIS_ACCUMULATION: {
    title: 'Debris and solid waste accumulated',
    explanation: 'Uncollected solid waste piles encroaching on civic drainage and roadway assets.',
  },
  ILLEGAL_DUMPING: {
    title: 'Possible unauthorized dumping',
    explanation: 'Check whether dated evidence shows waste deposited outside the authorized collection process.',
  },
  MISSED_COLLECTION: {
    title: 'Scheduled pickup collection missed',
    explanation: 'Municipal sanitation route did not complete scheduled service at designated point.',
  },
  PAVEMENT_DEFECT: {
    title: 'Pavement surface degraded',
    explanation: 'Asphalt surface cracking, potholes, or localized subsidence.',
  },
  UTILITY_EXCAVATION: {
    title: 'Utility excavation required',
    explanation: 'Sub-surface utility inspection or trenching necessary to verify underground integrity.',
  },
  CAPACITY_EXCEEDED: {
    title: 'Drainage flow capacity exceeded',
    explanation: 'Hydraulic conduit cross-section insufficient for peak runoff flow volume.',
  },
  RUNOFF_SURGE: {
    title: 'Extreme stormwater runoff surge',
    explanation: 'Short-duration high-intensity rainfall resulting in localized stormwater pooling.',
  },
  SUBSIDENCE: {
    title: 'Road bed subsidence',
    explanation: 'Settlement or depression in road surface resulting from soil erosion or compaction loss.',
  },
  EROSION_DETECTED: {
    title: 'Soil erosion detected',
    explanation: 'Sub-surface soil wash-out creating voids underneath structural pavement layers.',
  },
  CAPACITY_SHORTFALL: {
    title: 'Solid Waste Container Capacity Shortfall',
    explanation: 'Commercial waste generation rate exceeds designated container volume capacity between collection cycles.',
  },
  MISSED_PICKUP: {
    title: 'Missed Municipal Collection Cycle',
    explanation: 'Designated sanitation vehicle did not execute scheduled waste collection at service point.',
  },
  BIN_CAPACITY_EXCEEDED: {
    title: 'Collection Point Bin Capacity Exceeded',
    explanation: 'Observed solid waste overflow resulting from insufficient container volume.',
  },
  EXPECTED_PICKUPS_COMPLETED: {
    title: 'Scheduled Collection Pickups Completed',
    explanation: 'Municipal sanitation records confirm collection crew completed designated route on schedule.',
  },
  UNAUTHORIZED_DUMPING: {
    title: 'Unauthorized Commercial Waste Dumping',
    explanation: 'Unregistered commercial waste deposited outside authorized municipal collection points.',
  },
  DRAIN_CAPACITY_EXCEEDED: {
    title: 'Drainage Flow Capacity Exceeded',
    explanation: 'Rainfall volume exceeded maximum hydraulic discharge rate of stormwater conduit.',
  },
};

export function translateCauseCode(code?: string | null): CauseCodeTranslation {
  if (!code) {
    return {
      title: 'Possible cause',
      explanation: 'Unspecified diagnostic finding.',
    };
  }
  const upper = code.trim().toUpperCase();
  if (CAUSE_CODE_TRANSLATIONS[upper]) {
    return CAUSE_CODE_TRANSLATIONS[upper];
  }
  // Check if code contains subgrade
  if (upper.includes('SUBGRADE')) {
    return CAUSE_CODE_TRANSLATIONS['HYP-SUBGRADE'];
  }
  if (upper.includes('DRAIN') && (upper.includes('CLOG') || upper.includes('BLOCK'))) {
    return CAUSE_CODE_TRANSLATIONS['HYP-DRAIN-CLOG'];
  }
  if (upper.includes('WATER') && upper.includes('LEAK')) {
    return CAUSE_CODE_TRANSLATIONS['HYP-WATER-MAIN-LEAK'];
  }
  if (upper.includes('CAPACITY') && upper.includes('SHORT')) {
    return CAUSE_CODE_TRANSLATIONS['CAPACITY_SHORTFALL'];
  }
  if (upper.includes('MISSED') && (upper.includes('PICKUP') || upper.includes('COLLECT'))) {
    return CAUSE_CODE_TRANSLATIONS['MISSED_PICKUP'];
  }

  // Clean fallback: format as readable Title Case instead of raw code
  const cleanedTitle = code
    .replace(/^(HYP|CAUSE)-/i, '')
    .split(/[-_]/)
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ');

  return {
    title: cleanedTitle || 'Possible cause',
    explanation: 'Hypothesis recorded during diagnostic reasoning.',
  };
}

// --- Evidence Assessment vs Plan Coverage ---
export interface AssessmentInfo {
  label: string;
  badgeClass: string;
  tone: 'supported' | 'contradicted' | 'inconclusive' | 'default';
  description: string;
  isSupported: boolean;
  isContradicted: boolean;
  isInconclusive: boolean;
}

export function translateAssessment(status?: string | null): AssessmentInfo {
  const upper = (status || '').trim().toUpperCase();
  switch (upper) {
    case 'SUPPORTED':
      return {
        label: 'Supported',
        badgeClass: 'badge-verified',
        tone: 'supported',
        description: 'The recorded evidence supports this explanation. Remaining gaps may still require verification.',
        isSupported: true,
        isContradicted: false,
        isInconclusive: false,
      };
    case 'CONTRADICTED':
      return {
        label: 'Contradicted',
        badgeClass: 'badge-danger',
        tone: 'contradicted',
        description: 'The recorded evidence challenges this explanation. Review the sources and assessment history.',
        isSupported: false,
        isContradicted: true,
        isInconclusive: false,
      };
    case 'VERIFIED':
      return {label:'Verified explanation',badgeClass:'badge-verified',tone:'supported',description:'The assessment meets the declared cause-verification policy; this does not by itself verify the outcome of work.',isSupported:true,isContradicted:false,isInconclusive:false};
    case 'INCONCLUSIVE':
      return {
        label: 'Inconclusive',
        badgeClass: 'badge-warning',
        tone: 'inconclusive',
        description: 'Evidence is insufficient or conflicting; requires targeted field verification.',
        isSupported: false,
        isContradicted: false,
        isInconclusive: true,
      };
    default:
      return {
        label: upper === 'UNASSESSED' ? 'Awaiting evaluation' : translateStatus(status),
        badgeClass: 'badge-default',
        tone: 'default',
        description: 'Assessment pending further evidence.',
        isSupported: false,
        isContradicted: false,
        isInconclusive: false,
      };
  }
}

// --- Action Types Translations ---
export const ACTION_TYPE_TRANSLATIONS: Record<string, string> = {
  INSPECTION: 'Inspect the affected asset',
  DRAIN_BLOCKAGE_CLEARANCE: 'Clear the drain blockage',
  SUBGRADE_REPAIR: 'Repair the ground beneath the road',
  MISSED_PICKUP_RECOVERY: 'Complete the missed waste pickup',
  UTILITY_ISOLATION: 'Safely isolate the water pipe',
  UTILITY_LEAK_REPAIR: 'Repair the water pipe leak',
  EXCAVATE_TRENCH: 'Trench excavation',
  CLEAR_CULVERT: 'Culvert clearance',
  PATCH_ASPHALT: 'Asphalt pavement patching',
  INSPECT_MANHOLE: 'Manhole inspection',
  ISOLATE_UTILITY_SEGMENT: 'Isolate underground water pipe',
  REPAIR_UTILITY_LEAK: 'Repair pipe leak and verify seal',
  STABILIZE_ROAD_SUBGRADE: 'Stabilize road subgrade (ground beneath pavement)',
  SURFACE_PAVING_REPAIR: 'Restore asphalt pavement surface',
  CLEAR_INLET_OBSTRUCTION: 'Clear debris obstruction from drain inlet',
  DESILT_DRAINAGE_CHANNEL: 'Desilt downstream drainage channel',
  RECOVERY_WASTE_COLLECTION: 'Conduct recovery waste collection',
  INSPECT_FIELD_CONDITIONS: 'Conduct on-site physical inspection',
  DEPOSIT_SURVEILLANCE: 'Install waste disposal deterrent signage',
  CAPACITY_SURVEY: 'Perform flow capacity and rainfall survey',
  UTILITY_PRESSURE_TEST: 'Perform utility pressure test',
  ROAD_STRUCTURAL_TEST: 'Perform pavement structural test',
  CLEAR_ACCUMULATED_WASTE: 'Clear accumulated waste pile',
};

export function translateActionType(action?: string | null): string {
  if (!action) return 'Remediation task';
  const upper = action.trim().toUpperCase();
  if (ACTION_TYPE_TRANSLATIONS[upper]) {
    return ACTION_TYPE_TRANSLATIONS[upper];
  }
  return upper
    .split('_')
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(' ');
}

// --- Municipal Departments ---
export const DEPARTMENT_TRANSLATIONS: Record<string, string> = {
  'DEPT-ROADS': 'Roads & Infrastructure Maintenance',
  'DEPT-WATER': 'Water Utilities',
  'DEPT-ENVIRONMENT': 'Environmental & Waste Management',
  'DEPT-PUBLIC-WORKS': 'Public Works Department',
  'DEPT-DRAIN': 'Drainage & Stormwater Department',
  'DEPT-ROAD': 'Roads & Infrastructure Department',
  'DEPT-SAN': 'Sanitation & Waste Management',
  UNKNOWN: 'Unassigned Department',
};

export function translateDepartment(deptId?: string | null): string {
  if (!deptId) return 'Municipal Department';
  const upper = deptId.trim().toUpperCase();
  if (DEPARTMENT_TRANSLATIONS[upper]) {
    return DEPARTMENT_TRANSLATIONS[upper];
  }
  return deptId;
}

// --- Municipal Roles ---
export const ROLE_TRANSLATIONS: Record<string, string> = {
  OPERATOR_ANALYST: 'Investigation Analyst',
  OPERATOR_APPROVER: 'Supervising Approval Officer',
  OPERATOR_FIELD_LEAD: 'Field Operations Lead',
  OPERATOR_AUDITOR: 'Compliance Auditor',
  'OP-ANALYST': 'Investigation Analyst',
  'OP-APPROVER': 'Supervising Approval Officer',
  'OP-DRAIN-LEAD': 'Drainage Operations Lead',
  'OP-ROAD-LEAD': 'Roads Operations Lead',
  'OP-WASTE-LEAD': 'Waste Operations Lead',
  'OP-WATER-LEAD': 'Water Utility Lead',
  'OP-ADMIN': 'City Operations Administrator',
  Supervisor: 'Investigation supervisor',
  SUPERVISOR: 'Investigation supervisor',
  INVESTIGATOR: 'Evidence investigator',
  ROOTCAUSEANALYST: 'Cause assessment',
  RESOLUTIONPLANNER: 'Action planner',
  COORDINATOR: 'Workflow coordinator',
  DEPARTMENT_LEAD: 'Department lead',
  ANALYST: 'Investigation Analyst',
  APPROVER: 'Approval Officer',
  OPERATOR: 'Field Operations Lead',
  ADMIN: 'System Administrator',
};

export function translateRole(role?: string | null): string {
  if (!role) return 'Municipal Operator';
  const upper = role.trim().toUpperCase();
  return ROLE_TRANSLATIONS[upper] || translateStatus(role);
}

// --- Scenario Titles grounded in official catalog ---
export const SCENARIO_TITLES: Record<string, string> = {
  S01: 'Downstream drain, repeated flooding',
  S02: 'High rainfall, no blockage',
  S03: 'Potholes near healthy water main',
  S04: 'Confirmed underground utility leak',
  S05: 'Market waste demand plus missed pickup',
  S06: 'Unauthorized dumping despite reliable service',
  S07: 'Cross-category cascade',
  S08: 'Nearby but disconnected drains',
  S09: 'Work order is not resolution',
  S10: 'Inspection disproves favorite hypothesis',
  S11: 'Failure recurrence and cross-case memory',
  S12: 'MCP/weather down and spoofed tool instruction',
};

// --- Location Translations ---
export const LOCATION_TRANSLATIONS: Record<string, string> = {
  'LOC-JUNCTION': 'Market Junction',
  'LOC-MARKET': 'Central Market',
  'LOC-OUTFALL': 'Downstream Outfall',
  'LOC-ROAD': 'Market Approach Road',
  'LOC-WASTE-DEMO-DUMPING': 'Commercial Waste Disposal Zone',
  'LOC-WASTE-DEMO-SERVICE-02': 'Commercial Sanitation Sector 02',
  'LOC-WASTE-DEMO-SERVICE-01': 'Commercial Sanitation Sector 01',
  'LOC-ROAD-DEMO-01': 'Market Access Roadway Sector 01',
  'LOC-DRAIN-DEMO-01': 'Stormwater Inflow Junction 01',
};

export function translateLocation(locId?: string | null): string {
  if (!locId) return 'Civic location not specified';
  const upper = locId.trim().toUpperCase();
  if (LOCATION_TRANSLATIONS[upper]) {
    return LOCATION_TRANSLATIONS[upper];
  }
  if (upper.startsWith('LOC-WASTE-DEMO-SERVICE-')) {
    const num = upper.split('-').pop();
    return `Commercial Sanitation Sector ${num}`;
  }
  if (upper.startsWith('LOC-ROAD-DEMO-')) {
    const num = upper.split('-').pop();
    return `Market Access Roadway Sector ${num}`;
  }
  if (upper.startsWith('LOC-DRAIN-DEMO-')) {
    const num = upper.split('-').pop();
    return `Stormwater Inflow Junction ${num}`;
  }
  if (/^LOC-0*\d+$/.test(upper)) {
    const num = upper.replace('LOC-', '').replace(/^0+/, '');
    return `Civic District Site ${num.padStart(2, '0')}`;
  }
  return upper
    .replace(/^LOC-/, '')
    .split(/[-_]/)
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ');
}

// --- Infrastructure Asset Translations ---
export const ASSET_TRANSLATIONS: Record<string, string> = {
  'WASTE-100': 'Central Market Waste Collection Point',
  'WASTE-W03': 'Market Waste Collection Point W-03',
  'WASTE-DEMO-SERVICE-02': 'Commercial Waste Collection Point #02',
  'WASTE-DEMO-SERVICE-01': 'Commercial Waste Collection Point #01',
  'DRAIN-100': 'Stormwater Inlet Grate #100',
  'DRAIN-101': 'Downstream Stormwater Collector #101',
  'DRAIN-D12': 'Stormwater Conduit #D12',
  'DRAIN-D18': 'Downstream Drainage Conduit #D18',
  'ROAD-100': 'Market Approach Roadway Segment #100',
  'ROAD-SEG-402': 'Primary Road Segment #402',
  'PIPE-100': 'Pressurized Water Supply Main #100',
  'PIPE-701': 'Underground Water Pipe Segment #701',
};

export function translateAsset(assetId?: string | null): string {
  if (!assetId) return 'Infrastructure asset';
  const upper = assetId.trim().toUpperCase();
  if (ASSET_TRANSLATIONS[upper]) {
    return ASSET_TRANSLATIONS[upper];
  }
  if (upper.startsWith('WASTE-DEMO-SERVICE-')) {
    const num = upper.split('-').pop();
    return `Commercial Waste Collection Point #${num}`;
  }
  if (upper.startsWith('WASTE-')) {
    const num = upper.replace('WASTE-', '');
    return `Waste Collection Point #${num}`;
  }
  if (upper.startsWith('DRAIN-') || upper.startsWith('DRN-')) {
    const num = upper.replace(/^(DRAIN|DRN)-/, '');
    return `Drainage asset #${num}`;
  }
  if (upper.startsWith('PIPE-') || upper.startsWith('WAT-')) {
    const num = upper.replace(/^(PIPE|WAT)-/, '');
    return `Underground Water Pipe #${num}`;
  }
  if (upper.startsWith('ROAD-') || upper.startsWith('RDS-')) {
    const num = upper.replace(/^(ROAD|RDS)-/, '');
    return `Road Segment #${num}`;
  }
  if (upper.startsWith('ASSET-')) {
    const sub = upper.replace('ASSET-', '');
    return translateAsset(sub);
  }
  return upper
    .split(/[-_]/)
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ');
}

// --- MCP Tool Action Translations ---
export const TOOL_ACTION_TRANSLATIONS: Record<string, string> = {
  'civicly::get_pickup_execution_history': 'Query sanitation pickup execution history',
  'civicly::get_maintenance_history': 'Query municipal maintenance work history',
  'civicly::retrieve_external_evidence': 'Retrieve meteorological & sensor observations',
  'civicly::trace_infrastructure_dependencies': 'Trace connected infrastructure topology',
  'civicly::find_related_incidents': 'Find correlated recurrence incidents',
  'civicly::complaint_merge': 'Correlate citizen complaints into incident cluster',
  'civicly::submit_inspection_request': 'Request field engineering inspection',
  'official::query_graph_readonly': 'Execute readonly FalkorDB graph traversal',
  'official::list_nodes': 'Query FalkorDB knowledge graph nodes',
};

export function translateToolAction(toolName?: string | null): string {
  if (!toolName) return 'Agent reasoning action';
  const trimmed = toolName.trim();
  if (TOOL_ACTION_TRANSLATIONS[trimmed]) {
    return TOOL_ACTION_TRANSLATIONS[trimmed];
  }
  const clean = trimmed.replace(/^(civicly|official)::/, '');
  return clean
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ');
}

// --- Next Action Translations ---
export const NEXT_ACTION_TRANSLATIONS: Record<string, string> = {
  DURABLE_WORKER_OR_HUMAN_REVIEW: 'Review the saved case and its next required step',
  AWAITING_APPROVAL: 'Supervisory approval pending',
  INSPECT_D18: 'Inspect downstream drainage conduit D18',
  FOLLOW_UP_ORDINARY_RAINFALL: 'Monitor drainage under ordinary rainfall',
  ASSESS_CAPACITY: 'Assess stormwater runoff capacity and rainfall intensity',
  INSPECT_SUBGRADE: 'Conduct structural subgrade inspection beneath road',
  REPAIR_UTILITY_LEAK: 'Isolate and repair underground water pipe leak',
  RECOVERY_WASTE_COLLECTION: 'Deploy recovery waste collection vehicle',
};

export function translateNextAction(action?: string | null): string {
  if (!action) return 'Action pending';
  const upper = action.trim().toUpperCase();
  if (NEXT_ACTION_TRANSLATIONS[upper]) {
    return NEXT_ACTION_TRANSLATIONS[upper];
  }
  return upper
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ');
}

// --- Missing Evidence Formatting ---
export function formatMissingEvidence(item: string): string {
  if (!item) return '';
  if (item.includes(',')) {
    return item
      .split(',')
      .map((tok) => formatMissingEvidenceToken(tok.trim()))
      .join('; ');
  }
  return formatMissingEvidenceToken(item);
}

function formatMissingEvidenceToken(tok: string): string {
  if (tok.startsWith('EV-') || tok.startsWith('EVI-')) {
    return `Evidence reference #${formatShortIdentifier(tok)} needs review`;
  }
  if (tok.startsWith('INC-')) {
    return `Linked incident #${formatShortIdentifier(tok)} needs review`;
  }
  if (tok.startsWith('INSP-')) {
    return `Pending engineering field inspection (#${formatShortIdentifier(tok)})`;
  }
  const upper = tok.trim().toUpperCase();
  const KNOWN_TOKENS: Record<string, string> = {
    BIN_CAPACITY_EXCEEDED: 'Audit of container capacity vs. peak disposal volume',
    EXPECTED_PICKUPS_COMPLETED: 'Verification of municipal sanitation collection logs',
    DRAIN_INFLOW_RESTRICTION: 'Physical inspection of drainage inlet grate for sediment blockage',
    STRUCTURAL_INTEGRITY_TEST: 'Mechanical load test of pavement foundation',
    WATER_PRESSURE_TEST: 'Hydrostatic pressure test of municipal water main',
    RUNOFF_SURGE_MEASUREMENT: 'Measured storm runoff flow rate data',
  };
  if (KNOWN_TOKENS[upper]) return KNOWN_TOKENS[upper];
  return tok.replace(/\b(?:EV-REPORT|EV-JOURNAL|INC)-[A-Z0-9-]+/gi, id => `reference #${formatShortIdentifier(id)}`).replaceAll('_',' ');
}

// --- Text Sanitization for Agent Rationales & Questions ---
export function cleanTextIdentifiers(text: string): string {
  if (!text) return '';
  let result = text;
  for (const [raw, clean] of Object.entries(ASSET_TRANSLATIONS)) {
    result = result.replaceAll(raw, clean);
  }
  for (const [raw, clean] of Object.entries(LOCATION_TRANSLATIONS)) {
    result = result.replaceAll(raw, clean);
  }
  result = result.replace(/civicly::([a-z_]+)/g, (_, fn) => translateToolAction(`civicly::${fn}`));
  result = result.replace(/official::([a-z_]+)/g, (_, fn) => translateToolAction(`official::${fn}`));
  result = result.replace(/\b(?:ASSESS|HYP|EV-REPORT|EV-JOURNAL|INC|INS)-B\d+-[a-f0-9]{16,}\b/gi,id=>`reference #${formatShortIdentifier(id)}`);
  // Translate whole codes, longest action names first. Never turn a prefix such
  // as UTILITY_LEAK inside UTILITY_LEAK_REPAIR into a broken partial phrase.
  result = result.replace(/\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b/g,code=>{
    if(ACTION_TYPE_TRANSLATIONS[code])return translateActionType(code);
    if(CAUSE_CODE_TRANSLATIONS[code])return translateCauseCode(code).title;
    return translateStatus(code);
  });
  result = result.replace(/\bBLOCKAGE\b/g,translateCauseCode('BLOCKAGE').title);
  return result;
}

// --- Entity Names & Neutral Truthful Fallbacks ---
/** Explain the saved plan note without upgrading a possible cause to a fact.
 * The original reason stays available in technical details. Unknown coded notes
 * get a neutral summary rather than an invented interpretation.
 */
export function explainPlanConsideration(reason: string, addressed: boolean): string {
  let explanation: string;
  if (/^Assessment ASSESS-B\d+-[a-f0-9]+ found BLOCKAGE supported by reviewed inspection observations FLOW_RESTRICTED and OBSTRUCTION_OBSERVED on DRAIN-[A-Z0-9-]+\.$/.test(reason)) {
    explanation = 'The inspection found something blocking the drain and preventing water from flowing freely. This supports a blockage as a possible cause.';
  } else if (reason === 'Alternative hypothesis CAPACITY_DEFICIT assessed as INCONCLUSIVE due to lack of discriminating capacity test evidence.') {
    explanation = 'There is not enough evidence to tell whether the drain can handle the amount of water it receives.';
  } else if (/^Assessment evaluated confirming physical observations STRUCTURAL_TEST_FAILED and SUBGRADE_FAILURE_OBSERVED on ROAD-[A-Z0-9-]+, supporting subgrade failure mechanism\.$/.test(reason)) {
    explanation = 'The inspection found structural problems in the ground beneath the road. These findings support weakened ground as a possible cause of the damage.';
  } else if (/^Assessment evaluated normal pressure test observation PRESSURE_TEST_NORMAL on PIPE-[A-Z0-9-]+, contradicting the competing utility leak hypothesis\.$/.test(reason)) {
    explanation = 'The pressure test was normal. That finding argues against a pipe leak as the cause.';
  } else if (reason === 'Reviewed bounded mechanism supports conditional simulated remedy') {
    explanation = 'The reviewed evidence supports a possible repair, provided the conditions in this simulated plan are met.';
  } else if (reason === 'Retained uncertain extent does not authorize additional work') {
    explanation = 'The extent of any further damage is still uncertain. This does not justify extra work.';
  } else if (/\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b|\b(?:ASSESS|HYP|EV|INC|INS)-/i.test(reason)) {
    explanation = 'This possible cause was considered when the plan was prepared. The original assessment note is available in Technical details.';
  } else {
    explanation = reason.trim() || 'No explanation was recorded for this plan decision.';
  }
  return `${explanation} ${addressed ? 'The plan includes work to address this possible cause.' : 'The plan does not include work for this possible cause.'}`;
}

export interface EntityDisplay {
  primary: string;
  secondary?: string;
  shortId: string;
  kindLabel: string;
}

export function formatShortIdentifier(id: string): string {
  if (!id) return '';
  if (id.length <= 10) return id;
  const parts = id.split('-');
  const truncatePart = (p: string) => (p.length > 8 ? p.slice(0, 6) : p);

  if (parts.length >= 4 && parts[0] === 'INV') {
    return parts.slice(-3).map(truncatePart).join('-');
  }
  if (parts.length >= 3) {
    return parts.slice(-2).map(truncatePart).join('-');
  }
  return truncatePart(id);
}

export function formatEntityDisplayName(params: {
  id: string;
  name?: string;
  statement?: string;
  kind?: string;
  displayLabel?: string;
  issueType?: string;
  location?: string;
  causeCode?: string;
}): EntityDisplay {
  const { id, name, statement, kind, displayLabel, issueType, location, causeCode } = params;
  const shortId = formatShortIdentifier(id);

  // If a descriptive name or displayLabel exists and is not just the raw ID
  const effectiveLabel = name || displayLabel;
  if (effectiveLabel && effectiveLabel.trim() && effectiveLabel !== id) {
    return {
      primary: effectiveLabel,
      secondary: shortId !== effectiveLabel ? shortId : undefined,
      shortId,
      kindLabel: translateEntityKind(kind),
    };
  }

  // Derive truthful neutral fallback grounded in type/category without parsing IDs
  if (id.startsWith('INV-')) {
    const issueDesc = issueType ? formatIssueName(issueType) : 'Civic';
    return {
      primary: `${issueDesc} Investigation`,
      secondary: shortId,
      shortId,
      kindLabel: 'Investigation',
    };
  }

  if (id.startsWith('INC-')) {
    const issueDesc = issueType ? formatIssueName(issueType) : 'Civic';
    const locDesc = location ? ` at ${translateLocation(location)}` : '';
    return {
      primary: `Reported incident: ${issueDesc}${locDesc}`,
      secondary: shortId,
      shortId,
      kindLabel: 'Reported incident',
    };
  }

  if (id.startsWith('PLAN-')) {
    return {
      primary: 'Proposed action plan',
      secondary: shortId,
      shortId,
      kindLabel: 'Remediation plan',
    };
  }

  if (id.startsWith('HYP-')) {
    const cause = causeCode
      ? translateCauseCode(causeCode).title
      : statement
      ? translateCauseCode(statement).title
      : 'Possible cause';
    return {
      primary: cause,
      secondary: shortId,
      shortId,
      kindLabel: 'Possible cause',
    };
  }

  if (id.startsWith('EVI-') || id.startsWith('REP-')) {
    return {
      primary: 'Supporting evidence record',
      secondary: shortId,
      shortId,
      kindLabel: 'Supporting evidence',
    };
  }

  if (id.startsWith('WO-')) {
    return {
      primary: 'Remediation work order',
      secondary: shortId,
      shortId,
      kindLabel: 'Work order',
    };
  }

  if (id.startsWith('INSP-')) {
    return {
      primary: 'Field inspection record',
      secondary: shortId,
      shortId,
      kindLabel: 'Field inspection',
    };
  }

  if (id.startsWith('TASK-')) {
    return {
      primary: 'Remediation task',
      secondary: shortId,
      shortId,
      kindLabel: 'Plan task',
    };
  }

  if (
    kind === 'InfrastructureAsset' ||
    id.startsWith('WASTE-') ||
    id.startsWith('DRAIN-') ||
    id.startsWith('PIPE-') ||
    id.startsWith('ROAD-') ||
    id.startsWith('ASSET-')
  ) {
    const assetTitle = translateAsset(id);
    return {
      primary: assetTitle,
      secondary: shortId !== assetTitle ? shortId : undefined,
      shortId,
      kindLabel: 'Infrastructure asset',
    };
  }

  if (id.startsWith('LOC-')) {
    const locTitle = translateLocation(id);
    return {
      primary: locTitle,
      secondary: shortId !== locTitle ? shortId : undefined,
      shortId,
      kindLabel: 'Civic location',
    };
  }

  if (id.startsWith('CLUSTER-') || id.startsWith('PC-')) {
    return {
      primary: 'Problem recurrence cluster',
      secondary: shortId,
      shortId,
      kindLabel: 'Problem cluster',
    };
  }

  return {
    primary: translateEntityKind(kind) || 'Civic infrastructure entity',
    secondary: shortId,
    shortId,
    kindLabel: translateEntityKind(kind),
  };
}

export function translateEntityKind(kind?: string | null): string {
  if (!kind) return 'Civic entity';
  switch (kind) {
    case 'Incident':
      return 'Reported incident';
    case 'InfrastructureAsset':
      return 'Infrastructure asset';
    case 'Observation':
      return 'Field observation';
    case 'Evidence':
      return 'Supporting evidence';
    case 'Hypothesis':
      return 'Possible cause';
    case 'DecisionPath':
      return 'Recorded decision path';
    case 'ProblemCluster':
      return 'Problem recurrence cluster';
    case 'Procedure':
      return 'Municipal procedure';
    case 'WorkOrder':
      return 'Work order';
    case 'Inspection':
      return 'Field inspection';
    default:
      return kind
        .split(/(?=[A-Z])/)
        .join(' ');
  }
}

export function formatIssueName(issue?: string | null): string {
  if (!issue) return 'Civic infrastructure';
  switch (issue.toUpperCase()) {
    case 'WATERLOGGING':
      return 'Waterlogging';
    case 'ROAD_DAMAGE':
      return 'Road damage';
    case 'WASTE_ACCUMULATION':
      return 'Waste accumulation';
    default:
      return issue
        .split('_')
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
        .join(' ');
  }
}
