# B10-O-R corrective verification — PASS, human review pending

Scope: B10-O-R only. Accepted B10-O baseline committed locally as c16346a after
credential/runtime exclusions were verified. Baseline evidence confirms691 pass,
zero fail/skip/external Gemini. No push, ZIP, B11, graph migration, city import,
MCP contract weakening or live Gemini/countTokens request in this task.

## Corrections and evidence

1. **Byte/token unit mismatch:** byte arithmetic was incorrectly used for model-token
   preflight, retries and repair. Complete steering JSON now gets a SHA-pinned
   official Gemma3 SentencePiece proxy count, explicit25%+256 uncertainty allowance,
   plus4096 output tokens. Bytes remain separate metadata/financial heuristics.
   Google's checked tokenizer mapping does not establish exact Gemini3.8 support;
   the estimate is never called provider-confirmed. LIVE requires an authorized,
   financially reserved full-request countTokens call. No such call occurred here.
2. **Cumulative exposure:** each generation attempt gets independent dollar/token
   reservations. Validated actual usage replaces its token allowance; unknown
   usage retains allowance. Durable per-thread floors and SQLite reopen prevent
   stale checkpoint reset. Billing and token certainty are separate. Invalid
   totals fail closed. One valid but unexpectedly large simulated receipt plus
   prior consumption now fits checkpoint storage:1100000 recorded exactly and
   paused, without further actions. Storage ceiling2M is not an operational budget
   increase; default60000/max150000 token Budget is unchanged.
3. **Spending allocation:** new ledgers8/.50/concurrency1, explicit complex ceiling1.50,
   all configurable. Existing6/.15 witness remains row identical. A private
   SQLite backup was additively migrated, then explicitly configured with audit;
   charges/reservations/case allocations remain. No existing project cap was
   silently increased. Approximately$4 user credit remains outside the application
   allocation; this is not a Google billing hard cutoff.
4. **Exact hold recovery:** old project-wide hold lacked an adequate resolution path.
   Add exact request holds and immutable accounting/configuration audits; inspect
   reserved/charged/usage/pricing/caps, bind explicit operator/reason/evidence and
   stored usage hash, reprice under exact tariff, check caps and resolve only that
   settled-overage hold. Unknown billing and unattributable legacy holds cannot be
   cleared. Original requests/charges/legacy history remain. Fresh process recovery
   and reopen verified; new durable witness retains5120 known+held token exposure.
5. **Provider/runtime compatibility:** reject malformed envelope/usage/count fields,
   bound retries/repair/counting, correct stale retry failure categorization,
   preserve exact prompt/Selection/tool schemas. Explicit monotonic Budget recovery
   retains counters and same-thread journals; invalid Budget input and exhausted
   wake denial no longer quarantine an otherwise valid paused thread. Updated
   wake allowance can be applied before checking the old wake ceiling. Existing
   graph revision/evidence refresh and B09 authority checks remain mandatory.

## Three-category actual context proof

`B10OR-token-benchmark.json` records targeted real registry/B09/MCP contexts:
eight persisted assessment versions, four source observations, two competing
hypotheses, all16 approved discovered schemas, full historical classification/
provenance/path material. Road includes distinct incident identities and verified
pipe dependency reads; waste includes actual three-status pickup execution history
and collection context. No critical context field is removed by B10-O-R.

| Issue | Complete request bytes | Local proxy tokens | Planned input+output tokens |
|---|---:|---:|---:|
| WATERLOGGING | 66234 | 26499 | 37476 |
| ROAD_DAMAGE | 73621 | 29389 | 41089 |
| WASTE_ACCUMULATION | 81990 | 33895 | 46721 |

These proxy estimates include full prompt and structured-output constraints, unlike
the earlier context-only byte benchmark. Before/after projection byte/token plans
are both retained in JSON. UUID/source hashes can slightly change counts between
runs. Each exact estimate-1 rejected before generation, exact/+1 passed. Mock
responses reported130 simulated tokens; **no genuine Gemini token usage or cost
savings is claimed**. Explicit mocked countTokens boundary tests separately prove
count/schema/financial accounting behavior.

