#!/bin/bash
# SSH Connection with Retry Logic and Diagnostics
# 
# Usage: ssh-connect-with-retry.sh <user> <host> <command>
#
# This script provides robust SSH connectivity with:
# - Pre-connection network diagnostics
# - Exponential backoff retry logic
# - Detailed error reporting
# - Graceful degradation

set -euo pipefail

USER="${1:-}"
HOST="${2:-}"
COMMAND="${3:-echo 'Connection successful'}"

# Configuration
MAX_RETRIES="${MAX_SSH_RETRIES:-3}"
INITIAL_TIMEOUT="${SSH_CONNECT_TIMEOUT:-30}"
MAX_TIMEOUT=90

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log with timestamp
log() {
  echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"
}

log_error() {
  echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $*" >&2
}

log_warning() {
  echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $*"
}

log_success() {
  echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $*"
}

# Validate inputs
if [[ -z "$USER" || -z "$HOST" ]]; then
  log_error "Usage: $0 <user> <host> [command]"
  exit 1
fi

log "Starting SSH connection attempt to ${USER}@${HOST}"
log "Max retries: ${MAX_RETRIES}, Initial timeout: ${INITIAL_TIMEOUT}s"

# Pre-flight checks
log "=== Running Pre-Flight Network Diagnostics ==="

# 1. DNS Resolution
log "Checking DNS resolution..."
if host "$HOST" &>/dev/null || getent hosts "$HOST" &>/dev/null; then
  log_success "DNS resolution successful for ${HOST}"
  IP_ADDR=$(getent hosts "$HOST" 2>/dev/null | awk '{print $1}' | head -n1 || echo "unknown")
  log "Resolved IP: ${IP_ADDR}"
else
  log_warning "DNS resolution failed for ${HOST} (may be IP address)"
fi

# 2. ICMP Ping Test (optional, may be blocked by firewall)
log "Testing ICMP connectivity (ping)..."
if ping -c 2 -W 3 "$HOST" &>/dev/null; then
  log_success "ICMP ping successful"
else
  log_warning "ICMP ping failed (firewall may block ICMP)"
fi

# 3. TCP Port 22 Connectivity Test
log "Testing TCP connectivity to port 22..."
if command -v nc &>/dev/null; then
  if timeout 10 nc -zv "$HOST" 22 2>&1 | grep -q "succeeded\|open"; then
    log_success "Port 22 is reachable via TCP"
  else
    log_error "Port 22 is NOT reachable via TCP"
    log_error "Possible causes:"
    log_error "  1. Server is offline or unreachable"
    log_error "  2. Firewall blocking port 22"
    log_error "  3. SSH service not running"
    log_error "  4. Network routing issue"
    exit 1
  fi
else
  log_warning "netcat (nc) not available, skipping port test"
fi

# 4. SSH Service Detection
log "Testing SSH service response..."
if timeout 10 ssh-keyscan -T 5 -H "$HOST" 2>&1 | grep -q "ssh-"; then
  log_success "SSH service is responding"
else
  log_warning "SSH service did not respond to ssh-keyscan"
fi

log "=== Pre-Flight Diagnostics Complete ==="
echo ""

# Main retry loop with exponential backoff
ATTEMPT=1
TIMEOUT=$INITIAL_TIMEOUT

while [ $ATTEMPT -le $MAX_RETRIES ]; do
  log "=== Attempt ${ATTEMPT}/${MAX_RETRIES} (timeout: ${TIMEOUT}s) ==="
  
  # Try SSH connection
  if sshpass -e ssh \
    -o StrictHostKeyChecking=yes \
    -o ConnectTimeout=${TIMEOUT} \
    -o ServerAliveInterval=10 \
    -o ServerAliveCountMax=3 \
    -o BatchMode=no \
    "${USER}@${HOST}" \
    "${COMMAND}"; then
    
    log_success "SSH connection successful on attempt ${ATTEMPT}"
    exit 0
  fi
  
  EXIT_CODE=$?
  log_error "SSH connection failed with exit code ${EXIT_CODE}"
  
  # Check if we should retry
  if [ $ATTEMPT -lt $MAX_RETRIES ]; then
    # Calculate exponential backoff delay using POSIX-compatible loop
    # Attempt 1: 1s, 2: 2s, 3: 4s, 4: 8s, 5: 16s
    DELAY=1
    i=1
    while [ $i -lt $ATTEMPT ]; do
      DELAY=$((DELAY * 2))
      i=$((i + 1))
    done
    [ $DELAY -gt 30 ] && DELAY=30  # Cap at 30 seconds
    
    log_warning "Retrying in ${DELAY} seconds..."
    sleep "$DELAY"
    
    # Increase timeout for next attempt (exponential backoff)
    TIMEOUT=$((TIMEOUT + 20))
    [ $TIMEOUT -gt $MAX_TIMEOUT ] && TIMEOUT=$MAX_TIMEOUT
    
    ATTEMPT=$((ATTEMPT + 1))
  else
    log_error "All ${MAX_RETRIES} connection attempts failed"
    break
  fi
done

# All retries exhausted
echo ""
log_error "=== SSH Connection Failed After ${MAX_RETRIES} Attempts ==="
log_error "Troubleshooting Steps:"
log_error "1. Verify server is online and accessible from the internet"
log_error "2. Check SSH service is running: sudo systemctl status ssh"
log_error "3. Verify port 22 is open: sudo ss -tlnp | grep :22"
log_error "4. Check firewall rules allow GitHub Actions IP ranges"
log_error "5. Verify credentials in GitHub Secrets are correct"
log_error "6. Check server logs: sudo tail -f /var/log/auth.log"
echo ""
log_error "GitHub Actions IP Ranges: https://api.github.com/meta"
log_error "See: SSH_CONNECTION_TROUBLESHOOTING.md for detailed guidance"

exit 1
