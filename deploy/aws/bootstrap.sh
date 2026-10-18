#!/usr/bin/env bash
# EC2 user data. Infrastructure only; no secrets and no application/agent startup.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl gnupg git make python3.12 python3.12-venv python3.12-dev build-essential python3-boto3 unzip
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
printf 'deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu noble stable\n' > /etc/apt/sources.list.d/docker.list
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
printf 'deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main\n' > /etc/apt/sources.list.d/nodesource.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin nodejs caddy
systemctl enable --now docker
systemctl stop caddy
systemctl disable caddy
# Swap cushions dependency installation/build peaks; EBS is encrypted.
if ! test -f /swapfile; then
  fallocate -l 4G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  printf '/swapfile none swap sw 0 0\n' >> /etc/fstab
fi
if ! id civicly >/dev/null 2>&1; then useradd --create-home --shell /bin/bash civicly; fi
install -d -m 0700 -o civicly -g civicly /opt/civicly
# Ubuntu AWS AMIs include SSM Agent; make its boot activation explicit.
systemctl enable --now snap.amazon-ssm-agent.amazon-ssm-agent.service
printf 'BOOTSTRAP_READY\n' > /var/lib/civicly-bootstrap-status
