# Products Implementation Guide

**Status**: ✅ Backend Complete (Step 1-2)  
**Date**: January 10, 2026  
**Branch**: `feature/products-supplier-customer-m2m`

---

## 🎯 Overview

Implemented Product model with Many-to-Many relationships to Suppliers and Customers, enabling:
- **Product catalog management** (tenant-scoped)
- **Supplier-product associations** (M2M)
- **Customer-product associations** (M2M)
- **Filtered product lists** by supplier/customer
- **Nested endpoints** for filtered queries

---

## 🏗️ Architecture

### Shared-Schema Multi-Tenancy Pattern

```
Product (tenant_id) ←→ M2M ←→ Supplier (tenant_id)
                    ←→ M2M ←→ Customer (tenant_id)
```

**Key Principles:**
- All models have `tenant` ForeignKey
- Querysets filtered by `request.tenant`
- Standard Django migrations (NOT django-tenants)
- TenantManager for `.for_tenant()` queries

---

## 📋 Implementation Details

### Step 1: Database Models ✅

#### Product Model
**File**: `backend/tenant_apps/products/models.py`

**Key Fields:**
- `tenant` - ForeignKey to Tenant (REQUIRED for isolation)
- `product_code` - CharField (unique, indexed)
- `description_of_product_item` - TextField
- `supplier` - ForeignKey to Supplier (renamed to `supplied_products`)
- `type_of_protein`, `fresh_or_frozen`, `package_type` (choices)
- `unit_weight`, `is_active` (business logic)

**Manager**: Uses `TenantManager()` for `.for_tenant()` support

#### Supplier Model (Updated)
**File**: `backend/tenant_apps/suppliers/models.py`

**Added Field:**
```python
products = models.ManyToManyField(
    'products.Product',
    related_name="suppliers",
    blank=True,
    help_text="Products available from this supplier",
)
```

**Migration**: `0007_add_products_m2m.py`

#### Customer Model (Updated)
**File**: `backend/tenant_apps/customers/models.py`

**Added Field:**
```python
products = models.ManyToManyField(
    'products.Product',
    related_name="customers",
    blank=True,
    help_text="Products associated with this customer",
)
```

**Migration**: `0006_add_products_m2m.py`

---

### Step 2: API Endpoints ✅

#### ProductViewSet
**File**: `backend/tenant_apps/products/views.py`

**Endpoints:**
- `GET /api/v1/products/` - List all tenant products
- `POST /api/v1/products/` - Create product (auto-sets tenant)
- `GET /api/v1/products/{id}/` - Retrieve product details
- `PATCH /api/v1/products/{id}/` - Update product
- `DELETE /api/v1/products/{id}/` - Delete product

**Filtering:**
- `?supplier={id}` - Filter by supplier
- `?customer={id}` - Filter by customer (via M2M)
- `?type_of_protein=Beef` - Filter by protein type
- `?is_active=true` - Filter active products
- `?search=chicken` - Full-text search (code, description, supplier_item_number)

**Example Query:**
```bash
GET /api/v1/products/?supplier=abc-123&type_of_protein=Beef
```

#### Nested Supplier Endpoints
**File**: `backend/tenant_apps/suppliers/views.py`

**Added Action:**
```python
@action(detail=True, methods=['get'], url_path='products')
def products(self, request, pk=None):
    # Returns products associated with this supplier
```

**Endpoint:**
- `GET /api/v1/suppliers/{id}/products/` - List supplier's products

**Example:**
```bash
GET /api/v1/suppliers/abc-123/products/
# Returns: All products where supplier.products.filter(tenant=request.tenant)
```

#### Nested Customer Endpoints
**File**: `backend/tenant_apps/customers/views.py`

**Added Action:**
```python
@action(detail=True, methods=['get'], url_path='products')
def products(self, request, pk=None):
    # Returns products associated with this customer
```

**Endpoint:**
- `GET /api/v1/customers/{id}/products/` - List customer's products

**Example:**
```bash
GET /api/v1/customers/xyz-789/products/
# Returns: All products where customer.products.filter(tenant=request.tenant)
```

---

## 🔒 Security & Tenant Isolation

### Enforced at Multiple Levels

1. **Middleware**: `TenantMiddleware` sets `request.tenant` from:
   - `X-Tenant-ID` header
   - Domain match (TenantDomain)
   - Authenticated user's default tenant

2. **ViewSet**: `get_queryset()` filters by tenant:
   ```python
   def get_queryset(self):
       return super().get_queryset().filter(tenant=self.request.tenant)
   ```

3. **Creation**: `perform_create()` auto-assigns tenant:
   ```python
   def perform_create(self, serializer):
       serializer.save(tenant=self.request.tenant)
   ```

4. **Serializer**: `tenant` field is read-only:
   ```python
   read_only_fields = ["id", "tenant", "created_on", "modified_on"]
   ```

