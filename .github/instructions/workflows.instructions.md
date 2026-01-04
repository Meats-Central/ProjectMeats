---
applyTo:
  - .github/workflows/**/*.yml
  - .github/workflows/**/*.yaml
---

# GitHub Workflows Instructions

## 🏆 GOLDEN STANDARD CI/CD (Achieved: January 4, 2026)

### Critical Architecture Principles

**NEVER VIOLATE THESE RULES** - They are the result of extensive production hardening:

1. **Docker Deployment Method**
   - ✅ **ALWAYS** use `docker run` for production deployments via SSH
   - ❌ **NEVER** use `docker-compose` on remote hosts
   - **Why**: docker-compose v1/v2 version conflicts cause `KeyError: 'ContainerConfig'` failures
   - **Evidence**: 48 commits fixing docker-compose issues → universal `docker run` pattern = 100% reliability

2. **Parallel Execution Architecture**
   - ✅ **ALWAYS** maintain separate backend and frontend swimlanes
   - ✅ **ALWAYS** let frontend/backend build and test in parallel
   - ❌ **NEVER** make `deploy-frontend` depend on `deploy-backend`
   - **Impact**: 40% faster deployments (10-12 min vs 15-20 min)

3. **File System Standards**
   - ✅ **ALWAYS** name Dockerfiles as `Dockerfile` (PascalCase)
   - ❌ **NEVER** use lowercase `dockerfile`
   - **Why**: Case-sensitive Linux filesystems reject lowercase

4. **Image Management**
   - ✅ **ALWAYS** use SHA-tagged images: `${environment}-${github.sha}`
   - ✅ **ALWAYS** pull from registry before deployment
   - ❌ **NEVER** rely on `:latest` tag in production
   - **Why**: Immutable deployments enable reliable rollbacks

5. **Secrets Management**
   - ✅ **ALWAYS** generate secrets at deployment time from GitHub Secrets
   - ✅ **ALWAYS** use SCP to transfer sensitive files (bypasses bash quoting issues)
   - ❌ **NEVER** echo secrets or log them
   - ❌ **NEVER** hardcode secrets in workflows

6. **Heredoc Syntax**
   - ✅ **ALWAYS** use `<<-` operator for indented content
   - ✅ **ALWAYS** quote delimiters: `<<- 'EOF'`
   - ❌ **NEVER** use `<<` with indented EOF delimiter
   - **Why**: Prevents bash syntax errors in YAML context

## CI/CD Reliability & Efficiency Standards

### Deployment Method
- **ALWAYS use `docker run`** for starting containers in production deployments via SSH
- **NEVER use `docker-compose`** on remote hosts to prevent versioning and API incompatibilities (e.g., KeyError: 'ContainerConfig')
- The `docker run` pattern is universal and bypasses all docker-compose version conflicts

### Parallelization
- **Frontend and Backend deployments MUST run on parallel tracks**
- `deploy-frontend` should depend on `[migrate, test-frontend]`, but **NOT** on `deploy-backend`
- This eliminates the sequential bottleneck and reduces deployment time by ~40%

### File Standards
- Dockerfiles **MUST** be named exactly `Dockerfile` (PascalCase) for case-sensitive filesystem compatibility
- **NEVER** use lowercase `dockerfile` as this causes "No such file or directory" errors on Linux systems

### Image Management
- Always pull SHA-tagged images from registry: `docker pull $REG/$IMG:$TAG`
- Use immutable tags with format: `${environment}-${github.sha}`
- Never rely on `:latest` tag in production deployments

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

### Standard Job Flow (Parallel Tracks)
```yaml
jobs:
  # Parallel build jobs
  build-backend:
    # Build backend Docker image
  
  build-frontend:
    # Build frontend Docker image
  
  # Parallel test tracks
  test-backend:
    needs: [build-backend]
    # Backend tests
  
  test-frontend:
    needs: [build-frontend]
    # Frontend tests
  
  # Synchronization point
  migrate:
    needs: [test-backend]
    # Database migrations (decoupled)
  
  # Parallel deployments
  deploy-backend:
    needs: [migrate]
    # Backend deployment via docker run
  
  deploy-frontend:
    needs: [migrate, test-frontend]
    # Frontend deployment via docker run (NOT dependent on deploy-backend)
  
  # Validation
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
        
        # Install dependencies (exit on error)
        pip install -r backend/requirements.txt || exit 1
        
        # Run standard Django migrations (NOT migrate_schemas)
        python manage.py migrate --fake-initial --noinput
```

