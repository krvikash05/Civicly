# B13 demo authentication, approvals and authorized orders

B13 implements service foundations only: no API routes, field execution/completion, B15 delivery/worker, frontend or live provider. All18 product requirements remain binding; B10 genuine full acceptance OPEN/PARTIAL.

## Accounts and authentication
The accepted city corpus has5synthetic accounts (analyst, approver, drain/road/waste leads), not4, and no admin or utility lead. Preserve every original record. Private auth adds OP-ADMIN and OP-WATER-LEAD, the latter required by the accepted B12 road→WaterPipe inspection DAG.7small identities cover4role classes; no enterprise identity or public signup.

|Identity|Role|Scope|
|---|---|---|
|OP-ANALYST|ANALYST|Authenticated draft and submit; read|
|OP-APPROVER|APPROVER|Exact-scope approve/reject and authorize order; read|
|OP-DRAIN-LEAD|DEPARTMENT_LEAD|Own assigned Drainage work only|
|OP-ROAD-LEAD|DEPARTMENT_LEAD|Own assigned Road work only|
|OP-WASTE-LEAD|DEPARTMENT_LEAD|Own assigned Sanitation work only|
|OP-WATER-LEAD|DEPARTMENT_LEAD|Own assigned Water Utilities work only|
|OP-ADMIN|ADMIN|Read and audited session revocation only; no approval/work bypass|

Auth.provision uses PBKDF2-HMAC-SHA256600000 with random16byte salts, constant-time password/MAC comparisons, random256bit session nonce plus HMAC signature,30minute server-side expiry, logout/admin revocation and enabled-account checks on every call. Fixed server-owned role/department map, no caller identity claims. Local private SQLite stores credential hashes/signing key/sessions/auth audit; owner-only DB and credentials files0600, runtime directory0700. Passwords/tokens never enter graph, trace or public proof. Future API transport must supply the authenticated token, never Actor/role fields; no API endpoints implemented. Internal B09/B12 services/repositories remain trusted host capabilities behind this gateway, not public caller authentication endpoints.

