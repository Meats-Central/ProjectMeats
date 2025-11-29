# Runtime Environment Configuration

This document explains the runtime environment variable system implemented to solve the issue where frontend environment variables were baked in at build time instead of being configurable at runtime.

## Problem Statement

Previously, the frontend was using `process.env.REACT_APP_API_BASE_URL` which gets embedded into the JavaScript bundle during the build process. This meant:

1. The API endpoint was **hardcoded** in the build
2. Changing the API endpoint required **rebuilding the entire application**
3. The same Docker image couldn't be used across different environments (dev, UAT, prod)
4. Environment variables set at runtime (via GitHub Secrets or Docker) were **ignored**

This caused the frontend to make API requests to `http://localhost:8000` even when deployed to remote servers.

## Solution

We implemented a **runtime configuration system** that:

1. Loads configuration from `window.ENV` (set by `env-config.js`)
2. Falls back to `process.env` (build-time values)
3. Uses sensible defaults if neither is available

### How It Works

#### 1. Runtime Configuration Loading

The file `public/env-config.js` is loaded **before** the React application starts:

```html
<!-- In public/index.html -->
<script src="%PUBLIC_URL%/env-config.js"></script>
```

This script sets `window.ENV` with runtime configuration:

```javascript
// public/env-config.js
window.ENV = {
  API_BASE_URL: "http://localhost:8000/api/v1",
  ENVIRONMENT: "development"
};
```

#### 2. Configuration Utility

The `src/config/runtime.ts` module provides a centralized configuration system:

```typescript
import { config } from './config/runtime';

// Use config values
const apiUrl = config.API_BASE_URL;
const isEnabled = config.AI_ASSISTANT_ENABLED;
```

**Priority order:**
1. **Runtime config** from `window.ENV` (highest priority)
2. **Build-time config** from `process.env.REACT_APP_*`
3. **Default values** (lowest priority)

#### 3. Deployment Integration

During deployment, the `env-config.js` file is **replaced** with environment-specific values:

```bash
# In deployment workflow
sudo bash -c 'cat > /opt/pm/frontend/env/env-config.js <<JS
window.ENV = {
  API_BASE_URL: "${{ secrets.REACT_APP_API_BASE_URL }}",
  ENVIRONMENT: "production"
};
JS'

# Mount it into the Docker container
docker run -d \
  -v /opt/pm/frontend/env/env-config.js:/usr/share/nginx/html/env-config.js:ro \
  frontend-image:latest
```

## Usage

### For Developers

#### Local Development

No changes needed! The default `public/env-config.js` points to `http://localhost:8000/api/v1`.

#### Using the Config

Always import from `config/runtime` instead of using `process.env` directly:

```typescript
// ❌ DON'T DO THIS
const apiUrl = process.env.REACT_APP_API_BASE_URL || 'default';

// ✅ DO THIS
import { config } from '../config/runtime';
const apiUrl = config.API_BASE_URL;
```

#### Available Configuration

- `config.API_BASE_URL` - Backend API endpoint
- `config.ENVIRONMENT` - Current environment (development/staging/production)
- `config.AI_ASSISTANT_ENABLED` - Boolean feature flag
- `config.ENABLE_DOCUMENT_UPLOAD` - Boolean feature flag
- `config.ENABLE_CHAT_EXPORT` - Boolean feature flag
- `config.ENABLE_DEBUG` - Boolean debug mode
- `config.ENABLE_DEVTOOLS` - Boolean devtools enabled
- `config.MAX_FILE_SIZE` - Number, max file size in bytes
- `config.SUPPORTED_FILE_TYPES` - String, comma-separated file extensions

### For DevOps

#### Deployment Workflow

All deployment workflows (dev, UAT, prod) follow the same pattern:

1. **Create runtime config** with environment-specific values
2. **Mount the file** into the container at `/usr/share/nginx/html/env-config.js`
3. The frontend loads this configuration at runtime

Example from `.github/workflows/11-dev-deployment.yml`:

