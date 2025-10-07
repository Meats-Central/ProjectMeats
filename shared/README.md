# Shared Utilities

This directory contains shared utility functions and constants that can be used across multiple platforms (frontend web, mobile, etc.).

## Purpose

To maintain DRY (Don't Repeat Yourself) principles and ensure consistency across platforms, common utilities are centralized here.

## Usage

### Frontend (React Web App)
```typescript
import { formatCurrency, CONSTANTS } from '@/shared/utils';
// or via the re-export in frontend/src/shared/utils.ts
import { formatCurrency } from '../shared/utils';
```

### Mobile (React Native)
```typescript
import { formatCurrency, CONSTANTS } from '../shared/utils';
// This re-exports from ../../shared/utils
```

## Adding New Utilities

When adding new utilities:
1. Add them to `shared/utils.ts` at the root level
2. Ensure they work in both browser and React Native environments
3. Document the function with JSDoc comments
4. Add unit tests if applicable

## Available Utilities

- **Formatting**: `formatCurrency`, `formatDate`, `formatDateTime`, `formatFileSize`
- **Validation**: `isValidEmail`, `isValidPhone`, `isValidTenantRole`
- **Text Processing**: `generateSlug`, `truncateText`, `capitalizeWords`
- **User Utilities**: `getUserDisplayName`, `isTenantTrialExpired`, `getTrialDaysRemaining`
- **UI Helpers**: `generateRandomColor`, `debounce`
- **Error Handling**: `getErrorMessage`, `isNetworkError`
- **Constants**: `CONSTANTS` object with tenant roles, pagination size, file limits, etc.
