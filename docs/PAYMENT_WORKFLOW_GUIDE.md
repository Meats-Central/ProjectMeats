# Payment Workflow User Guide

**ProjectMeats (Meats Central) - Accounting Module**  
**Document Version:** 1.0  
**Last Updated:** January 2026  
**Status:** ✅ Production Ready

---

## Overview

The Payment Tracking System enables users to record and track payments for Purchase Orders (Payables), Sales Orders (Receivables), and Customer Invoices. This guide covers the complete workflow from viewing outstanding balances to recording payments and verifying status updates.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Accessing Accounting Pages](#accessing-accounting-pages)
3. [Recording Payments](#recording-payments)
4. [Payment Status Indicators](#payment-status-indicators)
5. [Payment Methods](#payment-methods)
6. [Validation Rules](#validation-rules)
7. [Troubleshooting](#troubleshooting)
8. [Backend Integration](#backend-integration)

---

## Quick Start

**To record a payment in 4 steps:**

1. Navigate to **Accounting** → **Payables P.O.'s** / **Receivables S.O.'s** / **Invoices**
2. Click any row to open the side panel
3. Click **💰 Record Payment** button (appears when status ≠ paid)
4. Fill in payment details and submit

---

## Accessing Accounting Pages

### Navigation Structure

```
Meats Central Dashboard
└── Accounting
    ├── Payables P.O.'s      (Purchase Orders - Money You Owe)
    ├── Receivables S.O.'s   (Sales Orders - Money Owed to You)
    └── Invoices             (Customer Invoices)
```

### What Each Page Shows

**Payables P.O.'s (Purchase Orders)**
- Supplier name
- Order number and date
- Total amount and outstanding balance
- Payment status (Unpaid / Partial / Paid)
- Filter by: All | Unpaid | Partial | Paid

**Receivables S.O.'s (Sales Orders)**
- Customer name
- Order number and date
- Total amount and outstanding balance
- Payment status (Unpaid / Partial / Paid)
- Filter by: All | Unpaid | Partial | Paid

**Invoices**
- Customer name
- Invoice number and date
- Total amount and outstanding balance
- Invoice status (Draft / Sent / Paid / Overdue / Cancelled)
- Filter by: All | Draft | Sent | Paid | Overdue | Cancelled

---

## Recording Payments

### Step-by-Step Workflow

#### 1. View Outstanding Orders/Invoices

- Navigate to the appropriate accounting page
- Use filters to focus on **Unpaid** or **Partial** items
- Outstanding amounts are displayed in the **Outstanding** column
- Status badges use color coding:
  - 🔴 **Red** = Unpaid (full balance due)
  - 🟡 **Yellow** = Partial (some payments received)
  - 🟢 **Green** = Paid (balance cleared)

#### 2. Open the Side Panel

- Click any row in the table to open the **side panel** (400px width)
- Panel displays:
  - Entity reference number (PO#, SO#, or Invoice#)
  - Supplier/Customer name
  - Order/Invoice date
  - **Financial Summary**: Total amount and Outstanding balance
  - **Payment Status** badge
  - Notes (if any)
  - **Activity Log** (recent activity feed)

#### 3. Click "Record Payment" Button

- Button location: **Top-right of side panel header** (before × close button)
- Button appearance: Green background with 💰 icon
- Button visibility:
  - **Payables/Receivables**: Hidden when `payment_status === 'paid'`
  - **Invoices**: Hidden when `status === 'paid'` OR `status === 'cancelled'`

#### 4. Fill Payment Details in Modal

**Payment Modal Fields:**

| Field | Description | Required | Validation |
|-------|-------------|----------|------------|
| **Amount** | Payment amount received/made | ✅ Yes | Must be > 0 and ≤ outstanding balance |
| **Payment Method** | How payment was received | ✅ Yes | Check / Wire Transfer / ACH / Credit Card / Cash / Other |
| **Reference Number** | Check# or confirmation# | ❌ No | Free text (e.g., "CHK-12345" or "WIRE-98765") |
| **Payment Date** | Date payment was received | ✅ Yes | Cannot be future date (max = today) |
| **Notes** | Additional context | ❌ No | Free text (e.g., "Partial payment per agreement") |

**Pre-filled Values:**
- **Amount**: Automatically pre-filled with **outstanding balance**
- **Payment Date**: Defaults to **today's date**

**Example Use Cases:**

**Scenario 1: Full Payment**
- Total: $10,000.00
- Outstanding: $10,000.00
- Action: Accept pre-filled $10,000.00, select payment method, submit
- Result: Status changes to **PAID** ✅

**Scenario 2: Partial Payment**
- Total: $10,000.00
- Outstanding: $10,000.00
- Action: Change amount to $5,000.00, select payment method, add note "First installment"
- Result: Status changes to **PARTIAL** 🟡, Outstanding updates to $5,000.00

**Scenario 3: Second Partial Payment**
- Total: $10,000.00
- Outstanding: $5,000.00 (after first payment)
- Action: Enter $5,000.00, select payment method, submit
- Result: Status changes to **PAID** ✅, Outstanding updates to $0.00

#### 5. Submit and Verify

- Click **Record Payment** button in modal
- System validates input (see [Validation Rules](#validation-rules))
- On success:
  - Modal closes automatically
  - Side panel refreshes with updated data
  - Table row updates with new status badge
  - Outstanding balance decreases
- On error:
  - Red error message appears in modal
  - Fix validation issues and resubmit

---

## Payment Status Indicators

### Status Badge Colors

The system uses **semantic colors** for universal recognition:

| Badge Color | Status | Meaning | Outstanding Amount |
|-------------|--------|---------|-------------------|
| 🔴 **Red** | UNPAID | No payments received | = Total Amount |
| 🟡 **Yellow** | PARTIAL | Some payments received | > $0 and < Total |
| 🟢 **Green** | PAID | Fully paid | $0.00 |

### Status Transitions

```
UNPAID (Red)
  ↓
  │ Record partial payment (< outstanding balance)
  ↓
PARTIAL (Yellow)
  ↓
  │ Record final payment (= outstanding balance)
  ↓
PAID (Green)
```

**Automatic Status Updates:**
- Status changes happen **immediately** after payment submission
- Backend calculates new outstanding balance: `Total - Sum(All Payments)`
- Frontend updates badge color based on new status

---

## Payment Methods

### Available Options

| Method | Description | Reference Number Example |
|--------|-------------|-------------------------|
| **Check** | Paper or electronic check | CHK-12345 |
| **Wire Transfer** | Bank wire transfer | WIRE-98765 |
| **ACH** | Automated Clearing House | ACH-202601150001 |
| **Credit Card** | Card payment | *Last 4 digits: 4532* |
| **Cash** | Cash payment | N/A |
| **Other** | Other payment methods | Custom reference |

**Best Practices:**
- Always include reference numbers for **Check** and **Wire Transfer**
- For ACH, include transaction ID from bank
- For credit card, use last 4 digits or transaction ID
- Cash payments may not need reference numbers

---

## Validation Rules

### Amount Validation

**Rules:**
- ✅ Amount must be **greater than 0**
- ✅ Amount must be **less than or equal to outstanding balance**
- ❌ Cannot record $0.00 payment
- ❌ Cannot record payment exceeding outstanding balance

**Error Messages:**
```
"Amount must be greater than 0"
"Amount cannot exceed outstanding balance ($X,XXX.XX)"
```

**Examples:**

| Outstanding | Input | Valid? | Reason |
|-------------|-------|--------|--------|
| $10,000.00 | $5,000.00 | ✅ Yes | Within range |
| $10,000.00 | $10,000.00 | ✅ Yes | Full payment |
| $10,000.00 | $15,000.00 | ❌ No | Exceeds outstanding |
| $10,000.00 | $0.00 | ❌ No | Must be > 0 |
| $10,000.00 | -$500.00 | ❌ No | Must be positive |

### Payment Date Validation

**Rules:**
- ✅ Date must be **today or earlier**
- ❌ Cannot record future-dated payments

**Reason:** Prevents accidental data entry errors and maintains accurate financial records.

### Required Fields

**Must Fill:**
- Amount
- Payment Method
- Payment Date

**Optional:**
- Reference Number (but **strongly recommended** for check/wire)
- Notes

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Record Payment" Button Not Visible

**Possible Causes:**
1. Order/Invoice is already fully paid
2. Invoice status is "Cancelled"

**Solution:**
- Check payment status badge in table
- If already **PAID** (green), no action needed
- If **CANCELLED**, payments cannot be recorded

---

#### Issue 2: Modal Shows "Amount cannot exceed outstanding balance"

**Cause:** Entered amount > outstanding balance

**Solution:**
- Verify outstanding balance in side panel: **Financial Summary → Outstanding**
- Adjust payment amount to be ≤ outstanding
- If paying in full, click pre-filled amount (should match outstanding)

---

#### Issue 3: Payment Submitted but Status Not Updating

**Possible Causes:**
1. Browser not refreshing data
2. Backend error (check Network tab)

**Solution:**
- Close and re-open side panel to refresh
- Hard refresh page (Ctrl+F5 or Cmd+Shift+R)
- Check browser console for errors
- Contact IT support if issue persists

---

#### Issue 4: Cannot Select Future Payment Date

**Cause:** Date picker enforces `max={today}` validation

**Solution:**
- This is **by design** to prevent data entry errors
- If payment was truly received today, use today's date
- If recording historical payment, select the actual past date

---

#### Issue 5: Modal Closes Immediately After Opening

**Cause:** Likely clicking "Record Payment" multiple times rapidly

**Solution:**
- Open side panel again
- Click "Record Payment" **once**
- Wait for modal to fully render before interacting

---

## Backend Integration

### API Endpoint

**POST** `/api/v1/payments/`

**Request Body:**
```json
{
  "purchase_order": 123,      // OR sales_order OR invoice (only one)
  "amount": "5000.00",
  "payment_method": "check",
  "reference_number": "CHK-12345",
  "payment_date": "2026-01-15",
  "notes": "Partial payment per agreement"
}
```

**Response (Success):**
```json
{
  "id": 456,
  "purchase_order": 123,
  "amount": "5000.00",
  "payment_method": "check",
  "reference_number": "CHK-12345",
  "payment_date": "2026-01-15",
  "notes": "Partial payment per agreement",
  "entity_type": "purchase_order",
  "entity_reference": "PO-2024-001",
  "created_at": "2026-01-15T10:30:00Z",
  "created_by": 1,
  "created_by_name": "John Doe",
  "tenant": "tenant-uuid"
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "amount": ["Amount cannot exceed outstanding balance"]
}
```

---

### Database Schema

**PaymentTransaction Model:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `tenant` | ForeignKey | Tenant isolation |
| `purchase_order` | ForeignKey (nullable) | Link to PO (if applicable) |
| `sales_order` | ForeignKey (nullable) | Link to SO (if applicable) |
| `invoice` | ForeignKey (nullable) | Link to Invoice (if applicable) |
| `amount` | Decimal(12,2) | Payment amount |
| `payment_method` | CharField | check/wire/ach/credit_card/cash/other |
| `reference_number` | CharField | Check# or confirmation# |
| `payment_date` | DateField | Date payment received |
| `notes` | TextField | Optional notes |
| `created_at` | DateTimeField | Timestamp |
| `created_by` | ForeignKey | User who recorded payment |

**Polymorphic Pattern:**
- Only **one** of `purchase_order`, `sales_order`, `invoice` should be set
- The non-null FK determines the parent entity

---

### Auto-Calculation Logic

**On PaymentTransaction.save():**

1. **Sum all payments** for parent entity:
   ```python
   total_paid = parent.payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
   ```

2. **Calculate outstanding balance:**
   ```python
   outstanding = parent.total_amount - total_paid
   ```

3. **Update payment_status:**
   - If `outstanding == 0`: `payment_status = 'paid'`
   - If `0 < outstanding < total`: `payment_status = 'partial'`
   - If `outstanding == total`: `payment_status = 'unpaid'`

4. **Save parent entity:**
   ```python
   parent.outstanding_amount = outstanding
   parent.payment_status = status
   parent.save()
   ```

**Additional Logic (Invoices Only):**
- If `payment_status == 'paid'`, also set `invoice.status = 'paid'`

---

## Advanced Features (Planned)

### Phase 2 Enhancements

1. **Payment History List**
   - Display all payments in side panel
   - Show: Date | Method | Reference# | Amount
   - Collapsible section above Activity Log

2. **Edit/Delete Payments**
   - Allow corrections to recorded payments
   - Recalculate outstanding balance on change
   - Audit trail for modifications

3. **Bulk Payment Recording**
   - Upload CSV of multiple payments
   - Validate and import in batch
   - Error reporting for failed imports

4. **Payment Reminders**
   - Email reminders for overdue invoices
   - Scheduled notifications to customers
   - Configurable reminder intervals

5. **Payment Reports**
   - Aging report (30/60/90 days)
   - Cash flow projections
   - Payment method breakdown
   - Export to Excel/PDF

---

## Glossary

| Term | Definition |
|------|------------|
| **Outstanding Amount** | Remaining balance after subtracting all recorded payments from total |
| **Total Amount** | Original order/invoice amount before any payments |
| **Payment Status** | Current state: Unpaid / Partial / Paid |
| **Side Panel** | 400px right-side panel showing entity details |
| **Entity** | Generic term for Purchase Order, Sales Order, or Invoice |
| **Tenant** | Isolated data environment for multi-tenant system |

---

## Support and Feedback

**Questions or Issues?**
- Contact: IT Support Team
- Email: support@meatscentral.com
- Documentation: `/docs/` folder in repository

**Feature Requests:**
- Submit via GitHub Issues
- Tag with `enhancement` label
- Include use case description

---

**Document Status:** ✅ Complete and Production-Ready  
**Related Documentation:**
- [PAYMENT_WORKFLOW_TECHNICAL.md](./PAYMENT_WORKFLOW_TECHNICAL.md) (Technical Implementation Details)
- [ROUTING_FIX_COMPLETE.md](./ROUTING_FIX_COMPLETE.md) (ERP Module Build-Out)
- [CONFIGURATION_AND_SECRETS.md](./CONFIGURATION_AND_SECRETS.md) (Environment Setup)

---

**Last Reviewed:** January 2026  
**Next Review Date:** April 2026
