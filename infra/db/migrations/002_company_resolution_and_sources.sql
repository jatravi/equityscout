BEGIN;

-- 1) Extend companies
ALTER TABLE companies
  ADD COLUMN IF NOT EXISTS nse_symbol TEXT,
  ADD COLUMN IF NOT EXISTS bse_code TEXT,
  ADD COLUMN IF NOT EXISTS cin TEXT,
  ADD COLUMN IF NOT EXISTS is_listed BOOLEAN NOT NULL DEFAULT TRUE;

-- 2) company_aliases
CREATE TABLE IF NOT EXISTS company_aliases (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  alias TEXT NOT NULL,
  alias_type TEXT NOT NULL, -- e.g. LEGAL_SHORT, BRAND, TICKER, COMMON
  confidence NUMERIC(4,3) NOT NULL DEFAULT 1.000 CHECK (confidence >= 0 AND confidence <= 1),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3) sources
CREATE TABLE IF NOT EXISTS sources (
  id UUID PRIMARY KEY,
  run_id UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  task_type TEXT NOT NULL,
  source_type TEXT NOT NULL, -- NSE_ANNOUNCEMENT, NSE_RESULTS, BSE_FILING, COMPANY_IR, etc.
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  publisher TEXT NOT NULL,
  published_at TIMESTAMPTZ NULL,
  discovered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  authority_score DOUBLE PRECISION NULL CHECK (authority_score >= 0 AND authority_score <= 1),
  rank_score DOUBLE PRECISION NULL CHECK (rank_score >= 0 AND rank_score <= 1),
  metadata_json JSONB NULL
);

-- 4) Indexes
CREATE INDEX IF NOT EXISTS idx_companies_nse_symbol ON companies(nse_symbol);
CREATE INDEX IF NOT EXISTS idx_companies_bse_code ON companies(bse_code);

CREATE INDEX IF NOT EXISTS idx_company_aliases_alias ON company_aliases(alias);
CREATE INDEX IF NOT EXISTS idx_company_aliases_company_id ON company_aliases(company_id);

CREATE INDEX IF NOT EXISTS idx_sources_run_id ON sources(run_id);
CREATE INDEX IF NOT EXISTS idx_sources_company_id ON sources(company_id);
CREATE INDEX IF NOT EXISTS idx_sources_task_type ON sources(task_type);

-- Unique source URL per company
CREATE UNIQUE INDEX IF NOT EXISTS uq_sources_url_company_id ON sources(url, company_id);

COMMIT;