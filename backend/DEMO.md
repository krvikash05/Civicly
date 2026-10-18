# B19 operator runbook — synthetic world, actual services

B18 accepted. B19 exposes scenario mechanics through authenticated API/CLI; this is not AI behavioral acceptance. The simulator releases dated observations, never selects tools, proposes a hypothesis, approves a plan, creates work or declares resolution. B10 genuine-provider acceptance remains OPEN/PARTIAL; no live provider, frontend or B20 execution.

## Private configuration and safe controls

Use accepted host profile/auth/memory/session setup from OPERATOR_CLI.md/API.md. All mutations need explicit keys. ADMIN is coordinator for reset and stage advance. Evidence release additionally requires a valid assigned department lead session and a separate ANALYST reviewer session. Passwords/tokens belong in private owner-only files; never argv/output. Three implemented routes:

| Route | Inputs and authority | Returned facts |
|---|---|---|
| GET /api/v1/demo/scenarios | Any authenticated operator; no query parameters | Twelve neutral numbered titles/categories; current actual case IDs/stage/readiness only |
| POST /api/v1/demo/reset | ADMIN; scenario_id S01–S12, explicit seed19/confirmtrue, variant PRIMARY/NEGATIVE, Idempotency-Key | Fresh source, safe profile-reference relative to host profile directory, stable baseline semantic hash, actual case/incident/cluster/asset/department IDs |
| POST /api/v1/demo/scenarios/{id}/advance | ADMIN; expected_current_stage/stage and relevant actual IDs/hash; Idempotency-Key; field/reviewer Bearer headers for release | Actual newly released evidence IDs, public stage and stage_advanced flag |

No graph/path/file/tool/shell selector is accepted. Unknown/repeated query parameters return422; irrelevant stage fields return422. `X-Field-Authorization` is restricted to scenario advance; `X-Reviewer-Authorization` permits only accepted operational inspection or scenario advance. Scenario list never loads evaluator catalog, hidden truth or reveal file. Host runtime-v1 world packets are loaded only by trusted reset/release code, not MCP/agent/retrieval code. Existing evaluator files are retained unchanged.

Reset retains previous records and profiles. Private new files are placed under the source profile's **host-controlled** parent: `demo-runs/<returned request reference>/profile.json`, `memory.json`, `world.json`, `reset.json`. Never share them. The response contains a relative reference, not credentials. Use new profile/memory files explicitly; operator sessions are source-bound, so log in again to new session files. The auth store remains the same. Same completed source/actor/key/body returns its historical receipt; changing the scenario under that key conflicts. Incomplete/uncertain reset stays blocked; do not change keys to bypass it.

Baseline imports a small validated canonical asset/location/department/route/schedule subset, preserving CANDIDATE ownership and schedules. Separate explicit synthetic survey records introduce DRAIN-100→DRAIN-101 flow for S01/S07/S10 and PIPE-100 UNDERLIES ROAD-100 for S03/S04, **without promoting any imported candidate**. Survey provenance proves topology/context, not a cause. S08 uses a new synthetic waste point location approximately20m from the drain, with no flow connection. S07 reports affected shared drainage context across independent issue cases; causality must still be investigated. D18 playbook logical role maps to DRAIN-101, upstream role DRAIN-100. Claims about old repairs, past pickup reliability or completed orders are clearly reported baseline source text; they are not invented verified historical operations.

The stable baseline hash covers actual copied physical records, normalized baseline reports and explicit survey composition. Runtime journal graph references, activation IDs and audit bookkeeping legitimately differ across fresh runs. Full graph byte identity is not claimed. Each release case has its own packet, inspection and department; cross-category stage remains BASELINE_VISIBLE until every case has its own persisted report. At most three cases and ten observations per packet; no automatic worker.

## Copy-paste setup and release

Use the shell helper from OPERATOR_CLI.md; globals precede commands. Here `$SESSION` initially belongs to ADMIN and `$PROFILE` is the current host source.

```sh
cli() { PYTHONPATH=backend backend/.venv/bin/python -m cli --profile "$PROFILE" --auth-store "$AUTH_STORE" --memory-profile "$MEMORY_PROFILE" --session "$SESSION" --at 2026-10-18T12:00:00.000000Z "$@"; }
cli demo scenarios
cat > /tmp/demo-reset.json <<'JSON'
{"scenario_id":"S07","seed":19,"confirm":true,"variant":"PRIMARY"}
JSON
cli demo reset --payload /tmp/demo-reset.json --key judge-s07-1
```

Read returned `profile_reference` and `scenario.cases`. Preserve the previous profile. Set PROFILE/MEMORY_PROFILE to new files relative to the old profile's parent; create new ADMIN/ANALYST/assigned-lead private sessions using accepted `auth login --credentials ... --key ...`. No token from an old source-bound session file can be reused blindly. Returned asset/department/case IDs supply inspection request JSON:

```json
{"investigation_id":"RETURNED_INV","asset_ids":["RETURNED_ASSET"],"department_id":"RETURNED_DEPARTMENT","inspection_type":"B19_FIELD_SURVEY"}
```

ANALYST calls `cli inspect request --payload request.json --key request-1`. Assigned lead calls `cli inspect transition --id "$INSPECTION" --payload transition.json --key transition-1` for REQUESTED, SCHEDULED(with scheduled_at <= controlled clock), IN_PROGRESS, using each returned current expected_hash. No scenario command performs these transitions or impersonates a field operator.

