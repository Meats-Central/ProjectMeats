# Frontend React-Refresh Build Error - Fix Guide

## Problem
The frontend fails to compile with errors:
```
Module not found: Error: You attempted to import /workspaces/ProjectMeats/frontend/node_modules/react-refresh/runtime.js 
which falls outside of the project src/ directory. Relative imports outside of src/ are not supported.
```

## Root Cause
This is a known issue in certain development environments (especially Docker/Codespaces/WSL) where:
1. The project path contains symbolic links or non-standard filesystem structures
2. Webpack's Module Scope Plugin is too restrictive about imports from node_modules
3. react-scripts 5.0.1 has strict path validation that conflicts with the environment

## Tested Solutions (All Failed)
1. ✗ Clearing node_modules and reinstalling
2. ✗ Adding SKIP_PREFLIGHT_CHECK=true
3. ✗ Clearing webpack cache
4. ✗ Creating custom webpack config overrides

## Recommended Solutions

### Solution 1: Use react-app-rewired (RECOMMENDED)
This allows you to customize webpack config without ejecting.

```bash
cd /workspaces/ProjectMeats/frontend

# Install react-app-rewired
npm install --save-dev react-app-rewired

# Create config-overrides.js
cat > config-overrides.js <<'EOCONFIG'
const ModuleScopePlugin = require('react-dev-utils/ModuleScopePlugin');

module.exports = function override(config, env) {
  // Remove ModuleScopePlugin which throws the error
  config.resolve.plugins = config.resolve.plugins.filter(
    plugin => !(plugin instanceof ModuleScopePlugin)
  );
  
  return config;
};
EOCONFIG

# Update package.json scripts
# Change:
#   "start": "react-scripts start"
# To:
#   "start": "react-app-rewired start"
# Same for build and test

npm run start
```

### Solution 2: Use CRACO (Alternative)
CRACO (Create React App Configuration Override) is another popular option.

```bash
cd /workspaces/ProjectMeats/frontend

# Install CRACO
npm install --save-dev @craco/craco

# Create craco.config.js
cat > craco.config.js <<'EOCONFIG'
const ModuleScopePlugin = require('react-dev-utils/ModuleScopePlugin');

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      webpackConfig.resolve.plugins = webpackConfig.resolve.plugins.filter(
        plugin => !(plugin instanceof ModuleScopePlugin)
      );
      return webpackConfig;
    },
  },
};
EOCONFIG

# Update package.json scripts to use craco instead of react-scripts
npm run start
```

### Solution 3: Eject react-scripts (NOT RECOMMENDED)
This is irreversible and makes future updates harder.

```bash
cd /workspaces/ProjectMeats/frontend
npm run eject
# Then manually edit config/webpack.config.js to remove ModuleScopePlugin
```

### Solution 4: Disable Fast Refresh (Workaround)
Temporarily disable react-refresh to at least get the app running.

```bash
cd /workspaces/ProjectMeats/frontend

# Add to .env.local
echo "FAST_REFRESH=false" >> .env.local

npm start
```

Note: This will disable hot-reloading, requiring full page refreshes for changes.

### Solution 5: Upgrade react-scripts (May Break Other Things)
```bash
cd /workspaces/ProjectMeats/frontend
npm install react-scripts@latest
npm start
```

## Quick Test Commands

```bash
# Test if issue is environment-specific
cd /workspaces/ProjectMeats/frontend
npm list react-scripts react-dev-utils
node -e "console.log(require('path').resolve('.'))"
ls -la node_modules/react-refresh/runtime.js

# Check for symlinks
find /workspaces/ProjectMeats/frontend -type l

# Test with production build (sometimes works when dev doesn't)
npm run build
npx serve -s build
```

## Implementation Priority
1. Try Solution 1 (react-app-rewired) - cleanest, most maintainable
2. Try Solution 4 (disable fast refresh) - quick workaround
3. Try Solution 2 (CRACO) - if you need more config options
4. Try Solution 5 (upgrade) - if willing to test thoroughly
5. Avoid Solution 3 (eject) - only as last resort

## Files to Create/Modify

### For react-app-rewired approach:
- Create: `frontend/config-overrides.js`
- Modify: `frontend/package.json` (scripts section)

### For CRACO approach:
- Create: `frontend/craco.config.js`
- Modify: `frontend/package.json` (scripts section)

## Additional Resources
- https://github.com/facebook/create-react-app/issues/11771
- https://github.com/timarney/react-app-rewired
- https://craco.js.org/

