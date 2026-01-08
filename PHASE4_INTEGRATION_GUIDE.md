# Phase 4: Frontend Integration & UX Alignment

## ✅ Components Created (Complete)

### 1. LocationSelector Component
**Path**: `frontend/src/components/Shared/LocationSelector.tsx`

**Features**:
- RLS-protected location fetching from `/api/locations/`
- Graceful error handling for 403 Forbidden (RLS rejection)
- Token expiration detection with automatic logout
- Optional type filtering (plant, warehouse, distribution_center)
- Loading states and retry functionality
- Theme-aware styling

**Usage**:
```typescript
import { LocationSelector } from '../components/Shared';

<LocationSelector
  value={formData.pick_up_location}
  onChange={(id) => setFormData({ ...formData, pick_up_location: id })}
  label="Pick-up Location"
  required
  type="warehouse"
/>
```

**RLS Error Handling**:
- 401 Unauthorized → Triggers logout after 2 seconds
- 403 Forbidden → Shows "Access denied" message with retry button
- Network timeout → Shows "Request timeout" message
- Empty response → Shows "No locations available"

### 2. MultiSelect Component
**Path**: `frontend/src/components/Shared/MultiSelect.tsx`

**Features**:
- Prevents array serialization bug: `['Sales', 'Logistics']` NOT `['Sales,Logistics']`
- Console logging for debugging array structure
- Visual feedback for selected items count
- Keyboard navigation (Ctrl/Cmd + click)
- Theme-aware styling

**Usage**:
```typescript
import { MultiSelect } from '../components/Shared';
import { DEPARTMENT_CHOICES } from '../utils/constants/choices';

<MultiSelect
  value={formData.departments_array || []}
  onChange={(values) => setFormData({ ...formData, departments_array: values })}
  options={DEPARTMENT_CHOICES}
  label="Departments"
  placeholder="Select multiple departments (hold Ctrl/Cmd)"
/>
```

**CRITICAL - Array Serialization**:
```typescript
// ✅ CORRECT: Array of individual strings
{
  "departments_array": ["Sales", "Logistics", "Doc's BOL"]
}

// ❌ WRONG: Single string with commas
{
  "departments_array": ["Sales,Logistics,Doc's BOL"]
}
```

The `MultiSelect` component uses `Array.from(e.target.selectedOptions).map(option => option.value)` to ensure proper serialization.

### 3. Backend Choices Constants
**Path**: `frontend/src/utils/constants/choices.ts`

**Features**:
- All constants match backend `TextChoices` classes
- Single source of truth for dropdown options
- Easy to update when backend changes

**Available Constants**:
- `DEPARTMENT_CHOICES` (5 options)
- `INDUSTRY_CHOICES` (7 options)
- `PROTEIN_TYPE_CHOICES` (9 options)
- `CARRIER_RELEASE_FORMAT_CHOICES` (4 options)
- `CERTIFICATE_TYPE_CHOICES` (8 options)
- `SHIPPING_OFFERED_CHOICES` (7 options)
- `PAYMENT_TERMS_CHOICES` (6 options)

## 🔧 Integration Instructions

### Step 1: Update Suppliers Page

**File**: `frontend/src/pages/Suppliers.tsx`

**Changes Required**:

1. **Add imports**:
```typescript
import { MultiSelect } from '../components/Shared';
import { DEPARTMENT_CHOICES } from '../utils/constants/choices';
```

2. **Update formData state** to include `departments_array`:
```typescript
const [formData, setFormData] = useState({
  name: '',
  contact_person: '',
  email: '',
  phone: '',
  address: '',
  city: '',
  state: '',
  zip_code: '',
  country: '',
  departments_array: [] as string[], // NEW
});
```

3. **Add MultiSelect field** in the form (after Country field):
```typescript
<FormGroup>
  <MultiSelect
    value={formData.departments_array}
    onChange={(values) => setFormData({ ...formData, departments_array: values })}
    options={DEPARTMENT_CHOICES}
    label="Departments"
    placeholder="Select departments (hold Ctrl/Cmd for multiple)"
  />
</FormGroup>
```

