# GitHub Workflows Instructions

## applyTo
- .github/workflows/**/*.yml
- .github/workflows/**/*.yaml

## Workflow Structure Standards

### Naming Convention
```yaml
name: "Action Description (Component via Method)"
# Examples:
# - Deploy Dev (Frontend + Backend via DOCR)
# - Deploy UAT (Frontend + Backend via DOCR)
# - Deploy Production (Frontend + Backend via DOCR)
```

### Trigger Patterns
```yaml
on:
  push:
    branches: [main, development, uat]
  workflow_dispatch:  # Always include manual trigger
  
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false  # Don't cancel production deploys
```

## Job Organization

### Standard Job Flow
```yaml
jobs:
  pre-deployment-checks:
    # Validation, ID generation, notifications
  
  build-and-push:
    needs: [pre-deployment-checks]
    # Build Docker images
  
  test-frontend:
    needs: [build-and-push]
    # Frontend tests
  
  test-backend:
    needs: [build-and-push]
    # Backend tests
  
  migrate:
    needs: [build-and-push, test-backend]
    # Database migrations (decoupled)
  
  deploy-frontend:
    needs: [migrate, test-frontend]
    # Frontend deployment
  
  deploy-backend:
    needs: [migrate]
    # Backend deployment
  
  post-deployment-validation:
    needs: [deploy-backend, deploy-frontend]
    # Health checks, smoke tests
```

## Image Tagging

### Immutable Tagging Pattern
```yaml
# ✅ CORRECT: Use SHA for deployments
tags: |
  ${{ env.REGISTRY }}/${{ env.IMAGE }}:${{ env.ENV }}-${{ github.sha }}
  ${{ env.REGISTRY }}/${{ env.IMAGE }}:${{ env.ENV }}-latest

# ❌ WRONG: Never use only -latest for production
tags: |
  ${{ env.REGISTRY }}/${{ env.IMAGE }}:latest
```

### Environment Prefixes
- `dev-${{ github.sha }}` - Development
- `uat-${{ github.sha }}` - UAT/Staging
- `prod-${{ github.sha }}` - Production

## Migration Jobs (Critical)

### Decoupled Migration Pattern
```yaml
migrate:
  runs-on: ubuntu-latest
  needs: [build-and-push, test-backend]
  environment: ${ENV}-backend
  timeout-minutes: 15
  
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    
    - name: Run idempotent migrations
      working-directory: ./backend
      env:
        DATABASE_URL: ${{ secrets.DB_URL }}
        SECRET_KEY: ${{ secrets.SECRET_KEY }}
        DJANGO_SETTINGS_MODULE: ${{ secrets.DJANGO_SETTINGS_MODULE }}
        DB_ENGINE: django.db.backends.postgresql
      run: |
        # Parse DATABASE_URL if production settings
        if [ -n "$DATABASE_URL" ]; then
          export DB_USER=$(echo "$DATABASE_URL" | sed -n 's|postgresql://\([^:]*\):.*|\1|p')
          export DB_PASSWORD=$(echo "$DATABASE_URL" | sed -n 's|postgresql://[^:]*:\([^@]*\)@.*|\1|p')
          export DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')
          export DB_PORT=$(echo "$DATABASE_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
          export DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')
        fi
        
        # Idempotent multi-tenant migrations
        python manage.py migrate_schemas --shared --fake-initial --noinput
        python manage.py create_super_tenant --no-input
        python manage.py migrate_schemas --tenant --noinput
```

**Key Points:**
- ✅ Always use `--fake-initial` for idempotency
- ✅ Run migrations in CI environment, not via SSH
- ✅ Block deployment if migrations fail
- ✅ Parse DATABASE_URL for production settings

## Deployment Jobs

### SSH Deployment Pattern
```yaml
deploy-backend:
  needs: [migrate]  # Wait for migrations
  environment: ${ENV}-backend
  
  steps:
    - name: Deploy
      env:
        SSHPASS: ${{ secrets.SSH_PASSWORD }}
      run: |
        sshpass -e ssh -o StrictHostKeyChecking=yes ${{ secrets.USER }}@${{ secrets.HOST }} <<'SSH'
        set -euo pipefail
        
        REG="${{ env.REGISTRY }}"
        IMG="${{ env.IMAGE }}"
        TAG="${{ env.ENV }}-${{ github.sha }}"
        
        # Pull SHA-tagged image (not -latest)
        sudo docker pull "$REG/$IMG:$TAG"
        
        # Stop old container
        sudo docker rm -f container-name || true
        
        # Start new container
        sudo docker run -d --name container-name \
          --restart unless-stopped \
          -p 8000:8000 \
          --env-file /path/to/.env \
          "$REG/$IMG:$TAG"
        SSH
```

