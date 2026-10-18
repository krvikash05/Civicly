import test from 'node:test';
import assert from 'node:assert/strict';
import {
  mapGraphSubgraphToCanvas,
  extractDecisionTraces,
  getNodeColor,
  getLinkColor,
  NODE_KIND_COLORS,
  EDGE_STATUS_COLORS,
} from '../lib/read/graph.ts';
import type {
  GraphSubgraphDTO,
  AgentTracePage,
  HypothesisPage,
  EvidenceDTO,
} from '../lib/generated/models.ts';
import { validSchema } from '../lib/api/validation.ts';

test('getNodeColor and getLinkColor return expected colors', () => {
  assert.equal(getNodeColor('Incident'), NODE_KIND_COLORS.Incident);
  assert.equal(getNodeColor('InfrastructureAsset'), NODE_KIND_COLORS.InfrastructureAsset);
  assert.equal(getNodeColor('Observation'), NODE_KIND_COLORS.Observation);
  assert.equal(getNodeColor('Evidence'), NODE_KIND_COLORS.Evidence);
  assert.equal(getNodeColor('Hypothesis'), NODE_KIND_COLORS.Hypothesis);
  assert.equal(getNodeColor('UnknownKind'), NODE_KIND_COLORS.Default);

  assert.equal(getLinkColor('VERIFIED', false), EDGE_STATUS_COLORS.verified);
  assert.equal(getLinkColor('CANDIDATE', false), EDGE_STATUS_COLORS.candidate);
  assert.equal(getLinkColor('UNKNOWN', false), EDGE_STATUS_COLORS.default);
  assert.equal(getLinkColor('VERIFIED', true), EDGE_STATUS_COLORS.decisionPath);
});

test('mapGraphSubgraphToCanvas maps nodes, edges, verified/candidate counts and decision paths', () => {
  const subgraph: GraphSubgraphDTO = {
    graph_revision: 42,
    as_of: '2026-10-18T12:00:00Z',
    truncated: false,
    reservations: ['RES-01'],
    decision_path_ids: ['PATH-01'],
    decision_paths: [
      {
        id: 'PATH-01',
        node_ids: ['NODE-01', 'NODE-02'],
        edge_ids: ['EDGE-01'],
        evidence_ids: ['EVID-01'],
        execution_id: 'EXEC-01',
      },
    ],
    nodes: [
      {
        id: 'NODE-01',
        labels: ['Incident'],
        kind: 'Incident',
        display_label: 'Waterlogging Incident #1',
        status: 'ACTIVE',
        source_kind: 'COMPLAINT',
        evidence_ids: ['EVID-01'],
        observed_at: '2026-10-18T10:00:00Z',
      },
      {
        id: 'NODE-02',
        labels: ['InfrastructureAsset'],
        kind: 'InfrastructureAsset',
        display_label: 'Storm Drain D-12',
        status: 'OPERATIONAL',
        source_kind: 'REGISTRY',
        evidence_ids: [],
        observed_at: null,
      },
      {
        id: 'NODE-03',
        labels: ['Observation'],
        kind: 'Observation',
        display_label: 'Rainfall Gauge R-01',
        status: 'RECORDED',
        source_kind: 'SENSOR',
        evidence_ids: [],
        observed_at: '2026-10-18T09:30:00Z',
      },
    ],
    edges: [
      {
        id: 'EDGE-01',
        type: 'DRAINS_TO',
        source: 'NODE-01',
        target: 'NODE-02',
        valid_from: '2026-10-18T10:00:00Z',
        valid_to: null,
        observed_at: '2026-10-18T10:00:00Z',
        verification_status: 'VERIFIED',
        source_evidence_ids: ['EVID-01'],
      },
      {
        id: 'EDGE-02',
        type: 'NEARBY',
        source: 'NODE-02',
        target: 'NODE-03',
        valid_from: null,
        valid_to: null,
        observed_at: null,
        verification_status: 'CANDIDATE',
        source_evidence_ids: [],
      },
    ],
  };

  const { data, stats } = mapGraphSubgraphToCanvas(subgraph);

  // Check stats
  assert.equal(stats.totalNodes, 3);
  assert.equal(stats.totalEdges, 2);
  assert.equal(stats.verifiedEdges, 1);
  assert.equal(stats.candidateEdges, 1);
  assert.equal(stats.decisionPathEdges, 1);
  assert.equal(stats.graphRevision, 42);
  assert.equal(stats.truncated, false);

  // Check node mapping
  assert.equal(data.nodes.length, 3);
  const n1 = data.nodes.find((n) => n.id === 'NODE-01')!;
  assert.equal(n1.caption, 'Waterlogging Incident #1');
  assert.equal(n1.data.is_decision_path, true);
  assert.equal(n1.color, '#2563EB'); // highlighted blue because in decision path

  const n3 = data.nodes.find((n) => n.id === 'NODE-03')!;
  assert.equal(n3.data.is_decision_path, false);
  assert.equal(n3.color, NODE_KIND_COLORS.Observation);

  // Check edge mapping
  assert.equal(data.links.length, 2);
  const e1 = data.links.find((l) => l.id === 'EDGE-01')!;
  assert.equal(e1.relationship, 'DRAINS_TO');
  assert.equal(e1.data.verification_status, 'VERIFIED');
  assert.equal(e1.data.is_decision_path, true);
  assert.equal(e1.color, EDGE_STATUS_COLORS.decisionPath);

  const e2 = data.links.find((l) => l.id === 'EDGE-02')!;
  assert.equal(e2.relationship, 'NEARBY');
  assert.equal(e2.data.verification_status, 'CANDIDATE');
  assert.equal(e2.data.is_decision_path, false);
  assert.equal(e2.color, EDGE_STATUS_COLORS.candidate);
});