Switch SESSION to ADMIN and prepare release JSON with the current inspection hash:
```json
{"expected_current_stage":"BASELINE_VISIBLE","stage":"EVIDENCE_REVEALED","investigation_id":"RETURNED_INV","inspection_id":"RETURNED_INS","expected_hash":"CURRENT_INSPECTION_HASH"}
```
```sh
cli demo advance --id S07 --payload release.json --key release-water-1 --field-session "$DRAIN_LEAD_SESSION" --reviewer-session "$ANALYST_SESSION"
cli evidence get --id "$RETURNED_EVIDENCE"
cli investigate hypotheses --id "$RETURNED_INV"
cli graph explain --id "$RETURNED_INV"
```

Repeat separately for S07 waste and road cases with their departments and unique explicit keys. This releases observations only; hypotheses remain operator/agent decisions. Run default offline worker only through separate accepted resume + `advance run`, labelled ReadPause. Release registers only its actual committed inspection event as PENDING; it does not automatically resume or change checkpoints. Explicit discovery can register other source events for a later bounded worker wake.

After evidence, independent investigation/draft/exact approval/work proceeds through accepted B12–B18 controls. A PLAN_AND_APPROVAL stage request needs plan_id with actual exact approved binding. FOLLOW_UP also needs work_order_id, actual COMPLETED status and independent qualifying outcome; no rainfall/pickup/wear opportunity means an actionable blocker, never fabricated success. No new operation bypasses those prerequisites. All candidate owners still require a supported verified responsibility source; the current public API has no owner-verification command. Do not patch retained graphs to bypass this gap.

## Readiness and presentation

See docs/evidence/B19-READINESS.md for every scenario/variant, R01–R18 observations and explicit B20–B23 boundaries. Recommended order: S07 category integration and graph, S01 ordinary water evidence, S03 proximity/reservations (independent utility inspection still required), S05 waste ledger, S10 contradiction, S11 failure/recurrence history gap, S09 no opportunity, S12 outage/untrusted source. Do not present source descriptions as solved cases. Utility repair, capacity upgrades, route redesign and dumping management exceed the three implemented remedial action types; no unrelated action/procedure substitution. S09 completed-work baseline and S11 failed/recurring operational histories require actual approved operator workflows and B22 proof, not seeded forged work orders.

Recovery: exit6/API409 RECOVERY_REQUIRED with UNKNOWN retains source-bound request/entity/investigation identities. Original COMMITTED journal/inspection may exist although stage still shows baseline. Exact replay is blocked; inspect the retained transport intent, release reservation and committed domain receipt through existing supported operator reconciliation. Do not auto retry, replace requests, delete evidence or clear quarantine. Raw journals/exceptions are never public output.

Focused reproducible tests and measured timings are in B19-COMMANDS/RESULTS; real mechanics are distinct from authored world content and scripted ReadPause. Both spec validators are static, not proof of AI decisions. Stop for B19 review; B20/frontend/live require authorization.

B19 isolation guard: InvestigationAgent.run, actual broker scope and domain MCP server apply a Python audit hook denying evaluator/world/playbook/evidence file reads (including symlink resolution and private world.json). Controller reads remain allowed outside this scope. This is not an OS sandbox or permission boundary for malicious arbitrary native code; no runtime agent filesystem/shell tool exists. Actual tools stay graph-scoped and read-only. The representative test checks denial inside actual MCP broker execution and scans actual returned baseline/released results and public projections. Document retrieval is source-allowlisted, never scenario/answer-file ingestion.

Stage readiness across S07: PLAN_AND_APPROVAL is recorded per actual case/plan, and FOLLOW_UP per actual case/work order; the global stage changes only when every case has the relevant receipt. The controller reuses Operations.validate for exact current plan/assignment/source checks and verified approval/order readback. The stage receipt never substitutes for the authoritative domain outcome.

### Final normative transport reconciliation
Reserved DTO fields are preserved: ScenarioDTO.stage; ScenarioPage.next_cursor(null)/total_count(12); SeedReport.nodes/relationships/source_documents/seed_fingerprint; SimulationStepDTO.scenario_id/stage/event_id/revealed_evidence_ids. Returned source/profile/case/readiness fields are additive. SeedReport counts are actual fresh canonical CivicEntity nodes/relationships/Document nodes; reused external SDK documents are not newly seeded, so source_documents is0. Stable seed_fingerprint equals baseline_content_hash. Explicit seed19 selects the version1 fixture; other seeds are rejected, confirm must be actual booleantrue. Advance uses expected_current_stage, not expected_stage. The released event_id is an actual durable PENDING B15 inspection event registered from its COMMITTED B09 journal, never a transport ID/fake execution. Registration is not worker delivery. Later stage event IDs reference actual approval/outcome prerequisites. Runtime investigation request identities include the fresh source via existing request_identity; logical assets/reports stay stable while actual investigations/threads/traces are disjoint, avoiding global trace collision across fresh resets.

## B20-R-OWNERSHIP explicit prerequisite
Fresh scenario reset still imports CANDIDATE ownership only. For legitimate planning, use the actual case asset/department returned by reset: authenticate as that seeded department lead, submit attributed SYNTHETIC inventory evidence, then switch to the independent analyst and review using returned responsibility ID/expected_hash. Verify CURRENT applicability via API/CLI readback before creating the sourced draft. No reset/planner promotion, approval bypass or inferred responsibility. Exact commands/temporal/provenance and UNKNOWN handling: backend/RESPONSIBILITY.md. Missing utility/capacity/route/dumping actions and pickup chronology remain separate blockers; full B20 is not complete.
