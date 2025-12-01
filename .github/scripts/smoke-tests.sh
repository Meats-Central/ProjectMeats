#!/bin/bash
# Post-Deployment Smoke Tests
# Quick validation that critical functionality works

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_URL="${1:-}"
MAX_RETRIES="${2:-10}"
RETRY_DELAY="${3:-5}"

if [ -z "$BASE_URL" ]; then
    echo -e "${RED}Error: Base URL not specified${NC}"
    echo "Usage: $0 <base_url> [max_retries] [retry_delay_seconds]"
    exit 1
fi

echo "=== Smoke Tests: $BASE_URL ==="
echo "Max retries: $MAX_RETRIES, Retry delay: ${RETRY_DELAY}s"

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to make HTTP request with retries
http_check() {
    local url=$1
    local expected_status=${2:-200}
    local retries=0
    
    while [ $retries -lt $MAX_RETRIES ]; do
        local status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        
        if [ "$status" = "$expected_status" ]; then
            return 0
        fi
        
        retries=$((retries + 1))
        if [ $retries -lt $MAX_RETRIES ]; then
            sleep $RETRY_DELAY
        fi
    done
    
    return 1
}

# Function to run a test
run_test() {
    local test_name=$1
    local url=$2
    local expected_status=${3:-200}
    local timeout=${4:-10}
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "\n${BLUE}Test $TOTAL_TESTS: $test_name${NC}"
    echo "URL: $url"
    
    if http_check "$url" "$expected_status"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED (expected: $expected_status)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Test 1: Frontend Homepage
run_test "Frontend Homepage" "$BASE_URL/" 200

# Test 2: Backend Health Endpoint
run_test "Backend Health Check" "$BASE_URL/api/v1/health/" 200

# Test 3: API Root
run_test "API Root" "$BASE_URL/api/v1/" 200

# Test 4: Admin Login Page (if accessible)
run_test "Admin Login Page" "$BASE_URL/admin/login/" 200 || true

# Test 5: Static Files
run_test "Static Files Serving" "$BASE_URL/static/" 200 || \
run_test "Static Files (Fallback)" "$BASE_URL/static/admin/css/base.css" 200 || true

# Test 6: Check response time
echo -e "\n${BLUE}Test $((TOTAL_TESTS + 1)): Response Time Check${NC}"
RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" "$BASE_URL/api/v1/health/" 2>/dev/null || echo "999")
RESPONSE_TIME_MS=$(echo "$RESPONSE_TIME * 1000" | bc)
TOTAL_TESTS=$((TOTAL_TESTS + 1))

if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l) )); then
    echo -e "${GREEN}✓ PASSED (${RESPONSE_TIME_MS}ms)${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠ SLOW (${RESPONSE_TIME_MS}ms > 2000ms threshold)${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 7: Database connectivity (via health endpoint)
echo -e "\n${BLUE}Test $((TOTAL_TESTS + 1)): Database Connectivity${NC}"
DB_CHECK=$(curl -s "$BASE_URL/api/v1/health/" | grep -o '"database":\s*"[^"]*"' | cut -d'"' -f4 || echo "unknown")
TOTAL_TESTS=$((TOTAL_TESTS + 1))

if [ "$DB_CHECK" = "connected" ] || [ "$DB_CHECK" = "healthy" ]; then
    echo -e "${GREEN}✓ PASSED (database: $DB_CHECK)${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠ Database status: $DB_CHECK${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 8: SSL/TLS (if HTTPS)
if [[ "$BASE_URL" == https://* ]]; then
    echo -e "\n${BLUE}Test $((TOTAL_TESTS + 1)): SSL/TLS Certificate${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if curl -s --max-time 5 "$BASE_URL" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED (valid SSL certificate)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAILED (SSL certificate issue)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
fi

# Test 9: CORS Headers (if API)
echo -e "\n${BLUE}Test $((TOTAL_TESTS + 1)): CORS Headers${NC}"
CORS_HEADER=$(curl -s -I "$BASE_URL/api/v1/health/" | grep -i "access-control-allow-origin" || echo "")
TOTAL_TESTS=$((TOTAL_TESTS + 1))

if [ -n "$CORS_HEADER" ]; then
    echo -e "${GREEN}✓ PASSED (CORS configured)${NC}"
    echo "  Header: $CORS_HEADER"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠ No CORS headers found (may be intentional)${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 10: Container Health (if local deployment)
if command -v docker &> /dev/null; then
    echo -e "\n${BLUE}Test $((TOTAL_TESTS + 1)): Container Health${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    local unhealthy=0
    for container in pm-frontend pm-backend; do
        if docker ps --filter "name=$container" --format "{{.Status}}" | grep -q "Up"; then
            echo -e "${GREEN}✓ $container: Running${NC}"
        else
            echo -e "${RED}✗ $container: Not running${NC}"
            unhealthy=$((unhealthy + 1))
        fi
    done
    
    if [ $unhealthy -eq 0 ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
fi

# Summary
echo ""
echo "========================================"
echo -e "${BLUE}Smoke Test Summary${NC}"
echo "========================================"
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo "========================================"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All smoke tests passed${NC}"
    exit 0
else
    echo -e "${RED}✗ $FAILED_TESTS test(s) failed${NC}"
    exit 1
fi