test('extractDecisionTraces connects Question Asked -> Graph Evidence -> Recorded Decision', () => {
  const subgraph: GraphSubgraphDTO = {
    graph_revision: 10,
    as_of: '2026-10-18T12:00:00Z',
    truncated: false,
    decision_path_ids: ['PATH-WATER-01'],
    decision_paths: [
      {
        id: 'PATH-WATER-01',
        node_ids: ['INC-01', 'DRAIN-D12'],
        edge_ids: ['DRAINS_TO_01'],
        evidence_ids: ['EVID-DRAIN-01'],
        execution_id: 'EXEC-TRACE-01',
      },
    ],
    nodes: [],
    edges: [],
    reservations: [],
  };

  const tracePage: AgentTracePage = {
    checkpoint_graph_revision: 10,
    refresh_required: false,
    error_codes: [],
    total_count: 3,
    next_cursor: null,
    graph_revision: 10,
    as_of: '2026-10-18T12:00:00Z',
    phase: 'INVESTIGATING',
    pause_reason: null,
    recovery_required: false,
    current_agent_role: 'INVESTIGATOR',
    active_incident_ids: ['INC-01'],
    historical_incident_ids: [],
    limitations: [],
    items: [
      // 1. Model-selected path event
      {
        event_id: 'EVT-01',
        investigation_id: 'INV-01',
        timestamp: '2026-10-18T10:05:00Z',
        agent_role: 'INVESTIGATOR',
        kind: 'TOOL',
        tool_name: 'civicly::traverse_drainage_network',
        status: 'SUCCESS',
        rationale_summary: 'Identify upstream drainage network connected to incident location to test hydraulic blockage.',
        graph_path_ids: ['PATH-WATER-01'],
        graph_revision: 10,
        execution_mode: 'DETERMINISTIC',
        decision_id: 'DEC-01',
      },
      // 2. Contextual graph read without selected path
      {
        event_id: 'EVT-02',
        investigation_id: 'INV-01',
        timestamp: '2026-10-18T10:06:00Z',
        agent_role: 'INVESTIGATOR',
        kind: 'TOOL',
        tool_name: 'civicly::get_recent_maintenance_logs',
        status: 'SUCCESS',
        rationale_summary: 'Inspect prior cleaning history for target drain.',
        graph_path_ids: [],
        graph_revision: 10,
        execution_mode: 'DETERMINISTIC',
        decision_id: 'DEC-02',
      },
      // 3. State transition event without tool
      {
        event_id: 'EVT-03',
        investigation_id: 'INV-01',
        timestamp: '2026-10-18T10:07:00Z',
        agent_role: 'INVESTIGATOR',
        kind: 'DECISION',
        tool_name: null,
        status: 'SUCCESS',
        rationale_summary: 'Advance investigation to hypotheses formulation.',
        graph_path_ids: [],
        graph_revision: 10,
        execution_mode: 'DETERMINISTIC',
        decision_id: null,
      },
    ],
  };

  const traceItems = extractDecisionTraces(tracePage, subgraph);
  assert.equal(traceItems.length, 3);

  // Check 1: Model-Selected Path
  const t1 = traceItems[0];
  assert.equal(t1.eventId, 'EVT-01');
  assert.equal(t1.questionAsked, 'Identify upstream drainage network connected to incident location to test hydraulic blockage.');
  assert.equal(t1.influenceCategory, 'MODEL_SELECTED_PATH');
  assert.match(t1.influenceExplanation, /Decision explicitly bound to FalkorDB path/);
  assert.deepEqual(t1.graphEvidence.nodeIds, ['INC-01', 'DRAIN-D12']);
  assert.deepEqual(t1.graphEvidence.edgeIds, ['DRAINS_TO_01']);
  assert.deepEqual(t1.graphEvidence.evidenceIds, ['EVID-DRAIN-01']);
  assert.equal(t1.recordedDecision.action, 'Execute civicly::traverse_drainage_network');
  assert.equal(t1.recordedDecision.decisionId, 'DEC-01');

  // Check 2: Contextual Graph Query
  const t2 = traceItems[1];
  assert.equal(t2.eventId, 'EVT-02');
  assert.equal(t2.influenceCategory, 'CONTEXTUAL_GRAPH_QUERY');
  assert.match(t2.influenceExplanation, /Contextual graph read retrieved knowledge from FalkorDB/);
  assert.equal(t2.recordedDecision.action, 'Execute civicly::get_recent_maintenance_logs');

  // Check 3: Unestablished Influence
  const t3 = traceItems[2];
  assert.equal(t3.eventId, 'EVT-03');
  assert.equal(t3.influenceCategory, 'UNESTABLISHED_INFLUENCE');
  assert.equal(
    t3.influenceExplanation,
    'Graph query executed as contextual background; no causal influence trace established for this step.',
  );
  assert.equal(t3.recordedDecision.action, 'DECISION');
});

