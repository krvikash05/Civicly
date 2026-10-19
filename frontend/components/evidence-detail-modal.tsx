'use client';

import React, { useEffect, useState } from 'react';
import type { EvidenceDTO } from '../lib/generated/models';
import {
  translateStatus,
  translateAsset,
  translateRole,
  translateDepartment,
  formatEntityDisplayName,
} from '../lib/read/display';
import { TechnicalDetails, CopyableIdentifier } from './technical-details';
import { useDemo } from './demo-connection';
import {displayTime} from '../lib/read/cases';

interface EvidenceDetailModalProps {
  evidenceId: string | null;
  onClose: () => void;
}

export function EvidenceDetailModal({ evidenceId, onClose }: EvidenceDetailModalProps) {
  const demo = useDemo();
  const [evidence, setEvidence] = useState<EvidenceDTO | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!evidenceId) {
      setEvidence(null);
      return;
    }

    let active = true;
    setLoading(true);
    setEvidence(null);
    setError(null);

    demo.connection.client
      .request('GET /api/v1/evidence/{id}', {
        params: { id: evidenceId },
      })
      .then((res) => {
        if (!active) return;
        setEvidence(res.data);
        setLoading(false);
      })
      .catch((err: any) => {
        if (!active) return;
        setError(err.message || 'Failed to load evidence record');
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [evidenceId, demo.connection.client]);

  if (!evidenceId) return null;

  return (
    <div
      className="modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="evidence-modal-title"
      onClick={onClose}
    >
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <header className="modal-header">
          <div>
            <span className="card-type-label">SOURCE RECORD</span>
            <h3 id="evidence-modal-title" style={{ margin: '0.1rem 0 0' }}>Evidence and source details</h3>
          </div>
          <button
            type="button"
            className="close-btn"
            onClick={onClose}
            aria-label="Close evidence details modal"
          >
            ✕
          </button>
        </header>

        <div className="modal-body">
          {loading && <p className="muted" style={{ padding: '1rem' }}>Loading the recorded evidence…</p>}

          {error && (
            <div className="error-banner" role="alert">
              <strong>Error Loading Evidence:</strong> {error}
            </div>
          )}

          {evidence && (
            <div className="evidence-details-stack">
              <div className="evidence-summary-card">
                <span className="summary-label">Recorded summary:</span>
                <p className="summary-prose">{evidence.summary}</p>
              </div>

              <div className="evidence-props-grid">
                <div className="detail-item">
                  <span className="detail-label">Evidence Type:</span>
                  <span className="badge badge-info">{translateStatus(evidence.evidence_type)}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Evidence review status:</span>
                  <span className="badge badge-verified">{translateStatus(evidence.reliability)}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Independent Review:</span>
                  <span
                    className={`badge ${
                      evidence.reviewed ? 'badge-verified' : 'badge-candidate'
                    }`}
                  >
                    {evidence.reviewed ? 'Review recorded' : 'No review recorded'}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Observed:</span>
                  <span className="prop-val">{evidence.observed_at ? displayTime(evidence.observed_at) : 'Not recorded'}</span>
                </div>
              </div>

              <p className="muted">Source: {translateStatus(evidence.source_kind)} · Recorded {displayTime(evidence.recorded_at)}</p>
              {evidence.observation_source && <div className="service-record-card"><h4>Who recorded and reviewed it?</h4><p>{translateDepartment(evidence.observation_source.department_id)} · {translateRole(evidence.observation_source.inspector_id)}</p><p>{evidence.observation_source.reviewed ? `Reviewed by ${translateRole(evidence.observation_source.reviewer_id)}` : 'No independent review recorded'}</p></div>}
              {!!evidence.findings?.length && <section><h4>Recorded observations</h4>{evidence.findings.map(finding=><article key={finding.id} className="service-record-card">
                <strong>{translateStatus(finding.observation.code)}</strong>
                <p>{translateAsset(finding.observation.asset_id)} · {displayTime(finding.observation.observed_at)}</p>
                <p>{translateStatus(finding.observation.result)} · {translateStatus(finding.verification_status)}</p>
                {finding.observation.value!=null && <p>Recorded value: {finding.observation.unit==='boolean' && [0,1].includes(finding.observation.value) ? (finding.observation.value===1?'Yes':'No') : `${finding.observation.value} ${finding.observation.unit??''}`}</p>}
                <p>Method: {translateStatus(finding.observation.method)}</p>
                <TechnicalDetails title="Original observation and identifiers" items={[
                  {label:'Original statement',value:<span>{finding.observation.statement}</span>},
                  {label:'Observation code',value:<code>{finding.observation.code}</code>},
                  {label:'Finding ID',value:<code>{finding.id}</code>,rawString:finding.id},
                ]}/>
              </article>)}</section>}

              {/* Service Record if present */}
              {evidence.service_record && (
                <div className="service-record-card">
                  <h4>Associated Sanitation Service Log</h4>
                  <div className="service-props">
                    <span>Scheduled: <strong>{evidence.service_record.scheduled_at ? displayTime(evidence.service_record.scheduled_at) : 'Not recorded'}</strong></span>
                    <span>Actual Pickup: <strong>{evidence.service_record.actual_at ? displayTime(evidence.service_record.actual_at) : 'Not recorded'}</strong></span>
                    <span>Recorded: <strong>{displayTime(evidence.service_record.recorded_at)}</strong></span>
                  </div>
                </div>
              )}

              {/* Limitations */}
              {evidence.limitations && evidence.limitations.length > 0 && (
                <div className="limitations-card">
                  <h4>What this record does not establish</h4>
                  <ul>
                    {evidence.limitations.map((lim, i) => (
                      <li key={i}>{lim}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Technical Details */}
              <div style={{ marginTop: '0.75rem' }}>
                {(() => {
                  const items = [
                    { label: 'Evidence ID', value: <code>{evidence.id}</code>, rawString: evidence.id },
                    { label: 'Source Kind', value: <code>{evidence.source_kind}</code>, rawString: evidence.source_kind },
                    { label: 'Source Record ID', value: <code>{evidence.source_record_id || 'None'}</code>, rawString: evidence.source_record_id || undefined },
                    { label: 'Recorded At', value: <span>{evidence.recorded_at}</span>, rawString: evidence.recorded_at },
                  ];
                  if (evidence.document_id) {
                    items.push({ label: 'Document Citation ID', value: <code>{evidence.document_id}</code>, rawString: String(evidence.document_id) });
                  }
                  return (
                    <TechnicalDetails
                      title="Technical evidence identifiers"
                      items={items}
                    />
                  );
                })()}
              </div>
            </div>
          )}
        </div>

        <footer className="modal-footer">
          <button type="button" className="button secondary" onClick={onClose}>
            Close
          </button>
        </footer>
      </div>
    </div>
  );
}
