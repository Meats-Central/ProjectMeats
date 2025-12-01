# ProjectMeats - AI Coding Agent Instructions

**Tech Stack**: Django 4.2.7 + DRF + PostgreSQL | React 18.2.0 + TypeScript + Ant Design | React Native | Multi-tenancy

---

## ⚠️ CRITICAL RULES (Read First)

**Branch Workflow**: Never push directly to `uat` or `main`. Always:
1. Create branch from `development` using pattern: `feature/<topic>`, `fix/<bug>`, `chore/<task>`
2. PR to `development` → Auto-PR to `UAT` → Auto-PR to `main`

**Multi-Tenancy**: All tenant-aware models must:
- Include `tenant = models.ForeignKey(Tenant, ...)` field
- Use `objects = TenantManager()` for queryset filtering
- Filter in ViewSets: `Supplier.objects.for_tenant(self.request.tenant)`

**Migrations**: Before any PR with model changes:
- Run `python manage.py makemigrations` and commit resulting files
- CharField with `blank=True` MUST have `default=''` (PostgreSQL requirement)
- Never modify applied migrations—create new ones

---

## Architecture Overview

```
backend/                          # Django 4.2.7 + DRF
├── apps/                        # Business domain apps
│   ├── tenants/                 # Multi-tenancy (Tenant, TenantUser, TenantDomain)
│   ├── suppliers/               # Supplier management (example tenant-aware app)
│   ├── customers/, contacts/, purchase_orders/, plants/, ...
│   └── core/                    # Base models (TimestampModel, TenantManager, TextChoices)
├── projectmeats/settings/       # Environment-specific settings (base, development, staging, production)
└── requirements.txt

frontend/                         # React 18.2.0 + TypeScript
├── src/
│   ├── config/tenantContext.ts  # Tenant detection from domain (acme.projectmeats.com → tenant='acme')
│   ├── services/apiService.ts   # API client with tenant-aware config
│   ├── components/, pages/, contexts/
│   └── types/                   # TypeScript interfaces for API responses
└── package.json

shared/                           # Cross-platform utilities (frontend + mobile)
```

---

## Essential Commands

```bash
# Development
./start_dev.sh                    # Start PostgreSQL + Backend + Frontend
make dev                          # Alternative: runs both servers
make test                         # Run all tests (backend + frontend)
make format && make lint          # Format (Black, isort) and lint (flake8)

# Database
cd backend && python manage.py makemigrations  # Create migrations (ALWAYS commit these)
cd backend && python manage.py migrate         # Apply migrations

# Pre-commit (REQUIRED after clone)
pre-commit install                # Validates migrations on every commit
```

---

## Key Patterns

### Backend Model Pattern (see `backend/apps/suppliers/models.py`)
```python
from apps.core.models import TimestampModel, TenantManager
from apps.tenants.models import Tenant

class Supplier(TimestampModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="suppliers", null=True, blank=True)
    name = models.CharField(max_length=255)
    # CharField with blank=True MUST have default=''
    street_address = models.CharField(max_length=255, blank=True, default='')
    
    objects = TenantManager()  # Provides .for_tenant(tenant) method
```

### Backend ViewSet Pattern (see `backend/apps/suppliers/views.py`)
```python
class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Supplier.objects.for_tenant(self.request.tenant)
        return Supplier.objects.none()  # Security: no tenant = no data
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)  # Auto-assign tenant
```

### Frontend API Service Pattern (see `frontend/src/services/apiService.ts`)
```typescript
// Tenant context automatically detected from domain
import { config } from '../config/runtime';
const apiClient = axios.create({ baseURL: config.API_BASE_URL });
```

---

## CI/CD Workflows (`.github/workflows/`)

- `11-dev-deployment.yml`: Deploys on push to `development`
- `12-uat-deployment.yml`: Deploys on push to `uat`
- `13-prod-deployment.yml`: Deploys on push to `main`
- `41-auto-promote-dev-to-uat.yml`: Creates PR after successful dev deployment
- `42-auto-promote-uat-to-main.yml`: Creates PR after successful UAT deployment

---

## Common Pitfalls (from copilot-log.md)

1. **Missing migration files**: Always run `makemigrations` and commit the files
2. **CharField without default**: `blank=True` requires `default=''` for PostgreSQL
3. **Missing tenant filtering**: All tenant-aware queries must use `.for_tenant()`
4. **CSRF/CORS mismatch**: Keep `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` synchronized

---

## Reference Documentation

- [Migration Guide](../docs/MIGRATION_GUIDE.md) - Comprehensive migration patterns
- [Authentication Guide](../docs/AUTHENTICATION_GUIDE.md) - Auth, permissions, superuser management
- [Troubleshooting](../docs/TROUBLESHOOTING.md) - Common issues and solutions
- [Branch Workflow](../branch-workflow-checklist.md) - Detailed git workflow

---

## Detailed Standards (Expanded Reference)

The following sections provide comprehensive standards for development, testing, security, and maintenance.

## 🚩 Branch Organization, Naming, Tagging, and Promotion

- **Branch Structure:**  
  Use three main branches following GitFlow-inspired workflow:
  - `development` (all features/fixes/experiments start + merge here)
  - `UAT` (staging; only code tested/reviewed in dev gets promoted here)
  - `main` (production; only code signed off in UAT is promoted here)

  See [Branch Workflow Checklist](../branch-workflow-checklist.md) for diagrams and step-by-step workflow.

- **Branch Naming Conventions:**  
  ```
  feature/<concise-topic>          # New features
  fix/<bug-topic>                  # Bugfixes
  chore/<infra-maintenance>        # Tooling, infra or CI
  refactor/<module>                # Refactoring
  hotfix/<emergency-topic>         # Emergency quick fixes
  docs/<documentation-topic>       # Documentation updates
  test/<test-topic>                # Test improvements
  perf/<performance-topic>         # Performance optimizations
  ```
  - Use lowercase/hyphens; prefix by type for scanning.
  - **CRITICAL**: Never work or merge directly in `main` or `UAT`.
  - **CRITICAL**: Never push changes directly to `uat` or `main` branches.
  - Keep branches focused and short-lived (< 2 weeks active).

- **Deployment Protection Rules (MUST FOLLOW):**
  1. **Always start with feature/fix branch** from `development`
  2. **Merge to `development` first** via Pull Request with review
  3. **Automated PR to `UAT`** triggers after merge to development (via `promote-dev-to-uat.yml`)
  4. **Review and test in UAT** environment before approval
  5. **Automated PR to `main`** triggers after merge to UAT (via `promote-uat-to-main.yml`)
  6. **Final review and deploy to production** only after UAT sign-off
  
  **Workflow Enforcement**:
  - ✅ feature/fix branch → development (via PR)
  - ✅ development → UAT (automated PR after success)
  - ✅ UAT → main (automated PR after success)
  - ❌ NEVER: Direct push to UAT
  - ❌ NEVER: Direct push to main
  - ❌ NEVER: Skip development branch
  - ❌ NEVER: Bypass automated promotion workflows

