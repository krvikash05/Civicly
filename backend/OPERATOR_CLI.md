# Civicly B18 operator CLI

B17/B17-R accepted. This is a local SIMULATED operator interface, not a new municipal engine or genuine live-model demonstration. B10fullgenuine acceptance remains OPEN/PARTIAL. No B19scenario generator, frontend or paid provider. Existing Python3.12environment and running FalkorDB/MCP/Saver/GraphRAG/auth dependencies required.

## Setup and secrets

`civicly` remains `cli.main:main`. From projectroot use `PYTHONPATH=backend backend/.venv/bin/python -m cli`. Existing `civicly health --env-file .env`, `migrate [--retry-failed]` and `schema-status` retain their original semantics. These infrastructure commands are distinct from the operator flow.

Every new command requires host-owned `--profile`, `--auth-store`, `--memory-profile`, `--session`; optional `--at` is a controlled UTC demonstration clock, not client authority over stored facts. Existing immutable migrations/capabilities/explicitdeliveryactivation must already be ready. Normal startup never migrates/seeds/activates/startsworker. Private source and memory profiles authorize the exact configured graph; no runtime graph/query/role/provider selectors.

Credential input is a private0600regular JSON file `{operator_id,demo_password}` created securely by the host. Sessions are saved0600without overwrite and bound to configured source/authstore; no password/token flags or output. Login is idempotent with the same private session file/key/operator while that session remains valid; an expired/revoked session must not be silently renewed. Use a new session file and explicit newlogin after proper operator action. Never share credential/session/profile/authstore files. Payload/query files accept bounded regular JSON; duplicatekeys/nonfinitevalues rejected. Complex mutation payloads are exactly accepted API schemas, with server identities/roles/request IDs excluded. Independent reviewer uses `--reviewer-session` privatefile, never JSON reviewer/token.

## Commands and accepted services

Global configuration flags precede the group/action. Mutation actions require `--key` and `--payload`. Resource actions take `--id`. Read filters use `--query` JSON and the exact B17-R allowlist (unsupported/repeated query parameters rejected). No arbitraryURL/Cypher/shell.

| Group | Actions | Accepted implementation |
|---|---|---|
| auth | login --credentials --key; whoami; logout --key | Existing Auth/API, private saved session |
| complaint | create/get/list | B08intake and scoped reads |
| investigate | open/get/resume/trace/hypotheses | B09case, B15queuedintent, B17state/trace |
| hypothesis | propose/assess/get | B09immutable assessments/history |
| evidence | get | Validated typed findings/source/review |
| inspect | request/transition/report/get | B09typed lifecycle; standalone reports unreviewed |
| plan | create/get/list/submit | B12sourcedDAG, B13exactsubmission |
| approve | decide/get/list | Exact version/hash/scope and APPROVER |
| work | create/get/list/status/progress/inspect/evaluate | B13/B14same auth/CAS/state/independent review |
| graph | explain/neighbors/asset | B17authorized neighborhood plus B03actual bounded evidence paths/provenance/reservations |
| source | document/procedures | Actual versioned B11citations, PROPOSED authority |
| advance | discover --key; run --key [--batches1..4] | Separate explicit B15discovery or bounded offlineWorker |
| reset | --key --output-dir NEW_PRIVATE_DIRECTORY | Fresh-only isolated starter, no retained graph reset |
| test | no extra command text | Actual bounded Services.health(readiness), no suites/lifecycle/live |

All actions use the configured in-process FastAPI/API→same Services path; no HTTP listener or webUI necessary. Auth/RBAC/strictmodels/errorenvelopes/exactbindings/source-bound idempotency/B16-RpostdispatchUNKNOWN are the same as the accepted API. Graph explain adds bounded actual hypothesis-evidence PathRecords from the accepted B03 template only if their endpoints/edges/evidence are in the authorized B17view at the same revision. These analysis paths are labelled context, not model-selected decisions. Read output uses typed public DTOs, no raw graph properties/journals/provider bodies/private reasoning. `--format text` adds a readable SIMULATED heading; default JSON is machine-readable with status/data/mode. Both contain actual public service output.

Exit0success,2validation/configinput,3authorization,4conflict/missingresource,5dependency/unavailable,6RECOVERY_REQUIRED/UNKNOWN. Errors are bounded/sanitized; supplied safe correlation/request/entity/investigation/plan IDs retained. No automated retry/replacementrequest/rollback/deletion/quarantineclearance. A failed response means inspect original durable intent/journal/checkpoint under existing recovery procedure; never choose a new key merely to bypass uncertainty. Exact successful domain/advance/reset replay returns original acknowledgment, not current execution authority. Authentication retains existing expiry/revocation semantics: repeated logout is denied after revocation and never resurrects a session.

## Advance and reset boundaries

Queued resume returns PENDING intent; it does not execute investigation. `advance discover` only registers existing committedfacts. `advance run` consumes at most1..4existing batches, performs no implicit discovery, uses accepted Runtime.ReadPause (one real MCPread thenpause) labelled B15_DETERMINISTIC_DEVELOPMENT_NO_PROVIDER. It is not a hardcoded scenario solver or autonomous model. Explicit ADMIN/ANALYST, key bound to source/operator/action/bounds. Existing fenced companion records DISPATCHING then DONE; uncertainty blocks same-key redispatch. Worker receipts/status checked; partial/recovery cannot report successful delivery. Work completion remains separate from independently dated outcome verification.

