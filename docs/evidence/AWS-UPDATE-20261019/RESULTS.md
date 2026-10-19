# AWS update — deployed and verified, 19 October 2026

The current version is live at **https://civicly-13-55-205-208.sslip.io** on the existing Sydney instance `i-00e332036cd609ff0`. This task supports R16/R18 and preserves all 18 requirements. It does not declare B10/B20/B-END or all 12 scenarios complete.

## What public visitors can now see

The dashboard reads graph revision **1056**, **4 active investigations**, **0 pending approvals**, **5 completed work orders** and **3 verified work orders**.

Three retained journeys are complete:

| Journey | Investigation |
|---|---|
| Drain blockage, clearance and rainfall follow-up | `INV-B09-8b006fb97aa2b908fc69addcf7ecd037` |
| Subgrade repair and wear follow-up | `INV-B09-f663f7a1473c4a28a941d147633e08ad` |
| Original utility isolation/repair followed by road repair | `INV-B09-b9d4d66e130ed348c4f6a50e9d66a891` |

All three actual approval records are APPROVED. Each journey exposes the retained investigation, evidence, approved plan, completed work, separate outcome and memory. Field work and observations remain explicitly synthetic; no new AI investigation or physical municipal repair is claimed.

The clean waste case remains OPEN with its TOKEN_BUDGET pause and no plan. Three other recovery cases retain their original flags and exact quarantine values. No blocked case was silently repaired.

Recent frontend improvements are deployed: readable workflow labels, Civicly’s AI wording and shortened description, centered scenario dialog, Next-section navigation, an inline case chooser, and explicit approved/completed plan copy.

## Staging, cutover and recovery

The expired CLI session was refreshed only after the human explicitly approved `aws login --profile civicly`. Preflight confirmed the hosted graph was still at revision818 with the two approvals pending, matching the state before the local completions.

The private export retained six primary graphs, the SDK ontology graph and 17 keys, including three quarantine strings. The source package contained 2,122 files plus a separately protected private snapshot. Runtime secrets, dependencies, builds and Git metadata were excluded from ordinary source collection. The required private configuration travelled only in the private snapshot.

Transfer used an AES256-encrypted S3 object with public access blocked and read access limited to the existing instance role and that exact object. The instance used its own role to download it and checked SHA-256. No credentials or signed URLs entered SSM parameters. The temporary object, bucket and grant were removed after verified download; local and EC2 archives remain private.

The app was built in a fresh release directory. Matching frozen lockfiles permitted reuse of installed libraries. Restoration targeted a new Docker volume on loopback port16379; the populated production database was never flushed. All expected keys, graph inventory, quarantine hashes and AOF were checked. ACLs were persisted before container recreation. A consistent backup of the hosted authentication/session database was preserved in the new release.

After staging passed, `/opt/civicly` switched to `/opt/civicly-releases/update-20261019-01`, and the staged database moved to production ports. The old application/runtime remains at `/opt/civicly-releases/previous-update-20261019-01`, with its old database volume retained. Services, hostname, TLS, instance, account plan and allocated EBS capacity are unchanged. The rollback procedure is documented in `deploy/aws/README.md`; its failure path was not deliberately injected on the public host. Rollback would restore the older snapshot, not merge subsequent writes.

## Actual verification

- **Real public HTTPS checks passed:** homepage and certificate; cross-origin login403; unauthenticated identity401; automatic analyst session; all readiness dependencies ready; dashboard counts; three completed plan/work/outcome/memory/graph/trace journeys; unchanged waste pause and recovery flags; procedures; authenticated SSE frame; logout and revoked-token401.
- **Actual browser checks passed:** water approval/completion/outcome/memory, new AI wording, Next navigation, centered960px scenario dialog, and selecting a real case from the empty workspace. Screenshots are retained.
- **Remote persistence/source checks passed:** eight critical source hashes match; three actual approved plans; three exact quarantine values; persistent ACL file; all expected snapshot keys; API, frontend and Caddy active after database container recreation.
- **Local checks passed:** the same verifier against the actual local system, both specification validators, shell syntax, Python compilation and scoped whitespace checks. The EC2 production build also passed its generated API/contract guards.
- **Zero provider requests** were recorded in the hosted ledger since08:00UTC. No worker, paid model run, full backend regression or EC2 reboot was started. The previous task’s100 frontend unit passes are historical evidence, not relabelled as a new AWS unit run.

See `public-proof.json`, `cloud-persistence-proof.json`, `deployed-source-hashes.json`, `release-summary.json` and `transfer-cleanup.json`.

## Corrected attempts retained

1. Read-only preflight used a nonexistent requirements.lock path; corrected to uv.lock and passed.
2. The initial staging build could not traverse a root-owned0700 parent. Corrected the parent to0711 while release/private paths remained0700/0600. The live app was unchanged.
3. Build and restore passed, but an assertion counted only six primary graphs and omitted the SDK ontology graph. Corrected the check to admit only snapshot-owned graph keys and verify exact quarantine values. Explicit restored-stage resume did not import again. Cutover happened only after validation passed.
4. The initial public verifier omitted the required Origin header on logout and received403. The verifier was corrected; the application’s cross-origin guard remained intact. The full public rerun passed.

The original archive was followed by two hash-verified corrections to the update script and installation of the verification helper. Patch summaries are in `release-summary.json`. Private payloads remain under ignored `.runtime/aws-update-20261019`.

## Changed paths and human review

New scripts: `deploy/aws/update-app.sh`, `deploy/aws/verify_update.py`. Updated guides: `deploy/aws/README.md`, `backend/DEMO_WALKTHROUGH.md`. Six root trackers receive append-only entries. New sanitized evidence is in this directory. No domain logic, frontend business logic, contract, migration or dependency version changed in this deployment task. GitHub was not pushed.

Open the public URL, confirm Demo connected and the dashboard counts. Choose waterlogging and follow Report → Investigation → Evidence → Plan & approval → Work → Monitoring & memory. Repeat the two road journeys. Waste must remain paused.

Nonbillable reproduction:

```sh
backend/.venv/bin/python deploy/aws/verify_update.py --output /tmp/civicly-public-update-proof.json
```

Expect PASS, three completed cases, five completed orders and zero pending approvals. If it fails, share sanitized command output/request ID and the proof; never private configuration.

**Exact next:** human public walkthrough. Resume backend work later as requested. Waste still needs reviewed reassessment, a sourced draft and exact approval, pickup work and the dated24hour observation window. No further phase started. Stop for review.
