'use client';

import React, { useState } from 'react';
import type {
  MonitoringDTO,
  ProcedureDTO,
  CaseMemoryDTO,
  OutcomeDTO,
} from '../lib/generated/models';
import {
  findClusterMonitoring,
  filterRelevantProcedures,
  getMonitoringStatusStyle,
  formatQuoteExcerpt,
} from '../lib/read/memory';
import { displayTime } from '../lib/read/cases';
import {
  translateStatus,
  translateDepartment,
  formatEntityDisplayName,
} from '../lib/read/display';
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
  onSelectEvidenceId,
  onRefetch,
}: MonitoringMemoryPanelProps) {
  const [expandedProcedureId, setExpandedProcedureId] = useState<string | null>(null);

  const clusterMonitoring = findClusterMonitoring(monitoringList, problemClusterId);
  const relevantProcedures = filterRelevantProcedures(procedures, null, issueType);

  const statusStyle = clusterMonitoring
    ? getMonitoringStatusStyle(clusterMonitoring.status)
    : getMonitoringStatusStyle('OPEN');

  return (
    <div className="monitoring-memory-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* 1. Core Invariant Callout */}
      <div className="resolution-distinction-banner">
        <div className="banner-icon" aria-hidden="true">⚠</div>
        <div className="banner-text">
          <strong>Operational Fact: Work Completion is NOT Verified Resolution</strong>
          <p>
            Physical execution of field work orders (clearing a drain inlet, patching road subgrade, or running a recovery collection)
            records work execution only.
            <strong> Verified resolution</strong> requires subsequent post-intervention monitoring across an independent observation opportunity
            (such as a comparable rainfall event or regular collection cycle) confirming no problem recurrence.
          </p>
        </div>
      </div>

      {/* 2. Cluster Monitoring & Verification Policy */}
      <section className="monitoring-section">
        <header className="section-header-row">
          <div>
            <span className="card-type-label">POST-INTERVENTION MONITORING</span>
            <h3 className="section-title">
              {problemClusterId
                ? `Recurrence Zone Monitoring`
                : 'Environmental Recurrence Monitoring'}
            </h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Independent environmental observation tracking recurrence risks across comparable civic conditions.
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
              <strong className="box-title">Verification Policy:</strong>
              <p className="policy-text">
                {clusterMonitoring.verification_policy}
              </p>
            </div>

            <div className="monitoring-checks-box">
              <strong className="box-title">Required Verification Checks:</strong>
              {clusterMonitoring.remaining_checks?.length ? (
                <ul className="checks-list">
                  {clusterMonitoring.remaining_checks.map((check, idx) => (
                    <li key={idx}>{check}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted text-sm" style={{ margin: '0.25rem 0 0' }}>
                  All scheduled verification observation cycles have completed.
                </p>
              )}
            </div>

            {clusterMonitoring.outcome_evidence_ids && clusterMonitoring.outcome_evidence_ids.length > 0 && (
              <div className="outcome-evidence-row">
                <strong>Outcome Evidence Collected: </strong>
                <div className="chips-row" style={{ display: 'inline-flex', marginLeft: '0.5rem' }}>
                  {clusterMonitoring.outcome_evidence_ids.map((evId) => (
                    <button
                      key={evId}
                      type="button"
                      className="chip chip-evidence"
                      onClick={() => onSelectEvidenceId?.(evId)}
                      title={`Inspect evidence ${evId}`}
                    >
                      Evidence ({evId.slice(-4)})
                    </button>
                  ))}
                </div>
              </div>
            )}

            <TechnicalDetails
              title="Technical cluster monitoring details"
              items={[
                { label: 'Problem Cluster ID', value: <code>{problemClusterId || clusterMonitoring.problem_cluster_id}</code>, rawString: problemClusterId || clusterMonitoring.problem_cluster_id },
                { label: 'Raw Monitoring Status', value: <code>{clusterMonitoring.status}</code>, rawString: clusterMonitoring.status },
                { label: 'Remaining Verification Checks', value: <span>{clusterMonitoring.remaining_checks?.length || 0} checks</span> },
              ]}
            />
          </div>
        ) : (
          <div className="empty-boxed-notice">
            No dedicated problem cluster monitoring record registered for this case.
          </div>
        )}
      </section>

      {/* 3. Recurrence & Historical Incident Context */}
      <section className="recurrence-section">
        <header className="section-header-row">
          <div>
            <h3 className="section-title">Prior Recurrence History</h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Earlier incidents recorded at or adjacent to this civic asset location.
            </p>
          </div>
          <span className="count-pill">{historicalIncidentIds.length}</span>
        </header>

        {historicalIncidentIds.length === 0 ? (
          <div className="empty-boxed-notice">
            No prior historical incidents registered in this cluster. This is an initial occurrence in the civic ledger.
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
              Sourced Municipal Procedures ({relevantProcedures.length})
            </h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Standard operating procedures and cited engineering specifications.
            </p>
          </div>
          <span className="count-pill">{relevantProcedures.length}</span>
        </header>

        {relevantProcedures.length === 0 ? (
          <div className="empty-boxed-notice">
            No specific procedure documents cited for this category.
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
                      <h4 className="card-main-title">{proc.title}</h4>
                      <p className="card-version-meta">
                        Standard {proc.procedure_id || proc.id} &bull; Version {proc.version} &bull; Effective: {displayTime(proc.effective_from)}
                      </p>
                    </div>

                    <div className="proc-badges">
                      <span
                        className="badge badge-untrusted"
                        title="Treated as untrusted municipal evidence, not tool instructions."
                      >
                        UNTRUSTED AS INSTRUCTIONS
                      </span>
                      <span className="badge badge-verified">
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

      {/* 5. Case Memory & Evaluated Outcomes */}
      <section className="case-memory-section">
        <header className="section-header-row">
          <div>
            <h3 className="section-title">Case Memory &amp; Outcomes</h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Permanent learning records compiled upon verified civic resolution.
            </p>
          </div>
        </header>

        {memory ? (
          <div className="memory-card">
            <h4 className="memory-type-title">Case Resolution Memory Record</h4>
            <p className="memory-summary-text">{memory.summary}</p>
            {memory.gaps?.length ? (
              <div className="memory-gaps-box">
                <strong>Noted Knowledge Gaps:</strong> {memory.gaps.join(', ')}
              </div>
            ) : null}

            <TechnicalDetails
              title="Technical memory references"
              items={[
                { label: 'Memory ID', value: <code>{memory.id}</code>, rawString: memory.id },
                { label: 'Memory Type', value: <code>{memory.memory_type}</code>, rawString: memory.memory_type },
              ]}
            />
          </div>
        ) : (
          <div className="empty-boxed-notice">
            <strong style={{ display: 'block', marginBottom: '0.25rem' }}>
              Case Memory Pending Verified Closure
            </strong>
            Permanent case memory records are compiled upon final outcome evaluation and verified case closure.
            While this case remains in active execution or monitoring, operational reasoning is grounded in active cluster monitoring and cited standard operating procedures.
          </div>
        )}

        {outcomes.length > 0 && (
          <div className="outcomes-block" style={{ marginTop: '1.25rem' }}>
            <h4 className="outcomes-title">Evaluated Resolution Outcomes ({outcomes.length})</h4>
            <div className="cards-stack">
              {outcomes.map((out) => (
                <div key={out.id} className="outcome-card">
                  <div className="outcome-top">
                    <strong>Resolution Evaluation</strong>
                    <span
                      className={`badge ${
                        out.case_closed ? 'badge-verified' : 'badge-candidate'
                      }`}
                    >
                      {out.case_closed ? 'CASE CLOSED' : 'MONITORING CONTINUES'}
                    </span>
                  </div>
                  <p className="outcome-result-text">
                    <strong>Result:</strong> {translateStatus(out.result)}
                  </p>
                  <p className="outcome-date-meta">
                    Evaluated: {displayTime(out.evaluated_at)}
                  </p>

                  <TechnicalDetails
                    title="Technical outcome references"
                    items={[
                      { label: 'Outcome ID', value: <code>{out.id}</code>, rawString: out.id },
                      { label: 'Raw Result', value: <code>{out.result}</code>, rawString: out.result },
                      { label: 'Case Closed', value: <span>{out.case_closed ? 'True' : 'False'}</span> },
                    ]}
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
