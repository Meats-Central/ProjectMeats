/**
 * Tests for runtime configuration utility
 */

// This file is a module (required for TypeScript isolatedModules)
export {};

describe('Runtime Configuration', () => {
  describe('getRuntimeConfig', () => {
    beforeEach(() => {
      // Clear window.ENV before each test
      delete (window as any).ENV;
    });

    it('should prioritize window.ENV over process.env', () => {
      // Import the functions fresh
      const { getRuntimeConfig } = require('./runtime');
      
      // Set both window.ENV and process.env
      (window as any).ENV = { API_BASE_URL: 'https://runtime.example.com/api/v1' };
      process.env.REACT_APP_API_BASE_URL = 'https://buildtime.example.com/api/v1';

      const result = getRuntimeConfig('API_BASE_URL', 'http://default.com/api/v1');
      expect(result).toBe('https://runtime.example.com/api/v1');
    });

    it('should fall back to process.env when window.ENV is not available', () => {
      const { getRuntimeConfig } = require('./runtime');
      
      process.env.REACT_APP_API_BASE_URL = 'https://buildtime.example.com/api/v1';

      const result = getRuntimeConfig('API_BASE_URL', 'http://default.com/api/v1');
      expect(result).toBe('https://buildtime.example.com/api/v1');
    });

    it('should use default value when neither window.ENV nor process.env is set', () => {
      const { getRuntimeConfig } = require('./runtime');
      
      delete process.env.REACT_APP_API_BASE_URL;
      const result = getRuntimeConfig('API_BASE_URL', 'http://default.com/api/v1');
      expect(result).toBe('http://default.com/api/v1');
    });

    it('should handle empty string values by falling back', () => {
      const { getRuntimeConfig } = require('./runtime');
      
      (window as any).ENV = { API_BASE_URL: '' };
      delete process.env.REACT_APP_API_BASE_URL;

      const result = getRuntimeConfig('API_BASE_URL', 'http://default.com/api/v1');
      expect(result).toBe('http://default.com/api/v1');
    });
  });

  describe('getRuntimeConfigBoolean', () => {
    beforeEach(() => {
      delete (window as any).ENV;
    });

    it('should return true for "true" string value', () => {
      const { getRuntimeConfigBoolean } = require('./runtime');
      
      (window as any).ENV = { AI_ASSISTANT_ENABLED: 'true' };
      const result = getRuntimeConfigBoolean('AI_ASSISTANT_ENABLED', false);
      expect(result).toBe(true);
    });

    it('should return true for "1" string value', () => {
      const { getRuntimeConfigBoolean } = require('./runtime');
      
      (window as any).ENV = { AI_ASSISTANT_ENABLED: '1' };
      const result = getRuntimeConfigBoolean('AI_ASSISTANT_ENABLED', false);
      expect(result).toBe(true);
    });

    it('should return false for "false" string value', () => {
      const { getRuntimeConfigBoolean } = require('./runtime');
      
      (window as any).ENV = { AI_ASSISTANT_ENABLED: 'false' };
      const result = getRuntimeConfigBoolean('AI_ASSISTANT_ENABLED', true);
      expect(result).toBe(false);
    });

    it('should return default value when not set', () => {
      const { getRuntimeConfigBoolean } = require('./runtime');
      
      delete process.env.REACT_APP_AI_ASSISTANT_ENABLED;
      const result = getRuntimeConfigBoolean('AI_ASSISTANT_ENABLED', true);
      expect(result).toBe(true);
    });
  });

  describe('getRuntimeConfigNumber', () => {
    beforeEach(() => {
      delete (window as any).ENV;
    });

    it('should parse valid number string', () => {
      const { getRuntimeConfigNumber } = require('./runtime');
      
      (window as any).ENV = { MAX_FILE_SIZE: '10485760' };
      const result = getRuntimeConfigNumber('MAX_FILE_SIZE', 0);
      expect(result).toBe(10485760);
    });

    it('should return default for invalid number string', () => {
      const { getRuntimeConfigNumber } = require('./runtime');
      
      (window as any).ENV = { MAX_FILE_SIZE: 'invalid' };
      const result = getRuntimeConfigNumber('MAX_FILE_SIZE', 1024);
      expect(result).toBe(1024);
    });

    it('should return default when not set', () => {
      const { getRuntimeConfigNumber } = require('./runtime');
      
      delete process.env.REACT_APP_MAX_FILE_SIZE;
      const result = getRuntimeConfigNumber('MAX_FILE_SIZE', 2048);
      expect(result).toBe(2048);
    });
  });

  describe('config object', () => {
    it('should have API_BASE_URL property', () => {
      const { config } = require('./runtime');
      expect(config).toHaveProperty('API_BASE_URL');
    });

    it('should have ENVIRONMENT property', () => {
      const { config } = require('./runtime');
      expect(config).toHaveProperty('ENVIRONMENT');
    });

    it('should have feature flag properties', () => {
      const { config } = require('./runtime');
      expect(config).toHaveProperty('AI_ASSISTANT_ENABLED');
      expect(config).toHaveProperty('ENABLE_DOCUMENT_UPLOAD');
      expect(config).toHaveProperty('ENABLE_CHAT_EXPORT');
    });
  });
});

