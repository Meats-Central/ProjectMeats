# PostgreSQL Row-Level Security (RLS) Implementation Guide

## Overview

This document describes the implementation of PostgreSQL Row-Level Security (RLS) for tenant isolation in ProjectMeats. RLS provides database-level enforcement of tenant isolation as an additional security layer beyond Django ORM filtering.

## Architecture

### Current State
- **Multi-tenancy Model**: Shared schema with tenant_id foreign keys
- **Middleware**: `TenantMiddleware` sets `request.tenant` from domain/header/user
- **Isolation Method**: Django ORM filtering with `queryset.filter(tenant=request.tenant)`

### Enhanced with RLS
- **Session Variable**: Middleware sets PostgreSQL session variable `app.current_tenant_id`
- **Database Policies**: RLS policies enforce tenant isolation at the database level
- **Defense in Depth**: Provides protection even if Django filtering is accidentally omitted

## Implementation Steps

### 1. Middleware Enhancement ✓ COMPLETED

The `TenantMiddleware` has been updated to set the PostgreSQL session variable:

```python
# In apps/tenants/middleware.py
if tenant:
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, false)",
                [str(tenant.id)]
            )
    except Exception as e:
        logger.warning(f"Failed to set PostgreSQL session variable: {e}")
```

### 2. Add Tenant Fields to Models (REQUIRED)

**Status**: NOT YET IMPLEMENTED

Before enabling RLS, all tenant-isolated models must have a `tenant` ForeignKey:

```python
# Example: PurchaseOrder model
class PurchaseOrder(TimestampModel):
    # Add tenant field
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        help_text="Tenant that owns this purchase order"
    )
    
    # ... rest of fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'order_date']),
        ]
```

**Required Migration**:
```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('purchase_orders', '0001_initial'),
        ('tenants', '0001_initial'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='tenant',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                to='tenants.Tenant',
                help_text="Tenant that owns this purchase order"
            ),
        ),
        migrations.AddIndex(
            model_name='purchaseorder',
            index=models.Index(fields=['tenant', 'order_date']),
        ),
    ]
```

### 3. Enable RLS and Create Policies

**Status**: PENDING (requires tenant fields first)

Once tenant fields are added, create a migration to enable RLS:

```python
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('purchase_orders', '0002_add_tenant_field'),
    ]
    
    operations = [
        migrations.RunSQL(
            sql="""
                -- Enable Row-Level Security
                ALTER TABLE tenant_apps_purchase_orders_purchaseorder 
                ENABLE ROW LEVEL SECURITY;
                
                -- Policy for SELECT: Users can only see their tenant's records
                CREATE POLICY tenant_isolation_select 
                ON tenant_apps_purchase_orders_purchaseorder
                FOR SELECT
                USING (
                    tenant_id::text = current_setting('app.current_tenant_id', true)
                    OR current_setting('app.current_tenant_id', true) IS NULL
                );
                
                -- Policy for INSERT: Can only insert into own tenant
                CREATE POLICY tenant_isolation_insert 
                ON tenant_apps_purchase_orders_purchaseorder
                FOR INSERT
                WITH CHECK (
                    tenant_id::text = current_setting('app.current_tenant_id', true)
                );
                
                -- Policy for UPDATE: Can only update own tenant's records
                CREATE POLICY tenant_isolation_update 
                ON tenant_apps_purchase_orders_purchaseorder
                FOR UPDATE
                USING (
                    tenant_id::text = current_setting('app.current_tenant_id', true)
                )
                WITH CHECK (
                    tenant_id::text = current_setting('app.current_tenant_id', true)
                );
                
                -- Policy for DELETE: Can only delete own tenant's records
                CREATE POLICY tenant_isolation_delete 
                ON tenant_apps_purchase_orders_purchaseorder
                FOR DELETE
                USING (
                    tenant_id::text = current_setting('app.current_tenant_id', true)
                );
            """,
            reverse_sql="""
                DROP POLICY IF EXISTS tenant_isolation_select 
                ON tenant_apps_purchase_orders_purchaseorder;
                
                DROP POLICY IF EXISTS tenant_isolation_insert 
                ON tenant_apps_purchase_orders_purchaseorder;
                
                DROP POLICY IF EXISTS tenant_isolation_update 
                ON tenant_apps_purchase_orders_purchaseorder;
                
                DROP POLICY IF EXISTS tenant_isolation_delete 
                ON tenant_apps_purchase_orders_purchaseorder;
                
                ALTER TABLE tenant_apps_purchase_orders_purchaseorder 
                DISABLE ROW LEVEL SECURITY;
            """,
        ),
    ]
```

### 4. Create RLS Tests

**Status**: PENDING

Create tests to verify RLS enforcement:

