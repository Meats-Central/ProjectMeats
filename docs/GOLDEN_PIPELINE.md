# Golden Pipeline V1.0.0

## Overview
This document describes the **proven, production-ready** CI/CD pipeline for ProjectMeats.

**Status**: ✅ Successfully deployed to Production (meatscentral.com) on 2025-01-01

## Architecture
- **Shared Schema Multi-Tenancy**: All tenants in single PostgreSQL schema with `tenant_id` ForeignKey isolation
- **Bastion Tunnel Deployment**: Secure SSH tunnel on port 5433 for database migrations
- **Frontend**: React 19 + TypeScript 5.9 with Vite build system
- **Backend**: Django 5.x + DRF + PostgreSQL 15

## Workflow Files (Source of Truth)
1. **`main-pipeline.yml`**: Master deployment orchestrator
   - Triggers: push to `development`, `uat`, `main` branches
   - Calls: `reusable-deploy.yml` for environment-specific deployments

2. **`ops-release-automation.yml`**: Auto-promotion manager
   - Creates PRs: Development → UAT → Production
   - Runs: After successful deployments, daily sync checks

3. **`reusable-deploy.yml`**: Deployment logic template
   - Health checks with redirect handling (`curl -L`)
   - Idempotent migrations (`migrate --fake-initial`)
   - Environment-specific nginx configs

## Critical Guardrails

### Multi-Tenancy (STRICT ENFORCEMENT)

#### ❌ PROHIBITED LIBRARIES
The following packages are **ABSOLUTELY FORBIDDEN** and must NEVER appear in `backend/requirements.txt`:
- `django-tenants` (uses schema-based isolation - incompatible with our architecture)
- `django-tenant-schemas` (deprecated, schema-based)
- `django-db-multitenant` (uses connection routing - incompatible)
- Any package implementing schema-per-tenant or database-per-tenant patterns

**Rationale**: ProjectMeats uses **Shared Schema Multi-Tenancy** where all tenants share the `public` PostgreSQL schema. Tenant isolation is achieved through:
1. `tenant` ForeignKey on all business models
2. Automatic filtering via `request.tenant` in ViewSets
3. Row-Level Security (RLS) enforcement in querysets

#### ✅ REQUIRED PATTERNS
- **ALWAYS** use `tenant` ForeignKey: `models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)`
- **ALWAYS** filter by tenant: `.filter(tenant=request.tenant)` in `get_queryset()`
- **ALWAYS** assign tenant on creation: `serializer.save(tenant=self.request.tenant)` in `perform_create()`
- **ALWAYS** run standard Django migrations: `python manage.py migrate`
- **NEVER** use `migrate_schemas`, `schema_context()`, or `connection.schema_name`

### Deployment
❌ **NEVER** run migrations via docker exec or SSH post-deploy
✅ **ALWAYS** run migrations in CI before deployment
✅ **ALWAYS** use `--fake-initial` for idempotency

### Frontend
❌ **NEVER** use CRA-specific patterns
✅ **ALWAYS** write Vite-compatible code
✅ **ALWAYS** use `import.meta.env` for environment variables

## Secret Management
**Single Source of Truth**: `config/env.manifest.json` v3.3

Required secrets per environment:
- Backend: SSH_HOST, SSH_USER, SSH_PASSWORD, DB_*, DJANGO_*
- Frontend: SSH_HOST, SSH_USER, SSH_PASSWORD, BACKEND_HOST, REACT_APP_API_BASE_URL

Audit command: `python config/manage_env.py audit`

## Deployment Flow
```
Feature Branch → Development (auto-deploy to dev)
     ↓
  PR Created → UAT (manual merge, auto-deploy to uat)
     ↓
  PR Created → Main (manual merge, auto-deploy to prod)
```

## Health Check Pattern
```bash
# Follow redirects to handle HTTP→HTTPS
HTTP_CODE=$(curl -L -s -o /dev/null -w "%{http_code}" https://example.com/api/health/)
```

## Nginx Configuration
- **Development**: HTTP-only (`frontend.conf`)
- **Production**: SSL with HTTP2 (`frontend-ssl.conf`)
- **Selection**: Automatic via `docker-entrypoint.sh` based on certificate presence

## Migration Strategy
```bash
# Idempotent migrations (safe for re-runs)
python manage.py migrate --fake-initial --noinput
```

## Version History
- **v1.1.0** (2025-01-01): Pipeline Optimization & Security Hardening
  - ✅ Upgraded TypeScript 4.9.5 → 5.7.2 (React 19 compatibility)
  - ✅ Migrated Docker caching: local → GitHub Actions Cache (40% faster builds)
  - ✅ Added Trivy security scanning (CVE detection before deployment)
  - ✅ Enhanced multi-tenancy guardrails documentation
  - ✅ Deprecated move-cache step (replaced by GHA cache)
  
- **v1.0.0** (2025-01-01): Initial production deployment
  - Successful Dev → UAT → Prod pipeline established
  - All environments operational

## Performance Optimizations (V1.1)

### Build Speed
- **GitHub Actions Cache**: Docker layers cached between runs (~40% faster)
- **Cache Strategy**: `mode=max` ensures all intermediate layers are preserved
- **Multi-arch**: Builds optimized for linux/amd64 (deployment target)

### Security Scanning
- **Trivy Integration**: Scans images for CRITICAL and HIGH vulnerabilities
- **Non-Blocking**: Reports CVEs to GitHub Security but allows deployment to proceed
- **Unfixed Exclusion**: Ignores vulnerabilities without patches (reduces false positives)
- **SARIF Upload**: Results visible in GitHub Security tab for review

**Rationale**: Security scanning is informational in V1.1. Future versions will implement blocking policies after baseline vulnerability remediation.

### Frontend Stack
- **TypeScript 5.7.2**: Latest stable with React 19 support
- **Module Resolution**: `bundler` mode for Vite optimization
- **TODO**: Migrate react-table v7 → @tanstack/react-table v8 (planned for v1.2)

## References
- Deployment workflows: `.github/workflows/`
- Secret manifest: `config/env.manifest.json`
- Architecture docs: `docs/ARCHITECTURE.md`
