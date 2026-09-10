-- Week 7: Validation + Reliability Hardening

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Add report validation columns
ALTER TABLE reports
    ADD COLUMN IF NOT EXISTS validation_status TEXT NOT NULL DEFAULT 'PENDING',
    ADD COLUMN IF NOT EXISTS validation_errors_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS validated_at TIMESTAMPTZ NULL;

CREATE INDEX IF NOT EXISTS ix_reports_validation_status ON reports(validation_status);

-- Per-run diagnostics snapshot table
CREATE TABLE IF NOT EXISTS run_diagnostics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

    token_input INT NOT NULL DEFAULT 0,
    token_output INT NOT NULL DEFAULT 0,
    estimated_cost NUMERIC(12, 6) NOT NULL DEFAULT 0,

    sources_total INT NOT NULL DEFAULT 0,
    sources_success INT NOT NULL DEFAULT 0,
    source_success_rate NUMERIC(6, 3) NOT NULL DEFAULT 0,

    docs_total INT NOT NULL DEFAULT 0,
    docs_parsed INT NOT NULL DEFAULT 0,
    parser_failure_rate NUMERIC(6, 3) NOT NULL DEFAULT 0,

    evidence_count INT NOT NULL DEFAULT 0,
    claims_count INT NOT NULL DEFAULT 0,
    citation_count INT NOT NULL DEFAULT 0,

    report_validation_status TEXT NOT NULL DEFAULT 'PENDING',
    validation_error_count INT NOT NULL DEFAULT 0,

    discover_ms INT NOT NULL DEFAULT 0,
    ingest_ms INT NOT NULL DEFAULT 0,
    extract_ms INT NOT NULL DEFAULT 0,
    claims_ms INT NOT NULL DEFAULT 0,
    report_ms INT NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_run_diagnostics_run_id ON run_diagnostics(run_id);
CREATE INDEX IF NOT EXISTS ix_run_diagnostics_created_at ON run_diagnostics(created_at DESC);