# Development Pipeline - Source of Truth

**Last Updated:** 2025-12-09  
**Status:** ✅ Production Ready  
**Version:** 2.0.0

---

## 🎯 Overview

This document is the **single source of truth** for the ProjectMeats development and deployment pipeline. All other documentation should reference this document or be considered deprecated.

**Quick Links:**
- [Architecture](#architecture)
- [Pipeline Stages](#pipeline-stages)
- [Secrets Configuration](#secrets-configuration)
- [Operational Commands](#operational-commands)
- [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture

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

**✅ WE USE:**
- Standard Django models with `tenant` ForeignKey
- Shared PostgreSQL `public` schema
- QuerySet filtering: `filter(tenant=request.tenant)`
- Standard migrations: `python manage.py migrate`

**❌ WE DO NOT USE:**
- `django-tenants` package
- `schema_context()` or `connection.schema_name`
- `migrate_schemas` commands
- Separate PostgreSQL schemas per tenant
- `TenantMixin` or `DomainMixin`

### Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend** | Django + DRF | 5.x |
| **Frontend** | React + TypeScript | 19 / 5.9 |
| **Database** | PostgreSQL (DO Managed) | 15 |
| **Containers** | Docker | Latest |
| **Registry** | DigitalOcean Container Registry | N/A |
| **Hosting** | DigitalOcean Droplets | Ubuntu 24.04 |

---

## 🔄 Pipeline Stages

### Workflow Architecture

```
Push to Branch (development/uat/main)
  ↓
[main-pipeline.yml]
  ├─→ Build Once
  │    ├─ Frontend Image → DOCR (dev-SHA)
  │    └─ Backend Image → DOCR (dev-SHA)
  │
  ├─→ Test (Parallel)
  │    ├─ Frontend Tests (SKIPPED - pending Vitest migration)
  │    └─ Backend Tests (pytest)
  │
  ├─→ Migrate (SSH to Backend Server)
  │    └─ python manage.py migrate --fake-initial --noinput
  │
  └─→ Deploy (Sequential)
       ├─ Backend First
       │   ├─ SSH to backend server
       │   ├─ Pull image (dev-SHA)
       │   ├─ Stop old container
       │   ├─ Start new container
       │   └─ Health check
       │
       └─ Frontend Second
           ├─ SSH to frontend server
           ├─ Generate env-config.js (runtime config)
           ├─ Pull image (dev-SHA)
           ├─ Stop old container
           ├─ Start new container (mount env-config.js)
           ├─ Configure nginx
           └─ Health check
```

### Key Features

**✅ Build Once, Deploy Many**
- Single Docker image built per commit (tagged with SHA)
- Same image deployed to Dev → UAT → Prod
- No rebuild between environments
- Frontend environment variables injected at runtime (not build-time)

**✅ SSH-Based Migrations**
- Migrations run on deployment server (not GitHub runner)
- Database firewall restricts access to deployment servers only
- No need to whitelist 5,462 GitHub Actions IP ranges
- Uses server's existing `.env` configuration

**✅ Idempotent Operations**
- `--fake-initial` flag prevents duplicate migration errors
- Can safely re-run deployments
- No downtime from repeated attempts

---

## 🔒 Secrets Configuration

### GitHub Environment Secrets

Secrets are **environment-scoped** using GitHub Environments:

| Environment Name | Branch | Purpose |
|------------------|--------|---------|
| `dev-backend` | `development` | Development backend secrets |
| `dev-frontend` | `development` | Development frontend secrets |
| `uat2-backend` | `uat` | UAT backend secrets |
| `uat2-frontend` | `uat` | UAT frontend secrets |
| `prod2-backend` | `main` | Production backend secrets |
| `prod2-frontend` | `main` | Production frontend secrets |

### Required Secrets Per Environment

#### Backend Environment Secrets
```
DEV_DATABASE_URL          # PostgreSQL connection string
DEV_SECRET_KEY            # Django secret key
DEV_DJANGO_SETTINGS_MODULE # projectmeats.settings.production
DEV_HOST                  # Backend server IP
DEV_USER                  # SSH username
DEV_SSH_PASSWORD          # SSH password
```

#### Frontend Environment Secrets
```
DEV_FRONTEND_HOST         # Frontend server IP
DEV_FRONTEND_USER         # SSH username
DEV_FRONTEND_SSH_KEY      # SSH private key (Ed25519)
DEV_BACKEND_IP            # Backend private IP (for nginx proxy)
VITE_API_BASE_URL         # Runtime API URL (for env-config.js)
```

#### Repository Secrets (Shared)
```
DO_ACCESS_TOKEN           # DigitalOcean API token
SLACK_WEBHOOK_URL         # (Optional) Deployment notifications
```

### Secret Naming Pattern

**Format:** `{ENV}_{COMPONENT}_{SECRET_NAME}`

Examples:
- Development: `DEV_DATABASE_URL`, `DEV_FRONTEND_HOST`
- UAT: `UAT_DATABASE_URL`, `UAT_FRONTEND_HOST`
- Production: `PROD_DATABASE_URL`, `PROD_FRONTEND_HOST`

---

## 🚀 Operational Commands

### Triggering Deployments

#### Automatic Deployment (Recommended)
```bash
# Development
git checkout development
git merge feature/my-feature
git push origin development
# → Triggers deployment to dev automatically

# UAT
# Merge the auto-created PR: development → uat
gh pr list --base uat
gh pr merge <PR-NUMBER> --squash
# → Triggers deployment to UAT

# Production
# Merge the auto-created PR: uat → main
gh pr list --base main
gh pr merge <PR-NUMBER> --squash
# → Triggers deployment to production
```

#### Manual Deployment
```bash
# Trigger via GitHub CLI
gh workflow run "Master Pipeline" --ref development

# Or via web interface
# Actions → Master Pipeline → Run workflow → Select branch
```

### Monitoring Deployments

```bash
# Watch live deployment
gh run watch

# View recent runs
gh run list --workflow "Master Pipeline" --limit 10

# View specific run details
gh run view <RUN_ID>

# Get failed job logs
gh run view <RUN_ID> --log-failed
```

### Rollback Procedures

#### Method 1: Re-run Previous Workflow
```bash
# Find last successful deployment
gh run list --workflow "Master Pipeline" --status success --limit 5

# Re-run by ID
gh run rerun <RUN_ID>
```

#### Method 2: Emergency Container Rollback
```bash
# SSH to backend server
ssh django@backend-server

# Find previous image
docker images | grep projectmeats-backend

# Stop current
docker rm -f pm-backend

# Start previous SHA
docker run -d --name pm-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file /home/django/ProjectMeats/backend/.env \
  registry.digitalocean.com/meatscentral/projectmeats-backend:dev-<PREVIOUS_SHA>
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Health Check Fails

**Symptoms:**
```
✗ Backend health check failed after 20 attempts
```

**Diagnosis:**
```bash
ssh django@backend-server
docker logs pm-backend --tail 50
curl http://localhost:8000/api/v1/health/
```

**Common Causes:**
- Container crashed on startup
- Database connection failure
- Migration not applied
- Port conflict

**Fix:**
```bash
docker restart pm-backend
# Or check logs and redeploy
```

#### 2. Frontend Shows 502 Bad Gateway

**Symptoms:**
```
Browser: 502 Bad Gateway (nginx)
```

**Diagnosis:**
```bash
ssh root@frontend-server
tail -f /var/log/nginx/error.log
curl http://localhost:8000/api/v1/health/  # Test backend
curl http://localhost:8080/  # Test frontend
```

**Fix:**
```bash
# Check nginx config
sudo nginx -t
sudo systemctl reload nginx

# Check backend reachability
ping <backend-private-ip>
curl http://<backend-private-ip>:8000/api/v1/health/
```

#### 3. Migration Fails

**Symptoms:**
```
django.db.utils.OperationalError: connection timeout
```

**Diagnosis:**
```bash
ssh django@backend-server
cd /home/django/ProjectMeats/backend
cat .env | grep DATABASE_URL
psql "$DATABASE_URL" -c "SELECT 1;"
```

**Fix:**
```bash
# Update DATABASE_URL if incorrect
nano .env

# Test connection
psql "$DATABASE_URL" -c "\\dt"

# Re-run migrations manually
python manage.py migrate --fake-initial --noinput
```

#### 4. Frontend Environment Variables Wrong

**Symptoms:**
```
Frontend API calls go to wrong URL (e.g., localhost instead of backend)
```

**Diagnosis:**
```bash
ssh root@frontend-server
cat /opt/pm/frontend/env/env-config.js
# Should show correct API_BASE_URL for environment
```

**Fix:**
```bash
# Regenerate env-config.js manually
cat > /opt/pm/frontend/env/env-config.js << 'EOF'
window.ENV = {
  API_BASE_URL: "https://dev.meatscentral.com",
  ENVIRONMENT: "development"
};
EOF

# Restart frontend container
docker restart pm-frontend
```

### Debug Checklist

When deployment fails, check in this order:

- [ ] **GitHub Actions Status** - All jobs green?
  ```bash
  gh run view <RUN_ID>
  ```

- [ ] **Containers Running?**
  ```bash
  ssh django@backend-server "docker ps | grep pm-"
  ssh root@frontend-server "docker ps | grep pm-"
  ```

- [ ] **Container Logs** - Any errors?
  ```bash
  ssh django@backend-server "docker logs pm-backend --tail 50"
  ssh root@frontend-server "docker logs pm-frontend --tail 50"
  ```

- [ ] **Health Endpoints** - Responding?
  ```bash
  curl http://dev.meatscentral.com/api/v1/health/
  curl http://dev.meatscentral.com/
  ```

- [ ] **Database Connection** - Accessible from server?
  ```bash
  ssh django@backend-server
  psql "$DATABASE_URL" -c "SELECT 1;"
  ```

- [ ] **Nginx Config** - Valid?
  ```bash
  ssh root@frontend-server "sudo nginx -t"
  ```

- [ ] **Environment Secrets** - All set correctly?
  ```bash
  gh secret list --env dev-backend
  gh secret list --env dev-frontend
  ```

---

## 🔮 Future Enhancements

### Planned Improvements

#### 1. Frontend Test Migration (Q1 2026)
**Current State:** Frontend tests skipped (Jest → Vitest migration pending)

**Action Items:**
- [ ] Migrate test framework from Jest to Vitest
- [ ] Replace `require()` with ES6 `import`
- [ ] Replace `jest.fn()` with `vi.fn()`
- [ ] Update test configuration
- [ ] Re-enable frontend tests in pipeline

#### 2. Runner-Based Migrations (Q1 2026)
**Current State:** Migrations run via SSH on deployment server

**Proposed:**
```yaml
migrate:
  runs-on: ubuntu-latest
  steps:
    - name: Run migrations from GitHub Runner
      env:
        DATABASE_URL: ${{ secrets.DEV_DATABASE_URL }}
      run: python manage.py migrate --fake-initial --noinput
```

**Requirements:**
- Database firewall must allow GitHub Actions IP ranges
- OR use self-hosted runner in DigitalOcean VPC
- OR use VPN/bastion for GitHub-hosted runners

**Benefits:**
- ✅ No SSH dependency
- ✅ Consistent environment
- ✅ Better error visibility
- ✅ Easier to debug locally

#### 3. Secret Management Upgrade (Q2 2026)
**Current State:** Secrets in `.env` files on servers

**Proposed:** Migrate to AWS Secrets Manager or HashiCorp Vault

**Benefits:**
- ✅ No secrets on disk
- ✅ Automatic rotation
- ✅ Audit logging
- ✅ Centralized management

#### 4. Zero-Downtime Deployments (Q2-Q3 2026)
**Current State:** Brief downtime during container swap

**Proposed Options:**
- **Option A:** Docker Compose with rolling updates
- **Option B:** Dokku (lightweight PaaS)
- **Option C:** Kubernetes

**Benefits:**
- ✅ Zero-downtime rollouts
- ✅ Automatic rollback on health check failure
- ✅ Multiple replicas for HA
- ✅ Self-healing containers

---

## 📚 Related Documentation

- [GitHub Secrets Configuration](./GITHUB_SECRETS_CONFIGURATION.md) - How to set up secrets
- [Architecture](./ARCHITECTURE.md) - System architecture overview
- [Contributing Guide](../CONTRIBUTING.md) - Development guidelines
- [Next Steps](./.github/NEXT_STEPS.md) - Immediate follow-up tasks

### Workflow Files

- `.github/workflows/main-pipeline.yml` - Orchestrator (triggers deployments)
- `.github/workflows/reusable-deploy.yml` - Worker (executes deployment logic)

### Archived Documentation

Obsolete docs have been moved to `docs/archive/legacy_2025/`:
- `GOLDEN_PIPELINE_REFERENCE.md` (superseded by this document)
- `DATABASE_MIGRATION_GUIDE.md` (contained outdated django-tenants references)
- `TENANT_ONBOARDING.md` (referenced schema creation - not applicable)

---

## 📝 Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-09 | 2.0.0 | Finalized after successful pipeline stabilization |
| 2025-12-09 | 1.0.0 | Initial source of truth document created |

---

**Questions or Issues?**
- Open an issue: https://github.com/Meats-Central/ProjectMeats/issues
- View workflow runs: https://github.com/Meats-Central/ProjectMeats/actions

---

*This document is the single source of truth for the development pipeline. All other deployment documentation should reference this document or be considered deprecated.*
