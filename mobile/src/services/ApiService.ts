import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { 
  LoginRequest, 
  LoginResponse, 
  User, 
  Tenant, 
  UserTenant, 
  ApiResponse,
  Customer,
  Supplier,
  Contact,
  Plant,
  Carrier
} from '../types';

class ApiServiceClass {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    // Use the same backend URL as the web frontend
    // In production, this should come from environment variables
    this.baseURL = __DEV__ 
      ? 'http://localhost:8000/api/v1' 
      : 'https://your-production-domain.com/api/v1';

    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  setAuthToken(token: string) {
    this.api.defaults.headers.common['Authorization'] = `Token ${token}`;
  }

  removeAuthToken() {
    delete this.api.defaults.headers.common['Authorization'];
  }

  // Authentication endpoints
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.api.post('/auth/login/', credentials);
    return response.data;
  }

  async logout(): Promise<void> {
    await this.api.post('/auth/logout/');
  }

  // Tenant endpoints
  async getTenants(): Promise<ApiResponse<Tenant>> {
    const response = await this.api.get('/api/tenants/');
    return response.data;
  }

  async getMyTenants(): Promise<UserTenant[]> {
    const response = await this.api.get('/api/tenants/my_tenants/');
    return response.data;
  }

  async createTenant(tenantData: Partial<Tenant>): Promise<Tenant> {
    const response = await this.api.post('/api/tenants/', tenantData);
    return response.data;
  }

  async getTenant(id: string): Promise<Tenant> {
    const response = await this.api.get(`/api/tenants/${id}/`);
    return response.data;
  }

  async updateTenant(id: string, tenantData: Partial<Tenant>): Promise<Tenant> {
    const response = await this.api.patch(`/api/tenants/${id}/`, tenantData);
    return response.data;
  }

  // Customer endpoints
  async getCustomers(): Promise<ApiResponse<Customer>> {
    const response = await this.api.get('/customers/');
    return response.data;
  }

  async getCustomer(id: number): Promise<Customer> {
    const response = await this.api.get(`/customers/${id}/`);
    return response.data;
  }

  async createCustomer(customerData: Partial<Customer>): Promise<Customer> {
    const response = await this.api.post('/customers/', customerData);
    return response.data;
  }

  async updateCustomer(id: number, customerData: Partial<Customer>): Promise<Customer> {
    const response = await this.api.patch(`/customers/${id}/`, customerData);
    return response.data;
  }

  async deleteCustomer(id: number): Promise<void> {
    await this.api.delete(`/customers/${id}/`);
  }

  // Supplier endpoints
  async getSuppliers(): Promise<ApiResponse<Supplier>> {
    const response = await this.api.get('/suppliers/');
    return response.data;
  }

  async getSupplier(id: number): Promise<Supplier> {
    const response = await this.api.get(`/suppliers/${id}/`);
    return response.data;
  }

  async createSupplier(supplierData: Partial<Supplier>): Promise<Supplier> {
    const response = await this.api.post('/suppliers/', supplierData);
    return response.data;
  }

  async updateSupplier(id: number, supplierData: Partial<Supplier>): Promise<Supplier> {
    const response = await this.api.patch(`/suppliers/${id}/`, supplierData);
    return response.data;
  }

  async deleteSupplier(id: number): Promise<void> {
    await this.api.delete(`/suppliers/${id}/`);
  }

  // Contact endpoints
  async getContacts(): Promise<ApiResponse<Contact>> {
    const response = await this.api.get('/contacts/');
    return response.data;
  }

  async getContact(id: number): Promise<Contact> {
    const response = await this.api.get(`/contacts/${id}/`);
    return response.data;
  }

  async createContact(contactData: Partial<Contact>): Promise<Contact> {
    const response = await this.api.post('/contacts/', contactData);
    return response.data;
  }

  async updateContact(id: number, contactData: Partial<Contact>): Promise<Contact> {
    const response = await this.api.patch(`/contacts/${id}/`, contactData);
    return response.data;
  }

  async deleteContact(id: number): Promise<void> {
    await this.api.delete(`/contacts/${id}/`);
  }

  // Plant endpoints
  async getPlants(): Promise<ApiResponse<Plant>> {
    const response = await this.api.get('/plants/');
    return response.data;
  }

  async getPlant(id: number): Promise<Plant> {
    const response = await this.api.get(`/plants/${id}/`);
    return response.data;
  }

  async createPlant(plantData: Partial<Plant>): Promise<Plant> {
    const response = await this.api.post('/plants/', plantData);
    return response.data;
  }

  async updatePlant(id: number, plantData: Partial<Plant>): Promise<Plant> {
    const response = await this.api.patch(`/plants/${id}/`, plantData);
    return response.data;
  }

  async deletePlant(id: number): Promise<void> {
    await this.api.delete(`/plants/${id}/`);
  }

  // Carrier endpoints
  async getCarriers(): Promise<ApiResponse<Carrier>> {
    const response = await this.api.get('/carriers/');
    return response.data;
  }

  async getCarrier(id: number): Promise<Carrier> {
    const response = await this.api.get(`/carriers/${id}/`);
    return response.data;
  }

  async createCarrier(carrierData: Partial<Carrier>): Promise<Carrier> {
    const response = await this.api.post('/carriers/', carrierData);
    return response.data;
  }

  async updateCarrier(id: number, carrierData: Partial<Carrier>): Promise<Carrier> {
    const response = await this.api.patch(`/carriers/${id}/`, carrierData);
    return response.data;
  }

  async deleteCarrier(id: number): Promise<void> {
    await this.api.delete(`/carriers/${id}/`);
  }

  // Health check
  async healthCheck(): Promise<any> {
    const response = await this.api.get('/health/');
    return response.data;
  }
}

export const ApiService = new ApiServiceClass();