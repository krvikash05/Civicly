import type {
  GraphSubgraphDTO,
  GraphNode,
  GraphEdge,
  DecisionPath,
  AgentTracePage,
  AgentTraceEvent,
  HypothesisPage,
  HypothesisDTO,
  EvidenceDTO,
} from '../generated/models.ts';
import {
  formatEntityDisplayName,
  translateStatus,
} from './display.ts';

export interface CanvasNode {
  id: string;
  labels: string[];
  color: string;
  visible: boolean;
  caption: string;
  size?: number;
  data: {
    originalId: string;
    kind: string;
    display_label: string;
    readableName: string;
    shortId: string;
    status?: string | null;
    source_kind?: string | null;
    evidence_ids: string[];
    observed_at?: string | null;
    is_decision_path: boolean;
  };
}

export interface CanvasLink {
  id: string;
  relationship: string;
  readableRelationship: string;
  color: string;
  source: string;
  target: string;
  visible: boolean;
  data: {
    originalId: string;
    type: string;
    verification_status: string;
    valid_from?: string | null;
    valid_to?: string | null;
    observed_at?: string | null;
    source_evidence_ids: string[];
    is_decision_path: boolean;
  };
}

export interface CanvasGraphData {
  nodes: CanvasNode[];
  links: CanvasLink[];
}

export interface GraphDisplayStats {
  totalNodes: number;
  totalEdges: number;
  verifiedEdges: number;
  candidateEdges: number;
  decisionPathEdges: number;
  truncated: boolean;
  searchLimited: boolean;
  graphRevision: number;
  asOf: string;
  reservations: string[];
  whatThisGraphShows: string;
}

export interface DecisionTraceItem {
  eventId: string;
  timestamp: string;
  agentRole: string;
  kind: string;
  toolName: string | null;
  status: string;
  questionAsked: string;
  graphEvidence: {
    nodeIds: string[];
    edgeIds: string[];
    evidenceIds: string[];
    summary: string;
  };
  recordedDecision: {
    action: string;
    rationaleSummary: string;
    decisionId: string | null;
    parentExecutionId: string | null;
  };
  influenceCategory: 'MODEL_SELECTED_PATH' | 'CONTEXTUAL_GRAPH_QUERY' | 'UNESTABLISHED_INFLUENCE';
  influenceExplanation: string;
}

export const NODE_KIND_COLORS: Record<string, string> = {
  Incident: '#DC2626',           // Crimson
  InfrastructureAsset: '#2563EB',// Blue
  Observation: '#7C3AED',        // Violet
  Evidence: '#0D9488',           // Teal
  Hypothesis: '#4F46E5',         // Indigo
  DecisionPath: '#D97706',       // Amber
  Default: '#475569',            // Slate
};

export const EDGE_STATUS_COLORS = {
  verified: '#059669',          // Emerald
  candidate: '#D97706',         // Amber
  decisionPath: '#2563EB',      // Highlight Blue
  default: '#64748B',           // Slate
};

export function getNodeColor(kind: string, labels: string[] = []): string {
  if (NODE_KIND_COLORS[kind]) return NODE_KIND_COLORS[kind];
  for (const label of labels) {
    if (NODE_KIND_COLORS[label]) return NODE_KIND_COLORS[label];
  }
  return NODE_KIND_COLORS.Default;
}

export function getLinkColor(status: string, isDecisionPath: boolean): string {
  if (isDecisionPath) return EDGE_STATUS_COLORS.decisionPath;
  if (status === 'VERIFIED') return EDGE_STATUS_COLORS.verified;
  if (status === 'CANDIDATE') return EDGE_STATUS_COLORS.candidate;
  return EDGE_STATUS_COLORS.default;
}

export function translateRelationshipType(relType: string): string {
  switch (relType.toUpperCase()) {
    case 'DRAINS_TO':
      return 'Drains into';
    case 'MAINTAINED_BY':
      return 'Maintained by';
    case 'UNDERLIES':
      return 'Underlies road';
    case 'OBSERVED_AT':
      return 'Observed at';
    case 'PART_OF':
      return 'Part of cluster';
    case 'EVALUATES':
      return 'Evaluates cause';
    case 'HAS_OUTCOME':
      return 'Has outcome';
    case 'HAS_EVIDENCE':
      return 'Supported by evidence';
    case 'AFFECTS':
      return 'Affects asset';
    case 'CONNECTED_TO':
      return 'Connected to';
    default:
      return relType
        .split('_')
        .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
        .join(' ');
  }
}

