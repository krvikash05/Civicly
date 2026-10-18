# B20-R-UTILITY-R before-edit record

Only this corrective pass is authorized. All R01–R18 remain binding; directly protects R04/R05/R09/R10/R11/R17/R18 through bounded sourced topology, complete task dependency scope and safe authority. No agent/provider capability claim.

Smallest correction: existing bounded verified-only topology discovers every utility repair touching any road-task target; reject more than one linked task with stable sanitized `UTILITY_MULTIPLE_REPAIR_PREDECESSORS`. Exactly one must be the precise UTILITY_VERIFICATION/depends_on predecessor. No linked repair retains existing no-utility behavior. No schema expansion, plan hash/default, migration, storage or recovery change. Existing operations.validate invokes the same remediation policy before new authority, so fresh topology is rechecked.

Touched paths planned: backend/app/services/planning/utility.py; existing focused utility units and real PRIMARY fixture; backend/UTILITY.md; contracts/resolution_planning.json semantics; six append-only trackers; new B20R-UTILITY-R evidence/patch/inventory. Existing test assertions retained. PRIMARY writes only new R-prefixed evidence; unchanged NEGATIVE not rerun. Prior accepted evidence files and retained DB graphs remain intact.

Risks: selecting one of several tasks or a non-linked substitute; multiple road targets hiding omitted predecessors; duplicate references; truncated/candidate topology; fresh topology changes after approval. Fail closed, no auto-repair/retry/clearance. No multi-predecessor workaround; operator must revise scope through a separately reviewed plan rather than bypass a necessary repair.

Exact planned commands (root):
1. CIVICLY_TEST_REQUEST_LOG=/tmp/B20R-UTILITY-R-repro-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_utility_intervention.py -k complete_road_binding -q (before fix; preserve review failure).
2. CIVICLY_TEST_REQUEST_LOG=/tmp/B20R-UTILITY-R-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_utility_intervention.py -q
3. FALKORDB_SOCKET_TIMEOUT_SECONDS=10 CIVICLY_TEST_REQUEST_LOG=/tmp/B20R-UTILITY-R-real-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/integration/test_utility_intervention_runtime.py::test_s04_primary_utility_intervention_and_uncertainty -q
4. CIVICLY_TEST_NO_LIVE=1 CIVICLY_REQUEST_AUDIT_FILE=/tmp/B20R-UTILITY-R-spec-provider.jsonl PYTHONPATH=backend/test_guards:backend make test-spec

Human verifies schema-valid ambiguous two-pipe plan rejected by real API before any plan/order exists, exact one-predecessor plan still completes accepted isolation→repair→verification→road/recovery journey, no old records altered, zero provider calls. No negative/broad/lifecycle/live suite. STOP for review; full B20 and B10 genuine acceptance remain open.
