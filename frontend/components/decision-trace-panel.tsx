'use client';

import React from 'react';
import type { AgentTracePage, GraphSubgraphDTO } from '../lib/generated/models';
import { extractDecisionTraces, DecisionTraceItem } from '../lib/read/graph';
import {
  translateRole,
  translateStatus,
  translateActionType,
  formatEntityDisplayName,
} from '../lib/read/display';
import { TechnicalDetails, CopyableIdentifier } from './technical-details';

interface DecisionTracePanelProps {
  tracePage: AgentTracePage | null;
  subgraph: GraphSubgraphDTO | null;
  onHighlightDecisionPath?: (pathId: string | null) => void;
  selectedDecisionPathId?: string | null;
  onSelectEvidenceId?: (id: string) => void;
}

export function DecisionTracePanel({
  tracePage,
  subgraph,
  onHighlightDecisionPath,
  selectedDecisionPathId,
  onSelectEvidenceId,
}: DecisionTracePanelProps) {
  if (!tracePage || !tracePage.items || tracePage.items.length === 0) {
    return (
      <div className="empty-trace-notice">
        <p className="muted" style={{ fontSize: '15px', fontWeight: 600 }}>
          No agent trace events have been recorded for this investigation yet.
        </p>
        <p className="muted text-sm" style={{ marginTop: '0.4rem' }}>
          When the autonomous investigator executes tool calls, retrieves graph evidence, or records decisions, the 3-part traceability record will display here.
        </p>
      </div>
    );
  }

  const items: DecisionTraceItem[] = extractDecisionTraces(tracePage, subgraph);

  return (
    <div className="decision-trace-panel">
      {/* Educational responsibility callout */}
      <div className="responsibility-banner">
        <h4>FalkorDB Graph Traceability & Agent Reasoning</h4>
        <p>
          <strong>Division of Responsibility:</strong> FalkorDB stores and retrieves verified
          connected knowledge. The autonomous agent reasons over returned evidence to formulate
          hypotheses and actions. Backend domain services enforce strict authorization, approval
          gates, and state machine transitions.
        </p>
      </div>

      <div className="trace-timeline">
        {items.map((item, idx) => {
          const roleTitle = translateRole(item.agentRole);
          const readableStatus = translateStatus(item.status);
          const toolAction = item.toolName ? translateActionType(item.toolName) : null;

          const techItems = [
            { label: 'Event ID', value: <code>{item.eventId}</code>, rawString: item.eventId },
            ...(item.recordedDecision.decisionId
              ? [{ label: 'Decision ID', value: <code>{item.recordedDecision.decisionId}</code>, rawString: item.recordedDecision.decisionId }]
              : []),
            ...(item.recordedDecision.parentExecutionId
              ? [{ label: 'Parent Execution ID', value: <code>{item.recordedDecision.parentExecutionId}</code>, rawString: item.recordedDecision.parentExecutionId }]
              : []),
            ...(item.toolName
              ? [{ label: 'Raw Tool Identifier', value: <code>{item.toolName}</code>, rawString: item.toolName }]
              : []),
            { label: 'Agent Role Code', value: <code>{item.agentRole}</code>, rawString: item.agentRole },
          ];

          return (
            <article
              key={item.eventId || idx}
              className={`trace-card ${
                item.influenceCategory === 'MODEL_SELECTED_PATH' ? 'card-highlighted' : ''
              }`}
            >
              {/* Step Header with Clean Wrapped Badges */}
              <header className="trace-card-header">
                <div className="trace-step-badge">
                  Step {idx + 1} &bull; {roleTitle}
                </div>
                <div className="trace-timestamp">
                  {new Date(item.timestamp).toLocaleTimeString('en-IN', {
                    timeZone: 'Asia/Kolkata',
                    hour12: false,
                  })}{' '}
                  IST
                </div>
                <span
                  className={`badge ${
                    item.status === 'SUCCESS' ? 'badge-verified' : 'badge-candidate'
                  }`}
                >
                  {readableStatus}
                </span>
              </header>

              {/* 3-Part Traceability Grid */}
              <div className="trace-three-part-grid">
                {/* Part 1: Question Asked */}
                <div className="trace-column col-question">
                  <div className="column-label">1. Question Asked</div>
                  <div className="column-content">
                    <p className="question-text">{item.questionAsked}</p>
                    {toolAction && (
                      <div className="tool-tag">
                        Action: <strong>{toolAction}</strong>
                      </div>
                    )}
                  </div>
                </div>

                {/* Part 2: Graph Evidence Returned */}
                <div className="trace-column col-evidence">
                  <div className="column-label">2. FalkorDB Graph Evidence</div>
                  <div className="column-content">
                    <p className="evidence-summary">{item.graphEvidence.summary}</p>

                    {item.graphEvidence.nodeIds.length > 0 && (
                      <div className="entity-pills">
                        <span className="pill-group-title">Connected entities:</span>
                        <div className="chips-row">
                          {item.graphEvidence.nodeIds.map((id) => {
                            const nameInfo = formatEntityDisplayName({ id });
                            return (
                              <span key={id} className="chip chip-asset" title={id}>
                                {nameInfo.primary} <small>({nameInfo.shortId})</small>
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {item.graphEvidence.evidenceIds.length > 0 && (
                      <div className="evidence-links" style={{ marginTop: '0.4rem' }}>
                        <span className="pill-group-title">Attributed evidence:</span>
                        <div className="chips-row">
                          {item.graphEvidence.evidenceIds.map((eid) => (
                            <button
                              key={eid}
                              type="button"
                              className="chip chip-evidence"
                              onClick={() => onSelectEvidenceId?.(eid)}
                              title={`Inspect evidence ${eid}`}
                            >
                              Evidence ({eid.slice(-4)})
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Part 3: Recorded Decision */}
                <div className="trace-column col-decision">
                  <div className="column-label">3. Recorded Decision</div>
                  <div className="column-content">
                    <div className="decision-action">
                      <strong>Action taken:</strong> {item.recordedDecision.action}
                    </div>
                    <p className="rationale-text">
                      <strong>Rationale:</strong> {item.recordedDecision.rationaleSummary}
                    </p>
                  </div>
                </div>
              </div>

              {/* Step Footer with Influence Attribution */}
              <footer className="trace-card-footer">
                <div className="influence-block">
                  <span
                    className={`influence-badge ${
                      item.influenceCategory === 'MODEL_SELECTED_PATH'
                        ? 'influence-selected'
                        : item.influenceCategory === 'CONTEXTUAL_GRAPH_QUERY'
                        ? 'influence-contextual'
                        : 'influence-unestablished'
                    }`}
                  >
                    {item.influenceCategory === 'MODEL_SELECTED_PATH'
                      ? 'Decision bound to graph path'
                      : item.influenceCategory === 'CONTEXTUAL_GRAPH_QUERY'
                      ? 'Contextual graph background'
                      : 'No causal trace established'}
                  </span>
                  <span className="influence-text">{item.influenceExplanation}</span>
                </div>

                {/* Technical Details for Step */}
                <div style={{ width: '100%', marginTop: '0.5rem' }}>
                  <TechnicalDetails
                    title="Technical step references"
                    items={techItems}
                  />
                </div>
              </footer>
            </article>
          );
        })}
      </div>
    </div>
  );
}
