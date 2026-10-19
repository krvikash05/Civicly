'use client';

import { useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Icon } from './icons';
import { Unavailable } from './unavailable';
import { useDemo } from './demo-connection';
import { useRead } from './use-read';
import { ReadMessage } from './read-state';
import { CaseDirectory } from './case-directory';
import { RecordedDecisionGraph } from './recorded-decision-graph';
import {recordedGraphSteps} from '../lib/read/decision-paths';
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
  translateNextAction,
  translateLocation,
  formatEntityDisplayName,
  formatShortIdentifier,
} from '../lib/read/display';
import { TechnicalDetails, CopyableIdentifier } from './technical-details';
import {ResponseTimeline} from './response-timeline';
import {stageTakeaway} from '../lib/read/stage-takeaway';
import {caseProgress,currentPlan,scopedOrders,incidentIntroduction,reportJourney} from '../lib/read/workflow';

const stages = [
  'Report',
  'Investigation',
  'Evidence',
  'Plan & approval',
  'Work',
  'Monitoring & memory',
];
const sectionIds=['report','investigation','evidence','plan','work','monitoring'];

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

  const requestedStage=sectionIds.indexOf(searchParams.get('section') ?? '');
  const stage=requestedStage<0?1:requestedStage;
  function setStage(index:number){
    if(!sectionIds[index])return;
    const params=new URLSearchParams(searchParams.toString());
    params.set('section',sectionIds[index]);
    router.replace('/investigations?'+params.toString()+'#case-workspace',{scroll:false});
  }
  const [isCasePickerOpen, setIsCasePickerOpen] = useState(false);
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
  const reportsRead = useRead(
    `case-introduction-reports:${primaryIncident?.id ?? ''}:${primaryIncident?.complaint_ids.join(',') ?? ''}`,
    async signal => Promise.all((primaryIncident?.complaint_ids ?? []).slice(0,3).map(async id =>
      (await demo.connection.client.request('GET /api/v1/complaints/{id}', {params:{id},signal})).data)),
    Boolean(primaryIncident)
  );

  // Load FalkorDB Subgraph for selected investigation
  const graphRead = useRead<GraphSubgraphDTO | null>(
    `investigation-graph:${investigationId ?? ''}`,
    async (signal) => {
      if (!investigationId) return null;
      const res = await demo.connection.client.request(
        'GET /api/v1/investigations/{id}/graph',
        {
          params: { id: investigationId },
          query: { depth: 4, include_candidates: true },
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
      return (await demo.connection.client.request('GET /api/v1/procedures', {query:{limit:50},signal})).data;
    },
    Boolean(investigationId),
  );

  // The memory API is keyed by Incident ID, including a completed episode.
  const memoryRead = useRead<{ items: CaseMemoryDTO[] } | null>(
    `case-memory:${primaryIncident?.id ?? ''}`,
    async signal => primaryIncident ? (await demo.connection.client.request('GET /api/v1/cases/{id}/memory',{params:{id:primaryIncident.id},signal})).data : null,
    Boolean(primaryIncident)
  );

  // Load Problem Cluster Outcomes if cluster ID is known
  const clusterId = investigation?.problem_cluster_id;
  const outcomesRead = useRead<{ items: OutcomeDTO[] } | null>(
    `cluster-outcomes:${clusterId ?? ''}`,
    async (signal) => {
      if (!clusterId) return null;
      return (await demo.connection.client.request('GET /api/v1/problem-clusters/{id}/outcomes',{params:{id:clusterId},signal})).data;
    },
    Boolean(clusterId),
  );

  const stream = useEventStream({
    token: demo.status === 'connected' ? demo.connection.getToken() : null,
    investigationId: investigationId,
    onRefetch: () => {
      selectedCase.refresh();
      reportsRead.refresh();
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

  const plan = currentPlan(plansRead.data?.items ?? [], investigation?.current_plan_id);
  const caseOrders = scopedOrders(workOrdersRead.data?.items ?? [],(plansRead.data?.items ?? []).map(p=>p.plan_id));
  const progress = investigation ? caseProgress(investigation,traceRead.data,plan,outcomesRead.data?.items,caseOrders) : null;
  const graphSteps=graphRead.data?recordedGraphSteps(traceRead.data,graphRead.data):[];
  const activeGraphPathId=graphSteps.find(s=>s.path.id===selectedDecisionPathId)?.path.id??graphSteps[0]?.path.id??null;
  const introduction = primaryIncident ? incidentIntroduction(primaryIncident,reportsRead.data ?? [],hypothesesRead.data?.items ?? []) : null;
  const reportOverview=reportJourney(primaryIncident?.issue_type ?? '',hypothesesRead.data?.items ?? null,plan,workOrdersRead.data?.items ?? null,outcomesRead.data?.items ?? null);
  const takeawayReads = [
    [selectedCase,reportsRead], [selectedCase,traceRead], [selectedCase,hypothesesRead],
    [selectedCase,plansRead,workOrdersRead], [selectedCase,plansRead,workOrdersRead],
    [selectedCase,plansRead,workOrdersRead,outcomesRead,memoryRead],
  ][stage];
  const takeawayUnavailable=takeawayReads.some(r=>r.status==='error'||r.status==='unavailable');
  const takeawayLoading=takeawayReads.some(r=>r.status==='loading');
  const takeaway=stageTakeaway({stage,report:introduction?.report,
    location:primaryIncident?.location_id?translateLocation(primaryIncident.location_id):undefined,
    trace:traceRead.data,hypotheses:hypothesesRead.data?.items,plan,orders:caseOrders,
    outcomes:outcomesRead.data?.items,memory:memoryRead.data?.items.find(m=>m.id===primaryIncident?.id),investigationId});
  const otherHistoricalIds=(investigation?.historical_incident_ids ?? []).filter(id=>!incidents.some(i=>i.id===id));



  function selectIssue(value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) params.set('issue', value);
    else params.delete('issue');
    params.delete('cursor');
    params.delete('investigation');
    params.delete('incident');
    setSelectedDecisionPathId(null);
    setInspectedEvidenceId(null);
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
              {investigation ? `Investigation #${formatShortIdentifier(investigation.id)}` : incidentParam ? `Incident #${formatShortIdentifier(incidentParam)}` : 'Selected case'}
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
            title="See who can investigate, approve and perform work"
          >
            <Icon name="check" size={14} /> Roles &amp; permissions
          </button>
        </div>
        <p>
          <Icon name="shield" size={16} />
          {demo.status === 'connected' ? (
            hasSelection ? (
              <span>{selectedCase.status==='ready'?'Case loaded':'Reading selected case'} &bull; Simulated municipal district</span>
            ) : (
              <span>Demo connected &bull; Select a case below to begin</span>
            )
          ) : (
            demo.message
          )}
        </p>
      </div>

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
                  {progress?.status ?? translateStatus(primaryIncident?.status)}
                </span>
              </div>
              <h2 className="selected-case-title">
                {investigation
                  ? `${issueName(primaryIncident?.issue_type || 'Civic Defect')} Investigation`
                  : `Reported Incident: ${issueName(primaryIncident?.issue_type || 'Civic Defect')}`}
              </h2>
              <div className="case-introduction">
                <p className="eyebrow">What was reported</p>
                {reportsRead.status === 'loading' ? <p>Loading the original report…</p> : reportsRead.status === 'error' ? <ReadMessage state={reportsRead} resourceName="original report" retry={reportsRead.refresh} /> : <p className="selected-case-subtitle">{introduction?.report ?? 'No linked report description is available in the loaded records.'}</p>}
                {primaryIncident && primaryIncident.complaint_ids.length > 1 && <p className="muted text-sm">Showing the first available linked report. {primaryIncident.complaint_ids.length} reports are linked to this incident.</p>}
                {investigation && <><p className="eyebrow">What the investigation examines</p><p>{introduction?.focus}</p></>}
              </div>
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
            {primaryIncident && <><span>Location: <strong>{primaryIncident.location_id ? translateLocation(primaryIncident.location_id) : 'Not recorded'}</strong></span><span>Incident began: <strong>{displayTime(primaryIncident.started_at)}</strong></span></>}
            <span>Case reference: <strong>#{formatShortIdentifier(investigation?.id ?? primaryIncident?.id ?? '')}</strong></span>
            {investigation && (
              <>
                {investigation.next_action && (
                  <span>
                    Next required action: <strong>{progress?.next}</strong>
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
                  { label: 'Legacy runtime label (configuration metadata, not proof of execution)', value: <code>{investigation.runtime_status}</code>, rawString: investigation.runtime_status },
                  { label: 'Raw next-action code', value: <code>{investigation.next_action}</code>, rawString: investigation.next_action },
                  { label: 'Last saved agent pause', value: <code>{traceRead.data?.pause_reason || 'Not recorded'}</code> },
                  { label: 'Raw Investigation Status', value: <code>{investigation.status}</code>, rawString: investigation.status },
                  { label: 'Last recorded agent role', value: <span>{investigation.current_agent_role ? translateRole(investigation.current_agent_role) : 'Not recorded'}</span> },
                  { label: 'Graph Revision', value: <span>{investigation.graph_revision}</span>, rawString: String(investigation.graph_revision) },
                  ...(investigation.problem_cluster_id ? [{ label: 'Problem Cluster ID', value: <code>{investigation.problem_cluster_id}</code>, rawString: investigation.problem_cluster_id }] : []),
                ] : []),
                ...(primaryIncident ? [
                  { label: 'Primary Incident ID', value: <code>{primaryIncident.id}</code>, rawString: primaryIncident.id },
                  { label: 'Location Identifier', value: <code>{primaryIncident.location_id || 'null'}</code>, rawString: primaryIncident.location_id || undefined },
                  { label: 'Linked problem group', value: <code>{primaryIncident.cluster_id ?? 'Not recorded'}</code> },
                  ...(reportsRead.data ?? []).filter(r=>r.incident_id===primaryIncident.id&&primaryIncident.complaint_ids.includes(r.id)).map(r=>({label:`Original report ${formatShortIdentifier(r.id)}`,value:<span>{r.description}</span>,rawString:r.description})),
                ] : []),
              ]}
            />
          </div>

          {!investigation && primaryIncident && (
            <div className="absence-notice">
              <Icon name="help" size={16} />
              <span>
                No investigation is linked in the loaded directory for this incident. The directory is bounded; additional records may exist.
              </span>
            </div>
          )}
        </div>
      )}

      {progress && <section className="case-notice" aria-label="Case progress summary">
        <div><strong>{progress.next}</strong><p>{progress.detail}</p><p className="muted text-sm">{progress.origin}. Saved agent pause: {progress.pause}. The saved agent step and the current work status are shown separately.</p></div>
      </section>}

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
            {hasSelection && stage < stages.length - 1 ? (
              <button
                type="button"
                className="button secondary"
                style={{ fontSize: 11, padding: '6px 10px', whiteSpace: 'normal', textAlign: 'left' }}
                onClick={() => setStage(stage + 1)}
              >
                Next: {stages[stage + 1]} <Icon name="arrow" size={14} />
              </button>
            ) : <Icon name={stage === 1 ? 'search' : 'file'} />}
          </div>

          {hasSelection && selectedCase.status==='ready' && (stage===0||investigation) && <aside className="stage-takeaway" aria-label="Stage takeaway" aria-live="polite">
            <span className="stage-takeaway-label">Key takeaway</span>
            <h3>{takeawayUnavailable?'The stage summary is unavailable':takeawayLoading?'Reading the saved case…':takeaway.title}</h3>
            <p>{takeawayUnavailable?'Some records could not be loaded. Check the messages below before drawing a conclusion.':takeawayLoading?'The takeaway will appear when this stage’s records have loaded.':takeaway.text}</p>
          </aside>}

          {hasSelection && investigation && stage>=3 && <div className="response-timeline-wrap">
            {[plansRead,workOrdersRead,outcomesRead].some(r=>r.status==='loading') ? <p className="muted text-sm">Reading the response milestones…</p>
              : plansRead.status!=='ready' ? <ReadMessage state={plansRead} resourceName="response plan" retry={plansRead.refresh}/>
              : <ResponseTimeline plan={plan}
                  orders={workOrdersRead.status==='ready'?caseOrders:null}
                  outcomes={outcomesRead.status==='ready'?outcomesRead.data?.items??[]:null}
                  onSelectStage={setStage} onSelectEvidence={setInspectedEvidenceId}/>}
          </div>}

          {hasSelection && selectedCase.status!=='ready' && <div className="stage-content case-loading-placeholder">
            {selectedCase.status==='loading'?<ReadMessage state={selectedCase} resourceName="selected case"/>:selectedCase.status==='unavailable'?<ReadMessage state={selectedCase} resourceName="selected case" retry={selectedCase.refresh}/>:<p className="muted text-sm">The selected case could not be loaded. Review the message above and try again.</p>}
          </div>}

          {!hasSelection && (
            <div className="stage-content">
              {isCasePickerOpen ? (
                <>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                    <h3>Available cases</h3>
                    <button type="button" className="button secondary" onClick={() => setIsCasePickerOpen(false)}>Close case list</button>
                  </div>
                  <CaseDirectory issue={issueParam} />
                </>
              ) : (
                <div className="empty-state">
                  <span className="empty-icon"><Icon name="file" size={27} /></span>
                  <h3>Choose a case to explore</h3>
                  <p>Select an available investigation or reported incident to follow its reports, evidence, plan and outcomes.</p>
                  <button type="button" className="button primary" onClick={() => setIsCasePickerOpen(true)} aria-expanded={false}>
                    Choose a case <Icon name="arrow" size={14} />
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Stage 0: Report & Recurrence */}
          {hasSelection && selectedCase.status==='ready' && stage === 0 && (
            <div className="stage-content">
              {hasSelection && selectedCase.data ? (
                <div className="stage-report-details">
                  <section className="report-overview" aria-label="Incident and investigation overview">
                    <div className="report-story-step">
                      <h4>What happened</h4>
                      {reportsRead.status==='error' ? <ReadMessage state={reportsRead} resourceName="original report" retry={reportsRead.refresh}/> : <p>{reportsRead.status==='loading' ? 'Loading the linked report…' : introduction?.report ?? 'A linked report description is not available.'}</p>}
                      <p className="report-story-context">{primaryIncident?.location_id ? translateLocation(primaryIncident.location_id) : 'Location not recorded'} · Incident began {displayTime(primaryIncident?.started_at ?? '')}</p>
                    </div>
                    {investigation && <>
                      <div className="report-story-step"><h4>Why it needed investigation</h4><p>{reportOverview.why}</p></div>
                      <div className="report-story-step">
                        <h4>What the evidence showed</h4>
                        {hypothesesRead.status==='error' ? <ReadMessage state={hypothesesRead} resourceName="evidence assessment" retry={hypothesesRead.refresh}/> : reportOverview.findings.length ? <ul>{reportOverview.findings.map((f,i)=><li key={i}>{f}</li>)}</ul> : <p>{hypothesesRead.status==='loading' ? 'Loading the recorded assessments…' : 'No assessed possible causes were returned. The cause remains to be established.'}</p>}
                        <p className="report-story-context">The Evidence section contains the supporting observations, contradictions and remaining questions.</p>
                      </div>
                      <div className="report-story-step">
                        <h4>What action followed</h4>
                        {plansRead.status==='error' ? <ReadMessage state={plansRead} resourceName="action plan" retry={plansRead.refresh}/> : <><p>{plansRead.status==='loading' ? 'Loading the saved plan…' : reportOverview.approval}</p>{reportOverview.response.length>0 && <ul>{reportOverview.response.map((r,i)=><li key={i}>{r}</li>)}</ul>}</>}
                        {workOrdersRead.status==='error' ? <ReadMessage state={workOrdersRead} resourceName="work records" retry={workOrdersRead.refresh}/> : <p>{reportOverview.work}</p>}
                        <p className="report-story-context">Plan & approval shows the exact scope and prerequisites; Work shows the recorded progress.</p>
                      </div>
                      <div className="report-story-step">
                        <h4>What happened after the work</h4>
                        {outcomesRead.status==='error' ? <ReadMessage state={outcomesRead} resourceName="follow-up outcomes" retry={outcomesRead.refresh}/> : <p>{outcomesRead.status==='loading'?'Loading the recorded follow-up…':reportOverview.followup}</p>}
                        <p><strong>Current next step:</strong> {progress?.next}. {progress?.detail}</p>
                      </div>
                    </>}
                  </section>
                  <h3>Linked incident reports ({incidents.length})</h3>
                  <div className="incident-cards">
                    {incidents.map((inc, incIdx) => (
                      <article className="incident-card" key={inc.id}>
                        <div className="incident-card-top">
                          <div>
                            <span className="card-type-label">CITIZEN INCIDENT REPORT #{incIdx + 1}</span>
                            <h4 style={{ margin: '2px 0 0', fontSize: '15px', fontWeight: 600 }}>
                              {issueName(inc.issue_type)} Incident
                              <span className="id-sub" style={{ marginLeft: '0.4rem', fontWeight: 400 }}>
                                (#{formatShortIdentifier(inc.id)})
                              </span>
                            </h4>
                          </div>
                          <span className="status-tag">{translateStatus(inc.status)}</span>
                        </div>
                        <div className="incident-card-meta">
                          <p>
                            <strong>Issue:</strong> {issueName(inc.issue_type)}{' '}
                            {inc.subtype && inc.subtype!=='UNSPECIFIED' ? `(${inc.subtype.replaceAll('_',' ').toLowerCase()})` : ''}
                          </p>
                          <p>
                            <strong>Location:</strong> {translateLocation(inc.location_id)}
                          </p>
                          <p>
                            <strong>Started:</strong> {displayTime(inc.started_at)}
                          </p>
                          {inc.ended_at && (
                            <p>
                              <strong>Ended:</strong> {displayTime(inc.ended_at)}
                            </p>
                          )}
                          {inc.complaint_ids?.length ? (
                            <p>
                              <strong>Linked reports:</strong> {inc.complaint_ids.length}
                            </p>
                          ) : null}
                        </div>
                        <TechnicalDetails
                          title="Technical incident references"
                          items={[
                            { label: 'Incident ID', value: <code>{inc.id}</code>, rawString: inc.id },
                            { label: 'Location ID', value: <code>{inc.location_id || 'null'}</code>, rawString: inc.location_id || undefined },
                            ...(inc.cluster_id ? [{ label: 'Cluster ID', value: <code>{inc.cluster_id}</code>, rawString: inc.cluster_id }] : []),
                            ...(inc.complaint_ids?.length ? [{ label: 'Complaint IDs', value: <span>{inc.complaint_ids.join(', ')}</span> }] : []),
                          ]}
                        />
                      </article>
                    ))}
                  </div>

                  {otherHistoricalIds.length ? (
                    <div className="historical-incidents">
                      <h4>Closed incident history</h4>
                      <p>Closed incident records linked to this investigation:</p>
                      <ul>
                        {otherHistoricalIds.map((id) => (
                          <li key={id}>Closed incident (#{formatShortIdentifier(id)})</li>
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
          {hasSelection && selectedCase.status==='ready' && stage === 1 && (
            <div className="stage-content">
              {hasSelection && investigation ? (
                <div className="stage-investigation-details">
                  <div className="investigation-status-block">
                    <div>
                      <small>Investigation Status</small>
                      <strong>{progress?.status}</strong>
                    </div>
                    <div className="recorded-agent-summary">
                      <small>Recorded agent activity</small>
                      <strong>{progress?.origin}</strong>
                      <p className="muted text-sm">{progress?.originDetail}</p>
                    </div>
                    <div>
                      <small>Possible causes considered</small>
                      <strong>{investigation.active_hypothesis_ids?.length ?? 0}</strong>
                    </div>
                    <div>
                      <small>Inspections awaiting findings</small>
                      <strong>{investigation.pending_inspection_ids?.length ?? 0}</strong>
                    </div>
                  </div>

                  {/* Scoped Live Event Stream for this Investigation */}
                  <div style={{ marginTop: '1.25rem' }}>
                    <LiveStreamPanel
                      status={stream.status}
                      lastEventId={stream.lastEventId}
                      events={stream.events}
                      onReconnect={stream.reconnect}
                      onClear={stream.clearEvents}
                      title="Saved case updates"
                      defaultExpanded={false}
                    />
                  </div>

                  {/* 3-Part Traceability Component */}
                  <h3 style={{ marginTop: '1.5rem', marginBottom: '0.75rem' }}>
                    How the agent investigated: question → evidence → decision
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
                      selectedDecisionPathId={activeGraphPathId}
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
          {hasSelection && selectedCase.status==='ready' && stage === 2 && (
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
                      plan={plan}
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
          {hasSelection && selectedCase.status==='ready' && stage === 3 && (
            <div className="stage-content">
              {hasSelection && investigation ? (
                <div className="stage-plan-details">
                  {plansRead.status === 'loading' && (
                    <p className="muted">Loading the plan and task dependencies…</p>
                  )}
                  {plansRead.status === 'error' && (
                    <ReadMessage state={plansRead} retry={plansRead.refresh} />
                  )}
                  {plansRead.status === 'ready' && (
                    <PlanApprovalPanel
                      plan={plan}
                      hypotheses={hypothesesRead.data?.items}
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
          {hasSelection && selectedCase.status==='ready' && stage === 4 && (
            <div className="stage-content">
              {hasSelection && investigation ? (
                <div className="stage-work-details">
                  {(workOrdersRead.status === 'loading'||plansRead.status==='loading') && (
                    <p className="muted">Loading dispatched work orders and inspections...</p>
                  )}
                  {workOrdersRead.status === 'error' && (
                    <ReadMessage state={workOrdersRead} retry={workOrdersRead.refresh} />
                  )}
                  {workOrdersRead.status === 'ready' && plansRead.status!=='loading' && (
                    <WorkOrdersPanel
                      investigationId={investigation.id}
                      planId={plan?.plan_id}
                      plan={plan}
                      pendingInspectionIds={investigation.pending_inspection_ids}
                      workOrders={caseOrders}
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
          {hasSelection && selectedCase.status==='ready' && stage === 5 && (
            <div className="stage-content">
              {hasSelection && investigation ? (
                <div className="stage-monitoring-details">
                  {[monitoringRead,proceduresRead,memoryRead,outcomesRead,plansRead,workOrdersRead].map((read,index)=>read.status==='error'?<ReadMessage key={index} resourceName={['monitoring records','procedure documents','case memory','outcome records','plan records','work records'][index]} state={read} retry={read.refresh}/>:null)}
                  {[monitoringRead,proceduresRead,memoryRead,outcomesRead,plansRead,workOrdersRead].some(read=>read.status==='loading') ? <ReadMessage state={{status:'loading',data:null,message:'Loading follow-up and memory…',requestId:null}} resourceName="follow-up and case memory"/> : <MonitoringMemoryPanel
                    investigationId={investigation.id}
                    plan={plan}
                    workOrders={caseOrders}
                    problemClusterId={investigation.problem_cluster_id}
                    issueType={primaryIncident?.issue_type || null}
                    historicalIncidentIds={(investigation.historical_incident_ids || []).filter(id=>id!==primaryIncident?.id)}
                    monitoringList={monitoringRead.data?.items || []}
                    procedures={proceduresRead.data?.items || []}
                    memory={memoryRead.data?.items.find(m=>m.id===primaryIncident?.id) ?? memoryRead.data?.items[0] ?? null}
                    outcomes={outcomesRead.data?.items || []}
                    onSelectEvidenceId={setInspectedEvidenceId}
                    onRefetch={() => {
                      monitoringRead.refresh();
                      proceduresRead.refresh();
                      memoryRead.refresh();
                      outcomesRead.refresh();
                    }}
                  />}
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
            {hasSelection && selectedCase.status!=='ready' ? <div className="graph-loading-box"><ReadMessage state={selectedCase} resourceName="case graph"/></div> : investigationId ? (
              <>
                {graphRead.data ? (
                  <RecordedDecisionGraph
                    key={investigationId}
                    subgraph={graphRead.data}
                    steps={graphSteps}
                    selectedPathId={activeGraphPathId}
                    onSelectPath={setSelectedDecisionPathId}
                    onSelectEvidenceId={setInspectedEvidenceId}
                    isExpanded={isGraphExpanded}
                    onToggleExpand={() => setIsGraphExpanded(!isGraphExpanded)}
                  />
                ) : graphRead.status === 'loading' ? (
                  <div className="graph-loading-box">
                    <ReadMessage state={graphRead} resourceName="connected graph evidence"/>
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
      {hasSelection && <section className="panel directory-panel" style={{ marginTop: 24 }}>
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
      </section>}

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
