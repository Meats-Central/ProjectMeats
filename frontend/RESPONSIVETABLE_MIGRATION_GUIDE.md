# ResponsiveTable Component Migration Guide

## Overview
This guide helps you migrate existing custom table implementations to use the shared `ResponsiveTable` component, reducing code duplication and ensuring consistent styling across the application.

## Benefits of Migration
- ✅ **DRY Principle**: Eliminate 100-200 lines of duplicate table styled-components
- ✅ **Consistent Styling**: Automatic theme compliance across all tables
- ✅ **Built-in Features**: Sorting, loading states, empty states included
- ✅ **Responsive Design**: Mobile/tablet/desktop breakpoints handled automatically
- ✅ **Type Safety**: TypeScript generics ensure type-safe data handling
- ✅ **Maintainability**: Bug fixes and enhancements benefit all tables

## Migration Steps

### Step 1: Analyze Current Implementation

Before migrating, document your current table's:

1. **Data Structure**: What interface/type describes your row data?
2. **Columns**: What columns are displayed? Which are sortable?
3. **Custom Rendering**: Do any columns have custom render logic (badges, buttons, links)?
4. **Actions**: Are there row-level actions (edit, delete, view)?
5. **Filtering**: Is there client-side or server-side filtering?

**Example Analysis (PayablePOs.tsx):**
```typescript
// Data structure
interface PurchaseOrder {
  id: number;
  order_number: string;
  supplier_name?: string;
  order_date: string;
  total_amount: string;
  payment_status?: 'unpaid' | 'partial' | 'paid';
  // ...
}

// Current columns
- Order # (sortable, clickable)
- Supplier (sortable)
- Order Date (sortable)
- Total Amount (sortable, formatted as currency)
- Payment Status (custom badge rendering)
- Actions (custom buttons: view, record payment)

// Current features
- Click row to open side panel
- Filter by payment status (unpaid/partial/paid)
- Record payment modal
- Activity feed integration
```

### Step 2: Define Column Configuration

Create your column configuration array using the ResponsiveTable `Column<T>` interface:

```typescript
import { Column } from '../components/Shared/ResponsiveTable';

const columns: Column<PurchaseOrder>[] = [
  {
    key: 'order_number',
    label: 'Order #',
    sortable: true,
    render: (order) => (
      <OrderNumberLink onClick={() => handleOrderClick(order)}>
        {order.order_number}
      </OrderNumberLink>
    )
  },
  {
    key: 'supplier_name',
    label: 'Supplier',
    sortable: true
  },
  {
    key: 'order_date',
    label: 'Order Date',
    sortable: true,
    render: (order) => formatDateLocal(order.order_date)
  },
  {
    key: 'total_amount',
    label: 'Total Amount',
    sortable: true,
    render: (order) => formatCurrency(parseFloat(order.total_amount))
  },
  {
    key: 'payment_status',
    label: 'Status',
    render: (order) => (
      <StatusBadge status={order.payment_status || 'unpaid'}>
        {order.payment_status || 'unpaid'}
      </StatusBadge>
    )
  },
  {
    key: 'actions',
    label: 'Actions',
    render: (order) => (
      <ActionButtons>
        <ActionButton onClick={() => handleRecordPayment(order)}>
          Record Payment
        </ActionButton>
      </ActionButtons>
    )
  }
];
```

### Step 3: Replace Custom Table Components

**BEFORE (Custom Implementation):**
```typescript
const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  @media (max-width: 768px) {
    min-width: 600px;
  }
`;

const TableHeader = styled.thead`
  background: rgb(var(--color-background));
  border-bottom: 1px solid rgb(var(--color-border));
  position: sticky;
  top: 0;
  z-index: 10;
`;

const TableRow = styled.tr<{ clickable?: boolean }>`
  border-bottom: 1px solid rgb(var(--color-border));
  cursor: ${props => props.clickable ? 'pointer' : 'default'};
  &:hover {
    background: rgba(var(--color-primary), 0.08);
  }
`;

// ... 50-100 more lines of styled components
```

**AFTER (ResponsiveTable):**
```typescript
import ResponsiveTable from '../components/Shared/ResponsiveTable';

<ResponsiveTable
  data={purchaseOrders}
  columns={columns}
  loading={loading}
  emptyMessage="No purchase orders found"
  onRowClick={(order) => handleOrderClick(order)}
/>
```

**Savings:** ~150 lines of code removed

### Step 4: Handle Row Click Events (Optional)

If your table supports clicking rows:

```typescript
const handleRowClick = (order: PurchaseOrder) => {
  setSelectedOrder(order);
  // Open side panel, modal, navigate, etc.
};

<ResponsiveTable
  data={purchaseOrders}
  columns={columns}
  onRowClick={handleRowClick}
