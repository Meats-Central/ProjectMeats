/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_ENVIRONMENT: string;
  readonly VITE_AI_ASSISTANT_ENABLED: string;
  readonly VITE_ENABLE_DOCUMENT_UPLOAD: string;
  readonly VITE_ENABLE_CHAT_EXPORT: string;
  readonly VITE_MAX_FILE_SIZE: string;
  readonly VITE_SUPPORTED_FILE_TYPES: string;
  readonly VITE_ENABLE_DEBUG: string;
  readonly VITE_ENABLE_DEVTOOLS: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
