# Gemini provider and spending accounting — B10-O-R2

Scope: Google Gemini Developer API, `gemini-3.8-flash`, v1beta
`generateContent` / `countTokens`. No live provider calls were authorized in R2.
Machine contract: `contracts/gemini_provider.json`; source:
`app.agents.{limits,provider,tokens,spending,models,runtime}`.

Google's [billing FAQ](https://ai.google.dev/gemini-api/docs/billing) calls token
counting unbilled; its [Count Tokens guide](https://firebase.google.com/docs/ai-logic/count-tokens)
explicitly identifies countTokens as having no charge and includes Gemini3.8.
The [REST reference](https://ai.google.dev/api/tokens) defines the input count,
not generated usage. This policy does not establish free generation or free
arbitrary endpoints. Source verification is2026-10-18, reverify before2027-01-01.
No undocumented billable count tariff is implemented.

For each new count attempt the host still checks live permission, exact scope,
concurrency and atomic financial reservation before sending. Its request ID and
immutable RESERVE/RECONCILE events remain. A verified endpoint contract settles
cost to zero immediately. Valid returned input count, policy version and completion
outcome are retained under count-specific metadata. HTTP errors/invalid payloads
and transport timeouts remain errors; a timeout's completion stays unconfirmed,
while billing is known zero for this verified nonbillable endpoint. Unknown or
expired policy retains the full reservation, including after reopen. Counting
never creates generation token_usage or fabricates zero-token generation receipts.
Historical count/charge/reservation rows are not automatically reclassified.

Generation remains independently reserved before every attempt, priced using the
versioned standard-text schedule, and reconciled only with validated usage. The
financial fence uses the greater of its conservative serialized-byte allowance
and known/planned input token count, plus twice the configured output price
allowance. That byte-based financial fence is not a model-token count. Missing
generation billing/usage keeps its dollar/token allowances held; over-reservation
charges preserve exact-request holds and audited operator recovery. Existing
immutable events, session locks, project/case caps and warning thresholds remain.

## Independent token and money controls

| Control | Current value / meaning |
|---|---|
| Published input limit |1048576 tokens per request, verified in [model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash) |
| Published output limit |65536 tokens per request |
| Configured output |4096 by default, separately configurable up to published limit |
| Offline request plan |SHA-pinned Gemma3 proxy +25%/256 framing allowance; expressly not exact Gemini3.8 |
| Authorized counted plan |Full generateContentRequest count +16 framing planning margin +configured output |
| New cumulative standard |400000 tokens, including known usage +unknown held attempt allowances |
| Complex token profile |800000, explicit host selection; no monetary authorization |
| Configurable token maximum |2000000, finite cumulative allowance, not provider request capacity |
| Checkpoint counter storage |4000000, so an overrun beyond the configured allowance can be recorded exactly and paused |
| New-ledger money |$8 project /$.50 default investigation /one concurrent session |
| Explicit complex money |Up to$1.50, separate approval/allocation and remaining-project checks |
| Other defaults |16 iterations /8tools /240seconds per wake /5wakes; recursion150 unchanged |

The standard token profile is sized from eight of the largest accepted actual
B09/MCP request plans:8×46721=373768, rounded up to50000 gives400000. Complex doubles
that allowance for16 such decisions. This is a bounded sizing policy, subsequently
checked with full multi-step contexts and plausible simulated receipts, not a
claim about genuine Gemini usage or billed savings. Actual receipt totals replace
only their own attempt's token reservation; unknown attempts remain conservative.
Every context includes all16 approved schemas and unchanged prompt B10-3. No
source/history/contradiction fields were dropped to make the benchmark fit.

## Configuration and existing state

`CIVICLY_LLM_MAX_INPUT_TOKENS` defaults1048576 and may lower that cap.
`CIVICLY_LLM_MAX_OUTPUT_TOKENS` defaults4096; maximum65536. Request input capacity
uses the reported count when available; the extra16 framing tokens are a cumulative
planning allowance, not a reduction of the published model input capacity.
`--max-tokens` configures cumulative allowance instead. A new CLI investigation
uses standard by default; `--budget-profile complex` selects800000 without changing
its dollar cap. Profiles and custom --max-tokens are mutually exclusive.

Previously persisted60000-token Budget values stay60000 when decoded. Resume
without new flags never upgrades them. Under a **separate authorized live
invocation only**, a trusted operator may use `--resume --budget-profile standard
--budget-reason 'Reviewed cumulative allocation increase'` or an explicit larger
--max-tokens. Existing --live opt-in and exact case/thread are still required.
The host validates monotonic increases before ownership, records prior/current/
reason in the same checkpoint, preserves accumulated tokens, native journal IDs
and source/evidence revision refresh. Dollar-cap increases use their separate
explicit --max-cost-usd /audited ledger configuration procedures in the runtime
guide. Raising tokens alone cannot raise or reset monetary limits.

No ledger schema migration is required in R2: existing requests, accounting_events,
token_usage/floors, config/cases, sessions and holds retain their format. No existing
private ledger is upgraded or reset by code defaults. Unknown historical billing
requires verified exact-request operator accounting; never delete reservations.

A genuine cumulative-token or money limit creates an explicit TOKEN_BUDGET or
PROJECT_SPENDING_CAP /INVESTIGATION_SPENDING_CAP pause with a durable checkpoint.
That is not resolution or verification. After approved increases, resume the same
thread; do not start a replacement investigation to bypass cumulative accounting.

Normal development uses MockTransport and the inherited HTTPX/DNS deny interlock.
A configured key grants no permission. Google token counting is an external call
even though nonbillable and remains prohibited during this corrective task.
See `docs/evidence/B10OR2-COMMANDS.md` for reproducible zero-provider tests and
`AGENTS_RUNTIME.md` for the still-unexecuted, separately approved live gate.

The provider records `TOKEN_BUDGET` when its next request cannot fit; the supervisor can also pause as `BUDGET_EXHAUSTED` when an iteration, tool, wake, time or cumulative-token boundary is already reached. Both persist the same thread before operator review.

Outer request-deadline cancellation also distinguishes stages: a count-only request reports `NOT_GENERATED`; `reservation_retained` is derived from the exact attempts and their count-policy settlements or generation holds. A settled-zero count does not create an uncertain-generation summary. Unknown count policy and missing generation receipts still report retained allowances.