The full mock HTTP path uses actual Gemini adapter → graph-dependent test selector
→ actual official/domain MCP discovery/call → B09 proposals/assessments/inspection
requests → real LangGraph/FalkorDBSaver → real SQLite usage reconciliation.
Reviewed contradiction + unreviewed support stays CONTESTED, with source IDs and
context-only classifications retained; actual next inspection changes accordingly.
Verified/candidate/disconnected topology alters the selected target without causal
promotion. Actual two-process checkpoint/ledger reopen, token/cost pauses, explicit
increases, invalid output repair,429/503/timeout/quota recovery are tested. These
are simulated model selections, not a claim of genuine model reasoning quality.

## Staged tests and failed attempts

- Stage1:29 pass/1 fail (correct denial, stale error category); fixed and58 pass.
- Stage2 first:10 pass/1 fail (authored support code outside policy).
- Stage2 second:59 pass/2 fail (selector failed to treat CONTESTED contradiction
  as relevant; pickup arguments violated strict existing schema). Fixture selector
  and arguments corrected; no B09 rule/schema or previous assertion weakened.
- Final targeted batch:76 pass in103.59s; extra immutable-audit/fresh-operator-process
  ledger batch10 pass in0.46s; final storage/wake-boundary/model/ledger batch29 pass
  in13.11s. Overlapping totals must not be added.
- Final complete regression: **740 PASS / 0 FAIL / 0 SKIP**,1249.98s:466 unit/274 real integration. All691 baseline cases unchanged plus49 new cases. Both specification validators PASS; whole-suite guard exit0, zero external Gemini,2 intentional blocked probes,0 unexpected attempts. Docker restart/recreation and Browser persistence PASS.
- Nonfatal SentencePiece SWIG deprecation warnings observed; no tests skipped to
  hide them. Live provider acceptance NOT RUN, because not authorized.

Exact commands, raw failed/final outputs and source patch/inventory are adjacent
B10OR-* artifacts; `backend/AGENTS_RUNTIME.md` contains setup, accounting recovery
and the separately authorized final-stage live acceptance procedure.

## Retained evidence and outstanding gates

Preflight verified unchanged retained B10 source revision103/80nodes/47edges,
content/audit/writer fingerprints, six SDK threads and12 executions. Post-lifecycle
checks PASS: retained city858nodes/1246edges revision2104, B01 probe, B05/B08/B09
sources,101 accepted trace observations and immutable B09R v1/v2 history unchanged.
All6 B10 SDK threads/12 executions and exact original source/audit/writer state
match. Four fresh rolling proofs were saved before exact accepted bytes restored. Original B10-O financial witness is read-only;
new probe records known/unknown exposure and resolved hold without erasure.

B10 genuine live three-category/contradiction/topology/B10-3 quality gates remain
**OPEN**. Provider availability/quota, historical/external billing uncertainty,
proxy-token model mismatch, count RPC billing uncertainty, vendor multi-query Saver
recovery and final canonical activation remain explicit limits. All42 city drainage
links remain CANDIDATE; imported history gaps and DEC-004 future-milestone findings
remain. Frozen55 legacy numeric defects are retained; accepted B04 converted data
remains separate and intact. All18 requirements are mandatory, not completed by
this correction. STOP for human B10-O-R review; any genuine live suite needs new
explicit authorization. B11 GraphRAG/memory is proposed only after that review/gate,
not started.


A supplemental legacy verification command failed its summary regex because the
raw successful pytest line contains ',2 warnings'. Data assertions reached before
that parser passed. B10OR-retention-parser-compatibility.json reproduces the exact
format mismatch. New scripts/verify_b10or_retained.py validates the untouched raw
summary/lifecycle/guard and reruns every unchanged original B09 data assertion; PASS.
This is evidence-tool compatibility, not a failed740-case suite or weakened test.
The final private financial witness matches before/after lifecycle exactly; original
B10-O witness rows remain unchanged. Source/security audit and actual patch/inventory
are B10OR-source-audit.json, B10OR-changes.patch and B10OR-FILES.md.

Final B10-O-R scope/security audit PASS:61 prior test files unchanged, all prior evidence byte-identical, actual private credential values/patterns absent, no leaked MCP children. No push or ZIP. Exact source inventory/patch is against c16346a; subsequent human review and separately authorized B10 live acceptance remain required.
