#!/usr/bin/env bash
# Usage: deploy_via_compose.sh <host> <user> <key> <env> <backend_image> <frontend_image> <app_domain>
set -euo pipefail
HOST="$1"; USER="$2"; KEY="$3"; ENV="$4"; BACK_IMG="$5"; FRONT_IMG="$6"; DOMAIN="$7"

read -r -d '' REMOTE <<'EOS'
set -euo pipefail
APP_DIR=/opt/projectmeats
mkdir -p "$APP_DIR"/{env,logs}
cd "$APP_DIR"

# Write image tags for compose
: "${BACKEND_IMAGE:?missing}"; : "${FRONTEND_IMAGE:?missing}"
printf 'IMAGE_TAG_BACKEND=%s\n'  "$BACKEND_IMAGE"   > env/image.env
printf 'IMAGE_TAG_FRONTEND=%s\n' "$FRONTEND_IMAGE" >> env/image.env

# Pull images & (re)create
docker login ghcr.io -u "$GITHUB_ACTOR" -p "$GITHUB_TOKEN" || true
docker pull "$BACKEND_IMAGE" || true
docker pull "$FRONTEND_IMAGE" || true

docker compose -f "docker-compose.${ENV}.yml" --env-file "env/${ENV}.env" --env-file env/image.env up -d

# Basic smoke checks (backend + frontend)
sleep 5
curl -fsS "http://127.0.0.1:8000/healthz" >/dev/null
curl -fsS "https://${DOMAIN}/healthz" >/dev/null || true  # if frontend proxies /healthz
EOS

GITHUB_ACTOR="${GITHUB_ACTOR:-github-actions}" \
GITHUB_TOKEN="${GITHUB_TOKEN:-}" \
BACKEND_IMAGE="$5" FRONTEND_IMAGE="$6" \
"$(dirname "$0")/_ssh.sh" "$HOST" "$USER" "$KEY" "$REMOTE"
