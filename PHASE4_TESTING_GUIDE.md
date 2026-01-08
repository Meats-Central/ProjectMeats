# Phase 4 Testing & Verification Guide

## ✅ INTEGRATION COMPLETE - READY FOR TESTING

**Status**: All forms updated with Phase 4 components
**Commit**: 83b5da6
**Files Changed**: 4 (Suppliers.tsx, Customers.tsx, PurchaseOrders.tsx, apiService.ts)

---

## 🎯 Critical Verification Points

### 1. Array Serialization Verification (HIGHEST PRIORITY)

**Problem**: Frontend might send single string with commas instead of proper array
**Impact**: Django ArrayField will reject with 400 Bad Request
**Test Location**: Suppliers form, Customers form

#### Test Procedure:

1. **Open Chrome DevTools**
   - Press F12 or Right-click → Inspect
   - Go to "Network" tab
   - Keep it open during form submission

2. **Test Suppliers Form**
   ```
   Step 1: Open Suppliers page
   Step 2: Click "+ Add Supplier"
   Step 3: Fill in required fields:
      - Company Name: "Test Supplier Inc"
      - Select 3 departments (hold Ctrl/Cmd):
        • Sales
        • Logistics
        • Doc's BOL
   Step 4: Click "Create Supplier"
   ```

3. **Verify Network Tab**
   ```
   - Find: POST /api/suppliers/
   - Click on the request
   - Go to "Payload" tab
   - Look for "departments_array"
   ```

4. **Expected Result** ✅:
   ```json
   {
     "name": "Test Supplier Inc",
     "departments_array": ["Sales", "Logistics", "Doc's BOL"]
   }
   ```

5. **Failure Pattern** ❌ (if you see this, STOP and report):
   ```json
   {
     "name": "Test Supplier Inc",
     "departments_array": ["Sales,Logistics,Doc's BOL"]
   }
   ```
   OR
   ```json
   {
     "name": "Test Supplier Inc",
     "departments_array": "Sales,Logistics,Doc's BOL"
   }
   ```

6. **Console Verification**:
   ```javascript
   // Look for this in Console tab:
   [MultiSelect] Selected values: (3) ['Sales', 'Logistics', "Doc's BOL"]
   ```

7. **Backend Response**:
   - Status: 201 Created ✅
   - OR Status: 400 Bad Request ❌ (array serialization bug)

---

### 2. RLS Error Handling Verification

**Problem**: LocationSelector might crash if RLS denies access
**Impact**: White screen of death or uncaught errors
**Test Location**: Purchase Orders form

#### Test Procedure:

1. **Simulate Token Expiration**
   ```javascript
   // Open Console (F12)
   localStorage.removeItem('authToken');
   ```

2. **Refresh Page**
   - Press F5 or Ctrl+R

3. **Try to Open Form**
   ```
   Step 1: Click "+ Add Purchase Order"
   Step 2: Observe LocationSelector behavior
   ```

4. **Expected Result** ✅:
   ```
   - LocationSelector shows: "Session expired - please log in again"
   - After 2 seconds: Redirect to /login page
   - NO white screen
   - NO uncaught TypeError
   ```

5. **Failure Pattern** ❌:
   ```
   - White screen
   - Console error: "Uncaught TypeError: Cannot read property..."
   - Form crashes completely
   ```

6. **Simulate RLS Rejection (403 Forbidden)**
   ```javascript
   // In Console, after re-login:
   // Modify token to invalid value
   localStorage.setItem('authToken', 'invalid_token_12345');
   ```

7. **Try Again**:
   ```
   Step 1: Refresh page
   Step 2: Click "+ Add Purchase Order"
   Step 3: Observe LocationSelector
   ```

8. **Expected Result** ✅:
   ```
   - LocationSelector shows: "Access denied - insufficient permissions"
   - Retry button appears
   - Form remains functional (other fields work)
   ```

---

### 3. Backend Field Name Mapping Verification

**Problem**: Frontend sends wrong field names to backend
**Impact**: 400 Bad Request: "Unknown field"
**Test Location**: Purchase Orders form

#### Pre-Deployment Verification (Local):

Check backend serializer field names:
```bash
# In backend directory
cd /workspaces/ProjectMeats/backend
python manage.py shell
```

