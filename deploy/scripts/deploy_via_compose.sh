#!/usr/bin/env bash
# Usage: deploy_via_compose.sh <host> <user> <key> <env> [<backend_image>] [<frontend_image>] <app_domain>
# Examples:
#   deploy_via_compose.sh dev.example.com deploy "$SSH_KEY" dev ghcr.io/meats-central-projectmeats-backend:sha ghcr.io/meats-central-projectmeats-frontend:sha dev.example.com
#   deploy_via_compose.sh uat.example.com deploy "$SSH_KEY" uat "" "" uat.example.com   # builds defaults from GITHUB_REPOSITORY/GITHUB_SHA

set -euo pipefail

# ---------- Args ----------
HOST="${1:?host required}"
USER="${2:?user required}"
KEY="${3:?ssh key required}"
ENV_NAME="${4:?env required: dev|uat|prod}"
BACK_ARG="${5:-}"
FRONT_ARG="${6:-}"
APP_DOMAIN="${7:?app domain required}"

# ---------- Helpers ----------
err() { printf >&2 "ERROR: %s\n" "$*"; }
info() { printf "==> %s\n" "$*"; }

# Normalize only the NAME (registry/repo), keep tag/digest as-is
normalize_image() {
  local img="$1"
  if [[ -z "$img" ]]; then
    echo ""
    return 0
  fi
  # split name:tag (or name@digest)
  local name tag sep
  if [[ "$img" == *@* ]]; then
    sep="@"; name="${img%@*}"; tag="${img#*@}"
    printf "%s@%s" "$(echo "$name" | tr '[:upper:]' '[:lower:]')" "$tag"
  elif [[ "$img" == *:* ]]; then
    sep=":"; name="${img%:*}"; tag="${img##*:}"
    printf "%s:%s" "$(echo "$name" | tr '[:upper:]' '[:lower:]')" "$tag"
  else
    # no tag; add :latest
    printf "%s:latest" "$(echo "$img" | tr '[:upper:]' '[:lower:]')"
  fi
}

# Build sane defaults if not provided (use ghcr.io/<owner>/<repo>-{backend,frontend}:<sha>)
build_default_images_if_needed() {
  local owner_lower repo_lowername sha base
  owner_lower="$(echo "${GITHUB_REPOSITORY_OWNER:-meats-central}" | tr '[:upper:]' '[:lower:]')"
  repo_lowername="$(echo "${GITHUB_REPOSITORY##*/}" | tr '[:upper:]' '[:lower:]')"
  sha="${GITHUB_SHA:-latest}"
  base="ghcr.io/${owner_lower}/${repo_lowername}"

  if [[ -z "$BACK_ARG" ]]; then
    BACK_ARG="${base}-backend:${sha}"
  fi
  if [[ -z "$FRONT_ARG" ]]; then
    FRONT_ARG="${base}-frontend:${sha}"
  fi
}

# ---------- Compute final image refs ----------
build_default_images_if_needed
BACKEND_IMAGE="$(normalize_image "$BACK_ARG")"
FRONTEND_IMAGE="$(normalize_image "$FRONT_ARG")"

info "Backend image: $BACKEND_IMAGE"
info "Frontend image: $FRONTEND_IMAGE"
info "Deploying to $ENV_NAME on $USER@$HOST (domain: $APP_DOMAIN)"

# ---------- SSH helper (inline; avoids dependency on _ssh.sh) ----------
ssh_exec() {
  local key_opt
  if [[ -n "${SSH_KEY_PATH:-}" && -f "${SSH_KEY_PATH}" ]]; then
    key_opt="-i ${SSH_KEY_PATH}"
  else
    # fallback to inline key (older behavior)
    key_opt="-i <(printf '%s\n' "$KEY")"
  fi

  # shellcheck disable=SC2029
  ssh ${key_opt} \
      -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
      "$USER@$HOST" "$@"
}

# ---------- Remote script ----------
# We pass environment variables explicitly to the remote shell to avoid relying on SSH env forwarding.
remote_env_prefix=$(
  printf "GITHUB_ACTOR=%q GITHUB_TOKEN=%q BACKEND_IMAGE=%q FRONTEND_IMAGE=%q APP_DOMAIN=%q ENV_NAME=%q" \
    "${GITHUB_ACTOR:-github-actions}" "${GITHUB_TOKEN:-}" \
    "$BACKEND_IMAGE" "$FRONTEND_IMAGE" "$APP_DOMAIN" "$ENV_NAME"
)

# shellcheck disable=SC2016
ssh_exec "${remote_env_prefix} bash -s" <<'REMOTE_EOF'
set -euo pipefail

APP_DIR=/opt/projectmeats
mkdir -p "$APP_DIR"/{env,logs}
cd "$APP_DIR"

# Docker login (GHCR). If token missing, skip but warn (pull may fail for private images).
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  echo "$GITHUB_TOKEN" | docker login ghcr.io -u "${GITHUB_ACTOR:-github-actions}" --password-stdin
else
  echo "WARN: GITHUB_TOKEN not provided; skipping docker login. Private GHCR pulls may fail." >&2
fi

# Write image.env for compose
cat > env/image.env <<EOV
IMAGE_TAG_BACKEND=${BACKEND_IMAGE}
IMAGE_TAG_FRONTEND=${FRONTEND_IMAGE}
EOV
chmod 600 env/image.env

# Pull images prior to up (faster fail if auth/refs wrong)
docker pull "${BACKEND_IMAGE}" || true
docker pull "${FRONTEND_IMAGE}" || true

# Compose up using environment-specific compose file
COMPOSE_FILE="docker-compose.${ENV_NAME}.yml"
if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "ERROR: $COMPOSE_FILE not found in $APP_DIR" >&2
  exit 2
fi

if [[ ! -f "env/${ENV_NAME}.env" ]]; then
  echo "ERROR: env/${ENV_NAME}.env not found in $APP_DIR" >&2
  exit 3
fi

docker compose -f "$COMPOSE_FILE" \
  --env-file "env/${ENV_NAME}.env" \
  --env-file "env/image.env" up -d

# Basic smoke checks (backend + frontend)
sleep 5
# Backend (direct container port via Traefik service port is internal, but a health endpoint on 8000 should be available)
if ! curl -fsS "http://127.0.0.1:8000/healthz" >/dev/null; then
  echo "WARN: backend local health check failed (http://127.0.0.1:8000/healthz)" >&2
fi
# Frontend public health (via domain routed through Traefik)
if ! curl -fsS "https://${APP_DOMAIN}/healthz" >/dev/null; then
  echo "WARN: frontend public health check failed (https://${APP_DOMAIN}/healthz)" >&2
fi

echo "Deploy complete for ${ENV_NAME} on ${APP_DOMAIN}"
REMOTE_EOF