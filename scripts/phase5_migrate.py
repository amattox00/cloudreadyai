#!/usr/bin/env python3
import os, sys
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL') or ''
if not DATABASE_URL:
    print('[phase5_migrate] No DATABASE_URL/POSTGRES_URL set; skipping.')
    sys.exit(0)

u = urlparse(DATABASE_URL)
# Support postgres:// and postgresql://
if u.scheme.startswith('postgres'):
    conn = psycopg2.connect(DATABASE_URL)
else:
    print('[phase5_migrate] Unsupported DB URL; skipping.')
    sys.exit(0)

DDL = [
    # Pricing cache for normalized SKU items
    '''CREATE TABLE IF NOT EXISTS cr_pricing_cache (
        id SERIAL PRIMARY KEY,
        provider TEXT NOT NULL,
        sku TEXT NOT NULL,
        region TEXT NOT NULL,
        unit TEXT NOT NULL,
        price_per_unit NUMERIC(18,8) NOT NULL,
        currency TEXT NOT NULL DEFAULT 'USD',
        description TEXT,
        raw JSONB,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(provider, sku, region, unit)
    );''',
    # Service matching templates (family → instance/storage/network templates)
    '''CREATE TABLE IF NOT EXISTS cr_service_templates (
        id SERIAL PRIMARY KEY,
        provider TEXT NOT NULL,
        family TEXT NOT NULL,
        template JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(provider, family)
    );''',
    # Recommendations history
    '''CREATE TABLE IF NOT EXISTS cr_recommendations (
        id SERIAL PRIMARY KEY,
        workload_id TEXT NOT NULL,
        input JSONB NOT NULL,
        decision JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );'''
]

with conn:
    with conn.cursor() as cur:
        for stmt in DDL:
            cur.execute(stmt)
        conn.commit()

print('[phase5_migrate] Completed successfully.')
