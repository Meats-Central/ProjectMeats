# Development Pipeline - Source of Truth

**Last Updated:** 2025-12-09  
**Status:** ✅ Production Ready  
**Version:** 3.0.0 (Bastion Tunnel Migration)

---

## 🎯 Overview

This document is the **single source of truth** for the ProjectMeats development and deployment pipeline. All other documentation should reference this document or be considered deprecated.

**Environment Manifest:** All secrets and environment variables are defined in [`config/env.manifest.json`](../config/env.manifest.json). See the [Secret Management](#secrets-configuration) section for details.

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

### Database Access Architecture

**Bastion Tunnel Mode (v3.0)**

```
┌─────────────────┐                ┌──────────────┐                ┌────────────────────┐
│ GitHub Runner   │   SSH Tunnel   │ Bastion Host │   Private Net  │ Managed Database   │
│                 │ ──────────────>│ (Droplet)    │ ──────────────>│ (Private Network)  │
│ localhost:5433  │   Port Forward │              │   5432         │ PostgreSQL         │
└─────────────────┘                └──────────────┘                └────────────────────┘
        │
        │ Docker --network host
        ▼
┌─────────────────┐
│ Docker Container│
│ (Backend Image) │
│                 │
│ DATABASE_URL=   │
│ postgresql://   │
│ user:pass@      │
│ 127.0.0.1:5433  │
└─────────────────┘
```

**Flow:**
1. GitHub runner creates SSH tunnel: `127.0.0.1:5433 → bastion → database:5432`
2. Runner pulls backend Docker image
3. Runner runs container with `--network host` to access tunnel
4. Container connects to `127.0.0.1:5433` (which tunnels to real database)
5. Migrations execute inside container
6. Tunnel cleaned up after completion

**Why This Works:**
- Database firewall only allows bastion host (not 5,462 GitHub IPs)
- Migrations run in Docker (same environment as deployment)
- Fully decoupled from deployment servers
- No venv/Python setup needed on runners

---

## 🔄 Pipeline Stages

### Workflow Architecture

```
Push to Branch (development/uat/main)
  ↓
[main-pipeline.yml] → [reusable-deploy.yml]
  ├─→ Build Once
  │    ├─ Frontend Image → DOCR (dev-SHA)
  │    └─ Backend Image → DOCR (dev-SHA)
  │
  ├─→ Test (Parallel)
  │    ├─ Frontend Tests (SKIPPED - pending Vitest migration)
  │    └─ Backend Tests (pytest)
  │
  ├─→ Migrate (Bastion Tunnel Mode)
  │    ├─ Create SSH tunnel: Runner → Bastion → Database
  │    ├─ Pull backend Docker image
  │    ├─ Run migrations in Docker container (--network host)
  │    └─ Cleanup tunnel
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

**✅ Bastion Tunnel Migrations (Runner-Based)**
- Migrations run **on GitHub runner** using Docker container
- SSH tunnel: `Runner → Bastion → Private Database`
- Database firewall restricts access to bastion host only
- No need to whitelist 5,462 GitHub Actions IP ranges
- Uses `--network host` for Docker container to access tunnel
- Fully decoupled from deployment servers

**✅ Idempotent Operations**
- `--fake-initial` flag prevents duplicate migration errors
- Can safely re-run deployments
- No downtime from repeated attempts

---

## 🔒 Secrets Configuration

### Environment Manifest (Single Source of Truth)

**📖 Complete Documentation**: [`docs/CONFIGURATION_AND_SECRETS.md`](CONFIGURATION_AND_SECRETS.md)

**All secrets and environment variables are defined in [`config/env.manifest.json`](../config/env.manifest.json) (v3.3).**

This manifest provides:
- Explicit mapping of runtime variables to GitHub Secrets
- Documentation of legacy naming inconsistencies
- Frontend environment variable support
- Automated secret auditing capabilities

**Audit Command (Run Before Deployments):**
```bash
python config/manage_env.py audit
```

### Quick Reference

For detailed information on:
- How secrets are resolved (environment + global)
- Legacy exceptions (STAGING_*, SSH_PASSWORD)
- Adding new environment variables
- Troubleshooting missing secrets

**See**: [`docs/CONFIGURATION_AND_SECRETS.md`](CONFIGURATION_AND_SECRETS.md)

### GitHub Environment Secrets

Secrets are **environment-scoped** using GitHub Environments:

| Environment Name | Branch | Purpose | Prefix |
|------------------|--------|---------|--------|
| `dev-backend` | `development` | Development backend secrets | `DEV` |
| `dev-frontend` | `development` | Development frontend secrets | `DEV` |
| `uat2-backend` | `uat` | UAT backend secrets | `UAT` |
| `uat2` | `uat` | UAT frontend secrets | `STAGING` ⚠️ |
| `prod2-backend` | `main` | Production backend secrets | `PROD` |
| `prod2-frontend` | `main` | Production frontend secrets | `PROD` |

⚠️ **Note**: UAT frontend uses legacy `STAGING_*` prefix and environment name `uat2` (not `uat2-frontend`). See manifest for details.

### Required Secrets Per Environment

**⚠️ Important:** All secret names below are defined in `config/env.manifest.json`. Never guess secret names—always reference the manifest or run the audit tool.

#### Backend Environment Secrets (from manifest)

**Infrastructure:**
```bash
DEV_HOST              # Bastion/Droplet IP (from manifest: BASTION_HOST)
DEV_USER              # SSH Username (from manifest: BASTION_USER)
DEV_SSH_PASSWORD      # SSH Password (from manifest: BASTION_SSH_PASSWORD)
DEV_DB_HOST           # Private Database Hostname (from manifest: DB_HOST pattern)
```

**Application:**
```bash
DEV_DATABASE_URL      # PostgreSQL connection string (from manifest: DATABASE_URL)
DEV_SECRET_KEY        # Django secret key (from manifest: SECRET_KEY pattern)
DEV_DB_USER           # Database username
DEV_DB_PASSWORD       # Database password
DEV_DB_NAME           # Database name
DEV_DB_PORT           # Database port (default: 5432)
```

**Computed Values (from environment config):**
```bash
# DJANGO_SETTINGS_MODULE is derived from manifest:
# dev-backend → projectmeats.settings.development
# uat2-backend → projectmeats.settings.staging
# prod2-backend → projectmeats.settings.production
```

#### Frontend Environment Secrets

```bash
DEV_FRONTEND_HOST     # Frontend server IP
DEV_FRONTEND_USER     # SSH username
DEV_FRONTEND_SSH_KEY  # SSH private key (Ed25519)
DEV_BACKEND_IP        # Backend private IP (for nginx proxy)
REACT_APP_API_BASE_URL # Runtime API URL (same name, environment-scoped)
```

#### Repository Secrets (Shared)
```bash
DO_ACCESS_TOKEN       # DigitalOcean API token
```

### Legacy Naming Patterns (Documented in Manifest)

**SSH Password Inconsistency:**
- Dev: `DEV_SSH_PASSWORD` (unique)
- UAT: `SSH_PASSWORD` (shared with Prod)
- Prod: `SSH_PASSWORD` (shared with UAT)

**Reason:** UAT and Prod share infrastructure historically.

### Secret Naming Pattern

**Format:** `{PREFIX}_{SECRET_NAME}`

Where `{PREFIX}` comes from `config/env.manifest.json`:
- `DEV` for development
- `UAT` for uat2-backend/uat2-frontend
- `PROD` for prod2-backend/prod2-frontend

**Examples:**
```bash
# Pattern-based (from manifest ci_secret_pattern)
{PREFIX}_SECRET_KEY → DEV_SECRET_KEY, UAT_SECRET_KEY, PROD_SECRET_KEY
{PREFIX}_DB_HOST → DEV_DB_HOST, UAT_DB_HOST, PROD_DB_HOST

# Explicit mapping (from manifest ci_secret_mapping)
BASTION_HOST:
  dev-backend → DEV_HOST
  uat2-backend → UAT_HOST
  prod2-backend → PROD_HOST
```

### Adding New Secrets

1. **Update manifest first:**
   ```bash
   vim config/env.manifest.json
   ```

2. **Add to GitHub:**
   ```bash
   gh secret set DEV_NEW_SECRET --body "value" --env dev-backend
   ```

3. **Verify:**
   ```bash
   python config/manage_env.py audit
   ```

**See:** [`config/ENV_MANIFEST_README.md`](../config/ENV_MANIFEST_README.md) for complete guide.

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

#### 1. Migration Fails - SSH Tunnel Issues

**Symptoms:**
```
django.db.utils.OperationalError: connection timeout
Error: Could not establish SSH tunnel
```

**Diagnosis:**
```bash
# Check if bastion host is reachable
ping $DEV_HOST

# Test SSH access
ssh -o StrictHostKeyChecking=no $DEV_USER@$DEV_HOST "echo 'SSH OK'"

# Verify database host is accessible from bastion
ssh $DEV_USER@$DEV_HOST "nc -zv $DEV_DB_HOST 5432"
```

**Common Causes:**
- Incorrect SSH credentials in GitHub Secrets
- Database hostname wrong in `DB_HOST` secret
- Database port not 5432 (check `DB_PORT` secret)
- Firewall blocking bastion → database connection

**Fix:**
```bash
# Verify secrets in manifest
cat config/env.manifest.json | jq '.variables.infrastructure'

# Run audit to check secret names
python config/manage_env.py audit

# Update secrets in GitHub
gh secret set DEV_DB_HOST --body "your-db-host" --env dev-backend
gh secret set DEV_SSH_PASSWORD --body "your-password" --env dev-backend
```

#### 2. Docker Container Can't Access Tunnel

**Symptoms:**
```
Error: Connection refused to 127.0.0.1:5433
Docker container can't reach tunnel on runner
```

**Diagnosis:**
```bash
# Check if tunnel is active on runner
ps aux | grep ssh | grep 5433

# Test from runner (not container)
PGPASSWORD="$DB_PASSWORD" psql -h 127.0.0.1 -p 5433 -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;"
```

**Fix:**
- Ensure Docker uses `--network host` mode
- Check workflow uses correct port (5433)
- Verify tunnel established before Docker run

#### 3. Health Check Fails

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

#### 4. Frontend Shows 502 Bad Gateway

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

#### 5. Secret Not Found Error

**Symptoms:**
```
Error: Secret DB_HOST not found
Error: Workflow failed to reference secrets.UAT_HOST
```

**Diagnosis:**
```bash
# Check manifest for correct secret name
cat config/env.manifest.json | jq '.variables.infrastructure.BASTION_HOST'

# Run audit
python config/manage_env.py audit
```

**Fix:**
1. Find correct secret name in manifest
2. Use exact name from `ci_secret_mapping`
3. Add to GitHub if missing:
   ```bash
   gh secret set UAT_HOST --body "value" --env uat2-backend
   ```

#### 6. Frontend Environment Variables Wrong

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
