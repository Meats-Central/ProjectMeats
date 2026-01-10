# Meats Central User Training Guide

**Target Audience:** Accounting Staff, Office Managers, and Financial Controllers  
**Feature Set:** Payment Recording, Activity Logging, and Call Management  
**Version:** 1.0 - January 2026  
**Status:** ✅ Production Ready

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Recording Payments](#recording-payments)
3. [Viewing Payment History](#viewing-payment-history)
4. [Managing Call Logs](#managing-call-logs)
5. [Using Activity Feeds](#using-activity-feeds)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Meats Central now includes powerful features to help you manage your daily accounting and communication tasks:

### What's New?

- **💰 Payment Recording** - Record payments against purchase orders, sales orders, and invoices
- **📜 Payment History** - View complete transaction history with references and dates
- **📞 Call Logging** - Schedule and track customer/supplier communications
- **📝 Activity Feeds** - See all notes and changes in one chronological feed

### Key Benefits

- **Real-Time Status Updates** - Payment statuses update instantly (Unpaid → Partial → Paid)
- **Audit Trail** - Every payment and activity is recorded with user and timestamp
- **Cross-Entity Support** - One interface works for POs, SOs, and Invoices
- **Multi-User Safe** - All actions are tenant-isolated and user-attributed

---

## 💰 Recording Payments

### Where to Record Payments

Navigate to any of these pages in the **Accounting** section:
- **Payables P.O.'s** - For supplier payments
- **Receivables S.O.'s** - For customer receipts
- **Invoices** - For invoice payments

### Step-by-Step: Recording a Payment

#### 1. Find the Order or Invoice

<img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 100'%3E%3Crect fill='%23f9fafb' width='600' height='100'/%3E%3Ctext x='10' y='30' font-family='Arial' font-size='14' fill='%23111827'%3EUse filters to find unpaid items:%3C/text%3E%3Crect x='10' y='45' width='120' height='30' rx='6' fill='%23ef4444' opacity='0.1' stroke='%23ef4444'/%3E%3Ctext x='35' y='66' font-family='Arial' font-size='13' font-weight='bold' fill='%23ef4444'%3EUNPAID%3C/text%3E%3C/svg%3E" alt="Filter for unpaid items" style="width: 100%; max-width: 600px;"/>

- Use the **Status Filter** at the top to show only "Unpaid" or "Partial" items
- Look for red (Unpaid) or yellow (Partial) status badges
- Click on any row to open the **Side Panel**

#### 2. Open the Payment Modal

<img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 80'%3E%3Crect fill='%23ffffff' width='600' height='80'/%3E%3Crect x='10' y='15' width='580' height='50' rx='8' fill='%23f9fafb' stroke='%23e5e7eb'/%3E%3Ctext x='20' y='35' font-family='Arial' font-size='16' font-weight='bold' fill='%23111827'%3EPO-2024-001%3C/text%3E%3Crect x='460' y='22' width='110' height='28' rx='6' fill='%2322c55e' opacity='0.1' stroke='%2322c55e'/%3E%3Ctext x='468' y='41' font-family='Arial' font-size='13' font-weight='600' fill='%2322c55e'%3E💰 Record Payment%3C/text%3E%3C/svg%3E" alt="Record Payment button" style="width: 100%; max-width: 600px;"/>

- In the side panel header, click the **💰 Record Payment** button
- The button only appears if the order/invoice is NOT fully paid
- A modal window will open with a payment form

#### 3. Fill in Payment Details

| Field | Description | Required |
|-------|-------------|----------|
| **Amount** | Pre-filled with outstanding balance. Edit for partial payments | ✅ Yes |
| **Payment Date** | Defaults to today. Cannot be future-dated | ✅ Yes |
| **Payment Method** | Choose: Check, Wire Transfer, ACH, Credit Card, Cash, or Other | ✅ Yes |
| **Reference Number** | Check number, wire confirmation, or transaction ID | ❌ Optional |
| **Notes** | Any additional context (e.g., "Partial payment pending wire completion") | ❌ Optional |

**Example - Full Payment:**
```
Amount:          $10,000.00  (pre-filled)
Payment Date:    01/08/2026  (today)
Payment Method:  Check
Reference:       CHK-54321
Notes:           Final payment for December order
```

**Example - Partial Payment:**
```
Amount:          $5,000.00   (edited from $10,000.00)
Payment Date:    01/08/2026  (today)
Payment Method:  Wire Transfer
Reference:       WIRE-ABC123
Notes:           First of two payments - balance due 01/15
```

#### 4. Submit and Verify

- Click **Record Payment** button
- The modal will close automatically on success
- The side panel and table will **refresh immediately**
- You should see:
  - ✅ Status badge change color (Red → Yellow → Green)
  - ✅ Outstanding amount decrease
  - ✅ New payment appear in Payment History
  - ✅ New activity note in Activity Log

### Payment Status Colors

| Status | Badge | Meaning |
|--------|-------|---------|
| 🔴 **UNPAID** | Red background | Full balance is outstanding |
| 🟡 **PARTIAL** | Yellow background | Some payments received, balance remains |
| 🟢 **PAID** | Green background | Fully paid - no outstanding balance |

---

## 📜 Viewing Payment History

### Where to Find Payment History

Payment history appears in the **Side Panel** for any order or invoice:

1. Click on any row in the table
2. Scroll down in the side panel
3. Look for the **"Payment History"** section (above Activity Log)

### What You'll See

Each payment transaction shows:

```
┌──────────────────────────────────────────┐
│ 01/08/2026              $5,000.00        │
│ Method: Check  Ref: CHK-54321  By: John  │
│ Note: Final payment for December order   │
└──────────────────────────────────────────┘
```

**Details Displayed:**
- **Date** - When payment was made/received
- **Amount** - Payment amount in green (success color)
- **Method** - How payment was made (Check, Wire, ACH, etc.)
- **Reference** - Check number or transaction ID
- **Created By** - Staff member who recorded the payment
- **Notes** - Any additional context provided

### Chronological Order

Payments are sorted **newest first**, so the most recent transaction appears at the top of the list.

### Empty State

If no payments have been recorded yet, you'll see:
```
┌──────────────────────────────────────────┐
│         No payment history yet           │
└──────────────────────────────────────────┘
```

---

## 📞 Managing Call Logs

### Accessing the Call Log

Navigate to **Cockpit → Call Log** in the main menu.

### Scheduling a Call

#### 1. Open the Schedule Form

- Click the **"+ Schedule Call"** button in the top-right corner
- A modal form will appear

#### 2. Fill in Call Details

| Field | Description | Required |
|-------|-------------|----------|
| **Date & Time** | When to make the call | ✅ Yes |
| **Customer/Supplier** | Who to call (dropdown with search) | ✅ Yes |
| **Reason** | Purpose of the call (e.g., "Follow up on invoice payment") | ✅ Yes |
| **Notes** | Additional context or talking points | ❌ Optional |
| **Status** | Scheduled, Completed, or Cancelled | ✅ Yes |

#### 3. Save and View

- Click **Save**
- The call appears in the main table with color-coded status
- Use filters to show only "Scheduled" calls for today's work queue

### Call Statuses

| Status | Color | Use Case |
|--------|-------|----------|
| **Scheduled** | Blue | Call is planned but not yet made |
| **Completed** | Green | Call was made successfully |
| **Cancelled** | Red | Call no longer needed |

### Updating Call Status

1. Click on the call row to open side panel
2. Click **Edit** button
3. Change status to "Completed"
4. Add notes about what was discussed
5. Save changes

---

## 📝 Using Activity Feeds

### What is an Activity Feed?

An **Activity Feed** is a chronological log of all notes, changes, and actions related to an order, invoice, or call. Think of it as a "conversation thread" for each business transaction.

### Where to Find Activity Feeds

Activity feeds appear in the **Side Panel** at the bottom:
- **Payables P.O.'s** - Purchase order activity
- **Receivables S.O.'s** - Sales order activity
- **Invoices** - Invoice activity
- **Call Log** - Call-specific notes

### Adding a Note

#### 1. Open the Side Panel

Click on any row in the table to open the details panel.

#### 2. Scroll to Activity Log

The Activity Feed is at the bottom of the side panel, below Payment History.

#### 3. Type Your Note

In the text box, type your note. Examples:
- "Called supplier - shipment delayed to Monday"
- "Customer requested revised invoice with updated pricing"
- "Confirmed wire transfer sent - should clear by EOD"

#### 4. Submit

- Click **Add Note** button
- Your note appears immediately at the top of the feed
- Your name and current timestamp are automatically recorded

### Reading Activity History

Each activity shows:
```
┌──────────────────────────────────────────┐
│ 👤 John Smith                            │
│ 🕐 2 hours ago                           │
│                                          │
│ Called supplier - shipment delayed to    │
│ Monday. Adjusted delivery schedule       │
│ accordingly.                             │
└──────────────────────────────────────────┘
```

**Details:**
- **User** - Who created the note
- **Time** - When it was created (relative time like "2 hours ago")
- **Content** - The note text
- **Type** - Icon indicates if it's a manual note (📝) or system event (⚙️)

### System-Generated Activities

Some activities are created automatically:
- **Payment Recorded** - When a payment is submitted via the modal
- **Status Changed** - When an order status changes
- **Created** - When the order/invoice was first created

---

## 🔄 Common Workflows

### Workflow 1: Processing a Customer Payment

**Scenario:** A customer sends a check for $5,000 against Invoice INV-2024-042 which has a $10,000 balance.

**Steps:**
1. Go to **Accounting → Invoices**
2. Filter by **Status: Unpaid**
3. Click on **INV-2024-042** row
4. Click **💰 Record Payment** button
5. Fill in payment details:
   - Amount: `$5,000.00`
   - Payment Date: `01/08/2026`
   - Method: `Check`
   - Reference: `CHK-78910`
   - Notes: `Partial payment - balance due 01/15`
6. Click **Record Payment**
7. **Result:** 
   - Status changes from RED (Unpaid) to YELLOW (Partial)
   - Outstanding balance shows `$5,000.00`
   - Payment appears in Payment History
   - Activity log shows "Payment of $5,000.00 recorded by [Your Name]"

### Workflow 2: Following Up on Overdue Invoice

**Scenario:** Invoice INV-2024-038 is 30 days overdue. You need to call the customer.

**Steps:**
1. Go to **Accounting → Invoices**
2. Find **INV-2024-038** (overdue with red status)
3. Click the row to open side panel
4. Go to **Cockpit → Call Log**
5. Click **+ Schedule Call**
6. Fill in:
   - Date & Time: `01/09/2026 10:00 AM`
   - Customer: Select customer from dropdown
   - Reason: `Follow up on overdue invoice INV-2024-038`
   - Status: `Scheduled`
7. Save the call
8. Next day at 10 AM, make the call
9. After the call, update status to `Completed`
10. Add note: "Spoke with accounts payable - wire transfer sent today, expect receipt 01/10"
11. Go back to **Invoices → INV-2024-038**
12. Add activity note: "Called customer - payment confirmed, wire in transit"

### Workflow 3: Reconciling Multiple Partial Payments

**Scenario:** Purchase Order PO-2024-055 had two partial payments. You need to verify full payment.

**Steps:**
1. Go to **Accounting → Payables P.O.'s**
2. Click on **PO-2024-055**
3. Check **Financial Summary** in side panel:
   - Total: `$15,000.00`
   - Outstanding: `$0.00`
   - Status: GREEN (Paid)
4. Scroll to **Payment History** section
5. Verify all payments are listed:
   ```
   12/20/2025  $10,000.00  Check CHK-11111
   01/05/2026  $5,000.00   Wire WIRE-22222
   ```
6. Add activity note: "Verified full payment received - closing PO"
7. Update PO status to "Completed" (if applicable)

---

## 🔧 Troubleshooting

### "Record Payment" Button Not Visible

**Possible Causes:**
- Order/Invoice is already marked as "Paid"
- Order/Invoice is "Cancelled"
- You don't have permission to record payments

**Solution:**
- Check the status badge - if it's GREEN (Paid), the button is hidden by design
- Verify with your manager if the item should be reopened
- Check with IT if you need payment recording permissions

### Payment Not Updating Status

**Possible Causes:**
- Network connection issue
- Page not refreshed after payment
- Caching issue in browser

**Solution:**
1. Wait 2-3 seconds after clicking "Record Payment"
2. If status doesn't update, close and reopen the side panel
3. Refresh the page (F5 or Ctrl+R)
4. If still not working, check your internet connection
5. Contact IT support if problem persists

### Payment History Not Loading

**Symptoms:**
- "Loading payment history..." message stays indefinitely
- Error message appears in Payment History section

**Solution:**
1. Refresh the page
2. Try closing and reopening the side panel
3. Check your internet connection
4. If issue continues for >5 minutes, contact IT support

### Wrong Amount Entered

**Scenario:** You recorded a payment with the wrong amount.

**Solution:**
- Payments **cannot be edited** once submitted (audit compliance)
- Contact your accounting manager or IT to void the incorrect payment
- A new correcting payment transaction will need to be created

### Activity Note Disappeared

**Possible Causes:**
- Note wasn't saved (network timeout during submission)
- Page was refreshed before save completed

**Solution:**
- Always wait for the note to appear in the feed before closing the panel
- If note is missing, simply re-add it
- Activity notes are permanent once they appear in the feed

### Can't Find Customer/Supplier in Call Log Dropdown

**Possible Causes:**
- Customer/Supplier is inactive in the system
- Name is spelled differently than expected
- Customer/Supplier hasn't been created yet

**Solution:**
1. Use the search box in the dropdown - try partial name matching
2. Check if the entity is active in **Master Data** section
3. If entity doesn't exist, create it first before scheduling the call
4. Contact IT if an active entity is not appearing in the list

---

## 📞 Getting Help

### Quick Reference Card

**Payment Recording:**
- Accounting → [Payables/Receivables/Invoices]
- Click row → 💰 Record Payment → Fill form → Submit

**Call Scheduling:**
- Cockpit → Call Log → + Schedule Call → Fill details → Save

**Activity Notes:**
- Click any row → Scroll to Activity Log → Type note → Add Note

### Support Contacts

| Issue Type | Contact | Response Time |
|------------|---------|---------------|
| **Payment Questions** | Accounting Manager | Same day |
| **Technical Issues** | IT Support | 1-2 hours |
| **Training Requests** | Office Manager | 1 week |
| **Feature Requests** | Project Lead | 2-4 weeks |

### Training Resources

- **Video Tutorials:** Available in the Help section (Coming Soon)
- **Live Training Sessions:** Monthly on 2nd Tuesday at 2 PM
- **Quick Start Guide:** Laminated card at each desk
- **This Document:** Bookmark for easy reference

---

## ✅ Best Practices

### Do's ✅

- **Record payments on the same day** they're received/sent
- **Include reference numbers** (check numbers, wire confirmations)
- **Add context in notes** - Future you will thank present you
- **Schedule calls proactively** - Don't rely on memory
- **Review Payment History** before calling customers about payments
- **Use Activity Feeds** to maintain institutional knowledge

### Don'ts ❌

- **Don't record future-dated payments** - Wait until the actual payment date
- **Don't skip reference numbers** - They're critical for audits
- **Don't leave cryptic notes** - Write complete sentences
- **Don't forget to mark calls as "Completed"** - Keeps the queue clean
- **Don't delete activity notes** - They're permanent by design
- **Don't guess payment amounts** - Verify with bank statements

---

## 📊 Key Performance Indicators

Track your efficiency with these metrics:

| Metric | Target | How to Track |
|--------|--------|--------------|
| **Payment Recording Lag** | <1 day | Compare payment date to record date |
| **Payment History Accuracy** | 100% | Cross-check with bank statements monthly |
| **Call Completion Rate** | >90% | Completed calls ÷ Scheduled calls |
| **Activity Note Frequency** | 2+ per order | Review activity feeds for coverage |

---

## 🎓 Training Checklist

Use this checklist to verify your understanding:

- [ ] I can filter orders by payment status (Unpaid, Partial, Paid)
- [ ] I can open the side panel and locate the Record Payment button
- [ ] I can record a full payment with all required fields
- [ ] I can record a partial payment by editing the pre-filled amount
- [ ] I can view payment history for any order or invoice
- [ ] I can schedule a call with customer/supplier details
- [ ] I can update a call status from Scheduled to Completed
- [ ] I can add activity notes to orders, invoices, and calls
- [ ] I know who to contact for different types of issues
- [ ] I understand the audit trail and why payments can't be edited

**Training Complete?** ✅  
**Date Completed:** _____________  
**Trainer Signature:** _____________

---

**Document Version:** 1.0  
**Last Updated:** January 8, 2026  
**Next Review:** April 2026  
**Maintained By:** ProjectMeats Team
