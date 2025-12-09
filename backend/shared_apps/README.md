# Shared Apps

This directory contains Django apps that are **shared across all tenants** (no tenant isolation).

## Rules
- Models here are NOT tenant-isolated (no `tenant` ForeignKey)
- Use standard Django `python manage.py migrate` for migrations
- Examples: tenants, auth/user models, global configurations

## Current Structure
Shared apps are currently in `../apps/tenants/` and Django's built-in apps. This directory is prepared for future migration to the recommended structure per docs/ARCHITECTURE.md.

## Multi-Tenancy
ProjectMeats uses a **shared-schema** approach where all data lives in a single PostgreSQL schema. Apps in this directory provide cross-tenant functionality like:
- Tenant management (`apps.tenants`)
- User authentication
- Global configuration