export function mapGraphSubgraphToCanvas(
  subgraph: GraphSubgraphDTO,
  selectedDecisionPathId?: string | null,
): { data: CanvasGraphData; stats: GraphDisplayStats } {
  const activeDecisionPathIds = new Set<string>();
  const decisionPathNodeIds = new Set<string>();
  const decisionPathEdgeIds = new Set<string>();

  if (subgraph.decision_paths && Array.isArray(subgraph.decision_paths)) {
    for (const dp of subgraph.decision_paths) {
      if (!selectedDecisionPathId || dp.id === selectedDecisionPathId) {
        activeDecisionPathIds.add(dp.id);
        dp.node_ids.forEach((id) => decisionPathNodeIds.add(id));
        dp.edge_ids.forEach((id) => decisionPathEdgeIds.add(id));
      }
    }
  }

  // Count entities by kind for grounded explanation
  const kindCounts: Record<string, number> = {};

  const nodes: CanvasNode[] = subgraph.nodes.map((node: GraphNode) => {
    const isDecisionPath = decisionPathNodeIds.has(node.id);
    const color = isDecisionPath
      ? '#2563EB'
      : getNodeColor(node.kind, node.labels);

    const nameInfo = formatEntityDisplayName({
      id: node.id,
      kind: node.kind,
      displayLabel: node.display_label,
    });

    kindCounts[nameInfo.kindLabel] = (kindCounts[nameInfo.kindLabel] || 0) + 1;

    return {
      id: node.id,
      labels: node.labels || [],
      color,
      visible: true,
      caption: nameInfo.primary,
      size: isDecisionPath ? 13 : 10,
      data: {
        originalId: node.id,
        kind: node.kind,
        display_label: node.display_label,
        readableName: nameInfo.primary,
        shortId: nameInfo.shortId,
        status: node.status ?? null,
        source_kind: node.source_kind ?? null,
        evidence_ids: node.evidence_ids || [],
        observed_at: node.observed_at ?? null,
        is_decision_path: isDecisionPath,
      },
    };
  });

  let verifiedCount = 0;
  let candidateCount = 0;
  let decisionPathCount = 0;

  const links: CanvasLink[] = subgraph.edges.map((edge: GraphEdge) => {
    const isDecisionPath = decisionPathEdgeIds.has(edge.id);
    const isVerified = edge.verification_status === 'VERIFIED';
    const isCandidate = edge.verification_status === 'CANDIDATE';

    if (isVerified) verifiedCount++;
    if (isCandidate) candidateCount++;
    if (isDecisionPath) decisionPathCount++;

    return {
      id: edge.id,
      relationship: edge.type,
      readableRelationship: translateRelationshipType(edge.type),
      color: getLinkColor(edge.verification_status, isDecisionPath),
      source: edge.source,
      target: edge.target,
      visible: true,
      data: {
        originalId: edge.id,
        type: edge.type,
        verification_status: edge.verification_status,
        valid_from: edge.valid_from ?? null,
        valid_to: edge.valid_to ?? null,
        observed_at: edge.observed_at ?? null,
        source_evidence_ids: edge.source_evidence_ids || [],
        is_decision_path: isDecisionPath,
      },
    };
  });

  // Build grounded "What this graph shows" narrative
  const kindSummary = Object.entries(kindCounts)
    .map(([kind, count]) => `${count} ${kind.toLowerCase()}${count > 1 ? 's' : ''}`)
    .join(', ');

  let whatThisGraphShows = `This view displays ${nodes.length} connected entities${kindSummary ? ` (${kindSummary})` : ''} and ${links.length} infrastructure relationships in FalkorDB.`;
  if (verifiedCount > 0 || candidateCount > 0) {
    whatThisGraphShows += ` ${verifiedCount} connection${verifiedCount !== 1 ? 's are' : ' is'} verified by municipal engineering records, and ${candidateCount} connection${candidateCount !== 1 ? 's remain' : ' remains'} candidate hypotheses.`;
  }
  if (decisionPathCount > 0) {
    whatThisGraphShows += ` ${decisionPathCount} relationship${decisionPathCount !== 1 ? 's are' : ' is'} highlighted as active decision paths influencing agent actions.`;
  }

  const stats: GraphDisplayStats = {
    totalNodes: nodes.length,
    totalEdges: links.length,
    verifiedEdges: verifiedCount,
    candidateEdges: candidateCount,
    decisionPathEdges: decisionPathCount,
    truncated: Boolean(subgraph.truncated),
    searchLimited: Boolean(subgraph.search_limited),
    graphRevision: subgraph.graph_revision,
    asOf: subgraph.as_of,
    reservations: subgraph.reservations || [],
    whatThisGraphShows,
  };

  return {
    data: { nodes, links },
    stats,
  };
}

