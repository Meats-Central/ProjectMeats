# Troubleshooting Guide

**Last Updated**: November 29, 2024  
**Tech Stack**: Django 4.2.7, React 18.2.0, PostgreSQL 15, django-tenants 3.5.0

---

## Table of Contents

1. [Database Issues](#database-issues)
2. [Migration Problems](#migration-problems)
3. [Deployment Failures](#deployment-failures)
4. [Authentication Issues](#authentication-issues)
5. [Multi-Tenancy Issues](#multi-tenancy-issues)
6. [Frontend Issues](#frontend-issues)
7. [CI/CD Pipeline Issues](#cicd-pipeline-issues)
8. [Network & Connection Issues](#network--connection-issues)

---

## Database Issues

### Issue: "Role does not exist"

**Symptom**:
```
django.db.utils.OperationalError: role "root" does not exist
```

**Causes**:
- Hardcoded database user in configuration
- Environment variables not loaded
- PostgreSQL using different default user

**Solutions**:

```bash
# 1. Check current database configuration
cd backend
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASES)

# 2. Update environment variables
# config/environments/development.env
DB_USER=postgres  # Use 'postgres' for PostgreSQL
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# 3. For CI/CD workflows
# Use 'postgres' as default in GitHub Actions
env:
  DB_USER: postgres
  DB_PASSWORD: postgres
```

**Prevention**: Always use environment variables for database credentials, never hardcode.

---

### Issue: "Connection refused" to PostgreSQL

**Symptom**:
```
django.db.utils.OperationalError: connection to server at "localhost", port 5432 failed
```

**Diagnosis**:
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check PostgreSQL status
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Check if port is in use
lsof -i :5432  # Unix
netstat -an | grep 5432  # Windows
```

**Solutions**:

```bash
# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS

# Or use Docker
docker run --name projectmeats-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=projectmeats_dev \
  -p 5432:5432 \
  -d postgres:15

# Verify connection
psql -h localhost -U postgres -d projectmeats_dev
```

---

### Issue: Database Connection Timeout

**Symptom**:
```
psycopg2.OperationalError: timeout expired
```

**Solutions**:

```python
# backend/projectmeats/settings/base.py
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'OPTIONS': {
            'connect_timeout': 10,  # Add timeout
            'options': '-c statement_timeout=30000'  # 30 seconds
        }
    }
}
```

---

## Migration Problems

### Issue: "Table already exists"

**Symptom**:
```
django.db.utils.ProgrammingError: relation "app_model" already exists
```

**Causes**:
- Non-idempotent migrations
- Migration run multiple times
- Manual table creation

**Solutions**:

```bash
# Option 1: Fake the migration (marks as applied without running)
python manage.py migrate --fake app_name 0001_initial

# Option 2: Make migration idempotent (edit migration file)
# Add IF NOT EXISTS check
class Migration(migrations.Migration):
    operations = [
        migrations.RunSQL(
            sql="CREATE TABLE IF NOT EXISTS app_model (...)",
            reverse_sql="DROP TABLE IF EXISTS app_model;"
        ),
    ]

# Option 3: Reset migrations (DEVELOPMENT ONLY!)
# Backup data first!
python manage.py dumpdata > backup.json

# Drop and recreate
python manage.py migrate app_name zero
rm backend/apps/app_name/migrations/0*.py
python manage.py makemigrations app_name
python manage.py migrate

# Restore data
python manage.py loaddata backup.json
```

---

### Issue: Migration Dependency Conflicts

**Symptom**:
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Diagnosis**:
```bash
# Check migration status
python manage.py showmigrations

# View migration plan
python manage.py migrate --plan

# Check for conflicts
python manage.py makemigrations --check
```

**Solutions**:

```bash
# Option 1: Merge migrations
python manage.py makemigrations --merge

# Option 2: Reset specific app migrations (DEVELOPMENT ONLY!)
python manage.py migrate app_name zero
# Delete migrations (keep __init__.py)
rm backend/apps/app_name/migrations/0*.py
python manage.py makemigrations app_name
python manage.py migrate

# Option 3: Squash migrations
python manage.py squashmigrations app_name 0001 0010
```

---

### Issue: Missing Migrations

**Symptom**:
```
CommandError: Your models in app 'app_name' have changes that are not yet reflected in a migration
```

**Solution**:

```bash
# Create missing migrations
python manage.py makemigrations

# Check what changed
python manage.py makemigrations --dry-run --verbosity 3

# Create with specific name
python manage.py makemigrations app_name --name add_email_field

# Commit migrations
git add backend/apps/app_name/migrations/
git commit -m "feat(app_name): Add migrations for new fields"
```

**Prevention**: Install pre-commit hooks to catch this before commit:

```bash
pre-commit install
# Now makemigrations --check runs automatically on commit
```

---

## Deployment Failures

### Issue: Gunicorn Won't Start

**Symptom**:
```
Error: application crashed during startup
```

**Diagnosis**:

```bash
# Check Gunicorn logs
journalctl -u gunicorn -n 50  # Linux
docker logs <container_id>    # Docker

# Test Gunicorn manually
cd backend
gunicorn projectmeats.wsgi:application --bind 0.0.0.0:8000
```

**Common Causes & Solutions**:

1. **Django Check Failures**
   ```bash
   # Run Django system checks
   python manage.py check
   
   # Fix any errors before starting Gunicorn
   ```

2. **Missing Environment Variables**
   ```bash
   # Verify all required variables set
   python manage.py check --deploy
   
   # Add missing variables to .env or environment
   ```

3. **Import Errors**
   ```bash
   # Test imports
   python -c "from projectmeats.wsgi import application"
   
   # Install missing dependencies
   pip install -r requirements.txt
   ```

---

### Issue: Deployment Workflow Fails

**Symptom**: GitHub Actions workflow fails at specific step

**Diagnosis**:

```bash
# View workflow logs
# GitHub → Actions → Select failed workflow → View logs

# Common failure points:
# 1. Build step
# 2. Test step  
# 3. Migration step
# 4. Health check step
```

**Solutions by Step**:

**Build Failures**:
```yaml
# Check Docker build logs
- name: Debug Docker build
  run: |
    docker build -f backend/Dockerfile . -t test --progress=plain
```

**Docker Build Issues - Missing Dependencies**:

**Symptom**: Frontend Docker build fails with npm errors
```
npm ERR! Cannot read properties of undefined (reading 'dev')
npm ERR! peer dep missing: js-yaml@^4.1.0, required by @istanbuljs/load-nyc-config
```

**Root Cause**: 
- Missing or corrupted dependencies in `package-lock.json`
- `npm ci` requires exact lockfile match (unlike `npm install`)
- Docker builds use `npm ci` for reproducible builds

**Solution**:
```bash
# 1. Regenerate package-lock.json if corrupted
cd frontend
rm package-lock.json
npm install

# 2. Verify all dependencies are in lockfile
npm ls js-yaml  # Should show dependency tree
npm ls          # Check for missing peer dependencies

# 3. For CI/CD builds, ensure package-lock.json is committed
git add frontend/package-lock.json
git commit -m "fix: restore missing dependencies in package-lock.json"

# 4. Test Docker build locally
docker build -f archived/docker/Dockerfile.frontend -t test-frontend .
```

**Prevention**:
- Always commit `package-lock.json` changes with dependency updates
- Use `npm ci` in CI/CD instead of `npm install` for consistency
- Run `npm audit` to check for issues: `cd frontend && npm audit`
- Test Docker builds locally before pushing

**Fixed in**: PR #647 (November 2024) - Restored yaml dependency

---

**Test Failures**:
```yaml
# Run tests locally with same configuration
- name: Run tests
  env:
    DB_ENGINE: django_tenants.postgresql_backend
    DB_NAME: test_db
    DB_USER: postgres
    DB_PASSWORD: postgres
    DB_HOST: localhost
    DB_PORT: 5432
  run: |
    cd backend
    python manage.py test --verbosity=2
```

**Migration Failures**:
```yaml
# Check migration status
- name: Check migrations
  run: |
    cd backend
    python manage.py showmigrations
    python manage.py migrate_schemas --shared
    python manage.py migrate_schemas --tenant
```

---

### Issue: Environment Variables Not Loading

**Symptom**: Deployment works locally but fails in CI/CD

**Diagnosis**:

```bash
# In workflow, add debug step
- name: Debug Environment
  run: |
    echo "DJANGO_ENV: $DJANGO_ENV"
    echo "DB_USER: $DB_USER"
    # Don't echo passwords!
```

**Solutions**:

```yaml
# Ensure secrets are properly configured
# GitHub → Settings → Secrets → Environment secrets

# Set environment in workflow
jobs:
  deploy:
    environment: development  # or staging, production
    env:
      DJANGO_ENV: development
      DB_USER: ${{ secrets.DB_USER }}
      DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

---

## Authentication Issues

### Issue: Superuser Creation Fails

**Symptom**:
```
CommandError: DEVELOPMENT_SUPERUSER_USERNAME environment variable not set
```

**Solutions**:

```bash
# Check environment
echo $DJANGO_ENV
echo $DEVELOPMENT_SUPERUSER_USERNAME

# Set environment variables
export DJANGO_ENV=development
export DEVELOPMENT_SUPERUSER_USERNAME=admin
export DEVELOPMENT_SUPERUSER_EMAIL=admin@example.com
export DEVELOPMENT_SUPERUSER_PASSWORD=SecurePassword123!

# Or use centralized config
python config/manage_env.py setup development

# Run command
cd backend
python manage.py setup_superuser
```

**For deployment**: Ensure GitHub Secrets are set:
- `{ENV}_SUPERUSER_USERNAME`
- `{ENV}_SUPERUSER_EMAIL`
- `{ENV}_SUPERUSER_PASSWORD`

---

### Issue: Admin Access Denied

**Symptom**: User cannot access Django admin panel

**Diagnosis**:

```python
# Check user status
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='myuser')
>>> print(f"is_staff: {user.is_staff}")
>>> print(f"is_superuser: {user.is_superuser}")
>>> print(f"permissions: {user.get_all_permissions()}")
```

**Solutions**:

```python
# Make user staff (required for admin access)
user.is_staff = True
user.save()

# Grant specific permissions
from django.contrib.auth.models import Permission
perm = Permission.objects.get(codename='change_customer')
user.user_permissions.add(perm)

# Or make superuser (all permissions)
user.is_superuser = True
user.save()
```

---

### Issue: Password Reset Not Working

**Symptom**: Password change doesn't take effect

**Cause**: Password not properly hashed

**Solution**:

```python
# WRONG - Don't do this
user.password = "newpassword"
user.save()

# CORRECT - Use set_password
user.set_password("newpassword")
user.save()

# Or use management command
python manage.py changepassword username
```

---

## Multi-Tenancy Issues

### Issue: Users See Data from Other Tenants

**Symptom**: Data leakage between tenants

**Diagnosis**:

```python
# Check tenant filtering
python manage.py shell
>>> from apps.customers.models import Customer
>>> Customer.objects.count()  # Shows all tenants' data
>>> # Should filter by tenant!
```

**Solution**:

```python
# Add tenant filtering to all views
class CustomerViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        tenant = get_current_tenant()
        if not tenant:
            return Customer.objects.none()
        return Customer.objects.filter(tenant=tenant)
    
    def perform_create(self, serializer):
        serializer.save(tenant=get_current_tenant())

# Or use custom manager
class TenantAwareManager(models.Manager):
    def get_queryset(self):
        tenant = get_current_tenant()
        if not tenant:
            return super().get_queryset().none()
        return super().get_queryset().filter(tenant=tenant)

class Customer(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    objects = TenantAwareManager()
```

---

### Issue: Tenant Schema Not Created

**Symptom**:
```
relation "tenant_schema.table" does not exist
```

**Solution**:

```bash
# Create tenant schema
python manage.py shell
>>> from apps.tenants.models import Client
>>> client = Client.objects.create(
...     schema_name='tenant_name',
...     name='Tenant Display Name'
... )
>>> # Schema created automatically

# Or use management command if available
python manage.py create_tenant \
  --schema-name=tenant_name \
  --name="Tenant Name"

# Migrate tenant schema
python manage.py migrate_schemas --schema=tenant_name
```

---

## Frontend Issues

### Issue: API Connection Errors

**Symptom**:
```
Network Error: Failed to fetch
CORS Error: No 'Access-Control-Allow-Origin' header
```

**Solutions**:

```bash
# 1. Check backend is running
curl http://localhost:8000/api/

# 2. Check CORS configuration
# backend/projectmeats/settings/base.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# 3. Check frontend API URL
# frontend/src/services/api.ts
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

# 4. Check .env file
# frontend/.env.local
REACT_APP_API_URL=http://localhost:8000
```

---

### Issue: React App Won't Start

**Symptom**:
```
Error: ENOENT: no such file or directory
Module not found
```

**Solutions**:

```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear cache
npm cache clean --force
npm install

# Check Node version
node --version  # Should be 16+
nvm use 16     # If using nvm
```

---

## CI/CD Pipeline Issues

### Issue: YAML Syntax Errors

**Symptom**:
```
Workflow syntax error
unexpected token
```

**Solutions**:

```bash
# Validate YAML locally
# Install yamllint
pip install yamllint

# Check workflow files
yamllint .github/workflows/

# Or use online validator
# https://www.yamllint.com/

# Fix common issues:
# 1. Indentation (use spaces, not tabs)
# 2. Here-doc syntax
# 3. Quote special characters
```

**Example Fix**:

```yaml
# WRONG
run: echo ${VAR}

# CORRECT
run: echo "${{ env.VAR }}"

# WRONG (here-doc)
run: |
  cat << EOF
  content
  EOF  # Missing closing

# CORRECT
run: |
  cat << 'EOF'
  content
  EOF
```

---

### Issue: Tests Pass Locally, Fail in CI

**Common Causes**:

1. **Different Environment**
   ```yaml
   # Match local environment in CI
   services:
     postgres:
       image: postgres:15  # Match local version
       env:
         POSTGRES_PASSWORD: postgres
         POSTGRES_USER: postgres
   ```

2. **Missing Dependencies**
   ```yaml
   - name: Install dependencies
     run: |
       pip install -r requirements.txt
       pip install -r requirements-dev.txt  # Don't forget test deps!
   ```

3. **Timing Issues**
   ```yaml
   # Wait for services
   - name: Wait for PostgreSQL
     run: |
       until pg_isready -h localhost -p 5432; do
         sleep 1
       done
   ```

---

## Network & Connection Issues

### Issue: Supplier Network Errors

**Symptom**: Supplier API returns 500 errors or network errors

**Diagnosis**:

```python
# Check supplier configuration
python manage.py shell
>>> from apps.suppliers.models import Supplier
>>> supplier = Supplier.objects.get(id=1)
>>> print(supplier.api_endpoint)
>>> print(supplier.is_active)
```

**Solutions**:

```python
# 1. Verify API endpoint is valid
# 2. Check network connectivity
# 3. Verify authentication credentials
# 4. Check for tenant context

# Add error handling
try:
    response = requests.get(supplier.api_endpoint, timeout=30)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error(f"Supplier API error: {e}")
    # Fallback or retry logic
```

---

### Issue: Static Files Not Loading

**Symptom**: CSS/JS files returning 404 in production

**Solutions**:

```bash
# Collect static files
cd backend
python manage.py collectstatic --noinput

# Check STATIC settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.STATIC_URL)
>>> print(settings.STATIC_ROOT)

# Configure properly
# backend/projectmeats/settings/production.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Ensure web server serves static files
# nginx example:
# location /static/ {
#     alias /path/to/staticfiles/;
# }
```

---

## Quick Diagnostic Commands

### Database
```bash
# Check connection
pg_isready -h localhost -p 5432

# Connect to database
psql -h localhost -U postgres -d projectmeats_dev

# List databases
\l

# List tables
\dt

# Check table schema
\d table_name
```

### Django
```bash
# System check
python manage.py check

# Deployment check
python manage.py check --deploy

# Show migrations
python manage.py showmigrations

# Test database connection
python manage.py dbshell
```

### Docker
```bash
# Check running containers
docker ps

# View logs
docker logs <container_id> --tail 100

# Execute commands in container
docker exec -it <container_id> bash

# Rebuild container
docker-compose down
docker-compose up --build
```

### Git/CI/CD
```bash
# Check workflow syntax
actionlint .github/workflows/*.yml

# View recent workflow runs
gh workflow list
gh run list --workflow="Deploy Dev"

# View logs
gh run view <run_id>
```

---

## Getting Help

### Log Collection

Before requesting help, collect relevant logs:

```bash
# Backend logs
cd backend
python manage.py runserver > server.log 2>&1

# Frontend logs  
cd frontend
npm start > frontend.log 2>&1

# Database logs
journalctl -u postgresql -n 100  # Linux
tail -f /usr/local/var/log/postgresql@15.log  # macOS

# CI/CD logs
# GitHub → Actions → Failed workflow → Download logs
```

### Reporting Issues

Include:
1. Error message (full stack trace)
2. Steps to reproduce
3. Environment details (OS, Python version, etc.)
4. Relevant configuration
5. What you've already tried

---

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django-Tenants Docs](https://django-tenants.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [GitHub Actions Docs](https://docs.github.com/actions)

Internal Docs:
- `docs/lessons-learned/3-MONTH-RETROSPECTIVE.md`
- `docs/MIGRATION_GUIDE.md`
- `docs/AUTHENTICATION_GUIDE.md`
- `docs/DEPLOYMENT_GUIDE.md`

---

**Maintainer**: Development Team  
**Review Cycle**: Monthly  
**Last Major Update**: November 2024
