-- SahiTol PostgreSQL / PostGIS Initialization Script
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify PostGIS installation
SELECT postgis_full_version();
