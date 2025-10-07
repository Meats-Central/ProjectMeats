// Shared utilities between web and mobile applications

/**
 * Format currency values
 */
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

/**
 * Format dates for display
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
};

/**
 * Format date and time for display
 */
export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

/**
 * Generate display name from user object
 */
export const getUserDisplayName = (user: {
  first_name?: string;
  last_name?: string;
  username: string;
}): string => {
  if (user.first_name && user.last_name) {
    return `${user.first_name} ${user.last_name}`;
  } else if (user.first_name) {
    return user.first_name;
  }
  return user.username;
};

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate phone number format (basic)
 */
export const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
  return phoneRegex.test(phone);
};

/**
 * Generate slug from string (for tenant slugs, etc.)
 */
export const generateSlug = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
    .replace(/^-|-$/g, '');
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Capitalize first letter of each word
 */
export const capitalizeWords = (text: string): string => {
  return text.replace(/\b\w/g, (char) => char.toUpperCase());
};

/**
 * Generate random color (for avatars, etc.)
 */
export const generateRandomColor = (seed: string): string => {
  const colors = [
    '#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6',
    '#1abc9c', '#34495e', '#e67e22', '#2ecc71', '#8e44ad'
  ];
  
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = seed.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  return colors[Math.abs(hash) % colors.length];
};

/**
 * Format file size for display
 */
export const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 Bytes';
  
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = bytes / Math.pow(1024, i);
  
  return `${size.toFixed(1)} ${sizes[i]}`;
};

/**
 * Debounce function for search inputs
 */
export const debounce = <T extends (...args: any[]) => void>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * Check if tenant trial is expired
 */
export const isTenantTrialExpired = (tenant: {
  is_trial: boolean;
  trial_ends_at?: string;
}): boolean => {
  if (!tenant.is_trial || !tenant.trial_ends_at) {
    return false;
  }
  return new Date() > new Date(tenant.trial_ends_at);
};

/**
 * Get days remaining in trial
 */
export const getTrialDaysRemaining = (trialEndsAt?: string): number => {
  if (!trialEndsAt) return 0;
  
  const now = new Date();
  const endDate = new Date(trialEndsAt);
  const diffTime = endDate.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return Math.max(0, diffDays);
};

/**
 * Constants that can be shared between platforms
 */
export const CONSTANTS = {
  TENANT_ROLES: {
    OWNER: 'owner',
    ADMIN: 'admin',
    MANAGER: 'manager',
    USER: 'user',
    READONLY: 'readonly',
  } as const,
  
  TENANT_ROLE_LABELS: {
    owner: 'Owner',
    admin: 'Administrator',
    manager: 'Manager',
    user: 'User',
    readonly: 'Read Only',
  } as const,
  
  API_PAGINATION_SIZE: 20,
  
  TRIAL_DAYS: 30,
  
  FILE_UPLOAD_MAX_SIZE: 10 * 1024 * 1024, // 10MB
  
  SUPPORTED_IMAGE_FORMATS: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
  
  SUPPORTED_DOCUMENT_FORMATS: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'],
} as const;

/**
 * Type guards for better type safety
 */
export const isValidTenantRole = (role: string): role is keyof typeof CONSTANTS.TENANT_ROLES => {
  return Object.values(CONSTANTS.TENANT_ROLES).includes(role as any);
};

/**
 * Error handling utilities
 */
export const getErrorMessage = (error: any): string => {
  if (typeof error === 'string') return error;
  if (error?.response?.data?.detail) return error.response.data.detail;
  if (error?.response?.data?.message) return error.response.data.message;
  if (error?.message) return error.message;
  return 'An unexpected error occurred';
};

export const isNetworkError = (error: any): boolean => {
  return error?.code === 'NETWORK_ERROR' || 
         error?.message === 'Network Error' ||
         !navigator?.onLine;
};