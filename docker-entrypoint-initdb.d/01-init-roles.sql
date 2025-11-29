-- Initialize database roles and permissions for ProjectMeats
-- This script is idempotent and can be run multiple times safely
-- NOTE: For production, ensure proper password management via environment variables

-- Ensure postgres user exists (should already exist in PostgreSQL Docker image)
-- This check is primarily for documentation and edge cases
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres') THEN
    -- In production, use environment variable: ${POSTGRES_PASSWORD}
    -- For local dev, the postgres user is created by the Docker image with POSTGRES_PASSWORD env var
    RAISE NOTICE 'postgres role should already exist in Docker PostgreSQL image';
  ELSE
    RAISE NOTICE 'postgres role already exists';
  END IF;
END
$$;

-- Create application user if needed (example for future use)
-- Uncomment and customize as needed for production deployments
-- DO $$
-- BEGIN
--   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'appuser') THEN
--     -- SECURITY: Use environment variable for password in production
--     -- CREATE ROLE appuser WITH LOGIN PASSWORD '${APP_USER_PASSWORD}';
--     RAISE NOTICE 'Created appuser role';
--   ELSE
--     RAISE NOTICE 'appuser role already exists';
--   END IF;
-- END
-- $$;

-- Grant necessary permissions
-- GRANT ALL PRIVILEGES ON DATABASE defaultdb TO postgres;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Log completion
DO $$
BEGIN
  RAISE NOTICE 'Database initialization completed successfully';
END
$$;
