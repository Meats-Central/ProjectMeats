# Phase 2 Multi-Tenancy Isolation - Implementation Checklist

**Date**: 2025-12-02  
**Commit**: 913ddb9  
**Status**: ✅ Code Complete - Pending Deployment Testing

## Pre-Deployment Checklist

### 1. GitHub Secrets Configuration

Verify all required secrets are set for each environment:

#### Development Environment (`dev-backend`)
```bash
gh secret list --env dev-backend
```

Required secrets:
- [ ] `DEV_DB_URL` - Format: `postgresql://user:pass@host:port/dbname`
- [ ] `DEV_SECRET_KEY` - Django secret key (50+ random characters)
- [ ] `DEV_DJANGO_SETTINGS_MODULE` - Usually `projectmeats.settings.production`

#### UAT Environment (`uat2-backend`)
```bash
gh secret list --env uat2-backend
```

Required secrets:
- [ ] `UAT_DB_URL` - Format: `postgresql://user:pass@host:port/dbname`
- [ ] `UAT_SECRET_KEY` - Django secret key (50+ random characters)
- [ ] `UAT_DJANGO_SETTINGS_MODULE` - Usually `projectmeats.settings.production`

#### Production Environment (`prod2-backend`)
```bash
gh secret list --env prod2-backend
```

Required secrets:
- [ ] `PROD_DB_URL` - Format: `postgresql://user:pass@host:port/dbname`
- [ ] `PROD_SECRET_KEY` - Django secret key (50+ random characters)
- [ ] `PROD_DJANGO_SETTINGS_MODULE` - Usually `projectmeats.settings.production`

### 2. Backend Validation

Verify django-tenants is properly configured:

```bash
# Check requirements.txt includes django-tenants
cd backend
grep django-tenants requirements.txt

# Verify management commands exist
python manage.py help migrate_schemas
python manage.py help create_super_tenant

# Test DATABASE_URL parsing locally (optional)
export DATABASE_URL="postgresql://testuser:testpass@localhost:5432/testdb"
export DB_USER=$(echo "$DATABASE_URL" | sed -n 's|postgresql://\([^:]*\):.*|\1|p')
echo "Parsed user: $DB_USER"  # Should show: testuser
```

### 3. Branch Protection

Current branch: `fix/update-upload-artifact-action`

Next steps:
- [ ] Push changes to remote: `git push origin fix/update-upload-artifact-action`
- [ ] Create PR to `development` branch
- [ ] Add reviewers
- [ ] Link to issue/task if applicable

## Testing Plan

### Phase 1: Development Environment Testing

1. **Trigger Dev Workflow**
   ```bash
   # Merge PR to development branch or manually trigger
   gh workflow run "Deploy Dev (Frontend + Backend via DOCR and GHCR)" --ref development
   ```

2. **Monitor Migration Job**
   - Watch GitHub Actions logs
   - Look for: "Parsed database configuration"
   - Verify: "Migrations completed successfully"

3. **Validate Database Schemas**
   ```sql
   -- Connect to dev database
   SELECT schema_name FROM information_schema.schemata 
   WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
   ORDER BY schema_name;
   
   -- Expected: public, super_tenant (and any other tenants)
   ```

4. **Check Super Tenant**
   ```python
   # Django shell or admin
   from apps.tenants.models import Client
   super_tenant = Client.objects.get(schema_name='super_tenant')
   print(f"Super tenant: {super_tenant.name}")
   ```

5. **Verify Application Health**
   ```bash
   curl https://dev.meatscentral.com/api/v1/health/
   # Should return HTTP 200
   ```

### Phase 2: UAT Environment Testing

After successful dev deployment:

1. **Promote to UAT**
   ```bash
   # Merge development to uat branch (via automated PR or manual)
   gh workflow run "Deploy UAT (Frontend + Backend via DOCR)" --ref uat
   ```

2. **Repeat validation steps** from Phase 1 for UAT environment

3. **Additional UAT Tests**
   - Test tenant creation via admin
   - Verify tenant schema isolation
   - Test multi-tenant data queries

### Phase 3: Production Deployment

After successful UAT validation:

1. **Pre-Production Checklist**
   - [ ] Dev deployment successful
   - [ ] UAT deployment successful
   - [ ] Schema isolation verified
   - [ ] Super tenant created
   - [ ] No migration errors
   - [ ] Health checks passing

2. **Promote to Production**
   ```bash
   # Merge uat to main branch (via automated PR)
   gh workflow run "Deploy Production (Frontend + Backend via DOCR)" --ref main
   ```

3. **Production Validation**
   - Monitor migration job (should complete in < 5 minutes)
   - Verify health checks pass
   - Run smoke tests
   - Validate schemas in production database
   - Check application logs for errors

## Monitoring & Observability

### Key Metrics to Track

1. **Migration Job Duration**
   - Baseline: < 5 minutes
   - Alert if: > 10 minutes

2. **Migration Success Rate**
   - Target: 100%
   - Alert if: Any failures

3. **Schema Count**
   - Monitor: Number of tenant schemas
   - Alert if: Unexpected schema creation/deletion