test('closed schema validation accepts valid GraphSubgraphDTO and rejects extra properties', () => {
  const validSubgraph: GraphSubgraphDTO = {
    graph_revision: 1,
    as_of: '2026-10-18T10:00:00Z',
    truncated: false,
    reservations: [],
    decision_path_ids: [],
    nodes: [],
    edges: [],
  };

  assert.equal(validSchema('GraphSubgraphDTO', validSubgraph), true);

  const invalidSubgraph = {
    ...validSubgraph,
    unsupported_invented_field: 'INVENTED',
  };
  assert.equal(validSchema('GraphSubgraphDTO', invalidSubgraph), false);
});

test('closed schema validation validates HypothesisPage and EvidenceDTO', () => {
  const validHypothesisPage: HypothesisPage = {
    total_count: 1,
    next_cursor: null,
    items: [
      {
        id: 'HYP-01',
        expected_hash: 'a'.repeat(64),
        statement: 'Culvert blockage caused backwater flooding.',
        cause_code: 'CULVERT_BLOCKAGE',
        status: 'SUPPORTED',
        current_assessment_id: 'ASSESS-01',
        assessment_history: [],
        supporting_evidence_ids: ['EVID-01'],
        contradicting_evidence_ids: [],
        missing_evidence: [],
        suspected_asset_ids: ['DRAIN-D12'],
      },
    ],
  };

  assert.equal(validSchema('HypothesisPage', validHypothesisPage), true);

  const validEvidence: EvidenceDTO = {
    id: 'EVID-01',
    expected_hash: 'b'.repeat(64),
    evidence_type: 'FIELD_INSPECTION',
    summary: 'Water utility field inspection attesting 90% silt accumulation.',
    source_kind: 'INSPECTION_REPORT',
    source_record_id: 'REC-01',
    reliability: 'VERIFIED',
    observed_at: '2026-10-18T09:00:00Z',
    recorded_at: '2026-10-18T09:15:00Z',
    document_id: 'DOC-FIELD-01',
    reviewed: true,
  };

  assert.equal(validSchema('EvidenceDTO', validEvidence), true);
});
