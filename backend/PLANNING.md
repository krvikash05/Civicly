# B12 typed resolution and coordination drafts

B12 advances R10 with R09/R11/R14/R15/R17 support; all18 requirements remain.
A persisted draft is not approved or executable. No B13 authentication/approval,
WorkOrder creation, dispatch, monitoring evaluation/worker, outbox/API/SSE/frontend.
B10 genuine three-category/contradiction/topology/end-to-end acceptance OPEN/PARTIAL;
no provider call authorized or used for B12.

## Contracts and ownership

`contracts/resolution_planning.json` exports closed Pydantic PlanDraft/TaskDraft/
Monitoring/PlanReceipt schemas from app.services.planning.models. Draft requires
investigation/issue, version/previous-plan identity, two distinct hypothesis+latest
immutable assessment references with addressed/alternative reasons, actual supporting/
contradicting Evidence references, typed tasks/targets/departments/priority/prerequisites/
DAG/evidence/assessment refs/source citations/expected outcomes/risks/uncertainty.
The accepted B12 foundation admitted sourced INSPECTION only. B12-R extends it
with the three bounded remedial policies and typed guards documented below; no
other action families are admitted. Priority uses existing severity
LOW/MODERATE/HIGH/CRITICAL; no invented MEDIUM, numeric confidence/cost/duration.

Monitoring describes criteria, not evaluation: water comparable follow-up rainfall+
waterlogging observations; road follow-up pavement+wear exposure; waste meaningful
scheduled/actual pickup+reaccumulation window. Observation opportunity and verification
criteria mandatory, absent opportunity UNRESOLVED, completion_implies_resolution false.
No invented fixed numeric opportunity window from missing historical evidence.

Resolver reads actual source-graph canonical MAINTAINED_BY relationships per target,
requires exactly one active VERIFIED edge with dated attributed verified Evidence,
and validates a visible Department. Candidate/unknown/conflicting owners block.
The claimed department must match verified responsibility; document authorship cannot
assign work. B11's source owner is preserved separately in citation/proof, not promoted
to accountable department. Applicable reviewed/current B11 citations are retrieved and
compared to exact source/version/chunk/hash/URI/owner/status, action code and actual
KnowledgeProcedure. PROPOSED procedures remain PROPOSED; revoked/superseded/invalid
sources block. Applicability currently uses manifest action_types and selected source,
not learned proof that a procedure is authoritative for every physical target.

All targets must be visible and linked by investigated incidents' AFFECTS or one of
the investigated hypotheses' CONCERNS. Assessments must be latest within their
hypothesis at validation cutoff; evidence must belong to the chosen assessments.
No hidden scenario data or arbitrary graph/query selector enters the service.

## Storage, versions and recovery

Registryv3/migrations0001–0003 unchanged. Apply compatible additive0004 explicitly
with `PlanMigration(db,authorized_graph).apply()` before using PlanningService.
No automatic migration from model/tool arguments; checksummed READY ledger and
OPERATIONAL index/constraints required. Supported canonical/source/test graph guard
remains original repository authorization. New CivicPlanDraft companion stores full
closed payload/hash/proof/request ID and source graph pointers. Native ResolutionPlan
status DRAFT, ActionTask status PROPOSED, PRODUCED_PLAN/HAS_TASK/DEPENDS_ON/ASSIGNED_TO/
TARGETS are actual graph records, in one existing fenced/audited repository statement.

B11 references are in a separate canonical graph. No cross-graph GOV_BY edge or
mirrored authority fabricated: companion stores canonical graph+Document/procedureID,
source version/hash/excerpt/chunk binding. SDK labels remain isolated. No public
ontology/property rename or changed schema enum. New migration is additive/repeatable;
failed index/constraint requires reviewed repair/retry, never graph/volume deletion.

Version IDs bind investigation/version; tasks get version-owned stable IDs. Draft
hash SHA256 covers normalized validated content (task/basis and set-like reference
order canonicalized), simulation mode, evidence, assignment, citations and monitoring.
New version must point to current head and increment once; old versions retained.
Writer lease serializes source validation/idempotency/version check/full mutation.
Exact request+payload replay returns original receipt, changed payload conflicts.
Response loss after full commit is recoverable via same request; test injects that
boundary. Pending repository outcomes use existing explicit recovery, never blind
partial acknowledgment or B15 infrastructure. Cross-graph atomicity not claimed:
source-memory revision rechecked before commit; historical draft and replay receipt
are not future executability validation. B13 must revalidate source/assessment/
owner versions and bind any later approval to exact hash/scope/assignee.

`Store.get` verifies companion/hash/strict draft/receipt/native plan binding; source
DAG and assigned-task projections are exercised in real tests. It is not a general
background integrity auditor or a universal immutable-write sandbox. Trusted low-level
administrator/repository access remains outside the model tool boundary.

