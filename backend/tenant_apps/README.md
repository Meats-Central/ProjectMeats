# Tenant Apps

This directory contains Django apps that are **tenant-specific** (isolated per tenant via `tenant_id` foreign keys).

## Rules
- All models here include a `tenant` ForeignKey for data isolation
- Use standard Django `python manage.py migrate` for migrations
- Examples: suppliers, customers, purchase_orders, products

## Current Structure
All tenant apps are currently in `../apps/`. This directory is prepared for future migration to the recommended structure per docs/ARCHITECTURE.md.

## Multi-Tenancy
ProjectMeats uses a **shared-schema** approach where all tenants share the same PostgreSQL schema. Tenant isolation is enforced via:
- `tenant` ForeignKey on all business models
- `TenantMiddleware` sets `request.tenant` from domain/header/user
- ViewSets filter querysets: `queryset.filter(tenant=request.tenant)`
