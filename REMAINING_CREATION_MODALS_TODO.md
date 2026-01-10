# 🚧 Remaining Creation Modals - TODO

**Date:** January 8, 2026  
**Status:** Schedule Call Modal ✅ Complete | 3 Modals Remaining  
**Branch:** `development` (up to date)  

---

## ✅ Completed (PR #1796)

### **Schedule Call Modal** - Cockpit Call Log
- ✅ Modal component created (`ScheduleCallModal.tsx`)
- ✅ Integrated into `CallLog.tsx`
- ✅ Form with 7 fields (Title, Description, Entity Type, Entity ID, Date/Time, Duration, Purpose)
- ✅ POST to `cockpit/scheduled-calls/`
- ✅ Auto-refresh on success
- ✅ Full validation and error handling
- ✅ Theme-compliant styling
- ✅ Build passing (9.94s)
- ✅ PR merged to development

---

## 🔄 Remaining Work (3 Modals)

### **1. Sales Order Creation Modal**

**Target Page:** `frontend/src/pages/SalesOrders/SalesOrders.tsx`  
**Button Location:** Line ~440: `<button onClick={() => alert('Coming soon...')}>+ New Sales Order</button>`  
**Endpoint:** `POST sales-orders/`

**Required Fields:**
```typescript
{
  customer: number;          // Dropdown from customers/
  product: number;           // Dropdown from products/
  quantity: number;          // Min 1
  unit_price: number;        // Min 0.01, step 0.01
  delivery_date?: string;    // Optional date picker
}
```

**Implementation Steps:**
1. Create `frontend/src/components/Shared/CreateSalesOrderModal.tsx`
2. Copy pattern from `ScheduleCallModal.tsx`
3. Add `useEffect` to fetch customers and products on modal open
4. Modify `SalesOrders.tsx`:
   - Import `CreateSalesOrderModal`
   - Add `showCreateModal` state
   - Replace `alert()` with `setShowCreateModal(true)`
   - Add modal component: `<CreateSalesOrderModal isOpen={showCreateModal} onClose={...} onSuccess={fetchOrders} />`
5. Export from `Shared/index.ts`
6. Test build
7. Create PR

**Estimated Time:** 45-60 minutes

---

### **2. Claim Creation Modal**

**Target Page:** `frontend/src/pages/Accounting/Claims.tsx`  
**Button Location:** Line ~537: `<button onClick={() => alert('Coming soon...')}>+ New Claim</button>`  
**Endpoint:** `POST claims/`

**Required Fields:**
```typescript
{
  type: 'damage' | 'shortage' | 'quality' | 'other';  // Dropdown
  amount: number;                                      // Min 0.01, step 0.01
  reason: string;                                      // Textarea, required
  purchase_order?: number;                             // Optional PO reference
  sales_order?: number;                                // Optional SO reference
}
```

**Implementation Steps:**
1. Create `frontend/src/components/Shared/CreateClaimModal.tsx`
2. Copy pattern from `ScheduleCallModal.tsx`
3. Add claim type dropdown (4 options)
4. Add optional PO/SO reference fields
5. Modify `Claims.tsx`:
   - Import `CreateClaimModal`
   - Add `showCreateModal` state
   - Replace `alert()` with `setShowCreateModal(true)`
   - Add modal component: `<CreateClaimModal isOpen={showCreateModal} onClose={...} onSuccess={fetchClaims} />`
6. Export from `Shared/index.ts`
7. Test build
8. Create PR

**Estimated Time:** 40-50 minutes

---

### **3. Invoice Creation Modal**

**Target Page:** `frontend/src/pages/Accounting/Invoices.tsx`  
**Button Location:** Line ~583: `<button onClick={() => alert('Coming soon...')}>+ New Invoice</button>`  
**Endpoint:** `POST invoices/`

