# ProjectMeats Testing Strategy

## Overview

This document outlines the testing strategy for ProjectMeats, covering backend and frontend testing approaches, tools, and best practices.

## Testing Philosophy

- **Test Pyramid**: More unit tests, fewer integration tests, minimal E2E tests
- **Test Coverage**: Aim for 80%+ coverage on critical business logic
- **CI/CD Integration**: All tests run automatically on push/PR
- **Fast Feedback**: Tests should run quickly to enable rapid development

## Backend Testing (Django)

### Test Structure

```
backend/
├── apps/
│   ├── customers/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   ├── test_serializers.py
│   │   │   └── test_api_endpoints.py
│   │   └── ...
│   └── ...
└── test_allowed_hosts_fix.py  # Configuration tests
```

### Testing Tools

- **Framework**: Django's built-in test framework (unittest)
- **Test Client**: Django REST Framework's APIClient
- **Fixtures**: Django fixtures for test data
- **Coverage**: coverage.py for code coverage reports
- **Factories**: Future: Factory Boy for test data generation

### Test Types

#### 1. Model Tests

Test model functionality, validation, and business logic.

```python
# apps/customers/tests/test_models.py
from django.test import TestCase
from apps.customers.models import Customer

class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="test@example.com"
        )
    
    def test_customer_creation(self):
        """Test customer is created with correct attributes"""
        self.assertEqual(self.customer.name, "Test Customer")
        self.assertEqual(self.customer.email, "test@example.com")
    
    def test_customer_str_representation(self):
        """Test string representation of customer"""
        self.assertEqual(str(self.customer), "Test Customer")
    
    def test_customer_validation(self):
        """Test customer email validation"""
        customer = Customer(name="Invalid", email="not-an-email")
        with self.assertRaises(ValidationError):
            customer.full_clean()
```

#### 2. API Endpoint Tests

Test REST API endpoints for correct responses and behavior.

```python
# apps/customers/tests/test_api_endpoints.py
from rest_framework.test import APITestCase
from rest_framework import status
from apps.customers.models import Customer

class CustomerAPITest(APITestCase):
    def setUp(self):
        self.customer_data = {
            'name': 'Test Customer',
            'email': 'test@example.com'
        }
    
    def test_create_customer(self):
        """Test creating a new customer via API"""
        response = self.client.post(
            '/api/v1/customers/',
            self.customer_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.get().name, 'Test Customer')
    
    def test_get_customer_list(self):
        """Test retrieving customer list"""
        Customer.objects.create(**self.customer_data)
        response = self.client.get('/api/v1/customers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_update_customer(self):
        """Test updating a customer"""
        customer = Customer.objects.create(**self.customer_data)
        response = self.client.patch(
            f'/api/v1/customers/{customer.id}/',
            {'name': 'Updated Name'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer.refresh_from_db()
        self.assertEqual(customer.name, 'Updated Name')
    
    def test_delete_customer(self):
        """Test deleting a customer"""
        customer = Customer.objects.create(**self.customer_data)
        response = self.client.delete(f'/api/v1/customers/{customer.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)
```

#### 3. Serializer Tests

Test data serialization and validation.

```python
# apps/customers/tests/test_serializers.py
from django.test import TestCase
from apps.customers.models import Customer
from apps.customers.serializers import CustomerSerializer

class CustomerSerializerTest(TestCase):
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data"""
        data = {
            'name': 'Test Customer',
            'email': 'test@example.com'
        }
        serializer = CustomerSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_with_invalid_email(self):
        """Test serializer rejects invalid email"""
        data = {
            'name': 'Test Customer',
            'email': 'not-an-email'
        }
        serializer = CustomerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
```

#### 4. View Tests

Test view logic and permissions.

```python
# apps/customers/tests/test_views.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class CustomerViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access API"""
        response = self.client.get('/api/v1/customers/')
        self.assertEqual(response.status_code, 401)
    
    def test_authenticated_access(self):
        """Test that authenticated users can access API"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/customers/')
        self.assertEqual(response.status_code, 200)
```

### Running Backend Tests

