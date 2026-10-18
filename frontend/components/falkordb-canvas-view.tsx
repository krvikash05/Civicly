'use client';

import React, { useEffect, useRef, useState } from 'react';
import type { GraphSubgraphDTO } from '../lib/generated/models';
import {
  mapGraphSubgraphToCanvas,
  CanvasNode,
  CanvasLink,
  NODE_KIND_COLORS,
  EDGE_STATUS_COLORS,
} from '../lib/read/graph';
import {
  translateStatus,
  formatEntityDisplayName,
} from '../lib/read/display';
import { TechnicalDetails, CopyableIdentifier } from './technical-details';

interface FalkorDBCanvasViewProps {
  subgraph: GraphSubgraphDTO;
  selectedDecisionPathId?: string | null;
  onSelectEvidenceId?: (id: string) => void;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

export function FalkorDBCanvasView({
  subgraph,
  selectedDecisionPathId,
  onSelectEvidenceId,
  isExpanded = false,
  onToggleExpand,
}: FalkorDBCanvasViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<any>(null);
  const [isClient, setIsClient] = useState(false);
  const [layoutMode, setLayoutMode] = useState<'force' | 'tree' | 'radial'>('force');
  const [selectedNode, setSelectedNode] = useState<CanvasNode | null>(null);
  const [selectedLink, setSelectedLink] = useState<CanvasLink | null>(null);
  const [showTableView, setShowTableView] = useState(false);
  const [showViewOptions, setShowViewOptions] = useState(false);

  // User manual interaction guard: do not override manual exploration on re-render
  const hasUserPannedRef = useRef(false);

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

          // Trigger auto-fit once when data signature initially updates
          setTimeout(() => {
            if (mounted && canvas?.zoomToFit && !hasUserPannedRef.current) {
              canvas.zoomToFit(0.15);
            }
          }, 150);
        }

