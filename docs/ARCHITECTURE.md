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