/>
```

### Step 5: Preserve Custom Styled Components

Keep only the custom styled components that are unique to your page:

```typescript
// KEEP - These are page-specific
const StatusBadge = styled.span<{ status: string }>`
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  ${props => {
    switch (props.status) {
      case 'paid':
        return 'background: rgba(34, 197, 94, 0.15); color: rgba(34, 197, 94, 1);';
      case 'partial':
        return 'background: rgba(234, 179, 8, 0.15); color: rgba(234, 179, 8, 1);';
      case 'unpaid':
      default:
        return 'background: rgba(239, 68, 68, 0.15); color: rgba(239, 68, 68, 1);';
    }
  }}
`;

const ActionButton = styled.button`
  background: rgb(var(--color-primary));
  color: white;
  border: none;
  padding: 0.375rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s ease;

  &:hover {
    opacity: 0.9;
  }
`;

// REMOVE - These are now handled by ResponsiveTable
// - Table, TableHeader, TableRow, TableHead, TableCell, TableWrapper, TableContainer
```

### Step 6: Test Thoroughly

After migration, verify:

1. **✅ Visual Appearance**: Table looks the same or better
2. **✅ Sorting**: Click column headers to sort data
3. **✅ Responsive Behavior**: Test on mobile (320px), tablet (768px), desktop (1024px+)
4. **✅ Row Click**: If applicable, clicking rows triggers correct action
5. **✅ Custom Rendering**: Status badges, buttons, links render correctly
6. **✅ Loading State**: Loading indicator appears when `loading={true}`
7. **✅ Empty State**: Empty message appears when `data={[]}`
8. **✅ Theme Compliance**: Toggle light/dark mode, verify colors update

### Step 7: Clean Up (Optional)

After successful migration:

1. Remove old table styled-components
2. Remove custom sorting logic (if any)
3. Remove custom loading/empty states
4. Update imports
5. Run ESLint to catch any issues

## Complete Migration Example

### Before: PayablePOs.tsx (547 lines)

```typescript
// 150+ lines of styled components for table structure
const Table = styled.table`...`;
const TableHeader = styled.thead`...`;
const TableRow = styled.tr`...`;
// ... etc

// 50+ lines of manual table rendering
<TableContainer>
  <TableWrapper>
    <Table>
      <TableHeader>
        <tr>
          <TableHead onClick={() => handleSort('order_number')}>
            Order # {sortColumn === 'order_number' && (sortDirection === 'asc' ? '↑' : '↓')}
          </TableHead>
          <TableHead onClick={() => handleSort('supplier_name')}>
            Supplier {sortColumn === 'supplier_name' && (sortDirection === 'asc' ? '↑' : '↓')}
          </TableHead>
          {/* ... more headers */}
        </tr>
      </TableHeader>
      <tbody>
        {filteredAndSortedOrders.map(order => (
          <TableRow key={order.id} clickable onClick={() => handleRowClick(order)}>
            <TableCell>{order.order_number}</TableCell>
            <TableCell>{order.supplier_name}</TableCell>
            {/* ... more cells */}
          </TableRow>
        ))}
      </tbody>
    </Table>
  </TableWrapper>
</TableContainer>

// 30+ lines of sorting logic
const [sortColumn, setSortColumn] = useState('order_date');
const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

const handleSort = (column: keyof PurchaseOrder) => {
  if (sortColumn === column) {
    setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
  } else {
    setSortColumn(column);
    setSortDirection('asc');
  }
};

const sortedOrders = [...orders].sort((a, b) => {
  // 20+ lines of sorting logic
});
```

### After: PayablePOs.tsx (~400 lines, -147 lines)

```typescript
import ResponsiveTable, { Column } from '../../components/Shared/ResponsiveTable';

// 10 lines of column configuration
const columns: Column<PurchaseOrder>[] = [
  { key: 'order_number', label: 'Order #', sortable: true },
  { key: 'supplier_name', label: 'Supplier', sortable: true },
  { 
    key: 'order_date', 
    label: 'Order Date', 
    sortable: true,
    render: (order) => formatDateLocal(order.order_date)
  },
  { 
    key: 'total_amount', 
    label: 'Total Amount', 
    sortable: true,
    render: (order) => formatCurrency(parseFloat(order.total_amount))
  },
  {
    key: 'payment_status',
    label: 'Status',
    render: (order) => <StatusBadge status={order.payment_status || 'unpaid'}>{order.payment_status || 'unpaid'}</StatusBadge>
  },
  {
    key: 'actions',
    label: 'Actions',
    render: (order) => (
      <ActionButton onClick={(e) => { e.stopPropagation(); handleRecordPayment(order); }}>
        Record Payment
      </ActionButton>
    )
  }
];

