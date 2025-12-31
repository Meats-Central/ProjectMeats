# V1.0.0 Golden Release Preparation

This document contains the commands and release notes for tagging the stable V1 baseline.

## Git Tagging Commands

After this cleanup PR is merged to `main`, execute these commands:

```bash
# Checkout the main branch
git checkout main
git pull origin main

# Create the golden tag
git tag -a v1.0.0-golden -m "V1.0.0 Golden Release - Stable Production Baseline"

# Push the tag to origin
git push origin v1.0.0-golden

# Verify the tag was created
git tag -l "v1.0.0*"
git show v1.0.0-golden
```

## GitHub Release Draft

Use the following content when creating the GitHub Release:

---

### Release Title
**V1.0.0 Golden - Stable Production Baseline**

### Release Description

```markdown
# 🎉 ProjectMeats V1.0.0 Golden Release

This release marks the **stable production baseline** for ProjectMeats after successful deployment to production (meatscentral.com).

## 🌟 Key Architecture Features

### Multi-Tenancy: Shared Schema Isolation
- **Pattern**: Row-level security via `tenant_id` ForeignKey
- **Database**: Single PostgreSQL cluster, shared `public` schema
- **Isolation**: All business models filtered by `tenant=request.tenant`
- **NO** schema-based multi-tenancy (django-tenants explicitly rejected)

### Deployment: GitHub Actions Pipeline
- **Pipeline**: Development → UAT → Production
- **Workflow Files**:
  - `main-pipeline.yml` - Orchestrates environment routing
  - `reusable-deploy.yml` - Reusable deployment worker
- **Container Registry**: DigitalOcean Container Registry (DOCR)
- **Image Tagging**: Immutable SHA-based tags (e.g., `production-{sha}`)

### Migrations: Bastion Tunnel Pattern
- **Execution**: GitHub Actions runner via SSH tunnel
- **Tunnel**: Local port 5433 → Private database port 5432
- **Command**: `python manage.py migrate --fake-initial --noinput`
- **Idempotent**: Safe to re-run multiple times
- **Security**: Database remains in private network

### Configuration: Manifest-Based Secrets
- **Source of Truth**: `config/env.manifest.json` (v3.3)
- **Audit Tool**: `python config/manage_env.py audit`
- **Validation**: Pre-deployment secret verification
- **Environments**: dev-backend, dev-frontend, uat-backend, uat-frontend, production-backend, production-frontend

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.x + Django REST Framework
- **Database**: PostgreSQL 15 (DigitalOcean Managed)
- **Authentication**: JWT-based with Django Rest Auth
- **API**: RESTful with Swagger/OpenAPI documentation

### Frontend
- **Framework**: React 19 + TypeScript 5.9
- **Build System**: In migration to Vite (currently react-app-rewired bridge)
- **UI Library**: Material-UI / Custom components
- **State Management**: React hooks + React Query

### Mobile (Planned)
- **Framework**: React Native
- **Shared Code**: TypeScript utilities and types

### Infrastructure
- **Hosting**: DigitalOcean Droplets
- **Container Registry**: DigitalOcean Container Registry
- **Database**: DigitalOcean Managed PostgreSQL
- **CI/CD**: GitHub Actions
- **Reverse Proxy**: Nginx (host-level + containerized)

## 📦 What's Included in V1.0.0

### Core Features
- ✅ Multi-tenant architecture with row-level security
- ✅ User authentication and authorization
- ✅ Guest mode for anonymous access
- ✅ Invitation-based user onboarding
- ✅ Role-based permissions (Owner, Admin, Staff, Member, Guest)
- ✅ RESTful API with comprehensive endpoints
- ✅ Admin dashboard for tenant management

### Deployment Infrastructure
- ✅ Production deployment at meatscentral.com
- ✅ UAT environment at uat.meatscentral.com
- ✅ Development environment at dev.meatscentral.com
- ✅ Automated CI/CD pipeline with health checks
- ✅ Zero-downtime deployments
- ✅ Automated database migrations via bastion tunnel

### Documentation
- ✅ Golden Pipeline documentation (GOLDEN_PIPELINE.md)
- ✅ Configuration and secrets management guide
- ✅ Development workflow guidelines
- ✅ Frontend environment variables guide
- ✅ Authentication and authorization explained
- ✅ Architecture documentation

### Developer Experience
- ✅ Organized script directories (dev, maintenance, testing)
- ✅ Integration test suite
- ✅ Environment manifest system
- ✅ Automated secret auditing
- ✅ Pre-commit hooks for code quality
- ✅ GitHub Copilot instructions

## 🔒 Security Highlights

- Database in private network (bastion access only)
- SSH tunnel for migrations (no direct runner access)
- Environment-scoped secrets in GitHub
- Immutable container images (SHA-tagged)
- HTTPS/TLS for all external traffic
- JWT-based API authentication
- Row-level tenant isolation

## 📊 Repository Organization

This release includes comprehensive repository cleanup:
- Historical documentation archived to `docs/archive/v1-launch-logs/`
- Utility scripts organized into categorized directories
- Deprecated `.env.example` files pointing to manifest system
- Clear separation of dev, testing, and maintenance scripts

## 🚀 Getting Started

### For Developers
```bash
# Clone the repository
git clone https://github.com/Meats-Central/ProjectMeats.git
cd ProjectMeats

