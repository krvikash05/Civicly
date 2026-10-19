# Actual deployment commands

AWS operations used official AWS MCP call_boto3; no local AWS CLI.
- DescribeInstanceInformation: target Online.
- Preflight SendCommand84c44998-cf48-46f2-b031-effc544fde5e: existing release02; API/frontend/Caddy active;13GiB disk free; locked frontend dependencies unchanged.
- Stage directory01e1ecb1-3517-46e8-a029-87f05689a144; seven source-fragment SendCommands listed in transfer-commands.json; all Success.
- First build9d8e56a2-d12a-4b3b-8a51-6aff5cbed659: staging symlink restriction; diagnosticsa58e388b-7524-42e4-8de9-90819f453f3d.
- Corrected build3f042760-72ef-4d00-aa00-168832fa2739: copied locked dependencies locally, npm --prefix frontend run build PASS.
- Frontend-only cutover8edd3460-4812-4bbb-b552-1a7309cf9eeb: new WorkingDirectory drop-in, daemon-reload, frontend restart, actual headline HTTP check, backend PID unchanged.
- Source/service proofe5543a3f-5651-4129-a277-46d35146eebd: all70source hashes match, frontend/API/Caddy active.
- Local npm --prefix frontend test and make test-spec PASS.
- Before/after: PYTHONPATH=backend backend/.venv/bin/python deploy/aws/verify_update.py --output docs/evidence/AWS-UI-20261019-01/public-{before,after}.json (actual separate paths); public real checks PASS.
- Exact staged scripts remain in ignored .runtime/aws-ui-20261019-01/stage-build.sh and cutover.sh; both bash -n PASS. Archive/front-end manifest excludes private runtime/configuration.
- Public browser screenshots and read-only checks described in RESULTS.md.
