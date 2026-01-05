# Phase 3: UX & Functional Polish - Task Manifest

**Status:** 🚧 In Progress  
**Start Date:** January 5, 2026  
**Target Completion:** Sprint 2026-Q1

---

## Overview

This phase focuses on polishing the user experience, fixing critical bugs, and implementing missing core pages. All changes maintain backward compatibility with the new Semantic Design System.

---

## 1. Dashboard & Navigation (Visual)

**Goal:** Unify iconography and improve navigation usability.

### Tasks

- [ ] **Icon Uniformity**
  - **File:** `frontend/src/pages/Dashboard.tsx`
  - **Action:** Force all summary card icons (Suppliers, Customers, POs, AR) to use `text-white` or a single theme color instead of mixed colors
  - **Benefit:** Consistent visual hierarchy
  - **Priority:** Medium

- [ ] **Clickable Cards**
  - **File:** `frontend/src/pages/Dashboard.tsx`
  - **Action:** Wrap each "Summary Card" component in a `Link` or `useNavigate` handler
  - **Target Routes:** `/suppliers`, `/customers`, `/purchase-orders`, `/accounts-receivable`
  - **Benefit:** Improved discoverability and navigation
  - **Priority:** High

- [ ] **Sidebar Icons**
  - **File:** `frontend/src/components/Layout/Sidebar.tsx`
  - **Action:** Ensure all navigation icons use consistent color (`text-white` or `text-gray-200`)
  - **Benefit:** Visual consistency
  - **Priority:** Medium

---

## 2. Layout & Search (UX)

**Goal:** Optimize search placement and sidebar behavior.

### Tasks

- [ ] **Global Search**
  - **From:** `frontend/src/components/Layout/Sidebar.tsx`
  - **To:** `frontend/src/components/Layout/Header.tsx`
  - **Action:** Move Search Bar to top header (centrally located or near user profile)
  - **Benefit:** Easy access, follows industry standard patterns
  - **Priority:** High

- [ ] **Sidebar Stability**
  - **File:** `frontend/src/components/Layout/Sidebar.tsx`
  - **Action:** Use `absolute` positioning or fixed width transitions
  - **Issue:** Expanding/collapsing causes main content to shift
  - **Benefit:** Smooth transitions, no content reflow
  - **Priority:** High

---

## 3. Data Entry Validation (Functional)

**Goal:** Enforce standard formats for Contacts, States, and Zips.

**Target Pages:** `/suppliers` and `/customers`

### Tasks

- [ ] **Phone Formatting**
  - **Files:** 
    - `frontend/src/pages/Suppliers.tsx` (Add/Edit forms)
    - `frontend/src/pages/Customers.tsx` (Add/Edit forms)
  - **Action:** Use masking library (e.g., `react-input-mask`) for format: `(XXX) XXX-XXXX`
  - **Benefit:** Data consistency, improved UX
  - **Priority:** High

- [ ] **Contact Types**
  - **Files:** Same as above
  - **Action:** Add "Type" selector (Mobile vs. Office) or split into two fields: `mobile_phone` and `office_phone`
  - **Benefit:** Better contact management
  - **Priority:** Medium

- [ ] **State Dropdown**
  - **Files:** Same as above
  - **Action:** Replace free-text "State" input with `<Select>` component
  - **Data Source:** US State Abbreviations (50 states)
  - **Benefit:** Data validation, prevent typos
  - **Priority:** High

- [ ] **Zip Code Validation**
  - **Files:** Same as above
  - **Action:** Enforce 5-digit limit (`maxLength={5}` and regex `^\d{5}$`)
  - **Benefit:** Data integrity
  - **Priority:** Medium

---

## 4. Visualization (Feature)

**Goal:** Make charts interactive and configurable.

### Tasks

- [ ] **Configurable Charts**
  - **File:** `frontend/src/pages/Dashboard.tsx`
  - **Action:** Add dropdown/toggle to switch chart metrics
  - **Options:**
    - "By Revenue" vs "By Volume"
    - "Last 30 Days" vs "YTD"
  - **Benefit:** Flexible data exploration
  - **Priority:** Medium

---

## 5. Missing Core Pages (New Feature Scaffolding)

**Goal:** Eliminate "Blank Pages" by implementing functional views.

### Tasks

#### 5.1 Cockpit (Schedule Slots)

- [ ] **Implementation**
  - **File:** `frontend/src/pages/Cockpit.tsx` (create if missing)
  - **Requirement:** Scheduler/Grid view showing "Schedule Slots" grouped by Customer and Supplier
  - **Action:**
    1. Use table or calendar component for slot display
    2. Show availability status (Available, Booked, Pending)
    3. Enable filtering by date range
    4. Add "Book Slot" action button
  - **Priority:** High

#### 5.2 Processes

- [ ] **Implementation**
  - **File:** `frontend/src/pages/Processes.tsx` (create if missing)
  - **Requirement:** Display active business processes/workflows
  - **Action:**
    1. Create data table with columns: ID, Type, Status, Last Updated
    2. Add status badges (Running, Completed, Failed)
    3. Enable sorting and filtering
    4. Add "View Details" action
  - **Priority:** Medium

