import type {SSEStream} from '../generated/models.ts';
import {validSchema} from './validation.ts';

export type SSEConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'reconnecting';

export interface SSEParsedFrame {
  id?: string;
  event?: string;
  data?: string;
}

export interface SSEParserState {
  buffer: string;
  currentFrame: {
    id?: string;
    event?: string;
    dataLines: string[];
  };
}

export function createParserState(): SSEParserState {
  return {
    buffer: '',
    currentFrame: {
      dataLines: [],
    },
  };
}

export function parseSSEChunk(
  chunk: string,
  state: SSEParserState
): SSEParsedFrame[] {
  state.buffer += chunk;
  const frames: SSEParsedFrame[] = [];
  const lines = state.buffer.split(/\r?\n/);
  // The last entry after split is an incomplete line if buffer didn't end with newline
  state.buffer = lines.pop() ?? '';

  for (const rawLine of lines) {
    const line = rawLine;

    // Blank line indicates dispatch of the current frame
    if (line === '') {
      if (
        state.currentFrame.dataLines.length > 0 ||
        state.currentFrame.event !== undefined ||
        state.currentFrame.id !== undefined
      ) {
        frames.push({
          id: state.currentFrame.id,
          event: state.currentFrame.event,
          data: state.currentFrame.dataLines.length > 0
            ? state.currentFrame.dataLines.join('\n')
            : undefined,
        });
      }
      state.currentFrame = { dataLines: [] };
      continue;
    }

    // Comment line ignored (e.g. ": heartbeat" or ": reconnect")
    if (line.startsWith(':')) {
      continue;
    }

    const colonIndex = line.indexOf(':');
    let field = line;
    let value = '';

    if (colonIndex !== -1) {
      field = line.slice(0, colonIndex);
      value = line.slice(colonIndex + 1);
      // Strip leading space if present
      if (value.startsWith(' ')) {
        value = value.slice(1);
      }
    }

    if (field === 'id') {
      state.currentFrame.id = value;
    } else if (field === 'event') {
      state.currentFrame.event = value;
    } else if (field === 'data') {
      state.currentFrame.dataLines.push(value);
    }
  }

  return frames;
}

export interface SSEClientOptions {
  token: string | null;
  investigationId?: string;
  baseUrl?: string;
  fetcher?: typeof fetch;
  initialCursor?: string | null;
  onEvent?: (event: { name: string; streamEvent?: SSEStream; rawData?: unknown; cursor?: string }) => void;
  onStatusChange?: (status: SSEConnectionStatus) => void;
  onRefetchRequired?: (reason: string) => void;
  onUnauthorized?: () => void;
  onError?: (err: Error) => void;
}

export class SSEClient {
  private status: SSEConnectionStatus = 'disconnected';
  private abortController: AbortController | null = null;
  private lastEventId: string | null = null;
  private token: string | null = null;
  private investigationId?: string;
  private baseUrl: string;
  private fetcher: typeof fetch;
  private isDestroyed = false;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectAttempt = 0;

  private onEvent?: (event: { name: string; streamEvent?: SSEStream; rawData?: unknown; cursor?: string }) => void;
  private onStatusChange?: (status: SSEConnectionStatus) => void;
  private onRefetchRequired?: (reason: string) => void;
  private onUnauthorized?: () => void;
  private onError?: (err: Error) => void;

  constructor(options: SSEClientOptions) {
    this.token = options.token;
    this.investigationId = options.investigationId;
    this.baseUrl = options.baseUrl ?? '/api/v1/events/stream';
    this.fetcher = options.fetcher ?? ((...args) => fetch(...args));
    this.lastEventId = options.initialCursor ?? null;

    this.onEvent = options.onEvent;
    this.onStatusChange = options.onStatusChange;
    this.onRefetchRequired = options.onRefetchRequired;
    this.onUnauthorized = options.onUnauthorized;
    this.onError = options.onError;
  }

  getStatus(): SSEConnectionStatus {
    return this.status;
  }

  getLastEventId(): string | null {
    return this.lastEventId;
  }

  setToken(token: string | null) {
    const changed = this.token !== token;
    this.token = token;
    if (changed && this.status !== 'disconnected') {
      this.reconnect(true);
    }
  }

  setInvestigationId(investigationId?: string) {
    const changed = this.investigationId !== investigationId;
    this.investigationId = investigationId;
    if (changed && this.status !== 'disconnected') {
      // Different scope: reconnect and request fresh authoritative data
      this.reconnect(true);
    }
  }

  start() {
    if (this.isDestroyed) return;
    this.abortController?.abort();
    this.clearReconnectTimer();
    this.reconnectAttempt = 0;
    this.connectLoop();
  }

