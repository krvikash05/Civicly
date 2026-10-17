# Acceptance and agent evaluation protocol

## Three test layers
1. **Deterministic unit**: Pydantic schema/enum validation, dedup, graph policy, plan DAG, auth, idempotency, procedure precedence, recurrence thresholds, temporal validity, monitoring. Mock LLM permitted to test orchestration; label MOCK.
2. **Real integrations**: local FalkorDB server, actual Cypher query paths/migrations/checkpointer, actual official and custom MCP client/server calls, seeded GraphRAG ingest/retrieval with real source references, API/CLI persistence and restart. If LLM provider unavailable mark live agent tests SKIPPED not PASS.
3. **Behavior/e2e**: agent uses tool selection and graph to solve or correctly defer cases in `contracts/scenarios/catalog.json`. Evaluate selected next actions, evidence provenance, avoided false claims, alternative cause checks, approvals, changed decisions when graph/evidence modified, and robust retry/reopen.

## Mandatory scenario set
S01 shared downstream obstruction (water); S02 extreme rain/capacity instead of blockage; S03 recurring pothole with false pipe-leak proximity; S04 utility leak physically verified; S05 market waste missed pickups plus peak-capacity; S06 unauthorized dumping despite on-time pickups; S07 cross-category waste→drain→flood→road with validated chain; S08 deceptive adjacent but disconnected drainage edge; S09 repeated work completion but no recurrence verification; S10 contradicting inspection and rejected hypothesis; S11 failed repair followed by recurrence and memory use; S12 missed MCP/external weather source and fallback/abstention. All are in `contracts/scenarios/catalog.json` and `docs/demo/SCENARIOS.md`.

## Test assertions (per scenario)
- Exposed graph: no hidden truth or later inspection until event stage.
- Correct source/issue/asset links at ingestion; graph trace contains paths and valid effective dates.
- Decision: agent selects allowed MCP tools based on missing evidence, not fixed string match. Changing cause evidence must change assessment or verification request where warranted.
- Contradiction: revises append-only assessment, preserves original reasoning, no numeric confidence without calibration.
- Planning: justified task DAG/owner/procedure; approval required, exact version/hashes checked, simulated progress tracked with actor evidence.
- Monitoring: incomplete until condition-specific follow-up; recurrence reopens and retrieves earlier case.
- Provenance: each meaningful claim has source refs, no invented measurements, weather or completed work.

## Evaluation metrics (do not fabricate performance scores)
- `correct_next_action_rate` = correct expected action category for scenario state; admissible actions may be a set, not a single exact string.
- `evidence_citation_rate` = significant claims referencing valid existing evidence/source / total claims.
- `unsafe_action_count` = unauthorized simulated work orders + physical completion without report; target 0.
- `graph_dependency_sensitivity` = number of counterfactual topology changes appropriately altering path evidence/plan / total applicable variants.
- `memory_reuse_rate` = reuse of relevant prior outcome/total applicable recurrence scenarios.
- `mcp_real_call_coverage` = actual runtime MCP tool executions validated / exercised planned tools.
- `recovery_pass_rate` = restart, duplicate event, denied approval, source unavailable cases meeting policy.
- `time/token usage` measured from actual run, no target until baseline.

## Hidden ground truth and evaluator independence
`data/scenarios/hidden_truth.json` mounted ONLY in evaluator, never API, agent, MCP, GraphRAG, indexing or frontend. Scenario catalog has safe initial description and expected observable behavior, not exact hidden cause leak. Place delayed observations in `data/scenarios/event_reveals.json`, controlled by a scenario-event injector which releases only stage-appropriate evidence. Require tests that fail if agent process can open hidden_truth path.

## Graph dependency ablation
Real graph instance 1 baseline; clone into isolated graph instance/namespace 2, remove shared DRAINS_TO edge, replace positive drain inspection with negative, or change pickup execution history. Run with same prompts and config; compare evidence paths and recommended next step. Different response due merely to model randomness is not proof; record graph diff and exact tool outputs.

## Golden trace recording
Store `tests/golden/*.json` only after live run; include tool calls/results, chosen decision ID, source evidence, graph revision and simulator stage, omitting secrets. Golden tests validate invariant semantics, not brittle exact LLM wording. Present judges with a trustworthy side-by-side evidence change demo.

## Backend completion gate B-END
Required: 18 objectives mapped to passing tests; all 12 scenarios or documented failure without dishonest success claim; graph migration fresh boot; MCP actual transport; GraphRAG sourced PDF/MD; agent checkpoint survives restart; work-order RBAC; outbox recovery; eventual frontend DTO queries and SSE; Docker local setup and reset; complete `decision.md`, `flow.md`, `test_log.md` with exact commands. Backend complete is not declared without this evidence.