Verified references: [Python3.12 hashlib](https://docs.python.org/3.12/library/hashlib.html#hashlib.pbkdf2_hmac), [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html). No dependency changes or production-auth claim.

Trusted fresh setup:
```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.services.operations configure
```
Actual workspace already configured; command refuses to overwrite credentials/signing key/sessions. Initial6account local setup was extended additively for missing utility lead; old passwords/key/revocation audit retained. Credentials stay in ignored `.runtime/auth/`; do not share/archive that directory. Actual sanitized login/denial/logout proof: docs/evidence/B13-auth-runtime.json.

## Services and exact binding
Operations(planning,auth) requires explicit additive OperationsMigration0005 readiness. Only canonical graph, a validated disposable B13 graph, or trusted active B10 profile can dispatch operations; graph-name pattern alone never grants active B10 access. Graph scope checked at dispatch/read/replay. Inputs are closed Submit/Decide/Order/Update models in contracts/operations.json, scoped to demo-city. Authenticated draft gateway resolves ANALYST identity internally; agent cannot impersonate an approving human or call an approval MCP tool.

Binding covers plan ID/version/content SHA plus the full native task IDs/action types/targets/accountable departments/assignees. Canonicalized set ordering and scope hash. Submission creates Approval PENDING and plan PENDING_APPROVAL. Decision CAS binds exact pending Approval and current plan, actor/time/reason/proof; approve changes native plan/tasks to APPROVED. Rejection records reason/history and REJECTED state; it checks exact current immutable binding/native projection/CAS without requiring revoked sources to become valid first. Audit says binding-only rejection, never authority for work.

Approve/order/update recheck current plan head, latest investigated assessments, source report/finding hashes, applicable B11 version/revocation and proposed status, verified ownership, exact native task/DAG/target/department projection and current enabled assignee identity. Evidence and documentary guidance remain separate. B11 procedures stay PROPOSED. Memory revision checked around source validation; no cross-graph transaction claim.

New version requires separate submission/approval. Current-head check immediately makes old approval unusable; submitting a revision also transitions old native plan SUPERSEDED with audited lifecycle attestation. Old Approval decisions/reasons remain historical records, not current authority. No approval reuse or reassignment shortcut.

Conditional human approval never changes immutable UNMET causal/safety conditions. Any UNMET typed gate or dependency task not COMPLETED blocks creation and progression. No waivers or findings synthesized. Existing accepted road→water inspection DAG verified; water order remains blocked while road task is only APPROVED. Later evidence-based change to immutable gates requires a revised plan/hash/approval; B14 not implemented.

## Work orders, CAS and audit
Only APPROVER can create after valid exact approval; native WorkOrder starts AUTHORIZED/SIMULATED. One deterministic ID per plan/native task prevents duplicate orders even across request keys. Exact key+actor+payload replay returns persisted historical result; changed reuse conflicts. Another key for same unchanged approved task records an audit alias without another WORK_ORDER_CREATED event. Historical replay receipt is never current authorization; new writes revalidate current proof, status and assignment.

Department lead can read/update only own exact approved assignee binding. B13 allows AUTHORIZED→ASSIGNED/CANCELLED and ASSIGNED→CANCELLED through normative state machine and expected native hash. IN_PROGRESS/COMPLETED and field/outcome evidence remain B14. Concurrent stale updates cannot both commit. Updated timestamps cannot move backward. Completion never implies civic resolution.

Native Approval/WorkOrder/StatusEvent/DomainEvent and IMPLEMENTS/AUTHORIZED_BY/HAS_EVENT/EMITTED_EVENT links plus request/audit/lifecycle companion are coupled in one existing fenced, parameterized graph statement. Registry0001–0004 unchanged.0005 adds unique/index/mandatory constraints for CivicOperationState and READY checksum ledger; real constraints/indexes checked OPERATIONAL. DomainEvent envelope in immutable operation payload has required contract fields, actor and result; native event.payload_ref points to it. PENDING delivery remains pending; no claim of event publication, worker, exactly-once or cross-graph ACID.

Commit/readback uncertainty is OpsRecovery (existing OutcomeUnknown subtype), carrying bounded graph/request/entity/operation/plan/approval identities and UNKNOWN commitment. No false rejection/automatic retry/delete/reset. Existing repository pending-write recovery retained; direct human service has no agent wake lease to clear. A future wake wrapper must retain its existing quarantine. Same-request explicit acknowledgment-loss replay tested without duplicates; native order/event/audit and private auth session verified in fresh Python process. No container lifecycle needed: new records reuse existing persistence protocol, no new DB engine or worker.

## B12 compatibility
CivicPlanDraft payload, SHA and receipt bytes remain immutable. B12 Store.get accepts legitimate B13 native lifecycle only when hashed lifecycle companion and immutable operation attestation match exact native properties/plan/version/hash. A raw rollback to DRAFT cannot bypass that check when an attestation exists. Original B12 receipt remains historical DRAFT/unapproved/non-executable; read audited native lifecycle for current status. Exact saved current_plan_id/version/hash checkpoints remain valid after legitimate approval; unchanged actual Saver checkpoint decoded under existing wake ownership. No lease check weakened. B12-R2 real post-commit mismatch still quarantines/retains one original plan and no false acknowledgment.

## Reproduction/review
See docs/evidence/B13-COMMANDS.md for exact executed commands and historical failures, B13-RESULTS.md for real scoped IDs, B13-FILES.md/B13-changes.patch for changes. Minimal convenient human command:
```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b13-human-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_operations_runtime.py::test_actual_approval_order_scope_idempotency_and_competing_updates -q
```
Creates a new isolated graph, never resets accepted data. Expect exact approval→AUTHORIZED order, attributable audit/events, same-request and same-task duplicate prevention, wrong-role/scope/department denials, one competing update, fresh-process auth/order proof. Ordinary pytest and children block external Gemini/countTokens. Inspect B13-flow.json without running anything for no-write review. APIs/DTO transport projection remain B16; contract service schemas are not a claim API routes exist.

## B14 current implementation (supersedes the historical B13-only boundary)

B13 is human accepted. B14 adds explicit handlers, not automatic dispatch/delivery.
`Operations.execute` dispatches closed Progress/Inspect/Evaluate/Recur commands from
`execution_models.py` to `execution.py`. All18 requirements binding; genuine B10
full acceptance remains OPEN/PARTIAL. No new dependencies or graph migration.

Assigned authenticated departmental lead first assigns through B13 Update, then
STARTs. WorkOrder ASSIGNED→IN_PROGRESS, ActionTask APPROVED→QUEUED→IN_PROGRESS,
ResolutionPlan APPROVED→IN_EXECUTION. BLOCK retains reason; ordinary BLOCKED task
can explicitly resume. FAIL requires ACTION_FAILED report, retains WorkOrder BLOCKED,
ActionTask FAILED and INCONCLUSIVE/INTERVENTION_FAILED immutable outcome. No automatic
failed-task retry. COMPLETE requires reviewed attributable ACTION_COMPLETED report
for every target after work start; tasks/order become COMPLETED. All tasks complete
moves native plan/investigation/cluster to MONITORING. Historical B12 draft bytes,
SHA, receipt and checkpoint references do not change;0005 lifecycle/operation
attestations independently validate legitimate current states.

Every fresh action validates current exact plan head/version/hash/full task scope,
assignee/department, current Approval and CAS; ownership and source procedure remain
current. START/order retain causal and safety/dependency gates. Unchanged assessed
meaning may advance to a new assessment ID only with original reviewed support
retained and identical contradictions. Changed meaning rejects further execution:
explicitly draft version+1 with previous_plan_id, submit its full binding and obtain
fresh human approval. Approved content/gates never rewritten. Recording actual
inspection/terminal results can truthfully finish already-started work after
contradiction; that does not grant authority for new work or verified resolution.
Dependent order creation/assignment works while native plan IN_EXECUTION.

Inspect wraps actual B09 RequestInspection/TransitionInspection/ReportInspection/
Assess models. Reuses EvidenceService.authorize/plan, native B09 Receipt/Journal and
Reader.evidence/report provenance validation. Compiler couples COMMITTED B09 journal,
report/findings/inspection update, operation/audit and PENDING event in one existing
fenced mutation. Planned journal references validated narrowly in operations storage;
B03 persisted-source validation unchanged. B08 recurrence planner accepts an optional
strictly bound planned intake journal for the same atomic batch, with ordinary B08
calls unchanged. No second report or dedup algorithm. Request IDs bind inner/outer
commands; unknown fields/target/type/method/unit/time rejected. Reports must be
SYNTHETIC; inspector is resolved assignee. Pass a separate authenticated ANALYST
`reviewer_token` and bounded review_reason: supplied Review is rejected, identity is
server-derived. Review is synthetic demonstration review, not government authority.

Verification uses `verification.py` / contracts.operations verification B14-1:

| Issue | Qualifying follow-up |
|---|---|
| WATERLOGGING | Explicit comparable-rainfall observation, then binary FOLLOWUP_WATERLOGGING (0 absent/1 present) |
| ROAD_DAMAGE | Explicit WEAR_EXPOSURE, then binary FOLLOWUP_PAVEMENT damage (0 absent/1 present) |
| WASTE_ACCUMULATION | Scheduled/actual matching integral pickups >=1, followed by >=24 actually elapsed hours and binary WASTE_REACCUMULATION |

24hours is a synthetic demo observation minimum, not a real municipal standard.
Rain comparability/wear is explicit authored sourced observation, not derived weather
or fabricated numeric engineering threshold. Measurement units closed: boolean,
pickups, hours; exposure/completion codes are qualitative without values/units.
Completion < window start <= all observations <= window end <= controlled clock.
Final finding follows exposure/window; all targets covered. UNKNOWN/missing leaves
MONITORING; conflicting values INCONCLUSIVE; adverse observation PROBLEM_PERSISTS.
No policy value lets operator/model submit a resolution label. Independent follow-up
uses separate reviewed post-completion report/source; same department may collect
observations, while a different authenticated analyst reviews and deterministic
policy decides. No claim of physically independent municipal inspectors.

Verified outcome references work/plan/approval, policy version, full evidence hashes,
source/finding provenance and window. Native outcome MITIGATION_VERIFIED with
assessment_status RESOLUTION_VERIFIED; never implies verified root cause. Each task
needs its own follow-up; all tasks/dependencies/gates and latest addressed assessment
checked before case closure. Success completes plan/investigation, records incident
ENDED time and cluster CONTROLLED. Recur requires new adverse qualifying window after
previous verified outcome, a new B08 occurrence AFTER_RECORDED_END in original cluster,
then REOPENED cluster/investigation + new immutable outcome. Original completed plan,
approval/repair/outcomes/assessments remain; existing B05 case paths retrieve them.
No recurrence cause inferred.

Exact requests replay historical receipts. Equivalent evaluation evidence/window
also deduplicates outcomes. Source-record uniqueness/B09 report journal and native
state guards prevent duplicate report/completion effects. UNKNOWN commit/readback
propagates OpsRecovery with graph/request/work/plan/approval, never false rejection,
automatic redraft/retry/delete or quarantine reset. Explicit same-request ACK-loss
replay is tested; changed post-write state requires operator reconciliation under
existing repository pending-write protocol. No agent wake/quarantine is introduced
for these direct authenticated handlers. Native events remain PENDING for B15.

Focused reproduction and retained graph IDs: docs/evidence/B14-COMMANDS.md and
B14-RESULTS.md. Tests use real local FalkorDB6.0.2, actual B09/B08/B11 services;
provider guard blocks Gemini/countTokens in pytest and inherited children. No live
provider, lifecycle, full regression or scenario-catalog run is claimed.

## B14-R current corrections

Current verification B14-2 supersedes B14-1 for fresh evaluations. The explicitly
synthetic24hour waste minimum now measures from each target's latest supplied
ACTUAL_PICKUPS observed_at, not evaluation-window start. Every supplied window must
claim >=24hours and actually elapse at least its claimed duration after that pickup;
final condition follows the window. Equal repeated aggregate counts are not summed
or inferred as vehicle identities: conservatively latest actual timestamp restarts
observation. Differing pickup totals remain INCONCLUSIVE, missing/short/unknown
opportunity MONITORING. Other target/coverage/review/source/chronology/contradiction
rules unchanged. `verification_v1.py` preserves original B14-1 bytes for historical
interpretation; contracts.operations.historical_verification retains its meaning.
Existing outcomes and exact-request replay keep original policy/provenance. No
retroactive outcome rewrite or inference that historical B14-1 success satisfies
B14-2. New evaluation signatures use new version.

Recurrence reuses the original investigation, atomically adding a temporal sourced
INVESTIGATES→new incident link with all original links retained. Response/event gives
investigation_id and investigates_relationship_id. Existing finite3incident bound
is enforced before commit; exceeding it requires explicit operator redesign, no
silent truncation/successor or unrelated infrastructure.

On explicit same-thread resume, `agents.recurrence.refresh` validates the new link,
B08 journal/canonical hash/COMMITTED receipt/AFTER_RECORDED_END, cluster/issue/targets,
prior dated end and actual reviewed recurrence reports. It projects active episode
IDs/assets and source hashes through full InvestigationState validation and records
a host-generated RECURRENCE_SCOPE_REFRESH audit; original ended episode links and
old checkpoints stay. Existing plan/hypothesis references remain historical episode
context, not causal authority for the new incident. Mandatory fresh MCP READ barrier
remains. Invalid/ambiguous refresh uses existing recovery/quarantine; no automatic
wake, historical checkpoint rewrite or caller-injected incident list. See
backend/AGENTS_RUNTIME.md and docs/evidence/B14R-RESULTS.md for actual focused proof.


## B20-R-UTILITY extension
Only the two closed synthetic utility actions and their typed persisted-evidence dependencies are added. See [UTILITY.md](UTILITY.md) for D022 authority, exact approval, isolation proof, component verification, road gating and unchanged UNKNOWN recovery. Old draft hashes and B14-2 outcome semantics remain intact.
