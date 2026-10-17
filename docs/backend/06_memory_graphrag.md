# Track 2 + 3: memory, checkpoints, GraphRAG, organizational brain

## Distinguish four persistence layers
1. **Checkpointed working state**: LangGraph thread per `investigation_id`, `FalkorDBSaver` managed namespace, interruptions for evidence/approval, resumes on new event and after restart. The `langchain-falkordb[langgraph]` checkpointer MUST pass an actual process-restart read test. Do not write directly into its internal graph schema.
2. **Episodic graph memory**: case story (incident -> evidence -> decision -> intervention -> outcome), chronological event and previous failed attempts. Query by asset/cluster, temporal validity and cause code.
3. **Semantic civic knowledge**: asset dependencies, known verified findings, past outcomes and similarity index. Invalidation/versioning when edges or conclusions superseded. Similar cases are suggestions, not proof.
4. **Procedural/org knowledge**: department responsibilities, work procedures, escalation rules, historic ticket decisions with document versions and source excerpts. GraphRAG-derived and linked to canonical Department/KnowledgeProcedure entities.

## GraphRAG SDK integration
Use official FalkorDB GraphRAG SDK (`graphrag-sdk`, tested Python version) for **municipal documentary knowledge**, e.g. 15-30 synthetic source documents: waste pickup SOP, blockage safety SOP, rainfall response policy, road excavation sign-off, pipeline leak protocol, department roster, historical tickets, resolution meeting notes. Import Markdown initially and PDF as compatible. Documentation describes text/PDF ingestion, schema-guided extraction, hybrid vector/fulltext/Cypher/relationship retrieval and citations.

**Isolation decision**: GraphRAG SDK may create its own labels/indexes and ontology. Set graph name `civicly_docs`, maintain its SDK-managed data separately from `civicly_knowledge`, link back via canonical `Document.external_id`, `content_hash`, `document_version`, and extracted `Evidence`/`KnowledgeProcedure` refs; avoid accidental collision of SDK-managed labels with hand-written canonical schema. The agent's retrieval runs through a domain tool that returns `source_document_id`, `source_version`, `quote_excerpt`, `passage_location`, `confidence_label`, `retrieved_at` (not a fabricated source).

### Ingestion contract
Source manifest: `document_id`, `title`, `source_kind`, `synthetic:bool`, `owner_department_id`, `effective_from`, `version`, `file_path`, `sha256`, `status`. Verify authenticity/provenance, dedupe by hash, only active version used for operational procedure. Incremental reingestion supersedes old version, but audit history intact. Extracted responsibilities are candidate statements until reviewed/confirmed; **verified responsibility from canonical graph takes precedence**. Fail with explicit `SOURCE_UNAVAILABLE` instead of inventing a procedure.

### Question flow
Supervisor -> `get_organizational_procedures` (Civicly MCP) -> document GraphRAG retrieval -> verify citation against actual document/excerpt -> join canonical `MAINTAINED_BY`, `GOVERNED_BY`, plan task department -> include procedural constraints in planner. Frontend can open original Markdown/PDF and show excerpt + version + page/section source. Do not treat natural language as executable instruction.

## Multi-agent coordination
Roles share canonical investigation/evidence IDs and checkpointed state, never simply pass a chat transcript. Each handoff has `from_role`, `to_role`, `case_id`, `graph_revision`, `evidence_ids`, `requested_output`, `handoff_event_id` and status. Worker serializes writes per investigation; parallel read-only queries allowed in bounded amount. Validate role output against contract before advancing supervisor.

## Concurrent access and memory scope
Hackathon-appropriate single demo municipality; all graph queries scope `municipality_id='demo-city'`, validated by services. Four fake operators with roles; no claim of tenant isolation against malicious administrators. Tests: concurrent reads; two work-order updates with stale revisions (only one accepted), duplicate event handling, simultaneous agent resume prevented by case lease. If true multi-user segregation is advertised later, implement cross-tenant isolation, do not pretend scope filter alone is sufficient.

## Correction protocol
When new inspection contradicts H1: append assessment H1-A2, link contradiction evidence, update current pointer/status with revision; persist prior H1-A1 and its decision justification; update CaseMemory to mark outdated finding, not erase it. New case retrieval sees history plus correction and reliability. On process restart checkpoint resumes without inventing missed history.
