# ProjectMeats Frontend UI/UX Standards

## 🎨 Theme System

### Overview
ProjectMeats uses a **semantic design system** with CSS custom properties that automatically adapt to:
- Light/Dark mode toggle
- Tenant-specific branding colors
- Responsive breakpoints

### CSS Custom Properties (ALWAYS USE THESE)

```css
/* Background Colors */
--color-background: /* Main background */
--color-surface: /* Card/panel backgrounds */
--color-surface-hover: /* Hover states */

/* Text Colors */
--color-text-primary: /* Primary text */
--color-text-secondary: /* Secondary/muted text */

/* UI Colors */
--color-primary: /* Primary brand color (tenant-specific) */
--color-border: /* Borders and dividers */
--color-error: /* Error states */
--color-success: /* Success states */
--color-warning: /* Warning states */

/* Radii */
--radius-sm: 0.375rem
--radius-md: 0.5rem
--radius-lg: 0.75rem

/* Shadows */
--shadow-sm: /* Small elevation */
--shadow-md: /* Medium elevation */
--shadow-lg: /* Large elevation */
```

### ❌ NEVER Do This (Hardcoded Colors)
```tsx
// ❌ WRONG - Hardcoded color
color: #2c3e50;
background: #e9ecef;
border: 1px solid #dee2e6;
```

### ✅ ALWAYS Do This (Theme Variables)
```tsx
// ✅ CORRECT - Theme-aware
color: rgb(var(--color-text-primary));
background: rgb(var(--color-surface));
border: 1px solid rgb(var(--color-border));
```

## 📱 Responsive Design Standards

### Breakpoints (Tailwind/Styled-Components)
```css
/* Mobile First Approach */
/* Default: 0-640px (mobile) */

@media (min-width: 640px) { /* sm: tablets portrait */ }
@media (min-width: 768px) { /* md: tablets landscape */ }
@media (min-width: 1024px) { /* lg: desktops */ }
@media (min-width: 1280px) { /* xl: large desktops */ }
```

### Required Patterns

#### Layout Stacking
```tsx
// ✅ CORRECT - Responsive grid
const Container = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  
  @media (min-width: 768px) {
    grid-template-columns: 1fr 1fr;
  }
  
  @media (min-width: 1024px) {
    grid-template-columns: 1fr 2fr 1fr;
  }
`;
```

#### Responsive Tables
```tsx
// ✅ CORRECT - No horizontal scroll on desktop
const TableWrapper = styled.div`
  overflow-y: auto;
  
  /* Only enable horizontal scroll on mobile when needed */
  @media (max-width: 768px) {
    overflow-x: auto;
  }
`;
```

#### Mobile-Friendly Buttons
```tsx
// ✅ CORRECT - Full width on mobile
const ButtonGroup = styled.div`
  display: flex;
  gap: 0.75rem;
  
  @media (max-width: 640px) {
    flex-direction: column;
    
    button {
      width: 100%;
    }
  }
`;
```

## 🧩 Shared Components

### When to Create Shared Components
- ✅ Used in 3+ places
- ✅ Encapsulates common pattern
- ✅ Benefits from centralized updates

### When to Keep Local
- ✅ Unique to one page/feature
- ✅ Complex business logic
- ✅ Frequent customization needed

### Available Shared Components

#### Modal (Portal-Based)
```tsx
import Modal from '@/components/Modal/Modal';

<Modal 
  isOpen={showModal} 
  onClose={() => setShowModal(false)} 
  title="My Modal"
  maxWidth="700px"
  footer={
    <>
      <CancelButton onClick={onClose}>Cancel</CancelButton>
      <SubmitButton onClick={onSubmit}>Submit</SubmitButton>
    </>
  }
>
  <p>Modal content here</p>
</Modal>
```

#### ActivityFeed
```tsx
import { ActivityFeed } from '@/components/Shared/ActivityFeed';

<ActivityFeed
  entityType="purchase_order"
  entityId={orderId}
  showCreateForm
  maxHeight="500px"
/>
```

#### ScheduleCallModal
```tsx
import { ScheduleCallModal } from '@/components/Shared/ScheduleCallModal';

<ScheduleCallModal
  isOpen={show}
  onClose={handleClose}
  onSuccess={handleSuccess}
  initialData={call} // For editing
/>
```

## 📋 Forms & Validation

### Standard Form Pattern
```tsx
import { useState } from 'react';

