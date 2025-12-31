# Project Meats

**Multi-tenant meat supply-chain platform** - Shared-schema multi-tenancy with Django + React

---

## 📚 Documentation

### Quick Links
- **Architecture**: [docs/GOLDEN_PIPELINE.md](docs/GOLDEN_PIPELINE.md) - Authoritative deployment architecture
- **Development**: [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) - Local setup guide
- **API Reference**: [docs/ENVIRONMENT_VARS.md](docs/ENVIRONMENT_VARS.md) - Environment variables
- **Contributing**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) - Contribution guidelines

### Core Documentation
| Document | Purpose |
|----------|---------|
| [GOLDEN_PIPELINE.md](docs/GOLDEN_PIPELINE.md) | 🏆 Deployment architecture (authoritative) |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture overview |
| [CONFIGURATION_AND_SECRETS.md](docs/CONFIGURATION_AND_SECRETS.md) | Secret management guide |
| [DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md) | Developer workflow |
| [QUICK_START.md](docs/QUICK_START.md) | Quick start guide |

### Operations
| Document | Purpose |
|----------|---------|
| [ENVIRONMENT_VARS.md](docs/ENVIRONMENT_VARS.md) | Environment variable reference |
| [TENANT_ACCESS_CONTROL.md](docs/TENANT_ACCESS_CONTROL.md) | Tenant access patterns |
| [GUEST_MODE_IMPLEMENTATION.md](docs/GUEST_MODE_IMPLEMENTATION.md) | Guest user system |
| [INVITE_ONLY_SYSTEM.md](docs/INVITE_ONLY_SYSTEM.md) | Invitation system |

### Setup & Configuration
| Document | Purpose |
|----------|---------|
| [LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) | Local development setup |
| [DEV_SETUP_REFERENCE.md](docs/DEV_SETUP_REFERENCE.md) | Development reference |
| [POSTGRESQL_MIGRATION_GUIDE.md](docs/POSTGRESQL_MIGRATION_GUIDE.md) | Database migration guide |

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Node.js 18+
- Python 3.12+
- PostgreSQL 15+ (via Docker)

### Local Development

```bash
# 1. Start Docker services (PostgreSQL, Redis)
make dev

# 2. Run migrations (standard Django, NOT migrate_schemas)
make migrate-all

# 3. Create superuser
cd backend && python manage.py createsuperuser

# 4. Start development servers
# Terminal 1: Backend
cd backend && python manage.py runserver

# Terminal 2: Frontend
cd frontend && npm start
```

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

---

## 🏗️ Architecture

### Multi-Tenancy: Shared Schema

ProjectMeats uses **shared-schema multi-tenancy** with row-level isolation:

```python
# ✅ CORRECT: Shared schema with tenant ForeignKey
class Customer(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    
    objects = TenantManager()  # Required for tenant isolation
```

❌ **NEVER** use `django-tenants` or schema-based isolation  
✅ **ALWAYS** use `tenant` ForeignKey with `TenantManager`

### Tech Stack

**Backend:**
- Django 5.x + Django REST Framework
- PostgreSQL 15 (shared schema)
- Redis (caching)
- Celery (async tasks)

**Frontend:**
- React 19 + TypeScript 5.9
- React Router v7
- TanStack Query (data fetching)
- Tailwind CSS

**Infrastructure:**
- Docker + Docker Compose
- GitHub Actions (CI/CD)
- DigitalOcean (hosting)
- Nginx (reverse proxy)

---

## 📂 Repository Structure

```
ProjectMeats/
├── backend/              # Django backend
│   ├── apps/            # Shared apps (tenants, core, etc.)
│   ├── tenant_apps/     # Tenant-specific apps
│   ├── projectmeats/    # Django project settings
│   └── manage.py
├── frontend/            # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── mobile/              # React Native app
├── config/              # Configuration & secrets
│   ├── env.manifest.json  # Secret definitions (source of truth)
│   └── manage_env.py      # Secret audit tool
├── docs/                # Documentation
│   ├── GOLDEN_PIPELINE.md  # Authoritative architecture
│   ├── archived/           # Temporary/fix documentation
│   └── ...
├── scripts/             # Utility scripts
├── .github/workflows/   # CI/CD pipelines
└── docker-compose.yml   # Local development
```

---

## 🔐 Environment Variables

All environment variables are defined in `config/env.manifest.json` (single source of truth).

### Audit Secrets

```bash
# Check if all required secrets are configured
python config/manage_env.py audit
```

### Common Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Django secret key | (50+ random characters) |
| `DJANGO_SETTINGS_MODULE` | Settings module | `projectmeats.settings.development` |

**Full Reference:** [docs/ENVIRONMENT_VARS.md](docs/ENVIRONMENT_VARS.md)

---

## 🧪 Testing

```bash
# Backend tests
cd backend
python manage.py test apps/ --verbosity=2

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

---

## 🚢 Deployment

Deployments follow the **Golden Pipeline** architecture:

```
development → UAT → main (production)
     ↓         ↓        ↓
   dev-env  uat-env  prod-env
```

**Deployment Guide:** [docs/GOLDEN_PIPELINE.md](docs/GOLDEN_PIPELINE.md)

### Key Principles

1. **Immutable Images**: SHA-tagged Docker images
2. **Bastion Tunnel**: Migrations via SSH tunnel (port 5433)
3. **Environment Secrets**: Scoped to GitHub Environments
4. **Health Checks**: Automated verification post-deploy

---

## 👥 Contributing

We welcome contributions! Please read our [Contributing Guide](docs/CONTRIBUTING.md).

### Branch Workflow

```bash
# 1. Create feature branch from development
git checkout development
git pull origin development
git checkout -b feature/your-feature-name

# 2. Make changes and commit
git add .
git commit -m "feat: your feature description"

# 3. Push and create PR
git push -u origin feature/your-feature-name
gh pr create --base development
```

### Development Rules

- **Multi-Tenancy**: All tenant models MUST use `objects = TenantManager()`
- **Migrations**: Use standard Django migrations (NOT `migrate_schemas`)
- **Testing**: Write tests for all new features
- **Documentation**: Update docs for architectural changes

---

## 📖 Additional Resources

### Configuration
- [config/env.manifest.json](config/env.manifest.json) - Secret definitions
- [config/README.md](config/README.md) - Configuration guide

### Workflows
- [.github/workflows/](. github/workflows/) - CI/CD pipelines
- [docs/branch-workflow-checklist.md](docs/branch-workflow-checklist.md) - Branch workflow

### Scripts
- [scripts/](scripts/) - Utility scripts
- [scripts/verify_golden_state.sh](scripts/verify_golden_state.sh) - Architecture verification

---

## 📝 License

Proprietary - All rights reserved

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/Meats-Central/ProjectMeats/issues)
- **Docs**: [docs/](docs/)
- **Architecture**: [docs/GOLDEN_PIPELINE.md](docs/GOLDEN_PIPELINE.md)

---

**Last Updated**: December 29, 2025  
**Status**: ✅ Active Development  
**Architecture Version**: Golden Pipeline v1.0

