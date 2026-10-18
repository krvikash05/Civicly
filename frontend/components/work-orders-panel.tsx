'use client';

import React, { useState, useEffect } from 'react';
import type { WorkOrderDTO, InspectionDTO } from '../lib/generated/models';
import { getStatusBadgeStyle } from '../lib/read/plans';
import { useDemo } from './demo-connection';

interface WorkOrdersPanelProps {
  investigationId: string;
  planId?: string | null;
  pendingInspectionIds?: string[];
  workOrders: WorkOrderDTO[];
  onSelectEvidenceId?: (id: string) => void;
  onRefetch?: () => void;
}

export function WorkOrdersPanel({
  investigationId,
  planId,
  pendingInspectionIds = [],
  workOrders = [],
  onSelectEvidenceId,
  onRefetch,
}: WorkOrdersPanelProps) {
  const demo = useDemo();
  const [inspections, setInspections] = useState<InspectionDTO[]>([]);
  const [loadingInspections, setLoadingInspections] = useState(false);

  // Load inspections linked to investigation
  useEffect(() => {
    if (!pendingInspectionIds || pendingInspectionIds.length === 0) {
      setInspections([]);
      return;
    }

    let isCancelled = false;
    async function loadInspections() {
      if (demo.status !== 'connected') return;
      setLoadingInspections(true);

      const results: InspectionDTO[] = [];
      for (const id of pendingInspectionIds) {
        try {
          const res = await demo.connection.client.request(
            'GET /api/v1/inspections/{id}',
            { params: { id } }
          );
          if (res.data) results.push(res.data);
        } catch (e) {
          // Ignore individual inspection fetch errors
        }
      }

      if (!isCancelled) {
        setInspections(results);
        setLoadingInspections(false);
      }
    }

    loadInspections();
    return () => {
      isCancelled = true;
    };
  }, [pendingInspectionIds.join(','), demo.status]);

  // Filter work orders that belong to the current plan if planId is provided
  const relevantWorkOrders = planId
    ? workOrders.filter((wo) => wo.plan_id === planId)
    : workOrders;

  return (
    <div className="work-orders-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* 1. Critical Invariant Callout */}
      <div
        className="resolution-distinction-banner"
        style={{
          padding: '0.85rem 1rem',
          borderRadius: '6px',
          backgroundColor: '#fef7e0',
          border: '1px solid #f9ab00',
          color: '#5c3b00',
          fontSize: '0.85rem',
          display: 'flex',
          gap: '0.75rem',
          alignItems: 'flex-start',
        }}
      >
        <div style={{ fontWeight: 700, fontSize: '1rem', lineHeight: 1 }}>⚠</div>
        <div>
          <strong>Operational Distinction: Work Completion is NOT Verified Resolution</strong>
          <p style={{ margin: '0.25rem 0 0 0', lineHeight: 1.4 }}>
            Physical completion of a work order records only that department crews performed the designated action.
            Long-term resolution cannot be assumed until independent post-intervention monitoring confirms the problem does not recur under comparable civic conditions (verified in Stage 6).
          </p>
        </div>
      </div>

      {/* 2. Field Inspections Section */}
      <div
        className="inspections-section"
        style={{
          padding: '1.25rem',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          backgroundColor: 'var(--surface)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <div>
            <h3 style={{ margin: '0 0 0.25rem 0', fontSize: '1.05rem' }}>Field Inspections</h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Physical verifications requested to establish or refute competing hypotheses.
            </p>
          </div>
          <span className="count-pill">{pendingInspectionIds.length}</span>
        </div>

        {loadingInspections ? (
          <p className="muted text-sm">Loading field inspection records...</p>
        ) : inspections.length === 0 ? (
          <div style={{ padding: '0.75rem', borderRadius: '4px', backgroundColor: '#f8f9fa', fontSize: '0.85rem', color: '#5f6368' }}>
            No pending field inspections currently registered for this case.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            {inspections.map((ins) => {
              const statusStyle = getStatusBadgeStyle(ins.status);

              return (
                <div
                  key={ins.id}
                  style={{
                    padding: '0.75rem 1rem',
                    borderRadius: '6px',
                    border: '1px solid var(--border)',
                    backgroundColor: '#ffffff',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.35rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong>{ins.id}</strong>
                    <span
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        padding: '2px 8px',
                        borderRadius: '10px',
                        backgroundColor: statusStyle.bg,
                        color: statusStyle.color,
                        border: `1px solid ${statusStyle.border}`,
                      }}
                    >
                      {ins.status}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    <span>Department: <strong>{ins.department_id}</strong></span> &bull;{' '}
                    <span>Target Assets: <code>{ins.asset_ids.join(', ') || 'General'}</code></span>
                  </div>

                  {ins.evidence_ids?.length > 0 && (
                    <div style={{ marginTop: '0.25rem', fontSize: '0.8rem' }}>
                      <span className="muted">Collected Evidence: </span>
                      {ins.evidence_ids.map((evId) => (
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
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 3. Authorized Work Orders Section */}
      <div
        className="work-orders-section"
        style={{
          padding: '1.25rem',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          backgroundColor: 'var(--surface)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <div>
            <h3 style={{ margin: '0 0 0.25rem 0', fontSize: '1.05rem' }}>Dispatched Work Orders</h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Physical remediation operations authorized by municipal approval.
            </p>
          </div>
          <span className="count-pill">{relevantWorkOrders.length}</span>
        </div>

        {relevantWorkOrders.length === 0 ? (
          <div
            style={{
              padding: '1.25rem',
              borderRadius: '6px',
              backgroundColor: '#f8f9fa',
              border: '1px dashed #dadce0',
              textAlign: 'center',
            }}
          >
            <p style={{ margin: '0 0 0.35rem 0', fontWeight: 600, fontSize: '0.9rem', color: '#3c4043' }}>
              No Work Orders Dispatched Yet
            </p>
            <p className="muted text-sm" style={{ margin: 0, maxWidth: '520px', marginLeft: 'auto', marginRight: 'auto' }}>
              Per backend creation guards, work orders cannot exist in draft state. They are generated only after formal approval of the plan by an authorized municipal approver (Role: <code>APPROVER</code>).
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {relevantWorkOrders.map((wo) => {
              const statusStyle = getStatusBadgeStyle(wo.status);

              return (
                <div
                  key={wo.id}
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
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <span className="eyebrow" style={{ margin: 0 }}>WORK ORDER</span>
                      <h4 style={{ margin: '0.1rem 0', fontSize: '0.95rem' }}>{wo.id}</h4>
                    </div>
                    <span
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        padding: '2px 8px',
                        borderRadius: '10px',
                        backgroundColor: statusStyle.bg,
                        color: statusStyle.color,
                        border: `1px solid ${statusStyle.border}`,
                      }}
                    >
                      {wo.status}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    <span>Task: <code>{wo.task_id}</code></span> &bull;{' '}
                    <span>Department: <strong>{wo.department_id}</strong></span> &bull;{' '}
                    <span>Assignee: <strong>{wo.assignee_id}</strong></span>
                  </div>

                  <div style={{ fontSize: '0.75rem', color: '#5f6368', marginTop: '0.2rem' }}>
                    <span>Authorized By: <strong>{wo.authorized_by}</strong></span> &bull;{' '}
                    <span>Execution Mode: <em>{wo.execution_mode || 'SIMULATED'}</em></span> &bull;{' '}
                    <span>
                      Resolution Verified:{' '}
                      <strong style={{ color: wo.resolution_verified ? '#137333' : '#b06000' }}>
                        {wo.resolution_verified ? 'YES' : 'PENDING MONITORING'}
                      </strong>
                    </span>
                  </div>

                  {wo.status === 'BLOCKED' && (
                    <div
                      style={{
                        marginTop: '0.5rem',
                        padding: '0.5rem',
                        borderRadius: '4px',
                        backgroundColor: '#fce8e6',
                        color: '#c5221f',
                        fontSize: '0.75rem',
                        border: '1px solid #f5c2c7',
                      }}
                    >
                      <strong>Execution Blocked: </strong> Field crews reported an impediment preventing task completion.
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
