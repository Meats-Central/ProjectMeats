# Data Model and Features Guide

This guide documents the data models and features available in ProjectMeats.

## Table of Contents

1. [Purchase Order Version History](#purchase-order-version-history)
2. [Data Models](#data-models)

---

## Purchase Order Version History

### Overview

The Purchase Order Version History feature automatically tracks all changes made to purchase orders, providing a complete audit trail for compliance and historical analysis.

### Features

- **Automatic Tracking**: Every create and update operation on a PurchaseOrder is automatically logged
- **Change Type Classification**: Changes are classified as "created", "updated", or "deleted"
- **User Attribution**: Tracks which user made the change (when available)
- **Field-Level Details**: Stores the specific fields that were changed and their new values
- **Chronological Ordering**: History entries are ordered by timestamp in descending order

### Data Model

The `PurchaseOrderHistory` model includes:

| Field | Type | Description |
|-------|------|-------------|
| `id` | BigAutoField | Primary key |
| `purchase_order` | ForeignKey | Reference to the PurchaseOrder |
| `changed_data` | JSONField | JSON object containing changed fields and values |
| `changed_by` | ForeignKey(User) | User who made the change (nullable) |
| `change_type` | CharField | Type of change: "created", "updated", or "deleted" |
| `created_on` | DateTimeField | Timestamp when the change was recorded |
| `modified_on` | DateTimeField | Last modification timestamp |

### API Usage

#### Retrieve History for a Purchase Order

**Endpoint:** `GET /api/v1/purchase-orders/{id}/history/`

**Example Request:**
```bash
curl -X GET \
  https://your-domain.com/api/v1/purchase-orders/123/history/ \
  -H 'Authorization: Token your-auth-token' \
  -H 'X-Tenant-ID: your-tenant-id'
```

**Example Response:**
```json
[
  {
    "id": 456,
    "purchase_order": 123,
    "purchase_order_number": "PO-001",
    "changed_data": {
      "status": "approved",
      "total_amount": "1500.00"
    },
    "changed_by": 5,
    "changed_by_username": "john.doe",
    "change_type": "updated",
    "created_on": "2025-10-13T10:30:00Z",
    "modified_on": "2025-10-13T10:30:00Z"
  },
  {
    "id": 455,
    "purchase_order": 123,
    "purchase_order_number": "PO-001",
    "changed_data": {
      "order_number": "PO-001",
      "supplier": "uuid-of-supplier",
      "total_amount": "1000.00",
      "status": "pending",
      "order_date": "2025-10-13"
    },
    "changed_by": 5,
    "changed_by_username": "john.doe",
    "change_type": "created",
    "created_on": "2025-10-13T09:00:00Z",
    "modified_on": "2025-10-13T09:00:00Z"
  }
]
```

### Implementation Details

#### Signal Handler

Changes are tracked using Django's `post_save` signal:

```python
@receiver(post_save, sender=PurchaseOrder)
def create_purchase_order_history(sender, instance, created, **kwargs):
    # Signal handler automatically creates history entries
    pass
```

The signal handler:
- Fires after every save operation on PurchaseOrder
- Skips during migrations and fixture loading (`raw=True`)
- Converts all field values to JSON-serializable formats
- Handles ForeignKey fields by storing their IDs
- Handles Date/DateTime fields by converting to ISO format
- Handles Decimal fields by converting to strings

#### Data Serialization

Field values are converted to JSON-serializable formats:
- **ForeignKey fields**: Stored as string representation of the UUID
- **Decimal fields**: Converted to strings
- **Date/DateTime fields**: Converted to ISO 8601 format
- **Null values**: Stored as `null`
- **Other fields**: Converted to strings

### Security Considerations

- History entries cannot be manually created via the admin interface
- History entries cannot be deleted to preserve audit trail
- Only authenticated users with proper permissions can view history
- User attribution is tracked when available through the signal

### Admin Interface

History entries can be viewed in the Django admin under:
- **Admin → Purchase Order Histories**

The admin interface is read-only and provides:
- List view with purchase order, change type, user, and timestamp
- Filtering by change type and creation date
- Search by purchase order number and username
- Detailed view of the changed data JSON

### Best Practices

1. **Reviewing Changes**: Use the history API endpoint to audit changes for compliance
2. **Performance**: History entries are indexed by purchase order and creation date for fast queries
3. **Data Retention**: Consider implementing a data retention policy for very old history entries
4. **User Context**: When programmatically creating/updating POs, pass user context when possible

### Example Use Cases

1. **Audit Trail**: Track who changed order amounts and when
2. **Compliance**: Demonstrate regulatory compliance with change tracking
3. **Dispute Resolution**: Review historical changes to resolve disputes
4. **Analytics**: Analyze patterns in order modifications
5. **Rollback Reference**: Use historical data to understand previous states

---

## Data Models

### Core Models

- **PurchaseOrder**: Main purchase order entity
- **PurchaseOrderHistory**: Version history for purchase orders
- **Supplier**: Supplier information
- **Customer**: Customer information
- **Carrier**: Carrier/logistics information
- **Plant**: Facility/plant information
- **Contact**: Contact person details

### Relationships

```
PurchaseOrder
├── supplier (ForeignKey → Supplier)
├── carrier (ForeignKey → Carrier, nullable)
├── plant (ForeignKey → Plant, nullable)
├── contact (ForeignKey → Contact, nullable)
├── tenant (ForeignKey → Tenant, nullable)
└── history (Reverse ForeignKey ← PurchaseOrderHistory)

PurchaseOrderHistory
├── purchase_order (ForeignKey → PurchaseOrder)
└── changed_by (ForeignKey → User, nullable)
```

### Field Reference

For detailed field information, refer to:
- [Backend Architecture](BACKEND_ARCHITECTURE.md)
- [Data Model Enhancements](DATA_MODEL_ENHANCEMENTS.md)

---

## Migration Notes

When deploying the version history feature:

1. **Run migrations**: `python manage.py migrate purchase_orders`
2. **Verify admin access**: Check that PurchaseOrderHistory appears in admin
3. **Test API endpoint**: Verify `/api/v1/purchase-orders/{id}/history/` works
4. **Monitor performance**: Watch for any performance impact on PO saves

### Database Indexes

The following indexes are automatically created:
- `purchase_order_id, created_on DESC` - For fast history lookups

---

## Troubleshooting

### History not being created

1. Check that migrations have been applied
2. Verify the signal is registered (check `apps.py`)
3. Ensure `raw=False` when saving (not during fixtures/migrations)

### JSON serialization errors

If you encounter JSON serialization errors:
- Check for custom field types that aren't handled
- Review the signal handler's type conversion logic
- Add custom serialization for new field types

### Performance issues

If history tracking causes performance issues:
- Consider batch operations that disable signals temporarily
- Implement async history creation for high-volume scenarios
- Add database read replicas for history queries

---

## Future Enhancements

Potential future improvements to the version history system:

1. **Field-level Diffing**: Show old vs new values for each changed field
2. **Restore Functionality**: Allow restoring to a previous version
3. **Change Notifications**: Email notifications for certain types of changes
4. **Advanced Filtering**: Filter history by date range, user, or change type
5. **Export**: Export history to CSV or PDF for reporting

---

*Last updated: 2025-10-13*
