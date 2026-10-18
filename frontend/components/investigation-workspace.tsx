'use client';

import { useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Icon } from './icons';
import { Unavailable } from './unavailable';
import { useDemo } from './demo-connection';
import { useRead } from './use-read';
import { ReadMessage } from './read-state';
import { CaseDirectory } from './case-directory';
import { FalkorDBCanvasView } from './falkordb-canvas-view';
import { DecisionTracePanel } from './decision-trace-panel';
import { HypothesesPanel } from './hypotheses-panel';
import { EvidenceDetailModal } from './evidence-detail-modal';
import { useEventStream } from './use-event-stream';
import { LiveStreamPanel } from './live-stream-panel';
import { PlanApprovalPanel } from './plan-approval-panel';
import { WorkOrdersPanel } from './work-orders-panel';
import { MonitoringMemoryPanel } from './monitoring-memory-panel';
import { ScenarioJourneyGuide } from './scenario-journey-guide';
import { RoleGovernanceModal } from './role-governance-modal';
import type {
  GraphSubgraphDTO,
  AgentTracePage,
  HypothesisPage,
  PlanDTO,
  WorkOrderDTO,
  MonitoringDTO,
  ProcedureDTO,
  CaseMemoryDTO,
  OutcomeDTO,
} from '../lib/generated/models';
import {
  parseIssue,
  issueName,
  displayStatus,
  displayTime,
  loadSelectedCase,
} from '../lib/read/cases';
import {
  translateStatus,
  translateRole,
  translateActionType,
  formatEntityDisplayName,
} from '../lib/read/display';
import { TechnicalDetails, CopyableIdentifier } from './technical-details';

const stages = [
  'Report',
  'Investigation',
  'Evidence',
  'Plan & approval',
  'Work',
  'Monitoring & memory',
];

const stageDescriptions = [
  ['Reports & recurrence', 'Original reports, incident grouping and prior occurrences.'],
  ['Agent activity & reasoning', 'Recorded tool choices, graph queries and 3-part decision rationales.'],
  ['Hypotheses & evidence', 'Compare supporting evidence, contradictions and missing information for each hypothesis.'],
  ['Plan & approval', 'Inspect task dependencies, responsible departments and the exact plan version requiring approval.'],
  ['Work & inspections', 'Follow authorized work orders, inspection reports, progress and blockers.'],
  ['Outcomes & case memory', 'Review independent monitoring, recurrence, past repairs and sourced procedures. Work completion alone does not establish resolution.'],
];

const issueOptions = [
  ['', 'All issue categories'],
  ['WATERLOGGING', 'Waterlogging'],
  ['ROAD_DAMAGE', 'Road damage'],
  ['WASTE_ACCUMULATION', 'Waste accumulation'],
];