#### 5.3 Reports (Customizable)

- [ ] **Implementation**
  - **File:** `frontend/src/pages/Reports.tsx` (create if missing)
  - **Requirement:** Dashboard of available reports with customization
  - **Action:**
    1. Create "Report Library" grid view
    2. Add filter/checkbox: "Show only reports I want to see"
    3. Persist preferences to localStorage or user preferences API
    4. Add "Run Report" and "Schedule Report" actions
  - **Priority:** Medium

---

## 6. Critical Bug Fixes

**Goal:** Resolve page load failures.

**Priority:** 🔴 HIGH (Blocker)

### Tasks

#### 6.1 Customers Page Crash

- [ ] **Investigation & Fix**
  - **URL:** `/customers`
  - **Issue:** Page fails to load (JS error or API 500)
  - **Action:**
    1. Check Browser Console for "Uncaught TypeError"
    2. Check Network Tab for 500/404 errors
    3. **If API error:** Verify `backend/apps/tenants/customers/views.py` handles `tenant_id` correctly
    4. **If Frontend error:** Verify `CustomerList` component handles empty/null data gracefully
  - **Testing:**
    - Test with empty customer list
    - Test with mock API errors
    - Test with different tenant contexts
  - **Priority:** 🔴 Critical

---

## Implementation Guidelines

### Phase 3 Standards

1. **Use Semantic Design System**
   - All new components must use CSS variables from `index.css`
   - Use semantic UI components from `components/ui/`
   - Follow color semantics: `primary`, `surface`, `danger` (not hex codes)

2. **TypeScript Enforcement**
   - All new files must be `.tsx` with proper types
   - No `any` types allowed
   - Define interfaces for all props and API responses

3. **Accessibility**
   - ARIA labels for all interactive elements
   - Keyboard navigation support
   - Minimum color contrast 4.5:1

4. **Performance**
   - Use React.memo for expensive components
   - Lazy load routes with `React.lazy()`
   - Debounce search inputs

5. **Testing**
   - Unit tests for utility functions
   - Integration tests for critical flows
   - Manual testing checklist before PR

---

## Testing Checklist

### Before Creating PR

- [ ] TypeScript compilation passes (`npm run type-check`)
- [ ] Build succeeds (`npm run build`)
- [ ] Linting passes (`npm run lint`)
- [ ] No console errors in development
- [ ] Tested in Chrome, Firefox, Safari
- [ ] Tested on mobile viewport
- [ ] Tested with empty/error states
- [ ] Tested with tenant switching

---

## Dependencies

### Required Packages

```json
{
  "react-input-mask": "^3.0.0",    // Phone formatting
  "date-fns": "^2.30.0",           // Date utilities
  "recharts": "^2.10.0"            // Already installed (charts)
}
```

### Installation

```bash
cd frontend
npm install react-input-mask date-fns
```

---

## File Structure

```
frontend/src/
├── pages/
│   ├── Dashboard.tsx           (Update: clickable cards, icons)
│   ├── Suppliers.tsx           (Update: validation)
│   ├── Customers.tsx           (Fix: crash, validation)
│   ├── Cockpit.tsx             (Create: schedule slots)
│   ├── Processes.tsx           (Create: workflow list)
│   └── Reports.tsx             (Create: report library)
├── components/
│   ├── Layout/
│   │   ├── Header.tsx          (Update: add search)
│   │   └── Sidebar.tsx         (Update: stability, icons)
│   ├── ui/
│   │   ├── Select.tsx          (Create: state dropdown)
│   │   ├── PhoneInput.tsx      (Create: masked input)
│   │   └── Badge.tsx           (Create: status badges)
│   └── Charts/
│       └── ConfigurableChart.tsx (Create: interactive charts)
└── utils/
    ├── constants/
    │   └── states.ts           (Create: US state list)
    └── validation/
        └── phoneUtils.ts       (Create: phone formatting)
```

---

## Progress Tracking

### Sprint 1 (Week 1-2)
- [ ] Critical bug fixes (Section 6)
- [ ] Layout improvements (Section 2)
- [ ] Dashboard navigation (Section 1)

### Sprint 2 (Week 3-4)
- [ ] Data validation (Section 3)
- [ ] Visualization (Section 4)

### Sprint 3 (Week 5-6)
- [ ] Missing pages (Section 5)
- [ ] Final polish and testing

---

## Success Criteria

- ✅ Zero critical bugs in production
- ✅ All pages load successfully
- ✅ Consistent iconography and colors
- ✅ Smooth sidebar transitions
- ✅ Phone numbers formatted consistently
- ✅ State selection uses dropdown
- ✅ Charts are interactive
- ✅ All core pages have functional content

---

## Related Documentation

- **Semantic Design System:** `docs/SEMANTIC_DESIGN_SYSTEM.md`
- **Component Library:** `frontend/src/components/ui/README.md`
- **Multi-Tenancy:** `docs/ARCHITECTURE.md`

---

**Last Updated:** January 5, 2026  
**Maintained By:** Frontend Team  
**Status:** 🚧 In Progress
