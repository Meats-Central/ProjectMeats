/**
 * Tests for runtime configuration utility
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getRuntimeConfig, getRuntimeConfigBoolean, getRuntimeConfigNumber, config, getCurrentTenant } from './runtime';

// This file is a module (required for TypeScript isolatedModules)
export {};

describe('Runtime Configuration', () => {
  describe('getRuntimeConfig', () => {
    beforeEach(() => {
      // Clear window.ENV before each test
      delete (window as any).ENV;
    });

    it('should prioritize window.ENV over process.env', () => {
      // Set both window.ENV and process.env
      (window as any).ENV = { API_BASE_URL: 'https://runtime.example.com/api/v1' };
      vi.stubEnv('VITE_API_BASE_URL', 'https://buildtime.example.com/api/v1');

      const result = getRuntimeConfig('API_BASE_URL', 'http://default.com/api/v1');
      expect(result).toBe('https://runtime.example.com/api/v1');
      
      vi.unstubAllEnvs();
    });

    it('should fall back to process.env when window.ENV is not available', () => {
      vi.stubEnv('VITE_CUSTOM_KEY', 'https://buildtime.example.com/api/v1');

      const result = getRuntimeConfig('CUSTOM_KEY', 'http://default.com/api/v1');
      expect(result).toBe('https://buildtime.example.com/api/v1');
      
      vi.unstubAllEnvs();
    });

    it('should use default value when neither window.ENV nor process.env is set', () => {
      const result = getRuntimeConfig('CUSTOM_KEY', 'http://default.com/api/v1');
      expect(result).toBe('http://default.com/api/v1');
    });

    it('should handle empty string values by falling back', () => {
      (window as any).ENV = { CUSTOM_KEY: '' };

      const result = getRuntimeConfig('CUSTOM_KEY', 'http://default.com/api/v1');
      expect(result).toBe('http://default.com/api/v1');
    });
  });

  describe('getRuntimeConfigBoolean', () => {
    beforeEach(() => {
      delete (window as any).ENV;
    });

    it('should return true for "true" string value', () => {
      (window as any).ENV = { AI_ASSISTANT_ENABLED: 'true' };
      const result = getRuntimeConfigBoolean('AI_ASSISTANT_ENABLED', false);
      expect(result).toBe(true);
    });

    it('should return true for "1" string value', () => {
      (window as any).ENV = { AI_ASSISTANT_ENABLED: '1' };
      const result = getRuntimeConfigBoolean('AI_ASSISTANT_ENABLED', false);
      expect(result).toBe(true);
    });

    it('should return false for "false" string value', () => {
      (window as any).ENV = { AI_ASSISTANT_ENABLED: 'false' };
      const result = getRuntimeConfigBoolean('AI_ASSISTANT_ENABLED', true);
      expect(result).toBe(false);
    });

    it('should return default value when not set', () => {
      const result = getRuntimeConfigBoolean('AI_ASSISTANT_ENABLED', true);
      expect(result).toBe(true);
    });
  });

  describe('getRuntimeConfigNumber', () => {
    beforeEach(() => {
      delete (window as any).ENV;
    });

    it('should parse valid number string', () => {
      (window as any).ENV = { MAX_FILE_SIZE: '10485760' };
      const result = getRuntimeConfigNumber('MAX_FILE_SIZE', 0);
      expect(result).toBe(10485760);
    });

    it('should return default for invalid number string', () => {
      (window as any).ENV = { MAX_FILE_SIZE: 'invalid' };
      const result = getRuntimeConfigNumber('MAX_FILE_SIZE', 1024);
      expect(result).toBe(1024);
    });

    it('should return default when not set', () => {
      const result = getRuntimeConfigNumber('MAX_FILE_SIZE', 2048);
      expect(result).toBe(2048);
    });
  });

  describe('config object', () => {
    it('should have API_BASE_URL property', () => {
      expect(config).toHaveProperty('API_BASE_URL');
    });

    it('should have ENVIRONMENT property', () => {
      expect(config).toHaveProperty('ENVIRONMENT');
    });

    it('should have feature flag properties', () => {
      expect(config).toHaveProperty('AI_ASSISTANT_ENABLED');
      expect(config).toHaveProperty('ENABLE_DOCUMENT_UPLOAD');
      expect(config).toHaveProperty('ENABLE_CHAT_EXPORT');
    });
  });

  describe('tenant-aware API_BASE_URL', () => {
    const originalLocation = window.location;
    
    beforeEach(() => {
      delete (window as any).ENV;
      delete (window as any).location;
      (window as any).location = { hostname: 'localhost' };
    });
    
    afterAll(() => {
      window.location = originalLocation;
    });

    it('should use tenant context for API_BASE_URL on localhost', () => {
      window.location.hostname = 'localhost';
      
      const result = getRuntimeConfig('API_BASE_URL', 'http://default.com/api/v1');
      expect(result).toBe('http://localhost:8000/api/v1');
    });

    it('should use tenant context for API_BASE_URL with tenant subdomain', () => {
      window.location.hostname = 'acme.meatscentral.com';
      
      const result = getRuntimeConfig('API_BASE_URL', 'http://default.com/api/v1');
      expect(result).toBe('https://acme-api.meatscentral.com/api/v1');
    });

    it('should prioritize window.ENV over tenant context for API_BASE_URL', () => {
      window.location.hostname = 'acme.meatscentral.com';
      (window as any).ENV = { API_BASE_URL: 'https://override.example.com/api/v1' };
      
      const result = getRuntimeConfig('API_BASE_URL', 'http://default.com/api/v1');
      expect(result).toBe('https://override.example.com/api/v1');
    });
  });

  describe('getCurrentTenant', () => {
    const originalLocation = window.location;
    
    beforeEach(() => {
      delete (window as any).location;
      (window as any).location = { hostname: 'localhost' };
    });
    
    afterAll(() => {
      window.location = originalLocation;
    });

    it('should return null for localhost', () => {
      window.location.hostname = 'localhost';
      
      expect(getCurrentTenant()).toBeNull();
    });

    it('should return tenant for tenant subdomain', () => {
      window.location.hostname = 'acme.meatscentral.com';
      
      expect(getCurrentTenant()).toBe('acme');
    });
  });
});

