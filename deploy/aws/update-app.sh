#!/usr/bin/env bash
# Staged update of the existing demo. Run from a fresh release directory as root.
# Retains the previous app and database volume. Never flushes a populated DB.
set -euo pipefail
RELEASE_ID=${1:?release id required}
[[ "$RELEASE_ID" =~ ^[a-z0-9-]+$ ]] || exit 2
RELEASE=$(pwd -P)
[[ "$RELEASE" == "/opt/civicly-releases/$RELEASE_ID" ]] || exit 2
OLD=$(readlink -f /opt/civicly)
PROJECT="civicly-$RELEASE_ID"
MODE=${2:-}
# The app account must traverse the parent; each release itself remains0700.
chmod 0711 /opt/civicly-releases
test -d "$OLD/backend/.venv"
test -f private-snapshot/manifest.json

# Frozen dependency equality is required before reusing installed libraries.
for lock in backend/uv.lock backend/mcp_runtime/package-lock.json frontend/package-lock.json; do
  cmp "$OLD/$lock" "$RELEASE/$lock"
done
if test -e .runtime; then
  # Explicit phase resumes preserve diagnostics and never restore into a used DB.
  [[ "$MODE" == --resume-prebuild || "$MODE" == --resume-restored ]]
  test ! -e .runtime/update-restore-proof.json
  test ! -e .runtime/update-readiness.json
  if [[ "$MODE" == --resume-prebuild ]]; then
    test -z "$(docker ps -aq --filter "label=com.docker.compose.project=$PROJECT")"
    mv .runtime/update-build.log .runtime/update-build-attempt-01.log
  else
    test -n "$(docker ps -q --filter "label=com.docker.compose.project=$PROJECT")"
    grep -q 'Compiled successfully' .runtime/update-build.log
  fi
else
  cp -a private-snapshot/.runtime .runtime
  cp private-snapshot/.env .env
  cp "$OLD/frontend/.env.local" frontend/.env.local
  chmod 600 .env frontend/.env.local
  cp -al "$OLD/backend/.venv" backend/.venv
  cp -al "$OLD/backend/mcp_runtime/node_modules" backend/mcp_runtime/node_modules
  cp -al "$OLD/frontend/node_modules" frontend/node_modules
fi
chown -R civicly:civicly "$RELEASE"
if [[ "$MODE" != --resume-restored ]]; then
sudo -u civicly npm --prefix frontend run build > .runtime/update-build.log 2>&1
printf 'STAGED_BUILD_PASS\n'

# Restore into a fresh, independently named volume on a temporary loopback port.
FALKORDB_PORT=16379 FALKORDB_BROWSER_PORT=16380 docker compose -p "$PROJECT" \
  -f compose.yaml -f deploy/aws/compose.override.yaml up -d --wait --wait-timeout 120
sudo -u civicly env PYTHONPATH=backend backend/.venv/bin/python scripts/aws_demo_snapshot.py \
  restore --directory "$RELEASE/private-snapshot" --port 16379
FALKORDB_PORT=16379 FALKORDB_BROWSER_PORT=16380 docker compose -p "$PROJECT" \
  -f compose.yaml -f deploy/aws/compose.override.yaml exec -T falkordb sh -c \
  'umask 077; redis-cli ACL LIST > /var/lib/falkordb/data/users.acl; chown --reference=/var/lib/falkordb/data/appendonlydir /var/lib/falkordb/data/users.acl'
cp deploy/aws/compose.persistent-acl.yaml compose.override.yaml
printf '\nCOMPOSE_PROJECT_NAME=%s\n' "$PROJECT" >> .env
chown civicly:civicly compose.override.yaml .env
fi

# Compare every restored key's existence and quarantine value before cutover.
sudo -u civicly backend/.venv/bin/python - <<'PY'
import hashlib,json
from pathlib import Path
import redis
r=redis.Redis(host='127.0.0.1',port=16379,socket_timeout=30)
m=json.loads(Path('private-snapshot/manifest.json').read_text())
assert all(r.exists(x['key']) for x in m['keys'])
actual={x.decode() if isinstance(x,bytes) else x for x in r.execute_command('GRAPH.LIST')}
assert set(m['graphs'])<=actual<=set(x['key'] for x in m['keys'])
for row in m['keys']:
    # SDK ontology is another graph, and telemetry is intentionally mutable.
    # Durable quarantine strings must match their exact original serialized value.
    if row['key'].endswith(':quarantine'):
        assert hashlib.sha256(r.dump(row['key'])).hexdigest()==row['sha256']
