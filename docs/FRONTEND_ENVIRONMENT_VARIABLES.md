# Frontend Environment Variables

**Last Updated:** December 10, 2025  
**Applies To:** React Frontend (Vite/CRA)  
**Source of Truth:** `config/env.manifest.json` v3.3

---

## Overview

ProjectMeats frontend uses **runtime configuration** to support multi-environment deployments without rebuilding. This guide covers environment variables for local development and deployment.

### Configuration Priority

1. **Runtime config** (`window.ENV` via `public/env-config.js`) - Highest priority
2. **Domain-based detection** (automatic via `tenantContext.ts`)
3. **Build-time env vars** (`import.meta.env.VITE_*` or `process.env.REACT_APP_*`)
4. **Default values** - Fallback

---

## Quick Start: Local Development

### 1. Create `.env.local` (Recommended)

```bash
# frontend/.env.local (not committed to git)

# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development

# Feature Flags
REACT_APP_AI_ASSISTANT_ENABLED=true

# Debug Options (development only)
VITE_ENABLE_DEBUG=true
VITE_ENABLE_DEVTOOLS=true
```

### 2. Start Development Server

```bash
cd frontend
npm install
npm start  # or: npm run dev (for Vite)
```

The app will automatically use `localhost:8000` for API calls.

---

## Environment-Specific Configuration

### Development (dev.meatscentral.com)

**Frontend URL:** `https://dev.meatscentral.com`  
**Backend URL:** `https://dev-backend.meatscentral.com/api/v1`

```bash
# For CI/CD or manual deployment
REACT_APP_API_BASE_URL=https://dev-backend.meatscentral.com/api/v1
REACT_APP_ENVIRONMENT=development
REACT_APP_AI_ASSISTANT_ENABLED=true
```

**Why separate backend subdomain?**
- Dev environment uses separate droplet for backend
- Allows independent backend/frontend deployments
- Mirrors production architecture (separate services)

### UAT/Staging (uat.meatscentral.com)

**Frontend URL:** `https://uat.meatscentral.com`  
**Backend URL:** `https://uat.meatscentral.com/api/v1`

```bash
REACT_APP_API_BASE_URL=https://uat.meatscentral.com/api/v1
REACT_APP_ENVIRONMENT=staging
REACT_APP_AI_ASSISTANT_ENABLED=true
```

**Note:** UAT uses same domain for frontend and backend (reverse proxy setup).

### Production (meatscentral.com)

**Frontend URL:** `https://meatscentral.com`  
**Backend URL:** `https://meatscentral.com/api/v1`

```bash
REACT_APP_API_BASE_URL=https://meatscentral.com/api/v1
REACT_APP_ENVIRONMENT=production
REACT_APP_AI_ASSISTANT_ENABLED=true
```

---

## All Available Variables

### API Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REACT_APP_API_BASE_URL` | Yes | `http://localhost:8000/api/v1` | Backend API endpoint |
| `REACT_APP_ENVIRONMENT` | No | `development` | Environment name (development, staging, production) |

**Example Usage:**
```typescript
// src/config/runtime.ts automatically loads these
import { config } from './config/runtime';
console.log(config.API_BASE_URL); // Uses REACT_APP_API_BASE_URL
```

### Feature Flags

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REACT_APP_AI_ASSISTANT_ENABLED` | boolean | `true` | Enable AI chat assistant |
| `REACT_APP_ENABLE_DOCUMENT_UPLOAD` | boolean | `true` | Enable file uploads in chat |
| `REACT_APP_ENABLE_CHAT_EXPORT` | boolean | `true` | Enable chat history export |

### UI Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REACT_APP_MAX_FILE_SIZE` | number | `10485760` | Max upload size (bytes, default 10MB) |
| `REACT_APP_SUPPORTED_FILE_TYPES` | string | `pdf,jpg,jpeg,png,txt,doc,docx` | Allowed file extensions |

### Development Tools

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `VITE_ENABLE_DEBUG` | boolean | `true` (dev only) | Enable debug logging |
| `VITE_ENABLE_DEVTOOLS` | boolean | `true` (dev only) | Enable React DevTools |

---

## Runtime Configuration (Recommended)

### For Deployments: Use `env-config.js`

The preferred method for deployments is to inject configuration at runtime:

**File:** `frontend/public/env-config.js`

```javascript
// This file is loaded before React starts
// Updated by deployment pipeline for each environment

window.ENV = {
  API_BASE_URL: "https://dev-backend.meatscentral.com/api/v1",
  ENVIRONMENT: "development",
  AI_ASSISTANT_ENABLED: "true"
};
```

**Benefits:**
- ✅ No rebuild needed for different environments
- ✅ Same Docker image works in dev/uat/prod
- ✅ Configuration changed at deployment time
- ✅ Overrides build-time variables

**Deployment Example:**
```bash
# On deployment server, update env-config.js
cat > /opt/pm/frontend/env/env-config.js << 'EOF'
window.ENV = {
  API_BASE_URL: "https://dev-backend.meatscentral.com/api/v1",
  ENVIRONMENT: "development"
};
EOF

# Mount into container
docker run -v /opt/pm/frontend/env/env-config.js:/usr/share/nginx/html/env-config.js:ro \
  frontend:latest
```

---

## Domain-Based Auto-Detection

The frontend **automatically detects** environment from domain:

