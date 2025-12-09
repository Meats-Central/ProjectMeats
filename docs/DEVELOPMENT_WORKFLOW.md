# Development Workflow - Source of Truth

**Last Updated:** 2025-12-09  
**Status:** ✅ Authoritative Reference  
**Version:** 1.0.0

---

## Table of Contents
1. [Architecture](#architecture)
2. [Pipeline Stages](#pipeline-stages)
3. [Environment Variables & Secrets](#environment-variables--secrets)
4. [Operational Commands](#operational-commands)
5. [Troubleshooting](#troubleshooting)
6. [Future Enhancements](#future-enhancements)

---

## Architecture

### Multi-Tenancy Model

**ProjectMeats uses Shared-Schema Multi-Tenancy with Row-Level Security.**

```
┌─────────────────────────────────────────────┐
│         PostgreSQL (Single Schema)          │
│                                             │
│  ┌──────────┬──────────┬──────────────┐   │
│  │ Tenant 1 │ Tenant 2 │ Tenant N     │   │
│  │ (Rows)   │ (Rows)   │ (Rows)       │   │
│  └──────────┴──────────┴──────────────┘   │
│                                             │
│  Isolation via tenant_id ForeignKey         │
└─────────────────────────────────────────────┘
```

**Key Principles:**
- ✅ **Standard Django Models** with `tenant` ForeignKey
- ✅ **Shared Schema** - All tables in PostgreSQL `public` schema
- ✅ **QuerySet Filtering** - `filter(tenant=request.tenant)`
- ✅ **Standard Migrations** - `python manage.py migrate`
- ❌ **NO django-tenants** - Not used
- ❌ **NO schema_context()** - Not used
- ❌ **NO migrate_schemas** - Not used

### Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend** | Django + DRF | 5.x |
| **Frontend** | React + TypeScript | 19 / 5.9 |
| **Database** | PostgreSQL (DO Managed) | 15 |
| **Containers** | Docker | Latest |
| **Registry** | DigitalOcean Container Registry + GHCR | N/A |
| **Hosting** | DigitalOcean Droplets | Ubuntu 24.04 |

### Infrastructure Topology

```
┌──────────────────────────────────────────────────────────────┐
│                     GitHub Actions                           │
│  (Build, Test, Migrate, Deploy)                             │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────────────┐
│              DigitalOcean Container Registry                 │
│  registry.digitalocean.com/meatscentral/                     │
│    - projectmeats-frontend:dev-SHA                           │
│    - projectmeats-backend:dev-SHA                            │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ↓ (SSH Deploy)
┌──────────────────────────────────────────────────────────────┐
│              Frontend Server (dev/UAT/prod)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Nginx (Port 80/443)                                   │ │
│  │    ├── /api/** → Backend Server:8000                   │ │
│  │    └── /** → Frontend Container:8080                   │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Docker Container: pm-frontend                         │ │
│  │    - Port: 8080 → 80                                   │ │
│  │    - Image: projectmeats-frontend:dev-SHA              │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                       │
                       ↓ (Private Network / VPC)
┌──────────────────────────────────────────────────────────────┐
│              Backend Server (dev/UAT/prod)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Docker Container: pm-backend                          │ │
│  │    - Port: 8000                                        │ │
│  │    - Image: projectmeats-backend:dev-SHA               │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────────────┐
│         DigitalOcean Managed PostgreSQL Database             │
│  - Host: db-postgresql-nyc3-12345-do-user-123456-0.db...    │
│  - Port: 25060                                               │
│  - SSL: Required                                             │
└──────────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages

### Overview

The deployment pipeline follows this sequence:

```
Push to Branch
  ↓
1. Lint & Validate
  ↓
2. Build & Push Images (Parallel)
  ├── Frontend → DOCR + GHCR
  └── Backend → DOCR + GHCR
  ↓
3. Test (Parallel)
  ├── Frontend Tests (npm run test:ci)
  └── Backend Tests (python manage.py test)
  ↓
4. Migrate Database
  ├── SSH to Backend Server
  └── python manage.py migrate --fake-initial
  ↓
5. Deploy (Sequential)
  ├── Deploy Backend First
  │   ├── SSH to Backend Server
  │   ├── Pull Image (dev-SHA tag)
  │   ├── Stop Old Container
  │   ├── Start New Container
  │   └── Health Check (localhost:8000/api/v1/health/)
  │
  └── Deploy Frontend Second
      ├── SSH to Frontend Server
      ├── Pull Image (dev-SHA tag)
      ├── Stop Old Container
      ├── Start New Container
      ├── Configure Nginx
      └── Health Check (localhost:80)
  ↓
6. Post-Deployment
  └── Slack Notification (Success/Failure)
```

### 1. Lint & Validate

**Job:** `lint-yaml`

```yaml
- Run yamllint on .github/workflows/
- Fail fast on syntax errors
```

**Purpose:** Prevent invalid YAML from breaking CI/CD.

### 2. Build & Push Images

**Jobs:** `build-and-push (frontend)`, `build-and-push (backend)`

**Strategy:** Matrix build (parallel execution)

#### Frontend Build
```dockerfile
# Context: ./
# Dockerfile: frontend/dockerfile

FROM node:18-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

#### Backend Build
```dockerfile
# Context: ./
# Dockerfile: backend/dockerfile

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
EXPOSE 8000
CMD ["gunicorn", "projectmeats.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### Image Tagging Strategy

**Format:** `<environment>-<git-sha>`

| Environment | Tag Example | Registry |
|-------------|-------------|----------|
| Development | `dev-ae2bac0f98d6aae` | DOCR + GHCR |
| UAT | `uat-1234567890abcd` | DOCR + GHCR |
| Production | `prod-fedcba0987654` | DOCR + GHCR |

**Registries:**
- **Primary:** `registry.digitalocean.com/meatscentral/`
- **Secondary:** `ghcr.io/meats-central/`

**Rationale:**
- ✅ **Immutable** - SHA tag never changes
- ✅ **Traceable** - Direct link to Git commit
- ✅ **Rollback-friendly** - Redeploy any previous SHA
- ✅ **Redundancy** - Two registries prevent single point of failure

### 3. Test

**Jobs:** `test-frontend`, `test-backend`

**Strategy:** Parallel execution

#### Frontend Tests
```bash
cd frontend
npm ci
npm run test:ci      # Jest with coverage
npm run type-check   # TypeScript compiler
```

#### Backend Tests
```bash
cd backend
pip install -r requirements.txt
python manage.py test apps/ --verbosity=2
```

**Database:** GitHub Actions PostgreSQL service container (ephemeral)

**Gating:** Deployment blocked if any test fails.

### 4. Migrate Database

**Job:** `migrate`

**Environment:** `dev-backend` / `uat-backend` / `prod-backend`

**Execution Method:** SSH to backend server

```bash
# SSH into backend server
ssh user@backend-server << 'MIGRATE'
set -euo pipefail

cd /home/django/ProjectMeats/backend
source ../venv/bin/activate

# Run idempotent migrations
python manage.py migrate --fake-initial --noinput

MIGRATE
```

**Key Flags:**
- `--fake-initial` - Skip already-applied initial migrations (idempotent)
- `--noinput` - Non-interactive mode for CI/CD

**Why SSH?**
- Database firewall restricts access to deployment servers only
- No need to expose DB to 5,462 GitHub Actions IP ranges
- Uses server's existing `.env` configuration

**Error Handling:**
- Migration failure blocks deployment
- Exits with non-zero code
- Slack notification sent

### 5. Deploy

#### A. Deploy Backend

**Job:** `deploy-backend`

**Environment:** `dev-backend` / `uat-backend` / `prod-backend`

**Process:**
1. **SSH to Backend Server**
   ```bash
   ssh user@backend-server
   ```

2. **Pull Image**
   ```bash
   docker pull registry.digitalocean.com/meatscentral/projectmeats-backend:dev-SHA
   ```

3. **Stop Old Container**
   ```bash
   docker rm -f pm-backend || true
   ```

4. **Start New Container**
   ```bash
   docker run -d --name pm-backend \
     --restart unless-stopped \
     -p 8000:8000 \
     --env-file /home/django/ProjectMeats/backend/.env \
     -v /home/django/ProjectMeats/media:/app/media \
     -v /home/django/ProjectMeats/staticfiles:/app/staticfiles \
     registry.digitalocean.com/meatscentral/projectmeats-backend:dev-SHA
   ```

5. **Health Check** (Retry loop: 20 attempts × 5s = 100s max)
   ```bash
   curl -f http://localhost:8000/api/v1/health/
   ```

**Deployment Secrets (.env file):**
```ini
DJANGO_SETTINGS_MODULE=projectmeats.settings.production
SECRET_KEY=<django-secret-key>
DATABASE_URL=postgresql://user:pass@host:25060/db?sslmode=require
ALLOWED_HOSTS=backend.meatscentral.com,10.17.0.13
CORS_ALLOWED_ORIGINS=https://dev.meatscentral.com
LOG_LEVEL=INFO
```

#### B. Deploy Frontend

**Job:** `deploy-frontend`

**Environment:** `dev-frontend` / `uat-frontend` / `prod-frontend`

**Dependency:** Waits for `deploy-backend` to succeed

**Process:**
1. **SSH to Frontend Server**
   ```bash
   ssh user@frontend-server
   ```

2. **Create Runtime Config**
   ```javascript
   // /opt/pm/frontend/env/env-config.js
   window.ENV = {
     API_BASE_URL: "https://dev.meatscentral.com",
     ENVIRONMENT: "development"
   };
   ```

3. **Pull Image**
   ```bash
   docker pull registry.digitalocean.com/meatscentral/projectmeats-frontend:dev-SHA
   ```

4. **Stop Old Container**
   ```bash
   docker rm -f pm-frontend || true
   ```

5. **Start New Container**
   ```bash
   docker run -d --name pm-frontend \
     --restart unless-stopped \
     -p 8080:80 \
     --add-host backend:10.17.0.13 \
     -v /opt/pm/frontend/env/env-config.js:/usr/share/nginx/html/env-config.js:ro \
     registry.digitalocean.com/meatscentral/projectmeats-frontend:dev-SHA
   ```

6. **Configure Nginx Reverse Proxy**
   ```nginx
   # /etc/nginx/conf.d/pm-frontend.conf
   server {
       listen 80;
       server_name _;
       
       # Route API, Admin, Static to Backend
       location ~ ^/(api|admin|static)/ {
           proxy_pass http://10.17.0.13:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_connect_timeout 60s;
           proxy_read_timeout 60s;
       }
       
       # Route Everything Else to Frontend
       location / {
           proxy_pass http://127.0.0.1:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

7. **Reload Nginx**
   ```bash
   nginx -t && systemctl reload nginx
   ```

8. **Health Check** (Retry loop: 20 attempts × 5s = 100s max)
   ```bash
   curl -f http://localhost:80/
   ```

### 6. Post-Deployment

**Job:** Runs in both `deploy-backend` and `deploy-frontend`

**Actions:**
- Send Slack notification with status
- Include commit SHA, environment, duration
- On failure: Include error logs

---

## Environment Variables & Secrets

### GitHub Repository Secrets

**Location:** Settings → Secrets and variables → Actions

#### Infrastructure Secrets

| Secret Name | Description | Example | Used By |
|-------------|-------------|---------|---------|
| `DO_ACCESS_TOKEN` | DigitalOcean API token | `dop_v1_abc123...` | All workflows |
| `DEV_HOST` | Backend server IP/hostname | `157.245.114.182` | Dev deployment |
| `DEV_USER` | Backend SSH username | `django` | Dev deployment |
| `DEV_SSH_PASSWORD` | Backend SSH password | `********` | Dev deployment |
| `DEV_FRONTEND_HOST` | Frontend server IP/hostname | `104.131.186.75` | Dev deployment |
| `DEV_FRONTEND_USER` | Frontend SSH username | `root` | Dev deployment |
| `DEV_FRONTEND_SSH_KEY` | Frontend SSH private key (Ed25519) | `-----BEGIN...` | Dev deployment |
| `DEV_BACKEND_IP` | Backend private IP (for nginx) | `10.17.0.13` | Dev deployment |

#### Application Configuration Secrets

| Secret Name | Description | Example | Used By |
|-------------|-------------|---------|---------|
| `DEV_DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:25060/db?sslmode=require` | Dev backend |
| `DEV_SECRET_KEY` | Django secret key | `django-insecure-abc123...` | Dev backend |
| `DEV_DJANGO_SETTINGS_MODULE` | Django settings module | `projectmeats.settings.production` | Dev backend |
| `DEV_ALLOWED_HOSTS` | Allowed HTTP Host headers | `dev.meatscentral.com,10.17.0.13` | Dev backend |
| `DEV_CORS_ALLOWED_ORIGINS` | CORS allowed origins | `https://dev.meatscentral.com` | Dev backend |
| `VITE_API_BASE_URL` | Frontend API base URL (Vite build) | `https://dev.meatscentral.com` | Dev frontend |

#### Optional Secrets

| Secret Name | Description | Default | Used By |
|-------------|-------------|---------|---------|
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications | N/A | All workflows |
| `LOG_LEVEL` | Django logging level | `INFO` | All backends |
| `DB_ENGINE` | Django DB engine | `django.db.backends.postgresql` | All backends |

### Environment-Specific Secrets

Secrets are prefixed by environment:
- `DEV_*` - Development
- `UAT_*` - UAT/Staging
- `PROD_*` - Production

**Example:**
```
DEV_DATABASE_URL=postgresql://dev_user:dev_pass@dev-db:25060/dev_db
UAT_DATABASE_URL=postgresql://uat_user:uat_pass@uat-db:25060/uat_db
PROD_DATABASE_URL=postgresql://prod_user:prod_pass@prod-db:25060/prod_db
```

### Required GitHub Actions Variables

**Location:** Settings → Secrets and variables → Actions → Variables

| Variable Name | Description | Example |
|---------------|-------------|---------|
| `DOCR_REGISTRY` | DigitalOcean registry URL | `registry.digitalocean.com/meatscentral` |
| `DOCR_REPO_FRONTEND` | Frontend image name | `projectmeats-frontend` |
| `DOCR_REPO_BACKEND` | Backend image name | `projectmeats-backend` |

---

## Operational Commands

### Deploying to Environments

#### Development
```bash
# Automatic on merge to development branch
git checkout development
git merge feature/my-feature
git push origin development

# Watch deployment
gh run watch
```

#### UAT
```bash
# Automatic PR created after dev deployment succeeds
# Review and merge: development → uat PR
gh pr list --base uat
gh pr merge <PR-NUMBER> --squash

# Watch deployment
gh run watch
```

#### Production
```bash
# Automatic PR created after UAT deployment succeeds
# Review and merge: uat → main PR
gh pr list --base main
gh pr merge <PR-NUMBER> --squash

# Watch deployment
gh run watch
```

### Manual Deployment Trigger

```bash
# Trigger deployment workflow manually
gh workflow run "11-dev-deployment.yml" --ref development
gh workflow run "12-uat-deployment.yml" --ref uat
gh workflow run "13-prod-deployment.yml" --ref main
```

### Rollback Procedure

**Method 1: Re-run Previous Successful Workflow**

```bash
# Find last successful deployment
gh run list --workflow "11-dev-deployment.yml" --limit 10

# Re-run by ID
gh run rerun <RUN_ID>
```

**Method 2: Deploy Previous Commit SHA**

```bash
# Find previous working commit
git log --oneline -10

# Create rollback branch
git checkout -b rollback/emergency-<date>
git reset --hard <WORKING_COMMIT_SHA>
git push -f origin rollback/emergency-<date>

# Create PR and merge (triggers deployment)
gh pr create --base development --head rollback/emergency-<date>
```

**Method 3: Manual Container Rollback (Emergency)**

```bash
# SSH to server
ssh user@backend-server

# Find previous image
docker images | grep projectmeats-backend

# Stop current
docker rm -f pm-backend

# Start previous image
docker run -d --name pm-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file /home/django/ProjectMeats/backend/.env \
  -v /home/django/ProjectMeats/media:/app/media \
  -v /home/django/ProjectMeats/staticfiles:/app/staticfiles \
  registry.digitalocean.com/meatscentral/projectmeats-backend:dev-<PREVIOUS_SHA>
```

### Viewing Logs

#### GitHub Actions Logs
```bash
# View workflow run logs
gh run view <RUN_ID> --log

# Follow live run
gh run watch <RUN_ID>

# Get failed job logs
gh run view <RUN_ID> --log-failed
```

#### Container Logs
```bash
# SSH to server
ssh user@backend-server

# View backend logs
docker logs pm-backend --tail 100 -f

# View frontend logs
ssh user@frontend-server
docker logs pm-frontend --tail 100 -f

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log
```

### Database Operations

#### Running Migrations Manually

```bash
# SSH to backend server
ssh user@backend-server

cd /home/django/ProjectMeats/backend
source ../venv/bin/activate

# Check migration status
python manage.py showmigrations

# Create new migrations (development only)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Rollback last migration
python manage.py migrate <app_name> <previous_migration_number>
```

#### Database Backup (via DigitalOcean Console)

```bash
# Automated daily backups configured in DO console
# Manual backup:
# 1. Go to DigitalOcean Console
# 2. Databases → Select database
# 3. Backups → Create Backup
```

### Container Management

#### Restart Containers
```bash
# Backend
ssh user@backend-server
docker restart pm-backend

# Frontend
ssh user@frontend-server
docker restart pm-frontend
```

#### View Container Stats
```bash
docker stats pm-backend pm-frontend
```

#### Shell into Container
```bash
# Backend Django shell
docker exec -it pm-backend python manage.py shell

# Backend bash
docker exec -it pm-backend bash

# Frontend bash
docker exec -it pm-frontend sh
```

---

## Troubleshooting

### Common Issues

#### 1. Health Check Fails After Deployment

**Symptoms:**
```
✗ Backend health check failed after 20 attempts (HTTP 000)
```

**Diagnosis:**
```bash
ssh user@backend-server
docker logs pm-backend --tail 50
docker ps | grep pm-backend
curl http://localhost:8000/api/v1/health/
```

**Common Causes:**
- Container crashed on startup (check logs)
- Database connection failure (check `DATABASE_URL`)
- Migration not applied (run `python manage.py migrate`)
- Port 8000 already in use (check `netstat -tlnp | grep 8000`)

**Resolution:**
```bash
# Restart container
docker restart pm-backend

# Or redeploy with correct config
docker rm -f pm-backend
docker run -d --name pm-backend ... <correct-image-tag>
```

#### 2. Frontend Shows 502 Bad Gateway

**Symptoms:**
```
Browser: 502 Bad Gateway (nginx error)
```

**Diagnosis:**
```bash
ssh user@frontend-server
tail -f /var/log/nginx/error.log
curl http://localhost:8000/api/v1/health/  # Test backend
curl http://localhost:8080/  # Test frontend container
```

**Common Causes:**
- Backend server not reachable (check `DEV_BACKEND_IP`)
- Backend container not running
- Nginx misconfiguration

**Resolution:**
```bash
# Fix nginx config
sudo nano /etc/nginx/conf.d/pm-frontend.conf
sudo nginx -t && sudo systemctl reload nginx

# Restart backend
ssh user@backend-server
docker restart pm-backend
```

#### 3. Database Migration Fails

**Symptoms:**
```
django.db.utils.OperationalError: could not connect to server
```

**Diagnosis:**
```bash
ssh user@backend-server
cd /home/django/ProjectMeats/backend
cat .env | grep DATABASE_URL
psql "$DATABASE_URL" -c "SELECT version();"
```

**Common Causes:**
- `DATABASE_URL` incorrect or expired
- Database server down (check DO console)
- SSL certificate issue (ensure `?sslmode=require`)
- Firewall blocking connection

**Resolution:**
```bash
# Update DATABASE_URL in .env
nano /home/django/ProjectMeats/backend/.env

# Test connection
psql "$DATABASE_URL" -c "\\dt"

# Re-run migrations
python manage.py migrate
```

#### 4. Build Fails in GitHub Actions

**Symptoms:**
```
Error: failed to solve: process "/bin/sh -c npm run build" did not complete successfully
```

**Diagnosis:**
```bash
# Check workflow logs
gh run view <RUN_ID> --log

# Test build locally
cd frontend
npm ci
npm run build
```

**Common Causes:**
- TypeScript errors
- Missing dependencies in `package.json`
- Environment variable not set
- Out of memory during build

**Resolution:**
```bash
# Fix TypeScript errors
npm run type-check

# Update dependencies
npm install <missing-package>

# Commit and push fix
git add .
git commit -m "fix: resolve build issues"
git push
```

#### 5. Docker Image Pull Fails

**Symptoms:**
```
Error: failed to pull image: unauthorized
```

**Diagnosis:**
```bash
# Test Docker login
echo "$DO_ACCESS_TOKEN" | docker login registry.digitalocean.com -u "$DO_ACCESS_TOKEN" --password-stdin
```

**Common Causes:**
- `DO_ACCESS_TOKEN` expired or incorrect
- Image doesn't exist (wrong tag)
- Registry permissions issue

**Resolution:**
```bash
# Generate new DO token
# 1. Go to DigitalOcean Console
# 2. API → Tokens/Keys → Generate New Token
# 3. Update DO_ACCESS_TOKEN secret in GitHub

# Or manually pull and tag
docker pull registry.digitalocean.com/meatscentral/projectmeats-backend:dev-SHA
```

### Debug Checklist

When deployment fails, check in this order:

- [ ] **GitHub Actions Status** - All jobs green?
  ```bash
  gh run view <RUN_ID>
  ```

- [ ] **Container Status** - Containers running?
  ```bash
  ssh user@backend-server "docker ps | grep pm-"
  ```

- [ ] **Container Logs** - Any errors?
  ```bash
  ssh user@backend-server "docker logs pm-backend --tail 50"
  ```

- [ ] **Health Endpoints** - Responding?
  ```bash
  curl http://localhost:8000/api/v1/health/
  curl http://localhost:80/
  ```

- [ ] **Database Connection** - DB accessible?
  ```bash
  psql "$DATABASE_URL" -c "SELECT 1;"
  ```

- [ ] **Nginx Config** - Valid?
  ```bash
  ssh user@frontend-server "sudo nginx -t"
  ```

- [ ] **Environment Variables** - All secrets set?
  ```bash
  gh secret list
  ```

- [ ] **Firewall Rules** - Ports open?
  ```bash
  sudo ufw status
  ```

---

## Future Enhancements

### Planned Improvements

#### 1. Migration Runner in GitHub Actions

**Current State:**
- Migrations run via SSH on the deployment server
- Depends on server's Python environment and `.env` file

**Proposed Change:**
```yaml
migrate:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: pip install -r backend/requirements.txt
    - name: Run migrations
      env:
        DATABASE_URL: ${{ secrets.DEV_DATABASE_URL }}
        SECRET_KEY: ${{ secrets.DEV_SECRET_KEY }}
      run: python manage.py migrate --fake-initial --noinput
```

**Benefits:**
- ✅ No SSH dependency
- ✅ Consistent environment (GitHub Runner)
- ✅ Better error visibility in CI logs
- ✅ Easier to debug (reproducible locally)

**Requirements:**
- Database firewall must allow GitHub Actions IP ranges
- OR use GitHub-hosted runner in DigitalOcean VPC

**Implementation Timeline:** Q1 2026

---

#### 2. Secret Management Upgrade

**Current State:**
- Secrets stored in `.env` file on deployment servers
- File persists on disk (security risk)
- Manual updates required per server

**Proposed Change:**
```bash
# Option A: AWS Secrets Manager
docker run -d --name pm-backend \
  --env-file <(aws secretsmanager get-secret-value --secret-id prod/backend --query SecretString --output text) \
  registry.digitalocean.com/meatscentral/projectmeats-backend:prod-SHA

# Option B: HashiCorp Vault
docker run -d --name pm-backend \
  --env-file <(vault kv get -format=json secret/prod/backend | jq -r '.data.data | to_entries[] | "\(.key)=\(.value)"') \
  registry.digitalocean.com/meatscentral/projectmeats-backend:prod-SHA

# Option C: Docker Secrets (Swarm/Compose)
docker stack deploy -c docker-compose.prod.yml projectmeats
```

**Benefits:**
- ✅ No secrets on disk
- ✅ Automatic rotation
- ✅ Audit logging
- ✅ Centralized management
- ✅ Encryption at rest and in transit

**Requirements:**
- Secret manager infrastructure setup
- Migration of existing secrets
- Updated deployment scripts

**Implementation Timeline:** Q2 2026

---

#### 3. Orchestration with Zero-Downtime Rollouts

**Current State:**
- `docker rm -f` stops old container immediately
- Brief downtime during container swap (~5-10 seconds)
- No health check before routing traffic

**Proposed Change:**

**Option A: Docker Compose with Rolling Updates**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: registry.digitalocean.com/meatscentral/projectmeats-backend:${TAG}
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      rollback_config:
        parallelism: 1
        delay: 10s
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
```

**Option B: Dokku (Lightweight PaaS)**
```bash
# One-time setup
dokku apps:create projectmeats-backend
dokku docker-options:add projectmeats-backend deploy "--env-file /var/lib/dokku/data/dokku-global-config/.env"

# Deploy (automatic zero-downtime)
dokku git:from-image projectmeats-backend registry.digitalocean.com/meatscentral/projectmeats-backend:prod-SHA
```

**Option C: Kubernetes (Full Orchestration)**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: backend
        image: registry.digitalocean.com/meatscentral/projectmeats-backend:prod-SHA
        livenessProbe:
          httpGet:
            path: /api/v1/health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**Benefits:**
- ✅ Zero-downtime deployments
- ✅ Automatic rollback on health check failure
- ✅ Multiple replicas for high availability
- ✅ Load balancing built-in
- ✅ Self-healing (restarts failed containers)

**Requirements:**
- Orchestrator infrastructure setup (Dokku/Portainer/K8s)
- Stateless application design (already implemented)
- Health check endpoints (already implemented)
- Load balancer configuration

**Recommendation:** Start with Dokku (simplest), migrate to K8s if scale requires.

**Implementation Timeline:** Q2-Q3 2026

---

### Nice-to-Have Enhancements

#### 4. Automated Rollback on Failed Health Checks

**Concept:**
```bash
# If new deployment fails health checks
# Automatically revert to previous working image
if ! health_check_passes; then
  docker rm -f pm-backend
  docker run -d --name pm-backend ... <PREVIOUS_WORKING_IMAGE>
  send_alert "Deployment failed, auto-rolled back"
fi
```

#### 5. Canary Deployments

**Concept:**
```bash
# Deploy new version to 10% of traffic
# Monitor error rates for 10 minutes
# If stable, route 100% traffic to new version
# If unstable, rollback automatically
```

#### 6. Database Migration Dry-Run

**Concept:**
```bash
# Before applying migrations, run in --plan mode
python manage.py migrate --plan
# Show SQL that will be executed
python manage.py sqlmigrate app_name migration_name
# Require manual approval for destructive changes
```

#### 7. Container Image Scanning

**Concept:**
```yaml
- name: Scan image for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'registry.digitalocean.com/meatscentral/projectmeats-backend:dev-SHA'
    severity: 'CRITICAL,HIGH'
```

---

## Appendix

### Related Documentation

- [Database Migration Guide](./DATABASE_MIGRATION_GUIDE.md) - Detailed migration procedures
- [Deployment Runbook](./DEPLOYMENT_RUNBOOK.md) - Step-by-step deployment instructions
- [Architecture Diagram](./ARCHITECTURE.md) - System architecture overview
- [Contributing Guide](../CONTRIBUTING.md) - Development guidelines
- [GitHub Secrets Configuration](./GITHUB_SECRETS_CONFIGURATION.md) - Secret setup guide

### Workflow Files

- `.github/workflows/11-dev-deployment.yml` - Development deployment
- `.github/workflows/12-uat-deployment.yml` - UAT deployment
- `.github/workflows/13-prod-deployment.yml` - Production deployment
- `.github/workflows/promote-dev-to-uat.yml` - Auto-promotion to UAT
- `.github/workflows/promote-uat-to-main.yml` - Auto-promotion to Production

### Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-09 | 1.0.0 | Initial source of truth document created |

---

**Questions or Issues?**
- Open an issue: https://github.com/Meats-Central/ProjectMeats/issues
- Slack: #projectmeats-dev
- Email: dev-team@meatscentral.com

---

*This document is the single source of truth for development workflows. All other deployment documentation should reference this document or be considered deprecated.*
