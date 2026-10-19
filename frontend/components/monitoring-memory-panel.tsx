'use client';

import React, { useState } from 'react';
import type {
  MonitoringDTO,
  ProcedureDTO,
  CaseMemoryDTO,
  OutcomeDTO,
  PlanDTO,
  WorkOrderDTO,
} from '../lib/generated/models';
import {
  findClusterMonitoring,
  filterRelevantProcedures,
  getMonitoringStatusStyle,
  formatQuoteExcerpt,
  explainOutcome,
  monitoringOpportunity,
} from '../lib/read/memory';
import { displayTime } from '../lib/read/cases';
import {
  translateStatus,
  translateActionType,
  translateDepartment,
  formatEntityDisplayName,
} from '../lib/read/display';
import {taskForOrder} from '../lib/read/workflow';
import { TechnicalDetails, CopyableIdentifier } from './technical-details';

interface MonitoringMemoryPanelProps {
  investigationId: string;
  problemClusterId?: string | null;
  issueType?: string | null;
  historicalIncidentIds?: string[];
  monitoringList?: MonitoringDTO[];
  procedures?: ProcedureDTO[];
  memory?: CaseMemoryDTO | null;
  outcomes?: OutcomeDTO[];
  plan?:PlanDTO|null;
  workOrders?:WorkOrderDTO[];
  onSelectEvidenceId?: (id: string) => void;
  onRefetch?: () => void;
}