  stop() {
    this.isDestroyed = true;
    this.clearReconnectTimer();
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
    this.setStatus('disconnected');
  }

  private setStatus(status: SSEConnectionStatus) {
    if (this.status !== status) {
      this.status = status;
      this.onStatusChange?.(status);
    }
  }

  private clearReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private reconnect(resetBackoff = false) {
    if (this.isDestroyed) return;
    this.clearReconnectTimer();
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
    if (resetBackoff) {
      this.reconnectAttempt = 0;
    }

    const backoff = Math.min(1000 * Math.pow(1.5, this.reconnectAttempt), 10000);
    this.reconnectAttempt++;
    this.setStatus('reconnecting');

    this.reconnectTimer = setTimeout(() => {
      this.connectLoop();
    }, backoff);
  }

  private async connectLoop() {
    if (this.isDestroyed) return;

    if (!this.token) {
      this.setStatus('disconnected');
      return;
    }

    this.setStatus(this.reconnectAttempt > 0 ? 'reconnecting' : 'connecting');
    this.abortController = new AbortController();
    const signal = this.abortController.signal;

    const url = new URL(this.baseUrl, 'http://127.0.0.1');
    if (this.lastEventId !== null && this.lastEventId !== undefined) {
      url.searchParams.set('cursor', this.lastEventId);
    }
    if (this.investigationId) {
      url.searchParams.set('investigation_id', this.investigationId);
    }

    const headers: Record<string, string> = {
      Accept: 'text/event-stream',
      Authorization: `Bearer ${this.token}`,
    };
    if (this.lastEventId !== null && this.lastEventId !== undefined) {
      headers['Last-Event-ID'] = this.lastEventId;
    }

    try {
      const response = await this.fetcher(url.pathname + url.search, {
        method: 'GET',
        headers,
        signal,
        cache: 'no-store',
        credentials: 'omit',
      });

      if (signal.aborted) return;

      // Handle 401 Unauthorized
      if (response.status === 401) {
        this.setStatus('disconnected');
        this.onUnauthorized?.();
        return;
      }

      // Handle 409 Cursor conflict / expired / future
      if (response.status === 409 || response.status === 422) {
        // As per backend contract: cursor is invalid/expired/future.
        // Reset cursor to null and trigger authoritative full refetch.
        this.lastEventId = null;
        this.onRefetchRequired?.('cursor_reset');
        this.reconnect(true);
        return;
      }

      if (!response.ok) {
        throw new Error(`SSE stream returned HTTP ${response.status}`);
      }

      if (!response.body) {
        throw new Error('SSE stream returned empty response body');
      }

      this.setStatus('connected');
      this.reconnectAttempt = 0;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      const parserState = createParserState();

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          // Normal stream end (backend 30s cycle)
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const frames = parseSSEChunk(chunk, parserState);

        for (const frame of frames) {
          if (frame.id !== undefined) {
            this.lastEventId = frame.id;
          }

          const eventName = frame.event ?? 'message';

          if (eventName === 'cursor') {
            try {
              const data = JSON.parse(frame.data ?? '{}');
              if (typeof data.cursor === 'number' || typeof data.cursor === 'string') {
                this.lastEventId = String(data.cursor);
              }
            } catch {
              // ignore invalid cursor json
            }
            continue;
          }

          if (eventName === 'error') {
            try {
              const data = JSON.parse(frame.data ?? '{}');
              if (data.code === 'UNAUTHORIZED') {
                this.setStatus('disconnected');
                this.onUnauthorized?.();
                return;
              }
            } catch {
              // ignore
            }
          }

          let streamEvent: SSEStream | undefined;
          let rawData: unknown;
          if (frame.data) {
            try {
              rawData = JSON.parse(frame.data);
              if (validSchema('SSEStream', rawData)) {
                streamEvent = rawData as SSEStream;
                this.lastEventId = String(streamEvent.cursor);
              }
            } catch {
              // Non-JSON or raw payload
            }
          }

          this.onEvent?.({
            name: eventName,
            streamEvent,
            rawData,
            cursor: this.lastEventId ?? undefined,
          });

          // Ground truth rule: any data event signals state change requiring authoritative sync
          this.onRefetchRequired?.(eventName);
        }
      }

      // Backend 30s cycle completed normally; refetch and cycle
      this.onRefetchRequired?.('stream_cycle');
      this.reconnect(true);
    } catch (err: unknown) {
      if (signal.aborted || this.isDestroyed) return;
      this.onError?.(err instanceof Error ? err : new Error(String(err)));
      this.reconnect();
    }
  }
}
