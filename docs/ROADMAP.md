# ProjectMeats Roadmap

**Last Updated**: November 2025

This document outlines the future development plans, suggested upgrades, and enhancement recommendations for ProjectMeats.

---

## 📋 Table of Contents

- [Current State](#-current-state)
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

## 🔧 CI/CD Pipeline Enhancements (December 2024 - Completed)

### Overview
Four-phase enhancement to improve deployment reliability, reproducibility, and developer experience.

### ✅ Phase 1: Decoupled Schema Migrations

**Status**: ✅ Completed (PR #844)

**Implemented**:
- Dedicated `migrate` job in all deployment workflows (dev, UAT, prod)
- Idempotent migration sequence:
  ```bash
  python backend/manage.py migrate_schemas --shared --fake-initial
  python backend/manage.py create_super_tenant --no-input
  python backend/manage.py migrate_schemas --tenant
  ```
- Environment-scoped secrets (DEV_DB_URL, UAT_DB_URL, PROD_DB_URL)
- Explicit permissions blocks for security
- Pip dependency caching to reduce job time
- Appropriate timeout-minutes per environment

**Benefits**:
- ✅ Better failure isolation
- ✅ Cleaner pipeline stages
- ✅ Consistent migration handling
- ✅ No migration logic in deploy jobs

**Files Changed**:
- `.github/workflows/11-dev-deployment.yml`
- `.github/workflows/12-uat-deployment.yml`
- `.github/workflows/13-prod-deployment.yml`

---

### ✅ Phase 2: Immutable Image Tagging

**Status**: ✅ Completed (PR #845)

**Implemented**:
- Deploy jobs use SHA-tagged images only: `{env}-${{ github.sha }}`
- Removed all `-latest` tag usage from deploy steps
- Build jobs still push both SHA and `-latest` tags (caching)
- Added validation workflow (`validate-immutable-tags.yml`)

**Tag Strategy**:
| Stage | Tags | Purpose |
|-------|------|---------|
| Build | `dev-abc123f`, `dev-latest` | Immutable + caching |
| Deploy | `dev-abc123f` only | Production safety |

**Benefits**:
- ✅ Exact tested artifact deployed
- ✅ Reproducible deployments
- ✅ Easy rollback to specific SHA
- ✅ No accidental version mutation

**Files Changed**:
- `.github/workflows/11-dev-deployment.yml`
- `.github/workflows/12-uat-deployment.yml`
- `.github/workflows/13-prod-deployment.yml`
- `.github/workflows/validate-immutable-tags.yml` (new)

---

### ✅ Phase 3: Orchestrated Health Checks

**Status**: ✅ Completed (PR #846)

**Implemented**:
- Reusable health check script: `.github/scripts/health-check.sh`
- Composite action: `.github/actions/health-check/action.yml`
- Comprehensive documentation: `docs/ORCHESTRATED_HEALTH_CHECKS.md`

**Health Check Script Features**:
- Configurable retry attempts and delays
- Detailed error diagnostics (HTTP codes, network failures)
- Timeout handling
- Clean exit codes

**Composite Action Inputs**:
| Input | Default | Description |
|-------|---------|-------------|
| `health-url` | (required) | Health endpoint URL |
| `max-attempts` | 20 | Maximum retry attempts |
| `delay-seconds` | 5 | Delay between retries |
| `initial-wait` | 10 | Wait before first check |

**Usage Example**:
```yaml
- name: Health check backend
  uses: ./.github/actions/health-check
  with:
    health-url: 'http://localhost:8000/api/v1/health/'
    max-attempts: '20'
    delay-seconds: '5'
```

**Benefits**:
- ✅ Standardized health checks
- ✅ Centralized retry logic
- ✅ Easy to maintain
- ✅ SSH-compatible

**Files Changed**:
- `.github/scripts/health-check.sh` (new)
- `.github/actions/health-check/action.yml` (new)
- `docs/ORCHESTRATED_HEALTH_CHECKS.md` (new)

---

### ✅ Phase 4: Developer Experience

**Status**: ✅ Completed (PR #847)

**Implemented**:

#### 1. Devcontainer Parity
- Enhanced `.devcontainer/devcontainer.json` with Docker-in-Docker
- Idempotent setup script: `.devcontainer/setup.sh`
- Runs full multi-tenant migration sequence on create
- Installs Python + Node dependencies
- Creates super tenant and guest tenant
- Ready for immediate development

**Setup Script Steps**:
1. Install Python dependencies
2. Install Node dependencies
3. Wait for PostgreSQL
4. Run multi-tenant migrations (idempotent)
5. Create super tenant
6. Create guest tenant

#### 2. Copilot Instructions
- Added comprehensive multi-tenancy section to `.github/copilot-instructions.md`
- Core rule: Always public and tenant schemas
- Tenant-aware query patterns with code examples
- Common pitfalls and correct patterns
- Migration best practices
- Debugging guide

**Key Guidance Added**:
- ✅ Tenant isolation in QuerySets
- ✅ perform_create() overrides
- ✅ migrate_schemas usage
- ✅ Health endpoint tenant middleware bypass
- ✅ Common debugging scenarios

#### 3. ROADMAP Documentation
- Added CI/CD Enhancements section (this section)
- Documents all 4 phases with status
- Includes pipeline diagram
- Lists benefits and files changed
- Provides future work items

**Benefits**:
- ✅ New developers onboard faster
- ✅ Consistent multi-tenant development
- ✅ AI agents understand architecture
- ✅ Prevents common mistakes

**Files Changed**:
- `.devcontainer/devcontainer.json`
- `.devcontainer/setup.sh` (new)
- `.github/copilot-instructions.md`
- `docs/ROADMAP.md` (this file)

---

### 📊 CI/CD Pipeline Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   Feature Branch                        │
│                        ↓                                 │
│              Push to Development                        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│               Deployment Pipeline                       │
│                                                          │
│  1. lint-yaml → Validate workflow syntax               │
│  2. build-and-push → Docker images (SHA + latest tags) │
│  3. test-frontend → Unit tests                         │
│  4. test-backend → Unit + integration tests            │
│  5. migrate → Idempotent schema migrations ⭐          │
│  6. deploy-frontend → Deploy with SHA tag ⭐           │
│  7. deploy-backend → Deploy with SHA tag ⭐            │
│  8. health-check → Orchestrated health probes ⭐       │
│  9. post-deployment → Smoke tests                      │
│                                                          │
│  ⭐ = Enhanced in 4-phase improvement                   │
└─────────────────────────────────────────────────────────┘
                         ↓
               Automated PR to UAT
                         ↓
               (Repeat pipeline)
                         ↓
               Automated PR to Main
                         ↓
            Production Deployment
```

---

### 🔮 Future CI/CD Enhancements

#### Short-term (Q1 2025)
- [ ] Integrate orchestrated health checks into deployment workflows
- [ ] Add Slack/Teams notifications on deployment failures
- [ ] Implement parallel test matrices (Django 4.2 + 5.0)
- [ ] Add migration failure monitoring/alerting

#### Medium-term (Q2 2025)
- [ ] BuildKit caching for faster Docker builds
- [ ] Artifact attestation with GitHub OIDC
- [ ] Deployment rollback automation
- [ ] Blue-green deployment strategy

#### Long-term (Q3-Q4 2025)
- [ ] Kubernetes/EKS migration for orchestration
- [ ] Prometheus metrics integration
- [ ] Distributed tracing (Jaeger/OpenTelemetry)
- [ ] Automated performance regression detection

---

### 📚 CI/CD Documentation References

- Orchestrated Health Checks: `docs/ORCHESTRATED_HEALTH_CHECKS.md`
- Multi-Tenancy Guide: `.github/copilot-instructions.md` (Multi-Tenancy section)
- Deployment Workflows: `.github/workflows/*deployment*.yml`
- Validation Workflows: `.github/workflows/validate-*.yml`
- Scripts: `.github/scripts/`
- Actions: `.github/actions/`

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