export function MonitoringMemoryPanel({
  investigationId,
  problemClusterId,
  issueType,
  historicalIncidentIds = [],
  monitoringList = [],
  procedures = [],
  memory = null,
  outcomes = [],
  plan=null,
  workOrders=[],
  onSelectEvidenceId,
  onRefetch,
}: MonitoringMemoryPanelProps) {
  const [expandedProcedureId, setExpandedProcedureId] = useState<string | null>(null);

  const clusterMonitoring = findClusterMonitoring(monitoringList, problemClusterId);
  const relevantProcedures = filterRelevantProcedures(procedures, null, issueType);
  const caseOrders=workOrders.filter(w=>w.plan_id===plan?.plan_id);
  const caseOutcomes=outcomes.filter(o=>caseOrders.some(w=>w.id===o.work_order_id)).sort((a,b)=>Date.parse(a.evaluated_at)-Date.parse(b.evaluated_at)||a.id.localeCompare(b.id));

  const statusStyle = clusterMonitoring
    ? getMonitoringStatusStyle(clusterMonitoring.status)
    : getMonitoringStatusStyle('OPEN');

  return (
    <div className="monitoring-memory-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* 1. Core Invariant Callout */}

      {/* 2. Cluster Monitoring & Verification Policy */}
      <section className="monitoring-section">
        <header className="section-header-row">
          <div>
            <span className="card-type-label">POST-INTERVENTION MONITORING</span>
            <h3 className="section-title">
              {problemClusterId
                ? `Follow-up and problem history`
                : 'Follow-up observations'}
            </h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Review dated observations after work and the evidence used to assess the outcome.
            </p>
          </div>
          {clusterMonitoring && (
            <span
              className="badge"
              style={{
                backgroundColor: statusStyle.bg,
                color: statusStyle.color,
                borderColor: statusStyle.border,
              }}
            >
              {translateStatus(clusterMonitoring.status)}
            </span>
          )}
        </header>

        {clusterMonitoring ? (
          <div className="monitoring-content-stack">
            <div className="monitoring-policy-box">
              <strong className="box-title">What the follow-up needs to establish</strong>
              <p className="policy-text">{monitoringOpportunity(issueType)}</p>
              <p className="monitoring-context">These are the checks to review, not a claim that every required observation has been collected.</p>
            </div>

            <div className="monitoring-checks-box">
              <strong className="box-title">What still needs checking</strong>
              {clusterMonitoring.remaining_checks?.length ? (
                <ul className="checks-list">
                  {clusterMonitoring.remaining_checks.map((check, idx) => (
                    <li key={idx}>{check}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted text-sm" style={{ margin: '0.25rem 0 0' }}>
                  No remaining checks are listed in this monitoring record. Review the outcome and its evidence before drawing a conclusion.
                </p>
              )}
            </div>

            {clusterMonitoring.outcome_evidence_ids && clusterMonitoring.outcome_evidence_ids.length > 0 && (
              <div className="outcome-evidence-row">
                <strong>Follow-up source records</strong>
                <div className="chips-row" style={{ display: 'inline-flex', marginLeft: '0.5rem' }}>
                  {clusterMonitoring.outcome_evidence_ids.map((evId,index) => (
                    <button
                      key={evId}
                      type="button"
                      className="chip chip-evidence"
                      onClick={() => onSelectEvidenceId?.(evId)}
                      title={`Inspect evidence ${evId}`}
                    >
                      Review observation {index+1}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <TechnicalDetails
              title="Technical cluster monitoring details"
              items={[
                { label: 'Problem Cluster ID', value: <code>{problemClusterId || clusterMonitoring.problem_cluster_id}</code>, rawString: problemClusterId || clusterMonitoring.problem_cluster_id },
                { label: 'Verification policy', value: <code>{clusterMonitoring.verification_policy}</code>, rawString: clusterMonitoring.verification_policy },
                { label: 'Raw Monitoring Status', value: <code>{clusterMonitoring.status}</code>, rawString: clusterMonitoring.status },
                { label: 'Remaining Verification Checks', value: <span>{clusterMonitoring.remaining_checks?.length || 0} checks</span> },
              ]}
            />
          </div>
        ) : (
          <div className="empty-boxed-notice">
            No follow-up monitoring record was returned for this case. {monitoringOpportunity(issueType)} This view does not establish that those checks have happened.
          </div>
        )}
      </section>

      {/* 5. Case Memory & Evaluated Outcomes */}
      <section className="case-memory-section">
        <header className="section-header-row">
          <div>
            <h3 className="section-title">What this case keeps for the future</h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Retained episodes, source evidence and outcomes for later investigation; not an automatically learned rule.
            </p>
          </div>
        </header>

        {memory ? (
          <div className="memory-card">
            <h4 className="memory-type-title">A record to consult if the problem returns</h4>
            <p className="memory-summary-text">The case retains its recorded outcomes and source evidence so a later investigation can check what was tried and what happened afterwards. It does not prove that the same cause applies to another incident.</p>
            <p>{memory.outcome_ids.length} saved outcome records · {memory.evidence_ids?.length ?? 0} linked source records</p>
            <div className="chips-row">{memory.evidence_ids?.map((id,index)=><button key={id} type="button" className="chip chip-evidence" onClick={()=>onSelectEvidenceId?.(id)}>Review saved source {index+1}</button>)}</div>
            {memory.gaps?.length ? (
              <div className="memory-gaps-box">
                <strong>Limits to keep in mind</strong><p>The saved record includes unresolved questions or qualifications. Review the original notes before reusing it; a past result is not an automatic rule for future cases.</p>
              </div>
            ) : null}

            <TechnicalDetails
              title="Technical memory references"
              items={[
                { label: 'Memory ID', value: <code>{memory.id}</code>, rawString: memory.id },
                { label: 'Memory Type', value: <code>{memory.memory_type}</code>, rawString: memory.memory_type },
                { label: 'Original saved summary', value: <span>{memory.summary ?? 'Not recorded'}</span> },
                { label: 'Original knowledge gaps', value: <span>{memory.gaps?.join('; ') || 'None returned'}</span> },
              ]}
            />
          </div>
        ) : (
          <div className="empty-boxed-notice">
            <strong style={{ display: 'block', marginBottom: '0.25rem' }}>
              No case memory returned
            </strong>
            No historical context was returned for this selected incident. This may reflect an incomplete episode, a bounded search, or a read error shown above; it does not prove that no history exists.
          </div>
        )}

        {caseOutcomes.length > 0 && (
          <div className="outcomes-block" style={{ marginTop: '1.25rem' }}>
            <h4 className="outcomes-title">Recorded follow-up history ({caseOutcomes.length})</h4>
            <p className="monitoring-context">Read these dated assessments in order. An earlier completion record can be followed by a later verification; earlier assessments remain part of the history.</p>
            <div className="cards-stack">
              {caseOutcomes.map((out) => {
                const order=caseOrders.find(w=>w.id===out.work_order_id);
                const task=order?taskForOrder(plan,order):undefined;
                return (
                <div key={out.id} className="outcome-card">
                  <div className="outcome-top">
                    <strong>{task?translateActionType(task.action_type):'Recorded work assessment'}</strong>
                    <span
                      className={`badge ${
                        out.case_closed ? 'badge-verified' : 'badge-candidate'
                      }`}
                    >
                      {out.case_closed ? 'This outcome closed an episode' : 'This outcome did not close the case'}
                    </span>
                  </div>
                  <p className="outcome-result-text">
                    {explainOutcome(out)}
                  </p>
                  <p className="monitoring-context">Assessment: {translateStatus(out.assessment_status)}</p>
                  <p className="outcome-date-meta">
                    Evaluated: {displayTime(out.evaluated_at)}
                  </p>
                  <div className="chips-row">{out.evidence_ids.map((id,index)=><button key={id} type="button" className="chip chip-evidence" onClick={()=>onSelectEvidenceId?.(id)}>Review follow-up source {index+1}</button>)}</div>

                  <TechnicalDetails
                    title="Technical outcome references"
                    items={[
                      { label: 'Outcome ID', value: <code>{out.id}</code>, rawString: out.id },
                      { label: 'Raw Result', value: <code>{out.result}</code>, rawString: out.result },
                      { label: 'Case Closed', value: <span>{out.case_closed ? 'True' : 'False'}</span> },
                    ]}
                  />
                </div>
              );})}
            </div>
          </div>
        )}
      </section>

      {/* 3. Recurrence & Historical Incident Context */}
      <section className="recurrence-section">
        <header className="section-header-row">
          <div>
            <h3 className="section-title">Has this happened before?</h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Other closed incident records linked to this investigation. Location alone does not establish recurrence.
            </p>
          </div>
          <span className="count-pill">{historicalIncidentIds.length}</span>
        </header>

        {historicalIncidentIds.length === 0 ? (
          <div className="empty-boxed-notice">
            No other closed incidents are linked in the loaded investigation. This does not establish that the problem has never occurred before.
          </div>
        ) : (
          <div className="recurrence-content">
            <p className="muted text-sm" style={{ margin: '0 0 0.5rem' }}>
              Prior incidents linked to this recurrence pattern:
            </p>
            <div className="chips-row">
              {historicalIncidentIds.map((id) => (
                <span key={id} className="chip chip-asset">
                  Reported incident <small>({id.slice(-4)})</small>
                </span>
              ))}
            </div>

            <div style={{ marginTop: '0.75rem' }}>
              <TechnicalDetails
                title="Technical incident list"
                items={historicalIncidentIds.map((id, idx) => ({
                  label: `Incident ${idx + 1}`,
                  value: <code>{id}</code>,
                  rawString: id,
                }))}
              />
            </div>
          </div>
        )}
      </section>

      {/* 4. Relevant Municipal Procedures & Cited Knowledge */}
      <section className="procedures-section">
        <header className="section-header-row">
          <div>
            <h3 className="section-title">
              Guidance for future work
            </h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Synthetic, proposed guidance available for this category. A relevant document is not necessarily cited by the current plan.
            </p>
          </div>
          <span className="count-pill">{relevantProcedures.length}</span>
        </header>

        {relevantProcedures.length === 0 ? (
          <div className="empty-boxed-notice">
            No matching procedure documents were returned for this category.
          </div>
        ) : (
          <div className="cards-stack">
            {relevantProcedures.map((proc) => {
              const isExpanded = expandedProcedureId === proc.id;
              const deptName = translateDepartment(proc.owner_department_id);

              return (
                <article key={proc.id} className="procedure-card">
                  <header className="card-top-row">
                    <div>
                      <span className="card-dept-label">{deptName}</span>
                      <h4 className="card-main-title">{proc.title.replace(/\b(?:SUBGRADE_REPAIR|DRAIN_BLOCKAGE_CLEARANCE|MISSED_PICKUP_RECOVERY|UTILITY_ISOLATION|UTILITY_LEAK_REPAIR)\b/g,code=>translateActionType(code))}</h4>
                    </div>

                    <div className="proc-badges">
                      <span
                        className="badge badge-untrusted"
                        title="Treated as untrusted municipal evidence, not tool instructions."
                      >
                        Reference material only
                      </span>
                      <span className="badge badge-candidate">
                        {translateStatus(proc.assertion_status)}
                      </span>
                    </div>
                  </header>

                  <div className="card-content-body">
                    {proc.citations?.length > 0 && (
                      <div className="citation-block">
                        <button
                          type="button"
                          className="toggle-specs-btn"
                          onClick={() => setExpandedProcedureId(isExpanded ? null : proc.id)}
                        >
                          {isExpanded ? 'Hide Citation Excerpt ▲' : 'View Citation Excerpt ▼'}
                        </button>

                        {isExpanded && (
                          <div className="citation-drawer">
                            <blockquote className="citation-quote">
                              "{formatQuoteExcerpt(proc.citations[0].quote_excerpt, 320)}"
                            </blockquote>
                            {proc.citations[0].passage_location && (
                              <p className="passage-meta">
                                Section reference: <code>{proc.citations[0].passage_location}</code>
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    <TechnicalDetails
                      title="Technical procedure metadata & checksum"
                      items={[
                        { label: 'Procedure ID', value: <code>{proc.procedure_id || proc.id}</code>, rawString: proc.procedure_id || proc.id },
                        { label: 'Version / effective date', value: <span>Version {proc.version} · {displayTime(proc.effective_from)}</span> },
                        { label: 'Owner Department ID', value: <code>{proc.owner_department_id}</code>, rawString: proc.owner_department_id },
                        { label: 'Document SHA-256', value: <code className="hash-code">{proc.sha256}</code>, rawString: proc.sha256 },
                        { label: 'Assertion Status', value: <code>{proc.assertion_status}</code>, rawString: proc.assertion_status },
                      ]}
                    />
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>


    </div>
  );
}
