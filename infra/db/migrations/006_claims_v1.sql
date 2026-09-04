-- Week 5: Analysis + Claims v1

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    run_id UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

    claim_type TEXT NOT NULL,         -- BUSINESS_MODEL | FINANCIAL_TREND | PROMOTER_GOVERNANCE
    claim_text TEXT NOT NULL,
    stance TEXT NULL,                 -- POSITIVE | NEUTRAL | NEGATIVE
    confidence DOUBLE PRECISION NOT NULL DEFAULT 0.5,

    contradiction_tag TEXT NOT NULL DEFAULT 'NONE',  -- NONE | INTRA_DOC | CROSS_DOC | METRIC_CONFLICT
    contradiction_note TEXT NULL,

    supporting_evidence_count INT NOT NULL DEFAULT 0,
    supporting_locators_json JSONB NOT NULL DEFAULT '[]'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_claims_run_id ON claims(run_id);
CREATE INDEX IF NOT EXISTS ix_claims_claim_type ON claims(claim_type);
CREATE INDEX IF NOT EXISTS ix_claims_confidence ON claims(confidence DESC);
CREATE INDEX IF NOT EXISTS ix_claims_contradiction_tag ON claims(contradiction_tag);
