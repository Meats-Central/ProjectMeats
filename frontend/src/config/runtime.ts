/**
 * Runtime Configuration Utility
 * 
 * This module provides runtime configuration that can be overridden
 * after the application is built and deployed. This solves the issue
 * where environment variables are baked in at build-time.
 * 
 * Configuration priority:
 * 1. Runtime config from window.ENV (set via env-config.js)
 * 2. Build-time environment variables (process.env.REACT_APP_*)
 * 3. Default values
 */

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
 * Priority: window.ENV > process.env > default
 */
function getRuntimeConfig(key: string, defaultValue: string = ''): string {
  // Check runtime config first (from env-config.js)
  if (window.ENV && key in window.ENV) {
    const value = window.ENV[key as keyof typeof window.ENV];
    if (value !== undefined && value !== null && value !== '') {
      return value;
    }
  }
  
  // Fall back to build-time environment variables
  const envKey = `REACT_APP_${key}`;
  const envValue = process.env[envKey];
  if (envValue !== undefined && envValue !== null && envValue !== '') {
    return envValue;
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
  // API Configuration
  API_BASE_URL: getRuntimeConfig('API_BASE_URL', 'http://localhost:8000/api/v1'),
  
  // Environment
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

// Export helper functions for dynamic config access
export { getRuntimeConfig, getRuntimeConfigBoolean, getRuntimeConfigNumber };

// Log configuration in development (but not during CI build)
if (process.env.NODE_ENV === 'development' && !process.env.CI) {
  // eslint-disable-next-line no-console
  console.log('[Runtime Config] Initialized with:', {
    API_BASE_URL: config.API_BASE_URL,
    ENVIRONMENT: config.ENVIRONMENT,
    source: window.ENV ? 'window.ENV (runtime)' : 'process.env (build-time)',
  });
}
