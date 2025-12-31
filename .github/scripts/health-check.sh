#!/bin/bash
# Reusable health check script for ProjectMeats deployments
# Usage: ./health-check.sh <url> <max_attempts> <delay_seconds>
#
# Examples:
#   ./health-check.sh "http://localhost:8000/api/v1/health/" 20 5
#   ./health-check.sh "https://meatscentral.com/api/v1/health/" 15 10

set -euo pipefail

# Arguments
HEALTH_URL="${1:-}"
MAX_ATTEMPTS="${2:-20}"
DELAY="${3:-5}"

# Validation
if [ -z "$HEALTH_URL" ]; then
  echo "❌ ERROR: Health URL is required"
  echo "Usage: $0 <url> [max_attempts] [delay_seconds]"
  exit 1
fi

# Constants
CURL_FAILURE_CODE="000"
EXPECTED_CODE="200"

echo "=== Health Check Configuration ==="
echo "URL: $HEALTH_URL"
echo "Max attempts: $MAX_ATTEMPTS"
echo "Delay: ${DELAY}s"
echo "Expected HTTP code: $EXPECTED_CODE"
echo "=================================="

ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
  # Perform health check with timeout
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time 15 \
    --retry 0 \
    --fail-early \
    "$HEALTH_URL" 2>/dev/null)
  CURL_EXIT=$?
  
  # If curl failed (exit code != 0), set to failure code
  if [ $CURL_EXIT -ne 0 ]; then
    HTTP_CODE="$CURL_FAILURE_CODE"
  fi
  
  # Success condition
  if [ "$HTTP_CODE" = "$EXPECTED_CODE" ]; then
    echo "✓ Health check PASSED (HTTP $HTTP_CODE) on attempt $ATTEMPT/$MAX_ATTEMPTS"
    exit 0
  fi
  
  # Failure condition (max attempts reached)
  if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "✗ Health check FAILED after $MAX_ATTEMPTS attempts"
    echo "   Last HTTP code: $HTTP_CODE"
    
    if [ "$HTTP_CODE" = "$CURL_FAILURE_CODE" ]; then
      echo "   Error: Network failure, DNS failure, or timeout"
      echo "   Possible causes:"
      echo "     - Service not running"
      echo "     - Firewall blocking connection"
      echo "     - DNS not resolving"
      echo "     - SSL/TLS handshake failure"
    else
      echo "   Error: HTTP $HTTP_CODE received (expected $EXPECTED_CODE)"
      echo "   Possible causes:"
      echo "     - Application error (500)"
      echo "     - Not found (404)"
      echo "     - Unauthorized (401/403)"
      echo "     - Redirect issue (301/302)"
    fi
    
    exit 1
  fi
  
  # Retry logic
  echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS: HTTP $HTTP_CODE (retrying in ${DELAY}s...)"
  sleep $DELAY
  ATTEMPT=$((ATTEMPT + 1))
done

# Should never reach here due to explicit exit in loop
echo "✗ Unexpected termination"
exit 1
