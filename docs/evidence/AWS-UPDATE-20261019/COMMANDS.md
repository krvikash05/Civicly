# Executed commands and results

- `aws login --profile civicly`: refreshed the expired session after explicit human confirmation.
- AWS CLI reads: confirmed the existing instance, SSM connectivity and exact instance role.
- `PYTHONPATH=backend backend/.venv/bin/python scripts/aws_demo_snapshot.py export --destination .runtime/aws-update-20261019/private-snapshot --host-config .runtime/demo-presenter/run-01/host-rehearsal02.json`: private fresh snapshot exported successfully.
- Created a source/private archive and verified SHA-256. Transferred through a private encrypted S3 bucket with public access blocked and only exact-object read access for the existing instance role. The instance downloaded and verified it. Temporary object, bucket and grant were removed afterward.

## SSM command history

| Command ID | Result |
|---|---|
| `3f450ec7-f701-4cb8-be91-312981269f3c` | Read-only preflight stopped at an incorrect lockfile path. |
| `36858f59-aca2-408e-9c81-0e81611fcff7` | Corrected preflight passed. |
| `3e86095f-d25b-4cde-a094-eb5bd7a9e47b` | Staging build failed on parent directory traversal permissions; live app unchanged. |
| `b3d72de3-8abd-4065-8b4c-035c246637a5` | Build and fresh restore passed; ontology graph count assertion stopped before cutover. |
| `a2d6d1aa-ba9a-4bfb-b499-77c40af2df27` | Corrected restored-stage validation, readiness and cutover passed; no second import. |

## Verification

```sh
backend/.venv/bin/python deploy/aws/verify_update.py --url http://127.0.0.1:3100 --output /tmp/civicly-local-proof.json
backend/.venv/bin/python deploy/aws/verify_update.py --output /tmp/civicly-public-proof.json
bash -n deploy/aws/update-app.sh
python3 -m py_compile deploy/aws/verify_update.py
make test-spec
```

Both real HTTP verification runs passed. The public run was corrected to send the required hosted Origin header on logout; cross-origin denial remained intact. Final remote checks passed for source hashes, three approved plans, exact quarantine values, persistent ACLs, active services and zero new provider requests. Actual browser checks and screenshots cover the public workflow and recent frontend changes.

Private SSM payloads, archives and configuration are intentionally excluded. Reuse the read-only verifier; do not replay fresh restoration or installation against populated targets. No full backend regression, EC2 reboot, paid model call or worker execution was performed for this update.