assert redis.Redis(host='127.0.0.1',port=16379,decode_responses=True).config_get('appendonly')['appendonly']=='yes'
Path('.runtime/update-restore-proof.json').write_text(json.dumps({'primary_graphs':len(m['graphs']),'total_graphs_including_sdk_ontology':len(actual),'keys':r.dbsize(),'all_expected_keys_present':True,'quarantine_values_preserved':True,'aof_enabled':True}))
print('STAGED_RESTORE_PASS')
PY

CUTOVER=0
SERVICES_STOPPED=0
rollback() {
  result=$?
  if [[ "$CUTOVER" == 1 ]]; then
    echo 'CUTOVER_FAILED_ROLLING_BACK'
    systemctl stop civicly-frontend civicly-api || true
    (cd "$RELEASE" && docker compose -p "$PROJECT" stop) || true
    if [[ -L /opt/civicly ]]; then unlink /opt/civicly; fi
    ln -s "$OLD" /opt/civicly
    (cd /opt/civicly && docker compose up -d --wait --wait-timeout 120) || true
    systemctl start civicly-api civicly-frontend || true
  elif [[ "$SERVICES_STOPPED" == 1 ]]; then
    systemctl start civicly-api civicly-frontend || true
  fi
  exit "$result"
}
trap rollback ERR
systemctl stop civicly-frontend civicly-api
SERVICES_STOPPED=1
# Refuse to replace graph records created on the hosted fork since preflight.
# Authentication sessions are backed up independently below.
if [[ -n "${CIVICLY_EXPECTED_OLD_REVISION:-}" ]]; then
  export OLD RELEASE
  PYTHONPATH="$OLD/backend" "$OLD/backend/.venv/bin/python" - <<'PY'
import json,os
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.demo_host.config import load
from app.active import load as active_load,active_scope
from app.graph.repository import GraphRepository
old=Path(os.environ['OLD']);host=load(old/'.runtime/aws-host.json');profile=active_load(host.profile)
with connect(Settings(_env_file=old/'.env')) as db,active_scope(profile):
    repo=GraphRepository(db,profile.graph)
    rows=repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.state,coalesce(m.repo_pending,''),m.repo_revision LIMIT 2")
    expected=int(os.environ['CIVICLY_EXPECTED_OLD_REVISION'])
    if rows!=[['READY','',expected]]:raise RuntimeError('HOSTED_SOURCE_CHANGED_SINCE_PREFLIGHT; preserve hosted records before updating')
    (Path(os.environ['RELEASE'])/'.runtime/update-old-source-check.json').write_text(json.dumps({'repository':rows,'expected_revision':expected,'hosted_writes_preserved':True}))
print('HOSTED_SOURCE_UNCHANGED_PASS')
PY
fi
# Keep the hosted authentication/session DB, rather than replacing cloud sessions.
export RELEASE
"$OLD/backend/.venv/bin/python" - <<'PY'
import json,os,sqlite3
from pathlib import Path
old=Path('/opt/civicly')
new=Path(os.environ['RELEASE'])
host=json.loads((old/'.runtime/aws-host.json').read_text())
relative=Path(host['auth_store']).relative_to(old)
target=new/relative
target.rename(target.with_name('auth-local-snapshot.sqlite3'))
with sqlite3.connect(f'file:{old/relative}?mode=ro',uri=True) as source,sqlite3.connect(target) as dest:source.backup(dest)
target.chmod(0o600)
PY
chown -R civicly:civicly .runtime
# After this point any failure restores the old application and old DB volume.
if [[ "$OLD" == /opt/civicly ]]; then
  OLD="/opt/civicly-releases/previous-$RELEASE_ID"
  test ! -e "$OLD"
  mv /opt/civicly "$OLD"
else
  unlink /opt/civicly
fi
CUTOVER=1
ln -s "$RELEASE" /opt/civicly
(cd "$OLD" && docker compose stop)
# Existing staged volume is retained while its container moves to production ports.
docker compose -p "$PROJECT" up -d --wait --wait-timeout 120
systemctl start civicly-api civicly-frontend
for check in $(seq 1 40); do
  if curl -fsS http://127.0.0.1:8010/api/v1/health/ready > .runtime/update-readiness.json \
     && curl -fsS http://127.0.0.1:3100/ > /dev/null; then break; fi
  sleep 2
done
backend/.venv/bin/python - <<'PY'
import json
from pathlib import Path
d=json.loads(Path('.runtime/update-readiness.json').read_text())['data']
assert d['status']=='ok' and all(v=='ready' for v in d['dependencies'].values()),d
print('APPLICATION_READINESS_PASS')
PY
trap - ERR
printf 'UPDATE_ACTIVE release=%s previous=%s project=%s\n' "$RELEASE" "$OLD" "$PROJECT"
