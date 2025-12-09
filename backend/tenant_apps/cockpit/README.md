# Cockpit App

## Purpose
Provides aggregated, polymorphic search across tenant-scoped models (Customer, Supplier, PurchaseOrder) for ProjectMeats frontend "Cockpit" search feature.

## Features
- **Multi-tenant isolation**: Automatically respects shared-schema tenancy via `TenantMiddleware`
- **Polymorphic search**: Returns unified results with `type` field for frontend icon rendering
- **Lightweight serializers**: Minimal data transfer for fast autocomplete/search

## API Endpoint
```
GET /api/v1/cockpit/slots/?q={query}
```

### Query Parameters
- `q` (string): Search query for filtering by name/order number

### Response Format
```json
[
  {
    "id": 1,
    "name": "ABC Corporation",
    "type": "customer",
    "contact_name": "John Doe",
    "email": "john@abc.com",
    "phone": "555-1234"
  },
  {
    "id": 2,
    "name": "XYZ Supplies",
    "type": "supplier",
    "contact_name": "Jane Smith",
    "email": "jane@xyz.com",
    "phone": "555-5678"
  },
  {
    "id": 3,
    "order_number": "PO-2024-001",
    "our_purchase_order_num": "INT-001",
    "type": "order",
    "status": "pending",
    "supplier_name": "XYZ Supplies",
    "total_amount": "1250.00"
  }
]
```

## Frontend Integration

### Type-to-Icon Mapping
- `customer` → Building icon
- `supplier` → Building/Factory icon  
- `order` → Truck icon

### Example React Usage
```typescript
import { Building, Truck } from 'lucide-react';

const iconMap = {
  customer: Building,
  supplier: Building,
  order: Truck,
};

const SearchResult = ({ item }) => {
  const Icon = iconMap[item.type];
  return (
    <div>
      <Icon /> {item.name || item.order_number}
    </div>
  );
};
```

## Architecture
- **No models**: View-only app, no database tables
- **Read-only ViewSet**: Uses `ReadOnlyModelViewSet` for GET operations only
- **Tenant filtering**: Queries are automatically scoped via `tenant_id` foreign keys
- **Result limiting**: Returns max 10 results per model type (30 total)

## Multi-Tenancy Notes
- All queries respect current tenant context via `TenantMiddleware`
- Queries are filtered by `tenant=request.tenant` in ViewSets
- Migrations run with standard Django `python manage.py migrate`

## Security
- Requires `IsAuthenticated` permission
- All queries are tenant-scoped (no cross-tenant data leakage)
- Input sanitization via Django ORM (no SQL injection risk)
