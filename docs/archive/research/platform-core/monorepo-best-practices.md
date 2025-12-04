# Django/React Monorepo Best Practices

## Overview

This document explores industry best practices for organizing Django/React monorepo projects, evaluating different architectural approaches, tooling strategies, and deployment patterns. The research focuses on standards applicable to the ProjectMeats platform.

**Research Date:** 2024  
**Scope:** Django backend + React frontend monorepo organization

---

## Table of Contents

1. [Monorepo vs Multi-Repo Architecture](#monorepo-vs-multi-repo-architecture)
2. [Directory Structure Patterns](#directory-structure-patterns)
3. [Dependency Management](#dependency-management)
4. [Build Tooling](#build-tooling)
5. [Code Sharing Strategies](#code-sharing-strategies)
6. [Testing Approaches](#testing-approaches)
7. [Deployment Patterns](#deployment-patterns)
8. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
9. [Recommendations for ProjectMeats](#recommendations-for-projectmeats)
10. [References](#references)

---

## Monorepo vs Multi-Repo Architecture

### Monorepo Approach

**Description:** Single repository containing both Django backend and React frontend code.

**Pros:**
- ✅ Atomic commits across frontend and backend
- ✅ Simplified dependency management for shared code
- ✅ Easier code review for full-stack features
- ✅ Single source of truth for version control
- ✅ Shared tooling and CI/CD configuration
- ✅ Better code discoverability
- ✅ Simplified local development setup

**Cons:**
- ❌ Larger repository size and clone times
- ❌ Potential for tighter coupling between services
- ❌ More complex CI/CD pipelines (need to detect changes)
- ❌ Build times can grow without proper tooling
- ❌ Different teams may have conflicting workflows
- ❌ Git history can become noisy

### Multi-Repo Approach

**Description:** Separate repositories for Django backend and React frontend.

**Pros:**
- ✅ Clear separation of concerns
- ✅ Independent versioning and releases
- ✅ Team autonomy (separate CI/CD, permissions)
- ✅ Smaller, faster repositories
- ✅ Technology-specific tooling per repo

**Cons:**
- ❌ Difficult to coordinate cross-stack changes
- ❌ Dependency management complexity (shared types, APIs)
- ❌ Multiple PRs required for feature work
- ❌ Harder to enforce consistency
- ❌ API contract drift risk
- ❌ More complex local development setup

---

## Directory Structure Patterns

### Pattern 1: Top-Level Separation (Current ProjectMeats)

```
ProjectMeats/
├── backend/                    # Django application
│   ├── apps/                  # Django apps
│   ├── projectmeats/          # Settings
│   └── requirements.txt
├── frontend/                   # React application
│   ├── src/
│   └── package.json
├── docs/                       # Shared documentation
├── config/                     # Shared configuration
└── Makefile                   # Unified commands
```

**Pros:**
- ✅ Clear separation between frontend/backend
- ✅ Technology-specific tooling stays isolated
- ✅ Easy to understand for new developers
- ✅ Standard pattern in industry

**Cons:**
- ❌ Shared code requires careful organization
- ❌ Can lead to duplication (types, constants)

### Pattern 2: Workspace-Based Organization

```
project/
├── packages/
│   ├── backend/               # Django app
│   ├── frontend/              # React app
│   ├── shared/                # Shared utilities
│   └── types/                 # Shared TypeScript types
├── tools/                      # Build tools
└── package.json               # Workspace root
```

**Pros:**
- ✅ Better for multiple frontend apps
- ✅ Explicit shared code location
- ✅ Works well with tools like Nx, Turborepo

**Cons:**
- ❌ More complex for simple Django/React setup
- ❌ Requires workspace tooling (yarn/pnpm workspaces)
- ❌ Less intuitive for Django developers

### Pattern 3: Services-Based Organization

```
project/
├── services/
│   ├── api/                   # Django
│   └── web/                   # React
├── libs/                       # Shared libraries
├── infrastructure/            # Deployment configs
└── docs/
```

**Pros:**
- ✅ Scalable for microservices
- ✅ Clear service boundaries

**Cons:**
- ❌ Overkill for Django/React setup
- ❌ Adds unnecessary complexity

**Recommendation:** Pattern 1 (Top-Level Separation) is optimal for Django/React monorepos.

---

## Dependency Management

### Python Dependencies (Backend)

**Approach 1: Single requirements.txt**

**Pros:**
- ✅ Simple and standard
- ✅ Works with all deployment platforms

**Cons:**
- ❌ No separation of dev/prod dependencies
- ❌ Manual dependency resolution

**Approach 2: Poetry/Pipenv**

**Pros:**
- ✅ Automatic dependency resolution
- ✅ Lock files for reproducibility
- ✅ Dev/prod dependency separation
- ✅ Virtual environment management

**Cons:**
- ❌ Additional tooling complexity
- ❌ Some platforms don't support natively

**Approach 3: requirements.txt + requirements-dev.txt**

```
backend/
├── requirements.txt           # Production
└── requirements-dev.txt       # Development
```

**Pros:**
- ✅ Simple separation
- ✅ Widely supported
- ✅ Clear dependency purposes

**Cons:**
- ❌ Manual dependency management
- ❌ No automatic lock files

**Recommendation:** Use requirements.txt + requirements-dev.txt for simplicity, or Poetry for better dependency management.

### JavaScript Dependencies (Frontend)

**Approach 1: npm with package-lock.json**

**Pros:**
- ✅ Default Node.js package manager
- ✅ Universal compatibility
- ✅ Lock file for consistency

**Cons:**
- ❌ Slower than alternatives
- ❌ Less efficient disk usage

**Approach 2: yarn with yarn.lock**

**Pros:**
- ✅ Faster than npm
- ✅ Better workspace support
- ✅ Deterministic installs

**Cons:**
- ❌ Another tool to maintain
- ❌ Yarn v1 vs v2+ differences

**Approach 3: pnpm**

**Pros:**
- ✅ Fastest installation
- ✅ Efficient disk usage (symlinks)
- ✅ Strict dependency resolution

**Cons:**
- ❌ Less widespread adoption
- ❌ Some compatibility issues

**Recommendation:** Use npm for simplicity or yarn for workspace support and speed.

---

## Build Tooling

### Frontend Build Tools

**Option 1: Create React App (CRA)**

**Pros:**
- ✅ Zero configuration
- ✅ Official React tooling
- ✅ Good for getting started

**Cons:**
- ❌ Limited customization
- ❌ Slower builds
- ❌ Maintenance concerns (project is less active)

**Option 2: Vite**

**Pros:**
- ✅ Extremely fast dev server (native ESM)
- ✅ Fast production builds (Rollup)
- ✅ Modern, actively maintained
- ✅ TypeScript support out-of-the-box

**Cons:**
- ❌ Relatively newer (less battle-tested)
- ❌ May require plugin configuration

**Option 3: Webpack (Custom)**

**Pros:**
- ✅ Maximum flexibility
- ✅ Large ecosystem
- ✅ Battle-tested

**Cons:**
- ❌ Complex configuration
- ❌ Slower than modern alternatives
- ❌ Steeper learning curve

**Recommendation:** Vite for new projects, or stick with CRA if already established.

### Backend Build Requirements

Django doesn't require a build step, but consider:

**Static Asset Management:**
- `collectstatic` for production
- WhiteNoise for serving static files
- CDN integration for production

**Migration Management:**
- Automated migration checks in CI/CD
- Squashing migrations periodically
- Migration reversibility testing

---

## Code Sharing Strategies

### Sharing TypeScript Types Between Backend and Frontend

**Approach 1: OpenAPI/Swagger Generation**

**Pros:**
- ✅ Auto-generated from Django models
- ✅ Always in sync with backend
- ✅ Works with drf-spectacular

**Cons:**
- ❌ Requires build step
- ❌ Generated code can be verbose

**Implementation:**
```bash
# Generate TypeScript types from OpenAPI schema
npm install openapi-typescript-codegen
openapi --input openapi.json --output ./src/generated
```

**Approach 2: Manual Type Definitions**

**Pros:**
- ✅ Full control over types
- ✅ Can be more concise

**Cons:**
- ❌ Manual synchronization required
- ❌ Risk of drift from backend

**Approach 3: Shared Package**

**Pros:**
- ✅ Single source of truth
- ✅ Reusable across projects

**Cons:**
- ❌ Adds complexity for simple projects
- ❌ Requires package publishing workflow

**Recommendation:** Use OpenAPI/Swagger generation with drf-spectacular for type safety.

### Sharing Constants and Enums

**Best Practice:**
```
backend/apps/core/constants.py    → Python constants
frontend/src/constants/            → TypeScript constants (synced)
```

**Options:**
1. Manual synchronization with documentation
2. Code generation from backend to frontend
3. API endpoint that returns constants (runtime)

**Recommendation:** Manual sync with API endpoint fallback for dynamic values.

### Sharing Utilities

**Backend:** Keep in `backend/apps/core/utils.py`  
**Frontend:** Keep in `frontend/src/utils/`  
**Shared:** Only for truly shared logic (consider API endpoint instead)

---

## Testing Approaches

### Backend Testing (Django)

**Unit Tests:**
```python
# apps/customers/tests/test_models.py
class CustomerModelTests(TestCase):
    def test_customer_creation(self):
        customer = Customer.objects.create(name="Test")
        self.assertEqual(customer.name, "Test")
```

**API Tests:**
```python
# apps/customers/tests/test_api.py
class CustomerAPITests(APITestCase):
    def test_list_customers(self):
        response = self.client.get('/api/customers/')
        self.assertEqual(response.status_code, 200)
```

**Coverage Goals:**
- Overall: 80%+
- Critical paths: 95%+ (auth, payments)
- New features: 100%

**Tools:**
- `pytest` or Django's built-in unittest
- `coverage.py` for coverage reports
- `factory_boy` for test data

### Frontend Testing (React)

**Unit Tests:**
```typescript
// components/CustomerList.test.tsx
describe('CustomerList', () => {
  it('renders customer names', () => {
    render(<CustomerList customers={mockData} />);
    expect(screen.getByText('Test Customer')).toBeInTheDocument();
  });
});
```

**Integration Tests:**
```typescript
// Integration with API
it('fetches and displays customers', async () => {
  render(<CustomerList />);
  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

**E2E Tests:**
- Playwright or Cypress
- Critical user flows
- Run in CI before deployment

**Tools:**
- Jest + React Testing Library
- Playwright/Cypress for E2E
- MSW (Mock Service Worker) for API mocking

### Monorepo Testing Strategy

**Pros of Unified Testing:**
- ✅ Single test command (`make test`)
- ✅ Consistent reporting
- ✅ Easier CI/CD integration

**Cons:**
- ❌ Longer test runs
- ❌ Need for change detection

**Best Practice:**
```makefile
test: test-backend test-frontend

test-backend:
    cd backend && python manage.py test

test-frontend:
    cd frontend && npm test

test-changed:
    # Run only tests for changed files
    # Requires tooling like Nx or custom scripts
```

**Recommendation:** Run all tests in CI, use change detection for local dev.

---

## Deployment Patterns

### Pattern 1: Monolithic Deployment

**Description:** Deploy backend and frontend as single unit.

**Pros:**
- ✅ Simpler deployment process
- ✅ Atomic deployments
- ✅ Django serves React static files

**Cons:**
- ❌ Coupled release cycles
- ❌ Less flexibility
- ❌ Requires backend rebuild for frontend changes

**Implementation:**
```bash
# Build frontend
cd frontend && npm run build

# Copy to Django static
cp -r build/* ../backend/static/

# Deploy Django (serves both)
cd backend && python manage.py collectstatic --noinput
```

### Pattern 2: Separate Services with Shared Deployment

**Description:** Backend and frontend deploy independently but coordinated.

**Pros:**
- ✅ Independent scaling
- ✅ Can update frontend without backend restart
- ✅ Better CDN integration

**Cons:**
- ❌ More complex infrastructure
- ❌ CORS configuration required
- ❌ Coordination for breaking changes

**Implementation:**
```yaml
# Backend: API server
- Django on server/container
- Exposes REST API

# Frontend: Static hosting
- React built to static files
- Served via CDN/Nginx/Vercel
```

### Pattern 3: Containerized Deployment

**Description:** Docker containers for each service.

**Pros:**
- ✅ Environment consistency
- ✅ Easy scaling
- ✅ Infrastructure as code

**Cons:**
- ❌ Additional complexity
- ❌ Larger build artifacts
- ❌ Requires orchestration (Docker Compose/K8s)

**Implementation:**
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
  
  frontend:
    build: ./frontend
    ports: ["3000:80"]
    depends_on: [backend]
```

**Recommendation:** Pattern 2 (Separate Services) for production, Pattern 3 (Containers) for complex deployments.

---

## Common Pitfalls and Solutions

### 1. **CORS Configuration Issues**

**Problem:** Frontend can't communicate with backend in development.

**Solution:**
```python
# backend/projectmeats/settings/development.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### 2. **API Contract Drift**

**Problem:** Frontend and backend models get out of sync.

**Solution:**
- Use OpenAPI schema generation
- Automated type generation
- API versioning strategy
- Contract testing

### 3. **Inconsistent Environment Configuration**

**Problem:** Different `.env` formats for Django and React.

**Solution:**
```
# Centralized config management
config/
├── environments/
│   ├── development.env       # Backend
│   └── frontend.env.template # Frontend
└── manage_env.py             # Setup script
```

### 4. **Build Artifact Management**

**Problem:** Frontend build artifacts committed to Git.

**Solution:**
```gitignore
# .gitignore
frontend/build/
frontend/dist/
backend/staticfiles/
backend/static/frontend/
```

### 5. **Slow CI/CD Pipelines**

**Problem:** Every commit triggers full frontend and backend builds.

**Solution:**
- Change detection (build only what changed)
- Caching (dependencies, build artifacts)
- Parallel job execution
- Incremental builds

**Example:**
```yaml
# .github/workflows/ci.yml
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      backend: ${{ steps.changes.outputs.backend }}
      frontend: ${{ steps.changes.outputs.frontend }}
    steps:
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            backend:
              - 'backend/**'
            frontend:
              - 'frontend/**'
```

### 6. **Dependency Conflicts**

**Problem:** Shared dependencies have version conflicts.

**Solution:**
- Lock files (package-lock.json, requirements.txt)
- Dependency update automation (Dependabot)
- Regular dependency audits
- Pinned versions in production

### 7. **Documentation Drift**

**Problem:** Docs don't reflect actual implementation.

**Solution:**
- Auto-generated API docs (drf-spectacular)
- Component documentation (Storybook)
- Docs in PR checklist
- Regular doc reviews

### 8. **Testing Overhead**

**Problem:** Test suite takes too long.

**Solution:**
- Parallel test execution
- Test prioritization (critical paths first)
- Change-based test selection
- Separate smoke/full test suites

---

## Recommendations for ProjectMeats

Based on the current structure and industry best practices:

### ✅ Keep Current Structure
- Top-level separation (`backend/`, `frontend/`) is optimal
- Shared `docs/` and `config/` are well-organized
- Makefile for unified commands is excellent

### ✅ Enhance These Areas

**1. Dependency Management:**
```bash
# Add requirements-dev.txt for backend
backend/
├── requirements.txt          # Production
└── requirements-dev.txt      # Dev tools (pytest, black, etc.)
```

**2. Type Safety:**
```bash
# Generate TypeScript types from Django models
npm install --save-dev openapi-typescript-codegen

# In CI/CD or pre-commit
python manage.py spectacular --file openapi.json
openapi --input openapi.json --output frontend/src/generated
```

**3. Testing Strategy:**
```makefile
# Makefile additions
test-unit-backend:
    cd backend && pytest apps/ -v --cov

test-unit-frontend:
    cd frontend && npm run test:unit

test-e2e:
    cd frontend && npm run test:e2e

test-changed:
    # Run only changed tests (implement with pytest-testmon)
```

**4. CI/CD Optimization:**
- Add change detection to avoid unnecessary builds
- Cache dependencies (pip, npm)
- Parallel job execution
- Separate smoke tests from full suite

**5. Documentation:**
- Keep API documentation auto-generated
- Add architecture decision records (ADRs)
- Document shared constants and types
- Maintain up-to-date deployment guides

### ✅ Best Practices Checklist

- [x] Clear directory separation (backend/frontend)
- [x] Shared documentation location
- [x] Unified development commands (Makefile)
- [x] Environment configuration management
- [ ] TypeScript type generation from OpenAPI
- [ ] Automated dependency updates (Dependabot)
- [ ] Change-based CI/CD optimization
- [ ] Comprehensive testing coverage (80%+)
- [ ] API versioning strategy
- [ ] Performance monitoring

---

## References

### Industry Standards
- [Google's Monorepo Practices](https://research.google/pubs/pub45424/)
- [Uber's Monorepo Structure](https://eng.uber.com/microservice-architecture/)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [12-Factor App Methodology](https://12factor.net/)

### Tools and Frameworks
- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [React Documentation](https://react.dev/learn)
- [drf-spectacular (OpenAPI)](https://drf-spectacular.readthedocs.io/)
- [Nx Monorepo Tools](https://nx.dev/)
- [Turborepo](https://turbo.build/)

### Testing
- [Django Testing Guide](https://docs.djangoproject.com/en/stable/topics/testing/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright](https://playwright.dev/)
- [pytest Documentation](https://docs.pytest.org/)

### CI/CD
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/learn-github-actions/best-practices)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Deployment Strategies](https://martinfowler.com/bliki/BlueGreenDeployment.html)

### Code Quality
- [Black (Python Formatter)](https://black.readthedocs.io/)
- [ESLint](https://eslint.org/)
- [Prettier](https://prettier.io/)
- [Pre-commit Hooks](https://pre-commit.com/)

---

## Conclusion

The Django/React monorepo pattern, when properly structured, provides an excellent balance of:
- **Developer Experience:** Unified development, atomic commits, simplified setup
- **Maintainability:** Shared tooling, consistent practices, better discoverability
- **Scalability:** Can evolve to multi-service architecture if needed

**Key Takeaways:**
1. Top-level separation (backend/frontend) is optimal for Django/React
2. Invest in type generation and API contract management
3. Optimize CI/CD with change detection and caching
4. Maintain high test coverage with efficient test strategies
5. Keep documentation close to code and auto-generated where possible

ProjectMeats' current structure aligns well with industry best practices. Focus on enhancing type safety, test coverage, and CI/CD efficiency to maximize the monorepo benefits.

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Maintained by:** ProjectMeats Team
