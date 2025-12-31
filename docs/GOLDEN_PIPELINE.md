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

### Multi-Tenancy
❌ **NEVER** use `django-tenants` or schema-based isolation
✅ **ALWAYS** use `tenant` ForeignKey with `.filter(tenant=request.tenant)`
✅ **ALWAYS** run standard Django migrations: `python manage.py migrate`

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
- **v1.0.0** (2025-01-01): Initial production deployment
- Successful Dev → UAT → Prod pipeline established
- All environments operational

## References
- Deployment workflows: `.github/workflows/`
- Secret manifest: `config/env.manifest.json`
- Architecture docs: `docs/ARCHITECTURE.md`
