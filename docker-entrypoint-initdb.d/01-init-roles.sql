-- Initialize database roles and permissions for ProjectMeats
-- This script is idempotent and can be run multiple times safely

-- Ensure postgres user exists (should already exist, but check anyway)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres') THEN
    CREATE ROLE postgres WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'postgres';
    RAISE NOTICE 'Created postgres role';
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
--     CREATE ROLE appuser WITH LOGIN PASSWORD 'changeme';
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
