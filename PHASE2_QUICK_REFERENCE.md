# Phase 2 Multi-Tenancy Isolation - Quick Reference

**Implementation Date**: 2025-12-02  
**Status**: ✅ Complete

## What Changed?

Enhanced all deployment workflows with **DATABASE_URL parsing** and **explicit DB_ENGINE** to support django-tenants multi-tenancy schema isolation.

## Modified Files

```
.github/workflows/11-dev-deployment.yml  (migrate job)
.github/workflows/12-uat-deployment.yml  (migrate job)
.github/workflows/13-prod-deployment.yml (migrate job)
```

## Key Additions

### 1. DB_ENGINE Environment Variable
```yaml
env:
  DB_ENGINE: django.db.backends.postgresql
```

### 2. DATABASE_URL Parsing
```bash
if [ -n "$DATABASE_URL" ]; then
  export DB_USER=$(echo "$DATABASE_URL" | sed -n 's|postgresql://\([^:]*\):.*|\1|p')
  export DB_PASSWORD=$(echo "$DATABASE_URL" | sed -n 's|postgresql://[^:]*:\([^@]*\)@.*|\1|p')
  export DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')
  export DB_PORT=$(echo "$DATABASE_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
  export DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')
fi
```

### 3. Three-Step Migration Process
```bash
# Step 1: Shared schema (public)
python manage.py migrate_schemas --shared --fake-initial --noinput

# Step 2: Super tenant
python manage.py create_super_tenant --no-input --verbosity=1

# Step 3: Tenant schemas
python manage.py migrate_schemas --tenant --noinput
```

## Required Secrets

### Development
- `DEV_DB_URL` - postgresql://user:pass@host:port/dbname
- `DEV_SECRET_KEY` - Django secret key
- `DEV_DJANGO_SETTINGS_MODULE` - projectmeats.settings.production

### UAT
- `UAT_DB_URL` - postgresql://user:pass@host:port/dbname
- `UAT_SECRET_KEY` - Django secret key
- `UAT_DJANGO_SETTINGS_MODULE` - projectmeats.settings.production

### Production
- `PROD_DB_URL` - postgresql://user:pass@host:port/dbname
- `PROD_SECRET_KEY` - Django secret key
- `PROD_DJANGO_SETTINGS_MODULE` - projectmeats.settings.production

## Testing Workflow

### 1. Pre-Deployment Checks
```bash
# Verify secrets are set
gh secret list --env dev-backend
gh secret list --env uat2-backend
gh secret list --env prod2-backend
```

### 2. Monitor Migration Job
```bash
# Watch GitHub Actions logs for:
✓ "Parsed database configuration"
✓ "Applying shared schema migrations"
✓ "Creating super tenant"
✓ "Applying tenant migrations"
✓ "Migrations completed successfully"
```

### 3. Post-Deployment Validation
```sql
-- Check schemas exist
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name NOT IN ('pg_catalog', 'information_schema');

-- Should show: public, super_tenant, and any other tenants
```

## Troubleshooting

### Issue: DATABASE_URL not parsed
**Symptom**: Migration fails with "DB_HOST not set"  
**Solution**: Verify DATABASE_URL secret format: `postgresql://user:pass@host:port/dbname`

### Issue: migrate_schemas command not found
**Symptom**: "migrate_schemas not available"  
**Solution**: Check django-tenants is in requirements.txt and installed

### Issue: Migration job blocks deployment
**Symptom**: deploy-backend waits indefinitely  
**Solution**: Check migrate job logs, fix errors, re-run workflow

### Issue: Idempotency fails
**Symptom**: "Table already exists" errors  
**Solution**: Verify --fake-initial flag is present in all migrate commands

## Rollback Strategy

If migration fails:
1. **Workflow automatically blocks deployment** (no containers deployed)
2. **Previous containers remain running** (no downtime)
3. **Fix migration issue and re-run workflow**

To manually rollback:
```bash
# SSH into server
docker ps  # Check running containers
docker logs pm-backend --tail 100  # Review logs
```

## Monitoring

### What to Watch
- Migration job duration (should be < 5 minutes)
- Schema creation success rate
- Tenant creation errors
- Database connection issues

### Success Indicators
✅ All three migration steps complete  
✅ Deployment proceeds after migrate job  
✅ Health checks pass post-deployment  
✅ No "Table already exists" errors  
✅ Schema isolation verified in database  

## Common Questions

**Q: Do I need to run migrations manually?**  
A: No, the `migrate` job runs automatically before deployment.

**Q: What happens if migration fails?**  
A: Deployment is blocked; previous version remains running.

**Q: Can I skip the migrate job?**  
A: No, it's required via `needs: [migrate]` dependency.

**Q: Is it safe to re-run migrations?**  
A: Yes, `--fake-initial` makes them idempotent.

**Q: How do I add a new tenant?**  
A: Use Django admin or management command; migrations will auto-apply.

## Related Documentation

- [Full Implementation Summary](./PHASE2_MULTI_TENANCY_ISOLATION_IMPLEMENTATION.md)
- [Multi-Tenancy Implementation](./MULTI_TENANCY_IMPLEMENTATION.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [CI/CD Django Tenants Fix](./CICD_DJANGO_TENANTS_FIX.md)

---

**Last Updated**: 2025-12-02  
**Verification Status**: ✅ All checks passed
