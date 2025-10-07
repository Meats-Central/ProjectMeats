# ProjectMeats Core Components Architecture

## Overview

The core components provide the foundational base models and common functionality used across all ProjectMeats applications. This document details the architecture, model hierarchy, and design patterns.

## Core Models Hierarchy

```
┌─────────────────────────────────────────────────┐
│         Django Model (Abstract)                  │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────┴─────────┬──────────────────┐
         │                   │                  │
         ▼                   ▼                  ▼
┌────────────────┐  ┌─────────────────┐  ┌──────────────┐
│ StatusModel    │  │ TimestampModel  │  │   Protein    │
│  (Abstract)    │  │   (Abstract)    │  │  (Concrete)  │
│                │  │                 │  │              │
│ - status       │  │ - created_on    │  │ - name       │
│                │  │ - modified_on   │  │              │
└────────────────┘  └────────┬────────┘  └──────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  OwnedModel     │
                    │   (Abstract)    │
                    │                 │
                    │ Inherits:       │
                    │ - created_on    │
                    │ - modified_on   │
                    │                 │
                    │ Adds:           │
                    │ - owner         │
                    │ - created_by    │
                    │ - modified_by   │
                    └─────────────────┘
                             │
                             │
                    Used by many apps:
                    - AI Assistant
                    - Customers
                    - Suppliers
                    - Purchase Orders
                    - etc.
```

## Model Components

### 1. Protein Model

**Purpose**: Central catalog of protein/meat types used across suppliers and customers.

**Fields**:
- `name` (CharField): Unique protein type (e.g., Beef, Pork, Chicken, Lamb)

**Features**:
- Unique constraint on name
- Alphabetically ordered by name
- Used by suppliers and customers for product categorization

**Usage Example**:
```python
from apps.core.models import Protein

beef = Protein.objects.create(name="Beef")
chicken = Protein.objects.create(name="Chicken")
```

### 2. StatusChoices Enum

**Purpose**: Standardized status values for entities across the application.

**Values**:
- `ACTIVE` ("active"): Entity is currently active
- `INACTIVE` ("inactive"): Entity is temporarily inactive
- `ARCHIVED` ("archived"): Entity is archived/deleted

**Usage Example**:
```python
from apps.core.models import StatusChoices

status = StatusChoices.ACTIVE
print(status.label)  # Output: "Active"
```

### 3. StatusModel (Abstract)

**Purpose**: Abstract base model providing status tracking functionality.

**Fields**:
- `status` (CharField): Current status using StatusChoices

**Features**:
- Default status is ACTIVE
- Uses StatusChoices enum for consistency
- Cannot be instantiated directly (abstract model)

**Usage Pattern**:
```python
from apps.core.models import StatusModel

class MyEntity(StatusModel):
    name = models.CharField(max_length=100)
    # Automatically has 'status' field
```

### 4. TimestampModel (Abstract)

**Purpose**: Abstract base model providing automatic timestamp tracking.

**Fields**:
- `created_on` (DateTimeField): Auto-set on creation
- `modified_on` (DateTimeField): Auto-updated on each save

**Features**:
- Automatic timestamp management
- No manual intervention required
- Immutable creation timestamp
- Cannot be instantiated directly (abstract model)

**Usage Pattern**:
```python
from apps.core.models import TimestampModel

class MyEntity(TimestampModel):
    name = models.CharField(max_length=100)
    # Automatically has 'created_on' and 'modified_on'
```

### 5. OwnedModel (Abstract)

**Purpose**: Abstract base model providing ownership and timestamp tracking.

**Inherits From**: TimestampModel

**Additional Fields**:
- `owner` (ForeignKey to User): Entity owner
- `created_by` (ForeignKey to User): User who created the entity
- `modified_by` (ForeignKey to User): User who last modified the entity

**Features**:
- All three foreign keys cascade on delete
- Automatic timestamp tracking (from TimestampModel)
- Dynamic related names using `%(class)s` pattern
- Help text for all ownership fields
- Cannot be instantiated directly (abstract model)

**Usage Pattern**:
```python
from apps.core.models import OwnedModel

class MyEntity(OwnedModel):
    name = models.CharField(max_length=100)
    # Automatically has:
    # - created_on, modified_on (from TimestampModel)
    # - owner, created_by, modified_by

entity = MyEntity.objects.create(
    name="Example",
    owner=user,
    created_by=user,
    modified_by=user
)

# Access related entities
user.myentity_created.all()   # Entities created by user
user.myentity_modified.all()  # Entities modified by user
```

## Design Patterns

### 1. Abstract Base Classes

Core models use Django's abstract base class pattern to provide reusable functionality without database tables:

- Promotes code reuse
- Ensures consistency across entities
- Reduces duplication
- No database overhead for abstract models

### 2. Composition Over Inheritance

Models can combine multiple abstract bases:

```python
class MyModel(StatusModel, TimestampModel):
    # Combines both status and timestamp functionality
    pass
```

### 3. Cascade Delete Protection

All ownership foreign keys use `CASCADE` delete to maintain referential integrity:

- When a user is deleted, their owned entities are also deleted
- Prevents orphaned records
- Enforces data consistency

### 4. Related Name Patterns

