# 🛠️ Developer Workflows Reference

**Last Updated:** 2025-12-01

This document provides a comprehensive reference for critical developer workflows, builds, tests, and debugging commands that aren't immediately obvious from file inspection alone. It consolidates essential development tasks in one place for quick reference.

---

## ⚡ Quick Reference

**Most Common Commands:**

```bash
# Start everything (recommended)
./start_dev.sh

# Run tests
make test                    # All tests
make test-backend           # Django tests only
make test-frontend          # React tests only

# Code quality
make format                 # Format Python code
make lint                   # Lint Python code
cd frontend && npm run lint # Lint TypeScript code

# Database
make migrate               # Apply migrations
make migrations            # Create migrations
make shell                 # Django shell

# Stop servers
./stop_dev.sh
```

**Essential Debugging:**
```bash
# Django shell with full context
cd backend && python manage.py shell

# Database shell
cd backend && python manage.py dbshell

# View logs
tail -f logs/backend.log
tail -f logs/frontend.log

# Check what's running
ps aux | grep -E "(runserver|npm)"
```

**Common Troubleshooting:**
```bash
# Kill stuck processes
lsof -ti :8000 | xargs kill -9
lsof -ti :3000 | xargs kill -9

# Reset database (development only)
cd backend && python manage.py flush

# Clear caches
find . -name "*.pyc" -delete
rm -rf frontend/node_modules/.cache
```

---

## 📋 Table of Contents

