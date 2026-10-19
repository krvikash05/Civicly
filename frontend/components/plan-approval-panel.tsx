'use client';

import React, { useState, useRef } from 'react';
import type { PlanDTO, PlanTaskBinding, TaskDraft, HypothesisDTO } from '../lib/generated/models';
import {
  computeTaskDag,
  formatShortHash,
  getStatusBadgeStyle,
  type DagTaskNode,
} from '../lib/read/plans';
import {
  translateStatus,
  cleanTextIdentifiers,
  translateActionType,
  translateDepartment,
  translateRole,
  translateCauseCode,
  formatEntityDisplayName,
} from '../lib/read/display';
import { TechnicalDetails, CopyableIdentifier } from './technical-details';
import { useDemo } from './demo-connection';
import {approvalAssignments} from '../lib/read/workflow';
import {ApiError} from '../lib/api/errors';

interface PlanApprovalPanelProps {
  plan: PlanDTO | null;
  investigationId: string;
  hypotheses?: HypothesisDTO[];
  onRefetch?: () => void;
}

export function PlanApprovalPanel({
  plan,
  investigationId,
  hypotheses = [],
  onRefetch,
}: PlanApprovalPanelProps) {
  const demo = useDemo();
  const [expandedTaskId, setExpandedTaskId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const intent = useRef<{scope:string;key:string;uncertain:boolean}|null>(null);

  if (!plan) {
    return (
      <div className="panel-empty-state" style={{ padding: '2.5rem 1.5rem', textAlign: 'center' }}>
        <p className="muted" style={{ fontSize: '15px', fontWeight: 600 }}>
          No remediation plan has been drafted yet for this investigation.
        </p>
        <p className="muted text-sm" style={{ marginTop: '0.5rem', maxWidth: '480px', marginLeft: 'auto', marginRight: 'auto' }}>
          A plan can be proposed after the evidence, responsible departments and source procedures have been checked. No plan was returned in the loaded records.
        </p>
        <div style={{ marginTop: '1.25rem' }}>
          <TechnicalDetails
            title="Technical context"
            items={[
              { label: 'Investigation ID', value: <code>{investigationId}</code>, rawString: investigationId },
              { label: 'Plan Status', value: <span>NOT_DRAFTED</span> },
            ]}
          />
        </div>
      </div>
    );
  }

  const tasks = plan.draft?.tasks || [];
  const bindings = plan.task_bindings || [];
  const dag = computeTaskDag(tasks, bindings);
  const statusBadgeStyle = getStatusBadgeStyle(plan.status);

  // Collect distinct departments from tasks
  const distinctDepts = Array.from(
    new Set([
      ...tasks.map((t) => t.department_id).filter(Boolean),
      ...bindings.map((b) => b.department_id).filter(Boolean),
    ])
  );

  async function handleSubmitForApproval() {
    if (!plan || submitting) return;
    if (demo.status !== 'connected') {
      setSubmitError('Demo session is not connected.');
      return;
    }

    setSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(null);

    try {
      const scope = `${plan.plan_id}:${plan.version}:${plan.content_hash}`;
      if(intent.current?.uncertain)throw new ApiError('RECOVERY_REQUIRED');
      const assignments = approvalAssignments(plan);
      if(intent.current?.scope!==scope)intent.current={scope,key:crypto.randomUUID(),uncertain:false};
      const idempotencyKey=intent.current!.key;
      await demo.connection.client.request(
        'POST /api/v1/plans/{id}/submit-approval',
        {
          params: { id: plan.plan_id },
          idempotencyKey,
          body: {
            plan_version: plan.version,
            plan_hash: plan.content_hash,
            assignments,
          },
        }
      );

      setSubmitSuccess('Plan successfully submitted for municipal supervisory approval.');
      if (onRefetch) onRefetch();
    } catch (err: any) {
      if(err instanceof ApiError && err.uncertain && intent.current)intent.current.uncertain=true;
      setSubmitError(
        err?.response?.error?.message ||
        err?.message ||
        'Failed to submit plan for approval. Verify operator role and plan state.'
      );
    } finally {
      setSubmitting(false);
    }
  }

  const techItems = [
    { label: 'Plan ID', value: <code>{plan.plan_id}</code>, rawString: plan.plan_id },
    { label: 'Investigation ID', value: <code>{plan.investigation_id}</code>, rawString: plan.investigation_id },
    { label: 'Plan Version', value: <span>Version {plan.version}</span>, rawString: String(plan.version) },
    { label: 'Raw Status', value: <code>{plan.status}</code>, rawString: plan.status },
    { label: 'Content Hash (SHA-256)', value: <code className="hash-code">{plan.content_hash}</code>, rawString: plan.content_hash },
    { label: 'Expected Hash', value: <code className="hash-code">{plan.expected_hash}</code>, rawString: plan.expected_hash },
    ...((plan as any).graph_revision ? [{ label: 'Graph Revision', value: <span>{(plan as any).graph_revision}</span>, rawString: String((plan as any).graph_revision) }] : []),
    { label: 'Execution Gates Verified', value: <span>{plan.execution_gates_verified ? 'Yes' : 'No (Pending Approval)'}</span> },
  ];

  return (
    <div className="plan-approval-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* 1. Redesigned Plan Overview Card with Clear Information Hierarchy */}
      <div className="plan-overview-card">
        <header className="plan-card-header">
          <div className="plan-title-block">
            <span className="eyebrow-label">ACTION PLAN</span>
            <h3 className="plan-main-title">Action plan and approval</h3>
            <p className="plan-subtitle">
              Version {plan.version} &bull; {translateStatus(plan.status)} &bull; {plan.simulated ? 'Simulated Execution' : 'Operational'}
            </p>
          </div>

          <div className="plan-badges-group">
            <span
              className="badge plan-status-badge"
              style={{
                backgroundColor: statusBadgeStyle.bg,
                color: statusBadgeStyle.color,
                borderColor: statusBadgeStyle.border,
              }}
            >
              {translateStatus(plan.status)}
            </span>
            {plan.simulated && (
              <span className="badge badge-simulated" title="Simulated environment demonstration">
                Simulated
              </span>
            )}
          </div>
        </header>

        {/* What the plan proposes */}
        <section className="plan-proposal-summary">
          <h4 className="section-subheading">What this plan proposes</h4>
          <p className="proposal-prose">
            This plan defines <strong>{tasks.length} coordinated municipal task{tasks.length !== 1 ? 's' : ''}</strong>{' '}
            structured across <strong>{dag.tiers.length} sequential execution tier{dag.tiers.length !== 1 ? 's' : ''}</strong>.{' '}
            {tasks.length > 0 && (
              <span>
                Key interventions include{' '}
                {tasks.map((t, idx) => (
                  <span key={t.id}>
                    <em>{translateActionType(t.action_type)}</em>
                    {idx < tasks.length - 2 ? ', ' : idx === tasks.length - 2 ? ', and ' : '.'}
                  </span>
                ))}
              </span>
            )}
          </p>

          {/* Responsible Departments */}
          {distinctDepts.length > 0 && (
            <div className="dept-chips-row">
              <span className="dept-label">Responsible departments:</span>
              <div className="dept-chips">
                {distinctDepts.map((d) => (
                  <span key={d} className="dept-chip">
                    {translateDepartment(d)}
                  </span>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Findings Addressed (Evaluation Basis) */}
        {plan.draft?.basis && plan.draft.basis.length > 0 && (
          <section className="plan-findings-section">
            <h4 className="section-subheading">
              Explanations covered by this plan ({plan.draft.basis.filter((b) => b.addressed).length} of {plan.draft.basis.length} explanations)
            </h4>
            <div className="findings-list">
              {plan.draft.basis.map((b, idx) => {
                const hypothesis=hypotheses.find(h=>h.id===b.hypothesis_id);
                const cause = hypothesis ? translateCauseCode(hypothesis.cause_code) : {title:'Assessed explanation'};
                const isAddressed = Boolean(b.addressed);

                return (
                  <div
                    key={idx}
                    className={`finding-card ${isAddressed ? 'finding-addressed' : 'finding-unaddressed'}`}
                  >
                    <div className="finding-top-row">
                      <div className="finding-title-group">
                        <strong className="finding-name">
                          {cause.title}
                        </strong>
                        <span className="finding-short-id">
                          ({formatEntityDisplayName({ id: b.hypothesis_id, kind: 'Hypothesis' }).shortId})
                        </span>
                      </div>
                      <span
                        className={`badge ${
                          isAddressed ? 'badge-plan-addressed' : 'badge-plan-unaddressed'
                        }`}
                      >
                        {isAddressed ? 'Addressed in plan' : 'Not addressed in plan'}
                      </span>
                    </div>
                    {b.reason && <><p className="finding-reason">{cleanTextIdentifiers(b.reason)}</p><TechnicalDetails title="Original planning rationale" items={[{label:'Original rationale',value:<span>{b.reason}</span>},{label:'Hypothesis ID',value:<code>{b.hypothesis_id}</code>},{label:'Assessment ID',value:<code>{b.assessment_id}</code>}]}/></>}
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* Execution Gates & Municipal Approval State */}
        <section className="plan-governance-section">
          <div className="governance-status-row">
            <div>
              <span className="governance-label">Approval & Execution Gates</span>
              <p className="governance-text">
                {plan.status === 'COMPLETED' ? (<strong>Plan approved and planned work completed. Review the separate outcome evidence in Monitoring &amp; memory.</strong>) : plan.status === 'MONITORING' ? (<strong>Plan approved and work completed; independent follow-up is still required.</strong>) : plan.status === 'IN_EXECUTION' ? (<strong>Approved work is in progress. Check the task sequence and unmet conditions.</strong>) : plan.status === 'APPROVED' ? (
                  <strong className="text-success">
                    Plan approved. Each work order still requires its own authorization and satisfied prerequisites.
                  </strong>
                ) : plan.status === 'PENDING_APPROVAL' ? (
                  <strong className="text-warning">
                    ⏳ Awaiting review by an authorized approval officer.
                  </strong>
                ) : (
                  <span className="text-muted">
                    Review the recorded plan state and its evidence before deciding whether a new submission is appropriate.
                  </span>
                )}
              </p>
            </div>

            {/* Action buttons for Analyst demo session */}
            {plan.status === 'DRAFT' && (
              <div className="plan-action-block">
                <button
                  type="button"
                  className="button primary"
                  onClick={handleSubmitForApproval}
                  disabled={submitting}
                >
                  {submitting ? 'Submitting…' : 'Submit for approval'}
                </button>
              </div>
            )}
          </div>

          {submitError && (
            <div className="form-error-banner" role="alert">
              <strong>Submission error:</strong> {submitError}
            </div>
          )}

          {submitSuccess && (
            <div className="form-success-banner" role="status">
              {submitSuccess}
            </div>
          )}

          {/* Separation of duties callout */}
          <div className="governance-callout">
            <span className="callout-icon">ℹ</span>
            <p>
              <strong>Approval protects the exact plan:</strong> An analyst can submit a proposal but cannot approve it. An independent approval officer reviews the version, tasks and assigned operators. Safety conditions and task prerequisites are checked separately before work can proceed.
            </p>
          </div>
        </section>

        {/* Technical Details (Expandable) */}
        <TechnicalDetails
          title="Technical plan specifications & hashes"
          items={techItems}
        />
      </div>

      {/* 2. Remediation Task DAG & Dependencies */}
      <div className="plan-dag-container">
        <div className="dag-header">
          <div>
            <h4 className="dag-title">Task Dependencies & Execution Sequence</h4>
            <p className="muted text-sm" style={{ margin: 0 }}>
              Tasks are grouped by their prerequisites. Later tasks wait for the required earlier work and evidence; this view does not start work automatically.
            </p>
          </div>
          <span className="count-pill">{tasks.length} tasks</span>
        </div>

        {dag.hasCycle && (
          <div className="cycle-warning-banner" role="alert">
            ⚠ Cyclic dependency detected in task plan graph. Tasks requiring circular resolution are flagged.
          </div>
        )}

        <div className="dag-tiers-list">
          {dag.tiers.map((tierTasks, tierIdx) => (
            <div key={tierIdx} className="dag-tier-group">
              <div className="tier-label-badge">
                Work sequence {tierIdx + 1} {tierIdx === 0 ? '(start with these tasks)' : '(after the required tasks)'}
              </div>

              <div className="tier-cards-grid">
                {tierTasks.map((task: DagTaskNode) => {
                  const isExpanded = expandedTaskId === task.id;
                  const taskActionTitle = translateActionType(task.action_type);
                  const taskDept = translateDepartment(task.department_id);

                  return (
                    <article key={task.id} className="task-dag-card">
                      <header className="task-card-header">
                        <div className="task-heading">
                          <span className="task-type-badge">{taskActionTitle}</span>
                          <span className="task-dept-badge">{taskDept}</span>
                        </div>
                        <span className={`badge ${getStatusBadgeStyle(task.status).color ? '' : ''}`}>
                          {translateStatus(task.status)}
                        </span>
                      </header>

                      <div className="task-card-body">
                        {/* Target Infrastructure Asset */}
                        {task.target_ids && task.target_ids.length > 0 && (
                          <div className="task-prop-row">
                            <span className="prop-name">Target Asset:</span>
                            <div className="target-chips">
                              {task.target_ids.map((tid) => {
                                const nameInfo = formatEntityDisplayName({ id: tid, kind: 'InfrastructureAsset' });
                                return (
                                  <span key={tid} className="target-chip">
                                    {nameInfo.primary} <small>({nameInfo.shortId})</small>
                                  </span>
                                );
                              })}
                            </div>
                          </div>
                        )}

                        {/* Dependencies */}
                        {task.depends_on && task.depends_on.length > 0 && (
                          <div className="task-prop-row">
                            <span className="prop-name">Requires completion of:</span>
                            <div className="dep-tags">
                              {task.depends_on.map((depId) => {
                                const depNode = tasks.find((t) => t.id === depId);
                                const depAction = depNode ? translateActionType(depNode.action_type) : depId;
                                return (
                                  <span key={depId} className="dep-tag">
                                    ↳ {depAction}
                                  </span>
                                );
                              })}
                            </div>
                          </div>
                        )}

                        {/* Expected Civic Outcome */}
                        {task.expected_outcome && (
                          <p className="task-outcome-text">
                            <strong>Expected outcome:</strong> {cleanTextIdentifiers(task.expected_outcome)}
                          </p>
                        )}

                        {/* Expandable Specifications */}
                        <div className="task-specs-toggle">
                          <button
                            type="button"
                            className="toggle-specs-btn"
                            onClick={() => setExpandedTaskId(isExpanded ? null : task.id)}
                            aria-expanded={isExpanded}
                          >
                            {isExpanded ? 'Hide specifications ▲' : 'View specifications & citations ▼'}
                          </button>
                        </div>

                        {isExpanded && (
                          <div className="task-specs-drawer">
                            {task.remediation && (
                              <div className="spec-item">
                                <span className="spec-label">Remediation Details:</span>
                                <p className="spec-val">
                                  Mode: {task.remediation.mode || 'Standard'} &bull; Conditions: {Array.isArray(task.remediation.conditions) ? `${task.remediation.conditions.length} prerequisite condition(s)` : 'Standard operating procedure'}
                                </p>
                              </div>
                            )}

                            {task.procedure_citation && (
                              <div className="spec-item">
                                <span className="spec-label">Municipal Procedure Citation:</span>
                                <p className="spec-val">
                                  Standard {task.procedure_citation.canonical_document_id || task.procedure_citation.source_document_id} (Version {task.procedure_citation.source_version})
                                </p>
                              </div>
                            )}

                            {task.verification_criteria && (
                              <div className="spec-item">
                                <span className="spec-label">Verification Criteria:</span>
                                <p className="spec-val">{task.verification_criteria}</p>
                              </div>
                            )}

                            {task.risks && task.risks.length > 0 && (
                              <div className="spec-item">
                                <span className="spec-label">Identified Operational Risks:</span>
                                <ul className="spec-list">
                                  {task.risks.map((r, i) => (
                                    <li key={i}>{r}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            <TechnicalDetails
                              title="Technical task identifiers"
                              items={[
                                { label: 'Task ID', value: <code>{task.id}</code>, rawString: task.id },
                                { label: 'Action Type Code', value: <code>{task.action_type}</code>, rawString: task.action_type },
                                { label: 'Department ID', value: <code>{task.department_id}</code>, rawString: task.department_id },
                                {
                                  label: 'Eligible Assignees',
                                  value: (
                                    <span>
                                      {task.eligible_assignees.map((a) => translateRole(a)).join(', ') || 'Department Lead'}
                                    </span>
                                  ),
                                },
                              ]}
                            />
                          </div>
                        )}
                      </div>
                    </article>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
