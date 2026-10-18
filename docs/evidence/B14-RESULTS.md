# B14 — technically passing, human review pending

B13 accepted. B14 ONLY: authenticated simulated execution, actual inspection/result
evidence, independent follow-up and recurrence with retained memory.41distinct
focused casesPASS:30unit/11real,0unresolvedFAIL/0SKIP. Both final specification
validatorsPASS. Historical failed attempts preserved in B14-COMMANDS.md/raw logs;
no mocked database success.12pytest/child interlocks show0external Gemini/countTokens
and0unexpected attempts. B10 full genuine Gemini acceptance OPEN/PARTIAL.

## Implemented behavior and actual proof

- Exact authenticated assignee/department, current plan/version/hash/full scope,
  Approval, CAS, ownership/procedure, typed causal/safety and dependency guards.
  START→IN_PROGRESS; task APPROVED→QUEUED→IN_PROGRESS; plan→IN_EXECUTION.
  BLOCK/resume explicit; failed attempt→WorkOrder BLOCKED/task FAILED with retained
  INCONCLUSIVE/INTERVENTION_FAILED outcome and report. No automatic retry.
- B09 authorize/plan/models/Receipt/Journal reused, native inspection/report/findings
  and immutable assessments checked by original Reader.evidence. Separate real
  ANALYST session supplies review identity. Exact targets/procedure, closed codes,
  method/units/source/time. Caller Review/desired resolution not accepted.
- COMPLETE requires dated reviewed ACTION_COMPLETED report per target. All tasks
  complete→MONITORING, ACTION_COMPLETED outcome. Missing exposure→MONITORING;
  unknown/missing/contradictory evidence never verifies; observed persistence→
  PROBLEM_PERSISTS. No completed-order inference of resolved civic condition.
- B14-1 explicit synthetic rules: comparable rain→waterlogging absent; relevant
  wear→pavement damage absent; matching scheduled/actual pickups >=1 followed by
  >=24 actually elapsed hours without reaccumulation.24hours is synthetic policy,
  not municipal standard. Reported comparability/wear is attributed qualitative
  observation, no external weather/physical threshold invented. All targets/time
  windows checked; independent rule decides, operator supplies observations.
- Verified outcome includes policy/window/intervention/approval and report/finding
  hashes. Native result MITIGATION_VERIFIED / assessment_status RESOLUTION_VERIFIED,
  never ROOT_CAUSE_ADDRESSED. All current approved tasks/dependencies/gates and
  follow-ups checked; latest addressed contradiction blocks case closure. Native
  plan/investigation COMPLETED; incidents ENDED/time; cluster CONTROLLED.
- New qualifying adverse follow-up after verified result uses B08 normalization/
  matching/pattern and AFTER_RECORDED_END classification. Distinct incident linked
  original cluster, cluster/investigation REOPENED, original completed plan,
  approval/repair/outcome/history preserved. No recurrence cause invented. Existing
  B05 case retrieval exports earlier order and verified outcome, not a new fake
  memory handler. Safe bounded gap wording replaces stale B05 unimplemented claim.
- Existing0005 companion/compiler extended without new migration. Narrow planned
  journal source checks allow atomic B09/B08 batches while preserving B03 checks;
  request/native changes/audit/event representation coupled in existing fence.
  Same-meaning latest assessments validated before original immutable gate IDs;
  changed meanings require explicit revised PlanDraft→submit→fresh approval.
  Evidence/result recording proof is labeled accurately, not a rejection.
- Exact command/report/completion replay creates no duplicate effects. Equivalent
  evaluation window/evidence deduplicates. Actual post-commit ACK loss reports
  OpsRecovery UNKNOWN identities; original completion/outcome retained, explicit
  exact-request replay recovers acknowledgment. No plan/version duplication or
  automatic redraft/delete/quarantine clearance. Existing pending-write recovery
  protocol unchanged, no new delivery infrastructure.

## Retained evidence

