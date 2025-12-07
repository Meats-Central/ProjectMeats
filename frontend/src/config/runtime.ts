/**
 * Runtime Configuration Utility
 * 
 * This module provides runtime configuration that can be overridden
 * after the application is built and deployed. This solves the issue
 * where environment variables are baked in at build-time.
 * 
 * Configuration priority for API_BASE_URL and ENVIRONMENT:
 * 1. Runtime config from window.ENV (set via env-config.js) - explicit override
 * 2. Tenant context from domain detection (via tenantContext.ts) - automatic
 * 3. Build-time environment variables (import.meta.env.VITE_* or process.env.REACT_APP_*) - legacy fallback
 * 4. Default values - last resort
 */

import { getTenantContext } from './tenantContext';

// Extend Window interface to include ENV
declare global {
  interface Window {
    ENV?: {
      API_BASE_URL?: string;
      ENVIRONMENT?: string;
      AI_ASSISTANT_ENABLED?: string;
      ENABLE_DOCUMENT_UPLOAD?: string;
      ENABLE_CHAT_EXPORT?: string;
      MAX_FILE_SIZE?: string;
      SUPPORTED_FILE_TYPES?: string;
      ENABLE_DEBUG?: string;
      ENABLE_DEVTOOLS?: string;
    };
  }
}

/**
 * Get runtime configuration value
 * Priority: window.ENV > tenant context > process.env > default
 * 
 * Note: For API_BASE_URL and ENVIRONMENT, we check window.ENV first
 * to allow explicit override, then fall back to tenant context.
 */
function getRuntimeConfig(key: string, defaultValue: string = ''): string {
  // Check runtime config from env-config.js first for explicit override
  if (window.ENV && key in window.ENV) {
    const value = window.ENV[key as keyof typeof window.ENV];
    if (value !== undefined && value !== null && value !== '') {
      return value;
    }
  }
  
  // For API_BASE_URL and ENVIRONMENT, use tenant context as fallback
  if (key === 'API_BASE_URL' || key === 'ENVIRONMENT') {
    try {
      const tenantContext = getTenantContext();
      if (key === 'API_BASE_URL' && tenantContext.apiBaseUrl) {
        return tenantContext.apiBaseUrl;
      }
      if (key === 'ENVIRONMENT' && tenantContext.environment) {
        return tenantContext.environment;
      }
    } catch (error) {
      // Silently fall through to other config sources if tenant context fails
      // This ensures backward compatibility
    }
  }
  
  // Fall back to build-time environment variables
  // Support both VITE_ (new) and REACT_APP_ (legacy) prefixes
  const viteEnvKey = `VITE_${key}`;
  const reactEnvKey = `REACT_APP_${key}`;
  
  // Try Vite prefix first
  const viteValue = import.meta.env?.[viteEnvKey];
  if (viteValue !== undefined && viteValue !== null && viteValue !== '') {
    return viteValue;
  }
  
  // Fall back to legacy REACT_APP_ prefix
  const reactValue = process.env?.[reactEnvKey];
  if (reactValue !== undefined && reactValue !== null && reactValue !== '') {
    return reactValue;
  }
  
  // Use default value
  return defaultValue;
}

/**
 * Get boolean configuration value
 */
function getRuntimeConfigBoolean(key: string, defaultValue: boolean = false): boolean {
  const value = getRuntimeConfig(key, String(defaultValue));
  return value === 'true' || value === '1';
}

/**
 * Get number configuration value
 */
function getRuntimeConfigNumber(key: string, defaultValue: number = 0): number {
  const value = getRuntimeConfig(key, String(defaultValue));
  const parsed = parseInt(value, 10);
  return isNaN(parsed) ? defaultValue : parsed;
}

// Export configuration values
export const config = {
  // API Configuration - uses tenant context for domain-based multi-tenancy
  API_BASE_URL: getRuntimeConfig('API_BASE_URL', 'http://localhost:8000/api/v1'),
  
  // Environment - uses tenant context for domain-based detection
  ENVIRONMENT: getRuntimeConfig('ENVIRONMENT', 'development'),
  
  // Feature Flags
  AI_ASSISTANT_ENABLED: getRuntimeConfigBoolean('AI_ASSISTANT_ENABLED', true),
  ENABLE_DOCUMENT_UPLOAD: getRuntimeConfigBoolean('ENABLE_DOCUMENT_UPLOAD', true),
  ENABLE_CHAT_EXPORT: getRuntimeConfigBoolean('ENABLE_CHAT_EXPORT', true),
  ENABLE_DEBUG: getRuntimeConfigBoolean('ENABLE_DEBUG', process.env.NODE_ENV === 'development'),
  ENABLE_DEVTOOLS: getRuntimeConfigBoolean('ENABLE_DEVTOOLS', process.env.NODE_ENV === 'development'),
  
  // UI Configuration
  MAX_FILE_SIZE: getRuntimeConfigNumber('MAX_FILE_SIZE', 10485760), // 10MB
  SUPPORTED_FILE_TYPES: getRuntimeConfig('SUPPORTED_FILE_TYPES', 'pdf,jpg,jpeg,png,txt,doc,docx,xls,xlsx'),
};

/**
 * Get current tenant information from domain
 * Exported for use in components that need tenant-specific logic
 */
export function getCurrentTenant(): string | null {
  try {
    const tenantContext = getTenantContext();
    return tenantContext.tenant;
  } catch (error) {
    return null;
  }
}

// Export helper functions for dynamic config access
export { getRuntimeConfig, getRuntimeConfigBoolean, getRuntimeConfigNumber };

// Log configuration source in development
// Note: This only runs once when the module is first imported
if (process.env.NODE_ENV === 'development') {
  // eslint-disable-next-line no-console
  console.log('[Runtime Config] Loaded from:', 
    window.ENV ? 'window.ENV (runtime)' : 'process.env (build-time)'
  );
  
  try {
    const tenantContext = getTenantContext();
    // eslint-disable-next-line no-console
    console.log('[Runtime Config] Multi-tenancy:', {
      tenant: tenantContext.tenant || 'none',
      environment: tenantContext.environment,
    });
  } catch (error) {
    // Ignore errors in development logging
  }
}
