/**
 * Tests for tenant context utility
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach, vi } from 'vitest';
import { getTenantContext, getTenantBranding, initializeTenantContext } from './tenantContext';

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
    // Restore original window.location (TypeScript 5.9 requires proper casting)
    Object.defineProperty(window, 'location', {
      value: originalLocation,
      writable: true
    });
  });
  
  beforeEach(() => {
    // Clear window.ENV before each test
    delete (window as any).ENV;
    // Reset location to localhost
    window.location.hostname = 'localhost';
  });
  
  describe('getTenantContext', () => {
    it('should detect localhost as development with no tenant', () => {
      window.location.hostname = 'localhost';
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('development');
      expect(context.apiBaseUrl).toBe('http://localhost:8000/api/v1');
    });
    
    it('should detect localhost:3000 as development with no tenant', () => {
      window.location.hostname = 'localhost:3000';
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('development');
      expect(context.apiBaseUrl).toBe('http://localhost:8000/api/v1');
    });
    
    it('should detect dev.meatscentral.com as development with no tenant', () => {
      window.location.hostname = 'dev.meatscentral.com';
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('development');
      expect(context.apiBaseUrl).toBe('https://dev.meatscentral.com/api/v1');
    });
    
    it('should detect uat.meatscentral.com as UAT with no tenant', () => {
      window.location.hostname = 'uat.meatscentral.com';
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('uat');
      expect(context.apiBaseUrl).toBe('https://uat.meatscentral.com/api/v1');
    });
    
    it('should detect meatscentral.com as production with no tenant', () => {
      window.location.hostname = 'meatscentral.com';
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('production');
      expect(context.apiBaseUrl).toBe('https://meatscentral.com/api/v1');
    });
    
    it('should detect acme-dev.meatscentral.com as development with acme tenant', () => {
      window.location.hostname = 'acme-dev.meatscentral.com';
      
      const context = getTenantContext();
      expect(context.tenant).toBe('acme');
      expect(context.environment).toBe('development');
      expect(context.apiBaseUrl).toBe('http://acme-dev-api.meatscentral.com/api/v1');
    });
    
    it('should detect acme-uat.meatscentral.com as UAT with acme tenant', () => {
      window.location.hostname = 'acme-uat.meatscentral.com';
      
      const context = getTenantContext();
      expect(context.tenant).toBe('acme');
      expect(context.environment).toBe('uat');
      expect(context.apiBaseUrl).toBe('https://acme-uat-api.meatscentral.com/api/v1');
    });
    
    it('should detect acme.meatscentral.com as production with acme tenant', () => {
      window.location.hostname = 'acme.meatscentral.com';
      
      const context = getTenantContext();
      expect(context.tenant).toBe('acme');
      expect(context.environment).toBe('production');
      expect(context.apiBaseUrl).toBe('https://acme-api.meatscentral.com/api/v1');
    });
    
    it('should detect custom-tenant.customdomain.com as production with custom-tenant', () => {
      window.location.hostname = 'custom-tenant.customdomain.com';
      
      const context = getTenantContext();
      expect(context.tenant).toBe('custom-tenant');
      expect(context.environment).toBe('production');
    });
    
    it('should ignore www subdomain', () => {
      window.location.hostname = 'www.meatscentral.com';
      
      const context = getTenantContext();
      expect(context.tenant).toBeNull();
      expect(context.environment).toBe('production');
    });
  });
  
  describe('getTenantBranding', () => {
    it('should return default branding for no tenant', () => {
      window.location.hostname = 'localhost';
      
      const branding = getTenantBranding();
      expect(branding.primaryColor).toBe('#1890ff');
      expect(branding.logoUrl).toBeNull();
    });
    
    it('should return default branding for tenant (placeholder)', () => {
      window.location.hostname = 'acme.meatscentral.com';
      
      const branding = getTenantBranding();
      expect(branding.primaryColor).toBe('#1890ff');
      expect(branding.logoUrl).toBeNull();
    });
  });
  
  describe('initializeTenantContext', () => {
    it('should initialize and return tenant context', () => {
      window.location.hostname = 'acme.meatscentral.com';
      
      const context = initializeTenantContext();
      expect(context.tenant).toBe('acme');
      expect(context.environment).toBe('production');
      expect(context.apiBaseUrl).toBeDefined();
    });
    
    it('should log in development mode', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      // Set NODE_ENV to development
      const originalNodeEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';
      window.location.hostname = 'localhost';
      
      initializeTenantContext();
      
      expect(consoleSpy).toHaveBeenCalled();
      
      // Restore
      process.env.NODE_ENV = originalNodeEnv;
      consoleSpy.mockRestore();
    });
  });
});