export function extractDecisionTraces(
  tracePage: AgentTracePage,
  subgraph?: GraphSubgraphDTO | null,
): DecisionTraceItem[] {
  if (!tracePage || !tracePage.items || !Array.isArray(tracePage.items)) {
    return [];
  }

  const pathMap = new Map<string, DecisionPath>();
  if (subgraph?.decision_paths) {
    for (const dp of subgraph.decision_paths) {
      pathMap.set(dp.id, dp);
    }
  }

  return tracePage.items.map((event: AgentTraceEvent) => {
    let question = event.rationale_summary || '';
    if (!question) {
      if (event.tool_name) {
        question = `Establish connected facts using MCP tool '${event.tool_name}'.`;
      } else {
        question = `Establish state transition for role ${event.agent_role}.`;
      }
    }

    const nodeIds: string[] = [];
    const edgeIds: string[] = [];
    const evidenceIds: string[] = [...(event.evidence_ids || [])];

    if (event.graph_path_ids && Array.isArray(event.graph_path_ids)) {
      for (const pId of event.graph_path_ids) {
        const found = pathMap.get(pId);
        if (found) {
          nodeIds.push(...found.node_ids);
          edgeIds.push(...found.edge_ids);
          evidenceIds.push(...found.evidence_ids);
        }
      }
    }

    let evidenceSummary = '';
    if (nodeIds.length > 0 || edgeIds.length > 0) {
      evidenceSummary = `FalkorDB returned ${nodeIds.length} node(s) and ${edgeIds.length} relationship(s) matching graph traversal.`;
    } else if (evidenceIds.length > 0) {
      evidenceSummary = `Attributed ${evidenceIds.length} evidence citation(s) from case record.`;
    } else if (event.validated_output) {
      evidenceSummary = `Tool execution output validated against contract schemas.`;
    } else {
      evidenceSummary = `No direct graph path entities recorded for this step.`;
    }

    const action = event.tool_name ? `Execute ${event.tool_name}` : event.kind;
    const rationale = event.rationale_summary || 'No rationale recorded by agent.';

    let influenceCategory: 'MODEL_SELECTED_PATH' | 'CONTEXTUAL_GRAPH_QUERY' | 'UNESTABLISHED_INFLUENCE' = 'UNESTABLISHED_INFLUENCE';
    let influenceExplanation = 'Graph query executed as contextual background; no causal influence trace established for this step.';

    if (event.graph_path_ids && event.graph_path_ids.length > 0) {
      influenceCategory = 'MODEL_SELECTED_PATH';
      influenceExplanation = `Decision explicitly bound to FalkorDB path(s): ${event.graph_path_ids.join(', ')}.`;
    } else if (event.tool_name && event.tool_name.startsWith('civicly::') && event.status === 'SUCCESS') {
      influenceCategory = 'CONTEXTUAL_GRAPH_QUERY';
      influenceExplanation = 'Contextual graph read retrieved knowledge from FalkorDB; agent reasoned over returned evidence without recording an isolated decision path.';
    }

    return {
      eventId: event.event_id,
      timestamp: event.timestamp,
      agentRole: event.agent_role,
      kind: event.kind,
      toolName: event.tool_name ?? null,
      status: event.status,
      questionAsked: question,
      graphEvidence: {
        nodeIds: Array.from(new Set(nodeIds)),
        edgeIds: Array.from(new Set(edgeIds)),
        evidenceIds: Array.from(new Set(evidenceIds)),
        summary: evidenceSummary,
      },
      recordedDecision: {
        action,
        rationaleSummary: rationale,
        decisionId: event.decision_id ?? null,
        parentExecutionId: event.parent_execution_id ?? null,
      },
      influenceCategory,
      influenceExplanation,
    };
  });
}
