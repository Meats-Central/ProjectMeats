# ProjectMeats – AI Coding Agent Instructions

**Stack**: Django 4.2.7 + DRF + PostgreSQL | React 18.2.0 + TypeScript | django-tenants multi-tenancy

## ⚠️ Critical Rules

1. **Branch Workflow**: NEVER push to `uat` or `main`. Always: `feature/*` → `development` → automated PR to `UAT` → automated PR to `main`
2. **Migrations**: Always run `python manage.py makemigrations` and commit migration files. CharField with `blank=True` MUST have `default=''`
3. **Tenant Isolation**: All tenant models need `tenant = ForeignKey(Tenant)` and views must filter by `request.tenant`

## Quick Commands

```bash
./start_dev.sh              # Start PostgreSQL + Django + React
make test                   # Run all tests
make format && make lint    # Format and lint before committing
pre-commit install          # Required after cloning (validates migrations)
```

## Architecture Patterns

### Backend (`backend/apps/`)
- **Models**: Extend `TimestampModel`, use `TenantManager` for tenant filtering (see `apps/suppliers/models.py`)
- **Views**: Extend `ModelViewSet`, use `IsAuthenticated`, filter queryset by `request.tenant` (see `apps/suppliers/views.py`)
- **Serializers**: Use `ModelSerializer`, implement `validate_<field>()` for field validation
- **Tenant Apps** (use `migrate_schemas`): suppliers, customers, purchase_orders, contacts, plants, carriers, accounts_receivables, ai_assistant, products, sales_orders, invoices

### Frontend (`frontend/src/`)
- **API Service**: Use `apiService` singleton from `services/apiService.ts` with automatic auth token injection
- **Tenant Context**: `X-Tenant-ID` header automatically added from `localStorage.tenantId`
- **Components**: Functional components with TypeScript interfaces for props

## Key Files

| Purpose | Location |
|---------|----------|
| Django settings | `backend/projectmeats/settings/{base,development,production}.py` |
| API routes | `backend/projectmeats/urls.py`, `backend/apps/*/urls.py` |
| Tenant models | `backend/apps/tenants/models.py` (Client, Domain, Tenant, TenantUser) |
| Frontend API | `frontend/src/services/apiService.ts` |
| CI/CD workflows | `.github/workflows/{11,12,13}-*-deployment.yml` |
| Environment config | `config/manage_env.py`, `config/environments/*.env` |

## Common Pitfalls

- ❌ Forgetting to commit migration files → CI fails
- ❌ CharField `blank=True` without `default=''` → PostgreSQL errors
- ❌ Missing `request.tenant` filter in ViewSet → data leakage between tenants
- ❌ Direct push to `uat`/`main` → breaks deployment pipeline

## Resources

- [Migration Guide](../docs/MIGRATION_GUIDE.md) – django-tenants migration patterns
- [Authentication Guide](../docs/AUTHENTICATION_GUIDE.md) – auth, permissions, superuser management
- [Troubleshooting](../docs/TROUBLESHOOTING.md) – common issues and solutions
- [copilot-log.md](copilot-log.md) – historical context and lessons learned
