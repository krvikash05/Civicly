# B18 — technically passing; human review pending

B17/B17-R were human accepted. B18 only: functional operator CLI over the accepted services, not a frontend, new domain implementation or full scenario generator. All R01–R18 remain binding. Genuine-provider B10 acceptance remains OPEN/PARTIAL. B19 and live provider execution require separate authorization.

## Implementation and decisions

`civicly` preserves health/migrate/schema-status through a byte-identical copy of the previous entrypoint in cli/legacy.py. Operator commands invoke the accepted configured FastAPI/application services in process: actual authentication, closed route/input/output schemas, RBAC, exact approval/CAS, source-bound idempotency, independent review and B16 recovery. No network HTTP server is needed. Private bounded owner-only credential/session files bind to the host source/auth store; secrets never become CLI arguments or public output. JSON and text summaries have stable exits 0/2/3/4/5/6.

Command inventory and service mapping: contracts/operator_cli.json and backend/OPERATOR_CLI.md. Investigation, typed inspections, evidence/hypothesis reads/writes, sourced drafts/submission/exact approval/rejection, work progress/completion/independent outcome, documents/citations and graph explanation use accepted interfaces. Graph explanation adds actual bounded B03 hypothesis/evidence paths filtered to the authorized B17 projection and same revision, explicitly context rather than model-selected causal reasoning.

Advance explicitly separates discovery from bounded offline worker consumption (maximum four batches). It uses existing Delivery/Worker/Runtime ReadPause and companion/fence records for receipts, source/actor/key/payload binding and uncertain replay blocking. No automatic worker/provider start. Queued resume is not completed investigation; completed work is not verified resolution.

Reset creates a server-generated fresh isolated source/Saver profile using existing migration/repository/ACL/cutover machinery. The strict existing B04 subset contains four fixture nodes and two actual relationships: DRAIN-100, LOC-005, DEPT-DRAIN, EVD-B04-IMPORT. Activation/audit/migration metadata is additional. Previous domain records/history are retained. A source/operator/key-bound receipt includes destination binding; exact replay is historical, changed destination conflicts, partial/uncertain execution stays blocked for manual reconciliation. No delete, retained-target reuse, automatic repair or B19 engine. Candidate ownership is preserved; the starter alone lacks verified planning prerequisites and no new ownership-verification API is claimed. `test` performs bounded actual dependency readiness; no arbitrary shell/test-suite/provider execution.

## Executed verification

**72 distinct passing pytest cases: 71 unit, one real integration; zero failures or skips.** Counts exclude reruns and specification/audit checks. The final new unit module has 70 distinct cases; one accepted foundation redaction case also passed. The final two initial-intent fault cases were exercised after an exception-only refinement, together with three overlapping replay cases. Those faults are mocked units, not database proof. No full historical suites or lifecycle tests ran.

The one shared real WATERLOGGING journey passed twice (129.07s initially; 132.37s after directly affected refinements). The refined execution used **71 successive actual CLI subprocess invocations**, not 71 integration tests. Offline ReadPause choices and authored fixture payloads are deterministic; FalkorDB 6.0.2, official/domain MCP initialization/discovery/calls, Saver, document/source SDK, services, authorization and persistence are real. Three existing dependency deprecation warnings occurred; no test failure was hidden.

Both specification validators passed in one final guarded `make test-spec` invocation. Six pytest/child interlock reports show zero external Gemini/countTokens requests and zero unexpected attempts. The accepted paid accounting ledger, sessions and holds remain unchanged. Exact commands/times: B18-COMMANDS.md; raw logs and zero-live reports alongside it.

### Persisted real proof

Source: `civicly_b10_test_4db45f24505941c88b4095d62ba1f5db`.
Investigation: `INV-B09-ec6c020a3071cf902f9b3f18578c562e`.
Plan: `PLAN-B12-c8e5593870da3a2eda117dfb20eed822`.
Exact approval: `APPROVAL-B13-1cbc986267e81e51f9c4192cac7bc156`.
Single work order: `WO-B13-795f203f67c97bb9d60827ed5d4c907a`.
Independent outcome: `OUTCOME-B13-68b1ffcff494a37c4e00884cfa7c40a2`, RESOLUTION_VERIFIED / MITIGATION_VERIFIED, with its own followup evidence. Completion and a no-opportunity monitoring evaluation preceded actual qualifying independent verification. Graph explanation returned an actual evidence path and document citation. Wrong-role mutation denied; successful duplicate replay retained one work order.

The test-only child injects EvidenceService.readback failure **after a real inspection commit**. CLI exits 6 with RECOVERY_REQUIRED / UNKNOWN and safe correlation/request/entity/investigation IDs. The COMMITTED journal and original inspection remain; ordinary exact replay exits 6 without redispatch or a second effect. Request `HTTP-B16-94a751469fb18114b6ddeccefcc6dbd3`, inspection `INS-B09-cf8394ab657af3bd652f37e3503603c2`. No quarantine is cleared and no plan/inspection is deleted or repaired. An operator must inspect the persisted receipt/journal and use the existing supported reconciliation procedure; changing keys is not recovery.

Fresh reset graphs `civicly_b10_test_f9b6b50318764355899d2a6501e3e33f` and `civicly_b10_test_5fc6b5906f5b4c77bdbc088bb15abac0` are distinct, with matching fixture hash `098e7c819cfc396a4dc92f03f75b77bc1e946dfce3a1cc9db0d060a115060d6c`. Exact replay is unchanged; same key/different destination and existing directory are rejected. Candidate authority and previous source/work history remain intact. Full sanitized proof: B18-cli-journey.json.

## Preservation, limitations and review

Read-only audit verifies all 1,429 baseline public files retained, all 1,003 prior evidence files byte-identical, previous tests/migrations/registry/data unchanged, append-only six trackers, original B01 probe, full retained B04 city content/hash and 42 candidate drainage links, and the original quarantined B12-R2 single plan. New public artifacts and patch are scanned against known private configuration values and secret patterns; no values are exported. Exact versions and actual preservation results are in B18-audit.json. The first audit lookup used pytest-current after a unit run and found no integration profile; corrected to locate the retained matching source profile across pytest directories. This was a read-only audit lookup failure, not a runtime acceptance failure. One earlier metadata utility used system Python without pydantic; corrected to the project venv before writes.

Limits: host-provisioned private configuration is required; no new public authentication/bootstrap system. Default worker behavior remains offline ReadPause, not a genuine autonomous-provider success. Accepted graph/search/history caps and evidence gaps remain explicit. Fresh starter reset is not a solved city scenario. Existing recovery/quarantine operator obligations remain. No dependencies, migrations, domain/storage/worker rules, imported city data, accounting or prior evidence were changed. The narrow patch is relative to the public B18 pre-edit snapshot, not HEAD, because earlier accepted work was already uncommitted.

Human verification: B18-WALKTHROUGH.md supplies secure configuration/login/readback commands and the single guarded fresh journey command; backend/OPERATOR_CLI.md documents actual payload sequences. Review B18-FILES.md and B18-changes.patch. **Stop after B18. Proposed next task: B19 deterministic scenario fixtures/generator and delayed-reveal proof, only after separate human authorization.**
