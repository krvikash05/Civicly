#!/usr/bin/env bash
# Run as root AFTER securely uploading source + snapshot to /opt/civicly.
set -euo pipefail
cd /opt/civicly
test ! -e .runtime
cp -a private-snapshot/.runtime .runtime
cp private-snapshot/.env .env
cp private-snapshot/frontend/.env.local frontend/.env.local
chmod 600 .env frontend/.env.local
chown -R civicly:civicly /opt/civicly
sudo -u civicly make setup
sudo -u civicly npm ci --prefix backend/mcp_runtime --ignore-scripts --no-audit --no-fund
# Only the configured exact snapshot is restored. Never seed/reset the migrated source.
docker compose -f compose.yaml -f deploy/aws/compose.override.yaml up -d --wait --wait-timeout 120
sudo -u civicly env PYTHONPATH=backend backend/.venv/bin/python scripts/aws_demo_snapshot.py restore --directory /opt/civicly/private-snapshot
# ACL SETUSER rules are not part of AOF: persist them before any restart.
docker compose exec -T falkordb sh -c 'umask 077; redis-cli ACL LIST > /var/lib/falkordb/data/users.acl; chown --reference=/var/lib/falkordb/data/appendonlydir /var/lib/falkordb/data/users.acl'
# A root override keeps ordinary future docker compose/make up invocations safe.
cp deploy/aws/compose.persistent-acl.yaml compose.override.yaml
docker compose up -d --wait --wait-timeout 120
# Metadata is available only to host administration; no AWS credentials in the app.
TOKEN=$(curl -fsS -X PUT -H 'X-aws-ec2-metadata-token-ttl-seconds:60' http://169.254.169.254/latest/api/token)
DEMO_IP=$(curl -fsS -H "X-aws-ec2-metadata-token:$TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4)
DEMO_HOSTNAME="civicly-${DEMO_IP//./-}.sslip.io"
export DEMO_HOSTNAME
sudo --preserve-env=DEMO_HOSTNAME -u civicly backend/.venv/bin/python - <<'PY'
from pathlib import Path
import os
path=Path('frontend/.env.local')
lines=[x for x in path.read_text().splitlines() if not x.startswith(('CIVICLY_PUBLIC_ORIGIN=','CIVICLY_API_ORIGIN='))]
lines+=['CIVICLY_PUBLIC_ORIGIN=https://'+os.environ['DEMO_HOSTNAME'],'CIVICLY_API_ORIGIN=http://127.0.0.1:8010']
path.write_text('\n'.join(lines)+'\n');path.chmod(0o600)
PY
sudo -u civicly npm ci --prefix frontend --no-audit --no-fund
(cd frontend && sudo -u civicly npm run build)
install -m 0644 deploy/aws/civicly-api.service /etc/systemd/system/civicly-api.service
install -m 0644 deploy/aws/civicly-frontend.service /etc/systemd/system/civicly-frontend.service
sed "s/DEMO_HOSTNAME/${DEMO_HOSTNAME}/g" deploy/aws/Caddyfile.template > /etc/caddy/Caddyfile
caddy validate --config /etc/caddy/Caddyfile
systemctl daemon-reload
systemctl enable --now civicly-api civicly-frontend
systemctl enable --now caddy
printf 'Application processes started; HTTPS/readiness still require verification.\n'