```python
# backend/apps/tenants/tests/test_rls.py
from django.test import TestCase
from django.db import connection
from apps.tenants.models import Tenant
from tenant_apps.purchase_orders.models import PurchaseOrder

class RLSTestCase(TestCase):
    """Test Row-Level Security enforcement."""
    
    def setUp(self):
        self.tenant1 = Tenant.objects.create(name="Tenant 1", slug="tenant1")
        self.tenant2 = Tenant.objects.create(name="Tenant 2", slug="tenant2")
        
        # Create purchase orders for each tenant
        self.po1 = PurchaseOrder.objects.create(
            tenant=self.tenant1,
            order_number="PO-001",
            # ... other fields
        )
        self.po2 = PurchaseOrder.objects.create(
            tenant=self.tenant2,
            order_number="PO-002",
            # ... other fields
        )
    
    def test_rls_isolation(self):
        """Test that RLS prevents cross-tenant data access."""
        # Set session variable for tenant1
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, false)",
                [str(self.tenant1.id)]
            )
        
        # Query should only return tenant1's purchase orders
        pos = PurchaseOrder.objects.all()
        self.assertEqual(pos.count(), 1)
        self.assertEqual(pos.first().id, self.po1.id)
        
        # Switch to tenant2
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, false)",
                [str(self.tenant2.id)]
            )
        
        # Query should only return tenant2's purchase orders
        pos = PurchaseOrder.objects.all()
        self.assertEqual(pos.count(), 1)
        self.assertEqual(pos.first().id, self.po2.id)
    
    def test_rls_insert_enforcement(self):
        """Test that RLS prevents inserting into wrong tenant."""
        # Set session variable for tenant1
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, false)",
                [str(self.tenant1.id)]
            )
        
        # Try to create PO for tenant2 (should fail with RLS)
        with self.assertRaises(Exception):
            PurchaseOrder.objects.create(
                tenant=self.tenant2,
                order_number="PO-003",
                # ... other fields
            )
    
    def test_rls_without_django_filter(self):
        """Test that RLS protects even without Django filtering."""
        # Set session variable for tenant1
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, false)",
                [str(self.tenant1.id)]
            )
        
        # Direct SQL query (bypassing Django ORM filtering)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM tenant_apps_purchase_orders_purchaseorder"
            )
            count = cursor.fetchone()[0]
        
        # Should only see tenant1's records
        self.assertEqual(count, 1)
```

## Benefits of RLS

1. **Defense in Depth**: Protects against accidental omission of tenant filters
2. **Database-Level Enforcement**: Works even with raw SQL queries
3. **Audit Compliance**: Provides verifiable tenant isolation at the database level
4. **Zero-Trust Architecture**: Each database connection is scoped to a specific tenant

## Rollout Strategy

### Phase 1: Preparation ✓
- [x] Update middleware to set PostgreSQL session variables
- [x] Document RLS implementation approach

### Phase 2: Model Migration (TODO)
- [ ] Add tenant ForeignKey to all business models
- [ ] Create data migration to backfill tenant_id for existing records
- [ ] Update ViewSets to enforce tenant on create/update

### Phase 3: RLS Enablement (TODO)
- [ ] Create migrations to enable RLS on each table
- [ ] Create comprehensive test suite for RLS
- [ ] Test in staging environment
- [ ] Monitor query performance impact

### Phase 4: Production Deployment (TODO)
- [ ] Deploy to production with feature flag
- [ ] Monitor logs for RLS policy violations
- [ ] Gradually enable RLS on all tables
- [ ] Document operational procedures

## Performance Considerations

1. **Index Optimization**: Ensure indexes on (tenant_id, ...) for all queries
2. **Session Variable Overhead**: Minimal (set once per request)
3. **Policy Evaluation**: PostgreSQL evaluates policies efficiently
4. **Query Planning**: No significant impact on query plans

## Maintenance

### Adding RLS to New Models

When creating new tenant-isolated models:

1. Add tenant ForeignKey to model
2. Create migration to enable RLS
3. Add RLS tests
4. Update documentation

### Monitoring

Monitor PostgreSQL logs for:
- RLS policy violations
- Performance degradation
- Unexpected access patterns

## References

- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Django Multi-tenancy Patterns](https://docs.djangoproject.com/en/stable/topics/db/multi-db/)
- ProjectMeats Architecture: `docs/ARCHITECTURE.md`

## Next Steps

1. **Add tenant fields to models** - Create migrations for all business models
2. **Backfill data** - Ensure existing records have tenant_id
3. **Enable RLS** - Create RLS migrations for each table
4. **Test thoroughly** - Comprehensive test coverage for RLS
5. **Deploy gradually** - Roll out RLS table by table
