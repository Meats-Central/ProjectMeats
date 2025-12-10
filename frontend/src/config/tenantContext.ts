/**
 * Tenant Context Utility
 * 
 * Extracts tenant and environment information from window.location.hostname
 * to support multi-tenancy via domain detection.
 * 
 * Domain Pattern Examples:
 * - localhost:3000 -> { tenant: null, environment: 'development' }
 * - dev.projectmeats.com -> { tenant: null, environment: 'development' }
 * - uat.projectmeats.com -> { tenant: null, environment: 'uat' }
 * - projectmeats.com -> { tenant: null, environment: 'production' }
 * - acme-dev.projectmeats.com -> { tenant: 'acme', environment: 'development' }
 * - acme-uat.projectmeats.com -> { tenant: 'acme', environment: 'uat' }
 * - acme.projectmeats.com -> { tenant: 'acme', environment: 'production' }
 * - custom-tenant.com -> { tenant: 'custom-tenant', environment: 'production' }
 */

export interface TenantInfo {
  tenant: string | null;
  environment: 'development' | 'uat' | 'production';
  apiBaseUrl: string;
}

/**
 * Environment detection patterns
 */
const ENVIRONMENT_PATTERNS = {
  development: ['localhost', 'dev.', '-dev.'],
  uat: ['uat.', '-uat.'],
  production: [], // Default fallback
};

/**
 * Default API base URLs per environment
 * 
 * UNIFIED PROXY ARCHITECTURE:
 * All environments use same-domain proxying to eliminate CORS issues.
 * Nginx on frontend server proxies /api/ requests to backend server.
 * 
 * Benefits:
 * - No CORS issues (browser sees same origin)
 * - Simplified configuration
 * - Better security (backend not exposed directly)
 * 
 * Note: For localhost, we still use direct backend connection since
 * there's no nginx proxy in local development.
 */
const DEFAULT_API_URLS = {
  development: 'https://dev.meatscentral.com/api/v1',
  uat: 'https://uat.meatscentral.com/api/v1',
  production: 'https://meatscentral.com/api/v1',
};

/**
 * Extract environment from hostname
 */
function extractEnvironment(hostname: string): 'development' | 'uat' | 'production' {
  // Check for localhost or development patterns
  if (ENVIRONMENT_PATTERNS.development.some(pattern => hostname.includes(pattern))) {
    return 'development';
  }
  
  // Check for UAT patterns
  if (ENVIRONMENT_PATTERNS.uat.some(pattern => hostname.includes(pattern))) {
    return 'uat';
  }
  
  // Default to production
  return 'production';
}

/**
 * Extract tenant identifier from hostname
 * 
 * Examples:
 * - acme-dev.projectmeats.com -> 'acme'
 * - acme-uat.projectmeats.com -> 'acme'
 * - acme.projectmeats.com -> 'acme'
 * - tenant1.customdomain.com -> 'tenant1'
 * - localhost -> null
 * - dev.projectmeats.com -> null
 */
function extractTenant(hostname: string, environment: string): string | null {
  // Localhost has no tenant
  if (hostname.includes('localhost')) {
    return null;
  }
  
  // Remove port if present
  const hostWithoutPort = hostname.split(':')[0];
  
  // Split hostname into parts
  const parts = hostWithoutPort.split('.');
  
  // If it's just the base domain (e.g., projectmeats.com), no tenant
  if (parts.length <= 2) {
    return null;
  }
  
  // Get the subdomain part
  const subdomain = parts[0];
  
  // Check if subdomain is just an environment indicator
  if (subdomain === 'dev' || subdomain === 'uat' || subdomain === 'www') {
    return null;
  }
  
  // Extract tenant from subdomain (remove environment suffix if present)
  if (environment === 'development' && subdomain.endsWith('-dev')) {
    return subdomain.slice(0, -4);
  }
  
  if (environment === 'uat' && subdomain.endsWith('-uat')) {
    return subdomain.slice(0, -4);
  }
  
  // Return subdomain as tenant identifier
  return subdomain;
}

/**
 * Build API base URL for tenant and environment
 * 
 * Priority:
 * 1. Tenant-specific API URL (if tenant detected)
 * 2. Localhost for local development
 * 3. Default API URL for environment
 * 
 * Note: window.ENV.API_BASE_URL is checked in runtime.ts, not here,
 * to maintain proper configuration priority chain.
 */
function buildApiBaseUrl(tenant: string | null, environment: 'development' | 'uat' | 'production', hostname: string): string {
  // For localhost, always use local backend
  if (hostname.includes('localhost')) {
    return 'http://localhost:8000/api/v1';
  }
  
  // For tenant-specific domains, construct the API URL
  if (tenant) {
    const protocol = environment === 'development' ? 'http' : 'https';
    
    // Build environment prefix based on environment
    let envPrefix = '';
    if (environment === 'development') {
      envPrefix = '-dev';
    } else if (environment === 'uat') {
      envPrefix = '-uat';
    } else {
      // Production has no prefix
      envPrefix = '';
    }
    
    // Use tenant-specific API endpoint
    return `${protocol}://${tenant}${envPrefix}-api.projectmeats.com/api/v1`;
  }
  
  // Fall back to default API URLs for deployed environments
  return DEFAULT_API_URLS[environment];
}

/**
 * Get current tenant context from hostname
 */
export function getTenantContext(): TenantInfo {
  const hostname = window.location.hostname;
  const environment = extractEnvironment(hostname);
  const tenant = extractTenant(hostname, environment);
  const apiBaseUrl = buildApiBaseUrl(tenant, environment, hostname);
  
  return {
    tenant,
    environment,
    apiBaseUrl,
  };
}

/**
 * Get tenant-specific branding color (can be extended later)
 */
export function getTenantBranding(): {
  primaryColor: string;
  logoUrl: string | null;
} {
  const { tenant } = getTenantContext();
  
  // Default branding
  const defaultBranding = {
    primaryColor: '#1890ff', // Ant Design default blue
    logoUrl: null,
  };
  
  // Tenant-specific branding could be loaded from API or configured here
  // This is a placeholder for future enhancement
  if (tenant) {
    // Could fetch from API: /api/v1/tenants/current/branding
    // For now, return default
    return defaultBranding;
  }
  
  return defaultBranding;
}

/**
 * Initialize tenant context (call this at app startup)
 * Logs tenant information in development mode
 */
export function initializeTenantContext(): TenantInfo {
  const context = getTenantContext();
  
  // Log in development mode only (without exposing full API URL)
  if (process.env.NODE_ENV === 'development') {
    // eslint-disable-next-line no-console
    console.log('[Tenant Context] Initialized:', {
      hostname: window.location.hostname,
      tenant: context.tenant || 'none',
      environment: context.environment,
      // Don't log full API URL to avoid exposing endpoint structure
    });
  }
  
  return context;
}
