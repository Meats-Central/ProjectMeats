/**
 * General API Service for ProjectMeats Business Management
 *
 * Handles communication with all Django REST API endpoints.
 */
import axios from "axios";

// API Configuration
const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("authToken");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

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
    const response = await apiClient.get("/suppliers/");
    return response.data.results || response.data;
  }

  async getSupplier(id: number): Promise<Supplier> {
    const response = await apiClient.get(`/suppliers/${id}/`);
    return response.data;
  }

  async createSupplier(supplier: Partial<Supplier>): Promise<Supplier> {
    const response = await apiClient.post("/suppliers/", supplier);
    return response.data;
  }

  async updateSupplier(
    id: number,
    supplier: Partial<Supplier>,
  ): Promise<Supplier> {
    const response = await apiClient.patch(`/suppliers/${id}/`, supplier);
    return response.data;
  }

  async deleteSupplier(id: number): Promise<void> {
    await apiClient.delete(`/suppliers/${id}/`);
  }

  // Customers
  async getCustomers(): Promise<Customer[]> {
    const response = await apiClient.get("/customers/");
    return response.data.results || response.data;
  }

  async getCustomer(id: number): Promise<Customer> {
    const response = await apiClient.get(`/customers/${id}/`);
    return response.data;
  }

  async createCustomer(customer: Partial<Customer>): Promise<Customer> {
    const response = await apiClient.post("/customers/", customer);
    return response.data;
  }

  async updateCustomer(
    id: number,
    customer: Partial<Customer>,
  ): Promise<Customer> {
    const response = await apiClient.patch(`/customers/${id}/`, customer);
    return response.data;
  }

  async deleteCustomer(id: number): Promise<void> {
    await apiClient.delete(`/customers/${id}/`);
  }

  // Purchase Orders
  async getPurchaseOrders(): Promise<PurchaseOrder[]> {
    try {
      const response = await apiClient.get("/purchase-orders/");
      return response.data.results || response.data;
    } catch (error) {
      console.error("Error fetching purchase orders:", error);
      throw new Error(
        "Purchase orders data unavailable. Please check your connection and try again.",
      );
    }
  }

  async getPurchaseOrder(id: number): Promise<PurchaseOrder> {
    const response = await apiClient.get(`/purchase-orders/${id}/`);
    return response.data;
  }

  async createPurchaseOrder(
    order: Partial<PurchaseOrder>,
  ): Promise<PurchaseOrder> {
    const response = await apiClient.post("/purchase-orders/", order);
    return response.data;
  }

  async updatePurchaseOrder(
    id: number,
    order: Partial<PurchaseOrder>,
  ): Promise<PurchaseOrder> {
    const response = await apiClient.patch(`/purchase-orders/${id}/`, order);
    return response.data;
  }

  async deletePurchaseOrder(id: number): Promise<void> {
    await apiClient.delete(`/purchase-orders/${id}/`);
  }

  // Contacts
  async getContacts(): Promise<Contact[]> {
    const response = await apiClient.get("/contacts/");
    return response.data.results || response.data;
  }

  async getContact(id: number): Promise<Contact> {
    const response = await apiClient.get(`/contacts/${id}/`);
    return response.data;
  }

  async createContact(contact: Partial<Contact>): Promise<Contact> {
    const response = await apiClient.post("/contacts/", contact);
    return response.data;
  }

  async updateContact(id: number, contact: Partial<Contact>): Promise<Contact> {
    const response = await apiClient.patch(`/contacts/${id}/`, contact);
    return response.data;
  }

  async deleteContact(id: number): Promise<void> {
    await apiClient.delete(`/contacts/${id}/`);
  }

  // Plants
  async getPlants(): Promise<Plant[]> {
    const response = await apiClient.get("/plants/");
    return response.data.results || response.data;
  }

  async getPlant(id: number): Promise<Plant> {
    const response = await apiClient.get(`/plants/${id}/`);
    return response.data;
  }

  async createPlant(plant: Partial<Plant>): Promise<Plant> {
    const response = await apiClient.post("/plants/", plant);
    return response.data;
  }

  async updatePlant(id: number, plant: Partial<Plant>): Promise<Plant> {
    const response = await apiClient.patch(`/plants/${id}/`, plant);
    return response.data;
  }

  async deletePlant(id: number): Promise<void> {
    await apiClient.delete(`/plants/${id}/`);
  }

  // Carriers
  async getCarriers(): Promise<Carrier[]> {
    const response = await apiClient.get("/carriers/");
    return response.data.results || response.data;
  }

  async getCarrier(id: number): Promise<Carrier> {
    const response = await apiClient.get(`/carriers/${id}/`);
    return response.data;
  }

  async createCarrier(carrier: Partial<Carrier>): Promise<Carrier> {
    const response = await apiClient.post("/carriers/", carrier);
    return response.data;
  }

  async updateCarrier(id: number, carrier: Partial<Carrier>): Promise<Carrier> {
    const response = await apiClient.patch(`/carriers/${id}/`, carrier);
    return response.data;
  }

  async deleteCarrier(id: number): Promise<void> {
    await apiClient.delete(`/carriers/${id}/`);
  }

  // Accounts Receivables
  async getAccountsReceivables(): Promise<AccountsReceivable[]> {
    const response = await apiClient.get("/accounts-receivables/");
    return response.data.results || response.data;
  }

  async getAccountsReceivable(id: number): Promise<AccountsReceivable> {
    const response = await apiClient.get(`/accounts-receivables/${id}/`);
    return response.data;
  }

  async createAccountsReceivable(
    ar: Partial<AccountsReceivable>,
  ): Promise<AccountsReceivable> {
    const response = await apiClient.post("/accounts-receivables/", ar);
    return response.data;
  }

  async updateAccountsReceivable(
    id: number,
    ar: Partial<AccountsReceivable>,
  ): Promise<AccountsReceivable> {
    const response = await apiClient.patch(`/accounts-receivables/${id}/`, ar);
    return response.data;
  }

  async deleteAccountsReceivable(id: number): Promise<void> {
    await apiClient.delete(`/accounts-receivables/${id}/`);
  }
}

// Export singleton instance
export const apiService = new ApiService();