Reset is ADMIN-only, explicitkey/newprivateoutputdirectory, servergenerated ActiveProfile/source/Saver. It validates the existing B04canonical bundle and copies only actual DRAIN-100,LOC-005,DEPT-DRAIN,EVD-B04-IMPORT + their2location/ownership edges using the existing schema/repository. Fixed content/timestamps/hash are deterministic across distinctnewgraphs. CANDIDATE ownership remainsCANDIDATE, not invented verified responsibility or physicalcause; no complaint/incident/work/action/hiddentruth seeded. A full case requires actual accepted evidence/knowledge/ownership prerequisites; reset alone is not a solved scenario. Existing approved memory/readcapability reused explicitly with newsource binding, authstore unchanged. Fresh target only, apply existing0001/0004/0005 there, provision exactread/SaverACL and explicitfreshcutover; no deletedoldgraph/volume/migrationchange/sourcepromotion. Oldsource andhistory remain.

Existing source/operator/key companion binds destination; a changed destination under the same key conflicts. DISPATCHING blocks uncertain replay even if a local manifest was written. Exclusive private STARTED manifest precedes provisioning; DONE requires exactfixture readback. Same completedrequest returns historicalreceipt, never clears current data. Reset administrative intent/audit appends to the previous source; existing domain records and history are not rewritten. Incomplete/unverified reset staysUNKNOWN/manualinspection, no automaticrepair or reuse of partialtarget. Newdirectory contains `profile.json`, `memory.json`, `reset.json`; contains secrets, never share. B19twelve scenarios/delayedreveals/evaluation remain deferred.

## Copy-paste operator walkthrough

Prepare existing private setup and authored accepted payload JSON files; no secrets below. Shell helper only invokes the fixed CLI, not arbitrary command strings:

```sh
cli() { PYTHONPATH=backend backend/.venv/bin/python -m cli --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --session "$SESSION" "$@"; }
cli auth login --credentials "$CREDENTIAL_FILE" --key login-1
cli auth whoami
cli investigate open --payload open-case.json --key open-case-1
cli investigate get --id "$INVESTIGATION"
cli investigate resume --id "$INVESTIGATION" --payload resume.json --key resume-1
cli advance run --key offline-wake-1 --batches 1
cli investigate trace --id "$INVESTIGATION"
cli inspect request --payload inspection-request.json --key inspection-1
cli inspect transition --id "$INSPECTION" --payload transition.json --key transition-1
cli inspect report --id "$INSPECTION" --payload observations.json --key report-1
cli plan create --payload sourced-plan.json --key draft-1
cli plan submit --id "$PLAN" --payload exact-submission.json --key submit-1
# Set SESSION to the authenticated APPROVER private session file.
cli approve decide --id "$APPROVAL" --payload exact-decision.json --key decision-1
cli work create --payload authorized-order.json --key order-1
# Set SESSION to assigned DEPARTMENT_LEAD; reports use independent analyst file.
cli work status --id "$WORK_ORDER" --payload assignment.json --key assignment-1
cli work progress --id "$WORK_ORDER" --payload start.json --key start-1
cli work inspect --id "$WORK_ORDER" --payload work-inspection.json --key work-inspection-1 --reviewer-session "$ANALYST_SESSION"
cli work progress --id "$WORK_ORDER" --payload completion.json --key complete-1
# Set SESSION back to ANALYST for actual follow-up evaluation.
cli work evaluate --id "$WORK_ORDER" --payload outcome-window.json --key outcome-1
cli work get --id "$WORK_ORDER"
cli graph explain --id "$INVESTIGATION" --query graph-query.json
cli source document --id "$CANONICAL_DOCUMENT"
cli advance discover --key discover-1
cli test
# ADMIN only; this creates a new starter, preserves current source.
cli reset --output-dir "$NEW_PRIVATE_DIRECTORY" --key fresh-demo-1
```

Payload examples/schema are available from existing accepted API/models and the actual subprocess proof. Transitions/inspection report follow exact accepted order and expected_hash; workapproval binds fullplan/version/hash/taskassignments. Completion requires attributable reviewed evidence; follow-up needs a real authorized inspection/report and qualifying observation opportunity, not arbitrary declared success. The test's authored payloads are clearly synthetic; operator commands neither choose hiddenanswers nor invent a verifiedcause.

Exact reproducible focused tests, command counts, retained IDs, failures and recovery/isolatedreset proof: docs/evidence/B18-COMMANDS.md/B18-RESULTS.md/B18-cli-journey.json. STOPfor B18review; B19/frontend/live not authorized.

Reset nodes/edges counts describe the4fixedfixture nodes/2edges; activation/audit/migration metadata is additional. A fresh starter intentionally lacks independently verified responsibility/causal evidence; existing accepted planning gates can block until their actual prerequisites are supplied through reviewed setup/services. B18 does not add an ownership-verification API or silently upgrade candidate records. The real acceptance journey uses existing accepted fixture evidence/verified ownership, then a newly CLI-opened case and operator-authored service commands.

## Current B19 additions — 2026-10-18
B18 accepted; B19 adds `demo scenarios`, `demo reset --payload ... --key ...`, and `demo advance --id Snn --payload ... --key ... --field-session ... --reviewer-session ...`, delegating the three accepted demo API routes. Historical B18 bare `reset` remains the same4node starter command; `demo reset` is the explicit twelve-scenario entrypoint. No caller graph/path/world/tool/shell selector. Use returned private profile reference and fresh source-bound login files. backend/DEMO.md contains actual returned-ID workflow, required field/reviewer/lifecycle/prerequisite gates and all limitations. B20/frontend/live remain unauthorized; B10 genuine OPEN/PARTIAL.

B20-R-OWNERSHIP fixed commands: `responsibility submit --payload FILE --key KEY`, `responsibility review --id ID --payload FILE --key KEY`, `responsibility get --id ID`. Use department lead then independent analyst sessions; shared API/domain validation and recovery apply. See backend/RESPONSIBILITY.md. Candidate reset behavior remains unchanged; no other B20 correction or live execution is authorized.
