# B11 — PASS, human review pending

Scope: Organizational Memory and FalkorDB GraphRAG only, primarily R09/R13/R14,
all18 requirements binding. Human explicitly authorized deferring B10 genuine
Gemini acceptance to final integration; it remains OPEN/PARTIAL. No B12+, frontend,
ZIP or remote push. Audited B10-O-R2 baseline770tests committed locally9f7ec1d,
preserving af42149 and all accepted evidence. This is milestone technical evidence,
not a claim that all organizational/model/product capabilities are complete.

## Implemented paths and actual behavior

`backend/app/memory/{models,sdk,storage,service,runtime,__main__}.py` implements
closed authorized sources/citations, actual SDK parse/ingest/index/retrieve, versioned
canonical references, staged reconciliation/revocation and trusted local setup.
Existing two organizational MCP read handlers and retrieve_case_memory now supply
source-backed procedures and corrected case history via existing broker/traces.
`app.agents.{mcp,server}` supports host-only memory capability and document cache
invalidation; original agent decisions/checkpoints/spending remain unchanged.
Actual CLI setup populated canonical `civicly_knowledge` and isolated `civicly_docs`.
No municipal city import, operations or automatic verified assertion promotion.

## SDK compatibility and dependencies

Official `graphrag-sdk[markdown,pdf]1.4.0`, pypdf6.21.1, markdown-it-py4.2.0,
FalkorDB Python1.8.0/server6.0.2. Verified actual published wheel/API, not copied
examples. Native SDK creates its own `<docs>__ontology` graph as well as document
index. Original fulltext procedure calls rejected by6.0.2 and opened SDK circuit
breaker. Narrow injected connection translates exactly two fixed legacy statements
to documented DDL; adapted **real SDK** Markdown+PDF ingest/finalize/vector retrieval
PASS. Original failure retained, no server/version replacement or SDK-source patch.

Public SDK GraphRAG.ingest/loaders/FixedSizeChunking/extraction strategy/stores/
LocalRetrieval run in production adapter. Offline lexical hash64 vectors and
lossless PROPOSED source extraction are explicit deterministic baseline strategies,
not genuine LLM extraction/learned semantic accuracy. NoLLM refuses invocation;
no generated Cypher/default multi-path completion or paid fallback. Actual retrieval
queries execute GRAPH.RO_QUERY. Main pipeline does not need LLM/fuzzy finalize;
chunk/lexical/mention graph and indices are real. Minimal spike separately exercised
SDK finalize. SDK dependencies require GLiNER/PyTorch etc; **no pretrained weights**
loaded/downloaded. Lock75→121packages; all75 prior locked versions unchanged,
100 installed distributions, frozen/offline sync and dependency checkPASS.

