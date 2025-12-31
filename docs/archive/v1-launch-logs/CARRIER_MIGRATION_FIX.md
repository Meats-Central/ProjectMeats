# Carrier Migration Fix - SeparateDatabaseAndState Pattern

## Problem
The carrier migration (`0002_carrier_tenant_and_more.py`) had a critical issue where Django's internal state (what it thinks the database looks like) was not properly decoupled from the actual database operations.

**Original Issue:**
```python
operations = [
    # Step 1: Raw SQL adds tenant_id column
    migrations.RunPython(add_tenant_field_if_not_exists, ...),
    
    # Step 2: Django tries to ADD the field again (FAILS if column exists!)
    migrations.AddField(model_name='carrier', name='tenant', ...),
    
    # Step 3: Add index
    migrations.AddIndex(...)
]
```

**Problem:** If the column already exists in the database (from a previous migration attempt or manual fix), the `AddField` operation would fail because Django doesn't know the column already exists.

## Solution: SeparateDatabaseAndState

Use Django's `SeparateDatabaseAndState` to decouple:
1. **State Operations** - Tell Django's migration system the field exists (for model validation)
2. **Database Operations** - Actually create the column in the database (idempotently)

### Fixed Migration Pattern

```python
operations = [
    migrations.SeparateDatabaseAndState(
        state_operations=[
            # Update Django's internal model state
            migrations.AddField(
                model_name='carrier',
                name='tenant',
                field=models.ForeignKey(...),
                preserve_default=False,
            ),
        ],
        database_operations=[
            # Idempotent SQL that checks if column exists
            migrations.RunPython(add_tenant_field_if_not_exists, ...),
        ],
    ),
    
    # Index creation (safe after ensuring column exists)
    migrations.AddIndex(
        model_name="carrier",
        index=models.Index(fields=["tenant", "name"], ...),
    ),
]
```

## How It Works

### State Operations (Django's Mental Model)
- Runs **first** to update Django's migration state
- Tells Django: "The `tenant` field exists on the `Carrier` model"
- Enables model validation, ORM queries, and admin integration
- **Does NOT touch the database**

### Database Operations (Actual SQL)
- Runs **second** to modify the actual database
- Uses idempotent SQL that checks if column exists before adding
- Safe to run multiple times (no-op if column already exists)
- Handles both fresh databases and existing production databases

## Why This Matters

### Without SeparateDatabaseAndState
```
❌ Migration applied previously (column exists in DB)
❌ Django re-runs migration
❌ Raw SQL: "Column exists? Skip." ✓
❌ AddField: "Adding column..." ✗ ERROR: column already exists
```

### With SeparateDatabaseAndState
```
✅ Migration applied previously (column exists in DB)
✅ Django re-runs migration
✅ State: "Update model registry" ✓
✅ Database: "Column exists? Skip." ✓
✅ Result: Idempotent, no errors
```

## Testing Results

### First Run (Fresh Database)
```bash
python manage.py migrate carriers
# Output:
# Applying carriers.0001_initial... OK (0.055s)
# Applying carriers.0002_carrier_tenant_and_more... OK (0.070s)
```

### Second Run (Already Applied)
```bash
python manage.py migrate carriers
# Output:
# No migrations to apply.
```

### Database Schema Verification
```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'carriers_carrier' AND column_name = 'tenant_id';

-- Result:
-- tenant_id | uuid | YES
```

### Index Verification
```sql
SELECT indexname FROM pg_indexes WHERE tablename = 'carriers_carrier';

-- Result includes:
-- carriers_ca_tenant__8e23de_idx
```

## Benefits

1. ✅ **Idempotent** - Safe to run multiple times
2. ✅ **State-Aware** - Django knows about the field for ORM operations
3. ✅ **Database-Safe** - Won't fail if column already exists
4. ✅ **Production-Ready** - Handles existing databases gracefully
5. ✅ **No Manual Intervention** - Automatic detection and handling

## Deployment

### Development/UAT/Production
```bash
cd backend
python manage.py migrate --fake-initial --noinput
```

**Expected Behavior:**
- Fresh database: Creates table → Adds tenant_id → Adds index
- Existing database without tenant_id: Adds tenant_id → Adds index
- Existing database with tenant_id: No-op (skips gracefully)

## Related Files
- `backend/tenant_apps/carriers/migrations/0002_carrier_tenant_and_more.py` - Fixed migration
- `backend/tenant_apps/carriers/models.py` - Carrier model with tenant ForeignKey

## Key Takeaways

### When to Use SeparateDatabaseAndState
Use this pattern when:
- Adding fields to existing tables in production
- Dealing with idempotent migrations
- Managing state vs. database inconsistencies
- Migrating legacy databases

### Pattern Template
```python
migrations.SeparateDatabaseAndState(
    state_operations=[
        # What Django thinks happened
        migrations.AddField(...)
    ],
    database_operations=[
        # What actually happens in the database
        migrations.RunPython(idempotent_function, ...)
    ],
)
```

## Django Documentation
- [SeparateDatabaseAndState](https://docs.djangoproject.com/en/5.0/ref/migration-operations/#separatedatabaseandstate)
- [Custom Migration Operations](https://docs.djangoproject.com/en/5.0/howto/writing-migrations/#data-migrations)

## Next Steps
This pattern should be applied to other tenant field migrations:
- `accounts_receivables/migrations/0003_*.py`
- `bug_reports/migrations/0003_*.py`
- `invoices/migrations/0003_*.py`
- `plants/migrations/0003_*.py`
- `products/migrations/0003_*.py`
- `purchase_orders/migrations/0003_*.py`
- `sales_orders/migrations/0003_*.py`

All should follow this same decoupled state/database pattern for production safety.
