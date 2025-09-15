#!/usr/bin/env sh
set -e

# Prefer runtime override; fall back to any build-time value that exists
API="${RUNTIME_API_BASE_URL:-${REACT_APP_API_BASE_URL:-}}"

# Write runtime config for the SPA
mkdir -p /web/build
cat > /web/build/env.js <<EOF
window.__ENV = {
  API_BASE_URL: "${API}"
};
EOF

exec "$@"
