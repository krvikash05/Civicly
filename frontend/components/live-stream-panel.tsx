'use client';

import React, { useState } from 'react';
import type { LiveFeedItem } from './use-event-stream.ts';
import type { SSEConnectionStatus } from '../lib/api/sse.ts';

interface LiveStreamPanelProps {
  status: SSEConnectionStatus;
  lastEventId: string | null;
  events: LiveFeedItem[];
  onReconnect?: () => void;
  onClear?: () => void;
  title?: string;
  defaultExpanded?: boolean;
}

export function LiveStreamPanel({
  status,
  lastEventId,
  events,
  onReconnect,
  onClear,
  title = 'Live Backend Event Stream',
  defaultExpanded = true,
}: LiveStreamPanelProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  const getStatusBadge = () => {
    switch (status) {
      case 'connected':
        return (
          <span className="stream-badge status-connected">
            <span className="status-pulse-dot pulse-green"></span>
            Connected {lastEventId ? `(#${lastEventId})` : ''}
          </span>
        );
      case 'connecting':
        return (
          <span className="stream-badge status-connecting">
            <span className="status-pulse-dot pulse-amber"></span>
            Connecting…
          </span>
        );
      case 'reconnecting':
        return (
          <span className="stream-badge status-reconnecting">
            <span className="status-pulse-dot pulse-amber"></span>
            Reconnecting…
          </span>
        );
      case 'disconnected':
      default:
        return (
          <span className="stream-badge status-disconnected">
            <span className="status-pulse-dot pulse-gray"></span>
            Disconnected
          </span>
        );
    }
  };

  const getEventTag = (name: string) => {
    switch (name) {
      case 'decision_recorded':
        return { label: 'Decision Recorded', css: 'tag-decision' };
      case 'case_tool_called':
        return { label: 'Tool Executed', css: 'tag-tool' };
      case 'case_updated':
        return { label: 'Case Updated', css: 'tag-case' };
      case 'inspection_recorded':
        return { label: 'Inspection Recorded', css: 'tag-inspection' };
      case 'inspection_requested':
        return { label: 'Inspection Requested', css: 'tag-inspection-req' };
      case 'approval_needed':
        return { label: 'Approval Needed', css: 'tag-approval' };
      case 'work_order_updated':
        return { label: 'Work Order Updated', css: 'tag-work' };
      case 'case_reopened':
        return { label: 'Recurrence Detected', css: 'tag-recurrence' };
      case 'error':
        return { label: 'Stream Error', css: 'tag-error' };
      default:
        return { label: name, css: 'tag-default' };
    }
  };

  return (
    <div className="live-stream-panel">
      <div className="stream-panel-header">
        <div className="stream-header-left">
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            className="stream-toggle-button"
            aria-expanded={expanded}
          >
            <span className="stream-toggle-arrow">{expanded ? '▼' : '▶'}</span>
            <strong>{title}</strong>
          </button>
          {getStatusBadge()}
        </div>
        <div className="stream-header-actions">
          {events.length > 0 && onClear && (
            <button type="button" onClick={onClear} className="stream-action-btn">
              Clear feed
            </button>
          )}
          {status !== 'connected' && onReconnect && (
            <button
              type="button"
              onClick={onReconnect}
              className="stream-action-btn primary-action"
            >
              Reconnect
            </button>
          )}
        </div>
      </div>

      {expanded && (
        <div className="stream-panel-body">
          <div className="stream-disclaimer">
            <strong>Architecture Notice:</strong> Persisted event stream over authenticated SSE.
            Stream events signal state changes; authoritative state is continuously re-synchronized via
            validated GET endpoints. Zero simulated or fabricated reasoning steps.
          </div>

          {events.length === 0 ? (
            <div className="stream-empty">
              No live mutation events received in this window. Stream is active and listening for persisted backend events.
            </div>
          ) : (
            <div className="stream-event-list">
              {events.map((ev) => {
                const tag = getEventTag(ev.name);
                const time = ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : '';
                const se = ev.streamEvent;
                return (
                  <div key={ev.id} className="stream-event-item">
                    <div className="stream-event-top">
                      <span className={`stream-event-tag ${tag.css}`}>{tag.label}</span>
                      {ev.cursor && <span className="stream-cursor">cursor #{ev.cursor}</span>}
                      <span className="stream-time">{time}</span>
                    </div>
                    <div className="stream-event-content">
                      {se ? (
                        <>
                          <span className="stream-entity-id">{se.entity_id}</span>
                          {se.investigation_id && (
                            <span className="stream-inv-id">
                              (inv: <code>{se.investigation_id}</code>)
                            </span>
                          )}
                          {se.payload?.operation && (
                            <span className="stream-operation">
                              op: <code>{se.payload.operation}</code>
                            </span>
                          )}
                          {se.source_kind && (
                            <span className="stream-source-kind">[{se.source_kind}]</span>
                          )}
                        </>
                      ) : (
                        <span className="stream-raw-data">{JSON.stringify(ev.rawData ?? {})}</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
