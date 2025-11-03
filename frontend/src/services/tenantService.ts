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
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
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
   */
  async uploadLogo(id: string, logoFile: File): Promise<Tenant> {
    const formData = new FormData();
    formData.append('logo', logoFile);

    const response = await apiClient.patch(`/tenants/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
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
   * Update tenant theme colors
   * @param id - Tenant ID
   * @param lightColor - Primary color for light theme (hex format)
   * @param darkColor - Primary color for dark theme (hex format)
   */
  async updateThemeColors(
    id: string,
    lightColor?: string,
    darkColor?: string
  ): Promise<TenantTheme> {
    const data: {
      primary_color_light?: string;
      primary_color_dark?: string;
    } = {};
    
    if (lightColor) data.primary_color_light = lightColor;
    if (darkColor) data.primary_color_dark = darkColor;

    const response = await apiClient.post(`/tenants/${id}/update_theme/`, data);
    return response.data;
  }
}

// Export singleton instance
export const tenantService = new TenantService();
