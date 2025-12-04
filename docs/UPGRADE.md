# Upgrade Guide

This document tracks major version upgrades and breaking changes that require developer attention.

---

## React 19 and TypeScript 5.9 Upgrade (2025-12-04)

### Changes
- **React**: Upgraded from 18.2.0 to 19.0.0
- **React DOM**: Upgraded from 18.2.0 to 19.0.0
- **TypeScript**: Upgraded from 4.9.5 to 5.9.0
- **React Types**: Updated @types/react and @types/react-dom to v19

### Breaking Changes & Migration Notes

#### React 19 Breaking Changes
1. **Ref Handling**: React 19 no longer uses `forwardRef` for components - refs are now passed as regular props
2. **New Hooks**: `use()` hook for reading promises and context
3. **Server Components**: Enhanced support for React Server Components (not used in our app yet)
4. **Deprecated APIs Removed**: Some legacy APIs from React 17/18 may no longer work

#### TypeScript 5.9 Breaking Changes
1. **Stricter Type Checking**: May catch previously missed type errors
2. **New Module Resolution**: Better ESM support
3. **Decorator Updates**: If using decorators, syntax may need updates

### Action Required
- Review all `forwardRef` usage and update to new ref prop pattern
- Test all components thoroughly
- Update any custom hooks that rely on React internals
- Fix any new TypeScript errors that surface

### Testing
Run the following to ensure compatibility:
```bash
cd frontend
npm run type-check  # TypeScript validation
npm run test:ci     # Unit tests
npm run build       # Production build
```

### Compatibility Notes
- **react-scripts@5.0.1** has peer dependency warnings with TypeScript 5.9 (expects ^4.x)
- This is non-blocking but may require updating to react-scripts@6.x in future
- All current functionality remains operational

### References
- [React 19 Changelog](https://react.dev/blog/2024/04/25/react-19)
- [TypeScript 5.9 Release Notes](https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/)

---

## Multi-Tenancy Guardrails Enforcement (2025-12-04)

### Changes
- Updated all deployment workflows to use `migrate_schemas` instead of `migrate`
- Added `--fake-initial` flag for idempotent migrations
- Enforced SCHEMAS_FIRST pattern across dev, UAT, and production

### Migration Commands
```bash
# Shared schema (public)
python backend/manage.py migrate_schemas --shared --fake-initial --noinput

# Create super tenant
python backend/manage.py create_super_tenant --no-input

# Tenant schemas
python backend/manage.py migrate_schemas --tenant --fake-initial --noinput
```

### Why This Matters
- **Idempotency**: `--fake-initial` allows safe re-runs without duplicating migrations
- **Multi-Tenancy**: `migrate_schemas` properly handles both public and tenant schemas
- **Deployment Safety**: Prevents race conditions and schema corruption

### Affected Workflows
- `.github/workflows/11-dev-deployment.yml`
- `.github/workflows/12-uat-deployment.yml`
- `.github/workflows/13-prod-deployment.yml`

---

## Future Upgrades

### Planned
- React Scripts 6.x (to resolve TypeScript 5.9 peer dependency warnings)
- Node 20 LTS (currently on Node 18)
- Django 5.0 (currently on Django 4.2.7)

### Under Consideration
- React Server Components adoption
- Next.js migration (long-term strategic decision)
- Vite replacement for Create React App

---

*Last Updated: 2025-12-04*
