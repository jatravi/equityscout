-- Week 3: documents storage + dedup constraints
-- Safe for PostgreSQL

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    run_id UUID NULL REFERENCES research_runs(id) ON DELETE SET NULL,
    source_id UUID NULL REFERENCES sources(id) ON DELETE SET NULL,

    -- original + normalized identity
    url TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    content_hash CHAR(64) NOT NULL, -- sha256 hex

    -- fetch metadata
    final_url TEXT NULL,
    http_status INT NULL,
    content_type TEXT NULL,
    content_length INT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- payload and parse status
    raw_bytes BYTEA NULL,
    parser_status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING|PARSED|FAILED
    parse_error TEXT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- canonical URL dedupe within a company
CREATE UNIQUE INDEX IF NOT EXISTS ux_documents_company_canonical_url
    ON documents(company_id, canonical_url);

-- Optional global content dedupe across all companies/runs.
-- Uncomment ONLY if you want strict global dedup:
-- CREATE UNIQUE INDEX IF NOT EXISTS ux_documents_content_hash
--     ON documents(content_hash);

CREATE INDEX IF NOT EXISTS ix_documents_run_id ON documents(run_id);
CREATE INDEX IF NOT EXISTS ix_documents_source_id ON documents(source_id);
CREATE INDEX IF NOT EXISTS ix_documents_fetched_at ON documents(fetched_at);
CREATE INDEX IF NOT EXISTS ix_documents_parser_status ON documents(parser_status);

-- updated_at trigger (if your project already has a shared trigger, reuse it)
CREATE OR REPLACE FUNCTION set_documents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_documents_updated_at ON documents;
CREATE TRIGGER trg_documents_updated_at
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION set_documents_updated_at();