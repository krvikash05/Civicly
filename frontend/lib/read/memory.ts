import type {
  ProcedureDTO,
  MonitoringDTO,
  CaseMemoryDTO,
  OutcomeDTO,
} from '../generated/models';

/**
 * Finds the specific monitoring record for a given problem cluster ID.
 */
export function findClusterMonitoring(
  monitoringList: MonitoringDTO[] = [],
  clusterId?: string | null
): MonitoringDTO | null {
  if (!clusterId || !monitoringList.length) return null;
  return monitoringList.find((m) => m.problem_cluster_id === clusterId) || null;
}

/**
 * Filters procedure documents relevant to an investigation's department or issue category.
 */
export function filterRelevantProcedures(
  procedures: ProcedureDTO[] = [],
  departmentId?: string | null,
  issueType?: string | null
): ProcedureDTO[] {
  if (!procedures.length) return [];
  if (!departmentId && !issueType) return procedures;

  const deptNormalized = departmentId?.toUpperCase() || '';
  const issueNormalized = issueType?.toUpperCase() || '';

  return procedures.filter((proc) => {
    const procDept = proc.owner_department_id?.toUpperCase() || '';
    const procTitle = proc.title?.toUpperCase() || '';

    // Match by department ID
    if (deptNormalized && procDept.includes(deptNormalized)) return true;

    // Match by issue category keywords
    if (issueNormalized === 'WATERLOGGING' && (procDept.includes('DRAIN') || procTitle.includes('DRAIN') || procTitle.includes('CULVERT'))) {
      return true;
    }
    if (issueNormalized === 'ROAD_DAMAGE' && (procDept.includes('ROAD') || procTitle.includes('ROAD') || procTitle.includes('SUBGRADE') || procTitle.includes('POTHOLE'))) {
      return true;
    }
    if (issueNormalized === 'WASTE_ACCUMULATION' && (procDept.includes('WASTE') || procDept.includes('SANITATION') || procTitle.includes('WASTE') || procTitle.includes('PICKUP'))) {
      return true;
    }

    return false;
  });
}

/**
 * Returns badge styling for cluster monitoring lifecycle statuses.
 */
export function getMonitoringStatusStyle(status: string): {
  bg: string;
  color: string;
  border: string;
} {
  switch (status.toUpperCase()) {
    case 'CONTROLLED':
    case 'RESOLVED':
    case 'COMPLETED':
      return { bg: '#e6f4ea', color: '#137333', border: '#b7e1cd' };
    case 'MONITORING':
      return { bg: '#e8f0fe', color: '#1a73e8', border: '#aecbfa' };
    case 'OPEN':
      return { bg: '#fef7e0', color: '#b06000', border: '#fce8b2' };
    case 'REOPENED':
      return { bg: '#fce8e6', color: '#c5221f', border: '#f5c2c7' };
    default:
      return { bg: '#f1f3f4', color: '#5f6368', border: '#dadce0' };
  }
}

/**
 * Truncates and cleans quote excerpts for display.
 */
export function formatQuoteExcerpt(quote?: string | null, maxLength = 240): string {
  if (!quote) return 'No excerpt recorded.';
  const cleaned = quote.replace(/[\r\n]+/g, ' ').trim();
  if (cleaned.length <= maxLength) return cleaned;
  return cleaned.slice(0, maxLength) + '…';
}
