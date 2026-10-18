'use client';

import { useState } from 'react';
import { MUNICIPAL_OPERATORS, OperatorProfile } from '../lib/read/roles';
import { useDemo } from './demo-connection';
import { Icon } from './icons';

interface RoleGovernanceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function RoleGovernanceModal({ isOpen, onClose }: RoleGovernanceModalProps) {
  const demo = useDemo();
  const [selectedOperatorId, setSelectedOperatorId] = useState<string>('OP-ANALYST');

  if (!isOpen) return null;

  const currentOperatorId = demo.identity?.account.id ?? 'OP-ANALYST';
  const selectedProfile: OperatorProfile =
    MUNICIPAL_OPERATORS[selectedOperatorId] ?? MUNICIPAL_OPERATORS['OP-ANALYST'];

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="role-governance-title"
    >
      <div className="modal-card role-modal-card">
        <div className="modal-header">
          <div>
            <span className="badge badge-verified" style={{ marginBottom: 6, display: 'inline-block' }}>
              MUNICIPAL GOVERNANCE &amp; RBAC
            </span>
            <h2 id="role-governance-title" style={{ margin: 0, fontSize: '1.25rem' }}>
              Operator Roles &amp; Authority Boundaries
            </h2>
          </div>
          <button
            type="button"
            className="modal-close"
            onClick={onClose}
            aria-label="Close role governance dialog"
          >
            ✕
          </button>
        </div>

        {/* Security & Invariant Notice */}
        <div className="governance-invariant-box" role="note">
          <div className="invariant-badge">
            <Icon name="check" size={14} /> SECURITY &amp; SEPARATION OF DUTIES
          </div>
          <p>
            Civicly operates without a judge sign-in form. An authorized <strong>Analyst</strong> account
            (<code>OP-ANALYST</code>) is automatically negotiated in-memory. In accordance with
            municipal governance invariants (<strong>R13, R15</strong>), analysts can investigate cases and
            draft plans, but <strong>cannot self-approve intervention</strong>. Approval requires an
            independent municipal <strong>Approver</strong> (<code>OP-APPROVER</code>).
          </p>
        </div>

        {/* Operator Selector Tabs */}
        <div className="operator-tabs-container">
          <label className="operator-tabs-label" id="operator-select-label">
            Select Municipal Operator to Inspect:
          </label>
          <div
            className="operator-tabs"
            role="tablist"
            aria-labelledby="operator-select-label"
          >
            {Object.values(MUNICIPAL_OPERATORS).map((op) => {
              const isCurrent = op.id === currentOperatorId;
              const isSelected = op.id === selectedOperatorId;
              return (
                <button
                  key={op.id}
                  type="button"
                  role="tab"
                  aria-selected={isSelected}
                  className={`operator-tab ${isSelected ? 'active' : ''} ${isCurrent ? 'current-session' : ''}`}
                  onClick={() => setSelectedOperatorId(op.id)}
                >
                  <span className="op-id">{op.id}</span>
                  <span className="op-role">{op.role}</span>
                  {isCurrent && <span className="current-badge">Active Session</span>}
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Operator Detail Card */}
        <div className="operator-detail-card" role="tabpanel">
          <div className="detail-top">
            <div>
              <h3 style={{ margin: '0 0 4px', fontSize: '1.1rem' }}>{selectedProfile.title}</h3>
              <p className="detail-dept">
                Department: <strong>{selectedProfile.departmentName}</strong> (<code>{selectedProfile.departmentId}</code>)
              </p>
            </div>
            <span className="role-tag-pill">{selectedProfile.role}</span>
          </div>

          <p className="detail-desc">{selectedProfile.description}</p>

          <div className="powers-grid">
            <div className="power-column allowed">
              <h4>
                <span className="indicator-dot allowed" /> Authorized Capabilities
              </h4>
              <ul>
                {selectedProfile.capabilities.map((cap, idx) => (
                  <li key={idx}>
                    <span className="check-icon">✓</span> {cap}
                  </li>
                ))}
              </ul>
            </div>

            <div className="power-column prohibited">
              <h4>
                <span className="indicator-dot prohibited" /> Governance Boundaries
              </h4>
              <ul>
                {selectedProfile.boundaries.map((bnd, idx) => (
                  <li key={idx}>
                    <span className="prohibited-icon">✕</span> {bnd}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="modal-footer" style={{ marginTop: 20 }}>
          <button type="button" className="button secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