4. **Update handleEdit** to populate `departments_array`:
```typescript
const handleEdit = (supplier: Supplier) => {
  setEditingSupplier(supplier);
  setFormData({
    name: supplier.name,
    contact_person: supplier.contact_person || '',
    email: supplier.email || '',
    phone: supplier.phone || '',
    address: supplier.address || '',
    city: supplier.city || '',
    state: supplier.state || '',
    zip_code: supplier.zip_code || '',
    country: supplier.country || '',
    departments_array: supplier.departments_array || [], // NEW
  });
  setShowForm(true);
};
```

5. **Update resetForm**:
```typescript
const resetForm = () => {
  setFormData({
    name: '',
    contact_person: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    country: '',
    departments_array: [], // NEW
  });
};
```

### Step 2: Update Customers Page

**File**: `frontend/src/pages/Customers.tsx`

**Changes Required** (similar to Suppliers):

1. **Add imports**:
```typescript
import { MultiSelect } from '../components/Shared';
import { INDUSTRY_CHOICES, PROTEIN_TYPE_CHOICES } from '../utils/constants/choices';
```

2. **Update formData state**:
```typescript
const [formData, setFormData] = useState({
  // ...existing fields
  industry_array: [] as string[], // NEW
  preferred_protein_types: [] as string[], // NEW
});
```

3. **Add MultiSelect fields**:
```typescript
<FormGroup>
  <MultiSelect
    value={formData.industry_array}
    onChange={(values) => setFormData({ ...formData, industry_array: values })}
    options={INDUSTRY_CHOICES}
    label="Industries"
  />
</FormGroup>

<FormGroup>
  <MultiSelect
    value={formData.preferred_protein_types}
    onChange={(values) => setFormData({ ...formData, preferred_protein_types: values })}
    options={PROTEIN_TYPE_CHOICES}
    label="Preferred Protein Types"
  />
</FormGroup>
```

### Step 3: Update Purchase Orders Page

**File**: `frontend/src/pages/PurchaseOrders.tsx`

**Changes Required**:

1. **Add imports**:
```typescript
import { LocationSelector } from '../components/Shared';
```

2. **Update formData state**:
```typescript
const [formData, setFormData] = useState({
  // ...existing fields
  pick_up_location: null as string | null, // NEW
  delivery_location: null as string | null, // NEW
});
```

3. **Add LocationSelector fields** in the form:
```typescript
<FormGroup>
  <LocationSelector
    value={formData.pick_up_location}
    onChange={(id) => setFormData({ ...formData, pick_up_location: id })}
    label="Pick-up Location"
    required
  />
</FormGroup>

<FormGroup>
  <LocationSelector
    value={formData.delivery_location}
    onChange={(id) => setFormData({ ...formData, delivery_location: id })}
    label="Delivery Location"
    required
  />
</FormGroup>
```

4. **CRITICAL: Verify API payload structure**

Check the backend serializer to determine if it expects:
- `pick_up_location` (UUID string) ✅ CORRECT
- OR `pick_up_location_id` (explicit ID suffix) ❌ Usually not needed

Test the payload in Network tab:
```json
{
  "supplier": 1,
  "order_number": "PO-12345",
  "pick_up_location": "uuid-here",
  "delivery_location": "uuid-here",
  "quantity": 100,
  "unit_price": "25.00"
}
```

### Step 4: Update Carriers Page

**File**: `frontend/src/pages/Carriers.tsx`

**Changes Required**:

1. **Add imports**:
```typescript
import { MultiSelect } from '../components/Shared';
import { DEPARTMENT_CHOICES } from '../utils/constants/choices';
```

2. **Update formData state**:
```typescript
const [formData, setFormData] = useState({
  // ...existing fields
  departments_array: [] as string[], // NEW
});
```

