# ProjectMeats Roadmap

**Last Updated**: December 2025

This document outlines the future development plans, suggested upgrades, and enhancement recommendations for ProjectMeats.

---

## 📋 Table of Contents

- [Current State](#-current-state)
- [CI/CD Improvements](#-cicd-improvements)
- [Planned Upgrades](#-planned-upgrades)
- [Enhancement Recommendations](#-enhancement-recommendations)
- [Monorepo Improvements](#-monorepo-improvements)
- [Technical Debt](#-technical-debt)
- [Timeline](#-timeline)

---

## 📊 Current State

### Technology Stack (As of December 2025)

| Component | Current Version | Status |
|-----------|-----------------|--------|
| Django | 4.2.7 | ✅ LTS (supported until April 2026) |
| Django REST Framework | 3.14.0 | ✅ Current |
| django-tenants | 3.5.0 | ✅ Current |
| React | 18.2.0 | ✅ Current |
| TypeScript | 4.9.5 | ⚠️ Update available |
| Node.js | 16+ | ⚠️ LTS ended, upgrade to 20+ |
| PostgreSQL | 12+ | ⚠️ Consider 15+ for features |
| Python | 3.9+ | ⚠️ Consider 3.11+ for performance |

---

## 🔄 CI/CD Improvements

This section documents recent and planned improvements to our CI/CD pipeline, deployment infrastructure, and developer experience.

### ✅ Completed Improvements

#### 1. Decoupled Migration Strategy

**Status**: ✅ Implemented

Django migrations are now **decoupled from CI/CD execution**. Instead of auto-generating migrations during deployment, developers must:

1. Run `python manage.py makemigrations` locally after model changes
2. Review the generated migration files for correctness
3. Commit migration files to version control
4. Push changes – CI/CD will only **apply** migrations, never generate them

**Benefits**:
- **Deterministic deployments**: Same migration files across all environments
- **Auditable schema changes**: All migrations are reviewed in PRs
- **Easier rollbacks**: Committed migrations can be reverted cleanly
- **No schema drift**: Prevents inconsistencies between dev/staging/production

**Developer Workflow**:
```bash
# 1. Make model changes
vim backend/apps/myapp/models.py

# 2. Generate migrations locally
cd backend && python manage.py makemigrations

# 3. Review migration file
cat apps/myapp/migrations/0XXX_auto_*.py

# 4. Test migration
python manage.py migrate

# 5. Commit and push
git add apps/myapp/migrations/
git commit -m "feat(myapp): add new field"
git push
```

**Related Documentation**:
- [Migration Best Practices](./MIGRATION_BEST_PRACTICES.md)
- [Deployment Guide - Migration Management](./DEPLOYMENT_GUIDE.md#migration-management)

---

#### 2. Immutable Image Tagging

**Status**: ✅ Implemented

All Docker images are now tagged with **immutable identifiers** based on the Git commit SHA:

```yaml
# Example: dev-abc1234 (first 7 chars of commit SHA)
tags:
  - $REGISTRY/$IMAGE:dev-${GITHUB_SHA::7}
  - $REGISTRY/$IMAGE:dev-latest
```

**Tag Strategy**:

| Environment | Immutable Tag | Mutable Tag |
|-------------|---------------|-------------|
| Development | `dev-{sha7}` | `dev-latest` |
| UAT/Staging | `uat-{sha7}` | `uat-latest` |
| Production | `prod-{sha7}` | `prod-latest` |

**Benefits**:
- **Full traceability**: Every deployment can be traced to exact source code
- **Easy rollback**: Deploy specific version by SHA tag
- **Audit compliance**: Immutable tags support regulatory requirements
- **Cache optimization**: Unique tags enable proper layer caching

**Rollback Example**:
```bash
# Rollback to specific version
docker pull $REGISTRY/$IMAGE:dev-abc1234
docker stop pm-backend
docker run -d --name pm-backend $REGISTRY/$IMAGE:dev-abc1234
```

---

#### 3. Orchestration-Based Deployments

**Status**: ✅ Implemented

Deployments are now fully orchestrated through GitHub Actions workflows with structured job dependencies:

**Deployment Pipeline**:
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  build-and-push │────▶│   test-backend  │────▶│  deploy-backend │
│   (Docker)      │     │   test-frontend │     │  deploy-frontend│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  health-checks  │
                                                │  smoke-tests    │
                                                └─────────────────┘
```

**Key Features**:
- **Matrix builds**: Parallel frontend/backend image builds
- **Test gates**: Deployments blocked until tests pass
- **Health verification**: Post-deployment smoke tests
- **Automated rollback**: Failed deployments trigger recovery
- **Concurrency control**: Prevents parallel deployments to same environment

**Workflow Files**:
- `11-dev-deployment.yml` - Development environment
- `12-uat-deployment.yml` - UAT/Staging environment
- `13-prod-deployment.yml` - Production environment
- `promote-dev-to-uat.yml` - Automated promotion PRs
- `promote-uat-to-main.yml` - Production promotion PRs

**Related Documentation**:
- [Deployment Hardening Guide](./DEPLOYMENT_HARDENING.md)
- [Deployment Stability Guide](./DEPLOYMENT_STABILITY_GUIDE.md)

---

#### 4. Devcontainer Parity

**Status**: ✅ Implemented

Development containers now use the same PostgreSQL version and configuration as production environments:

**Devcontainer Stack**:
```yaml
# .devcontainer/docker-compose.yml
services:
  app:
    build:
      dockerfile: .devcontainer/Dockerfile.dev
    depends_on:
      - db
    ports:
      - "8000:8000"
      - "3000:3000"

  db:
    image: postgres:15  # Same as production
    environment:
      POSTGRES_DB: projectmeats_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
```

**Parity Features**:
| Feature | Development | Production |
|---------|-------------|------------|
| Database | PostgreSQL 15 | PostgreSQL 15 |
| Schema isolation | django-tenants | django-tenants |
| Port mapping | 8000/3000/5432 | 8000/3000/5432 |
| Environment vars | `.env` + compose | GitHub Secrets |

**Benefits**:
- **No "works on my machine" issues**: Same database engine everywhere
- **Migration testing**: Developers test exact same migration behavior
- **Feature parity**: Multi-tenancy works identically in dev
- **Onboarding simplicity**: One command to start development

**Quick Start**:
```bash
# Open in VS Code with Dev Containers extension
code .

# Or use command line
devcontainer open .

# Manual Docker Compose
docker-compose -f .devcontainer/docker-compose.yml up
```

---

### 🔄 In Progress

#### Docker BuildKit Layer Caching

**Status**: 🔄 Planned for Phase 3

Implementing Docker BuildKit with layer caching to reduce build times by 50-70%:

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ env.ENVIRONMENT }}-${{ hashFiles('**/requirements.txt', '**/package-lock.json') }}
```

**Expected Impact**:
- Build time: 8min → 2min (75% reduction)
- Cache hit rate: 80-90% for typical workflows
- Annual savings: ~100 hours of CI/CD runtime

---

### 📋 Future Improvements

| Improvement | Priority | Complexity | Expected Savings |
|-------------|----------|------------|------------------|
| Parallel test execution | High | Medium | 5-10 min/deployment |
| Self-hosted runners | Low | High | 2-3 min/deployment |
| Registry consolidation (GHCR) | Medium | Low | Simpler auth |
| Dependency caching (npm/pip) | Medium | Low | 30s-1min/deployment |

---

## 🚀 Planned Upgrades

### Priority 1: Framework Updates

#### Django 5.x Upgrade

**Target**: Django 5.1 (when django-tenants support is stable)

**Benefits**:
- Simplified form rendering
- Database-generated defaults
- Async view improvements
- Field groups in admin

**Prerequisites**:
- Verify django-tenants 3.6+ compatibility
- Test all migrations
- Update deprecated APIs

**Migration Steps**:
1. Update `requirements.txt`: `Django==5.1`
2. Run `python manage.py check --deploy`
3. Fix deprecation warnings
4. Test all tenant operations
5. Update documentation

```python
# TODO: requirements.txt
# Django==4.2.7  # Current LTS
# Django==5.1    # Target upgrade (Q2 2026)
```

#### React 19 Upgrade

**Target**: React 19 (stable release)

**Benefits**:
- React Compiler (automatic memoization)
- Actions (form handling improvements)
- Document metadata support
- Asset loading improvements

**Prerequisites**:
- Verify all dependencies support React 19
- Update TypeScript to 5.x
- Review custom hooks for compatibility

**Migration Steps**:
1. Update `package.json`: `"react": "^19.0.0"`
2. Update React DOM: `"react-dom": "^19.0.0"`
3. Update TypeScript types
4. Test all components
5. Review and update deprecated patterns

```json
// TODO: package.json
// "react": "^18.2.0",      // Current
// "react": "^19.0.0",      // Target upgrade
```

### Priority 2: Language & Runtime Updates

#### TypeScript 5.x Upgrade

**Target**: TypeScript 5.3+

**Benefits**:
- Const type parameters
- All enums are union enums
- Improved module resolution
- Better performance

```json
// TODO: package.json
// "typescript": "^4.9.5",  // Current
// "typescript": "^5.3.0",  // Target upgrade
```

#### Python 3.11/3.12 Upgrade

**Target**: Python 3.11+ (significant performance improvements)

**Benefits**:
- 10-60% faster execution
- Better error messages
- Exception groups
- Task groups in asyncio

```python
# TODO: Update runtime requirements
# Python 3.9+ (current minimum)
# Python 3.11+ (recommended minimum)
```

#### Node.js 20 LTS Upgrade

**Target**: Node.js 20 LTS

**Benefits**:
- Native test runner
- Experimental permission model
- Performance improvements
- V8 engine updates

---

## 💡 Enhancement Recommendations

### Monorepo Management Tools

#### Option A: Nx (Recommended)

**Benefits**:
- Computation caching
- Affected commands (only rebuild what changed)
- Dependency graph visualization
- Plugin ecosystem

**Setup**:
```bash
npx nx init
```

**Configuration**:
```json
// nx.json
{
  "tasksRunnerOptions": {
    "default": {
      "runner": "nx/tasks-runners/default",
      "options": {
        "cacheableOperations": ["build", "test", "lint"]
      }
    }
  }
}
```

#### Option B: Turborepo

**Benefits**:
- Incremental builds
- Remote caching
- Parallel execution
- Minimal configuration

**Setup**:
```bash
npx turbo init
```

**Configuration**:
```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", "build/**"]
    },
    "test": {},
    "lint": {}
  }
}
```

### API Improvements

#### GraphQL Addition (Optional)

For complex querying needs, consider adding GraphQL alongside REST:

```python
# TODO: Consider graphene-django for GraphQL support
# pip install graphene-django
```

#### API Versioning Enhancement

```python
# TODO: Implement explicit API versioning
# /api/v1/ (current)
# /api/v2/ (future, with breaking changes)
```

### Testing Enhancements

#### End-to-End Testing

```bash
# TODO: Add Playwright for E2E testing
npm install -D @playwright/test
```

#### Visual Regression Testing

```bash
# TODO: Consider Chromatic for Storybook visual testing
npm install -D chromatic
```

---

## 🏗️ Monorepo Improvements

### Recommended Structure Evolution

```
ProjectMeats/
├── apps/
│   ├── backend/          # Django API (moved from /backend)
│   ├── frontend/         # React web (moved from /frontend)
│   └── mobile/           # React Native (moved from /mobile)
├── packages/
│   ├── shared/           # Shared TypeScript utilities
│   ├── ui/               # Shared UI components
│   └── config/           # Shared configurations
├── tools/
│   └── scripts/          # Build and deployment scripts
├── docs/                 # Documentation
├── nx.json               # Nx configuration
└── package.json          # Root package.json
```

### Shared Package Strategy

1. **@projectmeats/shared**: Common utilities, types
2. **@projectmeats/ui**: Reusable React components
3. **@projectmeats/config**: ESLint, TypeScript configs

### Build Optimization

- [ ] Implement incremental builds
- [ ] Add remote caching for CI
- [ ] Optimize Docker builds with layer caching
- [ ] Add build analytics

---

## 🔧 Technical Debt

### High Priority

| Item | Description | Effort |
|------|-------------|--------|
| Remove SQLite support | Standardize on PostgreSQL only | Low |
| Update deprecated APIs | Django/React deprecation warnings | Medium |
| Type coverage | Increase TypeScript strict mode coverage | Medium |
| Test coverage | Achieve 90%+ backend coverage | Medium |

### Medium Priority

| Item | Description | Effort |
|------|-------------|--------|
| Documentation consolidation | Further reduce duplicate docs | Low |
| Legacy script cleanup | Remove deprecated setup_env.py | Low |
| Dependency audit | Remove unused dependencies | Medium |
| Performance profiling | Identify and fix bottlenecks | High |

### Low Priority

| Item | Description | Effort |
|------|-------------|--------|
| Admin UI refresh | Update Django admin theme | Low |
| Logging standardization | Implement structured logging | Medium |
| Feature flags | Add feature flag system | Medium |

---

## 📅 Timeline

### Q1 2026

- [ ] TypeScript 5.x upgrade
- [ ] Node.js 20 LTS upgrade
- [ ] Python 3.11 minimum requirement
- [ ] Documentation cleanup completion

### Q2 2026

- [ ] Django 5.1 upgrade (pending django-tenants support)
- [ ] Evaluate monorepo tools (Nx vs Turborepo)
- [ ] E2E testing framework selection

### Q3 2026

- [ ] React 19 upgrade (after stable release)
- [ ] Implement selected monorepo tool
- [ ] Performance optimization sprint

### Q4 2026

- [ ] GraphQL evaluation/implementation
- [ ] Advanced caching strategies
- [ ] SOC 2 compliance preparation

---

## 📚 Resources

- [Django Release Roadmap](https://www.djangoproject.com/download/)
- [React Releases](https://react.dev/blog)
- [Nx Documentation](https://nx.dev/)
- [Turborepo Documentation](https://turbo.build/)
- [TypeScript Releases](https://www.typescriptlang.org/docs/handbook/release-notes/overview.html)

---

## 📝 Contributing to the Roadmap

Suggestions for the roadmap can be made by:

1. Opening a GitHub issue with the `enhancement` label
2. Discussing in team planning sessions
3. Submitting PRs with RFC documents in `docs/research/`

---

**Document Owner**: ProjectMeats Development Team  
**Review Frequency**: Quarterly
