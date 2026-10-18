import type {
  PlanDTO,
  PlanTaskBinding,
  TaskDraft,
  WorkOrderDTO,
  InspectionDTO,
} from '../generated/models';

export interface DagTaskNode {
  id: string;
  action_type: string;
  target_ids: string[];
  department_id: string;
  depends_on: string[];
  prerequisites: string[];
  status: string;
  tier: number;
  eligible_assignees: string[];
  remediation?: TaskDraft['remediation'];
  procedure_citation?: TaskDraft['procedure_citation'];
  expected_outcome?: string;
  verification_criteria?: string;
  risks?: string[];
  uncertainties?: string[];
}

export interface DagStructure {
  nodes: DagTaskNode[];
  tiers: DagTaskNode[][];
  hasCycle: boolean;
  totalTasks: number;
}

/**
 * Computes the topological tiers for tasks in a plan DAG.
 * Tiers indicate execution order: Tier 0 tasks have no prerequisites,
 * Tier 1 tasks depend only on Tier 0 tasks, etc.
 */
export function computeTaskDag(
  tasks: TaskDraft[] = [],
  taskBindings: PlanTaskBinding[] = []
): DagStructure {
  if (!tasks.length && !taskBindings.length) {
    return { nodes: [], tiers: [], hasCycle: false, totalTasks: 0 };
  }

  // Create lookup for bindings
  const bindingMap = new Map<string, PlanTaskBinding>();
  for (const b of taskBindings) {
    bindingMap.set(b.local_task_id || b.task_id, b);
  }

  // Normalize nodes
  const nodeMap = new Map<string, DagTaskNode>();
  const taskIds: string[] = [];

  for (const t of tasks) {
    const id = t.id;
    taskIds.push(id);
    const binding = bindingMap.get(id);

    const dependsOn = Array.isArray(t.depends_on)
      ? t.depends_on
      : binding?.depends_on_task_ids || [];

    nodeMap.set(id, {
      id,
      action_type: t.action_type || binding?.action_type || 'TASK',
      target_ids: t.target_ids || binding?.target_ids || [],
      department_id: t.department_id || binding?.department_id || 'UNKNOWN',
      depends_on: dependsOn,
      prerequisites: t.prerequisites || [],
      status: binding?.status || 'PROPOSED',
      tier: 0,
      eligible_assignees: binding?.eligible_assignee_ids || [],
      remediation: t.remediation,
      procedure_citation: t.procedure_citation,
      expected_outcome: t.expected_outcome,
      verification_criteria: t.verification_criteria,
      risks: t.risks,
      uncertainties: (t as any).uncertainties,
    });
  }

  // If bindings exist that were not in tasks, add them as well
  for (const b of taskBindings) {
    const id = b.local_task_id || b.task_id;
    if (!nodeMap.has(id)) {
      taskIds.push(id);
      nodeMap.set(id, {
        id,
        action_type: b.action_type || 'TASK',
        target_ids: b.target_ids || [],
        department_id: b.department_id || 'UNKNOWN',
        depends_on: b.depends_on_task_ids || [],
        prerequisites: [],
        status: b.status || 'PROPOSED',
        tier: 0,
        eligible_assignees: b.eligible_assignee_ids || [],
      });
    }
  }

  // Compute topological tiers
  const inDegree = new Map<string, number>();
  const children = new Map<string, string[]>();

  for (const id of taskIds) {
    inDegree.set(id, 0);
    children.set(id, []);
  }

  for (const id of taskIds) {
    const node = nodeMap.get(id)!;
    for (const depId of node.depends_on) {
      if (nodeMap.has(depId)) {
        inDegree.set(id, (inDegree.get(id) || 0) + 1);
        children.get(depId)!.push(id);
      }
    }
  }

  // Kahn's algorithm with tier assignment
  let currentQueue: string[] = [];
  for (const id of taskIds) {
    if ((inDegree.get(id) || 0) === 0) {
      currentQueue.push(id);
    }
  }

  const tiers: DagTaskNode[][] = [];
  let processedCount = 0;
  let currentTierIndex = 0;

  while (currentQueue.length > 0) {
    const tierNodes: DagTaskNode[] = [];
    const nextQueue: string[] = [];

    for (const id of currentQueue) {
      const node = nodeMap.get(id)!;
      node.tier = currentTierIndex;
      tierNodes.push(node);
      processedCount++;

      for (const childId of children.get(id) || []) {
        const remaining = (inDegree.get(childId) || 1) - 1;
        inDegree.set(childId, remaining);
        if (remaining === 0) {
          nextQueue.push(childId);
        }
      }
    }

    tiers.push(tierNodes);
    currentQueue = nextQueue;
    currentTierIndex++;
  }

  const hasCycle = processedCount < taskIds.length;

  // Fallback for cycle: put remaining unprocessed nodes in a final tier
  if (hasCycle) {
    const cycleTier: DagTaskNode[] = [];
    for (const id of taskIds) {
      if ((inDegree.get(id) || 0) > 0) {
        const node = nodeMap.get(id)!;
        node.tier = currentTierIndex;
        cycleTier.push(node);
      }
    }
    if (cycleTier.length) tiers.push(cycleTier);
  }

  return {
    nodes: Array.from(nodeMap.values()),
    tiers,
    hasCycle,
    totalTasks: taskIds.length,
  };
}

export function formatShortHash(hash?: string | null): string {
  if (!hash) return 'Not recorded';
  if (hash.length <= 16) return hash;
  return `${hash.slice(0, 8)}…${hash.slice(-8)}`;
}

export function getStatusBadgeStyle(status: string): {
  bg: string;
  color: string;
  border: string;
} {
  switch (status.toUpperCase()) {
    case 'APPROVED':
    case 'COMPLETED':
    case 'VERIFIED':
      return { bg: '#e6f4ea', color: '#137333', border: '#b7e1cd' };
    case 'PENDING_APPROVAL':
    case 'PENDING':
    case 'IN_PROGRESS':
    case 'SCHEDULED':
      return { bg: '#e8f0fe', color: '#1a73e8', border: '#aecbfa' };
    case 'DRAFT':
    case 'PROPOSED':
    case 'REQUESTED':
      return { bg: '#f1f3f4', color: '#5f6368', border: '#dadce0' };
    case 'BLOCKED':
    case 'FAILED':
    case 'REJECTED':
      return { bg: '#fce8e6', color: '#c5221f', border: '#f5c2c7' };
    case 'SUPERSEDED':
    case 'CANCELLED':
      return { bg: '#f8f9fa', color: '#80868b', border: '#dadce0' };
    default:
      return { bg: '#f1f3f4', color: '#3c4043', border: '#dadce0' };
  }
}
