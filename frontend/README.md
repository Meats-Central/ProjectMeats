# ProjectMeats Frontend

React + TypeScript frontend application for ProjectMeats business management system with multi-tenancy support.

## Table of Contents

- [Overview](#overview)
- [Multi-Tenancy Support](#multi-tenancy-support)
- [Getting Started](#getting-started)
- [Development](#development)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Architecture](#architecture)

## Overview

This is the frontend application for ProjectMeats, built with:

- **React 18.2.0** - Modern React with hooks and concurrent features
- **TypeScript 4.9.5** - Type-safe JavaScript
- **Ant Design 5.27.3** - UI component library
- **Axios 1.6.0** - HTTP client for API communication
- **React Router 6.30.1** - Client-side routing

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

1. **Tenant Context** - Extracted from domain (highest priority)
2. **window.ENV.API_BASE_URL** - Runtime configuration
3. **process.env.REACT_APP_API_BASE_URL** - Build-time environment variable
4. **Default value** - Fallback (lowest priority)

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
# Development server with hot reload
npm start

# Run tests in interactive watch mode
npm test

# Run tests with coverage (CI mode)
npm run test:ci

# Build for production
npm run build

# Type check without building
npm run type-check

# Lint code
npm run lint

# Auto-fix linting issues
npm run lint:fix

# Format code with Prettier
npm run format

# Serve production build locally
npm run serve
```

### Project Structure

```
frontend/
├── public/              # Static assets
│   ├── index.html       # HTML template
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
│   └── App.tsx         # Root component
├── package.json
└── tsconfig.json
```

## Configuration

### Environment Variables

The frontend uses a hybrid configuration system that supports both build-time and runtime configuration.

#### Build-time Variables (`.env`)

```bash
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
REACT_APP_AI_ASSISTANT_ENABLED=true
REACT_APP_ENABLE_DOCUMENT_UPLOAD=true
```

#### Runtime Variables (`public/env-config.js`)

For production deployments, you can override configuration at runtime:

```javascript
window.ENV = {
  API_BASE_URL: "https://api.example.com/api/v1",
  ENVIRONMENT: "production"
};
```

**Priority**: Tenant context → `window.ENV` → `process.env.REACT_APP_*` → defaults

See [RUNTIME_CONFIG.md](./RUNTIME_CONFIG.md) for detailed configuration guide.

## Testing

### Running Tests

```bash
# Interactive watch mode
npm test

# Single run with coverage (for CI)
npm run test:ci
```

### Test Coverage

The project maintains high test coverage for critical modules:

- **tenantContext.ts**: 100% coverage (domain detection logic)
- **runtime.ts**: 85%+ coverage (configuration management)

### Writing Tests

Tests are written using Jest and React Testing Library:

```typescript
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

## License

Proprietary - Meats Central
