# B11 organizational and multi-layer memory

B11 only. All18 requirements remain binding. The human explicitly deferred B10
genuine Gemini acceptance to final integration; it remains OPEN/PARTIAL. No B12+,
operational approval/dispatch/monitoring/API/frontend or paid model calls.

## Actual SDK and graph architecture

Pinned `graphrag-sdk[pdf,markdown]==1.4.0`, official Python client1.8.0 and server
6.0.2. The accepted direct dependency pins stay fixed; the SDK brings required
transitives including GLiNER/PyTorch/scipy/hnswlib. No pretrained model weights or
large-model inference. `app.memory.sdk.Connection` adapts only two fixed legacy
full-text creation procedure statements to documented DDL. Original unadapted
smoke failure and actual adapted MD/PDF vector retrieval are recorded. Public SDK
GraphRAG.ingest, MarkdownLoader/PdfLoader, FixedSizeChunking, extraction strategy,
GraphStore/VectorStore and built-in LocalRetrieval run, never mocked SDK clients.

SDK ontology labels/indices live in `civicly_docs` and its SDK-mandatory
`civicly_docs__ontology`. Canonical `civicly_knowledge` contains existing strict
Document nodes with immutable version-bound IDs `ORG:D001:1`, source URI/hash and
SDK pointer. Compatible additive0003 creates companion metadata/index/constraints
and waits OPERATIONAL. Registryv3 and0001/0002 byte-identical. Companion metadata
holds version/department/effective bounds/review/trust/chunks/checksums; public
registry fields are not silently renamed/relaxed. No SDK internal label is written
into canonical graph. Separate disposable B11 SDK and canonical targets in tests.

The ordinary offline path hashes lexical tokens into64-dimensional vectors and
indexes lossless SourceStatement nodes as PROPOSED. This is a deterministic
baseline with real graph retrieval, **not learned semantic quality or genuine
Gemini extraction/reasoning proof**. No unrestricted generated Cypher. NoLLM fails
if invoked; no paid fallback. Native SDK multi-path Cypher/completion is excluded
from investigator runtime. Chunk-vector ingestion needs no global fuzzy merge;
SDK chunk indexes are created and verified, while no LLM-based finalize is run
for the main offline pipeline (minimal smoke separately exercised finalize).

## Source contracts and ownership

Frozen `data/documents/manifest.json`/18MD originals preserved. New normalized
`data/documents/b11/manifest.json` maps the five exact department names to
DEPT-DRAIN/ROAD/WATER/SAN/COORD. Synthetic B11 curator review is an explicit demo
metadata registration, not an assertion of official municipal endorsement.
Canonical owner Department must exist. Source kind/authority remains SYNTHETIC.
D001-PDF@1 is a clearly labeled one-page PDF derivative of original D001@1, with
original path/hash and derived_from. PDF parsed by actual SDK pypdf loader.

Closed Pydantic/JSON contracts reject unknown fields, bad owner/scope/dates/version,
path traversal, symlinks, non-document paths, hash mismatches and obvious instruction/
evaluator markers. Only manifest-authorized files under data/documents are ingested;
no scenario/evaluator roots. Original byte hashes and parser-derived text/chunk
hashes are separate. Source text never grants tool permissions; citations carry
`trusted_as_instructions=false`, `assertion_status=PROPOSED`, exact source/version/
owner/hash/URI/chunk location, effective date and actual retrieval timestamp.
Source-reviewed synthetic text does not establish verified civic policy or causes.

## Consistency and recovery

A single host ingest lease per canonical/SDK graph (60s lease,30s deadline)
rejects competing writers; <=128×800 parsed characters is checked before SDK writes.
Controlled ingestion validates source → journal STAGED → actual SDK
load/chunk/extract/index → verify exact chunks and vector presence → INDEXED → one
existing fenced repository commit creates Document+READY companion → journal READY.
Only READY matching source/SDK records can be retrieved. No cross-graph transaction
claim. Retry after complete SDK write verifies loaded-text/chunk/vector integrity
and reuses stable IDs; retry after canonical acknowledgment loss reads the committed
reference. Tests inject both boundaries. Original chunks/versions remain; new
version appends, explicit supersedes must reference earlier same-owner version.
Highest effective version wins; revoked/superseded current sources do not silently
fall back to older policy. Historical cutoff still retrieves prior effective source.
Revocation requires operator/reason and atomically retains previous metadata in
history_json plus repository audit; no evidence or version deletion.

Incomplete SDK-internal ingestion is quarantined as SDK_PARTIAL_REQUIRES_REPAIR;
operator must inspect source/text/chunks/embedding status and use a reviewed SDK
repair on that incomplete version before retry. No blind deletion/rebuild or
invented success. SDK internal atomicity is not claimed. Canonical migration0003 retries
are additive/checksummed; failed constraints require explicit repair/retry, never
reset volumes. Reconciliation journal acknowledgment can be replayed; the atomic
READY companion, not the journal's last presentation phase, gates authoritative use.

## Runtime boundary and memory layers

