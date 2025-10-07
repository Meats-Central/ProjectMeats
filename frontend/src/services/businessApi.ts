/**
 * Business API Service for ProjectMeats
 *
 * Handles communication with business entities (suppliers, customers, etc.)
 */
import axios from "axios";

// API Configuration
const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api/v1";

const businessApiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for authentication
businessApiClient.interceptors.request.use(
  (config) => {
    // Add authentication token if available
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Response interceptor for error handling
businessApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle authentication errors
      localStorage.removeItem("authToken");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

// Generic API request helper
async function apiRequest<T>(
  endpoint: string,
  options: { method?: string; data?: any } = {},
): Promise<T> {
  const response = await businessApiClient.request({
    url: endpoint,
    method: options.method || "GET",
    data: options.data,
  });
  return response.data;
}

// Type Definitions
export interface Supplier {
  id?: number;
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  supplier_type?:
    | "meat_processor"
    | "packaging"
    | "equipment"
    | "logistics"
    | "other";
  is_active?: boolean;
  created_on?: string;
  modified_on?: string;
}

export interface Customer {
  id?: number;
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  customer_type?:
    | "restaurant"
    | "retail"
    | "distributor"
    | "food_service"
    | "other";
  is_active?: boolean;
  credit_limit?: number;
  payment_terms?: string;
  created_on?: string;
  modified_on?: string;
}

export interface Contact {
  id?: number;
  name: string;
  email?: string;
  phone?: string;
  position?: string;
  company?: string;
  notes?: string;
  is_active?: boolean;
  contact_type?: "supplier" | "customer" | "internal" | "other";
  created_on?: string;
  modified_on?: string;
}

export interface PurchaseOrder {
  id?: number;
  po_number: string;
  supplier?: number;
  order_date?: string;
  delivery_date?: string;
  status?:
    | "draft"
    | "pending"
    | "approved"
    | "ordered"
    | "received"
    | "cancelled";
  total_amount?: number;
  notes?: string;
  created_by?: number;
  created_on?: string;
  modified_on?: string;
}

export interface AccountsReceivable {
  id?: number;
  invoice_number: string;
  customer?: number;
  amount: number;
  due_date?: string;
  status?: "pending" | "paid" | "overdue" | "cancelled";
  description?: string;
  created_on?: string;
  modified_on?: string;
}

export interface Plant {
  id?: number;
  name: string;
  code?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  phone?: string;
  manager?: string;
  plant_type?: "processing" | "distribution" | "storage" | "office" | "other";
  capacity?: number;
  is_active?: boolean;
  created_on?: string;
  modified_on?: string;
}

export interface Carrier {
  id?: number;
  name: string;
  code?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  carrier_type?: "trucking" | "rail" | "air" | "ocean" | "courier" | "other";
  mc_number?: string;
  dot_number?: string;
  is_active?: boolean;
  created_on?: string;
  modified_on?: string;
}

// Generic CRUD functions
function createEntityAPI<T>(entityName: string) {
  return {
    list: async (): Promise<T[]> => {
      const response = await apiRequest<{ results: T[] }>(`/${entityName}/`);
      return response.results || [];
    },

    get: async (id: number): Promise<T> => {
      return apiRequest<T>(`/${entityName}/${id}/`);
    },

    create: async (data: Partial<T>): Promise<T> => {
      return apiRequest<T>(`/${entityName}/`, {
        method: "POST",
        data: data,
      });
    },

    update: async (id: number, data: Partial<T>): Promise<T> => {
      return apiRequest<T>(`/${entityName}/${id}/`, {
        method: "PUT",
        data: data,
      });
    },

    patch: async (id: number, data: Partial<T>): Promise<T> => {
      return apiRequest<T>(`/${entityName}/${id}/`, {
        method: "PATCH",
        data: data,
      });
    },

    delete: async (id: number): Promise<void> => {
      return apiRequest<void>(`/${entityName}/${id}/`, {
        method: "DELETE",
      });
    },
  };
}

// Export entity APIs
export const suppliersApi = createEntityAPI<Supplier>("suppliers");
export const customersApi = createEntityAPI<Customer>("customers");
export const contactsApi = createEntityAPI<Contact>("contacts");
export const purchaseOrdersApi =
  createEntityAPI<PurchaseOrder>("purchase-orders");
export const accountsReceivableApi = createEntityAPI<AccountsReceivable>(
  "accounts-receivable",
);
export const plantsApi = createEntityAPI<Plant>("plants");
export const carriersApi = createEntityAPI<Carrier>("carriers");

// Export default client
export default businessApiClient;
