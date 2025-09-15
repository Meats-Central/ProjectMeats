// frontend/src/aiService.ts

// ----- Runtime config (for single-image, per-env config via env.js) -----
declare global {
  interface Window {
    __ENV?: { API_BASE_URL?: string };
  }
}

// Safely compute a default origin for non-browser contexts (SSR/build)
const DEFAULT_ORIGIN =
  typeof window !== "undefined" && window.location ? window.location.origin : "";

/**
 * API base URL resolution (priority):
 * 1) window.__ENV.API_BASE_URL  (written at container start by env.js)
 * 2) process.env.REACT_APP_API_BASE_URL (baked at build time)
 * 3) `${window.location.origin}/api/v1` or `/api/v1` as a final fallback
 *
 * For Option B (separate API domains), set per environment:
 *   dev:  https://api-dev.meatscentral.com/api/v1
 *   uat:  https://api-uat.meatscentral.com/api/v1
 *   prod: https://api.meatscentral.com/api/v1
 */
export const API_BASE_URL = (() => {
  const runtime = window?.__ENV?.API_BASE_URL?.trim() || "";
  const build = (process.env.REACT_APP_API_BASE_URL || "").trim();
  const origin = DEFAULT_ORIGIN ? `${DEFAULT_ORIGIN}/api/v1` : "/api/v1";

  return (runtime || build || origin).replace(/\/$/, "");
})();

// -------------------- Types (adjust to your real backend shapes) --------------------
export type ID = string;

export interface ChatRequest {
  message: string;
  conversationId?: ID;
  // Add fields as needed (e.g., model, temperature, etc.)
  // model?: string;
  // stream?: boolean;
}

export interface ChatResponse {
  conversationId: ID;
  reply: string;
  // Optional server-provided fields:
  // tokensUsed?: number;
  // finishReason?: string;
  // meta?: Record<string, unknown>;
}

export interface HealthResponse {
  status: "ok" | "degraded" | "down";
  version?: string;
}

// -------------------- Small helper --------------------
const joinUrl = (base: string, path: string) =>
  `${base.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;

// -------------------- Error class (optional but handy) --------------------
export class ApiError extends Error {
  status?: number;
  bodySnippet?: string;

  constructor(message: string, opts?: { status?: number; bodySnippet?: string }) {
    super(message);
    this.name = "ApiError";
    this.status = opts?.status;
    this.bodySnippet = opts?.bodySnippet;
  }
}

// -------------------- Generic request --------------------
/**
 * Generic request helper.
 * Usage: const data = await apiRequest<MyType>("/ai-assistant/ai-chat/chat/", { method: "POST", body: JSON.stringify(payload) })
 */
export async function apiRequest<T = unknown>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const url = joinUrl(API_BASE_URL, path);
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(init.headers as HeadersInit),
  };

  // If you need cookies across domains, switch to: credentials: "include"
  // and ensure CORS on the backend allows credentials + sets SameSite=None.
  const res = await fetch(url, { ...init, headers /*, credentials: "same-origin" */ });

  if (!res.ok) {
    let snippet = "";
    try {
      snippet = (await res.text()).slice(0, 300);
    } catch {
      /* ignore */
    }
    throw new ApiError(`HTTP ${res.status} ${res.statusText}`, {
      status: res.status,
      bodySnippet: snippet,
    });
  }

  // If endpoint returns no body (e.g., 204), return undefined as T
  if (res.status === 204) return undefined as T;

  return (await res.json()) as T;
}

// -------------------- Concrete API functions --------------------
/** Health check from the API service (e.g., /api/v1/health/) */
export async function getHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/health/");
}

/**
 * Send a chat message to the backend (matches your current path)
 * Backend route: /api/v1/ai-assistant/ai-chat/chat/
 */
export async function sendMessage(data: ChatRequest): Promise<ChatResponse> {
  return apiRequest<ChatResponse>("/ai-assistant/ai-chat/chat/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
