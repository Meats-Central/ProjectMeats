// frontend/src/aiService.ts
import axios, {
  AxiosError,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosRequestHeaders,
} from 'axios';

// ---- Base URL (Option A: same-origin `/api/v1`) ----
const BUILD_TIME_BASE = (process.env.REACT_APP_API_BASE_URL || '').trim();
const SAME_ORIGIN_BASE =
  (typeof window !== 'undefined' && window.location
    ? `${window.location.origin}/api/v1`
    : '/api/v1'
  ).replace(/\/$/, '');
export const API_BASE_URL = (BUILD_TIME_BASE || SAME_ORIGIN_BASE).replace(/\/$/, '');

// ---- Axios instance ----
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// ---- Interceptors ----
apiClient.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null;
    if (token) {
      (config.headers ??= {} as AxiosRequestHeaders);
      (config.headers as Record<string, string>).Authorization = `Bearer ${token}`;
    }
    // If sending FormData, let axios set boundary automatically
    if (config.data instanceof FormData && config.headers) {
      delete (config.headers as Record<string, string>)['Content-Type'];
    } else {
      // Default JSON header
      (config.headers ??= {} as AxiosRequestHeaders);
      if (!(config.headers as Record<string, string>)['Content-Type']) {
        (config.headers as Record<string, string>)['Content-Type'] = 'application/json';
      }
    }
    // If you need cookie-based auth/CSRF, uncomment:
    // config.withCredentials = true;
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('authToken');
      const next = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `/login?next=${next}`;
    }
    return Promise.reject(error);
  }
);

// ---- Error helper ----
export class ApiError extends Error {
  status?: number;
  data?: unknown;
  constructor(message: string, opts?: { status?: number; data?: unknown }) {
    super(message);
    this.name = 'ApiError';
    this.status = opts?.status;
    this.data = opts?.data;
  }
}

// ---- Generic request (Axios) ----
export async function apiRequest<T = unknown>(
  endpoint: string,
  config: AxiosRequestConfig = {}
): Promise<T> {
  const finalConfig: AxiosRequestConfig = {
    url: endpoint,
    method: config.method ?? 'GET',
    ...config,
  };

  // Ensure JSON header for non-FormData bodies (request interceptor also covers this)
  if (!(finalConfig.data instanceof FormData)) {
    finalConfig.headers = {
      'Content-Type': 'application/json',
      ...(finalConfig.headers as Record<string, string>),
    };
  }

  try {
    const res: AxiosResponse<T> = await apiClient.request<T>(finalConfig);
    return res.data;
  } catch (err) {
    const e = err as AxiosError;
    const status = e.response?.status;
    const msg =
      e.message ||
      `Request failed${status ? ` with status ${status}` : ''}: ${endpoint}`;
    throw new ApiError(msg, { status, data: e.response?.data });
  }
}

// -------------------- Types --------------------
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

export interface ChatRequest {
  message: string;
  session_id?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  message_id: string;
  processing_time: number;
  metadata?: Record<string, any>;
}

export interface DocumentProcessingRequest {
  document_id: string;
  session_id?: string;
  processing_options?: Record<string, any>;
}

export interface DocumentProcessingResponse {
  task_id: string;
  document_id: string;
  status: string;
  message: string;
}

// -------------------- API wrappers --------------------
// Chat
export const chatApi = {
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> =>
    apiRequest<ChatResponse>('/ai-assistant/ai-chat/chat/', {
      method: 'POST',
      data,
    }),

  processDocument: async (
    data: DocumentProcessingRequest
  ): Promise<DocumentProcessingResponse> =>
    apiRequest<DocumentProcessingResponse>('/ai-assistant/ai-chat/process_document/', {
      method: 'POST',
      data,
    }),
};

// Chat Sessions
export const chatSessionsApi = {
  list: async (): Promise<ChatSession[]> =>
    apiRequest<ChatSession[]>('/ai-assistant/ai-sessions/'),

  get: async (sessionId: string): Promise<ChatSession> =>
    apiRequest<ChatSession>(`/ai-assistant/ai-sessions/${sessionId}/`),

  create: async (data: Partial<ChatSession>): Promise<ChatSession> =>
    apiRequest<ChatSession>('/ai-assistant/ai-sessions/', {
      method: 'POST',
      data,
    }),

  update: async (
    sessionId: string,
    data: Partial<ChatSession>
  ): Promise<ChatSession> =>
    apiRequest<ChatSession>(`/ai-assistant/ai-sessions/${sessionId}/`, {
      method: 'PATCH',
      data,
    }),

  delete: async (sessionId: string): Promise<void> =>
    apiRequest<void>(`/ai-assistant/ai-sessions/${sessionId}/`, {
      method: 'DELETE',
    }),

  getMessages: async (sessionId: string): Promise<ChatMessage[]> =>
    apiRequest<ChatMessage[]>(`/ai-assistant/ai-sessions/${sessionId}/messages/`),
};

// Documents
export const documentsApi = {
  upload: async (file: File, sessionId?: string): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    if (sessionId) formData.append('session_id', sessionId);

    const res: AxiosResponse<any> = await apiClient.post(
      '/ai-assistant/ai-documents/',
      formData
    );
    return res.data;
  },

  list: async (): Promise<any[]> =>
    apiRequest<any[]>('/ai-assistant/ai-documents/'),

  get: async (documentId: string): Promise<any> =>
    apiRequest<any>(`/ai-assistant/ai-documents/${documentId}/`),
};

// Utilities
export const aiUtils = {
  isEnabled: (): boolean => process.env.REACT_APP_AI_ASSISTANT_ENABLED === 'true',
  getConfig: () => ({
    apiBaseUrl: API_BASE_URL,
    enabled: aiUtils.isEnabled(),
    features: {
      chat: true,
      documentProcessing: true,
      entityExtraction: true,
    },
  }),
  formatProcessingTime: (seconds: number): string =>
    seconds < 1 ? `${Math.round(seconds * 1000)}ms` : `${seconds.toFixed(1)}s`,
  generateSessionTitle: (message: string): string =>
    message.length <= 50 ? message : `${message.substring(0, 47)}...`,
};

export default apiClient;
