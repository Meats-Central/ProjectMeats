#!/bin/bash
# Deployment Health Check and Validation Script
# Ensures deployment integrity before and after deployments

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
HEALTH_CHECK_URL="${HEALTH_CHECK_URL:-}"
MAX_RETRIES="${MAX_RETRIES:-30}"
RETRY_DELAY="${RETRY_DELAY:-10}"
TIMEOUT="${TIMEOUT:-10}"

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pre-deployment checks
check_environment_variables() {
    log_info "Checking required environment variables..."
    
    local required_vars=(
        "DJANGO_SETTINGS_MODULE"
        "SECRET_KEY"
        "DATABASE_URL"
        "ALLOWED_HOSTS"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        return 1
    fi
    
    log_info "✓ All required environment variables present"
    return 0
}

check_database_connection() {
    log_info "Checking database connectivity..."
    
    if ! python manage.py check --database default >/dev/null 2>&1; then
        log_error "Database connection failed"
        return 1
    fi
    
    log_info "✓ Database connection successful"
    return 0
}

check_migrations() {
    log_info "Checking migration status..."
    
    # Check if there are unapplied migrations
    if ! python manage.py migrate --check >/dev/null 2>&1; then
        log_warn "Unapplied migrations detected"
        python manage.py showmigrations --plan | grep -v "\\[X\\]" || true
    else
        log_info "✓ All migrations applied"
    fi
    
    return 0
}

check_static_files() {
    log_info "Checking static files..."
    
    if [[ ! -d "/app/staticfiles" ]] || [[ -z "$(ls -A /app/staticfiles 2>/dev/null)" ]]; then
        log_warn "Static files directory empty or missing"
        return 1
    fi
    
    log_info "✓ Static files present"
    return 0
}

# Health check with retries
health_check() {
    local url="$1"
    local retries=0
    
    log_info "Performing health check on $url"
    
    while [[ $retries -lt $MAX_RETRIES ]]; do
        # Use -L to follow redirects (e.g., HTTP 301 to HTTPS)
        # Still outputs only final HTTP code for validation
        if curl -L -f -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" | grep -q "200"; then
            log_info "✓ Health check passed (attempt $((retries + 1)))"
            return 0
        fi
        
        retries=$((retries + 1))
        if [[ $retries -lt $MAX_RETRIES ]]; then
            log_warn "Health check failed, retrying in ${RETRY_DELAY}s (attempt $retries/$MAX_RETRIES)"
            sleep "$RETRY_DELAY"
        fi
    done
    
    log_error "Health check failed after $MAX_RETRIES attempts"
    return 1
}

# Container health check
check_container_health() {
    log_info "Checking container health..."
    
    # Check if container is running
    if ! docker ps | grep -q "pm-backend"; then
        log_error "Backend container not running"
        return 1
    fi
    
    # Check container logs for errors
    local error_count=$(docker logs pm-backend --tail 100 2>&1 | grep -i "error" | wc -l)
    if [[ $error_count -gt 5 ]]; then
        log_warn "Found $error_count errors in recent logs"
    fi
    
    log_info "✓ Container health check passed"
    return 0
}

# Disk space check
check_disk_space() {
    log_info "Checking disk space..."
    
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [[ $usage -gt 90 ]]; then
        log_error "Disk usage critical: ${usage}%"
        return 1
    elif [[ $usage -gt 80 ]]; then
        log_warn "Disk usage high: ${usage}%"
    else
        log_info "✓ Disk space OK: ${usage}% used"
    fi
    
    return 0
}

# Docker cache cleanup
cleanup_docker_cache() {
    log_info "Cleaning up Docker build cache..."
    
    # Remove old build cache (keep last 7 days)
    docker builder prune -f --filter "until=168h" || true
    
    # Remove dangling images
    docker image prune -f || true
    
    log_info "✓ Docker cache cleaned"
}

# Run all pre-deployment checks
pre_deployment_checks() {
    log_info "========================================="
    log_info "Running Pre-Deployment Checks"
    log_info "========================================="
    
    local failed=0
    
    check_environment_variables || ((failed++))
    check_database_connection || ((failed++))
    check_migrations || ((failed++))
    check_disk_space || ((failed++))
    
    if [[ $failed -gt 0 ]]; then
        log_error "$failed pre-deployment checks failed"
        return 1
    fi
    
    log_info "========================================="
    log_info "✓ All pre-deployment checks passed"
    log_info "========================================="
    return 0
}

# Run all post-deployment checks
post_deployment_checks() {
    log_info "========================================="
    log_info "Running Post-Deployment Checks"
    log_info "========================================="
    
    local failed=0
    
    check_container_health || ((failed++))
    check_static_files || ((failed++))
    
    if [[ -n "$HEALTH_CHECK_URL" ]]; then
        health_check "$HEALTH_CHECK_URL" || ((failed++))
    else
        log_warn "HEALTH_CHECK_URL not set, skipping health check"
    fi
    
    if [[ $failed -gt 0 ]]; then
        log_error "$failed post-deployment checks failed"
        return 1
    fi
    
    log_info "========================================="
    log_info "✓ All post-deployment checks passed"
    log_info "========================================="
    return 0
}

# Rollback function
rollback() {
    log_error "Deployment failed, initiating rollback..."
    
    # Stop new container
    docker stop pm-backend || true
    
    # Restore from backup if available
    if docker ps -a | grep -q "pm-backend-backup"; then
        log_info "Restoring previous container..."
        docker rename pm-backend pm-backend-failed || true
        docker rename pm-backend-backup pm-backend || true
        docker start pm-backend || true
    fi
    
    log_info "Rollback completed"
}

# Main execution
main() {
    local mode="${1:-pre}"
    
    case "$mode" in
        pre)
            pre_deployment_checks
            ;;
        post)
            post_deployment_checks
            ;;
        health)
            if [[ -z "$HEALTH_CHECK_URL" ]]; then
                log_error "HEALTH_CHECK_URL required for health check"
                exit 1
            fi
            health_check "$HEALTH_CHECK_URL"
            ;;
        cleanup)
            cleanup_docker_cache
            ;;
        rollback)
            rollback
            ;;
        *)
            echo "Usage: $0 {pre|post|health|cleanup|rollback}"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
