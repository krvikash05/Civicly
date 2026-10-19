# Changed paths

Deployment code: deploy/aws/update-app.sh (hosted-source revision guard before cutover); deploy/aws/verify_update.py (latest six-order/MONITORING waste expectations and exclusive evidence output).
Documentation: deploy/aws/README.md, docs/evidence/AWS-UPDATE-20261019-02/.
Append-only trackers: decision.md, flow.md, implementation_status.md, test_log.md, blockers.md, task_board.md.

Existing frontend/backend working-tree changes were packaged for deployment without rewriting their source or staging unrelated files. Private snapshots, transfer files, script and manifests remain under ignored .runtime/aws-update-20261019-02; never publish them. EC2 release02/current symlink, separate new persistent database volume and existing supervised processes updated; previous release01 and older releases/volumes retained. Local app servers remain stopped. No Git commit/push.
