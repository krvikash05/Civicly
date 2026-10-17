# blockers.md — Current blockers and verification spikes

## Current status — B05, 2026-10-17 (takes precedence over history)

No active B05 environment blocker. B05 tests PASS; human review pending. City42 drainage links remain CANDIDATE;4 broader asset sets supported,8 starting-asset/6 cluster source conflicts and3 unspecified cluster contexts need author review. S07/history/55 unlinked measurements and DEC-004 dependencies remain OPEN at B08/B09/B11/B19/etc. Bounded-search/clone limits explicit; no B06 started.

---

No active implementation blocker is claimed. Verification spikes (NOT defects) are tracked in `docs/backend/12_falkordb_sources.md`.

## Template
### BLOCK-XXX / Bxx
- Symptom + minimal repro:
- Exact command + error:
- Impacted requirements:
- Attempts (non-destructive):
- Root cause hypothesis / needed human action:
- Workaround considered and why it preserves all objectives:
- State: OPEN / RESOLVED:

## B00 findings | 2026-10-17
### BLOCK-B00-01 — Environment | RESOLVED FOR AUDIT; B01 setup pending
- `python --version`: absent. `python3 scripts/validate_blueprint.py`: missing jsonschema, exit 1. Existing `python3.12` with jsonschema runs both validators successfully, no installs needed.
- `docker version`: sandbox socket denial; read-only escalated retry confirms running Engine 29.8.2. No Docker-start action needed.
- `git status --short`: not a git repository. Initialize local Git and isolated project dependencies in B01. No public account required.
- Selected provider/model/auth/MCP key variables unset in inspected process. Configure chosen model/provider locally before live tests; never paste keys into chat. Not a B00 blocker.
### BLOCK-B00-02 — Contract/fixture discrepancies | OPEN
- Confirmed: 55 expanded Observation nodes use unregistered value_number. Generator repeats it; supplied validators miss it. Reproduce with TEST-20261017-B00-04. Blocks trustworthy B04 import until aligned.
- DEC-004 details scope schema (B02), MCP envelope/traces (B07), source version/owner/PDF (B11), approval binding (B12/B13), event durability (B15), API mapping (B17), historical scenario records/evaluator isolation (B19).
- Human action needed now: review B00 and say continue for B01. No decision or credential needed to finish audit; later tasks must correct gaps before consuming affected contracts.
- Runtime proofs deferred by task boundary, not replaced by mocks: graph persistence, RO_QUERY, MCP, checkpoint restart, GraphRAG, durable recovery and live LLM.

## B01 follow-up | 2026-10-17
### BLOCK-B01-01 — Isolated dependency/Git sandbox access | RESOLVED
- Initial sandbox pip install failed DNS/network resolution; repeated authorized network install succeeded in backend/.venv only. Initial git init got Operation not permitted; approved escalation initialized main. Docker socket access used authorized escalation. No auto-review rejection occurred.
- Initial wrong image-entrypoint paths returned file-not-found; docker image inspect identified /var/lib/falkordb/bin/run.sh, then actual entrypoint/storage inspected successfully. No unsupported version workaround needed.
### BLOCK-B01-02 — Fresh graph health assumption | RESOLVED
- Repro: official client select_graph('civicly_knowledge').ro_query('RETURN $probe LIMIT 1', params={'probe':'health'}, timeout=1000) before initialization -> `Invalid graph operation on empty key`.
- First integration suite: 2 FAIL, 4 PASS (health and CLI failed). Fixed observational health with explicit uninitialized/null-read state; existing graph still requires real RO_QUERY. Final 15-test suite PASS. No sentinel inserted into canonical graph; B02 unchanged.
### BLOCK-B00-02 — Continued OPEN (not waived by B01)
- All 55 Observation.value_number defects remain; contracts and fixtures untouched. Same scope naming, MCP traces, approval binding, document ownership/version/PDF, historical records, event metadata/revision mapping and evaluator isolation findings in DEC-004 remain scheduled before consumption.
- Dependency compatibility with MCP/LangGraph/FalkorDBSaver/GraphRAG and live provider is still UNVERIFIED; not required for B01. Local graceful persistence does not resolve event durability or checkpoint recovery.
- Human action now: review B01; say continue for B02 when accepted. No active B01 environment blocker. If tests fail, share test output + test_log/blockers and redacted compose logs; never .env/full config containing secrets.