4. **Database Connection Errors**
   - Monitor: Connection failures during migration
   - Alert if: Any DATABASE_URL parsing errors

### Logs to Watch

```bash
# GitHub Actions logs
gh run list --workflow="11-dev-deployment.yml" --limit 5
gh run view <run-id> --log

# Container logs (on deployment server)
ssh user@host
docker logs pm-backend --tail 100 --follow

# Database logs (if accessible)
# Check for schema creation, tenant migrations
```

## Rollback Procedures

### If Migration Fails in Dev

1. **Check Logs**
   ```bash
   gh run view <run-id> --log
   ```

2. **Common Issues**
   - DATABASE_URL format incorrect → Fix secret, re-run
   - migrate_schemas command not found → Check django-tenants in requirements.txt
   - Schema already exists → Verify --fake-initial flag present
   - Connection refused → Check database connectivity

3. **Fix and Re-Run**
   - Fix the issue
   - Re-trigger workflow (no manual rollback needed)
   - Previous containers remain running (no downtime)

### If Migration Fails in UAT/Production

1. **Automatic Rollback**
   - Workflow blocks deployment if migrate job fails
   - Previous version continues running
   - No downtime occurs

2. **Manual Intervention** (if needed)
   ```bash
   # SSH to server
   ssh user@host
   
   # Check running containers
   docker ps
   
   # Review logs
   docker logs pm-backend --tail 200
   
   # If needed, manually rollback to previous image
   docker pull registry/image:previous-tag
   docker rm -f pm-backend
   docker run -d --name pm-backend ... registry/image:previous-tag
   ```

## Post-Deployment Validation

### Automated Checks

- [ ] Health endpoint returns 200
- [ ] Smoke tests pass
- [ ] No errors in application logs

### Manual Validation

```sql
-- 1. Verify schema structure
SELECT schema_name, 
       (SELECT count(*) FROM information_schema.tables 
        WHERE table_schema = s.schema_name) as table_count
FROM information_schema.schemata s
WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
ORDER BY schema_name;

-- 2. Check tenant records
SELECT id, schema_name, name, created_on 
FROM public.tenants_client
ORDER BY created_on;

-- 3. Verify domain mappings
SELECT d.domain, c.schema_name, d.is_primary
FROM public.tenants_domain d
JOIN public.tenants_client c ON d.tenant_id = c.id
ORDER BY d.domain;
```

### Application Testing

- [ ] Login functionality works
- [ ] Tenant switching works (if applicable)
- [ ] Data isolation verified (queries scoped to tenant)
- [ ] Admin panel accessible
- [ ] API endpoints responding correctly

## Success Criteria

### Must Have (Blocking)
✅ All three workflows updated  
✅ DATABASE_URL parsing implemented  
✅ DB_ENGINE environment variable set  
✅ Idempotent migrations with --fake-initial  
✅ Three-step migration process  
✅ Error handling and fallbacks  
✅ Documentation created  

### Should Have (Non-Blocking)
- [ ] Dev deployment successful
- [ ] UAT deployment successful
- [ ] Production deployment successful
- [ ] No schema conflicts
- [ ] Migration duration < 5 minutes

### Nice to Have (Future)
- [ ] Migration dry-run validation
- [ ] Pre-migration database backup
- [ ] Schema diff validation
- [ ] Automated rollback on failure
- [ ] Datadog/Sentry integration
- [ ] Slack notifications for migrations

## Sign-Off

### Code Review
- [ ] Changes reviewed by: _______________
- [ ] Approved by: _______________
- [ ] Date: _______________

### Testing
- [ ] Dev environment tested: _______________
- [ ] UAT environment tested: _______________
- [ ] Production deployed: _______________
- [ ] Date: _______________

### Documentation
- [ ] Implementation guide reviewed
- [ ] Quick reference validated
- [ ] Runbooks updated (if needed)
- [ ] Team notified

## Related Documentation

- [PHASE2_MULTI_TENANCY_ISOLATION_IMPLEMENTATION.md](./PHASE2_MULTI_TENANCY_ISOLATION_IMPLEMENTATION.md) - Full implementation details
- [PHASE2_QUICK_REFERENCE.md](./PHASE2_QUICK_REFERENCE.md) - Developer quick reference
- [MULTI_TENANCY_IMPLEMENTATION.md](./MULTI_TENANCY_IMPLEMENTATION.md) - Multi-tenancy architecture
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Deployment procedures
- [CICD_DJANGO_TENANTS_FIX.md](./CICD_DJANGO_TENANTS_FIX.md) - CI/CD configuration

## Support & Troubleshooting

### Contact
- **Implementation**: GitHub Copilot CLI
- **Review**: [Team Lead / DevOps]
- **Emergency**: [On-Call Contact]

### Resources
- GitHub Actions Docs: https://docs.github.com/en/actions
- django-tenants Docs: https://django-tenants.readthedocs.io/
- PostgreSQL Schema Docs: https://www.postgresql.org/docs/current/ddl-schemas.html

---

**Last Updated**: 2025-12-02  
**Status**: ✅ Ready for Testing  
**Next Action**: Push branch and create PR to `development`
