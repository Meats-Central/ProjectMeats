# ProjectMeats - Quick Reference Guide

**For detailed information, see [PROJECT_STRUCTURE_OVERVIEW.md](PROJECT_STRUCTURE_OVERVIEW.md)**

---

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Clone and setup
git clone https://github.com/Meats-Central/ProjectMeats.git
cd ProjectMeats
pre-commit install  # REQUIRED

# 2. Start everything
./start_dev.sh

# 3. Access
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/api/docs/
# Admin:     http://localhost:8000/admin/
```

---

## 📁 Project Structure At-a-Glance

```
ProjectMeats/
├── backend/              # Django 4.2.7 + DRF (1.4MB)
│   ├── apps/            # 14 business apps
│   │   ├── suppliers/
│   │   ├── customers/
│   │   ├── purchase_orders/
│   │   ├── accounts_receivables/
│   │   ├── tenants/     # Multi-tenancy (custom shared-schema)
│   │   ├── ai_assistant/
│   │   └── ...
│   └── projectmeats/    # Django config
│
├── frontend/            # React 18.2.0 + TypeScript (2.2MB)
│   └── src/
│       ├── components/  # 30+ UI components
│       ├── pages/       # 12 main screens
│       └── services/    # API layer
│
├── mobile/              # React Native (108KB)
├── docs/                # Documentation (1.6MB, 80+ files)
├── config/              # Environment configs
└── .github/workflows/   # 15 CI/CD workflows
```

---

## 🔑 Key Technologies

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Django + DRF | 4.2.7 + 3.14.0 |
| Database | PostgreSQL | 12+ (SQLite fallback) |
| Frontend | React + TypeScript | 18.2.0 + 4.9.5 |
| UI | Ant Design | 5.27.3 |
| Mobile | React Native | Latest |
| Multi-Tenancy | Custom Shared-Schema | (NOT django-tenants) |
| Testing | pytest + Jest | 95+ tests |
| CI/CD | GitHub Actions | 15 workflows |
| Deployment | DigitalOcean | App Platform |

---

## 💻 Essential Commands

### Development

```bash
# Start/Stop
./start_dev.sh          # Start all (PostgreSQL + Backend + Frontend)
./stop_dev.sh           # Stop all
make dev                # Start backend + frontend (manual)
make start              # Uses start_dev.sh
make stop               # Uses stop_dev.sh

# Individual servers
make backend            # Start Django only
make frontend           # Start React only
```

### Database

```bash
make migrate            # Apply migrations
make migrations         # Create new migrations
make shell              # Django shell
make superuser          # Create superuser + tenant
make sync-superuser     # Sync superuser from env
```

### Testing

```bash
make test               # All tests
make test-backend       # Django tests only
make test-frontend      # React tests only
```

### Code Quality

```bash
make format             # Format (black, isort)
make lint               # Lint (flake8)
make clean              # Clean artifacts