Working memory: original LangGraph/FalkorDBSaver and native journals unchanged.
Episodic: retrieve_case_memory reads immutable B09 assessment chronology/corrections,
with actual Evidence nodes, version links and provenance. Semantic: reuse B05
case/path projection; related histories are suggestions, not causal proof or new
verified outcomes. Procedural: two existing MCP tools get_organizational_procedures
and get_source_document_excerpt return bounded source citations. No new tool or
write privilege. Missing evidence, conflicting/disputed source, revoked/stale/
missing file or insufficient indexed results return typed absence/limitations.

Private0600 `.runtime/b11-active.json` grants a separate reader GRAPH.RO_QUERY on
exact document and canonical-reference keys. Existing official source/checkpoint/
trace credentials stay separate and unchanged. Authorized investigator source IDs
are explicit host config; another source has no memory capability, retaining
UNAVAILABLE handlers. Optional host memory_path supports isolated actual servers
in tests; callers cannot select graph/credential/path via tool arguments. Runtime
SDK queries use RO_QUERY; graph administration/write and arbitrary keys denied.
Retrieval caps:100 versions/20 candidate sources/12 SDK candidates/5 citations/
800chars per excerpt/128chunks/1MB source. Canonical memory revision rechecked
before acknowledgment. Organizational tool reads bypass civic-source-only cache
so document revocation never hides behind an unrelated civic revision. B10 context
interning/budgets remain unchanged, bounded tool calls limit payload growth.

## Reproduce

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.memory setup --output docs/evidence/B11-canonical-setup.json
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_memory_sources.py backend/tests/integration/test_memory_graphrag.py backend/tests/integration/test_memory_mcp.py backend/tests/integration/test_memory_case_history.py -q --durations=25
make test-spec
```

Setup is a trusted local operator command, not an MCP tool. It registers only
organizational owners/documents, never imports/promotes the city. Repeat verifies
identical source/chunks plus required vector/index state before replay receipts. Existing private config must
match exact canonical/docs targets; it is not silently replaced. After container
recreation, dynamic ACLs require exact-key reprovision (setup idempotent or verifier);
data/indices/checkpoints persist independently. Actual new test profiles and retained
records are checked by scripts/verify_b11_persistence.py; no credentials in proof.

Read docs/evidence/B11-RESULTS.md and B11-COMMANDS.md for actual results/failed attempts,
retained-data checks, provider interlock and exact review scope. A configurable key
is never live permission. Human review required before any next milestone.

Version>1 requires explicit supersedes of latest registered version. Exact-ID source reads cite verified SDK document chunks. B11-R corrects applicability search: global SDK top12 runs, then bounded verified eligible SDK chunk fallback prevents unrelated documents crowding out qualified sources. Fallback is explicitly reported and means source applicability, not learned semantic ranking. Up to20 eligible sources×128chunks are checked; only5citations×800characters returned, with truncation when more verified eligible chunks exist.

Canonical procedure identity: existing KnowledgeProcedure nodes use ORGPROC:<document_id>:<version>, exact document_ref to the versioned Document, normative string version and status PROPOSED. MCP procedure_id references that actual node and integer response version comes from validated source metadata. Source review never automatically verifies a procedure. New ingestion creates Doc+procedure+companion atomically; trusted replay additively backfills missing proposed procedures after source/chunk verification. No B12 planning/resolver/approval permission. See DEC-048 and final procedure tests.

Source date normalization is explicit: original date-only effective_from values are retained in the frozen manifest and interpreted as UTC start-of-day validity for this synthetic demonstration. This is a policy-validity boundary, not an invented observation or review time. Canonical created/retrieved timestamps remain actual UTC.

## B11-R corrective guarantees and remaining limits

Replay, complete-SDK retry, new canonical registration and retrieval share actual
index/vector checks: Chunk.embedding VECTOR OPERATIONAL/dimension64/cosine,
Chunk.text FULLTEXT, exact bounded chunk identities and finite64 vectors matching
the deterministic embedder within float32 tolerance. Missing/invalid state raises
SDK_PARTIAL_REQUIRES_REPAIR, including exact-document lookup; no successful replay,
automatic reset/rebuild or repair. These checks do not prove internal ANN membership,
exhaustive graph integrity or cross-graph atomic consistency.

Case memory selects latest applicable assessment revisions by assessed_at/id DESC
before requested budget+1 lookahead (maximum101), then presents the selected
revisions in chronological assessed_at/id ASC order. Temporal node and relationship
visibility is applied before the cap. Truncation reports older omitted history;
lookahead does not provide an exact omitted count. An OMITTED_PREDECESSOR gap keeps
the previous assessment ID as historical reference, never as returned evidence.
The existing envelope/outcome_summary contract is unchanged. Mutable hypothesis
visibility still gates historical cutoffs; no reconstruction of past mutable state.

Focused reproduction (ordinary provider interlock covers inherited children):
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11r-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_review.py -q --durations=10
CIVICLY_MEMORY_TEST_EVIDENCE_PREFIX=B11R CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-b11r-mcp-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_memory_graphrag.py::test_versions_supersession_revocation_and_missing_source backend/tests/integration/test_memory_mcp.py::test_real_sdk_domain_mcp_agent_checkpoint_and_fresh_process -q --durations=10
make test-spec
```
These are real SDK/FalkorDB/MCP tests; the agent uses a deterministic scripted model.
B10 genuine Gemini acceptance remains OPEN/PARTIAL. No B12 or lifecycle changes.
