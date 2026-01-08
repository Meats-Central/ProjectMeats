/**
 * TypeScript type definitions for ProjectMeats frontend.
 */

// Chat Types
export interface ChatSession {
  id: string;
  title?: string;
  session_status: 'active' | 'completed' | 'archived';
  context_data?: Record<string, unknown>;
  last_activity: string;
  created_on: string;
  modified_on: string;
  message_count: number;
}

export interface ChatMessage {
  id: string;
  session: string;
  message_type: 'user' | 'assistant' | 'system' | 'document';
  content: string;
  metadata?: Record<string, unknown>;
  is_processed: boolean;
  created_on: string;
  modified_on: string;
}

// User Types
export interface UserTenant {
  tenant__id: string;
  tenant__name: string;
  tenant__slug: string;
  role: string;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
  tenants?: UserTenant[];
}

// API Response Types
export interface APIError {
  error: string;
  message?: string;
  details?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Component Props Types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

// File Upload Types
export interface FileUploadProps {
  onFileUpload: (file: File) => Promise<UploadedDocument>;
  disabled?: boolean;
  acceptedFileTypes?: string[];
  maxFileSize?: number;
}

// Document Processing Types
export interface UploadedDocument {
  id: string;
  original_filename: string;
  file_size: number;
  file_type: string;
  document_type: string;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  extracted_text?: string;
  extracted_data?: Record<string, unknown>;
  created_on: string;
}

// ============================================================================
// Business Domain Types (Updated for Chunk 1-5)
// ============================================================================

/**
 * Location entity for tracking pickup and delivery addresses.
 * Added in Chunk 1: Locations App with RLS
 */
export interface Location {
  id: string;
  name: string;
  address: string;
  city: string;
  state_zip: string;
  contact_name?: string;
  contact_phone?: string;
  contact_email?: string;
  how_make_appointment?: string;
  plant_est_number?: string;
  supplier?: string;
  customer?: string;
  created_on: string;
  modified_on: string;
}

/**
 * Lightweight location reference for nested serializers.
 */
export interface LocationListItem {
  id: string;
  name: string;
  city: string;
  state_zip: string;
}

/**
 * Supplier entity.
 * Updated in Chunk 2: Added departments_array, locations
 */
export interface Supplier {
  id: string;
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
  plant?: string;
  proteins?: string[];
  edible_inedible?: string;
  type_of_plant?: string;
  type_of_certificate?: string;
  tested_product?: boolean;
  origin?: string;
  country_origin?: string;
  contacts?: string[];
  shipping_offered?: string;
  how_to_book_pickup?: string;
  offer_contracts?: boolean;
  offers_export_documents?: boolean;
  accounting_payment_terms?: string;
  credit_limits?: string;
  account_line_of_credit?: string;
  fresh_or_frozen?: string;
  package_type?: string;
  net_or_catch?: string;
  departments?: string; // Legacy comma-separated
  departments_array?: string[]; // NEW: Multi-select array
  locations?: LocationListItem[]; // NEW: Nested locations (read-only)
  accounting_terms?: string;
  accounting_line_of_credit?: string;
  credit_app_sent?: boolean;
  credit_app_set_up?: boolean;
  created_on: string;
  modified_on: string;
}

/**
 * Customer entity.
 * Updated in Chunk 2: Added industry_array, preferred_protein_types, locations
 */
export interface Customer {
  id: string;
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
  plant?: string;
  proteins?: string[];
  edible_inedible?: string;
  type_of_plant?: string;
  type_of_certificate?: string;
  purchasing_preference_origin?: string;
  industry?: string; // Legacy single value
  industry_array?: string[]; // NEW: Multi-select array
  preferred_protein_types?: string[]; // NEW: Multi-select array
  contacts?: string[];
  will_pickup_load?: boolean;
  locations?: LocationListItem[]; // NEW: Nested locations (read-only)
  accounting_payment_terms?: string;
  credit_limits?: string;
  account_line_of_credit?: string;
  buyer_contact_name?: string;
  buyer_contact_phone?: string;
  buyer_contact_email?: string;
  contact_title?: string;
  product_exportable?: boolean;
  accounting_terms?: string;
  accounting_line_of_credit?: string;
  created_on: string;
  modified_on: string;
}

/**
 * Carrier entity.
 * Updated in Chunk 3: Added departments_array
 */
export interface Carrier {
  id: string;
  name: string;
  code: string;
  carrier_type?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  mc_number?: string;
  dot_number?: string;
  insurance_provider?: string;
  insurance_policy_number?: string;
  insurance_expiry?: string;
  is_active?: boolean;
  notes?: string;
  my_customer_num_from_carrier?: string;
  accounting_payable_contact_name?: string;
  accounting_payable_contact_phone?: string;
  accounting_payable_contact_email?: string;
  sales_contact_name?: string;
  sales_contact_phone?: string;
  sales_contact_email?: string;
  accounting_payment_terms?: string;
  credit_limits?: string;
  account_line_of_credit?: string;
  departments?: string; // Legacy comma-separated
  departments_array?: string[]; // NEW: Multi-select array
  how_carrier_make_appointment?: string;
  contacts?: string[];
  created_at: string;
  updated_at: string;
  created_by?: string;
  created_by_name?: string;
}

/**
 * Product entity.
 * No changes needed (already uses type_of_protein correctly)
 */
export interface Product {
  id: string;
  product_code: string;
  description_of_product_item: string;
  type_of_protein?: string;
  fresh_or_frozen?: string;
  package_type?: string;
  net_or_catch?: string;
  edible_or_inedible?: string;
  tested_product?: boolean;
  supplier?: string;
  supplier_item_number?: string;
  plants_available?: string;
  origin?: string;
  carton_type?: string;
  pcs_per_carton?: string;
  uom?: string;
  namp?: string;
  usda?: string;
  ub?: string;
  unit_weight?: number;
  is_active?: boolean;
  created_on: string;
  modified_on: string;
}

/**
 * Purchase Order entity.
 * Updated in Chunk 3: Added pick_up_location, delivery_location, carrier_release_format
 */
export interface PurchaseOrder {
  id: string;
  order_number: string;
  supplier: string;
  product?: string;
  total_amount: number;
  status: string;
  order_date: string;
  delivery_date?: string;
  pick_up_date?: string;
  logistics_scenario?: string;
  pick_up_location?: string; // NEW: Location FK
  pick_up_location_details?: LocationListItem; // NEW: Nested (read-only)
  delivery_location?: string; // NEW: Location FK
  delivery_location_details?: LocationListItem; // NEW: Nested (read-only)
  plant?: string;
  carrier?: string;
  carrier_release_format?: string; // NEW: Choice field
  payment_terms?: string;
  notes?: string;
  created_on: string;
  modified_on: string;
}

/**
 * Sales Order entity.
 * Updated in Chunk 3: Added pick_up_location, delivery_location, carrier_release_format, plant_est_number
 */
export interface SalesOrder {
  id: string;
  tenant: string;
  our_sales_order_num: string;
  date_time_stamp: string;
  supplier: string;
  supplier_name?: string;
  customer: string;
  customer_name?: string;
  carrier?: string;
  carrier_name?: string;
  product?: string;
  product_code?: string;
  plant?: string;
  pick_up_location?: string; // NEW: Location FK
  pick_up_location_details?: LocationListItem; // NEW: Nested (read-only)
  delivery_location?: string; // NEW: Location FK
  delivery_location_details?: LocationListItem; // NEW: Nested (read-only)
  contact?: string;
  pick_up_date?: string;
  delivery_date?: string;
  delivery_po_num?: string;
  carrier_release_num?: string;
  carrier_release_format?: string; // NEW: Choice field
  plant_est_number?: string; // NEW: Plant establishment number
  quantity?: number;
  total_weight?: number;
  weight_unit?: string;
  status?: string;
  total_amount?: number;
  notes?: string;
  created_on: string;
  modified_on: string;
}

/**
 * Invoice entity.
 * Updated in Chunk 3: Added payment_terms (uses proper choices now)
 */
export interface Invoice {
  id: string;
  invoice_number: string;
  date_time_stamp: string;
  customer: string;
  sales_order?: string;
  product?: string;
  pick_up_date?: string;
  delivery_date?: string;
  due_date?: string;
  our_sales_order_num?: string;
  delivery_po_num?: string;
  payment_terms?: string; // Updated to use AccountingPaymentTermsChoices
  accounting_payable_contact_name?: string;
  accounting_payable_contact_phone?: string;
  accounting_payable_contact_email?: string;
  type_of_protein?: string; // Updated to use ProteinTypeChoices
  description_of_product_item?: string;
  quantity?: number;
  total_weight?: number;
  weight_unit?: string;
  edible_or_inedible?: string;
  tested_product?: boolean;
  unit_price?: number;
  total_amount: number;
  tax_amount?: number;
  status?: string;
  notes?: string;
  created_on: string;
  modified_on: string;
}
