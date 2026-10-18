# B10-O-R2 — PASS, human review pending

Scope: B10-O-R2 only, against locally committed accepted B10-O-R baseline
`af42149` (740PASS). No push, ZIP, Gemini/countTokens request or B11.
All18 requirements remain binding. This correction cannot complete B10's genuine
live model acceptance, GraphRAG, municipal operations, API or frontend.

## Root causes and corrected behavior

1. **Endpoint billing was conflated with generation uncertainty.** Every count
   request was financially reserved, then marked COUNT_BILLING_UNCONFIRMED even
   under Google's verified nonbillable countTokens policy. New endpoint/model/
   version/time-bound CountBillingPolicy distinguishes completion from billing.
   Count requests retain unique IDs and immutable reserve/reconcile events;
   known nonbilling settles zero, with returned input count/outcome/policy stored
   separately from generation usage. Count errors still fail; timeout completion
   stays unknown. Unknown/expired policy retains the reservation. No invented
   billable count tariff, arbitrary-endpoint exemption or automatic historical
   release. Explicit live permission remains required for counting.
2. **A per-investigation60000-token allowance was effectively one large request.**
   Request input/output capacity, full-request token plan, cumulative usage,
   independent dollars and iteration/tool/time/wake budgets now have separate
   named controls. New standard400000/complex800000/max2000000, provider input
   1048576/output65536, configured output4096. Counter storage4000000 allows
   exact overrun recording. Known input count is compared to model input capacity;
   the16-token framing margin belongs to cumulative planning. Financial reservation
   uses max(conservative byte fence,known/planned tokens); bytes never token admission.
3. **Safe budget pauses lacked an explicit top-level explanation in one path.**
   Provider token/input/money/hold failures now retain their host pause reason.
   Existing monotonic operator increase/reason/ownership/checkpoint/journal and
   revision refresh are reused. CLI standard/complex token profile changes grant
   no dollars. Previously saved60000 remains60000, and existing ledger caps/
   rows/holds are never silently reset. No ledger/schema/dependency migration.

Official policy, capacities, expiry and source links are recorded in
contracts/gemini_provider.json and backend/PROVIDER_ACCOUNTING.md. Runtime guide
and normative agent contracts agree. Count policy revalidation required before
2027-01-01; outside verified policy retain reservation.

## Controlled before/after reproduction

Actual pre-correction adapter with MockTransport and full structured schema:
explicit legacy $.15 case blocked before generation with $.093852750 held count;
explicit $.50/60000 tokens passed two decisions then TOKEN_BUDGET at45800 consumed,
with three uncertain counts and $.328202250 total exposure. The $.15 allocation
was explicit legacy reproduction, not the current new-case default.

Corrected same $.50 reproduction: eight consecutive decisions,183215 simulated
consumed tokens, $.186563250 simulated generation charges, zero count exposure
and zero uncertain requests. These figures demonstrate accounting with simulated
receipts, **not actual billed cost reductions**. Original and corrected request/
ledger histories are preserved in before-cost-reproduction/before-reproduction/
after-reproduction JSON; reproducible corrected script provided.

Default sizing: eight × accepted actual B09/MCP complete-request plan max46721
=373768, rounded upward to50000 →400000. Complex doubles it to800000. New growing
contexts reach larger per-request counts, so this is not a promise of eight
arbitrarily large decisions; actual six-step category tests validate the chosen
practical default, and remaining token and dollar admission always apply.

## Real runtime, simulated model acceptance

Six cases cover waterlogging, road verified/candidate pipe plus drainage links,
waste dated pickup/schedule history, generation503 and structured-output repair.
Every case makes six legitimate decisions through complete Gemini-style request →
MockTransport count → generation → strict B10-3/Selection/B09 nested schema → real
MCP/tool execution → real B09 evaluation → LangGraph → actual FalkorDBSaver → next
request. All16 schemas preserved, eight prior assessment versions, dated conflicts
and competing hypotheses, graph revision changes, longer history, actual older
road incident and pickup records. Test-only selector reacts to actual retrieved
facts; production routing is unchanged and no genuine model quality is claimed.

Simulated prompt receipts ~27000–61000 each, output512/thinking1536 each; every
case exceeds60000 cumulative but remains below400000 and pauses MISSING_EVIDENCE,
never falsely resolved/verified. Candidate pipe target stays road; verified target
can be pipe. Per-case exact counts/charges/requests/checkpoint/domain execution
IDs live in B10OR2-multistep-*.json; compact comparison in multistep-summary.json.
Two additional cases use two real interpreters for token and dollar pause,
explicit corresponding increase, source revision change/mandatory refresh, same
thread resume, counter and ledger continuity, and no duplicated native writes.
Original unknown generation holds remain; new count requests all settled zero.