**Key Points:**
- ✅ Always use `--fake-initial` for idempotency
- ✅ Run migrations in CI environment, not via SSH
- ✅ Block deployment if migrations fail
- ✅ Parse DATABASE_URL for production settings
- ✅ Use standard Django `migrate` command (NOT `migrate_schemas`)

## Deployment Jobs

### CRITICAL: Use docker run (NOT docker-compose)

**Why**: docker-compose v1.29.2 (Python legacy) has API incompatibilities with modern image metadata, causing `KeyError: 'ContainerConfig'` crashes. The `docker run` pattern is universal and version-agnostic.

### Backend Deployment Pattern
```yaml
deploy-backend:
  needs: [migrate]
  environment: ${ENV}-backend
  
  steps:
    - name: Deploy
      env:
        SSHPASS: ${{ secrets.SSH_PASSWORD }}
      run: |
        sshpass -e ssh -o StrictHostKeyChecking=no ${{ secrets.USER }}@${{ secrets.HOST }} <<'SSH'
        set -euo pipefail
        
        REG="${{ env.REGISTRY }}"
        IMG="${{ env.BACKEND_IMAGE }}"
        TAG="${{ env.ENV }}-${{ github.sha }}"
        
        # Login to registry
        echo "${{ secrets.DO_ACCESS_TOKEN }}" | docker login registry.digitalocean.com -u "${{ secrets.DO_ACCESS_TOKEN }}" --password-stdin
        
        # Pull SHA-tagged image
        docker pull "$REG/$IMG:$TAG"
        
        # Stop old container
        docker rm -f pm-backend projectmeats-backend || true
        
        # Start new container with docker run
        docker run -d --name pm-backend \
          --restart unless-stopped \
          -p 8000:8000 \
          --env-file /root/projectmeats/backend/.env \
          -v /root/projectmeats/media:/app/media \
          -v /root/projectmeats/staticfiles:/app/staticfiles \
          "$REG/$IMG:$TAG"
        SSH
```

### Frontend Deployment Pattern
```yaml
deploy-frontend:
  needs: [migrate, test-frontend]  # NOT deploy-backend (parallel)
  environment: ${ENV}-frontend
  
  steps:
    - name: Deploy
      env:
        SSHPASS: ${{ secrets.SSH_PASSWORD }}
      run: |
        sshpass -e ssh -o StrictHostKeyChecking=no ${{ secrets.USER }}@${{ secrets.HOST }} <<'SSH'
        set -euo pipefail
        
        REG="${{ env.REGISTRY }}"
        IMG="${{ env.FRONTEND_IMAGE }}"
        TAG="${{ env.ENV }}-${{ github.sha }}"
        
        # Login to registry
        echo "${{ secrets.DO_ACCESS_TOKEN }}" | docker login registry.digitalocean.com -u "${{ secrets.DO_ACCESS_TOKEN }}" --password-stdin
        
        # Pull SHA-tagged image
        docker pull "$REG/$IMG:$TAG"
        
        # Stop old container
        docker rm -f pm-frontend projectmeats-frontend || true
        
        # Start new container with docker run
        docker run -d --name pm-frontend \
          --restart unless-stopped \
          -p 127.0.0.1:8080:80 \
          -e REACT_APP_API_BASE_URL="${{ secrets.REACT_APP_API_BASE_URL }}" \
          -e BACKEND_HOST="${{ secrets.BACKEND_HOST }}" \
          -e DOMAIN_NAME="${{ secrets.DOMAIN_NAME }}" \
          "$REG/$IMG:$TAG"
        SSH
```

**Important:**
- ✅ Use `docker run` (universal, version-agnostic)
- ✅ Pull SHA-tagged image before starting
- ✅ Use heredoc (`<<'SSH'`) to prevent local expansion
- ✅ Use `set -euo pipefail` for error handling
- ❌ Never use `docker-compose up` on remote hosts
- ❌ Never depend on `:latest` tag
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
    - run: python manage.py migrate --fake-initial --noinput

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