OwnedModel uses `%(class)s` in related names for dynamic naming:

```python
# For a model named ChatSession
user.chatsession_created.all()   # Sessions created by user
user.chatsession_modified.all()  # Sessions modified by user
```

## Integration Points

### Apps Using Core Models

**Direct Usage**:
- Protein model: Used by Suppliers and Customers apps

**StatusModel**:
- Used by various apps for entity status tracking

**TimestampModel**:
- Customers app (Customer model)
- Other entity models requiring timestamps

**OwnedModel**:
- AI Assistant app (ChatSession, ChatMessage)
- Accounts Receivables app
- Purchase Orders app
- Other multi-tenant entities

## Testing Coverage

Core models have >80% test coverage with comprehensive unit tests:

### Test Categories

1. **Model Creation Tests**
   - Basic creation and field validation
   - Unique constraints
   - Default values

2. **Field Behavior Tests**
   - Auto-timestamp functionality
   - Cascade delete behavior
   - Related name access

3. **Abstract Model Tests**
   - Field presence verification
   - Inheritance hierarchy validation
   - Help text and metadata

4. **Integration Tests**
   - Multiple model interaction
   - Cross-app usage patterns

**Current Coverage**: 84% overall, 100% for models.py

## Environment Configuration

The environment management system (`config/manage_env.py`) provides:

- Centralized configuration management
- Environment-specific settings (dev/staging/prod)
- Validation and error checking
- Secret generation utilities

### Core Environment Variables

**Backend Required**:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode flag
- `ALLOWED_HOSTS`: Allowed host names
- `DATABASE_URL`: Database connection string
- `CORS_ALLOWED_ORIGINS`: CORS whitelist
- `API_VERSION`: API version string

**Frontend Required**:
- `REACT_APP_API_BASE_URL`: Backend API URL
- `REACT_APP_ENVIRONMENT`: Environment name
- `REACT_APP_AI_ASSISTANT_ENABLED`: AI feature flag

**Optional Backend**:
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `EMAIL_HOST`: SMTP server
- `EMAIL_HOST_USER`: SMTP username
- `EMAIL_HOST_PASSWORD`: SMTP password

### Environment Setup Flow

```
┌──────────────────────────────────────────────────────┐
│  python config/manage_env.py setup <environment>     │
└───────────────────┬──────────────────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Load Environment    │
         │  Template Files      │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Generate Secrets    │
         │  (if needed)         │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Copy to Backend/    │
         │  Frontend Dirs       │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Validate Config     │
         │  Required Vars       │
         └──────────┬───────────┘
                    │
                    ▼
              ✓ Success
```

### Validation Flow

```
┌──────────────────────────────────────────┐
│  python config/manage_env.py validate    │
└───────────────┬──────────────────────────┘
                │
                ▼
     ┌──────────────────────┐
     │  Check Backend .env  │
     └──────────┬───────────┘
                │
                ├─── Missing vars? → ❌ FAIL
                ├─── Empty vars? → ⚠️  WARN
                │
                ▼
     ┌──────────────────────┐
     │ Check Frontend .env  │
     └──────────┬───────────┘
                │
                ├─── Missing vars? → ❌ FAIL
                ├─── Empty vars? → ⚠️  WARN
                │
                ▼
           ✓ Success
```

## Future Enhancements

1. **Additional Base Models**
   - AuditModel for change tracking
   - SoftDeleteModel for soft deletion
   - VersionedModel for version control

2. **Extended Protein Model**
   - Category field (Red Meat, Poultry, Seafood)
   - Metadata for nutritional info
   - Supplier-specific attributes

3. **Enhanced StatusModel**
   - Status transition validation
   - Status change history
   - Workflow integration

4. **Environment Management**
   - Auto-secret rotation
   - Environment diff tool
   - Configuration validation in CI/CD

## Best Practices

### When to Use Each Base Model

**StatusModel**:
- Entities with lifecycle states
- Soft-deletable entities
- Entities requiring active/inactive toggle

**TimestampModel**:
- All persistent entities
- Audit trail requirements
- Data change tracking

**OwnedModel**:
- Multi-tenant entities
- User-specific data
- Entities requiring permission checks
- Audit trail with user attribution

### Migration Patterns

When adding core model inheritance to existing models:

```python
# 1. Add the inheritance
class MyModel(OwnedModel):  # Add base class
    # existing fields...
    pass

# 2. Create migration
# python manage.py makemigrations

# 3. Update existing records
# Provide default values or data migration
```

## Maintenance

### Running Tests

```bash
# Core model tests
cd backend && python manage.py test apps.core

# With coverage
coverage run --source='apps.core' manage.py test apps.core
coverage report

# Environment management tests
cd config && python -m pytest test_manage_env.py -v
```

### Code Quality

- All models have 100% test coverage
- Comprehensive docstrings
- Type hints where applicable
- Follows Django best practices

## References

- [Django Abstract Base Classes](https://docs.djangoproject.com/en/stable/topics/db/models/#abstract-base-classes)
- [Django Model Field Reference](https://docs.djangoproject.com/en/stable/ref/models/fields/)
- [ProjectMeats Environment Guide](ENVIRONMENT_GUIDE.md)
- [ProjectMeats Testing Guide](../README.md#testing)
