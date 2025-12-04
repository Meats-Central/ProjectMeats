# Model Defaults Migration Guide

## Overview

This document provides instructions for generating and applying migrations after adding default values to all non-nullable fields across all Django apps in the ProjectMeats backend.

## Summary of Changes

All Django models have been audited and updated to include explicit default values for non-nullable fields without them. This prevents IntegrityErrors when creating objects through Django admin or API endpoints.

### Apps Modified (12 total)

1. **accounts_receivables** - 2 fields updated
2. **bug_reports** - 7 fields updated  
3. **carriers** - 13 fields updated
4. **contacts** - 5 fields updated
5. **customers** - 14 fields updated
6. **invoices** - 10 fields updated
7. **plants** - 7 fields updated
8. **products** - 5 fields updated
9. **purchase_orders** - 6 fields updated
10. **sales_orders** - 3 fields updated
11. **suppliers** - 16 fields updated
12. **tenants** - 1 field updated

### Total Fields Updated: 89

## Migration Generation Commands

After these model changes are merged, run the following commands to generate migrations:

```bash
cd backend

# Generate migrations for all modified apps
python manage.py makemigrations accounts_receivables
python manage.py makemigrations bug_reports
python manage.py makemigrations carriers
python manage.py makemigrations contacts
python manage.py makemigrations customers
python manage.py makemigrations invoices
python manage.py makemigrations plants
python manage.py makemigrations products
python manage.py makemigrations purchase_orders
python manage.py makemigrations sales_orders
python manage.py makemigrations suppliers
python manage.py makemigrations tenants

# Or generate all at once
python manage.py makemigrations
```

## Migration Application

### Local Development

```bash
cd backend
python manage.py migrate
```

### Dev Environment

```bash
# SSH into dev server or use deployment workflow
python manage.py migrate --settings=projectmeats.settings.development
```

### UAT Environment

```bash
# SSH into UAT server or use deployment workflow  
python manage.py migrate --settings=projectmeats.settings.staging
```

### Production Environment

```bash
# Through CI/CD workflow with approvals
python manage.py migrate --settings=projectmeats.settings.production
```

## Types of Defaults Added

### CharField/TextField/EmailField with blank=True
- **Default value:** `default=''` (empty string)
- **Rationale:** Django CharField with blank=True should explicitly default to empty string to prevent None values

### DecimalField (non-nullable)
- **Default value:** `default=Decimal('0.00')`
- **Rationale:** Prevents IntegrityError for required decimal fields like amounts
- **Import added:** `from decimal import Decimal`

### BooleanField
- **Default value:** `default=False` or `default=True` (as appropriate)
- **Rationale:** Boolean fields should always have an explicit default

## Example Changes

### Before:
```python
accounting_payment_terms = models.CharField(
    max_length=50,
    choices=AccountingPaymentTermsChoices.choices,
    blank=True,
    help_text="Payment terms (e.g., Wire, ACH, Check)",
)
```

### After:
```python
accounting_payment_terms = models.CharField(
    max_length=50,
    choices=AccountingPaymentTermsChoices.choices,
    blank=True,
    default='',
    help_text="Payment terms (e.g., Wire, ACH, Check)",
)
```

### For DecimalField:
```python
# Before
total_amount = models.DecimalField(
    max_digits=10, decimal_places=2, help_text="Total order amount"
)

# After (with import added)
from decimal import Decimal

total_amount = models.DecimalField(
    max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Total order amount"
)
```

## Verification Steps

### 1. After Generating Migrations

```bash
# Review generated migration files
ls -la backend/apps/*/migrations/
```

### 2. Check Migration Plans

```bash
# See what migrations will be applied
python manage.py showmigrations
```

### 3. Test Locally

```bash
# Apply migrations locally
python manage.py migrate

# Test creating objects through admin
python manage.py runserver
# Navigate to http://localhost:8000/admin/
# Try creating objects in each modified app
```

### 4. Verify in Django Shell

```bash
python manage.py shell

# Test creating objects programmatically
from apps.suppliers.models import Supplier
s = Supplier(name="Test Supplier")
s.save()  # Should not raise IntegrityError

# Check default values
print(s.street_address)  # Should be ''
print(s.accounting_payment_terms)  # Should be ''
```

## Expected Migration Behavior

### For CharField/TextField/EmailField:
- Migrations will likely be **empty** or very small
- Adding `default=''` to CharField(blank=True) is typically a no-op at the database level
- Django handles this at the application layer

