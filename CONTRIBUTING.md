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

```bash
# Backend setup
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend setup (separate terminal)
cd frontend
npm install
npm start
```

### 2. Making Changes

1. **Create Feature Branch**: `git checkout -b feature/your-feature-name`
2. **Use Copilot**: For implementation tasks, tag issues with `copilot-ready`
3. **Follow TDD**: Write tests first, then implement
4. **Code Review**: All PRs require human review
5. **Test Coverage**: Maintain >90% test coverage

### 3. Multi-Tenancy Considerations

When working on tenant-aware features:

- **Models**: Add `tenant_id` field to all tenant-specific models
- **Views**: Use tenant-aware querysets
- **APIs**: Ensure proper tenant isolation
- **Tests**: Test with multiple tenants
- **Migrations**: Consider impact on existing tenants

### 4. Code Style

- **Backend**: Follow PEP 8, use `black` and `flake8`
- **Frontend**: Use TypeScript, follow React best practices
- **Database**: Use descriptive migration names
- **APIs**: Follow RESTful conventions

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
python manage.py test

# Run with coverage
pytest --cov=.

# Test specific app
python manage.py test apps.customers
```

### Frontend Testing
```bash
# Run unit tests
npm test

# Run with coverage
npm run test:ci

# E2E tests (when implemented)
npm run test:e2e
```

### Multi-Tenant Testing
- Test with multiple tenants
- Verify data isolation
- Test tenant switching
- Validate permissions

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

- **API Documentation**: Auto-generated with DRF Spectacular
- **Code Documentation**: Docstrings for all public functions
- **Architecture Documentation**: Keep ADRs (Architecture Decision Records)
- **User Documentation**: Maintain user guides and tutorials
- **Documentation Hub**: See [docs/README.md](docs/README.md) for complete documentation navigation

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