## B02 blocker disposition | 2026-10-17
### BLOCK-B02-01 — Vendor API/Cypher mismatches | RESOLVED
- Installed falkordb1.8.0 lacks docs create_constraint helper; QueryResult lacks statistics; FalkorDB6.0.2 rejects YIELD *. Minimal spikes in test_log failed with AttributeError/ResponseError, then passed using execute_command, known result API and explicit columns. No package swap or graph substitute.
### BLOCK-B02-02 — Premature asset_type restriction | RESOLVED
- First unit test run 31 PASS/1 FAIL: new subtype constants rejected five legacy values. Removed invented constant rule per DEC-008; canonical labels remain typed, original string vocabulary retained. Fixtures not modified. Final suite53 PASS.
### BLOCK-B00-02 — Partially resolved; remains OPEN
- RESOLVED only scope naming: municipality_id=demo-city is canonical v3, required on nodes/edges and synchronized contract metadata/specs. tenant_id not accepted as alias; future framework adapter only if verified necessary. No enterprise isolation claim.
- OPEN: all 55 Observation.value_number defects; explicit v1/v2 scope/version/edge-ID/date conversion required before B04 import. Strict adapter rejects incompatible records; supplied sources unchanged. Also still OPEN: MCP trace/envelopes, approval plan/assignee/scope binding, document ownership/version/PDF, historical fixture completeness, event durability/revision mapping and hidden evaluator isolation at their original stages.
- Native constraints lack CHECK-style type/unknown/endpoint/conditional/global-edge-ID enforcement. Proven limitation, addressed structurally by B02 validator; future B03 repositories/services must enforce graph-aware rules and use controlled write paths. Raw developer DB access remains privileged.
- No active B02 runtime blocker. Recovery never requires deleting B01 evidence/volumes; see backend/SCHEMA.md. Missing live provider/agent integrations remain outside B02.
- Human action: review B02; continue only when ready for B03. Share schema-status, test output/test_log/blockers on failure; never .env or secrets.

## B03 review | 2026-10-17

### BLOCK-B00-02 — Continued OPEN; no fixture repair/import
- All55 legacy Observation.value_number discrepancies remain, with original registry/
  fixture source hashes preserved. B03 cannot silently accept/discard unknown fields.
  Explicit reviewed B04 conversion must resolve them before canonical ingestion.
- Scope naming was resolved in B02 (municipality_id=demo-city); B03 enforces it.
  MCP trace/envelopes (B07), documents/provenance/PDF (B11), approval binding
  (B12/B13), historical completeness (B04/B19), event durability (B15), API mapping
  (B17) and hidden evaluation-data isolation (B19) remain open per DEC-004.

### B03 runtime projection issue — WORKAROUND VERIFIED; no active B03 blocker
- Minimal repro: MATCH a disconnected CivicSchemaMigration node, WITH m, then an
  upstream DRAINS_TO variable path and RETURN coalesce(m.repo_revision,0),nodes(p).
  Installed6.0.2 returned0 twice while separate revision read returned52 in initial
  spike; current reproducible report uses its fixture revision53. This observation
  does not establish root cause or an upstream fix.
- Avoided metadata projection entirely; bounded reads check actual revision before
  and after path retrieval/validation and retry once. Actual upstream templates now
  pass. Pending state blocks reasoning, and changed pending pre-state fails closed.
- Limits requiring future review: raw privileged writes bypass repository policies/
  revision; no enterprise isolation; no reconstructed historical node snapshots;
  policy scan/audit budgets fail closed; audit archival needs reviewed migration.
  Writer metadata/audit is not a domain outbox or MCP trace. Auth/state/approval/
  durable events remain later gates. No user environment action is needed for B03.

## B03-R corrective review | 2026-10-17
- No active B03-R environment blocker. IN_ZONE/PART_OF primary assignment omission,
  route/service schedule conflict gap, connector/total-hop mismatch and divergent
  test-target guards corrected with real tests. No schema migration or source-data
  correction was required; original review evidence is retained.
- BLOCK-B00-02 remains OPEN:55 Observation.value_number defects, explicit v1/v2→v3
  conversion before B04, and all remaining DEC-004 findings (MCP trace contracts,
  approval binding, document provenance/PDF, historical completeness, event durability,
  API mapping and hidden evaluation-data isolation). No silent waiver or field drop.
- Remaining schedule limitation: service_type is an exact existing string, not an
  ontology of aliases; B04 must review nomenclature. schedule_spec is opaque. Two
  overlapping same-service definitions cannot be proven compatible from free text;
  use one definition for recurring windows or nonoverlapping validity. No weekly
  recurrence parser or new properties introduced.