```bash
# Run all tests
cd backend && python manage.py test

# Run specific app tests
python manage.py test apps.customers

# Run specific test class
python manage.py test apps.customers.tests.test_models.CustomerModelTest

# Run specific test method
python manage.py test apps.customers.tests.test_models.CustomerModelTest.test_customer_creation

# Run with verbosity
python manage.py test --verbosity=2

# Keep test database for inspection
python manage.py test --keepdb

# Run tests in parallel
python manage.py test --parallel
```

### Code Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
# View at htmlcov/index.html

# Show missing lines
coverage report -m
```

## Frontend Testing (React)

### Test Structure

```
frontend/src/
├── components/
│   ├── Layout/
│   │   ├── Header.tsx
│   │   └── Header.test.tsx
│   └── ...
├── services/
│   ├── apiService.ts
│   └── apiService.test.ts
└── App.test.tsx
```

### Testing Tools

- **Framework**: Jest (via Create React App)
- **Testing Library**: React Testing Library
- **Mocking**: Jest mocks for API calls
- **Coverage**: Built-in Jest coverage

### Test Types

#### 1. Component Tests

Test component rendering and user interactions.

```typescript
// src/components/Layout/Header.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Header from './Header';

describe('Header Component', () => {
  test('renders header with logo', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );
    const logo = screen.getByText(/ProjectMeats/i);
    expect(logo).toBeInTheDocument();
  });

  test('displays user menu when authenticated', () => {
    render(
      <BrowserRouter>
        <Header isAuthenticated={true} user={{ name: 'Test User' }} />
      </BrowserRouter>
    );
    const userName = screen.getByText(/Test User/i);
    expect(userName).toBeInTheDocument();
  });

  test('shows login button when not authenticated', () => {
    render(
      <BrowserRouter>
        <Header isAuthenticated={false} />
      </BrowserRouter>
    );
    const loginButton = screen.getByText(/Login/i);
    expect(loginButton).toBeInTheDocument();
  });

  test('logout button calls logout function', () => {
    const mockLogout = jest.fn();
    render(
      <BrowserRouter>
        <Header 
          isAuthenticated={true} 
          user={{ name: 'Test User' }}
          onLogout={mockLogout}
        />
      </BrowserRouter>
    );
    const logoutButton = screen.getByText(/Logout/i);
    fireEvent.click(logoutButton);
    expect(mockLogout).toHaveBeenCalledTimes(1);
  });
});
```

#### 2. Service Tests

Test API service functions and error handling.

```typescript
// src/services/apiService.test.ts
import axios from 'axios';
import { apiService } from './apiService';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('successful GET request', async () => {
    const mockData = { id: 1, name: 'Test' };
    mockedAxios.get.mockResolvedValue({ data: mockData });

    const result = await apiService.get('/customers/1/');
    expect(result).toEqual(mockData);
    expect(mockedAxios.get).toHaveBeenCalledWith('/customers/1/');
  });

  test('handles API errors', async () => {
    const mockError = {
      response: {
        status: 404,
        data: { detail: 'Not found' }
      }
    };
    mockedAxios.get.mockRejectedValue(mockError);

    await expect(apiService.get('/customers/999/')).rejects.toThrow();
  });
});
```

#### 3. Hook Tests

Test custom React hooks.

```typescript
// src/hooks/useAuth.test.ts
import { renderHook, act } from '@testing-library/react';
import { useAuth } from './useAuth';