# Set up local environment
python scripts/dev/setup_env.py

# Start development servers
./scripts/dev/start_dev.sh
```

### For Operators
```bash
# Audit secrets before deployment
python config/manage_env.py audit

# Verify golden state
./scripts/maintenance/verify_golden_state.sh

# Deploy via GitHub Actions (automatic on push to main)
```

## 📖 Documentation

- **Golden Pipeline**: `docs/GOLDEN_PIPELINE.md`
- **Configuration**: `docs/CONFIGURATION_AND_SECRETS.md`
- **Frontend Variables**: `docs/FRONTEND_ENVIRONMENT_VARIABLES.md`
- **Development Workflow**: `docs/DEVELOPMENT_WORKFLOW.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Contributing**: `docs/CONTRIBUTING.md`

## 🎯 What's Next

This V1.0.0 golden release establishes the baseline. Future development will focus on:
- Frontend migration from react-app-rewired to Vite
- Mobile application development (React Native)
- Additional tenant management features
- Enhanced analytics and reporting
- Performance optimizations
- Feature enhancements based on user feedback

## 🙏 Acknowledgments

This stable release represents months of architectural iteration, including:
- Multiple deployment strategy refinements
- Schema-based multi-tenancy evaluation (and rejection)
- Secret management system evolution
- CI/CD pipeline optimization
- Documentation standardization

## 📝 Release Notes

### Changed
- Organized scripts into categorized directories (dev, maintenance, testing)
- Archived historical documentation to `docs/archive/v1-launch-logs/`
- Consolidated environment configuration to manifest-based system
- Standardized workflow files to use immutable image tags

### Fixed
- Migration execution now uses bastion tunnel pattern exclusively
- Secret drift eliminated via manifest validation
- Workflow health checks target correct ports
- Documentation accurately reflects production implementation

### Deprecated
- `.env.example` files (replaced by manifest + docs)
- Schema-based multi-tenancy patterns (never implemented)
- Manual migration execution (replaced by automated pipeline)

### Security
- Database isolated in private network
- Migrations execute via SSH tunnel (no direct access)
- Container images are immutable (SHA-tagged)
- Secrets validated pre-deployment

---

**Full Changelog**: https://github.com/Meats-Central/ProjectMeats/commits/v1.0.0-golden

**Documentation**: [docs/GOLDEN_PIPELINE.md](docs/GOLDEN_PIPELINE.md)

**Issues**: https://github.com/Meats-Central/ProjectMeats/issues
```

---

## Verification

After creating the release:

1. **Tag Verification**:
   ```bash
   git tag -l | grep v1.0.0
   git show v1.0.0-golden
   ```

2. **Release Verification**:
   - Visit https://github.com/Meats-Central/ProjectMeats/releases
   - Verify the release appears with correct tag
   - Check that release notes are properly formatted

3. **Documentation Verification**:
   - Ensure all linked documentation files exist
   - Verify GOLDEN_PIPELINE.md is accurate
   - Check that archive structure is correct

## Notes

- This tag should be created AFTER the cleanup PR is merged to `main`
- The tag name `v1.0.0-golden` indicates this is the golden/stable baseline
- Future releases should follow semantic versioning: v1.0.1, v1.1.0, v2.0.0, etc.
- The `-golden` suffix is unique to this baseline release
