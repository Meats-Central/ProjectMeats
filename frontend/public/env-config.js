// Runtime Environment Configuration
// This file is loaded before the React app starts and provides
// runtime configuration that can be changed after build/deployment.
//
// In production deployments, this file is replaced with actual
// environment-specific values by the deployment pipeline.
//
// For local development, these values match the .env.example defaults.

window.ENV = {
  API_BASE_URL: "http://localhost:8000/api/v1",
  ENVIRONMENT: "development"
};
