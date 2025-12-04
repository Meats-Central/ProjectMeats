# Shared Apps

This directory contains Django apps that live in the **public schema** (shared across all tenants).

## Rules
- Models here are NOT tenant-isolated
- Use `migrate_schemas --shared` for migrations
- Examples: tenants, auth/user models, global configurations

## Current Structure
Shared apps are currently in `../apps/tenants/` and Django's built-in apps. This directory is prepared for future migration to the recommended structure per docs/ARCHITECTURE.md.
