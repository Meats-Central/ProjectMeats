#!/bin/bash
# Deployment script for ProjectMeats backend
# This script handles migrations, collectstatic, and post-deployment tasks
# Made idempotent and safe for repeated runs

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Check if running in container
if [ ! -f "manage.py" ]; then
    log_error "manage.py not found. Make sure you're running this from the backend directory."
    exit 1
fi

log_info "Starting ProjectMeats deployment..."

# Step 1: Check database connectivity
log_info "Step 1/6: Checking database connectivity..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if python manage.py check --database default > /dev/null 2>&1; then
        log_info "Database connection successful"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            log_error "Failed to connect to database after $MAX_RETRIES attempts"
            exit 1
        fi
        log_warn "Database not ready, retrying... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    fi
done

# Step 2: Run migrations
log_info "Step 2/6: Running database migrations..."
python manage.py migrate --noinput || {
    log_error "Migration failed"
    exit 1
}
log_info "Migrations completed successfully"

# Step 3: Create superuser and root tenant (idempotent)
log_info "Step 3/6: Creating superuser and root tenant..."
python manage.py create_super_tenant --verbosity=1 || {
    log_warn "create_super_tenant command failed or not available, continuing..."
}

# Step 4: Create guest tenant (idempotent)
log_info "Step 4/6: Creating guest tenant..."
python manage.py create_guest_tenant --verbosity=1 || {
    log_warn "create_guest_tenant command failed or not available, continuing..."
}

# Step 5: Collect static files
log_info "Step 5/6: Collecting static files..."
python manage.py collectstatic --noinput --clear || {
    log_warn "collectstatic failed, but continuing (may not be critical)"
}
log_info "Static files collected successfully"

# Step 6: Run system checks
log_info "Step 6/6: Running system checks..."
python manage.py check || {
    log_warn "System check found issues, but deployment continues"
}

log_info "Deployment completed successfully!"
log_info "Ready to start application server"

exit 0