1. [Build Workflows](#build-workflows)
2. [Test Workflows](#test-workflows)
3. [Debugging Workflows](#debugging-workflows)
4. [Database Workflows](#database-workflows)
5. [Code Quality Workflows](#code-quality-workflows)
6. [Development Server Management](#development-server-management)
7. [Migration Workflows](#migration-workflows)
8. [CI/CD Integration](#cicd-integration)
9. [Performance Profiling](#performance-profiling)
10. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## 🏗️ Build Workflows

### Backend Build

Django doesn't require a traditional "build" step, but you need to prepare the application:

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Collect static files (for production)
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser (interactive)
python manage.py createsuperuser

# Or create superuser non-interactively with environment variables
DJANGO_ENV=development python manage.py setup_superuser

# Create tenant infrastructure
python manage.py create_super_tenant
```

**Key Points:**
- No compilation needed for Python/Django
- Static files collection is only needed for production deployments
- Migrations must be run before starting the server
- Multi-tenancy setup requires both `setup_superuser` and `create_super_tenant`

### Frontend Build

```bash
# Install dependencies
cd frontend
npm install

# Development build (with hot reload)
npm start

# Production build
npm run build

# Production build with explicit NODE_ENV
npm run build:production

# Type checking (without emitting files)
npm run type-check

# Serve production build locally
npm run serve

# Analyze bundle size
npm run analyze
```

**Build Output Locations:**
- **Development:** Served from memory, no files written
- **Production:** `frontend/build/` directory
- Static assets: `frontend/build/static/`

**Key Points:**
- Development builds are NOT optimized (larger, with source maps)
- Production builds are minified and optimized
- Environment variables (`REACT_APP_*`) are baked in at build time
- `npm run type-check` is useful for CI pipelines to catch TypeScript errors

---

## 🧪 Test Workflows

### Backend Tests (Django)

```bash
# Run all tests
cd backend
python manage.py test

# Run tests with verbose output
python manage.py test --verbosity=2

# Run specific app tests
python manage.py test apps.suppliers
python manage.py test apps.customers.tests

# Run specific test file
python manage.py test apps.suppliers.tests.test_models

# Run specific test class
python manage.py test apps.suppliers.tests.test_models.SupplierModelTests

# Run specific test method
python manage.py test apps.suppliers.tests.test_models.SupplierModelTests.test_create_supplier

# Run tests with coverage (using pytest)
pip install pytest-cov
pytest --cov=apps --cov-report=html --cov-report=term

# Run tests with pytest (alternative test runner)
pytest

# Run tests in parallel
python manage.py test --parallel

# Keep test database for inspection
python manage.py test --keepdb

# Run only failed tests from last run
pytest --lf  # last failed
pytest --ff  # failed first, then others
```

**Test Database:**
- Automatically created as `test_<database_name>`
- Destroyed after tests complete (unless `--keepdb` flag)
- Multi-tenancy: Both public schema and tenant schemas are set up

**Key Points:**
- Django's test runner uses unittest by default
- pytest-django provides more features (fixtures, markers, better output)
- Tests run in transactions and are rolled back automatically
- Use `@pytest.mark.django_db` for pytest tests that access the database

### Frontend Tests (React/Jest)

```bash
cd frontend

# Run tests interactively (watch mode)
npm test

# Run all tests once (CI mode)
npm run test:ci

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- src/components/Suppliers/SupplierList.test.tsx

# Run tests matching pattern
npm test -- --testNamePattern="should render"

# Update snapshots
npm test -- -u

# Run tests in silent mode (only failures)
npm test -- --silent

# Debug tests in Node
node --inspect-brk node_modules/.bin/react-app-rewired test --runInBand --no-cache
```

**Test File Locations:**
- `frontend/src/**/*.test.tsx` - Component tests
- `frontend/src/**/*.test.ts` - Utility/service tests

**Key Points:**
- Jest runs in watch mode by default (`npm test`)
- `test:ci` runs once and exits (for CI/CD pipelines)
- Snapshots are stored in `__snapshots__/` directories
- Coverage reports saved to `frontend/coverage/`

### Integration Tests

```bash
# Backend integration tests (API endpoints)
cd backend
python manage.py test apps.purchase_orders.test_api_endpoints

# Run with real database (not test DB)
# WARNING: This will affect your development database
python manage.py test --settings=projectmeats.settings.development

# Frontend integration tests
cd frontend
npm test -- --testPathPattern=integration
```

---

## 🐛 Debugging Workflows

### Backend Debugging (Django)

#### Using Django Debug Toolbar (Development)

Add to `backend/projectmeats/settings/development.py`:
```python
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

#### Using Python Debugger (pdb)

```python
# Insert breakpoint in your code
import pdb; pdb.set_trace()

# Or use Python 3.7+ built-in
breakpoint()
```

**pdb Commands:**
- `n` (next): Execute next line
- `s` (step): Step into function
- `c` (continue): Continue execution
- `l` (list): Show current code context
- `p variable`: Print variable value
- `pp variable`: Pretty-print variable
- `q` (quit): Exit debugger

#### Using VS Code Debugger

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Django: Debug Server",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/manage.py",
      "args": ["runserver", "--noreload"],
      "django": true,
      "justMyCode": true
    },
    {
      "name": "Django: Debug Tests",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/manage.py",
      "args": ["test", "apps.suppliers"],
      "django": true,
      "justMyCode": true
    }
  ]
}
```

#### Django Shell Debugging

```bash
# Interactive Python shell with Django context
cd backend
python manage.py shell

# Use IPython for better experience (if installed)
pip install ipython
python manage.py shell

# Example debugging session:
>>> from apps.suppliers.models import Supplier
>>> suppliers = Supplier.objects.all()
>>> print(suppliers.query)  # See the SQL query
>>> suppliers.explain()  # PostgreSQL query plan
```

#### Django Database Shell

```bash
# Direct database access
cd backend
python manage.py dbshell

# PostgreSQL commands:
\dt                    # List tables
\d+ table_name        # Describe table
\x                    # Expanded display (toggle)
SELECT * FROM apps_suppliers_supplier LIMIT 10;
```

#### Logging and Debugging Queries

```python
# In your view or model, log SQL queries:
from django.db import connection
from django.db import reset_queries

# Start tracking
reset_queries()

# Your code here
suppliers = Supplier.objects.select_related('created_by').all()

# Print queries
for query in connection.queries:
    print(f"SQL: {query['sql']}")
    print(f"Time: {query['time']}")
```

### Frontend Debugging (React)

#### Browser DevTools

```javascript
// Console logging
console.log('Debug:', data);
console.table(arrayData);
console.group('API Response');
console.log('Status:', response.status);
console.log('Data:', response.data);
console.groupEnd();

// Debugger statement
debugger;

// Performance tracking
console.time('API Call');
await fetchData();
console.timeEnd('API Call');
```

#### React DevTools

1. Install React DevTools browser extension
2. Open browser DevTools → React tab
3. Inspect component tree, props, and state
4. Profile component renders

#### VS Code Debugger for React

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Chrome: Debug Frontend",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend/src",
      "sourceMapPathOverrides": {
        "webpack:///src/*": "${webRoot}/*"
      }
    }
  ]
}
```

#### Network Debugging

```bash
# Watch network requests
# In browser DevTools: Network tab

# Or use curl to test API endpoints
curl -X GET http://localhost:8000/api/v1/suppliers/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -v

# Or use httpie (better than curl)
pip install httpie
http GET http://localhost:8000/api/v1/suppliers/ \
  Authorization:"Bearer YOUR_TOKEN"
```

#### Redux DevTools (if using Redux)

Install Redux DevTools extension and add to store configuration.

---

## 💾 Database Workflows

### Creating Migrations

```bash
cd backend

# Create migrations for all apps
python manage.py makemigrations

# Create migration for specific app
python manage.py makemigrations suppliers

# Create empty migration (for data migrations)
python manage.py makemigrations --empty suppliers

# Show migration plan without applying
python manage.py migrate --plan

# Show SQL for migration
python manage.py sqlmigrate suppliers 0001
```

### Applying Migrations

```bash
# Apply all migrations
python manage.py migrate

# Apply migrations for specific app
python manage.py migrate suppliers

# Apply up to specific migration
python manage.py migrate suppliers 0003

# Fake a migration (mark as applied without running)
python manage.py migrate suppliers 0003 --fake

# Rollback to previous migration
python manage.py migrate suppliers 0002

# Show migration status
python manage.py showmigrations

# Show which migrations are unapplied
python manage.py showmigrations --list
```

### Database Seeding

```bash
# Load initial data (fixtures)
cd backend
python manage.py loaddata apps/suppliers/fixtures/initial_suppliers.json

# Create fixture from existing data
python manage.py dumpdata suppliers.Supplier --indent=2 > fixtures/suppliers.json

# Custom management command for seeding
# Create: backend/apps/core/management/commands/seed_database.py
python manage.py seed_database
```

### Database Reset (Development Only)

```bash
# ⚠️ WARNING: This deletes all data!

# Option 1: Drop and recreate database (PostgreSQL)
sudo -u postgres psql -c "DROP DATABASE projectmeats_dev;"
sudo -u postgres psql -c "CREATE DATABASE projectmeats_dev;"
sudo -u postgres psql -c "ALTER DATABASE projectmeats_dev OWNER TO projectmeats_dev;"
cd backend
python manage.py migrate

# Option 2: Delete SQLite database file
rm backend/db.sqlite3
cd backend
python manage.py migrate

# Option 3: Flush database (delete all data, keep structure)
cd backend
python manage.py flush

# Recreate superuser and tenant after reset
python manage.py setup_superuser
python manage.py create_super_tenant
```

### Database Backup and Restore

```bash
# Backup PostgreSQL database
pg_dump -U projectmeats_dev -d projectmeats_dev > backup.sql

# Backup with custom format (recommended)
pg_dump -U projectmeats_dev -Fc -d projectmeats_dev > backup.dump

# Restore from SQL backup
psql -U projectmeats_dev -d projectmeats_dev < backup.sql

# Restore from custom format backup
pg_restore -U projectmeats_dev -d projectmeats_dev backup.dump

# Backup specific tables only
pg_dump -U projectmeats_dev -d projectmeats_dev -t apps_suppliers_supplier > suppliers.sql
```

### Database Inspection

```bash
# Django ORM inspection
cd backend
python manage.py shell

>>> from django.db import connection
>>> with connection.cursor() as cursor:
...     cursor.execute("SELECT COUNT(*) FROM apps_suppliers_supplier")
...     print(cursor.fetchone())

# Direct SQL via dbshell
python manage.py dbshell

-- PostgreSQL inspection commands
\dt                                  -- List all tables
\d+ apps_suppliers_supplier         -- Describe table structure
\di                                  -- List indexes
\dv                                  -- List views
SELECT * FROM django_migrations ORDER BY applied DESC LIMIT 10;
```

---

## ✅ Code Quality Workflows

### Python Code Formatting

```bash
cd backend

# Format with Black
black . --exclude=migrations

# Check what Black would change (dry-run)
black . --check --exclude=migrations

# Format specific file
black apps/suppliers/views.py

# Sort imports with isort
isort . --skip=migrations

# Check import sorting
isort . --check-only --skip=migrations

# Combine both (recommended before commit)
black . --exclude=migrations && isort . --skip=migrations
```

**Black Configuration:**
- Max line length: 88 characters (Black default)
- String quotes: Double quotes preferred
- Configuration in `pyproject.toml` or `.black` if present

### Python Linting

```bash
cd backend

# Lint with flake8
flake8 . --exclude=migrations

# Lint specific file
flake8 apps/suppliers/views.py

# Show statistics
flake8 . --exclude=migrations --statistics

# Generate HTML report
flake8 . --exclude=migrations --format=html --htmldir=flake8-report
```

**Common Flake8 Codes:**
- `E501`: Line too long
- `F401`: Module imported but unused
- `F841`: Local variable assigned but never used
- `E203`: Whitespace before ':' (ignored for Black compatibility)
- `W503`: Line break before binary operator (ignored for Black compatibility)

### Frontend Code Quality

```bash
cd frontend

# Lint TypeScript/JavaScript
npm run lint

# Auto-fix linting issues
npm run lint:fix

# Format with Prettier
npm run format

# Check formatting without changes
npx prettier --check "src/**/*.{js,jsx,ts,tsx,json,css,md}"

# Type check without emitting files
npm run type-check

# All checks (before committing)
npm run type-check && npm run lint && npm test -- --watchAll=false
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks (one-time setup)
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files

# Update hook versions
pre-commit autoupdate

# Skip hooks for a commit (not recommended)
git commit --no-verify -m "Skip hooks"
```

**Hooks Configured:**
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Large file check (>10MB)
- Merge conflict check
- Python syntax validation
- Black formatting
- isort import sorting
- flake8 linting
- Django migrations validation

---

## 🚀 Development Server Management

### Using start_dev.sh (Recommended)

```bash
# Start all services (PostgreSQL + Backend + Frontend)
./start_dev.sh

# Stop all services
./stop_dev.sh

# View logs
tail -f logs/backend.log
tail -f logs/frontend.log

# Check server status
ps aux | grep -E "(runserver|npm)" | grep -v grep
```

**What start_dev.sh does:**
1. Checks PostgreSQL is running, starts if needed
2. Creates database and user if they don't exist
3. Installs Python and Node dependencies if needed
4. Runs database migrations
5. Frees ports 3000 and 8000 if occupied
6. Starts Django backend (port 8000)
7. Starts React frontend (port 3000)
8. Saves PIDs for cleanup

### Using Makefile

```bash
# Start servers with automated script
make start

# Stop servers
make stop

# Start servers manually (parallel)
make dev

# Backend only
make backend

# Frontend only
make frontend

# Run migrations
make migrate

# Create migrations
make migrations

# Open Django shell
make shell

# Run tests
make test
make test-backend
make test-frontend

# Code quality
make format
make lint

# Cleanup
make clean
```

### Manual Server Management

```bash
# Backend (Django)
cd backend
python manage.py runserver 0.0.0.0:8000

# Backend with specific settings
DJANGO_SETTINGS_MODULE=projectmeats.settings.development python manage.py runserver

# Backend on different port
python manage.py runserver 0.0.0.0:8888

# Frontend (React)
cd frontend
npm start

# Frontend on different port
PORT=3001 npm start

# Frontend with custom env
REACT_APP_API_URL=http://localhost:8888/api/v1 npm start
```

### Kill Stuck Processes

```bash
# Find and kill processes on specific ports
lsof -ti :8000 | xargs kill -9
lsof -ti :3000 | xargs kill -9

# Kill all Django processes
pkill -9 -f "manage.py runserver"

# Kill all npm/node processes
pkill -9 -f "npm.*start"
pkill -9 -f "react-app-rewired"

# Check what's using a port
lsof -i :8000
netstat -tuln | grep 8000
ss -tuln | grep 8000
```

---

## 🔄 Migration Workflows

### Creating Data Migrations

```bash
cd backend

# Create empty migration for data changes
python manage.py makemigrations --empty suppliers --name=populate_default_suppliers

# Edit the generated migration file
# Example: backend/apps/suppliers/migrations/0004_populate_default_suppliers.py
```

Example data migration:
```python
from django.db import migrations

def populate_suppliers(apps, schema_editor):
    Supplier = apps.get_model('suppliers', 'Supplier')
    Supplier.objects.get_or_create(
        name='Default Supplier',
        defaults={'email': 'supplier@example.com'}
    )

def reverse_populate(apps, schema_editor):
    Supplier = apps.get_model('suppliers', 'Supplier')
    Supplier.objects.filter(name='Default Supplier').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('suppliers', '0003_auto_20240101_0000'),
    ]

    operations = [
        migrations.RunPython(populate_suppliers, reverse_populate),
    ]
```

### Handling Migration Conflicts

```bash
# Check for conflicts
python manage.py makemigrations --check

# Show migration plan
python manage.py migrate --plan

# Merge migrations (if multiple branches created migrations)
python manage.py makemigrations --merge

# Fake initial migration (for existing tables)
python manage.py migrate suppliers --fake-initial
```

### Rolling Back Migrations

```bash
# Rollback to previous migration
python manage.py migrate suppliers 0002

# Rollback all migrations for an app
python manage.py migrate suppliers zero

# Show what would be rolled back
python manage.py migrate suppliers 0002 --plan
```

### Testing Migrations

```bash
# Test forward and backward migration
cd backend

# Apply migration
python manage.py migrate suppliers 0004

# Verify data/schema
python manage.py shell
>>> from apps.suppliers.models import Supplier
>>> Supplier.objects.count()

# Rollback
python manage.py migrate suppliers 0003

# Verify rollback worked
python manage.py shell
>>> from apps.suppliers.models import Supplier
>>> Supplier.objects.count()

# Re-apply
python manage.py migrate suppliers 0004
```

---

## 🔗 CI/CD Integration

### Running Tests Like CI

```bash
# Backend tests (CI mode)
cd backend
python manage.py test --parallel --verbosity=2

# Frontend tests (CI mode)
cd frontend
npm run test:ci

# Pre-commit hooks (run all)
pre-commit run --all-files

# Check migrations are up to date
cd backend
python manage.py makemigrations --check --dry-run

# Combined CI checks (what CI actually runs)
cd backend
python manage.py test --parallel && \
python manage.py makemigrations --check && \
cd ../frontend && \
npm run test:ci && \
npm run type-check && \
npm run lint
```

### Local CI Simulation

Create a script `scripts/run_ci_checks.sh`:
```bash
#!/bin/bash
set -e

echo "=== Running Backend Tests ==="
cd backend
python manage.py test --parallel --verbosity=2

echo "=== Checking Migrations ==="
python manage.py makemigrations --check

echo "=== Running Frontend Tests ==="
cd ../frontend
npm run test:ci

echo "=== Type Checking ==="
npm run type-check

echo "=== Linting Frontend ==="
npm run lint

echo "=== All CI Checks Passed! ==="
```

Make it executable and run:
```bash
chmod +x scripts/run_ci_checks.sh
./scripts/run_ci_checks.sh
```

### GitHub Actions Workflows

Key workflows in `.github/workflows/`:
- `11-dev-deployment.yml`: Deploy to development
- `12-uat-deployment.yml`: Deploy to UAT/staging
- `13-prod-deployment.yml`: Deploy to production
- `promote-dev-to-uat.yml`: Promote dev to UAT
- `promote-uat-to-main.yml`: Promote UAT to main

**Trigger workflow manually:**
```bash
# Using GitHub CLI
gh workflow run 11-dev-deployment.yml

# View workflow runs
gh run list

# View logs for a run
gh run view <run-id> --log
```

---

## 📊 Performance Profiling

### Backend Performance Profiling

#### Django Debug Toolbar

Add to `backend/projectmeats/settings/development.py`:
```python
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ['127.0.0.1']
```

Then visit any page and check the debug toolbar for:
- SQL queries and their execution time
- Cache hits/misses
- Template rendering time
- Signal receivers

#### Using cProfile

```bash
cd backend

# Profile a management command
python -m cProfile -o profile.stats manage.py migrate

# Analyze profile
python -m pstats profile.stats
>>> sort cumtime
>>> stats 20

# Profile tests
python -m cProfile -o test_profile.stats manage.py test apps.suppliers
```

#### Django Silk (Alternative profiling tool)

```bash
pip install django-silk

# Add to INSTALLED_APPS in settings
INSTALLED_APPS += ['silk']

# Add to urls.py
urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

# Run migrations
python manage.py migrate

# Visit http://localhost:8000/silk/ for profiling data
```

### Frontend Performance Profiling

#### React DevTools Profiler

1. Open React DevTools
2. Go to "Profiler" tab
3. Click "Record"
4. Interact with app
5. Click "Stop"
6. Analyze component render times

#### Chrome DevTools Performance

1. Open Chrome DevTools (F12)
2. Go to "Performance" tab
3. Click "Record"
4. Interact with app
5. Click "Stop"
6. Analyze flame chart for bottlenecks

#### Lighthouse

```bash
# Run Lighthouse in Chrome DevTools
# Or use CLI
npm install -g lighthouse
lighthouse http://localhost:3000 --view

# Generate report
lighthouse http://localhost:3000 --output html --output-path report.html
```

#### Bundle Analysis

```bash
cd frontend

# Build with stats
npm run build -- --stats

# Analyze bundle
npx webpack-bundle-analyzer build/bundle-stats.json

# Alternative: Use source-map-explorer
npm install -g source-map-explorer
npm run build
source-map-explorer build/static/js/*.js
```

---

## 🚨 Troubleshooting Common Issues

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo service postgresql status

# Start PostgreSQL
sudo service postgresql start

# Test connection
psql -U projectmeats_dev -d projectmeats_dev -h localhost

# Check DATABASE_URL in .env
cat backend/.env | grep DATABASE_URL

# Verify database exists
sudo -u postgres psql -l | grep projectmeats_dev
```

### Migration Issues

```bash
# Fake a problematic migration
cd backend
python manage.py migrate suppliers 0004 --fake

# Show migration status
python manage.py showmigrations

# Reset migrations (nuclear option - development only)
# 1. Delete migration files (except __init__.py)
# 2. Drop database and recreate
# 3. Run makemigrations and migrate
```

### Port Conflicts

```bash
# Kill process on port 8000
lsof -ti :8000 | xargs kill -9

# Kill process on port 3000
lsof -ti :3000 | xargs kill -9

# Or use the start script which handles this automatically
./start_dev.sh
```

### Module Not Found Errors (Python)

```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify Django is installed
python -c "import django; print(django.get_version())"
```

### Module Not Found Errors (Node)

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# Clear React cache
rm -rf .cache

# Verify React is installed
npm list react
```

### Build Failures (Frontend)

```bash
cd frontend

# Clear cache
rm -rf node_modules/.cache

# Increase memory limit
NODE_OPTIONS="--max-old-space-size=4096" npm run build

# Disable source maps (faster builds)
GENERATE_SOURCEMAP=false npm run build

# Check for TypeScript errors
npm run type-check
```

### Test Failures

```bash
# Backend: Clear test database
cd backend
rm db.sqlite3  # if using SQLite
python manage.py test --keepdb --verbosity=2

# Frontend: Clear Jest cache
cd frontend
npm test -- --clearCache
npm test
```

### Authentication Issues (Development)

```bash
# Reset superuser
cd backend
python manage.py setup_superuser

# Create root tenant
python manage.py create_super_tenant

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"WATERMELON1219"}'
```

---

## 📚 Additional Resources

- **Main Documentation**: [README.md](README.md)
- **Local Development**: [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Testing Strategy**: [docs/TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)
- **Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Backend Architecture**: [docs/BACKEND_ARCHITECTURE.md](docs/BACKEND_ARCHITECTURE.md)
- **Frontend Architecture**: [docs/FRONTEND_ARCHITECTURE.md](docs/FRONTEND_ARCHITECTURE.md)

---

## 🤝 Need Help?

- **Documentation Hub**: [docs/README.md](docs/README.md)
- **GitHub Issues**: [Create an issue](https://github.com/Meats-Central/ProjectMeats/issues)
- **GitHub Discussions**: [Ask a question](https://github.com/Meats-Central/ProjectMeats/discussions)

---

**Remember:** This is a living document. If you discover new workflows or better approaches, please update this document and submit a PR!
