-- Binance AI Trader Pro — Initial DB Setup
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create default plans (run after alembic migrations)
-- These are inserted by the seed script