Official references used: [SDK](https://docs.falkordb.com/genai-tools/graphrag-sdk),
[strategies](https://docs.falkordb.com/graphrag/strategies),
[fulltext DDL](https://docs.falkordb.com/cypher/indexing/fulltext-index).
Compatibility is established by recorded local tests, not documentation promises.

## Source/version/ownership/citation contracts

Frozen18MD manifest and original sources unchanged. New normalized B11 manifest
maps exact department names to existing canonical DEPT-DRAIN/ROAD/WATER/SAN/COORD.
Synthetic curator review metadata is explicitly demo-authored, not government
approval. The19th source D001-PDF@1 is a visually inspected, labeled PDF derivative
of D001@1, retaining original path/hash and derived_from; real SDK PDF parser used.

Registryv3/0001/0002 unchanged. Compatible additive0003 establishes operational
companion indexes/unique/mandatory constraints and checksummed readiness ledger.
Existing strict Document properties carry `ORG:<document_id>:<version>`, source
URI/content hash/SDK pointer. Closed companion metadata holds canonical owner,
version/effective validity/supersession/review/authority/SDK chunk hashes. No SDK
labels or vector indexes collide with canonical graph. Actual post-lifecycle
counts: **19 canonical documents /19 SDK documents /19 indexed chunks /19 PROPOSED
source statements /0 SDK chunks in canonical graph**; SDK indices OPERATIONAL.

Citations carry source_document_id/source_version/canonical_document_id/owner ID,
URI/content checksum/quote excerpt/chunk location+hash/effective date/actual retrieval
time/review label/derived reference; strict schema rejects unsupported VERIFIED
claims or trusted-as-instructions. Reviewed synthetic source != established causal
truth. Only authorized manifest paths/hashes; traversal/symlinks/evaluator sources,
obvious prompt directives, malformed/missing/checksum-mismatched files denied.

## Examples and cross-graph recovery

D001@1 returns actual indexed excerpt: “Before recommending drain cleaning, verify
upstream inlet and downstream segment…” with exact original checksum and chunk ID.
D001-PDF@1 returns the same sourced procedure with derivative identity. See
B11-md-pdf-proof.json for actual graph/citation output; B11-canonical-runtime-proof.json
and canonical-setup.json/replay.json verify deployed targets. Repeated setup:
**19/19 replayed**, no duplicate Document/version/chunk identities.

Single-writer host lease60s/deadline30s, parsed text<=102400characters before writes.
STAGED → actual SDK parse/index → verified chunk/vector hashes → INDEXED → one
existing fenced canonical Document+READY companion transaction → READY. Cross-graph
transaction is not assumed. Only READY references are queryable. Tests interrupt
after SDK and after canonical registration, then retry safely with same identities.
A partial SDK-internal ingestion fails closed for explicit repair, never fictitious
success. Version2 appends and supersedes without erasing version1; historical
cutoff returns v1. Revocation is operator/reason-bound with prior metadata retained
atomically; current revoked/superseded source cannot fall back silently. Missing,
unreviewed, disputed, corrupt and insufficient data remain typed absence/gaps.

## MCP, agent and memory continuity

Actual initialize/tools-list/tools-call through separated official/Civicly brokers,
unchanged16-tool investigator catalog and common envelope/trace storage. New optional
citation fields are compatible closed extensions; absent capability stays UNAVAILABLE.
Runtime document reader is separate, exact-key RO credential; arbitrary keys/writes
are denied. No document path/graph/admin argument exposed to model.

Actual scripted READ→PAUSE→same-thread Saver resume, fresh interpreter retrieval,
source citations in B10 context and durable MCP traces PASS. A strengthened test
uses three distinct civic/reference/SDK graphs: revocation takes effect with civic
revision unchanged and no cached result reuse. Original B10 working state/native
journals and independent token/dollar controls remain. Case memory returns8actual
B09 assessment revisions with previous links and Evidence context; B05 historical
case paths are semantic suggestions, never fabricated verified outcomes.

## Tests and observed failures

- Focused source/SDK: initial23unitPASS; real SDK5PASS; stronger combined34PASS.
- Targeted final regression: **308PASS/0FAIL/0SKIP**,305.13s,226unit/82real integration.
- Final B11-only ingestion/source/MCP suite: **40PASS/0FAIL/0SKIP**,56.82s,25unit/15real.
- Strengthened three-graph actual MCP cache/Saver/fresh-process case:1PASS14.96s.
- Actual container restart+recreation/Browser test:1PASS15.22s.
- Distinct exercised cases across these overlapping final batches: **313**
  (227unit/86real integration); do not add overlapping totals. Both spec validators
  PASS, including new B11 static validation. Static checks are not runtime proof.

Full770regression **NOT RUN**, per authorization: compatible isolated0003, immutable
old registry/migrations/pins/tests, optional read handlers; targeted coverage of
affected schema/MCP/context/accounting and real brokers/Saver sufficed. No unresolved
cross-cutting regression required a full run. Slowest25 tests retained. Vendor
Pydantic class-config and two prior SentencePiece SWIG warnings retained, not skips.

Failures retained: SDK procedure incompatibility; unsupported uv index command/
stalled temporary pip install/cache permission; legacy verifier rolling-snapshot
selection; new fixture timeout15 vs existing10; two in-flight schema-transition
mismatches; actual case-memory missing Evidence context. Last corrected using
existing projector/merge, exact casePASS. No old test weakened/removed. PDF rendering
font configuration fixed locally; an unavailable optional renderer was bypassed
with configured bundled Poppler. Exact attempts/commands/logs in B11-COMMANDS.md.

## Persistence, retention, security and costs

Restart/recreation retained DB/Browser volumes; fresh process retrieved exact B11
source/version/chunk hashes and same public SDK checkpoint thread. Dynamic ACLs
reprovisioned with unchanged private credential/exact keys; no data reset. Original
B01 probe, B04city858nodes/1246edges revision2104/**42 CANDIDATE drainage links**,
B05/B08/B09 sources and101accepted trace observations, B09R v1/v2 corrections, B10
revision103/80nodes/47edges and all6original threads/12executions preserved. Original
ledger witnesses row-identical5120token exposure. Migration0001/0002 and all prior
source/test/evidence files preserved except explicitly listed application/docs/
contracts. Fresh rolling B07R proof saved separately before accepted bytes restored.

**External Gemini/countTokens requests:0. Cost:0 provider calls; no actual billed
savings claimed.** Whole targeted regression and inherited-child interlock exit0,
2intentional blocked probes,0unexpected attempts. All B11 HTTP/model selections
are offline/scripted; actual graph/MCP/Saver behavior is genuine. Final private-value/
secret/process audit, exact changed inventory and binary-inclusive review patch
are B11-source-audit.json /B11-FILES.md /B11-changes.patch. No credentials, runtime
profiles/ledgers, caches, Git internals or review ZIP included.

## Remaining gates and human verification

Offline lexical/source extraction is a baseline, not genuine semantic/model-quality
acceptance. Internal SDK partial-write repair is operator-reviewed, not automatic;
unknown/conflicting source text cannot establish verified procedures or civic facts.
Demo municipality scope is not enterprise tenant isolation. Current revocation is
security-authoritative even for historical lookup; older withdrawn metadata remains
in audit. Source corpus remains synthetic and limited; existing historical gaps/
DEC-004 future-phase findings remain. B10 genuine three-category/contradiction/
topology/B10-3 live gates stay OPEN/PARTIAL, explicitly deferred to final integration.

Human: run targeted commands in B11-COMMANDS.md and `make test-spec`; inspect
civicly_docs vs civicly_knowledge in Browser, D001/PDF source checksums/citations,
replay19/19, revocation and restart proofs. B11 technical PASS awaits review.
Proposed next only after approval: B12 typed plan drafts, source-backed owner/
procedure resolver, task DAG and monitoring criteria; no approval/execution work
or frontend yet. **STOP after B11.**

Final source-admission/excerpt refinement: version>1 requires explicit supersession of latest registered version;26source unit+1real version testPASS4.40s. Exact-ID excerpts use verified indexed SDK source chunks, avoiding semantic top-k starvation; affected real MD/PDF/version/MCP cases retested. No old test/source behavior weakened. Distinct final cases312(227unit/85real), overlapping batches not summed. Earlier lifecycle anchor preserved separately.

Canonical procedure identity: existing KnowledgeProcedure nodes use ORGPROC:<document_id>:<version>, exact document_ref to the versioned Document, normative string version and status PROPOSED. MCP procedure_id references that actual node and integer response version comes from validated source metadata. Source review never automatically verifies a procedure. New ingestion creates Doc+procedure+companion atomically; trusted replay additively backfills missing proposed procedures after source/chunk verification. No B12 planning/resolver/approval permission. See DEC-048 and final procedure tests.

DEC-048 completed: real KnowledgeProcedure ORGPROC IDs with exact Document references, normative string versions and PROPOSED status; integer MCP projection validated. Final5real source/version/recovery/MCP casesPASS25.10s. Canonical replay additively backfills19proposed procedures, preserving all Document IDs/hashes/chunks. Existing0001/0002/0003 unchanged; no planning/approval/operations. This final source behavior supersedes earlier B11 document-only procedure projections. Unique312cases unchanged.

Final procedure-state persistence verified: repeat only B01 lifecycle1PASS15.25s after DEC-048, earlier proof preserved under B11-earlier-*; fresh interpreter read exact final19PROPOSED procedure/document bindings, source/version/chunk hashes and same checkpoint thread. All original B01–B10/101traces/ledger witnesses rechecked unchanged. No additional full regression.

Source date normalization is explicit: original date-only effective_from values are retained in the frozen manifest and interpreted as UTC start-of-day validity for this synthetic demonstration. This is a policy-validity boundary, not an invented observation or review time. Canonical created/retrieved timestamps remain actual UTC.

Final UTC boundary verification: supersession compares canonical parsed instants, including optional fractional seconds, rather than string order. Exact real test rejects whole-second rollback from .1Z and accepts .2Z, retaining original and new procedure/document versions.1PASS, no earlier test or data changed. Final distinct coverage313(227unit/86integration), all final casesPASS; earlier overlapping batch counts remain historical.
