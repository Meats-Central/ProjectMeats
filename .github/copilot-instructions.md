# Copilot Instructions for ProjectMeats

This file provides GitHub Copilot with context about ProjectMeats - a multi-tenant SaaS platform for meat sales brokers, built with Django REST Framework (backend) and React TypeScript (frontend).

## Repository Structure

```
ProjectMeats/
├── backend/                    # Django REST Framework API
│   ├── apps/                  # Business domain apps (accounts_receivables, suppliers, customers, etc.)
│   │   └── [app_name]/
│   │       ├── models.py      # Django models
│   │       ├── views.py       # API viewsets
│   │       ├── serializers.py # DRF serializers
│   │       ├── admin.py       # Django admin
│   │       ├── urls.py        # URL routing
│   │       └── tests.py       # Unit tests
│   ├── manage.py
│   └── requirements.txt
├── frontend/                   # React TypeScript application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/            # Main application pages
│   │   ├── services/         # API communication
│   │   └── types/            # TypeScript type definitions
│   └── package.json
├── config/                    # Centralized environment configuration
├── docs/                      # Comprehensive documentation
├── .github/
│   ├── copilot-instructions.md  # This file
│   └── copilot-log.md          # Learning log for continuous improvement
└── Makefile                   # Development commands
```

## Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0, PostgreSQL
- **Frontend**: React 18.2.0, TypeScript, Styled Components
- **Testing**: pytest-django (backend), Jest/React Testing Library (frontend)
- **Code Quality**: black, flake8, isort (Python); eslint, prettier (TypeScript)
- **Multi-tenancy**: django-tenants with tenant_id isolation pattern
- **AI Features**: OpenAI GPT-4 integration for document processing

## General Development Guidelines

1. **Branch Strategy**: Always create a new feature branch from main, named descriptively (e.g., "feature/enhance-db-models" or "fix/api-validation-error").

2. **Task Review**: Review the entire task context carefully, including any referenced previous responses, PRs, or related issues.

3. **Minimize Changes**: Make the smallest possible changes to accomplish the goal. Don't refactor or "improve" unrelated code.

4. **Testing**: Always run existing tests before making changes, then add tests for new functionality. Never remove or modify tests unless specifically required by the task.

5. **Commit Messages**: Use conventional commit format: `type(scope): description` (e.g., "feat(customers): add export functionality")

6. **Review copilot-log.md**: Before starting any task, review `.github/copilot-log.md` for lessons learned from similar past tasks.

## Build, Test, and Quality Commands

### Backend (Django)
```bash
# Setup and run
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver  # Starts on http://localhost:8000

# Testing
python manage.py test                    # Run all tests
python manage.py test apps.customers     # Test specific app
pytest --cov=. --cov-report=html         # With coverage

# Code quality
black . --exclude=migrations             # Format code
isort . --skip=migrations                # Sort imports
flake8 . --exclude=migrations            # Lint code

# Database
python manage.py makemigrations          # Create migrations
python manage.py migrate                 # Apply migrations
python manage.py shell                   # Django shell

# Using Makefile
make backend         # Start backend server
make test-backend    # Run tests
make format          # Format code
make lint           # Lint code
make migrate        # Apply migrations
make migrations     # Create migrations
```

### Frontend (React/TypeScript)
```bash
# Setup and run
cd frontend
npm install
npm start           # Starts on http://localhost:3000

# Testing
npm test            # Interactive test mode
npm run test:ci     # CI mode (no watch, with coverage)

# Code quality
npm run lint        # Run ESLint
npm run lint:fix    # Fix ESLint issues
npm run format      # Format with Prettier
npm run type-check  # TypeScript type checking

# Build
npm run build                # Production build
npm run build:production     # Production build with NODE_ENV

# Using Makefile
make frontend         # Start frontend server
make test-frontend    # Run tests
```

### Full Stack
```bash
# Quick setup (recommended)
python setup_env.py           # Automated setup
# OR
python config/manage_env.py setup development

# Development
make dev              # Start both backend and frontend
make test             # Run all tests
make clean            # Clean build artifacts
```

## Django-Specific Patterns

### Database Models
When working with Django models:

