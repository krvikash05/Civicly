'use client';

import React, { useEffect, useRef, useState } from 'react';
import type { GraphSubgraphDTO } from '../lib/generated/models';
import {
  mapGraphSubgraphToCanvas,
  CanvasNode,
  CanvasLink,
  GraphDisplayStats,
  NODE_KIND_COLORS,
  EDGE_STATUS_COLORS,
} from '../lib/read/graph';

interface FalkorDBCanvasViewProps {
  subgraph: GraphSubgraphDTO;
  selectedDecisionPathId?: string | null;
  onSelectEvidenceId?: (id: string) => void;
}

export function FalkorDBCanvasView({
  subgraph,
  selectedDecisionPathId,
  onSelectEvidenceId,
}: FalkorDBCanvasViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<any>(null);
  const [isClient, setIsClient] = useState(false);
  const [layoutMode, setLayoutMode] = useState<'force' | 'tree' | 'radial'>('force');
  const [selectedNode, setSelectedNode] = useState<CanvasNode | null>(null);
  const [selectedLink, setSelectedLink] = useState<CanvasLink | null>(null);
  const [showTableView, setShowTableView] = useState(false);

  // Map subgraph DTO to Canvas data with memoization
  const { data: canvasData, stats } = React.useMemo(
    () => mapGraphSubgraphToCanvas(subgraph, selectedDecisionPathId),
    [subgraph, selectedDecisionPathId]
  );

  const lastDataSignature = useRef<string>('');

  useEffect(() => {
    setIsClient(true);
  }, []);

  // Initialize and update Canvas
  useEffect(() => {
    if (!isClient) return;

    let mounted = true;

    async function initOrUpdateCanvas() {
      try {
        // Dynamically import @falkordb/canvas only in browser
        await import('@falkordb/canvas');

        if (!mounted || !canvasRef.current) return;
        const canvas = canvasRef.current;

        const signature =
          canvasData.nodes.map((n) => n.id).sort().join(',') +
          '|' +
          canvasData.links.map((l) => l.id).sort().join(',') +
          '|' +
          (selectedDecisionPathId ?? '');

        // Only call setData if graph structure or decision path actually changed
        if (signature !== lastDataSignature.current) {
          lastDataSignature.current = signature;
          canvas.setData({
            nodes: canvasData.nodes,
            links: canvasData.links,
          });

          // Trigger auto fit after layout settles
          setTimeout(() => {
            if (mounted && canvas?.zoomToFit) {
              canvas.zoomToFit(0.15);
            }
          }, 150);
        }

        // Configure canvas behavior and styling without resetting simulation
        canvas.setConfig({
          backgroundColor: '#FFFFFF',
          foregroundColor: '#1E293B',
          layoutMode: layoutMode,
          linkLineDash: (link: any) =>
            link?.data?.verification_status === 'CANDIDATE' ? [4, 4] : [],
          eventHandlers: {
            onNodeClick: (node: any) => {
              setSelectedLink(null);
              setSelectedNode(node as CanvasNode);
            },
            onLinkClick: (link: any) => {
              setSelectedNode(null);
              setSelectedLink(link as CanvasLink);
            },
            onBackgroundClick: () => {
              setSelectedNode(null);
              setSelectedLink(null);
            },
          },
        });
      } catch (err) {
        console.error('Failed to initialize FalkorDB Canvas:', err);
      }
    }

    initOrUpdateCanvas();

    return () => {
      mounted = false;
    };
  }, [isClient, canvasData, layoutMode, selectedDecisionPathId]);

  const handleZoomIn = () => {
    if (canvasRef.current?.getZoom && canvasRef.current?.zoom) {
      const current = canvasRef.current.getZoom();
      canvasRef.current.zoom(current * 1.25);
    }
  };

  const handleZoomOut = () => {
    if (canvasRef.current?.getZoom && canvasRef.current?.zoom) {
      const current = canvasRef.current.getZoom();
      canvasRef.current.zoom(current * 0.8);
    }
  };

  const handleFit = () => {
    if (canvasRef.current?.zoomToFit) {
      canvasRef.current.zoomToFit(0.15);
    }
  };

  return (
    <div className="canvas-view-container">
      {/* Top Controls & Status Bar */}
      <div className="canvas-toolbar">
        <div className="canvas-toolbar-group">
          <label className="canvas-toolbar-label" htmlFor="layout-select">
            Layout:
          </label>
          <select
            id="layout-select"
            className="canvas-select"
            value={layoutMode}
            onChange={(e) => setLayoutMode(e.target.value as any)}
          >
            <option value="force">Force Directed (D3)</option>
            <option value="tree">Tree (Hierarchical)</option>
            <option value="radial">Radial</option>
          </select>

          <button
            type="button"
            className="canvas-btn"
            onClick={handleZoomIn}
            title="Zoom In"
            aria-label="Zoom in"
          >
            + Zoom
          </button>
          <button
            type="button"
            className="canvas-btn"
            onClick={handleZoomOut}
            title="Zoom Out"
            aria-label="Zoom out"
          >
            − Zoom
          </button>
          <button
            type="button"
            className="canvas-btn"
            onClick={handleFit}
            title="Fit to Viewport"
            aria-label="Fit graph to view"
          >
            Fit View
          </button>
        </div>

        <div className="canvas-toolbar-group">
          <button
            type="button"
            className={`canvas-toggle-btn ${showTableView ? 'active' : ''}`}
            onClick={() => setShowTableView(!showTableView)}
            aria-label="Toggle accessible table view"
          >
            {showTableView ? 'Show Graph Canvas' : 'Accessible Table View'}
          </button>
        </div>
      </div>

      {/* Subgraph Bounds & Truncation Banner */}
      <div className="canvas-meta-bar">
        <span>
          <strong>FalkorDB Subgraph:</strong> {stats.totalNodes} Nodes,{' '}
          {stats.totalEdges} Edges ({stats.verifiedEdges} Verified,{' '}
          {stats.candidateEdges} Candidate, {stats.decisionPathEdges} in Decision Path)
        </span>
        <span className="canvas-meta-rev">Revision: {stats.graphRevision}</span>
        {stats.truncated && (
          <span className="badge badge-warning">TRUNCATED AT CAPACITY</span>
        )}
        {stats.searchLimited && (
          <span className="badge badge-warning">SEARCH BOUND REACHED</span>
        )}
      </div>

      {/* Main View Area: Canvas or Accessible Table */}
      <div className="canvas-stage-wrapper" ref={containerRef}>
        {!showTableView ? (
          <div className="canvas-element-container">
            {isClient ? (
              // @ts-expect-error Custom element registered dynamically
              <falkordb-canvas
                ref={canvasRef}
                style={{ width: '100%', height: '520px', display: 'block' }}
              />
            ) : (
              <div className="canvas-loading-placeholder">
                Loading FalkorDB Graph Canvas...
              </div>
            )}
          </div>
        ) : (
          <div className="canvas-table-view" tabIndex={0} aria-label="Accessible Subgraph Entities">
            <h4>Accessible Graph Nodes ({canvasData.nodes.length})</h4>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Kind / Labels</th>
                    <th>Display Label</th>
                    <th>Status</th>
                    <th>Attributed Evidence</th>
                  </tr>
                </thead>
                <tbody>
                  {canvasData.nodes.map((n) => (
                    <tr
                      key={n.id}
                      className={selectedNode?.id === n.id ? 'row-selected' : ''}
                      onClick={() => setSelectedNode(n)}
                    >
                      <td><code>{n.id}</code></td>
                      <td>
                        <span
                          className="kind-pill"
                          style={{ borderColor: n.color, color: n.color }}
                        >
                          {n.data.kind}
                        </span>
                      </td>
                      <td>{n.caption}</td>
                      <td>{n.data.status || '—'}</td>
                      <td>
                        {n.data.evidence_ids.length > 0 ? (
                          n.data.evidence_ids.map((eid) => (
                            <button
                              key={eid}
                              type="button"
                              className="chip chip-evidence"
                              onClick={(e) => {
                                e.stopPropagation();
                                onSelectEvidenceId?.(eid);
                              }}
                            >
                              {eid}
                            </button>
                          ))
                        ) : (
                          '—'
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <h4 style={{ marginTop: '1.5rem' }}>
              Accessible Graph Relationships ({canvasData.links.length})
            </h4>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Relationship Type</th>
                    <th>Source</th>
                    <th>Target</th>
                    <th>Verification</th>
                    <th>Attributed Evidence</th>
                  </tr>
                </thead>
                <tbody>
                  {canvasData.links.map((l) => (
                    <tr
                      key={l.id}
                      className={selectedLink?.id === l.id ? 'row-selected' : ''}
                      onClick={() => setSelectedLink(l)}
                    >
                      <td><code>{l.id}</code></td>
                      <td><code>{l.relationship}</code></td>
                      <td><code>{String(l.source)}</code></td>
                      <td><code>{String(l.target)}</code></td>
                      <td>
                        <span
                          className={`badge ${
                            l.data.verification_status === 'VERIFIED'
                              ? 'badge-verified'
                              : 'badge-candidate'
                          }`}
                        >
                          {l.data.verification_status}
                        </span>
                      </td>
                      <td>
                        {l.data.source_evidence_ids.length > 0 ? (
                          l.data.source_evidence_ids.map((eid) => (
                            <button
                              key={eid}
                              type="button"
                              className="chip chip-evidence"
                              onClick={(e) => {
                                e.stopPropagation();
                                onSelectEvidenceId?.(eid);
                              }}
                            >
                              {eid}
                            </button>
                          ))
                        ) : (
                          '—'
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Selected Entity Inspector Panel */}
        {(selectedNode || selectedLink) && (
          <aside className="canvas-inspector" aria-label="Graph Entity Inspector">
            <div className="inspector-header">
              <h3>{selectedNode ? 'Node Details' : 'Relationship Details'}</h3>
              <button
                type="button"
                className="close-btn"
                onClick={() => {
                  setSelectedNode(null);
                  setSelectedLink(null);
                }}
                aria-label="Close inspector"
              >
                ✕
              </button>
            </div>

            {selectedNode && (
              <div className="inspector-content">
                <div className="inspector-prop">
                  <span className="prop-name">ID:</span>
                  <code className="prop-val">{selectedNode.id}</code>
                </div>
                <div className="inspector-prop">
                  <span className="prop-name">Display Label:</span>
                  <span className="prop-val font-semibold">{selectedNode.caption}</span>
                </div>
                <div className="inspector-prop">
                  <span className="prop-name">Kind:</span>
                  <span className="prop-val">
                    <span
                      className="kind-pill"
                      style={{
                        borderColor: selectedNode.color,
                        color: selectedNode.color,
                      }}
                    >
                      {selectedNode.data.kind}
                    </span>
                  </span>
                </div>
                <div className="inspector-prop">
                  <span className="prop-name">Labels:</span>
                  <span className="prop-val">{selectedNode.labels.join(', ') || '—'}</span>
                </div>
                <div className="inspector-prop">
                  <span className="prop-name">Status:</span>
                  <span className="prop-val">{selectedNode.data.status || '—'}</span>
                </div>
                {selectedNode.data.observed_at && (
                  <div className="inspector-prop">
                    <span className="prop-name">Observed:</span>
                    <span className="prop-val">{selectedNode.data.observed_at}</span>
                  </div>
                )}
                <div className="inspector-prop">
                  <span className="prop-name">Decision Path:</span>
                  <span className="prop-val">
                    {selectedNode.data.is_decision_path ? (
                      <span className="badge badge-decision">IN DECISION PATH</span>
                    ) : (
                      'Contextual Graph Node'
                    )}
                  </span>
                </div>
                <div className="inspector-prop">
                  <span className="prop-name">Attributed Evidence:</span>
                  <div className="prop-val-tags">
                    {selectedNode.data.evidence_ids.length > 0 ? (
                      selectedNode.data.evidence_ids.map((eid) => (
                        <button
                          key={eid}
                          type="button"
                          className="chip chip-evidence"
                          onClick={() => onSelectEvidenceId?.(eid)}
                        >
                          {eid}
                        </button>
                      ))
                    ) : (
                      <span className="muted">None directly linked</span>
                    )}
                  </div>
                </div>
              </div>
            )}

            {selectedLink && (
              <div className="inspector-content">
                <div className="inspector-prop">
                  <span className="prop-name">Relationship:</span>
                  <code className="prop-val">{selectedLink.relationship}</code>
                </div>
                <div className="inspector-prop">
                  <span className="prop-name">Source:</span>
                  <code className="prop-val">{String(selectedLink.source)}</code>
                </div>
                <div className="inspector-prop">
                  <span className="prop-name">Target:</span>
                  <code className="prop-val">{String(selectedLink.target)}</code>
                </div>
                <div className="inspector-prop">
                  <span className="prop-name">Verification Status:</span>
                  <span className="prop-val">
                    <span
                      className={`badge ${
                        selectedLink.data.verification_status === 'VERIFIED'
                          ? 'badge-verified'
                          : 'badge-candidate'
                      }`}
                    >
                      {selectedLink.data.verification_status}
                    </span>
                  </span>
                </div>
                <div className="inspector-prop">
                  <span className="prop-name">Line Style:</span>
                  <span className="prop-val">
                    {selectedLink.data.verification_status === 'VERIFIED'
                      ? 'Solid Line (Verified Knowledge)'
                      : 'Dashed Line (Candidate / Hypothesis)'}
                  </span>
                </div>
                {selectedLink.data.observed_at && (
                  <div className="inspector-prop">
                    <span className="prop-name">Observed:</span>
                    <span className="prop-val">{selectedLink.data.observed_at}</span>
                  </div>
                )}
                <div className="inspector-prop">
                  <span className="prop-name">Attributed Evidence:</span>
                  <div className="prop-val-tags">
                    {selectedLink.data.source_evidence_ids.length > 0 ? (
                      selectedLink.data.source_evidence_ids.map((eid) => (
                        <button
                          key={eid}
                          type="button"
                          className="chip chip-evidence"
                          onClick={() => onSelectEvidenceId?.(eid)}
                        >
                          {eid}
                        </button>
                      ))
                    ) : (
                      <span className="muted">None directly linked</span>
                    )}
                  </div>
                </div>
              </div>
            )}
          </aside>
        )}
      </div>

      {/* Visual Graph Legend */}
      <footer className="canvas-legend" aria-label="Graph Visualization Legend">
        <div className="legend-section">
          <span className="legend-title">Entity Kinds:</span>
          <span className="legend-item">
            <span
              className="legend-dot"
              style={{ backgroundColor: NODE_KIND_COLORS.Incident }}
            />
            Incident
          </span>
          <span className="legend-item">
            <span
              className="legend-dot"
              style={{ backgroundColor: NODE_KIND_COLORS.InfrastructureAsset }}
            />
            Infrastructure Asset
          </span>
          <span className="legend-item">
            <span
              className="legend-dot"
              style={{ backgroundColor: NODE_KIND_COLORS.Observation }}
            />
            Observation
          </span>
          <span className="legend-item">
            <span
              className="legend-dot"
              style={{ backgroundColor: NODE_KIND_COLORS.Evidence }}
            />
            Evidence
          </span>
          <span className="legend-item">
            <span
              className="legend-dot"
              style={{ backgroundColor: NODE_KIND_COLORS.Hypothesis }}
            />
            Hypothesis
          </span>
        </div>

        <div className="legend-section">
          <span className="legend-title">Relationships:</span>
          <span className="legend-item">
            <span
              className="legend-line"
              style={{ backgroundColor: EDGE_STATUS_COLORS.verified }}
            />
            Verified (Solid)
          </span>
          <span className="legend-item">
            <span
              className="legend-line legend-dashed"
              style={{ borderColor: EDGE_STATUS_COLORS.candidate }}
            />
            Candidate (Dashed)
          </span>
          <span className="legend-item">
            <span
              className="legend-line"
              style={{ backgroundColor: EDGE_STATUS_COLORS.decisionPath, height: '3px' }}
            />
            Decision Path (Highlighted)
          </span>
        </div>
      </footer>
    </div>
  );
}
