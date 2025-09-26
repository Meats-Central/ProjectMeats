#!/usr/bin/env bash
set -euo pipefail
host="$1"; user="$2"; key="$3"; shift 3
ssh -i <(printf '%s\n' "$key") -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$user@$host" "$@"
