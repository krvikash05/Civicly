# Exact deployment checks

Task AWS-UPDATE-20261019-02. AWS operations used official AWS MCP call_boto3 APIs; no local AWS CLI execution. No model or worker calls.

Local:
- npm --prefix frontend test →120 PASS/0FAIL/0SKIP; frontend-tests.txt.
- make test-spec →both validators PASS; spec-tests.txt.
- bash -n deploy/aws/update-app.sh →PASS.
- PYTHONPATH=backend backend/.venv/bin/python scripts/aws_demo_snapshot.py export --destination .runtime/aws-update-20261019-02/private-snapshot --host-config .runtime/demo-presenter/run-01/host-rehearsal02.json →6graphs/17keys. Private snapshot/archive are ignored and must not be published.
- PYTHONPATH=backend backend/.venv/bin/python deploy/aws/verify_update.py --output docs/evidence/AWS-UPDATE-20261019-02/public-proof.json →public real checks PASS; public-verification-output.txt. Safe read/auth verification only; use a NEW output path to rerun.

AWS management:
- STS GetCallerIdentity; EC2 DescribeInstances; SSM DescribeInstanceInformation →existing Sydney instance running/Online. SSM read-only preflight39d2a833-6522-4eff-bad1-fbf5c05d01e5 →old revision1056, services active,13GiB available.
- Temporary S3 CreateBucket/PutPublicAccessBlock/PutBucketEncryption and exact-object IAM PutRolePolicy; HTTPS upload through900-second presigned PUT. EC2 uses existing instance role for download; no credentials or signed URL placed in SSM commands.
- SSM SendCommand d4a233e8-7ca6-4925-8382-e1f7d25b717e: SHA256-verified private download, fresh extraction, then CIVICLY_EXPECTED_OLD_REVISION=1056 bash deploy/aws/update-app.sh update-20261019-02. Success; exact output in cutover-command-result.json.
- SSM read-only persistence command1ff941de-ba68-4329-a056-81967ef90880 →cloud-persistence-proof.json. Seven exact saved checkpoint/recovery comparisons, native revision1148, source hashes, persistent ACL/AOF and unchanged provider ledger.
- IAM DeleteRolePolicy, S3 DeleteObject/DeleteBucket →transfer-cleanup.json.
- Actual browser public homepage/dialog/waste Work/Monitoring verification; screenshots retained.

Previous app and volume are retained. The rollback procedure in deploy/aws/README.md is an operator-only restoration of the older cloud fork, not a merge of later writes. Public rollback was not deliberately fault-injected.