describe('useAuth Hook', () => {
  test('initializes with no user', () => {
    const { result } = renderHook(() => useAuth());
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  test('login sets user', async () => {
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    expect(result.current.user).toBeTruthy();
    expect(result.current.isAuthenticated).toBe(true);
  });
});
```

### Running Frontend Tests

```bash
# Run all tests
cd frontend && npm test

# Run tests in CI mode (no watch)
npm run test:ci

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- Header.test.tsx

# Update snapshots
npm test -- -u
```

## Integration Testing

### Backend Integration Tests

Test complete request/response cycles including database operations.

```python
# apps/purchase_orders/tests/test_integration.py
from django.test import TransactionTestCase
from apps.customers.models import Customer
from apps.suppliers.models import Supplier
from apps.purchase_orders.models import PurchaseOrder

class PurchaseOrderIntegrationTest(TransactionTestCase):
    def test_complete_order_workflow(self):
        """Test complete purchase order creation workflow"""
        # Create customer
        customer = Customer.objects.create(
            name="Test Customer",
            email="customer@example.com"
        )
        
        # Create supplier
        supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com"
        )
        
        # Create purchase order
        order = PurchaseOrder.objects.create(
            customer=customer,
            supplier=supplier,
            total_amount=1000.00
        )
        
        # Verify relationships
        self.assertEqual(order.customer.name, "Test Customer")
        self.assertEqual(order.supplier.name, "Test Supplier")
        self.assertEqual(order.status, 'pending')
        
        # Update order status
        order.status = 'confirmed'
        order.save()
        
        # Verify update
        order.refresh_from_db()
        self.assertEqual(order.status, 'confirmed')
```

## End-to-End Testing (Future)

### Tools (Planned)
- **Playwright** or **Cypress** for E2E testing
- Test complete user workflows
- Cross-browser testing

### Example E2E Test Structure

```typescript
// e2e/login.spec.ts
test('user can login and view dashboard', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('text=Login');
  await page.fill('input[name=email]', 'test@example.com');
  await page.fill('input[name=password]', 'password123');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL('http://localhost:3000/dashboard');
  await expect(page.locator('h1')).toContainText('Dashboard');
});
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python manage.py test
      - name: Generate coverage
        run: |
          cd backend
          coverage run --source='.' manage.py test
          coverage xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: 18
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm run test:ci
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Data Management

### Backend Fixtures

```python
# apps/customers/fixtures/test_data.json
[
  {
    "model": "customers.customer",
    "pk": 1,
    "fields": {
      "name": "Test Customer",
      "email": "test@example.com"
    }
  }
]
```

Load fixtures:
```bash
python manage.py loaddata test_data
```

### Factory Pattern (Future)

```python
# apps/customers/factories.py
import factory
from apps.customers.models import Customer

class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer
    
    name = factory.Faker('company')
    email = factory.Faker('email')
```

## Best Practices

### General
1. **Write tests first** (TDD when possible)
2. **Keep tests isolated** - no dependencies between tests
3. **Use descriptive test names** - explain what is being tested
4. **Test behavior, not implementation** - focus on outcomes
5. **Mock external dependencies** - API calls, file systems, etc.

### Backend-Specific
1. **Use transactions** - each test in its own transaction
2. **Clean up after tests** - database should be reset
3. **Test edge cases** - null values, invalid data
4. **Test permissions** - authentication and authorization

### Frontend-Specific
1. **Test user interactions** - clicks, form submissions
2. **Avoid testing implementation details** - test outcomes
3. **Use semantic queries** - getByRole, getByLabelText
4. **Mock API calls** - don't make real network requests

## Coverage Goals

- **Overall**: 80%+ code coverage
- **Critical paths**: 95%+ coverage (authentication, orders, payments)
- **New features**: 100% coverage required
- **Bug fixes**: Add regression test before fixing

## Running All Tests

```bash
# Root level Makefile
make test                    # Run all tests (backend + frontend)
make test-backend           # Backend only
make test-frontend          # Frontend only
```

## Monitoring Test Quality

### Metrics to Track
- Test coverage percentage
- Test execution time
- Number of failing tests
- Test flakiness (intermittent failures)

### Tools
- Coverage.py for backend coverage
- Jest coverage for frontend
- Codecov for coverage tracking
- GitHub Actions for CI/CD

## Future Improvements

1. **Visual Regression Testing**
   - Chromatic or Percy for UI testing
   - Catch visual bugs automatically

2. **Performance Testing**
   - Locust or Artillery for load testing
   - Lighthouse for frontend performance

3. **Security Testing**
   - OWASP ZAP for security scanning
   - Dependency scanning for vulnerabilities

4. **Mutation Testing**
   - Validate test quality by mutating code
   - Ensure tests actually catch bugs

## Resources

- [Django Testing](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [DRF Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [React Testing Library](https://testing-library.com/react)
- [Jest Documentation](https://jestjs.io/)
- [Testing Best Practices](https://testingjavascript.com/)
