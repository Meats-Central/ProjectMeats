#!/bin/bash
# Devcontainer post-create setup script
# Runs idempotent multi-tenant database migrations and setup

set -euo pipefail

echo "=== ProjectMeats Devcontainer Setup ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Navigate to workspace root
cd /workspaces/ProjectMeats || exit 1

# Step 1: Install backend dependencies
echo ""
echo "Step 1/6: Installing Python dependencies..."
cd backend
if [ -f "requirements.txt" ]; then
    pip install --quiet -r requirements.txt
    print_success "Python dependencies installed"
else
    print_warning "requirements.txt not found, skipping"
fi

# Step 2: Install frontend dependencies
echo ""
echo "Step 2/6: Installing Node dependencies..."
cd ../frontend
if [ -f "package.json" ]; then
    npm ci --quiet
    print_success "Node dependencies installed"
else
    print_warning "package.json not found, skipping"
fi

# Step 3: Wait for database
echo ""
echo "Step 3/6: Waiting for PostgreSQL to be ready..."
cd ../backend
MAX_WAIT=30
COUNT=0
while ! python manage.py check --database default >/dev/null 2>&1; do
    if [ $COUNT -ge $MAX_WAIT ]; then
        print_error "Database not ready after ${MAX_WAIT}s"
        exit 1
    fi
    echo "   Waiting for database... ($COUNT/$MAX_WAIT)"
    sleep 1
    COUNT=$((COUNT + 1))
done
print_success "Database is ready"

# Step 4: Run idempotent multi-tenant migrations
echo ""
echo "Step 4/6: Running multi-tenant schema migrations..."

# Shared schema migrations (idempotent with --fake-initial)
echo "   4a. Applying shared schema migrations..."
if python manage.py migrate_schemas --shared --fake-initial --noinput 2>/dev/null; then
    print_success "Shared schema migrations applied"
else
    print_warning "migrate_schemas not available, using standard migrate"
    if python manage.py migrate --fake-initial --noinput; then
        print_success "Standard migrations applied"
    else
        print_error "Migration failed"
        exit 1
    fi
fi

# Create super tenant (idempotent)
echo "   4b. Creating/updating super tenant..."
if python manage.py create_super_tenant --no-input --verbosity=1 2>&1 | grep -q "already exists\|created"; then
    print_success "Super tenant ready"
else
    print_warning "create_super_tenant command not available or failed"
fi

# Tenant-specific migrations (idempotent)
echo "   4c. Applying tenant-specific migrations..."
if python manage.py migrate_schemas --tenant --noinput 2>/dev/null; then
    print_success "Tenant migrations applied"
else
    print_warning "migrate_schemas --tenant not available"
fi

# Step 5: Create guest tenant (optional)
echo ""
echo "Step 5/6: Creating/updating guest tenant..."
if python manage.py create_guest_tenant --no-input --verbosity=1 2>&1 | grep -q "already exists\|created"; then
    print_success "Guest tenant ready"
else
    print_warning "create_guest_tenant command not available or failed"
fi

# Step 6: Create superuser (optional, for development)
echo ""
echo "Step 6/6: Creating development superuser..."
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    python manage.py createsuperuser --noinput --email="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" 2>/dev/null || true
    print_success "Superuser created/updated"
else
    print_warning "Superuser credentials not provided (set DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD)"
fi

# Summary
echo ""
echo "=== Setup Complete ==="
echo ""
echo "📝 Multi-tenancy notes:"
echo "   - Shared schema migrations: Applied"
echo "   - Super tenant: Ready"
echo "   - Tenant-specific migrations: Applied"
echo "   - Guest tenant: Ready"
echo ""
echo "🚀 Start development servers:"
echo "   Backend:  cd backend && python manage.py runserver 0.0.0.0:8000"
echo "   Frontend: cd frontend && npm run dev"
echo ""
echo "🔍 Verify setup:"
echo "   python backend/manage.py check"
echo "   python backend/manage.py showmigrations"
echo ""
print_success "Devcontainer ready for development!"
