/**
 * Tenant API Service
 *
 * Handles tenant-related API calls including branding and logo management.
 */
import axios from 'axios';
import { config } from '../config/runtime';

// API Configuration
const API_BASE_URL = config.API_BASE_URL;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Allow cookies for authentication
  xsrfCookieName: 'csrftoken', // Django's CSRF cookie name
  xsrfHeaderName: 'X-CSRFToken', // Django's expected CSRF header
});

// Request interceptor for authentication and tenant context
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    // Add tenant ID header if available
    const tenantId = localStorage.getItem('tenantId');
    if (tenantId) {
      config.headers['X-Tenant-ID'] = tenantId;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  domain?: string;
  contact_email: string;
  contact_phone?: string;
  is_active: boolean;
  is_trial: boolean;
  trial_ends_at?: string;
  user_count?: number;
  is_trial_expired?: boolean;
  created_at: string;
  updated_at: string;
  settings?: Record<string, unknown>;
  logo?: string | null;
}

export interface TenantTheme {
  logo_url: string | null;
  primary_color_light: string;
  primary_color_dark: string;
  name: string;
}

// Tenant API Service Class
export class TenantService {
  /**
   * Get the current user's tenants
   */
  async getMyTenants(): Promise<Tenant[]> {
    const response = await apiClient.get('/tenants/my_tenants/');
    return response.data;
  }

  /**
   * Get current tenant's theme settings
   */
  async getCurrentTheme(): Promise<TenantTheme> {
    const response = await apiClient.get('/tenants/current_theme/');
    return response.data;
  }

  /**
   * Get a specific tenant by ID
   */
  async getTenant(id: string): Promise<Tenant> {
    const response = await apiClient.get(`/tenants/${id}/`);
    return response.data;
  }

  /**
   * Update tenant information
   */
  async updateTenant(id: string, data: Partial<Tenant>): Promise<Tenant> {
    const response = await apiClient.patch(`/tenants/${id}/`, data);
    return response.data;
  }

  /**
   * Upload tenant logo
   * @param id - Tenant ID
   * @param logoFile - Logo image file
   * @throws {Error} With detailed message if upload fails
   */
  async uploadLogo(id: string, logoFile: File): Promise<Tenant> {
    try {
      const formData = new FormData();
      formData.append('logo', logoFile);

      const response = await apiClient.patch(`/tenants/${id}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      // Enhanced error handling with detailed messages
      if (error.response) {
        // Server responded with error
        const status = error.response.status;
        const data = error.response.data;
        
        if (status === 400) {
          // Validation error - extract specific message
          if (data.logo) {
            throw new Error(`Logo validation failed: ${Array.isArray(data.logo) ? data.logo.join(', ') : data.logo}`);
          } else if (data.detail) {
            throw new Error(`Upload failed: ${data.detail}`);
          } else {
            throw new Error(`Upload failed: ${JSON.stringify(data)}`);
          }
        } else if (status === 413) {
          throw new Error('Logo file is too large. Please use a file smaller than 5MB.');
        } else if (status === 500) {
          throw new Error('Server error while uploading logo. Please check server logs or try again later.');
        } else {
          throw new Error(`Upload failed with status ${status}: ${data.detail || 'Unknown error'}`);
        }
      } else if (error.request) {
        // Request made but no response
        throw new Error('Network error: Unable to reach server. Please check your connection.');
      } else {
        // Error setting up request
        throw new Error(`Upload error: ${error.message}`);
      }
    }
  }

  /**
   * Remove tenant logo
   * @param id - Tenant ID
   */
  async removeLogo(id: string): Promise<Tenant> {
    const response = await apiClient.patch(`/tenants/${id}/`, {
      logo: null,
    });
    return response.data;
  }

  /**
   * Update tenant theme colors via settings PATCH
   * This is the direct API method that sends colors as settings.theme
   * 
   * @param id - Tenant ID
   * @param colors - Theme colors object
   * @throws {Error} With detailed message if update fails
   */
  async updateTenantSettings(
    id: string,
    settings: {
      theme?: {
        primary_color?: string;
        primary_color_light?: string;
        primary_color_dark?: string;
      };
      [key: string]: any;
    }
  ): Promise<Tenant> {
    try {
      // CRITICAL: Explicitly set Content-Type to application/json
      // This prevents HTML response issues when updating settings
      const response = await apiClient.patch(
        `/tenants/${id}/`,
        { settings },
        {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error: any) {
      // Enhanced error handling
      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;
        
        // Check if response is HTML instead of JSON (common issue)
        const contentType = error.response.headers['content-type'];
        if (contentType && contentType.includes('text/html')) {
          console.error('Received HTML response instead of JSON:', {
            status,
            url: error.config?.url,
            method: error.config?.method,
          });
          throw new Error('Server returned HTML instead of JSON. Check server configuration and CORS settings.');
        }
        
        if (status === 400) {
          // Validation error - extract specific message
          if (data.settings) {
            const settingsErrors = typeof data.settings === 'object' 
              ? JSON.stringify(data.settings) 
              : data.settings;
            throw new Error(`Settings validation failed: ${settingsErrors}`);
          } else if (data.detail) {
            throw new Error(`Settings update failed: ${data.detail}`);
          } else {
            throw new Error(`Settings update failed: ${JSON.stringify(data)}`);
          }
        } else if (status === 403) {
          throw new Error('Permission denied: Only tenant owners and admins can update settings.');
        } else if (status === 500) {
          throw new Error('Server error while updating settings. Please check server logs or try again later.');
        } else {
          throw new Error(`Settings update failed with status ${status}: ${data.detail || 'Unknown error'}`);
        }
      } else if (error.request) {
        throw new Error('Network error: Unable to reach server. Please check your connection.');
      } else {
        throw new Error(`Settings update error: ${error.message}`);
      }
    }
  }

  /**
   * Update tenant theme colors via settings PATCH
   * @deprecated Use updateTenantSettings for direct settings update
   * @param id - Tenant ID
   * @param lightColor - Primary color for light theme (hex format)
   * @param darkColor - Primary color for dark theme (hex format)
   * @throws {Error} With detailed message if update fails
   */
  async updateThemeColors(
    id: string,
    lightColor?: string,
    darkColor?: string
  ): Promise<TenantTheme> {
    try {
      const data: {
        primary_color_light?: string;
        primary_color_dark?: string;
      } = {};
      
      if (lightColor) data.primary_color_light = lightColor;
      if (darkColor) data.primary_color_dark = darkColor;

      const response = await apiClient.post(`/tenants/${id}/update_theme/`, data);
      return response.data;
    } catch (error: any) {
      // Enhanced error handling
      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;
        
        if (status === 400) {
          // Validation error
          if (data.error) {
            throw new Error(`Theme update failed: ${data.error}`);
          } else {
            throw new Error(`Theme update failed: ${JSON.stringify(data)}`);
          }
        } else if (status === 403) {
          throw new Error('Permission denied: Only tenant owners and admins can update theme colors.');
        } else if (status === 500) {
          throw new Error('Server error while updating theme. Please check server logs or try again later.');
        } else {
          throw new Error(`Theme update failed with status ${status}: ${data.detail || data.error || 'Unknown error'}`);
        }
      } else if (error.request) {
        throw new Error('Network error: Unable to reach server. Please check your connection.');
      } else {
        throw new Error(`Theme update error: ${error.message}`);
      }
    }
  }
}

// Export singleton instance
export const tenantService = new TenantService();
