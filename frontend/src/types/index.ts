/**
 * TypeScript type definitions for ProjectMeats frontend.
 */

// Chat Types
export interface ChatSession {
  id: string;
  title?: string;
  session_status: 'active' | 'completed' | 'archived';
  context_data?: Record<string, any>;
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
  metadata?: Record<string, any>;
  is_processed: boolean;
  created_on: string;
  modified_on: string;
}

// User Types
export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
}

// API Response Types
export interface APIError {
  error: string;
  message?: string;
  details?: Record<string, any>;
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
  onFileUpload: (file: File) => Promise<any>;
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
  extracted_data?: Record<string, any>;
  created_on: string;
}