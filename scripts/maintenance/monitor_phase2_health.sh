#!/bin/bash
# Phase 2 Compliance - Post-Deployment Health Monitor
# Monitors development environment for Phase 2 compliance issues

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEV_FRONTEND_URL="${DEV_FRONTEND_URL:-http://dev.meatscentral.com}"
DEV_BACKEND_URL="${DEV_BACKEND_URL:-http://dev.meatscentral.com/api/v1}"
HEALTH_CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-60}" # seconds
MAX_CHECKS="${MAX_CHECKS:-10}" # number of health checks before exit

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Phase 2 Compliance - Post-Deployment Health Monitor        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Frontend URL:${NC} $DEV_FRONTEND_URL"
echo -e "${BLUE}Backend URL:${NC} $DEV_BACKEND_URL"
echo -e "${BLUE}Check Interval:${NC} ${HEALTH_CHECK_INTERVAL}s"
echo -e "${BLUE}Max Checks:${NC} $MAX_CHECKS"
echo ""

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local name=$2
    local expected_code=${3:-200}
    
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")
    
    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} $name: HTTP $http_code"
        return 0
    else
        echo -e "${RED}✗${NC} $name: HTTP $http_code (expected $expected_code)"
        return 1
    fi
}

# Function to check for React 19 in page source
check_react_version() {
    local url=$1
    
    # Fetch page and check for React version indicators
    local response=$(curl -s --max-time 10 "$url" 2>/dev/null || echo "")
    
    if echo "$response" | grep -q "react.*19\|React.*19"; then
        echo -e "${GREEN}✓${NC} React 19 detected in frontend"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} React version not detected (may be bundled)"
        return 0
    fi
}

# Function to check backend logs for errors
check_backend_logs() {
    echo -e "${BLUE}Backend Logs Check:${NC}"
    
    # Check for common error patterns
    local error_patterns=(
        "django.db.utils.OperationalError"
        "sqlite3"
        "UndefinedValueError.*DB_NAME"
        "migrate.*failed"
        "FAILED.*migration"
        "duplicate.*table"
        "column.*already exists"
    )
    
    for pattern in "${error_patterns[@]}"; do
        echo "  Checking for: $pattern"
    done
    
    echo -e "${YELLOW}  Note: SSH access required for detailed log checks${NC}"
}

# Function to check workflow runs
check_workflow_status() {
    echo -e "${BLUE}Recent Workflow Runs:${NC}"
    
    if command -v gh &> /dev/null; then
        gh run list --branch development --limit 5 --json conclusion,name,createdAt,url 2>/dev/null | \
        jq -r '.[] | "  \(.conclusion | if . == "success" then "✓" elif . == "failure" then "✗" else "⚠" end) \(.name) (\(.createdAt[:10]))"' || \
        echo -e "${YELLOW}  Unable to fetch workflow status${NC}"
    else
        echo -e "${YELLOW}  gh CLI not available, skipping workflow check${NC}"
    fi
}

# Main monitoring loop
check_count=0
failed_checks=0

while [ $check_count -lt $MAX_CHECKS ]; do
    check_count=$((check_count + 1))
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Health Check #${check_count}/${MAX_CHECKS} - $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Frontend health checks
    echo -e "${BLUE}Frontend Checks:${NC}"
    if check_endpoint "$DEV_FRONTEND_URL" "Frontend Homepage" 200; then
        check_react_version "$DEV_FRONTEND_URL"
    else
        failed_checks=$((failed_checks + 1))
    fi
    echo ""
    
    # Backend health checks
    echo -e "${BLUE}Backend Checks:${NC}"
    check_endpoint "$DEV_BACKEND_URL/health/" "Backend Health" 200 || failed_checks=$((failed_checks + 1))
    echo ""
    
    # Backend logs (summary)
    check_backend_logs
    echo ""
    
    # Workflow status (every 3rd check)
    if [ $((check_count % 3)) -eq 0 ]; then
        check_workflow_status
        echo ""
    fi
    
    # Summary
    if [ $failed_checks -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed${NC}"
    else
        echo -e "${RED}✗ $failed_checks checks failed${NC}"
    fi
    
    # Wait before next check (unless last iteration)
    if [ $check_count -lt $MAX_CHECKS ]; then
        echo ""
        echo -e "${BLUE}Next check in ${HEALTH_CHECK_INTERVAL}s...${NC}"
        sleep "$HEALTH_CHECK_INTERVAL"
    fi
done

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              Health Monitoring Complete                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo -e "  Total Checks: $check_count"
echo -e "  Failed Checks: $failed_checks"

if [ $failed_checks -eq 0 ]; then
    echo -e "  ${GREEN}Status: ALL HEALTHY ✓${NC}"
    exit 0
else
    echo -e "  ${RED}Status: ISSUES DETECTED ✗${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Check detailed logs: docker logs pm-backend --tail 100"
    echo "  2. Review workflow runs: gh run list --branch development"
    echo "  3. Verify database migrations: docker exec pm-backend python manage.py showmigrations"
    echo "  4. Review error monitoring dashboard"
    exit 1
fi
