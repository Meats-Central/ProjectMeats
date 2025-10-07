# Repository Best Practices - ProjectMeats

## Overview

This document outlines the best practices and conventions for the ProjectMeats repository to maintain code quality, consistency, and collaboration efficiency.

## Repository Structure

### Directory Organization

```
ProjectMeats/
├── .github/                    # GitHub-specific files
│   ├── workflows/             # CI/CD workflows
│   └── ISSUE_TEMPLATE/        # Issue templates
├── backend/                    # Django backend
│   ├── apps/                  # Business applications
│   ├── projectmeats/          # Project settings
│   ├── static/                # Static files
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React frontend
│   ├── src/                   # Source code
│   ├── public/                # Public assets
│   └── package.json           # Node dependencies
├── config/                     # Configuration management
│   └── manage_env.py          # Environment setup tool
├── docs/                       # Documentation
│   ├── workflows/             # CI/CD documentation
│   ├── legacy/                # Archived docs
│   └── *.md                   # Main documentation
├── deploy/                     # Deployment configurations
├── archived/                   # Archived Docker & Terraform files
├── mobile/                     # Mobile app (future)
├── .gitignore                 # Git ignore rules
├── Makefile                   # Development commands
├── README.md                  # Project overview
└── CONTRIBUTING.md            # Contribution guidelines
```

### File Naming Conventions

- **Python**: snake_case (e.g., `purchase_orders.py`)
- **TypeScript/JavaScript**: PascalCase for components (e.g., `Header.tsx`), camelCase for utilities (e.g., `apiService.ts`)
- **Documentation**: SCREAMING_SNAKE_CASE for root docs (e.g., `README.md`), kebab-case for detailed docs (e.g., `backend-architecture.md`)
- **Configuration**: lowercase with extensions (e.g., `docker-compose.yml`, `.env.example`)

## Version Control (Git)

### Branch Strategy

