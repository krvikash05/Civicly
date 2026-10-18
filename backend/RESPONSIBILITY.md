# Explicit synthetic responsibility acquisition

B20-R-OWNERSHIP only. All18 requirements remain binding; full B20 remains PARTIAL/BLOCKED. Existing B19 reset stays candidate-only. No MCP write tool or automatic owner promotion exists.

A seeded DEPARTMENT_LEAD submits responsibility only for its authenticated department. A distinct authenticated ANALYST independently reviews it. ADMIN and APPROVER may read but cannot submit/review; approval and work authority remain unchanged. Caller-supplied actor, verification status, graph selector or arbitrary edge fields are rejected.

- POST `/api/v1/responsibilities`: actual asset_id, department_id, source_id, source_record_id, source_version(default1), source_kind=SYNTHETIC, observed_at, valid_from, optional valid_to. UTC Z timestamps normalize consistently; observed_at<=valid_from, observation not future to submission, valid_to>valid_from. Source identity is source graph/source ID/record/version. Same identity with different content/submitter conflicts. This creates immutable UNVERIFIED/REPORTED assertion Evidence and durable audit/event, never ownership authority.
- POST `/api/v1/responsibilities/{id}/review`: expected_hash returned by submission, reviewed=true and reason; authenticate as independent ANALYST. The source native/hash/typed provenance, actual asset/department, submitter scope and chronology are revalidated under the writer fence. Overlapping verified ownership rejects. A successful atomic review adds immutable VERIFIED synthetic inventory Evidence, sourced MAINTAINED_BY and hashed operation/state/event. VERIFIED means independently reviewed synthetic administrative responsibility, not a physical cause or executable approval.
- GET `/api/v1/responsibilities/{id}`: bounded safe typed IDs/source/version/dates/hash/submitter/reviewer/relationship/event status. No raw source prose or private journal returned. Department leads read only their own department; other seeded read roles may inspect. Status and applicability are separate: SUBMITTED/UNREVIEWED or VERIFIED with HISTORICAL/FUTURE/CURRENT. Future/historical records are not current planning authority.

Original candidate links/evidence and assertion bytes stay unchanged. Verified intervals are exclusive, half-open. No API can silently end, replace, revoke or rewrite an open-ended verified assignment. A new overlapping assertion may remain SUBMITTED but its review fails; a disputed open-ended assignment requires separately authorized correction, not this workflow. Finite nonoverlapping intervals provide explicit succession. Existing scan bounds fail closed. Existing procedures, reviewed causal evidence and typed safety gates remain independently mandatory.

Every new draft binds exact ownership source/edge IDs and hashes. Operations revalidate these against the saved proof before new approval/work. An expired assignment and same-department replacement still invalidate the old binding; old draft payload/hash/receipt/checkpoint bytes are retained. Compatible older proofs bind their existing IDs, with hashes checked where recorded. No approval is fabricated and no historical plan is rewritten merely to mark it stale.

Writes reuse the existing0005 CivicOperationState and canonical Evidence/DomainEvent/MAINTAINED_BY schema. The repository fence/CAS and one fixed parameterized batch atomically commit source/review/relationship/operation/event. Staged verified review evidence is validated against its immutable submitted source before compilation; no generic caller-controlled source exemption. GRAPH_EVIDENCE_CHANGED remains durable through existing B15 source discovery; it is informational until explicitly bound to a case, with no automatic worker execution.

Exact authenticated HTTP replay returns the saved DONE response; changed same-key content conflicts. Post-commit/readback/projection uncertainty returns existing409RECOVERY_REQUIRED/UNKNOWN with original source-bound request/entity IDs. Intent remains DISPATCHING, exact replay blocks without redispatch. Safe GET can verify committed records but does not clear the intent or quarantine. Operators must inspect the existing operation receipt/native graph evidence and use supported reconciliation review; do not change keys, delete records or fabricate success. A failed checkpoint/write may prevent additional recovery feedback; last durable intent remains authoritative.

## Operator commands (normal private globals/session setup)

Use backend/OPERATOR_CLI.md for profile/auth/memory/session globals. Each POST requires explicit key. The submitting session belongs to the department lead; switch to the independent analyst session for review. Actual returned IDs/hashes must be used; never hand-insert a verified edge.

```sh
cli responsibility submit --payload /tmp/responsibility.json --key inventory-assertion-1
cli responsibility get --id RETURNED_RESPONSIBILITY_ID
# Review JSON: {"expected_hash":"RETURNED_HASH","reviewed":true,"reason":"Independent synthetic inventory review"}
cli responsibility review --id RETURNED_RESPONSIBILITY_ID --payload /tmp/responsibility-review.json --key inventory-review-1
cli responsibility get --id RETURNED_RESPONSIBILITY_ID
```

Example explicitly synthetic assertion payload:
```json
{"asset_id":"DRAIN-101","department_id":"DEPT-DRAIN","source_id":"synthetic-inventory","source_record_id":"drain-101-responsibility","source_version":1,"source_kind":"SYNTHETIC","observed_at":"2026-10-18T12:00:00Z","valid_from":"2026-10-19T12:00:00Z","valid_to":"2026-10-19T13:00:00Z"}
```

These are illustrative dates; applicability follows the host's actual/configured synthetic clock. Responsibility evidence is untrusted as instructions. No utility/capacity/route/dumping intervention or pickup chronology capability is implemented here; B10 genuine-provider gate stays OPEN/PARTIAL. STOP for review.
