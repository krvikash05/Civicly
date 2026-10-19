# AWS-UPDATE-20261019-02 — PASS

19 October 2026. Existing public demo: https://civicly-13-55-205-208.sslip.io
Existing instance: i-00e332036cd609ff0, ap-southeast-2. Active release /opt/civicly-releases/update-20261019-02; previous /opt/civicly-releases/update-20261019-01 retained with its separate database volume.

## Delivered

Latest frontend through F26: clearer homepage, incident/report descriptions, compact case/work/monitoring cards, report-stage links, next-stage navigation, case chooser, scenario journey status and functional dashboard record dialogs. The retained graph is revision1148: three completed investigations, one MONITORING investigation, three OPEN recovery cases; six completed work orders, three verified work orders and zero pending approvals. The approved waste pickup, independently reviewed completion and dated monitoring evidence are now hosted. Its saved prior AI budget pause remains distinct from current work status. No future observations, false closure or new AI recommendation was created.

## Verification actually run

- Frontend tests:120 PASS, zero failures/skips. These are offline tests, not live-agent verification.
- Both local specification validators PASS; deployment shell syntax PASS.
- Real EC2 production Next.js build/API/contract/type validation PASS.
- Fresh private restoration:6 primary graphs plus SDK ontology graph,17 durable keys; original3 quarantine dump hashes preserved. Persistent AOF and users.acl verified after the staged container was recreated on production ports.
- Hosted-source guard:READY revision1056 with empty pending marker immediately after stopping services; cutover refused to replace newer cloud graph writes. Cloud auth/session DB was separately backed up and retained.
- Public HTTPS acceptance PASS: homepage, automatic analyst login, unauthenticated/cross-origin/revoked-session denials, dashboard4/0/6/3 counts,3 completed cases and their work/outcomes/memory, waste MONITORING with its exact approved plan hash and one completed order, bounded graph and recorded traces,3 recovery flags, cited procedures and actual SSE frame.
- Fresh cloud readback PASS:all7 thread/checkpoint IDs/data hashes and3 quarantine hashes match local predeployment proof; source READY revision1148/empty pending;140 historical provider requests,0 sessions/holds/unsettled requests. New external provider requests0. No worker started.
- Actual public browser:updated homepage connected, work card dialog listed6 real work orders, waste completed work and monitoring/graph loaded. Screenshots retained.

## Packaging and transfer

A private archive included working-tree source and the fresh snapshot; .git, dependencies, generated builds and ordinary secret environment paths were excluded from public source inventory. Private configuration was included only under private-snapshot and transferred solely to this project's encrypted, public-blocked temporary S3 bucket. SHA25695bf09f4001481eb4564b8a129aa975383e1c2937cdb9daee9332c83ad69ae8f matched on EC2 before extraction. Existing dependency lockfile hashes matched before installed libraries were reused. Selected deployed source hashes match the release manifest. Temporary exact-object instance permission, object and bucket were removed after verified transfer. No new instance, account-plan upgrade or public database port was introduced. Extra retained volumes use existing allocated EBS disk.

One initial prepared archive was replaced in the temporary staging object before any EC2 download when the hosted-write guard was added. Both local archives remain private; only the guarded archive was deployed. Two initial curl connection failures occurred while the supervised API was starting; bounded readiness subsequently passed. No deployment retry or failed cutover occurred. Rollback trap was not fault-injected on the public instance.

## Human verification and remaining limits

Open the homepage and confirm Demo connected plus6 work completed. Click that card, then Complete the missed waste pickup; inspect Work and Monitoring & memory. Open Plan & approval to see its recorded approval. Browse one completed road or waterlogging case for verified outcomes and memory.

Waste still needs independent dated post-pickup evidence after20October2026 16:19:17.747 IST before closure. Three other cases retain their quarantines and need the already identified tested reconciliation extension. B10/B20/B-END acceptance remains partial; deployment does not close those gates. Current cloud and local graphs now form independent forks; future snapshots must again check hosted writes. Local frontend/backend remain stopped as requested; local FalkorDB and saved data were retained. No Git push was performed.

Exact next task:human public walkthrough, then the bounded recovery reconciliation microtask when continued. Stop after this deployment.
