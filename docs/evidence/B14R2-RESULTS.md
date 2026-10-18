# B14-R2 — technically passing, human review pending

The refresh subtracted active IDs from all retained graph IDs, so the second wake
misclassified the original ENDED incident as a new recurrence. It then attempted to
parse that old episode's original journal with recurrence semantics.

Correction: use persisted host RECURRENCE_SCOPE_REFRESH proof to identify previously
validated history, rechecking scoped link/journal hash, B08 receipt hash/classification/
relation, issue/cluster and end-before-adopted timing. Only proven history is excluded
from additions. Unknown ACTIVE or ENDED additions still go through the original
strict new-episode validation; malformed source journals fail safely. Existing finite
bound, new-episode target/evidence/temporal checks, ownership/quarantine and fresh MCP
READ requirements remain. No new storage/state schema or caller, no historical
checkpoint edits or failed-graph/quarantine repair.

8distinctPASS:7focused mock-reader unit cases +1real two-resume integration case;
0FAIL/0SKIP. Both spec validatorsPASS once.2pytest/child interlocks show0external
Gemini/countTokens/0unexpected. Scripted model selections are not genuine AI proof.
No waste/remedial/full suites/live/lifecycle/B15.

B14R2-outcome-WATERLOGGING.json retains all original B14/B14-R assertions and adds
checkpoint_refresh.second_resume: wakes2, correct active incident, actual source
update/fresh READ, three cumulative durable MCP executions, original and first-resume
checkpoints unchanged, one scope refresh audit, scope links and domain events
unchanged. Original incident/outcomes/memory paths retained. Tests reuse one setup;
no failing test or broad corrective rerun in this pass.

Exact files/patch/commands: B14R2-FILES.md, B14R2-changes.patch, B14R2-COMMANDS.md.
All six trackers receive concise append-only entries. Prior public evidence retained.

Human verification: inspect checkpoint_refresh and second_resume in the proof.
Optional isolated reproduction from project root:

```sh
CIVICLY_OPERATIONS_EVIDENCE_PREFIX=B14R2 CIVICLY_B14R_CHECKPOINT_PROOF=1 CIVICLY_TEST_REQUEST_LOG=/tmp/b14r2-human-provider.jsonl backend/.venv/bin/python -m pytest 'backend/tests/integration/test_execution_runtime.py::test_actual_three_issue_completion_verification_and_water_recurrence[WATERLOGGING]' -q --tb=short
```

Expect1PASS and two explicit successful resumes; new isolated graph, no paid call.
Share sanitized B14R2 test log/provider proof if failing; never .env/.runtime/session.
Invalid/changed history proof still requires operator reconciliation under existing
recovery procedure. No quarantine cleared. B14-R synthetic policy/three-incident
limits remain; B10 full genuine Gemini acceptance OPEN/PARTIAL, all18requirements
binding. STOP for B14-R2 review; B15 unauthorized.