1. **Add tenant awareness**: All business models must include tenant isolation
   ```python
   from apps.tenants.models import Tenant
   
   class Customer(models.Model):
       tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
       # ... other fields
   ```

2. **Field best practices**:
   - Use appropriate field types (CharField, TextField, IntegerField, etc.)
   - Set `null=True` for database NULL, `blank=True` for form validation
   - Add `help_text` for admin interface clarity
   - Use `choices` for predefined options
   - Add `db_index=True` for frequently queried fields

3. **Always update related components**:
   - **models.py**: Define the model with proper field types and constraints
   - **admin.py**: Register model and configure admin interface (list_display, search_fields, fieldsets)
   - **serializers.py**: Create/update serializer for API endpoints
   - **views.py**: Add/update viewsets if new endpoints needed
   - **urls.py**: Register new viewsets in URL routing
   - **tests.py**: Add comprehensive unit tests

4. **Migration workflow**:
   ```bash
   # Create migrations
   python manage.py makemigrations
   
   # Review generated migration before applying
   cat backend/apps/[app]/migrations/000X_*.py
   
   # Apply migrations
   python manage.py migrate
   
   # Test in Django admin
   python manage.py runserver
   # Visit http://localhost:8000/admin
   ```

### API Development (Django REST Framework)

Follow this pattern for new endpoints:

1. **Model** (if needed): Define in `models.py`
2. **Serializer**: Create in `serializers.py`
   ```python
   from rest_framework import serializers
   
   class CustomerSerializer(serializers.ModelSerializer):
       class Meta:
           model = Customer
           fields = ['id', 'name', 'email', ...]
           read_only_fields = ['id', 'created_at']
   ```

3. **ViewSet**: Add in `views.py`
   ```python
   from rest_framework import viewsets
   
   class CustomerViewSet(viewsets.ModelViewSet):
       queryset = Customer.objects.all()
       serializer_class = CustomerSerializer
       
       def get_queryset(self):
           # Tenant-aware filtering
           return self.queryset.filter(tenant=self.request.tenant)
   ```

4. **URL Routing**: Register in `urls.py`
   ```python
   from rest_framework.routers import DefaultRouter
   
   router = DefaultRouter()
   router.register(r'customers', CustomerViewSet)
   ```

5. **Tests**: Add in `tests.py`
   ```python
   from django.test import TestCase
   from rest_framework.test import APIClient
   
   class CustomerAPITest(TestCase):
       def setUp(self):
           self.client = APIClient()
           # ... setup test data
       
       def test_list_customers(self):
           response = self.client.get('/api/customers/')
           self.assertEqual(response.status_code, 200)
   ```

## React/TypeScript Patterns

### Component Structure
```typescript
// Functional component with TypeScript
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

interface CustomerListProps {
  tenantId: string;
  onSelect?: (customer: Customer) => void;
}

export const CustomerList: React.FC<CustomerListProps> = ({ tenantId, onSelect }) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch data
  }, [tenantId]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage>{error}</ErrorMessage>;

  return <Container>{/* ... */}</Container>;
};
```

### API Integration
Use the existing service layer in `frontend/src/services/`:
```typescript
import { apiService } from '../services/apiService';

const customers = await apiService.get<Customer[]>('/api/customers/');
```

### Testing Components
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