3. **Add MultiSelect field**:
```typescript
<FormGroup>
  <MultiSelect
    value={formData.departments_array}
    onChange={(values) => setFormData({ ...formData, departments_array: values })}
    options={DEPARTMENT_CHOICES}
    label="Departments"
  />
</FormGroup>
```

## 🧪 Testing Checklist

### Unit Testing (Console Verification)

1. **Array Serialization Test**:
```javascript
// Open browser console on Suppliers form
// Select multiple departments
// Check console output:
// "[MultiSelect] Selected values: ['Sales', 'Logistics', "Doc's BOL"]"
// Should see 3 separate strings, NOT comma-separated
```

2. **RLS Error Handling Test**:
```javascript
// Open browser console on PurchaseOrders form
// Clear authToken: localStorage.removeItem('authToken')
// Try to open form
// Expected: LocationSelector shows "Authentication required"
// After 2 seconds, redirect to /login
```

3. **Network Tab Validation**:
```javascript
// Open DevTools Network tab
// Create a new Supplier with departments selected
// Find POST /api/suppliers/ request
// Click "Payload" tab
// Verify JSON structure:
{
  "name": "Test Supplier",
  "departments_array": ["Sales", "Logistics"] // ✅ Array of strings
}
// NOT: "departments_array": "Sales,Logistics" // ❌ Single string
```

### Integration Testing (Manual)

1. **Location Selector Test**:
   - [ ] Open PurchaseOrders form
   - [ ] Verify LocationSelector loads locations
   - [ ] Select pick-up location
   - [ ] Select delivery location
   - [ ] Submit form
   - [ ] Verify API call includes location UUIDs
   - [ ] Check backend logs for tenant filtering

2. **MultiSelect Test**:
   - [ ] Open Suppliers form
   - [ ] Select 3 departments
   - [ ] Verify "3 items selected" message
   - [ ] Submit form
   - [ ] Verify API call has array of 3 strings
   - [ ] Edit supplier
   - [ ] Verify departments are pre-selected correctly

3. **RLS Error Test**:
   - [ ] Open PurchaseOrders form
   - [ ] In DevTools, modify authToken to invalid value
   - [ ] Try to load LocationSelector
   - [ ] Expected: Shows "Access denied" with Retry button
   - [ ] Click Retry
   - [ ] Expected: Still fails (token still invalid)
   - [ ] Fix token, click Retry
   - [ ] Expected: Locations load successfully

### Backend Field Mapping Verification

**CRITICAL CHECK**: Field names must match backend serializers.

Run this test after deployment:
```bash
# SSH into dev server
sudo docker exec -it pm-backend python manage.py shell

>>> from tenant_apps.purchase_orders.serializers import PurchaseOrderSerializer
>>> print(PurchaseOrderSerializer().fields.keys())
# Look for: 'pick_up_location', 'delivery_location'
# NOT: 'pick_up_location_id', 'delivery_location_id'
```

If serializer expects `_id` suffix:
```typescript
// Update form submit handler
const payload = {
  ...formData,
  pick_up_location_id: formData.pick_up_location, // Add _id suffix
  delivery_location_id: formData.delivery_location,
};
delete payload.pick_up_location; // Remove non-suffixed version
delete payload.delivery_location;
```

## ⚠️ Common Pitfalls & Solutions

### Problem 1: Array Serialization Bug
**Symptom**: Backend returns 400 error: "Expected a list of items but got type 'str'"

**Cause**: Frontend sending `["Sales,Logistics"]` instead of `["Sales", "Logistics"]`

**Solution**: Use the `MultiSelect` component which properly extracts individual option values.

**Debug**:
```typescript
// Add console.log in form submit handler
console.log('Payload:', JSON.stringify(formData, null, 2));
// Check if arrays are properly structured
```

### Problem 2: RLS 403 Forbidden
**Symptom**: LocationSelector shows "Access denied" on valid user

**Causes**:
1. Missing `X-Tenant-ID` header
2. User not assigned to correct tenant
3. Backend RLS policy misconfigured