- **main**: Production-ready code
- **develop**: Development branch (if using GitFlow)
- **feature/**: Feature branches (`feature/add-customer-portal`)
- **fix/**: Bug fixes (`fix/login-validation`)
- **hotfix/**: Critical production fixes (`hotfix/security-patch`)
- **copilot/**: GitHub Copilot automated changes

### Commit Messages

Follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

**Examples:**
```
feat(customers): add customer export functionality

Add CSV and Excel export options for customer data.
Includes filtering and custom field selection.

Closes #123
```

```
fix(auth): resolve token expiration handling

- Fix token refresh logic
- Add better error messages
- Update tests

Fixes #456
```

### What to Commit

**DO commit:**
- Source code
- Configuration templates (`.env.example`)
- Documentation
- Tests
- Build configuration
- Infrastructure as code

**DO NOT commit:**
- Secrets and API keys
- Environment files (`.env`)
- Build artifacts (`build/`, `dist/`)
- Dependencies (`node_modules/`, `venv/`)
- IDE-specific files (`.vscode/settings.json`)
- Database files (`*.db`, `*.sqlite3`)
- Log files (`*.log`)
- Temporary files (`*.tmp`, `*.backup`)
- Personal configuration

### .gitignore Best Practices

The repository maintains a comprehensive `.gitignore`:

```gitignore
# Environment files
.env
.env.local
*.env.backup
.env.*.backup

# Build artifacts
build/
dist/
node_modules/

# Python
__pycache__/
*.pyc
*.pyo
venv/

# Database
*.db
*.sqlite3
db.sqlite3

# Temporary files
*.tmp
*.backup
*_backup.py
*_original*.py

# IDE
.vscode/settings.json.user
.idea/

# OS
.DS_Store
Thumbs.db
```

## Code Quality

### Python (Backend)

#### Style Guide
- Follow PEP 8
- Use Black for formatting
- Use isort for import sorting
- Use flake8 for linting

#### Code Formatting
```bash
# Format code
cd backend
black . --exclude=migrations
isort . --skip=migrations

# Lint code
flake8 . --exclude=migrations
```

#### Type Hints
Use type hints for function signatures:

```python
from typing import List, Optional
from apps.customers.models import Customer

def get_active_customers(limit: Optional[int] = None) -> List[Customer]:
    """Retrieve active customers with optional limit."""
    queryset = Customer.objects.filter(is_active=True)
    if limit:
        queryset = queryset[:limit]
    return list(queryset)
```

#### Docstrings
Use Google-style docstrings:

```python
def create_order(customer_id: int, items: List[dict]) -> PurchaseOrder:
    """Create a new purchase order.
    
    Args:
        customer_id: ID of the customer placing the order
        items: List of order items with product_id and quantity
        
    Returns:
        Created PurchaseOrder instance
        
    Raises:
        Customer.DoesNotExist: If customer not found
        ValidationError: If order data is invalid
    """
    pass
```

### TypeScript/React (Frontend)

#### Style Guide
- Use ESLint with React rules
- Use Prettier for formatting
- Follow React best practices

#### Code Formatting
```bash
# Format code
cd frontend
npm run format

# Lint code
npm run lint
npm run lint:fix

# Type check
npm run type-check
```

#### Component Structure
```typescript
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

interface HeaderProps {
  title: string;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ title, onLogout }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  
  return (
    <HeaderContainer>
      <Title>{title}</Title>
      {onLogout && (
        <LogoutButton onClick={onLogout}>Logout</LogoutButton>
      )}
    </HeaderContainer>
  );
};

const HeaderContainer = styled.header`
  display: flex;
  justify-content: space-between;
  padding: 1rem;
`;

const Title = styled.h1`
  font-size: 1.5rem;
`;

const LogoutButton = styled.button`
  padding: 0.5rem 1rem;
`;
```

### Code Comments

**When to Comment:**
- Complex business logic
- Non-obvious solutions
- TODOs and FIXMEs
- API integration details
- Security considerations

**When NOT to Comment:**
- Obvious code
- Self-explanatory variable names
- Standard patterns

**Good Comments:**
```python
# Calculate tax based on customer's state and product category
# See: https://docs.example.com/tax-calculation
tax_rate = self._get_tax_rate(customer.state, product.category)

# TODO: Replace with Redis caching after migration (Issue #456)
cache = local_memory_cache
```

**Bad Comments:**
```python
# Increment counter
counter += 1

# Get user
user = User.objects.get(id=user_id)
```

## Testing

### Test Coverage Goals
- Overall: 80%+
- Critical paths: 95%+ (auth, payments, orders)
- New features: 100% coverage required

### Test Organization

**Backend:**
```
apps/customers/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_serializers.py
│   └── test_api_endpoints.py
```

**Frontend:**
```
src/components/Header/
├── Header.tsx
├── Header.test.tsx
└── Header.stories.tsx
```

### Running Tests
```bash
# Backend
make test-backend
cd backend && python manage.py test

# Frontend
make test-frontend
cd frontend && npm test

# All
make test
```

## Documentation

### Documentation Requirements

**Every feature should have:**
1. Code comments for complex logic
2. API documentation (OpenAPI/Swagger)
3. README updates if needed
4. User-facing documentation if applicable

### Documentation Structure

- **Root README.md**: Project overview, quick start
- **CONTRIBUTING.md**: Contribution guidelines
- **docs/**: Detailed documentation
  - Architecture documents
  - Deployment guides
  - API documentation
  - Troubleshooting guides

### Documentation Style

- Write in clear, concise language
- Include code examples
- Use diagrams for complex concepts
- Keep documentation up-to-date with code changes
- Link to external resources when helpful

### API Documentation

All API endpoints must be documented:

```python
class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing customers.
    
    list: Return a list of all customers
    create: Create a new customer
    retrieve: Return a specific customer
    update: Update a customer
    partial_update: Partially update a customer
    destroy: Delete a customer
    """
    pass
```

## Dependencies

### Adding Dependencies

**Backend (Python):**
1. Add to `requirements.txt` with version
2. Document why it's needed
3. Check for security vulnerabilities
4. Consider size and maintenance status

```txt
# Email validation and normalization
email-validator==2.1.0
```

**Frontend (Node):**
1. Use `npm install --save` or `npm install --save-dev`
2. Document in package.json comments if needed
3. Check bundle size impact
4. Review license compatibility

### Dependency Updates

- Review security advisories regularly
- Test updates in development first
- Update dependencies incrementally
- Document breaking changes

```bash
# Check for outdated packages
cd backend && pip list --outdated
cd frontend && npm outdated

# Update with care
pip install --upgrade package-name
npm update package-name
```

## Security

### Environment Variables

**Never commit:**
- API keys
- Database passwords
- Secret keys
- Private keys/certificates

**Always:**
- Use `.env` files (gitignored)
- Provide `.env.example` templates
- Document required variables
- Use strong, unique secrets per environment

### Code Security

- Sanitize user input
- Use parameterized queries (ORM handles this)
- Validate and escape output
- Use HTTPS in production
- Enable CSRF protection
- Implement rate limiting
- Review dependencies for vulnerabilities

### Secret Management

**Development:**
- Local `.env` files
- Never commit to git

**Production:**
- Environment variables
- Secret management services (AWS Secrets Manager, etc.)
- Encrypted configuration

## Performance

### Backend Optimization

- Use database indexes
- Implement caching (Redis)
- Optimize queries (select_related, prefetch_related)
- Use pagination for large datasets
- Profile slow endpoints

### Frontend Optimization

- Code splitting
- Lazy loading
- Minimize bundle size
- Optimize images
- Use production builds

## Continuous Integration

### CI/CD Pipeline

All code must pass:
1. Linting checks
2. Type checking (TypeScript)
3. Unit tests
4. Integration tests
5. Build verification

### Pre-commit Checks

Recommended pre-commit hooks:
```bash
# .git/hooks/pre-commit
#!/bin/bash
cd backend && black --check . && flake8 .
cd frontend && npm run lint && npm run type-check
```

## Code Review

### Pull Request Guidelines

**Before submitting:**
- Ensure tests pass
- Update documentation
- Follow commit message conventions
- Keep changes focused and small
- Add relevant reviewers

**PR Description should include:**
- What changed and why
- Testing performed
- Breaking changes
- Related issues/tickets

**Code Review Checklist:**
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No sensitive data committed
- [ ] Performance considered
- [ ] Security implications reviewed

## Issue Tracking

### Issue Templates

Use provided templates for:
- Bug reports
- Feature requests
- Improvement suggestions

### Labels

Standard labels:
- `bug`: Bug fixes
- `feature`: New features
- `documentation`: Documentation updates
- `enhancement`: Improvements
- `priority:high/medium/low`: Priority levels
- `good-first-issue`: Good for newcomers
- `copilot-ready`: Can be handled by AI

## Development Workflow

### Standard Workflow

1. Create branch from `main`
2. Make changes
3. Write/update tests
4. Run tests locally
5. Commit with good messages
6. Push to remote
7. Create pull request
8. Address review comments
9. Merge after approval

### Local Development

```bash
# Setup
python config/manage_env.py setup development
make setup

# Development
make dev  # Starts both backend and frontend

# Testing
make test

# Code quality
make format
make lint
```

## Deployment

### Deployment Checklist

Before deploying:
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Database migrations reviewed
- [ ] Backup created
- [ ] Rollback plan ready

### Environment Strategy

- **Development**: Local development
- **Staging**: Pre-production testing
- **Production**: Live environment

Each environment has:
- Separate configuration
- Separate database
- Separate secrets
- Separate domain/subdomain

## Maintenance

### Regular Tasks

**Weekly:**
- Review open issues
- Update dependencies if needed
- Check CI/CD status

**Monthly:**
- Security audit
- Performance review
- Documentation review
- Cleanup old branches

**Quarterly:**
- Major dependency updates
- Architecture review
- Technical debt assessment

## Tools and IDE Setup

### Recommended VS Code Extensions

**Python:**
- Python
- Pylance
- Black Formatter
- isort

**JavaScript/TypeScript:**
- ESLint
- Prettier
- TypeScript and JavaScript Language Features

**General:**
- GitLens
- Docker
- EditorConfig

### EditorConfig

`.editorconfig` for consistent formatting:
```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4

[*.{js,jsx,ts,tsx,json}]
indent_style = space
indent_size = 2

[*.{yml,yaml}]
indent_style = space
indent_size = 2
```

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [PEP 8 - Python Style Guide](https://pep8.org/)
- [React Best Practices](https://react.dev/learn)
- [Git Best Practices](https://git-scm.com/book/en/v2)
- [12 Factor App](https://12factor.net/)

## Getting Help

- Check documentation first
- Search existing issues
- Ask in team discussions
- Create detailed issues with context
- Tag appropriate reviewers

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines.

---

**Last Updated:** 2024
**Maintained by:** ProjectMeats Team