```python
from tenant_apps.purchase_orders.serializers import PurchaseOrderSerializer
serializer = PurchaseOrderSerializer()
print(list(serializer.fields.keys()))

# Look for:
# ['id', 'order_number', 'supplier', 'pick_up_location', 'delivery_location', ...]
# NOT: 'pick_up_location_id', 'delivery_location_id'
```

#### Post-Deployment Verification:

1. **Test Purchase Order Creation**
   ```
   Step 1: Open Purchase Orders page
   Step 2: Click "+ Add Purchase Order"
   Step 3: Fill in required fields:
      - Order Number: (auto-generated)
      - Supplier: Select any
      - Total Amount: 1000.00
      - Pick-up Location: Select any
      - Delivery Location: Select any
   Step 4: Click "Create Purchase Order"
   ```

2. **Verify Network Tab**
   ```
   - Find: POST /api/purchase-orders/ (or /purchase_orders/)
   - Go to "Payload" tab
   ```

3. **Expected Payload** ✅:
   ```json
   {
     "order_number": "123",
     "supplier": 1,
     "total_amount": 1000.00,
     "pick_up_location": "uuid-string-here",
     "delivery_location": "uuid-string-here"
   }
   ```

4. **Backend Response**:
   - Status: 201 Created ✅
   - Response includes: `"pick_up_location_details": {...}` (nested object)

5. **Failure Pattern** ❌:
   ```json
   Response: 400 Bad Request
   {
     "pick_up_location_id": ["Unknown field"]
   }
   ```
   OR
   ```json
   {
     "pick_up_location": ["This field is required"]
   }
   ```

6. **Fix If Needed**:
   ```typescript
   // If backend expects _id suffix, update PurchaseOrders.tsx:
   const payload = {
     ...formData,
     pick_up_location_id: formData.pick_up_location,
     delivery_location_id: formData.delivery_location,
   };
   delete payload.pick_up_location;
   delete payload.delivery_location;
   ```

---

## 🔍 Additional Testing Checklist

### Suppliers Form Testing

- [ ] **Create Supplier**
  - [ ] Select 1 department → Saves correctly
  - [ ] Select 3 departments → All 3 saved
  - [ ] Select 0 departments → Saves with empty array `[]`
  - [ ] Network tab shows proper array structure

- [ ] **Edit Supplier**
  - [ ] Open existing supplier
  - [ ] Departments pre-selected correctly
  - [ ] Change departments → Updates correctly
  - [ ] Remove all departments → Saves empty array

- [ ] **Display**
  - [ ] MultiSelect shows "X items selected" counter
  - [ ] Selected items highlighted in list
  - [ ] Keyboard navigation works (Ctrl+click)

### Customers Form Testing

- [ ] **Create Customer**
  - [ ] Select 2 industries → Saves correctly
  - [ ] Select 3 protein types → Saves correctly
  - [ ] Network tab shows 2 separate arrays

- [ ] **Edit Customer**
  - [ ] Both MultiSelects pre-populate correctly
  - [ ] Can change both independently
  - [ ] Removing all items works

### Purchase Orders Form Testing

- [ ] **Create Purchase Order**
  - [ ] LocationSelector loads locations (not empty)
  - [ ] Can select pick-up location
  - [ ] Can select delivery location
  - [ ] Can select same location for both
  - [ ] Network tab shows UUID strings

- [ ] **Edit Purchase Order**
  - [ ] Locations pre-selected correctly
  - [ ] Can change locations
  - [ ] Can clear locations (set to null)

- [ ] **Location Selector**
  - [ ] Shows "Loading locations..." initially
  - [ ] Shows location format: "Name - Type (City, State)"
  - [ ] No duplicates in list
  - [ ] Locations filtered by tenant (RLS)

---

## 🐛 Troubleshooting Guide

### Issue: Array shows as single string

**Symptoms**:
```json
"departments_array": "Sales,Logistics"
```

**Cause**: MultiSelect not extracting values correctly

**Debug**:
```javascript
// Check console for:
[MultiSelect] Selected values: ...
// Should show array, not string
```

**Fix**: Component already handles this, but verify imports

---

### Issue: LocationSelector shows "No locations available"

**Symptoms**:
- Dropdown empty
- Console shows 200 OK response but no data

