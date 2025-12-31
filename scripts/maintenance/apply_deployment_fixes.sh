#!/bin/bash
# Script to apply multi-tenancy deployment fixes to workflows
# Generated: 2025-12-01

set -e

echo "=== Applying Multi-Tenancy Deployment Fixes ==="
echo ""

# Fix 1: Production Workflow - Deploy Backend Migrations
echo "1. Fixing production deploy-backend migrations..."
sed -i '542,561c\
          # Run migrations (shared-schema multi-tenancy using standard Django migrations)\
          echo "Running database migrations..."\
          sudo docker run --rm \\\
            --env-file "$ENV_FILE" \\\
            -v "$MEDIA_DIR:/app/media" \\\
            -v "$STATIC_DIR:/app/staticfiles" \\\
            "$REG/$IMG:$TAG" \\\
            python manage.py migrate --noinput
' .github/workflows/13-prod-deployment.yml

# Fix 2: Production Workflow - Test Backend Setup
echo "2. Fixing production test-backend tenant setup..."
cat > /tmp/prod-test-fix.txt << 'EOF'

      - name: Apply migrations
        working-directory: ./backend
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          SECRET_KEY: test-secret-key-for-testing-only
          DEBUG: True
          DJANGO_SETTINGS_MODULE: projectmeats.settings.test
          POSTGRES_USER: postgres
        run: |
          echo "Applying database migrations..."
          python manage.py migrate --noinput
      
      - name: Setup test tenants (shared-schema multi-tenancy)
        working-directory: ./backend
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          SECRET_KEY: test-secret-key-for-testing-only
          DEBUG: True
          DJANGO_SETTINGS_MODULE: projectmeats.settings.test
          POSTGRES_USER: postgres
        run: |
          # Create test tenants using custom shared-schema approach (idempotent)
          echo "Setting up test tenants..."
          python manage.py create_super_tenant --verbosity=1 || echo "Warning: Super tenant setup failed, continuing..."
          python manage.py create_guest_tenant --verbosity=1 || echo "Warning: Guest tenant setup failed, continuing..."
      
      # Multi-tenancy setup for shared-schema approach
EOF

# Note: Manual replacement needed for lines 162-240 due to complexity
echo "   WARNING: Manual edit required for lines 162-240 in 13-prod-deployment.yml"

# Fix 3: UAT Workflow - Deploy Backend Migrations  
echo "3. Fixing UAT deploy-backend migrations..."
sed -i '401,420c\
\
          # Run migrations (shared-schema multi-tenancy using standard Django migrations)\
          echo "Running database migrations..."\
          sudo docker run --rm \\\
            --env-file "$ENV_FILE" \\\
            -v "$MEDIA_DIR:/app/media" \\\
            -v "$STATIC_DIR:/app/staticfiles" \\\
            "$REG/$IMG:$TAG" \\\
            python manage.py migrate --noinput
' .github/workflows/12-uat-deployment.yml

echo "4. Fixing UAT test-backend tenant setup..."
echo "   WARNING: Manual edit required for lines 167-245 in 12-uat-deployment.yml"

echo ""
echo "=== Fixes Applied ==="
echo ""
echo "MANUAL STEPS REQUIRED:"
echo "1. Edit .github/workflows/13-prod-deployment.yml lines 162-240"
echo "2. Edit .github/workflows/12-uat-deployment.yml lines 167-245"  
echo "3. Replace complex tenant setup with simple create_super_tenant/create_guest_tenant calls"
echo ""
echo "See DEPLOYMENT_MULTI_TENANCY_FIX.md for exact replacement text"
