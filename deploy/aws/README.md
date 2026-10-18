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
