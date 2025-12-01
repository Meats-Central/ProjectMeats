#!/bin/bash
# Workflow Validation Script
# Validates GitHub Actions workflow syntax and configuration

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check YAML syntax
validate_yaml_syntax() {
    log_info "Validating YAML syntax..."
    
    local failed=0
    
    for workflow in .github/workflows/*.yml; do
        if [[ -f "$workflow" ]]; then
            if ! python -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
                log_error "Invalid YAML syntax in $workflow"
                ((failed++))
            else
                log_info "✓ $workflow"
            fi
        fi
    done
    
    if [[ $failed -gt 0 ]]; then
        log_error "$failed workflow files have syntax errors"
        return 1
    fi
    
    log_info "✓ All workflow files have valid YAML syntax"
    return 0
}

# Check for required secrets
check_required_secrets() {
    log_info "Checking for required secrets references..."
    
    local required_secrets=(
        "DO_ACCESS_TOKEN"
        "DEV_HOST"
        "DEV_USER"
        "DEV_SSH_PASSWORD"
        "STAGING_HOST"
        "STAGING_USER"
        "SSH_PASSWORD"
        "PRODUCTION_HOST"
        "PRODUCTION_USER"
    )
    
    local missing=()
    
    for secret in "${required_secrets[@]}"; do
        if ! grep -r "secrets\.$secret" .github/workflows/*.yml >/dev/null 2>&1; then
            missing+=("$secret")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        log_warn "Secrets not referenced in workflows: ${missing[*]}"
    else
        log_info "✓ All required secrets referenced"
    fi
    
    return 0
}

# Check for cache configuration
check_cache_config() {
    log_info "Checking Docker cache configuration..."
    
    local workflows=(.github/workflows/*-deployment.yml)
    local failed=0
    
    for workflow in "${workflows[@]}"; do
        if ! grep -q "actions/cache@v3" "$workflow"; then
            log_warn "No cache configuration in $workflow"
            ((failed++))
        fi
        
        if ! grep -q "buildx-cache" "$workflow"; then
            log_warn "No BuildKit cache in $workflow"
            ((failed++))
        fi
    done
    
    if [[ $failed -eq 0 ]]; then
        log_info "✓ All deployment workflows have cache configured"
    fi
    
    return 0
}

# Check for health checks
check_health_checks() {
    log_info "Checking for health check steps..."
    
    local workflows=(.github/workflows/*-deployment.yml)
    
    for workflow in "${workflows[@]}"; do
        if ! grep -q "health" "$workflow"; then
            log_warn "No health check found in $workflow"
        else
            log_info "✓ Health check found in $workflow"
        fi
    done
    
    return 0
}

# Check for fetch-depth configuration
check_fetch_depth() {
    log_info "Checking fetch-depth configuration..."
    
    local workflows=(.github/workflows/*.yml)
    local issues=0
    
    for workflow in "${workflows[@]}"; do
        # Check if using checkout action
        if grep -q "actions/checkout@v4" "$workflow"; then
            # Check if fetch-depth is set
            if ! grep -A 3 "actions/checkout@v4" "$workflow" | grep -q "fetch-depth"; then
                log_warn "No fetch-depth set in $workflow (will use default full history)"
                ((issues++))
            fi
        fi
    done
    
    if [[ $issues -eq 0 ]]; then
        log_info "✓ All checkouts have fetch-depth configured"
    fi
    
    return 0
}

# Check for error handling
check_error_handling() {
    log_info "Checking error handling in deployment scripts..."
    
    local scripts=(.github/scripts/*.sh)
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            if ! head -5 "$script" | grep -q "set -euo pipefail"; then
                log_warn "Missing 'set -euo pipefail' in $script"
            else
                log_info "✓ $script has error handling"
            fi
        fi
    done
    
    return 0
}

# Check for timeout configurations
check_timeouts() {
    log_info "Checking workflow timeouts..."
    
    local workflows=(.github/workflows/*-deployment.yml)
    
    for workflow in "${workflows[@]}"; do
        if ! grep -q "timeout-minutes" "$workflow"; then
            log_warn "No timeout configured in $workflow"
        else
            log_info "✓ Timeout configured in $workflow"
        fi
    done
    
    return 0
}

# Check for retry logic
check_retry_logic() {
    log_info "Checking retry logic in health checks..."
    
    local workflows=(.github/workflows/*-deployment.yml)
    local has_retry=0
    
    for workflow in "${workflows[@]}"; do
        if grep -q "for i in" "$workflow" || grep -q "MAX_ATTEMPTS" "$workflow"; then
            ((has_retry++))
        fi
    done
    
    if [[ $has_retry -gt 0 ]]; then
        log_info "✓ Retry logic found in $has_retry workflows"
    else
        log_warn "No retry logic found in workflows"
    fi
    
    return 0
}

# Check for migration safety
check_migration_safety() {
    log_info "Checking migration safety..."
    
    # Check if makemigrations is still in CI (should be removed)
    if grep -r "makemigrations" .github/workflows/*-deployment.yml | grep -v "^#"; then
        log_error "Found makemigrations in deployment workflows (should be removed)"
        return 1
    fi
    
    log_info "✓ No dynamic migration generation in CI"
    return 0
}

# Check for proper concurrency control
check_concurrency() {
    log_info "Checking concurrency control..."
    
    local workflows=(.github/workflows/*-deployment.yml)
    
    for workflow in "${workflows[@]}"; do
        if grep -q "concurrency:" "$workflow"; then
            log_info "✓ Concurrency control in $workflow"
        else
            log_warn "No concurrency control in $workflow"
        fi
    done
    
    return 0
}

# Check for environment-specific configurations
check_env_separation() {
    log_info "Checking environment separation..."
    
    # Check for env-specific secret usage
    local envs=("DEV" "UAT" "STAGING" "PROD")
    
    for env in "${envs[@]}"; do
        if grep -r "${env}_" .github/workflows/*.yml >/dev/null 2>&1; then
            log_info "✓ Found ${env}-specific configuration"
        fi
    done
    
    return 0
}

# Main validation
main() {
    log_info "========================================="
    log_info "GitHub Actions Workflow Validation"
    log_info "========================================="
    
    local failed=0
    
    validate_yaml_syntax || ((failed++))
    check_required_secrets || ((failed++))
    check_cache_config || ((failed++))
    check_health_checks || ((failed++))
    check_fetch_depth || ((failed++))
    check_error_handling || ((failed++))
    check_timeouts || ((failed++))
    check_retry_logic || ((failed++))
    check_migration_safety || ((failed++))
    check_concurrency || ((failed++))
    check_env_separation || ((failed++))
    
    log_info "========================================="
    
    if [[ $failed -gt 0 ]]; then
        log_error "Validation completed with $failed failures"
        return 1
    fi
    
    log_info "✓ All validations passed"
    log_info "========================================="
    return 0
}

main "$@"