**Required Fields:**
```typescript
{
  customer: number;              // Dropdown from customers/
  sales_order?: number;          // Optional dropdown from sales-orders/
  amount: number;                // Min 0.01, step 0.01
  due_date: string;              // Date picker (required)
  description?: string;          // Optional textarea
  line_items?: Array<{           // Optional array
    description: string;
    quantity: number;
    unit_price: number;
  }>;
}
```

**Implementation Steps:**
1. Create `frontend/src/components/Shared/CreateInvoiceModal.tsx`
2. Copy pattern from `ScheduleCallModal.tsx`
3. Add customer dropdown (fetch from `customers/`)
4. Add optional sales order dropdown (fetch from `sales-orders/`)
5. Add due date picker
6. Modify `Invoices.tsx`:
   - Import `CreateInvoiceModal`
   - Add `showCreateModal` state
   - Replace `alert()` with `setShowCreateModal(true)`
   - Add modal component: `<CreateInvoiceModal isOpen={showCreateModal} onClose={...} onSuccess={fetchInvoices} />`
7. Export from `Shared/index.ts`
8. Test build
9. Create PR

**Estimated Time:** 50-60 minutes

---

## 📋 Common Pattern (Reusable Template)

All modals follow this structure:

### **Component Structure:**
```typescript
// 1. Imports
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { apiClient } from '../../services/apiService';

// 2. Props Interface
interface CreateXModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

// 3. Styled Components (copy from ScheduleCallModal)
const Overlay = styled.div<{ isOpen: boolean }>`...`;
const Modal = styled.div`...`;
const ModalHeader = styled.div`...`;
// ... etc

// 4. Component Function
export const CreateXModal: React.FC<CreateXModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  // 4a. State
  const [field1, setField1] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 4b. Fetch Options (if dropdowns needed)
  useEffect(() => {
    if (isOpen) {
      fetchOptions();
    }
  }, [isOpen]);

  // 4c. Reset Form
  const resetForm = () => {
    setField1('');
    setError(null);
  };

  // 4d. Handle Close
  const handleClose = () => {
    if (!submitting) {
      resetForm();
      onClose();
    }
  };

  // 4e. Handle Submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!field1) {
      setError('Field is required');
      return;
    }

    setSubmitting(true);

    try {
      const payload = { field1 };
      await apiClient.post('endpoint/', payload);

      resetForm();
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  // 4f. Render
  if (!isOpen) return null;

  return (
    <Overlay isOpen={isOpen} onClick={handleClose}>
      <Modal onClick={(e) => e.stopPropagation()}>
        <form onSubmit={handleSubmit}>
          <ModalHeader>
            <ModalTitle>Create X</ModalTitle>
            <CloseButton type="button" onClick={handleClose}>&times;</CloseButton>
          </ModalHeader>

          <ModalBody>
            {/* Form fields here */}
            {error && <ErrorMessage>{error}</ErrorMessage>}
          </ModalBody>

          <ModalFooter>
            <CancelButton type="button" onClick={handleClose} disabled={submitting}>
              Cancel
            </CancelButton>
            <SubmitButton type="submit" disabled={submitting}>
              {submitting ? 'Creating...' : 'Create X'}
            </SubmitButton>
          </ModalFooter>
        </form>
      </Modal>
    </Overlay>
  );
};
```

---

## 🎨 Theme Compliance Checklist

For each modal, ensure:

- [ ] All colors use design tokens:
  - `rgb(var(--color-primary))` for buttons
  - `rgb(var(--color-surface))` for modal background
  - `rgb(var(--color-text-primary))` for primary text
  - `rgb(var(--color-text-secondary))` for help text
  - `rgb(var(--color-border))` for borders

- [ ] No hardcoded hex colors (`#ffffff`, `#000000`, etc.)

- [ ] Respects light/dark mode automatically

- [ ] Matches existing modal patterns (RecordPaymentModal, ScheduleCallModal)

---

## 🧪 Testing Checklist (Per Modal)

Before creating PR:

- [ ] Build passes: `cd frontend && npm run build`
- [ ] Modal opens on button click
- [ ] Form fields populate correctly
- [ ] Validation messages display on errors
- [ ] Successful submission refreshes parent list
- [ ] Modal closes after success
- [ ] Cancel button works
- [ ] Close (×) button works
- [ ] Click outside modal closes it (optional behavior)
- [ ] Theme tokens applied (no hardcoded colors)
- [ ] No TypeScript errors
- [ ] No console errors in browser

---

## 📦 Deliverables (Per Modal)

1. **New Modal Component**
   - File: `frontend/src/components/Shared/Create[X]Modal.tsx`
   - Lines: ~350-450 (depending on fields)

2. **Modified Parent Page**
   - File: `frontend/src/pages/[Path]/[PageName].tsx`
   - Changes: Import modal, add state, wire button, add component

3. **Updated Exports**
   - File: `frontend/src/components/Shared/index.ts`
   - Change: Add export line

4. **Pull Request**
   - Title: `feat: Add [X] Creation Modal`
   - Description: Follow PR #1796 pattern
   - Assign reviewers
   - Merge to development after approval

---

## 🚀 Recommended Implementation Order

1. **Sales Order Modal** (Most straightforward)
   - Uses dropdowns for customer/product
   - Simple numeric fields
   - Good learning template

2. **Claim Modal** (Medium complexity)
   - Claim type dropdown
   - Optional PO/SO references
   - Reason textarea

3. **Invoice Modal** (Most complex)
   - Multiple dropdowns
   - Optional line items (future enhancement)
   - Complex business logic

---

## 🎯 Success Criteria

For each modal:

### **Functional Requirements:**
- ✅ Button click opens modal
- ✅ Form submits to correct endpoint
- ✅ Parent list refreshes on success
- ✅ Error handling shows user-friendly messages
- ✅ Validation prevents invalid submissions

### **Non-Functional Requirements:**
- ✅ Build time < 12 seconds
- ✅ No TypeScript errors
- ✅ Theme-compliant (uses design tokens)
- ✅ Consistent with existing modals
- ✅ Mobile-responsive (modal fits on small screens)

---

## 📚 Reference Files

**Copy Pattern From:**
- `frontend/src/components/Shared/ScheduleCallModal.tsx` (✅ PR #1796)
- `frontend/src/components/Shared/RecordPaymentModal.tsx` (✅ PR #1779)

**Reference Styling From:**
- `frontend/src/index.css` (Design tokens)
- All styled components use `rgb(var(--color-*))` pattern

**Reference API Integration:**
- `frontend/src/services/apiService.ts` (baseURL config)
- Use relative paths: `apiClient.post('sales-orders/', payload)`
- NOT: `apiClient.post('/api/v1/sales-orders/', payload)` (double prefix)

---

## ⏱️ Total Time Estimate

- **Sales Order Modal:** 45-60 minutes
- **Claim Modal:** 40-50 minutes
- **Invoice Modal:** 50-60 minutes
- **Testing & PR Creation:** 30 minutes total
- **Total:** ~3-4 hours for all three modals

---

## 🎉 When Complete

After all 3 modals are implemented and merged:

1. **Update `DEPLOYMENT_STATUS_FINAL.md`**
   - Mark "Creation Modals" as 100% complete
   - Update feature list

2. **Test End-to-End Workflow**
   - Schedule a call
   - Create a sales order
   - Create a claim
   - Create an invoice
   - Verify all appear in their respective lists

3. **Deploy to Dev Environment**
   - Follow `DEPLOYMENT_NEXT_STEPS.md`
   - Run smoke tests
   - Verify all modals work in deployed environment

4. **Promote to UAT**
   - After QA approval
   - Beta test with real users
   - Collect feedback

5. **Document for Users**
   - Update `USER_TRAINING_GUIDE.md`
   - Add screenshots of new modals
   - Create video walkthrough

---

**Status:** 📋 Ready for Implementation  
**Next Step:** Implement Sales Order Modal  
**Estimated Completion:** 3-4 hours of focused work  

**All patterns established, just needs execution!** 🚀