## 🎯 Golden Standard Quick Reference

### Perfect Deployment Pattern

**Backend Deployment** (Universal, Version-Agnostic):
```bash
# 1. Pull SHA-tagged image
docker pull registry.digitalocean.com/meatscentral/projectmeats-backend:dev-abc123

# 2. Stop old container
docker rm -f pm-backend || true

# 3. Start new container with docker run
docker run -d --name pm-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file /root/projectmeats/backend/.env \
  -v /root/projectmeats/media:/app/media \
  -v /root/projectmeats/staticfiles:/app/staticfiles \
  registry.digitalocean.com/meatscentral/projectmeats-backend:dev-abc123
```

**Frontend Deployment** (Universal, Version-Agnostic):
```bash
# 1. Pull SHA-tagged image
docker pull registry.digitalocean.com/meatscentral/projectmeats-frontend:dev-abc123

# 2. Stop old container
docker rm -f pm-frontend || true

# 3. Start new container with docker run
docker run -d --name pm-frontend \
  --restart unless-stopped \
  -p 127.0.0.1:8080:80 \
  -e REACT_APP_API_BASE_URL="https://dev.meatscentral.com" \
  -e BACKEND_HOST="backend" \
  -e DOMAIN_NAME="dev.meatscentral.com" \
  -v /opt/pm/frontend/env:/usr/share/nginx/html/env:ro \
  registry.digitalocean.com/meatscentral/projectmeats-frontend:dev-abc123
```

### Parallel Swimlane Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND SWIMLANE                         │
├─────────────────────────────────────────────────────────────┤
│  build-backend                                              │
│    ↓                                                        │
│  security-scan-backend (non-blocking)                       │
│    ↓                                                        │
│  test-backend                                               │
│    ↓                                                        │
│  migrate ←──────────────────────────────────────────────┐   │
│    ↓                                                    │   │
│  deploy-backend                                         │   │
└─────────────────────────────────────────────────────────┼───┘
                                                          │
┌─────────────────────────────────────────────────────────┼───┐
│                   FRONTEND SWIMLANE                     │   │
├─────────────────────────────────────────────────────────┼───┤
│  build-frontend                                         │   │
│    ↓                                                    │   │
│  security-scan-frontend (non-blocking)                  │   │
│    ↓                                                    │   │
│  test-frontend                                          │   │
│    ↓                                                    │   │
│  deploy-frontend ←──────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

Synchronization Point: Both deploy jobs wait for migrate to complete
```

### Job Dependencies (Locked Down)

```yaml
# Backend Track
build-backend:
  needs: []  # Starts immediately

security-scan-backend:
  needs: [build-backend]
  continue-on-error: true  # Non-blocking

test-backend:
  needs: [build-backend]

migrate:
  needs: [test-backend]
  timeout-minutes: 15

deploy-backend:
  needs: [migrate]

# Frontend Track  
build-frontend:
  needs: []  # Starts immediately (parallel with backend)

security-scan-frontend:
  needs: [build-frontend]
  continue-on-error: true  # Non-blocking

test-frontend:
  needs: [build-frontend]

deploy-frontend:
  needs: [migrate, test-frontend, security-scan-frontend]
  # Does NOT need deploy-backend (parallel deployment)
```

### Workflow Naming Standards

**Run Names** (with emojis for easy scanning):
```yaml
# Main Pipeline
run-name: "${{ github.event_name == 'pull_request' && format('🔍 PR Check: {0}', github.event.pull_request.title) || format('�� Deploy: {0}', github.ref_name) }}"

# PR Validation
run-name: "🔍 PR Check: ${{ github.event.pull_request.title }}"

# Ops Release Automation
run-name: >-
  ${{ 
    github.event_name == 'workflow_run' && format('Auto-Promote: {0} to {1}', github.event.workflow_run.head_branch, github.event.workflow_run.head_branch == 'development' && 'UAT' || 'Production') ||
    format('Manual: {0}', inputs.task)
  }}
```

**Job Names** (descriptive, self-documenting):
```yaml
build-backend:
  name: "Build & Push Backend Image"

security-scan-backend:
  name: "Security Scan: Backend"

test-backend:
  name: "Test Backend"

