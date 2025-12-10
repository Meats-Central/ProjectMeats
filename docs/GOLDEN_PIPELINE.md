# Golden CI/CD Pipeline
**The Authoritative Reference for ProjectMeats Deployment Architecture**

> **Status**: ✅ ACTIVE - This is the definitive implementation standard  
> **Version**: 1.0 (December 2025)  
> **Authority**: All deployment practices must conform to this document

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Multi-Tenancy: Shared Schema](#multi-tenancy-shared-schema)
4. [Secret Management: Manifest-Driven](#secret-management-manifest-driven)
5. [Migration Strategy: Bastion Tunnel](#migration-strategy-bastion-tunnel)
6. [Frontend Strategy: Dockerized Nginx](#frontend-strategy-dockerized-nginx)
7. [Environment Map](#environment-map)
8. [Deployment Workflow](#deployment-workflow)
9. [Golden Rules](#golden-rules)
10. [Verification](#verification)

---

## Overview

The **Golden CI/CD Pipeline** represents the finalized, production-tested deployment architecture for ProjectMeats. This document serves as the single source of truth for all deployment practices.

### Core Pillars

1. **Shared-Schema Multi-Tenancy** - Row-level security via `tenant_id` ForeignKey
2. **Manifest-Based Secrets** - All configuration in `config/env.manifest.json`
3. **Bastion Tunnel Migrations** - Runner-based execution through SSH tunnel
4. **Dockerized Deployment** - Immutable container images with SHA tags

### What Makes It "Golden"

✅ **Battle-Tested**: All components verified in production  
✅ **Documented**: Every decision has clear rationale  
✅ **Enforced**: AI and developer guidelines prevent deviation  
✅ **Auditable**: Automated verification scripts  

---

## Architecture Principles

### 1. Separation of Concerns

```
┌─────────────────────────────────────────────────────────────┐
│                     CI/CD Pipeline                          │
├─────────────────┬───────────────┬───────────────────────────┤
│   Build & Test  │   Migrate DB  │   Deploy Services         │
│   (GitHub)      │   (Runner)    │   (Droplets)              │
└─────────────────┴───────────────┴───────────────────────────┘
         │                 │                    │
         ▼                 ▼                    ▼
    Docker Images    SSH Tunnel          Container Runtime
    (DOCR/GHCR)      (Port 5433)         (Port 8000/8080)
```

### 2. Infrastructure Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Source Control** | Code versioning | GitHub (development, uat, main) |
| **CI/CD** | Build, test, deploy | GitHub Actions |
| **Container Registry** | Image storage | DigitalOcean Container Registry |
| **Database** | PostgreSQL cluster | DigitalOcean Managed DB |
| **Web Servers** | Backend API | DigitalOcean Droplet (Django) |
| **Web Servers** | Frontend UI | DigitalOcean Droplet (Nginx) |
| **Bastion** | Secure DB access | SSH tunnel via droplet |

### 3. Security Model

- **Network Isolation**: Database in private network
- **Bastion Access**: SSH tunnel for migrations
- **Environment Secrets**: Scoped to GitHub Environments
- **Immutable Images**: SHA-tagged containers
- **TLS Everywhere**: HTTPS for all external traffic

---

## Multi-Tenancy: Shared Schema

### The Golden Standard: Row-Level Security

**ProjectMeats uses SHARED SCHEMA multi-tenancy with tenant isolation via ForeignKey.**

```python
# ✅ CORRECT: Shared schema with tenant ForeignKey
class Customer(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'email']),
        ]

# ViewSet with tenant filtering
class CustomerViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Customer.objects.filter(tenant=self.request.tenant)
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)
```

### Architecture Details

**Database Structure:**
```
PostgreSQL (Single Cluster)
└── public schema (ALL tenants)
    ├── tenants_tenant (tenant metadata)
    ├── accounts_user (tenant=FK)
    ├── customers_customer (tenant=FK)
    ├── suppliers_supplier (tenant=FK)
    └── ... (all business models have tenant FK)
```

**Isolation Mechanism:**
- `TenantMiddleware` sets `request.tenant` from domain/header/user
- All ViewSets filter: `.filter(tenant=request.tenant)`
- All creates assign: `tenant=request.tenant`
- No schema switching, no schema routing

### What We DO NOT Use

❌ **NEVER use these patterns:**
- `django-tenants` package or any schema-based library
- `schema_context()` or `connection.schema_name`
- `migrate_schemas` or `migrate --tenant` commands
- Separate PostgreSQL schemas per tenant
- `DATABASE_ROUTERS` for tenant routing
- `TENANT_MODEL` or `TENANT_DOMAIN_MODEL` settings

### Migration Commands

```bash
# ✅ CORRECT: Standard Django migrations
python manage.py makemigrations
python manage.py migrate --fake-initial --noinput

# ❌ WRONG: Schema-based commands
python manage.py migrate_schemas  # Does not exist in our system
```

---

## Secret Management: Manifest-Driven

### The Golden Standard: Single Source of Truth

**ALL environment variables and secrets are defined in `config/env.manifest.json` (v3.3).**

### Manifest Structure

```json
{
  "project": "ProjectMeats",
  "version": "3.3",
  "environments": {
    "dev-backend": { "type": "backend", "prefix": "DEV" },
    "uat2": { "type": "frontend", "prefix": "STAGING" }
  },
  "variables": {
    "infrastructure": {
      "BASTION_HOST": {
        "description": "Droplet IP",
        "ci_secret_mapping": {
          "dev-backend": "DEV_HOST",
          "uat2": "STAGING_HOST"
        }
      }
    }
  }
}
```

### Secret Resolution Logic

```
Available Secrets = Environment Secrets ∪ Global Repository Secrets
```

**GitHub Secrets Architecture:**
1. **Environment Secrets** (Scoped): `dev-backend`, `uat2`, etc.
2. **Global Repository Secrets** (Available to all): `DO_ACCESS_TOKEN`, `GITHUB_TOKEN`

### Audit Tool

```bash
# Validate all secrets before deployment
python config/manage_env.py audit

# Expected output:
# ✓ Fetched N Global Repository Secrets
# Scanning Environment: dev-backend...
#   ✅ All Clear (X env-specific secrets found)
```

### Workflow Integration

```yaml
# Workflows reference secrets via manifest mappings
environment: dev-backend
env:
  DB_HOST: ${{ secrets.DEV_DB_HOST }}
  DB_USER: ${{ secrets.DEV_DB_USER }}
  DB_PASSWORD: ${{ secrets.DEV_DB_PASSWORD }}
```

### Golden Rules for Secrets

✅ **ALWAYS**:
- Read manifest first: `cat config/env.manifest.json`
- Run audit before changes: `python config/manage_env.py audit`
- Use manifest-defined names (no guessing)
- Document legacy exceptions in manifest

❌ **NEVER**:
- Guess secret names ("it's probably DEV_*")
- Hardcode secrets in code or docs
- Create `.env.example` files with values
- Reference archived documentation

**Documentation**: [`docs/CONFIGURATION_AND_SECRETS.md`](CONFIGURATION_AND_SECRETS.md)

---

## Migration Strategy: Bastion Tunnel

### The Golden Standard: Runner-Based Execution

**Migrations run on GitHub Actions runner via SSH tunnel to private database.**

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│ GitHub Actions Runner (Ubuntu)                           │
│                                                           │
│  1. Create SSH Tunnel                                    │
│     ssh -L 5433:db.internal:5432 user@bastion           │
│                                                           │
│  2. Run Docker Container                                 │
│     docker run --network host \                          │
│       -e DATABASE_URL=postgresql://...@127.0.0.1:5433/db │
│       backend:sha python manage.py migrate               │
│                                                           │
│  3. Cleanup Tunnel                                       │
└──────────────────────────────────────────────────────────┘
         │                                  │
         │ SSH (port 22)                    │ Tunnel (port 5433)
         ▼                                  ▼
    Bastion Droplet ──────────────► Private Database
    (Public IP)                      (db.internal:5432)
```

### Implementation Steps

#### 1. Install Tools
```bash
sudo apt-get update -qq
sudo apt-get install -y openssh-client sshpass postgresql-client
```

#### 2. Create SSH Tunnel
```bash
sshpass -p "$SSHPASS" ssh -o StrictHostKeyChecking=no -f -N \
  -L 5433:$DB_HOST:$DB_PORT \
  $BASTION_USER@$BASTION_HOST
```

**Tunnel Mapping:**
- **Local**: `127.0.0.1:5433` (on runner)
- **Remote**: `$DB_HOST:$DB_PORT` (private database)
- **Via**: Bastion droplet (has access to private network)

#### 3. Test Connectivity
```bash
PGPASSWORD="$DB_PASSWORD" psql \
  -h 127.0.0.1 \
  -p 5433 \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -c "SELECT version();"
```

#### 4. Run Migrations
```bash
# Construct DATABASE_URL pointing to tunnel
DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@127.0.0.1:5433/$DB_NAME"

# Run migrations with Docker (host networking)
docker run --rm \
  --network host \
  -e DATABASE_URL="$DATABASE_URL" \
  -e DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE" \
  -e SECRET_KEY="$SECRET_KEY" \
  backend:sha \
  python manage.py migrate --fake-initial --noinput
```

**Why `--network host`**: Allows container to access tunnel on `localhost:5433`

#### 5. Cleanup
```bash
# Kill tunnel process
pkill -f "ssh.*5433" || true
```

### Why This Approach

✅ **Security**: Database stays in private network  
✅ **Decoupled**: Migrations run separately from web deployment  
✅ **Idempotent**: `--fake-initial` handles re-runs  
✅ **Auditable**: All logs in GitHub Actions  
✅ **Reliable**: No SSH access needed from deployed containers  

### What We DO NOT Use

❌ **NEVER use these patterns:**
- SSH from deployed container to run migrations
- Migrations as part of web server startup
- Direct database access from GitHub runners
- Schema-based migration commands
- Manual SSH sessions for migrations

---

## Frontend Strategy: Dockerized Nginx

### The Golden Standard: Container + Reverse Proxy

**Frontend runs as Dockerized Nginx container behind host-level reverse proxy.**

### Architecture

```
External Request
    │
    ▼
Host Nginx (Port 80) ───────┐
    │                       │
    │ /api/* /admin/*       │ /*
    │                       │
    ▼                       ▼
Backend Droplet      Frontend Container
(Port 8000)          (Port 8080:80)
                          │
                          ▼
                     React SPA
                  (/usr/share/nginx/html)
```

### Container Configuration

**Docker Run:**
```bash
docker run -d --name pm-frontend \
  --restart unless-stopped \
  -p 8080:80 \
  --add-host backend:$BACKEND_IP \
  -v /opt/pm/frontend/env/env-config.js:/usr/share/nginx/html/env-config.js:ro \
  frontend:sha
```

**Port Mapping:**
- Container listens on port 80 (internal)
- Mapped to host port 8080
- Host nginx proxies to 127.0.0.1:8080

### Host Nginx Configuration

```nginx
server {
    listen 80;
    server_name _ localhost;
    
    # API/Admin routes → Backend
    location ~ ^/(api|admin|static)/ {
        proxy_pass http://BACKEND_IP:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # All other routes → Frontend container
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Health Check

```bash
# Check container directly (primary)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/)

# Check reverse proxy (secondary, informational)
PROXY_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80/)
```

**Why check container first:**
- Verifies application is running
- Independent of proxy configuration
- Faster and more reliable
- Proxy issues don't block deployment

### Runtime Configuration

**env-config.js** (injected at runtime):
```javascript
window.ENV = {
  API_BASE_URL: "https://dev.meatscentral.com",
  ENVIRONMENT: "development"
};
```

**Mounted at:** `/usr/share/nginx/html/env-config.js`  
**Loaded by:** `index.html` via `<script>` tag

---

## Environment Map

### The 6 Deployment Environments

| Environment | Type | Prefix | GitHub Env | Branch | URL |
|-------------|------|--------|------------|--------|-----|
| `dev-backend` | backend | `DEV` | dev-backend | development | N/A (API only) |
| `dev-frontend` | frontend | `DEV` | dev-frontend | development | https://dev.meatscentral.com |
| `uat2-backend` | backend | `UAT` | uat2-backend | uat | N/A (API only) |
| `uat2` | frontend | `STAGING` ⚠️ | uat2 | uat | https://uat.meatscentral.com |
| `prod2-backend` | backend | `PROD` | prod2-backend | main | N/A (API only) |
| `prod2-frontend` | frontend | `PROD` | prod2-frontend | main | https://meatscentral.com |

⚠️ **Legacy Exception**: UAT frontend uses `STAGING` prefix and environment name `uat2` (not `uat2-frontend`) due to pre-standardization naming.

### Secret Prefix Patterns

| Environment | Infrastructure | Application | Frontend |
|-------------|----------------|-------------|----------|
| dev-backend | `DEV_HOST`, `DEV_USER` | `DEV_DB_HOST`, `DEV_SECRET_KEY` | N/A |
| dev-frontend | `DEV_HOST`, `DEV_USER` | N/A | `REACT_APP_*` |
| uat2-backend | `UAT_HOST`, `UAT_USER` | `UAT_DB_HOST`, `UAT_SECRET_KEY` | N/A |
| uat2 | `STAGING_HOST`, `STAGING_USER` ⚠️ | N/A | `REACT_APP_*` |
| prod2-backend | `PROD_HOST`, `PROD_USER` | `PROD_DB_HOST`, `PROD_SECRET_KEY` | N/A |
| prod2-frontend | `PRODUCTION_HOST` ⚠️ | N/A | `REACT_APP_*` |

### Shared Secrets

**SSH_PASSWORD** (Global):
- Used by: `uat2-backend`, `uat2`, `prod2-backend`, `prod2-frontend`
- Scope: Global repository secret
- Why: Legacy infrastructure uses single SSH password for UAT/Prod

---

## Deployment Workflow

### Complete Deployment Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Trigger (Push to branch)                                 │
└──────────────────┬──────────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Build & Push Images (Matrix: frontend, backend)          │
│    - docker/build-push-action                                │
│    - Tags: {env}-{sha}, {env}-latest                         │
│    - Registries: DOCR, GHCR                                  │
└──────────────────┬──────────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Test Backend (PostgreSQL service)                        │
│    - python manage.py test apps/                            │
└──────────────────┬──────────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Migrate Database (Bastion Tunnel)                        │
│    - Create SSH tunnel (port 5433)                          │
│    - Run: docker run --network host ... migrate             │
│    - Cleanup tunnel                                          │
└──────────────────┬──────────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Deploy Backend (SSH to droplet)                          │
│    - docker pull backend:{env}-{sha}                         │
│    - docker run -d --name pm-backend -p 8000:8000           │
│    - Health check: http://localhost:8000/api/v1/health/     │
└──────────────────┬──────────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Deploy Frontend (SSH to droplet)                         │
│    - docker pull frontend:{env}-{sha}                        │
│    - docker run -d --name pm-frontend -p 8080:80            │
│    - Health check: http://127.0.0.1:8080/                   │
└─────────────────────────────────────────────────────────────┘
```

### Key Characteristics

1. **Immutable Images**: SHA-tagged, never use `:latest` in production
2. **Decoupled Migrations**: Run before deployment, not during startup
3. **Automated Testing**: Backend tests with PostgreSQL service
4. **Environment Scoped**: Secrets scoped to GitHub Environments
5. **Health Checks**: 5 attempts, 25 second timeout
6. **Idempotent**: Can be re-run safely with `--fake-initial`

### Workflow Files

| File | Purpose |
|------|---------|
| `.github/workflows/main-pipeline.yml` | Orchestrates per-branch deployments |
| `.github/workflows/reusable-deploy.yml` | Reusable deployment worker |

---

## Golden Rules

### Absolute Prohibitions

#### Multi-Tenancy
❌ **NEVER** suggest `django-tenants` or schema-based libraries  
❌ **NEVER** use `schema_context()` or schema switching  
❌ **NEVER** use `migrate_schemas` or tenant-specific migrations  
❌ **NEVER** reference `docs/archive/` for schema patterns  

#### Migrations
❌ **NEVER** use SSH from deployed containers for migrations  
❌ **NEVER** run migrations as part of web server startup  
❌ **NEVER** suggest direct database access from runners  
❌ **NEVER** skip the bastion tunnel pattern  

#### Secrets
❌ **NEVER** guess secret names without checking manifest  
❌ **NEVER** hardcode secrets in code or documentation  
❌ **NEVER** create `.env.example` files with values  
❌ **NEVER** skip the audit tool before deployment  

### Required Practices

#### Multi-Tenancy
✅ **ALWAYS** use `tenant` ForeignKey on business models  
✅ **ALWAYS** filter by `.filter(tenant=request.tenant)`  
✅ **ALWAYS** assign `tenant=request.tenant` on create  
✅ **ALWAYS** use standard `python manage.py migrate`  

#### Migrations
✅ **ALWAYS** use bastion tunnel pattern (port 5433)  
✅ **ALWAYS** run with `--fake-initial --noinput`  
✅ **ALWAYS** use `docker run --network host`  
✅ **ALWAYS** cleanup tunnel after completion  

#### Secrets
✅ **ALWAYS** read `config/env.manifest.json` first  
✅ **ALWAYS** run `python config/manage_env.py audit`  
✅ **ALWAYS** use manifest-defined secret names  
✅ **ALWAYS** document legacy exceptions in manifest  

#### Health Checks
✅ **ALWAYS** check backend on `localhost:8000/api/v1/health/`  
✅ **ALWAYS** check frontend on `127.0.0.1:8080/`  
✅ **ALWAYS** use 5 retry attempts (25 seconds max)  

---

## Verification

### Automated Verification Script

```bash
#!/bin/bash
# scripts/verify_golden_state.sh
# Verifies the Golden Pipeline implementation

echo "🔍 Verifying Golden Pipeline State..."
echo ""

ERRORS=0

# 1. Check manifest exists
if [ -f "config/env.manifest.json" ]; then
    echo "✅ config/env.manifest.json exists"
else
    echo "❌ config/env.manifest.json NOT FOUND"
    ERRORS=$((ERRORS + 1))
fi

# 2. Check manage_env.py supports audit
if grep -q "def audit_secrets" config/manage_env.py 2>/dev/null; then
    echo "✅ manage_env.py has audit_secrets method"
else
    echo "❌ manage_env.py missing audit_secrets"
    ERRORS=$((ERRORS + 1))
fi

# 3. Check workflow has bastion tunnel
if grep -q "ssh -L 5433" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ reusable-deploy.yml uses SSH tunnel (port 5433)"
else
    echo "❌ reusable-deploy.yml missing SSH tunnel"
    ERRORS=$((ERRORS + 1))
fi

# 4. Check workflow uses --network host
if grep -q "\\-\\-network host" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ reusable-deploy.yml uses Docker host networking"
else
    echo "❌ reusable-deploy.yml missing --network host"
    ERRORS=$((ERRORS + 1))
fi

# 5. Check frontend health check
if grep -q "127.0.0.1:8080" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ reusable-deploy.yml checks frontend container directly"
else
    echo "❌ reusable-deploy.yml frontend check incorrect"
    ERRORS=$((ERRORS + 1))
fi

# 6. Check for prohibited patterns
if grep -q "django-tenants" backend/requirements.txt 2>/dev/null; then
    echo "❌ CRITICAL: django-tenants found in requirements.txt"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No django-tenants in requirements.txt"
fi

# 7. Check documentation exists
if [ -f "docs/GOLDEN_PIPELINE.md" ]; then
    echo "✅ docs/GOLDEN_PIPELINE.md exists"
else
    echo "❌ docs/GOLDEN_PIPELINE.md NOT FOUND"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "docs/CONFIGURATION_AND_SECRETS.md" ]; then
    echo "✅ docs/CONFIGURATION_AND_SECRETS.md exists"
else
    echo "❌ docs/CONFIGURATION_AND_SECRETS.md NOT FOUND"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "────────────────────────────────────"
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed! Golden Pipeline verified."
    exit 0
else
    echo "❌ $ERRORS check(s) failed. Review errors above."
    exit 1
fi
```

### Manual Verification Checklist

- [ ] Manifest version is 3.3 or higher
- [ ] All 6 environments defined in manifest
- [ ] Audit tool runs without errors
- [ ] Workflow uses bastion tunnel (port 5433)
- [ ] Frontend health check uses 127.0.0.1:8080
- [ ] Backend health check uses localhost:8000
- [ ] No django-tenants in requirements.txt
- [ ] Documentation references this file as authority

---

## Related Documentation

### Primary References
- [`config/env.manifest.json`](../config/env.manifest.json) - Secret definitions
- [`docs/CONFIGURATION_AND_SECRETS.md`](CONFIGURATION_AND_SECRETS.md) - Secret management guide
- [`.github/workflows/reusable-deploy.yml`](../.github/workflows/reusable-deploy.yml) - Deployment implementation

### Supporting Documentation
- [`docs/DEVELOPMENT_PIPELINE.md`](DEVELOPMENT_PIPELINE.md) - Developer workflow
- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) - System architecture
- [`config/README.md`](../config/README.md) - Configuration quick reference

### Archived Documentation
**DO NOT REFERENCE** (moved to `docs/archive/legacy_v2/`):
- Old deployment guides with SSH-based migrations
- Schema-based multi-tenancy documentation
- Manual secret configuration guides

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-10 | Initial Golden Pipeline documentation |

---

**Last Updated**: December 10, 2025  
**Maintained By**: DevOps Team  
**Status**: ✅ ACTIVE AND ENFORCED  

**If this document conflicts with other documentation, this document is authoritative.**