| Proof file | Actual observation |
|---|---|
| B14-outcome-WATERLOGGING.json | Completion→no opportunity→verified→new recurrence, original outcome in existing memory |
| B14-outcome-ROAD_DAMAGE.json | Actual supported subgrade plan/authorized work→wear/pavement follow-up verifies |
| B14-outcome-WASTE_ACCUMULATION.json | Actual pickup recovery→scheduled/actual+25hour authored window verifies |
| B14-failure.json | Failure report/order/task/outcome retained, restart of failed task denied |
| B14-contradiction.json | DRAIN_CLEAR revises original assessment, original history retained; completion allowed but closure INCONCLUSIVE |
| B14-recovery-denials.json | Wrong roles/dept/stale approval/CAS/state/evidence refused; legitimate reassess/resume; ACK loss→one completion then persistence |
| B14-dependency.json | Road→Water order blocked until predecessor complete, then assigned/executed while plan IN_EXECUTION; immutable draft unchanged |
| B14-regression-B13-*.json | Accepted approval/order/CAS, stale sources/supersession/rejection, conditional gate and actual leased Saver checkpoint compatibility |
| B14-audit.json | Original registry/migrations/data/MCP/agents/ledger/quarantine and prior evidence retained; actual versions/zero provider |

B14-file-audit.json/B14-FILES.md/B14-changes.patch give exact working-tree changes.
B13-FILES.md has only the explicitly requested annotated sentence correction; prior
test evidence not rewritten. B13 test output redirected by evidence-only plugin.

## Test selection and limits

18new pure policy cases +12directly affected authentication/state/gate unit cases;
7new real B14 cases +4accepted approval/CAS/source/gate/checkpoint cases. Overlapping
reruns not extra cases. Actual FalkorDB/B09/B08/B11 SDK operations; checkpoint case
uses clearly scripted PAUSE model with real MCP/Saver/fresh process, not genuine
Gemini. No full770/313/B12/B13 suite, all-catalog scenario run, live smoke, lifecycle,
API, scheduler, worker, dispatch, new dependencies or source-data import. Existing
storage consistency retained; actual single-mutation/ACK-loss and fresh-process
regression suffice without container restart/recreation.12zero-provider proofs;
accepted paid ledger remains2historical requests/$0.00571350/$0held.

Demonstration policy is deliberately limited: explicit staged observations, binary
condition findings and report-level pickup totals, not hydraulic/structural models
or per-vehicle telemetry. Same department can collect follow-up, separate analyst
reviews; no claim of physically independent field organizations. Source procedures
remain synthetic/PROPOSED. Bounded history scans fail closed; no global absence or
verified causal explanation. No event delivery/wakeup guarantee newly implemented;
PENDING native event representations await B15. Earlier intentional quarantines
remain operator-managed and untouched. All18 requirements remain binding, no full
product/backend completion claim.

## Human verification (about two minutes)

1. Read B14-outcome-WATERLOGGING.json: note graph, binding, ACTION_COMPLETED,
   no_opportunity MONITORING, verified policy/evidence/window, recurrence/new incident
   and existing memory paths containing original work/order/outcome. Road/waste
   proofs show their separate conditions. B14-recovery-denials.json records UNKNOWN
   and retained original completion, then persistent follow-up.
2. In existing FalkorDB Browser choose graph from that file. Run bounded read:
   `MATCH (w:WorkOrder)-[r:RESULTED_IN]->(o:InterventionOutcome) RETURN w,r,o LIMIT 10`.
   Original order remains COMPLETED; old verified outcome and later recurrence
   coexist. Inspect ProblemCluster/Investigation REOPENED and old incident ENDED.
3. Optional repeat in a fresh isolated graph (no paid request):

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/b14-human-provider.jsonl backend/.venv/bin/python -m pytest 'backend/tests/integration/test_execution_runtime.py::test_actual_three_issue_completion_verification_and_water_recurrence[WATERLOGGING]' -q --tb=short
```

Expect1PASS; creates another isolated target, never resets accepted city. If local
socket fails, grant local test access/start existing Compose service without removing
volumes. Share sanitized B14 test output and provider proof, never .env/.runtime/
password/session. Unknown real writes require operator inspect original graph/
request/order/plan/approval/pending audit, stop old owner and reconcile through the
existing reviewed recovery procedure before any separately authorized resume;
never clear quarantine simply to retry.

Next proposed B15: durable outbox delivery/single-worker lease, idempotent event
consumers/resume triggers, retry/reconciliation and persisted SSE events. Not
implemented or authorized here. STOP for human B14 review.