```yaml
- name: Deploy frontend container
  run: |
    # Create runtime config
    sudo bash -c 'cat > /opt/pm/frontend/env/env-config.js <<JS
    window.ENV = {
      API_BASE_URL: "${{ secrets.REACT_APP_API_BASE_URL }}",
      ENVIRONMENT: "development"
    };
    JS'
    
    # Deploy container with volume mount
    sudo docker run -d \
      -p 8080:80 \
      -v /opt/pm/frontend/env/env-config.js:/usr/share/nginx/html/env-config.js:ro \
      registry/frontend:dev-latest
```

#### Environment Variables

Required GitHub Secrets:

- `REACT_APP_API_BASE_URL` - Backend API endpoint (e.g., `https://api.example.com/api/v1`)
- `REACT_APP_AI_ASSISTANT_ENABLED` - `true` or `false`
- `REACT_APP_ENABLE_DOCUMENT_UPLOAD` - `true` or `false`
- `REACT_APP_ENABLE_CHAT_EXPORT` - `true` or `false`
- `REACT_APP_MAX_FILE_SIZE` - Number as string (e.g., `10485760`)
- `REACT_APP_SUPPORTED_FILE_TYPES` - Comma-separated extensions (e.g., `pdf,jpg,png`)

## Testing

### Unit Tests

Tests are located in `src/config/runtime.test.ts`:

```bash
npm run test:ci
```

**Coverage:** 94% of runtime.ts

### Manual Testing

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Verify env-config.js exists:**
   ```bash
   ls -la build/env-config.js
   ```

3. **Test with custom config:**
   ```bash
   # Modify build/env-config.js
   echo 'window.ENV = { API_BASE_URL: "https://test.example.com/api/v1" };' > build/env-config.js
   
   # Serve and test
   npx serve -s build
   ```

4. **Check browser console:**
   - Open browser dev tools
   - You should see: `[Runtime Config] Loaded from: window.ENV (runtime)`

## Benefits

✅ **Single build, multiple environments** - Same Docker image for dev, UAT, and prod  
✅ **Runtime configuration** - No rebuild needed to change API endpoints  
✅ **Environment consistency** - All environments use the same deployment pattern  
✅ **Backward compatible** - Falls back to build-time env vars if runtime config unavailable  
✅ **Type-safe** - TypeScript definitions for all config values  
✅ **Well-tested** - 14 unit tests with 94% coverage  

## Migration Guide

If you have existing code using `process.env.REACT_APP_*`:

1. Import the config utility:
   ```typescript
   import { config } from '../config/runtime';
   ```

2. Replace `process.env` references:
   ```typescript
   // Before
   const url = process.env.REACT_APP_API_BASE_URL || 'default';
   
   // After
   const url = config.API_BASE_URL;
   ```

3. For dynamic config access:
   ```typescript
   import { getRuntimeConfig } from '../config/runtime';
   
   const value = getRuntimeConfig('CUSTOM_VALUE', 'default');
   ```

## Troubleshooting

### Frontend still hitting localhost

1. **Check env-config.js is loaded:**
   - Open browser dev tools → Network tab
   - Verify `env-config.js` is loaded with 200 status

2. **Check window.ENV:**
   - Open browser console
   - Type `window.ENV` and press Enter
   - Verify it contains the correct values

3. **Check deployment:**
   - SSH to server: `cat /opt/pm/frontend/env/env-config.js`
   - Verify the file has correct values
   - Verify Docker volume mount: `docker inspect pm-frontend | grep env-config`

### Build fails with "Cannot be compiled under --isolatedModules"

Test files need to be modules. Add `export {};` to the top of test files.

### Config values not updating

The config object is created once at module load time. To get dynamic values, use the helper functions:

```typescript
import { getRuntimeConfig } from '../config/runtime';

// This gets the current value each time it's called
const currentValue = getRuntimeConfig('SOME_KEY', 'default');
```

## Security Considerations

1. **Sensitive values:** While API URLs are generally not secret, avoid logging them in production
2. **GitHub Secrets:** All runtime values come from GitHub Secrets, which should be properly secured
3. **File permissions:** The env-config.js file should be readable (644) but owned by root
4. **Volume mount:** Use read-only mount (`:ro`) to prevent container modifications

## References

- [12-Factor App: Config](https://12factor.net/config)
- [Create React App: Environment Variables](https://create-react-app.dev/docs/adding-custom-environment-variables/)
- Issue: Frontend API calls to localhost instead of remote endpoint
- PR: #[number] - Fix frontend runtime environment variable configuration