- B04 performance remains UNVERIFIED, not a failed B03-R gate. Repeated type scans,
  global edge-ID scans and growing scalar audit may limit import speed. Benchmark
  plan defines pilot/full/repeat measurements and correctness gates; no bulk shortcut
  implemented. Existing policy/audit budgets fail closed and cannot be bypassed to
  meet timing. Proposed optimization/archival needs review and real guarantees.
- Variable traversals remain bounded to6 total edges; search_limited explicitly
  prevents treating empty results as global absence. Historical node snapshots are
  not reconstructed. Privileged raw DB access still bypasses application policy;
  the namespace guard is not authorization/RBAC. These limits remain documented.

## B04 source findings and retained limitations | 2026-10-17
- BLOCK-B00-02 numeric portion RESOLVED in explicit B04 conversion:55 measurements
  preserve values/units/observed dates; originals remain frozen as regression evidence.
  DEC-004 aggregate remains OPEN for designated MCP traces/transport (B06/B07),
  GraphRAG source ownership/version/PDF completeness (B11), approval binding (B12/B13),
  event durability (B15), API mapping (B16/B17), historical fixtures and evaluator
  runtime isolation (B19). Source visibility guards are not runtime mount isolation.
- BLOCK-B04-DATA — OPEN: legacy109 pickup inconsistencies,15 report chronology
  conflicts quarantined (342 records including218 dependent edges). New generator
  revision explicitly authors corrected synthetic data, not a historical recovery.
 68 unsupported verified associations downgraded;154 unknown statuses made CANDIDATE.
 25 coordinate binary residues explicitly normalized at verified wire precision.
 110 pickup local-clock/schedule-text warnings, service aliases,55 unlinked
  observations, binding/incident differences, absent historical WorkOrder/AgentDecision
  chains and S07 physical topology gaps remain for B08/B11/B19. No invented dates,
  inspections, physical connections, licensed source claims or PDF evidence.
- BLOCK-B04-PERF — OPEN LIMITATION: single-scalar audit and same-kind scans scale
  quadratically;10,000 audit/2,000 per-kind/policy-step limits remain unchanged. Timing
  targets do not establish larger-city readiness. Largest scans/query/byte totals are
  measured; cycle/schedule comparison totals and lock-wait distributions are not.
  AOF delta is server-wide net snapshot affected by verified automatic rewrites,
  not cumulative I/O. No untested bulk/audit optimization introduced.
- First pilot precision failure retained graph
  civicly_b04_test_407a845eafb843b7955dcc4bd00335e0. No source conflicts are “repaired”
  by deleting it. Canonical promotion of B04 fixture is intentionally unperformed;
  review retained isolated final graph before any later authorization.

## B05 current source and algorithm limitations | 2026-10-17
- No active B05 environment blocker. Actual native BFS invocation includes expired
  link; selected filtered Cypher strategy tested. No native feature absence claimed.
- BLOCK-B05-DATA — OPEN:city0 verified drainage paths (all42 candidate); four broader
  investigative bindings legitimate (S01/S02/S05/S07), eight starting-asset source
  conflicts need author confirmation, six primary-cluster conflicts/three unspecified
  contexts. Do not automatically rewrite or promote data. S07 full cross-category
  topology,55 unlinked Observations and missing repairs/decisions/outcomes remain
  B08/B09/B11/B19. One existing ROAD-R08 inspection is contextual, not resolution proof.
- BLOCK-B05-BOUNDS — DOCUMENTED LIMITATION:bounded paths/induced components do not
  prove global absence/completeness. City case searches can truncate; partial ranks
  are lower bounds.5s deadline cooperative around bounded I/O, not real-time process
  cancellation. Full city exceeds complete clone120node/200edge cap and is refused;
  properly evidenced small fixtures demonstrate required ablations. Explicitly
  inspected drainage cycles are not automatically reauthorized during clone copy.
- BLOCK-B00-02 numeric portion remains RESOLVED by B04; originals/55-defect regression
  preserved. Remaining DEC-004 MCP trace/envelopes (B06/B07), memory/GraphRAG document
  owner/version/PDF (B10/B11), approval (B12/B13), event durability (B15), API mapping
  (B16/B17), fixture histories/evaluator process isolation (B19) stay OPEN.
- Existing policy/audit scaling limits remain:counterfactual copying uses ordinary
  writes, not a new bulk shortcut; source/canonical/retained volumes never reset.
  No full scenario, agent or frontend capability declared complete by B05.