# Pre-commit (required)
pre-commit install      # Setup hooks
pre-commit run --all-files  # Test hooks
```

### Environment

```bash
python config/manage_env.py setup development
python config/manage_env.py setup staging
python config/manage_env.py setup production
python config/manage_env.py validate
```

### Deployment Testing

```bash
make deploy-test        # Test config
make deploy-check       # Full validation
make health-check URL=https://your-app.com
python simulate_deployment.py --environment production
```

---

## 🏗️ Core Business Apps

| App | Purpose | Lines (Models) | Key Features |
|-----|---------|----------------|--------------|
| `suppliers` | Supplier management | 218 | Profiles, performance tracking |
| `customers` | Customer relationships | ~160 | CRM, preferences, history |
| `purchase_orders` | PO processing | 568 | Multi-item orders, workflows |
| `accounts_receivables` | Payment tracking | ~100 | AR reports, aging |
| `tenants` | Multi-tenancy | 470 | Users, roles, invitations |
| `ai_assistant` | GPT-4 integration | ~200 | Chat, document processing |
| `products` | Product catalog | 177 | NAMP codes, specifications |
| `sales_orders` | Sales management | 163 | Customer orders |
| `invoices` | Invoice generation | ~50 | PDF generation |
| `plants` | Processing facilities | ~100 | Capacity management |
| `carriers` | Shipping carriers | ~80 | Rate management |
| `contacts` | Contact management | ~90 | Unified contacts |
| `bug_reports` | Bug reporting | ~30 | GitHub integration |
| `core` | Shared utilities | ~200 | Auth, preferences, utils |

---

## 🔐 Multi-Tenancy ⚠️ IMPORTANT

**ProjectMeats uses CUSTOM SHARED-SCHEMA multi-tenancy**

❌ **NOT using:**
- django-tenants schema-based isolation
- TenantMixin / DomainMixin
- SHARED_APPS / TENANT_APPS
- django_tenants.postgresql_backend

✅ **Using instead:**
- Custom `Tenant` model with foreign keys
- `TenantMiddleware` for tenant resolution
- Role-based permissions (Owner, Admin, Manager, Member, Guest)
- Invitation system for user onboarding
- Shared database schema for all tenants

**Models:**
- `Tenant` - Organization entity
- `TenantUser` - User-tenant association with roles
- `TenantDomain` - Domain routing
- `TenantInvitation` - User invitation system

---

## 🌲 Git Workflow

### Branches

```
development  → Development and testing
UAT          → Staging/acceptance
main         → Production
```

### Branch Naming

```
feature/<description>
fix/<description>
hotfix/<description>
```

### Workflow

1. Create feature branch from `development`
2. Commit with pre-commit hooks
3. PR to `development` → review & merge
4. Auto-PR to `UAT` (via workflow)
5. Test in UAT → review & merge
6. Auto-PR to `main` (via workflow)
7. Deploy to production

**⚠️ NEVER push directly to `UAT` or `main`**

---

## 📚 Documentation

### Must-Read

- [PROJECT_STRUCTURE_OVERVIEW.md](PROJECT_STRUCTURE_OVERVIEW.md) - Complete project guide
- [README.md](README.md) - Main documentation
- [docs/README.md](docs/README.md) - Documentation hub
- [branch-workflow-checklist.md](branch-workflow-checklist.md) - Git workflow
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guide

### Guides

- [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) - Database migrations
- [docs/AUTHENTICATION_GUIDE.md](docs/AUTHENTICATION_GUIDE.md) - Auth & permissions
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues
- [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Deployment
- [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) - Local dev setup

### Architecture

- [docs/BACKEND_ARCHITECTURE.md](docs/BACKEND_ARCHITECTURE.md) - Django patterns
- [docs/FRONTEND_ARCHITECTURE.md](docs/FRONTEND_ARCHITECTURE.md) - React structure
- [docs/MULTI_TENANCY_GUIDE.md](docs/MULTI_TENANCY_GUIDE.md) - Multi-tenancy
- [docs/TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md) - Testing approach

---

## 🔧 Environment Variables

### Development (`config/environments/development.env`)

```bash
# Database (PostgreSQL recommended)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=projectmeats_dev
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Superuser
DEVELOPMENT_SUPERUSER_USERNAME=admin
DEVELOPMENT_SUPERUSER_EMAIL=admin@meatscentral.com
DEVELOPMENT_SUPERUSER_PASSWORD=DevAdmin123!SecurePass

# Django
DJANGO_ENV=development
DEBUG=True
SECRET_KEY=dev-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Staging/Production

Set as GitHub Secrets:
- `STAGING_SUPERUSER_USERNAME/EMAIL/PASSWORD`
- `PRODUCTION_SUPERUSER_USERNAME/EMAIL/PASSWORD`
- `DATABASE_URL`
- `SECRET_KEY`
- `DO_ACCESS_TOKEN`

---

## 🧪 Testing

