-- =====================================================================
-- CloudReadyAI — Phase B Step 1
-- Core Ingestion Tables
-- =====================================================================

CREATE TABLE IF NOT EXISTS ingestion_runs (
    run_id          TEXT PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    customer        TEXT,
    description     TEXT,
    source_type     TEXT,                -- vcenter|csv|json|mixed
    file_count      INTEGER DEFAULT 0,
    status          TEXT DEFAULT 'created',  -- created|uploading|queued|running|completed|failed
    error_message   TEXT
);

CREATE TABLE IF NOT EXISTS ingestion_files (
    file_id         TEXT PRIMARY KEY,
    run_id          TEXT REFERENCES ingestion_runs(run_id),
    filename        TEXT,
    s3_key          TEXT,          -- s3://bucket/prefix/file.csv
    uploaded_at     TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================
-- Normalized Workload Data Tables
-- =====================================================================

CREATE TABLE IF NOT EXISTS servers (
    server_id       TEXT PRIMARY KEY,
    run_id          TEXT REFERENCES ingestion_runs(run_id),
    hostname        TEXT,
    ip              TEXT,
    cpu_cores       INTEGER,
    memory_gb       NUMERIC,
    os              TEXT,
    environment     TEXT,
    raw             JSONB,         -- full original row
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS apps (
    app_id          TEXT PRIMARY KEY,
    run_id          TEXT REFERENCES ingestion_runs(run_id),
    name            TEXT,
    owner           TEXT,
    business_unit   TEXT,
    tier            TEXT,
    raw             JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS storage (
    storage_id      TEXT PRIMARY KEY,
    run_id          TEXT REFERENCES ingestion_runs(run_id),
    server_id       TEXT,
    size_gb         NUMERIC,
    type            TEXT,
    raw             JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS networks (
    flow_id         TEXT PRIMARY KEY,
    run_id          TEXT REFERENCES ingestion_runs(run_id),
    src             TEXT,
    dest            TEXT,
    port            INTEGER,
    protocol        TEXT,
    bytes           BIGINT,
    raw             JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS relationships (
    rel_id          TEXT PRIMARY KEY,
    run_id          TEXT REFERENCES ingestion_runs(run_id),
    from_type       TEXT,          -- server|app|storage|network
    from_id         TEXT,
    to_type         TEXT,
    to_id           TEXT,
    relationship    TEXT,          -- runs|depends_on|uses|connects_to|reads_from
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================
-- Helpful Indexes
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_servers_run  ON servers(run_id);
CREATE INDEX IF NOT EXISTS idx_apps_run     ON apps(run_id);
CREATE INDEX IF NOT EXISTS idx_storage_run  ON storage(run_id);
CREATE INDEX IF NOT EXISTS idx_networks_run ON networks(run_id);
CREATE INDEX IF NOT EXISTS idx_rel_run      ON relationships(run_id);
CREATE INDEX IF NOT EXISTS idx_files_run    ON ingestion_files(run_id);

-- Done
