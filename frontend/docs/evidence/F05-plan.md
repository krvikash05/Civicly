# F05 Implementation Plan: Authenticated Fetch SSE, Persisted Event & Cursor Frames, Reconnect/Refetch

## Objective
Implement microtask **`F05`**:
- Authenticated fetch-based SSE stream over `/api/v1/events/stream` (not unauthenticated native `EventSource`).
- Parse real SSE frames: `id`, `event`, `data`.
- Handle cursor control: retain `Last-Event-ID` across reconnects.
- Handle error boundaries: 409 `CURSOR_EXPIRED`/`CURSOR_FUTURE`/`CURSOR_CONFLICT` reset cursor to 0 and trigger authoritative full refetch.
- Handle session boundaries: 401 invalidates session and stops retrying.
- Authoritative state synchronization: on reconnect or incoming state events, trigger authoritative GET refetches; never treat the SSE stream as sole ground truth.
- Honest presentation: zero fabricated or simulated "thinking" animations; events reflect persisted backend mutations and recorded traces only.

## Files to Touch
1. `frontend/lib/api/proxy.ts`: Allow `/api/v1/events/stream` through proxy, forward `Last-Event-ID` header, stream response body with `text/event-stream`.
2. `frontend/lib/api/sse.ts`: Streaming client implementing fetch-based SSE reader, chunk parser, backoff reconnect, cursor tracking, and event emitter.
3. `frontend/components/use-event-stream.ts`: React hook connecting SSE to `useDemo` session and selected investigation context.
4. `frontend/components/live-stream-panel.tsx`: UI component displaying live connection status, event feed, and authoritative refetch indicators.
5. `frontend/app/page.tsx` & `frontend/components/investigation-workspace.tsx`: Integrate live stream panel and trigger cache revalidation on events.
6. `frontend/app/globals.css`: Styles for live stream feed, pulse badge, and event cards.
7. `frontend/tests/sse.test.ts`: Unit tests for parser, cursor management, error recovery, and event dispatching.
8. `frontend/scripts/integration_probe.ts`: Add real probe for `/api/v1/events/stream`.
9. `frontend/scripts/verify_integration.py`: Verify SSE streaming in isolated runtime.

## Invariants & Guardrails
- R01–R18 preserved; explainability R15 enforced.
- Memory-only tokens; no credentials in logs, URLs, or browser storage.
- Proxy allows only loopback hosts; no unauthorized route bypassing.