### For DecimalField:
- Migrations may include ALTER TABLE commands
- Existing NULL values (if any) will be converted to default values
- **Note:** Ensure no existing data will be adversely affected

### For Non-Blank Fields with Defaults:
- More significant migrations may be generated
- Review carefully before applying to production

## Rollback Plan

If migrations cause issues:

```bash
# Rollback to previous migration
python manage.py migrate app_name previous_migration_name

# Example
python manage.py migrate suppliers 0004_supplier_account_line_of_credit_and_more
```

## Testing Checklist

After applying migrations in each environment:

- [ ] All migrations applied successfully
- [ ] No migration warnings or errors
- [ ] Can create new objects through admin without IntegrityError
- [ ] Can create new objects through API without IntegrityError  
- [ ] Existing objects still load correctly
- [ ] All serializers handle new defaults properly
- [ ] All admin forms display correctly
- [ ] No data loss or corruption

## Detailed Field Changes by App

### suppliers (16 fields)
- street_address, edible_inedible, type_of_plant, type_of_certificate
- origin, country_origin, shipping_offered, how_to_book_pickup
- accounting_payment_terms, credit_limits, account_line_of_credit
- fresh_or_frozen, package_type, net_or_catch, departments
- accounting_terms, accounting_line_of_credit

### customers (14 fields)
- street_address, edible_inedible, type_of_plant
- purchasing_preference_origin, industry
- accounting_payment_terms, credit_limits, account_line_of_credit
- buyer_contact_name, buyer_contact_phone, buyer_contact_email
- type_of_certificate, accounting_terms, accounting_line_of_credit

### contacts (5 fields)
- contact_type, contact_title, main_phone, direct_phone, cell_phone

### carriers (13 fields)
- contact_person, phone, email, address, city, state, zip_code
- mc_number, dot_number, insurance_provider, insurance_policy_number, notes
- my_customer_num_from_carrier, accounting_payable_contact_name
- accounting_payable_contact_phone, accounting_payable_contact_email
- sales_contact_name, sales_contact_phone, sales_contact_email
- accounting_payment_terms, credit_limits, account_line_of_credit
- departments, how_carrier_make_appointment

### plants (7 fields)
- plant_est_num, address, city, state, zip_code, phone, email, manager

### products (5 fields)
- type_of_protein, fresh_or_frozen, package_type, net_or_catch, edible_or_inedible

### purchase_orders (6 fields)
- total_amount (DecimalField), our_purchase_order_num
- supplier_confirmation_order_num, carrier_release_format
- carrier_release_num, how_carrier_make_appointment

### sales_orders (3 fields)
- delivery_po_num, carrier_release_num, notes

### invoices (10 fields)
- our_sales_order_num, delivery_po_num
- accounting_payable_contact_name, accounting_payable_contact_phone
- accounting_payable_contact_email, type_of_protein
- description_of_product_item, edible_or_inedible
- total_amount (DecimalField), notes

### bug_reports (7 fields)
- reporter_email, browser, os, screen_resolution, url
- steps_to_reproduce, expected_behavior, actual_behavior

### tenants (1 field)
- contact_phone

### accounts_receivables (2 fields)
- amount (DecimalField), description

## Notes

1. **Backward Compatibility:** All changes are backward compatible. Existing data is preserved.

2. **No Breaking Changes:** Adding defaults to CharField with blank=True does not break existing functionality.

3. **API Impact:** Serializers may need to be updated if they expect None values instead of empty strings. Review serializers after migration.

4. **Admin Impact:** Admin forms will now show empty strings instead of None for blank fields. This is the desired behavior.

5. **Data Integrity:** These changes **improve** data integrity by ensuring consistent default values.

## Support

If you encounter issues during migration:

1. Check migration files for unexpected changes
2. Review database logs for errors
3. Test in local environment first
4. Use migration rollback if necessary
5. Contact development team for assistance

## Completion Checklist

- [ ] All model changes reviewed and approved
- [ ] Migrations generated for all 12 apps
- [ ] Migrations applied and tested locally
- [ ] Migrations applied and tested on dev
- [ ] All admin forms tested for creating objects
- [ ] All API endpoints tested for creating objects
- [ ] Migrations applied and tested on UAT
- [ ] Production deployment approved and scheduled
- [ ] Migrations applied to production
- [ ] Post-deployment verification complete
