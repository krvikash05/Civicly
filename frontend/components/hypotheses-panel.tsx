'use client';

import React from 'react';
import type { HypothesisPage, HypothesisDTO, PlanDTO } from '../lib/generated/models';
import {
  translateCauseCode,
  translateAssessment,
  formatEntityDisplayName,
} from '../lib/read/display';
import { TechnicalDetails, CopyableIdentifier } from './technical-details';

interface HypothesesPanelProps {
  hypothesisPage: HypothesisPage | null;
  plan?: PlanDTO | null;
  onSelectEvidenceId?: (id: string) => void;
  onSelectAssetId?: (id: string) => void;
}

export function HypothesesPanel({
  hypothesisPage,
  plan,
  onSelectEvidenceId,
  onSelectAssetId,
}: HypothesesPanelProps) {
  if (!hypothesisPage || !hypothesisPage.items || hypothesisPage.items.length === 0) {
    return (
      <div className="empty-panel-notice">
        <p className="muted">
          No differential hypotheses have been formulated for this investigation yet.
        </p>
        <p className="muted text-sm" style={{ marginTop: '0.4rem' }}>
          As the investigation agent queries the FalkorDB knowledge graph and analyzes observations,
          competing hypotheses will appear here with evidence assessments.
        </p>
      </div>
    );
  }

  // Pre-index plan evaluation basis to determine Plan Coverage independently from Evidence Assessment
  const planBasisMap = new Map<string, { addressed: boolean; reason: string }>();
  if (plan?.draft?.basis && Array.isArray(plan.draft.basis)) {
    for (const b of plan.draft.basis) {
      planBasisMap.set(b.hypothesis_id, {
        addressed: Boolean(b.addressed),
        reason: b.reason || '',
      });
    }
  }

  return (
    <div className="hypotheses-panel">
      <div className="panel-intro">
        <h3>Competing Hypotheses & Differential Diagnostics</h3>
        <p className="muted">
          The agent formulates competing hypotheses based on observed defect patterns. Sourced
          evidence independently supports or contradicts each hypothesis. Hypotheses requiring
          additional physical verification list missing inspection evidence.
        </p>
      </div>

      <div className="hypotheses-grid">
        {hypothesisPage.items.map((hyp: HypothesisDTO) => {
          const cause = translateCauseCode(hyp.cause_code);
          const assessment = translateAssessment(hyp.status);
          const planBasis = planBasisMap.get(hyp.id);

          // Plan coverage is distinct from evidence assessment
          const isAddressedInPlan = planBasis ? planBasis.addressed : null;

          const techItems = [
            {
              label: 'Hypothesis ID',
              value: <code>{hyp.id}</code>,
              rawString: hyp.id,
            },
            {
              label: 'Cause Code',
              value: <code>{hyp.cause_code}</code>,
              rawString: hyp.cause_code,
            },
            {
              label: 'Raw Status',
              value: <code>{hyp.status}</code>,
              rawString: hyp.status,
            },
            {
              label: 'Current Assessment ID',
              value: <code>{hyp.current_assessment_id || 'Not recorded'}</code>,
              rawString: hyp.current_assessment_id || undefined,
            },
            ...(hyp.assessment_history?.length
              ? [
                  {
                    label: 'Assessment Revisions',
                    value: <span>{hyp.assessment_history.length} recorded</span>,
                  },
                ]
              : []),
          ];

          return (
            <article key={hyp.id} className="hypothesis-card">
              {/* Header with wrapped tags and clear hierarchy */}
              <header className="hyp-header">
                <div className="hyp-heading-group">
                  <span className="eyebrow-label">POSSIBLE CAUSE</span>
                  <h4 className="hyp-title">{cause.title}</h4>
                </div>

                <div className="hyp-badges-row">
                  {/* Evidence Assessment Badge */}
                  <span
                    className={`badge ${assessment.badgeClass}`}
                    title={assessment.description}
                  >
                    Assessment: {assessment.label}
                  </span>

                  {/* Separate Plan Coverage Badge */}
                  {isAddressedInPlan !== null ? (
                    <span
                      className={`badge ${
                        isAddressedInPlan ? 'badge-plan-addressed' : 'badge-plan-unaddressed'
                      }`}
                    >
                      {isAddressedInPlan ? 'Addressed in plan' : 'Not addressed in plan'}
                    </span>
                  ) : (
                    <span className="badge badge-plan-pending">Plan pending draft</span>
                  )}
                </div>
              </header>

              <div className="hyp-body">
                {/* Short supported contextual explanation */}
                <p className="hyp-explanation">{cause.explanation}</p>

                {/* Attributed original statement */}
                {hyp.statement && hyp.statement !== cause.title && (
                  <div className="hyp-statement-box">
                    <span className="box-label">Original attributed statement:</span>
                    <p className="hyp-statement-text">{hyp.statement}</p>
                  </div>
                )}

                {/* Suspected Assets */}
                {hyp.suspected_asset_ids && hyp.suspected_asset_ids.length > 0 && (
                  <div className="hyp-section">
                    <span className="section-label">Suspected Assets ({hyp.suspected_asset_ids.length}):</span>
                    <div className="chips-row">
                      {hyp.suspected_asset_ids.map((aid: string) => {
                        const nameInfo = formatEntityDisplayName({ id: aid, kind: 'InfrastructureAsset' });
                        return (
                          <button
                            key={aid}
                            type="button"
                            className="chip chip-asset"
                            onClick={() => onSelectAssetId?.(aid)}
                            title={`Select ${aid}`}
                          >
                            <span className="chip-label">{nameInfo.primary}</span>
                            <span className="chip-sub">({nameInfo.shortId})</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Supporting Observations */}
                <div className="hyp-section">
                  <span className="section-label text-success">
                    Supporting observations ({hyp.supporting_evidence_ids?.length || 0}):
                  </span>
                  <div className="chips-row">
                    {hyp.supporting_evidence_ids && hyp.supporting_evidence_ids.length > 0 ? (
                      hyp.supporting_evidence_ids.map((eid: string) => (
                        <button
                          key={eid}
                          type="button"
                          className="chip chip-evidence"
                          onClick={() => onSelectEvidenceId?.(eid)}
                          title={`Inspect evidence ${eid}`}
                        >
                          <span className="chip-label">Evidence</span>
                          <span className="chip-sub">({eid.length > 12 ? `${eid.slice(0, 8)}…` : eid})</span>
                        </button>
                      ))
                    ) : (
                      <span className="muted text-sm">None recorded</span>
                    )}
                  </div>
                </div>

                {/* Contradicting Observations */}
                <div className="hyp-section">
                  <span className="section-label text-danger">
                    Contradicting observations ({hyp.contradicting_evidence_ids?.length || 0}):
                  </span>
                  <div className="chips-row">
                    {hyp.contradicting_evidence_ids && hyp.contradicting_evidence_ids.length > 0 ? (
                      hyp.contradicting_evidence_ids.map((eid: string) => (
                        <button
                          key={eid}
                          type="button"
                          className="chip chip-danger"
                          onClick={() => onSelectEvidenceId?.(eid)}
                          title={`Inspect evidence ${eid}`}
                        >
                          <span className="chip-label">Evidence</span>
                          <span className="chip-sub">({eid.length > 12 ? `${eid.slice(0, 8)}…` : eid})</span>
                        </button>
                      ))
                    ) : (
                      <span className="muted text-sm">None recorded</span>
                    )}
                  </div>
                </div>

                {/* What remains uncertain / Missing Evidence */}
                {hyp.missing_evidence && hyp.missing_evidence.length > 0 ? (
                  <div className="hyp-section missing-section">
                    <span className="section-label text-warning">
                      What remains uncertain (Missing evidence):
                    </span>
                    <ul className="missing-list">
                      {hyp.missing_evidence.map((me: string, i: number) => (
                        <li key={i}>{me}</li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <div className="hyp-section uncertain-resolved">
                    <span className="section-label text-muted">
                      What remains uncertain:
                    </span>
                    <p className="text-sm muted" style={{ margin: 0 }}>
                      No missing physical evidence checklists recorded.
                    </p>
                  </div>
                )}

                {/* Plan Basis Rationale if evaluated in plan */}
                {planBasis && planBasis.reason && (
                  <div className="hyp-section plan-basis-note">
                    <span className="section-label">Remediation plan consideration:</span>
                    <p className="text-sm" style={{ margin: 0, color: '#33483c' }}>
                      {planBasis.reason}
                    </p>
                  </div>
                )}

                {/* Expandable Technical Details with Copy Buttons */}
                <TechnicalDetails items={techItems} />
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}
