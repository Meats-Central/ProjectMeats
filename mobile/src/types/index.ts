// Base types shared between web and mobile apps

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  date_joined: string;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  domain?: string;
  contact_email: string;
  contact_phone: string;
  is_active: boolean;
  is_trial: boolean;
  trial_ends_at?: string;
  user_count: number;
  is_trial_expired: boolean;
  created_at: string;
  updated_at: string;
  settings: Record<string, any>;
}

export interface TenantUser {
  id: number;
  tenant: Tenant;
  user: User;
  role: 'owner' | 'admin' | 'manager' | 'user' | 'readonly';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserTenant {
  tenant_id: string;
  tenant_name: string;
  tenant_slug: string;
  role: 'owner' | 'admin' | 'manager' | 'user' | 'readonly';
  is_active: boolean;
  is_trial: boolean;
  created_at: string;
}

// API Response types
export interface ApiResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface ApiError {
  detail?: string;
  [key: string]: any;
}

// Navigation types
export type RootStackParamList = {
  Login: undefined;
  Tenants: undefined;
  Home: undefined;
};

// Authentication types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

// Common entity types (shared with backend)
export interface Customer {
  id: number;
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  street_address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  plant?: number;
  proteins?: number[];
  edible_inedible?: string;
  type_of_plant?: string;
  purchasing_preference_origin?: string;
  industry?: string;
  contacts?: number[];
  will_pickup_load?: boolean;
  accounting_terms?: string;
  accounting_line_of_credit?: string;
  created_on: string;
  modified_on: string;
}

export interface Supplier {
  id: number;
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  street_address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  plant?: number;
  proteins?: number[];
  edible_inedible?: string;
  type_of_plant?: string;
  type_of_certificate?: string;
  tested_product?: boolean;
  origin?: string;
  country_origin?: string;
  contacts?: number[];
  shipping_offered?: string;
  how_to_book_pickup?: string;
  offer_contracts?: boolean;
  offers_export_documents?: boolean;
  accounting_terms?: string;
  accounting_line_of_credit?: string;
  credit_app_sent?: boolean;
  credit_app_set_up?: boolean;
  created_on: string;
  modified_on: string;
}

export interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  position?: string;
  customer?: number;
  supplier?: number;
  created_on: string;
  modified_on: string;
}

export interface Plant {
  id: number;
  name: string;
  location: string;
  capacity?: number;
  description?: string;
  created_on: string;
  modified_on: string;
}

export interface Carrier {
  id: number;
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  service_area?: string;
  created_on: string;
  modified_on: string;
}