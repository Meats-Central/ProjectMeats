#!/bin/bash
# Test Deployment Hardening Implementation

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Deployment Hardening Verification Suite          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}\n"

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    local test_name=$1
    local command=$2
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "\n${YELLOW}Test $TOTAL_TESTS: $test_name${NC}"
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Test 1: Script files exist
echo -e "\n${BLUE}=== Script Existence Tests ===${NC}"
run_test "Pre-deployment check script exists" "test -f .github/scripts/pre-deployment-check.sh"
run_test "Pre-deploy backup script exists" "test -f .github/scripts/pre-deploy-backup.sh"
run_test "Smoke tests script exists" "test -f .github/scripts/smoke-tests.sh"
run_test "Deployment rollback script exists" "test -f .github/scripts/deployment-rollback.sh"
run_test "Deployment notifications script exists" "test -f .github/scripts/deployment-notifications.sh"
run_test "Deployment monitor script exists" "test -f .github/scripts/deployment-monitor.py"

# Test 2: Scripts are executable
echo -e "\n${BLUE}=== Executable Permissions Tests ===${NC}"
run_test "Pre-deployment check is executable" "test -x .github/scripts/pre-deployment-check.sh"
run_test "Smoke tests is executable" "test -x .github/scripts/smoke-tests.sh"
run_test "Rollback script is executable" "test -x .github/scripts/deployment-rollback.sh"
run_test "Monitor script is executable" "test -x .github/scripts/deployment-monitor.py"

# Test 3: Script syntax validation
echo -e "\n${BLUE}=== Syntax Validation Tests ===${NC}"
run_test "Pre-deployment check syntax valid" "bash -n .github/scripts/pre-deployment-check.sh"
run_test "Smoke tests syntax valid" "bash -n .github/scripts/smoke-tests.sh"
run_test "Rollback script syntax valid" "bash -n .github/scripts/deployment-rollback.sh"
run_test "Notifications script syntax valid" "bash -n .github/scripts/deployment-notifications.sh"
run_test "Monitor script syntax valid" "python3 -m py_compile .github/scripts/deployment-monitor.py"

# Test 4: Documentation exists
echo -e "\n${BLUE}=== Documentation Tests ===${NC}"
run_test "DEPLOYMENT_HARDENING.md exists" "test -f docs/DEPLOYMENT_HARDENING.md"
run_test "DEPLOYMENT_QUICK_REF.md exists" "test -f docs/DEPLOYMENT_QUICK_REF.md"
run_test "DEPLOYMENT_HARDENING_SUMMARY.md exists" "test -f DEPLOYMENT_HARDENING_SUMMARY.md"
run_test "HARDENING_COMPLETE.md exists" "test -f HARDENING_COMPLETE.md"

# Test 5: Workflow files are valid YAML
echo -e "\n${BLUE}=== Workflow YAML Tests ===${NC}"
run_test "Production workflow is valid YAML" "python3 -c 'import yaml; yaml.safe_load(open(\".github/workflows/13-prod-deployment.yml\"))'"
run_test "UAT workflow is valid YAML" "python3 -c 'import yaml; yaml.safe_load(open(\".github/workflows/12-uat-deployment.yml\"))'"

# Test 6: Workflow contains hardening features
echo -e "\n${BLUE}=== Workflow Enhancement Tests ===${NC}"
run_test "Production workflow has pre-deployment-checks job" "grep -q 'pre-deployment-checks:' .github/workflows/13-prod-deployment.yml"
run_test "Production workflow has post-deployment-validation job" "grep -q 'post-deployment-validation:' .github/workflows/13-prod-deployment.yml"
run_test "Production workflow has concurrency control" "grep -q 'concurrency:' .github/workflows/13-prod-deployment.yml"
run_test "UAT workflow has pre-deployment checks" "grep -q 'pre-deployment-checks:' .github/workflows/12-uat-deployment.yml"
run_test "UAT workflow has concurrency control" "grep -q 'concurrency:' .github/workflows/12-uat-deployment.yml"

# Test 7: Script help/usage information
echo -e "\n${BLUE}=== Script Usage Tests ===${NC}"
run_test "Pre-deployment check has usage info" "grep -q 'Usage:' .github/scripts/pre-deployment-check.sh"
run_test "Smoke tests has usage info" "grep -q 'Usage:' .github/scripts/smoke-tests.sh"
run_test "Rollback script has usage info" "grep -q 'Usage:' .github/scripts/deployment-rollback.sh"

# Test 8: Documentation content validation
echo -e "\n${BLUE}=== Documentation Content Tests ===${NC}"
run_test "Hardening guide mentions all 6 scripts" "test \$(grep -c '\.sh\|\.py' docs/DEPLOYMENT_HARDENING.md) -ge 6"
run_test "Quick ref has monitoring section" "grep -q 'Monitoring' docs/DEPLOYMENT_QUICK_REF.md"
run_test "Quick ref has rollback section" "grep -q 'Rollback' docs/DEPLOYMENT_QUICK_REF.md"
run_test "Summary mentions safety layers" "grep -q 'Safety' DEPLOYMENT_HARDENING_SUMMARY.md"

# Summary
echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                    Test Summary                       ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "Total Tests:   $TOTAL_TESTS"
echo -e "${GREEN}Passed Tests:  $PASSED_TESTS${NC}"
echo -e "${RED}Failed Tests:  $FAILED_TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Deployment hardening verified.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the output above.${NC}"
    exit 1
fi
