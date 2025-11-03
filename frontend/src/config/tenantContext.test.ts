/**
 * Tests for tenant context utility
 */

// This file is a module (required for TypeScript isolatedModules)
export {};

describe('Tenant Context', () => {
  // Save original window.location
  const originalLocation = window.location;
  
  beforeAll(() => {
    // Mock window.location
    delete (window as any).location;
    (window as any).location = { hostname: 'localhost' };
  });
  
  afterAll(() => {
    // Restore original window.location
    window.location = originalLocation;
  });
  
  beforeEach(() => {
    // Clear window.ENV before each test
    delete (window as any).ENV;
    // Reset location to localhost
    window.location.hostname = 'localhost';
    
    // Clear module cache to get fresh imports
    jest.resetModules();
  });
  
  describe('getTenantContext', () => {
    it('should detect localhost as development with no tenant', () => {
      window.location.hostname = 'localhost';
      const { getTenantContext } = require('./tenantContext');
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('development');
      expect(context.apiBaseUrl).toBe('http://localhost:8000/api/v1');
    });
    
    it('should detect localhost:3000 as development with no tenant', () => {
      window.location.hostname = 'localhost:3000';
      const { getTenantContext } = require('./tenantContext');
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('development');
      expect(context.apiBaseUrl).toBe('http://localhost:8000/api/v1');
    });
    
    it('should detect dev.projectmeats.com as development with no tenant', () => {
      window.location.hostname = 'dev.projectmeats.com';
      const { getTenantContext } = require('./tenantContext');
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('development');
      expect(context.apiBaseUrl).toBe('http://localhost:8000/api/v1');
    });
    
    it('should detect uat.projectmeats.com as UAT with no tenant', () => {
      window.location.hostname = 'uat.projectmeats.com';
      const { getTenantContext } = require('./tenantContext');
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('uat');
      expect(context.apiBaseUrl).toBe('https://uat-api.projectmeats.com/api/v1');
    });
    
    it('should detect projectmeats.com as production with no tenant', () => {
      window.location.hostname = 'projectmeats.com';
      const { getTenantContext } = require('./tenantContext');
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('production');
      expect(context.apiBaseUrl).toBe('https://api.projectmeats.com/api/v1');
    });
    
    it('should detect acme-dev.projectmeats.com as development with acme tenant', () => {
      window.location.hostname = 'acme-dev.projectmeats.com';
      const { getTenantContext } = require('./tenantContext');
      
      const context = getTenantContext();
      expect(context.tenant).toBe('acme');
      expect(context.environment).toBe('development');
      expect(context.apiBaseUrl).toBe('http://acme-dev-api.projectmeats.com/api/v1');
    });
    
    it('should detect acme-uat.projectmeats.com as UAT with acme tenant', () => {
      window.location.hostname = 'acme-uat.projectmeats.com';
      const { getTenantContext } = require('./tenantContext');
      
      const context = getTenantContext();
      expect(context.tenant).toBe('acme');
      expect(context.environment).toBe('uat');
      expect(context.apiBaseUrl).toBe('https://acme-uat-api.projectmeats.com/api/v1');
    });
    
    it('should detect acme.projectmeats.com as production with acme tenant', () => {
      window.location.hostname = 'acme.projectmeats.com';
      const { getTenantContext } = require('./tenantContext');
      
      const context = getTenantContext();
      expect(context.tenant).toBe('acme');
      expect(context.environment).toBe('production');
      expect(context.apiBaseUrl).toBe('https://acme-api.projectmeats.com/api/v1');
    });
    
    it('should detect custom-tenant.customdomain.com as production with custom-tenant', () => {
      window.location.hostname = 'custom-tenant.customdomain.com';
      const { getTenantContext } = require('./tenantContext');
      
      const context = getTenantContext();
      expect(context.tenant).toBe('custom-tenant');
      expect(context.environment).toBe('production');
    });
    
    it('should ignore www subdomain', () => {
      window.location.hostname = 'www.projectmeats.com';
      const { getTenantContext } = require('./tenantContext');
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('production');
    });
  });
  
  describe('getTenantBranding', () => {
    it('should return default branding for no tenant', () => {
      window.location.hostname = 'localhost';
      const { getTenantBranding } = require('./tenantContext');
      
      const branding = getTenantBranding();
      expect(branding.primaryColor).toBe('#1890ff');
      expect(branding.logoUrl).toBeNull();
    });
    
    it('should return default branding for tenant (placeholder)', () => {
      window.location.hostname = 'acme.projectmeats.com';
      const { getTenantBranding } = require('./tenantContext');
      
      const branding = getTenantBranding();
      expect(branding.primaryColor).toBe('#1890ff');
      expect(branding.logoUrl).toBeNull();
    });
  });
  
  describe('initializeTenantContext', () => {
    it('should initialize and return tenant context', () => {
      window.location.hostname = 'acme.projectmeats.com';
      const { initializeTenantContext } = require('./tenantContext');
      
      const context = initializeTenantContext();
      expect(context.tenant).toBe('acme');
      expect(context.environment).toBe('production');
      expect(context.apiBaseUrl).toBeDefined();
    });
    
    it('should log in development mode', () => {
      const originalEnv = process.env.NODE_ENV;
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      process.env.NODE_ENV = 'development';
      window.location.hostname = 'localhost';
      
      // Clear and reload module
      jest.resetModules();
      const { initializeTenantContext } = require('./tenantContext');
      
      initializeTenantContext();
      
      expect(consoleSpy).toHaveBeenCalled();
      
      // Restore
      process.env.NODE_ENV = originalEnv;
      consoleSpy.mockRestore();
    });
  });
});
