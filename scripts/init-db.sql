-- Database initialization script for Job Board Backend
-- This script sets up the initial database configuration

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database user if it doesn't exist (for development)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'job_board_user') THEN
        CREATE ROLE job_board_user WITH LOGIN PASSWORD 'job_board_password';
    END IF;
END
$$;

-- Grant necessary permissions
GRANT CONNECT ON DATABASE postgres TO job_board_user;
GRANT USAGE ON SCHEMA public TO job_board_user;
GRANT CREATE ON SCHEMA public TO job_board_user;

-- Create indexes for performance (will be created by Django migrations as well)
-- These are here as documentation of the expected indexes

-- Performance optimization settings
ALTER SYSTEM SET track_activity_query_size = 2048;

-- Connection pooling settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Reload configuration
SELECT pg_reload_conf();