const MyForm = () => {
  const [formData, setFormData] = useState({ name: '', email: '' });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrors({});
    
    try {
      await apiClient.post('/endpoint', formData);
      onSuccess();
    } catch (err: any) {
      setErrors(err.response?.data || { general: 'Failed to submit' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <FormGroup>
        <Label>Name *</Label>
        <Input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          disabled={submitting}
        />
        {errors.name && <ErrorMessage>{errors.name}</ErrorMessage>}
      </FormGroup>
      
      <SubmitButton type="submit" disabled={submitting}>
        {submitting ? 'Submitting...' : 'Submit'}
      </SubmitButton>
    </form>
  );
};
```

## 🎭 Status Badges

### Standard Status Colors
```tsx
// ✅ CORRECT - Consistent status colors across app
const StatusBadge = styled.span<{ status: string }>`
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  
  ${props => {
    switch (props.status) {
      case 'success':
      case 'completed':
      case 'paid':
        return `
          background: rgba(34, 197, 94, 0.15);
          color: rgb(34, 197, 94);
        `;
      case 'warning':
      case 'pending':
      case 'partial':
        return `
          background: rgba(234, 179, 8, 0.15);
          color: rgba(234, 179, 8, 1);
        `;
      case 'error':
      case 'failed':
      case 'overdue':
      case 'unpaid':
        return `
          background: rgba(239, 68, 68, 0.15);
          color: rgb(239, 68, 68);
        `;
      default:
        return `
          background: rgba(59, 130, 246, 0.15);
          color: rgb(59, 130, 246);
        `;
    }
  }}
`;
```

## 🔍 Accessibility Standards

### Required Practices
1. ✅ Use semantic HTML (`<button>`, `<nav>`, `<main>`, `<article>`)
2. ✅ Add ARIA labels to interactive elements
3. ✅ Ensure keyboard navigation works (Tab, Enter, Escape)
4. ✅ Minimum color contrast: 4.5:1 for normal text
5. ✅ Focus indicators visible and clear
6. ✅ Test with screen readers

### Example
```tsx
<button
  onClick={handleClick}
  aria-label="Close modal"
  aria-describedby="modal-description"
  disabled={loading}
>
  <CloseIcon aria-hidden="true" />
</button>
```

## 🧪 Testing Checklist

### Before Committing
- [ ] Works in both light and dark modes
- [ ] Responsive on mobile (320px), tablet (768px), desktop (1024px+)
- [ ] No horizontal scroll on any screen size
- [ ] All text readable (contrast ratio)
- [ ] Keyboard navigation works
- [ ] No console errors or warnings
- [ ] Follows theme variable conventions
- [ ] Matches existing page patterns

## 📦 Component Creation Checklist

### Before Creating New Component
1. [ ] Check if similar component exists
2. [ ] Determine if truly reusable (3+ use cases)
3. [ ] Plan props interface with TypeScript
4. [ ] Use theme variables (no hardcoded colors)
5. [ ] Add responsive breakpoints
6. [ ] Include accessibility features
7. [ ] Document usage with examples
8. [ ] Export from index.ts

## 🚀 Performance Best Practices

### React Optimization
```tsx
// ✅ Memoize expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  return <ComplexView data={data} />;
});

// ✅ Memoize expensive calculations
const memoizedValue = useMemo(() => {
  return computeExpensiveValue(a, b);
}, [a, b]);

// ✅ Memoize callbacks
const memoizedCallback = useCallback(() => {
  doSomething(a, b);
}, [a, b]);
```

### List Rendering
```tsx
// ✅ CORRECT - Stable keys
items.map(item => <Item key={item.id} data={item} />)

// ❌ WRONG - Index as key (unstable)
items.map((item, index) => <Item key={index} data={item} />)
```

## 🔗 Related Documentation
- `/docs/ARCHITECTURE.md` - System architecture
- `/docs/CONFIGURATION_AND_SECRETS.md` - Environment setup
- `/frontend/src/config/theme.ts` - Theme configuration
- `/.copilotignore` - Excluded patterns

## 📝 Change Log
- **2026-01-10**: Initial UI Standards documentation
- **2026-01-10**: Updated Modal component with theme variables
- **2026-01-10**: Documented responsive table patterns

---

**Maintained By**: Frontend Team  
**Last Updated**: 2026-01-10  
**Status**: ✅ Active
