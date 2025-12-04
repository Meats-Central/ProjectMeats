# Tenant Apps

This directory contains Django apps that are **tenant-specific** (isolated per schema).

## Rules
- All models here get their own table in each tenant's PostgreSQL schema
- Use `migrate_schemas --tenant` for migrations
- Examples: suppliers, customers, purchase_orders, products

## Current Structure
All tenant apps are currently in `../apps/`. This directory is prepared for future migration to the recommended structure per docs/ARCHITECTURE.md.