- **Tagging & Releases:**  
  - Tag major/minor releases in `main` using semantic versioning: `vX.Y.Z`
  - Pre-release tags: `vX.Y.Z-alpha.N`, `vX.Y.Z-beta.N`, `vX.Y.Z-rc.N`
  - Environment tags: `vX.Y.Z-dev`, `vX.Y.Z-uat`
  - Use annotated tags for official releases: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
  - Follow [Semantic Versioning 2.0.0](https://semver.org/): MAJOR.MINOR.PATCH
  - Remove obsolete tags/branches as part of monthly repo maintenance.

- **Branch Protection:**  
  - Enable branch protection in GitHub settings: require status checks, reviews, restrict force-pushes/deletes on `main`, `UAT`, `development`.
  - Require at least 1 approval for PRs to `development`, 2 for `UAT` and `main`.
  - Enforce linear history (no merge commits) on protected branches.
  - Require CI/CD checks to pass before merge.

---

## 💡 Auto-PR Creation for Environment Promotion (via GitHub Actions)

Auto-promotion between environments is implemented in `.github/workflows/` with workflows like below:

> **Note**: All environment promotion PRs are managed **exclusively** by the superior workflows (`promote-dev-to-uat.yml` and `promote-uat-to-main.yml`). These workflows automatically close any existing stale PRs before creating a new one to ensure only the latest changes are promoted. No other workflow files should be used for this purpose.

**Example**: Promote changes from `development` → `UAT` automatically after merge:

```yaml name=.github/workflows/promote-dev-to-uat.yml
name: Promote Dev to UAT

on:
  push:
    branches:
      - development
  workflow_dispatch:

jobs:
  create-uat-pr:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Create Pull Request to UAT
        uses: peter-evans/create-pull-request@v5
        with:
          source-branch: development
          destination-branch: uat
          title: 'Promote development to UAT'
          body: |
            Auto-created PR to promote tested changes from development to UAT environment.
          labels: uat-promotion, automation
          reviewers: Vacilator
```

Repeat similarly for `UAT` → `main`.

**Key Features of Superior Promotion Workflows:**
- **Automatic Stale PR Management**: Before creating a new PR, the workflow checks for and closes any existing open PRs between the same branches, preventing duplicate or conflicting PRs
- **Fresh Promotion**: Each workflow run creates a PR with the latest commits from the source branch
- **Manual Trigger Support**: Workflows can be triggered manually via `workflow_dispatch` in addition to automatic triggers on branch pushes
- **Reviewer Assignment**: Automatically assigns reviewers (e.g., `Vacilator`) for accountability

**Workflow Requirements:**
- Ensure only fast-forward, conflict-free merges
- PR is auto-created, not auto-merged (review/approval required, CI must pass)
- Template body should clearly state promotion reason/scope
- Configure branch protection to prevent unintended merges

---

## 📄 Documentation, File Placement, Standards & Logging

- **Documentation Structure:**  
  - Main guides: `/docs/` directory and root `README.md`
  - API documentation: with module code (`backend/apps/<app>/docs/`, `frontend/docs/`)
  - Architecture decisions: `/docs/architecture/` using ADR (Architecture Decision Records) format
  - Workflow/process: `/docs/workflows/` (branch flow, environments, CI/CD)
  - Archived/deprecated: `/archived/docs/` with migration notes
  - Use visual aids: diagrams (`mermaid`/PlantUML), flowcharts, sequence diagrams
  - Include code examples, usage patterns, and common pitfalls

- **Documentation Quality Standards:**
  - Every public API endpoint must have OpenAPI/Swagger documentation
  - Complex business logic requires inline comments explaining "why", not "what"
  - README files in each major directory explaining purpose and structure
  - Update docs in the same PR as code changes (not separately)
  - Use consistent markdown formatting (linting with markdownlint)
  - Include table of contents for docs > 200 lines
  - Add "Last Updated" dates to documentation

- **Copilot Logging:**  
  - After each PR/task, add to `copilot-log.md`:
    ```markdown
    ## Task: [Brief task] - [Date: YYYY-MM-DD]
    - **Issue**: #[issue-number]
    - **Actions Taken**: [Bullet list of changes]
    - **Files Modified**: [Key files changed]
    - **Misses/Failures**: [What didn't work, errors encountered]
    - **Lessons Learned**: [Insights for future tasks]
    - **Time Spent**: [Approximate duration]
    ```
  - Include security considerations and performance impacts
  - Document any tech debt created or resolved

- **API Documentation Standards:**
  - Use drf-spectacular for auto-generated OpenAPI schemas
  - Document all query parameters, request/response bodies, error codes
  - Include example requests/responses for complex endpoints
  - Document rate limits, authentication requirements, pagination
  - Keep API version in URL path (`/api/v1/`)
  
- **Code Comments Best Practices:**
  - Use docstrings for all public functions/classes (Google/NumPy style for Python, JSDoc for TypeScript)
  - Comment complex algorithms, business rules, and non-obvious decisions
  - Avoid obvious comments that restate the code
  - Keep comments up-to-date with code changes (outdated comments are worse than no comments)
  - Use TODO/FIXME/NOTE tags with issue references

---

## 🔒 Code Quality & Security Standards

### Security Best Practices (OWASP Top 10 Compliance)

- **Authentication & Authorization:**
  - Never store passwords in plain text; use Django's built-in password hashing
  - Implement proper session management; set secure cookie flags (HttpOnly, Secure, SameSite)
  - Use CSRF protection on all state-changing operations
  - Implement rate limiting on authentication endpoints (use django-ratelimit)
  - Enforce strong password policies (min 12 chars, complexity requirements)
  - Use multi-factor authentication (MFA) for admin accounts

- **Data Protection:**
  - Encrypt sensitive data at rest (use Django's encrypted fields or database-level encryption)
  - Use HTTPS/TLS for all data in transit (enforce in production via middleware)
  - Implement proper tenant isolation in multi-tenant architecture (django-tenants)
  - Sanitize all user inputs to prevent XSS, SQL injection, command injection
  - Use parameterized queries exclusively (ORM handles this, never use raw SQL with string interpolation)
  - Implement Content Security Policy (CSP) headers

- **Secrets Management:**
  - Never commit secrets to version control (use `.env` files, exclude in `.gitignore`)
  - Use django-environ or python-decouple for environment variables
  - Rotate secrets regularly (API keys, database passwords, JWT secrets)
  - Use GitHub Secrets for CI/CD credentials
  - Scan for exposed secrets using git-secrets or truffleHog
  - Use different secrets for each environment (dev/UAT/prod)

- **Dependency Security:**
  - Run `pip-audit` (Python) and `npm audit` (Node) regularly
  - Enable Dependabot for automated vulnerability alerts
  - Pin exact versions in requirements.txt and package-lock.json
  - Review security advisories before updating major dependencies
  - Remove unused dependencies monthly

- **Code Security Practices:**
  - Validate and sanitize all external inputs (API requests, file uploads, user input)
  - Use Django's built-in protections (CSRF, XSS, clickjacking, SQL injection)
  - Implement proper error handling without exposing sensitive information
  - Use security headers (X-Frame-Options, X-Content-Type-Options, HSTS)
  - Log security events (failed login attempts, permission denials)
  - Implement API rate limiting to prevent abuse

### Code Quality Standards

- **Linting & Formatting:**
  - **Python**: Black (formatting), isort (imports), flake8 (linting)
  - **TypeScript**: ESLint + Prettier
  - **Pre-commit hooks**: Enforce formatting before commit (see `.pre-commit-config.yaml`)
  - Max line length: 100 characters (Python), 120 (TypeScript)
  - Run `make format` before committing, `make lint` to check

- **Code Review Standards:**
  - All code must be reviewed by at least one other developer
  - Review checklist: correctness, security, performance, readability, tests
  - No PR should exceed 400 lines of changes (split into smaller PRs)
  - Address all review comments before merging
  - Use conventional commits for clear history

- **Static Analysis:**
  - Run type checking: `mypy` for Python (future), `tsc --noEmit` for TypeScript
  - Use Pylint/Bandit for Python security scanning
  - Use SonarQube or CodeClimate for code quality metrics
  - Maintain code quality scores above 'B' grade

- **Error Handling & Logging:**
  - Use structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Never log sensitive data (passwords, tokens, PII)
  - Implement centralized error tracking (Sentry or similar)
  - Return appropriate HTTP status codes with descriptive error messages
  - Include correlation IDs for request tracing
  - Use Django's logging configuration with rotating file handlers

---

## ✅ Testing Strategy & Coverage

### Testing Philosophy
- **Test Pyramid**: 70% unit tests, 20% integration tests, 10% E2E tests
- **Coverage Target**: Minimum 80% overall, 90%+ for critical business logic
- **TDD Approach**: Write tests before or alongside code when possible
- **Fast Feedback**: Unit tests should run in < 1 minute

### Backend Testing (Django + DRF)

- **Test Organization:**
  ```
  backend/apps/<app>/tests/
  ├── __init__.py
  ├── test_models.py          # Model validation, business logic
  ├── test_views.py           # View layer logic
  ├── test_serializers.py     # Serialization, validation
  ├── test_api_endpoints.py   # API integration tests
  └── factories.py            # Factory Boy fixtures (future)
  ```

- **Test Types & Tools:**
  - **Unit Tests**: Django TestCase, pytest-django
  - **API Tests**: DRF's APIClient for endpoint testing
  - **Database Tests**: Use TestCase (transactions) for DB isolation
  - **Coverage**: Run `pytest --cov=apps --cov-report=html`
  - **Fixtures**: Use Factory Boy for test data generation (reduces boilerplate)

- **Testing Best Practices:**
  - Test one thing per test method (single responsibility)
  - Use descriptive test names: `test_<method>_<scenario>_<expected_result>`
  - Mock external dependencies (APIs, file system, email)
  - Test edge cases, error conditions, and boundary values
  - Test tenant isolation in multi-tenant features
  - Avoid test interdependencies (each test should be independent)

### Frontend Testing (React + TypeScript)

- **Test Organization:**
  ```
  frontend/src/components/
  ├── Button/
  │   ├── Button.tsx
  │   ├── Button.test.tsx      # Component tests
  │   └── Button.stories.tsx    # Storybook stories
  ```

- **Test Types & Tools:**
  - **Unit Tests**: React Testing Library + Jest
  - **Component Tests**: Test user interactions, not implementation details
  - **Integration Tests**: Test component integration with APIs
  - **E2E Tests**: Cypress or Playwright (future)
  - **Visual Regression**: Storybook + Chromatic (future)

- **Testing Standards:**
  - Test user-facing behavior, not internal state
  - Use accessible queries (getByRole, getByLabelText)
  - Mock API calls with MSW (Mock Service Worker)
  - Test accessibility (aria labels, keyboard navigation)
  - Maintain > 70% coverage for components

### Testing Checklist (Required for PRs)
- [ ] Unit tests for new functions/methods
- [ ] Integration tests for API endpoints
- [ ] Update existing tests for modified code
- [ ] All tests pass locally: `make test`
- [ ] Coverage doesn't decrease
- [ ] Test edge cases and error scenarios
- [ ] Mock external dependencies
- [ ] Tests are independent and repeatable

---

## 🎯 API Design & Backend Standards (Django + DRF)

### RESTful API Design Principles

- **URL Structure:**
  - Use nouns for resources: `/api/v1/customers/`, `/api/v1/orders/`
  - Use HTTP verbs for actions: GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
  - Nest related resources: `/api/v1/customers/{id}/orders/`
  - Version APIs in URL: `/api/v1/`, `/api/v2/`
  - Use plural nouns: `/customers/` not `/customer/`

- **HTTP Status Codes:**
  - 200 OK: Successful GET, PUT, PATCH
  - 201 Created: Successful POST with resource creation
  - 204 No Content: Successful DELETE
  - 400 Bad Request: Invalid input, validation errors
  - 401 Unauthorized: Missing or invalid authentication
  - 403 Forbidden: Authenticated but no permission
  - 404 Not Found: Resource doesn't exist
  - 409 Conflict: Duplicate resource or conflict
  - 500 Internal Server Error: Unexpected server error

- **Response Format:**
  ```json
  {
    "data": { ... },           // Actual response data
    "meta": {                   // Metadata
      "page": 1,
      "per_page": 20,
      "total": 100
    },
    "errors": [ ... ]           // Validation/error details
  }
  ```

- **Pagination:**
  - Use cursor-based pagination for large datasets
  - Default page size: 20-50 items
  - Include pagination metadata in response
  - Support `?page=N&page_size=M` query parameters

- **Filtering & Searching:**
  - Use query parameters: `?status=active&created_after=2024-01-01`
  - Support common filters: date ranges, status, search terms
  - Use django-filter for consistent filtering
  - Document all supported filters in API docs

### Django Best Practices

- **Models:**
  - Use explicit field names (avoid abbreviations)
  - Add `verbose_name` and `help_text` for admin interface
  - Implement `__str__` method for readable representations
  - Use `Meta.ordering` for consistent default ordering
  - Add database indexes on frequently queried fields
  - Use `unique=True` or `unique_together` for data integrity
  - Implement model validation in `clean()` method

- **QuerySet Optimization:**
  - Use `select_related()` for foreign keys (SQL JOIN)
  - Use `prefetch_related()` for reverse foreign keys and M2M
  - Use `only()` or `defer()` to limit fetched fields
  - Avoid N+1 queries (use Django Debug Toolbar to detect)
  - Use `annotate()` and `aggregate()` for complex queries
  - Cache expensive queries with Django's cache framework

- **Serializers:**
  - Use `ModelSerializer` for model-based serializers
  - Implement field-level validation: `validate_<field_name>()`
  - Implement object-level validation: `validate()`
  - Use nested serializers for related objects
  - Use `read_only_fields` for computed/auto-generated fields
  - Document all fields in docstrings

- **ViewSets & Permissions:**
  - Use `ModelViewSet` for standard CRUD operations
  - Implement custom actions with `@action` decorator
  - Use DRF permissions: IsAuthenticated, IsAdminUser, custom permissions
  - Implement tenant-based permissions for multi-tenancy
  - Override `get_queryset()` to filter by tenant
  - Use throttling for rate limiting

- **Migrations:**
  - Always run `makemigrations` before committing model changes
  - Review migration files before committing
  - Test migrations in development before UAT/production
  - Use `RunPython` for data migrations
  - Never edit applied migrations (create new ones)
  - Document complex migrations with comments
  - Test rollback procedures for critical migrations

---

## ⚛️ Frontend Standards (React + TypeScript)

### Component Architecture

- **Component Organization:**
  ```
  src/components/
  ├── common/              # Reusable UI components (Button, Input, Modal)
  ├── layout/              # Layout components (Header, Footer, Sidebar)
  ├── features/            # Feature-specific components
  └── screens/             # Page-level components
  ```

- **Component Best Practices:**
  - Use functional components with hooks (no class components)
  - Keep components small and focused (< 300 lines)
  - Extract reusable logic into custom hooks
  - Use TypeScript interfaces for props
  - Implement proper prop validation
  - Use React.memo() for expensive components
  - Avoid inline function definitions in render

- **State Management:**
  - Use React Context for global state (auth, theme)
  - Use local state (useState) for component-specific state
  - Consider Redux/Zustand for complex state (future)
  - Lift state to common ancestor when sharing between components
  - Use useReducer for complex state logic
  - Avoid prop drilling (use context or composition)

- **Hooks Best Practices:**
  - Follow Rules of Hooks (only call at top level, only in React functions)
  - Use `useEffect` for side effects (API calls, subscriptions)
  - Clean up effects with return function
  - Use `useMemo` for expensive computations
  - Use `useCallback` to memoize functions passed as props
  - Create custom hooks for reusable logic (prefix with `use`)

### TypeScript Best Practices

- **Type Safety:**
  - Avoid `any` type (use `unknown` if type is truly unknown)
  - Define interfaces for all props, state, API responses
  - Use union types for explicit state values
  - Use enums for fixed sets of values
  - Enable strict mode in tsconfig.json
  - Use type guards for runtime type checking

- **Type Organization:**
  ```
  src/types/
  ├── api.ts               # API request/response types
  ├── models.ts            # Domain model types
  └── components.ts        # Component prop types
  ```

### Styling Best Practices

- **Styled Components:**
  - Use styled-components for component-level styles
  - Create reusable styled components in `src/styles/`
  - Use theme for consistent colors, spacing, typography
  - Avoid inline styles (use styled components)
  - Use CSS variables for dynamic values
  - Support dark mode via theme switching

- **Performance Optimization:**
  - Use React.lazy() and Suspense for code splitting
  - Implement virtualization for long lists (react-window)
  - Optimize images (use WebP, lazy loading)
  - Minimize bundle size (analyze with webpack-bundle-analyzer)
  - Use production builds for deployment
  - Implement service workers for PWA (future)

- **Ant Design Usage:**
  - Use Ant Design components consistently
  - Customize theme via ConfigProvider
  - Follow Ant Design best practices and patterns
  - Don't mix UI libraries (stick to Ant Design)

---

## ⚡ Performance Optimization

### Backend Performance

- **Database Optimization:**
  - Add indexes on frequently queried fields (foreign keys, search fields)
  - Use database-level constraints for data integrity
  - Implement database connection pooling
  - Use read replicas for read-heavy workloads (future)
  - Monitor slow queries with Django Debug Toolbar
  - Optimize query performance with `EXPLAIN ANALYZE`

- **Caching Strategy:**
  - Cache expensive computations and queries
  - Use Redis for session storage and caching (production)
  - Implement API response caching (django-cache-memoize)
  - Use template fragment caching for repeated content
  - Set appropriate cache TTL values
  - Implement cache invalidation strategy

- **API Performance:**
  - Implement pagination for list endpoints (max 100 items per page)
  - Use field selection: `?fields=id,name` to reduce payload
  - Compress responses with gzip/brotli
  - Use ETags for cache validation
  - Implement rate limiting to prevent abuse
  - Monitor API response times (< 200ms target)

### Frontend Performance

- **Loading Performance:**
  - Code splitting by route (React.lazy + Suspense)
  - Lazy load images and heavy components
  - Minimize initial bundle size (< 200KB gzipped target)
  - Use tree shaking to eliminate dead code
  - Optimize font loading (font-display: swap)
  - Preload critical resources

- **Runtime Performance:**
  - Minimize re-renders with React.memo, useMemo, useCallback
  - Virtualize long lists (react-window for > 100 items)
  - Debounce search inputs and expensive operations
  - Use Web Workers for heavy computations
  - Optimize images (WebP, responsive images, lazy loading)
  - Profile with React DevTools Profiler

- **Network Optimization:**
  - Implement request deduplication
  - Use SWR or React Query for data fetching (future)
  - Batch API requests where possible
  - Implement optimistic updates for better UX
  - Use HTTP/2 for multiplexing
  - Minimize third-party scripts

### Performance Monitoring

- **Metrics to Track:**
  - API response time (p50, p95, p99)
  - Database query time
  - Frontend page load time (First Contentful Paint, Time to Interactive)
  - Bundle size over time
  - Error rates and exceptions
  - User-centric metrics (Core Web Vitals)

- **Tools:**
  - Backend: Django Debug Toolbar, New Relic, DataDog
  - Frontend: Lighthouse, WebPageTest, Chrome DevTools
  - Real User Monitoring (RUM) for production insights

---

## ♿ Accessibility & Internationalization

### Accessibility (WCAG 2.1 AA Compliance)

- **Semantic HTML:**
  - Use proper HTML elements (button, nav, main, header, footer)
  - Use heading hierarchy (h1, h2, h3) correctly
  - Use landmark roles (role="navigation", role="main")
  - Avoid div/span soup

- **Keyboard Navigation:**
  - All interactive elements must be keyboard accessible
  - Implement logical tab order (tabIndex)
  - Support common keyboard shortcuts (Esc to close modals)
  - Visible focus indicators on all interactive elements
  - No keyboard traps

- **Screen Reader Support:**
  - Add ARIA labels to all interactive elements
  - Use aria-describedby for help text
  - Use aria-live for dynamic content updates
  - Test with screen readers (NVDA, JAWS, VoiceOver)
  - Provide alt text for all images
  - Use aria-hidden for decorative elements

- **Visual Accessibility:**
  - Maintain color contrast ratio > 4.5:1 for normal text, > 3:1 for large text
  - Don't rely on color alone to convey information
  - Support text resizing up to 200%
  - Avoid flashing content (seizure risk)
  - Use relative units (rem, em) instead of px

- **Forms & Validation:**
  - Associate labels with inputs (for attribute)
  - Provide clear error messages
  - Use aria-invalid and aria-describedby for errors
  - Support autocomplete attributes
  - Group related inputs with fieldset/legend

### Internationalization (i18n)

- **Backend (Django):**
  - Use Django's translation framework (gettext)
  - Mark all user-facing strings for translation
  - Use locale middleware for language detection
  - Support multiple timezones
  - Format dates, numbers, currency by locale

- **Frontend (React):**
  - Use react-i18next or react-intl
  - Extract all user-facing strings
  - Support RTL languages (Arabic, Hebrew)
  - Implement language switcher
  - Load translations dynamically

- **Best Practices:**
  - Use ICU message format for pluralization
  - Avoid string concatenation (use placeholders)
  - Test all languages in UI
  - Provide fallback to English
  - Consider cultural differences in icons, colors

---

- **Regular Clean-Up:**  
  - Remove unused deps, dead code, deprecated configs/scripts
  - Archive inactive branches/tags (> 3 months old unless needed)
  - Format/lint all code before merge (Black for Python, Prettier for JS/TS)

- **Refactoring:**  
  - Modularize/reduce tech debt, maintain/test coverage
  - No breaking API/model changes without migration plan/docs/review
  - Remove feature flags once stable

- **Maintenance:**  
  - Audit permissions, branches, tags, dependencies monthly
  - Remove/Archive obsolete Terraform/HCL/infra unless strictly needed
  - Sync CI/CD pipeline configs to current branch/env structure

---

## ⚡ Requirements & Dependency Management

### Python/Django Backend

- **Dependency Files:**
  - `backend/requirements.txt`: All dependencies with pinned versions
  - `pyproject.toml`: Project metadata and optional dependencies
  - Use pip-tools for dependency management: `pip-compile requirements.in`

- **Dependency Best Practices:**
  - Pin exact versions for production: `Django==4.2.7` (not `Django>=4.2`)
  - Use version ranges for development only
  - Document why each dependency is needed
  - Run `pip-audit` monthly for security vulnerabilities
  - Review Dependabot alerts within 1 week
  - Test dependency updates in development first
  - Update dependencies quarterly (minor versions monthly)

- **Security Scanning:**
  - Run `pip-audit` before releases
  - Enable GitHub Dependabot alerts
  - Use Safety or Snyk for continuous monitoring
  - Review CVEs for critical dependencies
  - Have rollback plan for failed updates

### TypeScript/Node Frontend

- **Dependency Files:**
  - `frontend/package.json`: All dependencies
  - `frontend/package-lock.json`: Locked versions (never delete!)
  - Separate dependencies from devDependencies

- **Dependency Best Practices:**
  - Use exact versions in package.json for production deps
  - Use `^` for devDependencies to allow minor updates
  - Run `npm audit` or `yarn audit` monthly
  - Remove unused packages: `npm prune` or `npx depcheck`
  - Keep React and TypeScript up-to-date (quarterly)
  - Use `npm ci` in CI/CD (faster, uses lock file)

- **Bundle Size Management:**
  - Monitor bundle size with webpack-bundle-analyzer
  - Avoid large dependencies (moment.js → date-fns, lodash → individual imports)
  - Use tree shaking to eliminate dead code
  - Keep total bundle < 500KB gzipped
  - Alert on > 10% bundle size increase

### Mobile Dependencies (React Native)

- **Dependency Management:**
  - Keep React Native version synchronized with React
  - Test native modules thoroughly before upgrading
  - Use patch-package for critical third-party fixes
  - Document native dependency requirements
  - Test on both iOS and Android after updates

### Shared Dependencies

- Synchronize TypeScript versions across frontend/mobile
- Share utility packages via `/shared` directory
- Document breaking changes in shared utilities
- Version shared code semantically

### Dependency Update Strategy

1. **Monthly**: Check for security updates, apply critical patches
2. **Quarterly**: Update minor versions, test thoroughly
3. **Annually**: Review all dependencies, remove unused, update major versions
4. **Immediately**: Apply security patches for critical vulnerabilities

---

## 🔄 CI/CD & Deployment Best Practices

### Continuous Integration

- **Automated Checks (Run on every PR):**
  - Linting: Python (flake8), TypeScript (eslint)
  - Formatting: Black, Prettier
  - Type checking: mypy (future), tsc
  - Unit tests: Backend (pytest), Frontend (Jest)
  - Security scans: pip-audit, npm audit
  - Code coverage: pytest-cov (min 80%)
  - Build validation: Docker builds, frontend production build

- **PR Requirements:**
  - All CI checks must pass (no exceptions)
  - At least 1 code review approval
  - No merge conflicts
  - Branch naming validation
  - PR title follows conventional commits
  - Tests cover new code
  - Documentation updated

### Deployment Workflow

> **CRITICAL**: Environment promotion PRs (development → UAT → production) are managed **exclusively** by automated workflows (`.github/workflows/promote-dev-to-uat.yml` and `.github/workflows/promote-uat-to-main.yml`). These workflows automatically close stale PRs and create fresh ones with the latest commits. 

**Deployment Protection Rules:**
- ❌ **NEVER** push changes directly to `uat` or `main` branches
- ❌ **NEVER** create manual PRs for environment promotion
- ❌ **NEVER** bypass the automated promotion workflows
- ✅ **ALWAYS** start with feature/fix branch from `development`
- ✅ **ALWAYS** let automated workflows handle promotion PRs
- ✅ **ALWAYS** wait for UAT testing before promoting to production

**Correct Workflow:**
1. Create feature/fix branch: `git checkout -b feature/my-feature development`
2. Develop and test locally
3. Push branch: `git push origin feature/my-feature`
4. Create PR to `development` via GitHub UI
5. After review and merge, `promote-dev-to-uat.yml` automatically creates PR to `UAT`
6. Test in UAT environment, then merge PR
7. After UAT merge, `promote-uat-to-main.yml` automatically creates PR to `main`
8. Final review and merge to deploy to production

- **Environment Progression:**
  ```
  feature/fix branch → development → UAT → main (production)
  ```
  - Development: Auto-deploy on merge to `development`
  - UAT: Auto-deploy on merge to `UAT` (requires approval and testing)
  - Production: Auto-deploy on merge to `main` (requires 2 approvals)

- **Deployment Gates:**
  - All tests pass in source environment
  - Code review approved
  - Security scans clean
  - Performance benchmarks met
  - Database migrations tested
  - Rollback plan documented

- **Deployment Checklist:**
  - [ ] Database migrations tested in staging
  - [ ] Environment variables updated
  - [ ] Feature flags configured
  - [ ] Monitoring/alerting configured
  - [ ] Rollback procedure documented
  - [ ] Health checks passing
  - [ ] Performance metrics baseline
  - [ ] Security scan passed

### Infrastructure as Code

- **Archived Infrastructure:**
  - Terraform and Docker configs archived in `/archived`
  - Current deployment uses DigitalOcean App Platform
  - Infrastructure changes require review

- **Configuration Management:**
  - Use `config/manage_env.py` for environment setup
  - Store secrets in GitHub Secrets, not in code
  - Use `.env.example` files as templates
  - Document all required environment variables
  - Validate environment configuration before deployment

### Monitoring & Observability

- **Application Monitoring:**
  - Implement health check endpoints (`/health`, `/ready`)
  - Monitor API response times and error rates
  - Track database query performance
  - Monitor memory usage and CPU
  - Set up alerts for critical failures

- **Logging Best Practices:**
  - Use structured logging (JSON format in production)
  - Include correlation IDs for request tracing
  - Log levels: DEBUG (dev only), INFO, WARNING, ERROR, CRITICAL
  - Don't log sensitive data (PII, passwords, tokens)
  - Centralize logs (CloudWatch, Datadog, Splunk)
  - Set up log retention policies

- **Alerting:**
  - Error rate > 5% → Page on-call
  - Response time > 2s → Warning
  - Database connection failures → Critical alert
  - Security events → Immediate notification
  - Deploy failures → Team notification

### Rollback Procedures

- **Database Rollbacks:**
  - Test migration rollbacks before production
  - Use reversible migrations (avoid data loss)
  - Backup database before major migrations
  - Document rollback steps in migration

- **Application Rollbacks:**
  - Use container tags for easy rollback
  - Keep previous 3 versions deployed
  - Document rollback procedure in deployment docs
  - Test rollback in UAT environment
  - Monitor closely after rollback

---

## ⚙️ Coding Guidelines & Component Update Checklists

### General Development Principles

- Always update relevant files for component changes (models, admin, serializers, forms, templates, docs, tests)
- Test locally and in UAT before production
- Use descriptive commits referencing issues/PRs following Conventional Commits
- Keep PRs focused and small (< 400 lines of changes)
- Review your own PR before requesting review
- Address all review comments or explain why not

### Django/Backend Development

- **Migrations:**
  - Use Django model best practices (explicit field names, help_text, verbose_name)
  - **CRITICAL:** Never modify applied migrations (see [Migration Best Practices](../docs/MIGRATION_BEST_PRACTICES.md))
  - **CRITICAL RULE - TENANT_APPS:** For **any** change to a model in `TENANT_APPS` (see `backend/projectmeats/settings/base.py`):
    - Run `python manage.py makemigrations <app_name>` AND commit the migration file
    - Use `python manage.py migrate_schemas` for applying migrations, NOT `manage.py migrate`
    - For testing with `TENANT_CREATION_FAKES_MIGRATIONS` enabled, use `migrate_schemas --fake` if needed
    - TENANT_APPS include: accounts_receivables, suppliers, customers, contacts, purchase_orders, plants, carriers, bug_reports, ai_assistant, products, sales_orders, invoices
    - SHARED_APPS (use regular `migrate`): core, tenants, and Django core apps
  - Always run `python manage.py makemigrations --check` before committing
  - Test migrations on fresh database locally before PR
  - Use minimal dependencies (only depend on migrations you actually need)
  - CharField with `blank=True` MUST have `default=''` for PostgreSQL
  - Always commit migration files with model changes
  - Update admin.py/serializers/tests/docs for new fields
  - Add database indexes on frequently queried fields
  - Implement model validation in `clean()` method
  - Test migration rollback procedures (`migrate <app> <previous_migration>`)
  - Document complex migrations with docstrings explaining "why"

- **API Development:**
  - Follow RESTful conventions
  - Use ModelSerializer for consistency
  - Implement proper error handling and validation
  - Add comprehensive API documentation
  - Test all endpoints with APIClient
  - Implement tenant isolation for multi-tenant features

### Frontend/TypeScript Development

- **Component Development:**
  - Use functional components with hooks
  - Implement proper TypeScript types for all props
  - Keep components small and focused (< 300 lines)
  - Write tests alongside component development
  - Use Storybook for component documentation
  - Ensure accessibility (keyboard navigation, ARIA labels)

- **API Integration:**
  - Maintain API contract compatibility with backend
  - Document all API interactions in frontend docs
  - Implement proper error handling and loading states
  - Use TypeScript interfaces for API responses
  - Add integration tests for API calls

### Mobile Development (React Native)

- **Cross-Platform Considerations:**
  - Test on both iOS and Android
  - Use platform-specific code sparingly
  - Share logic with frontend via `/shared` utilities
  - Follow React Native best practices
  - Test on physical devices before release

### Continuous Improvement

- Use copilot-log.md for postmortems and to prevent repeated errors
- Log and solve recurring issues through workflow updates
- Conduct code reviews to share knowledge
- Refactor technical debt regularly
- Update this document with new learnings

---

## 🧹 Clean-Ups, Refactoring, & Repository Health

### Regular Clean-Up Schedule

- **Weekly:**
  - Review and close stale PRs (> 14 days inactive)
  - Check for broken CI/CD pipelines
  - Review security alerts from Dependabot

- **Monthly:**
  - Remove unused dependencies (run `npx depcheck`, `pip-audit`)
  - Archive merged branches (automated via workflow `51-cleanup-branches-tags.yml`)
  - Review and update documentation
  - Check for dead code with coverage tools
  - Audit database indexes and query performance
  - Review error logs for recurring issues

- **Quarterly:**
  - Update dependencies (minor/patch versions)
  - Review and refactor technical debt
  - Audit user permissions and access controls
  - Review and optimize database schema
  - Clean up feature flags (remove stable features)
  - Update third-party integrations

- **Annually:**
  - Major dependency updates (Python, Django, React, TypeScript)
  - Review and update security policies
  - Audit entire codebase for deprecated patterns
  - Review and optimize infrastructure costs
  - Update development tooling

### Refactoring Best Practices

- **When to Refactor:**
  - Code duplication (DRY principle violated)
  - Functions/components > 300 lines
  - Cyclomatic complexity > 10
  - Test coverage < 80% on critical paths
  - Performance bottlenecks identified
  - Deprecated patterns or libraries in use

- **Refactoring Guidelines:**
  - Refactor in small, incremental steps
  - Ensure tests pass before and after refactoring
  - Don't change behavior and refactor simultaneously
  - Update documentation alongside refactoring
  - Get code review for significant refactors
  - No breaking API/model changes without migration plan/docs/review
  - Use feature flags for gradual rollouts

- **Technical Debt Management:**
  - Document tech debt with TODO/FIXME comments and issue references
  - Track tech debt in GitHub issues with `tech-debt` label
  - Allocate 20% of sprint time to tech debt reduction
  - Prioritize security and performance-related debt
  - Remove feature flags once stable (< 30 days after release)

### Code Formatting & Linting

- **Automated Formatting:**
  - Run `make format` before committing
  - Black for Python (line length: 100)
  - Prettier for TypeScript/JavaScript (line length: 120)
  - Pre-commit hooks enforce formatting automatically
  - Configure IDE to format on save

- **Linting Standards:**
  - Run `make lint` to check code quality
  - Flake8 for Python (extend-ignore: E203, W503)
  - ESLint for TypeScript
  - Fix all linting errors before committing
  - Use `# noqa` sparingly and with justification

### Repository Maintenance

- **Branch Management:**
  - Delete merged branches immediately (or rely on automated cleanup)
  - Archive inactive feature branches (> 90 days old)
  - Protect main branches (main, UAT, development)
  - Never force-push to protected branches
  - Keep branch names descriptive and follow conventions

- **Tag Management:**
  - Keep only necessary tags (releases, important milestones)
  - Remove pre-release tags after final release (except last 10)
  - Use semantic versioning consistently
  - Annotate tags with release notes

- **Documentation Maintenance:**
  - Archive outdated documentation to `/archived/docs/`
  - Update README when architecture/setup changes
  - Keep API documentation synchronized with code
  - Review and update troubleshooting guides
  - Maintain changelog with all significant changes

- **Infrastructure Cleanup:**
  - Remove/Archive obsolete Terraform/Docker configs (archived in `/archived`)
  - Current deployment uses DigitalOcean App Platform
  - Sync CI/CD pipeline configs to current branch/env structure
  - Remove unused environment variables
  - Clean up test data in databases

### Repository Health Metrics

- **Code Quality Metrics:**
  - Test coverage > 80% overall, > 90% for critical paths
  - Code quality grade > 'B' (SonarQube/CodeClimate)
  - Zero critical security vulnerabilities
  - Linting errors: 0
  - Build success rate > 95%

- **Process Metrics:**
  - PR merge time < 2 days (target)
  - Open PR count < 10
  - Stale PR count: 0
  - CI/CD pipeline success rate > 95%
  - Deployment frequency: multiple per week

- **Maintenance Metrics:**
  - Open security alerts: 0 critical, < 5 total
  - Dependency freshness: < 3 months old
  - Documentation coverage: all public APIs documented
  - Tech debt issues: trending downward

---

## ⚡ Checklist Summaries

### Migration Verification Checklist

- [ ] Run `python manage.py makemigrations` locally
- [ ] Run `python manage.py migrate` locally
- [ ] Test model changes in Django admin interface
- [ ] Update admin.py for new fields (display, filters, search)
- [ ] Update serializers for API exposure
- [ ] Update forms for frontend compatibility
- [ ] Update templates if using Django templates
- [ ] Add/update unit tests for model changes
- [ ] Add/update API endpoint tests
- [ ] Test migration in development environment
- [ ] Document migration dependencies and prerequisites
- [ ] Test migration rollback procedure
- [ ] Update API documentation (OpenAPI schema)
- [ ] Check for N+1 query issues
- [ ] Add database indexes if needed
- [ ] Verify tenant isolation (multi-tenancy)

### Component Update Checklist

- [ ] **Models**: Field changes, types, constraints, indexes
- [ ] **Admin**: Register new fields, filters, search, display
- [ ] **Serializers**: Add fields, validation, nested serializers
- [ ] **Views/ViewSets**: Handle new fields, permissions, filtering
- [ ] **Forms**: Support in UI, validation
- [ ] **Templates**: Show new fields, formatting
- [ ] **Tests**: Unit tests, integration tests, edge cases
- [ ] **API Docs**: Update OpenAPI schema, examples
- [ ] **Frontend Types**: Update TypeScript interfaces
- [ ] **Frontend Components**: Display/edit new fields
- [ ] **Documentation**: Update user docs, API docs
- [ ] **Migrations**: Create and test migrations
- [ ] **Permissions**: Verify tenant isolation and permissions

### PR Review Checklist

- [ ] Code follows style guide and passes linting
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No security vulnerabilities introduced
- [ ] Performance impact considered
- [ ] Error handling implemented
- [ ] Logging added for important operations
- [ ] API contracts maintained (backward compatibility)
- [ ] Database migrations reviewed
- [ ] Environment variables documented
- [ ] Secrets not committed
- [ ] Code is readable and maintainable
- [ ] No TODO/FIXME without issue reference
- [ ] Accessibility considered (frontend)
- [ ] Mobile compatibility tested (if applicable)

### UAT and Production Verification

- **UAT Verification:**
  - [ ] Migrations run successfully
  - [ ] All automated tests pass
  - [ ] UI/UX tested manually
  - [ ] API endpoints tested with real data
  - [ ] Permissions and tenant isolation verified
  - [ ] Performance acceptable (< 2s response time)
  - [ ] No console errors or warnings
  - [ ] Mobile responsive (if applicable)
  - [ ] Accessibility checked (keyboard, screen reader)
  - [ ] Edge cases and error scenarios tested

- **Production Verification:**
  - [ ] All UAT checks passed
  - [ ] CI/CD approvals obtained (2 for production)
  - [ ] Monitoring and alerting configured
  - [ ] Health checks passing
  - [ ] Database backups verified
  - [ ] Rollback procedure documented and tested
  - [ ] API performance within SLA (< 200ms p95)
  - [ ] Error rates < 1%
  - [ ] No security alerts
  - [ ] Customer communication sent (if user-facing)

### Security Checklist

- [ ] Input validation on all user inputs
- [ ] Output encoding to prevent XSS
- [ ] CSRF protection enabled
- [ ] Authentication required on protected endpoints
- [ ] Authorization checks implemented
- [ ] Secrets not hardcoded or committed
- [ ] Dependencies scanned for vulnerabilities
- [ ] SQL injection prevented (use ORM)
- [ ] Rate limiting implemented on APIs
- [ ] HTTPS enforced in production
- [ ] Security headers configured (CSP, HSTS, etc.)
- [ ] Sensitive data encrypted at rest
- [ ] Logging doesn't expose sensitive data
- [ ] Error messages don't leak implementation details
- [ ] Tenant isolation verified (multi-tenancy)

---

## 🏷️ Common Pitfalls to Avoid

### Development Pitfalls

- **Missing Updates:**
  - Missing admin/serializer updates for model changes
  - Incomplete migrations or forgotten migration files
  - API documentation not updated with code changes
  - Frontend types not synchronized with backend
  - Tests not covering new code paths

- **Code Quality Issues:**
  - Committing with linting errors
  - Skipping code reviews or rubber-stamping
  - Large PRs that are hard to review (> 400 lines)
  - Not testing edge cases or error conditions
  - Hardcoding values instead of configuration

- **Security Mistakes:**
  - Committing secrets or API keys
  - Missing input validation or sanitization
  - Exposing sensitive data in logs or error messages
  - Not implementing rate limiting on APIs
  - Using outdated dependencies with known vulnerabilities

### Process Pitfalls

- **Workflow Violations:**
  - Direct merges to production branches (main, UAT)
  - Skipping CI/CD status checks
  - Force-pushing to protected branches
  - Not following branch naming conventions
  - Merging PRs without required approvals

- **Documentation Failures:**
  - Outdated documentation and stale guides
  - Missing architecture decision records
  - API inconsistencies across stack
  - Not documenting breaking changes
  - Missing migration rollback procedures

- **Deployment Issues:**
  - Deploying without testing migrations in staging
  - Not having rollback plan
  - Missing environment variable configuration
  - Deploying during peak hours without warning
  - Not monitoring post-deployment metrics

### Technical Debt Pitfalls

- **Accumulating Debt:**
  - Unused/deprecated dependencies not removed
  - Test or dead code not cleaned up
  - Feature flags left indefinitely
  - Stale branches and tags piling up
  - TODO/FIXME comments without tracking

- **Architecture Issues:**
  - N+1 database queries
  - Missing database indexes on queried fields
  - Large bundle sizes (> 500KB gzipped)
  - Synchronous operations blocking request handling
  - Not implementing caching for expensive operations

---

## 🔗 References & Resources

### Official Documentation
- [Django Documentation](https://docs.djangoproject.com/en/4.2/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [React Native Documentation](https://reactnative.dev/)

### Best Practices & Standards
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [12-Factor App](https://12factor.net/)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)

### Repository-Specific Documentation
- [Branch Workflow Checklist](../branch-workflow-checklist.md)
- [Repository Best Practices](../docs/REPOSITORY_BEST_PRACTICES.md)
- [Migration Best Practices](../docs/MIGRATION_BEST_PRACTICES.md) - **Essential reading for all backend work**
- [Deployment Troubleshooting](../docs/DEPLOYMENT_TROUBLESHOOTING.md) - **Required for deployment issues**
- [Testing Strategy](../docs/TESTING_STRATEGY.md)
- [Deployment Guide](../DEPLOYMENT_GUIDE.md)
- [Backend Architecture](../docs/BACKEND_ARCHITECTURE.md)
- [Frontend Architecture](../docs/FRONTEND_ARCHITECTURE.md)
- [Multi-Tenancy Guide](../docs/MULTI_TENANCY_GUIDE.md)

### Tools & Libraries
- [Django Tenants](https://django-tenants.readthedocs.io/) - Multi-tenancy
- [drf-spectacular](https://drf-spectacular.readthedocs.io/) - OpenAPI documentation
- [Ant Design](https://ant.design/) - React UI components
- [Styled Components](https://styled-components.com/) - CSS in JS
- [React Testing Library](https://testing-library.com/react) - Testing
- [Storybook](https://storybook.js.org/) - Component development

### Security Resources
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [Django Security Guide](https://docs.djangoproject.com/en/4.2/topics/security/)
- [npm Security Best Practices](https://docs.npmjs.com/packages-and-modules/securing-your-code)

### Questions & Support
- Open an issue for questions or improvements
- Start a repository discussion for architectural decisions
- Refer to `copilot-log.md` for historical context and lessons learned
- Review closed PRs for implementation examples

---

## 📊 Copilot Agent Efficiency & Lessons Learned

### Overview
This section consolidates key lessons from 50+ PR deployments (documented in [copilot-log.md](../copilot-log.md)) to improve Copilot agent efficiency and prevent recurring issues.

### Critical Migration Lessons (Most Common Issues)

**Issue Frequency:** 8+ tasks in copilot-log related to migration problems

1. **Never Modify Applied Migrations**
   - ❌ Changing dependencies after migration is applied
   - ✅ Create new migration to fix issues
   - See: [Migration Best Practices](../docs/MIGRATION_BEST_PRACTICES.md)

2. **Minimal Migration Dependencies**
   - ❌ Depending on unnecessary later migrations
   - ✅ Only depend on migrations that create models/fields you reference
   - Rule: ForeignKey only needs the migration that creates the target model

3. **PostgreSQL CharField Defaults**
   - ❌ `CharField(blank=True)` without `default=''`
   - ✅ `CharField(blank=True, default='')` always
   - Why: PostgreSQL distinguishes between empty string and NULL

4. **Test Migrations on Fresh Database**
   - Before every PR, test: `dropdb test_db && createdb test_db && python manage.py migrate`
   - Prevents: InconsistentMigrationHistory errors in production

### Deployment & Configuration Lessons

**Issue Frequency:** 5+ tasks related to deployment configuration

1. **CSRF_TRUSTED_ORIGINS Must Match CORS_ALLOWED_ORIGINS**
   - Common error: Admin 403 errors from cross-domain requests
   - Solution: Keep CSRF and CORS configurations synchronized
   - Both should include all frontend and backend domains

2. **Static Files Need Persistent Volume Mounts**
   - Issue: Admin CSS/JS 404 errors
   - Cause: `collectstatic` ran in temporary container without volume
   - Solution: Always mount staticfiles volume for both collectstatic and app container
   - Required permissions: `chown -R 1000:1000 /path/to/staticfiles`

3. **Database Backups Before Migrations**
   - Always backup before applying migrations
   - Automated in deployment workflows via `.github/scripts/backup-database.sh`
   - Keeps last 7 backups automatically

4. **Environment Variable Validation**
   - Use `.github/scripts/validate-environment.sh` to check required vars
   - Validates: SECRET_KEY, DATABASE_URL, CORS/CSRF config, security settings
   - Warns about misconfigurations before deployment

### Multi-Tenancy Lessons

**Issue Frequency:** 4+ tasks related to tenant isolation

1. **TenantFilteredAdmin for All Tenant Models**
   - All admin classes for models with `tenant` field must extend `TenantFilteredAdmin`
   - Ensures non-superuser staff only see their tenant's data
   - Pattern: `class MyAdmin(TenantFilteredAdmin)` instead of `admin.ModelAdmin`

2. **Tenant-Aware ViewSets**
   - Override `get_queryset()` to filter by tenant
   - Fall back to user's first tenant if needed
   - Pattern:
     ```python
     def get_queryset(self):
         user = self.request.user
         tenant = getattr(user, 'tenant', None) or user.tenantuser_set.first()?.tenant
         return super().get_queryset().filter(tenant=tenant)
     ```

3. **Automatic Tenant Assignment**
   - Use signals or override `perform_create()` to auto-assign tenant
   - Never require frontend to send tenant ID

### Testing & Validation Lessons

**Issue Frequency:** 6+ tasks improved by better testing

1. **Pre-commit Hooks Prevent Common Issues**
   - Syntax validation for migration files
   - Checking for unapplied migrations
   - Black/isort/flake8 formatting
   - Install: `pip install pre-commit && pre-commit install`

2. **Migration Validation in CI/CD**
   - All workflows now include `.github/scripts/validate-migrations.sh`
   - Validates: syntax, dependencies, conflicts, fresh database test
   - Prevents migration issues from reaching deployment

3. **Error Handling Patterns**
   - Always use try/except in ViewSets with proper error logging
   - Return descriptive error messages (not just 500)
   - Pattern:
     ```python
     try:
         # operation
     except Exception as e:
         logger.error(f"Error in {self.__class__.__name__}: {str(e)}")
         return Response({"error": str(e)}, status=500)
     ```

### Code Organization Lessons

**Issue Frequency:** 3+ tasks could be prevented by base classes

1. **Create Base Classes for Common Patterns**
   - Suggested: `TenantAwareViewSet` with built-in tenant filtering
   - Suggested: `BaseSerializer` with common validation patterns
   - Benefit: DRY principle, consistent behavior across codebase

2. **Custom Exception Handlers**
   - Create DRF custom exception handler for consistent error responses
   - Centralize error logging
   - Benefit: Better error tracking, consistent API responses

### Security Lessons

**Issue Frequency:** 3+ tasks related to security configuration

1. **Never Log Sensitive Data**
   - No passwords, tokens, PII in logs
   - Use `[REDACTED]` placeholders
   - Filter sensitive fields in error reports

2. **Production Security Checklist**
   - DEBUG = False
   - SESSION_COOKIE_SECURE = True
   - CSRF_COOKIE_SECURE = True
   - ALLOWED_HOSTS properly configured
   - Secrets in environment variables (never in code)

3. **Tenant Isolation in Queries**
   - Always filter by tenant at database level (not just UI)
   - Use `TenantFilteredAdmin` and tenant-aware querysets
   - Test with non-superuser accounts

### Performance Lessons

**Issue Frequency:** 2+ tasks related to performance

1. **Use select_related() and prefetch_related()**
   - Avoid N+1 queries in list views
   - Pattern: `queryset.select_related('tenant', 'user').prefetch_related('items')`
   - Use Django Debug Toolbar to detect N+1 queries

2. **Minimize Bundle Size**
   - Frontend bundles should be < 500KB gzipped
   - Use code splitting with `React.lazy()`
   - Avoid large dependencies (moment.js → date-fns)

### Automation Improvements Implemented

Based on recurring issues, we've added:

1. **Migration Validation Script** (`.github/scripts/validate-migrations.sh`)
   - Checks syntax, dependencies, conflicts
   - Tests on fresh database in CI
   - Prevents 90% of migration-related deployment failures

2. **Environment Validation Script** (`.github/scripts/validate-environment.sh`)
   - Validates required environment variables
   - Checks CORS/CSRF consistency
   - Warns about insecure configurations

3. **Database Backup Script** (`.github/scripts/backup-database.sh`)
   - Automatic backups before migrations
   - Keeps last 7 backups
   - Compresses to save space

4. **Enhanced Pre-commit Hooks** (`.pre-commit-config.yaml`)
   - Migration syntax validation
   - Unapplied migration detection
   - Python formatting and linting

5. **Migration Validation in CI/CD**
   - All deployment workflows include migration validation
   - Runs on every PR before deployment
   - Fails fast to prevent deployment issues

### Efficiency Metrics

**Before Improvements:**
- Migration-related deployment failures: ~30% of deployments
- Average time to diagnose issues: 2-3 hours
- Repeated issues: Same patterns in 5+ tasks

**After Improvements:**
- Migration-related deployment failures: Target < 5%
- Average time to diagnose: < 30 minutes (with troubleshooting guide)
- Repeated issues: Prevented by automation

### Quick Reference: Common Copilot Agent Tasks

**Before Creating PR:**
- [ ] Run `.github/scripts/validate-migrations.sh` (if backend changes)
- [ ] Run `.github/scripts/validate-environment.sh` (if config changes)
- [ ] Test migrations on fresh database
- [ ] Ensure pre-commit hooks pass
- [ ] Review [Migration Best Practices](../docs/MIGRATION_BEST_PRACTICES.md)
- [ ] Update copilot-log.md with lessons learned

**For Migration Changes:**
- [ ] **CRITICAL: Before creating a PR, always run `python manage.py makemigrations` locally. If new files are generated, they MUST be committed. The CI pipeline will now fail any PR that has unapplied migrations, detected via the new pre-commit hook.**
- [ ] Never modify applied migrations
- [ ] Use minimal dependencies
- [ ] Add `default=''` to CharField with `blank=True`
- [ ] Test rollback: `python manage.py migrate <app> <previous>`
- [ ] Document complex migrations with docstrings
- [ ] Verify migration plan: `python manage.py migrate --plan`

**For Deployment Issues:**
- [ ] If the deployment fails with "Unapplied migrations detected", the developer MUST run `git pull`, execute `python manage.py makemigrations`, commit the new file(s), and push to re-trigger the pipeline
- [ ] Check [Deployment Troubleshooting](../docs/DEPLOYMENT_TROUBLESHOOTING.md) first
- [ ] Review GitHub Actions logs
- [ ] SSH to server and check container logs
- [ ] Compare working vs broken environment variables
- [ ] Follow rollback procedure if needed

**For Admin Changes:**
- [ ] Extend `TenantFilteredAdmin` for tenant models
- [ ] Test with non-superuser account
- [ ] Verify superuser still sees all data
- [ ] Check CSRF_TRUSTED_ORIGINS includes admin domain

### Resources for Copilot Agents

- **copilot-log.md** - 4700+ lines of historical lessons, search for similar issues
- **MIGRATION_BEST_PRACTICES.md** - Comprehensive migration guide
- **DEPLOYMENT_TROUBLESHOOTING.md** - Step-by-step issue resolution
- **Validation scripts** in `.github/scripts/` - Use these to validate changes
- **Deployment workflows** in `.github/workflows/` - Reference for CI/CD patterns

---

**Last Updated**: 2025-12-01  
**Version**: 4.0 (Restructured with concise quick-reference section and comprehensive detailed standards)