## Runtime and old checkpoints

Existing structured Selection schema/action names retained. Successor B12-1 prompt
adds RECOMMEND `{plan_draft:...}`; controlled_action_schemas.RECOMMEND supplies exact
closed input schema. Source text is untrusted; model cannot repair meaning/self-grant
approval. ResolutionPlanner calls the same PlanningService as trusted operator use.
Invalid drafts pause PLAN_CLARIFICATION_REQUIRED; no automatic action rewriting or
unbounded replanning. Accepted draft ID/version/hash go to workflow state/observations,
then human-review pause. Native Saver and decision/MCP traces/accounting unchanged.

Optional trusted injected PlanningService supports isolated integration. Normal
runtime uses host-authorized memory capability only; missing0004 or memory config
pauses, never automatic migration/data seeding/model-selected write transport.
Legacy RECOMMEND `{next_action,target_ids,basis_evidence_ids,limitations}` keeps its
original nonbinding validation. Old checkpoints default current_plan_id/version/hash
None. Once a draft receipt exists, decode verifies exact saved investigation/version/
hash. Historical B10/B11 prompts and recorded prompt hashes preserved.

## Reproduce without provider requests

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b12-check-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_planning.py backend/tests/integration/test_planning_runtime_store.py backend/tests/integration/test_planning_agent.py -q --durations=10
make test-spec
```
These are pure validation plus actual isolated FalkorDB/SDK/MCP/LangGraph/Saver tests;
model responses scripted. The inherited ordinary test guard blocks external
Gemini/countTokens, including Python child processes. See docs/evidence/B12-COMMANDS.md
for the exact focused batches actually executed and historical failed attempts.

For a quick no-write review, inspect `docs/evidence/B12-ROAD_DAMAGE-draft.json`:
receipt status/version/hash, native task ID map, cross-department dependency and
owner evidence; source citations/PROPOSED status; monitoring criteria. Read
B12-agent-fresh-process.json for native checkpoint and same draft/receipt binding.
No container restart required for payload-only additive graph storage: existing
volume durability protocol unchanged; actual fresh-process read/resume verified.
No claim B12 plans are approved or the backend complete. STOP for human review.


## B12-R remedial proposal policy
`policy.py` admits exactly three additional codes: DRAIN_BLOCKAGE_CLEARANCE (WATERLOGGING/BLOCKAGE, DrainInlet or DrainSegment, DEPT-DRAIN), SUBGRADE_REPAIR (ROAD_DAMAGE/SUBGRADE_FAILURE, RoadSegment, DEPT-ROAD), MISSED_PICKUP_RECOVERY (WASTE_ACCUMULATION/MISSED_PICKUP, WasteCollectionPoint, DEPT-SAN). INSPECTION remains available. Latest addressed B09 SUPPORTED or VERIFIED assessment and reviewed target-specific supporting report observations are required; contradiction/insufficient support blocks remediation. Current report/finding hashes must match the assessment. Procedure text is never physical evidence.

Task.remediation is optional only for historical/new inspection drafts. Remedial tasks require mode SUPPORTED_NOW or CONDITIONAL and exactly two typed conditions: CAUSAL_INSPECTION and SAFETY_REVIEW. MET requires bounded task evidence references; causal MET requires all normative confirming codes, safety MET requires DRAIN_CLEARANCE_SAFETY_REVIEWED, SUBGRADE_REPAIR_SAFETY_REVIEWED or PICKUP_RECOVERY_SAFETY_REVIEWED respectively. These are explicitly new synthetic demo observation codes, validated through existing B09 attributed, dated, reviewed report/journal/finding reads. Safety scope is source-defined (flow/confined-space/disposal; utility/excavation/traffic/infiltration; crew/route/waste handling/disposal). They are not real-world clearance certificates.

SUPPORTED_NOW requires both gates MET and no future task dependencies. CONDITIONAL has at least one UNMET gate. Unmet causal inspection must name an existing INSPECTION task in depends_on that covers each target. Unmet safety review stays an explicit future gate (no fake completion); free-text prerequisites cannot satisfy either. Outcomes/verification/risks/issue-specific monitoring stay mandatory. Draft-mode distinction confers no approval/execution permission, even when supported now. Every native ResolutionPlan remains DRAFT, ActionTask PROPOSED, SIMULATED/unapproved/non-executable. No operational writes.

### Sources and operator setup
The 18 frozen sources and B11 manifest remain unchanged. Separate data/documents/b12r/manifest.json registers only newly authored D019–D021 version1 MD demonstration policies. Author: Codex B12-R AI-assisted synthetic policy author. Source REVIEWED means automated author self-review for consistency of these demo guards only; not independent human review, government approval or recovered historical authority. reviewed_by, effective timestamp, owner, action applicability and SHA256 are explicit. All KnowledgeProcedure and citation assertions remain PROPOSED. The actual B11 SDK ingests/retrieves these through its unchanged reviewed-only source pipeline.

Optional trusted operator command (not executed on retained canonical graphs by B12-R):
```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.memory setup --manifest data/documents/b12r/manifest.json --output /tmp/civicly-b12r-source-setup.json
```
This explicitly registers the three sources using existing B11 SDK/bootstrap and retains previous versions/documents. It is not an agent tool. Tests ingest only isolated memory graphs; no automatic retained-data import, schema change or container restart.

### Feedback and recovery
Closed Feedback contains stable code/category/resolution, max8 safe task IDs and field paths, static <=240-character explanation and draft_committed NO/UNKNOWN. Pydantic input values/unknown property names/exception bodies are never copied. Workflow planning_feedback plus PLAN_DRAFT_REJECTED observation persist safe domain/schema rejections and known pre-write storage-capability failures. Action policy is also supplied in actual supervisor context; no second orchestration system or automatic replan.

DAG/schema/action/prerequisite corrections request DRAFT_CLARIFICATION; missing evidence/ownership/source capability requests MISSING_EVIDENCE_OR_CAPABILITY. Pre-write migration/storage readiness failure pauses PLAN_OPERATOR_RECOVERY_REQUIRED, distinct from clarification. Unknown failures, uncertain writes and wake ownership failures raise sanitized RecoveryRequired into the existing quarantine. Checkpoint failures remain outside planner acknowledgment and also quarantine; no claim that feedback was persisted after a lost lease or failed checkpoint. Operator must inspect the last durable checkpoint and reconcile native request IDs. A committed draft with acknowledgment loss is never labeled definitely rejected; native Store replay remains authoritative.

Normalization omits remediation only when absent, preserving accepted B12 hash representation (including previous_plan_id=None). New conditions/evidence order normalize deterministically; old versions remain readable. 0001–0004 and dependency locks are unchanged. No B13 authority, dispatch, executor or monitor.

## B12-R2 commit-boundary failure classification
Pre-write model/domain validation remains actionable and uncommitted for that attempt. Once Store.commit is attempted, any commit-response or subsequent acknowledgment verification failure is PlanRecoveryRequired (existing OutcomeUnknown subtype), never an ordinary draft rejection. Missing/mismatched readback and Pydantic/storage readback errors return no receipt. Saved-request replay read/receipt verification failures also require recovery. Intentional after-commit acknowledgment-loss injection preserves its historical RuntimeError marker and healthy exact-request replay behavior.

Recovery context retains only validated graph, exact request ID, investigation ID, plan ID, expected version/hash and a fixed stage; no raw exceptions/source/model text. Runtime propagates it on RecoveryRequired into the unchanged wake quarantine. Last durable checkpoint/decision and CivicPlanDraft request/payload provide reconciliation evidence; a failed node/checkpoint does not promise a new persisted feedback record. Legacy PlanningBlocked PLAN_READBACK is conservatively UNKNOWN/operator recovery. No response labels the plan safely usable before integrity/readback verification.

For operator review: stop the old process and verify ownership; inspect the original request/decision, companion payload/hash, native plan and repository pending-write state using existing read/recovery facilities. Resolve actual integrity/ownership/checkpoint uncertainty through the established reviewed procedure before considering any later explicit resume. Do not create a new version or change request ID as a repair. B12-R2 leaves its isolated fault graph's quarantine in place, with one original plan/version and no automatic replay, retry, deletion or reset. The separate healthy replay test uses its original exact request and existing supported path. See docs/evidence/B12R2-RESULTS.md. No B13 or live calls.

## B13 compatible native lifecycle
B13 operations are authenticated through the separate Operations gateway. Native plans may legitimately become PENDING_APPROVAL/APPROVED/REJECTED/SUPERSEDED; immutable B12 draft payload/receipt/hash are retained. Store.get requires a matching B13 hashed lifecycle and operation attestation for these states, and checks an existing attestation even if native state is improperly rolled back to DRAFT. Historical PlanReceipt remains DRAFT/unapproved; it is not a current authorization. Actual saved checkpoint decoding after approval verified under the existing ownership lease. New current-head versions invalidate old approval usability; assignees bind in exact B13 approval scope. See backend/OPERATIONS.md; no B14 execution or live call authorized.


## B20-R-UTILITY extension
Only the two closed synthetic utility actions and their typed persisted-evidence dependencies are added. See [UTILITY.md](UTILITY.md) for D022 authority, exact approval, isolation proof, component verification, road gating and unchanged UNKNOWN recovery. Old draft hashes and B14-2 outcome semantics remain intact.