**Solution**:
```typescript
// Check localStorage
console.log('Token:', localStorage.getItem('authToken'));
console.log('Tenant ID:', localStorage.getItem('tenantId'));

// If tenantId is null, user needs tenant assignment
// Check backend: User.tenant FK must be set
```

### Problem 3: Field Name Mismatch
**Symptom**: 400 error: "Unknown field: pick_up_location_id"

**Cause**: Frontend sending `pick_up_location_id` but backend expects `pick_up_location`

**Solution**: Check backend serializer field names:
```python
# backend/tenant_apps/purchase_orders/serializers.py
class PurchaseOrderSerializer(serializers.ModelSerializer):
    pick_up_location = serializers.PrimaryKeyRelatedField(...)  # Uses this name
    # NOT pick_up_location_id
```

Frontend should match:
```typescript
{
  "pick_up_location": "uuid-here", // ✅ Matches serializer
  "pick_up_location_id": "uuid-here" // ❌ Wrong
}
```

### Problem 4: Empty LocationSelector
**Symptom**: LocationSelector shows "No locations available" even though locations exist

**Causes**:
1. No locations created yet (run seed command)
2. RLS filtering out locations (tenant mismatch)
3. API endpoint not configured

**Solution**:
```bash
# 1. Run seed command to create test data
sudo docker exec -it pm-backend python manage.py seed_logistics_data

# 2. Verify locations exist and are accessible
sudo docker exec -it pm-backend python manage.py shell
>>> from tenant_apps.locations.models import Location
>>> Location.objects.count()
3  # Expected: At least 1 location

# 3. Test API endpoint directly
curl https://dev.meatscentral.com/api/locations/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "X-Tenant-ID: YOUR_TENANT_ID"
# Expected: JSON array of locations
```

## 📊 Deployment Checklist

### Pre-Deployment
- [ ] All components type-check with `npm run type-check`
- [ ] Console logs show proper array serialization
- [ ] Network tab shows correct JSON payloads
- [ ] No TypeScript errors in VS Code

### Post-Deployment (Dev Environment)
- [ ] Run seed command: `python manage.py seed_logistics_data`
- [ ] Test LocationSelector loads 3 seed locations
- [ ] Test MultiSelect on Suppliers form
- [ ] Test MultiSelect on Customers form
- [ ] Test LocationSelector on PurchaseOrders form
- [ ] Verify API payloads in Network tab
- [ ] Check backend logs for any serialization errors

### Performance Monitoring
- [ ] LocationSelector fetch time < 500ms
- [ ] No excessive re-renders on MultiSelect changes
- [ ] Form submit time < 1 second
- [ ] No memory leaks on repeated form open/close

## 🎯 Success Criteria

Phase 4 is complete when:

1. ✅ LocationSelector component successfully fetches locations filtered by RLS
2. ✅ MultiSelect component sends proper array structure (no serialization bugs)
3. ✅ Suppliers form saves `departments_array` correctly
4. ✅ Customers form saves `industry_array` and `preferred_protein_types`
5. ✅ PurchaseOrders form saves `pick_up_location` and `delivery_location`
6. ✅ RLS 403 errors handled gracefully with retry functionality
7. ✅ Token expiration triggers automatic logout
8. ✅ All forms display existing array data when editing

## 📚 Next Steps (Phase 5)

After Phase 4 completion:

1. **Phase 5: Sales Orders Integration**
   - Add LocationSelector to SalesOrders form
   - Add carrier_release_format dropdown
   - Add plant_est_number field

2. **Phase 6: Advanced UX**
   - Add location autocomplete search
   - Add location quick-create modal
   - Add bulk department assignment

3. **Phase 7: Testing & Documentation**
   - Write Jest tests for components
   - Add Storybook stories
   - Update API documentation

---

**Document Status**: ✅ Complete  
**Phase**: 4 of 7  
**Last Updated**: 2026-01-08  
**Next Review**: After Phase 4 deployment to dev