migrate:
  name: "Run Database Migrations"

deploy-backend:
  name: "Deploy Backend Container"
```

### Trigger Configuration (Clean, No Noise)

**Main Pipeline** (Deployments Only):
```yaml
on:
  push:
    branches: [development, uat, main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - 'archived/**'
  workflow_dispatch:  # Manual triggers

# ❌ NO pull_request trigger (handled by pr-validation.yml)
```

**PR Validation** (Validation Only):
```yaml
on:
  pull_request:
    branches: [development, uat, main]

# ❌ NO push trigger (handled by main-pipeline.yml)
```

### Secrets Generation Pattern

**Backend .env Creation**:
```yaml
- name: Create Backend .env File Locally
  run: |
    cat <<- 'EOF' > backend.env
    DJANGO_SECRET_KEY=${{ secrets.DJANGO_SECRET_KEY }}
    DJANGO_SETTINGS_MODULE=${{ secrets.DJANGO_SETTINGS_MODULE }}
    ALLOWED_HOSTS=${{ secrets.ALLOWED_HOSTS }}
    DEBUG=${{ secrets.DEBUG }}
    DB_NAME=${{ secrets.DB_NAME }}
    DB_USER=${{ secrets.DB_USER }}
    DB_PASSWORD=${{ secrets.DB_PASSWORD }}
    DB_HOST=${{ secrets.DB_HOST }}
    DB_PORT=${{ secrets.DB_PORT }}
    DB_ENGINE=django.db.backends.postgresql
    EOF

- name: Transfer .env to Server
  env:
    SSHPASS: ${{ secrets.SSH_PASSWORD }}
  run: |
    sshpass -e ssh -o StrictHostKeyChecking=no ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} "mkdir -p /root/projectmeats/backend"
    sshpass -e scp -o StrictHostKeyChecking=no backend.env ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }}:/root/projectmeats/backend/.env
```

### File Permissions Pattern

**Preemptive Permission Fixes**:
```bash
# In deployment SSH block, BEFORE docker run:
mkdir -p /root/projectmeats/staticfiles
chown -R 1000:1000 /root/projectmeats/staticfiles
chmod -R 775 /root/projectmeats/staticfiles
```

### Health Check Pattern

**Post-Deployment Validation**:
```bash
MAX_ATTEMPTS=15
ATTEMPT=1
HEALTH_URL="https://$DOMAIN/api/health/"

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
docker logs pm-backend --tail 50
exit 1
```

## 📚 Related Documentation

- **Achievement Report**: `/docs/GOLDEN_STANDARD_ACHIEVEMENT.md`
- **Configuration Guide**: `/docs/CONFIGURATION_AND_SECRETS.md`
- **Deployment History**: See commits from Jan 3-4, 2026 (48 commits)

## 🔒 Final Security Checklist

Before deploying to production, verify:

- [ ] All secrets stored in GitHub Environment Secrets (not repository secrets)
- [ ] No secrets logged in workflow output
- [ ] SSH host key verification enabled
- [ ] Containers run as non-root user (UID 1000)
- [ ] Security scans reviewed (Trivy results in GitHub Security tab)
- [ ] Database on private network (not exposed)
- [ ] Frontend bound to localhost (proxied through nginx)
- [ ] SSL certificates valid and auto-renewing
- [ ] Backup procedures tested and documented
- [ ] Rollback procedures tested and documented

## 🎓 Training & Knowledge Transfer

**New Team Members** should:
1. Read this document completely
2. Review `/docs/GOLDEN_STANDARD_ACHIEVEMENT.md`
3. Study the parallel swimlane architecture diagram
4. Review successful workflow runs in GitHub Actions
5. Practice manual deployment on dev environment
6. Shadow experienced team member during production deployment

**Key Concepts to Master**:
- Docker run vs docker-compose (and why we chose run)
- Parallel swimlane architecture
- Immutable image tagging with SHA
- Heredoc syntax with `<<-` operator
- GitHub Actions workflow_call pattern
- Environment-scoped secrets

---

**Document Status**: ✅ LOCKED - Golden Standard Achieved  
**Last Major Update**: January 4, 2026  
**Next Review Date**: April 1, 2026  
**Maintained By**: Infrastructure Team
