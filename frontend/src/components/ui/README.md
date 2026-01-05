# Semantic UI Components

## Overview

This directory contains **semantic UI components** that use CSS variables for styling. These components are designed to work with ProjectMeats' **tenant-specific branding system**.

## Key Principle: Separation of Structure and Appearance

### Before (Hardcoded Colors)
```tsx
const Button = styled.button`
  background-color: #DC2626;  /* ❌ Hardcoded red */
  color: white;
`;
```

### After (Semantic Design System)
```tsx
const Button = styled.button`
  background-color: rgb(var(--color-primary));  /* ✅ Tenant-specific */
  color: rgb(var(--color-primary-foreground));
`;
```

**Result**: The same component can be Meats Central red for one tenant, blue for another, without any code changes.

## Available Components

### 1. Button

```tsx
import { Button } from '@/components/ui';

<Button variant="primary" size="md" onClick={handleClick}>
  Save Changes
</Button>
```

**Variants**:
- `primary` - Uses `--color-primary` (tenant brand color)
- `secondary` - Uses `--color-secondary` (gray-800)
- `outline` - Transparent with border
- `ghost` - Transparent, hover effect only
- `danger` - Red for destructive actions

**Sizes**: `sm` | `md` | `lg`

### 2. Card

```tsx
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui';

<Card padding="md">
  <CardHeader 
    title="Dashboard" 
    description="Welcome back!"
    actions={<Button>New</Button>}
  />
  <CardContent>
    Your content here
  </CardContent>
  <CardFooter>
    Footer actions
  </CardFooter>
</Card>
```

### 3. PageContainer

```tsx
import { PageContainer } from '@/components/ui';

<PageContainer 
  title="Dashboard" 
  description="Manage your meat operations"
  actions={<Button>Add Item</Button>}
  maxWidth="lg"
>
  <Card>Content</Card>
</PageContainer>
```

**Max Width Options**:
- `sm` (640px)
- `md` (768px)
- `lg` (1024px)
- `xl` (1280px)
- `full` (100%, default)

## CSS Variables Reference

All components use semantic CSS variables defined in `src/index.css`:

### Brand Colors (Tenant-Specific)
```css
--color-primary          /* Main brand color */
--color-primary-hover    /* Hover state */
--color-primary-active   /* Active state */
--color-primary-foreground /* Text on primary */
```

### UI Colors (Standardized)
```css
--color-background       /* Page background */
--color-surface          /* Card/panel background */
--color-surface-hover    /* Hover state */
--color-text-primary     /* Main text */
--color-text-secondary   /* Muted text */
--color-border           /* Borders */
```

### Status Colors (Standardized)
```css
--color-success          /* Green */
--color-warning          /* Yellow */
--color-danger           /* Red */
--color-error            /* Error red */
--color-info             /* Blue */
```

## How Tenant Branding Works

1. **Tenant logs in** → Backend returns `primary_color_light` and `primary_color_dark`
2. **ThemeContext** injects colors into CSS variables via `injectTenantColors()`
3. **All components** automatically update because they reference CSS variables
4. **Zero re-renders** - CSS handles the repaint, not React

## Migration Guide

### Converting Old Components

**Before** (Hardcoded):
```tsx
const OldButton = styled.button`
  background-color: #DC2626;
  color: white;
  &:hover {
    background-color: #B91C1C;
  }
`;
```

**After** (Semantic):
```tsx
const NewButton = styled.button`
  background-color: rgb(var(--color-primary));
  color: rgb(var(--color-primary-foreground));
  &:hover {
    background-color: rgb(var(--color-primary-hover));
  }
`;
```

### Or Just Use the Component

```tsx
// Instead of creating your own styled button, use the semantic one:
import { Button } from '@/components/ui';

<Button variant="primary">Click Me</Button>
```

## Benefits

1. **Zero CSS Bloat** - One button style serves all tenants
2. **Instant Theme Changes** - CSS variables repaint without React re-renders
3. **Type Safety** - TypeScript ensures correct variant usage
4. **Consistent UX** - All buttons/cards look similar across the app
5. **Easy Maintenance** - Change once in `index.css`, applies everywhere

## Purpose
- Atomic UI components (buttons, inputs, cards, etc.)
- Fully typed with TypeScript
- Accessible (ARIA compliant)
- **NEW**: Semantic design system with CSS variables

## Notes

- All components use `styled-components` for styling
- CSS variables are defined in RGB format for alpha transparency support
- Dark theme overrides are handled via `[data-theme="dark"]` in `index.css`
- Components are fully responsive and accessible
