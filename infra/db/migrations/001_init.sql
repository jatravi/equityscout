-- 001_init.sql
-- Baseline schema for EquityScout Week 1 foundations

-- Optional but recommended for UUID generation (Postgres 13+)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =========================
-- companies
-- =========================
CREATE TABLE IF NOT EXISTS companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  legal_name TEXT NOT NULL,
  display_name TEXT,
  market TEXT NOT NULL DEFAULT 'IN',
  nse_symbol TEXT,
  bse_code TEXT,
  isin TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_companies_market_legal_name UNIQUE (market, legal_name)
);

-- Optional uniqueness for ISIN when present
CREATE UNIQUE INDEX IF NOT EXISTS uq_companies_isin_not_null
  ON companies (isin)
  WHERE isin IS NOT NULL;

-- =========================
-- research_runs
-- =========================
CREATE TABLE IF NOT EXISTS research_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
  input_company_text TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  error_message TEXT,
  config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_research_runs_status
    CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'PARTIAL'))
);

CREATE INDEX IF NOT EXISTS idx_research_runs_company_status
  ON research_runs (company_id, status);

CREATE INDEX IF NOT EXISTS idx_research_runs_created_at_desc
  ON research_runs (created_at DESC);

-- =========================
-- research_tasks
-- =========================
CREATE TABLE IF NOT EXISTS research_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  task_type TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_research_tasks_task_type
    CHECK (task_type IN ('BUSINESS', 'FINANCIAL', 'PROMOTER')),
  CONSTRAINT chk_research_tasks_status
    CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'PARTIAL')),
  CONSTRAINT uq_research_tasks_run_task_type
    UNIQUE (run_id, task_type)
);

CREATE INDEX IF NOT EXISTS idx_research_tasks_run_status
  ON research_tasks (run_id, status);

-- =========================
-- reports
-- =========================
CREATE TABLE IF NOT EXISTS reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL UNIQUE REFERENCES research_runs(id) ON DELETE CASCADE,
  markdown TEXT NOT NULL,
  validation_status TEXT NOT NULL DEFAULT 'PENDING',
  version INT NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);