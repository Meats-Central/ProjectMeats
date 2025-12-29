# 📚 Development Environment Setup Reference

This document provides a complete reference for setting up and managing the ProjectMeats development environment.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Scripts Reference](#scripts-reference)
3. [Make Commands](#make-commands)
4. [PostgreSQL Setup](#postgresql-setup)
5. [Troubleshooting](#troubleshooting)
6. [Environment Variables](#environment-variables)
7. [Common Tasks](#common-tasks)

---

## Quick Start

### Fastest Way to Start

```bash
./start_dev.sh
```

### Stop Servers

```bash
./stop_dev.sh
```

---

## Scripts Reference

### `start_dev.sh`

Automated development server startup script that handles everything.

**What it does:**
1. ✅ Checks if PostgreSQL is installed and running
2. ✅ Starts PostgreSQL service if stopped
3. ✅ Creates database `projectmeats_dev` if it doesn't exist
4. ✅ Creates database user `projectmeats_dev` if it doesn't exist
5. ✅ Checks Python dependencies are installed
6. ✅ Checks Node dependencies are installed
7. ✅ Runs database migrations
8. ✅ Frees ports 3000 and 8000 if they're occupied
9. ✅ Starts Django backend server on port 8000
10. ✅ Starts React frontend server on port 3000
11. ✅ Saves logs to `logs/backend.log` and `logs/frontend.log`
12. ✅ Saves PIDs for easy cleanup

**Usage:**
```bash
./start_dev.sh

# View logs while running
tail -f logs/backend.log logs/frontend.log
```

**Environment Variables (optional):**
```bash
DB_NAME=projectmeats_dev      # Default database name
DB_USER=projectmeats_dev      # Default database user
DB_PASSWORD=devpassword       # Default database password
```

### `stop_dev.sh`

Gracefully stops all development servers.

**What it does:**
1. Stops backend server using saved PID
2. Stops frontend server using saved PID
3. Cleans up any remaining zombie processes
4. Removes PID files

**Usage:**
```bash
./stop_dev.sh
```

---

## Make Commands

### Server Management

```bash
# Start all servers (uses start_dev.sh)
make start

# Stop all servers (uses stop_dev.sh)
make stop

# Start servers manually (parallel)
make dev

# Start backend only
make backend

# Start frontend only
make frontend
```

### Database Commands

```bash
# Run migrations
make migrate

# Create new migrations
make migrations

# Open Django shell
make shell

# Create/update superuser
make superuser

# Sync superuser password from environment
make sync-superuser
```

### Testing

```bash
# Run all tests
make test

# Backend tests only
make test-backend

# Frontend tests only
make test-frontend
```

### Code Quality

```bash
# Format code (black, isort)
make format

# Lint code (flake8)
make lint

# Generate API documentation
make docs

# Clean build artifacts
make clean
```

### Environment Management

```bash
# Setup development environment
make env-dev

# Setup staging environment
make env-staging

# Setup production environment
make env-prod

# Validate environment configuration
make env-validate

# Generate secure secrets
make env-secrets
```

### Deployment Testing

```bash
# Test deployment configuration
make deploy-test

# Comprehensive deployment validation
make deploy-check

# Simulate full deployment process
make deploy-simulate

# Health check (requires URL)
make health-check URL=https://your-app.com
```

---

## PostgreSQL Setup

### Installation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download from: https://www.postgresql.org/download/windows/

### Manual Database Setup

If you need to manually configure the database:

```bash
# Start PostgreSQL
sudo service postgresql start

# Create database
sudo -u postgres psql -c "CREATE DATABASE projectmeats_dev;"

# Create user
sudo -u postgres psql -c "CREATE USER projectmeats_dev WITH PASSWORD 'devpassword';"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_dev TO projectmeats_dev;"

# Set owner
sudo -u postgres psql -c "ALTER DATABASE projectmeats_dev OWNER TO projectmeats_dev;"
```

### Verify Database Connection

```bash
# Test connection
psql -U projectmeats_dev -d projectmeats_dev -h localhost

# Or check from Django
cd backend
python manage.py dbshell
```

---

## Troubleshooting

### PostgreSQL Not Starting

```bash
# Check status
sudo service postgresql status

# Start service
sudo service postgresql start

# Restart service
sudo service postgresql restart

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Port Already in Use

The `start_dev.sh` script automatically handles this, but if needed manually:

```bash
# Find process on port
lsof -i :8000
lsof -i :3000

# Kill process
kill -9 <PID>

# Or kill by port
lsof -ti :8000 | xargs kill -9
lsof -ti :3000 | xargs kill -9
```

### Database Connection Refused

1. Check PostgreSQL is running:
   ```bash
   sudo service postgresql status
   ```

2. Check connection settings in `backend/.env`:
   ```bash
   cat backend/.env | grep DATABASE_URL
   ```

3. Verify database exists:
   ```bash
   sudo -u postgres psql -l | grep projectmeats_dev
   ```

4. Test connection:
   ```bash
   psql -U projectmeats_dev -d projectmeats_dev -h localhost -W
   ```

### Migration Errors

```bash
# Check migration status
cd backend
python manage.py showmigrations

# Fake a migration if needed
python manage.py migrate --fake <app_name> <migration_name>

# Reset migrations (⚠️ Development only)
python manage.py migrate --run-syncdb
```

### Frontend Won't Start

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json .cache
npm install

# Clear npm cache if issues persist
npm cache clean --force
npm install
```

### Zombie Processes

```bash
# Kill all Django processes
pkill -9 -f "manage.py runserver"

# Kill all npm/node processes
pkill -9 -f "react-app-rewired"
pkill -9 -f "npm.*start"

# Or use the stop script
./stop_dev.sh
```

---

## Environment Variables

### Backend (.env location: `backend/.env`)

```env
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-dev-key-change-in-production
DJANGO_SETTINGS_MODULE=projectmeats.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# Database (PostgreSQL)
DATABASE_URL=postgresql://projectmeats_dev:devpassword@localhost:5432/projectmeats_dev

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# API Configuration
API_VERSION=v1

# Email (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Logging
LOG_LEVEL=DEBUG
```

### Frontend (.env location: `frontend/.env`)

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENV=development
```

---

## Common Tasks

### Create a Superuser

```bash
cd backend
python manage.py createsuperuser
```

### Access Django Admin

1. Create superuser (see above)
2. Navigate to: http://localhost:8000/admin
3. Login with superuser credentials

### Run Tests

```bash
# All tests
make test

# Backend only
cd backend && python manage.py test

# Frontend only
cd frontend && npm test

# Specific test file
cd backend && python manage.py test apps.suppliers.tests.test_models
```

### View API Documentation

Once servers are running:
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Format Code

```bash
# Format backend
cd backend
black . --exclude=migrations
isort . --skip=migrations

# Or use make
make format
```

### Create New Django App

```bash
cd backend/apps
django-admin startapp <app_name>
```

### Create New Migration

```bash
cd backend
python manage.py makemigrations <app_name>
python manage.py migrate
```

### Reset Database (⚠️ Development Only)

```bash
# Drop and recreate database
sudo -u postgres psql -c "DROP DATABASE projectmeats_dev;"
sudo -u postgres psql -c "CREATE DATABASE projectmeats_dev;"
sudo -u postgres psql -c "ALTER DATABASE projectmeats_dev OWNER TO projectmeats_dev;"

# Run migrations
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### Monitor Server Logs

```bash
# If using start_dev.sh
tail -f logs/backend.log
tail -f logs/frontend.log

# Both at once
tail -f logs/*.log

# Django debug messages only
tail -f logs/backend.log | grep ERROR

# Frontend compilation errors
tail -f logs/frontend.log | grep -i error
```

### Check Server Status

```bash
# Check processes
ps aux | grep -E "(runserver|npm)" | grep -v grep

# Check ports
netstat -tuln | grep -E ":(3000|8000)"
# or
ss -tuln | grep -E ":(3000|8000)"

# Test backend API
curl http://localhost:8000/api/v1/

# Test frontend
curl http://localhost:3000/
```

---

## Performance Tips

### Backend

```bash
# Use production-like server for testing
cd backend
gunicorn projectmeats.wsgi:application --bind 0.0.0.0:8000

# Enable query logging for debugging
# Add to backend/projectmeats/settings/development.py:
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        },
    },
}
```

### Frontend

```bash
# Build production bundle
cd frontend
npm run build

# Analyze bundle size
npm install --save-dev webpack-bundle-analyzer
npm run build -- --stats
npx webpack-bundle-analyzer build/bundle-stats.json
```

---

## Additional Resources

- **Main README**: [README.md](README.md)
- **Local Development**: [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)
- **Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Branch Workflow**: [branch-workflow-checklist.md](branch-workflow-checklist.md)

---

**Need Help?** Check the documentation or create an issue on GitHub.
