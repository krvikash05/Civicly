'use client';

import React, { useState } from 'react';
import type { LiveFeedItem } from './use-event-stream.ts';
import {translateStatus,formatEntityDisplayName} from '../lib/read/display';
import {TechnicalDetails} from './technical-details';
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
  title = 'Saved case updates',
  defaultExpanded = true,
}: LiveStreamPanelProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  const getStatusBadge = () => {
    switch (status) {
      case 'connected':
        return (
          <span className="stream-badge status-connected">
            <span className="status-pulse-dot pulse-green"></span>
            Connected to saved updates
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
        return { label: translateStatus(name), css: 'tag-default' };
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
            These are saved case events. The workspace reloads records when updates arrive. A connected feed does not mean an AI agent is currently running.
          </div>

          {events.length === 0 ? (
            <div className="stream-empty">
              No saved updates have arrived during this viewing session. This does not mean the case has no earlier history.
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

                      <span className="stream-time">{time}</span>
                    </div>
                    <div className="stream-event-content">
                      {se ? (
                        <>
                          <span>{formatEntityDisplayName({id:se.entity_id}).primary}</span>
                          {se.payload?.operation && <span> · {translateStatus(String(se.payload.operation))}</span>}
                          {se.source_kind && <span> · {translateStatus(se.source_kind)}</span>}
                          <TechnicalDetails title="Update references" items={[
                            {label:'Record ID',value:<code>{se.entity_id}</code>,rawString:se.entity_id},
                            {label:'Event type',value:<code>{ev.name}</code>},
                            {label:'Stream position',value:<code>{ev.cursor||'Not recorded'}</code>},
                          ]}/>

                        </>
                      ) : (
                        <span>Connection or replay information received. The case records remain the source of truth.</span>
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
