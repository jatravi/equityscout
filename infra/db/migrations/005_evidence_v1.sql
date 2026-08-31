-- Week 4: Evidence extraction v1
-- Requires: documents + parsed_documents tables from Week 3

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    run_id UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    evidence_type TEXT NOT NULL, -- BUSINESS_SIGNAL | FINANCIAL_METRIC | PROMOTER_HOLDING
    key TEXT NOT NULL,           -- revenue, net_profit, promoter_holding_pct, etc.

    value_text TEXT NULL,
    value_num DOUBLE PRECISION NULL,
    value_unit TEXT NULL,
    period TEXT NULL,

    confidence DOUBLE PRECISION NOT NULL DEFAULT 0.5,

    locator_json JSONB NOT NULL DEFAULT '{}'::jsonb, -- required source locator
    snippet TEXT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- deterministic dedupe for repeated extraction output
CREATE UNIQUE INDEX IF NOT EXISTS ux_evidence_dedupe
ON evidence (
    run_id,
    document_id,
    evidence_type,
    key,
    COALESCE(value_text, ''),
    COALESCE(value_num::text, ''),
    COALESCE(value_unit, ''),
    COALESCE(period, '')
);

CREATE INDEX IF NOT EXISTS ix_evidence_run_id ON evidence(run_id);
CREATE INDEX IF NOT EXISTS ix_evidence_document_id ON evidence(document_id);
CREATE INDEX IF NOT EXISTS ix_evidence_type ON evidence(evidence_type);
CREATE INDEX IF NOT EXISTS ix_evidence_key ON evidence(key);