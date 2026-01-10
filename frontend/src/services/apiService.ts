/**
 * General API Service for ProjectMeats Business Management
 *
 * Handles communication with all Django REST API endpoints.
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

// Helper function for enhanced error handling with Axios error details
interface AxiosError {
  response?: {
    data?: {
      message?: string;
      error?: string;
      detail?: string;
      details?: string;
      [key: string]: unknown;
    };
    status?: number;
    statusText?: string;
  };
  request?: unknown;
  message?: string;
  code?: string;
  config?: {
    url?: string;
    method?: string;
    baseURL?: string;
  };
}

function getErrorMessage(error: unknown): string {
  if (typeof error === 'string') return error;
  
  if (error && typeof error === 'object') {
    const axiosError = error as AxiosError;
    
    // If we have a response from the server, extract the error message
    if (axiosError.response?.data) {
      const data = axiosError.response.data;
      const errorMsg = data.message || data.error || data.detail || data.details;
      if (errorMsg && typeof errorMsg === 'string') {
        return errorMsg;
      }
      // If data is an object with multiple errors, stringify it
      if (typeof data === 'object' && Object.keys(data).length > 0) {
        return JSON.stringify(data);
      }
    }
    
    // Network errors (no response from server)
    if (axiosError.request && !axiosError.response) {
      const url = axiosError.config?.url || 'unknown endpoint';
      const baseURL = axiosError.config?.baseURL || '';
      
      // Properly construct full URL
      let fullURL = url;
      if (baseURL) {
        try {
          // Use URL constructor for proper URL joining
          fullURL = new URL(url, baseURL).href;
        } catch {
          // Fallback to simple concatenation if URL constructor fails
          fullURL = baseURL.replace(/\/$/, '') + '/' + url.replace(/^\//, '');
        }
      }
      
      // Provide more specific error messages based on error code
      if (axiosError.code === 'ERR_NETWORK') {
        return `Unable to connect to the server at ${fullURL}. Please check your internet connection or contact support.`;
      }
      if (axiosError.code === 'ECONNABORTED' || axiosError.message?.includes('timeout')) {
        return `Request to ${fullURL} timed out. The server may be experiencing high load. Please try again.`;
      }
      if (axiosError.code === 'ERR_BAD_REQUEST') {
        return `Invalid request to ${fullURL}. Please contact support.`;
      }
      
      // Generic network error with URL
      return `Network error while connecting to ${fullURL}. ${axiosError.message || 'Please check your connection and try again.'}`;
    }
    
    // HTTP error responses with status codes
    if (axiosError.response?.status) {
      const status = axiosError.response.status;
      const statusText = axiosError.response.statusText || '';
      
      if (status === 401) return 'Authentication required. Please log in again.';
      if (status === 403) return 'You do not have permission to perform this action.';
      if (status === 404) return 'The requested resource was not found.';
      if (status === 500) return 'Server error. Please try again later or contact support.';
      if (status >= 400 && status < 500) return `Request error: ${statusText}`;
      if (status >= 500) return `Server error: ${statusText}`;
    }
    
    // Fallback to error message if available
    if (axiosError.message) return axiosError.message;
  }
  
  if (error instanceof Error) return error.message;
  
  return 'An unknown error occurred. Please try again.';
}

// Types
export interface Supplier {
  id: number;
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  departments_array?: string[]; // Phase 4: ArrayField
  products?: number[]; // Product IDs for M2M relationship
  created_at: string;
  updated_at: string;
}

export interface Customer {
  id: number;
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  industry_array?: string[]; // Phase 4: ArrayField
  preferred_protein_types?: string[]; // Phase 4: ArrayField
  products?: number[]; // Product IDs for M2M relationship
  created_at: string;
  updated_at: string;
}

export interface PurchaseOrder {
  id: number;
  order_number: string;
  supplier: number;
  total_amount: number;
  status: string;
  order_date: string;
  delivery_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  logistics_scenario?: string;
  total_weight?: number;
  weight_unit?: string;
  pick_up_location?: string | null; // Phase 4: Location UUID
  delivery_location?: string | null; // Phase 4: Location UUID
}

export interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  company?: string;
  position?: string;
  created_at: string;
  updated_at: string;
}

export interface Plant {
  id: number;
  name: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  phone?: string;
  manager?: string;
  created_at: string;
  updated_at: string;
}

export interface Carrier {
  id: number;
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  service_areas?: string;
  created_at: string;
  updated_at: string;
}

export interface AccountsReceivable {
  id: number;
  customer: number;
  invoice_number: string;
  amount: number;
  due_date: string;
  status: string;
  created_at: string;
  updated_at: string;
}

// API Service Class
export class ApiService {
  // Suppliers
  async getSuppliers(): Promise<Supplier[]> {
    const response = await apiClient.get('/suppliers/');
    return response.data.results || response.data;
  }

  async getSupplier(id: number): Promise<Supplier> {
    const response = await apiClient.get(`/suppliers/${id}/`);
    return response.data;
  }

  async createSupplier(supplier: Partial<Supplier>): Promise<Supplier> {
    try {
      // Log request details for debugging (excluding sensitive data)
      // eslint-disable-next-line no-console
      console.debug('[API] Creating supplier:', {
        endpoint: '/suppliers/',
        hasAuth: !!localStorage.getItem('authToken'),
        hasTenant: !!localStorage.getItem('tenantId'),
        baseURL: API_BASE_URL,
      });
      
      const response = await apiClient.post('/suppliers/', supplier);
      // eslint-disable-next-line no-console
      console.debug('[API] Supplier created successfully:', response.data);
      return response.data;
    } catch (error: unknown) {
      // Log detailed error information for debugging
      const axiosError = error as AxiosError;
      // eslint-disable-next-line no-console
      console.error('[API] Failed to create supplier:', {
        message: getErrorMessage(error),
        status: axiosError.response?.status,
        statusText: axiosError.response?.statusText,
        errorCode: axiosError.code,
        url: axiosError.config?.url,
        baseURL: axiosError.config?.baseURL,
        hasResponse: !!axiosError.response,
        hasRequest: !!axiosError.request,
      });
      
      // Re-throw with enhanced error message
      throw new Error(getErrorMessage(error));
    }
  }

  async updateSupplier(id: number, supplier: Partial<Supplier>): Promise<Supplier> {
    try {
      // eslint-disable-next-line no-console
      console.debug('[API] Updating supplier:', {
        id,
        endpoint: `/suppliers/${id}/`,
        baseURL: API_BASE_URL,
      });
      
      const response = await apiClient.patch(`/suppliers/${id}/`, supplier);
      // eslint-disable-next-line no-console
      console.debug('[API] Supplier updated successfully:', response.data);
      return response.data;
    } catch (error: unknown) {
      const axiosError = error as AxiosError;
      // eslint-disable-next-line no-console
      console.error('[API] Failed to update supplier:', {
        message: getErrorMessage(error),
        status: axiosError.response?.status,
        errorCode: axiosError.code,
      });
      
      throw new Error(getErrorMessage(error));
    }
  }

  async deleteSupplier(id: number): Promise<void> {
    await apiClient.delete(`/suppliers/${id}/`);
  }

  // Customers
  async getCustomers(): Promise<Customer[]> {
    const response = await apiClient.get('/customers/');
    return response.data.results || response.data;
  }

  async getCustomer(id: number): Promise<Customer> {
    const response = await apiClient.get(`/customers/${id}/`);
    return response.data;
  }

  async createCustomer(customer: Partial<Customer>): Promise<Customer> {
    try {
      const response = await apiClient.post('/customers/', customer);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to create customer: ${getErrorMessage(error)}`);
    }
  }

  async updateCustomer(id: number, customer: Partial<Customer>): Promise<Customer> {
    try {
      const response = await apiClient.patch(`/customers/${id}/`, customer);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to update customer: ${getErrorMessage(error)}`);
    }
  }

  async deleteCustomer(id: number): Promise<void> {
    await apiClient.delete(`/customers/${id}/`);
  }

  // Purchase Orders
  async getPurchaseOrders(): Promise<PurchaseOrder[]> {
    try {
      const response = await apiClient.get('/purchase-orders/');
      return response.data.results || response.data;
    } catch (error) {
      console.error('Error fetching purchase orders:', error);
      throw new Error(
        'Purchase orders data unavailable. Please check your connection and try again.'
      );
    }
  }

  async getPurchaseOrder(id: number): Promise<PurchaseOrder> {
    const response = await apiClient.get(`/purchase-orders/${id}/`);
    return response.data;
  }

  async createPurchaseOrder(order: Partial<PurchaseOrder>): Promise<PurchaseOrder> {
    try {
      const response = await apiClient.post('/purchase-orders/', order);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to create purchase order: ${getErrorMessage(error)}`);
    }
  }

  async updatePurchaseOrder(id: number, order: Partial<PurchaseOrder>): Promise<PurchaseOrder> {
    try {
      const response = await apiClient.patch(`/purchase-orders/${id}/`, order);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to update purchase order: ${getErrorMessage(error)}`);
    }
  }

  async deletePurchaseOrder(id: number): Promise<void> {
    await apiClient.delete(`/purchase-orders/${id}/`);
  }

  // Contacts
  async getContacts(): Promise<Contact[]> {
    const response = await apiClient.get('/contacts/');
    return response.data.results || response.data;
  }

  async getContact(id: number): Promise<Contact> {
    const response = await apiClient.get(`/contacts/${id}/`);
    return response.data;
  }

  async createContact(contact: Partial<Contact>): Promise<Contact> {
    try {
      const response = await apiClient.post('/contacts/', contact);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to create contact: ${getErrorMessage(error)}`);
    }
  }

  async updateContact(id: number, contact: Partial<Contact>): Promise<Contact> {
    try {
      const response = await apiClient.patch(`/contacts/${id}/`, contact);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to update contact: ${getErrorMessage(error)}`);
    }
  }

  async deleteContact(id: number): Promise<void> {
    await apiClient.delete(`/contacts/${id}/`);
  }

  // Plants
  async getPlants(): Promise<Plant[]> {
    const response = await apiClient.get('/plants/');
    return response.data.results || response.data;
  }

  async getPlant(id: number): Promise<Plant> {
    const response = await apiClient.get(`/plants/${id}/`);
    return response.data;
  }

  async createPlant(plant: Partial<Plant>): Promise<Plant> {
    try {
      const response = await apiClient.post('/plants/', plant);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to create plant: ${getErrorMessage(error)}`);
    }
  }

  async updatePlant(id: number, plant: Partial<Plant>): Promise<Plant> {
    try {
      const response = await apiClient.patch(`/plants/${id}/`, plant);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to update plant: ${getErrorMessage(error)}`);
    }
  }

  async deletePlant(id: number): Promise<void> {
    await apiClient.delete(`/plants/${id}/`);
  }

  // Carriers
  async getCarriers(): Promise<Carrier[]> {
    const response = await apiClient.get('/carriers/');
    return response.data.results || response.data;
  }

  async getCarrier(id: number): Promise<Carrier> {
    const response = await apiClient.get(`/carriers/${id}/`);
    return response.data;
  }

  async createCarrier(carrier: Partial<Carrier>): Promise<Carrier> {
    try {
      const response = await apiClient.post('/carriers/', carrier);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to create carrier: ${getErrorMessage(error)}`);
    }
  }

  async updateCarrier(id: number, carrier: Partial<Carrier>): Promise<Carrier> {
    try {
      const response = await apiClient.patch(`/carriers/${id}/`, carrier);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to update carrier: ${getErrorMessage(error)}`);
    }
  }

  async deleteCarrier(id: number): Promise<void> {
    await apiClient.delete(`/carriers/${id}/`);
  }

  // Accounts Receivables
  async getAccountsReceivables(): Promise<AccountsReceivable[]> {
    const response = await apiClient.get('/accounts-receivables/');
    return response.data.results || response.data;
  }

  async getAccountsReceivable(id: number): Promise<AccountsReceivable> {
    const response = await apiClient.get(`/accounts-receivables/${id}/`);
    return response.data;
  }

  async createAccountsReceivable(ar: Partial<AccountsReceivable>): Promise<AccountsReceivable> {
    try {
      const response = await apiClient.post('/accounts-receivables/', ar);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to create accounts receivable: ${getErrorMessage(error)}`);
    }
  }

  async updateAccountsReceivable(
    id: number,
    ar: Partial<AccountsReceivable>
  ): Promise<AccountsReceivable> {
    try {
      const response = await apiClient.patch(`/accounts-receivables/${id}/`, ar);
      return response.data;
    } catch (error: unknown) {
      throw new Error(`Failed to update accounts receivable: ${getErrorMessage(error)}`);
    }
  }

  async deleteAccountsReceivable(id: number): Promise<void> {
    await apiClient.delete(`/accounts-receivables/${id}/`);
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export apiClient for direct axios usage in components
export { apiClient };
