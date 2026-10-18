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
import { formatShortHash } from '../lib/read/plans';
import { displayTime } from '../lib/read/cases';

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
    <div className="monitoring-memory-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* 1. Core Invariant Callout */}
      <div
        className="resolution-distinction-banner"
        style={{
          padding: '1rem 1.25rem',
          borderRadius: '8px',
          backgroundColor: '#fef7e0',
          border: '1px solid #f9ab00',
          color: '#5c3b00',
          fontSize: '0.85rem',
          display: 'flex',
          gap: '0.85rem',
          alignItems: 'flex-start',
        }}
      >
        <div style={{ fontWeight: 700, fontSize: '1.15rem', lineHeight: 1 }}>⚠</div>
        <div>
          <strong style={{ fontSize: '0.95rem' }}>
            Operational Fact: Work Completion is NOT Verified Resolution
          </strong>
          <p style={{ margin: '0.35rem 0 0 0', lineHeight: 1.45 }}>
            Physical completion of field work orders (clearing a drain inlet, patching subgrade, or running a recovery collection)
            records work execution only.
            <strong> Verified resolution</strong> requires subsequent post-intervention monitoring across an independent observation opportunity
            (such as a comparable rainfall event or regular collection cycle) confirming no problem recurrence.
          </p>
        </div>
      </div>

      {/* 2. Cluster Monitoring & Verification Policy */}
      <div
        className="monitoring-section"
        style={{
          padding: '1.25rem',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          backgroundColor: 'var(--surface)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <div>
            <span className="eyebrow" style={{ margin: 0 }}>POST-INTERVENTION MONITORING</span>
            <h3 style={{ margin: '0.15rem 0', fontSize: '1.1rem' }}>
              Problem Cluster {problemClusterId || 'General Context'}
            </h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Independent environmental observation tracking recurrence risks.
            </p>
          </div>
          {clusterMonitoring && (
            <span
              style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                padding: '3px 10px',
                borderRadius: '12px',
                backgroundColor: statusStyle.bg,
                color: statusStyle.color,
                border: `1px solid ${statusStyle.border}`,
              }}
            >
              {clusterMonitoring.status}
            </span>
          )}
        </div>

        {clusterMonitoring ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
            <div
              style={{
                padding: '0.75rem',
                borderRadius: '6px',
                backgroundColor: '#ffffff',
                border: '1px solid var(--border)',
              }}
            >
              <strong style={{ color: '#202124' }}>Verification Policy:</strong>
              <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-secondary)' }}>
                {clusterMonitoring.verification_policy}
              </p>
            </div>

            <div
              style={{
                padding: '0.75rem',
                borderRadius: '6px',
                backgroundColor: '#ffffff',
                border: '1px solid var(--border)',
              }}
            >
              <strong style={{ color: '#202124' }}>Required Verification Checks:</strong>
              {clusterMonitoring.remaining_checks?.length ? (
                <ul style={{ margin: '0.35rem 0 0 0', paddingLeft: '1.2rem', color: 'var(--text-secondary)' }}>
                  {clusterMonitoring.remaining_checks.map((check, idx) => (
                    <li key={idx}>{check}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted text-sm" style={{ margin: '0.2rem 0 0 0' }}>
                  All scheduled verification checks completed.
                </p>
              )}
            </div>

            {clusterMonitoring.outcome_evidence_ids?.length ? (
              <div style={{ fontSize: '0.8rem' }}>
                <strong style={{ color: '#202124' }}>Outcome Evidence Collected: </strong>
                {clusterMonitoring.outcome_evidence_ids.map((evId) => (
                  <button
                    key={evId}
                    type="button"
                    onClick={() => onSelectEvidenceId?.(evId)}
                    style={{
                      background: '#e6f4ea',
                      color: '#137333',
                      border: '1px solid #b7e1cd',
                      borderRadius: '3px',
                      padding: '1px 6px',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                      marginRight: '4px',
                      fontWeight: 600,
                    }}
                  >
                    {evId} ↗
                  </button>
                ))}
              </div>
            ) : null}
          </div>
        ) : (
          <p className="muted text-sm" style={{ margin: '0.5rem 0 0 0' }}>
            No dedicated problem cluster monitoring record registered for this case.
          </p>
        )}
      </div>

      {/* 3. Recurrence & Historical Incident Context */}
      <div
        className="recurrence-section"
        style={{
          padding: '1.25rem',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          backgroundColor: 'var(--surface)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <div>
            <h3 style={{ margin: '0 0 0.15rem 0', fontSize: '1.05rem' }}>Recurrence Context</h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Earlier occurrences linked to this civic defect pattern.
            </p>
          </div>
          <span className="count-pill">{historicalIncidentIds.length}</span>
        </div>

        {historicalIncidentIds.length === 0 ? (
          <div style={{ padding: '0.75rem', borderRadius: '4px', backgroundColor: '#f8f9fa', fontSize: '0.85rem', color: '#5f6368' }}>
            No prior historical incidents registered in this cluster. This is an initial occurrence in the civic ledger.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Prior incidents linked to this recurrence pattern:
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {historicalIncidentIds.map((id) => (
                <span
                  key={id}
                  style={{
                    padding: '2px 8px',
                    borderRadius: '4px',
                    backgroundColor: '#ffffff',
                    border: '1px solid var(--border)',
                    fontSize: '0.8rem',
                    fontFamily: 'monospace',
                  }}
                >
                  {id}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 4. Relevant Municipal Procedures & Cited Knowledge */}
      <div
        className="procedures-section"
        style={{
          padding: '1.25rem',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          backgroundColor: 'var(--surface)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <div>
            <h3 style={{ margin: '0 0 0.15rem 0', fontSize: '1.05rem' }}>
              Sourced Municipal Procedures ({relevantProcedures.length})
            </h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Official standard operating procedures and cited guidelines.
            </p>
          </div>
          <span className="count-pill">{relevantProcedures.length}</span>
        </div>

        {relevantProcedures.length === 0 ? (
          <p className="muted text-sm">No specific procedure documents cited for this category.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {relevantProcedures.map((proc) => {
              const isExpanded = expandedProcedureId === proc.id;

              return (
                <div
                  key={proc.id}
                  style={{
                    padding: '0.85rem 1rem',
                    borderRadius: '6px',
                    border: '1px solid var(--border)',
                    backgroundColor: '#ffffff',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.35rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <div>
                      <span
                        style={{
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          color: '#5f6368',
                        }}
                      >
                        {proc.owner_department_id}
                      </span>
                      <h4 style={{ margin: '0.1rem 0', fontSize: '0.95rem' }}>{proc.title}</h4>
                      <p className="muted text-sm" style={{ margin: 0 }}>
                        ID: <code>{proc.procedure_id || proc.id}</code> &bull; Version: <strong>v{proc.version}</strong>
                      </p>
                    </div>

                    <div style={{ display: 'flex', gap: '0.35rem', alignItems: 'center' }}>
                      <span
                        style={{
                          fontSize: '0.68rem',
                          fontWeight: 600,
                          padding: '2px 6px',
                          borderRadius: '4px',
                          backgroundColor: '#f1f3f4',
                          color: '#5f6368',
                          border: '1px solid #dadce0',
                        }}
                        title="Treated as untrusted domain evidence, not tool instructions."
                      >
                        UNTRUSTED AS INSTRUCTIONS
                      </span>
                      <span
                        style={{
                          fontSize: '0.68rem',
                          fontWeight: 600,
                          padding: '2px 6px',
                          borderRadius: '4px',
                          backgroundColor: '#e8f0fe',
                          color: '#1a73e8',
                          border: '1px solid #aecbfa',
                        }}
                      >
                        {proc.assertion_status}
                      </span>
                    </div>
                  </div>

                  <div style={{ fontSize: '0.75rem', color: '#5f6368', marginTop: '0.2rem' }}>
                    <span>Checksum: <code title={proc.sha256}>{formatShortHash(proc.sha256)}</code></span> &bull;{' '}
                    <span>Effective: {displayTime(proc.effective_from)}</span>
                  </div>

                  {proc.citations?.length > 0 && (
                    <div style={{ marginTop: '0.35rem' }}>
                      <button
                        type="button"
                        onClick={() => setExpandedProcedureId(isExpanded ? null : proc.id)}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: 'var(--brand)',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                          padding: 0,
                        }}
                      >
                        {isExpanded ? 'Hide Citation Excerpt ▲' : 'View Citation Excerpt ▼'}
                      </button>

                      {isExpanded && (
                        <div
                          style={{
                            marginTop: '0.5rem',
                            padding: '0.6rem 0.75rem',
                            backgroundColor: '#f8f9fa',
                            borderRadius: '4px',
                            border: '1px solid #e8eaed',
                            fontSize: '0.8rem',
                          }}
                        >
                          <blockquote
                            style={{
                              margin: 0,
                              paddingLeft: '0.5rem',
                              borderLeft: '2px solid #bdc1c6',
                              fontStyle: 'italic',
                              color: '#3c4043',
                            }}
                          >
                            "{formatQuoteExcerpt(proc.citations[0].quote_excerpt, 320)}"
                          </blockquote>
                          {proc.citations[0].passage_location && (
                            <div style={{ marginTop: '0.35rem', fontSize: '0.7rem', color: '#5f6368' }}>
                              Passage: <code>{proc.citations[0].passage_location}</code>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 5. Case Memory & Evaluated Outcomes */}
      <div
        className="case-memory-section"
        style={{
          padding: '1.25rem',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          backgroundColor: 'var(--surface)',
        }}
      >
        <h3 style={{ margin: '0 0 0.15rem 0', fontSize: '1.05rem' }}>Case Memory &amp; Outcomes</h3>
        <p className="muted text-sm" style={{ margin: '0 0 0.75rem 0' }}>
          Long-term learning and closed resolution assessments.
        </p>

        {memory ? (
          <div
            style={{
              padding: '0.85rem 1rem',
              borderRadius: '6px',
              backgroundColor: '#ffffff',
              border: '1px solid var(--border)',
              fontSize: '0.85rem',
            }}
          >
            <div><strong>Memory Context ID:</strong> <code>{memory.id}</code></div>
            <div><strong>Type:</strong> {memory.memory_type}</div>
            <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-secondary)' }}>{memory.summary}</p>
            {memory.gaps?.length ? (
              <div style={{ marginTop: '0.35rem', fontSize: '0.8rem', color: '#5f6368' }}>
                <strong>Evidence Gaps:</strong> {memory.gaps.join(', ')}
              </div>
            ) : null}
          </div>
        ) : (
          <div
            style={{
              padding: '1rem',
              borderRadius: '6px',
              backgroundColor: '#f8f9fa',
              border: '1px dashed #dadce0',
              textAlign: 'center',
            }}
          >
            <p style={{ margin: '0 0 0.25rem 0', fontWeight: 600, fontSize: '0.9rem', color: '#3c4043' }}>
              Case Memory Pending Verified Closure
            </p>
            <p className="muted text-sm" style={{ margin: 0, maxWidth: '500px', marginLeft: 'auto', marginRight: 'auto' }}>
              Permanent case memory records are compiled upon final outcome evaluation and verified case closure.
              While this case remains in planning or active execution, decisions are grounded in active cluster monitoring and cited standard procedures.
            </p>
          </div>
        )}

        {outcomes.length > 0 && (
          <div style={{ marginTop: '1rem' }}>
            <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.95rem' }}>Evaluated Outcomes ({outcomes.length})</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {outcomes.map((out) => (
                <div
                  key={out.id}
                  style={{
                    padding: '0.65rem 0.85rem',
                    borderRadius: '4px',
                    border: '1px solid var(--border)',
                    backgroundColor: '#ffffff',
                    fontSize: '0.8rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <strong>Outcome {out.id}</strong>
                    <span style={{ fontWeight: 600, color: out.case_closed ? '#137333' : '#b06000' }}>
                      {out.case_closed ? 'CASE CLOSED' : 'MONITORING CONTINUES'}
                    </span>
                  </div>
                  <div>Result: {out.result}</div>
                  <div>Evaluated: {displayTime(out.evaluated_at)}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