test('renders customer list', async () => {
  render(<CustomerList tenantId="123" />);
  await waitFor(() => {
    expect(screen.getByText(/customers/i)).toBeInTheDocument();
  });
});
```

## Continuous Learning and Logging

For every task, after completion and before creating the PR, append an entry to `.github/copilot-log.md`:

### Log Entry Format:
```markdown
## Task: [Brief task description] - [Date: YYYY-MM-DD]
- **Actions Taken**: [List key steps taken to complete the task]
- **Misses/Failures**: [What was overlooked, didn't work, or caused issues]
- **Lessons Learned**: [Key insights and understanding gained]
- **Efficiency Suggestions**: [Ways to improve this type of task next time]
```

**Guidelines**:
- Keep entries concise (under 200 words)
- Be specific about what went wrong and why
- Review previous logs before starting similar tasks
- If repeating a past mistake, acknowledge it and propose preventive measures

## Multi-Tenancy Considerations

ProjectMeats uses a **shared database, shared schema** multi-tenancy pattern with tenant_id isolation.

### Key Requirements:
1. **All business models** must have a `tenant` ForeignKey field
2. **All queries** must filter by tenant to prevent data leakage
3. **API ViewSets** must override `get_queryset()` to filter by `request.tenant`
4. **Tests** must verify tenant isolation (create data for multiple tenants, verify only own tenant's data is returned)

### Example:
```python
# Model
class Customer(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

# ViewSet
class CustomerViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Customer.objects.filter(tenant=self.request.tenant)

# Test
def test_tenant_isolation(self):
    tenant1 = Tenant.objects.create(name="Tenant1")
    tenant2 = Tenant.objects.create(name="Tenant2")
    customer1 = Customer.objects.create(tenant=tenant1, name="Customer1")
    customer2 = Customer.objects.create(tenant=tenant2, name="Customer2")
    
    # Request as tenant1 should only see customer1
    self.client.force_authenticate(user=tenant1_user)
    response = self.client.get('/api/customers/')
    self.assertEqual(len(response.data), 1)
```

## Database Migration Guidelines

### Migration Workflow:
1. **Make changes** to `models.py`
2. **Create migration**: `python manage.py makemigrations`
3. **Review migration**: Check the generated migration file for correctness
4. **Test migration**: Apply locally with `python manage.py migrate`
5. **Test rollback**: Ensure migration can be rolled back if needed
6. **Update admin**: Add new fields to `admin.py` (list_display, fieldsets, etc.)
7. **Update serializers**: Include new fields in API serializers
8. **Update tests**: Add tests for new fields/functionality
9. **Verify in admin**: Start server and check Django admin interface

### Migration Best Practices:
- **Review before applying**: Always review auto-generated migrations
- **Data migrations**: Use `RunPython` for data transformations
- **Backwards compatibility**: Consider existing data when adding constraints
- **Index strategically**: Add `db_index=True` for frequently queried fields
- **Document complex migrations**: Add comments for non-obvious changes

### Migration Verification Checklist

Before considering any database-related task complete:

- [ ] Run `python manage.py makemigrations` locally
- [ ] Run `python manage.py migrate` locally  
- [ ] Test model changes in Django admin interface
- [ ] Update admin.py registrations for new fields
- [ ] Update serializers.py for API endpoints
- [ ] Update forms.py if frontend forms are affected
- [ ] Test API endpoints with new fields
- [ ] Verify field visibility in admin interface
- [ ] Document migration dependencies and potential rollback procedures

## Component Update Checklist

When adding new model fields or relationships:

- [ ] **Models**: Add fields with appropriate types, constraints, and defaults
- [ ] **Admin**: Update admin.py to display new fields in list_display, fieldsets, etc.
- [ ] **Serializers**: Update API serializers to include new fields
- [ ] **Views**: Update views if they need to handle new fields
- [ ] **Forms**: Update frontend forms if they interact with new fields
- [ ] **Templates**: Update templates if they display new data
- [ ] **Tests**: Add or update tests for new functionality
- [ ] **Documentation**: Update API documentation and field descriptions

## UAT and Production Verification

After deploying changes:

1. **UAT Environment** (uat.meatscentral.com):
   - [ ] Verify migrations were applied successfully
   - [ ] Check admin interface for field visibility
   - [ ] Test API endpoints return new fields
   - [ ] Verify frontend displays new data correctly
   - [ ] Check for any console errors or warnings

2. **Production Environment**:
   - [ ] Confirm CI/CD workflow approvals completed
   - [ ] Monitor deployment logs for migration success
   - [ ] Verify field visibility and functionality
   - [ ] Check performance impact of new fields
   - [ ] Monitor error logs for any issues

## Security Best Practices

1. **Authentication & Authorization**:
   - Always verify user authentication before processing requests
   - Enforce tenant isolation at the database query level
   - Use Django's permission system for authorization

2. **Data Validation**:
   - Validate all user inputs in serializers
   - Use Django's built-in validators when possible
   - Sanitize data before database operations

3. **API Security**:
   - Use HTTPS in production (enforced by deployment config)
   - Implement rate limiting for public endpoints
   - Never expose sensitive data in API responses
   - Use read_only_fields for system-managed fields

4. **Environment Variables**:
   - Store secrets in environment variables, never in code
   - Use `django-environ` for configuration management
   - Check `.env.example` for required variables

## Performance Considerations

1. **Database Queries**:
   - Use `select_related()` and `prefetch_related()` to avoid N+1 queries
   - Add database indexes for frequently filtered/ordered fields
   - Use `.only()` and `.defer()` to limit field selection when appropriate

2. **API Responses**:
   - Implement pagination for list endpoints (DRF's PageNumberPagination)
   - Use caching for expensive queries
   - Consider API response compression

3. **Frontend Performance**:
   - Code splitting and lazy loading for routes
   - Memoize expensive computations with `useMemo`
   - Debounce search inputs and API calls
   - Use React.memo for pure components

## Error Prevention Strategies

1. **Before Starting**: Always review `.github/copilot-log.md` for similar past tasks and lessons learned
2. **During Development**: Use the checklists above systematically
3. **Testing**: Test locally before pushing, test on UAT before production
4. **Documentation**: Document any non-standard approaches or workarounds
5. **Review**: Have changes reviewed by team members for complex modifications

## Common Pitfalls to Avoid

1. **Missing Admin Updates**: Always update admin.py when adding model fields
2. **Incomplete Migrations**: Ensure migrations handle data preservation and constraints
3. **API Inconsistencies**: Update serializers to maintain API contract consistency
4. **Frontend Disconnection**: Ensure frontend components can handle new data structures
5. **Testing Gaps**: Don't skip local testing before UAT deployment
6. **Documentation Lag**: Update documentation as changes are made, not afterwards
7. **Tenant Leakage**: Always filter queries by tenant in multi-tenant features
8. **Breaking Changes**: Maintain backwards compatibility in API changes

## Deployment and Environment

### Environments:
- **Development**: Local development environment (localhost)
- **UAT/Staging**: uat.meatscentral.com - Test environment for validation
- **Production**: Production environment - Requires approval for deployments

### Deployment Workflow:
1. Changes are tested locally
2. PR created and reviewed
3. Merge to develop triggers UAT deployment
4. After UAT validation, merge to main
5. Production deployment requires manual approval

### Environment Configuration:
Use the centralized configuration system:
```bash
python config/manage_env.py setup development   # Dev setup
python config/manage_env.py setup staging       # Staging setup
python config/manage_env.py validate            # Validate config
```

### Post-Deployment Verification:
After deployment, verify:
- Migrations applied successfully
- Admin interface accessible and functional
- API endpoints responding correctly
- Frontend displaying data properly
- No console errors or warnings

See `.github/copilot-log.md` for common deployment issues and their resolutions.

## Related Documentation

For more detailed information, refer to:
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Comprehensive contribution guidelines
- **[README.md](../README.md)** - Project overview and quick start
- **[docs/BACKEND_ARCHITECTURE.md](../docs/BACKEND_ARCHITECTURE.md)** - Backend architecture details
- **[docs/FRONTEND_ARCHITECTURE.md](../docs/FRONTEND_ARCHITECTURE.md)** - Frontend architecture details
- **[docs/TESTING_STRATEGY.md](../docs/TESTING_STRATEGY.md)** - Testing guidelines and examples
- **[docs/DEPLOYMENT_GUIDE.md](../docs/DEPLOYMENT_GUIDE.md)** - Deployment procedures
- **[docs/ENVIRONMENT_GUIDE.md](../docs/ENVIRONMENT_GUIDE.md)** - Environment configuration
- **[.github/copilot-log.md](copilot-log.md)** - Learning log with past lessons and common issues

## Getting Help

If you encounter issues or need clarification:
1. Check the `.github/copilot-log.md` for similar past issues
2. Review the relevant documentation in the `docs/` directory
3. Consult the `CONTRIBUTING.md` file for development guidelines
4. Check existing issues and PRs for context
5. Ask in the PR comments if implementing a specific task

---

**Remember**: 
- Always run tests before and after changes
- Review `copilot-log.md` for lessons learned
- Update the log when completing tasks
- Keep changes minimal and focused
- Maintain backwards compatibility