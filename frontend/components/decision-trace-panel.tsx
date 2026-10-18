'use client';

import React from 'react';
import type { AgentTracePage, GraphSubgraphDTO, DecisionPath } from '../lib/generated/models';
import { extractDecisionTraces, DecisionTraceItem } from '../lib/read/graph';

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
        <p className="muted">
          No agent trace events have been recorded for this investigation yet.
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
        {items.map((item, idx) => (
          <article
            key={item.eventId || idx}
            className={`trace-card ${
              item.influenceCategory === 'MODEL_SELECTED_PATH' ? 'card-highlighted' : ''
            }`}
          >
            {/* Step Header */}
            <header className="trace-card-header">
              <div className="trace-step-badge">
                Step {idx + 1} &bull; {item.agentRole}
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
                {item.status}
              </span>
            </header>

            {/* 3-Part Traceability Grid */}
            <div className="trace-three-part-grid">
              {/* Part 1: Question Asked */}
              <div className="trace-column col-question">
                <div className="column-label">1. Question Asked</div>
                <div className="column-content">
                  <p className="question-text">{item.questionAsked}</p>
                  {item.toolName && (
                    <div className="tool-tag">
                      Tool: <code>{item.toolName}</code>
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
                      <span className="pill-group-title">Nodes:</span>
                      {item.graphEvidence.nodeIds.map((id) => (
                        <code key={id} className="pill-code">
                          {id}
                        </code>
                      ))}
                    </div>
                  )}

                  {item.graphEvidence.evidenceIds.length > 0 && (
                    <div className="evidence-links">
                      <span className="pill-group-title">Evidence:</span>
                      {item.graphEvidence.evidenceIds.map((eid) => (
                        <button
                          key={eid}
                          type="button"
                          className="chip chip-evidence"
                          onClick={() => onSelectEvidenceId?.(eid)}
                        >
                          {eid}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Part 3: Recorded Decision */}
              <div className="trace-column col-decision">
                <div className="column-label">3. Recorded Decision</div>
                <div className="column-content">
                  <div className="decision-action">
                    <strong>Action:</strong> {item.recordedDecision.action}
                  </div>
                  <p className="rationale-text">
                    <strong>Rationale:</strong> {item.recordedDecision.rationaleSummary}
                  </p>
                  {item.recordedDecision.decisionId && (
                    <div className="decision-meta">
                      Decision ID: <code>{item.recordedDecision.decisionId}</code>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Influence Attribution Footer */}
            <footer className="trace-card-footer">
              <span
                className={`influence-badge ${
                  item.influenceCategory === 'MODEL_SELECTED_PATH'
                    ? 'influence-selected'
                    : item.influenceCategory === 'CONTEXTUAL_GRAPH_QUERY'
                    ? 'influence-contextual'
                    : 'influence-unestablished'
                }`}
              >
                {item.influenceCategory === 'MODEL_SELECTED_PATH' && '★ Model-Selected Path'}
                {item.influenceCategory === 'CONTEXTUAL_GRAPH_QUERY' && 'ℹ Contextual Graph Query'}
                {item.influenceCategory === 'UNESTABLISHED_INFLUENCE' && '⚠ Unestablished Influence'}
              </span>
              <span className="influence-text">{item.influenceExplanation}</span>

              {/* Optional decision path highlight trigger */}
              {item.influenceCategory === 'MODEL_SELECTED_PATH' && subgraph?.decision_paths && (
                <button
                  type="button"
                  className="btn-link-action"
                  onClick={() => {
                    const matchedPath = subgraph.decision_paths?.find((p: DecisionPath) =>
                      p.node_ids.some((nid: string) => item.graphEvidence.nodeIds.includes(nid)),
                    );
                    if (matchedPath) {
                      onHighlightDecisionPath?.(
                        selectedDecisionPathId === matchedPath.id ? null : matchedPath.id,
                      );
                    }
                  }}
                >
                  {selectedDecisionPathId ? 'Clear Highlight' : 'Highlight in Graph'}
                </button>
              )}
            </footer>
          </article>
        ))}
      </div>
    </div>
  );
}
