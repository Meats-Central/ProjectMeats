# Contributing to ProjectMeats

Welcome to ProjectMeats! This guide will help you contribute effectively to our multi-tenant SaaS platform using GitHub Copilot and following our development practices.

## GitHub Copilot Guidelines

### When to Use @copilot

Use `@copilot` for the following agent-led tasks:

- **Code Generation**: API implementations, boilerplate code, model definitions
- **Test Creation**: Unit tests, integration tests, E2E test scenarios
- **Documentation**: API documentation, code comments, README updates
- **Refactoring**: Code optimization, structure improvements
- **Migration Scripts**: Database migrations, data transformations

### Human Review Required

The following tasks require human review and strategic decision-making:

- **Architecture Decisions**: Multi-tenancy patterns, database design choices
- **Security Implementations**: Authentication, authorization, data isolation
- **CI/CD Configuration**: Deployment strategies, environment configurations
- **Business Logic**: Core domain logic, complex validation rules
- **Performance Optimization**: Database queries, caching strategies

## Task Delegation via Issues

### Issue Templates

When creating issues for Copilot to handle, use these templates:

#### API Implementation Template
```markdown
## API Implementation Request

**Endpoint**: `POST /api/v1/[resource]`
**Description**: [Brief description of what this endpoint should do]

**Requirements**:
- [ ] Django model if needed
- [ ] Serializer with validation
- [ ] ViewSet with CRUD operations
- [ ] URL configuration
- [ ] Basic unit tests
- [ ] API documentation

**Acceptance Criteria**:
- Follows existing API patterns
- Includes proper error handling
- Has tenant isolation (if applicable)
- Passes all tests

**Labels**: `enhancement`, `api`, `copilot-ready`
```

#### Bug Fix Template
```markdown
## Bug Fix Request

**Issue**: [Description of the bug]
**Steps to Reproduce**: 
1. [Step one]
2. [Step two]
3. [Expected vs actual behavior]

**Affected Files**: [List of files that might need changes]

**Requirements**:
- [ ] Root cause analysis
- [ ] Fix implementation
- [ ] Test to prevent regression
- [ ] Update documentation if needed

**Labels**: `bug`, `copilot-ready`
```

#### Feature Implementation Template
```markdown
## Feature Implementation

**Feature**: [Feature name]
**Description**: [Detailed description]

**Technical Requirements**:
- [ ] Frontend components (if applicable)
- [ ] Backend API endpoints (if applicable)
- [ ] Database changes (if applicable)
- [ ] Tests for all new code
- [ ] Documentation updates

**User Stories**:
- As a [user type], I want [goal] so that [benefit]

**Labels**: `enhancement`, `feature`, `copilot-ready`
```

## Development Workflow

### 1. Setup Development Environment

**Recommended Setup (using centralized config):**
```bash
# Use centralized environment manager
python config/manage_env.py setup development

# Install backend dependencies
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Install frontend dependencies (separate terminal)
cd frontend
npm install
npm start
```

**Alternative Setup (using Makefile):**
```bash
# Complete setup (backend + frontend)
make setup

# Run development servers
make dev

# Or run individually
make backend   # Backend only
make frontend  # Frontend only
```

**See [Environment Guide](docs/ENVIRONMENT_GUIDE.md) for detailed environment configuration.**

### 2. Making Changes