### Test Isolation
```bash
# User A (tenant_1) creates product
POST /api/v1/products/
{"product_code": "BEEF-001", "description": "Ribeye"}
# Returns: {"id": "abc", "tenant": "tenant_1", ...}

# User B (tenant_2) tries to access
GET /api/v1/products/abc/
# Returns: 404 (tenant filter blocks access)
```

---

## 🧪 Testing Procedures

### 1. Migrate Locally
```bash
cd /workspaces/ProjectMeats/backend
python manage.py migrate --fake-initial --noinput
```

### 2. Create Test Data
```bash
python manage.py shell
```

```python
from apps.tenants.models import Tenant
from tenant_apps.suppliers.models import Supplier
from tenant_apps.customers.models import Customer
from tenant_apps.products.models import Product

# Get tenant
tenant = Tenant.objects.first()

# Create supplier
supplier = Supplier.objects.create(
    tenant=tenant,
    name="Premium Beef Co",
    email="contact@premiumbeef.com"
)

# Create customer
customer = Customer.objects.create(
    tenant=tenant,
    name="Restaurant Group Inc",
    email="orders@restaurantgroup.com"
)

# Create products
product1 = Product.objects.create(
    tenant=tenant,
    product_code="BEEF-001",
    description_of_product_item="Ribeye Steak, Choice Grade",
    type_of_protein="Beef",
    fresh_or_frozen="Fresh",
    unit_weight=12.50,
    supplier=supplier
)

product2 = Product.objects.create(
    tenant=tenant,
    product_code="BEEF-002",
    description_of_product_item="Ground Beef, 80/20",
    type_of_protein="Beef",
    fresh_or_frozen="Fresh",
    unit_weight=10.00,
    supplier=supplier
)

# Associate products with supplier (M2M)
supplier.products.add(product1, product2)

# Associate products with customer (M2M)
customer.products.add(product1)

print(f"✓ Created {Product.objects.filter(tenant=tenant).count()} products")
print(f"✓ Supplier has {supplier.products.count()} products")
print(f"✓ Customer has {customer.products.count()} products")
```

### 3. Test API Endpoints
```bash
# Get all products (requires authentication + tenant header)
curl -H "X-Tenant-ID: {tenant_id}" \
     -H "Authorization: Token {token}" \
     http://localhost:8000/api/v1/products/

# Filter by supplier
curl -H "X-Tenant-ID: {tenant_id}" \
     -H "Authorization: Token {token}" \
     http://localhost:8000/api/v1/products/?supplier={supplier_id}

# Get supplier's products (nested endpoint)
curl -H "X-Tenant-ID: {tenant_id}" \
     -H "Authorization: Token {token}" \
     http://localhost:8000/api/v1/suppliers/{supplier_id}/products/

# Get customer's products (nested endpoint)
curl -H "X-Tenant-ID: {tenant_id}" \
     -H "Authorization: Token {token}" \
     http://localhost:8000/api/v1/customers/{customer_id}/products/
```

---

## 📊 Database Migrations

### Created Migrations

1. **`products/0005_add_products_m2m.py`**
   - Renames `Product.supplier` related_name to `supplied_products`
   - Prevents clash with new M2M field

2. **`suppliers/0007_add_products_m2m.py`**
   - Adds `Supplier.products` M2M field
   - Creates junction table: `suppliers_supplier_products`

3. **`customers/0006_add_products_m2m.py`**
   - Adds `Customer.products` M2M field
   - Creates junction table: `customers_customer_products`

### Migration Safety

✅ **Idempotent**: Safe to run with `--fake-initial`  
✅ **Backward Compatible**: No data loss  
✅ **Reversible**: Can be rolled back  
✅ **Tested Locally**: Applied successfully in dev environment

### Deployment Commands
```bash
# CI/CD pipeline (already configured in reusable-deploy.yml)
python manage.py migrate --fake-initial --noinput
```

---

## 🚀 Next Steps (Frontend Implementation)

### Step 3: Frontend Products Subpages
**Files to Create:**
- `frontend/src/pages/Suppliers/Products.tsx`
- `frontend/src/pages/Customers/Products.tsx`

**Features:**
- Nested routes: `/suppliers/:id/products` and `/customers/:id/products`
- Use `ResponsiveTable` component
- Fetch from nested endpoints: `apiClient.get(\`suppliers/\${id}/products/\`)`
- '+ New Product' button opens `CreateProductModal`
- Empty state: "No products associated – add one!"

### Step 4: Multi-Select Products in Forms
**Files to Update:**
- `frontend/src/pages/Suppliers/CreateSupplierModal.tsx`
- `frontend/src/pages/Suppliers/EditSupplierModal.tsx`
- `frontend/src/pages/Customers/CreateCustomerModal.tsx`
- `frontend/src/pages/Customers/EditCustomerModal.tsx`

**Features:**
- Add "Products" field with `SearchableSelect` (multi-select)
- Fetch all tenant products: `apiClient.get('/products/')`
- Pre-populate with existing associations on edit
- On submit: Include `product_ids` array in payload

### Step 5: Filter Product Dropdown in Orders
**Files to Update:**
- `frontend/src/pages/SalesOrders/CreateSalesOrderModal.tsx`
- `frontend/src/pages/PurchaseOrders/CreatePurchaseOrderModal.tsx`

