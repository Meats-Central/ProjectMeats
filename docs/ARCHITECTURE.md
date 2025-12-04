# Project Meats — Current Architecture (Authoritative — December 2025)

## Stack
- Backend: Django 5.x + django-tenants 3.x + PostgreSQL 15+
- Frontend: React 19 + TypeScript 5.9 + Vite 5 + dnd-kit + TanStack Query
- Multi-Tenancy: **Schema-based isolation only** (django-tenants)
- No `tenant_id` foreign keys anywhere in business models

## Directory Structure (Mandatory)
```
/backend/
  manage.py
  /shared_apps/      ← public schema only (auth, tenants, etc.)
  /tenant_apps/      ← all business logic lives here
/frontend/
  src/
    /features/       ← new feature-sliced layout
    /components/ui/  ← shadcn/ui components
```

## Golden Rules (never break)
1. Always use schema context (`connection.schema_name`, `tenant_schema()`)
2. Migrations → `python manage.py migrate_schemas` (never plain migrate on tenant data)
3. All Celery tasks must be tenant-aware
4. Sidebar is Dark Mode with white text (#ffffff on #0f172a)
5. All new components use React 19 + TypeScript strict mode

This file overrides every older doc. If something contradicts this file → this file wins.

---

## Phase 1 – Core Platform Foundation ✓ Closed December 2025

### Completed Components
- ✅ **CI/CD Pipeline**: GitHub Actions workflows for dev/UAT/production
- ✅ **Branch Protection**: Semantic PR checks and branch flow validation
- ✅ **Multi-Tenant Migrations**: `migrate_schemas` commands in Makefile
- ✅ **Docker Setup**: docker-compose for local development
- ✅ **Code Standards**: EditorConfig, linting, formatting rules
- ✅ **Documentation**: Single source of truth established (docs/ARCHITECTURE.md)

### Key Achievements
- Django 5.x + psycopg3 (modern PostgreSQL adapter)
- React 19 + TypeScript 5.9 strict mode
- Feature-sliced directory structure prepared
- 137 legacy docs archived to prevent AI hallucinations

**Status**: Production-ready foundation. All future work builds on this baseline.
