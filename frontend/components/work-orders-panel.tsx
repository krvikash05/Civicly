'use client';

import React, { useState, useEffect } from 'react';
import type { WorkOrderDTO, InspectionDTO, PlanDTO } from '../lib/generated/models';
import { getStatusBadgeStyle } from '../lib/read/plans';
import {
  translateStatus,
  translateActionType,
  translateDepartment,
  translateRole,
  formatEntityDisplayName,
} from '../lib/read/display';
import { TechnicalDetails, CopyableIdentifier } from './technical-details';
import { useDemo } from './demo-connection';
import {taskForOrder,describeWork} from '../lib/read/workflow';

interface WorkOrdersPanelProps {
  investigationId: string;
  planId?: string | null;
  plan?: PlanDTO | null;
  pendingInspectionIds?: string[];
  workOrders: WorkOrderDTO[];
  onSelectEvidenceId?: (id: string) => void;
  onRefetch?: () => void;
}

export function WorkOrdersPanel({
  investigationId,
  planId,
  plan,
  pendingInspectionIds = [],
  workOrders = [],
  onSelectEvidenceId,
  onRefetch,
}: WorkOrdersPanelProps) {
  const demo = useDemo();
  const [inspections, setInspections] = useState<InspectionDTO[]>([]);
  const [loadingInspections, setLoadingInspections] = useState(false);
  const [inspectionError,setInspectionError]=useState<string|null>(null);

  // Load inspections linked to investigation
  useEffect(() => {
    if (!pendingInspectionIds || pendingInspectionIds.length === 0) {
      setInspections([]);
      return;
    }

    let isCancelled = false;
    async function loadInspections() {
      if (demo.status !== 'connected') return;
      setLoadingInspections(true);setInspectionError(null);

      const results: InspectionDTO[] = [];
      for (const id of pendingInspectionIds) {
        try {
          const res = await demo.connection.client.request(
            'GET /api/v1/inspections/{id}',
            { params: { id } }
          );
          if (res.data) results.push(res.data);
        } catch {
          if(!isCancelled)setInspectionError('Some inspection records could not be loaded. Missing records are not proof that no inspection exists.');
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

  const relevantWorkOrders = planId
    ? workOrders.filter((wo) => wo.plan_id === planId)
    : [];

  return (
    <div className="work-orders-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* 1. Critical Invariant Callout */}

      {/* 2. Field Inspections Section */}
      <section className="inspections-section">
        <div className="section-header-row">
          <div>
            <h3 className="section-title">Field Inspections</h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Pending checks to gather evidence about the possible cause.
            </p>
          </div>
          <span className="count-pill">{pendingInspectionIds.length}</span>
        </div>

        {inspectionError && <p role="alert">{inspectionError}</p>}
        {loadingInspections ? (
          <p className="muted text-sm" style={{ padding: '0.75rem' }}>Loading field inspection records…</p>
        ) : inspections.length === 0 ? (
          <div className="empty-boxed-notice">
            No pending field inspections currently registered for this case.
          </div>
        ) : (
          <div className="cards-stack">
            {inspections.map((ins) => {
              const statusStyle = getStatusBadgeStyle(ins.status);
              const deptName = translateDepartment(ins.department_id);

              return (
                <article key={ins.id} className="inspection-card">
                  <header className="card-top-row">
                    <div>
                      <span className="card-type-label">FIELD INSPECTION</span>
                      <h4 className="card-main-title">{deptName}</h4>
                    </div>
                    <span
                      className="badge"
                      style={{
                        backgroundColor: statusStyle.bg,
                        color: statusStyle.color,
                        borderColor: statusStyle.border,
                      }}
                    >
                      {translateStatus(ins.status)}
                    </span>
                  </header>

                  <div className="card-content-body">
                    {ins.asset_ids && ins.asset_ids.length > 0 && (
                      <div className="prop-line">
                        <span className="prop-name">Target Assets:</span>
                        <div className="chips-row">
                          {ins.asset_ids.map((aid) => (
                            <span key={aid} className="chip chip-asset">
                              {formatEntityDisplayName({ id: aid, kind: 'InfrastructureAsset' }).primary}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {(ins as any).findings && (
                      <div className="findings-summary-box">
                        <span className="box-label">Inspection Findings:</span>
                        <p className="findings-text">{(ins as any).findings}</p>
                      </div>
                    )}

                    {ins.evidence_ids && ins.evidence_ids.length > 0 && (
                      <div className="prop-line">
                        <span className="prop-name">Linked Evidence:</span>
                        <div className="chips-row">
                          {ins.evidence_ids.map((eid) => (
                            <button
                              key={eid}
                              type="button"
                              className="chip chip-evidence"
                              onClick={() => onSelectEvidenceId?.(eid)}
                            >
                              Evidence ({eid.slice(-4)})
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    <TechnicalDetails
                      title="Technical inspection references"
                      items={[
                        { label: 'Inspection ID', value: <code>{ins.id}</code>, rawString: ins.id },
                        { label: 'Department ID', value: <code>{ins.department_id}</code>, rawString: ins.department_id },
                        { label: 'Raw Status', value: <code>{ins.status}</code>, rawString: ins.status },
                      ]}
                    />
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>

      {/* 3. Authorized Work Orders Section */}
      <section className="work-orders-section">
        <div className="section-header-row">
          <div>
            <h3 className="section-title">Authorized Work Orders</h3>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Simulated work authorized under an approved plan. Follow-up verification is shown separately.
            </p>
          </div>
          <span className="count-pill">{relevantWorkOrders.length}</span>
        </div>

        {relevantWorkOrders.length === 0 ? (
          <div className="empty-boxed-notice">
            No work orders for this investigation were returned in the loaded records. An approved plan and satisfied prerequisites are required before work can be authorized.
          </div>
        ) : (
          <div className="cards-stack">
            {relevantWorkOrders.map((wo, idx) => {
              const statusStyle = getStatusBadgeStyle(wo.status);
              const matchedTask = taskForOrder(plan,wo);
              const rawAction = matchedTask?.action_type;
              const actionTitle = rawAction
                ? translateActionType(rawAction)
                : `Remediation Work Order #${idx + 1}`;
              const deptName = translateDepartment(wo.department_id);
              const assigneeName = translateRole(wo.assignee_id || (wo as any).assigned_to);
              const prerequisites=(matchedTask?.depends_on ?? []).map(id=>plan?.draft.tasks.find(t=>t.id===id)).filter(Boolean);

              return (
                <article key={wo.id} className="work-order-card">
                  <header className="card-top-row">
                    <div>
                      <span className="card-type-label">AUTHORIZED WORK ORDER #{idx + 1}</span>
                      <h4 className="card-main-title">{actionTitle}</h4>
                      <p className="card-subtitle-dept">
                        {deptName}
                      </p>
                    </div>
                    <span
                      className="badge"
                      style={{
                        backgroundColor: statusStyle.bg,
                        color: statusStyle.color,
                        borderColor: statusStyle.border,
                      }}
                    >
                      {translateStatus(wo.status)}
                    </span>
                  </header>

                  <div className="card-content-body">
                    <p className="work-order-description">{describeWork(rawAction)}</p>
                    {prerequisites.length>0 && <p className="work-order-prerequisite"><strong>Required first:</strong> {prerequisites.map(t=>translateActionType(t!.action_type)).join('; ')}. The plan also defines the evidence needed before this work can begin.</p>}
                    <div className="prop-line">
                      <span className="prop-name">Responsible lead</span>
                      <span className="prop-val font-semibold">{assigneeName}</span>
                    </div>

                    {!!matchedTask?.target_ids.length && (
                      <div className="prop-line">
                        <span className="prop-name">Work location / asset</span>
                        <div className="chips-row">
                          {matchedTask!.target_ids.map((tid) => (
                            <span key={tid} className="chip chip-asset">
                              {formatEntityDisplayName({ id: tid, kind: 'InfrastructureAsset' }).primary}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {(wo as any).execution_blocker && (
                      <div className="blocker-alert" role="alert">
                        <strong>Deployment Blocker:</strong> {(wo as any).execution_blocker}
                      </div>
                    )}

                    <div className="work-order-outcome"><span className="prop-name">Follow-up</span><span>{wo.resolution_verified?'Resolution verified by follow-up':wo.latest_assessment_status?translateStatus(wo.latest_assessment_status):'No follow-up assessment recorded'}</span></div>
                    <TechnicalDetails
                      title="Technical work order details"
                      items={[
                        { label: 'Work Order ID', value: <code>{wo.id}</code>, rawString: wo.id },
                        { label: 'Plan ID', value: <code>{wo.plan_id}</code>, rawString: wo.plan_id },
                        ...((wo as any).plan_version ? [{ label: 'Plan Version', value: <span>Version {(wo as any).plan_version}</span> }] : []),
                        { label: 'Task ID', value: <code>{wo.task_id}</code>, rawString: wo.task_id },
                        { label: 'Raw Status', value: <code>{wo.status}</code>, rawString: wo.status },
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
