# Common Development Tasks

**Last Updated**: December 1, 2024  
**Purpose**: Step-by-step guides for frequent development operations

---

## 📋 Table of Contents

1. [Environment Setup](#environment-setup)
2. [Daily Development Workflow](#daily-development-workflow)
3. [Database Operations](#database-operations)
4. [API Development](#api-development)
5. [Frontend Development](#frontend-development)
6. [Testing](#testing)
7. [Git & Branch Operations](#git--branch-operations)
8. [Debugging](#debugging)
9. [Deployment](#deployment)
10. [Maintenance](#maintenance)

---

## 🚀 Environment Setup

### First-Time Setup
```bash
# 1. Clone repository
git clone https://github.com/Meats-Central/ProjectMeats.git
cd ProjectMeats

# 2. Install pre-commit hooks (REQUIRED)
pre-commit install

# 3. Quick setup (recommended)
./start_dev.sh

# OR manual setup
python config/manage_env.py setup development
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
make migrate
make dev
```

### Updating Your Environment
```bash
# Update Python dependencies
cd backend
pip install -r requirements.txt

# Update Node dependencies
cd frontend
npm install

# Apply new migrations
cd backend
python manage.py migrate_schemas
```

---

## 💻 Daily Development Workflow

### Starting Your Day
```bash
# 1. Update your local repo
git checkout development
git pull origin development

# 2. Start servers
./start_dev.sh

# 3. Check services are running
# Backend: http://localhost:8000/api/docs/
# Frontend: http://localhost:3000
```

### Creating a New Feature
```bash
# 1. Create feature branch from development
git checkout development
git pull origin development
git checkout -b feature/my-feature

# 2. Make changes
# ... code ...

# 3. Test changes
make test

# 4. Format and lint
make format
make lint

# 5. Commit (pre-commit hooks will run)
git add .
git commit -m "feat(scope): description"

# 6. Push and create PR to development
git push origin feature/my-feature
# Create PR at: https://github.com/Meats-Central/ProjectMeats/pulls
```

### Ending Your Day
```bash
# Stop servers
./stop_dev.sh

# Commit work in progress
git add .
git commit -m "wip: save progress on feature"
git push origin feature/my-feature
```

---

## 🗄️ Database Operations

### Creating a New Model
```python
# 1. Define model in backend/apps/<app>/models.py
from django.db import models
from apps.core.models import BaseModel

class MyModel(BaseModel):  # BaseModel adds created_at, updated_at
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'myapp_mymodel'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
```

```bash
# 2. Create migration
cd backend
python manage.py makemigrations <app_name>

# 3. Review migration file
cat apps/<app_name>/migrations/000X_*.py

# 4. Apply migration to shared schema
python manage.py migrate_schemas --shared

# 5. Apply migration to all tenant schemas
python manage.py migrate_schemas

# 6. Verify migration
python manage.py showmigrations <app_name>
```

### Modifying an Existing Model
```python
# 1. Edit model in backend/apps/<app>/models.py
class MyModel(BaseModel):
    name = models.CharField(max_length=255)
    # New field
    email = models.EmailField(blank=True, null=True)
```

```bash
# 2. Create migration
python manage.py makemigrations <app_name>

# 3. Check migration
python manage.py sqlmigrate <app_name> 000X

# 4. Apply migration
python manage.py migrate_schemas --shared  # For shared apps
python manage.py migrate_schemas           # For tenant apps
```

### Creating a Data Migration
```bash
# 1. Create empty migration
cd backend
python manage.py makemigrations --empty <app_name> -n migrate_data

# 2. Edit migration file
```

```python
# apps/<app_name>/migrations/000X_migrate_data.py
from django.db import migrations

def migrate_data_forward(apps, schema_editor):
    MyModel = apps.get_model('<app_name>', 'MyModel')
    # Perform data migration
    for obj in MyModel.objects.filter(old_field__isnull=True):
        obj.new_field = calculate_value(obj)
        obj.save()

def migrate_data_backward(apps, schema_editor):
    # Reverse migration if needed
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('<app_name>', '000X_previous_migration'),
    ]
    
    operations = [
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
    ]
```

```bash
# 3. Apply migration
python manage.py migrate_schemas
```

### Resetting Database (Development Only)
```bash
# WARNING: Destroys all data!

# Option 1: Drop and recreate database
dropdb projectmeats_dev
createdb projectmeats_dev

# Option 2: Delete migration files and reset
rm backend/apps/*/migrations/0*.py
python manage.py makemigrations
python manage.py migrate_schemas
```

### Inspecting Database
```bash
# Django shell
cd backend
python manage.py shell

# List all models
>>> from django.apps import apps
>>> for model in apps.get_models():
...     print(model._meta.label)

# Query data
>>> from apps.suppliers.models import Supplier
>>> Supplier.objects.all()
>>> Supplier.objects.filter(is_active=True).count()

# Check tenant schemas
>>> from apps.tenants.models import Client
>>> Client.objects.all()
```

---

## 🔌 API Development

### Creating a New API Endpoint (Full Stack)

#### Backend: Model
```python
# backend/apps/<app>/models.py
from django.db import models
from apps.core.models import BaseModel

class Product(BaseModel):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'products_product'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
```

#### Backend: Serializer
```python
# backend/apps/<app>/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'price', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_sku(self, value):
        """Custom validation for SKU"""
        if len(value) < 3:
            raise serializers.ValidationError("SKU must be at least 3 characters")
        return value.upper()
```

#### Backend: ViewSet
```python
# backend/apps/<app>/views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing products.
    
    list: Get all products
    retrieve: Get a single product
    create: Create a new product
    update: Update a product
    partial_update: Partially update a product
    destroy: Delete a product
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'sku']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']
```

#### Backend: URLs
```python
# backend/apps/<app>/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
```

```python
# backend/projectmeats/urls.py (add to existing)
from django.urls import path, include

urlpatterns = [
    # ... existing patterns
    path('api/v1/', include('apps.products.urls')),
]
```

#### Backend: Tests
```python
# backend/apps/<app>/tests/test_views.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import Product

User = get_user_model()

class ProductAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_products(self):
        """Test listing products"""
        Product.objects.create(name='Product 1', sku='SKU001', price=10.00)
        Product.objects.create(name='Product 2', sku='SKU002', price=20.00)
        
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_create_product(self):
        """Test creating a product"""
        data = {
            'name': 'New Product',
            'sku': 'SKU003',
            'price': 30.00,
            'is_active': True
        }
        response = self.client.post('/api/v1/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
    
    def test_update_product(self):
        """Test updating a product"""
        product = Product.objects.create(name='Old Name', sku='SKU001', price=10.00)
        data = {'name': 'New Name'}
        response = self.client.patch(f'/api/v1/products/{product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.name, 'New Name')
```

```bash
# Run tests
cd backend
python manage.py test apps.products
```

#### Frontend: Types
```typescript
// frontend/src/types/business.types.ts
export interface Product {
  id: number;
  name: string;
  sku: string;
  price: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductCreateInput {
  name: string;
  sku: string;
  price: number;
  is_active?: boolean;
}
```

#### Frontend: API Service
```typescript
// frontend/src/services/businessApi.ts
import { api } from './api';
import { Product, ProductCreateInput } from '../types/business.types';

export const productApi = {
  // List all products
  list: async (): Promise<Product[]> => {
    const response = await api.get('/api/v1/products/');
    return response.data;
  },
  
  // Get single product
  get: async (id: number): Promise<Product> => {
    const response = await api.get(`/api/v1/products/${id}/`);
    return response.data;
  },
  
  // Create product
  create: async (data: ProductCreateInput): Promise<Product> => {
    const response = await api.post('/api/v1/products/', data);
    return response.data;
  },
  
  // Update product
  update: async (id: number, data: Partial<Product>): Promise<Product> => {
    const response = await api.patch(`/api/v1/products/${id}/`, data);
    return response.data;
  },
  
  // Delete product
  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/v1/products/${id}/`);
  },
};
```

#### Frontend: Component
```typescript
// frontend/src/pages/Products/ProductList.tsx
import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { productApi } from '../../services/businessApi';
import { Product } from '../../types/business.types';

const Container = styled.div`
  padding: 20px;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

export const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    loadProducts();
  }, []);
  
  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await productApi.list();
      setProducts(data);
    } catch (err) {
      setError('Failed to load products');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <Container>Loading...</Container>;
  if (error) return <Container>Error: {error}</Container>;
  
  return (
    <Container>
      <h1>Products</h1>
      <Table>
        <thead>
          <tr>
            <th>Name</th>
            <th>SKU</th>
            <th>Price</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.id}>
              <td>{product.name}</td>
              <td>{product.sku}</td>
              <td>${product.price}</td>
              <td>{product.is_active ? 'Active' : 'Inactive'}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Container>
  );
};
```

---

## 🎨 Frontend Development

### Creating a New Page Component
```typescript
// 1. Create page directory
// frontend/src/pages/NewPage/

// 2. Create component file
// frontend/src/pages/NewPage/index.tsx
import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Title = styled.h1`
  font-size: 24px;
  margin-bottom: 20px;
`;

export const NewPage: React.FC = () => {
  return (
    <Container>
      <Title>New Page</Title>
      {/* Content */}
    </Container>
  );
};

// 3. Add route in App.tsx
// frontend/src/App.tsx
import { NewPage } from './pages/NewPage';

// In Routes:
<Route path="/new-page" element={<NewPage />} />
```

### Creating a Reusable Component
```typescript
// frontend/src/components/common/Button.tsx
import React from 'react';
import styled from 'styled-components';

interface ButtonProps {
  onClick?: () => void;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
}

const StyledButton = styled.button<{ variant: string }>`
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  
  background-color: ${props => {
    switch (props.variant) {
      case 'primary': return '#007bff';
      case 'secondary': return '#6c757d';
      case 'danger': return '#dc3545';
      default: return '#007bff';
    }
  }};
  
  color: white;
  
  &:hover {
    opacity: 0.8;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

export const Button: React.FC<ButtonProps> = ({
  onClick,
  children,
  variant = 'primary',
  disabled = false,
}) => {
  return (
    <StyledButton onClick={onClick} variant={variant} disabled={disabled}>
      {children}
    </StyledButton>
  );
};
```

### Adding a React Context
```typescript
// frontend/src/contexts/SettingsContext.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface SettingsContextType {
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const SettingsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  
  return (
    <SettingsContext.Provider value={{ theme, setTheme }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within SettingsProvider');
  }
  return context;
};

// Usage in App.tsx:
// <SettingsProvider>
//   <App />
// </SettingsProvider>
```

---

## 🧪 Testing

### Writing Backend Tests
```python
# backend/apps/<app>/tests/test_models.py
from django.test import TestCase
from ..models import MyModel

class MyModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.obj = MyModel.objects.create(name='Test')
    
    def test_string_representation(self):
        """Test __str__ method"""
        self.assertEqual(str(self.obj), 'Test')
    
    def test_default_values(self):
        """Test default field values"""
        self.assertTrue(self.obj.is_active)
```

### Running Backend Tests
```bash
cd backend

# All tests
python manage.py test

# Specific app
python manage.py test apps.suppliers

# Specific test file
python manage.py test apps.suppliers.tests.test_models

# Specific test class
python manage.py test apps.suppliers.tests.test_models.SupplierTest

# Specific test method
python manage.py test apps.suppliers.tests.test_models.SupplierTest.test_creation

# With coverage
pytest --cov=apps --cov-report=html
# View: open htmlcov/index.html
```

### Writing Frontend Tests
```typescript
// frontend/src/components/__tests__/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../Button';

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByText('Click me')).toBeDisabled();
  });
});
```

### Running Frontend Tests
```bash
cd frontend

# All tests
npm test

# Watch mode (default)
npm test -- --watch

# Coverage
npm test -- --coverage

# Specific file
npm test -- Button.test.tsx

# Update snapshots
npm test -- -u
```

---

## 🌿 Git & Branch Operations

### Creating a Feature Branch
```bash
# Update development
git checkout development
git pull origin development

# Create feature branch
git checkout -b feature/my-feature

# Push to remote
git push -u origin feature/my-feature
```

### Keeping Your Branch Up to Date
```bash
# While on your feature branch
git fetch origin
git rebase origin/development

# Or merge (if rebase causes issues)
git merge origin/development

# Push updates
git push origin feature/my-feature --force-with-lease
```

### Creating a Pull Request
```bash
# 1. Push your branch
git push origin feature/my-feature

# 2. Go to GitHub
# https://github.com/Meats-Central/ProjectMeats/pulls

# 3. Click "New Pull Request"
# Base: development
# Compare: feature/my-feature

# 4. Fill in details
# Title: feat(scope): description
# Description: Explain changes, link issues

# 5. Request reviews
# Add reviewers from team

# 6. Ensure CI passes
# Fix any failing checks
```

### Resolving Merge Conflicts
```bash
# 1. Update your branch
git checkout feature/my-feature
git fetch origin
git merge origin/development

# 2. Identify conflicts
git status

# 3. Resolve conflicts in editor
# Look for <<<<<<< HEAD markers

# 4. Mark as resolved
git add <resolved-files>

# 5. Complete merge
git commit

# 6. Push
git push origin feature/my-feature
```

---

## 🐛 Debugging

### Backend Debugging
```bash
# Enable DEBUG mode (development only)
# In backend/projectmeats/settings/development.py
DEBUG = True

# Django shell for testing queries
cd backend
python manage.py shell

# Example debugging session:
>>> from apps.suppliers.models import Supplier
>>> from django.db import connection
>>> from django.db import reset_queries

# Enable query logging
>>> from django.conf import settings
>>> settings.DEBUG = True

# Run query and see SQL
>>> suppliers = list(Supplier.objects.all())
>>> print(connection.queries)

# Test specific function
>>> from apps.suppliers.views import some_function
>>> result = some_function(test_data)
>>> print(result)
```

### Frontend Debugging
```typescript
// Add console.log statements
console.log('Debug info:', variable);

// Use React DevTools
// Install: https://react-devtools.com/

// Network debugging
// 1. Open browser DevTools (F12)
// 2. Network tab
// 3. Filter: XHR/Fetch
// 4. Inspect API calls

// Error boundaries
// frontend/src/components/ErrorBoundary.tsx
import React, { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <div>Something went wrong: {this.state.error?.message}</div>;
    }
    return this.props.children;
  }
}
```

---

## 🚀 Deployment

### Pre-Deployment Checklist
```bash
# 1. All tests pass
make test

# 2. Code formatted
make format

# 3. No lint errors
make lint

# 4. Migrations created
python manage.py makemigrations --check

# 5. Environment variables set
python config/manage_env.py validate

# 6. Branch workflow followed
# feature → development → UAT → main
```

### Manual Deployment (Emergency Only)
```bash
# SSH to server
ssh user@server-ip

# Navigate to app directory
cd /app

# Pull latest code
git pull origin main

# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# Run migrations
cd backend
python manage.py migrate_schemas

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## 🔧 Maintenance

### Cleaning Up Old Branches
```bash
# List merged branches
git branch --merged development

# Delete local branch
git branch -d feature/old-feature

# Delete remote branch
git push origin --delete feature/old-feature
```

### Updating Documentation
```bash
# Add documentation
# Edit relevant .md files in docs/

# Commit
git add docs/
git commit -m "docs: update <topic> documentation"
```

### Database Maintenance
```bash
# Backup database
pg_dump projectmeats_prod > backup_$(date +%Y%m%d).sql

# Restore database
psql projectmeats_prod < backup_20241201.sql

# Vacuum database (PostgreSQL)
psql projectmeats_prod -c "VACUUM ANALYZE;"
```

---

**Last Updated**: December 1, 2024  
**Maintained by**: ProjectMeats Team  
**Version**: 1.0.0