| Domain | Environment | API URL (auto-detected) |
|--------|-------------|-------------------------|
| `localhost:3000` | development | `http://localhost:8000/api/v1` |
| `dev.meatscentral.com` | development | `https://dev-backend.meatscentral.com/api/v1` |
| `uat.meatscentral.com` | uat | `https://uat.meatscentral.com/api/v1` |
| `meatscentral.com` | production | `https://meatscentral.com/api/v1` |

**Implementation:** See `src/config/tenantContext.ts`

This means you often **don't need** to set `REACT_APP_API_BASE_URL` explicitly!

---

## Best Practices

### ✅ DO

1. **Use `.env.local` for local development**
   ```bash
   # Never commit .env.local to git
   echo ".env.local" >> .gitignore
   ```

2. **Use runtime config for deployments**
   - Update `public/env-config.js` at deployment time
   - No rebuild needed

3. **Leverage domain-based detection**
   - Let the app auto-detect environment from URL
   - Only override when needed

4. **Use GitHub Secrets for CI/CD**
   ```bash
   # Set in GitHub repo settings → Secrets
   gh secret set REACT_APP_API_BASE_URL --env dev-frontend
   ```

5. **Follow naming conventions**
   - Vite: `VITE_*` prefix
   - CRA legacy: `REACT_APP_*` prefix
   - Both work (runtime.ts handles both)

### ❌ DON'T

1. **Don't commit secrets to `.env` files**
   ```bash
   # Bad - secrets in version control
   git add .env
   
   # Good - keep secrets out of git
   echo ".env.local" >> .gitignore
   ```

2. **Don't hardcode API URLs in code**
   ```typescript
   // ❌ Bad
   const API_URL = "https://dev-backend.meatscentral.com";
   
   // ✅ Good
   import { config } from '@/config/runtime';
   const API_URL = config.API_BASE_URL;
   ```

3. **Don't use production URLs in development**
   ```bash
   # ❌ Bad - will hit production API
   REACT_APP_API_BASE_URL=https://meatscentral.com/api/v1
   
   # ✅ Good - use local backend
   REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
   ```

4. **Don't duplicate .env files**
   - Use `.env.local` (not committed)
   - Reference this doc for examples
   - Use manifest system (`config/env.manifest.json`)

---

## Troubleshooting

### API calls go to wrong URL

**Problem:** Frontend is calling localhost instead of dev-backend.

**Solution:**
1. Check browser console for detected config:
   ```javascript
   // Should log on app start
   [Runtime Config] Loaded from: window.ENV (runtime)
   [Tenant Context] environment: development
   ```

2. Verify `env-config.js` if deployed:
   ```bash
   docker exec pm-frontend cat /usr/share/nginx/html/env-config.js
   ```

3. Check domain detection:
   ```javascript
   // In browser console
   window.location.hostname  // Should match expected domain
   ```

### Environment variables not loading

**CRA → Vite Migration Note:**
- Old: `process.env.REACT_APP_*`
- New: `import.meta.env.VITE_*`
- Both work! (`runtime.ts` handles compatibility)

**Solution:**
```typescript
// Use the config module (handles both)
import { config } from '@/config/runtime';
const apiUrl = config.API_BASE_URL;  // Works with both systems
```

### Changes not reflecting

**Problem:** Updated `.env` but app still uses old values.

**Solution:**
1. Restart dev server (env vars are loaded at startup)
   ```bash
   # Stop server (Ctrl+C)
   npm start  # Restart
   ```

2. Clear cache if using Vite:
   ```bash
   rm -rf node_modules/.vite
   npm start
   ```

---

## Related Documentation

- **Manifest System:** [`config/env.manifest.json`](../config/env.manifest.json)
- **Configuration Guide:** [`docs/CONFIGURATION_AND_SECRETS.md`](./CONFIGURATION_AND_SECRETS.md)
- **Golden Pipeline:** [`docs/GOLDEN_PIPELINE.md`](./GOLDEN_PIPELINE.md)
- **Runtime Config:** [`frontend/src/config/runtime.ts`](../frontend/src/config/runtime.ts)
- **Tenant Context:** [`frontend/src/config/tenantContext.ts`](../frontend/src/config/tenantContext.ts)

### External Resources

- [React Environment Variables Best Practices](https://create-react-app.dev/docs/adding-custom-environment-variables/)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [Create React App: Environment Variables](https://create-react-app.dev/docs/adding-custom-environment-variables/)

---

## Migration from .env.example

**Old approach (deprecated):**
- Multiple `.env.example` files
- Manual secret management
- Copy/paste configuration

**New approach (current):**
- Single source: `config/env.manifest.json`
- Automated validation: `python config/manage_env.py audit`
- Runtime configuration: `public/env-config.js`
- Domain-based detection: `src/config/tenantContext.ts`

**To migrate your workflow:**
1. Stop copying from `.env.example`
2. Read [`docs/CONFIGURATION_AND_SECRETS.md`](./CONFIGURATION_AND_SECRETS.md)
3. Use manifest system for secret definitions
4. Use runtime config for deployments
5. Let domain detection handle the rest

---

**Questions?** See [`docs/CONFIGURATION_AND_SECRETS.md`](./CONFIGURATION_AND_SECRETS.md) or run:
```bash
python config/manage_env.py audit
```
