# ProjectMeats Frontend

React + TypeScript frontend application for ProjectMeats business management system with multi-tenancy support.

**Built with Vite** for fast builds and modern development experience.

## Table of Contents

- [Overview](#overview)
- [Multi-Tenancy Support](#multi-tenancy-support)
- [Getting Started](#getting-started)
- [Development](#development)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Architecture](#architecture)
- [Migration from CRA](#migration-from-cra)

## Overview

This is the frontend application for ProjectMeats, built with:

- **React 19.0.0** - Latest React with improved performance
- **TypeScript 4.9.5** - Type-safe JavaScript
- **Vite 6.4.1** - Next-generation frontend tooling (⚡ 10-100x faster HMR)
- **Ant Design 5.27.3** - UI component library
- **Axios 1.6.0** - HTTP client for API communication
- **React Router 6.30.1** - Client-side routing
- **Vitest** - Fast unit testing with Vite

## Multi-Tenancy Support

The frontend supports **multi-tenancy via domain detection**, allowing different organizations (tenants) to access their isolated data through tenant-specific subdomains.

### How It Works

The application automatically detects the tenant and environment from `window.location.hostname`:

#### Domain Patterns

| Domain | Tenant | Environment | API Endpoint |
|--------|--------|-------------|--------------|
| `localhost:3000` | `null` | development | `http://localhost:8000/api/v1` |
| `dev.projectmeats.com` | `null` | development | `http://localhost:8000/api/v1` |
| `uat.projectmeats.com` | `null` | uat | `https://uat-api.projectmeats.com/api/v1` |
| `projectmeats.com` | `null` | production | `https://api.projectmeats.com/api/v1` |
| `acme-dev.projectmeats.com` | `acme` | development | `http://acme-dev-api.projectmeats.com/api/v1` |
| `acme-uat.projectmeats.com` | `acme` | uat | `https://acme-uat-api.projectmeats.com/api/v1` |
| `acme.projectmeats.com` | `acme` | production | `https://acme-api.projectmeats.com/api/v1` |

### Key Features

✅ **Automatic tenant detection** from domain  
✅ **Environment-aware** API URL configuration  
✅ **Override support** via `window.ENV` for custom deployments  
✅ **Type-safe** TypeScript implementation  
✅ **Fully tested** with comprehensive unit tests  

### Tenant Context API

```typescript
import { getTenantContext, getCurrentTenant } from './config/tenantContext';

// Get full tenant context
const context = getTenantContext();
console.log(context.tenant);       // 'acme' or null
console.log(context.environment);  // 'development' | 'uat' | 'production'
console.log(context.apiBaseUrl);   // Tenant-specific API endpoint

// Get just the tenant identifier
const tenant = getCurrentTenant(); // 'acme' or null
```

### Configuration Priority

The API base URL is determined in this order:

1. **window.ENV.API_BASE_URL** - Runtime configuration (explicit override, highest priority)
2. **Tenant Context** - Extracted from domain (automatic detection)
3. **process.env.REACT_APP_API_BASE_URL** - Build-time environment variable
4. **Default value** - Fallback (lowest priority)

This allows deployment teams to explicitly override tenant detection when needed while still providing automatic detection by default.

### For Developers

#### Local Development

No special configuration needed! Just run:

```bash
npm start
```

The app will detect `localhost` and use:
- Tenant: `null` (no tenant)
- Environment: `development`
- API URL: `http://localhost:8000/api/v1`

#### Testing with Tenant Subdomains

To test tenant-specific behavior locally, you can modify your `/etc/hosts`:

```bash
# Add to /etc/hosts
127.0.0.1 acme-dev.localhost
127.0.0.1 tenant2-dev.localhost
```

Then access:
- `http://acme-dev.localhost:3000` - Tenant: `acme`
- `http://tenant2-dev.localhost:3000` - Tenant: `tenant2`

**Note**: You'll need to configure your backend to handle these tenant-specific requests.

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running (see backend README)

### Installation

```bash
# Install dependencies
npm ci

# Start development server
npm start
```

The application will open at `http://localhost:3000`.

## Development

### Available Scripts

```bash
# Development server with hot reload (Vite)
npm start
# or
npm run dev

# Run tests with Vitest
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage (CI mode)
npm run test:ci

# Build for production
npm run build

# Preview production build
npm run preview

# Type check without building
npm run type-check

# Lint code
npm run lint

# Auto-fix linting issues
npm run lint:fix

# Format code with Prettier
npm run format
```

### Project Structure

```
frontend/
├── public/              # Static assets (served as-is)
│   └── env-config.js    # Runtime configuration (can be replaced at deploy time)
├── src/
│   ├── components/      # Reusable UI components
│   ├── config/          # Configuration utilities
│   │   ├── runtime.ts           # Runtime configuration with multi-tenancy
│   │   ├── tenantContext.ts     # Tenant detection from domain
│   │   └── theme.ts             # Theme configuration
│   ├── contexts/        # React contexts (Auth, Theme, Navigation)
│   ├── pages/          # Page components
│   ├── services/       # API service layer
│   │   ├── apiService.ts        # Main API client
│   │   ├── authService.ts       # Authentication
│   │   └── tenantService.ts     # Tenant management
│   ├── types/          # TypeScript type definitions
│   ├── App.tsx         # Root component
│   ├── index.tsx       # Entry point
│   └── vite-env.d.ts   # Vite environment types
├── index.html          # HTML template (in root for Vite)
├── vite.config.ts      # Vite configuration
├── vitest.setup.ts     # Test setup
├── package.json
└── tsconfig.json
```

## Configuration

### Environment Variables

The frontend uses a hybrid configuration system that supports both build-time and runtime configuration.

#### Build-time Variables (`.env`)

**Note**: Vite uses `VITE_` prefix (not `REACT_APP_`):

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_ENVIRONMENT=development
VITE_AI_ASSISTANT_ENABLED=true
VITE_ENABLE_DOCUMENT_UPLOAD=true
```

Access in code:
```typescript
// Vite environment variables
const apiUrl = import.meta.env.VITE_API_BASE_URL;
const isDev = import.meta.env.MODE === 'development';
```

#### Runtime Variables (`public/env-config.js`)

For production deployments, you can override configuration at runtime:

```javascript
window.ENV = {
  API_BASE_URL: "https://api.example.com/api/v1",
  ENVIRONMENT: "production"
};
```

**Priority**: `window.ENV` → Tenant context → `import.meta.env.VITE_*` → defaults

See [RUNTIME_CONFIG.md](./RUNTIME_CONFIG.md) for detailed configuration guide.

## Testing

### Running Tests

The project uses **Vitest** for fast, Vite-native testing:

```bash
# Interactive watch mode
npm test

# With UI dashboard
npm run test:ui

# Single run with coverage (for CI)
npm run test:ci
```

### Test Coverage

The project maintains high test coverage for critical modules:

- **tenantContext.ts**: 100% coverage (domain detection logic)
- **runtime.ts**: 85%+ coverage (configuration management)

### Writing Tests

Tests are written using Vitest and React Testing Library:

```typescript
import { describe, it, expect } from 'vitest';
import { getTenantContext } from './config/tenantContext';

describe('getTenantContext', () => {
  it('should detect tenant from subdomain', () => {
    window.location.hostname = 'acme.projectmeats.com';
    const context = getTenantContext();
    expect(context.tenant).toBe('acme');
  });
});
```

## Deployment

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

### Deployment Options

#### Option 1: Static Hosting with Runtime Config

1. Build the application
2. Replace `build/env-config.js` with environment-specific values
3. Deploy to static hosting (Nginx, S3, etc.)

```bash
# Example: UAT deployment
cat > build/env-config.js <<JS
window.ENV = {
  API_BASE_URL: "https://uat-api.projectmeats.com/api/v1",
  ENVIRONMENT: "uat"
};
JS
```

#### Option 2: Docker Deployment

See deployment workflows in `.github/workflows/`:
- `11-dev-deployment.yml` - Development environment
- `12-uat-deployment.yml` - UAT/Staging environment
- `13-prod-deployment.yml` - Production environment

### Multi-Tenancy Deployment

For tenant-specific deployments:

1. **DNS Configuration**: Set up subdomains pointing to your server
   - `acme.projectmeats.com` → Your server IP
   - `acme-uat.projectmeats.com` → Your UAT server IP

2. **Backend Configuration**: Ensure backend handles tenant routing

3. **Frontend**: No special configuration needed! Domain detection is automatic.

## Architecture

### Multi-Tenancy Architecture

```
┌─────────────────────────────────────────────────────────┐
│              User visits domain                         │
│        (e.g., acme.projectmeats.com)                   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│         tenantContext.ts extracts:                      │
│         • Tenant: 'acme'                                │
│         • Environment: 'production'                     │
│         • API URL: https://acme-api.projectmeats.com    │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│      runtime.ts configures application with:            │
│      • config.API_BASE_URL (tenant-aware)               │
│      • config.ENVIRONMENT                               │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│     API services use tenant-aware config:               │
│     • apiService.ts                                     │
│     • authService.ts                                    │
│     • tenantService.ts                                  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│    All API requests go to correct endpoint              │
│    with proper tenant context headers                   │
└─────────────────────────────────────────────────────────┘
```

### API Client Configuration

All API services automatically use the tenant-aware configuration:

```typescript
// No changes needed in API calls!
import { apiService } from './services/apiService';

// Automatically uses correct API endpoint based on domain
const suppliers = await apiService.getSuppliers();
```

### Backward Compatibility

The multi-tenancy feature is **fully backward compatible**:

- Single-tenant deployments work without changes
- Existing environment variable configuration still works
- No breaking changes to existing code

## Troubleshooting

### Frontend hitting wrong API endpoint

1. Check browser console for tenant context logs (development mode)
2. Verify `window.location.hostname` is correct
3. Check if `window.ENV.API_BASE_URL` is overriding tenant context

### Tenant not detected correctly

1. Ensure domain follows naming convention (see [Domain Patterns](#domain-patterns))
2. Check for typos in subdomain
3. Verify DNS configuration

### Tests failing

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm ci

# Run tests
npm run test:ci
```

## Contributing

1. Follow existing code patterns and TypeScript best practices
2. Write tests for new features
3. Run linting and type checking before committing
4. Update documentation for significant changes

## Related Documentation

- [RUNTIME_CONFIG.md](./RUNTIME_CONFIG.md) - Detailed runtime configuration guide
- [Backend API Documentation](../backend/README.md)
- [Deployment Guide](../DEPLOYMENT_GUIDE.md)
- [Multi-Tenancy Guide](../docs/MULTI_TENANCY_GUIDE.md)

## Migration from CRA

### What Changed

The frontend has been migrated from **Create React App (CRA)** to **Vite** for improved developer experience and build performance.

#### Key Changes

1. **Build Tool**: Webpack → Vite
   - ⚡ 10-100x faster Hot Module Replacement (HMR)
   - ⚡ Instant server start (no bundling in dev mode)
   - ⚡ Faster production builds

2. **Environment Variables**: `REACT_APP_*` → `VITE_*`
   ```diff
   - REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
   + VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

3. **Environment Access**: `process.env` → `import.meta.env`
   ```diff
   - const apiUrl = process.env.REACT_APP_API_BASE_URL;
   + const apiUrl = import.meta.env.VITE_API_BASE_URL;
   ```

4. **Testing**: Jest → Vitest
   - Native Vite integration
   - Same API as Jest (compatible)
   - Faster test execution

5. **Configuration Files**:
   - Removed: `config-overrides.js`, `react-scripts`
   - Added: `vite.config.ts`, `vitest.setup.ts`

#### Backward Compatibility

The migration maintains **full backward compatibility**:
- Runtime configuration (`window.ENV`) still works
- Tenant detection unchanged
- API services unchanged
- No breaking changes to application code

#### Developer Benefits

- **Faster iteration**: HMR updates in <50ms
- **Modern tooling**: Native ESM, top-level await
- **Better DX**: Clearer error messages, faster TypeScript checking
- **Future-proof**: Vite is the standard for modern React apps

### Migration Guide for Developers

If you have local environment variables:

1. Rename `.env` variables:
   ```bash
   # Old .env
   REACT_APP_MY_VAR=value
   
   # New .env
   VITE_MY_VAR=value
   ```

2. Update code references:
   ```typescript
   // Old
   const myVar = process.env.REACT_APP_MY_VAR;
   
   // New
   const myVar = import.meta.env.VITE_MY_VAR;
   ```

3. No other changes needed! The migration is complete.

## License

Proprietary - Meats Central
