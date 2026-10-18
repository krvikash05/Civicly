'use client';

import React, { useEffect, useState } from 'react';
import type { EvidenceDTO } from '../lib/generated/models';
import { useDemo } from './demo-connection';

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
        console.error('Failed to load evidence details:', err);
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
          <h3 id="evidence-modal-title">Attributed Evidence: <code>{evidenceId}</code></h3>
          <button
            type="button"
            className="close-btn"
            onClick={onClose}
            aria-label="Close modal"
          >
            ✕
          </button>
        </header>

        <div className="modal-body">
          {loading && <p className="muted">Fetching authoritative evidence from backend...</p>}

          {error && (
            <div className="error-banner">
              <strong>Error Loading Evidence:</strong> {error}
            </div>
          )}

          {evidence && (
            <div className="evidence-details-grid">
              <div className="detail-item">
                <span className="detail-label">Evidence Type:</span>
                <span className="badge badge-info">{evidence.evidence_type}</span>
              </div>

              <div className="detail-item">
                <span className="detail-label">Reliability:</span>
                <span className="badge badge-verified">{evidence.reliability}</span>
              </div>

              <div className="detail-item">
                <span className="detail-label">Source Kind:</span>
                <code>{evidence.source_kind}</code>
              </div>

              <div className="detail-item">
                <span className="detail-label">Source Record ID:</span>
                <code>{evidence.source_record_id}</code>
              </div>

              <div className="detail-item">
                <span className="detail-label">Observed At:</span>
                <span>{evidence.observed_at || '—'}</span>
              </div>

              <div className="detail-item">
                <span className="detail-label">Recorded At:</span>
                <span>{evidence.recorded_at}</span>
              </div>

              <div className="detail-item full-width">
                <span className="detail-label">Summary:</span>
                <p className="evidence-summary-text">{evidence.summary}</p>
              </div>

              <div className="detail-item">
                <span className="detail-label">Independent Review:</span>
                <span>
                  {evidence.reviewed ? (
                    <span className="badge badge-verified">REVIEWED & ATTESTED</span>
                  ) : (
                    <span className="badge badge-candidate">UNREVIEWED / RAW</span>
                  )}
                </span>
              </div>

              {evidence.document_id && (
                <div className="detail-item">
                  <span className="detail-label">Document Citation:</span>
                  <code>{evidence.document_id}</code>
                </div>
              )}

              {/* Service Record if present */}
              {evidence.service_record && (
                <div className="detail-item full-width service-record-card">
                  <h4>Associated Service Record</h4>
                  <div className="service-props">
                    <span>Pickup ID: <code>{evidence.service_record.pickup_id}</code></span>
                    <span>Report Evidence ID: <code>{evidence.service_record.report_evidence_id}</code></span>
                  </div>
                </div>
              )}

              {/* Limitations */}
              {evidence.limitations && evidence.limitations.length > 0 && (
                <div className="detail-item full-width limitations-card">
                  <h4>Recorded Data Limitations</h4>
                  <ul>
                    {evidence.limitations.map((lim: string, i: number) => (
                      <li key={i}>{lim}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        <footer className="modal-footer">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </footer>
      </div>
    </div>
  );
}
