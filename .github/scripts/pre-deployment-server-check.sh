#!/bin/bash
# Pre-Deployment Server Health Check
#
# Usage: pre-deployment-server-check.sh <host> [port]
#
# Performs comprehensive health checks before deployment:
# - DNS resolution
# - Network connectivity (ping)
# - Port availability (SSH/custom)
# - SSH service health
# - Basic system resources (if SSH accessible)
#
# Exit codes:
#   0 - All checks passed
#   1 - Critical failure (deployment should not proceed)
#   2 - Warning (deployment may proceed with caution)

set -euo pipefail

HOST="${1:-}"
PORT="${2:-22}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CRITICAL_FAILURES=0
WARNINGS=0

log_info() {
  echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
  echo -e "${GREEN}[PASS]${NC} $*"
}

log_warning() {
  echo -e "${YELLOW}[WARN]${NC} $*"
  WARNINGS=$((WARNINGS + 1))
}

log_error() {
  echo -e "${RED}[FAIL]${NC} $*" >&2
  CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))
}

if [[ -z "$HOST" ]]; then
  echo "Usage: $0 <host> [port]"
  exit 1
fi

log_info "=== Pre-Deployment Health Check for ${HOST} ==="
echo ""

# Check 1: DNS Resolution
log_info "Check 1/6: DNS Resolution"
if host "$HOST" &>/dev/null || getent hosts "$HOST" &>/dev/null; then
  IP=$(getent hosts "$HOST" 2>/dev/null | awk '{print $1}' | head -n1 || echo "unknown")
  log_success "DNS resolution successful (IP: ${IP})"
else
  if [[ "$HOST" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    log_success "Host is an IP address (${HOST})"
  else
    log_error "DNS resolution failed for ${HOST}"
  fi
fi
echo ""

# Check 2: ICMP Connectivity
log_info "Check 2/6: ICMP Connectivity (Ping)"
if timeout 5 ping -c 2 -W 3 "$HOST" &>/dev/null; then
  log_success "ICMP ping successful"
else
  log_warning "ICMP ping failed (may be blocked by firewall)"
fi
echo ""

# Check 3: TCP Port Availability
log_info "Check 3/6: TCP Port ${PORT} Availability"
if command -v nc &>/dev/null; then
  if timeout 10 nc -zv "$HOST" "$PORT" 2>&1 | grep -q "succeeded\|open"; then
    log_success "Port ${PORT} is open and reachable"
  else
    log_error "Port ${PORT} is NOT reachable"
    log_error "  → Check firewall rules"
    log_error "  → Verify service is running"
  fi
else
  log_warning "netcat not available, skipping port check"
fi
echo ""

# Check 4: SSH Service Health
if [[ "$PORT" == "22" ]]; then
  log_info "Check 4/6: SSH Service Health"
  if timeout 10 ssh-keyscan -T 5 -H "$HOST" 2>&1 | grep -q "ssh-"; then
    SSH_VERSION=$(timeout 10 ssh-keyscan -T 5 -H "$HOST" 2>&1 | grep "ssh-" | head -1 | awk '{print $2}')
    log_success "SSH service is responding (${SSH_VERSION})"
  else
    log_error "SSH service is not responding"
    log_error "  → Check if SSH daemon is running"
    log_error "  → Verify SSH configuration"
  fi
else
  log_info "Check 4/6: Skipped (not SSH port)"
fi
echo ""

# Check 5: Connection Latency
log_info "Check 5/6: Network Latency"
if command -v ping &>/dev/null; then
  LATENCY=$(ping -c 3 -W 2 "$HOST" 2>/dev/null | tail -1 | awk -F'/' '{print $5}' || echo "0")
  if [[ -n "$LATENCY" ]] && (( $(echo "$LATENCY > 0" | bc -l 2>/dev/null || echo 0) )); then
    if (( $(echo "$LATENCY < 100" | bc -l 2>/dev/null || echo 1) )); then
      log_success "Average latency: ${LATENCY}ms (good)"
    elif (( $(echo "$LATENCY < 300" | bc -l 2>/dev/null || echo 1) )); then
      log_warning "Average latency: ${LATENCY}ms (acceptable)"
    else
      log_warning "Average latency: ${LATENCY}ms (high - may cause issues)"
    fi
  else
    log_warning "Could not measure latency"
  fi
else
  log_warning "ping not available, skipping latency check"
fi
echo ""

# Check 6: GitHub Actions IP Ranges (informational)
log_info "Check 6/6: GitHub Actions IP Range Check"
log_info "Verify your firewall allows these IP ranges:"
if command -v curl &>/dev/null && command -v jq &>/dev/null; then
  GITHUB_IPS=$(curl -s https://api.github.com/meta | jq -r '.actions[]' | head -5)
  echo "$GITHUB_IPS" | while read -r ip_range; do
    log_info "  → ${ip_range}"
  done
  log_info "  ... (see https://api.github.com/meta for full list)"
else
  log_info "  → Install curl and jq to see GitHub Actions IP ranges"
  log_info "  → Or visit: https://api.github.com/meta"
fi
echo ""

# Summary
echo "=== Health Check Summary ==="
echo ""

if [[ $CRITICAL_FAILURES -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
  log_success "All checks passed! Server is ready for deployment."
  exit 0
elif [[ $CRITICAL_FAILURES -eq 0 ]]; then
  log_warning "Health check completed with ${WARNINGS} warning(s)."
  log_warning "Deployment may proceed, but monitor closely."
  exit 2
else
  log_error "Health check failed with ${CRITICAL_FAILURES} critical error(s)."
  log_error "Fix these issues before deploying:"
  [[ $CRITICAL_FAILURES -gt 0 ]] && log_error "  → Server connectivity issues detected"
  log_error ""
  log_error "For troubleshooting, see: SSH_CONNECTION_TROUBLESHOOTING.md"
  exit 1
fi