**Features:**
- On Customer/Supplier select: Refetch products filtered by selected ID
- Product dropdown: `apiClient.get(\`products/?customer=\${customerId}\`)`
- Fallback: Show all tenant products if no selection
- Use TanStack Query for reactive updates

---

## 📝 Files Modified

### Backend Files (7 files)

1. **`tenant_apps/products/models.py`** (+1, -1 lines)
   - Renamed `supplier` related_name to `supplied_products`

2. **`tenant_apps/products/serializers.py`** (+11, -5 lines)
   - Added `supplier_name` read-only field
   - Made `tenant` read-only
   - Added `product_code` and `description_of_product_item` as required

3. **`tenant_apps/products/views.py`** (+49, -3 lines)
   - Created `ProductViewSet` with tenant filtering
   - Added DjangoFilterBackend for filtering
   - Custom filtering for M2M relationships

4. **`tenant_apps/products/urls.py`** (+6, -4 lines)
   - Registered `ProductViewSet` router

5. **`tenant_apps/suppliers/models.py`** (+5, 0 lines)
   - Added `products` M2M field

6. **`tenant_apps/suppliers/serializers.py`** (+1, 0 lines)
   - Added `products` to fields list

7. **`tenant_apps/suppliers/views.py`** (+19, +1 lines)
   - Added `@action` import
   - Added `products()` action endpoint

8. **`tenant_apps/customers/models.py`** (+5, 0 lines)
   - Added `products` M2M field

9. **`tenant_apps/customers/serializers.py`** (+1, 0 lines)
   - Added `products` to fields list

10. **`tenant_apps/customers/views.py`** (+19, +1 lines)
    - Added `@action` import
    - Added `products()` action endpoint

### Migrations (3 files)

1. **`products/migrations/0005_add_products_m2m.py`**
   - AlterField: `Product.supplier` related_name

2. **`suppliers/migrations/0007_add_products_m2m.py`**
   - AddField: `Supplier.products` M2M

3. **`customers/migrations/0006_add_products_m2m.py`**
   - AddField: `Customer.products` M2M

---

## ✅ Success Criteria

### Backend (Completed)
- [x] Product model with tenant isolation
- [x] M2M relationships to Supplier and Customer
- [x] ProductViewSet with filtering
- [x] Nested endpoints for supplier/customer products
- [x] Migrations applied successfully
- [x] API endpoints tested and working

### Frontend (Pending)
- [ ] Products subpages under Suppliers/Customers
- [ ] Multi-select products in Supplier/Customer forms
- [ ] Filtered product dropdown in Sales/Purchase Orders
- [ ] Create/Edit product modals
- [ ] Empty states and loading indicators

### Deployment (Pending)
- [ ] Merge to development branch
- [ ] CI/CD pipeline runs successfully (<12 min)
- [ ] Migrations applied in dev environment
- [ ] Manual testing on dev.meatscentral.com
- [ ] Promotion to UAT for QA testing

---

## 🔍 Troubleshooting

### Issue: "Reverse accessor clashes"
**Symptom**: Migration fails with `fields.E302` error  
**Cause**: `Product.supplier` used `related_name="products"`, conflicting with M2M field  
**Solution**: Changed to `related_name="supplied_products"` ✅

### Issue: "No tenant context"
**Symptom**: Empty queryset or 403 errors  
**Cause**: Missing `X-Tenant-ID` header or user not associated with tenant  
**Solution**: Ensure TenantMiddleware is enabled and user has TenantUser record

### Issue: "M2M field not in serializer"
**Symptom**: Products don't appear in Supplier/Customer API responses  
**Cause**: Forgot to add `products` to serializer fields list  
**Solution**: Added to `SupplierSerializer.Meta.fields` and `CustomerSerializer.Meta.fields` ✅

---

## 📚 Related Documentation

- **Multi-Tenancy Architecture**: `/docs/ARCHITECTURE.md`
- **API Standards**: `/.copilot-instructions.md` (Backend section)
- **CI/CD Optimizations**: `/CI_PERFORMANCE_OPTIMIZATION.md`
- **Deployment Guide**: `/.github/workflows/reusable-deploy.yml`

---

## 🎓 Key Learnings

1. **M2M Relationships**: Use `related_name` carefully to avoid clashes with existing ForeignKeys
2. **Nested Endpoints**: `@action` decorator creates clean REST patterns: `/suppliers/{id}/products/`
3. **Tenant Filtering**: Always filter M2M querysets by tenant to prevent data leakage
4. **Migration Naming**: Descriptive names like `add_products_m2m` improve clarity
5. **Idempotency**: `--fake-initial` flag ensures migrations are safe in CI/CD

---

**Document Status**: ✅ Backend Implementation Complete  
**Next Action**: Create feature branch and commit changes  
**Estimated Frontend Work**: 4-6 hours  
**Deployment ETA**: January 11, 2026 (after frontend implementation)