1. **Create Feature Branch**: `git checkout -b feature/your-feature-name`
2. **Use Copilot**: For implementation tasks, tag issues with `copilot-ready`
3. **Follow TDD**: Write tests first, then implement
4. **Code Review**: All PRs require human review
5. **Test Coverage**: Aim for 80%+ coverage (95%+ for critical paths)
6. **Documentation**: Update relevant docs with your changes
7. **Commit Messages**: Use [Conventional Commits](https://www.conventionalcommits.org/) format

**Example Commit Message:**
```
feat(customers): add customer export functionality

Add CSV and Excel export options for customer data.
Includes filtering and custom field selection.

Closes #123
```

**See [Repository Best Practices](docs/REPOSITORY_BEST_PRACTICES.md) for detailed workflow guidelines.**

### 3. Multi-Tenancy Considerations

When working on tenant-aware features:

- **Models**: Add `tenant_id` field to all tenant-specific models
- **Views**: Use tenant-aware querysets
- **APIs**: Ensure proper tenant isolation
- **Tests**: Test with multiple tenants
- **Migrations**: Consider impact on existing tenants

### 4. Code Style

**Backend (Python):**
- Follow PEP 8 style guide
- Use `black` for formatting: `cd backend && black . --exclude=migrations`
- Use `flake8` for linting: `flake8 . --exclude=migrations`
- Use `isort` for import sorting: `isort . --skip=migrations`
- Add type hints where appropriate
- Write Google-style docstrings

**Frontend (TypeScript/React):**
- Use TypeScript for type safety
- Follow React best practices and hooks patterns
- Use `eslint` for linting: `npm run lint`
- Use `prettier` for formatting: `npm run format`
- Write comprehensive prop types
- Follow component composition patterns

**Database:**
- Use descriptive migration names
- Add comments for complex migrations
- Test migrations with rollback scenarios

**APIs:**
- Follow RESTful conventions (see [Backend Architecture](docs/BACKEND_ARCHITECTURE.md))
- Use proper HTTP methods and status codes
- Implement pagination for list endpoints
- Add filtering and search capabilities
- Document all endpoints with OpenAPI/Swagger

**See [Repository Best Practices](docs/REPOSITORY_BEST_PRACTICES.md) for complete code quality guidelines.**

## Architecture Guidelines

### Current Stack
- **Backend**: Django + Django REST Framework
- **Frontend**: React + TypeScript
- **Database**: PostgreSQL (multi-tenant ready)
- **Deployment**: DigitalOcean Apps Platform
- **CI/CD**: GitHub Actions

### Multi-Tenancy Pattern
- **Shared Database, Shared Schema**: Using tenant_id for isolation
- **Tenant Model**: Central tenant management
- **Middleware**: Tenant detection and setting
- **API**: Tenant-aware endpoints

### Plugin Architecture
- **Django Apps**: Modular feature apps
- **Extension Points**: Django signals and hooks
- **Sandboxing**: Isolated plugin environments
- **APIs**: Well-defined extension interfaces

## Testing Strategy

### Backend Testing
```bash
# Run all tests
cd backend && python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report

# Test specific app
python manage.py test apps.customers

# Using Makefile
make test-backend
```

### Frontend Testing
```bash
# Run unit tests
cd frontend && npm test

# Run in CI mode (no watch)
npm run test:ci

# Using Makefile
make test-frontend
```

### Multi-Tenant Testing
- Test with multiple tenants
- Verify data isolation
- Test tenant switching
- Validate permissions

**See [Testing Strategy](docs/TESTING_STRATEGY.md) for comprehensive testing guidelines, examples, and best practices.**

## Deployment Process

### Staging Deployment
- Automatic deployment on PR merge to `develop`
- Runs full test suite
- Deployed to staging environment

### Production Deployment
- Manual trigger from `main` branch
- Requires approval from maintainers
- Blue-green deployment strategy
- Rollback capability

## Security Considerations

- **Tenant Isolation**: Strict data separation
- **Authentication**: Token-based auth with tenant context
- **Authorization**: Role-based access control
- **Rate Limiting**: Per-tenant rate limiting
- **Data Encryption**: Encrypt sensitive data at rest

## Performance Guidelines

- **Database**: Use indexes, avoid N+1 queries
- **API**: Implement pagination and filtering
- **Frontend**: Code splitting and lazy loading
- **Caching**: Use Redis for frequently accessed data

## Documentation

### Documentation Structure

ProjectMeats maintains comprehensive documentation in the `docs/` directory:

- **[Documentation Hub](docs/README.md)** - Central navigation for all documentation
- **[Backend Architecture](docs/BACKEND_ARCHITECTURE.md)** - Django backend structure and patterns
- **[Frontend Architecture](docs/FRONTEND_ARCHITECTURE.md)** - React frontend structure and components
- **[Testing Strategy](docs/TESTING_STRATEGY.md)** - Comprehensive testing guide
- **[Repository Best Practices](docs/REPOSITORY_BEST_PRACTICES.md)** - Development workflow and standards
- **[Environment Guide](docs/ENVIRONMENT_GUIDE.md)** - Environment configuration
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Deployment procedures

### Documentation Requirements

When contributing:
- **API Documentation**: Auto-generated with DRF Spectacular
- **Code Documentation**: Docstrings for all public functions (Google-style)
- **Architecture Documentation**: Keep ADRs (Architecture Decision Records)
- **User Documentation**: Maintain user guides and tutorials
- **Update Docs**: Always update relevant documentation with code changes

## Getting Help

- **Issues**: Create detailed issues using templates above
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the [Documentation Hub](docs/README.md) first
- **Code Review**: Tag appropriate reviewers

## Labels for Issues

- `copilot-ready`: Can be handled by GitHub Copilot
- `human-review`: Requires human decision-making
- `api`: API-related changes
- `frontend`: React/TypeScript changes
- `backend`: Django changes
- `database`: Database changes
- `deployment`: CI/CD and infrastructure
- `security`: Security-related issues
- `performance`: Performance optimization
- `documentation`: Documentation updates

Remember: GitHub Copilot is a powerful tool for implementation, but human judgment is essential for architectural decisions, security reviews, and strategic planning.