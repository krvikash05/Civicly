# B12-R2 — technically PASS, human review pending

Only commit/replay failure classification corrected. All18 requirements, B12/B12-R planning/remediation/source/feedback behavior retained; no B13 or live calls.

Root cause: PlanningService.create committed then raised PlanningBlocked PLAN_READBACK, and feedback classified every PlanningBlocked as draft_committed NO. Adjacent saved-replay read/receipt Pydantic failures could likewise be classified as invalid incoming drafts despite an existing committed plan. A commit call itself can also lose its acknowledgment after writing.

Correction: narrow PlanRecoveryRequired extends existing OutcomeUnknown. Commit attempt plus subsequent ACK verification is one guarded recovery boundary; saved-replay read/receipt verification has its own boundary. Exceptions become static sanitized recovery failures, never raw input/error bodies. Healthy receipt returned only after successful verification. Existing after_commit fault marker remains INJECTED_ACK_LOSS/RuntimeError compatible. Proven pre-write model/domain failures stay actionable/uncommitted for that attempt. Legacy PlanningBlocked PLAN_READBACK is conservatively UNKNOWN/operator recovery even outside the corrected service. No schema/storage/migration/policy/source changes.

Runtime retains graph/request/investigation/plan identity, expected version/hash and fixed failure stage on its existing RecoveryRequired. It propagates through unchanged wake quarantine without PLAN_DRAFT_REJECTED or safe receipt acknowledgment. No newly durable feedback is promised after failed graph/checkpoint execution; last durable checkpoint/decision and stored companion remain evidence. No automatic redraft/version/retry/replay/delete/reset/quarantine clearance.

## Real retained-plan proof
See B12R2-postcommit-recovery.json:
- graph `civicly_b10_test_d9704ec856cc4d2faf5d34cdb88f6a86`
- original request `PLANREQ-B10-e4489d1363618bfe26d9372bb16319d9`
- investigation `INV-B09-d8b67c785a6aa6bdcf800dbefe0a4f2f`
- plan `PLAN-B12-0cceb341285ac43da7c23f9295ca3ba2`, version1, hash `a59b83042912ceacc272b87529fc9b317d9a1b5cdef6fc30e34c20dbfb920924`
- thread `cae06eff299049a1816dd796609c444b`; last durable checkpoint `1f1cac37-5356-6a46-8003-a6fba1056adb`

ACK-only mismatch injected after a genuine commit; physical storage never corrupted. Runtime raises PLAN_OPERATOR_RECOVERY_REQUIRED with stage ACKNOWLEDGMENT_VERIFICATION. Read-only original Store.get independently verifies stored companion/hash/native binding; payload digest stays identical. Exactly1ResolutionPlan/version1 and1companion with original request/investigation; no duplicate/new version. Last durable state has original RECOMMEND decision (iteration2/wake0), no current plan receipt or false rejection feedback/observation. Quarantine remains set. External sanitized operator diagnostic says UNKNOWN/OPERATOR_RECOVERY and is explicitly not a persisted checkpoint acknowledgment. Plans remain unapproved/non-executable DRAFT.

No reconciliation wake or repair was attempted. Operator still must stop the old process/confirm ownership, inspect exact original request/decision, companion/native/hash and pending write state, and reconcile the last checkpoint under the established reviewed recovery procedure before any separately authorized resume. Do not change request/thread/version or clear quarantine merely to proceed. The separate healthy case demonstrates existing exact-request acknowledgment-loss replay unchanged, not an automatic repair of this quarantined case.

## Focused verification
18distinctPASS:16unit/2real;0unresolvedFAIL/0SKIP. Unit6new plus10directly affected old feedback/recovery branches; no remedial suite. Real new mismatch/quarantine case plus one unchanged healthy ack-loss/idempotent/version case. Initial real1PASS/1test regexFAIL20.21s retained; LangGraph appends task note, so corrected assertion only and reran solely new case in a new graph:1PASS12.21s. Unit16PASS0.98s. Both SPEC validatorsPASS once. No full B12/B12-R/770/313, remedial scenarios, live smoke, paid request or lifecycle operation. Scripted model/fault injection explicitly distinct from real SDK/FalkorDB/MCP/LangGraph/Saver.

All exact commands/raw logs/counts in B12R2-COMMANDS.md/B12R2-test-summary.json. Three inherited provider guards prove0external Gemini/countTokens/0unexpected attempts; accepted live ledger untouched. B12R2-FILES.md and actual narrow B12R2-changes.patch list code/tests/docs; B12R2-source-audit.json verifies older evidence/records source files and all accepted tests preserved, immutable migrations/source policies unchanged, secret scanPASS. Read-only retained-city counts unchanged; no write target was a retained city/accepted graph.

Human: inspect the recovery JSON for graph+original identities, count1/version1, UNKNOWN diagnostic, no false acknowledgment and quarantine retained. Reproduce only the single mismatch test from COMMANDS; it creates a new isolated case. No reset needed or authorized. Current-source integrity is read-only verified in the test, but the failed wake is still quarantined and no usable runtime receipt was emitted.

No unresolved implementation failure in this focused scope. Remaining limitation is intentional operator reconciliation for quarantined test wakes, and B10 full genuine live acceptance remains OPEN/PARTIAL. All B12-R action/source/safety limitations and future DEC-004 gates persist. Next proposed B13 authentication/approval/idempotent work-order boundary requires explicit authorization. STOP for human review.
