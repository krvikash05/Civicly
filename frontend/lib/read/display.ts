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
  COMPLETED: 'Work completed',
  VERIFIED: 'Verified resolution',
  CLOSED: 'Case closed',
  ENDED: 'Incident ended',
  NOT_STARTED: 'Not started',
  BLOCKED: 'Blocked by prerequisite',
  FAILED: 'Failed',

  // Hypothesis Assessments (strictly separated from plan coverage)
  SUPPORTED: 'Supported by verified evidence',
  CONTRADICTED: 'Contradicted by field inspection',
  INCONCLUSIVE: 'Inconclusive (pending evidence)',

  // Monitoring Statuses
  MONITORING: 'Under post-intervention monitoring',
  CONTROLLED: 'Controlled (no recurrence)',
  REOPENED: 'Reopened due to recurrence',

  // Verification & Edge Statuses
  CANDIDATE: 'Candidate (unverified)',
  REVISION_PENDING: 'Revision pending',
};

export function translateStatus(status?: string | null): string {
  if (!status) return 'Status unavailable';
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
    title: 'Unauthorized waste disposal observed',
    explanation: 'Solid waste deposited outside scheduled municipal collection cycles.',
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
  const title = upper
    .split('_')
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(' ');
  return {
    title,
    explanation: `Diagnostic finding recorded under code ${code}.`,
  };
}

// --- Evidence Assessment vs Plan Coverage ---
export interface AssessmentInfo {
  label: string;
  badgeClass: string;
  tone: 'supported' | 'contradicted' | 'inconclusive' | 'default';
  description: string;
}

export function translateAssessment(status?: string | null): AssessmentInfo {
  const upper = (status || '').trim().toUpperCase();
  switch (upper) {
    case 'SUPPORTED':
      return {
        label: 'Supported',
        badgeClass: 'badge-verified',
        tone: 'supported',
        description: 'Verified physical evidence corroborates this possible cause.',
      };
    case 'CONTRADICTED':
      return {
        label: 'Contradicted',
        badgeClass: 'badge-danger',
        tone: 'contradicted',
        description: 'Verified inspection or diagnostic measurements refute this cause.',
      };
    case 'INCONCLUSIVE':
      return {
        label: 'Inconclusive',
        badgeClass: 'badge-candidate',
        tone: 'inconclusive',
        description: 'Evidence is insufficient or conflicting; requires targeted field verification.',
      };
    default:
      return {
        label: status || 'Pending',
        badgeClass: 'badge-default',
        tone: 'default',
        description: 'Assessment pending further evidence.',
      };
  }
}

// --- Action Types Translations ---
export const ACTION_TYPE_TRANSLATIONS: Record<string, string> = {
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
  'DEPT-DRAIN': 'Drainage & Stormwater Department',
  'DEPT-ROAD': 'Roads & Infrastructure Department',
  'DEPT-SAN': 'Sanitation & Waste Management',
  'DEPT-WATER': 'Water Supply & Sewerage Board',
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
  'OP-ANALYST': 'Investigation Analyst',
  'OP-APPROVER': 'Supervising Approval Officer',
  'OP-DRAIN-LEAD': 'Drainage Operations Lead',
  'OP-ROAD-LEAD': 'Roads Operations Lead',
  'OP-WASTE-LEAD': 'Waste Operations Lead',
  'OP-WATER-LEAD': 'Water Utility Lead',
  'OP-ADMIN': 'City Operations Administrator',
  ANALYST: 'Investigation Analyst',
  APPROVER: 'Approval Officer',
  OPERATOR: 'Field Operations Lead',
  ADMIN: 'System Administrator',
};

export function translateRole(role?: string | null): string {
  if (!role) return 'Municipal Operator';
  const upper = role.trim().toUpperCase();
  return ROLE_TRANSLATIONS[upper] || role;
}

// --- Entity Names & Neutral Truthful Fallbacks ---
export interface EntityDisplay {
  primary: string;
  secondary?: string;
  shortId: string;
  kindLabel: string;
}

export function formatShortIdentifier(id: string): string {
  if (!id) return '';
  if (id.length <= 14) return id;
  // If format PREFIX-Bxx-hash, show prefix and tail
  const parts = id.split('-');
  if (parts.length >= 3) {
    const prefix = parts[0];
    const tail = parts[parts.length - 1];
    return `${prefix}-…${tail.slice(-4)}`;
  }
  return `${id.slice(0, 6)}…${id.slice(-4)}`;
}

export function formatEntityDisplayName(params: {
  id: string;
  kind?: string;
  displayLabel?: string;
  issueType?: string;
  location?: string;
  causeCode?: string;
}): EntityDisplay {
  const { id, kind, displayLabel, issueType, location, causeCode } = params;
  const shortId = formatShortIdentifier(id);

  // If a descriptive displayLabel exists and is not just the raw ID
  if (displayLabel && displayLabel.trim() && displayLabel !== id) {
    return {
      primary: displayLabel,
      secondary: shortId !== displayLabel ? shortId : undefined,
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
    const locDesc = location ? ` at ${location}` : '';
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
    const cause = causeCode ? translateCauseCode(causeCode).title : 'Possible cause';
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

  if (id.startsWith('DRAIN-') || id.startsWith('DRN-')) {
    return {
      primary: 'Stormwater drain inlet',
      secondary: shortId,
      shortId,
      kindLabel: 'Drain inlet',
    };
  }

  if (id.startsWith('PIPE-') || id.startsWith('WAT-')) {
    return {
      primary: 'Underground water pipe',
      secondary: shortId,
      shortId,
      kindLabel: 'Water pipe',
    };
  }

  if (id.startsWith('ROAD-') || id.startsWith('RDS-')) {
    return {
      primary: 'Municipal road segment',
      secondary: shortId,
      shortId,
      kindLabel: 'Road segment',
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
        .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
        .join(' ');
  }
}
