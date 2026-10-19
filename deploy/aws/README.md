# Latest frontend update — verified 19 October 2026 (ui-20261019-01)

The [public demo](https://civicly-13-55-205-208.sslip.io) now serves reviewed frontend changes through F37, including **Every civic problem has a story. Follow it to resolution.**, the featured case, graph guide, stage takeaways, response timeline, curated journeys and calmer loading states.

Frontend service WorkingDirectory is `/opt/civicly-frontend-releases/ui-20261019-01/frontend`, selected through `/etc/systemd/system/civicly-frontend.service.d/50-ui-release.conf`. Backend and database still use `/opt/civicly` → `/opt/civicly-releases/update-20261019-02`; their services/volumes were not restarted or replaced. Graph revision1148 and retained case/work/outcome/recovery states are unchanged. Local servers were left running.

136 frontend tests, both spec validators, actual EC2 production build, all70source hashes, public HTTPS/API/SSE/security checks and browser walkthrough passed. One staging-only Turbopack symlink error was corrected by copying locked dependencies into the frontend release. No provider calls, worker wakes, S3 transfer resources or IAM changes.

[Results and exact checks](../../docs/evidence/AWS-UI-20261019-01/RESULTS.md) · [Public acceptance](../../docs/evidence/AWS-UI-20261019-01/public-after.json) · [Preservation comparison](../../docs/evidence/AWS-UI-20261019-01/preservation-comparison.json)

Frontend-only rollback, if explicitly chosen: remove the new `50-ui-release.conf` override, run `systemctl daemon-reload`, then `systemctl restart civicly-frontend`. This restores the previous frontend working directory without reverting any database. Retain both frontend releases. The historical full-release rollback instructions below are separate and must not be used for this frontend-only update.

Backend acceptance/recovery and waste follow-up obligations remain open. Next: human public walkthrough.

---

# Latest update — verified 19 October 2026 (release02)

The [public demo](https://civicly-13-55-205-208.sslip.io) now serves frontend F15–F26 and retained graph revision1148: **three completed cases, one under monitoring, three recovery-blocked cases, six completed work orders and three verified work orders**. The approved waste pickup is complete; its independent post-pickup monitoring remains outstanding. Earliest eligible follow-up is20October2026 at4:19pm IST; elapsed time alone does not prove resolution.

Active `/opt/civicly-releases/update-20261019-02`, previous `/opt/civicly-releases/update-20261019-01`; `/opt/civicly` points to the active release. Docker project `civicly-update-20261019-02`. Both previous app and database volumes remain retained. Public host, EC2 instance, TLS, services, account plan and allocated disk remain unchanged. A cutover guard checked the old hosted graph was still READY revision1056 with no pending write; hosted auth sessions were backed up separately.

120 frontend tests, both spec validators, actual EC2 production build, public HTTPS/API/SSE/security checks and fresh cloud persistence/source-hash checks passed. Seven exact checkpoints and three quarantines remain unchanged; no provider calls or worker execution. Temporary private S3 archive/bucket and exact-object instance permission removed. Local app servers remain stopped.

Evidence: [results](../../docs/evidence/AWS-UPDATE-20261019-02/RESULTS.md), [public acceptance](../../docs/evidence/AWS-UPDATE-20261019-02/public-proof.json), [cloud persistence](../../docs/evidence/AWS-UPDATE-20261019-02/cloud-persistence-proof.json).

## Rollback from release02

Only choose this after reviewing any subsequent cloud writes. It restores release01's earlier graph snapshot; it does not merge newer records. Release02 and its volume remain retained.

```sh
systemctl stop civicly-frontend civicly-api
cd /opt/civicly
docker compose stop
unlink /opt/civicly
ln -s /opt/civicly-releases/update-20261019-01 /opt/civicly
cd /opt/civicly
docker compose up -d --wait --wait-timeout 120
systemctl start civicly-api civicly-frontend
```

This is deployment acceptance; B10/B20/B-END and recovery/monitoring obligations remain open. Next:public human walkthrough, then separately continued recovery reconciliation. Historical notes below are retained unchanged.

---

# Current update — verified on 19 October 2026

The existing [public demo](https://civicly-13-55-205-208.sslip.io) now serves the current frontend and retained graph revision1056: three completed investigations, five completed work orders, three verified work orders and zero pending approvals. Waterlogging and the second road repair now show exact approval, completed work, separate follow-up and memory. Waste keeps its TOKEN_BUDGET pause; three recovery cases remain blocked. Recent readable labels, centered scenario dialog, Next-section buttons and inline case chooser are verified on the public site.

Active release: `/opt/civicly-releases/update-20261019-01`, reached through `/opt/civicly`. Previous app/runtime: `/opt/civicly-releases/previous-update-20261019-01`. Active Docker Compose project: `civicly-update-20261019-01`, container `civicly-update-20261019-01-falkordb-1`. Old project `civicly` is stopped with its volumes retained. All databases remain loopback-only. Services retain the existing systemd names, public hostname, EC2 instance, TLS configuration, account plan and allocated EBS capacity.

`update-app.sh` stages the build and a fresh database volume before a guarded cutover. It compares frozen dependency lockfiles before reusing installed libraries, preserves the hosted auth/session DB through SQLite backup, validates17snapshotkeys including six primary graphs plus the SDK ontology graph, compares exact quarantine dump hashes, persists ACLs before container recreation and checks application readiness. Explicit phase-resume modes never restore over a populated database. A rollback trap restores the old release/volume if cutover readiness fails; that failure path was not deliberately injected on the public host.

Verification: [public proof](../../docs/evidence/AWS-UPDATE-20261019/public-proof.json), [persistent ACL/quarantine and approval proof](../../docs/evidence/AWS-UPDATE-20261019/cloud-persistence-proof.json), [results](../../docs/evidence/AWS-UPDATE-20261019/RESULTS.md). Public HTTPS, automatic login, source hashes, three completed cases, graph/trace/procedures/memory, SSE, cross-origin and revoked-session denials passed. No provider request or worker was started. Temporary encrypted private S3 transfer storage and its exact-object instance-role grant were removed after verified download. Existing private snapshots/archives and both old/new EC2 database volumes remain available for recovery.

## Reversible manual rollback for this update

Run only as an explicitly chosen operator rollback via SSM, after assessing any new cloud writes. This restores the older hosted snapshot; it does not merge later records. The new volume/release remain retained.

```sh
systemctl stop civicly-frontend civicly-api
cd /opt/civicly
docker compose stop
unlink /opt/civicly
ln -s /opt/civicly-releases/previous-update-20261019-01 /opt/civicly
cd /opt/civicly
docker compose up -d --wait --wait-timeout 120
systemctl start civicly-api civicly-frontend
```

No new EC2 instance, paid model run or permanent AWS staging storage was added. Extra Docker release data uses the existing allocated EBS disk; the original ongoing hosting charges still apply. This update is deployment acceptance, not full B10/B20/B-END completion. Exact next: human public walkthrough; resume the separately reviewed clean-waste workflow later. Historical deployment notes below remain intact.

---

# Current deployment — verified on 18 October 2026

Civicly is live at **https://civicly-13-55-205-208.sslip.io** on instance `i-00e332036cd609ff0` in `ap-southeast-2`. The human approved the configuration and approximately **US$2.87/day before credits** (US$87.36 for a 730-hour month). No upgrade from the Free plan occurred.

Public HTTPS, automatic analyst login, dashboard, completed road case, graph, trace, procedures, saved memory and SSE frames passed actual network checks. All checks passed again after a full EC2 reboot. Restricted database accounts survived a container recreation and the reboot. AOF and `users.acl` are on the encrypted persistent volume. Only ports 80/443 are public; administration is through Systems Manager. The temporary S3 archive, bucket and exact-object access policy were removed after installation.

Fresh cloud official and domain MCP discovery/read calls passed. The procedure lookup returned three cited excerpts with `PARTIAL` and its synthetic/proposed reservation retained. This is an operator smoke check, not autonomous model selection. No Gemini requests or automatic paid worker were started. Existing pending approvals, token-budget stops and broader B10/B20/B-END acceptance gaps remain.

Verification: `docs/evidence/AWS-DEPLOY-{public-proof,post-reboot-proof,reboot-readiness,MCP-proof,restore-proof,https-proxy-proof}.json` and `AWS-DEPLOY-browser.png`. The original failed installation (missing C++ compiler), SSE buffering failure and overly strict MCP smoke assertion are retained in the task history and corrected. `bootstrap.sh` now installs build-essential/Python headers; Caddy excludes SSE from compression and requests uncompressed upstream responses. `compose.persistent-acl.yaml` is installed as the host's root `compose.override.yaml` only after the initial ACL export.

Actual cloud versions: Ubuntu 24.04, Python 3.12.3, Node 22.23.3, Docker 29.9.1, Compose 5.6.0, Caddy 2.6.2, pinned FalkorDB 6.0.2 amd64 image. Application Python/Node dependencies remain locked.

## Human verification

1. Open the public URL and confirm **Demo connected**.
2. Open `/investigations?investigation=INV-B09-b9d4d66e130ed348c4f6a50e9d66a891`; inspect the recorded graph, trace, completed work and outcome memory. Municipal field actions are explicitly synthetic.
3. Confirm the event stream connects. Read the source reservations and pending cases rather than treating deployment as full backend acceptance.

The server remains running for the demo. Stop/start can change its dynamic public IPv4 address and temporary hostname; a reboot does not. Before stopping, retain data and plan to update Caddy plus `CIVICLY_PUBLIC_ORIGIN` after start. The protected 30 GB EBS disk is retained on termination and continues storage charges until explicitly removed.

## Administration and future recovery

Use Systems Manager Run Command/Session Manager for this exact instance. Services are `civicly-api`, `civicly-frontend`, `caddy` and the Docker `civicly-falkordb-1` container. App directory `/opt/civicly`; private host `/opt/civicly/.runtime/aws-host.json`; API/frontend bind to 127.0.0.1:8010/3100. `docker compose` at the app root includes the generated persistent-ACL override. Never rerun fresh-only restoration on a populated database. Local private snapshots and source remain in ignored `.runtime/aws-deploy/`. Cloud changes after migration are independent of the retained local demo.

Existing UI limitation observed during browser verification: some investigation-list category badges do not match their linked incident category; the incident API and category summary retain the actual values. This pre-existing presentation issue was not changed as part of hosting.

Exact next task: human cloud demo walkthrough; optional separately authorized bounded live-worker verification or existing backend B21 work after review.

The preparation notes below are historical and superseded by the verified status above.

---

# Civicly AWS demo deployment — prepared, not launched

Task AWS-DEPLOY, 18 October 2026. Human requested Sydney (`ap-southeast-2`), the new AWS experience, a temporary hostname and HIGH guidance. This deploys the retained demonstrator, not a claim of full B10/B20/B-END acceptance.

## Reviewable launch configuration

`launch-plan.json` records exact instance/AMI/VPC/subnet, encrypted 30GB gp3 disk, SSM-only administration and ports80/443. No inbound SSH, DB, Browser or MCP. Official pinned FalkorDB image index supports amd64 and arm64. Candidate c7i-flex.large (2vCPU/4GiB) is marked FreeTierEligible by actual DescribeInstanceTypes. t4g.medium is not eligible on this Free plan. Source Docker DB uses2.184GiB including unrelated review graphs; only six required graphs and their durable keys are migrated. Four GiB swap cushions installation/build peaks, not a memory-performance guarantee.

Actual FreeTier API: FREE/ACTIVE,100USDremainingcredit. Public on-demand PriceList: compute$0.11072/h,IPv4$0.005/h,gp3$0.096/GB-month. Scripted estimate$87.36/730-hourmonth or$2.87/day, before credits, tax, transfer, backups or Gemini. Charges consume credits; this is not indefinitely free hosting. No upgrade to Paid is authorized. EBS retained on termination for recovery and continues consuming storage credit until explicitly removed. Termination protection is enabled. IAM role will have SSMCore plus temporary exact-object deployment read; deployment S3 object will be private,encrypted,temporary.

The retrieved AWS EC2 launch procedure explicitly requires presenting proposed defaults for confirmation. No cloud resources may be created until the human confirms this launch plan/cost. Workload=web-server/demo,environment=development. Existing defaultVPC publicsubnet2a routes throughIGW,4091freeIPs; AMI Canonical Ubuntu24.04amd64 ami-0c4c0d31978150116. These facts must be rechecked if delayed. No ALB/NAT/EKS/managed database is needed for this bounded demonstrator.

## Prepared artifacts and migration

- `bootstrap.sh`: Ubuntu dependencies,Docker,Node22,Caddy,SSMAgent,swap,unprivilegedciviclyuser. No embedded secrets or application/model startup.
- `compose.override.yaml`: restart policy, Browserdisabled,graphhealthcheck; inherited DBbinding remains127.0.0.1.
- `civicly-api.service`, `civicly-frontend.service`: unprivileged service supervision,loopbackAPI8010/frontend3100.
- `Caddyfile.template`: automaticHTTPS for `civicly-<IPv4-with-dashes>.sslip.io`,streamingproxy toNext,no publicdirectAPI. Temporary DNS/certificate issuance must be tested; hostname changes when dynamicIPv4 changes afterstop/start.
- `scripts/aws_demo_snapshot.py`: fresh-onlyprivateexport,sourcewriterfence,binarysafeRedisDUMP,hashes,selectedgraphs+quarantines,exactACLs,SQLitebackup,privatehost/analystconfig. Restore refusesnonemptyDB and checksallpayloadhashesbeforewrites. Restore is infrastructure import,never an agent tool. A failed partial restore requires retained diagnostics/fresh empty proof target,not blindreplace.
- `install-app.sh`: installs frozenPython/Node dependencies,restoresonlyfreshdatabase,buildsfrontend,configuresrealhostname,startsAPI/frontend/Caddy. No resets/seeding,approval changes,liveGemini or automaticworker. Original source/checkpoint IDs and budgets remain; absolute paths translated only in a new aws-host.json. Original privatehostfiles/compatibility proofs remain historical; new cloud liveexecution requires separately verifiedsource/configauthorization. Do not run an offline scripted worker on these live threads.

Private export lives in ignored `.runtime/aws-deploy/snapshot-04`; failedpreparationattempts01/02 and successful03 retained. Never commit/upload it publicly or paste its contents. Sourcebundle must exclude `.env`,`.runtime`,dependencies,Gitmetadata and builds. Transfer privatebundle only to the authorized project over TLS with shortlivedsignedURLs/privateS3; no secrets inSSMparameters/userdata/publicevidence. Recreate privatefilepermissions and preserve spending/authSQLite backups. Existing localdemo remains intact; its writes must not be confused with the latercloudfork.

## Verification already executed

- `npm test` infrontend:81PASS,0FAIL/0SKIP,including two hosted-originsecuritytests. These are offline/fake-fetch tests,not cloudproof.
- `npm run typecheck`, `npm run build`:PASS;generatedAPIandcontractguardPASS59operations/55paths/185schemas.
- `backend/.venv/bin/python scripts/validate_blueprint.py` and `scripts/validate_handoff.py`:PASS;staticonly.
- `bash -n deploy/aws/bootstrap.sh deploy/aws/install-app.sh`:PASS;syntaxonly,not afreshUbuntuinstallproof.
- Realprivateexport+isolatedrestore:sixgraphs/17keys,PASSmatchingnodecounts,quarantinevalues,read-onlyallowedread/deniedwrite. `docs/evidence/AWS-DEPLOY-restore-proof.json` contains sanitizedresults. Proofcontainer separateport16379;sourceDB unchangedexcepttemporaryexportwriterlease.
- AWSRunInstancesDryRun returnedDryRunOperation;noinstancecreated. FirsterrorhandlerusedaClientErrornameunavailableinMCPsandbox;correctedhandlerpreservestheactualAWSresult. Dry-run doesnotreservecapacity orproveapplicationstartup.
- Initialexportsretained: decoded-keyincompatibility corrected withbinaryRedisconnection;relativepatherror corrected withresolvedhostpath. No sourcecaseupdates/providerrequests.

## Required cloud acceptance after approval

Create taggedSSMrole/securitygroup/private stagingstorage and exact instance; waitforSSM/cloud-init. Transfer source/privatebundle; checkits hashes and filepermissions. Install frozen dependencies and restore; start supervisedAPI/frontend/Caddy. Verify validHTTPS,automaticanalystsession,dashboard,allthreecategories,completedroadcase,graphpaths,trace,citations,memory andauthenticatedSSE throughthepublicproxy. Verify revoked/invalidsessions andunapprovedwritesremainblocked. Restartservices/container and re-readsameIDs/status/quarantines/checkpoint/memory; checkdurablevolume. No paidmodelcall isneededforinitialdeploymentacceptance; separately authorizedboundedliveproof mayfollow. Record actual instanceURL/resourceIDs/costs and retention/deletioninstructions. Never claimcloudreadybasedsolelyonprocessstartup.

Exact next task: AWS-DEPLOY launch+cloudverification of this reviewed package, after explicit configuration/cost confirmation. Remaining backendacceptance gates areunchanged.
