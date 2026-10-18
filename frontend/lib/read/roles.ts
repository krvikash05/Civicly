/**
 * Municipal Role Governance and Identity Model for Civicly
 * Reflects backend OPERATORS and RBAC policies in app/services/operations/auth.py
 */

export interface OperatorProfile {
  id: string;
  role: 'ANALYST' | 'APPROVER' | 'DEPARTMENT_LEAD' | 'ADMIN';
  departmentId: string;
  departmentName: string;
  title: string;
  description: string;
  capabilities: string[];
  boundaries: string[];
}

export const MUNICIPAL_OPERATORS: Record<string, OperatorProfile> = {
  'OP-ANALYST': {
    id: 'OP-ANALYST',
    role: 'ANALYST',
    departmentId: 'DEPT-COORD',
    departmentName: 'Municipal Operations Coordination',
    title: 'Civic Intelligence Analyst (Connected Demo Operator)',
    description:
      'Investigates recurring civic defects across waterlogging, road damage, and waste accumulation. Follows FalkorDB graph evidence, queries hypotheses, and drafts remediation plans.',
    capabilities: [
      'Query and inspect FalkorDB connected knowledge graph',
      'Follow agent reasoning steps and MCP tool traces',
      'Evaluate competing causal hypotheses and cited evidence',
      'Draft and submit remediation plans with SHA-256 hash digests',
      'Monitor cluster post-intervention verification progress',
    ],
    boundaries: [
      'Cannot approve remediation plans (requires independent APPROVER)',
      'Cannot dispatch physical work orders directly',
      'Cannot reset or reconfigure municipal databases',
    ],
  },
  'OP-APPROVER': {
    id: 'OP-APPROVER',
    role: 'APPROVER',
    departmentId: 'DEPT-COORD',
    departmentName: 'Municipal Governance & Oversight',
    title: 'Independent Municipal Approver',
    description:
      'Provides independent review and governance over AI-generated and analyst-submitted remediation plans before physical municipal intervention occurs.',
    capabilities: [
      'Review submitted remediation plans and prerequisite safety conditions',
      'Approve remediation plans bound to plan ID, version, and content hash',
      'Reject plans with explicit municipal justification',
      'Authorize emergency work order dispatch following plan approval',
    ],
    boundaries: [
      'Cannot draft plans (strict separation of duties from ANALYST)',
      'Cannot self-execute field repairs',
    ],
  },
  'OP-DRAIN-LEAD': {
    id: 'OP-DRAIN-LEAD',
    role: 'DEPARTMENT_LEAD',
    departmentId: 'DEPT-DRAIN',
    departmentName: 'Stormwater & Drainage Department',
    title: 'Drainage Department Lead',
    description:
      'Responsible for municipal stormwater infrastructure, culvert desiltation, catchbasin maintenance, and pump stations.',
    capabilities: [
      'Review drainage inspection requests and assign field crews',
      'Verify catchbasin and culvert clearance operations',
      'Access internal drainage standard operating procedures',
    ],
    boundaries: [
      'Authority limited to DEPT-DRAIN jurisdiction and assets',
    ],
  },
  'OP-ROAD-LEAD': {
    id: 'OP-ROAD-LEAD',
    role: 'DEPARTMENT_LEAD',
    departmentId: 'DEPT-ROAD',
    departmentName: 'Roads & Infrastructure Maintenance',
    title: 'Roads Department Lead',
    description:
      'Oversees arterial road networks, pavement repairs, subgrade stabilization, and asphalt resurfacing.',
    capabilities: [
      'Commission asphalt and subgrade inspection teams',
      'Manage road repair work orders and contractor dispatches',
      'Access internal road maintenance standard operating procedures',
    ],
    boundaries: [
      'Authority limited to DEPT-ROAD jurisdiction and assets',
    ],
  },
  'OP-WASTE-LEAD': {
    id: 'OP-WASTE-LEAD',
    role: 'DEPARTMENT_LEAD',
    departmentId: 'DEPT-SAN',
    departmentName: 'Sanitation & Solid Waste Management',
    title: 'Sanitation Department Lead',
    description:
      'Coordinates municipal waste collection routes, illegal dumping clearance, and landfill logistics.',
    capabilities: [
      'Track waste collection truck GPS telemetry and route schedules',
      'Dispatch overflow and illegal dumping response teams',
      'Access sanitation standard operating procedures',
    ],
    boundaries: [
      'Authority limited to DEPT-SAN jurisdiction and assets',
    ],
  },
  'OP-WATER-LEAD': {
    id: 'OP-WATER-LEAD',
    role: 'DEPARTMENT_LEAD',
    departmentId: 'DEPT-WATER',
    departmentName: 'Water Supply & Utility Distribution',
    title: 'Water Supply Utility Lead',
    description:
      'Manages pressurized potable water mains, utility valve networks, and subsurface leak detection.',
    capabilities: [
      'Monitor water main telemetry and hydraulic pressure sensors',
      'Dispatch utility emergency excavation and valve shutoff crews',
      'Access water distribution operating procedures',
    ],
    boundaries: [
      'Authority limited to DEPT-WATER jurisdiction and assets',
    ],
  },
  'OP-ADMIN': {
    id: 'OP-ADMIN',
    role: 'ADMIN',
    departmentId: 'DEPT-COORD',
    departmentName: 'Municipal Operations Administration',
    title: 'System & Platform Administrator',
    description:
      'Maintains platform integrity, manages operator accounts, and administers test scenario provisioning.',
    capabilities: [
      'Reset and seed demonstration scenarios (S01–S12)',
      'Provision and revoke operator access tokens',
      'Manage FalkorDB graph schemas and migration versions',
    ],
    boundaries: [
      'Operational actions must be logged in audit trail',
    ],
  },
};

export function getOperatorProfile(id: string): OperatorProfile {
  return (
    MUNICIPAL_OPERATORS[id] ?? {
      id,
      role: 'ANALYST',
      departmentId: 'DEPT-COORD',
      departmentName: 'Municipal Operations',
      title: `Operator (${id})`,
      description: 'Municipal operator account.',
      capabilities: ['Inspect public investigations and dashboard reads'],
      boundaries: ['Actions subject to backend role-based access control'],
    }
  );
}

export function isActionPermitted(
  operatorRole: string,
  action: 'DRAFT_PLAN' | 'SUBMIT_PLAN' | 'APPROVE_PLAN' | 'DISPATCH_WORK' | 'RESET_DEMO'
): boolean {
  switch (action) {
    case 'DRAFT_PLAN':
    case 'SUBMIT_PLAN':
      return operatorRole === 'ANALYST' || operatorRole === 'ADMIN';
    case 'APPROVE_PLAN':
      return operatorRole === 'APPROVER' || operatorRole === 'ADMIN';
    case 'DISPATCH_WORK':
      return (
        operatorRole === 'APPROVER' ||
        operatorRole === 'DEPARTMENT_LEAD' ||
        operatorRole === 'ADMIN'
      );
    case 'RESET_DEMO':
      return operatorRole === 'ADMIN';
    default:
      return false;
  }
}
