import test from 'node:test';
import assert from 'node:assert/strict';
import {
  parseSSEChunk,
  createParserState,
  SSEClient,
} from '../lib/api/sse.ts';

test('parseSSEChunk handles standard SSE frames with id, event, and data', () => {
  const state = createParserState();
  const chunk = 'id: 42\nevent: case_updated\ndata: {"entity_id":"INC-001"}\n\n';
  const frames = parseSSEChunk(chunk, state);

  assert.equal(frames.length, 1);
  assert.equal(frames[0].id, '42');
  assert.equal(frames[0].event, 'case_updated');
  assert.equal(frames[0].data, '{"entity_id":"INC-001"}');
});

test('parseSSEChunk ignores comment lines like heartbeats', () => {
  const state = createParserState();
  const chunk = ': heartbeat\n\n: reconnect and refetch\n\nid: 10\nevent: cursor\ndata: {"cursor":10}\n\n';
  const frames = parseSSEChunk(chunk, state);

  assert.equal(frames.length, 1);
  assert.equal(frames[0].id, '10');
  assert.equal(frames[0].event, 'cursor');
});

test('parseSSEChunk handles multi-line data and buffer splits across chunks', () => {
  const state = createParserState();
  const chunk1 = 'id: 99\nevent: decision_recorded\ndata: {"step":1,';
  const chunk2 = '"decision":"DISPATCH"}\n\n';

  const frames1 = parseSSEChunk(chunk1, state);
  assert.equal(frames1.length, 0); // incomplete frame

  const frames2 = parseSSEChunk(chunk2, state);
  assert.equal(frames2.length, 1);
  assert.equal(frames2[0].id, '99');
  assert.equal(frames2[0].event, 'decision_recorded');
  assert.equal(frames2[0].data, '{"step":1,"decision":"DISPATCH"}');
});

test('SSEClient disconnects without token', () => {
  const client = new SSEClient({
    token: null,
  });

  client.start();
  assert.equal(client.getStatus(), 'disconnected');
  client.stop();
});

test('SSEClient connects and dispatches events on 200 stream', async () => {
  let requestedUrl = '';
  let requestedHeaders: Record<string, string> = {};

  const streamBody = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();
      controller.enqueue(
        encoder.encode(
          'id: 101\nevent: case_updated\ndata: {"event_id":"EVT-1","timestamp":"2026-10-18T10:00:00Z","cursor":101,"id":"EVT-1","event_type":"INCIDENT_UPDATED","entity_id":"INC-1","investigation_id":"INV-1","revision":1,"occurred_at":"2026-10-18T10:00:00Z","source_kind":"MUNICIPAL_FEED","simulation_mode":"SIMULATED","payload_schema_version":1,"payload":{},"source_ref":"FEED-1"}\n\n'
        )
      );
      controller.close();
    },
  });

  const mockFetcher: typeof fetch = async (url, init) => {
    requestedUrl = String(url);
    requestedHeaders = Object.fromEntries(new Headers(init?.headers).entries());
    return new Response(streamBody, {
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' },
    });
  };

  const receivedEvents: string[] = [];
  let refetchCount = 0;

  const client = new SSEClient({
    token: 'test-token-123',
    investigationId: 'INV-1',
    fetcher: mockFetcher,
    onEvent: (ev) => {
      receivedEvents.push(ev.name);
    },
    onRefetchRequired: () => {
      refetchCount++;
    },
  });

  client.start();

  // Wait for stream to consume
  await new Promise((r) => setTimeout(r, 60));

  assert.match(requestedUrl, /investigation_id=INV-1/);
  assert.equal(requestedHeaders['authorization'], 'Bearer test-token-123');
  assert.equal(requestedHeaders['accept'], 'text/event-stream');
  assert.equal(receivedEvents.length, 1);
  assert.equal(receivedEvents[0], 'case_updated');
  assert.equal(client.getLastEventId(), '101');
  assert(refetchCount >= 1);

  client.stop();
});

test('SSEClient on 401 triggers onUnauthorized and disconnects without retrying', async () => {
  let unauthorizedFired = false;
  let fetchAttempts = 0;

  const mockFetcher: typeof fetch = async () => {
    fetchAttempts++;
    return new Response(JSON.stringify({ error: { code: 'UNAUTHORIZED' } }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  };

  const client = new SSEClient({
    token: 'expired-token',
    fetcher: mockFetcher,
    onUnauthorized: () => {
      unauthorizedFired = true;
    },
  });

  client.start();
  await new Promise((r) => setTimeout(r, 40));

  assert.equal(unauthorizedFired, true);
  assert.equal(client.getStatus(), 'disconnected');
  assert.equal(fetchAttempts, 1); // No infinite retry loop on 401

  client.stop();
});

test('SSEClient on 409 resets cursor and triggers onRefetchRequired', async () => {
  let refetchReasons: string[] = [];
  let attempt = 0;

  const mockFetcher: typeof fetch = async (url, init) => {
    attempt++;
    const headers = new Headers(init?.headers);
    if (attempt === 1) {
      assert.equal(headers.get('Last-Event-ID'), '999');
      return new Response(JSON.stringify({ error: { code: 'CURSOR_EXPIRED' } }), {
        status: 409,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    // Second attempt should not send the stale cursor
    assert.equal(headers.get('Last-Event-ID'), null);
    return new Response(new ReadableStream({ start(c) { c.close(); } }), {
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' },
    });
  };

  const client = new SSEClient({
    token: 'valid-token',
    initialCursor: '999',
    fetcher: mockFetcher,
    onRefetchRequired: (reason) => {
      refetchReasons.push(reason);
    },
  });

  client.start();
  await new Promise((r) => setTimeout(r, 60));

  assert.equal(client.getLastEventId(), null);
  assert(refetchReasons.includes('cursor_reset'));

  client.stop();
});
