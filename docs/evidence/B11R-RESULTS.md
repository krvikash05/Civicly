# B11-R — technically PASS; human review pending

Only the three authorized memory corrections, R09/R13/R14 plus R07/R15 boundaries;
all18 requirements retained. No B12/frontend/live Gemini/dependency/migration changes.
B11 acceptance remains human-reviewed. B10 genuine Gemini acceptance OPEN/PARTIAL.

## Reproduced causes and corrections

1. Global SDK LocalRetrieval top12 ran before source eligibility. The initial real
   corpus regression failed because eligible Coordination D018 was omitted; the
   same real ranking contained neither Water Utilities chunk. A read-only deployed
   comparison of the saved original Memory class and corrected class produced
   **0 citations before, D005/D017 after**. SDK1.4.0 has no source-filter option in
   LocalRetrieval/VectorStore.search_chunks. Retain actual SDK search; add bounded
   fallback over actual verified eligible SDK chunks. Metadata cannot become a
   citation. Eligibility, review/version/revocation, canonical revision and chunk
   checks still apply. ELIGIBLE_SOURCE_FALLBACK reports applicability rather than
   semantic ranking. Caps20sources/128chunks per source/5citations/800chars unchanged.
2. Registered replay compared source/chunks and bypassed existing SDK ingest's
   vector-presence check. The missing-vector test reproduced successful replay.
   Shared SDK.validate_indexing now checks replay, complete-SDK retry, new ingest
   and retrieval: OPERATIONAL Chunk.embedding VECTOR64/cosine, text FULLTEXT,
   exact bounded chunk IDs/count and finite64 vectors matching deterministic
   embedder within float32 tolerance. Healthy replay passes; missing vectors,
   wrong64vector and missingvectorindex explicitly raise SDK_PARTIAL_REQUIRES_REPAIR.
   Exact-document retrieval also fails closed. No automatic repair or retained
   graph reset. Observable metadata/vectors are verified, not internal ANN membership.
3. Ascending assessment query+cap selected the oldest revision for max_results1,
   reproduced in an8revision history. Query now applies temporal node/relationship
   visibility, selects newest assessed_at/id DESC with budget+1 lookahead<=101,
   then sorts selected output chronologically ASC. A104revision investigation
   retains the newest100 and newest1. Earlier cutoff excludes later-created
   hypothesis/history. Truncation reports older omitted history, exact total unknown.
   OMITTED_PREDECESSOR gaps preserve IDs as historical references, not returned evidence.
   Existing envelope/outcome_summary schema unchanged; behavior documented in
   contracts/organizational_memory.json, backend/MEMORY.md and DEC-049.

## Focused verification and observed failures

**7 distinct real integration cases pass;0 unresolved failures/0 skips.**
No separate unit batch: actual graph scenarios directly exercise new validation
branches, chronology and schema validation without mocked database/SDK results.

- Pre-correction reproduction:3failed/2deselected,16.44s, intentionally retained.
- First corrected batch:4PASS/1FAIL,28.07s. The new long-history fixture hit B09's
  unchanged per-hypothesis guard. No product change: use8+96 revisions across two
  hypotheses in one investigation, each within the guard.
- Rerun only affected history case:1PASS16.68s.
- Existing supersession/revocation test plus extended actual MCP/Saver test:
  2PASS16.36s. Real initialize/tools-list/tools-call, Water D005/D017 citations,
  strict result schemas/provenance, revocation, same-thread resume, fresh interpreter
  retrieval and existing ACL denials. Model is scripted; SDK/FalkorDB/MCP/Saver real.
- Both specification validators PASS once via final `make test-spec`.
- Additional read-only retained deployed old/new Water comparison PASS; not counted
  as another pytest case. Initial diagnostic command used nonexistent app.db import;
  corrected to app.graph.connection, with no database action on the failed attempt.

Counts overlap: three reproduction failures recur in the corrected cases. Final
unique passing set is first corrected4 + affected history1 + compatibility2 =7.
No770-case or313-case rerun: narrow memory/query corrections, all10seeded
source department/action pairs covered by one real19-source corpus test, healthy
and three corrupt index states isolated, small/overcap/temporal history verified,
and directly affected version/broker/checkpoint path selected. No cross-cutting
change requires broader regression. No container lifecycle operation because no
migration/persistence/lifecycle behavior changed. Vendor deprecations retained.

## Retention, zero calls and limitations

All prior B11 and accepted evidence files checked byte-identical. Source/schema
registry/migrations0001–0003, dependencies, city, original checkpoints and ledger
implementation unchanged; runtime writes only newly owned test graphs/ACL profiles.
Deployed comparison is read-only. Corruption tests retain explicitly damaged
isolated graph names for review, never repair/delete accepted data or volumes.
Test proof output prefix supports B11R while preserving default existing test usage.

All four pytest guard proofs:0 external Gemini/countTokens,0 blocked/unexpected
attempts, inherited by Python child processes. Read-only comparison ran with the
same inherited provider interlock. No provider charges from this execution.
Offline lexical embeddings/lossless source extraction and scripted agent behavior
are not genuine Gemini acceptance or learned semantic quality.

Remaining: human review; B10 genuine gates OPEN/PARTIAL; source/version/citation
caps, manual SDK partial repair, no ANN internal-membership/cross-graph atomicity
proof. Historical mutable hypothesis visibility is preserved; no reconstruction
of past mutable graph state. Future approval/event/API/evaluation gates remain.

## Review and human verification

Exact commands: B11R-COMMANDS.md. Exact paths: B11R-FILES.md.
Actual source diff: B11R-changes.patch against the pre-B11-R working-tree snapshot,
not the older GitHEAD which predates B11. Original B11 patch is unchanged.

From repository root run the two passing commands in B11R-COMMANDS.md and
`make test-spec`. Expect5real review cases plus2compatibility cases passing,
D005/D017 citations and zero calls in the `/tmp/*-provider.json` guard reports.
If anything differs, share the raw pytest output and sanitized guard JSON; never
share `.env` or runtime credential profiles. No lifecycle or setup/reset command.

STOP after B11-R. Proposed next task B12 typed draft plan/DAG/owner/procedure and
monitoring criteria, only after human approval; no operational execution yet.