**Important:**
- ✅ Use quoted heredoc (`<<'SSH'`) to prevent local expansion
- ✅ Use `set -euo pipefail` for error handling
- ✅ Always pull SHA-tagged image
- ✅ Never run migrations in deploy step (use migrate job)

## Security Best Practices

### Secrets Management
```yaml
# ✅ Use environment-scoped secrets
environment:
  name: prod-backend
env:
  DATABASE_URL: ${{ secrets.PROD_DB_URL }}
  SECRET_KEY: ${{ secrets.PROD_SECRET_KEY }}

# ❌ Never hardcode secrets
env:
  DATABASE_URL: "postgresql://user:pass@localhost/db"
```

### Permissions
```yaml
permissions:
  contents: read
  packages: write  # Only if pushing images
  id-token: write  # Only if using OIDC
```

## Caching

### Docker Layer Caching
```yaml
- name: Cache Docker layers
  uses: actions/cache@v4
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ matrix.app }}-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-buildx-${{ matrix.app }}-
```

### Dependency Caching
```yaml
# Python
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# Node
- uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'npm'
    cache-dependency-path: 'frontend/package-lock.json'
```

## Health Checks

### Post-Deployment Validation
```yaml
- name: Health check
  run: |
    MAX_ATTEMPTS=15
    ATTEMPT=1
    
    while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
      HTTP_CODE=$(curl -L -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")
      
      if [ "$HTTP_CODE" = "200" ]; then
        echo "✓ Health check passed"
        exit 0
      fi
      
      echo "Attempt $ATTEMPT/$MAX_ATTEMPTS (HTTP $HTTP_CODE)..."
      sleep 5
      ATTEMPT=$((ATTEMPT + 1))
    done
    
    echo "✗ Health check failed"
    exit 1
```

## Testing Jobs

### Backend Tests
```yaml
test-backend:
  services:
    postgres:
      image: postgres:15
      env:
        POSTGRES_PASSWORD: postgres
        POSTGRES_USER: postgres
        POSTGRES_DB: test_db
      options: >-
        --health-cmd pg_isready
        --health-interval 10s
        --health-timeout 5s
        --health-retries 5
      ports:
        - 5432:5432
  
  steps:
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      run: python manage.py test apps/ --verbosity=2
```

## Matrix Strategy

### Multi-Component Builds
```yaml
strategy:
  matrix:
    app: [frontend, backend]
    
steps:
  - name: Build ${{ matrix.app }}
    uses: docker/build-push-action@v5
    with:
      context: .
      file: ${{ matrix.app }}/dockerfile
      push: true
      tags: ${{ env.REGISTRY }}/${{ matrix.app }}:${{ env.ENV }}-${{ github.sha }}
```

## Common Pitfalls

### ❌ Don't Do This
```yaml
# Mutable tags in production
tags: image:latest

# Migrations in deployment step
run: |
  docker pull image
  docker run image python manage.py migrate  # Wrong!
  docker run -d image

# No error handling
run: |
  command1
  command2  # Will run even if command1 fails

# Hardcoded values
run: echo "SECRET_KEY=hardcoded123" > .env
```

### ✅ Do This Instead
```yaml
# Immutable tags
tags: image:prod-${{ github.sha }}

# Separate migrate job
migrate:
  steps:
    - run: python manage.py migrate_schemas --shared --fake-initial

deploy:
  needs: [migrate]
  steps:
    - run: docker run -d image

# Error handling
run: |
  set -euo pipefail
  command1
  command2

# Use secrets
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

## Workflow Maintenance

### Regular Updates
- Pin actions to SHA (security)
- Update action versions quarterly
- Test workflows in feature branches
- Monitor workflow duration
- Clean up old workflow runs

### Documentation
- Document workflow triggers
- Explain environment requirements
- Link to runbooks for failures
- Keep secrets inventory updated