**Cause**: Seed data not created, or RLS filtering out locations

**Debug**:
```bash
# SSH to dev server
sudo docker exec -it pm-backend python manage.py shell
```

```python
from tenant_apps.locations.models import Location
print(Location.objects.count())
# Should be > 0

# Check your tenant
from apps.tenants.models import Tenant
tenant = Tenant.objects.first()
print(Location.objects.filter(tenant=tenant).count())
```

**Fix**:
```bash
# Create seed data
sudo docker exec -it pm-backend python manage.py seed_logistics_data
```

---

### Issue: 400 Bad Request on form submit

**Symptoms**:
- Form submission fails
- Network tab shows 400 status
- Error message about field validation

**Debug**:
```json
// Check response body in Network tab
{
  "departments_array": ["Expected a list of items but got type 'str'"]
}
```

**Cause**: Array serialization bug

**Fix**: Verify MultiSelect component is imported and used correctly

---

### Issue: 403 Forbidden on LocationSelector

**Symptoms**:
- LocationSelector shows "Access denied"
- Other API calls work fine

**Cause**: RLS policy rejecting request

**Debug**:
```javascript
// Check console
[LocationSelector] RLS policy rejected request: ...
```

**Fix**:
1. Verify user has tenant assigned
2. Check `X-Tenant-ID` header in request
3. Verify RLS policy on backend

---

## 📊 Success Criteria

Phase 4 Integration is successful when:

- [ ] **Array Serialization**: All MultiSelect forms send proper arrays (3/3 forms)
- [ ] **RLS Error Handling**: LocationSelector handles 401/403 gracefully (no crashes)
- [ ] **Field Mapping**: Backend accepts location UUIDs without errors
- [ ] **Edit Functionality**: All forms pre-populate arrays/locations correctly
- [ ] **User Experience**: No white screens, helpful error messages
- [ ] **Network Payloads**: All requests match backend serializer expectations

---

## 🚀 Deployment Verification Steps

After deployment to dev environment:

1. **Backend Verification** (15 min)
   ```bash
   # SSH to dev server
   ssh user@dev.meatscentral.com
   
   # Check backend logs
   sudo docker logs pm-backend --tail 50
   # Should NOT see: ArrayField errors, RLS errors
   
   # Run seed command
   sudo docker exec -it pm-backend python manage.py seed_logistics_data
   # Expected: Creates 3 locations, 2 suppliers, etc.
   
   # Test API directly
   curl https://dev.meatscentral.com/api/locations/ \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "X-Tenant-ID: YOUR_TENANT_ID"
   # Expected: JSON array of locations
   ```

2. **Frontend Verification** (20 min)
   - Open https://dev.meatscentral.com
   - Test all 3 forms (Suppliers, Customers, Purchase Orders)
   - Verify Network tab payloads
   - Test edit functionality

3. **Integration Test** (15 min)
   - Create supplier with departments
   - Create customer with industries/proteins
   - Create purchase order with locations
   - Verify data appears correctly in database

---

## 📞 Support Contacts

If issues arise:

**Array Serialization Issues**:
- Check: `PHASE4_INTEGRATION_GUIDE.md` - "Array Serialization Bug Prevention"
- Fix: Verify MultiSelect component import and usage

**RLS Issues**:
- Check: Backend logs for RLS policy errors
- Fix: Verify tenant assignment in Django admin

**Field Mapping Issues**:
- Check: Backend serializer field names in Django shell
- Fix: Update frontend field names to match backend

**Emergency Rollback**:
```bash
# If deployment breaks
git revert 83b5da6
git push origin feature/model-updates
```

---

## ✅ Final Checklist Before Approval

- [ ] All 3 critical verifications completed
- [ ] Array serialization tested (Network tab)
- [ ] RLS error handling tested (token expiration)
- [ ] Field name mapping verified (backend serializer)
- [ ] All forms create/edit/display work correctly
- [ ] No console errors or warnings
- [ ] TypeScript compilation successful
- [ ] Documentation updated

---

**Testing Complete**: __________  
**Tested By**: __________  
**Date**: __________  
**Approval**: __________

---

**Phase 4 Status**: ✅ INTEGRATION COMPLETE - AWAITING TESTING
**Next Phase**: Deploy to dev → Test → PR Review → UAT