        // Configure canvas behavior and styling
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
            onPan: () => {
              hasUserPannedRef.current = true;
            },
            onZoom: () => {
              hasUserPannedRef.current = true;
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

  // ResizeObserver: auto fit only on container dimension change if user hasn't actively explored
  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(() => {
      if (canvasRef.current?.zoomToFit && !hasUserPannedRef.current) {
        canvasRef.current.zoomToFit(0.15);
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const handleZoomIn = () => {
    hasUserPannedRef.current = true;
    if (canvasRef.current?.getZoom && canvasRef.current?.zoom) {
      const current = canvasRef.current.getZoom();
      canvasRef.current.zoom(current * 1.25);
    }
  };

  const handleZoomOut = () => {
    hasUserPannedRef.current = true;
    if (canvasRef.current?.getZoom && canvasRef.current?.zoom) {
      const current = canvasRef.current.getZoom();
      canvasRef.current.zoom(current * 0.8);
    }
  };

  const handleFit = () => {
    hasUserPannedRef.current = false;
    if (canvasRef.current?.zoomToFit) {
      canvasRef.current.zoomToFit(0.15);
    }
  };

  const hasDecisionPaths = stats.decisionPathEdges > 0;

  return (
    <div className={`canvas-view-container ${isExpanded ? 'canvas-expanded' : ''}`}>
      {/* 1. Grounded "What this graph shows" Caption */}
      <div className="canvas-grounded-caption">
        <div className="caption-icon" aria-hidden="true">🕸</div>
        <div className="caption-text-block">
          <span className="caption-heading">What this graph shows</span>
          <p className="caption-body">{stats.whatThisGraphShows}</p>
          {!hasDecisionPaths && (
            <p className="caption-no-path">
              <em>Note:</em> No recorded decision path is available in this view.
              The displayed contextual graph shows background infrastructure topology; it does not represent an isolated causal trace.
            </p>
          )}
        </div>
      </div>

      {/* 2. Top Controls & Action Bar */}
      <div className="canvas-toolbar">
        {/* Core Quick Action Buttons */}
        <div className="canvas-toolbar-group">
          <button
            type="button"
            className="canvas-btn"
            onClick={handleZoomIn}
            title="Zoom in graph view"
            aria-label="Zoom in"
          >
            + Zoom
          </button>
          <button
            type="button"
            className="canvas-btn"
            onClick={handleZoomOut}
            title="Zoom out graph view"
            aria-label="Zoom out"
          >
            − Zoom
          </button>
          <button
            type="button"
            className="canvas-btn highlight"
            onClick={handleFit}
            title="Fit graph to view bounds"
            aria-label="Fit graph to view"
          >
            Fit View
          </button>

          {onToggleExpand && (
            <button
              type="button"
              className="canvas-btn"
              onClick={onToggleExpand}
              title={isExpanded ? 'Collapse graph to side panel' : 'Expand graph to wide view'}
            >
              {isExpanded ? 'Collapse' : 'Expand Graph'}
            </button>
          )}
        </div>

        {/* View Options & Accessible Table Toggle */}
        <div className="canvas-toolbar-group">
          <div className="view-options-wrapper">
            <button
              type="button"
              className={`canvas-btn ${showViewOptions ? 'active' : ''}`}
              onClick={() => setShowViewOptions(!showViewOptions)}
              aria-expanded={showViewOptions}
            >
              View options ▾
            </button>

            {showViewOptions && (
              <div className="view-options-dropdown" role="region" aria-label="Graph display options">
                <label className="view-option-label" htmlFor="network-layout-select">
                  Network layout:
                </label>
                <select
                  id="network-layout-select"
                  className="canvas-select"
                  value={layoutMode}
                  onChange={(e) => {
                    setLayoutMode(e.target.value as any);
                    hasUserPannedRef.current = false;
                  }}
                >
                  <option value="force">Network layout (Force-directed)</option>
                  <option value="tree">Hierarchical flow (Tree)</option>
                  <option value="radial">Concentric rings (Radial)</option>
                </select>
              </div>
            )}
          </div>

          <button
            type="button"
            className={`canvas-toggle-btn ${showTableView ? 'active' : ''}`}
            onClick={() => setShowTableView(!showTableView)}
            aria-label="Toggle accessible tabular data view"
          >
            {showTableView ? 'Show Graph Canvas' : 'Accessible Table View'}
          </button>
        </div>
      </div>

      {/* 3. Accurate Graph Limit Messaging & Graph Bounds */}
      <div className="canvas-meta-bar">
        <div className="meta-stats-text">
          <strong>FalkorDB Subgraph:</strong> {stats.totalNodes} Nodes &bull; {stats.totalEdges} Edges ({stats.verifiedEdges} Verified, {stats.candidateEdges} Candidate)
        </div>

        <div className="meta-badges-group">
          {stats.searchLimited && (
            <span className="badge badge-warning" title="Traversal depth deliberately bounded by query policy">
              Limited graph view (bounded query)
            </span>
          )}
          {stats.truncated && (
            <span className="badge badge-warning" title="Results reached node capacity limit">
              Some connections are not shown
            </span>
          )}
        </div>
      </div>

      {/* 4. Main Stage Area: FalkorDB Canvas or Accessible Table */}
      <div className="canvas-stage-wrapper" ref={containerRef}>
        {!showTableView ? (
          <div className="canvas-element-container">
            {isClient ? (
              // @ts-expect-error Custom element registered dynamically by @falkordb/canvas
              <falkordb-canvas
                ref={canvasRef}
                style={{ width: '100%', height: isExpanded ? '680px' : '520px', display: 'block' }}
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
                    <th>Entity</th>
                    <th>Kind</th>
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
                      onClick={() => {
                        setSelectedLink(null);
                        setSelectedNode(n);
                      }}
                      tabIndex={0}
                    >
                      <td><code>{n.data.shortId}</code></td>
                      <td>
                        <span
                          className="kind-pill"
                          style={{ borderColor: n.color, color: n.color }}
                        >
                          {n.data.kind}
                        </span>
                      </td>
                      <td><strong>{n.caption}</strong></td>
                      <td>{translateStatus(n.data.status)}</td>
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
                              Evidence
                            </button>
                          ))
                        ) : (
                          <span className="muted">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <h4 style={{ marginTop: '1.25rem' }}>Accessible Graph Relationships ({canvasData.links.length})</h4>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Source Entity</th>
                    <th>Relationship</th>
                    <th>Target Entity</th>
                    <th>Verification</th>
                  </tr>
                </thead>
                <tbody>
                  {canvasData.links.map((l) => (
                    <tr
                      key={l.id}
                      className={selectedLink?.id === l.id ? 'row-selected' : ''}
                      onClick={() => {
                        setSelectedNode(null);
                        setSelectedLink(l);
                      }}
                      tabIndex={0}
                    >
                      <td><code>{formatEntityDisplayName({ id: String(l.source) }).primary}</code></td>
                      <td><strong>{l.readableRelationship}</strong></td>
                      <td><code>{formatEntityDisplayName({ id: String(l.target) }).primary}</code></td>
                      <td>
                        <span
                          className={`badge ${
                            l.data.verification_status === 'VERIFIED'
                              ? 'badge-verified'
                              : 'badge-candidate'
                          }`}
                        >
                          {translateStatus(l.data.verification_status)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 5. Attributed Inspector Drawer */}
        {(selectedNode || selectedLink) && (
          <aside className="canvas-inspector" aria-label="Graph Entity Details">
            <div className="inspector-header">
              <h3>{selectedNode ? selectedNode.caption : selectedLink?.readableRelationship}</h3>
              <button
                type="button"
                className="close-btn"
                onClick={() => {
                  setSelectedNode(null);
                  setSelectedLink(null);
                }}
                aria-label="Close details inspector"
              >
                ✕
              </button>
            </div>

            {selectedNode && (
              <div className="inspector-content">
                <div className="inspector-prop">
                  <span className="prop-name">Entity Type:</span>
                  <span
                    className="kind-pill"
                    style={{
                      borderColor: selectedNode.color,
                      color: selectedNode.color,
                    }}
                  >
                    {selectedNode.data.kind}
                  </span>
                </div>

                <div className="inspector-prop">
                  <span className="prop-name">Name / Description:</span>
                  <p className="prop-val font-semibold">{selectedNode.caption}</p>
                </div>

                <div className="inspector-prop">
                  <span className="prop-name">Operational Status:</span>
                  <span className="prop-val">{translateStatus(selectedNode.data.status)}</span>
                </div>

                {selectedNode.data.observed_at && (
                  <div className="inspector-prop">
                    <span className="prop-name">Observation Timestamp:</span>
                    <span className="prop-val">{selectedNode.data.observed_at}</span>
                  </div>
                )}

                <div className="inspector-prop">
                  <span className="prop-name">Decision Role:</span>
                  <span className="prop-val">
                    {selectedNode.data.is_decision_path ? (
                      <span className="badge badge-decision">IN RECORDED DECISION PATH</span>
                    ) : (
                      'Contextual Graph Entity'
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
                          Evidence ({eid.slice(-4)})
                        </button>
                      ))
                    ) : (
                      <span className="muted">None directly linked</span>
                    )}
                  </div>
                </div>

                {/* Technical Details for Node */}
                <div style={{ marginTop: '0.75rem' }}>
                  <TechnicalDetails
                    items={[
                      { label: 'Canonical Node ID', value: <code>{selectedNode.id}</code>, rawString: selectedNode.id },
                      { label: 'Graph Labels', value: <span>{selectedNode.labels.join(', ') || '—'}</span> },
                      { label: 'Raw Status', value: <code>{selectedNode.data.status || 'null'}</code>, rawString: selectedNode.data.status || undefined },
                    ]}
                  />
                </div>
              </div>
            )}

            {selectedLink && (
              <div className="inspector-content">
                <div className="inspector-prop">
                  <span className="prop-name">Relationship Type:</span>
                  <span className="prop-val font-semibold">{selectedLink.readableRelationship}</span>
                </div>

                <div className="inspector-prop">
                  <span className="prop-name">From Source:</span>
                  <p className="prop-val">{formatEntityDisplayName({ id: String(selectedLink.source) }).primary}</p>
                </div>

                <div className="inspector-prop">
                  <span className="prop-name">To Target:</span>
                  <p className="prop-val">{formatEntityDisplayName({ id: String(selectedLink.target) }).primary}</p>
                </div>

                <div className="inspector-prop">
                  <span className="prop-name">Verification Status:</span>
                  <span
                    className={`badge ${
                      selectedLink.data.verification_status === 'VERIFIED'
                        ? 'badge-verified'
                        : 'badge-candidate'
                    }`}
                  >
                    {translateStatus(selectedLink.data.verification_status)}
                  </span>
                </div>

                <div className="inspector-prop">
                  <span className="prop-name">Visual Representation:</span>
                  <span className="prop-val">
                    {selectedLink.data.verification_status === 'VERIFIED'
                      ? 'Solid Line (Verified Knowledge)'
                      : 'Dashed Line (Candidate / Hypothesis)'}
                  </span>
                </div>

                {selectedLink.data.observed_at && (
                  <div className="inspector-prop">
                    <span className="prop-name">Observed Timestamp:</span>
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
                          Evidence ({eid.slice(-4)})
                        </button>
                      ))
                    ) : (
                      <span className="muted">None directly linked</span>
                    )}
                  </div>
                </div>

                {/* Technical Details for Relationship */}
                <div style={{ marginTop: '0.75rem' }}>
                  <TechnicalDetails
                    items={[
                      { label: 'Edge ID', value: <code>{selectedLink.id}</code>, rawString: selectedLink.id },
                      { label: 'Raw Relationship', value: <code>{selectedLink.relationship}</code>, rawString: selectedLink.relationship },
                      { label: 'Raw Source ID', value: <code>{String(selectedLink.source)}</code>, rawString: String(selectedLink.source) },
                      { label: 'Raw Target ID', value: <code>{String(selectedLink.target)}</code>, rawString: String(selectedLink.target) },
                    ]}
                  />
                </div>
              </div>
            )}
          </aside>
        )}
      </div>

      {/* 6. Visual Graph Legend & Technical Subgraph Revision */}
      <footer className="canvas-legend" aria-label="Graph Visualization Legend">
        <div className="legend-section">
          <span className="legend-title">Entity Kinds:</span>
          <span className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: NODE_KIND_COLORS.Incident }} />
            Incident
          </span>
          <span className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: NODE_KIND_COLORS.InfrastructureAsset }} />
            Infrastructure Asset
          </span>
          <span className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: NODE_KIND_COLORS.Observation }} />
            Observation
          </span>
          <span className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: NODE_KIND_COLORS.Evidence }} />
            Evidence
          </span>
          <span className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: NODE_KIND_COLORS.Hypothesis }} />
            Hypothesis
          </span>
        </div>

        <div className="legend-section">
          <span className="legend-title">Relationships:</span>
          <span className="legend-item">
            <span className="legend-line" style={{ backgroundColor: EDGE_STATUS_COLORS.verified }} />
            Verified (Solid)
          </span>
          <span className="legend-item">
            <span className="legend-line legend-dashed" style={{ borderColor: EDGE_STATUS_COLORS.candidate }} />
            Candidate (Dashed)
          </span>
          <span className="legend-item">
            <span className="legend-line" style={{ backgroundColor: EDGE_STATUS_COLORS.decisionPath, height: '3px' }} />
            Decision Path (Highlighted)
          </span>
        </div>

        {/* Technical Subgraph Details */}
        <div style={{ width: '100%', marginTop: '0.5rem' }}>
          <TechnicalDetails
            title="Technical graph metadata & revision"
            items={[
              { label: 'Graph Revision', value: <span>{stats.graphRevision}</span>, rawString: String(stats.graphRevision) },
              { label: 'As Of', value: <span>{stats.asOf}</span>, rawString: stats.asOf },
              { label: 'Query Search Limited', value: <span>{stats.searchLimited ? 'True (Bounded)' : 'False'}</span> },
              { label: 'Result Set Truncated', value: <span>{stats.truncated ? 'True' : 'False'}</span> },
            ]}
          />
        </div>
      </footer>
    </div>
  );
}