New unit tests cover repeated free counting, rejection400/401/403/429/500/503,
timeout, malformed payload, unknown/expired/version policy, generation failure,
process reopen, realistic sequential usage, exact input-cap boundaries, provider
bounds and saved settings. Twenty-two new unit plus eight integration cases; no old
test removed. Two existing unit files have explicitly compatible billing/bound
assertion updates; every other accepted test file remains byte-identical.

## Verification

Stage1:98PASS4.37s; later focused final16PASS.60s and parity1PASS.18s.
Stage2:8PASS108.57s; targeted final water1PASS11.46s, context3PASS33.87s,
stricter road incident assertion1PASS13.46s. Batches overlap; never sum them.
One sandbox-denied Redis setup attempt1ERROR1.12s was rerun with local runtime
access and passed; no application failure or data/validation weakening.
Both specification validators PASS. Final complete regression: **770PASS/0FAIL/0SKIP** in1206.63s,488unit/282real integration;30new cases,740retained. One final full run with --durations=25 and --run-persistence. Guard exit0, zero external requests,2intentional blocked probes,0unexpected attempts. Original container restart/recreation and Browser checks PASS. Slowest25 tests in B10OR2-durations.txt; full raw log and guard are retained.
Two existing SentencePiece SWIG deprecation warnings are expected and retained.
Exact commands/raw outputs: B10OR2-COMMANDS.md and adjacent prefixed artifacts.

## Remaining limitations and review boundary

B10 remains PARTIAL: genuinely authorized three-category Gemini investigation,
contradiction/topology comparison and prompt B10-3 live quality gates remain OPEN.
Historical provider503/429 failures are not erased by these simulations. No live
provider calls were authorized or made; ordinary whole-suite interlock blocks
external HTTP/DNS in inherited Python processes. Offline Gemma3 remains a proxy,
not exact Gemini3.8; published policy/pricing can expire, historical/external
billing is unknown, project allocation is not a Google account billing hard cap.
Existing SDK multi-query recovery limits/canonical activation and DEC-004 later
phase findings remain. All42 retained city drainage links CANDIDATE; historical
repair/inspection gaps preserved. Frozen55 legacy numeric defects remain audit
witnesses; accepted B04 canonical conversion unchanged. No B11 work.

Human review should inspect endpoint-specific zero settlements vs unknown holds,
finite default sizing and receipt provenance, exact input boundaries, actual MCP/
B09/Saver flows, same-thread pause/resume, retained data and independent money.
Only separately authorized genuine B10 live gates may follow acceptance; B11
requires separate authorization after B10 acceptance. STOP at this correction.


### Final-verification timeout edge case

While the first full attempt was running, review identified an old outer-deadline
summary that inferred retained reservation/uncertain generation from any HTTP
call, including a zero-settled count-only timeout. Ledger data already remained
correct. Interrupted gracefully after148PASS/0FAIL/0SKIP,688.36s; exit2 deliberate
KeyboardInterrupt, preserved raw log and zero-live guard. No completed full run
was discarded solely for a harness change. Corrected summary now derives retained
holds from exact count/generation attempt metadata and says NOT_GENERATED for
count-only cancellation. Added known/unknown-policy outer-deadline cases and
reran original generation recovery tests:14PASS4.57s; actual MCP/Saver case1PASS11.17s and both specification validators PASS. Restarted final
acceptance only after those focused checks and retained-source preflight passed.


## Final retention and review evidence

All post-lifecycle checks PASS: B01 persistence; B04 city858/1246 revision2104;
B05/B08/B09 sources and101 accepted trace observations; B09R original v1/v2;
B10 source revision103/80nodes/47edges/content/audit/writer state and all6
SDK threads/12 executions. Original accounting witnesses row-identical,5120
durable token exposure preserved. Fresh rolling proofs saved under R2 prefix
before accepted bytes restored. Registryv3/migrations0001/0002, frozen75-package
lock and all prior evidence unchanged. Warning-aware raw-log adapter reuses the
original B09 data/history assertions without rewriting logs or old verifiers.

Exact scope/security audit and actual source patch/inventory: B10OR2-source-audit.json,
B10OR2-changes.patch, B10OR2-FILES.md. Private credentials/runtime/ledgers/caches
excluded; actual private values and secret patterns scanned without printing.
No leaked MCP child processes. Local accepted baseline af42149; no remote push.

All ten B10-O-R2 technical completion criteria are satisfied by the recorded
zero-provider unit and actual-runtime tests, subject to human review. This
does not satisfy B10 genuine live acceptance. STOP; no B11 implementation.

Evidence-only export attempts also encountered a wrong event-sort column and a summary glob matching itself; corrected after inspecting their actual data shapes. The exact repro/export reruns passed, with no application/test changes. These and the sandbox setup error are recorded in B10OR2-failed-attempts.json and B10OR2-COMMANDS.md; they do not change the final770/0/0 result.
