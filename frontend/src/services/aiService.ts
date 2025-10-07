/**
 * API Service for ProjectMeats AI Assistant
 *
 * Handles communication with the Django REST API backend.
 * Includes fixed endpoints from PR #63.
 */
import axios from "axios";

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "/api/v1";

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
apiClient.interceptors.response.use(
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

// API helper function
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status} ${response.statusText}`,
    );
  }

  return response.json();
}

// Type definitions
export interface ChatSession {
  id: string;
  title?: string;
  session_status: "active" | "completed" | "archived";
  context_data?: Record<string, any>;
  last_activity: string;
  created_on: string;
  modified_on: string;
  message_count: number;
}

export interface ChatMessage {
  id: string;
  session: string;
  message_type: "user" | "assistant" | "system" | "document";
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

// Chat API
export const chatApi = {
  /**
   * Send a message and get AI response
   * Fixed endpoint: /ai-assistant/ai-chat/chat/ (from PR #63)
   */
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    return apiRequest<ChatResponse>("/ai-assistant/ai-chat/chat/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * Process a document with AI
   * Fixed endpoint: /ai-assistant/ai-chat/process_document/ (from PR #63)
   */
  processDocument: async (
    data: DocumentProcessingRequest,
  ): Promise<DocumentProcessingResponse> => {
    return apiRequest<DocumentProcessingResponse>(
      "/ai-assistant/ai-chat/process_document/",
      {
        method: "POST",
        body: JSON.stringify(data),
      },
    );
  },
};

// Chat Sessions API
export const chatSessionsApi = {
  /**
   * List all chat sessions for the current user
   */
  list: async (): Promise<ChatSession[]> => {
    return apiRequest<ChatSession[]>("/ai-assistant/ai-sessions/");
  },

  /**
   * Get a specific chat session
   */
  get: async (sessionId: string): Promise<ChatSession> => {
    return apiRequest<ChatSession>(`/ai-assistant/ai-sessions/${sessionId}/`);
  },

  /**
   * Create a new chat session
   */
  create: async (data: Partial<ChatSession>): Promise<ChatSession> => {
    return apiRequest<ChatSession>("/ai-assistant/ai-sessions/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * Update a chat session
   */
  update: async (
    sessionId: string,
    data: Partial<ChatSession>,
  ): Promise<ChatSession> => {
    return apiRequest<ChatSession>(`/ai-assistant/ai-sessions/${sessionId}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a chat session
   */
  delete: async (sessionId: string): Promise<void> => {
    return apiRequest<void>(`/ai-assistant/ai-sessions/${sessionId}/`, {
      method: "DELETE",
    });
  },

  /**
   * Get messages for a specific session
   */
  getMessages: async (sessionId: string): Promise<ChatMessage[]> => {
    return apiRequest<ChatMessage[]>(
      `/ai-assistant/ai-sessions/${sessionId}/messages/`,
    );
  },
};

// Documents API
export const documentsApi = {
  /**
   * Upload a document
   */
  upload: async (file: File, sessionId?: string): Promise<any> => {
    const formData = new FormData();
    formData.append("file", file);
    if (sessionId) {
      formData.append("session_id", sessionId);
    }

    return apiRequest<any>("/ai-assistant/ai-documents/", {
      method: "POST",
      body: formData,
      headers: {}, // Remove Content-Type to let browser set it for FormData
    });
  },

  /**
   * List uploaded documents
   */
  list: async (): Promise<any[]> => {
    return apiRequest<any[]>("/ai-assistant/ai-documents/");
  },

  /**
   * Get document processing status
   */
  get: async (documentId: string): Promise<any> => {
    return apiRequest<any>(`/ai-assistant/ai-documents/${documentId}/`);
  },
};

// AI Utils
export const aiUtils = {
  /**
   * Check if AI assistant is enabled
   */
  isEnabled: (): boolean => {
    return process.env.REACT_APP_AI_ASSISTANT_ENABLED === "true";
  },

  /**
   * Get AI assistant configuration
   */
  getConfig: () => ({
    apiBaseUrl: API_BASE_URL,
    enabled: aiUtils.isEnabled(),
    features: {
      chat: true,
      documentProcessing: true,
      entityExtraction: true,
    },
  }),

  /**
   * Format processing time for display
   */
  formatProcessingTime: (seconds: number): string => {
    if (seconds < 1) {
      return `${Math.round(seconds * 1000)}ms`;
    }
    return `${seconds.toFixed(1)}s`;
  },

  /**
   * Generate session title from first message
   */
  generateSessionTitle: (message: string): string => {
    const maxLength = 50;
    if (message.length <= maxLength) {
      return message;
    }
    return message.substring(0, maxLength - 3) + "...";
  },
};

export default apiClient;
