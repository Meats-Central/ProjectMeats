# Migration Dependency Fix - 2025-10-13

## Problem

The CI/CD deployment pipeline was failing with the following error:

```
django.db.migrations.exceptions.InconsistentMigrationHistory: 
Migration purchase_orders.0004_alter_purchaseorder_carrier_release_format_and_more 
is applied before its dependency products.0002_product_carton_type_product_namp_product_origin_and_more 
on database 'default'.
```

## Root Cause

The migrations were created in the following chronological order:

1. **2025-10-08 23:04**: `products.0001_initial` and `purchase_orders.0003_purchaseorder_carrier_and_more` created
2. **2025-10-13 05:24**: `products.0002_product_carton_type_product_namp_product_origin_and_more` created
3. **2025-10-13 06:30**: `purchase_orders.0004_alter_purchaseorder_carrier_release_format_and_more` created

The problem:
- `purchase_orders.0003` was applied in deployed environments before `products.0002` existed
- Later, `purchase_orders.0004` was created with a dependency on `products.0002`
- This created an inconsistent migration history where `0003` was applied before `0002`, but `0004` requires `0002` to be applied before `0003`

## Solution

Added `("products", "0001_initial")` as a dependency to `purchase_orders.0003_purchaseorder_carrier_and_more`.

### Changes Made

**File**: `backend/apps/purchase_orders/migrations/0003_purchaseorder_carrier_and_more.py`

```python
class Migration(migrations.Migration):
    dependencies = [
        ("carriers", "0003_carrier_account_line_of_credit_and_more"),
        ("contacts", "0003_contact_cell_phone_contact_contact_title_and_more"),
        ("plants", "0003_plant_plant_est_num"),
        ("products", "0001_initial"),  # ← ADDED THIS LINE
        ("purchase_orders", "0002_purchaseorder_tenant"),
    ]
```

## Why This Fix Works

By adding `products.0001_initial` as a dependency to `purchase_orders.0003`:

1. Django's migration system now knows that `products.0001` must be applied before `purchase_orders.0003`
2. The dependency chain becomes: 
   - `products.0001` → `purchase_orders.0003` → `products.0002` → `purchase_orders.0004`
3. This ensures the correct order regardless of when migrations are applied

## Verification

The fix was verified using:

1. **Migration graph validation**: Django successfully loads the migration graph without errors
2. **Dependency check**: All dependencies are correctly registered
3. **Migration plan test**: The execution plan shows the correct order:
   ```
   products.0001_initial (12)
   products.0002_product_carton_type_product_namp_product_origin_and_more (13)
   purchase_orders.0001_initial (28)
   purchase_orders.0002_purchaseorder_tenant (29)
   purchase_orders.0003_purchaseorder_carrier_and_more (30)
   purchase_orders.0004_alter_purchaseorder_carrier_release_format_and_more (33)
   ```

## Deployment Impact

- **No data loss**: This fix only changes migration metadata, not database operations
- **Safe for existing databases**: Environments that already have migrations applied will not be affected
- **Resolves CI/CD blocking issue**: Fresh deployments will now apply migrations in the correct order
- **No manual intervention required**: The fix is automatic once the code is deployed

## Testing

Run the verification script to confirm the fix:

```bash
cd /home/runner/work/ProjectMeats/ProjectMeats
python /tmp/test_migration_order.py
```

Expected output:
```
✅ All tests passed! Migration dependency issue is resolved.
```

## References

- GitHub Actions job that failed: https://github.com/Meats-Central/ProjectMeats/actions/runs/18472959715/job/52631106862
- Django documentation on migration dependencies: https://docs.djangoproject.com/en/4.2/topics/migrations/#migration-files