export function InvestigationWorkspace() {
  const demo = useDemo();
  const searchParams = useSearchParams();
  const router = useRouter();

  const [stage, setStage] = useState(1);
  const [selectedDecisionPathId, setSelectedDecisionPathId] = useState<string | null>(null);
  const [inspectedEvidenceId, setInspectedEvidenceId] = useState<string | null>(null);
  const [isJourneysOpen, setIsJourneysOpen] = useState(false);
  const [isRolesOpen, setIsRolesOpen] = useState(false);
  const [isGraphExpanded, setIsGraphExpanded] = useState(false);

  const issueParam = parseIssue(searchParams.get('issue'));
  const investigationParam = searchParams.get('investigation') ?? undefined;
  const incidentParam = searchParams.get('incident') ?? undefined;

  const hasSelection = Boolean(investigationParam || incidentParam);

  const selectedCase = useRead(
    `selected-case:${investigationParam ?? ''}:${incidentParam ?? ''}:${issueParam ?? ''}`,
    async (signal) =>
      loadSelectedCase(
        demo.connection.client,
        {
          investigation: investigationParam,
          incident: incidentParam,
          issue: issueParam,
        },
        signal,
      ),
    hasSelection,
  );

  const investigation = selectedCase.data?.investigation;
  const incidents = selectedCase.data?.incidents ?? [];
  const primaryIncident = incidents[0];
  const investigationId = investigation?.id;

  // Load FalkorDB Subgraph for selected investigation
  const graphRead = useRead<GraphSubgraphDTO | null>(
    `investigation-graph:${investigationId ?? ''}`,
    async (signal) => {
      if (!investigationId) return null;
      const res = await demo.connection.client.request(
        'GET /api/v1/investigations/{id}/graph',
        {
          params: { id: investigationId },
          query: { include_candidates: true },
          signal,
        },
      );
      return res.data;
    },
    Boolean(investigationId),
  );

  // Load Agent Trace for selected investigation
  const traceRead = useRead<AgentTracePage | null>(
    `investigation-trace:${investigationId ?? ''}`,
    async (signal) => {
      if (!investigationId) return null;
      const res = await demo.connection.client.request(
        'GET /api/v1/investigations/{id}/trace',
        {
          params: { id: investigationId },
          signal,
        },
      );
      return res.data;
    },
    Boolean(investigationId),
  );

  // Load Competing Hypotheses for selected investigation
  const hypothesesRead = useRead<HypothesisPage | null>(
    `investigation-hypotheses:${investigationId ?? ''}`,
    async (signal) => {
      if (!investigationId) return null;
      const res = await demo.connection.client.request(
        'GET /api/v1/investigations/{id}/hypotheses',
        {
          params: { id: investigationId },
          signal,
        },
      );
      return res.data;
    },
    Boolean(investigationId),
  );

  // Load Resolution Plans for selected investigation
  const plansRead = useRead<{ items: PlanDTO[] } | null>(
    `investigation-plans:${investigationId ?? ''}`,
    async (signal) => {
      if (!investigationId) return null;
      const res = await demo.connection.client.request(
        'GET /api/v1/investigations/{id}/plans',
        {
          params: { id: investigationId },
          signal,
        },
      );
      return res.data;
    },
    Boolean(investigationId),
  );

  // Load Work Orders
  const workOrdersRead = useRead<{ items: WorkOrderDTO[] } | null>(
    `investigation-work-orders:${investigationId ?? ''}`,
    async (signal) => {
      if (!investigationId) return null;
      const res = await demo.connection.client.request(
        'GET /api/v1/work-orders',
        {
          query: { limit: 50 },
          signal,
        },
      );
      return res.data;
    },
    Boolean(investigationId),
  );

  // Load Cluster Monitoring records
  const monitoringRead = useRead<{ items: MonitoringDTO[] } | null>(
    `monitoring-records:${investigationId ?? ''}`,
    async (signal) => {
      const res = await demo.connection.client.request(
        'GET /api/v1/monitoring',
        {
          query: { limit: 50 },
          signal,
        },
      );
      return res.data;
    },
    Boolean(investigationId),
  );

  // Load Sourced Procedures (handles 409 DEPENDENCY_BLOCKED when memory service is pending)
  const proceduresRead = useRead<{ items: ProcedureDTO[] } | null>(
    `procedures-library`,
    async (signal) => {
      try {
        const res = await demo.connection.client.request(
          'GET /api/v1/procedures',
          {
            query: { limit: 50 },
            signal,
          },
        );
        return res.data;
      } catch (e: any) {
        // Memory dependency may not be provisioned in all environments
        return null;
      }
    },
    Boolean(investigationId),
  );

  // Load Case Memory (returns null if case is not yet closed / 409 DEPENDENCY_BLOCKED)
  const memoryRead = useRead<{ items: CaseMemoryDTO[] } | null>(
    `case-memory:${investigationId ?? ''}`,
    async (signal) => {
      if (!investigationId) return null;
      try {
        const res = await demo.connection.client.request(
          'GET /api/v1/cases/{id}/memory',
          {
            params: { id: investigationId },
            signal,
          },
        );
        return res.data;
      } catch (e: any) {
        // Expected when case outcomes are not yet closed
        return null;
      }
    },
    Boolean(investigationId),
  );

  // Load Problem Cluster Outcomes if cluster ID is known
  const clusterId = investigation?.problem_cluster_id;
  const outcomesRead = useRead<{ items: OutcomeDTO[] } | null>(
    `cluster-outcomes:${clusterId ?? ''}`,
    async (signal) => {
      if (!clusterId) return null;
      try {
        const res = await demo.connection.client.request(
          'GET /api/v1/problem-clusters/{id}/outcomes',
          {
            params: { id: clusterId },
            signal,
          },
        );
        return res.data;
      } catch (e: any) {
        return null;
      }
    },
    Boolean(clusterId),
  );

  const stream = useEventStream({
    token: demo.status === 'connected' ? demo.connection.getToken() : null,
    investigationId: investigationId,
    onRefetch: () => {
      selectedCase.refresh();
      graphRead.refresh();
      traceRead.refresh();
      hypothesesRead.refresh();
      plansRead.refresh();
      workOrdersRead.refresh();
      monitoringRead.refresh();
      proceduresRead.refresh();
      memoryRead.refresh();
      outcomesRead.refresh();
    },
  });


  function selectIssue(value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) params.set('issue', value);
    else params.delete('issue');
    params.delete('cursor');
    const query = params.toString() ? '?' + params.toString() : '';
    router.push('/investigations' + query, { scroll: false });
  }

  function clearSelection() {
    const params = new URLSearchParams(searchParams.toString());
    params.delete('investigation');
    params.delete('incident');
    const query = params.toString() ? '?' + params.toString() : '';
    setSelectedDecisionPathId(null);
    setInspectedEvidenceId(null);
    router.push('/investigations' + query, { scroll: false });
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">FROM REPORT TO RESOLUTION</p>
          <h1>Investigations Studio</h1>
          <p>Follow the case. Understand the connected graph evidence behind every next step.</p>
        </div>
        {hasSelection ? (
          <div className="selected-case-badge">
            <span className="live-dot" />
            <span>
              {investigation ? `Investigation ${investigation.id}` : `Incident ${incidentParam}`}
            </span>
            <button
              type="button"
              className="text-button"
              onClick={clearSelection}
              title="Clear selection"
            >
              Clear
            </button>
          </div>
        ) : (
          <span className="outline-badge">
            <span /> No case selected
          </span>
        )}
      </div>

      <div className="workspace-controls">
        <label htmlFor="issue-filter">
          Issue category
          <select
            id="issue-filter"
            value={issueParam ?? ''}
            onChange={(e) => selectIssue(e.target.value)}
          >
            {issueOptions.map(([val, label]) => (
              <option value={val} key={val}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <button
            type="button"
            className="topbar-action-pill"
            onClick={() => setIsJourneysOpen(true)}
            aria-haspopup="dialog"
            title="Browse all 12 pre-seeded demonstration scenarios"
          >
            <Icon name="layers" size={14} /> Scenarios (S01–S12)
          </button>
          <button
            type="button"
            className="topbar-action-pill"
            onClick={() => setIsRolesOpen(true)}
            aria-haspopup="dialog"
            title="Inspect municipal operator roles and RBAC governance"
          >
            <Icon name="check" size={14} /> Roles &amp; RBAC
          </button>
        </div>
        <p>
          <Icon name="shield" size={16} />
          {demo.status === 'connected' ? (
            hasSelection ? (
              <span>Case loaded &bull; Simulated municipal district</span>
            ) : (
              <span>Demo connected &bull; Select a case below to begin</span>
            )
          ) : (
            demo.message
          )}
        </p>
      </div>

      {hasSelection && selectedCase.status === 'loading' && (
        <div className="case-notice">
          <Icon name="clock" size={18} />
          <span>Loading selected case details…</span>
        </div>
      )}

      {hasSelection && selectedCase.status === 'error' && (
        <div style={{ marginBottom: 20 }}>
          <ReadMessage state={selectedCase} retry={selectedCase.refresh} />
        </div>
      )}

      {hasSelection && selectedCase.status === 'ready' && (
        <div className="selected-case-card">
          <div className="selected-case-header">
            <div className="case-header-main">
              <div className="case-pills">
                <span className="case-kind-tag">
                  {investigation ? 'REGISTERED INVESTIGATION' : 'REPORTED INCIDENT'}
                </span>
                {primaryIncident && (
                  <span className="case-issue-tag">
                    {issueName(primaryIncident.issue_type)}
                  </span>
                )}
                <span className="status-tag">
                  {translateStatus(investigation?.status ?? primaryIncident?.status)}
                </span>
              </div>
              <h2 className="selected-case-title">
                {investigation
                  ? `${issueName(primaryIncident?.issue_type || 'Civic Defect')} Investigation`
                  : `Reported Incident: ${issueName(primaryIncident?.issue_type || 'Civic Defect')}`}
              </h2>
              <p className="selected-case-subtitle">
                {investigation ? (
                  <>
                    Case reference: <strong>{formatEntityDisplayName({ id: investigation.id }).shortId}</strong> &bull; Status: {translateStatus(investigation.status)} &bull; {investigation.problem_cluster_id ? `Problem cluster ${investigation.problem_cluster_id}` : 'Single defect context'}
                  </>
                ) : (
                  <>
                    Incident reference: <strong>{formatEntityDisplayName({ id: primaryIncident?.id || '' }).shortId}</strong> &bull; Started: {displayTime(primaryIncident?.started_at || '')}
                  </>
                )}
              </p>
            </div>
            <button
              type="button"
              className="button secondary small"
              onClick={clearSelection}
            >
              Change selection
            </button>
          </div>

          <div className="selected-case-meta">
            {investigation && (
              <>
                {investigation.problem_cluster_id && (
                  <span>
                    Problem cluster: <strong>{investigation.problem_cluster_id}</strong>
                  </span>
                )}
                {investigation.current_agent_role && (
                  <span>
                    Active agent role: <strong>{translateRole(investigation.current_agent_role)}</strong>
                  </span>
                )}
                {investigation.next_action && (
                  <span>
                    Next required action: <strong>{translateActionType(investigation.next_action)}</strong>
                  </span>
                )}
                {investigation.graph_revision !== undefined && (
                  <span>
                    Graph revision: <strong>{investigation.graph_revision}</strong>
                  </span>
                )}
              </>
            )}
            {primaryIncident && !investigation && (
              <>
                <span>
                  Location: <strong>{primaryIncident.location_id ?? 'Civic location not specified'}</strong>
                </span>
                <span>
                  Started: <strong>{displayTime(primaryIncident.started_at)}</strong>
                </span>
                {primaryIncident.cluster_id && (
                  <span>
                    Cluster: <strong>{primaryIncident.cluster_id}</strong>
                  </span>
                )}
              </>
            )}
          </div>

          {/* Technical Details for Selected Case */}
          <div style={{ marginTop: '0.85rem' }}>
            <TechnicalDetails
              title="Technical case identifiers & references"
              items={[
                ...(investigation ? [
                  { label: 'Investigation ID', value: <code>{investigation.id}</code>, rawString: investigation.id },
                  { label: 'Raw Investigation Status', value: <code>{investigation.status}</code>, rawString: investigation.status },
                  { label: 'Graph Revision', value: <span>{investigation.graph_revision}</span>, rawString: String(investigation.graph_revision) },
                  ...(investigation.problem_cluster_id ? [{ label: 'Problem Cluster ID', value: <code>{investigation.problem_cluster_id}</code>, rawString: investigation.problem_cluster_id }] : []),
                ] : []),
                ...(primaryIncident ? [
                  { label: 'Primary Incident ID', value: <code>{primaryIncident.id}</code>, rawString: primaryIncident.id },
                  { label: 'Location Identifier', value: <code>{primaryIncident.location_id || 'null'}</code>, rawString: primaryIncident.location_id || undefined },
                ] : []),
              ]}
            />
          </div>

          {!investigation && primaryIncident && (
            <div className="absence-notice">
              <Icon name="help" size={16} />
              <span>
                No exposed investigation link is registered for this incident in the demo catalog.
                Direct investigation listing is not supported by the current API; this is not proof that no investigation exists.
              </span>
            </div>
          )}
        </div>
      )}

      {!hasSelection && (
        <div className="case-notice">
          <Icon name="help" size={18} />
          <span>
            <strong>No case selected.</strong> Choose a registered demo investigation or reported incident from the directory below.
            Selecting a workspace section does not advance an investigation.
          </span>
        </div>
      )}

      {/* Lifecycle Navigation Tabs */}
      <nav className="stage-nav" aria-label="Investigation sections">
        {stages.map((label, index) => (
          <button
            key={label}
            type="button"
            className={stage === index ? 'selected' : ''}
            onClick={() => setStage(index)}
            aria-current={stage === index ? 'step' : undefined}
          >
            <span className="stage-number">{String(index + 1).padStart(2, '0')}</span>
            {label}
          </button>
        ))}
      </nav>

      {/* Investigation Grid: Left Workspace Panel + Right Graph Panel */}
      <div className={`investigation-grid ${isGraphExpanded ? 'graph-expanded' : ''}`} id="case-workspace">
        {/* Left Case Workspace Panel */}
        <section className="panel case-panel" aria-live="polite">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">CASE WORKSPACE &bull; STAGE {stage + 1}</p>
              <h2>{stageDescriptions[stage][0]}</h2>
            </div>
            <Icon name={stage === 1 ? 'search' : 'file'} />
          </div>

          {/* Stage 0: Report & Recurrence */}
          {stage === 0 && (
            <div className="stage-content">
              {hasSelection && selectedCase.data ? (
                <div className="stage-report-details">
                  <h3>Linked incident reports ({incidents.length})</h3>
                  <div className="incident-cards">
                    {incidents.map((inc) => (
                      <article className="incident-card" key={inc.id}>
                        <div className="incident-card-top">
                          <strong>{inc.id}</strong>
                          <span className="status-tag">{displayStatus(inc.status)}</span>
                        </div>
                        <div className="incident-card-meta">
                          <p>
                            <strong>Issue:</strong> {issueName(inc.issue_type)}{' '}
                            {inc.subtype ? `(${inc.subtype})` : ''}
                          </p>
                          <p>
                            <strong>Location:</strong> {inc.location_id ?? 'Not recorded'}
                          </p>
                          <p>
                            <strong>Started:</strong> {displayTime(inc.started_at)}
                          </p>
                          {inc.ended_at && (
                            <p>
                              <strong>Ended:</strong> {displayTime(inc.ended_at)}
                            </p>
                          )}
                          {inc.cluster_id && (
                            <p>
                              <strong>Cluster:</strong> {inc.cluster_id}
                            </p>
                          )}
                          {inc.complaint_ids?.length ? (
                            <p>
                              <strong>Complaints:</strong> {inc.complaint_ids.join(', ')}
                            </p>
                          ) : null}
                        </div>
                      </article>
                    ))}
                  </div>

                  {investigation?.historical_incident_ids?.length ? (
                    <div className="historical-incidents">
                      <h4>Historical recurrence context</h4>
                      <p>Earlier incidents linked to this problem pattern:</p>
                      <ul>
                        {investigation.historical_incident_ids.map((id) => (
                          <li key={id}>{id}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                </div>
              ) : (
                <Unavailable title="Select a case to inspect reports" icon="file">
                  Original reports, incident grouping and prior occurrences will appear here when a case is selected.
                </Unavailable>
              )}
            </div>
          )}

          {/* Stage 1: Investigation & Agent Decision Trace */}
          {stage === 1 && (
            <div className="stage-content">
              {hasSelection && investigation ? (
                <div className="stage-investigation-details">
                  <div className="investigation-status-block">
                    <div>
                      <small>Investigation Status</small>
                      <strong>{displayStatus(investigation.status)}</strong>
                    </div>
                    {investigation.runtime_status && (
                      <div>
                        <small>Runtime Status</small>
                        <strong>{investigation.runtime_status}</strong>
                      </div>
                    )}
                    <div>
                      <small>Active Hypotheses</small>
                      <strong>{investigation.active_hypothesis_ids?.length ?? 0}</strong>
                    </div>
                    <div>
                      <small>Pending Inspections</small>
                      <strong>{investigation.pending_inspection_ids?.length ?? 0}</strong>
                    </div>
                  </div>

                  {investigation.next_action && (
                    <div className="next-action-card">
                      <Icon name="arrow" size={16} />
                      <div>
                        <strong>Next required action</strong>
                        <p>{investigation.next_action}</p>
                      </div>
                    </div>
                  )}

                  {/* Scoped Live Event Stream for this Investigation */}
                  <div style={{ marginTop: '1.25rem' }}>
                    <LiveStreamPanel
                      status={stream.status}
                      lastEventId={stream.lastEventId}
                      events={stream.events}
                      onReconnect={stream.reconnect}
                      onClear={stream.clearEvents}
                      title={`Investigation Event Stream (${investigation.id})`}
                      defaultExpanded={false}
                    />
                  </div>

                  {/* 3-Part Traceability Component */}
                  <h3 style={{ marginTop: '1.5rem', marginBottom: '0.75rem' }}>
                    Agent Decision Traceability (Question &rarr; FalkorDB &rarr; Decision)
                  </h3>


                  {traceRead.status === 'loading' && (
                    <p className="muted">Loading agent decision traces...</p>
                  )}
                  {traceRead.status === 'error' && (
                    <ReadMessage state={traceRead} retry={traceRead.refresh} />
                  )}
                  {traceRead.status === 'ready' && (
                    <DecisionTracePanel
                      tracePage={traceRead.data}
                      subgraph={graphRead.data}
                      onHighlightDecisionPath={setSelectedDecisionPathId}
                      selectedDecisionPathId={selectedDecisionPathId}
                      onSelectEvidenceId={setInspectedEvidenceId}
                    />
                  )}
                </div>
              ) : (
                <Unavailable title="Select an investigation" icon="search">
                  Recorded tool choices, graph queries and decision rationales will appear here when an investigation is selected.
                </Unavailable>
              )}
            </div>
          )}

          {/* Stage 2: Evidence & Hypotheses */}
          {stage === 2 && (
            <div className="stage-content">
              {hasSelection && investigation ? (
                <div className="stage-evidence-details">
                  {hypothesesRead.status === 'loading' && (
                    <p className="muted">Loading competing hypotheses...</p>
                  )}
                  {hypothesesRead.status === 'error' && (
                    <ReadMessage state={hypothesesRead} retry={hypothesesRead.refresh} />
                  )}
                  {hypothesesRead.status === 'ready' && (
                    <HypothesesPanel
                      hypothesisPage={hypothesesRead.data}
                      plan={plansRead.data?.items?.[0] || null}
                      onSelectEvidenceId={setInspectedEvidenceId}
                    />
                  )}
                </div>
              ) : (
                <Unavailable title="Select an investigation to view hypotheses" icon="shield">
                  Competing hypotheses, supporting and contradicting evidence, and missing information will appear here.
                </Unavailable>
              )}
            </div>
          )}

          {/* Stage 3: Plan & Approval */}
          {stage === 3 && (
            <div className="stage-content">
              {hasSelection && investigation ? (
                <div className="stage-plan-details">
                  {plansRead.status === 'loading' && (
                    <p className="muted">Loading remediation plan and task DAG...</p>
                  )}
                  {plansRead.status === 'error' && (
                    <ReadMessage state={plansRead} retry={plansRead.refresh} />
                  )}
                  {plansRead.status === 'ready' && (
                    <PlanApprovalPanel
                      plan={plansRead.data?.items?.[0] || null}
                      investigationId={investigation.id}
                      onRefetch={plansRead.refresh}
                    />
                  )}
                </div>
              ) : (
                <Unavailable title="Select an investigation" icon="file">
                  Inspect task dependencies, responsible departments and the exact plan version requiring approval.
                </Unavailable>
              )}
            </div>
          )}

          {/* Stage 4: Work & Inspections */}
          {stage === 4 && (
            <div className="stage-content">
              {hasSelection && investigation ? (
                <div className="stage-work-details">
                  {workOrdersRead.status === 'loading' && (
                    <p className="muted">Loading dispatched work orders and inspections...</p>
                  )}
                  {workOrdersRead.status === 'error' && (
                    <ReadMessage state={workOrdersRead} retry={workOrdersRead.refresh} />
                  )}
                  {workOrdersRead.status === 'ready' && (
                    <WorkOrdersPanel
                      investigationId={investigation.id}
                      planId={investigation.current_plan_id || plansRead.data?.items?.[0]?.plan_id}
                      pendingInspectionIds={investigation.pending_inspection_ids}
                      workOrders={workOrdersRead.data?.items || []}
                      onSelectEvidenceId={setInspectedEvidenceId}
                      onRefetch={workOrdersRead.refresh}
                    />
                  )}
                </div>
              ) : (
                <Unavailable title="Select an investigation" icon="clock">
                  Follow authorized work orders, inspection reports, progress and blockers.
                </Unavailable>
              )}
            </div>
          )}

          {/* Stage 5: Outcomes & Case Memory */}
          {stage === 5 && (
            <div className="stage-content">
              {hasSelection && investigation ? (
                <div className="stage-monitoring-details">
                  <MonitoringMemoryPanel
                    investigationId={investigation.id}
                    problemClusterId={investigation.problem_cluster_id}
                    issueType={primaryIncident?.issue_type || null}
                    historicalIncidentIds={investigation.historical_incident_ids || []}
                    monitoringList={monitoringRead.data?.items || []}
                    procedures={proceduresRead.data?.items || []}
                    memory={memoryRead.data?.items?.[0] || null}
                    outcomes={outcomesRead.data?.items || []}
                    onSelectEvidenceId={setInspectedEvidenceId}
                    onRefetch={() => {
                      monitoringRead.refresh();
                      proceduresRead.refresh();
                      memoryRead.refresh();
                      outcomesRead.refresh();
                    }}
                  />
                </div>
              ) : (
                <Unavailable title="Select an investigation" icon="shield">
                  Review independent monitoring, recurrence, past repairs and sourced procedures. Work completion alone does not establish resolution.
                </Unavailable>
              )}
            </div>
          )}

          <div className="case-note">
            <Icon name="shield" size={17} />
            <span>
              Reports, hypotheses and verified findings remain distinct. Every finding needs attributed evidence.
            </span>
          </div>
        </section>

        {/* Right Graph Evidence Panel with Official FalkorDB Canvas */}
        <section className="panel graph-panel" id="graph-evidence">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">FALKORDB &bull; GRAPH EVIDENCE</p>
              <h2>The connections behind the decision</h2>
            </div>
            <span className="graph-chip">
              <Icon name="graph" size={15} /> Official Canvas
            </span>
          </div>

          <div className="graph-surface">
            {investigationId ? (
              <>
                {graphRead.data ? (
                  <FalkorDBCanvasView
                    subgraph={graphRead.data}
                    selectedDecisionPathId={selectedDecisionPathId}
                    onSelectEvidenceId={setInspectedEvidenceId}
                    isExpanded={isGraphExpanded}
                    onToggleExpand={() => setIsGraphExpanded(!isGraphExpanded)}
                  />
                ) : graphRead.status === 'loading' ? (
                  <div className="graph-loading-box">
                    <p>Loading FalkorDB subgraph for investigation {investigationId}...</p>
                  </div>
                ) : graphRead.status === 'error' ? (
                  <div style={{ padding: '1rem' }}>
                    <ReadMessage state={graphRead} retry={graphRead.refresh} />
                  </div>
                ) : null}
              </>
            ) : primaryIncident ? (
              <Unavailable title="Unlinked Incident Record" icon="graph">
                This incident has not yet been registered in an active scenario investigation.
                Bounded graph projections are compiled through investigation entities.
              </Unavailable>
            ) : (
              <Unavailable title="Select a case to inspect graph evidence" icon="graph">
                Select a case and a recorded decision to inspect its actual graph paths, source evidence and relationship status.
              </Unavailable>
            )}
          </div>

          <details className="graph-explanation" style={{ marginTop: '1rem' }}>
            <summary>How does FalkorDB support this investigation?</summary>
            <p>
              FalkorDB stores and retrieves connected infrastructure assets, incidents, evidence,
              and historical maintenance records using OpenCypher and GraphRAG. The agent queries
              FalkorDB through runtime MCP tools to discover connected facts, formulate competing
              hypotheses, and establish causal paths.
            </p>
            <p>
              <strong>Truthful Traceability:</strong> Highlighted paths must come from recorded
              evidence. A relationship or nearby location alone does not prove a cause; when
              influence is not established by the trace, it remains explicitly unestablished.
            </p>
          </details>
        </section>
      </div>

      {/* Evidence Detail Modal */}
      <EvidenceDetailModal
        evidenceId={inspectedEvidenceId}
        onClose={() => setInspectedEvidenceId(null)}
      />

      {/* Bottom Case Directory */}
      <section className="panel directory-panel" style={{ marginTop: 24 }}>
        <div className="panel-heading">
          <div>
            <p className="eyebrow">EXPLORE CASES</p>
            <h2>Case directory &amp; reported incidents</h2>
            <p>Select a registered demo investigation or browse accessible incidents.</p>
          </div>
          <Icon name="search" />
        </div>
        <div style={{ padding: '0 22px 22px' }}>
          <CaseDirectory issue={issueParam} />
        </div>
      </section>

      {/* Scenario Journeys Modal */}
      <ScenarioJourneyGuide
        isOpen={isJourneysOpen}
        onClose={() => setIsJourneysOpen(false)}
      />

      {/* Municipal Role Governance Modal */}
      <RoleGovernanceModal
        isOpen={isRolesOpen}
        onClose={() => setIsRolesOpen(false)}
      />
    </>
  );
}
