'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { SSEClient, type SSEConnectionStatus } from '../lib/api/sse.ts';
import type { SSEStream } from '../lib/generated/models.ts';

export interface LiveFeedItem {
  id: string;
  name: string;
  timestamp: string;
  cursor?: string;
  streamEvent?: SSEStream;
  rawData?: unknown;
}

export interface UseEventStreamOptions {
  token: string | null;
  investigationId?: string;
  onRefetch?: (reason: string) => void;
  maxEvents?: number;
}

export function useEventStream(options: UseEventStreamOptions) {
  const { token, investigationId, onRefetch, maxEvents = 50 } = options;
  const [status, setStatus] = useState<SSEConnectionStatus>('disconnected');
  const [lastEventId, setLastEventId] = useState<string | null>(null);
  const [events, setEvents] = useState<LiveFeedItem[]>([]);

  const clientRef = useRef<SSEClient | null>(null);
  const onRefetchRef = useRef(onRefetch);
  onRefetchRef.current = onRefetch;

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  const reconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.start();
    }
  }, []);

  useEffect(() => {
    if (!token) {
      setStatus('disconnected');
      return;
    }

    let debounceTimer: ReturnType<typeof setTimeout> | null = null;

    const client = new SSEClient({
      token,
      investigationId,
      onStatusChange: (nextStatus) => {
        setStatus(nextStatus);
      },
      onEvent: (ev) => {
        setLastEventId(ev.cursor ?? null);
        const item: LiveFeedItem = {
          id: ev.streamEvent?.event_id ?? (crypto.randomUUID ? crypto.randomUUID() : String(Date.now() + Math.random())),
          name: ev.name,
          timestamp: ev.streamEvent?.timestamp ?? new Date().toISOString(),
          cursor: ev.cursor,
          streamEvent: ev.streamEvent,
          rawData: ev.rawData,
        };
        setEvents((prev) => [item, ...prev].slice(0, maxEvents));
      },
      onRefetchRequired: (reason) => {
        if (debounceTimer) {
          clearTimeout(debounceTimer);
        }
        debounceTimer = setTimeout(() => {
          onRefetchRef.current?.(reason);
        }, 1200);
      },
    });

    clientRef.current = client;
    client.start();

    return () => {
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }
      client.stop();
      clientRef.current = null;
    };
  }, [token, investigationId, maxEvents]);

  return {
    status,
    lastEventId,
    events,
    clearEvents,
    reconnect,
  };
}