### Backend (95+ tests)

```bash
# All tests
cd backend && python manage.py test

# With pytest
cd backend && pytest

# With coverage
cd backend && pytest --cov

# Specific app
cd backend && python manage.py test apps.tenants

# Specific test
cd backend && python manage.py test apps.tenants.tests.TestTenantMiddleware
```

### Frontend

```bash
# All tests
cd frontend && npm test

# CI mode
cd frontend && npm run test:ci

# With coverage
cd frontend && npm test -- --coverage
```

---

## 🚀 CI/CD Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `11-dev-deployment.yml` | Push to `development` | Dev deployment |
| `12-uat-deployment.yml` | Push to `UAT` | UAT deployment |
| `13-prod-deployment.yml` | Push to `main` | Production deployment |
| `promote-dev-to-uat.yml` | Merge to `development` | Auto-PR to UAT |
| `promote-uat-to-main.yml` | Merge to `UAT` | Auto-PR to main |
| `21-db-backup-restore-do.yml` | Schedule | Database backups |
| `51-cleanup-branches-tags.yml` | Schedule | Cleanup |

---

## 🐛 Common Issues

### Pre-commit hooks not running

```bash
pre-commit install
pre-commit run --all-files
```

### Module not found

```bash
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### Database connection error

```bash
# Check PostgreSQL is running
pg_isready

# Or use SQLite fallback
# Set DB_ENGINE=django.db.backends.sqlite3 in .env
```

### CORS errors

```bash
# Ensure both servers running on correct ports
# Backend: 8000, Frontend: 3000
```

### Migration conflicts

```bash
cd backend
python manage.py showmigrations
python manage.py migrate --fake-initial
```

---

## 📞 Getting Help

1. Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Search GitHub issues
3. Review [PROJECT_STRUCTURE_OVERVIEW.md](PROJECT_STRUCTURE_OVERVIEW.md)
4. Create new issue with details

---

## 🎯 Key Technical Decisions

1. **Multi-Tenancy:** Custom shared-schema (NOT django-tenants)
2. **Database:** PostgreSQL primary, SQLite fallback
3. **API Docs:** drf-spectacular (OpenAPI 3.0)
4. **Frontend:** React + TypeScript (not Next.js)
5. **State:** React Context (not Redux)
6. **UI:** Ant Design + Styled Components
7. **Testing:** pytest-django + Jest
8. **CI/CD:** GitHub Actions
9. **Deployment:** DigitalOcean App Platform
10. **Code Quality:** Pre-commit hooks (required)

---

## 📊 Project Metrics

- **Backend:** 4,534+ lines (models + views)
- **Frontend:** 30+ components
- **Tests:** 95+ tests
- **Documentation:** 80+ files
- **Workflows:** 15 CI/CD workflows
- **Apps:** 14 business applications
- **Models:** 20+ major models
- **API Endpoints:** 50+ REST endpoints

---

## 🔗 Important URLs

### Local Development
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

### Production
- Dev: `dev2-backend.ondigitalocean.app`
- UAT: `uat2-backend.ondigitalocean.app`
- Prod: `prod2-backend.ondigitalocean.app`

---

## 💡 Pro Tips

1. **Always run `pre-commit install` after clone** - Prevents CI failures
2. **Use `./start_dev.sh`** - Handles everything automatically
3. **Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) first** - Common issues documented
4. **Never push to UAT/main directly** - Use promotion workflow
5. **Test locally with PostgreSQL** - Matches production
6. **Run tests before PR** - `make test`
7. **Format code before commit** - `make format`
8. **Update docs with code changes** - Keep docs in sync
9. **Use Makefile commands** - Easier than remembering full commands
10. **Read [PROJECT_STRUCTURE_OVERVIEW.md](PROJECT_STRUCTURE_OVERVIEW.md)** - Comprehensive guide

---

**Last Updated:** 2025-12-01  
**Quick Reference Version:** 1.0