// 3 lines to render table
<ResponsiveTable
  data={filteredOrders}
  columns={columns}
  loading={loading}
  emptyMessage="No purchase orders found"
  onRowClick={handleRowClick}
/>

// Keep only page-specific styled components (StatusBadge, ActionButton, etc.)
```

**Result:** 
- 147 lines removed
- Sorting logic eliminated (built-in)
- Loading/empty states handled automatically
- Responsive design guaranteed
- Theme compliance ensured

## Migration Checklist

### Pre-Migration
- [ ] Document current table structure and features
- [ ] Identify custom rendering requirements
- [ ] Note any special interactions (row click, inline edit, etc.)
- [ ] List all styled components to be replaced

### During Migration
- [ ] Create column configuration array
- [ ] Replace custom table components with ResponsiveTable
- [ ] Implement custom render functions for complex columns
- [ ] Handle row click events if needed
- [ ] Remove redundant sorting logic
- [ ] Keep only page-specific styled components

### Post-Migration
- [ ] Test visual appearance (same or better)
- [ ] Test sorting functionality
- [ ] Test responsive behavior (mobile/tablet/desktop)
- [ ] Test row interactions
- [ ] Test loading and empty states
- [ ] Test theme compliance (light/dark mode)
- [ ] Remove old styled components
- [ ] Update documentation if needed

## Common Patterns

### Pattern 1: Clickable Order Number
```typescript
{
  key: 'order_number',
  label: 'Order #',
  sortable: true,
  render: (order) => (
    <OrderNumberLink onClick={(e) => { e.stopPropagation(); navigate(`/orders/${order.id}`); }}>
      {order.order_number}
    </OrderNumberLink>
  )
}
```

### Pattern 2: Status Badge
```typescript
{
  key: 'status',
  label: 'Status',
  render: (row) => <StatusBadge status={row.status}>{row.status}</StatusBadge>
}
```

### Pattern 3: Action Buttons
```typescript
{
  key: 'actions',
  label: 'Actions',
  render: (row) => (
    <ActionButtons>
      <IconButton onClick={(e) => { e.stopPropagation(); handleEdit(row); }}>✏️</IconButton>
      <IconButton onClick={(e) => { e.stopPropagation(); handleDelete(row); }}>🗑️</IconButton>
    </ActionButtons>
  )
}
```

### Pattern 4: Formatted Currency
```typescript
{
  key: 'amount',
  label: 'Amount',
  sortable: true,
  render: (row) => formatCurrency(parseFloat(row.amount))
}
```

### Pattern 5: Formatted Date
```typescript
{
  key: 'created_date',
  label: 'Created',
  sortable: true,
  render: (row) => formatDateLocal(row.created_date)
}
```

## Pages Ready for Migration

### High Priority (Similar Patterns)
1. **PayablePOs.tsx** (547 lines) - Estimated savings: ~150 lines
2. **Invoices.tsx** (663 lines) - Estimated savings: ~150 lines
3. **ReceivableSOs.tsx** (547 lines) - Estimated savings: ~150 lines
4. **SalesOrders.tsx** (673 lines) - Estimated savings: ~150 lines

**Total Estimated Savings: ~600 lines of duplicate code**

### Lower Priority (Uses Ant Design)
- Locations.tsx (already uses Ant Design Table)
- Plants.tsx (already uses Ant Design Table)

## FAQ

### Q: What if my table has complex interactions?
**A:** Use the `onRowClick` prop for row-level actions, and use `e.stopPropagation()` in column render functions for cell-level actions (buttons, links).

### Q: Can I customize the table styling?
**A:** ResponsiveTable uses theme variables. If you need table-specific styling, wrap it in a styled div with custom CSS.

### Q: What about pagination?
**A:** ResponsiveTable handles client-side display. For server-side pagination, pass filtered/paginated data and handle pagination in your component.

### Q: How do I handle complex sorting?
**A:** ResponsiveTable sorts by the column key. For complex sorting (nested objects, dates), transform your data before passing to the table.

### Q: Can I mix sortable and non-sortable columns?
**A:** Yes! Set `sortable: true` only for columns that should be sortable.

## Support

For questions or issues:
1. Review ResponsiveTable component source code (`frontend/src/components/Shared/ResponsiveTable.tsx`)
2. Check UI_STANDARDS.md for theme compliance guidelines
3. Ask in #frontend channel

## Next Steps

1. **Choose a table to migrate** (start with PayablePOs.tsx or ReceivableSOs.tsx)
2. **Create a feature branch** (`feat/migrate-payable-pos-table`)
3. **Follow the migration steps** in this guide
4. **Test thoroughly** using the checklist
5. **Submit PR** with before/after screenshots
6. **Repeat** for remaining tables

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-10  
**Maintained By:** UI Standardization Team
